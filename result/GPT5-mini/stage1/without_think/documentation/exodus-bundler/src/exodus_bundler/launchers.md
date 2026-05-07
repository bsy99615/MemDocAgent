# `launchers.py`

## `src.exodus_bundler.launchers.CompilerNotFoundError` · *class*

## Summary:
Represents the specific error raised when a required external compiler or tool cannot be found or resolved by the launchers subsystem.

## Description:
This is a lightweight, semantic Exception subclass used to signal that the system attempted to locate or invoke an external compiler (or equivalent tool) and failed to find an executable to satisfy that need. It exists so calling code can distinguish "compiler-not-found" failures from other kinds of errors (runtime/OS errors, process failures, etc.) and handle them separately (for example, by presenting an actionable error to the user or falling back to an alternative strategy).

Scenarios where instances are created:
- Any launcher or preparatory routine that requires an external compiler or tool and is unable to locate an executable on PATH or at a configured location.
- When a lookup function (e.g., one that wraps distutils.spawn.find_executable or other resolver logic) completes without finding a usable binary and needs to abort with a specific, catchable error.

Note: The source for known callers was not available in this component's scope; callers are any module components that need to detect and communicate a missing compiler condition.

Motivation and responsibility:
- Purposefully separates the domain-level failure "compiler is missing" from generic exceptions.
- Responsibility boundary: Represent only the presence of that condition. It does not implement resolution logic, logging, or remediation steps — those are responsibilities of the callers.

## State:
This class does not add any new attributes beyond what BaseException provides. The effective state is inherited from Python's BaseException/Exception:

- args (tuple): Inherited. Holds positional arguments passed at construction, commonly a single human-readable message.
  - Typical usage: args[0] is a string message describing which compiler or tool was not found (e.g., "gcc not found" or "C compiler missing: clang").
  - Valid values: any hashable/value objects acceptable to Exception. Callers normally pass a single str.
- No additional attributes, no mutable state held by this class.

Class invariants:
- Instances must be treated as immutable signals; callers should not depend on mutation of instance attributes.
- The presence of an instance indicates a lookup/resolve failure for an external compiler/tool; no additional internal flags are present.

## Lifecycle:
Creation:
- Instantiate by calling with zero or more positional arguments, typically a single descriptive string:
  - Example instantiation intent (described in prose): raise CompilerNotFoundError with a message naming the missing tool or describing attempted search locations.
- There are no custom factory methods on this class; standard Exception instantiation is used.

Usage:
- Typical sequence:
  1. Component attempts to locate or validate a compiler.
  2. If no suitable executable is found, create and raise CompilerNotFoundError, optionally with a message describing the attempted names/paths.
  3. Higher-level code may catch CompilerNotFoundError specifically to provide user-friendly error text, suggest installation steps, or attempt a fallback path.
- Ordering/Sequencing constraints: None beyond the usual raise/catch semantics for exceptions.

Destruction:
- No special cleanup is required. Instances are subject to normal Python garbage collection once no references remain.
- This class is not a context manager and provides no close or teardown APIs.

## Method Map:
flowchart TD
    A[Start: launcher needs compiler] --> B{Compiler found?}
    B -- yes --> C[Proceed to invoke compiler]
    B -- no --> D[Raise CompilerNotFoundError]
    D --> E[Catch at caller or bubble up]
    E --> F[Handle: inform user / attempt fallback]

(Note: The class itself has no methods beyond Exception/ BaseException; the diagram shows where it fits in typical call flow.)

## Raises:
- The __init__ of this subclass does not introduce new exceptions beyond those that Exception/BaseException may raise in pathological situations.
- Typical behavior: constructing CompilerNotFoundError with any positional arguments mirrors Exception construction and will not raise; consequently, callers should not expect additional exceptions from instantiation itself.
- When raised, it signals the specific condition "required compiler/tool not found."

## Example:
- Creation intent (descriptive):
  - A launcher attempts to resolve "gcc" and "clang" on PATH and in configured tool directories. If none are found, the launcher raises CompilerNotFoundError with a message such as "No C compiler found: tried ['gcc','clang']".
- Handling intent (descriptive):
  - The CLI entrypoint catches CompilerNotFoundError to display an explanatory message to the user and exit with a non-zero status or to suggest installation instructions. Other exception types (e.g., process invocation errors) are handled separately.

## `src.exodus_bundler.launchers.find_executable` · *function*

