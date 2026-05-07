# `boto_service_definitions.py`

## `trailscraper.boto_service_definitions.boto_service_definition_files` · *function*

## Summary:
Returns a list of absolute filesystem paths for all botocore service definition JSON files (files named service-*.json) present inside the installed botocore package data directory.

## Description:
This function locates the installed botocore package data directory using pkg_resources.resource_filename and walks that directory tree to collect every file whose filename matches the pattern service-*.json. It exists to centralize the logic for locating botocore service definition JSON files so callers can load or analyze those definitions without duplicating filesystem-lookup code.

Known callers within the codebase:
- No direct callers were discovered during this documentation generation. Typical consumers are modules that need to parse or inspect botocore service definitions (for example, a module that extracts API operations, shapes, or endpoints from botocore’s JSON service descriptions).

Why this is a separate function:
- Encapsulates the platform- and package-dependent logic for locating botocore's data directory and enumerating service-*.json files.
- Keeps file discovery separate from parsing/processing logic so callers receive a simple list of file paths and can independently decide how to open/parse them or handle errors.

## Args:
- None.

## Returns:
- list[str]: A list of absolute filesystem paths (strings). Each element is the full path to a file whose basename matches service-*.json under the botocore data directory.
- Possible return values:
    - A list of one or more file paths when matching files are found.
    - An empty list when no matching files are present.
- The function never returns None.

## Raises:
- This function does not explicitly raise custom exceptions; it propagates exceptions raised by the underlying calls:
    - Exceptions from pkg_resources.resource_filename if the botocore package cannot be located or its data directory cannot be resolved (for example, pkg_resources.DistributionNotFound or other pkg_resources exceptions).
    - Any exceptions raised while accessing the filesystem during os.walk (e.g., OSError variants) will propagate.
- No exceptions are caught or suppressed within the function.

## Constraints:
Preconditions:
- The runtime environment should have the botocore package installed and accessible to pkg_resources. If botocore is missing or its package metadata is not available, resource_filename will raise an error and this function will fail.

Postconditions:
- On successful return, the returned list contains the absolute paths of all files under the located botocore data directory whose names match service-*.json.
- No filesystem modifications are made by the function.

## Side Effects:
- Performs read-only filesystem operations (pkg_resources metadata resolution and os.walk over the botocore data directory). There are no writes to disk, network calls, or global-state mutations performed by this function.

## Control Flow:
flowchart TD
    Start([Start]) --> ResolvePkgResources[Call resource_filename(Requirement('botocore'), 'botocore/data')]
    ResolvePkgResources -->|error| RaiseResourceError([Raise/propagate pkg_resources error])
    ResolvePkgResources --> WalkFS[os.walk(botocore_data_dir)]
    WalkFS --> ForEachDir[For each directory encountered]
    ForEachDir --> ForEachFile[For each file name in directory]
    ForEachFile --> MatchPattern{fnmatch file_in_dir == "service-*.json"?}
    MatchPattern -->|yes| BuildPath[os.path.join(dirname, file_in_dir) -> add to list]
    MatchPattern -->|no| SkipFile[skip file]
    BuildPath --> ContinueLoop[continue]
    SkipFile --> ContinueLoop
    ContinueLoop --> AfterWalk[After walk completes]
    AfterWalk --> ReturnList[Return list of matching file paths]
    ReturnList --> End([End])

## Examples:
Example — iterate service definition files and load them safely:
1. Call the function to get service definition file paths.
2. If the returned list is empty, handle that case (no definitions available).
3. For each returned path, open the file and parse JSON, handling file or JSON errors per-file so a single bad file does not stop processing.

Conceptual usage (pseudocode steps):
- paths = boto_service_definition_files()
- if not paths:
    - handle "no definitions found" (log, fallback, or raise)
- for path in paths:
    - try:
        - with open(path, 'r') as fh:
            - data = json.load(fh)
        - process service definition contained in data
    - except (OSError, json.JSONDecodeError) as e:
        - log or handle the error for this file and continue to next

This approach ensures callers separate discovery (this function) from parsing and error handling (caller responsibility).

## `trailscraper.boto_service_definitions.service_definition_file` · *function*

## Summary:
Return the filesystem path of the "latest" botocore JSON service definition for a given AWS service name by filtering the list of discovered botocore service-*.json files, sorting them, and returning the final element.

## Description:
This function locates all botocore service definition files (via boto_service_definition_files()), filters them to those that match the shell-style pattern "**/{servicename}/*/service-*.json", sorts the matching paths lexicographically, and returns the last entry (the element at index -1) from the sorted list.

