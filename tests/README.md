# Test Suites

**synthetic data only, no production credentials, no production services**

## Folder Structure

- `characterization/`: records current behaviour of existing code before it changes
- `unit/`: pure logic
- `contract/`: checks against provider and payment contracts using controlled fakes
- `integration/`: multiple components with real SQLite in temporary folders
- `acceptance/`: end-to-end feature scenarios
- `_harness/`: shared test helpers and fakes

## Running Tests

`.venv/bin/python -m pytest tests --network=deny`

The network guard in `_harness/network_guard.py` is always on, with or without `--network=deny`. A test fails if it opens a socket to anything other than loopback, looks up a host name other than `localhost`, or opens a SQLite file outside pytest's temporary directory for the run (use `tmp_path`).
