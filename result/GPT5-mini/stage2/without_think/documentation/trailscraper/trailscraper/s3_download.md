# `s3_download.py`

## `trailscraper.s3_download._s3_key_prefix` · *function*

## Summary:
Constructs and returns the S3 key prefix path used by AWS CloudTrail log objects for a specific account, region and date.

## Description:
This helper formats a CloudTrail S3 key prefix of the form:
    {prefix}AWSLogs/{account_id}/CloudTrail/{region}/{YYYY}/{MM}/{DD}/

Known callers:
    - No direct callers were found in the provided source for this repository snapshot. 
    - Typical callers are functions that list or download CloudTrail objects from S3 (e.g., S3 listing, filtering, or download routines) which need a deterministic prefix to enumerate objects for a single account/region/day.

Why this function exists:
    - Encapsulates the canonical CloudTrail S3 key layout in one place so other code can call it without duplicating string-format logic.
    - Keeps date-to-path formatting consistent across code paths and makes it easier to change the layout if AWS or project conventions change.

## Args:
    prefix (str):
        Base S3 path or bucket/key prefix to prepend. Examples: 's3://my-bucket/', 'my-bucket/prefix/' or ''.
        Note: the function performs a simple string concatenation; callers should ensure any needed separators (trailing slash) are present if required.
    date (datetime.date or datetime.datetime):
        Date-like object providing integer attributes year, month, and day. Both datetime.date and datetime.datetime are valid.
    account_id (str or int):
        AWS account identifier; typically a 12-digit numeric string. Any value accepted by str() will be used in the path.
    region (str):
        AWS region name string (e.g., 'us-east-1', 'eu-west-1').

Interdependencies:
    - None between parameters other than that `date` must expose year/month/day attributes.

## Returns:
    str: The formatted S3 key prefix string ending with a trailing slash. Examples of returned value:
        - 's3://my-bucket/AWSLogs/123456789012/CloudTrail/us-west-2/2023/09/05/'
        - 'AWSLogs/123456789012/CloudTrail/us-east-1/2022/12/31/'

Edge-case return values:
    - If prefix is the empty string, the returned string begins with 'AWSLogs/...'.
    - If prefix does not end with a separator, the returned string will directly concatenate prefix and 'AWSLogs...' (callers should normalize prefix if they require a separator).

## Raises:
    - No exceptions are explicitly raised by the function.
    - Possible runtime exceptions that can surface from misuse:
        * AttributeError: if `date` does not have year/month/day attributes.
        * TypeError or ValueError: highly unlikely from f-string formatting, but may occur if provided objects override attribute access in unusual ways.
    - These are not raised deliberately by the function; callers should validate inputs before calling if they need strict guarantees.

## Constraints:
Preconditions:
    - `date` must be an object with integer year, month, and day attributes.
    - `prefix`, `account_id`, and `region` must be convertible to strings (the function uses f-string formatting which calls str()).

Postconditions:
    - The returned string always ends with a '/' character.
    - The returned string contains the year as a 4-digit integer, and month/day zero-padded to two digits.

## Side Effects:
    - None. The function performs pure string construction and does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    Start --> BuildComponents
    BuildComponents --> FormatString
    FormatString --> ReturnResult
    ReturnResult --> End

Nodes:
    Start: entry
    BuildComponents: validate inputs conceptually (no runtime validation performed)
    FormatString: assemble f-string with year/month/day zero-padded
    ReturnResult: return constructed prefix
    End: exit

## Examples:
- Example 1 (typical):
    Inputs:
        prefix = 's3://my-bucket/'
        date = 2023-09-05 (datetime.date(2023, 9, 5))
        account_id = '123456789012'
        region = 'us-west-2'
    Returned value:
        's3://my-bucket/AWSLogs/123456789012/CloudTrail/us-west-2/2023/09/05/'

