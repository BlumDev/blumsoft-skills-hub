"""Unit tests for the gen-asset ComfyUI scripts.

No ComfyUI is started or contacted here: the scripts are imported as modules and only
their pure parts are exercised (workflow injection, history parsing, input file naming).
Importing them is side effect free, main() sits behind the __main__ guard.

  python -m unittest tests.test_gen_asset
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
GEN_ASSET = ROOT / 'skills/custom/gen-asset'
HIRES_WORKFLOWS = ('sdxl_hires.api.json', 'sd15_anime_hires.api.json')


def load_script(name):
    path = GEN_ASSET / 'scripts' / name
    spec = importlib.util.spec_from_file_location('gen_asset_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


comfy_generate = load_script('comfy_generate.py')
upscale = load_script('upscale.py')
ledger = load_script('ledger.py')

# What /history/<id> returns once a prompt died on ComfyUI's side: an entry that exists,
# carries a status and will never grow images.
FAILED_HISTORY_ENTRY = {
    'outputs': {},
    'status': {
        'status_str': 'error',
        'completed': False,
        'messages': [
            ['execution_start', {'prompt_id': 'p1'}],
            ['execution_error', {
                'node_id': '4',
                'node_type': 'CheckpointLoaderSimple',
                'exception_type': 'FileNotFoundError',
                'exception_message': 'checkpoint not found',
            }],
        ],
    },
}

# The same shape once a prompt finished: an entry carrying the image download() fetches.
SUCCESS_HISTORY_ENTRY = {
    'outputs': {'9': {'images': [{'filename': 'hero_00001_.png', 'subfolder': '', 'type': 'output'}]}},
    'status': {'status_str': 'success', 'completed': True},
}

# A prompt ComfyUI has accepted but not finished: no images, no verdict. The poll loop must
# keep waiting on this one and end on its own budget.
QUEUED_HISTORY_ENTRY = {'outputs': {}}


def workflow(name):
    with open(GEN_ASSET / 'workflows' / name, encoding='utf-8') as fh:
        return json.load(fh)


def by_title(graph):
    """The inputs of every node, keyed by the _meta.title marker inject() matches on."""
    return {
        node['_meta']['title']: node['inputs']
        for node in graph.values()
        if node.get('_meta', {}).get('title')
    }


def cli_args(**overrides):
    args = dict(
        prompt='a red apple', negative='', width=1024, height=1024,
        seed=4242, steps=None, checkpoint=None, lora=None, lora_strength=0.8,
    )
    args.update(overrides)
    return argparse.Namespace(**args)


class InjectSeedTests(unittest.TestCase):
    def test_seed_reaches_both_samplers_of_the_hires_workflows(self):
        for name in HIRES_WORKFLOWS:
            with self.subTest(workflow=name):
                template = by_title(workflow(name))
                self.assertNotEqual(
                    template['SAMPLER_HIRES']['seed'], 4242,
                    'the template must carry a different seed, otherwise this test cannot fail',
                )

                nodes = by_title(comfy_generate.inject(workflow(name), cli_args(seed=4242)))
                self.assertEqual(nodes['SAMPLER']['seed'], 4242)
                self.assertEqual(nodes['SAMPLER_HIRES']['seed'], 4242)

    def test_steps_stay_on_the_base_pass(self):
        # The hires pass runs deliberately fewer steps than the base pass, so --steps must
        # not be pushed onto it.
        for name in HIRES_WORKFLOWS:
            with self.subTest(workflow=name):
                template = by_title(workflow(name))
                nodes = by_title(comfy_generate.inject(workflow(name), cli_args(steps=12)))
                self.assertEqual(nodes['SAMPLER']['steps'], 12)
                self.assertEqual(nodes['SAMPLER_HIRES']['steps'], template['SAMPLER_HIRES']['steps'])

    def test_seed_reaches_the_single_sampler_workflows(self):
        for name in ('sdxl_t2i.api.json', 'flux_schnell_t2i.api.json', 'chroma_t2i.api.json'):
            with self.subTest(workflow=name):
                nodes = by_title(comfy_generate.inject(workflow(name), cli_args(seed=7)))
                self.assertEqual(nodes['SAMPLER']['seed'], 7)
                self.assertNotIn('SAMPLER_HIRES', nodes)


class ExecutionErrorTests(unittest.TestCase):
    """Both scripts carry their own copy of the helper, so both are checked."""

    def test_names_node_and_message_of_a_failed_run(self):
        for module in (comfy_generate, upscale):
            with self.subTest(module=module.__name__):
                message = module.execution_error(FAILED_HISTORY_ENTRY)
                self.assertIn('CheckpointLoaderSimple', message)
                self.assertIn('checkpoint not found', message)

    def test_reports_a_failed_run_that_carries_no_detail(self):
        for module in (comfy_generate, upscale):
            with self.subTest(module=module.__name__):
                entry = {'outputs': {}, 'status': {'status_str': 'error', 'messages': None}}
                self.assertTrue(module.execution_error(entry))

    def test_keeps_waiting_on_anything_that_is_not_a_reported_error(self):
        # A wrong abort would kill a healthy run, so every unclear shape must return None.
        healthy = (
            {'outputs': {}},                                        # queued, no status yet
            {'outputs': {}, 'status': {'status_str': 'success'}},   # done, images read elsewhere
            {'outputs': {}, 'status': {}},                          # status without a verdict
            {'outputs': {}, 'status': None},                        # unexpected shape
            {'outputs': {}, 'status': 'error'},                     # status not a dict
        )
        for module in (comfy_generate, upscale):
            for entry in healthy:
                with self.subTest(module=module.__name__, entry=entry):
                    self.assertIsNone(module.execution_error(entry))


def stub_api(history_entry, polls, on_prompt=None):
    """Replacement for the scripts' api(): answers every call from memory and records polls.

    on_prompt fires while the prompt is queued, the moment the real ComfyUI would read the
    input file. That is the only window in which a run's copy of it exists.
    """
    def api(base, path, payload=None, timeout=600):
        if path == '/system_stats':
            return {}
        if path == '/prompt':
            if on_prompt:
                on_prompt()
            return {'prompt_id': 'p1'}
        polls.append(path)
        return {'p1': history_entry}
    return api


class FakeClock:
    """Deterministic stand-in for the time module: nothing really sleeps, the clock just moves.

    Both scripts reach the clock through their module level `time`, so replacing that name
    makes the poll loop measurable without waiting for it.
    """

    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def slow_poll_api(history_entry, clock, poll_cost, polls):
    """api() replacement whose /history call burns poll_cost seconds of the fake wall clock.

    Records the timeout each poll was given, which is what a hanging ComfyUI would be able to
    block for.
    """
    def api(base, path, payload=None, timeout=600):
        if path == '/system_stats':
            return {}
        if path == '/prompt':
            return {'prompt_id': 'p1'}
        polls.append(timeout)
        clock.now += poll_cost
        return {'p1': history_entry}
    return api


def fake_download(base, image, out_path):
    """Stand-in for download(): writes what a real /view call would deliver."""
    with open(out_path, 'wb') as fh:
        fh.write(b'upscaled')


def staged_inputs(folder):
    """Everything in the stand-in for ComfyUI's shared input folder, name -> bytes.

    A folder that does not exist counts as empty: for a run that stages somewhere else the
    absence is exactly what has to be measured.
    """
    if not os.path.isdir(folder):
        return {}
    return {name: (Path(folder) / name).read_bytes() for name in sorted(os.listdir(folder))}


class PollLoopTests(unittest.TestCase):
    """main() end to end against a stubbed HTTP layer, no ComfyUI is started or contacted."""

    def test_comfy_generate_aborts_on_a_failed_prompt(self):
        polls = []
        with tempfile.TemporaryDirectory() as tmp:
            argv = [
                'comfy_generate.py',
                '--workflow', str(GEN_ASSET / 'workflows/sdxl_t2i.api.json'),
                '--prompt', 'a red apple',
                '--out', os.path.join(tmp, 'out.png'),
                # Short timeout on purpose: without the fix this bounds the test at four
                # polls instead of the 600 the default would run through.
                '--timeout', '6',
            ]
            with mock.patch.object(comfy_generate, 'api', stub_api(FAILED_HISTORY_ENTRY, polls)), \
                    mock.patch.object(sys, 'argv', argv), \
                    contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    comfy_generate.main()

            self.assertIn('checkpoint not found', str(raised.exception))
            self.assertEqual(len(polls), 1, 'the run must end on the first poll, not on the timeout')
            self.assertFalse(os.path.exists(os.path.join(tmp, 'out.png')))

    def test_upscale_aborts_on_a_failed_prompt(self):
        polls = []
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, 'hero.png')
            with open(source, 'wb') as fh:
                fh.write(b'not really a png')
            comfy_input = os.path.join(tmp, 'comfy-input')
            argv = ['upscale.py', '--image', source, '--out', os.path.join(tmp, 'hero_2x.png'),
                    '--timeout', '6']

            with mock.patch.object(upscale, 'api', stub_api(FAILED_HISTORY_ENTRY, polls)), \
                    mock.patch.object(upscale, 'COMFY_INPUT', comfy_input), \
                    mock.patch.object(sys, 'argv', argv), \
                    contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    upscale.main()

            self.assertIn('checkpoint not found', str(raised.exception))
            self.assertEqual(len(polls), 1, 'the run must end on the first poll, not on the timeout')


class LedgerFindTests(unittest.TestCase):
    """One half written JSONL line must not take the whole recall index down."""

    def find(self, path, **overrides):
        args = argparse.Namespace(vertical=None, tag=None, min_rating=None, limit=10)
        for key, value in overrides.items():
            setattr(args, key, value)
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(ledger, 'LEDGER', path), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            ledger.cmd_find(args)
        return out.getvalue(), err.getvalue()

    def write_ledger(self, tmp, *lines):
        path = os.path.join(tmp, 'ledger.jsonl')
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(''.join(line + '\n' for line in lines))
        return path

    def write_ledger_bytes(self, tmp, blob):
        """The ledger as raw bytes: a half written line can be broken below the text layer."""
        path = os.path.join(tmp, 'ledger.jsonl')
        with open(path, 'wb') as fh:
            fh.write(blob)
        return path

    def test_a_truncated_line_does_not_hide_the_intact_entries(self):
        # An add killed mid-append leaves exactly this behind. json.loads on it used to raise
        # and every later find died with a JSONDecodeError, however many good lines there were.
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_ledger(
                tmp,
                json.dumps({'image': 'first.png', 'rating': 5, 'vertical': 'winzer'}),
                '{"image": "half-written.png", "rating"',
                json.dumps({'image': 'second.png', 'rating': 4, 'vertical': 'winzer'}),
            )
            out, err = self.find(path)

        self.assertIn('first.png', out)
        self.assertIn('second.png', out)
        self.assertNotIn('half-written.png', out)
        self.assertIn('Zeile 2', err, 'the skipped line has to be named, not swallowed')

    def test_a_line_broken_mid_utf8_does_not_hide_the_intact_entries(self):
        # cmd_add writes with ensure_ascii=False, so a prompt, a note or a Windows path with an
        # umlaut sits in the file as multi byte UTF-8. An add killed inside such a character
        # leaves a byte the decoder cannot finish, and that raises while the file is being
        # iterated, i.e. before json.loads is ever reached: the skip path above never ran and
        # the whole index was gone again.
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_ledger_bytes(
                tmp,
                json.dumps({'image': 'first.png', 'rating': 5}).encode('utf-8') + b'\n'
                + b'{"note": "\xc3',  # first byte of 'ü', the add died right here
            )
            out, err = self.find(path)

        self.assertIn('first.png', out)
        self.assertIn('Zeile 2', err, 'the unreadable line has to be named, not swallowed')

    def test_filters_still_apply_to_what_survived(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self.write_ledger(
                tmp,
                json.dumps({'image': 'winzer.png', 'rating': 5, 'vertical': 'winzer'}),
                '}broken{',
                json.dumps({'image': 'food.png', 'rating': 5, 'vertical': 'food'}),
            )
            out, _ = self.find(path, vertical='winzer')

        self.assertIn('winzer.png', out)
        self.assertNotIn('food.png', out)


class PollBudgetTests(unittest.TestCase):
    """--timeout is a wall clock: it bounds the whole run and every single poll inside it.

    The loop used to count 1.5s sleeps and hand the HTTP call no timeout at all, so it ran for
    --timeout/1.5 polls of up to api()'s default (600s / 900s) each.
    """

    def run_until_timeout(self, module, argv, clock, polls, poll_cost):
        api = slow_poll_api(QUEUED_HISTORY_ENTRY, clock, poll_cost, polls)
        with mock.patch.object(module, 'api', api), \
                mock.patch.object(module, 'time', clock), \
                mock.patch.object(sys, 'argv', argv), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                module.main()
        return raised.exception

    def assert_budget_kept(self, exception, clock, polls, budget):
        self.assertIn(f'Timeout nach {budget:g}s', str(exception))
        self.assertTrue(all(t <= budget for t in polls),
                        f'no single poll may be allowed to block longer than the budget: {polls}')
        self.assertEqual(len(polls), 1, 'a poll that eats the budget leaves room for no other')
        self.assertLessEqual(clock.now, budget + 1.5, 'the run must end when --timeout says so')

    def test_comfy_generate_keeps_the_timeout_budget(self):
        clock, polls = FakeClock(), []
        with tempfile.TemporaryDirectory() as tmp:
            argv = [
                'comfy_generate.py',
                '--workflow', str(GEN_ASSET / 'workflows/sdxl_t2i.api.json'),
                '--prompt', 'a red apple',
                '--out', os.path.join(tmp, 'out.png'),
                '--timeout', '6',
            ]
            exception = self.run_until_timeout(comfy_generate, argv, clock, polls, poll_cost=4.0)

        self.assert_budget_kept(exception, clock, polls, budget=6.0)

    def test_upscale_keeps_the_timeout_budget(self):
        clock, polls = FakeClock(), []
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, 'hero.png')
            with open(source, 'wb') as fh:
                fh.write(b'not really a png')
            argv = ['upscale.py', '--image', source, '--out', os.path.join(tmp, 'hero_2x.png'),
                    '--timeout', '6']
            with mock.patch.object(upscale, 'COMFY_INPUT', os.path.join(tmp, 'comfy-input')):
                exception = self.run_until_timeout(upscale, argv, clock, polls, poll_cost=4.0)

        self.assert_budget_kept(exception, clock, polls, budget=6.0)


class UpscaleInputFileTests(unittest.TestCase):
    def test_input_name_is_unique_and_stays_a_bare_filename(self):
        first = upscale.input_filename(os.path.join('out', 'hero.png'))
        second = upscale.input_filename(os.path.join('projekt', 'hero.png'))

        self.assertNotEqual(first, second)
        for name in (first, second):
            self.assertTrue(name.startswith('upscale_src_'), name)
            self.assertTrue(name.endswith('hero.png'), name)
            self.assertEqual(os.path.basename(name), name, 'no path segment may leak into the name')

    def test_two_runs_with_the_same_basename_keep_separate_input_files(self):
        # The input folder is shared by every run and by the ComfyUI instance itself. Two
        # images called hero.png used to end up as the same file there, so the second run
        # overwrote the input of the first one while that was still working on it.
        # Measured while the prompt is queued, because every run now removes its copy again:
        # after the run there is nothing left to compare, during it there is.
        with tempfile.TemporaryDirectory() as tmp:
            comfy_input = os.path.join(tmp, 'comfy-input')
            staged = []
            for folder in ('out', 'projekt'):
                source = os.path.join(tmp, folder, 'hero.png')
                os.makedirs(os.path.dirname(source))
                with open(source, 'wb') as fh:
                    fh.write(folder.encode())

                argv = ['upscale.py', '--image', source,
                        '--out', os.path.join(tmp, folder + '_2x.png'), '--timeout', '6']
                api = stub_api(FAILED_HISTORY_ENTRY, [],
                               on_prompt=lambda: staged.append(staged_inputs(comfy_input)))
                with mock.patch.object(upscale, 'api', api), \
                        mock.patch.object(upscale, 'COMFY_INPUT', comfy_input), \
                        mock.patch.object(sys, 'argv', argv), \
                        contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        upscale.main()

            self.assertEqual([len(snapshot) for snapshot in staged], [1, 1])
            (first_name, first_bytes), (second_name, second_bytes) = (
                next(iter(snapshot.items())) for snapshot in staged
            )
            self.assertNotEqual(first_name, second_name,
                                'the second run must not reuse the input file name of the first')
            self.assertEqual([first_bytes, second_bytes], [b'out', b'projekt'])


class UpscaleInputDirTests(unittest.TestCase):
    """The staging folder has to belong to the ComfyUI behind --url, not to this machine."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        self.source = os.path.join(self.tmp, 'hero.png')
        with open(self.source, 'wb') as fh:
            fh.write(b'not really a png')
        self.local_input = os.path.join(self.tmp, 'local-comfy-input')

    def run_main(self, argv, staged, watch=None):
        # Snapshot taken while the prompt is queued: that is the only window in which a run's
        # copy exists, every path removes it again.
        folder = watch or self.local_input
        api = stub_api(FAILED_HISTORY_ENTRY, [],
                       on_prompt=lambda: staged.append(staged_inputs(folder)))
        with mock.patch.object(upscale, 'api', api), \
                mock.patch.object(upscale, 'COMFY_INPUT', self.local_input), \
                mock.patch.object(sys, 'argv', argv), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                upscale.main()
        return raised.exception

    def test_refuses_a_remote_url_without_an_input_dir(self):
        # The old code copied into the local folder no matter what --url said. The remote
        # server never saw the file, so the run only ever ended in its 1200s timeout.
        staged = []
        exception = self.run_main(
            ['upscale.py', '--image', self.source, '--out', os.path.join(self.tmp, 'o.png'),
             '--url', 'http://gpu-box:8188', '--timeout', '6'],
            staged,
        )

        self.assertIn('--input-dir', str(exception))
        self.assertEqual(staged, [], 'no prompt may be submitted for a folder the server cannot read')
        self.assertFalse(os.path.exists(self.local_input),
                         'nothing may be staged into the local folder for a remote instance')

    def test_input_dir_lets_a_remote_url_stage_where_the_server_reads(self):
        remote_input = os.path.join(self.tmp, 'mounted-comfy-input')
        staged = []
        self.run_main(
            ['upscale.py', '--image', self.source, '--out', os.path.join(self.tmp, 'o.png'),
             '--url', 'http://gpu-box:8188', '--input-dir', remote_input, '--timeout', '6'],
            staged, watch=remote_input,
        )

        self.assertEqual([len(snapshot) for snapshot in staged], [1],
                         'the copy has to land in the folder --input-dir names')
        self.assertFalse(os.path.exists(self.local_input), 'the local default must stay untouched')

    def test_a_local_url_still_uses_the_installation_default(self):
        staged = []
        self.run_main(
            ['upscale.py', '--image', self.source, '--out', os.path.join(self.tmp, 'o.png'),
             '--timeout', '6'],
            staged,
        )

        self.assertEqual([len(snapshot) for snapshot in staged], [1],
                         'the default path must keep staging into COMFY_INPUT')


