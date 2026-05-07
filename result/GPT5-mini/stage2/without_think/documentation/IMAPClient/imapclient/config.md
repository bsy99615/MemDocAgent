# `config.py`

## `imapclient.config.getenv` · *function*

## Summary:
Reads a configuration value from the process environment using a fixed "imapclient_" prefix and returns the environment value when present, otherwise returns the provided fallback.

## Description:
This helper centralizes lookup of environment-backed configuration values for the imapclient package. It constructs an environment variable name by concatenating the literal prefix "imapclient_" with the supplied name and then returns the environment value if set, otherwise the caller-supplied default.

Known callers within the codebase:
- No explicit callers are declared in this file. This function is intended to be used by configuration-loading code in the same module or by other modules that need to allow overriding configuration via environment variables (for example, to check for "imapclient_host", "imapclient_port", "imapclient_ssl", etc.).

Why this logic is extracted:
- Encapsulates the exact environment key naming convention (the fixed "imapclient_" prefix) in one place so all callers use a consistent policy.
- Keeps callers simple (they provide only the logical name and a fallback) and avoids repeating string-concatenation and default logic across the codebase.

## Args:
    name (str): The logical name of the configuration item (e.g., "host", "port", "ssl").
        - Must be a plain string; it is appended verbatim to the prefix.
        - Do not include the "imapclient_" prefix; passing a name that already contains that prefix will result in an environment key with the prefix duplicated.
    default (Optional[str]): The fallback value returned when the constructed environment variable is not set.
        - May be None to indicate no fallback.

## Returns:
    Optional[str]: If the environment contains a value for the key "imapclient_" + name, that string value is returned.
    Otherwise, returns the provided default argument (which may be None).

    Possible return values:
    - A non-empty string if the corresponding environment variable is set to a non-empty value.
    - An empty string if the environment variable is set to the empty string.
    - The value of the `default` parameter when the environment variable is not present.

## Raises:
    This function does not raise exceptions under normal use.
    - It performs a read-only lookup on the process environment using the standard os.environ.get API, which does not raise when used with string keys.
    - If the process environment is in an unusual state (e.g., os.environ is replaced with an object whose get method raises), any exceptions would originate from that object; this function itself does not intentionally raise.

## Constraints:
    Preconditions:
    - The caller must supply a valid string for `name`.
    - The environment is expected to be accessible via os.environ (typical in standard Python execution environments).

    Postconditions:
    - No global state or environment is modified.
    - The returned value is either the exact string stored in the environment for the constructed key or the exact `default` value passed in.

## Side Effects:
    - None. The function performs only a read from the process environment; it does not write files, print to stdout/stderr, mutate global variables, perform network I/O, or call external services.

## Control Flow:
flowchart TD
    Start --> BuildKey["Build key: 'imapclient_' + name"]
    BuildKey --> Lookup["Lookup os.environ.get(key, default)"]
    Lookup --> Found{"Environment has key?"}
    Found -- Yes --> ReturnEnv["Return environment value (may be empty string)"]
    Found -- No --> ReturnDefault["Return provided default (may be None)"]
    ReturnEnv --> End
    ReturnDefault --> End

## Examples:
- Typical usage scenario (described in prose):
    A configuration loader wants to allow environment overrides for a "host" setting. It calls this helper with name="host" and default="imap.example.org". At runtime:
    - If the process environment contains a variable named exactly "imapclient_host", its string value is returned (even if it is the empty string).
    - If "imapclient_host" is not present, the function returns "imap.example.org".
    - Note: Environment keys are matched exactly; using uppercase keys like "IMAPCLIENT_HOST" on case-sensitive systems will not match the lowercase "imapclient_host" key produced by this function.

- Edge-case behavior:
    If a caller passes name="imapclient_host" (i.e., already including the prefix), the function will construct the key "imapclient_imapclient_host" and look for that exact environment variable; this is usually not desired. Callers should pass the name fragment without the prefix.

## `imapclient.config.get_config_defaults` · *function*

## Summary:
Returns the package-level configuration defaults as a mapping of configuration keys to default values, applying environment-backed overrides for sensitive/text values via the helper that prefixes keys with "imapclient_".

## Description:
This function centralizes the canonical default configuration values used by imapclient. Several values (username, password, oauth2-related fields) are resolved through the package getenv helper so they may be overridden by environment variables named "imapclient_<name>" (for example, "imapclient_username"). The function itself performs no parsing or validation beyond assembling the default mapping.

Known callers within the repository snapshot:
- No direct callers were discovered in the provided code snapshot. This function is intended to be invoked by configuration-loading code or higher-level connection/setup routines (for example: a load_config function, CLI argument processing, or connection factory) to obtain baseline defaults before applying user-supplied configuration and validation.

Why this logic is extracted:
- Encapsulates the canonical default values in a single place so all configuration-loading code obtains the same baseline.
- Centralizes the environment-override points (via getenv) so the environment naming convention ("imapclient_" prefix) is used consistently.
- Keeps higher-level code focused on merging and validating configuration instead of enumerating defaults.

