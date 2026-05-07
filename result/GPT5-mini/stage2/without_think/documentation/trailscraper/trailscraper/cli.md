# `cli.py`

## `trailscraper.cli.root_group` · *function*

## Summary:
Configure the process-wide logging levels when the CLI requests verbose output: set the root logger to DEBUG and reduce noise from specific third-party loggers by setting them to INFO.

## Description:
A small initialization helper that mutates logging state based on a single parameter. It centralizes three logger-level adjustments used at CLI startup.

Known callers within the provided code snapshot:
- No direct callers were found in the provided repository snapshot. The intended placement is a CLI startup path immediately after the CLI's command-line parser determines whether verbose mode was requested.

Why this logic is extracted:
- Keeps CLI startup code concise by isolating global logging configuration in one place.
- Enforces a single responsibility: deciding and applying appropriate logger levels when verbose output is desired.

## Args:
- verbose (no explicit type annotation in source): Evaluated with a truthiness test (the function executes its configuration block when "if verbose" evaluates to True). Typical usage passes a boolean value (True or False). Any truthy value will trigger configuration; falsy values leave logging unchanged.

## Returns:
- None. The function performs in-place mutation of logging state and does not return a value.

## Raises:
- The implementation does not explicitly raise exceptions.
- Possible exceptions only arise if the logging subsystem is broken or monkey-patched in a way that makes logging.getLogger or Logger.setLevel raise; such exceptions are not introduced by this code in a normal Python runtime.

## Constraints:
- Preconditions:
  - The standard library logging module is available (normal Python runtime).
  - The caller should pass a value whose truthiness reflects whether verbose logging is desired.
- Postconditions (after the function returns):
  - If the provided argument is truthy:
    - logging.getLogger() (the root logger) will have had setLevel(logging.DEBUG) invoked.
    - logging.getLogger('botocore') will have had setLevel(logging.INFO) invoked.
    - logging.getLogger('s3transfer') will have had setLevel(logging.INFO) invoked.
  - If the provided argument is falsy:
    - No setLevel calls are performed by this function; existing logger levels remain unchanged.
- The function does not configure logging handlers, formatters, or call logging.basicConfig; whether DEBUG-level messages are emitted also depends on existing handlers and their levels.

## Side Effects:
- Global logging state mutation:
  - Calls logging.getLogger() and sets the root logger level to logging.DEBUG (numeric value 10) when verbose is truthy.
  - Calls logging.getLogger('botocore') and logging.getLogger('s3transfer') and sets both to logging.INFO (numeric value 20) when verbose is truthy.
- No file or network I/O is performed.
- No changes to other global state or external services.
- Does not add or modify handlers; if no handlers are configured, changing logger levels may not produce visible output.

## Control Flow:
flowchart TD
    Start --> CheckVerbose
    CheckVerbose{verbose is truthy?}
    CheckVerbose -- Yes --> GetRootLogger[logging.getLogger() -> root logger]
    GetRootLogger --> SetRootLevel[setLevel(logging.DEBUG)]
    SetRootLevel --> GetBotocore[logging.getLogger('botocore')]
    GetBotocore --> SetBotocore[setLevel(logging.INFO)]
    SetBotocore --> GetS3Transfer[logging.getLogger('s3transfer')]
    GetS3Transfer --> SetS3Transfer[setLevel(logging.INFO)]
    SetS3Transfer --> End
    CheckVerbose -- No --> End

## Examples (usage guidance, non-code):
- CLI startup integration:
  1. Parse command-line arguments to determine whether the user requested verbose output (e.g., via a "--verbose" flag).
  2. Call this helper with the parsed flag value. If the flag was present (truthy), the root logger will be set to DEBUG and the two named third-party loggers will be reduced to INFO.
  3. Continue CLI initialization (configure handlers or formatters if necessary). Note: setting logger levels here does not replace the need to configure handlers; to actually see DEBUG messages, ensure at least one handler permits DEBUG output.

- Testing or programmatic use:
  - To enable verbose logging in a test helper, pass a truthy value to the function and then verify logger.level for the root and the two named loggers.
  - To leave global logging untouched during tests, pass a falsy value.

- Error-handling guidance:
  - No explicit error handling is required in normal usage. If your environment modifies the logging API, guard this call with try/except to surface or recover from unexpected exceptions coming from the logging subsystem.

## `trailscraper.cli.download` · *function*

## Summary:
Initiates downloading CloudTrail log files from S3 into a local directory for a specified time window and, optionally, blocks until the local archive contains events up to the requested end time.

## Description:
This function performs two coordinated responsibilities:
1. Parse human-friendly time range inputs into datetime objects and invoke the CloudTrail/S3 download routine for that window.
2. If requested, poll the local log directory and repeatedly attempt downloads until the most recent event timestamp observed locally is strictly greater than the requested end time.

