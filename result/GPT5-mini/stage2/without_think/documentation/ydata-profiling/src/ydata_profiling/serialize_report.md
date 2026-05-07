# `serialize_report.py`

## `src.ydata_profiling.serialize_report.SerializeReport` · *class*

*No documentation generated.*

### `src.ydata_profiling.serialize_report.SerializeReport.df_hash` · *method*

## Summary:
Returns the stored DataFrame hash placeholder used during serialize/deserialize operations; in the current implementation it always returns None and does not modify object state.

## Description:
Known callers and contexts:
- SerializeReport.dumps — reads this property when serializing the object into bytes to include the DataFrame identifier alongside the report, configuration and description set.
- SerializeReport.loads — compares the loaded df_hash with this property's value to decide whether the loaded data matches the current ProfileReport; used during deserialization to validate compatibility.
- SerializeReport.load — calls loads and therefore is part of the same deserialization pipeline.

Why this is a separate property:
- It is an explicit abstraction representing the DataFrame identity used for serialization integrity checks. Keeping it as a dedicated property allows subclasses or future implementations to compute or store a deterministic hash (for example, based on the DataFrame contents or metadata) without changing serialization logic scattered elsewhere. In the present codebase the property acts as a stable extension point and placeholder value.

## Args:
None. This is a read-only property with no parameters.

## Returns:
Optional[str]
- Current implementation: always returns None.
- Intended/possible values (for implementers): a deterministic string identifier (hash) for the associated DataFrame, or None if no identifier is available.
- Edge cases: callers should expect None and handle it (the current loads implementation accepts df_hash == None as valid).

## Raises:
None. The property accessor does not raise exceptions.

## State Changes:
Attributes READ:
- None. The current property implementation does not access any self.<attr> fields.

Attributes WRITTEN:
- None. The property does not modify any attributes.

Note: The class declares an attribute _df_hash which is set by SerializeReport.loads when loading serialized data, but this property does not currently read or return that attribute.

## Constraints:
Preconditions:
- None required to call this property. The object may be in any state.

Postconditions:
- The property returns None (current implementation).
- Calling this property does not change the object's state.

## Side Effects:
- None. There is no I/O, no external service calls, and no mutation of objects outside self.

## Implementation guidance (for reimplementers):
- To convert this placeholder into a functional data-frame hash:
  - Ensure determinism: produce the same string for semantically identical DataFrames across runs (consider using stable serialization of content and metadata).
  - Keep it cheap enough for typical usage patterns, or cache the computed value on self (for example, assign into self._df_hash) and have this property return that cached value.
  - Maintain the current contract: property must return Optional[str], and loads/dumps expect None to be an acceptable value.
  - If you choose to read or write self._df_hash inside the property, document that change and ensure loads' compatibility checks remain correct.

### `src.ydata_profiling.serialize_report.SerializeReport.dumps` · *method*

## Summary:
Serialize the serializer's core state into a pickle-encoded bytes object — producing a stable binary snapshot of the profile configuration, description set, report tree, and DataFrame fingerprint for persistence or transmission.

## Description:
This method gathers four internally-held values (the DataFrame fingerprint, the profiling Settings, the computed description set, and the presentation report root) and returns their pickle serialization as bytes. It performs a local import of the Python pickle module and uses pickle.dumps on a Python list containing these four values in a fixed order.

Known callers and lifecycle:
- SerializeReport.dump: writes the returned bytes to disk as a .pp file.
- External callers that need an in-memory binary snapshot of a ProfileReport or SerializeReport for caching, remote transfer, or embedding.
- The corresponding loads method expects the exact serialization shape produced here; dumps and loads form the canonical (de)serialization pair for saved ProfileReport state.

Why this is a separate method:
- Centralizes the binary wire-format (a list of four elements pickled) so format changes are localized.
- Allows independent testing of serialization behavior and clearer error handling by callers.
- Keeps I/O concerns separate (dumps returns bytes; dump writes them to disk).

## Args:
This method takes no arguments.

## Returns:
bytes: A bytes object produced by pickle.dumps called on a Python list of exactly four elements in this order:
    1. df_hash (Optional[str]): the DataFrame fingerprint (may be None).
    2. config (Settings): the profiling configuration object.
    3. _description_set (Optional[BaseDescription]): the description set (may be None).
    4. _report (Optional[Root]): the presentation report root (may be None).

Edge-case return values:
- The method always returns a bytes instance on successful pickling. If any element is not picklable, no bytes are returned and an exception is raised instead.

