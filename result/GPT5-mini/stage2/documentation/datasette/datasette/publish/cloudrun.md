# `cloudrun.py`

## `datasette.publish.cloudrun.publish_subcommand` · *function*

*No documentation generated.*

## `datasette.publish.cloudrun.get_existing_services` · *function*

## Summary:
Queries the local gcloud configuration for Cloud Run services (managed platform), parses the JSON output, and returns a list of lightweight service descriptors (name, creation timestamp, and URL).

## Description:
This utility is intended to be used by the Cloud Run publish workflow to enumerate services already deployed in the current gcloud project and region. Typical callers invoke this function before deciding whether to create, update, or reuse an existing service during a deployment pipeline.

This logic is extracted into its own function to:
- Encapsulate the subprocess invocation and JSON parsing in one place.
- Provide a single point to handle common error conditions from the gcloud call and JSON decoding.
- Keep higher-level deployment logic focused on decision-making (create vs update) rather than on low-level command invocation and parsing.

Known callers within the codebase:
- Functions in the same publish/cloudrun module that perform deployment decisions (e.g., the publish command flow). If no direct caller is found in a particular scan, expect this to be called by the Cloud Run publishing command implementation during the prepare-or-deploy stage.

## Args:
This function takes no arguments.

## Returns:
list[dict]: A list of service descriptor dictionaries, one per Cloud Run service returned by gcloud, with these keys:
- "name" (str): The Cloud Run service resource name (service["metadata"]["name"]).
- "created" (str): Creation timestamp string from metadata.creationTimestamp (ISO 8601 string as returned by gcloud).
- "url" (str): The public URL for the service from status.address.url.

Edge-case return values:
- An empty list [] if gcloud returns no services.
- The function will not return partial entries; it attempts to build a descriptor for every element in the parsed JSON array and return a list of those descriptors.

## Raises:
- subprocess.CalledProcessError: If the gcloud CLI exits with a non-zero status, check_output will raise this; it indicates gcloud couldn't complete the request (e.g., not installed, not authenticated, invalid configuration, or network error).
- json.JSONDecodeError: If the output from the gcloud command is not valid JSON (for example, if gcloud emitted an error message or different format), json.loads will raise this.
- KeyError or TypeError: If an expected key path is missing from an individual service dict (for example, missing "status" or "address"), attempting to index into service["status"]["address"]["url"] or service["metadata"]["..."] can raise KeyError or a TypeError when a component is None. This indicates the command succeeded but the returned service representation differs from the expected shape.

## Constraints:
Preconditions:
- The gcloud CLI must be installed and available on PATH.
- The user must be authenticated and have access to the gcloud project and region that should be queried.
- The current environment must permit executing subprocesses (no sandbox restrictions blocking check_output).

Postconditions:
- If the call returns normally (no exception), the returned list contains one descriptor dict per service object returned by gcloud, each with the three keys "name", "created", and "url".
- No global state in Python is modified by this function.

## Side Effects:
- Executes an external process: runs the gcloud CLI command "gcloud run services list --platform=managed --format json". This implies network usage and interaction with Google Cloud APIs via the gcloud binary.
- No files are read or written by this function.
- No direct modifications to external services are performed (read-only/list operation).

## Control Flow:
flowchart TD
    A[Start] --> B[Run gcloud run services list --format json via subprocess.check_output]
    B --> C{Did subprocess complete successfully?}
    C -- No --> D[raise subprocess.CalledProcessError]
    C -- Yes --> E[json.loads(output)]
    E --> F{Valid JSON array?}
    F -- No --> G[raise json.JSONDecodeError]
    F -- Yes --> H[for each service in array -> build descriptor dict]
    H --> I{Any service missing expected keys?}
    I -- Yes --> J[raise KeyError/TypeError when accessing missing fields]
    I -- No --> K[append descriptor]
    K --> L[Return list of descriptors]
    J --> (propagates exception)

## Examples (usage described):
- Typical happy-path usage:
  - Caller invokes this function at the start of a Cloud Run publish workflow to get existing services.
  - The returned list is iterated to check whether a service with a desired name already exists; if it does, the deployment path may choose to update that service, otherwise create a new one.

- Error handling guidance:
  - Catch subprocess.CalledProcessError to handle gcloud not being present, authentication errors, or permission issues; include logging of the underlying command output for diagnosis.
  - Catch json.JSONDecodeError to detect unexpected output formats (gcloud error text instead of JSON) and surface the raw output for debugging.
  - When consuming the returned descriptors, be prepared for KeyError/TypeError if the gcloud response schema differs; callers may validate presence of "url" before assuming it's a valid HTTP endpoint.

