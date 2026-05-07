# `scripts`

## Tree:
scripts/
└── generate_identifier_pattern.py

## Role:
Generates a regular expression pattern for validating Python identifier characters by combining standard word characters with special Unicode characters.

## Description:
This module provides functionality to automatically generate a regular expression pattern that accurately matches valid Python identifiers. It identifies Unicode characters that are valid identifier starters but are not matched by the standard `\w` regex pattern, and combines them into a comprehensive identifier validation pattern. This is used as a build-time script to update Jinja2's internal identifier validation logic.

## Components:
- `build_pattern(ranges: list[tuple[str, str]]) -> str`: Constructs a compact string representation of character ranges.
- `collapse_ranges(data: str) -> Generator[tuple[str, str], None, None]`: Groups consecutive characters into ranges based on ASCII values.
- `get_characters() -> Generator[str, None, None]`: Generates Unicode characters that are valid Python identifiers but not word characters.
- `main() -> None`: Main entry point that writes the generated pattern to a Python file.

## Public API:
- `build_pattern(ranges: list[tuple[str, str]]) -> str`
  - Constructs a compact string pattern from a list of character ranges.
  - Usage: Used internally to format character ranges into a regex-compatible string.
- `collapse_ranges(data: str) -> Generator[tuple[str, str], None, None]`
  - Groups consecutive characters into ranges.
  - Usage: Extracts contiguous character sequences from a string.
- `get_characters() -> Generator[str, None, None]`
  - Yields Unicode characters that are valid Python identifiers but not word characters.
  - Usage: Identifies special Unicode characters that extend identifier validity.
- `main() -> None`
  - Generates and writes the final identifier pattern to a file.
  - Usage: Run as a standalone script to update `src/jinja2/_identifier.py`.

## Dependencies:
- `itertools.groupby`: Used in `collapse_ranges` to group consecutive characters.
- `re`: Used in `get_characters` to check regex patterns.
- `sys`: Used in `get_characters` to iterate over Unicode code points.
- `os.path`: Used in `main` to resolve the target file path.

## Constraints:
- Must be run from the `scripts/` directory.
- Target file (`src/jinja2/_identifier.py`) must be writable.
- Assumes standard Python identifier rules and Unicode support.
- All character ranges must consist of valid ASCII characters.

---

## Files

- [`generate_identifier_pattern.py`](scripts/generate_identifier_pattern.md)

