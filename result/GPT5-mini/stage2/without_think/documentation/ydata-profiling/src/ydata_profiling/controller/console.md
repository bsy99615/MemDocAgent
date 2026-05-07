# `console.py`

## `src.ydata_profiling.controller.console.parse_args` · *function*

## Summary:
Parse command-line arguments for the profiling CLI and return an argparse.Namespace containing the parsed options and positional arguments.

## Description:
This function constructs an argparse.ArgumentParser configured for the ydata-profiling command-line interface and parses the provided argument list (or sys.argv if args is None). It centralizes CLI option definitions so other parts of the console entry-point can obtain a validated and well-documented Namespace of options.

Known callers within the provided code excerpt:
    - No direct callers are present in the provided file excerpt. Typically this function is called by the console/CLI entrypoint or a `main` function when launching the profiling tool from the command line (i.e., early in the CLI pipeline, before reading data or creating a report).

Why this logic is a separate function:
    - It isolates CLI parsing from downstream logic (data reading and report generation), making the CLI definition easier to test, maintain, and reuse. The function's responsibility boundary is strictly: define CLI options and perform argument parsing — not to interpret or act on the parsed values.

## Args:
    args (Optional[List[Any]]): A list of command-line arguments to parse (typically a list of strings).
        - Type: Optional[List[Any]]
        - Default: None
        - Behavior:
            * If None, argparse.parse_args() will parse sys.argv[1:] (standard argparse behavior).
            * Practical callers should pass a list of strings (e.g., ['-s', 'input.csv']).
        - Constraints:
            * Elements should be string-like; passing non-iterable or non-string items may raise TypeError or cause parsing to fail (argparse will typically raise SystemExit on type mismatches).

## Returns:
    argparse.Namespace: Namespace with attributes corresponding to the CLI options and positional arguments:
        - version: (handled by argparse's version action; not present on successful return when version is printed because that action exits)
        - silent (bool): True if -s/--silent provided; otherwise False.
        - minimal (bool): True if -m/--minimal provided; otherwise False.
        - explorative (bool): True if -e/--explorative provided; otherwise False.
        - pool_size (int): Number of CPU cores to use (default 0).
        - title (str): Report title (default "Pandas Profiling Report").
        - infer_dtypes (bool): True if --infer_dtypes provided; False by default or set False by --no-infer_dtypes. The two flags share the same destination; the last occurrence wins.
        - config_file (Optional[str]): Path to a YAML config file or None.
        - input_file (str): Positional; path to input file to profile (required).
        - output_file (Optional[str]): Positional; optional output report file path. If None, the CLI help suggests replacing the input file extension with .html, but this function itself only parses and returns None (it does not perform replacement).

    Edge cases:
        - On successful parsing, a Namespace is returned.
        - On parse errors, or when argparse prints help/version, argparse will exit the program by raising SystemExit (see Raises).

## Raises:
    SystemExit:
        - Triggered by argparse when:
            * The provided arguments are invalid (e.g., missing required positional input_file).
            * The user requests help (-h/--help) — argparse prints help and exits.
            * The --version flag is present: argparse's version action prints the program version (using the imported __version__) and exits.
            * Type conversion for options (e.g., non-integer value for --pool_size) fails — argparse will print an error and exit.
        - These are direct effects of calling parser.parse_args(args) (argparse's behavior).

## Constraints:
    Preconditions:
        - The caller should provide args as a list-like of strings or pass None to use the process argv.
        - The environment must have the imported __version__ available (the parser uses it to format --version output); in normal package execution this will be satisfied by the module import.

    Postconditions:
        - Returns an argparse.Namespace with attributes described above.
        - No mutation of global state or filesystem is performed by this function.
        - If parse fails or help/version is requested, the function will not return but instead raise SystemExit (argparse behavior).

## Side Effects:
    - This function has no I/O or persistent side effects by itself.
    - Indirect side effects from argparse.parse_args:
        * Calling parse_args with malformed input or help/version triggers argparse output to stdout/stderr and raises SystemExit.
    - No network, file, or external-state writes occur in this function.

## Control Flow:
flowchart TD
    A[Start parse_args(args)] --> B[Create ArgumentParser]
    B --> C[Add --version action (uses __version__)]
    C --> D[Add -s/--silent flag]
    D --> E[Add -m/--minimal flag]
    E --> F[Add -e/--explorative flag]
    F --> G[Add --pool_size (int, default 0)]
    G --> H[Add --title (str, default "Pandas Profiling Report")]
    H --> I[Add --infer_dtypes (store_true)]
    I --> J[Add --no-infer_dtypes (dest=infer_dtypes, store_false)]
    J --> K[Add --config_file (str, default None)]
    K --> L[Add positional input_file (str, required)]
    L --> M[Add positional output_file (str, nargs='?', default None)]
    M --> N[Call parser.parse_args(args)]
    N --> O{Argument parsing result}
    O -->|Valid args| P[Return Namespace with attributes]
    O -->|Invalid args or -h/--help| Q[argparse prints message and raises SystemExit]
    O -->|--version present| R[argparse prints version (uses __version__) and raises SystemExit]

## Examples:
1) Basic usage from Python code (parse programmatic args and inspect results):
    try:
        ns = parse_args(['input.csv'])
        # ns.input_file == 'input.csv'
        # ns.output_file == None
        # downstream code should decide output path when ns.output_file is None
    except SystemExit as e:
        # argparse prints message to stdout/stderr and exits; handle or re-raise as appropriate
        raise

2) Provide output path and options:
    try:
        ns = parse_args(['-s', '--pool_size', '4', '--title', 'My Report', 'data.csv', 'report.html'])
        # ns.silent == True
        # ns.pool_size == 4
        # ns.title == 'My Report'
        # ns.input_file == 'data.csv'
        # ns.output_file == 'report.html'
    except SystemExit:
        # handle parse failures (e.g., incorrect types, missing required positional)
        pass

