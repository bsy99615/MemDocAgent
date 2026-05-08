# `cloudtrail_api_record_source.py`

## `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource` · *class*

## Summary:
Represents a CloudTrail-backed record source that calls the AWS CloudTrail API (LookupEvents) and converts each returned CloudTrailEvent JSON string into parsed Record objects via the shared _parse_record helper.

## Description:
This class is a small adaptor that queries the CloudTrail service for events between two timestamps and maps each CloudTrail event JSON payload into the project Record type using trailscraper.cloudtrail._parse_record.

Typical scenarios:
- Instantiate when you want to load CloudTrail events directly from the AWS CloudTrail API instead of reading event files.
- Called by higher-level pipelines that accept lists of parsed Records for further processing (filtering, statement generation, analysis).
- Known dependency: trailscraper.cloudtrail._parse_record which performs JSON->Record mapping and may return None for parse failures.

Responsibility boundary:
- This class is responsible only for:
  * Querying CloudTrail for events between two timestamps.
  * Deserializing the CloudTrailEvent JSON strings and delegating parsing to _parse_record.
- It does NOT perform filtering, validation beyond JSON deserialization, or persistence of results.
- It does not manage pagination beyond using the boto3 paginator; boto3 handles the pagination iteration.

## State:
- Attributes:
    - _client (boto3.CloudTrail): instance created in __init__ by boto3.client('cloudtrail').
        * Type: the object returned by boto3.client('cloudtrail').
        * Valid values: a live boto3 CloudTrail client object.
        * Invariant: if __init__ completed successfully, _client is set to a boto3 CloudTrail client.
- __init__ parameters:
    - None. The constructor takes no arguments and immediately creates a boto3 CloudTrail client.
- Class invariants:
    - After construction, self._client refers to a CloudTrail client instance (subject to boto3's behavior).
    - No other attributes are created or mutated by methods in this class.

## Lifecycle:
- Creation:
    - Instantiate with CloudTrailAPIRecordSource().
    - No arguments are required.
    - __init__ calls boto3.client('cloudtrail') at construction time; this may attempt to read AWS config/credentials.
- Usage:
    - Call load_from_api(from_date, to_date) to retrieve events between the two timestamps.
    - from_date and to_date must be provided (see Method section for expected types).
    - Typical sequence:
        1. Instantiate: source = CloudTrailAPIRecordSource()
        2. Query: records = source.load_from_api(from_dt, to_dt)
        3. Process the returned list, taking care to skip None entries and handle exceptions that may have propagated.
    - Methods may be called repeatedly; there is no per-call resource acquisition beyond boto3 client/paginator usage.
- Destruction / cleanup:
    - There is no explicit close() or context-manager support.
    - No explicit network or file handles are held beyond boto3 client internals; rely on Python/Garbage Collection and boto3 for cleanup.

## Method Map:
flowchart LR
    Init[__init__()] --> CreatesClient[self._client = boto3.client('cloudtrail')]
    Load[load_from_api(from_date,to_date)] --> LocalClient[client = boto3.client('cloudtrail')]
    LocalClient --> Paginator[client.get_paginator('lookup_events')]
    Paginator --> Paginate[response_iterator = paginator.paginate(StartTime=from_date, EndTime=to_date)]
    Paginate --> ForResponses[for response in response_iterator]
    ForResponses --> ForEvents[for event in response['Events']]
    ForEvents --> JsonLoad[json.loads(event['CloudTrailEvent'])]
    JsonLoad --> Parse[_parse_record(parsed_json)]
    Parse --> Append[records.append(parsed_record)]
    Append --> Return[return records]

Notes:
- The class stores a client at __init__ but load_from_api instantiates a fresh local client instead of using self._client.

## Methods (behavioral detail)
- __init__(self)
    - Side effect: creates and stores a boto3 CloudTrail client at self._client.
    - Typical failure modes: boto3.client may raise boto3/botocore exceptions if AWS configuration or environment is invalid.

- load_from_api(self, from_date, to_date)
    - Purpose: Query CloudTrail LookupEvents for events whose timestamp is between from_date and to_date, parse each event payload, and return a list of parsed results.
    - Args:
        * from_date (datetime.datetime): lower bound timestamp for LookupEvents StartTime. Provide a datetime-compatible object (e.g., datetime.datetime). No timezone conversion is applied by this wrapper; pass the desired UTC-aware or naive datetime consistent with your boto3 usage.
        * to_date (datetime.datetime): upper bound timestamp for LookupEvents EndTime. Same expectations as from_date.
    - Returns:
        list: A list of parsed results where each element is the exact value returned by _parse_record(json.loads(event['CloudTrailEvent'])) for a given event, in the order returned by the paginator.
        - Important: _parse_record may return None for events it could not parse (it logs a warning and returns None on missing required top-level keys). This implementation appends whatever _parse_record returns; therefore the returned list may contain None entries. Callers should filter or skip None entries as appropriate.
    - Side effects:
        * Calls boto3.client('cloudtrail'), paginator.get_paginator('lookup_events'), and iterates responses.
        * Calls json.loads on event['CloudTrailEvent'] and then _parse_record.
    - Exceptions that may propagate (non-exhaustive):
        * boto3/botocore exceptions raised by boto3.client, paginator, or network/API errors (e.g., authentication/authorization issues, throttling, connection errors).
        * KeyError: if a response does not contain expected top-level keys such as response['Events'] or event does not contain 'CloudTrailEvent', a KeyError will be raised by the code accessing those keys.
        * json.JSONDecodeError: if event['CloudTrailEvent'] contains invalid JSON.
        * Any exception raised from _parse_record other than KeyError (notably ValueError for malformed timestamps, TypeError) will propagate to the caller.
    - Notes:
        * The method currently constructs a fresh boto3 client inside load_from_api rather than using self._client from __init__. This is an observable behavior (not a functional requirement) and may be changed if reuse is desired.

## Raises:
- Exceptions potentially raised by __init__:
    - Any exception raised by boto3.client('cloudtrail') (e.g., configuration-related exceptions). These are not explicitly caught.
- Exceptions potentially raised by load_from_api:
    - boto3/botocore exceptions from API calls or pagination.
    - KeyError if expected keys are missing in boto3 responses (response['Events'] or event['CloudTrailEvent']).
    - json.JSONDecodeError when the CloudTrailEvent string is invalid JSON.
    - ValueError, TypeError, or other exceptions propagated from _parse_record (e.g., ValueError for bad timestamp format).
    - Any other unexpected exception raised during iteration will propagate.

## Example:
1) Basic usage (happy path):
    - Preconditions: valid AWS credentials/configuration available to boto3; from_dt and to_dt are datetime.datetime instances.
    - Pattern:
        source = CloudTrailAPIRecordSource()
        try:
            records = source.load_from_api(from_dt, to_dt)
        except Exception as exc:
            # handle or log cloud/API errors, JSON errors, or parse errors that propagated
            raise

        # records is a list of items returned by _parse_record; some items may be None
        parsed_records = [r for r in records if r is not None]
        for rec in parsed_records:
            # process Record instances
            pass