## Args:
None.

## Returns:
Dict[str, Any]: A dictionary mapping configuration option names to their default values. The returned mapping contains the following keys and values as produced directly by the function:

- "username" -> Optional[str]
    - Value: result of getenv("username", None)
    - Semantics: string from environment "imapclient_username" if present (may be empty string), otherwise None.

- "password" -> Optional[str]
    - Value: result of getenv("password", None)
    - Semantics: string from environment "imapclient_password" if present, otherwise None.

- "ssl" -> bool
    - Value: True
    - Semantics: whether to use SSL/TLS by default.

- "ssl_check_hostname" -> bool
    - Value: True
    - Semantics: whether hostname checking on SSL connections is enabled by default.

- "ssl_verify_cert" -> bool
    - Value: True
    - Semantics: whether certificate verification is enabled by default.

- "ssl_ca_file" -> Optional[str]
    - Value: None
    - Semantics: path to CA bundle file when provided elsewhere; default is None (no custom CA file).

- "timeout" -> Any (None)
    - Value: None
    - Semantics: default network/operation timeout is not set here; callers may interpret None as "use system/library default" or "no timeout".

- "starttls" -> bool
    - Value: False
    - Semantics: whether STARTTLS should be attempted by default (disabled).

- "stream" -> bool
    - Value: False
    - Semantics: whether to use streaming mode by default (disabled).

- "oauth2" -> bool
    - Value: False
    - Semantics: whether OAuth2 authentication is enabled by default (disabled).

- "oauth2_client_id" -> Optional[str]
    - Value: result of getenv("oauth2_client_id", None)
    - Semantics: client id from environment "imapclient_oauth2_client_id" if present, otherwise None.

- "oauth2_client_secret" -> Optional[str]
    - Value: result of getenv("oauth2_client_secret", None)
    - Semantics: client secret from environment "imapclient_oauth2_client_secret" if present, otherwise None.

- "oauth2_refresh_token" -> Optional[str]
    - Value: result of getenv("oauth2_refresh_token", None)
    - Semantics: refresh token from environment "imapclient_oauth2_refresh_token" if present, otherwise None.

- "expect_failure" -> Any (None)
    - Value: None
    - Semantics: placeholder default used by tests or callers to indicate an expected failure mode; semantics are decided by the caller.

Notes on types:
- The getenv-derived values are not coerced: they return exactly the string stored in the environment or the provided fallback (None). Callers that expect booleans, numbers, or other types must parse/coerce those values explicitly after merging defaults with user configuration.

## Raises:
This function does not raise exceptions by itself. Any exceptions would originate from the getenv helper (which, under normal circumstances, does not raise) or from environment access being replaced by a non-standard object that raises on lookup — such cases are outside the intended normal operation.

## Constraints:
Preconditions:
- The getenv helper (in the same module) must be available and callable. That helper constructs environment keys by prefixing "imapclient_" to the logical name and returning the environment string or the provided fallback.
- Callers should expect string-typed values for getenv-derived keys (or None) and must perform any necessary type conversion.

Postconditions:
- The returned dictionary contains exactly the keys listed above.
- Values are the literal defaults encoded in the function body or the raw environment string values returned by getenv; no additional validation or coercion is performed.

## Side Effects:
- None. The function creates and returns an in-memory dictionary and performs read-only environment lookups via getenv. It does not mutate any global state, write files, perform network I/O, or print to stdout/stderr.

## Control Flow:
flowchart TD
    Start --> BuildMap["Begin building defaults map"]
    BuildMap --> UsernameEnv["Call getenv('username', None)"]
    UsernameEnv --> PasswordEnv["Call getenv('password', None)"]
    PasswordEnv --> StaticBooleans["Set static boolean defaults (ssl, ssl_check_hostname, ssl_verify_cert, starttls, stream, oauth2)"]
    StaticBooleans --> StaticNulls["Set static None defaults (ssl_ca_file, timeout, expect_failure)"]
    StaticNulls --> OAuthEnvs["Call getenv for oauth2_client_id/secret/refresh_token"]
    OAuthEnvs --> ReturnMap["Return assembled dict"]
    ReturnMap --> End

    UsernameEnv -->|env present| UsernameFromEnv["username := env value"]
    UsernameEnv -->|env absent| UsernameDefault["username := None"]
    PasswordEnv -->|env present| PasswordFromEnv["password := env value"]
    PasswordEnv -->|env absent| PasswordDefault["password := None"]
    OAuthEnvs -->|env present| OAuthFromEnv["oauth fields := env values"]
    OAuthEnvs -->|env absent| OAuthDefault["oauth fields := None"]

## Examples:
- Environment override scenario (prose):
    If the process environment contains an entry named "imapclient_username" with value "alice", then get_config_defaults()["username"] will be the string "alice". If that environment variable is not set, the returned "username" value will be None.