3) Conflicting dtype flags:
    ns = parse_args(['--infer_dtypes', '--no-infer_dtypes', 'data.csv'])
    # The flags share the same dest (infer_dtypes); the last one wins.
    # In this example, ns.infer_dtypes == False

Notes:
    - This function only parses and returns arguments; decision logic (e.g., default output filename generation when output_file is None, or how pool_size=0 is interpreted) is expected to be implemented by the caller.
    - The --version action uses the imported __version__ constant for its printed value.

## `src.ydata_profiling.controller.console.main` · *function*

## Summary:
Orchestrates CLI parsing, loads the specified input file into a pandas DataFrame, constructs a ProfileReport using the parsed options, and writes the report to an output file (defaulting to input-with-.html).

## Description:
This function is the high-level console entry point that wires three responsibilities together:
1. Parse command-line or programmatic arguments via parse_args(args).
2. Read the dataset from disk into a pandas.DataFrame via read_pandas.
3. Instantiate ProfileReport with the DataFrame and remaining options, then persist the report via ProfileReport.to_file.

Known callers and typical context:
- Intended to be invoked as the CLI entry point for the ydata-profiling command (e.g., a console script) or called programmatically from Python with a list of argument strings.
- Internally it calls parse_args(args), read_pandas(input_file_path), ProfileReport(...), and p.to_file(...).

Why this is extracted:
- Keeps orchestration separate from argument parsing, data reading, and report generation. The function enforces the responsibility boundary of turning parsed CLI options into concrete I/O and a ProfileReport construction call, while leaving parsing and I/O details to their respective helpers.

## Args:
    args (Optional[List[Any]]): Optional list of arguments to parse (typically list[str]).
        - Type: Optional[List[Any]]
        - Default: None — when None, parse_args will use argparse.parse_args() default behavior (sys.argv[1:]).
        - Notes:
            * Items should be string-like values suitable for argparse.
            * If parse_args raises (e.g., invalid args, help/version requested), that SystemExit propagates and main will not continue.