Known callers and typical context:
- Invoked by CLI command handlers that implement a "download" subcommand or programmatic entrypoints that need a local cache of CloudTrail logs for a given time range.
- Typical trigger: user supplies bucket/prefix, optional org/account/region scoping, a time range (from_s, to_s) and optionally requests waiting until logs are caught up.

Why this is a separate function:
- Groups time parsing, a single-call download orchestration, and an optional wait/retry loop into a single unit with a clear responsibility boundary. This keeps CLI parsing and downstream analysis separate from download orchestration and waiting semantics.

## Args:
    bucket (str)
        S3 bucket name containing CloudTrail logs. Must be reachable by configured AWS credentials.
    prefix (str)
        S3 key prefix for CloudTrail objects. May be empty or None to indicate no prefix.
    org_id (str)
        Organization ID used by the downloader for scoping, or None if not used.
    account_id (str)
        AWS account ID to scope downloads; may be None.
    region (str)
        AWS region identifier to scope the download/API calls; may be None.
    log_dir (str)
        Local path to store downloaded logs. Supports ~ expansion; will be expanded with os.path.expanduser.
    from_s (str)
        Human-readable start time (e.g., "2023-01-01", "2023-01-01T00:00", "3 days ago"). Must be parseable by time_utils.parse_human_readable_time.
    to_s (str)
        Human-readable end time. Must be parseable by time_utils.parse_human_readable_time and logically represent a time >= from_s for meaningful behavior.
    wait (bool)
        If True, after the initial download the function repeatedly checks the local directory and re-invokes downloads until the latest observed local event timestamp is strictly greater than the parsed `to` datetime. If False, performs a single download and returns.
    parallelism (any)
        Forwarded to download_cloudtrail_logs to control how the downloader operates in parallel. Exact accepted types/values and semantics are defined by that routine.

Interdependencies:
- from_s and to_s are parsed with time_utils.parse_human_readable_time; their timezone (tzinfo) is used when converting/printing last observed timestamps.
- LocalDirectoryRecordSource(log_dir).last_event_timestamp_in_dir() is expected to return a timezone-aware datetime representing the most recent event; the function assumes this and compares it to parsed to_date.
- The download logic delegates to download_cloudtrail_logs, which (as documented) computes the set of CloudTrail S3 prefixes for the requested accounts/regions/date-range and downloads any missing CloudTrail objects under those prefixes into the provided local directory.

## Returns:
    None

Notes:
- The function does not return details about what was downloaded. A successful return indicates no exceptions were raised and, if wait=True, (barring races) the local latest event timestamp was observed to be strictly greater than the parsed `to` datetime.

## Raises:
    - Exceptions from time_utils.parse_human_readable_time if from_s or to_s are invalid (propagated).
    - Exceptions raised by download_cloudtrail_logs are propagated to the caller (the downloader may raise network, AWS-related, or other runtime exceptions as documented by that routine).
    - Exceptions from LocalDirectoryRecordSource(...).last_event_timestamp_in_dir() (e.g., filesystem access errors) are propagated.
    - TypeError: if last_event_timestamp_in_dir() returns None, the comparison `last_timestamp <= to_date` will raise a TypeError.
    - ValueError: if last_event_timestamp_in_dir() returns a naive datetime (tzinfo is None), calling last_timestamp.astimezone(to_date.tzinfo) may raise ValueError.
    - Note: The function does not catch or translate these exceptions; callers should handle them.

## Constraints:
Preconditions:
    - AWS credentials and network connectivity must be available to download_cloudtrail_logs.
    - log_dir must be a path that can be expanded and is writable by the downloader.
    - from_s and to_s must be parseable; callers should prefer timezone-aware inputs or ensure consistent timezone semantics.
    - LocalDirectoryRecordSource(log_dir).last_event_timestamp_in_dir() should return a timezone-aware datetime (not None) for valid waiting behavior.

Postconditions:
    - download_cloudtrail_logs is invoked at least once with parsed from_date and to_date.
    - If wait=True and the function returns normally, the last observed local event timestamp was strictly greater than the parsed to_date at the time of the final check.
    - If wait=True and logs never arrive, the function will loop indefinitely (see Side Effects / Risks).

## Side Effects:
    - Network I/O: download_cloudtrail_logs will compute CloudTrail S3 prefixes for the requested scope and download any missing objects into `log_dir`.
    - Filesystem writes to `log_dir` (new or updated CloudTrail log files).
    - Console output via click.echo when wait=True and logs are behind the requested `to` time.
    - Periodic sleeping (time.sleep(60)) between retries when waiting.
    - Repeated calls to download_cloudtrail_logs during wait; may result in repeated network and S3 requests.

