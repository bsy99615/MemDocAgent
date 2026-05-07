# `generate_authors.py`

## `misc.generate_authors.drop_recurrences` · *function*

## Summary:
Yields items from the input iterable with duplicate occurrences removed, preserving the order of each element's first appearance.

## Description:
This function scans an input iterable and yields each distinct, hashable item the first time it appears; subsequent occurrences of the same item are skipped. Known callers within the codebase: none discovered during repository inspection (the function appears standalone). Typical usage: invoked in data-processing or author-list generation pipelines where order-preserving deduplication of an incoming sequence is required (e.g., when converting a stream of names into a canonical ordered list without repeats).

Why this logic is extracted into its own function:
- Responsibility boundary: encapsulates a small, reusable utility — order-preserving duplicate filtering — that can be reused anywhere an iterable needs deduplication without changing the input order.
- Avoids inlining duplication-removal logic at call sites and makes the intent explicit (drop repeated occurrences while preserving first-seen order).
- Returns a lazy iterator so callers can consume processed values without constructing an intermediate list unless they choose to.

## Args:
    iterable (iterable): Any iterable of items whose elements are expected to be hashable. The function accepts sequences, generators, iterators, or any object implementing the iterable protocol.
    - Allowed values: any iterable.
    - Important constraint: elements must be hashable (e.g., str, int, tuple of hashables). If an element is unhashable (e.g., list, dict, set), a TypeError will be raised at the point the unhashable element is encountered.

## Returns:
    iterator: A generator/iterator that yields elements from the input iterable in the same order as their first occurrence, with duplicates omitted.
    - The returned object is lazy: elements are produced on iteration, not computed up-front.
    - Possible edge-case return behaviors:
        * If the input iterable is empty, the iterator yields no items.
        * For infinite iterables, the generator will continue yielding unique items until the process is terminated; memory usage may grow unbounded as seen items accumulate.

## Raises:
    TypeError: Raised if an element of the iterable is unhashable when the function attempts to check membership or add it to the internal set (this is raised implicitly by the underlying set operations).
    Note: The function does not explicitly raise other exceptions; exceptions raised by the input iterable during iteration (e.g., StopIteration implicitly signals completion) will propagate to the caller.

## Constraints:
    Preconditions:
    - The caller must pass an iterable.
    - Elements yielded by the iterable should be hashable if the caller wants deduplication to succeed without exceptions.
    - The caller should be aware that the function maintains an internal set of seen items; memory usage is proportional to the number of distinct elements seen so far.

    Postconditions:
    - After iterating to completion, every value yielded was the first occurrence of that value in the input iterable.
    - No value will be yielded twice.
    - The order of yielded items matches the order of their first appearance in the input.

## Side Effects:
    - No I/O is performed (no file, network, stdout/stderr operations).
    - No global state is mutated.
    - Only local in-memory state: an internal Python set that accumulates seen items.
    - No external services are called.

## Control Flow:
flowchart TD
    Start([Start])
    ReadItem[/For each item in iterable/]
    IsSeen{item in seen set?}
    AddAndYield[Add item to set; yield item]
    Continue[/Continue to next item/]
    End([End])

    Start --> ReadItem
    ReadItem --> IsSeen
    IsSeen -- No --> AddAndYield
    AddAndYield --> Continue
    IsSeen -- Yes --> Continue
    Continue --> ReadItem
    ReadItem --> End

## Examples:
- Typical deduplication scenario:
    * Input: a sequence that may contain repeated names in the order they were encountered.
    * Behavior: the function yields each name only when it is first observed, preserving that order for downstream processing (for example, producing an ordered author list without duplicates).

- Memory and infinite streams:
    * Input: an unbounded stream of items that may contain repeats.
    * Behavior: the generator will continue emitting new unique items but will also keep growing its internal set of seen items; for long-running or unbounded streams, callers should consider whether unbounded memory growth is acceptable or whether a bounded deduplication strategy (e.g., time-windowed or probabilistic filters) is required.

- Error handling for unhashable elements:
    * If the input iterable yields a list or dict (which are unhashable), a TypeError will be raised at the moment the function checks membership or attempts to add that element to the set. Callers that may receive unhashable elements should pre-process them (e.g., convert lists to tuples) or handle TypeError exceptions when iterating.