## Summary:
Searches for a binary by first attempting the original system lookup and, if that fails or is skipped, by walking upward from a configured parent directory to find a release-like directory whose basename is a 64-character hex string, then checking the PATH-like directories inside that release directory for the requested binary. Returns the first filesystem path found or None if not found.

## Description:
This function encapsulates a two-stage strategy for locating an executable:
1. Try the original system lookup (delegated to a global helper expected to be named find_executable_original).
2. If that either fails or is intentionally skipped (testing mode), walk upward from a configured starting directory (expected to be provided as the global parent_directory). For each ancestor directory whose basename matches a 64-character hexadecimal string, iterate PATH-style entries and test for the binary at <ancestor>/<hex-basename>/<path-entry>/<binary_name>.

Known callers within the provided code snapshot:
- No callers were found in the provided repository snapshot. (If other modules call this function, they were not included in the supplied context.)

Typical trigger/context:
- Used when the runtime must prefer a bundled copy of a tool shipped inside a release/commit directory (the hex basename looks like a commit or release id) over the system-installed binary, while still allowing the system binary to be used by default.
- skip_original_for_testing is typically used in unit tests to force searching for the bundled binary rather than returning the system binary.

Why this logic is extracted into its own function:
- The lookup strategy is non-trivial (system lookup + repository-oriented search with specific directory pattern + PATH-entry remapping). Extracting it centralizes the policy for how executables are located, keeps callers simple, and makes testing (via skip_original_for_testing) straightforward without duplicating path-manipulation logic.

## Args:
    binary_name (str)
        The filename of the executable to locate (e.g., "git" or "python3").
        Must be a non-empty string. The function does not validate that this is a valid filename beyond being passed to os.path.join and checked with os.path.exists.

    skip_original_for_testing (bool, optional)
        Defaults to False.
        If True, the function will skip returning the result from the original system lookup and will proceed to the upward-directory bundled search (useful in tests to avoid depending on system state).

Interdependencies:
- The function expects two globals to exist in the module scope:
    * find_executable_original: a callable that accepts (binary_name) and returns a system path (str) or None.
    * parent_directory: a starting directory path (str) used as the initial point for upward traversal.
  If these globals are not defined, calling this function will raise a NameError.

## Returns:
    str or None
    - Returns the absolute or relative filesystem path (string) to the first candidate that exists on disk:
        * If find_executable_original(binary_name) returns a non-empty path and skip_original_for_testing is False, that path is returned immediately.
        * Otherwise, returns the first candidate path that exists where candidates are constructed as:
            os.path.join(ancestor_directory, hex_basename, bin_entry_relpath, binary_name)
          where ancestor_directory/basename is obtained by walking up from parent_directory and hex_basename matches the regex [A-Fa-f0-9]{64}; bin_entry_relpath is the PATH entry converted to a relative path if it was absolute.
    - Returns None implicitly if no candidate is found (no explicit return at end of function).

Possible return shapes and edge cases:
- A filesystem path string that points to an existing file (note: existence is checked with os.path.exists; the function does not verify execute permissions).
- None if nothing is found.
- If find_executable_original returns a path-like object (not a str) the function will return it unchanged, subject to Python's truthiness rules.

## Raises:
    NameError
        If either of the expected globals (find_executable_original or parent_directory) are not defined in the module scope, the first attempt to reference them will raise NameError.

    (No other exceptions are explicitly raised by the function itself. Underlying calls may raise exceptions if e.g. os.path operations receive unexpected types, but those are not raised intentionally by the implementation.)

## Constraints:
Preconditions:
- binary_name should be a non-empty string; callers must ensure sensible filenames.
- Module-scope globals must be provided:
    * find_executable_original: callable(binary_name) -> str|None
    * parent_directory: str path used as the starting point for upward traversal
- It is expected that os.environ is a mapping-like object (standard os.environ) and PATH entries are separated by ':'.

Postconditions:
- If PATH was missing from os.environ at call time, PATH will be set to '/bin/:/usr/bin/' by this function before further processing.
- The function makes no guarantees about the returned path being executable (only that it exists).
- The function will not modify anything else in the environment or filesystem.

## Side Effects:
- May mutate os.environ by setting os.environ['PATH'] to '/bin/:/usr/bin/' if PATH is absent.
- Reads the filesystem via os.path.exists for candidate paths; it does not perform writes, network I/O, spawn subprocesses, or change file permissions.
- Does not check executable permission bits; a returned path may not be runnable.

