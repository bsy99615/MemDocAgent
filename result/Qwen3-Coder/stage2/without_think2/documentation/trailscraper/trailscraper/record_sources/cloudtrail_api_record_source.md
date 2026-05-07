# `cloudtrail_api_record_source.py`

## `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource` · *class*

## Summary:
A CloudTrail API record source that fetches and parses CloudTrail events from AWS using the CloudTrail API.

## Description:
This class provides an interface for retrieving CloudTrail events from AWS within a specified time range and converting them into structured Record objects. It serves as a data source for trailscraper's analysis capabilities, enabling examination of AWS service usage patterns and access control events.

The class is designed to be instantiated by the application's main workflow components that require CloudTrail data for analysis. It encapsulates the complexity of AWS API interactions and CloudTrail event parsing into a clean, reusable interface.

## State:
- `_client`: boto3.client('cloudtrail') - AWS CloudTrail client instance used for API calls
  - Type: boto3.client
  - Valid range: Initialized AWS CloudTrail client
  - Invariant: Set during initialization, remains constant throughout object lifetime

## Lifecycle:
- Creation: Instantiate with `CloudTrailAPIRecordSource()` - no arguments required
- Usage: Call `load_from_api(from_date, to_date)` to retrieve and parse CloudTrail events
- Destruction: No explicit cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
flowchart TD
    A[CloudTrailAPIRecordSource] --> B[load_from_api]
    B --> C[boto3.client('cloudtrail')]
    C --> D[get_paginator('lookup_events')]
    D --> E[paginate(StartTime, EndTime)]
    E --> F[Iterate responses]
    F --> G[Iterate Events]
    G --> H[json.loads(CloudTrailEvent)]
    H --> I[_parse_record]
    I --> J[Return records list]
```

## Raises:
- No explicit exceptions raised by `__init__`
- Exceptions from underlying AWS API calls or JSON parsing may propagate upward

## Example:
```python
from datetime import datetime
from trailscraper.record_sources.cloudtrail_api_record_source import CloudTrailAPIRecordSource

# Create the record source
source = CloudTrailAPIRecordSource()

# Load records from a date range
from_date = datetime(2023, 1, 1)
to_date = datetime(2023, 1, 2)
records = source.load_from_api(from_date, to_date)

# Process the records
for record in records:
    print(f"Event: {record.event_name} from {record.event_source}")
```

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.__init__` · *method*

## Summary:
Initializes the CloudTrailAPIRecordSource by creating a CloudTrail client for API interactions.

## Description:
This method sets up the AWS CloudTrail client that will be used to fetch CloudTrail records from the AWS API. It is called during object instantiation to establish the necessary AWS service connection.

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
    Postconditions: The instance will have a valid CloudTrail client stored in self._client

## Side Effects:
    None

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.load_from_api` · *method*

## Summary:
Retrieves and parses CloudTrail events from AWS API within a specified date range.

## Description:
Fetches CloudTrail events from AWS using the lookup_events API with pagination, then parses each event into structured Record objects. This method serves as the primary data ingestion mechanism for CloudTrail records, enabling downstream processing and analysis of AWS service activity.

The method is designed as a separate function to encapsulate the complexity of AWS API interactions and event parsing, providing a clean interface for the CloudTrailAPIRecordSource class to retrieve audit data.

## Args:
    from_date (datetime): Start time for event retrieval (inclusive)
    to_date (datetime): End time for event retrieval (exclusive)

## Returns:
    list[Record]: A list of parsed Record objects representing CloudTrail events, or empty list if no events found

## Raises:
    Exception: Propagates any exceptions raised by boto3 client operations or CloudTrail API calls

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - from_date must be a datetime object earlier than to_date
        - Both from_date and to_date must be timezone-aware datetime objects
        - AWS credentials must be configured with appropriate permissions for CloudTrail lookup_events
        - The CloudTrail service must be available in the configured AWS region
        
    Postconditions:
        - Returns a list of Record objects with parsed CloudTrail data
        - All returned records are from the specified time range
        - Empty list is returned when no events match the criteria

## Side Effects:
    - Makes external API calls to AWS CloudTrail service
    - May perform network I/O operations
    - Uses boto3 client for CloudTrail service