- Merging defaults with user config (prose):
    Typical usage is: obtain this defaults mapping, then update or merge it with values parsed from a configuration file and then with CLI arguments. After merging, perform type coercion and validation. Example flow:
    1. base = get_config_defaults()
    2. file_conf = parse_config_file(...)
    3. merged = {**base, **file_conf, **cli_args}
    4. Validate and coerce merged["timeout"], merged["ssl"], etc., since getenv-derived values are strings or None.

- Edge case:
    If an environment variable exists but is the empty string (e.g., "imapclient_password" = ""), the returned value will be the empty string — callers should treat empty string as a distinct value from None and handle it explicitly if that distinction matters.

## `imapclient.config.parse_config_file` · *function*

## Summary:
Load an INI-style configuration file, parse the DEFAULT section into a typed argparse.Namespace, validate that DEFAULT does not request an expected failure, and collect per-section typed Namespaces in the returned Namespace.alternates mapping.

## Description:
This function centralizes the file-level loading and top-level assembly of configuration data. It:
- Constructs a configparser.ConfigParser seeded with textual package defaults (via get_string_config_defaults()).
- Attempts to read the specified filename into that parser.
- Uses the helper _read_config_section to convert the parser's DEFAULT section into a typed argparse.Namespace (host, port, ssl, timeout, username, password, oauth2 fields, expect_failure, etc.).
- Ensures the DEFAULT section does not set the expect_failure flag (this is considered a configuration error).
- Iterates over all non-default sections present in the parser and converts each into a Namespace using _read_config_section, storing them in conf.alternates as a dict[str, argparse.Namespace].

Known callers within the provided snapshot:
- No direct callsites were found in the supplied code snapshot. Typical callers (outside the snapshot) are application startup or CLI configuration-loading routines that need a single consolidated configuration object representing the DEFAULT settings plus any named alternate server profiles.

Why this logic is extracted:
- Responsibility boundary: isolates file I/O and the assembly of a top-level configuration object from the lower-level parsing rules in _read_config_section. This keeps higher-level code focused on "load-and-apply" semantics and delegates option-level type coercion and validation to the dedicated helper.

## Args:
    filename (str)
        Filesystem path to the configuration file expected to be in INI/ConfigParser format. The function passes this path to configparser.ConfigParser.read(). The caller should provide a path-like string; no further normalization is performed by this function.

## Returns:
    argparse.Namespace
        A Namespace produced by parsing the DEFAULT section via _read_config_section, augmented with a single attribute:
        - alternates (dict[str, argparse.Namespace]):
            Mapping of each non-default section name to the Namespace produced by _read_config_section for that section.
        The Namespace returned for DEFAULT contains the full set of typed configuration attributes defined by _read_config_section (for example: host, port, ssl, starttls, ssl_ca_file, timeout, stream, username, password, oauth2, oauth2_client_id, oauth2_client_secret, oauth2_refresh_token, expect_failure, etc.). All those attributes will always be present on the Namespace (some may be None).