- Example 2 (prefix without trailing slash — caller must normalize if needed):
    Inputs:
        prefix = 's3://my-bucket'  (no trailing slash)
        date = 2021-01-01
        account_id = 987654321098
        region = 'eu-central-1'
    Returned value:
        's3://my-bucketAWSLogs/987654321098/CloudTrail/eu-central-1/2021/01/01/'
    Note: Because the function concatenates `prefix` and 'AWSLogs...' directly, callers that expect a separator should provide one in `prefix`.

- Example 3 (using datetime.datetime):
    Inputs:
        prefix = ''
        date = 2020-12-31T23:59:59 (datetime.datetime(2020,12,31,23,59,59))
        account_id = '000111222333'
        region = 'ap-southeast-2'
    Returned value:
        'AWSLogs/000111222333/CloudTrail/ap-southeast-2/2020/12/31/'

## `trailscraper.s3_download._s3_key_prefix_for_org_trails` · *function*

## Summary:
Constructs the S3 key prefix (folder path) for an AWS CloudTrail organization-trail object for a given date, organization, account, and AWS region.

## Description:
This is a small helper that formats the path portion of S3 object keys where CloudTrail organization logs are stored using the common AWSLogs layout. Typical usage is inside an S3-listing or S3-download pipeline that needs to compute the prefix (folder) to list or fetch CloudTrail objects for a specific date and account.

Known callers in the codebase:
    - No direct callers were found in the repository search. The function is intended for internal use by the s3_download module to build S3 prefixes for CloudTrail logs.

Why this is extracted:
    - Keeps string formatting for S3 CloudTrail layout centralized and consistent across the module.
    - Encapsulates the S3 key pattern so callers don't repeat formatting logic and so future pattern changes require a single edit.

## Args:
    prefix (str):
        - The leading S3 prefix or bucket/key base to prepend (for example 's3://my-bucket/' or 'my-bucket/prefix/').
        - Recommended: supply a string that ends with a slash if you want the returned value to be an absolute prefix under a bucket (function does not add a slash between prefix and 'AWSLogs').
    date (datetime.date or datetime.datetime or any object with year, month, day attributes):
        - The date for which to build the key prefix. The attributes year (int), month (int), and day (int) are read.
        - Month and day will be zero-padded to two digits in the output.
    org_id (str):
        - AWS Organization ID (the folder name used by AWS Logs for organization trails).
    account_id (str):
        - AWS account ID (the account owning the trail objects).
    region (str):
        - AWS region code (for example: 'us-east-1').

Interdependencies:
    - date must expose integer year, month, and day attributes that are valid for integer formatting.
    - prefix is concatenated as-is; callers are responsible for ensuring any required separator (slash) is present.

## Returns:
    str: The formatted S3 key prefix string representing the CloudTrail path for the provided values. The returned string always ends with a trailing slash.
    - Example pattern returned:
        prefix + "AWSLogs/{org_id}/{account_id}/CloudTrail/{region}/{YYYY}/{MM}/{DD}/"
    - Edge cases:
        - If prefix is the empty string, the return will start with "AWSLogs/.../".
        - If prefix does not end with '/', the returned string will be a direct concatenation without an extra separator (caller should ensure correct prefix formatting).

## Raises:
    - AttributeError: If the provided date object lacks any of the attributes 'year', 'month', or 'day'.
    - TypeError: If month/day values are not integers and the integer-specific format specifier is applied (e.g., formatting a non-int with :02d).
    - Note: The function performs no explicit validation; these exceptions are the implicit runtime exceptions that can occur during formatting.

## Constraints:
Preconditions:
    - prefix should be a str (or otherwise string-coercible) and formatted as desired (including or excluding trailing slash).
    - date must provide integer-like year, month, day attributes.
    - org_id, account_id, and region should be string-like values appropriate for S3 key path segments (no embedded path traversal concerns are checked).

Postconditions:
    - Returns a string that ends with a slash and follows the AWSLogs CloudTrail directory layout for the given date.
    - No mutation of input arguments or global state is performed.

## Side Effects:
    - None. The function performs no I/O, network operations, logging, or mutation of external state.

