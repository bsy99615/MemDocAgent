# `trailscraper.record_sources`

## Tree:
record_sources/
├── cloudtrail_api_record_source.py
└── local_directory_record_source.py

## Role:
Provide source adapters that produce lists of parsed Record objects from two distinct record backends: the AWS CloudTrail LookupEvents API and a local filesystem directory of CloudTrail delivery files. The module owns discovery and retrieval of raw CloudTrail events and converts them (directly or via helper classes) into the repository's Record objects for downstream pipelines.

## Description:
Where and when this module is used
- Primary consumers:
  - Ingestion and analysis pipelines that require a uniform list of Record objects regardless of whether events are read from AWS CloudTrail API or from locally-stored CloudTrail delivery files.
  - Higher-level orchestration code that needs a simple interface to "load records between two datetimes" without implementing backend-specific traversal/pagination logic.
- Typical usage patterns:
  - Use the CloudTrail API adapter to fetch events across a time window directly from AWS.
  - Use the local-directory adapter to scan a filesystem root for CloudTrail delivery files and aggregate parsed records from the subset of files whose filename-derived timestamps overlap a requested timeframe.

Why these components are grouped here
- Cohesion principle: both classes implement the same conceptual responsibility — act as a "record source" that returns parsed Record objects — but differ in the underlying transport: network API vs local filesystem. Grouping them isolates backend-specific retrieval logic behind a small, consistent surface that other modules can import (see component docs for details).
- Layer boundary: this module belongs to the collection/ingestion layer of the repo. It is intentionally thin and delegates parsing responsibilities to trailscraper.cloudtrail helpers (LogFile and _parse_record).

See component-level documentation for implementation details:
- trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource
- trailscraper.record_sources.local_directory_record_source.LocalDirectoryRecordSource

## Components:
- CloudTrailAPIRecordSource()
  - Signature: CloudTrailAPIRecordSource()
  - One-line role: Query AWS CloudTrail (LookupEvents) over a time window and map each event JSON to the project Record type via trailscraper.cloudtrail._parse_record.
  - See: trailscraper.record_sources.cloudtrail_api_record_source.CloudTrailAPIRecordSource

- CloudTrailAPIRecordSource.load_from_api(from_date, to_date)
  - Signature: load_from_api(from_date: datetime.datetime, to_date: datetime.datetime) -> list
  - One-line role: Use a boto3 paginator to iterate LookupEvents responses between the supplied datetimes, decode each event's CloudTrailEvent JSON, parse with _parse_record, and return a flat list of parsed items (may include None items from parse failures).

- LocalDirectoryRecordSource(log_dir)
  - Signature: LocalDirectoryRecordSource(log_dir: str)
  - One-line role: Hold a configured directory root and provide methods to discover and aggregate Record objects from CloudTrail delivery files under that root.
  - See: trailscraper.record_sources.local_directory_record_source.LocalDirectoryRecordSource

- LocalDirectoryRecordSource._valid_log_files()
  - Signature: _valid_log_files() -> Iterable[LogFile]
  - One-line role: Lazily traverse the directory tree under log_dir, wrap file paths with LogFile, yield only those LogFile instances whose filenames validate (LogFile.has_valid_filename()) and log warnings for invalid filenames.

- LocalDirectoryRecordSource.load_from_dir(from_date, to_date)
  - Signature: load_from_dir(from_date: datetime.datetime, to_date: datetime.datetime) -> list[Record]
  - One-line role: Select LogFile instances whose filename-derived timestamp overlaps the requested window (LogFile.contains_events_for_timeframe) and aggregate their parsed records into a single list.

- LocalDirectoryRecordSource.last_event_timestamp_in_dir()
  - Signature: last_event_timestamp_in_dir() -> datetime.datetime
  - One-line role: Find the most-recent LogFile by filename timestamp, load its records, and return the largest record.event_time.

Mermaid dependency graph (internal relationships)
graph LR
  A[CloudTrailAPIRecordSource] -->|calls| B[trailscraper.cloudtrail._parse_record]
  A -->|uses| C[boto3 CloudTrail paginator]
  C -->|performs| D[AWS CloudTrail service]
  E[LocalDirectoryRecordSource] -->|constructs| F[trailscraper.cloudtrail.LogFile]
  F -->|provides| G[LogFile.records(), LogFile.timestamp(), LogFile.has_valid_filename(), LogFile.contains_events_for_timeframe]
  E -->|uses| H[os.walk / filesystem]
  B -->|returns| I[Record]
  G -->|returns| I

## Public API:
- CloudTrailAPIRecordSource()
  - Description: Create an adapter instance that is conceptually ready to query CloudTrail.
  - Usage note: The constructor creates a boto3 CloudTrail client during initialization (self._client). The load_from_api method currently constructs a local boto3 client as well; callers should not rely on client reuse semantics. Ensure boto3 is available and AWS credentials/config are configured in the environment.

