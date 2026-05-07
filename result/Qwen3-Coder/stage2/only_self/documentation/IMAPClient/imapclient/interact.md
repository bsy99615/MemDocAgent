# `interact.py`

## `imapclient.interact.command_line` · *function*

## Summary:
Parses command-line arguments for IMAP client configuration and handles interactive credential prompts.

## Description:
Processes command-line arguments for configuring an IMAP client connection, supporting both direct command-line options and configuration file input. The function provides a unified interface for specifying IMAP connection parameters including host, username, password, port, and SSL settings. When a configuration file is specified, it validates that no conflicting command-line options are provided and parses the file accordingly. For missing compulsory arguments, it prompts the user for input securely via getpass.

## Args:
    None: This function does not accept any parameters directly.

## Returns:
    argparse.Namespace: A namespace object containing parsed configuration parameters with the following attributes:
        - host (str): IMAP server hostname
        - username (str): Authentication username
        - password (str): Authentication password
        - port (int): IMAP server port number
        - ssl (bool): Whether to use SSL/TLS encryption
        - insecure (bool): Whether to use insecure connection (without SSL/TLS)
        - file (str): Path to configuration file (if specified)

## Raises:
    SystemExit: Raised by argparse when invalid arguments are provided or when help is requested
    ValueError: Raised when configuration file contains invalid settings (specifically if DEFAULT section has expect_failure)
    FileNotFoundError: Raised when specified configuration file cannot be found or read

## Constraints:
    Preconditions:
        - Command-line arguments must be valid according to argparse specification
        - If a configuration file is specified, no other command-line options can be used
        - Required arguments (host, username, password) must be provided either via command-line or through interactive prompts
        
    Postconditions:
        - All required arguments are populated with valid values
        - SSL configuration is properly resolved (either from --ssl flag or --insecure flag)
        - Configuration file parsing occurs only when -f/--file option is explicitly provided

## Side Effects:
    - Reads configuration file from disk when -f/--file option is used
    - Prompts user for input via terminal when required arguments are missing
    - Uses getpass to securely collect password input

## Control Flow:
```mermaid
flowchart TD
    A[command_line called] --> B[Create ArgumentParser]
    B --> C[Add host argument]
    C --> D[Add username argument]
    D --> E[Add password argument]
    E --> F[Add port argument]
    F --> G[Add SSL mutually exclusive group]
    G --> H[Add insecure argument]
    H --> I[Add file argument]
    I --> J[Parse command line arguments]
    J --> K{File option provided?}
    K -- Yes --> L[Validate no other options provided]
    L --> M[Parse config file]
    M --> N[Return parsed config]
    K -- No --> O[Set SSL default based on insecure flag]
    O --> P[Check for compulsory args]
    P --> Q{Compulsory arg missing?}
    Q -- Yes --> R[Get password via getpass]
    R --> S[Set argument value]
    Q -- No --> T[Continue with existing value]
    S --> U{More compulsory args?}
    U -->|Yes| P
    U -->|No| V[Return parsed args]
```

## Examples:
```python
# Basic usage with command-line arguments
# python script.py -H imap.example.com -u user@example.com -p secret123

# Using configuration file
# python script.py -f config.ini

# With SSL disabled
# python script.py -H imap.example.com -u user@example.com -p secret123 --insecure

# Interactive prompt for missing arguments
# python script.py -H imap.example.com -u user@example.com
# (Will prompt for password)
```

## `imapclient.interact.main` · *function*

## Summary:
Launches an interactive IMAP client session with multiple shell fallback options.

## Description:
Establishes an IMAP client connection using configuration parsed from command-line arguments and launches an interactive Python shell. The function attempts to use modern shell implementations (ptpython, IPython 4.x, IPython 0.11) before falling back to Python's built-in code.interact. This function serves as the entry point for interactive IMAP client sessions.

## Args:
    None - This function does not accept parameters directly. It depends on an external `command_line()` function to parse command-line arguments.

## Returns:
    int: Exit status code (0 for successful execution).

## Raises:
    ImportError: When required shell libraries are not installed (ptpython, various IPython versions, or code module).

## Constraints:
    Preconditions:
    - Command-line arguments must be valid for IMAP connection
    - IMAP server must be reachable
    - Required shell libraries must be installable
    
    Postconditions:
    - An IMAP client instance is created and connected
    - Either an interactive shell is launched or an ImportError is raised

## Side Effects:
    - Prints connection status messages to stdout
    - Establishes network connection to IMAP server
    - Launches interactive shell process (blocking operation)
    - May import additional modules dynamically

## Control Flow:
```mermaid
flowchart TD
    A[Start main()] --> B[Call external command_line() function]
    B --> C[Create IMAP client with create_client_from_config]
    C --> D[Print "Connecting..."]
    D --> E[Print "Connected."]
    E --> F[Define shell attempt functions (ptpython, ipython_400, ipython_011, ipython_010, builtin)]
    F --> G[Iterate through shell attempts]
    G --> H{Try shell attempt}
    H -->|ImportError| I[Skip and continue]
    H -->|Success| J[Break loop and launch shell]
    I --> K{More attempts?}
    K -->|Yes| G
    K -->|No| L[Raise ImportError]
    J --> M[Exit with status 0]
    L --> N[Raise ImportError]
```

## Examples:
```python
# Typical usage from command line:
# python -m imapclient.interact --host=imap.example.com --user=john

# After running, user gets interactive prompt:
# IMAPClient instance is "c"
# >>> c.list_folders()
# >>> c.select_folder('INBOX')
# >>> c.search(['UNSEEN'])
```

