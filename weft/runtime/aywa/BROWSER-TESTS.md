# Telemetry browser regression

From the repository root:

```sh
python3 -m pip install -r scripts/requirements-browser.txt
python3 -m playwright install chromium
python3 scripts/test_telemetry_browser.py
```

On Linux CI, use `python3 -m playwright install --with-deps chromium` to install
the browser's system dependencies as well. The test uses the Chromium version
paired with the pinned Playwright release. For a preinstalled system browser:

```sh
WEFT_BROWSER_EXECUTABLE=/usr/bin/chromium python3 scripts/test_telemetry_browser.py
```

The test starts its own loopback HTTP server on an available port and closes it
afterward. It loads the actual `WeftLoomEngine` and module worker in Chromium;
there are no mocked workers or external requests. A minimal page isolates the
telemetry path from GPU rendering and third-party widget dependencies.

At both `/` and `/nested/site/`, it checks that a later valid packet arrives
through worker polling, invalid hashes preserve the previous values, HTTP and
empty-response failures appear in the HUD, and a later valid packet recovers.
It also checks the requested endpoint and preservation of existing query
parameters. The 100 ms polling interval is test configuration; the site keeps
its 60-second interval.

This is an integration check for issue #41. It does not establish renderer
performance, production telemetry freshness, or end-to-end publisher identity.