Operational risks:
    - If LocalDirectoryRecordSource.last_event_timestamp_in_dir() returns None or a naive datetime, this function may raise TypeError or ValueError.
    - If logs never reach the requested `to` time, wait=True causes an infinite loop that repeatedly downloads and sleeps; callers should guard against unbounded blocking (e.g., run in background, add external timeout).

## Control Flow:
flowchart TD
    A[Start] --> B[expanduser(log_dir)]
    B --> C[parse from_s -> from_date]
    C --> D[parse to_s -> to_date]
    D --> E[call download_cloudtrail_logs(log_dir, bucket, prefix, org_id, account_id, region, from_date, to_date, parallelism)]
    E --> F{wait is True?}
    F -- No --> G[Return None]
    F -- Yes --> H[last_timestamp = LocalDirectoryRecordSource(log_dir).last_event_timestamp_in_dir()]
    H --> I{last_timestamp is None?}
    I -- Yes --> X[TypeError will be raised on comparison -> propagate]
    I -- No --> J{last_timestamp <= to_date ?}
    J -- No --> G
    J -- Yes --> K[click.echo status with last_timestamp.astimezone(to_date.tzinfo)]
    K --> L[sleep 60s]
    L --> E2[call download_cloudtrail_logs(...) again]
    E2 --> H
    X --> End[Exception propagates]

## Examples:
- Non-blocking download:
    - Caller parses CLI args then calls download(..., wait=False, ...). The function will perform one download attempt and return. Caller inspects `log_dir` to see downloaded files or to start processing immediately.

- Blocking until logs caught up:
    - Caller calls download(..., wait=True, ...). The function:
        - Parses times, calls the downloader, then checks the latest event timestamp in `log_dir`.
        - If the latest is <= requested end time, it prints a status line with the observed timestamp (converted to the end-time tzinfo), sleeps 60 seconds, re-invokes the downloader, and repeats until local logs are newer than `to`.
    - Example of defensive invocation pattern:
        - Run this function from orchestration code that enforces an overall timeout or runs it in a separate worker thread/process. Wrap the call in try/except to handle parsing, network, and filesystem exceptions. If you expect empty directories initially, either ensure the directory is seeded with at least one event timestamped earlier than `to` or be prepared to handle TypeError/ValueError as described above.

- Error-handling guidance:
    - Treat exceptions from the downloader as potentially transient; implement caller-side retry/backoff or orchestration timeouts as appropriate. For timestamp normalization issues, inspect the local directory contents and ensure last_event_timestamp_in_dir() returns valid timezone-aware datetimes.

## `trailscraper.cli.select` · *function*

## Summary:
Load CloudTrail records from a local directory or the CloudTrail API, filter them by timeframe and optional assumed-role ARN(s), and print a JSON object with the selected records' original payloads to stdout; the function itself returns None.

## Description:
This function performs the CLI-facing orchestration for selecting CloudTrail events:
- Expands the provided log_dir path (os.path.expanduser).
- Parses human-readable start/end time strings into datetime objects via time_utils.parse_human_readable_time.
- Loads parsed Record objects either:
  - from the AWS CloudTrail API via CloudTrailAPIRecordSource().load_from_api(from_date, to_date) when use_cloudtrail_api is True, or
  - from local CloudTrail delivery files via LocalDirectoryRecordSource(log_dir).load_from_dir(from_date, to_date) when use_cloudtrail_api is False.
- Calls filter_records(records, filter_assumed_role_arn, from_date, to_date) to apply timeframe and assumed-role ARN filtering.
- Extracts record.raw_source for each filtered record and prints a JSON object {"Records": [...] } to stdout using click.echo(json.dumps(...)).

Why this is separated:
- Provides a single, testable CLI implementation for the record selection + serialization pipeline.
- Keeps CLI argument handling thin while centralizing source selection, filtering, and the canonical output format.

Known callers / usage context:
- Intended as the body logic for a CLI "select" command (click command handler) or to be invoked by scripts/tests that expect JSON printed to stdout.
- Not designed to be called by code that needs the result as a Python object — callers that need programmatic access should call the record sources and filter_records directly.