- CloudTrailAPIRecordSource.load_from_api(from_date, to_date) -> list
  - Description: Return a list of parsed items produced by trailscraper.cloudtrail._parse_record for every event returned by CloudTrail LookupEvents between from_date and to_date.
  - Usage note:
    - Pass datetime.datetime objects acceptable to boto3 for StartTime and EndTime (prefer timezone-aware UTC datetimes).
    - The returned list preserves paginator order and may contain None entries for events that _parse_record could not parse; callers should filter None.
    - Exceptions from boto3, json decoding, KeyError for unexpected response keys, or exceptions from _parse_record propagate to the caller.

- LocalDirectoryRecordSource(log_dir: str)
  - Description: Construct a directory-backed record source that will scan log_dir for CloudTrail delivery files.
  - Usage note:
    - log_dir is stored as-is; no existence check is performed at construction time.

- LocalDirectoryRecordSource.load_from_dir(from_date, to_date) -> list[Record]
  - Description: Aggregate and return parsed Record objects from files whose filename-derived timestamps overlap the requested window.
  - Usage note:
    - Provide datetime objects comparable with LogFile.timestamp() (LogFile returns tz-aware UTC datetimes; prefer tz-aware datetimes to avoid TypeError).
    - Selection is done by filename timestamp only — individual returned records may fall outside the exact from_date/to_date range.

- LocalDirectoryRecordSource.last_event_timestamp_in_dir() -> datetime.datetime
  - Description: Return the event_time of the most-recent record found in the most-recent log file (by filename timestamp) under log_dir.
  - Usage note:
    - Raises/provides errors when no valid files or records exist; callers should handle exceptions signaling "no data".

## Dependencies:
Internal (repo) dependencies
- trailscraper.cloudtrail
  - Purpose: Provides LogFile (filename parsing, file reading, records() implementation) and _parse_record (JSON dict -> Record mapping). Both record source classes delegate parsing and per-file logic to this module.
  - Link to component docs: consult trailscraper.cloudtrail.LogFile and trailscraper.cloudtrail._parse_record for parsing semantics, error behaviors, and timestamp formats.

External / standard library dependencies
- boto3 (third-party)
  - Purpose: CloudTrailAPIRecordSource uses boto3.client('cloudtrail') and a paginator for the LookupEvents operation to fetch cloud events.
  - Note: boto3 must be installed and configured; AWS credentials and network access are required at runtime.

- json (stdlib)
  - Purpose: Decode CloudTrailEvent JSON strings provided in LookupEvents responses before handing the dict to _parse_record.

- os (stdlib)
  - Purpose: Filesystem traversal (os.walk) to discover files under the configured directory for LocalDirectoryRecordSource.

- logging (stdlib)
  - Purpose: Emit warnings for invalid filenames discovered during directory traversal.

- datetime (stdlib types referenced)
  - Purpose: Timestamp arguments and comparisons; callers should pass datetime.datetime objects compatible with LogFile.timestamp() and boto3.

## Constraints:
- Callers must supply datetime objects appropriate for the backend:
  - For CloudTrailAPIRecordSource.load_from_api: pass datetime values accepted by boto3 (prefer timezone-aware UTC datetimes if timezone correctness matters).
  - For LocalDirectoryRecordSource.load_from_dir and last_event_timestamp_in_dir: supply datetimes comparable with LogFile.timestamp() (LogFile returns tz-aware UTC datetimes; mixing naive and aware datetimes will raise TypeError).
- Error propagation:
  - Both adapters intentionally propagate exceptions from their dependencies: boto3/botocore errors, json.JSONDecodeError, and any exceptions raised by trailscraper.cloudtrail.LogFile or _parse_record. Callers should wrap calls when they require retries, backoff, or graceful degradation.
- Handling of parse failures:
  - CloudTrailAPIRecordSource preserves whatever _parse_record returns; _parse_record may return None for unparseable events. Callers must filter None before treating results as fully-parsed Records.
- Thread-safety and concurrency:
  - These classes do not provide explicit synchronization. They hold small immutable state (CloudTrailAPIRecordSource stores a client object; LocalDirectoryRecordSource stores a log_dir string). Concurrent reads from multiple threads are generally safe if:
    - The filesystem is stable (no concurrent moving/deletion of files), and
    - boto3 client usage is acceptable in your concurrency model (boto3 clients are generally safe for concurrent use, but creating per-thread clients is recommended in high-concurrency scenarios).
  - Do not assume these adapters implement internal retries; callers should handle retries or backoff externally.
- Ordering and memory:
  - CloudTrail API retrieval preserves the paginator's order; LocalDirectoryRecordSource returns records in the filesystem discovery order (os.walk order). Neither adapter streams results to the caller by default — both return lists that may be large; for very large windows prefer implementing streaming/iterator behavior at a higher level.
- Initialization prerequisites:
  - CloudTrailAPIRecordSource: boto3 importable and the runtime environment configured with AWS credentials (or an IAM role) so that client construction and API calls succeed.
  - LocalDirectoryRecordSource: trailscraper.cloudtrail.LogFile must be available; log_dir should be a filesystem path string pointing to a readable directory when methods that traverse the tree are invoked.

---

## Files

- [`cloudtrail_api_record_source.py`](record_sources/cloudtrail_api_record_source.md)
- [`local_directory_record_source.py`](record_sources/local_directory_record_source.md)

