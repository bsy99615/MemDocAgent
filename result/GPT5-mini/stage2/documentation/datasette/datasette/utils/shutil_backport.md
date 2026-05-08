# `shutil_backport.py`

## `datasette.utils.shutil_backport._copytree` · *function*

## Summary:
Recursively copies a directory tree represented by an iterable of directory entries into a destination path, preserving file data and metadata and optionally replicating symlinks; returns the destination path on success.

## Description:
This internal helper performs the core traversal and copy work for a higher-level copytree wrapper. It is responsible for iterating the provided directory entries from a source directory, applying ignore rules, creating the destination directory, and copying each entry (files, directories, and symlinks) to the destination. Errors encountered while copying individual entries are collected and raised as a single aggregated shutil.Error at the end.

Known callers within the codebase:
- The module's public wrapper function copytree (datasette.utils.shutil_backport.copytree) — _copytree is intended to be invoked by that wrapper and is also invoked indirectly via recursive calls to copytree inside this helper. The wrapper typically prepares the entries (for example by calling os.scandir(src)) and forwards them to this helper.
- Recursive control flow in this helper calls the public copytree (not the underscore helper) to descend into directories and to handle symlinked directories when following symlinks is requested.

Why this logic is extracted:
- Enforces a clear responsibility boundary: this function focuses on the iteration over a directory's entries and how individual entries are processed (symlink handling, recursion, copying), while the surrounding wrapper is expected to handle preparing the entries (scanning directory) and the initial public API. Extracting this logic avoids duplicating traversal and error-aggregation code and centralizes behavior (ignore handling, copystat decisions, aggregated error reporting).

## Args:
    entries (iterable): Iterable of directory-entry objects (os.DirEntry-like) representing the contents of the source directory. Each entry must provide at least:
        - name (str)
        - is_dir() -> bool
        - is_symlink() -> bool
       Typical source: the iterator returned by os.scandir(src).
    src (str): Path to the source directory whose entries are represented by `entries`. Used to construct absolute entry paths and for copying metadata from the source directory to the destination.
    dst (str): Path to the destination directory where entries will be copied. The function will attempt to create this directory (see dirs_exist_ok).
    symlinks (bool): If True, symbolic links in the source are reproduced as symbolic links at the destination. If False, symbolic links are dereferenced (copied or recursed into depending on their targets).
    ignore (callable or None): Optional callable with signature ignore(src_path: str, names: set[str]) -> set[str]. Called once for the src directory to obtain a set of entry names to skip. If None, no names are ignored.
    copy_function (callable): Callable used to copy non-directory file entries (e.g., shutil.copy or shutil.copy2). It must accept (src, dst) arguments. When this is exactly shutil.copy or shutil.copy2 the function prefers passing DirEntry objects to downstream file operations where supported.
    ignore_dangling_symlinks (bool): When symlinks is False and a symlink's target does not exist, if this flag is True the dangling symlink will be skipped instead of raising or attempting to copy.
    dirs_exist_ok (bool, optional): Passed to os.makedirs as its exist_ok parameter. If False (default), os.makedirs(dst, exist_ok=False) will raise if dst already exists; if True, existing destination directories are allowed and creation is a no-op.

Interdependencies and notes:
- entries and src must correspond (i.e., entries should enumerate the contents of src). The function constructs entry paths with os.path.join(src, srcentry.name).
- Behavior for file copying differs slightly depending on whether copy_function is the imported copy or copy2: in those cases the function passes the DirEntry object to copy operations (via srcobj), otherwise it passes the path string.

## Returns:
    str: The `dst` path passed in. The function returns the destination path when copying completes successfully (no aggregated errors).

Edge / special return behavior:
- The function always returns dst on success; it never returns partial results. If any per-entry errors were recorded, it raises an aggregated Error instead of returning.

## Raises:
    shutil.Error: Raised when one or more file/directory copy operations failed. The raised Error groups individual error items; the code aggregates errors in a list and at the end raises Error(errors). Each element in the aggregated errors is typically a tuple of (src_path, dst_path, error_message) or other error entries propagated from nested shutil.Error exceptions.
    OSError (possible): Precondition/early errors from operations executed before per-entry exception handling (for example, os.makedirs when dirs_exist_ok is False and the destination already exists, or permission errors on initial directory creation) are not caught by the function and will propagate as OSError.

Exact triggering conditions observed in code:
- Errors encountered while copying individual entries (caught as shutil.Error or OSError) are recorded and cause a final shutil.Error to be raised.
- copystat(src, dst) at the end is attempted; if it raises OSError and the exception has no winerror attribute (or winerror is None), the error is recorded and will cause a final shutil.Error. On Windows, OSError exceptions that expose a non-None winerror attribute are ignored for copystat.