- Consuming the result:
    * Because the function returns a lazy iterator, callers may iterate directly (for item in drop_recurrences(iterable): ...) or materialize a collection (e.g., construct a list) depending on downstream needs and memory constraints.

## `misc.generate_authors.iterate_authors_by_chronological_order` · *function*

## Summary:
Runs git log for a given ref and returns an iterator of author names in chronological (oldest-first) order with duplicate names removed (each name yielded only on its first occurrence).

## Description:
This function invokes the git command-line tool to obtain the commit history for the specified branch/ref, parses the output to extract each commit's author name, and returns a lazy iterator that yields author names in chronological order while removing repeated occurrences (preserving the first time each author appears).

Known callers within the codebase:
- No direct callers were discovered during repository inspection. The function is intended to be used where an ordered, deduplicated list of authors is required (for example, constructing contributor lists or changelog authors), and may be called from higher-level author-generation or reporting pipelines.

Why this logic is factored out:
- Responsibility separation: encapsulates the steps of (1) running the git log command with a particular format, (2) parsing the raw output into author names, and (3) applying order-preserving deduplication. This keeps callers free from subprocess and parsing concerns and returns a lazy iterable for downstream consumption.
- Reuse and clarity: centralizes git invocation and parsing details (format string, encoding, reverse order) so changes to those details are localized to this function.
- Efficiency: subprocess invocation and decoding are performed once; the returned values are produced lazily via the deduplication iterator so callers can iterate without materializing an intermediate list of unique names unless they choose to.

## Args:
    branch (str): A git reference accepted by `git log` (e.g., branch name like 'main', 'master', or commit-ish such as 'HEAD' or 'origin/main').
        - Must be a str. Passing None or a non-str in the argument sequence will raise a TypeError from subprocess internals.
        - The string is passed directly to git; common git ref syntaxes are supported.
        - The current working directory at call time must be a Git repository (or git will emit an error).

## Returns:
    iterator[str]: A lazy iterator that yields author names (str) in chronological order (oldest commit first), with duplicates removed so each author name appears only the first time it is encountered.
    - If no commits are returned by git for the given ref, the iterator yields no items.
    - The iterator is produced by wrapping a generator that extracts the second semicolon-separated field (author name) from each git log line through drop_recurrences; therefore actual yield-time errors (e.g., parsing errors) will surface when the caller iterates.

## Raises:
    FileNotFoundError:
        - If the 'git' executable is not available on PATH, subprocess.run will raise FileNotFoundError.
    TypeError:
        - If branch is not a str (e.g., None) so that the argument sequence passed to subprocess.run contains a non-str element.
    UnicodeDecodeError:
        - If stdout bytes cannot be decoded as UTF-8 when calling decode('utf-8').
    IndexError:
        - If a line in the git output does not contain the expected semicolon-separated fields, accessing split(";")[1] will raise IndexError. This can happen when stdout contains empty lines or unexpectedly formatted lines (for example, if git returned an error message on stdout or the format string did not produce the expected output).
    OSError / Other subprocess-related errors:
        - Other low-level OS errors thrown by subprocess.run (rare) will propagate.

Note: subprocess.run is invoked without check=True, so a non-zero git exit code will not raise CalledProcessError automatically; instead, the function proceeds using whatever stdout content was produced and may raise parsing errors thereafter.

## Constraints:
Preconditions:
    - The caller's current working directory must be inside the target git repository (or pass an absolute/appropriate working directory externally before calling).
    - The provided branch must be a valid git ref (or at least a string acceptable to git log).
    - The environment must have the 'git' executable installed and accessible on PATH.
    - The function expects git log output formatted as "<timestamp>;<author name>;<author email>" per commit (this is enforced by the --format option).

Postconditions:
    - The returned iterator will yield author names in the order of first appearance from oldest to newest commit for the requested branch/ref.
    - No author name will be yielded more than once.
    - The subprocess has been executed and its entire stdout has been decoded and split into lines before any items are yielded; only the deduplication and final yielding are lazy.