## Args:
    log_dir (str):
        - Filesystem path string to a directory containing CloudTrail delivery files.
        - Must be a string-compatible value because os.path.expanduser(log_dir) is called unconditionally at function start.
        - Note: even when use_cloudtrail_api is True the function still calls os.path.expanduser(log_dir) — therefore log_dir must be a valid string to avoid a TypeError.
    filter_assumed_role_arn (None | str | Iterable[str]):
        - Passed directly to filter_records as arns_to_filter_for.
        - Preferred: supply None to disable ARN filtering, or supply an explicit iterable of ARN strings (e.g., ["arn:..."]).
        - Warning: passing a bare string (e.g., "arn:aws:...") will be treated as an iterable of characters; wrap single-ARN values in a list to avoid that pitfall.
    use_cloudtrail_api (bool):
        - When True, the function loads records via CloudTrailAPIRecordSource().load_from_api(from_date, to_date).
        - When False, it loads from LocalDirectoryRecordSource(log_dir).load_from_dir(from_date, to_date).
    from_s (str):
        - Human-readable start time string parsed by time_utils.parse_human_readable_time (dateparser-based).
        - parse_human_readable_time may return a timezone-aware datetime or None when parsing fails; select does not validate the returned value.
    to_s (str):
        - Human-readable end time string parsed the same way as from_s.

Interdependencies and type notes:
- from_s and to_s must parse into datetime objects comparable with the record-source methods and with each other; mixing timezone-aware and naive datetimes can raise TypeError during comparisons downstream.
- filter_assumed_role_arn must be None or an iterable of strings as expected by filter_records; wrapping single strings in a list is recommended.

## Returns:
    None
    - The function writes a single JSON string to stdout via click.echo.
    - Printed JSON format: {"Records": [record1_raw_source, record2_raw_source, ...]}
        - Each recordN_raw_source is the record.raw_source attribute of a filtered Record object (typically a mapping/dict containing the original CloudTrail JSON for that event).
    - If no records match the filters, the printed JSON contains "Records": [].
    - The function does not return Python objects to the caller.

## Raises:
The function does not internally catch exceptions from its dependencies. Callers should expect these exceptions (non-exhaustive):
    - TypeError:
        * If log_dir is None or not string-like, os.path.expanduser(log_dir) will raise TypeError (expanduser expects a string or os.PathLike).
        * If parse_human_readable_time returns None and downstream code attempts datetime comparisons, TypeError may occur.
    - ValueError:
        * Can originate from downstream parsing functions (e.g., malformed timestamps in records).
    - boto3 / botocore exceptions:
        * When use_cloudtrail_api is True, creating clients or paginating LookupEvents may raise authentication, permission, throttling, or network-related exceptions.
    - FileNotFoundError / OSError:
        * When use_cloudtrail_api is False, LocalDirectoryRecordSource may raise filesystem-related errors if the directory is unreadable or os.walk fails.
    - json.JSONDecodeError:
        * If any record.raw_source or log file payload is invalid JSON at lower layers, this may propagate during parsing or when constructing the raw_source values.
    - KeyError / AttributeError:
        * If records contain unexpected shapes or None values (CloudTrailAPIRecordSource.load_from_api may include None entries returned by _parse_record), filter_records or the list comprehension that accesses record.raw_source may raise AttributeError or TypeError.
    - TypeError from json.dumps:
        * If record.raw_source contains non-JSON-serializable values, json.dumps will raise TypeError.

Important behavior note:
- CloudTrailAPIRecordSource.load_from_api may return a list containing None elements (when _parse_record could not parse an event). select forwards the returned list to filter_records without pre-filtering None entries — callers should be aware that None entries may cause filter_records or the record.raw_source access to raise exceptions.

## Constraints:
Preconditions:
    - log_dir must be a string-like path (even if the API branch will be used) because os.path.expanduser is invoked unconditionally.
    - If using the API branch: boto3 must be configured and credentials must permit LookupEvents (or callers must accept API errors).
    - from_s and to_s should parse successfully into datetime objects compatible with record-source methods (prefer timezone-aware UTC datetimes).
    - filter_assumed_role_arn should be None or an explicit iterable of ARN strings.

Postconditions:
    - The function prints a JSON object with key "Records" to stdout containing the raw_source values of records that passed filter_records.
    - No module-level mutable state is altered by select.

## Side Effects:
    - Writes to stdout via click.echo(json.dumps(...)).
    - Possible network I/O when use_cloudtrail_api is True (AWS CloudTrail LookupEvents).
    - Possible filesystem I/O when use_cloudtrail_api is False (reading gzip JSON files via LocalDirectoryRecordSource and its LogFile readers).
    - Lower-level components may emit logging; select itself does not log.