## Raises:
This method does not catch exceptions from pickle.dumps; any exception raised by pickle.dumps is propagated to the caller. Examples include (but are not limited to):
    - pickle.PicklingError or pickle.PickleError: if pickle cannot serialize an object.
    - TypeError or AttributeError: commonly raised when an object contains unpicklable components.
    - Other exceptions raised by the pickle implementation for unusual object graphs.

Callers should handle or translate these exceptions if they require custom error messages or fallback behavior.

## State Changes:
Attributes READ:
    - self.df_hash (property; Optional[str])
    - self.config (Settings)
    - self._description_set (Optional[BaseDescription])
    - self._report (Optional[Root])

Attributes WRITTEN:
    - None. The method does not mutate the instance.

## Constraints:
Preconditions:
    - No runtime preconditions enforced by this method; attributes may be None.
    - For successful serialization, the values referenced above must be picklable by the running Python pickle implementation.

Postconditions:
    - On success, returns a bytes object containing pickle.dumps([...]) where the list elements are as described in Returns.
    - The instance's attributes remain unchanged.

## Side Effects:
    - No file or network I/O is performed by this method.
    - Performs a local import of the pickle module and uses CPU/memory proportional to the size of objects being pickled.
    - Security note: the bytes produced by this method must not be unpickled in an untrusted context. The corresponding loads method will accept and restore these bytes, but unpickling arbitrary external data is unsafe.
    - The method relies on the pickle format/version chosen by the running Python interpreter (pickle.dumps is called without an explicit protocol argument), so compatibility across different Python/pickle versions is governed by the pickle defaults on the two environments.

### `src.ydata_profiling.serialize_report.SerializeReport.loads` · *method*

## Summary:
Deserialize a previously serialized report (bytes) into this instance, validating types and updating the instance's internal config, description set, report and dataframe-hash if compatible.

## Description:
This method is the inverse of dumps(); it expects bytes produced by dumps() (pickle-serialized 4-tuple) and restores the saved state into the current object when compatible. Known callers:
- SerializeReport.load (calls loads with bytes read from a .pp file)
- Any user or utility that has byte content produced by SerializeReport.dumps and wants to restore it into an existing instance

Typical lifecycle: called during the "restore" stage of a saved/profile-report lifecycle — i.e., when loading a persisted ProfileReport/SerializeReport from disk or a byte stream. It is separated into its own method to centralize deserialization, validation, and state-updating logic so that both file-based loading (load) and other byte-based loading callers can reuse the same behavior and validation steps.

## Args:
    data (bytes): A bytes object produced by SerializeReport.dumps (pickle of a 4-element list: [df_hash, config, description_set, report]). The expected contents are:
        - df_hash: str | None
        - config: ydata_profiling.config.Settings
        - description_set: ydata_profiling.model.BaseDescription | None
        - report: ydata_profiling.report.presentation.core.Root | None

## Returns:
    Union[ProfileReport, SerializeReport]:
        Returns self (the instance on which the method was called). If this method is invoked on a ProfileReport subclass instance, the returned object will be that ProfileReport instance.

## Raises:
    ValueError("Failed to load data") from Exception:
        Raised when pickle.loads(data) raises any exception (for example, if `data` is not a valid pickle). The original exception is chained.

    ValueError("Failed to load data: file may be damaged or from an incompatible version"):
        Raised when the unpickled tuple does not match the expected types:
            - df_hash is not None and not a str
            - loaded_config is not an instance of Settings
            - loaded_description_set is not None and not an instance of BaseDescription
            - loaded_report is not None and not an instance of Root

    ValueError("DataFrame does not match with the current ProfileReport."):
        Raised when the loaded df_hash does not equal self.df_hash and self.df is not None (i.e., the current instance already has a DataFrame that differs from the saved one).

    (Implicit) KeyError / TypeError / AttributeError:
        The method accesses loaded_description_set.package["ydata_profiling_version"] when loaded_description_set is not None; if the structure differs from expectations this access may raise KeyError/TypeError/AttributeError. Such exceptions are not caught by the method.

## State Changes:
Attributes READ:
    - self.df_hash (property) — used to compare with loaded df_hash
    - self.df — checked to decide whether a mismatch should raise
    - self._description_set — checked to decide whether to overwrite
    - self._report — checked to decide whether to overwrite

Attributes WRITTEN:
    - self._description_set: set to loaded_description_set if and only if self._description_set is currently None
    - self._report: set to loaded_report if and only if self._report is currently None
    - self.config: always overwritten with loaded_config on successful load
    - self._df_hash: set to the loaded df_hash on successful load

