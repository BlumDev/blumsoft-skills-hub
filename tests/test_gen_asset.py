"""Unit tests for the gen-asset ComfyUI scripts.

No ComfyUI is started or contacted here: the scripts are imported as modules and only
their pure parts are exercised (workflow injection, history parsing, input file naming).
Importing them is side effect free, main() sits behind the __main__ guard.

  python -m unittest tests.test_gen_asset
"""
import argparse
import importlib.util
import json
from pathlib import Path
import unittest


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


if __name__ == '__main__':
    unittest.main()