## Control Flow:
flowchart TD
    Start --> CheckPATH
    CheckPATH -->|'PATH' not in os.environ| SetDefaultPATH
    SetDefaultPATH --> CallOriginal
    CheckPATH -->|'PATH' in os.environ| CallOriginal
    CallOriginal -->|executable and not skip_original_for_testing| ReturnOriginal
    CallOriginal -->|not (executable and not skip_original_for_testing)| SetupTraversal
    SetupTraversal --> WhileLoop[while True: split directory]
    WhileLoop -->|basename empty| EndLoop
    WhileLoop -->|basename matches 64 hex chars| ForEachPATHEntry
    ForEachPATHEntry -->|bin_entry is absolute| ConvertToRelpath
    ForEachPATHEntry --> BuildCandidate
    BuildCandidate -->|os.path.exists(candidate)| ReturnCandidate
    BuildCandidate -->|not exists| ContinuePATHEntries
    ContinuePATHEntries --> NextPATHEntryOrLoop
    NextPATHEntryOrLoop --> WhileLoop
    EndLoop --> ReturnNone
    ReturnOriginal --> End
    ReturnCandidate --> End
    ReturnNone --> End

## Examples:
Example 1 — normal usage (best-effort):
- Caller wants a binary and is OK with the system-installed binary when present.
- Behavior: returns system binary path if available; otherwise searches for a bundled copy.

Example (pseudocode):
    try:
        path = find_executable("mytool")
        if path is None:
            raise RuntimeError("tool not found")
        # Use path (may still need to check executable permission)
    except NameError as e:
        # The module may not have been fully initialized (missing globals)
        # Handle or log the misconfiguration.
        raise

Example 2 — testing mode forcing bundled lookup:
    # In tests you may set skip_original_for_testing=True to force bundled search.
    path = find_executable("mytool", skip_original_for_testing=True)
    # This ensures the function does not return the system binary even if present.

Notes:
- Because the function only uses os.path.exists to validate candidates, callers that need an actually runnable binary should additionally check os.access(path, os.X_OK) or attempt to execute the binary and handle failures.
- If you integrate this function, ensure the module provides the expected globals (find_executable_original and parent_directory) or wrap calls to handle NameError gracefully.

## `src.exodus_bundler.launchers.compile` · *function*

## Summary:
Attempt to compile C source into a static executable by trying a musl-based toolchain first and falling back to a diet-based toolchain; returns the compiled executable bytes on success or raises a CompilerNotFoundError if no suitable compiler is available.

## Description:
- Known callers and context:
    - Typical callers are higher-level bundler/launcher code that programmatically generate C source and need a compiled, self-contained binary for embedding, bundling, or execution.
    - This function is typically invoked in the pipeline stage: source generation → compile(...) → embed/write the returned binary.
    - No specific direct callers were discovered in the snapshot; callers that previously invoked compile_musl or compile_diet can call this function to get automatic fallback behavior.

- Why this logic is extracted:
    - Centralizes the compiler-resolution and fallback policy in a single place so callers do not need to duplicate the logic of trying multiple toolchains.
    - Enforces a clear responsibility boundary: choose a usable compiler (musl first, then diet) and delegate actual compile lifecycle (temp files, subprocess invocation, cleanup, error reporting) to the underlying helpers (compile_musl and compile_diet).
    - Keeps higher-level code simpler and ensures consistent error semantics for the "no compiler available" case.

## Args:
    code (str)
        - C source code text to compile.
        - Must be a Unicode text string (not bytes).
        - Interdependencies: this argument is forwarded unchanged to compile_musl and compile_diet; both helpers expect a valid C source string and will perform temporary-file I/O and subprocess invocations.

## Returns:
    bytes
    - On success returns a bytes object containing the entire compiled executable (the raw binary).
    - Success semantics:
        * If compile_musl succeeds, its returned bytes are returned directly.
        * If compile_musl raises CompilerNotFoundError, compile_diet is attempted and, if it succeeds, its returned bytes are returned.
    - The function does not return partial or intermediate data; failures raise exceptions.

## Raises:
    CompilerNotFoundError
        - Raised when neither the musl-based toolchain nor the diet-based toolchain is available.
        - Exact condition: compile_musl(code) raised CompilerNotFoundError, and subsequently compile_diet(code) also raised CompilerNotFoundError.
        - Exact message produced by this function when raising: 'No suiteable C compiler was found.' (note: the message contains the same spelling as in the implementation).
    AssertionError
        - Propagated from compile_musl or compile_diet when compile_helper detects a non-zero compiler exit code (i.e., a compilation error). The AssertionError message typically contains the compiler stderr.
    OSError / FileNotFoundError / other subprocess-related exceptions
        - Any OS-level or I/O exceptions raised by the underlying helpers (temporary file creation, subprocess invocation) are not caught here and will propagate to the caller.