## Constraints:
Preconditions:
    - data must be bytes produced by SerializeReport.dumps or otherwise a pickle of a 4-tuple/list matching the expected types (df_hash, Settings, BaseDescription|None, Root|None).
    - If the current instance has self.df not None, then the loaded df_hash must equal self.df_hash; otherwise a ValueError is raised.
    - Callers should NOT pass untrusted data (pickle deserialization executes arbitrary code).

Postconditions (if no exception raised):
    - self.config == loaded_config
    - self._df_hash == df_hash (the loaded df_hash)
    - If self._description_set was None prior to calling, it is now set to loaded_description_set; otherwise it is unchanged and a warning is emitted.
    - If self._report was None prior to calling, it is now set to loaded_report; otherwise it is unchanged and a warning is emitted.

## Side Effects:
    - Emits warnings.warn when attempting to overwrite an existing _description_set or _report (it does not overwrite in those cases).
    - Emits a warnings.warn if the loaded description set indicates a different ydata_profiling package version than the currently installed __version__.
    - No file I/O is performed directly by this method (file I/O occurs in SerializeReport.load which reads bytes and then calls loads).
    - Security: uses pickle.loads which can execute arbitrary code during deserialization. Do not call loads on untrusted or unauthenticated byte streams.

### `src.ydata_profiling.serialize_report.SerializeReport.dump` · *method*

## Summary:
Writes the serialized binary representation of this SerializeReport instance to disk at the given path, ensuring the file has a ".pp" suffix. Does not modify the object's in-memory state.

## Description:
This method is the file-IO wrapper around the in-memory serialization performed by self.dumps(). It is typically invoked when a user or a persistence/serialization step needs to persist a ProfileReport/SerializeReport snapshot to disk for later re-loading. No callers are enumerated in the local memory snapshot; in practice it is called from code that needs to save a generated profile report or by higher-level save utility functions.

Keeping the write logic in a separate method:
- isolates disk I/O from the serialization logic contained in dumps(), enabling easier testing (serialize in-memory vs write to disk),
- centralizes the rule that persisted files use the ".pp" suffix,
- keeps error propagation from pickle and file I/O explicit to the caller.

## Args:
    output_file (Union[pathlib.Path, str]):
        - Path-like target where the serialized bytes will be written.
        - The argument may be either a pathlib.Path or a string accepted by Path(...).
        - The final filename will always be adjusted to have the ".pp" suffix: e.g., "/tmp/report" -> "/tmp/report.pp", "/tmp/report.json" -> "/tmp/report.pp".
        - There is no default; this parameter is required.

## Returns:
    None
    - On success the method returns None.
    - The primary observable effect is the creation or overwriting of a file at the resolved path containing the bytes returned by self.dumps().

## Raises:
    - pickle.PicklingError, TypeError:
        - Propagated from self.dumps() if the in-memory objects (config, description set, report, etc.) cannot be pickled.
    - FileNotFoundError:
        - If the parent directory of the resolved path does not exist, write_bytes(...) will raise this error.
    - PermissionError:
        - If the process lacks permission to write to the target location.
    - IsADirectoryError:
        - If the resolved path points to an existing directory rather than a file.
    - OSError (other subclasses):
        - Any other low-level I/O error from Path.write_bytes(...) may be propagated.
    - TypeError:
        - If output_file is not convertible to a Path (e.g., a value of an unsupported type), constructing Path(str(output_file)) or later file operations may raise TypeError.

## State Changes:
    Attributes READ:
        - self.dumps() is invoked; therefore the following attributes are read by this operation (as used by dumps()):
            - self.df_hash
            - self.config
            - self._description_set
            - self._report
    Attributes WRITTEN:
        - None. The method does not mutate any self.<attr> on the object.

## Constraints:
    Preconditions:
        - self.dumps() must return bytes (the current dumps implementation returns pickle.dumps([...]) and thus returns bytes).
        - The caller must provide a writable path or a path whose parent directory already exists.
        - The object state (config, report, description set) should be in a form that is picklable if persistence is desired.

    Postconditions:
        - A file exists at the resolved path with the ".pp" suffix and contains exactly the bytes produced by self.dumps().
        - self remains unchanged (no in-memory attributes are modified by this method).
        - If an error occurs (pickle or I/O), the method raises an exception and no silent partial state change on self occurs.

## Side Effects:
    - Performs disk I/O: creates or overwrites a file at the resolved path.
    - Does not call external network services.
    - May cause warnings or exceptions to propagate from self.dumps() (pickle) or from the filesystem.
    - No other global state or external object is mutated by this method.

