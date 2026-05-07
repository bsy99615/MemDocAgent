# `utils.py`

## `onlinejudge_command.utils.new_session_with_our_user_agent` · *function*

## Summary:
Creates and yields a prepared requests.Session whose User-Agent header contains this package's metadata, and which is wrapped with a cookie-jar context manager that loads/saves cookies at the given filesystem path.

## Description:
This function constructs a new requests.Session, inserts a package-specific User-Agent header, and yields the session while it is wrapped by the cookie-jar context manager provided by onlinejudge.utils.with_cookiejar. The cookie-jarring context manager is responsible for loading cookies from the file at path when entering and persisting them on exit; malformed cookie stores result in an http.cookiejar.LoadError which this function logs and re-raises.

Known callers within the repository snapshot:
- None discovered in the provided snapshot. Typical callers are CLI command handlers or helper routines that need a short-lived HTTP session with persistent cookies for interacting with remote services (for example, inside a "with" block around network operations).

Why this is a separate function:
- Encapsulates three orthogonal responsibilities into one reusable unit: (1) create an isolated requests.Session, (2) ensure the session uses a consistent, package-identifying User-Agent, and (3) attach cookie persistence to a specified file path. Extracting this logic avoids duplication wherever a cookie-backed session with the project User-Agent is required.

Implementation note:
- The function body is a generator that yields a requests.Session and is intended to be used as a context manager (i.e., implemented or exposed via contextlib.contextmanager) so callers can write 'with new_session_with_our_user_agent(path=...) as session: ...'.

## Args:
    path (pathlib.Path):
        Path to the cookie storage file (cookie jar). Expected to be a pathlib.Path object pointing to a file the process can read and write. No default — caller must pass a concrete Path.

## Returns:
    Iterator[requests.Session]:
        A generator-based context manager that yields a configured requests.Session object.
        - The yielded Session has its headers['User-Agent'] set to a string formatted as:
          '{package_name}/{version} (+{url})' where package_name, version and url are taken from
          the package metadata variables referenced in the implementation (version.__package_name__, version.__version__, version.__url__).
        - The session is yielded inside the utils.with_cookiejar(session, path=path) context, so callers are expected to use the function as a context manager; the cookiefile loading/saving lifecycle is handled by that context.

Edge-case return behavior:
- The function yields exactly one Session value to the caller; on normal exit, control returns to context manager exit logic (which ensures the cookie store is persisted). If cookie loading fails, the function does not yield and instead logs and re-raises http.cookiejar.LoadError.

## Raises:
    http.cookiejar.LoadError:
        Raised when the underlying cookie-jar loader (called by utils.with_cookiejar) encounters a malformed or unreadable cookie file. The function logs an informational message (prefixed by the module's HINT constant, if present) advising that the cookie file may be deleted, then re-raises the same LoadError.

    Any exception raised by requests.Session() or by utils.with_cookiejar:
        The function does not catch other exceptions; they propagate to the caller.

## Constraints:
Preconditions:
    - The caller must pass a pathlib.Path object for path.
    - The process must have filesystem permissions to read the cookie file and to write it if changes are saved.
    - onlinejudge.utils.with_cookiejar must be implemented as a context manager that accepts (session, path=...) and may raise http.cookiejar.LoadError on bad cookie files.

Postconditions:
    - If the function yields successfully, the yielded requests.Session has a 'User-Agent' header containing the package metadata.
    - The cookie context opened by utils.with_cookiejar is active while the caller holds the yielded Session; after the context exits, cookie persistence/cleanup is handled by the context manager.

## Side Effects:
    - Potential filesystem I/O through the cookiejar context manager: loading or writing the cookie file at path.
    - Logging side effects:
        - A debug log is emitted with the resolved User-Agent string.
        - If cookie loading fails, an info-level log is emitted suggesting deletion of the broken cookie file (prefixed by HINT if defined in the module).
    - No network operations are performed by this function itself; the returned Session may be used to perform network I/O by the caller.

## Control Flow:
flowchart TD
    Start --> CreateSession[Create requests.Session()]
    CreateSession --> SetUA[Set session.headers['User-Agent']]
    SetUA --> TryWithCookiejar{Enter with_cookiejar(session, path)}
    TryWithCookiejar -->|success| YieldSession[Yield session to caller]
    YieldSession -->|caller exits context| ExitWithCookiejar[Exit cookiejar context (persist cookies)]
    ExitWithCookiejar --> End
    TryWithCookiejar -->|http.cookiejar.LoadError| LogInfo[Log HINT + deletion hint]
    LogInfo --> Reraise[Re-raise LoadError]
    Reraise --> End

## Examples:
Example usage as a context manager (recommended pattern):

    from pathlib import Path
    import contextlib

    cookie_path = Path.home() / '.example_cookie.jar'
    # The function is a generator intended to be exposed as a context manager
    # (e.g. using @contextlib.contextmanager when implemented).
    with new_session_with_our_user_agent(path=cookie_path) as session:
        # session is a requests.Session with 'User-Agent' set
        response = session.get('https://example.com/login')
        # perform authenticated actions that rely on cookies saved at cookie_path

Example with error handling for corrupt cookie jar:

    cookie_path = Path('cookies.jar')
    try:
        with new_session_with_our_user_agent(path=cookie_path) as session:
            # use session
            pass
    except http.cookiejar.LoadError:
        # the function has already logged an informational hint; caller can
        # decide to remove the cookie file and retry
        cookie_path.unlink(missing_ok=True)
        # optionally retry logic here

Notes for reimplementation:
    - Ensure you set the session header exactly as in the implementation using the package metadata attributes referenced (package name, version, url).
    - Implement this function as a generator-based context manager (use @contextlib.contextmanager) or wrap the generator so that callers can use the "with" statement.
    - The behavior and message for http.cookiejar.LoadError should match the original: log an info-level hint that the cookie file can be deleted, then re-raise the original LoadError.

## `onlinejudge_command.utils.textfile` · *function*

## Summary:
Ensure a text string ends with a newline: return the input unchanged if it already ends with '\n'; otherwise append CRLF ("\r\n") if the input contains any CRLF sequences, or append LF ("\n") otherwise. The returned string always ends with '\n' (either as LF or as part of CRLF).

## Description:
A minimal utility to normalize trailing-newline behavior for textual content. Callers should use this function immediately before emitting text (writing to files, sending to subprocesses, or producing textual output) when a trailing newline is required and when preserving an existing CRLF preference in the content is desirable.

Known callers within this module: none found in the provided excerpt. (A repository-wide search was not performed; callers may exist elsewhere in the project.)

Responsibility boundary:
- This function only inspects and returns a string with a guaranteed trailing newline. It performs no encoding/decoding, no I/O, and does not coerce input types. Input validation (e.g., converting bytes to str or handling None) is the caller's responsibility.

## Args:
    s (str): Required. A Python text string (unicode). The function relies on the string methods endswith and the substring membership operator; passing a non-str may raise built-in exceptions.

    Notes on interdependencies:
    - Both checks (s.endswith('\n') and '\r\n' in s) are performed in order; the presence of a trailing '\n' short-circuits the CRLF check.

## Returns:
    str: A text string that is guaranteed to end with '\n'.

    Behavior by input:
    - If s.endswith('\n') is True (this includes strings ending with '\r\n'), the original s is returned unchanged (the same object reference is returned).
    - Else if the substring '\r\n' appears anywhere in s, returns s + '\r\n'.
    - Else returns s + '\n'.

    Examples of result mapping:
    - "" -> "\n"
    - "a" -> "a\n"
    - "a\n" -> "a\n" (returned unchanged)
    - "a\r\n" -> "a\r\n" (returned unchanged)
    - "a\r" -> "a\r\n" (since '\r\n' not present, '\n' appended; result ends with '\r\n')
    - "x\r\ny" -> "x\r\ny\r\n" (CRLF appended because '\r\n' appears somewhere in the content)

## Raises:
    AttributeError:
        - Trigger: If s has no endswith attribute (e.g., s is None or an int), the call s.endswith('\n') raises AttributeError.
    TypeError:
        - Trigger: If s is a different sequence type incompatible with the str-based operations, e.g. bytes:
            * b'abc'.endswith('\n') raises TypeError because bytes.endswith expects a bytes-like argument.
            * '\r\n' in b'abc' raises TypeError because membership checks require operands of compatible types.
    Note: The function does not explicitly validate types; these exceptions are raised by the underlying string operations.

## Constraints:
Preconditions:
    - Caller must pass a Python str. No automatic decoding or coercion is performed.

Postconditions:
    - The return value is a str whose final character is '\n'.
    - If the input already ended with '\n', the returned object is the exact same object reference as the argument (the function returns s).

Performance:
    - Time complexity: O(n) where n is len(s). The membership check for '\r\n' scans the string; endswith performs a constant-time suffix comparison for the final character(s) but overall the function's dominant cost is linear in the length of s.
    - Space complexity: O(1) additional space; if concatenation occurs, a new string of length len(s)+1 or len(s)+2 is allocated as required by Python string immutability.

## Side Effects:
    - None. The function is pure: it does not perform I/O, network calls, or mutate global state.

## Control Flow:
flowchart TD
    A[Start: receive s (expected str)] --> B{s.endswith('\n')?}
    B -- yes --> C[Return s (unchanged)]
    B -- no --> D{'\r\n' in s?}
    D -- yes --> E[Return s + '\r\n']
    D -- no --> F[Return s + '\n']

## Examples:
1) Basic usage before file write:
    s = "result: 42"
    out = textfile(s)           # "result: 42\n"
    with open('out.txt', 'w', encoding='utf-8') as f:
        f.write(out)

