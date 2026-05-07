# `console.py`

## `src.ydata_profiling.controller.console.parse_args` · *function*

## Summary:
Parses command-line arguments for the ydata-profiling console application to configure report generation settings.

## Description:
This function serves as the argument parser for the profiling console interface, extracting user-provided configuration options from the command line. It defines all available command-line flags and positional arguments needed to control the behavior of the profiling process, including input/output file specifications, reporting options, and performance tuning parameters.

The function is extracted into its own component to separate the concerns of argument parsing from the core profiling logic, enabling better testability and maintainability of the console interface.

## Args:
    args (Optional[List[Any]], optional): List of command-line arguments to parse. If None, uses sys.argv. Defaults to None.

## Returns:
    argparse.Namespace: Parsed arguments namespace containing all configured options and file paths.

## Raises:
    SystemExit: Raised by argparse when invalid arguments are provided or when --help is specified.

## Constraints:
    Preconditions:
        - The input_file argument must specify a valid file path that can be read by pandas
        - If output_file is provided, it must be a valid file path for writing
        - The config_file argument, if provided, must point to a valid YAML configuration file
    
    Postconditions:
        - All arguments are validated according to their specified types and constraints
        - Required arguments are present and properly formatted
        - Default values are applied for unspecified optional arguments

## Side Effects:
    - None directly observable from this function
    - May cause program termination via SystemExit if invalid arguments are provided
    - Uses argparse's built-in help/version display mechanisms

## Control Flow:
```mermaid
flowchart TD
    A[Start parse_args] --> B{args provided?}
    B -->|Yes| C[parser.parse_args(args)]
    B -->|No| D[parser.parse_args(sys.argv)]
    C --> E[Return parsed namespace]
    D --> E
```

## Examples:
    # Basic usage with default settings
    parsed_args = parse_args(['data.csv'])
    
    # With explicit output file
    parsed_args = parse_args(['data.csv', 'report.html'])
    
    # With silent flag
    parsed_args = parse_args(['-s', 'data.csv'])
    
    # With minimal configuration
    parsed_args = parse_args(['-m', 'data.csv'])
    
    # With custom title and pool size
    parsed_args = parse_args(['--title', 'My Report', '--pool_size', '4', 'data.csv'])
    
    # With explorative mode and config file
    parsed_args = parse_args(['-e', '--config_file', 'my_config.yaml', 'data.csv'])
    
    # Using version flag
    parsed_args = parse_args(['--version'])
```

## `src.ydata_profiling.controller.console.main` · *function*

## Summary:
Main entry point for the ydata-profiling console application that orchestrates data profiling, report generation, and file output.

## Description:
This function serves as the primary execution controller for the ydata-profiling command-line interface. It coordinates the complete workflow from parsing user-provided arguments, loading input data, generating a statistical profile report, and saving the results to an output file. The function is designed to be called either directly from the command line or programmatically with custom argument lists.

The function is extracted into its own component to encapsulate the end-to-end console workflow, separating it from the argument parsing logic and report generation internals. This modular approach enables clean separation of concerns, facilitates testing of individual components, and provides a clear entry point for the console application.

## Args:
    args (Optional[List[Any]], optional): List of command-line arguments to parse. If None, uses sys.argv. Defaults to None.

## Returns:
    None: This function does not return any value.

## Raises:
    SystemExit: Raised by argparse when invalid arguments are provided or when --help is specified.
    FileNotFoundError: Raised when the input_file cannot be found or accessed.
    pandas.errors.EmptyDataError: Raised when the input file contains no data.
    ValueError: Raised when tar compression is not supported directly by pandas.
    Exception: Propagated from underlying operations such as file I/O or report generation failures.

## Constraints:
    Preconditions:
        - The input_file argument must specify a valid file path that can be read by pandas
        - If output_file is provided, it must be a valid file path for writing
        - The config_file argument, if provided, must point to a valid YAML configuration file
        - All other arguments must conform to their expected types and ranges
    
    Postconditions:
        - A profiling report is generated and saved to the specified output location
        - The output file is created with proper permissions for writing
        - All temporary resources are properly cleaned up

## Side Effects:
    - Reads input file from disk using pandas
    - Writes HTML report file to disk
    - May print help/version information to stdout
    - Calls external libraries for data processing and report generation

## Control Flow:
```mermaid
flowchart TD
    A[Start main] --> B[parsed_args = parse_args(args)]
    B --> C[kwargs = vars(parsed_args)]
    C --> D[input_file = Path(kwargs.pop("input_file"))]
    D --> E[output_file = kwargs.pop("output_file")]
    E --> F{output_file is None?}
    F -->|Yes| G[output_file = str(input_file.with_suffix(".html"))]
    F -->|No| H[Skip]
    G --> I[silent = kwargs.pop("silent")]
    H --> I
    I --> J[df = read_pandas(input_file)]
    J --> K[ProfileReport(df, **kwargs)]
    K --> L[p.to_file(Path(output_file), silent=silent)]
    L --> M[End]
```

## Examples:
    # Basic usage with default settings
    main(['data.csv'])
    
    # With explicit output file
    main(['data.csv', 'report.html'])
    
    # With silent flag
    main(['-s', 'data.csv'])
    
    # With minimal configuration
    main(['-m', 'data.csv'])
    
    # With custom title and pool size
    main(['--title', 'My Report', '--pool_size', '4', 'data.csv'])
    
    # With explorative mode and config file
    main(['-e', '--config_file', 'my_config.yaml', 'data.csv'])
    
    # Using version flag
    main(['--version'])
```