2) Defensive usage with per-event inspection:
    source = CloudTrailAPIRecordSource()
    records = []
    try:
        raw_results = source.load_from_api(from_dt, to_dt)
    except json.JSONDecodeError:
        # handle bad CloudTrailEvent JSON for one of the events
        raise
    except Exception:
        # handle broader boto3/botocore exceptions (credentials, network, throttling)
        raise

    for item in raw_results:
        if item is None:
            # _parse_record logged a warning for this event; skip it
            continue
        # item is a parsed Record; use it

## Implementation notes / caveats:
- _parse_record returns None when required top-level CloudTrail fields are missing; this class does not filter out None, so callers must handle them.
- There is an inconsistency: __init__ stores a client in self._client but load_from_api creates a new local client. This is an observable behavior and may have been intentional or an oversight.
- No explicit resource cleanup API is provided.

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.__init__` · *method*

## Summary:
Creates and stores a boto3 CloudTrail client on the instance so the object has a ready-to-use CloudTrail API client after construction.

## Description:
Known callers and lifecycle context:
- Typically called by application or test code when creating a new CloudTrailAPIRecordSource instance (e.g., source = CloudTrailAPIRecordSource()) as the setup/initialization step of a pipeline that will later call load_from_api(...) to fetch events.
- Called at object creation time; this is the constructor that establishes the instance-level runtime dependency on boto3's CloudTrail client.
- Tests or dependency-injection helpers may instantiate this class to obtain an object with a valid self._client attribute.

Why this is a separate method:
- As the class constructor, __init__ encapsulates instance initialization and ensures the object invariant (presence of a CloudTrail client) immediately after instantiation.
- Separating client creation into __init__ (rather than inlining client setup in each method) clarifies intent, centralizes initialization, and enables easier mocking or replacement of the client in tests by overriding the attribute after construction.

## Args:
- None.

## Returns:
- None (constructors implicitly return None). The effect is observable via mutated instance state (self._client).

## Raises:
- Any exception raised by boto3.client('cloudtrail') during client construction will propagate unchanged. Examples (non-exhaustive): configuration/credentials related exceptions raised by boto3/botocore when constructing a client. These exceptions are not caught here.

## State Changes:
- Attributes READ:
    - None (this method does not read any existing instance attributes).
- Attributes WRITTEN:
    - self._client: set to the object returned by boto3.client('cloudtrail').

## Constraints:
- Preconditions:
    - The boto3 module must be importable.
    - The runtime environment should be in a state where boto3 can construct a CloudTrail client (AWS config/credentials may be required depending on boto3's configuration). No other instance state is required.
- Postconditions:
    - After successful return, self._client is assigned and refers to the boto3 CloudTrail client instance returned by boto3.client('cloudtrail').
    - If boto3.client raises, the instance may not be fully constructed and self._client will not be set.

## Side Effects:
- Calls boto3.client('cloudtrail') which:
    - May read local AWS configuration (files, environment variables, IAM role metadata) while creating the client.
    - May raise exceptions related to boto3/botocore configuration or initialization.
    - Does not itself perform AWS network API calls as part of client construction (network calls typically occur when client methods are invoked), but boto3 may perform some environment metadata lookups depending on configuration.
- No other external I/O, file writes, or mutations of objects outside self are performed by this method.

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.load_from_api` · *method*