- Example flow (non-code description):
  1. Call get_existing_services().
  2. If a CalledProcessError is raised, instruct the user to verify gcloud installation, authentication, and project selection.
  3. If json.JSONDecodeError is raised, inspect the raw gcloud output to see whether gcloud printed an error message; fix the underlying cause (authentication, API enablement).
  4. If the call returns a list, search by descriptor["name"] for the target service and read descriptor["url"] to obtain the service endpoint for subsequent health checks or to decide between reuse vs creation.

## `datasette.publish.cloudrun._validate_memory` · *function*

## Summary:
Validate a user-supplied memory size string for the Cloud Run publish command and return it unchanged if it matches the expected format, otherwise raise a click.BadParameter describing the expected format.

## Description:
This function is designed to be used as a Click callback/validator for a command-line option that accepts a memory size string (for example, a --memory option on a publish command in the cloudrun publisher). Typical caller:
- The Click option definition for the Cloud Run publish command in this module (datasette.publish.cloudrun) — called during Click's option parsing/validation stage when the user supplies the --memory value.

Why this logic is extracted:
- Centralizes and isolates the memory-format validation rule so the same rule can be reused where the --memory option is defined or referenced.
- Keeps the command definition concise and delegates input validation/argument error reporting to a focused helper function that raises the appropriate Click exception with a clear message.

## Args:
    ctx (click.Context): Click invocation context supplied by Click when running a callback. Not inspected by this function.
    param (click.Parameter): The Click parameter object that triggered the callback. Not inspected by this function.
    value (str | None): The user-provided memory value to validate. Expected to be a string like "1Gi" or "512Mi", or None if the option was not provided.

Notes on parameter interdependency:
- Only the 'value' parameter is relevant for validation; 'ctx' and 'param' are present to match Click's callback signature and are not used.

## Returns:
    str | None: Returns the original value unchanged when it is either falsy (None or empty) or matches the exact expected format.
    Possible return cases:
      - None (or empty/falsey): returned unchanged — treated as "option not provided".
      - Valid string such as "1Gi", "2G", "512Mi", "256M": returned unchanged.

## Raises:
    click.BadParameter: Raised when a non-empty value is provided that does not match the required pattern. The exact error message produced is:
      --memory should be a number then Gi/G/Mi/M e.g 1Gi
    Trigger condition:
      - value is truthy and re.match(r"^\d+(Gi|G|Mi|M)$", value) returns None.

## Constraints:
Preconditions:
    - Caller should supply typical Click callback arguments (ctx, param, value).
    - If 'value' is provided, it is expected to be a native Python string (Click typically supplies this).
    - The function assumes case-sensitive units (see pattern below).

Postconditions:
    - If the function returns normally, the returned value is either falsy (None) or a string that exactly matches the pattern: one or more decimal digits followed immediately by one of the units Gi, G, Mi, or M (case-sensitive).
    - If the function raises, no value is returned and Click is expected to display the BadParameter message to the user.

## Side Effects:
    - None. This function performs pure validation only.
    - No I/O, no global state mutation, no network or external service calls.

## Control Flow:
flowchart TD
    Start --> IsValueTruthy{value truthy?}
    IsValueTruthy -- No --> ReturnNoneOrValue[Return value unchanged]
    IsValueTruthy -- Yes --> RegexMatch{re.match(^\d+(Gi|G|Mi|M)$, value) ?}
    RegexMatch -- Yes --> ReturnValue[Return value unchanged]
    RegexMatch -- No --> RaiseBadParameter[Raise click.BadParameter("--memory should be a number then Gi/G/Mi/M e.g 1Gi")]

Notes on the pattern and decision points:
    - The pattern is anchored at both ends (^) and ($) so the entire string must match.
    - Only integer (whole number) digits are allowed before the unit; decimals, signs (+/-), or spaces will fail.
    - Units are case-sensitive and must be one of: Gi, G, Mi, M.

## Examples:
    Example inputs -> outcome
    - None -> returns None (option not provided)
    - "" (empty string) -> returns "" (treated as falsy by the function check)
    - "1Gi" -> returns "1Gi" (valid)
    - "256Mi" -> returns "256Mi" (valid)
    - "2G" -> returns "2G" (valid)
    - "512M" -> returns "512M" (valid)
    - "1gi" -> raises click.BadParameter (unit is lowercase; pattern is case-sensitive)
    - "1.5Gi" -> raises click.BadParameter (decimal not allowed)
    - "Gi" -> raises click.BadParameter (missing leading number)
    - "1 GB" -> raises click.BadParameter (space and unit not in allowed set)
    - "1024" -> raises click.BadParameter (missing unit)

Usage guidance:
    - Use this function as the `callback` argument for a Click option that accepts memory sizes so invalid inputs produce a clear CLI error message.
    - If you need to accept lowercase units or decimal quantities, change the validation pattern accordingly before using this validator.