## Control Flow:
flowchart TD
    A[Start: receive inputs prefix,date,org_id,account_id,region] --> B{date has year,month,day?}
    B -->|yes| C[Format year as YYYY, month/day as zero-padded MM/DD]
    C --> D[Concatenate prefix + AWSLogs/.../{YYYY}/{MM}/{DD}/]
    D --> E[Return formatted string (ends with '/')]
    B -->|no| F[Accessing missing attribute raises AttributeError at runtime]

## Examples:
Example (described, not code):
    - Given prefix = "s3://my-bucket/", date = 2021-03-05, org_id = "o-abc123", account_id = "123456789012", region = "us-east-1"
      The function will return:
      "s3://my-bucket/AWSLogs/o-abc123/123456789012/CloudTrail/us-east-1/2021/03/05/"

    - Caller responsibility example notes:
      * If you pass prefix="my-bucket/prefix" (no trailing slash), result will be
        "my-bucket/prefixAWSLogs/..." — ensure prefix ends with '/' when composing bucket-level paths.
      * If you pass a date-like object missing .month, an AttributeError will be raised when the function attempts to read date.month.

## `trailscraper.s3_download._s3_key_prefixes` · *function*

## Summary:
Produces a list of S3 key prefix strings (one per account/region/day and optionally organization) covering every day in the inclusive date range [from_date, to_date].

## Description:
- Known callers:
    - No direct callers were found in the repository snapshot. This function is intended for internal use within the s3_download pipeline to enumerate S3 prefixes to list or download AWS CloudTrail objects across multiple accounts, regions, and dates.
- Typical usage context:
    - Called during an S3-listing or download stage that needs to compute all CloudTrail S3 prefix paths to inspect or download CloudTrail objects for a set of accounts/regions across a contiguous date interval.
- Why this logic is extracted:
    - Centralizes and documents the combinatorial logic that expands date ranges and multiplies by accounts/regions (and optionally organization ids). Separating this responsibility keeps higher-level listing/download code focused on I/O and lets callers obtain the exact set of prefixes deterministically from a single function.

## Args:
    prefix (str)
        Base S3 prefix or bucket/key base to prepend to the CloudTrail layout (e.g., 's3://my-bucket/' or 'my-bucket/prefix/').
        The function concatenates this string as-is; callers should include a trailing slash if they need a separator before 'AWSLogs'.
    org_ids (iterable[str] or None or False-y)
        Iterable of AWS Organization IDs (strings). If truthy (non-empty), organization-style prefixes are generated using the org-specific helper.
        If None or an empty iterable (false-y), organization IDs are ignored and account-style prefixes are produced.
    account_ids (iterable[str])
        Iterable of AWS account identifiers (strings or values convertible to str). Must be iterable; if empty, the result is an empty list.
    regions (iterable[str])
        Iterable of AWS region strings (e.g., 'us-east-1'). Must be iterable; if empty, the result is an empty list.
    from_date (datetime.datetime or datetime.date-like)
        Start of the inclusive date range. The function calls from_date.astimezone(pytz.utc) to compute the UTC difference — see Preconditions.
    to_date (datetime.datetime or datetime.date-like)
        End of the inclusive date range. Likewise converted to UTC for the delta calculation.

Notes on interdependencies:
    - The function computes the day-span using UTC-normalized datetimes (to_date.astimezone(pytz.utc) - from_date.astimezone(pytz.utc)) but then generates date entries by subtracting whole days from the original to_date object. For correct and predictable results around timezone/DST boundaries you should pass timezone-aware datetimes and understand that the returned day objects preserve to_date's original tzinfo.

## Returns:
    list[str]
        A (possibly empty) list of formatted S3 key prefix strings.
        - If org_ids is truthy (non-empty), returns entries produced by _s3_key_prefix_for_org_trails(prefix, day, org_id, account_id, region) for every combination of org_id × account_id × day × region.
        - If org_ids is false-y (None or empty), returns entries produced by _s3_key_prefix(prefix, day, account_id, region) for every combination of account_id × day × region.
        - If any of account_ids, regions, or the computed days list are empty, the function returns an empty list.
        - The number of returned prefixes equals:
            len(days) * len(account_ids) * len(regions)  (when org_ids is empty)
            len(days) * len(account_ids) * len(regions) * len(org_ids)  (when org_ids is non-empty)