## Constraints:
- Preconditions:
    - code must be a valid C source string (text/unicode).
    - The runtime environment must permit creating temporary files and spawning subprocesses (permissions, available disk space, working filesystem).
- Postconditions:
    - On successful return, the caller receives bytes representing a compiled static executable produced by either the musl toolchain or the diet toolchain.
    - If the function raises CompilerNotFoundError, no compilation was attempted (both toolchains were unavailable) or both helpers signalled a missing compiler; underlying helpers perform their own cleanup of any temporary resources they touched.

## Side Effects:
- No direct I/O or subprocess work is performed by this function itself other than calling the underlying helpers; however, side effects result from those helpers:
    - Disk I/O: underlying helpers create and remove temporary files (source file, output binary).
    - Process execution: invokes external compiler binaries (musl-gcc or diet/gcc) via subprocess; stdout/stderr are captured by the helpers.
    - No network calls, no persistent global state mutations introduced by this function itself.

## Control Flow:
flowchart TD
    A[Start: call compile(code)] --> B[Call compile_musl(code)]
    B --> C{compile_musl returns or raises}
    C -- returns bytes --> D[Return bytes to caller]
    C -- raises CompilerNotFoundError --> E[Call compile_diet(code)]
    E --> F{compile_diet returns or raises}
    F -- returns bytes --> D
    F -- raises CompilerNotFoundError --> G[Raise CompilerNotFoundError('No suiteable C compiler was found.')]
    C -- raises other exception (AssertionError/OSError/...) --> H[Propagate that exception to caller]
    F -- raises other exception (AssertionError/OSError/...) --> H

## Examples:
- Typical usage with fallback handling:
    try:
        c_source = 'int main(void){return 0;}\\n'
        binary_bytes = compile(c_source)
        # binary_bytes is the compiled executable; e.g., write to disk or embed into a bundle
        with open('program_static', 'wb') as f:
            f.write(binary_bytes)
    except CompilerNotFoundError as e:
        # Neither musl nor diet toolchains were found; inform the user or provide installation steps
        print("No suitable C compiler available:", e)
    except AssertionError as e:
        # Compilation attempted but failed (compiler returned non-zero); e contains compiler stderr
        print("Compilation failed:", e)
    except (OSError, FileNotFoundError) as e:
        # Environment or I/O error while attempting compilation
        print("Environment error while compiling:", e)

Notes:
- This function intentionally only catches CompilerNotFoundError from the first attempt in order to try the fallback; all other exceptions from the helpers (including compilation failures and OS errors) are intentionally propagated to preserve their original diagnostics.
- If a caller needs to know which toolchain produced the binary or detailed diagnostics about missing binaries, it should either call compile_musl/compile_diet directly or resolve tool availability prior to calling this helper.

## `src.exodus_bundler.launchers.compile_diet` · *function*

## Summary:
Finds the external "diet" and "gcc" executables and compiles the provided C source into a static binary by delegating to the shared compile_helper, returning the compiled executable bytes.

## Description:
- Known callers:
    - No explicit callers were discovered in the supplied repository snapshot. Typical callers are higher-level bundler or launcher code that programmatically generate C source and require a compiled, self-contained binary for execution or bundling.
- Typical trigger/context:
    - Invoked when the system needs to compile a C snippet using the "diet" toolchain (with "gcc" also present) to produce a static, optimized executable image.
- Why this logic is extracted:
    - This function encapsulates the specific tool-resolution policy and the decision to require both "diet" and "gcc" before attempting compilation. It keeps caller code concise by deferring the full compile lifecycle (temp files, process invocation, cleanup, error handling) to compile_helper, while enforcing the precondition that both compilers must be locatable before proceeding.

## Args:
    code (str)
        - C source code to compile.
        - Must be a text string (not bytes). The string is forwarded to compile_helper unchanged.
        - There are no default values.
        - Interdependencies:
            * This function assumes compile_helper accepts the same code string and an initial argv list; compile_diet supplies [diet_path, 'gcc'] as the initial argv.

## Returns:
    bytes
    - The raw bytes of the compiled executable produced by compile_helper.
    - Edge cases:
        * If compile_helper succeeds, a bytes object containing the full binary is returned.
        * This function does not return partially compiled output; failures during compilation will surface as exceptions (see Raises).

