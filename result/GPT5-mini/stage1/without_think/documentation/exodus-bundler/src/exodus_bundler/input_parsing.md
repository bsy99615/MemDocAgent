# `input_parsing.py`

## `src.exodus_bundler.input_parsing.extract_exec_path` · *function*

## Summary:
Extracts and returns the executable path string from a single parsed call-site-like line (e.g., method("path", ...)) after removing an optional "[pid N]" prefix; returns None when no matching pattern is found.

## Description:
This function normalizes a single input line by removing a leading "[pid N]" token (via strip_pid_prefix) and then looks for a leading call expression whose callee is one of the globally-configured exec method names (exec_methods). For the first matching method it expects a substring of the form method("...path...", ...). When that exact pattern is found it extracts and returns the string inside the first pair of opening double-quote and the closing sequence '", '.

Known callers within the provided codebase:
- No direct callers were discovered in the provided repository context. Typical callers would be log- or trace-parsing routines that need to extract the path argument from recorded execution calls (for example, while parsing lines that log execv/execve/exec* invocations).

Why this is a separate function:
- It isolates a small, well-defined parsing responsibility (recognize call-like text and extract the first-argument path) from higher-level parsing logic. Separating this makes the overall parser easier to read, test, and reuse across different input-processing paths where the same call-site extraction is needed.

## Args:
    line (str): A single textual input line to examine. Must be a Python str. The function expects textual input; passing non-str values may raise a TypeError in the dependency (strip_pid_prefix) or in string operations.

Notes on argument interdependencies:
    - The function calls strip_pid_prefix(line) first; therefore the passed value must be acceptable to that function (see its contract: it expects a str).
    - The behavior also depends on the global variable exec_methods: it must be defined and be an iterable of strings (each string is a method name). If exec_methods is missing or contains non-string items, runtime errors may occur.

## Returns:
    str | None

    - If a matching method is found and the remainder of the line after method + '("' contains the substring '", ' (a closing quote followed by a comma and a space), the function returns the characters between the opening quote and that exact '", ' sequence. That value usually represents an executable file path string from the first argument of the call-like text.
    - If a matching method is found but the exact separator '", ' is not present after the opening quote, extraction for that method fails and the function continues checking the next method.
    - If no method in exec_methods matches the start of the (prefix-stripped) line, the function returns None.
    - The returned string may be empty (for example if the call contains an empty string argument: method("", ...)), which is a valid possible result.
    - The function never returns other types.

## Raises:
    - NameError: If the global name exec_methods is not defined at call time, attempting to iterate over it raises a NameError.
    - TypeError: If line is not a str (for example None) then strip_pid_prefix or the subsequent string operations (startswith, slicing) may raise a TypeError.
    - TypeError: If exec_methods is defined but not iterable, or if its items are not strings, concatenation method + '("' will raise a TypeError.
    - Any exceptions raised by strip_pid_prefix are propagated.

## Constraints:
Preconditions:
    - The caller must pass a Python str as line.
    - The global exec_methods must be defined and be an iterable of str method names (e.g., ["execv", "execve"]).
    - The intended input format is a line that begins (after optional "[pid N]" removal) with a method name immediately followed by an opening parenthesis and a double-quote, e.g., method("...

Postconditions:
    - If the function returns a str, that string is the exact substring that appeared between the first opening double-quote after the matched method prefix and the subsequent '", ' sequence.
    - If the function returns None, no matching method call pattern (with the expected separator '", ') was found at the start of the normalized line.

## Side Effects:
    - None observable: the function performs no I/O, does not mutate global state, and only calls strip_pid_prefix (a pure string transformation).
    - It relies on the global exec_methods value but does not modify it.

## Control Flow:
flowchart TD
    A[Start: call extract_exec_path(line)] --> B[Call strip_pid_prefix(line)]
    B --> C{For each method in exec_methods}
    C --> D[Compute prefix = method + '("']
    D --> E{line.startswith(prefix)?}
    E -- no --> C
    E -- yes --> F[Remove prefix: line = line[len(prefix):]]
    F --> G[parts = line.split('", ')]
    G --> H{len(parts) > 1 ?}
    H -- yes --> I[Return parts[0]]
    H -- no --> C
    C --> J[End of methods] --> K[Return None]

## Examples:
1) Typical successful extraction
    input: '[pid 12] execv("/usr/bin/python", ["python", "script.py"])'
    precondition: exec_methods contains 'execv'
    result: '/usr/bin/python'