Edge-case returns:
    - If to_date < from_date (when normalized to UTC), delta.days will be negative and the constructed days list will be empty; the function then returns an empty list.
    - If any iterable argument is empty or non-iterable, behavior is either an empty result (if empty iterable) or a TypeError (if not iterable).

## Raises:
    - ValueError or TypeError from datetime.astimezone:
        * Calling .astimezone(pytz.utc) on inappropriate date objects (for example, certain naive datetimes in some contexts) can raise ValueError. The function does not catch this; callers should provide timezone-aware datetimes to avoid this.
    - AttributeError:
        * If from_date or to_date do not implement astimezone, an AttributeError will surface.
    - TypeError:
        * If account_ids, regions, or org_ids are not iterable, a TypeError will be raised when the function attempts to iterate over them.
    - Other runtime exceptions can propagate from the helper functions (_s3_key_prefix and _s3_key_prefix_for_org_trails) if they encounter invalid inputs (these helpers perform string-formatting and may raise AttributeError/TypeError if date-like objects lack expected attributes).

## Constraints:
Preconditions:
    - from_date and to_date should be datetime-like objects with .astimezone available and ideally timezone-aware (having tzinfo). For predictable inclusive-day semantics across timezones, pass timezone-aware datetimes.
    - account_ids and regions must be iterables of values convertible to strings.
    - If you intend organization-specific prefixes, provide org_ids as a non-empty iterable of strings.

Postconditions:
    - Returns a list of S3 prefix strings (possibly empty) constructed by delegating to the appropriate helper per combination.
    - No mutation of inputs or external/global state.

## Side Effects:
    - None. The function is pure: it does not perform network calls, I/O, logging, or modify global state. It only computes and returns a list of strings.

## Control Flow:
flowchart TD
    Start --> ComputeDelta[Compute delta = to_date.astimezone(pytz.utc) - from_date.astimezone(pytz.utc)]
    ComputeDelta --> BuildDays[Build days list: days = [to_date - timedelta(days=i) for i in 0..delta.days]]
    BuildDays --> CheckOrg{org_ids is truthy?}
    CheckOrg -->|yes| OrgLoop[Comprehend over org_id × account_id × day × region\nCall _s3_key_prefix_for_org_trails(...) per combination]
    OrgLoop --> ReturnOrg[Return list of org-prefixed strings]
    CheckOrg -->|no| NonOrgLoop[Comprehend over account_id × day × region\nCall _s3_key_prefix(...) per combination]
    NonOrgLoop --> ReturnNonOrg[Return list of account-prefixed strings]
    ReturnOrg --> End
    ReturnNonOrg --> End

Notes on flow:
    - If delta.days < 0 then BuildDays produces an empty list and the final returned list is empty.
    - Any TypeError/AttributeError raised while computing delta or while iterating will propagate to the caller.

## Examples:
1) Non-organization case (typical):
    - Inputs:
        prefix = 's3://my-bucket/'
        org_ids = None
        account_ids = ['111111111111', '222222222222']
        regions = ['us-east-1']
        from_date = 2023-09-01T00:00:00+00:00
        to_date   = 2023-09-03T00:00:00+00:00
    - Behavior:
        delta.days == 2 -> days = [2023-09-03, 2023-09-02, 2023-09-01] (each as the same type as to_date minus days)
        Returns one _s3_key_prefix(...) result per account × day × region (2 accounts × 3 days × 1 region = 6 prefixes).
    - Example returned entries (pattern, assuming helper formats as AWSLogs/{account}/CloudTrail/{region}/{YYYY}/{MM}/{DD}/):
        's3://my-bucket/AWSLogs/111111111111/CloudTrail/us-east-1/2023/09/03/'
        's3://my-bucket/AWSLogs/222222222222/CloudTrail/us-east-1/2023/09/03/'
        's3://my-bucket/AWSLogs/111111111111/CloudTrail/us-east-1/2023/09/02/'
        ... and so on for the remaining day/account combinations.