## Raises:
    CompilerNotFoundError
        - Raised when either the "diet" executable or the "gcc" executable cannot be located (i.e., find_executable returned None for either).
        - Message provided by the current implementation: 'The diet compiler was not found.' (Note: the message is static in the implementation and does not distinguish which binary is missing.)
    AssertionError (propagated)
        - If compile_helper detects a non-zero compiler exit code it asserts and raises AssertionError with the compiler stderr text. compile_diet does not catch this, so callers should be prepared to handle it.
    OSError / FileNotFoundError / other subprocess or I/O errors (propagated)
        - Underlying operations in find_executable or compile_helper (temporary file operations, process creation) may raise OS-level exceptions which are not caught here and will propagate to the caller.

## Constraints:
- Preconditions:
    - The runtime environment must permit looking up executables on PATH (find_executable must be callable and functional).
    - The caller must pass valid C source text as a str in the code parameter.
    - Both "diet" and "gcc" must be resolvable via the configured find_executable; otherwise CompilerNotFoundError is raised.
- Postconditions:
    - If the function returns normally, the returned value is bytes representing a compiled static executable produced by the resolved "diet" / "gcc" toolchain (as returned by compile_helper).
    - If an exception is raised, no binary bytes are returned and any temporary resources used by compile_helper are cleaned up by that helper.

## Side Effects:
- Calls find_executable twice; depending on the module's find_executable implementation this may read/os.environ or mutate PATH (the find_executable in this module may set a default PATH if missing).
- Delegates work to compile_helper which:
    - Writes temporary files (source and output) to disk.
    - Spawns external processes (the compilers) and captures their stdout/stderr.
    - Removes temporary files in its cleanup path.
- No network I/O or persistent global state (beyond any modifications compile_helper or find_executable perform) is introduced by compile_diet itself.

## Control Flow:
flowchart TD
    A[Start: compile_diet(code)] --> B[find_executable('diet')]
    B --> C[find_executable('gcc')]
    C --> D{Either diet or gcc is None?}
    D -- Yes --> E[Raise CompilerNotFoundError('The diet compiler was not found.')]
    D -- No --> F[Call compile_helper(code, [diet_path, 'gcc'])]
    F --> G[compile_helper returns bytes or raises AssertionError/OSError]
    G --> H[Return compiled bytes] 
    E --> I[Exception propagates to caller]

## Examples:
- Typical successful usage:
    Try to compile C source and obtain binary bytes; handle environment error and compilation failure.
    try:
        binary = compile_diet(c_source_text)
        # binary is a bytes object containing the compiled static executable
        # e.g., write to disk or embed into a bundle
        with open('program_static', 'wb') as f:
            f.write(binary)
    except CompilerNotFoundError as e:
        # The environment does not have the required toolchain; notify user or fallback
        print("Required compiler not available:", e)
    except AssertionError as e:
        # Compilation failed; e contains the compiler stderr message
        print("Compilation failed:", e)
    except (OSError, FileNotFoundError) as e:
        # Filesystem or process creation error
        print("Environment error while compiling:", e)

Notes:
- The CompilerNotFoundError message is static in the current implementation and may not indicate which executable was missing when both are checked; callers that need a precise message may inspect the environment before calling or re-resolve the tools for finer diagnostics.
- Because compile_helper appends flags such as '-static' and '-O3' before invoking the compiler, compilation can fail on systems without static linking support or missing static libraries; such failures surface as AssertionError from compile_helper.

## `src.exodus_bundler.launchers.compile_helper` · *function*

## Summary:
Compiles C source text into a static optimized binary by invoking an external compiler and returns the produced binary as bytes.

## Description:
This helper writes the provided C source code to a temporary .c file, invokes an external compiler process (using the supplied argument list augmented with '-static' and '-O3'), and returns the compiled executable's bytes.

Known callers:
- No direct callers were provided in the supplied context. Typical callers are higher-level bundler/launcher code that generate or assemble C source programmatically and need to produce a self-contained executable image.

Why this logic is extracted:
- The function encapsulates the full lifecycle for compiling ephemeral C source: create temporary files, write source, construct and run the compiler command, check the compiler exit status, read the produced binary, and guarantee cleanup. Extracting this logic prevents repeated temporary-file/process-management code and centralizes error handling and cleanup.