2) Successful extraction without pid prefix
    input: 'execv("/bin/ls", ["ls", "-la"])'
    precondition: exec_methods contains 'execv'
    result: '/bin/ls'

3) No match because different separator
    input: 'execv("/bin/ls")'  (no comma+space after the closing quote)
    result: None  (the function only recognizes the exact sequence '", ' after the closing quote)

4) No match because method not in exec_methods
    input: 'spawn("/sbin/daemon", ...)'
    precondition: exec_methods does not contain 'spawn'
    result: None

5) Edge-case: empty first argument
    input: 'execv("", ["arg"])'
    precondition: exec_methods contains 'execv'
    result: ''  (empty string is returned)

6) Runtime error when exec_methods missing
    input: 'execv("/bin/ls", ["ls"])'
    precondition: exec_methods is not defined
    behavior: NameError is raised when attempting to iterate exec_methods

Implementation notes for reimplementers:
    - strip_pid_prefix must be called first and should accept the incoming line type.
    - The function must iterate exec_methods in order and stop at the first successful extraction.
    - Matching is literal and sensitive to exact characters and spacing: it requires method + '("' at the start and '", ' (quote, comma, space) as the separator after the closing quote.
    - The function intentionally does not attempt to unescape quoted characters, handle nested quotes, or parse arbitrary argument lists — it performs a simple textual extraction suitable for predictable log formats.

## `src.exodus_bundler.input_parsing.extract_open_path` · *function*

## Summary:
Extracts the file path token from a strace-style open/openat syscall line when the line text contains O_RDONLY and does not contain ENOENT or O_DIRECTORY; returns None otherwise.

## Description:
This helper parses a single textual syscall trace line (for example, output produced by strace) and attempts to return the path argument that appears between the first pair of quotes after an open/openat prefix. It first normalizes the input by removing an optional leading "[pid N]" prefix using strip_pid_prefix, then checks for one of two prefixes and applies a set of textual filters.

Known callers within the provided codebase:
- No direct callers were discovered in the provided snapshot. Typical callers are functions in an input-parsing pipeline that scan syscall trace lines to discover which files a traced process attempted to open for read.

Why this logic is extracted:
- The parsing and filtering rules for open/openat lines are compact but used in multiple places when extracting candidate file paths from textual traces. Centralizing this logic improves clarity and avoids duplicating the exact substring checks across the parsing pipeline.

## Args:
    line (str): A single syscall trace line. Expected format examples:
        - 'open("/path/to/file", O_RDONLY|O_CLOEXEC) = 3'
        - '[pid 123] openat(AT_FDCWD, "/path", O_RDONLY) = 4'
    Notes:
        - The function will call strip_pid_prefix(line) first; callers should pass a str. Passing non-str values (e.g., None) may cause a TypeError from strip_pid_prefix or from subsequent string operations.
        - Matching is case-sensitive and relies on the exact substrings used in common strace output.

## Returns:
    str | None:
    - Returns the exact path substring (as a str) that appears between the opening quote and the closing quote immediately following a supported prefix, when all textual checks pass:
        * After pid-stripping, the line must start with one of:
            - 'openat(AT_FDCWD, "'
            - 'open("'
        * The remainder after the prefix must split into exactly two parts using the separator '", ' (i.e., parts = remainder.split('", '), expecting len(parts) == 2).
        * The second part (flags/result text) must contain 'O_RDONLY'.
        * The second part must not contain 'ENOENT'.
        * The second part must not contain 'O_DIRECTORY'.
    - Returns None if any of the above conditions are not met (unsupported prefix, malformed format, missing O_RDONLY, presence of ENOENT, presence of O_DIRECTORY).
    - Important: The function does NOT parse or verify the syscall return value. It may return a path even if the syscall ultimately failed with an error other than ENOENT (e.g., EACCES) because only the textual checks above are applied.