2) Organization case:
    - Inputs:
        prefix = 's3://org-bucket/'
        org_ids = ['o-abc123']
        account_ids = ['123456789012']
        regions = ['us-west-2', 'eu-west-1']
        from_date = to_date = 2022-01-01T00:00:00+00:00
    - Behavior:
        delta.days == 0 -> days = [to_date]
        Returns len(org_ids) × len(account_ids) × len(regions) × len(days) = 1 × 1 × 2 × 1 = 2 prefixes produced by _s3_key_prefix_for_org_trails.
    - Example returned entries:
        's3://org-bucket/AWSLogs/o-abc123/123456789012/CloudTrail/us-west-2/2022/01/01/'
        's3://org-bucket/AWSLogs/o-abc123/123456789012/CloudTrail/eu-west-1/2022/01/01/'

3) Edge cases and error handling:
    - If to_date < from_date (after UTC normalization), the function returns an empty list (no prefixes).
    - If account_ids or regions is an empty iterable, the function returns an empty list (no prefixes).
    - If from_date or to_date are not timezone-aware and astimezone raises ValueError, callers should catch that and convert/attach tzinfo before calling.

## `trailscraper.s3_download._s3_download_recursive` · *function*

## Summary:
Recursively lists S3 objects under the given prefixes and downloads any missing files into the specified local directory using a thread pool.

## Description:
This helper performs two responsibilities: (1) traverse the S3 prefix tree (using the list_objects paginator with Delimiter="/") to collect object keys that match the provided prefixes and do not already exist locally, and (2) download those objects concurrently to the target directory.

Known callers within the provided codebase:
    - No direct callers were present in the provided source snapshot. The function is intended to be invoked by a higher-level orchestration routine that decides which bucket, prefixes, and target directory to sync (for example, a public s3_download wrapper or a pipeline task that syncs specific S3 prefixes to disk).

Why this logic is extracted:
    - Traversing S3 prefixes (including pruning unnecessary branches) and concurrently downloading files are two cohesive behaviors that are reusable and sufficiently complex to justify isolation.
    - Extraction keeps the higher-level orchestration simple (it can provide bucket/prefix parameters and handle errors), and hides threading, boto3 client-per-thread, pagination, directory creation, and file-existence checks inside a single focused function.

## Args:
    bucket (str):
        - Name of the S3 bucket to list from and download objects in.
        - Must be a non-empty bucket name as accepted by boto3.
    prefixes (list[str]):
        - A list of S3 prefix strings that identify which object keys to download.
        - Each prefix should match the format used with S3 ListObjects Prefix/CommonPrefixes (commonly ending with a slash for "directory-like" prefixes, e.g., "path/to/folder/"). The function treats prefixes as exact prefix strings to match against the paginator results.
        - The function will only add objects whose immediate parent prefix equals one of the provided prefixes; nested traversal is gated by checking whether a sub-prefix is a parent of any provided prefix.
        - Must be an iterable of strings; an empty list will result in no files being selected for download.
    target_dir (str):
        - Local filesystem path that will serve as the root directory for downloaded objects.
        - For each object key K, the target file path is computed as target_dir + os.sep + K. The function will create parent directories as needed.
        - The caller need not pre-create target_dir; the function will create missing directories for each file's parent.
    parallelism (int):
        - Maximum number of worker threads to use for concurrent downloads (passed to ThreadPoolExecutor as max_workers).
        - Must be a positive integer (>= 1). Non-positive values will cause ThreadPoolExecutor construction to raise a ValueError.

Notes on interdependencies:
    - prefixes determines which branches are traversed and which object keys are selected; incorrect prefix formatting will cause either no files to be selected or wrong ones.
    - target_dir is used directly to build download paths; it must be writable by the process.

## Returns:
    None

    - The function does not return any value. Its effect is to download missing files from S3 into target_dir.
    - If downloads succeed, the local filesystem will contain files corresponding to the selected keys.
    - If any download task or filesystem operation raises an exception, that exception will propagate out of this function (see Raises).

