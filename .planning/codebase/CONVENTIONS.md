# Code Conventions

Source: `/home/henrik/dev/henrik/git/firestarter_prom/firestarter_app/firestarter/`

## File Naming

- All Python source files use `snake_case`: `eprom_operations.py`, `serial_comm.py`, `logging_utils.py`, `eprom_info.py`
- Shell test scripts use underscores: `firestarter_test.sh`, `write_test.sh`
- Data files use lowercase with hyphens (JSON): `database_generated.json`, `pin-maps.json`, `database_overrides.json`

## Module Header Pattern

Every Python file begins with a module-level docstring following this template:

```python
"""
Project Name: Firestarter
Copyright (c) 2024/2025 Henrik Olsson

Permission is hereby granted under MIT license.

<Module Description>
"""
```

## Class and Function Naming

- Classes use `PascalCase`: `EpromOperator`, `SerialCommunicator`, `ConfigManager`, `EpromDatabase`, `SingleLineStatusHandler`, `ClassProgressHandler`
- Public functions/methods use `snake_case`: `read_eprom()`, `find_and_connect()`, `build_flags()`
- Private/internal methods prefixed with a single underscore: `_setup_operation()`, `_disconnect_programmer()`, `_run_state_machine()`, `_probe_port()`, `_parse_response_line()`
- Constants use `UPPER_SNAKE_CASE`: `COMMAND_READ`, `FLAG_FORCE`, `BAUD_RATE`, `BUFFER_SIZE`
- Module-level logger always named after the class/module context: `logger = logging.getLogger("EpromOperator")`

## Import Organization

Imports follow PEP 8 grouping (stdlib, then third-party, then local), without explicit blank-line separation enforced by tooling:

```python
# 1. Standard library
import os, time, json, logging, re
from typing import Optional, Tuple
from contextlib import contextmanager

# 2. Third-party
import serial
import tqdm

# 3. Local (relative imports using package name, not relative dots)
from firestarter.constants import *
from firestarter.config import ConfigManager
```

Note: `from firestarter.constants import *` is used widely to pull in all command and flag constants. This is the one place a wildcard import is used intentionally.

## Type Annotations

Type hints are used on method signatures but not universally throughout the codebase. Common patterns:

```python
def method(self, name: str, data: dict, flags: int = 0) -> bool:
def method(self, x: Optional[str] = None) -> Tuple[bool, Optional[int]]:
```

The `Optional`, `Tuple`, `Dict`, `Callable`, `List`, `Generator` types are imported from `typing`.

Union types use the Python 3.10+ `X | Y` syntax in some places despite the `>=3.9` requirement:

```python
self.comm: SerialCommunicator | None = None
```

## Error Handling Patterns

- Custom exception classes inherit from `Exception` or from a project-level base exception:
  - `SerialError(Exception)` - base serial exception
  - `SerialTimeoutError(SerialError)` - timeout subclass
  - `ProgrammerNotFoundError(SerialError)` - no programmer detected
  - `FirmwareOutdatedError(SerialError)` - firmware too old
  - `EpromOperationError(Exception)` - EPROM operation failure
- Exceptions are caught specifically (not bare `except:`), then either re-raised or logged and a falsy return value returned
- Operations that fail typically return `False` (or `(False, None)` for multi-value returns) rather than raising up to the caller
- `IOError` is caught separately for file operations
- `finally:` blocks ensure cleanup (e.g., `_disconnect_programmer()`) always runs

## Logging Approach

- Every module creates a module-level logger:
  ```python
  logger = logging.getLogger("ModuleName")
  ```
- `serial_comm.py` creates a secondary logger for hardware feedback: `rurp_logger = logging.getLogger("RURP")`
- Log levels used consistently:
  - `logger.debug(...)` for internal state, data dumps, timing
  - `logger.info(...)` for user-visible progress and results
  - `logger.warning(...)` for non-fatal issues (checksum note, unexpected responses)
  - `logger.error(...)` for failures (file not found, parse errors, hardware errors)
- F-strings are used exclusively for log message formatting
- A custom `SingleLineStatusHandler` (in `logging_utils.py`) supports overwriting a status line in the terminal using a `status='start'/'end'` extra key
- Logging is configured once in `main.py`; all other modules only create loggers, never configure handlers

## Docstring Style

- Module-level: multi-line `"""..."""` docstrings describing purpose, responsibilities, and key data structures
- Class-level: multi-line docstrings describing purpose and what the class manages
- Function-level: mixed usage. Simple/private methods often have no docstring. Public utility functions use Google-style docstrings with `Args:` and `Returns:` sections:
  ```python
  def extract_hex_to_decimal(input_string):
      """
      Extracts a hexadecimal number from a string and converts it to decimal.

      Args:
          input_string (str): ...
      Returns:
          int: ... or None if not found.
      """
  ```
- Many methods in core operation classes lack docstrings; inline comments are used instead

## Comment Usage

- Inline `#` comments explain non-obvious logic, protocol details, and hardware constraints
- Section dividers used in `main.py` to group CLI argument parsers (no formal region markers)
- TODO-style comments are absent; notes about design intent are left as inline comments
- `# Example usage (for testing this module directly)` blocks appear at the bottom of some modules with a `if __name__ == "__main__":` guard

## Design Patterns

- **Singleton**: `EpromDatabase` and `ConfigManager` use a singleton pattern (instantiated once, reused)
- **Context manager**: `_operation_context()` in `EpromOperator` wraps setup/teardown using `@contextmanager`
- **State machine**: `_run_state_machine()` drives INIT/MAIN/END phases of hardware protocol
- **Named tuple**: `Response = namedtuple('Response', ['type', 'message'])` for structured serial responses
- **Wildcard constants**: All constants from `constants.py` imported with `*` in modules that need them