2) Preserve CRLF when present in content:
    s = "header\r\nbody"        # contains CRLF internally but no trailing newline
    textfile(s)                 # returns "header\r\nbody\r\n"

3) Trailing '\r' only:
    s = "line\r"
    textfile(s)                 # returns "line\r\n" (appends '\n')

4) Empty string:
    textfile("")                # returns "\n"

5) Handling unexpected types (wrap to provide clearer error):
    def safe_textfile(x):
        if not isinstance(x, str):
            raise TypeError("textfile expects str, got {}".format(type(x).__name__))
        return textfile(x)

    safe_textfile(b"abc")       # raises TypeError with clearer message
    safe_textfile(None)         # raises TypeError with clearer message

## `onlinejudge_command.utils.exec_command` · *function*

## Summary:
Runs an external command (given as a single shell-like string) in a subprocess, captures its stdout as bytes, measures wall-clock elapsed time, optionally measures peak memory via GNU time, and returns a summary dict plus the subprocess.Popen object.

## Description:
This helper centralizes subprocess invocation, timeout handling, platform-specific argument handling (POSIX vs Windows), optional integration with GNU time for peak memory measurement, and cleanup (terminating the process or process group). It is intended for CLI commands and utilities that must run external programs (for example, user-submitted solutions, compilers, or test-runner binaries).

Known callers:
- This function is exported from onlinejudge_command.utils for use by other modules. During documentation generation no concrete callers were discovered inside the local snapshot (a repository-wide search was not performed by this tool). Callers are typically CLI subcommands and test/execution harnesses; to find actual call-sites, search the repository for "exec_command(".

Why this logic is extracted:
- Running external programs reliably requires consistent handling of argument splitting, cross-platform invocation, capturing stdout, forwarding stderr, timeout behavior, process-group cleanup, and optional memory measurement. Extracting these responsibilities into a single function prevents code duplication and ensures consistent semantics across all callers.

## Args:
    command_str (str)
        Shell-like command string to execute. On POSIX the string is split with shlex.split into an argv list; on Windows the original string is passed to Popen (so Windows command-line parsing applies).
    stdin (Optional[BinaryIO], keyword-only, default=None)
        File-like object to attach to the child's stdin. If `input` is provided (see below), this must be None; the function asserts this and sets stdin to a PIPE internally.
    input (Optional[bytes], keyword-only, default=None)
        Bytes to send to the child's stdin via proc.communicate(). If provided, the function sets stdin = subprocess.PIPE automatically and asserts the caller did not supply stdin.
    timeout (Optional[float], keyword-only, default=None)
        Timeout in seconds passed to proc.communicate(). If None, communicate waits indefinitely.
    gnu_time (Optional[str], keyword-only, default=None)
        Path to a GNU `time` executable (e.g., '/usr/bin/time'). When provided the command is wrapped so GNU time writes peak-resident-set-size (format '%M') to a temporary file; that value is parsed and returned in info['memory'] (as megabytes). On POSIX, when gnu_time is used, the function creates a separate process group (via os.setsid) so it can terminate the whole group.

Interdependencies:
- If `input` is not None, `stdin` must be None (the function asserts this and sets stdin to subprocess.PIPE).
- Providing `gnu_time` changes how the command is invoked and enables memory collection; it also affects process-group creation and cleanup on POSIX.