## Raises:
    - Any exceptions raised by boto3 or botocore during client creation, listing, or download (for example, botocore.exceptions.ClientError) — these propagate directly.
    - OSError (or subclasses) raised during directory creation (os.makedirs) or other local filesystem operations.
    - ValueError or other exceptions coming from ThreadPoolExecutor if parallelism is invalid.
    - Any exception raised while iterating the paginator or while downloading a file will be raised to the caller when the worker results are consumed; exceptions raised inside worker threads are re-raised when consume(results) iterates the executor.map result.

Exact conditions in the implementation:
    - boto3.client('s3') creation errors occur inside get_s3_client() on the first thread that calls it.
    - paginator.paginate errors surface while listing in _list_files_to_download.
    - get_s3_client().download_file(...) may raise network or client errors per boto3 behavior; because executor results are consumed, those exceptions will be raised on the calling thread when consume(...) runs.

## Constraints:
Preconditions:
    - AWS credentials and network access must be configured so boto3.client('s3') can connect and authorize against the specified bucket.
    - The process must have write permission to create files and directories under target_dir.
    - prefixes must be finite and appropriate for S3 listing; passing prefixes that cannot match any CommonPrefixes will produce an empty download set.

Postconditions:
    - On successful return, all selected object keys that did not previously exist under target_dir have been downloaded.
    - If the function returns normally, the local filesystem contains the downloaded files; any pre-existing files with the same key paths are preserved (the code skips downloading existing files).
    - If the function raises, some downloads may have completed while others may have failed; the caller is responsible for handling partial state.

## Side Effects:
    - Network I/O: Creates boto3 S3 clients (one per thread) and performs S3 ListObjects (via paginator.paginate) and DownloadFile calls.
    - Filesystem I/O: Creates directories (os.makedirs) and writes files under target_dir.
    - Logging: Emits INFO-level log entries for listing prefixes and for each attempted download and skip.
    - Thread-local state: Stores a boto3 S3 client object on a thread-local object to provide one client per worker thread.
    - No global variables in the module are modified.

## Control Flow:
flowchart TD
    Start --> InitThreadLocal[Create thread-local storage]
    InitThreadLocal --> ListRoot[Call _list_files_to_download("")]
    ListRoot --> ListLoop[Paginator.paginate over results]
    ListLoop --> HasCommon[Result has CommonPrefixes?]
    HasCommon -->|yes| ForEachPrefix[for each prefix_result in CommonPrefixes]
    ForEachPrefix --> StartsWithCheck{Does any provided prefix\nstart with prefix_result.Prefix?}
    StartsWithCheck -->|yes| Recurse[_list_files_to_download(prefix_result.Prefix)]
    Recurse --> ListLoop
    HasCommon -->|no| CheckContents[Result has Contents?]
    CheckContents -->|yes| ForEachContent[for each content in Contents]
    ForEachContent --> InPrefixes{Is current_prefix in prefixes?}
    InPrefixes -->|yes| PrepareTarget[compute target path; ensure parent exists]
    PrepareTarget --> FileExists{Does target file already exist?}
    FileExists -->|no| AppendList[append key to files_to_download]
    FileExists -->|yes| LogSkip[log skipping existing file]
    ForEachContent --> ListLoop
    ListLoop --> ReturnFiles[return files_to_download list]
    ReturnFiles --> ThreadPool[Create ThreadPoolExecutor(max_workers=parallelism)]
    ThreadPool --> MapDownloads[executor.map(_download_file, files_to_download)]
    MapDownloads --> ConsumeResults[consume(map results) — raises on worker exceptions]
    ConsumeResults --> End[Return None or propagate exception]