## Raises:
    ValueError
        If the parsed DEFAULT section has expect_failure set (truthy according to _read_config_section's parsing), this function raises ValueError("expect_failure should not be set for the DEFAULT section").

    Any exception raised by _read_config_section
        - configparser.NoSectionError, configparser.NoOptionError:
            May be raised if required options are missing when _read_config_section accesses them for the DEFAULT or any alternate section.
        - ValueError:
            May be raised if numeric parsing (port, timeout) or boolean parsing inside _read_config_section fails for any section.
        These exceptions are not caught here and therefore propagate to the caller.

    Note: parser.read(...) itself does not raise exceptions from this function; parsing/validation errors surface when _read_config_section inspects section options.

## Constraints:
Preconditions:
    - filename must be a string path to a configuration file. The caller is responsible for ensuring the path is sensible (readable, correct location). This function does not open the file with explicit exception handling beyond what configparser provides.

Postconditions:
    - Returns an argparse.Namespace representing the DEFAULT configuration; its alternates attribute contains parsed Namespaces for all non-default sections present in the file.
    - If no non-default sections are present, alternates will be an empty dict.
    - The function will have validated that DEFAULT does not set expect_failure; if it does, the function raises ValueError and does not return.

## Side Effects:
    - I/O: Calls configparser.ConfigParser.read(filename) which attempts to read the file at the given path (file-system read).
    - No other global state is mutated by this function.
    - No network I/O or external service calls occur.
    - All additional parsing/expansion side effects (for example, expanding ssl_ca_file via os.path.expanduser) are performed inside _read_config_section.

## Control Flow:
flowchart TD
    Start --> CreateParser[get_string_config_defaults() -> ConfigParser(defaults)]
    CreateParser --> ReadFile[parser.read(filename)]
    ReadFile --> ParseDefault[_read_config_section(parser, "DEFAULT") -> conf]
    ParseDefault --> CheckExpect{conf.expect_failure truthy?}
    CheckExpect -- Yes --> RaiseValueError[raise ValueError("expect_failure should not be set for the DEFAULT section")]
    CheckExpect -- No --> InitAlternates[conf.alternates = {}]
    InitAlternates --> IterateSections[for each section in parser.sections()]
    IterateSections --> ReadSection[_read_config_section(parser, section) -> section_ns]
    ReadSection --> StoreAlternate[conf.alternates[section] = section_ns]
    StoreAlternate --> IterateSections
    IterateSections --> ReturnConf[return conf]
    ReturnConf --> End

## Examples:
- Typical usage (happy path):
    Call parse_config_file and use returned values to configure an IMAP client. Handle configuration errors if they arise.
    1. conf = parse_config_file("/etc/imapclient/config.ini")
    2. default_host = conf.host
    3. alternates = conf.alternates  # dict of named profiles

- Error handling example:
    Try to load the configuration and present a user-friendly error if DEFAULT requests expect_failure or options are malformed.
    1. try:
         conf = parse_config_file(user_path)
       except ValueError as exc:
         # handle the explicit expect_failure-in-DEFAULT error
       except (configparser.NoSectionError, configparser.NoOptionError, ValueError) as exc:
         # handle missing or malformed options propagated from _read_config_section

- Notes for callers:
    - Because _read_config_section performs type coercion (ints, floats, booleans) and path expansion for ssl_ca_file, callers receive typed values and should not duplicate those conversions.
    - To customize parsing behavior, modify _read_config_section; parse_config_file's role is orchestration (file loading + assembly).

## `imapclient.config.get_string_config_defaults` · *function*

## Summary:
Return a string-oriented view of the package configuration defaults by converting boolean and falsy default values into canonical textual representations.

## Description:
This function calls get_config_defaults() (which returns the package's in-memory defaults dictionary) and converts its values so they are suitable for text-based storage or display:
- True becomes "true"
- False becomes "false"
- Any other falsy value (None, empty string, 0, empty container, etc.) becomes the empty string ""
- Any other truthy value is preserved as-is in the returned mapping

Known callers within the provided snapshot:
- None discovered. The function is intended for use by code that needs a textual representation of defaults (for example, emitting defaults into a config file, serialising defaults for CLI help output, or preparing defaults for environment-based export).

Why this logic is extracted:
- Ensures a single, consistent rule set for serializing the canonical defaults to text, so all serialization or display code uses identical string forms for booleans and empty/absent values.
- Keeps callers focused on merging and validating configuration rather than remembering textual conversion rules.

## Args:
None.

## Returns:
Dict[str, str]
- A dictionary with the same keys as get_config_defaults() (which returns an in-memory Dict[str, Any]).
- Conversion rules applied to each original value v:
    - If v is exactly the boolean True (identity check), the returned value is the string "true".
    - If v is exactly the boolean False (identity check), the returned value is the string "false".
    - If v is falsy (not v) and not the boolean True/False (examples: None, empty string, 0, empty list), the returned value is the empty string "".
    - Otherwise (truthy non-boolean values, such as a non-empty string), the original value v is preserved and stored in the returned dict.
- Note: Although the function is annotated to return Dict[str, str], preserved non-string truthy values from get_config_defaults() will be carried through unchanged by the implementation. Callers that require strictly string-typed values should explicitly cast/convert the results.

## Raises:
- The function itself does not raise exceptions.
- Any exceptions will come from get_config_defaults(), for example if that helper is modified to raise; under normal operation get_config_defaults() performs read-only environment lookups and returns a plain dict.

## Constraints:
Preconditions:
- get_config_defaults() is expected to return an in-memory dictionary mapping strings to values (Dict[str, Any]) — the implementation iterates get_config_defaults().items().

Postconditions:
- The returned dict contains exactly the keys returned by get_config_defaults(), with values transformed according to the conversion rules described above.
- No mutation of the original dict returned by get_config_defaults() occurs.

## Side Effects:
- None. The function constructs and returns a new dictionary in memory; it performs no I/O and does not mutate global state.

## Control Flow:
flowchart TD
    Start --> CallDefaults["Call get_config_defaults() (returns in-memory dict)"]
    CallDefaults --> Iterate["Iterate over each (key, value)"]
    Iterate --> IsTrue["Is value exactly True?"]
    IsTrue -- yes --> SetTrue["out[key] := \"true\""]
    IsTrue -- no --> IsFalse["Is value exactly False?"]
    IsFalse -- yes --> SetFalse["out[key] := \"false\""]
    IsFalse -- no --> IsFalsy["Is value falsy? (not value)"]
    IsFalsy -- yes --> SetEmpty["out[key] := \"\""]
    IsFalsy -- no --> Preserve["out[key] := original value"]
    Preserve --> Next["continue loop"]
    SetTrue --> Next
    SetFalse --> Next
    SetEmpty --> Next
    Next --> Iterate
    Iterate --> Return["Return constructed dict"]
    Return --> End

## Examples:
- Conversion example (prose):
    If get_config_defaults() returns:
    {
      "username": None,
      "password": "",
      "ssl": True,
      "oauth2": False,
      "host": "imap.example"
    }
    then get_string_config_defaults() returns:
    {
      "username": "",
      "password": "",
      "ssl": "true",
      "oauth2": "false",
      "host": "imap.example"
    }

- Practical usage guidance (prose):
    Use this function when you need textual defaults for writing config files or displaying defaults. After merging these stringified defaults with user-provided values, perform explicit parsing/coercion (for example, convert "true"/"false" back to booleans, treat "" as None where appropriate).

## `imapclient.config._read_config_section` · *function*

## Summary:
Reads a single section from a ConfigParser and converts its options into a structured argparse.Namespace of typed values (strings, booleans, ints/floats when present), expanding the ssl_ca_file path if provided.

## Description:
This helper extracts configuration values from the given configparser.ConfigParser for a single section name and returns them as an argparse.Namespace with a fixed set of attributes expected by the caller (host, port, ssl, starttls, etc.).

Known callers:
- No specific callsites are present in the provided snippet. Typical callers are higher-level configuration-loading functions that:
  1) construct or read a config file into a configparser.ConfigParser, and
  2) call this helper with that parser and a chosen section name to produce a uniform configuration Namespace used to construct or configure an IMAP client.