## Returns:
Tuple[Dict[str, Any], subprocess.Popen]
    - info (dict):
        - 'answer' -> Optional[bytes]:
            The stdout captured from the child process as raw bytes. If the child produced no stdout or the function timed out, this will be None. Important: if proc.communicate() raises subprocess.TimeoutExpired, this implementation does not extract partial output from the exception; the function leaves 'answer' as None.
        - 'elapsed' -> float:
            Wall-clock elapsed time in seconds measured using time.perf_counter() from just before launching the subprocess to after communication and termination/cleanup.
        - 'memory' -> Optional[float]:
            Peak memory in megabytes as reported by GNU time (the last numeric line reported by GNU time is treated as kilobytes and divided by 1000 to produce MB). If gnu_time was not provided or output could not be parsed as a trailing integer line, this is None.
    - proc (subprocess.Popen):
        The Popen instance used to run the process. Note that this function attempts to terminate the process (or process group) before returning; proc may therefore refer to a process that has been signaled/terminated.

Possible return scenarios:
- Successful run, no gnu_time: info contains 'answer' (bytes or None), 'elapsed' (float), 'memory' = None.
- Successful run, gnu_time provided and produced parseable output: 'memory' is float (MB).
- communicate timed out: 'answer' remains None, elapsed measures until cleanup, process was requested to terminate.
- Popen failed with FileNotFoundError or PermissionError: function logs an error and exits the Python process (does not return).

## Raises:
    - AssertionError:
        If caller supplies both `stdin` and `input`, the function asserts that stdin is None and raises AssertionError.
    - SystemExit via sys.exit(1):
        When subprocess.Popen raises FileNotFoundError (executable not found), the function logs "No such file or directory: <command>" and calls sys.exit(1).
        When subprocess.Popen raises PermissionError (permission denied), the function logs "Permission denied: <command>" and calls sys.exit(1).
    - Note: subprocess.TimeoutExpired thrown by proc.communicate() is caught internally; the function does not re-raise it.

## Constraints:
Preconditions:
    - command_str should be a valid command string appropriate for the target platform.
    - If `input` is provided, the caller must not set `stdin`.

Postconditions:
    - The returned info dict always contains keys 'answer', 'elapsed', and 'memory'.
    - The function attempts to terminate the child process (or process group on POSIX when using gnu_time) before returning.
    - If gnu_time was used and produced a numeric trailing line, info['memory'] is set to that value in megabytes; otherwise it is None.

## Side Effects:
    - Captures the child's stdout into memory (could be large — callers should avoid invoking with commands that produce unbounded output).
    - Forwards child's stderr directly to the parent's stderr (no capture).
    - When gnu_time is used, creates a temporary file to hold GNU time output; that file is cleaned up by the tempfile context manager.
    - On POSIX with gnu_time, may call os.setsid to create a new process group and os.killpg to send SIGTERM to the group during cleanup.
    - On Popen FileNotFoundError or PermissionError, calls logger.error then sys.exit(1), terminating the entire Python process.

## Control Flow:
flowchart TD
    Start --> CheckInput{input is not None?}
    CheckInput -- yes --> AssertStdin[assert stdin is None; stdin = PIPE]
    CheckInput -- no --> KeepStdin[use provided stdin]
    AssertStdin --> GnuTimeCheck
    KeepStdin --> GnuTimeCheck
    GnuTimeCheck{gnu_time is not None?} -- yes --> CreateTmp[create NamedTemporaryFile; prepend gnu_time wrapper to argv]
    GnuTimeCheck -- no --> NoTmp[use ExitStack; argv = shlex.split(command_str)]
    CreateTmp --> WindowsCheck
    NoTmp --> WindowsCheck
    WindowsCheck{os.name == 'nt'?} -- yes --> UseString[use command_str string for Popen]
    WindowsCheck -- no --> UseList[use argv list for Popen]
    UseString --> StartTimer
    UseList --> StartTimer
    StartTimer --> PreexecSetup{gnu_time and posix?}
    PreexecSetup -- yes --> SetPreexec[preexec_fn = os.setsid]
    PreexecSetup -- no --> NoPreexec[preexec_fn = None]
    SetPreexec --> TryPopen
    NoPreexec --> TryPopen
    TryPopen --> PopenError{FileNotFoundError or PermissionError?}
    PopenError -- yes --> LogAndExit[logger.error(...); sys.exit(1)]
    PopenError -- no --> ProcCreated[proc created]
    ProcCreated --> CommunicateTry[try proc.communicate(input=input, timeout=timeout)]
    CommunicateTry -- TimeoutExpired --> TimeoutHandled[pass]
    CommunicateTry -- no --> CapturedAnswer[answer assigned from communicate]
    TimeoutHandled --> Cleanup
    CapturedAnswer --> Cleanup
    Cleanup --> IfPreexecKill{preexec_fn set?}
    IfPreexecKill -- yes --> KillGroup[try os.killpg(..., SIGTERM) except ProcessLookupError pass]
    IfPreexecKill -- no --> TerminateProc[proc.terminate()]
    KillGroup --> StopTimer
    TerminateProc --> StopTimer
    StopTimer --> ReadGnuTime{gnu_time provided?}
    ReadGnuTime -- yes --> ParseTmpFile[read tmp file; if last line is digits -> memory = int/1000]
    ReadGnuTime -- no --> MemoryNone[memory = None]
    ParseTmpFile --> BuildInfo
    MemoryNone --> BuildInfo
    BuildInfo --> Return[return info, proc]

## Examples:
- Basic run and read stdout:
    info, proc = exec_command('echo hello')
    if info['answer'] is not None:
        print(info['answer'].decode().strip())  # 'hello'
    print('elapsed (s):', info['elapsed'])

- Send input bytes:
    info, proc = exec_command('python -c "import sys; print(sys.stdin.read().upper())"', input=b'abc\n')
    print(info['answer'].decode())  # 'ABC\n'

- Timeout handling (communicate times out; partial output is discarded by this implementation):
    info, proc = exec_command('sleep 10 && echo done', timeout=1.0)
    # Because communicate raised TimeoutExpired and the code does not extract exception.output,
    # info['answer'] will be None
    if info['answer'] is None:
        print('timed out or no stdout')

- Measure memory using GNU time (POSIX):
    info, proc = exec_command('./heavy_binary', gnu_time='/usr/bin/time')
    if info['memory'] is not None:
        print('peak memory (MB):', info['memory'])

Implementation hints:
    - Use shlex.split(command_str) on POSIX. On Windows pass the original string to Popen.
    - When wrapping with GNU time, invoke: [gnu_time, '-f', '%M', '-o', tmpfile, '--'] + argv and parse the last line of tmpfile as kilobytes (divide by 1000 to get MB).
    - Use time.perf_counter() to measure elapsed time.
    - If starting a new process group on POSIX (os.setsid), terminate the group with os.killpg(os.getpgid(proc.pid), signal.SIGTERM).
    - Forward stderr to sys.stderr rather than capturing it.

## `onlinejudge_command.utils.green` · *function*

