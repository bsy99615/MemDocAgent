# `cloudtrail_api_record_source.py`

## `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource` · *class*

## Summary:
A CloudTrail API record source that fetches and parses CloudTrail events from AWS for policy analysis.

## Description:
The CloudTrailAPIRecordSource class provides an interface for retrieving CloudTrail events from AWS using the CloudTrail API. It serves as a data source for IAM policy analysis by fetching events within a specified time range and converting them into structured Record objects. This class abstracts away the complexity of AWS API interactions and JSON parsing, providing a clean interface for accessing CloudTrail data.

This class is designed to be used as part of a larger system for analyzing AWS CloudTrail logs to generate IAM policies or assess access patterns. It implements the standard pattern of fetching paginated results from AWS services and transforming raw data into a structured format suitable for downstream processing.

## State:
- _client: boto3.client('cloudtrail') - AWS CloudTrail client instance used for API calls
  - Type: boto3.client
  - Invariant: Initialized in __init__, remains constant throughout object lifetime

## Lifecycle:
- Creation: Instantiate with `CloudTrailAPIRecordSource()` - no arguments required
- Usage: Call `load_from_api(from_date, to_date)` to fetch records within a date range
- Destruction: No explicit cleanup required; relies on Python's garbage collection for boto3 client resources

## Method Map:
```mermaid
graph TD
    A[CloudTrailAPIRecordSource] --> B[load_from_api]
    B --> C[boto3.client('cloudtrail')]
    C --> D[get_paginator('lookup_events')]
    D --> E[paginate(StartTime, EndTime)]
    E --> F[Iterate responses]
    F --> G[Iterate Events]
    G --> H[json.loads(event['CloudTrailEvent'])]
    H --> I[_parse_record()]
    I --> J[Return records list]
```

## Raises:
- No explicit exceptions are raised by __init__ method
- The load_from_api method may raise boto3 client exceptions if AWS API calls fail
- The _parse_record function may raise KeyError if CloudTrail events are malformed

## Example:
```python
from datetime import datetime
from trailscraper.record_sources.cloudtrail_api_record_source import CloudTrailAPIRecordSource

# Create the record source
source = CloudTrailAPIRecordSource()

# Fetch CloudTrail events from a specific time period
from_date = datetime(2023, 1, 1)
to_date = datetime(2023, 1, 2)
records = source.load_from_api(from_date, to_date)

# Process the records
for record in records:
    print(f"Event: {record.event_name} from {record.event_source}")
```

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.__init__` · *method*

## Summary:
Initializes a CloudTrail API client for fetching CloudTrail records.

## Description:
This method sets up the AWS CloudTrail client that will be used to make API calls to retrieve CloudTrail log events. It creates a boto3 client specifically configured for the CloudTrail service, which is essential for the record scraping functionality of this source.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self._client

## Constraints:
    Preconditions: None
    Postconditions: The instance will have a properly initialized CloudTrail client available for subsequent operations.

## Side Effects:
    Creates a boto3 client instance which may involve credential resolution and potential network calls during client initialization.

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.load_from_api` · *method*

## Summary:
Fetches and parses CloudTrail events from AWS API within a specified date range into structured record objects.

## Description:
Retrieves CloudTrail events from AWS using the CloudTrail API's lookup_events operation, paginates through all results, and converts each event into a structured Record object for further analysis. This method serves as the primary data ingestion mechanism for CloudTrail event data from AWS.

The method is designed as a separate component to isolate the AWS API interaction and data transformation logic, making it easier to test, mock, and replace with alternative data sources while maintaining the same interface contract.

## Args:
    from_date (datetime): Start timestamp for filtering CloudTrail events
    to_date (datetime): End timestamp for filtering CloudTrail events

## Returns:
    list[Record]: A list of parsed Record objects representing CloudTrail events, or empty list if no events found

## Raises:
    ClientError: When AWS API calls fail due to authentication issues, rate limiting, or invalid parameters
    KeyError: When CloudTrail event data is malformed and missing required fields
    json.JSONDecodeError: When CloudTrail event JSON parsing fails

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - from_date must be a datetime object representing a valid start time
        - to_date must be a datetime object representing a valid end time
        - from_date must be earlier than or equal to to_date
        - Both dates must be within AWS CloudTrail's supported time range
        
    Postconditions:
        - Returns a list of Record objects with parsed CloudTrail event data
        - All returned records are valid and properly formatted
        - If no events exist in the time range, returns an empty list

## Side Effects:
    - Makes external HTTP calls to AWS CloudTrail API
    - Performs JSON parsing operations on CloudTrail event data
    - May involve significant I/O operations depending on the date range size