## Constraints:
Preconditions:
- `entries` must be an iterable of DirEntry-like objects that correspond to the contents of `src`. If they are not aligned with `src`, constructed paths will be incorrect and behavior is undefined.
- The caller must ensure that `src` exists and is readable; otherwise os.listdir/os.scandir or other upstream code will fail before or while gathering `entries`.
- If dirs_exist_ok is False, dst must not already exist (or os.makedirs will raise OSError).

Postconditions:
- On successful return (no exception), the directory tree represented by `entries` has been copied into `dst`. File metadata copying via copystat is attempted for each created item and for the directory itself; however, platform-specific limitations may cause some metadata operations to be skipped (e.g., certain Windows errors).
- If the function raises shutil.Error, some files/directories may have been copied before failure; the error contains the list of individual failures so the caller can decide on cleanup or retry semantics.

## Side Effects:
- Filesystem I/O:
    - Creates the destination directory `dst` (via os.makedirs).
    - Writes files and directories, creates symlinks (os.symlink) when symlinks=True, or dereferences symlinks and copies their targets when symlinks=False.
    - Calls copy_function for file copies which performs the actual file data copying.
    - Calls shutil.copystat to attempt to replicate file/directory metadata (timestamps, permission bits) from source to destination. For symlinks, copystat is invoked with follow_symlinks=False to copy link metadata when symlinks=True.
- No network I/O or global state mutation outside the filesystem is performed by this function.
- Error aggregation: collects errors rather than aborting on first failure, and only raises aggregated errors at the end (unless an OSError escapes early).

## Control Flow:
flowchart TD
    Start --> ComputeIgnoredNames
    ComputeIgnoredNames --> MakeDstDir
    MakeDstDir --> InitErrors
    InitErrors --> ForEachEntry
    ForEachEntry --> IsIgnored{srcentry.name in ignored_names?}
    IsIgnored -- Yes --> NextEntry
    IsIgnored -- No --> BuildPaths
    BuildPaths --> IsSymlink{srcentry.is_symlink()?}
    IsSymlink -- Yes --> ReadLink
    ReadLink --> SymlinksFlag{symlinks?}
    SymlinksFlag -- Yes --> CreateSymlink --> CopyStatSymlink --> NextEntry
    SymlinksFlag -- No --> DanglingCheck{link target exists?}
    DanglingCheck -- No & ignore_dangling_symlinks True --> NextEntry
    DanglingCheck -- Yes or ignore_dangling_symlinks False --> SymlinkIsDir{srcentry.is_dir()?}
    SymlinkIsDir -- Yes --> RecursiveCopyDir --> NextEntry
    SymlinkIsDir -- No --> CopyFileFromSrcobj --> NextEntry
    IsSymlink -- No --> IsDir{srcentry.is_dir()?}
    IsDir -- Yes --> RecursiveCopyDir --> NextEntry
    IsDir -- No --> CopyFileFromSrcentry --> NextEntry
    NextEntry --> ForEachEntry
    ForEachEntry --> AfterLoop
    AfterLoop --> CopyStatSrcToDst
    CopyStatSrcToDst --> CheckErrors{errors non-empty?}
    CheckErrors -- Yes --> RaiseAggregatedError
    CheckErrors -- No --> ReturnDst
    ReturnDst --> End

## Examples:
Typical usage pattern (conceptual, not an API definition):
- The public copytree wrapper calls os.scandir(src) and passes the resulting iterator (entries) along with src, dst, and flags to _copytree. Example call sequence the wrapper would perform:
    - entries = os.scandir(src)
    - _copytree(entries, src, dst, symlinks, ignore, copy_function, ignore_dangling_symlinks, dirs_exist_ok)
- Error handling:
    - The wrapper should either catch shutil.Error to inspect the aggregated list of failures (for logging, cleanup, or retry) or allow it to propagate to signal that the copy did not fully succeed.
- When preserving symlinks exactly: pass symlinks=True; when wanting to copy link targets instead, pass symlinks=False and set ignore_dangling_symlinks according to whether dangling symlinks should be skipped.

Notes for implementers/readers:
- This helper assumes a cooperative wrapper that provides a correct entries iterable for the provided src. If integrating into a different environment, ensure you supply os.DirEntry-compatible objects and appropriate copy_function semantics.
- Because errors are aggregated, callers that need atomic behavior (either full success or no changes) must implement their own staging or cleanup logic when an aggregated error is raised.

## `datasette.utils.shutil_backport.copytree` · *function*

*No documentation generated.*

