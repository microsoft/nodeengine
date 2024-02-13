# Troubleshooting

While we do our best to announce changes to our codebase and environment, this project is in a constant and rapid state of flux. Below are some errors that have arisen over time and how they may be resolved.

### ERROR: Error importing module '\<MODULE>': cannot import name '\<MODULE>' from '\<PACKAGE>' ...

It appears a package is not installed properly.  Requirements may have changed.

- Follow `pip install...` step in [README.md#quickstart](../README.md#quickstart) again

### ERROR: Package 'node-engine' requires a different Python: 3.10.9 not in '3.12,>=3.11'

Python 3.11 is required.

- Install the latest 3.11 version of Python
    - Windows: https://www.python.org/downloads/windows/
- Delete any existing `.venv` directory`
- Follow `venv` and `pip` related steps in [README.md#quickstart](../README.md#quickstart) again