## Examples (usage and error handling, described):
    Example: Sync a single S3 prefix tree to a local path
        - Inputs:
            bucket = "my-bucket"
            prefixes = ["datasets/run-2026-04-01/"]
            target_dir = "/var/data/my-bucket"
            parallelism = 8
        - Behavior:
            1. The function will list the bucket starting at the empty prefix and recursively descend only into S3 common prefixes that are parents of "datasets/run-2026-04-01/".
            2. When it reaches the prefix "datasets/run-2026-04-01/", it will collect keys from Contents. For each key K it computes the file path "/var/data/my-bucket/K". It creates missing parent directories and skips any key whose target file already exists.
            3. It will concurrently download all missing keys using up to 8 threads. If any download fails, the exception will be raised back to the caller once results are consumed.

    Error handling guidance:
        - Wrap the call in a try/except that handles boto3/botocore ClientError and OSError to detect authentication, network, or filesystem problems.
        - If partial downloads are undesirable, callers should run the function in a try/except and clean up incomplete files or run a retry strategy on failure.

## `trailscraper.s3_download.download_cloudtrail_logs` · *function*

## Summary:
Compute the set of CloudTrail S3 prefixes for the requested accounts/regions/date-range and download any missing CloudTrail objects under those prefixes into a local directory.

## Description:
- Known callers within the repository:
    - No direct callers were found in the provided code snapshot. This function is a top-level convenience routine intended to be invoked by an orchestration step or a CLI/task that needs to sync CloudTrail logs from S3 into local storage for analysis or archival.
    - Typical trigger/context: run as part of a data collection pipeline or one-off sync job that periodically pulls CloudTrail logs for a set of AWS accounts and regions over a specified date interval.

- Why this logic is extracted:
    - This function composes two distinct responsibilities — expansion of CloudTrail key prefixes for the combinatorial set of org/account/region/dates, and the actual S3 listing + concurrent download of objects under those prefixes. Extracting this composition keeps callers succinct (they request "download CloudTrail logs for X") and centralizes error handling, precondition documentation, and orchestration of the two helper steps (_s3_key_prefixes and _s3_download_recursive).

## Args:
    target_dir (str)
        Local filesystem directory where S3 object keys will be downloaded.
        - Must be writable by the process.
        - The function will create parent directories for each file as needed.
    bucket (str)
        Name of the S3 bucket that stores CloudTrail logs.
        - Must be a valid, non-empty S3 bucket name accessible by the configured AWS credentials.
    cloudtrail_prefix (str)
        Base S3 prefix under which CloudTrail logs live (the value passed into _s3_key_prefixes).
        - This string is concatenated as-is. If you require a separator before AWSLogs, include a trailing slash in this value.
    org_ids (iterable[str] or None or false-y)
        If truthy (non-empty iterable), organization-style S3 prefixes will be generated for each org_id × account_id × region × day.
        If None or empty, account-style prefixes will be generated.
    account_ids (iterable[str])
        Iterable of AWS account identifiers (strings or values convertible to str). If empty, no prefixes will be produced and nothing will be downloaded.
    regions (iterable[str])
        Iterable of AWS region strings (e.g., 'us-east-1'). If empty, no prefixes will be produced and nothing will be downloaded.
    from_date (datetime.datetime or date-like)
        Inclusive start of date range. The helper normalizes to UTC for computing the span; prefer timezone-aware datetimes.
    to_date (datetime.datetime or date-like)
        Inclusive end of date range. See from_date notes about timezone-awareness.
    parallelism (int)
        Maximum number of concurrent download worker threads.
        - Must be a positive integer (>= 1). Invalid values will cause ThreadPoolExecutor to raise.

Notes on interdependencies:
    - The number of prefixes (and therefore candidate downloads) depends on account_ids × regions × number_of_days_in_range (and multiplied by len(org_ids) if org_ids is provided).
    - If the computed prefixes list is empty (for example, because to_date < from_date, or account_ids/regions are empty), the function will not attempt any downloads.

## Returns:
    None

    - The function does not return a value. Its observable effect is that any missing S3 objects under the computed prefixes are downloaded into target_dir.
    - Possible post-call states:
        - Normal return: all selected missing objects were downloaded successfully (pre-existing files were skipped).
        - Exception raised: some or all downloads may have failed; partial files or a partially-populated target_dir are possible.