## Summary:
Returns the input text wrapped with ANSI color codes that make the text appear green when printed to a terminal that honors these codes.

## Description:
This small utility centralizes the creation of a green-colored string by prefixing the text with the green foreground code and suffixing it with the reset code from the colorama library.

Known callers within the provided context:
    - No callers were provided with this task. In a typical CLI codebase, this function is used by UI/printing helpers and command implementations when they need to display success messages or positively-highlighted text in the terminal.

Why this is a separate function:
    - It encapsulates the exact sequence of prefixing and resetting ANSI codes so callers need not duplicate the colorama constants or remember to reset the color. This keeps formatting consistent and easier to update (e.g., if a different style or additional formatting is desired).

## Args:
    s (str): The text to colorize. The function expects a Python string. Passing a non-string value will result in a runtime TypeError when attempting string concatenation.

## Returns:
    str: A new string equal to colorama.Fore.GREEN + s + colorama.Fore.RESET.
    - On success the returned string begins with the green ANSI sequence and ends with the reset sequence so that subsequent terminal output is unmodified.
    - No other return values are possible.

## Raises:
    TypeError: If `s` is not a str (e.g., attempting to concatenate a non-str object with the colorama string constants will raise a TypeError).

## Constraints:
    Preconditions:
        - colorama must be importable (the module is referenced by the function).
        - The caller should pass a str. The type hint enforces this expectation but is not enforced at runtime.
    Postconditions:
        - The returned value is a str that, when printed to a terminal supporting ANSI sequences, will display the original text in green and then reset the terminal color.

## Side Effects:
    - None. The function performs no I/O, does not mutate external state, and does not call colorama.init() or any other external APIs. It merely constructs and returns a string.

## Control Flow:
flowchart TD
    Start([start]) --> Concat[/"Concatenate: colorama.Fore.GREEN + s + colorama.Fore.RESET"/]
    Concat --> Return[/return concatenated string/]
    Concat --> TypeError{"s is not a str -> TypeError"}
    TypeError --> End([end])
    Return --> End

## Examples:
    Example 1 — typical usage (prints green "OK"):
        print(green("OK"))

    Example 2 — safety when input may be non-string:
        try:
            value = 123  # not a str
            print(green(value))  # will raise TypeError
        except TypeError:
            # Convert to string explicitly before coloring
            print(green(str(value)))

## `onlinejudge_command.utils.red` · *function*

## Summary:
Wraps the provided string with ANSI color codes that render it in red when printed to a terminal that supports ANSI/colorama.

## Description:
This utility isolates the logic for applying the red foreground color escape sequences from the colorama library so other parts of the CLI can consistently colorize error or alert text. It simply prefixes the string with colorama.Fore.RED and suffixes it with colorama.Fore.RESET.

Known callers within the repository snapshot:
- None explicitly identified in this file. This function is intended for use by CLI output routines that want a quick way to colorize messages (e.g., printing errors or highlights). Callers are typically command handlers or presentation helpers that prepare user-visible strings for stdout/stderr.

Why this is a separate function:
- Centralizes the color-wrapping convention (prefix and reset) to avoid duplication and to make it straightforward to change color/formatting in a single place.
- Keeps call sites concise and focused on message content rather than color escape management.

## Args:
    s (str): The text to be colorized. Must be of Python str type. If a non-str value is passed, Python will raise a TypeError at concatenation time.

## Returns:
    str: A new string equal to colorama.Fore.RED + s + colorama.Fore.RESET.

    Possible return values and edge cases:
    - If s is '', returns the red prefix followed immediately by the reset sequence (i.e., an empty visible message but with color codes present).
    - The actual colorization effect when printing depends on the terminal and whether colorama has been properly initialized on platforms that require it (notably Windows). The function always returns the raw escape sequences as provided by colorama.Fore constants.

## Raises:
    TypeError: If s is not a str (e.g., passing None, bytes, or an object without a str concatenation path), Python's string concatenation will raise TypeError.
    (The function does not explicitly raise exceptions itself.)

## Constraints:
Preconditions:
    - The caller should pass a Python str.
    - colorama must be importable (this module imports it at file scope). On some platforms (Windows) callers should call colorama.init() at program startup to ensure color codes are translated correctly.

Postconditions:
    - The returned value is a str that begins with the red color escape sequence and ends with the reset sequence, guaranteeing that subsequent text printed after this string is not left red by this fragment.

## Side Effects:
    - None. The function does not perform I/O, mutate global variables, write to disk, or call external services.
    - It does read from the colorama module-level constants but does not alter colorama state.

## Control Flow:
flowchart TD
    Start --> Concat["Concatenate: prefix + s + suffix"]
    Concat --> Return["Return resulting string"]
    Return --> End

## Examples:
    # Basic usage in a CLI printing an error message:
    import colorama
    colorama.init()  # recommended on Windows; safe to call on other platforms
    print(red("Error: file not found"))

    # Handling non-str inputs explicitly to avoid TypeError:
    value = None
    if value is None:
        print(red("Error: missing value"))
    else:
        print(red(str(value)))

## `onlinejudge_command.utils.green_diff` · *function*