## Control Flow:
flowchart TD
    Start --> Expand[log_dir = os.path.expanduser(log_dir)]
    Expand --> ParseFrom[from_date = parse_human_readable_time(from_s)]
    ParseFrom --> ParseTo[to_date = parse_human_readable_time(to_s)]
    ParseTo --> Branch{use_cloudtrail_api?}
    Branch -- True --> API[records = CloudTrailAPIRecordSource().load_from_api(from_date,to_date)]
    Branch -- False --> Local[records = LocalDirectoryRecordSource(log_dir).load_from_dir(from_date,to_date)]
    API --> AfterLoad[records obtained (may contain None entries)]
    Local --> AfterLoad
    AfterLoad --> Filtered[filtered_records = filter_records(records, filter_assumed_role_arn, from_date, to_date)]
    Filtered --> MapRaw[filtered_records_as_json = [record.raw_source for record in filtered_records]]
    MapRaw --> Dump[json_payload = json.dumps({"Records": filtered_records_as_json})]
    Dump --> Echo[click.echo(json_payload)]
    Echo --> End

Notes:
- Any step may raise exceptions propagated from the underlying helpers; select contains no try/except handlers.
- The list comprehension assumes filtered_records contains objects with a raw_source attribute; if filtered_records contains unexpected values (None or primitive types), the comprehension may raise AttributeError or TypeError.

## Examples:
1) Local-directory selection (happy path)
    - Ensure times parse to datetimes and directory exists:
        select("~/cloudtrail-logs", None, False, "2021-06-01T00:00Z", "2021-06-02T00:00Z")
    - If an invalid time string is provided or log_dir is wrong, wrap in try/except to handle parse or filesystem errors.

2) CloudTrail API selection with an ARN filter (preferred form)
    - Pass a valid log_dir string even if it will not be used, because expanduser is called:
        select("~/.irrelevant", ["arn:aws:iam::123456789012:role/MyRole"], True, "2021-06-01T00:00Z", "2021-06-02T00:00Z")
    - Note: supply the ARN as a one-element list to avoid it being treated as an iterable of characters.

3) Defensive integration guidance
    - If you require the selected records in-memory (not printed), call the record source and filter_records directly:
        from trailscraper.record_sources.local_directory_record_source import LocalDirectoryRecordSource
        records = LocalDirectoryRecordSource("~/cloudtrail-logs").load_from_dir(start_dt, end_dt)
        filtered = filter_records(records, ["arn:..."], start_dt, end_dt)
    - In CLI automation, capture stdout from the process and parse the printed JSON.

## `trailscraper.cli.generate` · *function*

## Summary:
Read a CloudTrail JSON payload from standard input, extract and parse the "Records" array into Record objects, generate an IAM policy document from those records, and write the policy JSON to standard output.

## Description:
- Known callers / invocation context:
    - Intended as a command-line entrypoint that is executed when a user pipes or provides a CloudTrail JSON payload on stdin. Typical usage is from a shell pipeline (for example: cat cloudtrail_payload.json | <tool> generate > policy.json). The function itself has no parameters and is invoked by the process that runs the CLI command.
    - Typical trigger: after obtaining a CloudTrail delivery JSON object (for example a single S3-delivered CloudTrail file or a CloudTrail API delivery payload) a user or automation pipeline pipes that JSON into this CLI to produce a least-privilege policy derived from the events.

- Reason this logic is factored out:
    - Encapsulates the end-to-end mapping of: read CloudTrail payload from stdin -> parse records -> generate policy -> emit JSON. Keeping this sequence in a single small function keeps the CLI entrypoint concise and isolates the IO and orchestration steps from the parsing and policy-generation logic, which live in parse_records and policy_generator.generate_policy respectively.

## Args:
    None.
    - This function reads input exclusively from process stdin (via click.get_text_stream('stdin')) and does not accept parameters.

## Returns:
    None (implicit).
    - Effect: writes the policy JSON string produced by policy.to_json() to standard output via click.echo.
    - No Python value is returned to the caller.

## Raises:
    - json.JSONDecodeError (or more generally ValueError/JSONDecodeError thrown by json.load):
        * Condition: stdin does not contain valid JSON.
    - KeyError:
        * Condition: top-level JSON object does not contain the 'Records' key (the expression json.load(stdin)['Records'] will raise KeyError).
    - TypeError (or other iteration errors propagated from parse_records):
        * Condition: the value stored at ['Records'] is not an iterable suitable for parse_records, or parse_records iterates over inputs that cause iteration-based TypeError.
    - Any exceptions raised by parse_records or the underlying single-record parser:
        * Condition: malformed record fields (e.g., malformed timestamps) that cause parse_records or its _parse_record helper to raise propagate here.
    - Any exceptions raised by policy_generator.generate_policy:
        * Condition: unexpected Record contents or internal errors while constructing the PolicyDocument will propagate.
    - BrokenPipeError (or OSError on write):
        * Condition: writing output via click.echo fails because the stdout pipe was closed by a downstream consumer.

