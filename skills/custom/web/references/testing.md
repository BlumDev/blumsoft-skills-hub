# Browser/E2E testing

Test local web applications by writing native Python Playwright scripts.

A helper script `scripts/with_server.py` manages server lifecycle (one or more servers). Run it with `--help` before using it. Treat bundled scripts as black boxes: invoke them directly, do not read their source, to keep your context clean.

## Choosing an approach

- **Static HTML**: read the HTML file directly to find selectors, then write a Playwright script. If reading is incomplete, treat it as dynamic.
- **Dynamic webapp, server not running**: run `python scripts/with_server.py --help`, then use the helper plus a simplified Playwright script.
- **Dynamic webapp, server running**: do reconnaissance, then act (see below).

## Using with_server.py

Single server:
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

Multiple servers (e.g. backend + frontend):
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

Your automation script holds only Playwright logic; servers are managed for you:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)  # always headless chromium
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')  # CRITICAL: wait for JS to execute
    # ... automation logic
    browser.close()
```

## Reconnaissance, then action

1. Inspect the rendered DOM:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```
2. Identify selectors from what was rendered.
3. Execute actions with the discovered selectors.

Always wait for `networkidle` before inspecting a dynamic app; never inspect the DOM beforehand.

## Best practices

- Use `sync_playwright()` for synchronous scripts.
- Always close the browser when done.
- Use descriptive selectors: `text=`, `role=`, CSS, or IDs.
- Add waits where needed: `page.wait_for_selector()` or `page.wait_for_timeout()`.
