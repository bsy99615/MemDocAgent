# `cloudtrail_api_record_source.py`

## `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource` · *class*

## Summary:
A CloudTrail API record source that fetches and parses CloudTrail events from AWS using the lookup_events API.

## Description:
The CloudTrailAPIRecordSource class provides an interface for retrieving CloudTrail events from AWS through the CloudTrail API. It is designed to be used as a data source for security analysis and auditing workflows, specifically fetching events within a specified time range and converting them into structured Record objects.

This class implements a record source abstraction that allows the system to retrieve CloudTrail data from AWS API rather than from local files or other sources. It handles pagination automatically and integrates with the existing CloudTrail event parsing infrastructure.

## State:
- _client: boto3.client('cloudtrail') instance for making API calls (currently unused in load_from_api)
  - Type: boto3.client object
  - Valid range: Initialized with AWS CloudTrail service client
  - Invariant: Must be a valid CloudTrail client instance for API operations

## Lifecycle:
- Creation: Instantiate with no arguments; initializes internal boto3 CloudTrail client (though not used in load_from_api)
- Usage: Call load_from_api() method with from_date and to_date parameters to fetch records
- Destruction: No explicit cleanup required; relies on Python's garbage collection for boto3 client

## Method Map:
```mermaid
graph TD
    A[CloudTrailAPIRecordSource] --> B[load_from_api(from_date, to_date)]
    B --> C[boto3.client('cloudtrail')]
    C --> D[get_paginator('lookup_events')]
    D --> E[paginate(StartTime=from_date, EndTime=to_date)]
    E --> F[Iterate through responses]
    F --> G[Parse each event with _parse_record]
    G --> H[Return list of Record objects]
```

## Raises:
- __init__: May raise boto3.exceptions.ClientError if AWS credentials are invalid or insufficient permissions
- load_from_api: May raise exceptions from boto3 operations or _parse_record function:
  - boto3.exceptions.ClientError: When API calls fail due to permissions, invalid dates, or service issues
  - KeyError: When _parse_record encounters malformed CloudTrail events
  - ValueError: When datetime parsing fails in _parse_record

## Example:
```python
from datetime import datetime
from trailscraper.record_sources.cloudtrail_api_record_source import CloudTrailAPIRecordSource

# Create the record source
source = CloudTrailAPIRecordSource()

# Fetch CloudTrail events from a specific time range
from_date = datetime(2023, 1, 1)
to_date = datetime(2023, 1, 2)
records = source.load_from_api(from_date, to_date)

# Process the records
for record in records:
    print(f"Event: {record.event_name} from {record.event_source}")
```

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.__init__` · *method*

## Summary:
Initializes a CloudTrailAPIRecordSource instance by creating a boto3 CloudTrail client for API interactions.

## Description:
Configures the CloudTrailAPIRecordSource object with a boto3 CloudTrail client that will be used for making API calls to retrieve CloudTrail events. This method is called during object instantiation and sets up the necessary AWS service client for subsequent API operations.

The method follows the standard boto3 pattern for creating service clients and stores the client instance in the object's internal state for later use in API operations.

## Args:
    None

## Returns:
    None

## Raises:
    boto3.exceptions.ClientError: May be raised during client creation if AWS credentials are invalid or insufficient permissions exist for accessing the CloudTrail service.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._client - stores the initialized boto3 CloudTrail client instance

## Constraints:
    Preconditions: None
    Postconditions: The self._client attribute is initialized with a valid boto3 CloudTrail client instance

## Side Effects:
    None

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.load_from_api` · *method*

## Summary:
Fetches and parses CloudTrail events from AWS within a specified time range into structured record objects.

## Description:
Retrieves CloudTrail events from AWS using the CloudTrail API's lookup_events operation, paginates through results, and converts each raw CloudTrail event into a structured Record object for security analysis. This method serves as the primary interface for obtaining CloudTrail data from the AWS API.

The method uses boto3's pagination feature to handle potentially large result sets efficiently. Each retrieved event is parsed using the internal `_parse_record` function which extracts meaningful metadata and handles malformed records gracefully by returning None. Note that this implementation creates a new boto3 client instance rather than using the class's existing client.

## Args:
    from_date (datetime): Start timestamp for filtering CloudTrail events (inclusive)
    to_date (datetime): End timestamp for filtering CloudTrail events (exclusive)

## Returns:
    list[Record]: A list of parsed Record objects representing CloudTrail events within the specified time range. Returns an empty list if no events are found or if all events fail parsing.

## Raises:
    ClientError: Raised when the AWS CloudTrail API call fails due to authentication issues, invalid parameters, or service unavailability.
    KeyError: May be raised by _parse_record when processing malformed CloudTrail events that lack required fields.
    ValueError: May be raised by _parse_record when processing CloudTrail events with invalid timestamp formats.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - Both from_date and to_date must be datetime objects
        - from_date must be earlier than to_date
        - The AWS credentials must have appropriate permissions for CloudTrail lookup_events operation
        - The time range should be within the retention period of CloudTrail logs (typically 90 days)

    Postconditions:
        - Returns a list of Record objects or empty list if no events found
        - All returned records have been processed through _parse_record function
        - The method does not modify any instance state

## Side Effects:
    - Makes external API calls to AWS CloudTrail service
    - May perform I/O operations for network communication with AWS
    - Uses boto3 client for CloudTrail API interactions
    - May log warnings when _parse_record encounters malformed CloudTrail events