## Constraints:
- Preconditions:
    - stdin must contain a JSON object (i.e., top-level JSON mapping) with a key 'Records' whose value is an iterable (typically a list) of CloudTrail event record objects (JSON mappings).
    - The elements of that iterable should be the raw CloudTrail event dicts expected by parse_records (each element normally containing keys like 'eventSource', 'eventName', 'eventTime', etc.).
    - The runtime environment must have click configured appropriately for CLI IO (standard stdin/stdout available).

- Postconditions:
    - On successful completion, a single policy JSON string (policy.to_json()) has been written to stdout.
    - No return value is produced.
    - If parse_records returns an empty list (no successfully parsed events), the policy generator will still be called with an empty list and its produced policy (representation depends on policy_generator behavior) will be written to stdout.

## Side Effects:
- I/O:
    - Reads from process stdin (click.get_text_stream('stdin')).
    - Writes to process stdout via click.echo.
- No direct file, network, or persistent storage operations are performed by this function itself.
- External calls:
    - Delegates to parse_records(...) which may log warnings for records that fail to parse.
    - Delegates to policy_generator.generate_policy(...) which constructs a PolicyDocument object.
- Global state:
    - The function does not modify module-level or global variables.

## Control Flow:
flowchart TD
    A[Start] --> B[Open stdin via click.get_text_stream('stdin')]
    B --> C[json.load(stdin) => payload]
    C --> D{payload contains 'Records' key?}
    D -- no --> E[KeyError raised -> propagate -> exit]
    D -- yes --> F[records_json = payload['Records']]
    F --> G[records = parse_records(records_json)]
    G --> H{parse_records raises?}
    H -- yes --> I[Exception propagates -> exit]
    H -- no --> J[policy = policy_generator.generate_policy(records)]
    J --> K{generate_policy raises?}
    K -- yes --> L[Exception propagates -> exit]
    K -- no --> M[text = policy.to_json()]
    M --> N[click.echo(text) -> write to stdout]
    N --> O[Success: exit with None]

## Examples:
1) Typical shell pipeline (realistic):
    - Given a CloudTrail delivery JSON file (cloudtrail_payload.json) containing a top-level "Records" array:
        cat cloudtrail_payload.json | trailscraper generate > policy.json
    - Effect: policy.json will contain the policy JSON produced from the parsed events.

2) Handling invalid JSON input:
    - If the stdin stream is empty or contains invalid JSON, the command will fail with a JSON decoding error; wrap invocation in shell logic to detect failures:
        if ! cat cloudtrail_payload.json | trailscraper generate > policy.json 2>/dev/null; then
            echo "policy generation failed — input invalid or processing error"
        fi

3) Programmatic testing note (unit test / harness):
    - To unit-test the orchestration without forking a new process, supply valid JSON to the process stdin when invoking the CLI runner used by click (or run the function inside a click test runner that captures stdout/stderr). Be prepared to catch JSONDecodeError, KeyError, or other propagation from parse_records/policy generation when asserting behavior.

Notes and recommendations:
- Wrap this function's execution in a try/except at the outer CLI layer if you need user-friendly error messages or nonzero exit codes instead of stack traces.
- Because parse_records may propagate exceptions for malformed nested fields (for example malformed timestamps), callers that must be resilient to corrupt events should validate or sanitize input before piping into this function or add higher-level exception handling around the CLI entrypoint.

## `trailscraper.cli.guess` · *function*

## Summary:
Reads an IAM policy JSON from standard input, expands/“guesses” additional statements constrained by the provided prefixes, and writes the resulting policy JSON to standard output.