### `src.ydata_profiling.serialize_report.SerializeReport.load` · *method*

## Summary:
Read a serialized report file from disk, deserialize its contents into this object, and return the same object (self) after applying any compatible loaded state.

## Description:
This method is a thin I/O wrapper that accepts a filesystem path (Path or str), reads the raw bytes from that file, and delegates the actual deserialization and validation to the loads(...) method. It is typically called when restoring a previously saved ProfileReport/SerializeReport from a ".pp" file during a report-loading or application startup step. The separation keeps file I/O (reading bytes from disk) isolated from parsing/validation logic (handled by loads), enabling unit testing of deserialization without disk access and reusing loads for other byte-oriented input sources.

Known callers / lifecycle stage:
- Code paths that restore a saved report from disk (for example, code that previously called dump(output_file) to save a report).
- Any consumer reconstructing a ProfileReport from a file as part of persistence/restore workflows.

Why this is a separate method:
- Encapsulates file-system access and path normalization.
- Delegates all parsing, validation, and assignment logic to loads to avoid duplicating deserialization code and to support non-file byte sources.

## Args:
    load_file (Union[pathlib.Path, str]):
        Path-like target pointing to a file containing the pickled report bytes.
        - Allowed forms: pathlib.Path or any object convertible to a string path (str).
        - The path is passed to Path(...).read_bytes(), so it must exist and be readable by the process.
        - There is no automatic suffix enforcement here; callers typically use the same path used when the file was created (commonly with ".pp" suffix from dump).

## Returns:
    Union[ProfileReport, SerializeReport]:
        Returns the same object (self) after attempting to deserialize and apply the loaded state.
        - On success, self is returned.
        - The return type is the concrete instance type (SerializeReport or a subclass such as ProfileReport).
        - No new object is created by this method; all modifications are applied in-place.

## Raises:
    FileNotFoundError:
        If the provided path does not exist or is not readable, Path(...).read_bytes() will raise this (or a related OSError).
    ValueError("Failed to load data"):
        If unpickling the file bytes fails (pickle.loads raises any exception). The original exception is chained.
    ValueError("Failed to load data: file may be damaged or from an incompatible version"):
        If the unpickled tuple does not conform to the expected types/shape (type checks performed in loads).
    ValueError("DataFrame does not match with the current ProfileReport."):
        If the stored dataframe hash does not match the instance's current df_hash and the instance already has an associated DataFrame (self.df is not None). In this case, nothing is modified and this error is raised.
    Any other exceptions raised by loads(...) are propagated unchanged.

## State Changes:
Attributes READ:
    - self.df_hash: compared to the deserialized df_hash to ensure the loaded data matches the current DataFrame.
    - self.df: tested to determine whether a hash mismatch should block loading.
    - self._description_set: inspected to decide whether the loaded description_set can be applied.
    - self._report: inspected to decide whether the loaded presentation report can be applied.

Attributes WRITTEN (may be modified by loads):
    - self._description_set: set to the loaded description set when the current value is None; otherwise left unchanged.
    - self._report: set to the loaded presentation-root when the current value is None; otherwise left unchanged.
    - self.config: replaced by the loaded Settings object from the file.
    - self._df_hash: set to the loaded df_hash when loading succeeds.

## Constraints:
Preconditions:
    - load_file must be a valid path (Path or convertible to str) pointing to a readable file.
    - The file contents must be pickled bytes produced by the corresponding dumps(...) implementation that produces a tuple in the expected order: (df_hash, config, description_set, report).
    - If this instance already has a DataFrame (self.df is not None), the stored df_hash in the file must equal self.df_hash; otherwise loading will be rejected to avoid applying a report describing a different DataFrame.

Postconditions:
    - On successful return, self.config will equal the Settings object loaded from the file.
    - If self._description_set was None before the call and the file contained a description set, self._description_set will be set to the loaded one.
    - If self._report was None before the call and the file contained a report, self._report will be set to the loaded one.
    - self._df_hash will be set to the df_hash value contained in the file (which may be None).
    - If version metadata exists in the loaded description set and differs from the running package version, a warning will be emitted but loading still proceeds.

## Side Effects:
    - Performs file I/O: reads the entire file content into memory (Path.read_bytes()).
    - Calls loads(...), which performs unpickling (pickle.loads) — this executes code during unpickling and can be unsafe for untrusted inputs.
    - Emits warnings via warnings.warn in cases where parts of the current object are preserved (not overwritten) or when the saved package version differs from the running version.
    - No network or external service calls are performed.
    - Mutates the calling object (self) in-place as described in State Changes.

