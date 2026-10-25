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

`.venv/bin/python -m pytest tests`