## Raises:
    - No exceptions are explicitly raised by the function itself.
    - Indirect exceptions:
        * If `line` is not a str, strip_pid_prefix or the string operations may raise TypeError. Callers must ensure textual input.

## Constraints:
Preconditions:
    - The caller must supply a Python str containing the syscall trace text.
    - The input should use the typical strace formatting: a quoted pathname followed by '", ' then flags and possibly the return value/error text.

Postconditions:
    - If a non-None value is returned, it is the exact substring that was between the quotes after the recognized prefix.
    - The function does not modify external state.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state. It only calls the pure function strip_pid_prefix.

## Control Flow:
flowchart TD
    Start([start]) --> Strip[Call strip_pid_prefix(line)]
    Strip --> CheckPrefix{starts with 'openat(AT_FDCWD, "' or 'open("'}
    CheckPrefix -- no --> ReturnNone1[return None]
    CheckPrefix -- yes --> Split[remainder = line[len(prefix):]; parts = remainder.split('", ')]
    Split --> PartsLen{len(parts) == 2?}
    PartsLen -- no --> ReturnNone2[try next prefix or return None]
    PartsLen -- yes --> CheckENOENT{ 'ENOENT' in parts[1]? }
    CheckENOENT -- yes --> ReturnNone3[try next prefix or return None]
    CheckENOENT -- no --> CheckO_RDONLY{ 'O_RDONLY' in parts[1]? }
    CheckO_RDONLY -- no --> ReturnNone4[try next prefix or return None]
    CheckO_RDONLY -- yes --> CheckODIR{ 'O_DIRECTORY' in parts[1]? }
    CheckODIR -- yes --> ReturnNone5[try next prefix or return None]
    CheckODIR -- no --> ReturnPath[return parts[0]]
    ReturnPath --> End([end])

## Examples:
1) Extracted when O_RDONLY present:
    input: 'open("/etc/hosts", O_RDONLY|O_CLOEXEC) = 3'
    output: '/etc/hosts'
    note: The function does not inspect the numeric return value; it only checked that 'O_RDONLY' appears and no excluded substrings are present.

2) Extracted after pid prefix removal:
    input: '[pid 123] openat(AT_FDCWD, "/var/log/app.log", O_RDONLY) = 4'
    output: '/var/log/app.log'

3) Not extracted: ENOENT present in result text
    input: 'open("/nonexistent", O_RDONLY) = -1 ENOENT (No such file or directory)'
    output: None

4) Not extracted: not read-only
    input: 'open("/tmp/data", O_WRONLY|O_CREAT) = 3'
    output: None

5) Not extracted: O_DIRECTORY present
    input: 'open("/etc", O_RDONLY|O_DIRECTORY) = 3'
    output: None

6) Edge case — other error present (function will still extract because only ENOENT is excluded):
    input: 'open("/secret", O_RDONLY) = -1 EACCES (Permission denied)'
    output: '/secret'
    note: This demonstrates that callers should not assume a returned path means the syscall succeeded; the function only applies textual filters described above.

## `src.exodus_bundler.input_parsing.extract_stat_path` · *function*

## Summary:
Extracts and returns the file path argument from a stat(...) call text if the line contains a successful stat invocation; otherwise returns None.

## Description:
Parses a single normalized log or trace line to detect a pattern of the form stat("...path...", ...). If the line begins with a process-id prefix like "[pid N]" that prefix is removed first (via strip_pid_prefix) before parsing. This function returns the extracted path only for stat calls that look syntactically complete and do not indicate an ENOENT (file-not-found) error in the remainder of the text.

Known callers within the codebase:
- No specific call sites were discovered in the provided repository context. Typical callers are higher-level input-parsing routines that scan syscall traces or logs (for example, processing strace-like output) and wish to collect paths that were passed to stat().