## Description:
- Known callers and contexts:
    - No direct code callers were discovered in the repository snapshot. This function is intended to serve as the handler for a CLI subcommand (i.e., invoked when a user runs the trailscraper CLI's "guess" command). Typical trigger: a user pipes or redirects a policy JSON into the CLI and invokes the guess subcommand with one or more prefix arguments to limit expansion.
- Why this logic is extracted:
    - Responsibility boundary: encapsulates the CLI-level orchestration for a single pipeline step — read policy JSON from stdin, prepare prefix parameters, call the policy-expansion pipeline (guess_statements), and print the final JSON. Extracting this isolates I/O and argument handling from the core expansion logic (guess_statements and parse_policy_document), keeping the expansion logic testable and reusable without CLI-specific code.

## Args:
    only (iterable[str]):
        - Required.
        - An iterable of strings representing allowed action prefixes. Each element will be title-cased (s.title()) before being passed to the expansion logic.
        - Allowed values: any string values are accepted; semantics of the prefixes (what they match) are defined by the underlying expansion helpers invoked by guess_statements.
        - Interdependencies:
            - The function assumes `only` is iterable. Passing None or a non-iterable will raise a TypeError at runtime when iterating.
            - The resulting allowed_prefixes are forwarded directly to guess_statements and thus must follow any constraints expected by that function (e.g., strings representing service/action prefixes).

## Returns:
    None
    - Effect: the expanded PolicyDocument is serialized and written to stdout using click.echo(policy.to_json()).
    - There is no return value; callers should read stdout to obtain the resulting JSON.
    - Edge-case outputs:
        - If the input policy has no statements, the function will still print a valid PolicyDocument JSON whose "Statement" list is empty (assuming parse_policy_document and guess_statements succeed).
        - If guess_statements returns a PolicyDocument with the same content as the input, that JSON will be printed unchanged (except for any formatting differences from PolicyDocument.to_json()).

## Raises:
    - json.JSONDecodeError (or ValueError on older Python versions)
        - When parse_policy_document fails because stdin does not contain valid JSON.
    - KeyError
        - When parse_policy_document finds the parsed JSON lacks required top-level keys such as 'Statement' or 'Version'.
    - AttributeError / TypeError
        - If the provided policy-like object lacks expected attributes, or if `only` is not iterable and iteration fails.
    - Any exception raised by guess_statements
        - Examples: AttributeError (missing policy.Version), FileNotFoundError / OSError / ValueError — these propagate unchanged from the expansion helpers called by guess_statements.
    - Any exception raised by PolicyDocument.to_json (propagated)
    - Note: this function does not catch or wrap exceptions; all exceptions propagate to the caller (CLI runtime).

## Constraints:
- Preconditions:
    - Standard input (stdin) must contain a valid AWS-style policy JSON object (text) with at least the top-level keys expected by parse_policy_document ('Statement' and 'Version').
    - The `only` parameter must be an iterable of strings (it may be empty).
- Postconditions:
    - On successful completion, stdout contains the JSON serialization of the PolicyDocument returned by guess_statements (PolicyDocument.to_json()).
    - The function does not return a value and does not mutate the input policy object (guess_statements constructs and returns a new PolicyDocument).
    - If an exception occurs, no output is guaranteed; exceptions propagate to the process/CLI runner.

## Side Effects:
- I/O:
    - Reads from standard input (via click.get_text_stream('stdin')) and consumes that stream.
    - Writes to standard output (via click.echo) the JSON produced by PolicyDocument.to_json().
- External state:
    - The function itself does not mutate globals, files, or network state. However, guess_statements or deeper helpers may perform I/O or side-effectful operations; those side effects will propagate.
- No database or persistent store updates are performed directly by this function.

## Control Flow:
flowchart TD
    Start([Start]) --> ReadStdin[Read stdin with click.get_text_stream('stdin')]
    ReadStdin --> Parse[Call parse_policy_document(stdin)]
    Parse --> |success| BuildPrefixes[Transform only -> allowed_prefixes (s.title())]
    Parse --> |parse error| RaiseParseErr[Raise JSONDecodeError/ValueError/KeyError and exit]
    BuildPrefixes --> CallGuess[Call guess_statements(policy, allowed_prefixes)]
    CallGuess --> |success| Serialize[Call policy.to_json()]
    Serialize --> Echo[Write JSON to stdout via click.echo]
    CallGuess --> |error| RaiseGuessErr[Propagate exception from guess_statements and exit]
    Echo --> End([End])

## Examples:
- CLI (pipe) usage (conceptual):
    - A user who has a policy file can pipe it into the CLI and request expansion limited to particular prefixes. The function reads stdin and prints the expanded policy JSON to stdout.
    - Example (shell conceptual): cat policy.json | trailscraper guess <prefix1> <prefix2>
      - Behavior: the policy from policy.json is read from stdin; allowed prefixes are built by title-casing the provided arguments; the expanded policy JSON is printed to stdout.

- Programmatic/testing usage (simulate stdin):
    - To test or call this function from Python without invoking the full CLI, provide a text stream containing policy JSON as the current process stdin (click.get_text_stream reads from process stdin). A test can temporarily replace process stdin with an in-memory text stream containing the policy JSON, then call guess(['s3']) and capture stdout to assert the printed JSON.
    - Error handling guidance:
        - Wrap calls in try/except when running in automated contexts where malformed input or expansion-time I/O errors should be handled gracefully. For CLI usage, allowing exceptions to propagate will typically result in a non-zero exit status and a stack trace printed by the CLI runtime.

## `trailscraper.cli.last_event_timestamp` · *function*

## Summary:
Prints the timestamp of the most recent event found in a local CloudTrail-style log directory.

## Description:
This is a tiny CLI helper that:
- Expands tilde/user-home notation in the provided path, instantiates a LocalDirectoryRecordSource for that directory, obtains the most recent event timestamp from the record source, and writes that timestamp to stdout via click.echo.
- It does not return the timestamp to the caller; the result is emitted to stdout as a side effect.

Known callers:
- No direct callers were discovered in the codebase snapshot provided. The function is defined in the CLI module and is intended as a small helper that can be invoked from CLI wiring (a click command) or called directly from other orchestration code.

Why this is a separate function:
- Responsibility separation: this function handles the user-facing CLI concerns (path expansion and printing) and delegates all file traversal, filename parsing, and record-loading logic to LocalDirectoryRecordSource.last_event_timestamp_in_dir(). Extracting this logic keeps CLI plumbing separate from record-source logic and centralizes the output formatting/side-effect in one place.

## Args:
    log_dir (str): Path to the directory root that contains CloudTrail-delivered log files.
        - Allowed values: any string acceptable to os.path.expanduser and os.walk (absolute or relative path, may include ~).
        - Interdependency: The function assumes LocalDirectoryRecordSource(log_dir) will be able to traverse the directory. For deterministic behavior, supply a path that exists and is readable by the process.

## Returns:
    None
    - The function prints the result of LocalDirectoryRecordSource(log_dir).last_event_timestamp_in_dir() to stdout using click.echo and does not return a value.
    - The printed value is the string-converted representation of the datetime object returned by the underlying record source (click.echo will convert the datetime to a string representation).

## Raises:
This function does not explicitly raise exceptions itself, but it propagates exceptions raised by its constituents:

    - FileNotFoundError, OSError:
        - If the expanded log_dir does not exist or cannot be accessed, os.walk used by LocalDirectoryRecordSource may raise these.
    - StopIteration / IndexError / ValueError:
        - If there are no valid log files under log_dir or the selected latest file has no records, the underlying "last" operation or sequence access in LocalDirectoryRecordSource.last_event_timestamp_in_dir() will raise an iteration/index error.
    - JSONDecodeError, parse-related exceptions:
        - If the latest log file is malformed or record parsing fails while loading records, these exceptions from the LogFile / parse_records pipeline will propagate.
    - TypeError:
        - If LogFile/record timestamp comparisons encounter naive vs aware datetime mismatches or other incompatible types, a TypeError may propagate.

Callers should catch these exceptions if they want to present user-friendly error messages or fallback behavior.

## Constraints:
Preconditions:
    - log_dir must be a string acceptable to os.path.expanduser.
    - For deterministic operation, the directory should contain CloudTrail-style files with filenames that LocalDirectoryRecordSource/LogFile recognize as valid (the record-source expects filename-derived timestamps).
    - Prefer timezone-aware UTC datetimes inside the log files/records to avoid datetime comparison issues in the underlying code.

Postconditions:
    - If the function completes without raising, a single line containing the string representation of the most recent event timestamp (as returned by the record source) will have been written to stdout.
    - No persistent state is modified by this function.

## Side Effects:
    - I/O: writes one line to stdout using click.echo.
    - No file writes, network calls, or global state mutations are performed directly by this function.
    - External calls: instantiates LocalDirectoryRecordSource(log_dir) and invokes its last_event_timestamp_in_dir(), which performs filesystem reads and JSON parsing as appropriate.

## Control Flow:
flowchart TD
    Start[Start: last_event_timestamp(log_dir)] --> Expand[Call os.path.expanduser(log_dir)]
    Expand --> Instantiate[Instantiate LocalDirectoryRecordSource(expanded_log_dir)]
    Instantiate --> GetLast[Call last_event_timestamp_in_dir() on record source]
    GetLast --> Success{last_event_timestamp_in_dir() returned value or raised?}
    Success --> |returned datetime| Echo[click.echo(datetime) -> End (None returned)]
    Success --> |raised exception| Propagate[Exception propagates to caller -> End]

## Examples:
1) Direct call from Python (simple, synchronous):
    - Usage: call the helper directly from code that wants the CLI-style printed output.
    - Behavior: prints the most recent event timestamp or raises on error.
    Example:
    Call last_event_timestamp('~/cloudtrail-logs')
    - Possible outcomes:
        - Prints: 2021-06-01 12:34:56+00:00
        - Raises FileNotFoundError if the directory does not exist
        - Raises parsing exceptions if the most-recent file is malformed

2) Defensive usage with error handling:
    - If invoking from a script that should not crash the process, catch the propagated exceptions and present a friendly message.
    Example:
    Try:
        last_event_timestamp('/var/log/cloudtrail')
    Except FileNotFoundError:
        print('Log directory not found')
    Except Exception as e:
        print('Failed to determine last event timestamp:', e)

Notes:
    - Because this function prints to stdout and returns None, callers that need the datetime object programmatically should call LocalDirectoryRecordSource(log_dir).last_event_timestamp_in_dir() directly instead of using this helper.