## Args:
    code (str):
        - C source code to compile.
        - Must be a text string (not bytes). The function writes this string to a temporary file using text mode.
    initial_args (list[str] or tuple[str, ...]):
        - The argv list passed to the compiler process. The first element must be an executable name or path (for example 'gcc' or '/usr/bin/gcc').
        - The function will append ['-static', '-O3', input_filename, '-o', output_filename] to this list before invoking the compiler.
        - The function does not validate compiler flags beyond concatenation; the caller is responsible for supplying any required flags (e.g., language standard) if needed.

## Returns:
    bytes
    - The raw contents of the compiled output file (the produced binary), read in binary mode.
    - On success, a bytes object containing the entire compiled executable is returned.
    - The function never returns partial or text output from the compiler; compiler stdout/stderr are captured but not returned.

## Raises:
    AssertionError
        - Raised when the compiler process exits with a non-zero return code.
        - The assertion message includes the compiler stderr decoded as UTF-8: 'There was an error compiling: %s' % stderr.decode('utf-8')
    OSError / FileNotFoundError (propagated)
        - File-system operations (tempfile creation, open(), read(), os.remove()) and process creation may raise standard I/O or OS-level exceptions; these are not caught by the function and will propagate to the caller.
    CalledProcessError is not raised explicitly by this function (the code uses assert), so callers should handle AssertionError for compilation failures.

## Constraints:
Preconditions:
    - The caller must provide valid C source text in code.
    - initial_args must be a sequence acceptable to subprocess.Popen (first element must identify an executable accessible via PATH or absolute path).
    - The running environment must permit creating temporary files and executing subprocesses.

Postconditions (guarantees after return or raise):
    - The two temporary files created (input source and output binary) are removed in the finally block whether compilation succeeded or failed.
    - If the function returns normally, the returned bytes represent the content of the output file that existed at the time it was read.

## Side Effects:
    - Writes two temporary files to the local filesystem:
        * a temporary input source file with suffix '.c'
        * a temporary output file for the produced binary
    - Invokes an external process via subprocess.Popen with stdout/stderr captured (no output is printed by this function).
    - No network calls, no modification of global variables, and no persistent state changes beyond the temporary filesystem activity (which is cleaned up).

## Control Flow:
flowchart TD
    Start --> CreateTempInput
    CreateTempInput --> CreateTempOutput
    CreateTempOutput --> WriteSource
    WriteSource --> BuildArgs
    BuildArgs --> RunCompiler
    RunCompiler --> Communicate
    Communicate --> CheckReturnCode
    CheckReturnCode -->|0 (success)| ReadOutput
    CheckReturnCode -->|non-zero| AssertionError
    ReadOutput --> ReturnBytes
    AssertionError --> Cleanup
    ReturnBytes --> Cleanup
    Cleanup --> End

## Examples:
Example (typical usage):
    # Prepare simple C program and compile with 'gcc' present in PATH.
    c_src = r'''
    #include <stdio.h>
    int main(void) {
        puts("hello");
        return 0;
    }
    '''
    try:
        binary_bytes = compile_helper(c_src, ['gcc'])
        # binary_bytes now contains the compiled static executable bytes
        # Example: write to disk or embed in a bundle
        with open('hello_static', 'wb') as f:
            f.write(binary_bytes)
    except AssertionError as e:
        # Compilation failed: e contains the compiler stderr text
        print("Compilation failed:", e)
    except (OSError, FileNotFoundError) as e:
        # Filesystem or execution problem (e.g., 'gcc' not found)
        print("Environment error:", e)

Notes and caveats:
    - The function forces '-static' and '-O3' in the compiler invocation. On systems without static linking support or without static libraries installed, compilation may fail.
    - Because the function asserts on non-zero compiler exit code, callers should catch AssertionError to handle compiler errors. If you prefer raising a different exception type, wrap calls to this function accordingly.

## `src.exodus_bundler.launchers.compile_musl` · *function*

## Summary:
Wraps an external musl-based C compiler lookup and compiles the provided C source into a static executable, returning the compiled binary bytes.

## Description:
- Known callers and context:
    - Higher-level bundler/launcher code that programmatically generates C source and needs a statically-linked executable built with musl for portability or sandboxing.
    - Typical pipeline stage: source-generation → call compile_musl(code) to produce executable bytes → embed or bundle the returned binary.
- Why this function exists:
    - Responsibility boundary: select the musl-capable compiler executable ("musl-gcc") and delegate the full compile lifecycle to a shared helper (compile_helper). This keeps compiler-resolution logic separate from the complex temporary-file, subprocess, and cleanup logic that compile_helper implements. It prevents duplicated path-resolution code across callers.