Known callers within the codebase:
- No direct callers were discovered during documentation generation. Typical consumers are modules that need a single service definition JSON file path for a specific AWS service (for example, to open and parse the chosen service's JSON description).

Why extracted into its own function:
- Encapsulates the logic for selecting a single service definition file for a named service from the full set of botocore service definition files. This separates discovery (boto_service_definition_files) from selection (filter → sort → pick last) allowing callers to request "the selected file" directly without duplicating filtering and selection logic.

Notes:
- Matching is performed using Python's fnmatch (shell-style wildcards) against the list of paths returned by boto_service_definition_files(). Because boto_service_definition_files() returns absolute file paths, the pattern "**/{servicename}/*/service-*.json" is applied to those path strings.
- The function calls boto_service_definition_files() twice; as boto_service_definition_files performs filesystem enumeration this duplicates work and may be inefficient. If repeated calls to boto_service_definition_files() can return different results (e.g., concurrent filesystem changes), behavior may vary between the two calls.

## Args:
    servicename (str): AWS service identifier used in the path-matching pattern (for example "s3", "ec2", "iam").
        - Required: must be a non-empty string.
        - Allowed values: any string; practical values are botocore service directory names. If the provided servicename does not appear in the filesystem paths produced by boto_service_definition_files(), no match will be found and the function will raise IndexError.
        - No other parameters.

## Returns:
    str: An absolute filesystem path (string) that is the last element of the lexicographically sorted list of paths matching the pattern "**/{servicename}/*/service-*.json".
    - Typical successful return: a valid path to a service-*.json file for the requested service.
    - Edge-case returns: the function does not return None. If no matching files exist the function does not return gracefully — it raises (see Raises).

## Raises:
    IndexError:
        - Trigger condition: the filtered list of matching service definition paths is empty, so attempting to access service_definitions_for_service[-1] raises IndexError.
        - This is the primary failure mode callers must guard against if a servicename may be absent.

    Propagated exceptions from boto_service_definition_files():
        - Examples: pkg_resources.DistributionNotFound or other pkg_resources exceptions if the botocore package cannot be located; OSError or other filesystem errors emitted by os.walk inside boto_service_definition_files().
        - These exceptions are not caught or transformed by this function — they propagate to the caller.

## Constraints:
Preconditions:
    - The runtime must have the botocore package discoverable by pkg_resources (since boto_service_definition_files() uses pkg_resources.resource_filename).
    - servicename should correspond to a directory name used inside botocore data paths (non-empty string).

Postconditions:
    - On successful return, the caller receives a single string path pointing to a botocore service-*.json file matching the servicename pattern.
    - No global state or filesystem modifications are performed by this function; it only triggers read operations via boto_service_definition_files().

## Side Effects:
    - Indirect read-only filesystem I/O: calls boto_service_definition_files(), which resolves pkg_resources and walks the botocore data directory.
    - No writes, network calls, or global-state mutations originate from this function.

## Control Flow:
flowchart TD
    Start([Start]) --> CallDiscover[Call boto_service_definition_files()]
    CallDiscover --> GetAllPaths[Receive list of file paths]
    GetAllPaths --> Filter[Run fnmatch.filter(paths, "**/{servicename}/*/service-*.json")]
    Filter --> Sort[Sort filtered list lexicographically]
    Sort --> EmptyCheck{Is filtered list empty?}
    EmptyCheck -->|yes| RaiseIndexError[Raise IndexError (no matches)]
    EmptyCheck -->|no| ReturnLast[Return last element of sorted list]
    ReturnLast --> End([End])

## Examples:
Example — safe usage pattern with error handling:
1. Attempt to obtain the selected service definition path and open it, handling the absent-service case and potential pkg_resources/filesystem errors.

    try:
        path = service_definition_file("s3")
    except IndexError:
        # No service definition matched "s3" — handle (log, fallback, or raise a clearer error)
        handle_no_definition()
    except Exception as e:
        # Propagated errors from boto_service_definition_files (pkg_resources, filesystem) — handle or re-raise
        handle_environment_error(e)
    else:
        # Open and parse the JSON definition at the returned path
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        process_service_definition(data)

Example — defensive check before calling (to avoid IndexError):
    all_paths = boto_service_definition_files()
    matches = fnmatch.filter(all_paths, "**/ec2/*/service-*.json")
    if not matches:
        handle_no_definition()
    else:
        matches.sort()
        chosen = matches[-1]
        with open(chosen, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        process_service_definition(data)

These examples show how to handle the two common failure modes:
- no matches for the given servicename (IndexError if unhandled), and
- environment/discovery errors raised by boto_service_definition_files().

## `trailscraper.boto_service_definitions.operation_definition` · *function*

## Summary:
Return the operation model dictionary for a named operation from a service's botocore JSON definition file.

## Description:
This function opens the selected botocore service JSON definition file for the requested AWS service (using service_definition_file(servicename)), parses the JSON, and returns the mapping that describes the named operation inside the service's "operations" section.

Known callers within the codebase:
- None discovered during documentation generation. Typical consumers are code paths that need the metadata for a specific API operation (for example, to inspect input/output shapes, documentation, parameters, or error shapes before generating client calls or shaping telemetry).

Why this logic is extracted:
- Encapsulates the small but repeated pattern of: obtain the chosen service-definition file path, open and parse it, then return the operation entry. This separates file-selection (service_definition_file) and JSON parsing/operation lookup into a single convenience helper so callers don't duplicate open/parse/access code and so they receive a single well-defined failure surface (exceptions from file discovery, file I/O, JSON parsing, or missing operation).

## Args:
    servicename (str): AWS service identifier used to choose the service definition file (e.g., "s3", "ec2", "iam").
        - Required: must be a non-empty string.
        - Behavior: passed to service_definition_file(servicename) to locate a filesystem path; invalid or missing servicename may cause service_definition_file to raise IndexError or related discovery errors.
    operationname (str): The name of the operation to retrieve from the service definition's "operations" mapping (exact key expected as present in the JSON).
        - Required: must be a non-empty string matching a key in the parsed JSON's "operations" object.
        - Interdependency: operationname lookup only makes sense for a valid servicename that yields a JSON file containing an "operations" mapping.

## Returns:
    dict: The operation model dictionary corresponding to the requested operationname from the parsed service definition JSON, i.e., service_definition['operations'][operationname].
    - Normal return: a dict (mapping) containing the operation description (parameters, shapes, documentation, errors, etc.) as present in the botocore JSON.
    - Edge cases:
        - The function never returns None. If the "operations" mapping does not contain operationname, a KeyError is raised (see Raises).
        - If the JSON cannot be parsed, json.JSONDecodeError (or a subclass) is raised.
        - If opening the file fails, an OSError/FileNotFoundError (or other I/O exception) is raised.

## Raises:
    IndexError:
        - Condition: propagated from service_definition_file(servicename) when no matching service definition file is found and service_definition_file attempts to select the last element of an empty list.
    KeyError:
        - Condition: the parsed service definition JSON contains no key equal to operationname within its top-level "operations" mapping; triggered by service_definition['operations'][operationname].
    json.JSONDecodeError (or ValueError in some Python versions):
        - Condition: the file content is not valid JSON and json.loads fails.
    OSError / FileNotFoundError:
        - Condition: opening the returned path fails (e.g., file removed between discovery and open, or insufficient permissions).
    pkg_resources.* exceptions (e.g., DistributionNotFound) or other exceptions raised by service_definition_file or its subcalls:
        - Condition: underlying discovery via pkg_resources.resource_filename or filesystem enumeration fails; these exceptions are propagated unchanged.

## Constraints:
Preconditions:
    - The runtime environment must be able to locate botocore service definition files via service_definition_file(servicename); otherwise callers should expect IndexError or pkg_resources errors.
    - servicename and operationname should be valid, non-empty strings appropriate for botocore service and operation keys.

Postconditions:
    - On success, the caller receives a dict representing the requested operation model. No files are left open (the file is opened using a context manager and closed on exit).
    - No global state or external resources are modified by this function.

## Side Effects:
    - Performs read-only filesystem I/O: opens and reads the chosen service-definition JSON file.
    - No network I/O, no writes, and no mutation of global variables within this function itself.
    - External state mutations may occur indirectly through service_definition_file (e.g., pkg_resources lookups) but are not performed by this function.

## Control Flow:
flowchart TD
    Start([Start]) --> ResolvePath[Call service_definition_file(servicename)]
    ResolvePath --> OpenFile[Open returned file path]
    OpenFile --> ReadContent[Read file content]
    ReadContent --> ParseJSON[json.loads(content)]
    ParseJSON --> GetOps{Does top-level "operations" exist and is mapping?}
    GetOps -->|no| KeyErrorRaise[Raise KeyError when accessing operations mapping]
    GetOps -->|yes| LookupOp[Access service_definition['operations'][operationname]]
    LookupOp -->|found| ReturnOp[Return operation dict]
    LookupOp -->|missing| KeyErrorRaise2[Raise KeyError (operationname not found)]
    KeyErrorRaise --> End([End])
    KeyErrorRaise2 --> End([End])
    ReturnOp --> End([End])

## Examples:
Example — typical usage with robust error handling:
    try:
        op = operation_definition("s3", "PutObject")
    except IndexError:
        # No service definition file could be selected for "s3"
        handle_missing_service_definition()
    except (OSError, FileNotFoundError):
        # File disappeared or I/O error while opening
        handle_io_failure()
    except json.JSONDecodeError:
        # Malformed JSON file
        handle_corrupt_definition()
    except KeyError:
        # Operation "PutObject" not present in the service's "operations" mapping
        handle_missing_operation()
    except Exception as e:
        # Any other propagated discovery/ pkg_resources errors
        handle_unexpected_error(e)
    else:
        # Use the returned operation model (a dict) to inspect input shapes, documentation, etc.
        process_operation_model(op)

Example — defensive pre-check to avoid KeyError:
    # Enumerate and inspect the parsed definition before direct lookup
    path = service_definition_file("ec2")
    with open(path, "r", encoding="utf-8") as fh:
        svc = json.load(fh)
    ops = svc.get("operations") or {}
    if "RunInstances" not in ops:
        handle_missing_operation()
    else:
        run_instances_model = ops["RunInstances"]
        process_operation_model(run_instances_model)