class UpscaleInputCleanupTests(unittest.TestCase):
    """The copy in the shared input folder belongs to one run and must not outlive it."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = tmp.name
        self.comfy_input = os.path.join(self.tmp, 'comfy-input')
        self.source = os.path.join(self.tmp, 'hero.png')
        with open(self.source, 'wb') as fh:
            fh.write(b'not really a png')
        self.out = os.path.join(self.tmp, 'hero_2x.png')

    @contextlib.contextmanager
    def patched(self, history_entry):
        argv = ['upscale.py', '--image', self.source, '--out', self.out, '--timeout', '6']
        with mock.patch.object(upscale, 'api', stub_api(history_entry, [])), \
                mock.patch.object(upscale, 'COMFY_INPUT', self.comfy_input), \
                mock.patch.object(upscale, 'download', fake_download), \
                mock.patch.object(sys, 'argv', argv), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            yield

    def test_removes_the_copy_after_a_successful_run(self):
        with self.patched(SUCCESS_HISTORY_ENTRY):
            upscale.main()

        self.assertTrue(os.path.exists(self.out), 'the run must have produced its output')
        self.assertEqual(os.listdir(self.comfy_input), [],
                         'a finished run leaves nothing behind in the shared input folder')

    def test_removes_the_copy_when_comfyui_reports_an_error(self):
        with self.patched(FAILED_HISTORY_ENTRY):
            with self.assertRaises(SystemExit):
                upscale.main()

        self.assertEqual(os.listdir(self.comfy_input), [],
                         'the error path must clean up too, it is the one that repeats')

    def test_keeps_the_copy_when_the_run_times_out(self):
        # A timeout says nothing about the job: it can still be sitting in ComfyUI's queue,
        # and ComfyUI opens the input only once it starts. Removing the copy here made the
        # queued job fail later in LoadImage and threw the GPU work away.
        clock = FakeClock()
        with self.patched(QUEUED_HISTORY_ENTRY), mock.patch.object(upscale, 'time', clock):
            with self.assertRaises(SystemExit) as raised:
                upscale.main()

        staged = os.listdir(self.comfy_input)
        self.assertEqual(len(staged), 1, 'the queued job still needs its input image')
        self.assertIn(staged[0], str(raised.exception),
                      'the timeout message must name the file it deliberately left behind')


if __name__ == '__main__':
    unittest.main()