## Args:
    code (str)
        - C source code text to compile.
        - Must be a Unicode text string (not bytes). The string is written to a temporary .c file by the underlying compile_helper.
        - No other parameters; the function always attempts to use the first available "musl-gcc" executable found on PATH.

## Returns:
    bytes
    - The raw contents of the compiled executable (the produced binary), as returned by compile_helper.
    - On success, a bytes object containing the entire compiled static executable is returned.
    - There are no other return-value variants.

## Raises:
    CompilerNotFoundError
        - Raised when a "musl-gcc" executable cannot be found on the system PATH.
        - Exact message raised by this function: "The musl compiler was not found."
    AssertionError
        - Propagated from compile_helper when the invoked compiler process exits with a non-zero return code.
        - The AssertionError message includes the compiler stderr decoded as UTF-8 (e.g., "There was an error compiling: <compiler-stderr>").
    OSError / FileNotFoundError (propagated)
        - Filesystem or process creation errors raised by compile_helper (temporary file creation, read/write, subprocess invocation) are not caught and will propagate.

## Constraints:
- Preconditions:
    - Caller must supply valid C source text in code.
    - The environment must allow creating temporary files and spawning subprocesses.
    - The system PATH must contain a working musl-gcc executable for successful compilation.
- Postconditions:
    - If the function returns normally, the returned bytes represent the compiled executable as it existed when read; compile_helper guarantees the temporary files used for compilation are removed as part of its cleanup.
    - If an exception is raised, no persistent temporary files remain (cleanup is performed by compile_helper), and the exception describes the failure cause (missing compiler vs. compile-time error vs. OS-level error).

## Side Effects:
- Disk I/O: the underlying compile_helper creates at least two temporary files (a .c source input and an output binary) and removes them during cleanup.
- Process execution: invokes an external compiler process (musl-gcc) via subprocess; the function captures compiler stdout/stderr but does not print them.
- No network I/O, no global state mutation, and no long-lived external side effects (temporary files are deleted).

## Control Flow:
flowchart TD
    A[Start: call compile_musl(code)] --> B{find_executable('musl-gcc') found?}
    B -- no --> C[Raise CompilerNotFoundError("The musl compiler was not found.")]
    B -- yes --> D[Call compile_helper(code, [musl_path])]
    D --> E{compile_helper returns or raises}
    E -- returns bytes --> F[Return compiled bytes to caller]
    E -- raises AssertionError --> G[Propagate AssertionError (compile error)]
    E -- raises OSError/FileNotFoundError --> H[Propagate OS-level error]
    F --> I[End]
    G --> I
    H --> I

## Examples:
- Typical usage with error handling (illustrative):
    try:
        # compile a generated C program into a static musl-linked executable
        c_source = 'int main(void){return 0;}\n'
        binary = compile_musl(c_source)
        # binary is bytes of the compiled executable; caller may write it to disk or embed it
    except CompilerNotFoundError as e:
        # musl-gcc is not installed or not on PATH
        print("Musl compiler not available:", e)
    except AssertionError as e:
        # Compilation failed; e contains compiler stderr text
        print("Compilation failed:", e)
    except (OSError, FileNotFoundError) as e:
        # Filesystem or subprocess execution problem
        print("Environment error while compiling:", e)

## `src.exodus_bundler.launchers.construct_bash_launcher` · *function*

## Summary:
Renders and returns the text of a POSIX shell launcher script by preparing template context (linker dirname/basename, library path, executable, and a normalized full_linker flag) and delegating to the templating engine.

## Description:
This function prepares the specific variables required by the 'launcher.sh' template and calls the templating layer to produce the final launcher script text. It performs small, deterministic transformations (path splitting and boolean normalization) and does not perform any file I/O or process execution itself.

Known callers:
    - No call sites were provided in the supplied context. To locate actual callers, search the repository for references to this function name.
    - Typical call sites in a bundling system would be packaging or deployment routines that need to produce an on-disk launcher script which embeds linker and runtime paths prior to packaging or distribution.

Why this logic is a separate function:
    - Centralizes the mapping from high-level parameters to template variables so callers don't need to know template internals.
    - Keeps template rendering isolated to a single place so different callers can reuse consistent launcher generation.
    - Simplifies unit testing by allowing tests to assert on returned template text without touching the filesystem.