Why this logic is extracted:
- Responsibility boundary: centralizes the mapping from raw configparser string values to typed, semantically named attributes. This consolidates parsing rules (boolean parsing, optional numeric parsing, empty-string-as-none, and user-path expansion for certificate files) so callers receive a consistent typed object rather than repeating parsing logic throughout the codebase.

## Args:
    parser (configparser.ConfigParser):
        A populated ConfigParser instance. Must contain the requested section (otherwise a configparser.NoSectionError will be raised by parser.get).
    section (str):
        The name of the section in the parser to read values from.

Notes on parameters:
- The function assumes the parser has already been loaded with configuration data (from a file or string). It does not read files itself.
- All option names used by the function are fixed and hard-coded (see Returns). Some options are treated as required (their absence results in configparser.NoOptionError); others will be interpreted as optional and returned as None.

## Returns:
argparse.Namespace with the following attributes (exact attribute names and their value types):
    host (str)
        Raw string returned by parser.get(section, "host").
    port (Optional[int])
        If the "port" option is missing -> None. If present but empty -> None. Otherwise parsed with int(), possibly raising ValueError for invalid numeric text.
    ssl (bool)
        Parsed with parser.getboolean(section, "ssl"). Presence of the option is required; if missing, configparser.NoOptionError is raised.
    starttls (bool)
        Parsed with parser.getboolean(section, "starttls").
    ssl_check_hostname (bool)
        Parsed with parser.getboolean(section, "ssl_check_hostname").
    ssl_verify_cert (bool)
        Parsed with parser.getboolean(section, "ssl_verify_cert").
    ssl_ca_file (Optional[str])
        Raw value of "ssl_ca_file" expanded with os.path.expanduser() if non-empty/truthy. If the option is missing, configparser.NoOptionError is raised by the inner get helper.
    timeout (Optional[float])
        If "timeout" is missing or empty -> None. Otherwise parsed with float(), possibly raising ValueError for invalid numeric text.
    stream (bool)
        Parsed with parser.getboolean(section, "stream").
    username (str)
        Raw string returned by parser.get(section, "username").
    password (str)
        Raw string returned by parser.get(section, "password").
    oauth2 (bool)
        Parsed with parser.getboolean(section, "oauth2").
    oauth2_client_id (str)
        Raw string returned by parser.get(section, "oauth2_client_id").
    oauth2_client_secret (str)
        Raw string returned by parser.get(section, "oauth2_client_secret").
    oauth2_refresh_token (str)
        Raw string returned by parser.get(section, "oauth2_refresh_token").
    expect_failure (str)
        Raw string returned by parser.get(section, "expect_failure").

All returned attribute names are always present on the Namespace object; their values reflect the parsing rules above (some may be None).

## Raises:
    configparser.NoSectionError:
        If the specified section does not exist in parser (raised by parser.get calls).
    configparser.NoOptionError:
        If a named option is required by the code path and missing. Specifically:
            - The inner get(name) wrapper calls parser.get(section, name) and will propagate NoOptionError for options used via get(...).
            - The getboolean wrapper calls parser.getboolean(section, name) and will propagate NoOptionError for boolean options if missing.
    ValueError:
        When parsing numeric values:
            - If "port" is present and not empty but cannot be converted with int(), int() will raise ValueError.
            - If "timeout" is present and not empty but cannot be converted with float(), float() will raise ValueError.
        Additionally, configparser.getboolean may raise a ValueError if a boolean option contains an invalid value that configparser cannot interpret as boolean.
    Any other exceptions raised by configparser methods (e.g., configparser.Error) may propagate.