## Summary:
Return the input string wrapped with ANSI sequences that highlight it with a bright green background and (by the function's construction) leave the terminal foreground set to green after the string.

## Description:
This helper formats a single string so it appears highlighted in terminals that understand ANSI color sequences. It is intended for highlighting added/positive lines in diffs or similar textual output where a green highlight signals success or addition.

Known callers within the codebase:
- No explicit callers were found in the provided module snapshot. Typical callers are functions that render or print diff lines, status messages, or other text where a green highlight is desirable.

Why this is extracted:
- Coloring/formatting a diff line is a small, reusable formatting concern that is clearer and less error-prone when centralized. Extracting it avoids duplication and makes it easier to change the exact sequence of ANSI attributes in one place.

## Args:
    s (str): The input text to highlight. Must be a str; passing another type will cause a runtime TypeError when Python attempts to concatenate the value into the ANSI string.

## Returns:
    str: A new string containing ANSI escape sequences (via colorama constants) that, when printed to a compatible terminal, render the original text with:
      - bright style enabled during the text,
      - a green background while the text is printed,
      - after the returned string, the terminal foreground color will be set to green (because the final appended escape is Fore.GREEN).
    Edge cases:
      - If s is the empty string, the return value will still contain the ANSI sequences (i.e., highlighting wrappers with no visible inner characters).
      - If s already contains ANSI sequences, those sequences are not removed or normalized; they will be embedded between the wrapper sequences.

## Raises:
    TypeError: If the caller passes a non-str object for s, Python string concatenation will raise TypeError (this is not explicitly checked in the function).

## Constraints:
    Preconditions:
      - colorama must be importable in the runtime environment (the module uses colorama constants).
      - The caller should assume the terminal or output consumer supports ANSI escape sequences for visible highlighting.
    Postconditions:
      - The function does not mutate inputs; it returns a composed string.
      - The returned string ends with an ANSI sequence that sets the foreground color to green (no automatic reset to default foreground is included).

## Side Effects:
    - None: the function performs no I/O, network access, global state mutation, or external service calls. It only constructs and returns a string.
    - Note: printing the returned string to a terminal will change the terminal's appearance (color) for subsequent text because the returned sequence leaves the foreground set to green. The caller is responsible for resetting colors after printing if a reset is desired.

## Control Flow:
flowchart TD
    Start([Start])
    CheckType{is s a str?}
    Concat[Concatenate ANSI prefix + s + ANSI suffix]
    Return([Return composed string])
    Error([TypeError raised by Python])
    Start --> CheckType
    CheckType -- yes --> Concat --> Return
    CheckType -- no --> Error

## Examples:
- Typical usage (printing a highlighted diff line):
    print(green_diff("+ added file"))  # prints a bright, green-background line; subsequent text may be green

- Avoid leaving the rest of the terminal colored by resetting after printing (caller responsibility):
    print(green_diff("+ added file"), end="")
    print(colorama.Style.RESET_ALL)  # reset style and colors for subsequent output

- Handling empty input:
    highlighted = green_diff("")  # returns a string containing only ANSI wrappers; printing it shows an empty highlighted region

Note: Because the function returns ANSI sequences rather than performing output itself, callers should decide where and when to print the returned string and whether to follow it with a reset (e.g., colorama.Style.RESET_ALL or colorama.Fore.RESET) to restore normal terminal colors.

## `onlinejudge_command.utils.red_diff` · *function*

## Summary:
Wraps the given string with ANSI escape sequences (via colorama constants) to render the text with a red background and bright style for display in terminals; the returned string also ends by setting the foreground color to red.

## Description:
This helper prepares a short piece of terminal text so it appears highlighted as a bright-on-red diff block when printed to a terminal that understands ANSI color sequences (or when colorama is initialized to translate them on Windows).

Known callers within the codebase:
    - No explicit callers are determined from this file alone. Search the repository for occurrences of "red_diff(" to locate call sites.
Typical usage context:
    - Used where terminal-formatted diffs, errors, or highlighted messages are assembled for human-readable CLI output.
Why this is a separate function:
    - Centralizes the exact sequence of color/attribute escape codes used to highlight a piece of text. This avoids repeating the same concatenation logic and makes it easier to update highlighting style in one place.

## Args:
    s (str): The input text to highlight. Must be a Python str. Passing non-str types will raise a TypeError (due to concatenation) unless explicitly converted before calling.

## Returns:
    str: The input text wrapped with colorama escape-sequence constants:
        - Prefix: colorama.Fore.RESET + colorama.Back.RED + colorama.Style.BRIGHT
        - Suffix: colorama.Style.NORMAL + colorama.Back.RESET + colorama.Fore.RED
    The returned string contains ANSI/VT100-like escape sequences and therefore is intended for terminal output. Note that the function intentionally ends with colorama.Fore.RED (i.e., it leaves the foreground color set to red), so subsequent printed text will remain red unless the caller resets colors (for example with colorama.Style.RESET_ALL or colorama.Fore.RESET).

Edge-case return values:
    - If s is the empty string (""), the function returns the same sequence of escape codes without visible characters in between; the terminal effects (background, brightness, and trailing foreground red) still apply.
    - The function never returns None.

## Raises:
    TypeError: If a non-str is passed (for example an int or None) Python will raise TypeError during concatenation. The function itself does not explicitly validate types or raise custom exceptions.

## Constraints:
Preconditions:
    - colorama must be importable (this module imports it at file level).
    - For correct appearance on Windows consoles, the application should call colorama.init() before printing the returned string (or otherwise ensure ANSI sequences are translated).

Postconditions:
    - The returned value is a str containing ANSI escape sequences.
    - After printing the returned string, the terminal's foreground color will be set to red unless the caller explicitly resets it.

## Side Effects:
    - The function performs no I/O itself (no printing, file, network, or OS calls).
    - It does not mutate global variables or external state.
    - However, because the returned string ends with an ANSI code that sets the terminal's foreground color to red, printing it will affect terminal colors for subsequent output until the program resets colors.

## Control Flow:
flowchart TD
    Start --> BuildPrefix[Set prefix: Fore.RESET + Back.RED + Style.BRIGHT]
    BuildPrefix --> AppendText[Append input text s]
    AppendText --> BuildSuffix[Append suffix: Style.NORMAL + Back.RESET + Fore.RED]
    BuildSuffix --> Return[Return concatenated string]
    Return --> End

## Examples:
Example 1 — printing a highlighted diff line and then resetting colors so following output is normal:
    import colorama
    colorama.init()  # recommended on Windows
    line = " - expected: 1, actual: 2"
    highlighted = red_diff(line)
    print(highlighted)
    # Reset to avoid leaking the red foreground to subsequent output
    print(colorama.Style.RESET_ALL)

Example 2 — storing multiple highlighted lines and joining:
    lines = ["- a", "- b"]
    highlighted_lines = [red_diff(l) for l in lines]
    # join and print; remember to reset after printing
    print("\\n".join(highlighted_lines))
    print(colorama.Fore.RESET)

Notes:
    - If you want the highlighting to be self-contained (i.e., not to affect subsequent text), wrap the result with a final colorama.Style.RESET_ALL or colorama.Fore.RESET after printing.
    - The exact appearance depends on the terminal and whether colorama.init() has been called (on Windows, colorama.init() enables translation of ANSI codes to Win32 calls).

## `onlinejudge_command.utils.success` · *function*

## Summary:
Returns a single-line, green-colored success label followed by the provided message suitable for CLI output.

## Description:
- Known callers within the codebase: None found in the scanned repository snapshot. This utility is intended for use by CLI command handlers or any code path that needs to display a short "SUCCESS: <message>" status to the user.
- Typical trigger/context: Called when an operation completes successfully and a visually highlighted success message should be printed to standard output or logged.
- Why this is a separate function: Centralizes the string format and color styling for success messages so callers do not duplicate ANSI/Colorama escape sequences. It enforces a single canonical prefix ("SUCCESS: ") and color (green) across the codebase, making future style changes (e.g., different color, different prefix) trivial to apply in one place.

## Args:
    msg (str): The message body to append after the "SUCCESS: " prefix.
        - Type: str (annotated)
        - Allowed values: any string, including empty string.
        - Interdependencies: None. The function concatenates this value directly to the prefix; it expects a string-like value.

## Returns:
    str: A new string formed by the concatenation of:
        colorama.Fore.GREEN + 'SUCCESS' + colorama.Style.RESET + ': ' + msg
    - Effectively this is the "SUCCESS: " label with ANSI/colorama color codes for green applied to the label only, followed by the provided message.
    - Example return when msg == "Done": "<GREEN>SUCCESS<RESET>: Done" (where <GREEN> and <RESET> are the actual sequences provided by colorama).
    - Edge cases:
        - If msg is the empty string, the returned string ends with ": ".
        - If msg already contains ANSI sequences or newline characters, those are preserved verbatim.

## Raises:
    TypeError: If a non-string is passed for msg that cannot be concatenated with str. Because the function uses plain string concatenation, passing e.g. None or an integer will raise a TypeError at runtime.

## Constraints:
- Preconditions:
    - The module-level import of colorama must succeed (colorama is available). The function references colorama.Fore and colorama.Style.
    - The caller should supply a string for msg to avoid runtime TypeError from concatenation.
- Postconditions:
    - The function returns deterministically without mutating external state.
    - The returned string always begins with the color-encoded "SUCCESS" label followed by ": " and then the original msg content.

## Side Effects:
- The function itself has no I/O and does not mutate global state.
- It does not call colorama.init(); therefore, whether color sequences render as colors (instead of raw ANSI escape codes) depends on the environment and whether colorama has been initialized elsewhere (for example, by the program startup code).
- No network, filesystem, or logging side effects occur.

## Control Flow:
flowchart TD
    A[call success(msg)] --> B[compute prefix = colorama.Fore.GREEN + "SUCCESS"]
    B --> C[append colorama.Style.RESET + ": "]
    C --> D[concatenate prefix + msg]
    D --> E[return resulting string]

## Examples:
- Basic usage:
    - Typical pattern in a CLI command:
        1. Optionally initialize colorama once at program startup (recommended on some platforms): colorama.init()
        2. Print the success message:
            print(success("Solved 1 / 1 cases"))
- Handling non-string inputs (defensive):
    - Convert non-string values before calling to avoid TypeError:
        print(success(str(result_count) + " items processed"))
- Empty message:
    - print(success(""))  # returns "<GREEN>SUCCESS<RESET>: "

Notes:
- The function is intentionally minimal: it only prepares and returns the formatted string. Callers decide whether to print it, log it, or otherwise consume it.

## `onlinejudge_command.utils.failure` · *function*

## Summary:
Returns a console-ready failure label prefixed to the provided message, using colorama to render the "FAILURE" label in red.

## Description:
This is a tiny presentation helper that formats an error/failure message for CLI output by prepending a red "FAILURE" label followed by a colon and a space. It centralizes the exact text and color formatting so callers can produce consistent failure output across the application.

Known callers within the codebase:
    - No explicit call sites were identified during this documentation pass. Consumers are typically command handlers or CLI utilities that need to present error results to users.

Why this logic is extracted:
    - Keeps CLI text formatting consistent (same label, punctuation, and color).
    - Avoids duplicating color/label formatting at many call sites.
    - Makes it trivial to change the formatted prefix in one place if needed.

## Args:
    msg (str): The message text to display after the failure label.
        - Required: this function expects a Python str. Passing a non-str (e.g., int) will raise a TypeError due to string concatenation.
        - There are no other allowed ranges or enumerated values; any string content is accepted.

## Returns:
    str: A single string consisting of:
        - colorama.Fore.RED (ANSI sequence or equivalent)
        - the literal label "FAILURE"
        - colorama.Style.RESET (resets color formatting)
        - the literal string ": "
        - the supplied msg
    Example return (conceptual, raw form):
        "<RED>FAILURE<RESET>: " + msg

    Notes on return values and edge cases:
        - If msg is an empty string, the function returns a labeled prefix followed by ": " and nothing else (i.e., "FAILURE: " with color codes).
        - If msg is not a str, the function raises TypeError (see Raises).

## Raises:
    TypeError: If msg is not a str. The function performs string concatenation; Python will raise a TypeError for non-str operands (e.g., int or bytes) when concatenated with str.

## Constraints:
    Preconditions:
        - msg must be a str (or a value explicitly converted to str by the caller).
        - colorama must be importable (the module is referenced; if colorama import failed at module import time, the process would have failed earlier).
    Postconditions:
        - The returned value is a str that begins with the "FAILURE" label (including colorama color-control sequences) followed by ": " and then the original msg content.

## Side Effects:
    - None. This function does not perform I/O, mutate global state, or call external services.
    - It only constructs and returns a string. Rendering of color sequences to an actual colored display depends on the terminal environment and whether colorama.init() or equivalent terminal support is active.

## Control Flow:
flowchart TD
    A[Start] --> B{Is msg a str?}
    B -- Yes --> C[Concatenate colorama.Fore.RED + "FAILURE" + colorama.Style.RESET + ": " + msg]
    B -- No --> D[TypeError raised by Python during concatenation]
    C --> E[Return formatted str]
    D --> F[Exception propagates]

## Examples:
Example 1 — simple printing to stdout:
    # Preferred: ensure msg is a str
    print(failure("unable to fetch problem data"))

Example 2 — safe usage when msg may be non-string:
    # Convert non-string values to str before calling to avoid TypeError
    value = 404
    print(failure(str(value) + " Not Found"))

Example 3 — using with logging or stderr:
    # Logging frameworks typically expect plain strings; pass the returned string to logger or print to stderr
    import sys
    sys.stderr.write(failure("command timed out") + "\n")

## `onlinejudge_command.utils.remove_suffix` · *function*

## Summary:
Removes a given trailing substring from a string, returning the prefix before that suffix; fails if the input does not end with the suffix.

## Description:
This small utility enforces the precondition that the input string ends with the provided suffix and returns the original string with that trailing suffix removed.

Known callers:
- No callers were discovered within the same module during analysis. Call sites in other modules were not inspected.

Why this function exists:
- Encapsulates a common operation (remove a known trailing suffix) into a single, well-named place so callers can rely on a consistent precondition check and removal behavior instead of repeating the same pattern across the codebase.

## Args:
    s (str): The original string expected to end with `suffix`.
    suffix (str): The trailing substring to remove from `s`. May be an empty string.

Interdependencies:
- The function requires that s.endswith(suffix) is True; otherwise it triggers an assertion.

## Returns:
    str: The input string with the final occurrence of `suffix` removed.
    - If suffix == "": returns an empty string (because slicing with -0 yields s[:0]).
    - If len(s) == len(suffix) and s.endswith(suffix): returns an empty string.
    - For normal cases where 0 < len(suffix) < len(s), returns s[0:len(s)-len(suffix)].

## Raises:
    AssertionError: Raised if s.endswith(suffix) is False at runtime (i.e., the precondition is not met).
    Note: Because the implementation uses an assert statement, assertions may be disabled when Python is run with optimizations (python -O); in that case the check will be skipped and an incorrect slice may be returned instead of raising.

## Constraints:
Preconditions:
- Both arguments must be Python strings (str). Passing non-str types will result in a TypeError when str methods are used.
- Caller must ensure that s.endswith(suffix) is True for intended behavior; otherwise an AssertionError is raised (unless assertions are disabled).

Postconditions:
- The returned value is a str whose concatenation with `suffix` equals the original string `s` when assertions are honored.
- No mutations occur to input data; operation is pure and returns a new string.

## Side Effects:
- None. The function performs no I/O, does not mutate external state, and makes no network or filesystem calls.

## Control Flow:
flowchart TD
    Start --> CheckEndsWith
    CheckEndsWith{ s.endswith(suffix) ? }
    CheckEndsWith -- False --> RaiseAssertion[AssertionError raised]
    CheckEndsWith -- True --> ComputeResult[return s[:-len(suffix)]]
    ComputeResult --> End
    RaiseAssertion --> End

## Examples:
- Typical successful usage: if s is "solution.cpp" and suffix is ".cpp", the function returns "solution".
- Edge case where suffix is empty: if s is "abc" and suffix is "", the function returns "" (empty string) because slicing uses -0.
- Handling incorrect input:
    - If s is "file.txt" and suffix is ".pdf", the function will raise AssertionError because s.endswith(".pdf") is False.
    - To call safely in production where asserts might be disabled, check the precondition explicitly before calling:
      - Example pattern (described): if not s.endswith(suffix): raise ValueError("...") else call remove_suffix(s, suffix).

Notes and recommendations:
- Because assertions can be disabled with Python optimizations, callers that require guaranteed runtime validation should either:
    1) Validate s.endswith(suffix) themselves and raise a concrete exception (ValueError) before calling, or
    2) Replace the assert in this function with an explicit conditional and exception if you control the function.