## Summary:
Calls the AWS CloudTrail LookupEvents API over the specified time window using a paginator, parses each event's CloudTrailEvent JSON via trailscraper.cloudtrail._parse_record, and returns a flat list of the parsed records. The method performs network I/O and does not modify the instance.

## Description:
This method:
- Creates a boto3 CloudTrail client (boto3.client('cloudtrail')).
- Requests a paginator for the 'lookup_events' operation.
- Calls paginator.paginate with StartTime=from_date and EndTime=to_date to obtain a page iterator.
- Iterates every page in the response iterator; for each page it iterates response['Events'] and for each event it decodes event['CloudTrailEvent'] with json.loads, passes the resulting dict to trailscraper.cloudtrail._parse_record, and appends the returned value to a local list.
- Returns the list of parsed records after all pages are processed.

This encapsulates API interaction, pagination, JSON decoding, and record parsing so callers receive ready-to-use parsed records.

Call context and lifecycle:
- The source code does not define callers. In typical ingestion pipelines, this method is invoked during the collection/harvest stage to retrieve CloudTrail-based records for downstream processing.

Why this is a standalone method:
- Keeps CloudTrail-specific API calling and pagination separate from orchestration, persistence, or transformation logic.
- Localizes JSON decoding and conversion to the repository's record format via _parse_record.

## Args:
    from_date:
        Value passed directly as StartTime to paginator.paginate(...). The method does not validate or convert this value; callers must provide a value acceptable to boto3 for StartTime (commonly a datetime.datetime).
    to_date:
        Value passed directly as EndTime to paginator.paginate(...). The method does not validate or convert this value; callers must provide a value acceptable to boto3 for EndTime (commonly a datetime.datetime).

Notes:
- The method does not check or normalize timezones; provide consistent, preferably timezone-aware, datetimes if timezone correctness matters.
- The method does not enforce from_date <= to_date; such a condition should be ensured by the caller.

## Returns:
    list:
        A list containing the values returned by trailscraper.cloudtrail._parse_record for each event found in the specified interval. If no events are found, the method returns an empty list.

## Raises:
The method does not catch exceptions; the following error sources can propagate to callers:

    - Exceptions raised by boto3/botocore when creating the client, obtaining the paginator, or while paginating (e.g., authentication, network, permission, or service errors).
    - KeyError if expected keys are absent in the AWS response objects (the code accesses response['Events'] and event['CloudTrailEvent']).
    - json.JSONDecodeError if event['CloudTrailEvent'] contains invalid JSON.
    - Any exception raised by trailscraper.cloudtrail._parse_record when parsing the decoded event dict.

Callers should wrap this method if they need to handle or transform these exceptions.

## State Changes:
Attributes READ:
    None — the method does not read any instance-level attributes (no self.<attr> access).

Attributes WRITTEN:
    None — the method does not modify the instance or other external mutable state.

## Constraints:
Preconditions:
    - boto3 must be importable and usable in the runtime environment.
    - AWS credentials/configuration and network access must be present so boto3.client('cloudtrail') succeeds.
    - from_date and to_date must be acceptable to boto3 for StartTime and EndTime respectively.

Postconditions:
    - The instance remains unchanged.
    - The returned list includes one element per parsed event produced by _parse_record for all events returned by AWS within the provided time window (possibly empty).

## Side Effects:
    - Network I/O: issues paginated lookup_events requests to the AWS CloudTrail service.
    - May result in API consumption (which can cause throttling or usage costs depending on account settings).
    - No retries, logging, or exception translation occur in this method; callers must implement those concerns if needed.

## Implementation details (exact operations and keys accessed):
    - boto3.client('cloudtrail') is called.
    - paginator = client.get_paginator('lookup_events')
    - response_iterator = paginator.paginate(StartTime=from_date, EndTime=to_date)
    - For each response in response_iterator: iterate response['Events']
    - For each event: access event['CloudTrailEvent'], call json.loads(event['CloudTrailEvent']), then call trailscraper.cloudtrail._parse_record(parsed_json) and append result to records

## Practical recommendations for callers:
    - Provide datetime values compatible with your boto3 configuration and use timezone-aware datetimes to avoid ambiguity.
    - If the expected result set can be very large, consider implementing a streaming/iterator approach instead of collecting all parsed records into memory at once.
    - Wrap the call in try/except blocks when you need to handle AWS errors, JSON decoding issues, or parsing errors from _parse_record.