## Returns:
    None
    - On success the function writes the report to disk and returns None.

## Raises:
    SystemExit:
        - Raised by parse_args(args) when argparse handles invalid arguments, prints help, or prints version; this prevents normal return.

    ValueError:
        - Raised by read_pandas when the input file has a .tar extension; read_pandas explicitly raises ValueError("tar compression is not supported...") for .tar files.

    Any exception raised by read_pandas, ProfileReport construction, or ProfileReport.to_file:
        - These exceptions are not caught here and will propagate to the caller. The function does not fabricate or convert exceptions.

## Constraints:
    Preconditions:
        - parse_args must return a Namespace where vars(parsed_args) contains (at minimum) the keys/attributes "input_file", "output_file", and "silent" — the implementation pops these three keys.
        - The input_file path must refer to a file type supported by read_pandas for successful loading (read_pandas handles many common extensions; .tar is explicitly unsupported).

    Postconditions:
        - If the function returns without raising, a report file exists at the computed output path.
        - If the parsed output_file was None, the output path is computed as str(Path(input_file).with_suffix(".html")).

## Side Effects:
    - File I/O:
        * Reads from disk using pandas readers via read_pandas(input_file).
        * Writes the generated report to disk via p.to_file(Path(output_file), silent=silent).
    - Process behavior:
        * parse_args may print help/version messages and raise SystemExit (typical argparse behavior).
    - No global module-level state is modified by this function itself.

## Control Flow:
flowchart TD
    Start([Start main(args)]) --> Parse[Call parse_args(args)]
    Parse -->|SystemExit on invalid/help/version| ExitSys[(SystemExit raised)]
    Parse --> Vars[kwargs = vars(parsed_args)]
    Vars --> PopInput[Pop "input_file" -> input_path = Path(value)]
    PopInput --> PopOutput[Pop "output_file"]
    PopOutput -->|None| DefaultOutput[Set output_file = str(input_path.with_suffix(".html"))]
    PopOutput -->|not None| UseOutput[Use provided output_file string]
    DefaultOutput --> PopSilent
    UseOutput --> PopSilent
    PopSilent[Pop "silent" -> silent]
    PopSilent --> ReadDF[Call read_pandas(input_path) -> df]
    ReadDF -->|ValueError for .tar or other IO errors| ErrorRead[(Error propagated)]
    ReadDF --> Build[ProfileReport(df, **remaining_kwargs)]
    Build -->|ProfileReport ctor error| ErrorBuild[(Error propagated)]
    Build --> Write[Call p.to_file(Path(output_file), silent=silent)]
    Write -->|to_file error| ErrorWrite[(Error propagated)]
    Write --> End([Return None])

## Examples:
1) Basic invocation — default output (input extension replaced by .html):
    try:
        main(['data.csv'])
        # Behavior:
        # - parse_args returns namespace with input_file='data.csv', output_file=None (if not provided), silent flag value
        # - output file computed as 'data.html' (input basename with .html suffix)
        # - data.csv is read via read_pandas; report written to 'data.html'
    except SystemExit:
        # argparse handled help/version or invalid args and exited
        raise

2) Provide output path and forward additional options (kwargs forwarded to ProfileReport):
    try:
        # Example demonstrates that options parsed by parse_args other than input/output/silent
        # are forwarded to ProfileReport via kwargs.
        main(['--title', 'Sales Report', 'sales.csv', 'sales_report.html'])
        # parse_args sets title='Sales Report'; 'title' ends up in kwargs forwarded to ProfileReport
    except Exception as e:
        # Read or write failure, or ProfileReport errors, will propagate here
        print("Failed to generate profiling report:", e)

Notes for implementers:
- The function converts parsed_args to a dict (vars), then pops three keys. All remaining keys are passed into ProfileReport as keyword arguments; reimplementers must preserve this forwarding behavior.
- Do not swallow exceptions here — design choice is to let callers handle I/O, parsing, or report-generation errors.
- The implementation relies on read_pandas for supported file types and on parse_args for required CLI options.