Why this logic is extracted:
- Isolating the extraction of a stat() path encapsulates the small, well-defined responsibility of recognizing and pulling out a path argument from a single line. This keeps tracing/log parsing logic simple and reusable (e.g., callers need not repeat pid-prefix stripping, prefix matching, splitting, and ENOENT filtering).

## Args:
    line (str): A single text line to inspect. Expected to be a Python str containing a normalized log/trace entry. The function delegates initial normalization to strip_pid_prefix(line) and therefore expects textual input; passing non-str values (e.g., None) may raise a TypeError upstream in strip_pid_prefix or during str operations.

## Returns:
    str or None:
    - str: The raw path substring extracted from inside the first stat("...") argument when all of these are true:
        * After removing an optional leading "[pid N]" prefix, the line starts with the literal prefix stat(".
        * The substring after stat(" contains a closing '", ' sequence such that splitting on '", ' yields exactly two parts (the path part and the remainder).
        * The remainder (the second part after splitting) does not contain the substring 'ENOENT'.
      The returned string is the path portion exactly as it appears between the opening quote after stat( and the closing quote before the comma; it is not unescaped or normalized further.
    - None: Returned when any of the above conditions is not met, specifically:
        * The (pid-stripped) line does not start with stat(",
        * The split on '", ' does not produce exactly two pieces,
        * The remainder contains 'ENOENT' (indicating a missing file or an error),
        * Or when the input is malformed relative to the expected pattern.

## Raises:
    - This function itself does not explicitly raise exceptions. However, the following runtime errors may occur due to improper inputs:
        * TypeError (or other exceptions raised by strip_pid_prefix): if `line` is not a str and strip_pid_prefix uses regex functions or string operations that expect str.
    Callers should pass validated strings to avoid these errors.

## Constraints:
Preconditions:
    - Caller should pass a Python str representing a single line of trace/log text.
    - Lines intended for successful extraction should conform to the pattern:
      optional leading "[pid N]" prefix (handled by strip_pid_prefix), followed immediately by stat("PATH", <rest>).
Postconditions:
    - If a non-None value is returned, it is a str representing the exact PATH substring between the opening stat(" and the closing ", sequence.
    - The function has no side effects and does not mutate its input.

## Side Effects:
    - None. The function performs no I/O, does not modify global state, and does not call external services. It only calls strip_pid_prefix (a pure text transformation) and performs string operations.

## Control Flow:
flowchart TD
    Start --> A[Call strip_pid_prefix(line)]
    A --> B{line.startswith('stat("')}
    B -- No --> ReturnNone1[Return None]
    B -- Yes --> C[rest = line[len('stat("'):]]
    C --> D[parts = rest.split('", ')]
    D --> E{len(parts) == 2}
    E -- No --> ReturnNone2[Return None]
    E -- Yes --> F{ 'ENOENT' in parts[1] }
    F -- Yes --> ReturnNone3[Return None]
    F -- No --> ReturnPath[Return parts[0]]

## Examples:
1) Successful extraction
    input: 'stat("/etc/hosts", 0) = 0'
    output: '/etc/hosts'

2) With leading pid prefix (stripped first)
    input: '[pid 42] stat("/var/log/app.log", 0) = 0'
    output: '/var/log/app.log'

3) ENOENT present (treated as failure)
    input: 'stat("/nonexistent", -1) = -1 ENOENT (No such file or directory)'
    output: None

4) Malformed stat invocation (no closing '", ')
    input: 'stat("/incomplete_path" )'
    output: None

5) Non-string input (caller must guard)
    input: None
    behavior: May raise TypeError in strip_pid_prefix or during string operations; callers should validate before calling.

Notes:
- The function does not attempt to unescape or normalize quoted characters inside the extracted path; it returns the raw substring found between the quotes.
- The split uses the exact sequence '", ' (quote, comma, space). Variations (e.g., '",' without space) will cause the function to return None.

## `src.exodus_bundler.input_parsing.extract_paths` · *function*