## `onlinejudge_command.utils.is_windows_subsystem_for_linux` · *function*

## Summary:
Detects whether the current Python process is running inside the Windows Subsystem for Linux (WSL) and returns True if so, otherwise False.

## Description:
This function centralizes platform detection logic to decide if the runtime environment is WSL. It performs two checks against the system information returned by the standard library: the operating system name must appear as Linux, and the release string must contain the substring "microsoft" (case-insensitive).

Known callers within the codebase:
- No direct callers were discovered in the provided repository snapshot. (It is designed as a small utility function intended for conditional behavior elsewhere, e.g., adjusting path handling, terminal/TTY behavior, or subprocess invocation when running under WSL.)

Why this logic is extracted:
- Responsibility: Encapsulates the WSL-detection heuristic in one place so all modules that need to adapt behavior for WSL can call a single, well-named function rather than duplicating the platform-check logic.
- Boundaries: Keeps platform-detection concerns isolated from higher-level logic (avoiding scattering platform-specific string checks throughout the codebase).

## Args:
- None

## Returns:
bool
- True: the runtime appears to be WSL. This happens when:
    - platform.uname().system == 'Linux' AND
    - the lowercase of platform.uname().release contains the substring 'microsoft'
- False: any other condition (including when the system is not Linux or the release string does not contain 'microsoft').