## Constraints:
Preconditions:
    - parser must be an initialized and populated configparser.ConfigParser.
    - The caller should ensure the requested section name is correct; otherwise configparser.NoSectionError will be raised.
    - Option values that are intended to be numeric must be valid textual representations (e.g., "993" for port, "10.5" for timeout) or left empty to yield None.

Postconditions:
    - Returns an argparse.Namespace with the fixed set of attributes described above.
    - If ssl_ca_file was present and non-empty, its value is expanded with os.path.expanduser() (tilde expansion applied).
    - No global state is mutated by this function.

## Side Effects:
    - Calls os.path.expanduser on the ssl_ca_file value when non-empty; this only performs string transformation (no file I/O).
    - Calls into configparser APIs to read values; this does not mutate the parser.
    - No network I/O, file reads/writes, logging, or external service calls occur.

## Control Flow:
flowchart TD
    A[Start: called with parser and section] --> B{Section exists?}
    B -- No --> C[Raise configparser.NoSectionError]
    B -- Yes --> D[Define helpers: get, getboolean, get_allowing_none]
    D --> E[Read ssl_ca_file via get]
    E --> F{ssl_ca_file truthy?}
    F -- Yes --> G[ssl_ca_file = os.path.expanduser(value)]
    F -- No --> H[ssl_ca_file stays falsy/None]
    G --> I[Read each configured option with appropriate helper]
    H --> I
    I --> J[Construct argparse.Namespace with all attributes]
    J --> K[Return Namespace]
    I --> |numeric parse present and invalid| L[Raise ValueError]
    I --> |missing required option| M[Raise configparser.NoOptionError]

## Examples (usage pattern, described):
- Typical usage (in prose):
    1. Create and populate a ConfigParser from a file or string.
    2. Call this helper with that parser and a section name (e.g., "imap").
    3. If the section is missing, handle configparser.NoSectionError.
    4. If numeric options are present but malformed, catch ValueError.
    5. Use the returned Namespace to configure an IMAP client constructor (host, port, ssl, username, password, etc.).

- Error handling guidance:
    - Wrap the call in try/except to catch configparser.NoSectionError and configparser.NoOptionError when required options are missing.
    - Validate or coerce numeric fields before calling if you want to provide user-friendly error messages; otherwise allow ValueError to propagate and be handled by the caller.

## `imapclient.config.refresh_oauth2_token` · *function*

## Summary:
Performs an OAuth2 refresh-token exchange against the provider endpoint mapped for the given hostname and returns the provider-supplied access token string.

## Description:
This function looks up the token-refresh endpoint URL for the provided hostname in the global OAUTH2_REFRESH_URLS mapping, constructs a URL-encoded POST payload containing the client credentials and refresh token, posts it to the endpoint using urllib.request.urlopen, parses the JSON response, and returns the value of the "access_token" field.

Known callers and usage context:
- Not referenced directly in the local snippet; typical callers are higher-level IMAP/OAuth2 authentication code that needs a fresh access token before opening or re-authenticating an IMAP connection.
- Typical trigger: called when an access token has expired or is absent and a refresh token is available.

Why this is a separate function:
- Encapsulates network I/O, request payload construction, and JSON parsing for the refresh flow.
- Centralizes error propagation and decoding behavior so callers can implement consistent retry and error handling policies.

## Args:
    hostname (str)
        Key used to select the provider's token endpoint from the global OAUTH2_REFRESH_URLS mapping. Must match an existing key; otherwise a ValueError is raised.
    client_id (str)
        OAuth2 client identifier. Must be ASCII-encodable; the function encodes it with .encode("ascii") before sending.
    client_secret (str)
        OAuth2 client secret. Must be ASCII-encodable; encoded with .encode("ascii") before sending.
    refresh_token (str)
        OAuth2 refresh token previously issued by the provider. Must be ASCII-encodable; encoded with .encode("ascii") before sending.

Notes on parameter interdependencies:
- All three credential parameters are encoded to ASCII bytes; if any contain non-ASCII characters, calling this function will raise UnicodeEncodeError.
- hostname must be present in OAUTH2_REFRESH_URLS; the mapping determines the exact endpoint used.

## Returns:
    str: The access token string extracted from the provider's JSON response under the "access_token" key.

Possible return scenarios:
- Normal: returns the access token as a str.
- The function does not return on error conditions described under Raises.

## Raises:
    ValueError:
        If hostname is not found in the OAUTH2_REFRESH_URLS mapping (explicit check in code).
    UnicodeEncodeError:
        If client_id, client_secret, or refresh_token contain characters that cannot be encoded with ASCII (triggered by .encode("ascii")).
    urllib.error.HTTPError or urllib.error.URLError:
        Errors raised by urllib.request.urlopen for HTTP error responses or network-level failures; these are not caught inside the function.
    UnicodeDecodeError:
        If the response bytes cannot be decoded as ASCII by response.decode("ascii").
    json.JSONDecodeError:
        If the decoded response is not valid JSON.
    KeyError:
        If the parsed JSON does not contain the "access_token" key (the function accesses ["access_token"] directly).

