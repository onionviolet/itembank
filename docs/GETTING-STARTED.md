<!-- generated-by: gsd-doc-writer -->
# Getting started

## Prerequisites

- Git
- Python 3.11 or a compatible newer Python 3 release
- Node.js 20 only when running the JavaScript editor tests

The core CLI has no installation step and uses the Python standard library.

## Installation steps

1. Clone the private repository after the owner grants access.

   ```bash
   git clone https://github.com/onionviolet/itembank.git
   cd itembank
   ```

2. Confirm the CLI contract.

   ```bash
   python itembank.py spec
   ```

3. Run the fast contributor gates.

   ```bash
   python scripts/preflight.py --quick
   ```

## First run

Build the synthetic sample bank into an offline quiz:

```bash
python itembank.py build fixtures/sample_bank.md /tmp/itembank-sample.html
```

Do not use a real question bank inside the repository.

## Common setup issues

- On Windows, use `python` from the standard python.org installer. If your environment exposes only `python3`, substitute it in the commands.
- The full preflight installs JavaScript packages under `tests/js/`. Use `python scripts/preflight.py --quick` when Node.js is unavailable.
- A private clone returns an authentication error until the repository owner adds your GitHub account.

## Next steps

Read [Development](DEVELOPMENT.md), [Testing](TESTING.md), and [Contributing](../CONTRIBUTING.md) before changing code.