## Raises:
    - Any exceptions propagated from _s3_key_prefixes:
        * AttributeError, TypeError, ValueError (for example, when from_date/to_date lack astimezone, or non-iterable collections are passed).
    - Any exceptions propagated from _s3_download_recursive:
        * botocore.exceptions.ClientError (or other boto3/botocore runtime/client errors) raised during listing or download.
        * OSError (or subclass) raised during filesystem operations (os.makedirs, file writes).
        * ValueError raised by ThreadPoolExecutor if parallelism is invalid.
        * Any other runtime exceptions raised while listing/downloading; exceptions raised inside worker threads are re-raised when results are consumed.
    - No exceptions are caught or wrapped by download_cloudtrail_logs itself; callers should catch the above as needed.

## Constraints:
Preconditions:
    - AWS credentials and network access must be configured so that boto3.client('s3') can authenticate and access the specified bucket.
    - target_dir must be a path writable by the calling process.
    - from_date and to_date should preferably be timezone-aware datetimes (objects supporting astimezone) to avoid ValueError and to obtain predictable inclusive-day semantics across timezones.
    - account_ids and regions must be iterable; empty iterables will result in no prefixes/downloads.
    - parallelism must be a positive integer.

Postconditions:
    - On successful return, every S3 object under the computed prefixes that did not previously exist under target_dir has been downloaded and saved using the object key's path relative to target_dir.
    - No return value is provided; the file system reflects the downloaded files and pre-existing files are preserved.

## Side Effects:
    - Network I/O: creates boto3 S3 clients (one per worker thread) and performs S3 ListObjects and DownloadFile requests.
    - Filesystem I/O: creates directories and writes files under target_dir.
    - Logging: _s3_download_recursive logs listing and download/skipping events to the module logger at INFO level.
    - Thread-local state: boto3 clients are cached per-thread inside the helper.
    - No global in-process state is mutated by this function directly.

## Control Flow:
flowchart TD
    Start --> ComputePrefixes[Call _s3_key_prefixes(cloudtrail_prefix, org_ids, account_ids, regions, from_date, to_date)]
    ComputePrefixes --> CheckEmpty{prefixes list empty?}
    CheckEmpty -->|yes| EndNoWork[Return (no downloads)]
    CheckEmpty -->|no| CallDownload[Call _s3_download_recursive(bucket, prefixes, target_dir, parallelism)]
    CallDownload -->|succeeds| EndSuccess[Return None (all selected files downloaded or skipped)]
    CallDownload -->|exception| EndError[Propagate exception to caller]
    EndNoWork --> EndSuccess

Notes:
    - Exceptions raised while computing prefixes or during downloads propagate to the caller.
    - If an exception occurs during downloads, some files may have been downloaded before the failure.

## Examples:
1) Periodic pipeline sync (recommended pattern with error handling):
    - Intent: download CloudTrail logs for two accounts in us-east-1 across a three-day window.
    - Parameters:
        target_dir = /data/cloudtrail
        bucket = my-cloudtrail-bucket
        cloudtrail_prefix = 's3://my-cloudtrail-bucket/'  (or '' depending on how your helpers format keys)
        org_ids = None
        account_ids = ['111111111111','222222222222']
        regions = ['us-east-1']
        from_date = 2023-10-01T00:00:00+00:00
        to_date =   2023-10-03T00:00:00+00:00
        parallelism = 8
    - Behavior:
        - Expands to the prefixes for each account × each of the three days × the region and invokes the recursive downloader to fetch any missing objects under those prefixes.
    - Error handling guidance:
        - Wrap the call in try/except to handle botocore.exceptions.ClientError and OSError; on failure, you may re-run the same call (it is idempotent for existing files because the downloader skips files whose target already exists).

2) No-op case:
    - If account_ids or regions is an empty list, or if to_date < from_date (after UTC normalization), the function computes zero prefixes and returns without attempting any network activity.

3) Partial-failure awareness:
    - Because downloads are done concurrently and worker exceptions are re-raised when results are consumed, callers who need transactional behavior should run this in a guarded environment and clean up partial files upon exception before retrying.