## Side Effects:
    - External process invocation: runs the git command-line tool in the current working directory. This may read repository data from disk and consume CPU/time.
    - No files are written, no network calls are made by this function itself, and nothing is printed to stdout/stderr by this function (git's stdout/stderr are captured).
    - No global in-process state is mutated by this function; however, external environment state (e.g., disk reads by git) is involved.
    - Potentially observable behavior: if git writes to stderr (for example, when the ref does not exist), that information is captured but not acted upon by the function.

## Control Flow:
flowchart TD
    Start([Start])
    RunGit[/Run subprocess.run('git','log', branch, --encoding=utf-8, --full-history, --reverse, --format=...)/]
    RunSuccess{Subprocess invocation succeeded?}
    Decode[/Decode stdout bytes with utf-8/]
    Split[/Split decoded text into lines/]
    GenCreate[/Create generator extracting split(";")[1] for each line/]
    ReturnIterator[/Wrap generator with drop_recurrences and return iterator/]
    Iterate[(/When caller iterates:/) For each generated name]
    DedupCheck{Seen before? (drop_recurrences)}
    YieldName[/Yield name if first-seen/]
    Continue[/Continue/]
    ErrorBranch([Errors: FileNotFoundError, UnicodeDecodeError, IndexError, TypeError, or other subprocess errors])
    End([End])

    Start --> RunGit
    RunGit --> RunSuccess
    RunSuccess -- No --> ErrorBranch
    RunSuccess -- Yes --> Decode
    Decode --> Split --> GenCreate --> ReturnIterator --> Iterate
    Iterate --> DedupCheck
    DedupCheck -- No --> YieldName --> Continue --> Iterate
    DedupCheck -- Yes --> Continue --> Iterate
    ErrorBranch --> End
    Continue --> End

## Examples (descriptive, end-to-end):
- Simple consumption:
    * Typical call: request authors for the 'main' branch. The function runs git log for that ref, decodes output, and returns an iterator that yields each author name once, in chronological order (oldest commit author first). A caller can iterate the returned iterator to display or collect author names.

- Error handling pattern:
    * If 'git' is not installed, a FileNotFoundError will be raised at call time; callers that rely on this function on diverse environments should catch FileNotFoundError and provide a fallback (e.g., skip generation or use a precomputed author list).
    * If the git output is unexpectedly formatted (for example, empty lines or git wrote error messages to stdout), the iterator may raise IndexError when iterated; robust callers should handle IndexError (or validate git output prior to consuming the iterator).
    * If repository encoding is not UTF-8, decoding may raise UnicodeDecodeError; callers should either ensure repository encodings are UTF-8 or be prepared to handle UnicodeDecodeError.

- Usage note for large histories:
    * The subprocess run and decode occur synchronously and load git stdout into memory as a single string split into lines. On very large repositories with millions of commits, memory usage may be significant. After that point, deduplication is lazy, but the initial capture is not streaming. For extreme-scale repos, consider an alternative that streams git output and parses lines incrementally.

## `misc.generate_authors.print_authors` · *function*

## Summary:
Writes each unique author name (one per line) for the given git ref to the process stdout stream in the order returned by the underlying author iterator.

## Description:
This function iterates the author names produced by iterate_authors_by_chronological_order(branch) and writes each name as a UTF-8-encoded byte sequence followed by a POSIX newline (b'\n') to sys.stdout.buffer.

Known callers within the codebase:
- No direct callers were discovered in repository inspection. Typical use is in author-generation or reporting pipelines where the program should emit a plain-text list of contributors (one-per-line) to standard output or a piped consumer.

Why this logic is factored out:
- Separation of concerns: printing/IO responsibilities are isolated from the logic that collects and deduplicates author names. This keeps iteration and encoding/printing behavior centralized so callers that need printed output can call this helper rather than duplicating write logic.
- Reuse and clarity: centralizes formatting/encoding decisions (write bytes, append newline) and ensures consistent output for consumers or shell pipelines.

## Args:
    branch (str):
        - A git reference accepted by git log (e.g., 'main', 'HEAD', 'origin/main').
        - Must be a str. Passing a non-str may cause TypeError when the underlying iterator invokes subprocess logic.
        - The current working directory at call time must be a Git repository (this is a precondition of the underlying iterator).

## Returns:
    None
    - The function performs side-effecting writes to sys.stdout.buffer and does not return a value.
    - If the underlying iterator yields no authors, nothing is written and the function returns None.

## Raises:
This function does not raise exceptions directly inside its body beyond those raised by called operations; exceptions from iteration or I/O propagate to the caller:

    - FileNotFoundError:
        - Propagates if the underlying iterate_authors_by_chronological_order triggers subprocess.run and the 'git' executable is not found on PATH.
    - TypeError:
        - May propagate if branch is not a str and that causes subprocess internals to raise TypeError.
    - UnicodeDecodeError:
        - May be raised by the underlying iterator when decoding git output; will surface during iteration if decoding fails.
    - IndexError:
        - May be raised by the underlying iterator when parsing unexpectedly formatted git output; will surface during iteration.
    - UnicodeEncodeError:
        - Raised if author.encode() fails to encode the author string to bytes using the default encoding (UTF-8) — for example, if the string contains unencodable surrogate data in narrow-Python builds or similar pathological cases.
    - BrokenPipeError / OSError:
        - Raised when writing to sys.stdout.buffer if the receiving pipe is closed (common when the program is piped and the consumer exits early) or other low-level I/O errors occur.
    - AttributeError:
        - May be raised if sys.stdout does not expose a buffer attribute (for example, when stdout is replaced by an object lacking buffer); callers that replace stdout should ensure a binary buffer is available.

All exceptions above originate from the called iterator or the sys.stdout.buffer.write calls and are not caught by this function.

## Constraints:
Preconditions:
    - The caller must execute this function from within a directory that is a Git repository (or otherwise ensure the underlying iterator can run git against the intended repo).
    - The branch argument must be a valid git ref string acceptable to git log.
    - sys.stdout must be available and expose a binary buffer attribute (sys.stdout.buffer) that accepts bytes; otherwise an AttributeError will occur.

Postconditions:
    - For each author name yielded by iterate_authors_by_chronological_order(branch), an encoded line (author.encode() followed by b'\n') has been written to sys.stdout.buffer in the same order they are produced by the iterator.
    - The function does not flush stdout explicitly; written bytes may remain buffered until an explicit flush or process termination.
    - The function returns None after iteration completes (or after an exception propagates).

## Side Effects:
    - I/O: writes bytes to sys.stdout.buffer for each author (one line per author).
    - External process side effects are indirect: the underlying iterator runs git as a subprocess; any side effects of that call (disk reads, CPU usage) are external to this function.
    - No files are modified, no network calls are made by this function directly, and no global in-process state is modified by this function.

## Control Flow:
flowchart TD
    Start([Start])
    CallIter[/Call iterate_authors_by_chronological_order(branch) -> iterator/]
    ForEachAuthor{For each author in iterator}
    Encode[/Call author.encode() (bytes)/]
    Write[/sys.stdout.buffer.write(bytes)/]
    WriteNL[/sys.stdout.buffer.write(b'\\n')/]
    Continue[/Continue loop/]
    End([Return None])
    Errors([Errors propagate: FileNotFoundError, IndexError, UnicodeDecodeError, UnicodeEncodeError, BrokenPipeError, AttributeError, OSError])
    Start --> CallIter
    CallIter --> ForEachAuthor
    ForEachAuthor --> Encode --> Write --> WriteNL --> Continue --> ForEachAuthor
    ForEachAuthor -- iterator exhausted --> End
    CallIter -- iterator creation/iteration error --> Errors
    Encode -- encode error --> Errors
    Write -- write error --> Errors

## Examples:
- Basic usage (printing authors to stdout):
    Typical invocation in a program that should emit a contributor list to standard output:
    Call print_authors with a branch/ref (for example, 'main' or 'HEAD'). The program will write one author name per line to stdout in the chronological order provided by the underlying iterator.

- Robust invocation with error handling (descriptive):
    When running in environments where git might be missing or the output may be malformed, wrap the call to print_authors in exception handling to provide fallback behavior or a friendly error message. For example, a caller may catch FileNotFoundError to skip generation when git is not installed, catch BrokenPipeError to exit cleanly when piped consumers terminate early, and catch IndexError or UnicodeDecodeError if git output is unexpected — logging or falling back to a precomputed author list in those cases.

Notes and implementation hints for callers:
    - If you need the output in another stream (not stdout), redirect sys.stdout to an object that exposes buffer (or provide a small wrapper that offers a binary write method) before calling this function.
    - Because this function does not flush after writes, callers that immediately rely on downstream consumers receiving the data should flush sys.stdout (sys.stdout.flush()) or call os.fsync on the underlying file descriptor if needed.
    - For very large repositories, be aware that the underlying iterator may collect git stdout into memory before producing yields; consider a streaming alternative if memory usage is a concern.

