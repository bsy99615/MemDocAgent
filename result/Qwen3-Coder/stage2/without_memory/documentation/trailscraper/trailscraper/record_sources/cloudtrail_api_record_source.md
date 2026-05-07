# `cloudtrail_api_record_source.py`

## `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource` · *class*

## Summary:
A record source that fetches AWS CloudTrail events from the CloudTrail API for a specified time range.

## Description:
This class provides an interface to retrieve CloudTrail events from AWS using the CloudTrail API's lookup_events functionality. It is designed to be used as a data source for processing CloudTrail records, particularly for security auditing and compliance monitoring. The class handles pagination automatically and converts raw CloudTrail JSON events into structured Record objects.

## State:
- `_client`: boto3.client('cloudtrail') instance created in __init__ (currently unused)
  - Type: boto3.client
  - Valid range: AWS CloudTrail service client

## Lifecycle:
- Creation: Instantiate with `CloudTrailAPIRecordSource()` - no arguments required
- Usage: Call `load_from_api(from_date, to_date)` to fetch events within a time range
- Destruction: No explicit cleanup required; relies on boto3's connection management

## Method Map:
```mermaid
graph TD
    A[CloudTrailAPIRecordSource] --> B[load_from_api]
    B --> C[boto3.client('cloudtrail')]
    C --> D[get_paginator('lookup_events')]
    D --> E[paginate(StartTime, EndTime)]
    E --> F[response_iterator]
    F --> G{response['Events']}
    G --> H[_parse_record(json.loads(event['CloudTrailEvent']))]
    H --> I[Record objects]
    I --> J[return records]
```

## Raises:
- No explicit exceptions are raised by __init__
- Exceptions from boto3 client operations or JSON parsing may propagate upward
- Invalid date formats or AWS authentication issues could cause runtime errors

## Example:
```python
from datetime import datetime
from trailscraper.record_sources.cloudtrail_api_record_source import CloudTrailAPIRecordSource

# Create the record source
source = CloudTrailAPIRecordSource()

# Define time range
start_time = datetime(2023, 1, 1)
end_time = datetime(2023, 1, 2)

# Load records from CloudTrail API
records = source.load_from_api(start_time, end_time)

# Process records
for record in records:
    print(f"Event: {record.event_name} from {record.event_source}")
```

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.__init__` · *method*

## Summary:
Initializes a CloudTrail API record source by creating and storing a boto3 CloudTrail client for subsequent API operations.

## Description:
This method sets up the AWS CloudTrail client that will be used to fetch CloudTrail events from the AWS API. It creates a boto3 client for the CloudTrail service and stores it as an instance variable for later use by other methods in the class.

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
    Postconditions: The instance will have a valid boto3 CloudTrail client stored in self._client

## Side Effects:
    None

### `trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource.load_from_api` · *method*

## Summary:
Fetches CloudTrail events from AWS API within a specified date range and parses them into Record objects.

## Description:
Retrieves CloudTrail events from AWS using the CloudTrail API's lookup_events operation with pagination. This method is designed to fetch events within a specific time window and convert them into structured Record objects for further processing. The method handles large result sets through pagination and includes error handling for malformed events.

This method exists as a separate function to encapsulate the AWS API interaction and parsing logic, making it reusable and testable. It provides a clean interface for retrieving CloudTrail data while abstracting away the complexity of the AWS SDK and event parsing.

## Args:
    from_date (datetime): Start time for fetching CloudTrail events (inclusive)
    to_date (datetime): End time for fetching CloudTrail events (exclusive)

## Returns:
    list[Record]: A list of parsed CloudTrail Record objects containing event metadata such as event source, event name, timestamp, resources, and roles. Returns an empty list if no events are found.

## Raises:
    ClientError: When the AWS CloudTrail API call fails due to permissions, invalid parameters, or service issues
    KeyError: When CloudTrail event data is missing required fields during parsing

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - from_date must be a datetime object representing a valid start time
    - to_date must be a datetime object representing a valid end time
    - to_date must be after from_date
    - AWS credentials must be configured with appropriate CloudTrail permissions
    
    Postconditions:
    - Returns a list of Record objects (empty list if no events found)
    - All returned Record objects are properly parsed with valid timestamps and event data

## Side Effects:
    - Makes external HTTP calls to AWS CloudTrail API
    - May perform I/O operations for network requests and JSON parsing
    - Uses boto3 client which may cache credentials or connections