## Constraints:
Preconditions:
- OAUTH2_REFRESH_URLS (global) must exist and map the given hostname to a valid HTTP/HTTPS token endpoint URL.
- Network access to the chosen endpoint must be available.
- client_id, client_secret, and refresh_token must be ASCII-encodable strings.

Postconditions:
- On successful return, an access token string (the "access_token" field value) has been retrieved from the provider response.
- The function does not persist or cache tokens; callers are responsible for storing tokens if desired.

## Side Effects:
- Network I/O: performs an HTTP POST to the provider's token endpoint and reads the response body via urllib.request.urlopen.
- No file I/O, no writes to global state, and no stdout/stderr output are performed by this function itself.
- External service call: interacts with the OAuth2 provider which may log or rate-limit requests.

## Implementation details (behavioral notes):
- The function builds a form payload where the values for client_id, client_secret, refresh_token are bytes (via .encode("ascii")) and grant_type is the bytes literal b"refresh_token"; the payload is then URL-encoded (urllib.parse.urlencode) and the resulting string encoded to ASCII bytes before being passed to urllib.request.urlopen.
- The function does not explicitly set HTTP headers (such as Content-Type); it relies on urllib to perform the request with the encoded body as provided. Callers should not assume a specific Content-Type header is present unless verified at runtime.

## Control Flow:
flowchart TD
    A[Start: call refresh_oauth2_token(hostname, client_id, client_secret, refresh_token)]
    A --> B{OAUTH2_REFRESH_URLS.get(hostname)}
    B -- missing --> C[Raise ValueError (unknown hostname)]
    B -- found --> D[Encode client_id, client_secret, refresh_token to ASCII bytes; set grant_type=b"refresh_token"]
    D --> E[URL-encode form data and encode to ASCII bytes]
    E --> F[POST to endpoint via urllib.request.urlopen]
    F --> G{urllib raises HTTPError/URLError?}
    G -- yes --> H[Propagate network/HTTP error]
    G -- no --> I[Read response bytes]
    I --> J[Decode response bytes using ASCII -> may raise UnicodeDecodeError]
    J --> K[Parse JSON with json.loads -> may raise JSONDecodeError]
    K --> L{"access_token" present in parsed JSON?}
    L -- no --> M[Raise KeyError]
    L -- yes --> N[Return access_token as str]
    N --> Z[End]

## Examples:
Typical usage with robust error handling

    try:
        access_token = refresh_oauth2_token(
            "provider.example.com",
            my_client_id,
            my_client_secret,
            my_refresh_token,
        )
    except ValueError as exc:
        # Configuration error: hostname not configured
        configure_provider()
    except UnicodeEncodeError:
        # Input contained non-ASCII characters
        sanitize_credentials()
    except urllib.error.HTTPError as http_exc:
        # Provider returned an HTTP error (e.g., invalid_grant)
        handle_http_error(http_exc)
    except urllib.error.URLError as url_exc:
        # Network or DNS failure
        handle_network_error(url_exc)
    except UnicodeDecodeError:
        # Provider returned bytes not decodable as ASCII
        handle_unexpected_encoding()
    except json.JSONDecodeError:
        # Provider returned malformed JSON
        handle_malformed_response()
    except KeyError:
        # JSON did not have an "access_token" field
        handle_missing_token()
    else:
        # Use the returned access_token for authenticated requests
        use_access_token(access_token)

Notes:
- In production, callers should inspect HTTP error payloads (often JSON with error details) and implement retries, backoff, and secure storage for client secrets and refresh tokens.
- If you need a specific Content-Type header or different encoding behavior, perform the HTTP request explicitly (e.g., using urllib.request.Request to set headers) rather than relying on this helper.

## `imapclient.config.get_oauth2_token` · *function*

## Summary:
Returns a cached OAuth2 access token for the given client/refresh-token combination if available; otherwise performs a refresh-token exchange and caches the resulting access token before returning it.

## Description:
This helper centralizes token retrieval and simple in-memory caching for OAuth2 access tokens keyed by the provider hostname and client credentials.

Known callers and usage context:
- Typical callers are higher-level IMAP/OAuth2 authentication code paths that need a valid access token before opening or re-authenticating an IMAP connection.
- Typical trigger: called when code needs an access token for a hostname/client pair and wants to avoid unnecessary refresh requests when a recently-obtained token is still available.

Why this logic is factored into its own function:
- Separates caching policy from the low-level refresh HTTP exchange implemented by refresh_oauth2_token.
- Ensures callers get a single, simple API that hides the cache lookup, refresh call, and cache population.
- Keeps refresh_oauth2_token focused on network I/O and parsing while this function manages the in-process cache lifecycle.