## Summary:
Extracts file path candidates from an input text blob that contains strace-style lines; when the input appears to be strace output (detected by examining the first non-empty line) the function returns a deduplicated list of extracted paths (optionally filtered to existing, readable non-directory files). If the input does not look like strace output the function returns the normalized non-empty input lines.

## Description:
- Known callers:
    - No direct callers were discovered in the provided repository snapshot. Typical callers are higher-level trace/log parsing or bundling code that provides the text output of strace (or similar) and needs to collect file paths that the traced process executed, opened for read, or stat()ed.
    - Common usage pattern: pass the full text content of a trace/log file to extract_paths during an input-parsing stage to obtain candidate file paths for further processing (e.g., bundling, analysis).

- Why this is a separate function:
    - It centralizes the orchestration of several small, focused extractors (extract_exec_path, extract_open_path, extract_stat_path), deduplication, blacklist filtering, and optional filesystem validation into one predictable unit. Keeping this logic separate prevents duplication and makes it easy to test "path extraction from a block of trace text" as a single step in the pipeline.

## Args:
    content (str):
        - The entire textual input to parse. Typical value is the content of a strace-style log or other trace output.
        - The function calls content.splitlines() and performs strip() on each line, so the input must support splitlines() (a Python str is expected). Passing None or other inappropriate types may raise a TypeError or AttributeError.
    existing_only (bool, default=True):
        - If True, only include candidate paths that pass on-disk checks: os.path.exists(path) is True, os.access(path, os.R_OK) is True, and os.path.isdir(path) is False.
        - If False, include candidate paths found by the extractors regardless of whether they currently exist on disk.
        - Interdependencies: when existing_only is True the function performs filesystem queries; when False it only applies textual and blacklist filters.

## Returns:
    list[str]:
    - When the input contains no non-empty lines:
        * Returns an empty list (the normalized lines list).
    - When the first non-empty line is not recognized as an "exec" call by extract_exec_path (i.e., the function determines the input is not strace-like):
        * Returns the list of non-empty, stripped lines (list of strings). This is the normalized input lines, not extracted path candidates.
    - When the input is recognized as strace/log-style (determined by extract_exec_path(lines[0]) is not None):
        * Returns a list of deduplicated path strings discovered by scanning every non-empty line with the helper extractors in this order:
            1. extract_exec_path(line)
            2. extract_open_path(line)
            3. extract_stat_path(line)
          The first non-None result is taken as the candidate for that line.
        * Candidate strings that start with any prefix in the global blacklisted_directories are excluded.
        * If existing_only is True, only candidates passing the filesystem checks (exists, readable, not a directory) are included.
        * Deduplication is performed using a set, so the returned list has no duplicate paths. The ordering of paths in the returned list is not guaranteed (set iteration order is arbitrary).
    - Edge-case return values:
        * If none of the extractors find a valid path in strace mode, the returned list will be empty.
        * The function always returns a list of strings in all code paths.

## Raises:
    - TypeError / AttributeError:
        * If `content` is not a str-like object the initial content.splitlines() or subsequent string operations may raise AttributeError or TypeError.
        * If the helper extractors (extract_exec_path, extract_open_path, extract_stat_path) expect str inputs and receive non-str values, they may raise TypeError; those errors propagate.
    - NameError:
        * If any of the global symbols referenced are not defined at runtime — for example extract_exec_path, extract_open_path, extract_stat_path, or blacklisted_directories — a NameError will be raised when the function attempts to use them.
    - TypeError:
        * If blacklisted_directories exists but is not an iterable of strings, evaluating path.startswith(directory) may raise a TypeError. The function assumes blacklisted_directories is an iterable of str prefixes.
    - No other exceptions are explicitly raised by this function; filesystem checks (os.path.exists, os.access) are expected to behave according to the standard os module semantics and may raise OSError in extremely unusual environments (these exceptions are not explicitly handled and will propagate).