## Args:
    linker (str):
        Path to the linker program that the launcher should reference. Examples: "/usr/bin/ld", "/opt/custom/ld", or "ld".
        - Behavior: os.path.split(linker) is used to produce (linker_dirname, linker_basename).
        - If linker has no directory component (e.g., "ld"), linker_dirname becomes an empty string and linker_basename becomes the full original string.
        - If linker is not a string-like object (e.g., None), os.path.split will raise a TypeError; such exceptions propagate.
    library_path (str):
        Path to the runtime library directory the launcher should use or expose (for example, a bundled lib directory). Forwarded unchanged to the template context.
    executable (str):
        Path or name of the executable the launcher will invoke. Forwarded unchanged to the template context.
    full_linker (bool, optional):
        Flag indicating whether the linker should be treated as a "full" linker. Default is True.
        - Internally normalized to the string 'true' if truthy, otherwise 'false' (lowercase).
        - Note: non-boolean truthy/falsy values are coerced by Python truthiness rules before normalization.

## Template variables passed:
    The function calls render_template_file('launcher.sh', ...) with the following keyword variables:
        - linker_basename: str (tail component from os.path.split(linker))
        - linker_dirname: str (head component from os.path.split(linker); may be empty)
        - library_path: str (as passed)
        - executable: str (as passed)
        - full_linker: str ('true' or 'false')

## Returns:
    str (or whatever render_template_file returns):
        The rendered template result produced by render_template_file for the 'launcher.sh' template using the context above.
        - Typically a Unicode string that is the content of a shell script.
        - This function does not validate or post-process the returned value; non-string returns from render_template_file are returned unchanged.
        - Edge cases:
            * If linker == "" then linker_dirname == "" and linker_basename == "" in the template context.
            * If render_template_file returns None or another non-string, the caller will receive that value.

## Raises:
    - Propagates any exception raised by os.path.split or render_template_file. Examples that may occur (originating from called functions):
        * TypeError: if linker is not a str/bytes-like object and os.path.split rejects it.
        * FileNotFoundError / OSError: if the template resource is missing or unreadable inside the templating layer.
        * TemplateSyntaxError (or equivalent): if the template contains errors; exact exception type depends on the templating implementation.
    - This function itself does not raise application-specific exceptions.

## Constraints:
Preconditions:
    - All input parameters should be strings except full_linker which should be a boolean. The function will coerce truthiness for full_linker but callers should pass an explicit bool for clarity.
    - The templating system must be able to locate a template named 'launcher.sh'; otherwise rendering will fail.
Postconditions:
    - The function returns exactly the value produced by the templating layer given the prepared context.
    - No input objects are mutated.
    - No files are written, no subprocesses spawned, and no global state is modified by this function alone.

## Side Effects:
    - Indirect I/O: render_template_file may read template files or package resources; any such I/O is performed by the templating layer.
    - No direct filesystem writes, network calls, logging, or subprocess calls are made by this function itself.

## Control Flow:
flowchart TD
    A[Start] --> B[Call construct_bash_launcher(linker,...)]
    B --> C[Split linker -> (linker_dirname, linker_basename) via os.path.split]
    C --> D[Evaluate full_linker truthiness]
    D -->|truthy| E[Set full_linker = 'true']
    D -->|falsy| F[Set full_linker = 'false']
    E --> G[Invoke render_template_file('launcher.sh', context...)]
    F --> G
    G --> H[Return templating result]
    H --> I[End]

## Examples:
Example: Generate launcher text then write it to a target file atomically and make it executable (descriptive steps):
    1. Call construct_bash_launcher("/usr/bin/ld", "/opt/mybundle/lib", "/opt/mybundle/bin/myapp", full_linker=False).
       - Receive a string containing the rendered launcher script (or an exception if rendering failed).
    2. To persist the launcher:
       - Create a temporary file (for example via tempfile.NamedTemporaryFile(delete=False) or tempfile.mkstemp()).
       - Write the returned string to that temporary file using text mode and an appropriate encoding (utf-8).
       - Flush and close the file descriptor.
       - Atomically move (os.replace) the temporary file to the intended destination path (e.g., "/opt/mybundle/bin/launcher").
       - Make the file executable (os.chmod(destination, 0o755)).
    3. Error handling pattern:
       - Wrap the call in try/except to handle exceptions raised by the templating layer (e.g., FileNotFoundError, OSError, template errors).
       - On failure, log the error and abort or fall back to an alternative launcher strategy.

## `src.exodus_bundler.launchers.construct_binary_launcher` · *function*

*No documentation generated.*

