# `setup.py`

## `fix_doc` · *function*

## Summary:
Removes any text block delimited by the literal markers ".. PYPI-BEGIN" and "PYPI-END" from the provided text and returns the cleaned string.

## Description:
Typical callers:
- Intended to be used from packaging scripts (for example, within the same setup.py) to sanitize a project's long description before passing it to packaging tools or publishing tools. The typical trigger is preparing README or long-description content that contains sections intended for local distribution only and must be removed for PyPI.

Responsibility boundary:
- Encapsulates the single responsibility of removing one or more literal marker-delimited regions from a text blob. It is small and isolated so the setup/packaging code can call a simple function rather than inline a regex each time. This keeps the transformation consistent and testable.

## Args:
    txt (str): The input text to process. Must be a Python str (Unicode text). The function treats the input as plain text and will not interpret bytes; passing non-str values will raise a TypeError.

Notes on parameter behavior:
- The markers are matched literally and case-sensitively. Leading/trailing whitespace around the markers is significant and will be considered part of the matched region only if it is within the marker boundaries.
- The function supports multiple marker-delimited blocks; all non-overlapping occurrences are removed.

## Returns:
    str: A new string derived from the input with every substring that starts with the literal sequence ".. PYPI-BEGIN" and ends at the next literal "PYPI-END" removed (including both markers and everything between them). If no markers are present, the returned value equals the input.

Possible return-value scenarios:
- If the input contains one or more complete marker pairs, those blocks are removed and the rest of the text is preserved in original order.
- If marker pairs are absent, the input is returned unchanged.
- If a start marker exists without a corresponding end marker later in the text, no removal occurs for that unmatched region because the pattern requires a closing "PYPI-END" to match.

## Raises:
    TypeError: If txt is not a str. The underlying substitution operation expects a text string; passing e.g. None or a non-string object will raise a TypeError.

(There are no other explicit exceptions thrown by this function in normal operation because the regex pattern is constant and valid.)

## Constraints:
Preconditions:
- Caller must provide a valid Python str for txt.
- The markers must be the literal sequences ".. PYPI-BEGIN" and "PYPI-END"; the function does not accept alternative marker names.

Postconditions:
- The returned string contains no substrings that match the full marker-delimited pattern described above.
- The original input object is not modified; a new string is produced.

Behavioral notes and edge cases:
- Matching is case-sensitive.
- The pattern uses a non-greedy match and is applied globally: multiple non-overlapping blocks are removed.
- Because of the non-greedy semantics, when multiple start/end pairs are present, each minimal matching pair is removed rather than one large span between the first start and the last end.
- The pattern spans newlines, so blocks that include line breaks are removed entirely.
- Overlapping marker pairs (e.g., nested markers) are resolved according to the regex engine's non-overlapping matching rules; nesting is not specially supported.

## Side Effects:
- None. The function performs pure text transformation in memory and does not perform any I/O, mutate external state, write files, print to stdout, or call external services.

## Control Flow:
flowchart TD
    Start --> ValidateInput
    ValidateInput{Is txt a str?}
    ValidateInput -- No --> RaiseTypeError[Raise TypeError]
    ValidateInput -- Yes --> PerformSubstitution[Run regex substitution across txt]
    PerformSubstitution --> ReturnResult[Return cleaned string]
    ReturnResult --> End

## Examples:
- Example (single block removed):
    Input: "Intro\n.. PYPI-BEGIN\ninternal notes\nPYPI-END\nConclusion"
    Output: "Intro\n\nConclusion"
- Example (multiple blocks removed):
    Input: "A\n.. PYPI-BEGIN\nsecret1\nPYPI-END\nB\n.. PYPI-BEGIN\nsecret2\nPYPI-END\nC"
    Output: "A\n\nB\n\nC"
- Example (no markers present):
    Input: "Public README content"
    Output: "Public README content"
- Example (invalid input handling):
    If a non-string value is supplied (for example, None), the function raises a TypeError; callers should validate or convert inputs to str before calling if necessary.