## Args:
    hostname (str):
        Provider hostname used as part of the cache key and forwarded to refresh_oauth2_token. Must be the same canonical key used by the global provider configuration.
    client_id (str):
        OAuth2 client identifier; used in the cache key and passed through to refresh_oauth2_token.
    client_secret (str):
        OAuth2 client secret; used in the cache key and passed through to refresh_oauth2_token.
    refresh_token (str):
        OAuth2 refresh token; used in the cache key and passed through to refresh_oauth2_token.

Notes on interdependencies:
- All four arguments are combined into a single tuple cache key (hostname, client_id, client_secret, refresh_token). If any value differs (even by encoding or whitespace), a different cache entry is used.
- This function does not validate the credentials itself; validation and network exchange occur inside refresh_oauth2_token.

## Returns:
    str: An OAuth2 access token string.
    - If a cached token exists for the exact tuple (hostname, client_id, client_secret, refresh_token), that cached string is returned immediately.
    - Otherwise refresh_oauth2_token(...) is called; its returned access token string is stored into the cache under the tuple key and returned.
    - There are no special sentinel return values; errors are surfaced via exceptions (see Raises).

## Raises:
    Any exception raised by refresh_oauth2_token when a cache miss occurs:
        - Common propagated exceptions include ValueError (unknown hostname), UnicodeEncodeError (non-ASCII credential data), urllib.error.HTTPError/URLError (network or HTTP errors), json.JSONDecodeError, KeyError (missing "access_token" in provider response), etc.
    NameError:
        - If the global cache object _oauth2_cache is not defined in the module scope, a NameError will be raised when the function attempts to access it. (Callers should ensure the module defines a mutable mapping object named _oauth2_cache.)

## Constraints:
Preconditions:
- The module must define a global mapping object named _oauth2_cache that supports .get(key) and item assignment (e.g., a dict). If this mapping is absent or not mapping-like, the function will raise (NameError or TypeError).
- Caller-supplied arguments must be hashable (strings are expected). The function does not coerce or normalize argument values before using them as cache components.

Postconditions:
- On successful return (no exception), _oauth2_cache[ (hostname, client_id, client_secret, refresh_token) ] is set to the returned token string.
- The returned value is the cached token (if present) or the freshly-obtained token from refresh_oauth2_token.

## Side Effects:
- Reads from and writes to the module-level in-memory cache object _oauth2_cache.
- On cache miss, performs network I/O indirectly by calling refresh_oauth2_token (which issues an HTTP POST to the provider's token endpoint).
- No file I/O or stdout/stderr output are performed by this function itself.
- Potential global-state mutation: overwrites any previous token stored under the same cache key.

## Concurrency and safety:
- The code performs get() and then assignment on _oauth2_cache without synchronization. In multi-threaded contexts this can cause redundant refresh calls or race conditions; callers that require thread-safety should wrap calls with their own locking or use a thread-safe cache implementation for _oauth2_cache.

## Control Flow:
flowchart TD
    A[Start: call get_oauth2_token(hostname, client_id, client_secret, refresh_token)]
    A --> B[Create cache_key = (hostname, client_id, client_secret, refresh_token)]
    B --> C{_oauth2_cache.get(cache_key)}
    C -- token found --> D[Return cached token]
    C -- cache miss (None) --> E[Call refresh_oauth2_token(hostname, client_id, client_secret, refresh_token)]
    E --> F{refresh_oauth2_token raises?}
    F -- raises --> G[Propagate exception to caller]
    F -- returns token --> H[_oauth2_cache[cache_key] = token]
    H --> I[Return token]

## Examples:
- Typical usage (happy path):
    token = get_oauth2_token("provider.example.com", my_client_id, my_client_secret, my_refresh_token)
    # Use token to authenticate an IMAP connection.

- Usage with error handling (cache miss may trigger network errors):
    try:
        token = get_oauth2_token("provider.example.com", cid, secret, rtoken)
    except ValueError:
        # Unknown provider hostname in configuration
        configure_provider()
    except (urllib.error.URLError, urllib.error.HTTPError) as net_exc:
        # Network or provider error occurred during refresh
        handle_network_error(net_exc)
    except Exception:
        # Other errors (encoding, JSON parsing, missing access_token) propagated from refresh_oauth2_token
        handle_unexpected_error()
    else:
        use_token(token)

- Note on cache behavior demonstration:
    1) First call with a given (hostname,client_id,client_secret,refresh_token) tuple triggers refresh_oauth2_token and stores the returned token.
    2) Subsequent calls with the identical tuple return the cached token immediately without making network requests (until the process restarts or the module cache is cleared/overwritten).

Notes:
- This function does not implement token expiration semantics; it caches blindly based on the tuple key and relies on callers or a separate cache invalidation strategy to refresh tokens that have expired.
- If you need expiration-aware caching or persistent storage, replace or wrap _oauth2_cache with a more sophisticated cache implementation and/or perform explicit expiry checks before returning a cached token.

## `imapclient.config.create_client_from_config` · *function*

*No documentation generated.*