Edge-case considerations:
- The function assumes platform.uname() returns an object with string attributes 'system' and 'release'. If platform.uname() returns unexpected non-string values, calling .lower() on the release value will raise an AttributeError (see Constraints).

## Raises:
- AttributeError: if platform.uname().release is not a string (because the code calls .lower() on it).
- Any other exceptions that platform.uname() itself might raise (rare; typically platform.uname() returns a named tuple of strings).

## Constraints:
Preconditions:
- The standard library function platform.uname() must be available and return an object with at least the attributes .system and .release (normally true for CPython on standard platforms).
- The caller should ensure the environment has not monkeypatched platform.uname() to return non-string release values if they wish to avoid exceptions.

Postconditions:
- The function returns a boolean value indicating whether the current runtime appears to be WSL; it does not modify program state or external resources.

## Side Effects:
- None. This function performs only pure reads from the platform module and returns a boolean. It performs no I/O, no global state mutation, and no network access.

## Control Flow:
flowchart TD
    A[Start] --> B{platform.uname().system == 'Linux'?}
    B -- No --> G[Return False]
    B -- Yes --> C{'microsoft' in platform.uname().release.lower()?}
    C -- Yes --> H[Return True]
    C -- No --> G[Return False]

## Examples:
- Typical usage in application code (prose):
  Call this function when you need to apply WSL-specific behavior, for example: adjusting executable paths, choosing shell invocation flags, or handling console/tty capabilities differently. Use the boolean result to branch once and then keep higher-level logic portable.

- Minimal illustrative example (pseudo-Python; does not include function implementation):
  if is_windows_subsystem_for_linux():
      # apply WSL-specific adjustments, e.g. translate paths or change subprocess args
      apply_wsl_workarounds()
  else:
      # normal non-WSL behavior
      run_standard_flow()

- Error handling guidance:
  If your application must be robust to unexpected monkeypatching of platform.uname() or non-standard environments, guard calls with try/except to handle AttributeError:
  try:
      if is_windows_subsystem_for_linux():
          ...
  except AttributeError:
      # fallback behavior if platform.uname() yields unexpected types
      handle_unknown_platform()

## `onlinejudge_command.utils.webbrowser_register_explorer_exe` · *function*

## Summary:
Register a Windows Explorer-backed web browser in Python's webbrowser registry when running inside Windows Subsystem for Linux (WSL), or do nothing on other platforms.

## Description:
This function ensures that, when the process is running under WSL, a webbrowser registry entry named "explorer" is created that delegates to the host Windows executable explorer.exe. This lets higher-level code request the "explorer" browser name and open URLs or file paths using Windows Explorer from within WSL.

Known callers within the codebase:
- No direct callers were discovered in the provided repository snapshot. This function is designed as a small initialization helper that can be called during program startup or before any code that may call webbrowser.get('explorer') or otherwise expects an 'explorer' browser to exist.

Why this logic is extracted into its own function:
- Responsibility: Encapsulates the platform-specific registration logic (WSL-only) so that callers can remain platform-agnostic. Higher-level modules only need to call this single helper at initialization instead of repeating the same platform-check and registration code.
- Boundary: Keeps side-effects (mutation of the webbrowser registry) confined to one place and documents the compatibility/compatibility-version behavior (different register signature usage for Python <3.7 and >=3.7).