## Constraints:
- Preconditions:
    - The caller should pass a Python str (or similar with splitlines()) as content.
    - The global helper functions extract_exec_path, extract_open_path, extract_stat_path must be available and accept a single string argument, returning either a path string or None.
    - The global blacklisted_directories must be defined and be an iterable of string directory prefixes (e.g., ['/dev', '/proc']) to be used in prefix filtering.
- Postconditions:
    - The function returns a list of strings (either normalized input lines or extracted path candidates).
    - When strace-mode is active and existing_only=True, every returned path satisfies:
        * os.path.exists(path) is True
        * os.access(path, os.R_OK) is True
        * os.path.isdir(path) is False
    - The returned list contains unique values (duplicates removed). No ordering guarantees are provided.

## Side Effects:
- Filesystem queries:
    - The function calls os.path.exists(path) and os.access(path, os.R_OK) when existing_only is True. These are read-only checks but perform system calls (no file mutation).
- No I/O such as writing files, network calls, or stdout/stderr printing occurs.
- No global variables are modified by this function. It only reads globals (helpers and blacklisted_directories).

## Control Flow:
flowchart TD
    Start([Start]) --> Normalize[Normalize input: lines = non-empty stripped lines]
    Normalize --> EmptyCheck{len(lines) == 0?}
    EmptyCheck -- Yes --> ReturnEmpty[Return lines (empty list)]
    EmptyCheck -- No --> StraceCheck{strace_mode = extract_exec_path(lines[0]) is not None}
    StraceCheck -- No --> ReturnLines[Return lines (normalized non-empty lines)]
    StraceCheck -- Yes --> ForEach[For each line in lines]
    ForEach --> Extract[Call extract_exec_path(line) or extract_open_path(line) or extract_stat_path(line)]
    Extract --> PathFound{path is not None?}
    PathFound -- No --> NextLine[continue loop]
    PathFound -- Yes --> BlacklistCheck{any(path.startswith(dir) for dir in blacklisted_directories)?}
    BlacklistCheck -- Yes --> NextLine
    BlacklistCheck -- No --> ExistingOnlyCheck{existing_only?}
    ExistingOnlyCheck -- No --> AddPath[add path to set; continue]
    ExistingOnlyCheck -- Yes --> FSChecks{os.path.exists(path) and os.access(path,os.R_OK) and not os.path.isdir(path)?}
    FSChecks -- True --> AddPath
    FSChecks -- False --> NextLine
    NextLine --> ForEach
    AddPath --> ForEach
    ForEach --> End[Return list(paths) (deduplicated, order undefined)]

## Examples:
1) Empty input
    - input content: "" (empty string)
    - result: [] (empty list)

2) Non-strace input (first non-empty line not recognized as exec call)
    - input content:
        "This is a simple text file\nAnother line\n"
    - result: ["This is a simple text file", "Another line"] (normalized non-empty lines)

3) Strace input — existing_only=True (default)
    - assumptions:
        * extract_exec_path/open/stat extract paths from lines like 'execv("/usr/bin/cmd", ...)', 'open("/etc/hosts", O_RDONLY, ...)', 'stat("/etc/hosts", ...)' respectively.
        * blacklisted_directories contains ['/proc', '/dev'].
        * The file '/etc/hosts' exists and is readable; '/tmp/unreadable' exists but is not readable; '/nonexistent' does not exist.
    - input content (multiline strace-style):
        '[pid 1] execv("/bin/app", ["app"])'
        'open("/etc/hosts", O_RDONLY) = 3'
        'open("/tmp/unreadable", O_RDONLY) = -1 EACCES (Permission denied)'
        'stat("/nonexistent", 0) = -1 ENOENT (No such file or directory)'
        'open("/proc/self/status", O_RDONLY) = 3'
    - behavior:
        * '/bin/app' and '/etc/hosts' are candidate paths.
        * '/tmp/unreadable' fails the os.access(..., R_OK) check and is excluded when existing_only=True.
        * '/nonexistent' does not exist and is excluded.
        * '/proc/self/status' is excluded due to blacklist prefix '/proc'.
    - result (order undefined): e.g. ['/bin/app', '/etc/hosts']

