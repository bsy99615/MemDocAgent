# `interact.py`

## `imapclient.interact.command_line` · *function*

## Summary:
Parses command-line arguments for configuring an IMAP client connection, supporting both direct CLI options and configuration file loading.

## Description:
Processes command-line arguments to configure IMAP client connection parameters. This function provides a unified interface for specifying IMAP connection settings through command-line flags, with support for loading configurations from files. It handles SSL/TLS connection options, compulsory authentication parameters, and interactive password prompts when needed.

The function is extracted into its own component to encapsulate all argument parsing and validation logic, separating configuration concerns from the core IMAP client functionality. This promotes reusability and makes testing easier by providing a clean interface for different input methods.

## Args:
    None: This function takes no parameters directly, but reads from standard command-line arguments.

## Returns:
    argparse.Namespace: A namespace object containing parsed configuration parameters with the following attributes:
        - host (str): IMAP server hostname
        - username (str): Authentication username
        - password (str): Authentication password
        - port (int): IMAP server port number
        - ssl (bool): Whether to use SSL/TLS connection
        - insecure (bool): Whether to use insecure connection (without SSL/TLS)
        - file (str): Path to configuration file (if provided)

## Raises:
    SystemExit: Raised by argparse when invalid arguments are provided or when -f/--file is used with other options.

## Constraints:
    Preconditions:
        - Command-line arguments must be properly formatted
        - If a configuration file is specified, no other command-line options can be used
        - Compulsory arguments (host, username, password) must be provided either via CLI or through interactive prompts
    Postconditions:
        - All required configuration parameters are present in the returned namespace
        - SSL configuration is properly resolved (ssl = not insecure)
        - Password prompts are only shown when necessary

## Side Effects:
    - Reads command-line arguments using argparse
    - May prompt user for password input via getpass when required
    - Reads configuration files from disk when -f/--file option is used
    - May exit the program with error codes if validation fails

## Control Flow:
```mermaid
flowchart TD
    A[Start command_line()] --> B[Parsing CLI arguments]
    B --> C{File option provided?}
    C -->|Yes| D[Validate no other options]
    D --> E[Parse config file]
    E --> F[Return parsed config]
    C -->|No| G[Resolve SSL settings]
    G --> H[Check compulsory args]
    H --> I{Compulsory arg missing?}
    I -->|Yes| J[Get password via getpass]
    J --> K[Set value in args]
    I -->|No| L[Continue processing]
    K --> L
    L --> M[Return args]
```

## Examples:
```python
# Basic usage with direct arguments
# python script.py -H imap.example.com -u user@example.com -p secret

# Using configuration file
# python script.py -f config.ini

# Using insecure connection
# python script.py -H imap.example.com -u user@example.com -p secret --insecure

# Interactive password prompt
# python script.py -H imap.example.com -u user@example.com
# (will prompt for password)
```

## `imapclient.interact.main` · *function*

## Summary
Establishes an IMAP client connection and launches an interactive shell for manual email account manipulation.

## Description
This function orchestrates the complete process of connecting to an IMAP server and providing an interactive Python environment for manual email account management. It parses command-line arguments, establishes the IMAP connection, and attempts to launch an enhanced interactive shell with fallback options.

The function is extracted into its own component to encapsulate the end-to-end workflow of connection setup and interactive session initiation, separating this concern from the underlying configuration and connection logic. This allows for clean separation of concerns where argument parsing, connection establishment, and shell interaction are handled independently.

## Args
    None: This function does not accept any parameters directly.

## Returns
    int: Always returns 0 to indicate successful completion of the interactive session.

## Raises
    ImportError: When required interactive shell libraries (ptpython, IPython) are not installed, causing fallback to simpler alternatives.

## Constraints
    Preconditions:
        - Command-line arguments must be properly formatted and valid
        - Required connection parameters (host, username, password) must be provided
        - Network connectivity must be available for IMAP server connection
    Postconditions:
        - An IMAP client connection is established and ready for use
        - An interactive shell session is initiated with the client available as variable "c"
        - All fallback shell implementations are attempted in order of preference

## Side Effects
    - Reads command-line arguments using argparse
    - Establishes network connection to IMAP server
    - May prompt user for password input via getpass when required
    - Creates and initializes an IMAP client instance
    - Launches an interactive Python shell session
    - May read configuration files from disk when -f/--file option is used

## Control Flow
```mermaid
flowchart TD
    A[Start main()] --> B[Parse command-line arguments]
    B --> C[Connect to IMAP server]
    C --> D{Connection successful?}
    D -- No --> E[Exit with error]
    D -- Yes --> F[Prepare shell attempt list]
    F --> G{Try ptpython}
    G -- ImportError --> H[Try IPython 4.0+]
    H -- ImportError --> I[Try IPython 0.11]
    I -- ImportError --> J[Try IPython 0.10]
    J -- ImportError --> K[Try builtin code.interact]
    K -- ImportError --> L[All shells failed - exit]
    G -- Success --> M[Launch ptpython]
    H -- Success --> N[Launch IPython 4.0+]
    I -- Success --> O[Launch IPython 0.11]
    J -- Success --> P[Launch IPython 0.10]
    K -- Success --> Q[Launch builtin shell]
    M --> R[End]
    N --> R
    O --> R
    P --> R
    Q --> R
```

## Examples
```python
# Basic usage with direct arguments
# python imapclient/interact.py -H imap.example.com -u user@example.com -p secret

# Using configuration file
# python imapclient/interact.py -f config.ini

# Interactive password prompt
# python imapclient/interact.py -H imap.example.com -u user@example.com
# (will prompt for password)

# After launching, you'll have access to the IMAPClient instance as variable "c"
# >>> c.list_folders()
# >>> c.select_folder('INBOX')
# >>> c.search(['UNSEEN'])
```