## Args:
- None

## Returns:
- None
- Side-effect: May register a browser under the name "explorer" in the global webbrowser registry when running under WSL. If not running under WSL, the function returns immediately and does nothing.

## Raises:
- Propagates any exception raised by is_windows_subsystem_for_linux(). In particular, AttributeError may be raised if platform.uname().release is not a string (see is_windows_subsystem_for_linux behavior).
- Propagates any exception raised by webbrowser.GenericBrowser(...) or webbrowser.register(...). For example, if the webbrowser API raises a TypeError or other runtime error due to unexpected environment conditions, that exception will propagate to the caller.
- No exceptions are raised explicitly by this function in its body; all errors originate from called routines.

## Constraints:
Preconditions:
- The standard library webbrowser module must be available (this module is imported at file scope).
- The helper is meaningful only when running inside WSL; callers should not rely on it registering anything on non-WSL platforms.
- The platform-detection helper is_windows_subsystem_for_linux() must behave as expected (see its documentation: it calls platform.uname()).

Postconditions:
- If the runtime is detected as WSL:
    - The global webbrowser registry contains an entry named "explorer".
    - The registered entry uses an instance created by webbrowser.GenericBrowser('explorer.exe').
    - For Python versions >= 3.7, the registration is marked preferred=True; for older Python versions the preferred flag is not provided (legacy behavior).
- If the runtime is not WSL: the webbrowser registry is unchanged by this function.

## Side Effects:
- Mutates the global state of the standard library webbrowser module by calling webbrowser.register(...), adding (or replacing) the "explorer" entry in the registry.
- No file, network, or stdout/stderr I/O is performed by this function.
- No other global variables or external resources are modified.

## Control Flow:
flowchart TD
    A[Start] --> B{is_windows_subsystem_for_linux()?}
    B -- No --> C[Return (do nothing)]
    B -- Yes --> D[Create instance = webbrowser.GenericBrowser('explorer.exe')]
    D --> E{sys.version_info < (3,7)?}
    E -- Yes --> F[webbrowser.register('explorer', None, instance)]
    E -- No --> G[webbrowser.register('explorer', None, instance, preferred=True)]
    F --> H[Return None]
    G --> H[Return None]

## Examples:
- Typical initialization usage (high-level description):
  Call this function once at program startup (or before any code that may request a browser named "explorer") to ensure the registry entry exists when running under WSL. If the call fails due to unexpected platform data or webbrowser API errors, log or handle the exception at initialization time.

- Example usage pattern (pseudocode / prose):
  1. At application startup call webbrowser_register_explorer_exe().
  2. Later, to open a file or URL from WSL using the Windows host:
     - Attempt to retrieve the registered browser by name: webbrowser.get('explorer')
     - Use the browser's open/open_new/open_new_tab API to open the target path/URL.
  3. If webbrowser.get('explorer') fails because registration did not occur, fall back to webbrowser.open(...) or another cross-platform strategy.

- Error handling guidance:
  If your initialization must be robust against unusual platform information or environment issues, wrap the call in a try/except that catches exceptions from is_windows_subsystem_for_linux and webbrowser.register and applies a fallback (for example, skip registration and log a warning).

## `onlinejudge_command.utils.get_default_command` · *function*

## Summary:
Return the platform-appropriate default filename for a compiled contestant program (Windows: a.exe; others: a.out).

## Description:
Known callers within the repository snapshot:
- No direct call sites were found in the provided snapshot for this specific function. It is intended to be used by higher-level utilities that need a sensible default command/path to execute compiled solutions (for example, test runners or submission runners that compile C/C++/Rust solutions and then run the produced binary).

Why this logic is extracted:
- Centralizes the platform-specific decision about a default compiled executable name so callers can rely on a single, well-documented source of truth rather than duplicating platform checks.
- Encapsulates the mapping from platform.system() to the default relative executable path, keeping callers simpler and easier to test.

## Args:
- This function takes no arguments.

## Returns:
- str: a relative path string representing the default executable to run.
  - On Windows (when platform.system() == 'Windows'): returns the string '.\\a.exe' (written in source as r'.\a.exe'). This is a relative path using a backslash.
  - On all other platforms: returns the string './a.out', a relative path using a Unix-style forward slash.
- Possible edge cases:
  - The function never returns None or an empty string; it always returns one of the two strings above.
  - It does not check whether the file actually exists, is executable, or is accessible.

## Raises:
- This function raises no exceptions itself.
  - It calls platform.system(), which is not expected to raise under normal circumstances. Any unexpected exceptions propagated from the platform module are not caught here.

## Constraints:
Preconditions:
- No preconditions are required beyond a working Python runtime and a functioning platform.system() call.

Postconditions:
- The return value is guaranteed to be a non-empty relative path string that a caller can attempt to execute or test for existence.
- No mutation of global state or I/O is performed by this function.

## Side Effects:
- None. The function performs no I/O, does not mutate global state, and makes no network calls.

## Control Flow:
flowchart TD
    Start(("start"))
    Check{platform.system() == "Windows"}
    WinReturn["return '.\\a.exe'"]
    UnixReturn["return './a.out'"]
    Start --> Check
    Check -- True --> WinReturn
    Check -- False --> UnixReturn

## Examples:
Example 1 — basic use in a runner:
- Purpose: obtain a default command and attempt to run it with subprocess; handle errors when the executable is missing.
- Usage (illustrative; adapt to your code style):
    cmd = get_default_command()
    # Note: cmd is a single string with a relative path. Many runtimes prefer a list of args:
    argv = [cmd]
    try:
        # Attempt to run the default executable; this will raise FileNotFoundError if it doesn't exist,
        # or subprocess.CalledProcessError if you use check=True and the process exits non-zero.
        subprocess.run(argv, check=True)
    except FileNotFoundError:
        # The default executable was not present — caller should handle compilation or report an error.
        handle_missing_executable(cmd)
    except subprocess.CalledProcessError as e:
        # The executable ran but returned a non-zero exit code.
        handle_runtime_failure(e.returncode)

Example 2 — checking existence before execution:
    cmd = get_default_command()
    if not os.path.exists(cmd):
        # Compile or inform the user that the binary is missing.
        build_solution()
    else:
        run_solution(cmd)

Notes:
- Callers that spawn a process should be aware this function returns a relative path; depending on the working directory and how compilation is performed, callers may need to resolve the path to an absolute path or change working directory before execution.
- If cross-platform path normalization is required, callers should convert or normalize the returned path (for example, using pathlib.Path returned_path.resolve() or os.path.normpath) before passing it to lower-level OS APIs.