4) Strace input — existing_only=False (include non-existent candidates)
    - same input as (3) but existing_only=False
    - result (duplicates removed, order undefined): e.g. ['/bin/app', '/etc/hosts', '/tmp/unreadable', '/nonexistent']
    - note: blacklist filtering still applies; blacklisted prefixes are excluded even when existing_only=False.

Implementation notes for reimplementers:
- Treat the first non-empty, stripped line as the signal for whether the input is strace-like: call extract_exec_path(lines[0]) and check for non-None.
- Use the helper extractors in the specific order (exec, open, stat) and take the first non-None return as the path candidate per line.
- Apply prefix blacklist filtering with any(path.startswith(directory) for directory in blacklisted_directories).
- Use a set to deduplicate found paths; return list(paths) (no ordering guarantee).
- When existing_only is True, perform filesystem checks exactly as in the original: os.path.exists(path) and os.access(path, os.R_OK) and not os.path.isdir(path).

## `src.exodus_bundler.input_parsing.strip_pid_prefix` · *function*

## Summary:
Removes a leading process-id prefix of the form "[pid <digits>]" (with optional trailing whitespace) from the start of a text line, returning the remainder unchanged if no such prefix is present.

## Description:
This function is intended to be used while normalizing or sanitizing log or message lines that may be prefixed with a process id token like "[pid 123]". It detects and strips that prefix only when it appears at the beginning of the input string.

Known callers within the codebase:
- No specific callers are discovered in the provided file context. Typical callers are log-parsing or input-normalization functions that process lines emitted by multi-process systems or libraries that annotate lines with a "[pid N]" prefix.

Why this logic is extracted:
- The responsibility of detecting and removing a "[pid N]" prefix is a small, well-defined transformation that is useful in multiple places where raw lines are normalized before further parsing. Extracting it improves readability and reduces duplication in the parsing pipeline.

## Args:
    line (str): A single text line to inspect and potentially strip. Must be a Python str (not None). The function expects textual input; passing other types may cause a runtime error from the underlying regex engine.

## Returns:
    str: The input line with a leading "[pid <digits>]" prefix removed, if present. Possible return values:
    - If the input begins with a substring matching the pattern "[pid" followed by at least one whitespace, one or more digits, a closing "]", and any following whitespace (regex: r'\[pid\s+\d+\]\s*'), the returned string is everything after that matched prefix.
    - If the input does not begin with such a prefix, the original input string is returned unchanged.
    - For an empty string input, the empty string is returned.

## Raises:
    This function does not explicitly raise exceptions in its implementation. However:
    - If `line` is not a str (for example, None or an incompatible type), the call into the regex engine (re.match) may raise a TypeError. Callers should pass textual input.

## Constraints:
Preconditions:
    - `line` should be a Python str containing the text to normalize.
    - The function only inspects the start of the string (re.match behavior); leading whitespace or other characters before the bracket will prevent a match.

Postconditions:
    - The returned value is a str.
    - If a prefix matching the pattern exists at the start, the returned string will not contain that prefix; otherwise, it will be identical to the input.

## Side Effects:
    - None. The function performs no I/O and does not mutate external state.

## Control Flow:
flowchart TD
    A[Start: call with line (str)] --> B{re.match(r'\[pid\s+\d+\]\s*', line)}
    B -- match --> C[Compute prefix_len = len(match.group())]
    C --> D[Return line[prefix_len:]]
    B -- no match --> E[Return line]

## Examples:
1) Basic removal
    input: "[pid 123] Hello world"
    output: "Hello world"

2) Multiple spaces between pid and digits
    input: "[pid    42]foo"
    output: "foo"

3) No prefix (unchanged)
    input: "INFO: [pid 5] start"
    note: No removal because the bracketed token is not at the start
    output: "INFO: [pid 5] start"

4) Empty string
    input: ""
    output: ""

5) Non-string input (caller should guard)
    input: None
    behavior: re.match will raise a TypeError; call site should validate or convert input first.

