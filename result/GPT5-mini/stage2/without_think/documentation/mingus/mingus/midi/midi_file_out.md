# `midi_file_out.py`

## `mingus.midi.midi_file_out.MidiFile` · *class*

## Summary:
Represents a MIDI file container that aggregates one or more track objects, builds the standard MIDI file header, concatenates per-track MIDI data, and writes the resulting bytes to disk.

## Description:
The MidiFile class encapsulates the construction and serialization of a format-1 MIDI file (multi-track). Each instance holds an ordered collection of track-like objects (typically instances of mingus.midi.midi_track.MidiTrack or other objects that implement the same minimal interface). MidiFile is responsible for:
- Producing the MThd header for a multi-track MIDI file with the configured time division.
- Concatenating valid track chunks (header + track data + end-of-track) to produce the final MIDI byte stream.
- Resetting contained tracks and writing the full MIDI byte stream to a file.

Typical usage scenarios:
- Assemble multiple MidiTrack objects (one per MIDI channel/part), add them to a MidiFile, and write the combined file to disk.
- Use when exporting generated music (Tracks/Bars/Notes) from memory to a .mid file.

Known callers / factories:
- Callers construct MidiTrack (or compatible) objects and pass a list to MidiFile(tracks=...).
- The rest of the mingus library produces MidiTrack instances; those are the intended compatible objects.

Motivation / responsibility boundary:
This class isolates file-level formatting (MTHD chunk + concatenation of track chunks) and I/O. It does not process musical content (note generation, tempo changes, etc.) — that is the responsibility of Track/MidiTrack. MidiFile expects tracks to already contain correctly formatted track_data and to implement get_midi_data() and reset().

## State:
Public attributes (state kept on the instance):
- tracks: list
  - Type: list of track-like objects (expected types: mingus.midi.midi_track.MidiTrack or any object implementing the required interface).
  - Valid values: any list; elements must expose:
    - attribute track_data (bytes) containing the track's raw data (may be empty b"").
    - method get_midi_data() -> bytes: returns track chunk bytes (header + track_data + end_of_track).
    - method reset(): resets the track to empty state.
  - Notes: A class-level default tracks = [] exists in the source; this is a mutable class attribute. Implementations should avoid sharing this list across instances. When constructing users should pass a new list (defaulting to None in __init__ produces a fresh list). The instance attribute self.tracks overrides the class attribute after __init__.

- time_division: bytes
  - Type: 2-byte big-endian bytes representing MIDI time division (ticks per quarter).
  - Default value (class-level): b"\x00\x48" (0x0048 == 72 ticks per quarter-note).
  - Valid range/values: exactly 2 bytes. The bytes are appended verbatim to the header; the value must comply with MIDI file format expectations.

Class invariants:
- After initialization, self.tracks is a list object (possibly empty).
- Each element in self.tracks is expected to have the minimal track interface described above (track_data bytes, get_midi_data(), reset()).
- time_division must be exactly two bytes when building the header.

Important implementation/behavioral notes (observed in source):
- get_midi_data() filters tracks for inclusion using t.track_data != b"" (only tracks with non-empty bytes are included in the concatenation).
- header() counts tracks using t.track_data != "" (a string) — this is inconsistent with the bytes check in get_midi_data() and will cause an incorrect track count in the header if track_data is a bytes object. Reimplementations should use a consistent bytes-empty check for both header and concatenation to avoid mismatched track counts.
- tracks is declared at class scope as a mutable list; this often leads to shared state across instances unless overridden in __init__. When reimplementing, make tracks an instance attribute initialized to an empty list if no tracks are provided.

## Lifecycle:
Creation:
- Constructor signature: MidiFile(tracks=None)
  - tracks: optional list of track-like objects. If omitted or None, an empty list is used.
  - The constructor calls reset() then assigns self.tracks = tracks (the reset call iterates over current self.tracks and calls reset() on each element; because self.tracks is temporarily the class attribute at start, this will call reset on any pre-existing class-level tracks if present — another reason to avoid class-level mutable defaults).
  - No exceptions are explicitly raised by the constructor in the source, but if passed tracks contains objects without the expected attributes, later methods will raise AttributeError when called.

Usage (typical method ordering):
1. Instantiate: mf = MidiFile([track1, track2, ...]) — tracks can be empty.
2. Optionally modify tracks (append, remove) or set instance time_division.
3. Create/ensure each track has been populated (e.g., via MidiTrack.play_Track / play_Bar, etc.) so track.track_data contains the track's events.
4. Obtain bytes: data = mf.get_midi_data() — returns full file bytes (header + all non-empty track chunks).
5. Persist to disk: mf.write_file(path, verbose=False) — writes the bytes to the file path. write_file returns True on success, False on failure.

Sequence constraints:
- No strict ordering is enforced by MidiFile, but calling get_midi_data() or write_file() before tracks are populated will produce a file with no track chunks (header will indicate the track count computed by header()).
- If reset() is called after tracks have been populated, each track.reset() will be invoked, clearing track_data and delta-time; subsequent get_midi_data() will reflect empty tracks.

Destruction / cleanup:
- No context manager or destructor is provided. write_file handles file opening/writing/closing itself and always closes the file handle on success or error path when using the present code path. There are no other external resources to release.
- If implementing an equivalent, ensure files are closed (use with open(..., "wb") to guarantee closure).

## Method Map:
Graph of method relationships and typical call flow (Mermaid flowchart):

flowchart TD
    A[__init__] --> B[reset]
    A --> C[tracks assigned]
    C --> D[get_midi_data]
    D --> E[header]
    D --> F[track.get_midi_data for each non-empty track]
    E --> G[uses time_division]
    H[write_file(path, verbose)] --> D
    B --> I[for each track: track.reset()]

Notes:
- header() is invoked only by get_midi_data().
- write_file() calls get_midi_data() and performs I/O.
- reset() iterates over self.tracks and invokes each track.reset().

## Methods (behavioral details sufficient to reimplement):
- __init__(self, tracks=None)
  - Purpose: initialize instance state.
  - Behavior: If tracks is None, use a new empty list. Call reset() (which calls reset on tracks present at that time), then set self.tracks = tracks.
  - Edge cases: Because reset() runs before self.tracks is set from argument, if the class-level attribute tracks contains entries they'll be reset; avoid class-level mutable defaults.

- get_midi_data(self) -> bytes
  - Purpose: return the full MIDI file byte stream.
  - Behavior:
    - Collects track chunk bytes by iterating self.tracks and calling t.get_midi_data() on each t whose t.track_data is not empty (source checks for bytes inequality against b"").
    - Concatenate header() with the concatenated track chunk bytes and return the resulting bytes object.
  - Constraints:
    - Each track must implement get_midi_data() and have track_data attribute (bytes).
    - If any element lacks these, AttributeError will occur.
  - Edge cases:
    - Empty or all-empty tracks result in header-only output (header still produced).
    - Be aware of the header/track-count mismatch bug in the original (see "State").

- header(self) -> bytes
  - Purpose: build the MIDI file MThd chunk (header chunk) for a format-1 file.
  - Behavior:
    - Count number_of_tracks = the number of tracks that should be present in the resulting file. The original source computes this count with an inconsistent empty check (compares track_data to an empty string). A correct reimplementation should count only tracks where t.track_data is non-empty (bytes).
    - Pack the 2-byte big-endian track count into two bytes and append self.time_division (2 bytes) to complete the 14-byte header:
      - Fixed prefix: b"MThd" + 4-byte length b"\x00\x00\x00\x06" + format bytes b"\x00\x01" (format 1).
      - Then the 2-byte track count and the 2-byte time division.
  - Constraints:
    - time_division must be exactly two bytes.
  - Example: header returns b"MThd\x00\x00\x00\x06\x00\x01" + track_count_bytes + time_division

- reset(self)
  - Purpose: reset child tracks to empty state.
  - Behavior: iterate over self.tracks and call t.reset() for each t. Uses list comprehension in the source (side-effect only).
  - Edge cases: If tracks contains objects without reset method, an AttributeError will be raised.

- write_file(self, file, verbose=False) -> bool
  - Purpose: serialize and persist the MIDI bytes to disk.
  - Parameters:
    - file: str or path-like — the file path to write to.
    - verbose: bool — when True prints the number of bytes written and the file path on success.
  - Behavior:
    - Calls get_midi_data() to produce bytes.
    - Attempts to open file for binary writing ("wb"). If opening fails, prints an error to stdout and returns False.
    - Attempts to write the bytes to the file. If writing fails, prints an error and returns False.
    - Closes the file and returns True on success. If verbose, prints the byte length and file name.
  - Error handling:
    - The source code catches all exceptions when opening and writing (broad except), prints a message, and returns False. Reimplementations should prefer catching specific exceptions (IOError/OSError) and optionally re-raising or returning status.
  - Edge cases:
    - If get_midi_data() raises, the write_file method will propagate unless caught internally. In source, get_midi_data() is called before the open, so any exceptions there are not caught by the open/write try/except blocks.

## Raises:
- __init__:
  - The constructor does not explicitly raise; however, since it calls reset() before assigning self.tracks (and reset() iterates over class-level tracks if present), if class-level tracks contain objects whose reset() raises, that exception will propagate out of __init__.
- get_midi_data / header:
  - AttributeError: if elements of self.tracks do not have track_data or get_midi_data.
  - ValueError / TypeError: if time_division is not exactly two bytes or if track_count encoding fails (in implementations that format numeric values).
- reset:
  - AttributeError: if any track in self.tracks does not implement reset().
- write_file:
  - In the provided source, file open/write errors are caught and cause write_file to return False and print messages. If reimplemented to allow exceptions to propagate, IO-related exceptions (OSError, IOError) may be raised.

## Example:
Create a MidiFile with two MidiTrack-compatible objects, get the MIDI bytes, and write to disk.

Example sequence (pseudo-code):
- Create/populate two MidiTrack instances (track1, track2) so each has track_data populated.
- mf = MidiFile(tracks=[track1, track2])
- data = mf.get_midi_data()               # header + concatenated non-empty track chunks
- success = mf.write_file("output.mid", verbose=True)
- If success is True, "output.mid" contains a valid MIDI format-1 file assembled from the given tracks.

Implementation hints and gotchas:
- Ensure the header's track count equals the number of track chunks appended. Use the same emptiness check (bytes != b"") in both header() and get_midi_data().
- Avoid the class-level mutable default for tracks; initialize an instance attribute to an empty list when no tracks are provided.
- Use context managers when writing files to guarantee proper closure and to handle errors precisely.
- Validate that time_division is two bytes when building the header to avoid malformed files.

### `mingus.midi.midi_file_out.MidiFile.__init__` · *method*

## Summary:
Constructs a MidiFile instance by invoking the class's reset behavior and assigning the instance's tracks reference to the provided list (or a newly-created empty list), leaving the object in a ready state for MIDI data generation and writing.

## Description:
The constructor performs two steps:
1. Calls reset(), which iterates over the current self.tracks and calls reset() on each contained track object.
2. Assigns self.tracks to the caller-supplied tracks argument, or to a fresh empty list when tracks is None.

Known callers and context:
- Called when code creates a MidiFile to prepare MIDI content: typical lifecycle is instantiate MidiFile -> populate or mutate self.tracks -> call get_midi_data() or write_file().
- The method is invoked automatically on object instantiation; no other internal code in the class calls the constructor directly.

Why reset() is invoked here:
- reset() centralizes per-track reinitialization. Invoking it from __init__ ensures any pre-existing tracks (notably the class-level MidiFile.tracks default) are reset consistently without duplicating reset logic inside the constructor.

## Args:
    tracks (list-like or None, optional): Default None.
        - If None, a new empty list is created and assigned to self.tracks.
        - If provided, the value is assigned directly to self.tracks (no shallow or deep copy performed).
        - Expected element shape: objects implementing track-like behavior (e.g., a reset() method, later used by get_midi_data(), and exposing track_data). The constructor does not validate element types.

## Returns:
    None: The constructor returns implicitly; no value is returned.

## Raises:
    TypeError: If the existing self.tracks (accessed inside reset()) is not iterable, the list-comprehension in reset() will raise TypeError during iteration.
    AttributeError: If any element in the iterable accessed by reset() lacks a reset() attribute, calling reset() on that element raises AttributeError and propagates out of __init__.
    Any exception raised by a track.reset() implementation will propagate out of the constructor.

## State Changes:
    Attributes READ:
        - self.tracks (read by reset(); at this time the instance attribute may not exist, so the class attribute MidiFile.tracks is used if present)
    Attributes WRITTEN:
        - self.tracks (assigned to the provided tracks object or to a new empty list when tracks is None)

## Constraints:
    Preconditions:
        - No strict typing enforced by the constructor. For safe subsequent use of the MidiFile instance, self.tracks should be an iterable (preferably a list) whose elements implement the interfaces expected by other MidiFile methods (reset(), get_midi_data(), and expose track_data).
        - Be aware that reset() runs before assigning the incoming tracks: if the class-level attribute MidiFile.tracks contains shared track objects, they will be reset during construction.

    Postconditions:
        - self.tracks references the provided tracks argument if it was not None, otherwise a new empty list.
        - No other instance attributes are modified by __init__.

## Side Effects:
    - Invokes reset() which iterates over and calls reset() on the current self.tracks collection; because this occurs before assignment, it may mutate objects in the class-level MidiFile.tracks (shared across instances).
    - Assigning self.tracks does not clone the list; caller and instance share the same list object, so subsequent mutations to that list by either party are visible to the other.
    - No file I/O or network I/O occurs inside the constructor.

## Example:
    - Typical instantiation:
      MidiFile()                # creates instance with an empty tracks list
      MidiFile(tracks=[])       # explicitly supplies an empty list
      MidiFile(tracks=existing) # assigns existing (shared) list reference

### `mingus.midi.midi_file_out.MidiFile.get_midi_data` · *method*

## Summary:
Assembles and returns the complete MIDI file bytes by concatenating the file header with the binary data of all tracks that contain non-empty track data. Does not modify the MidiFile object.

## Description:
This method collects the MIDI data for every track in self.tracks whose track_data is non-empty (tracks where t.track_data != b"") by calling each track's get_midi_data() and concatenating their bytes together. It prefixes the concatenated track bytes with the file header returned by self.header() and returns the resulting bytes object.

Known callers and lifecycle stage:
- MidiFile.write_file calls this method to obtain the full MIDI file bytes immediately before writing to disk. Typical lifecycle: after building or populating Track/MidiTrack objects and their track_data, call get_midi_data() to serialize the file for persistence or transmission.
- External code may call this method when it needs an in-memory bytes representation of the MIDI file (e.g., for sending over a network, embedding in another container, or unit testing).

Why this logic is a separate method:
- Serialization is logically distinct from track construction/manipulation; isolating it makes the serialization step reusable (e.g., write_file and other consumers).
- Centralizing header + track assembly reduces duplication and keeps file-format specific concatenation in one place.

Note / Caveat:
- This method relies on header(), and header() itself enumerates tracks to compute the track count. There is a small inconsistency in the current header() implementation (it compares track_data to the empty string "" rather than the empty bytes b""), which may affect the track count calculation in some edge cases; get_midi_data filters tracks using b"".

## Args:
This method takes no explicit arguments (self only).

## Returns:
bytes: A bytes object that is the full serialized MIDI file:
    - Begins with the standard MIDI file header bytes returned by self.header().
    - Followed by zero or more track chunks produced by each track's get_midi_data().
    - If no tracks contain non-empty track_data, returns header bytes followed by an empty body (i.e., header only).

## Raises:
This method does not raise explicit exceptions itself, but may propagate exceptions raised by:
    - Missing attributes or incorrect types on track objects (AttributeError or TypeError) if a track does not have track_data or get_midi_data.
    - Exceptions raised by an individual track's get_midi_data() implementation.
    - Any exceptions raised by header() (e.g., if header() relies on attributes that are malformed).

## State Changes:
Attributes READ:
    - self.tracks (list of track-like objects): iterated to select tracks and to call t.get_midi_data().
    - For each selected track t, reads t.track_data to decide whether to include the track and calls t.get_midi_data() (which itself reads t.track_data and returns track bytes).
    - Indirectly reads attributes used by header(), e.g., self.time_division (header() reads this attribute).

Attributes WRITTEN:
    - None. The method does not modify self or contained track objects (it only reads and calls their getter/serialization methods). Note: an individual track's get_midi_data() could mutate that track if its implementation does so; that would be a side effect of the track implementation, not this method itself.

## Constraints:
Preconditions:
    - self.tracks must be an iterable (typically list) of objects that:
        * expose a track_data attribute (bytes-like) and
        * implement a get_midi_data() method that returns bytes representing the full track chunk.
    - header() must be present and return a bytes object suitable as the start of a MIDI file.
    - track.track_data is expected to be bytes. get_midi_data filters tracks using the test t.track_data != b"".

Postconditions:
    - Returns a bytes object representing a serialized MIDI file (header followed by serialized track chunks for each selected track).
    - Does not change self.tracks or MidiFile attributes.

## Side Effects:
    - No I/O or external service calls are performed by this method.
    - The only observable effects are calls to each selected track's get_midi_data(); if those methods mutate track state, such mutations will occur as a side effect (this method does not itself perform such mutations).
    - Any exceptions from header() or track.get_midi_data() will propagate to the caller.

### `mingus.midi.midi_file_out.MidiFile.header` · *method*

## Summary:
Produces and returns the 14-byte MIDI file header chunk (bytes) for this MidiFile instance and does not modify object state.

## Description:
This method constructs the standard MIDI header chunk (MThd) containing:
- the 4-byte chunk ID "MThd",
- the 4-byte chunk length (always 6),
- the 2-byte MIDI format (0x0001, multi-track),
- a 2-byte track count computed from this object's tracks,
- and the 2-byte time division stored on the object.

Known callers and call context:
- MidiFile.get_midi_data: invokes header() as the first part of assembling the full MIDI file bytes. get_midi_data then appends per-track MIDI data and returns the complete file body.
- MidiFile.write_file: indirectly uses header() via get_midi_data when writing the file to disk.

Why this logic is a dedicated method:
- The header is a self-contained, protocol-specified byte sequence that is reused whenever the file's binary representation is produced. Isolating header construction keeps get_midi_data focused on assembling track data and makes header generation easier to test and maintain.

## Args:
None.

## Returns:
bytes: A bytes object containing the MIDI file header chunk. Structure:
- b"MThd" (4 bytes)
- b"\x00\x00\x00\x06" (4 bytes: chunk length = 6)
- b"\x00\x01" (2 bytes: MIDI format 1)
- 2 bytes: big-endian track count (computed from self.tracks)
- 2 bytes: time division (self.time_division, appended as-is)

Edge cases:
- If there are zero qualifying tracks, the track count is b'\x00\x00'.
- If self.time_division is not a bytes-like object of length 2, the returned header will be malformed or concatenation will raise a TypeError.

## Raises:
No exceptions are explicitly raised by this method. Runtime exceptions that can occur due to malformed object state:
- TypeError: if any piece concatenated is not a bytes-like object (for example, if self.time_division is a str rather than bytes).
- binascii.Error (or ValueError in some Python versions) is unlikely here because the code formats the track count as a zero-padded 4-hex-digit string before calling a2b_hex; under normal operation this is well-formed.

## State Changes:
Attributes READ:
- self.tracks: iterated to compute the number of (non-empty) tracks.
- self.time_division: appended to the header as the 2-byte division field.

Attributes WRITTEN:
- None. This method does not modify any attributes.

## Constraints:
Preconditions:
- self.tracks must be an iterable of track-like objects exposing a track_data attribute.
- self.time_division should be a bytes object representing two bytes (e.g., b'\x00\x48') to produce a valid MIDI time division field.

Important note about track filtering:
- This method computes the track count using the expression that compares each track's track_data to an empty string (""), i.e., it counts tracks where t.track_data != "". Because track_data is elsewhere (e.g., in get_midi_data) checked against an empty bytes object (b""), a type mismatch (bytes vs. str) may lead to incorrect counting: comparing bytes to str always yields inequality in Python 3, so empty tracks stored as b'' will be counted as non-empty here. Callers relying on consistent filtering should ensure track_data uses the same type expected by this method.

Postconditions:
- Returns a bytes object conforming to the MIDI header chunk format described above, provided preconditions hold.
- Does not alter self or external state.

## Side Effects:
- None: the method performs no I/O and does not modify global state or any objects outside self. It only reads attributes and returns a bytes object.

### `mingus.midi.midi_file_out.MidiFile.reset` · *method*

## Summary:
Calls reset() on every track in the file, clearing each track's generated MIDI data and resetting its per-track timing state.

## Description:
Known callers and context:
- MidiFile.__init__: invoked during object construction to ensure any pre-existing tracks are reset before the instance is populated (note: __init__ calls reset() before assigning the constructor's tracks argument to self.tracks).
- External callers (user code): may call this method when reusing a MidiFile instance to clear all tracks' internal state before regenerating MIDI data or writing a new file.

Why this is a separate method:
- Centralizes the "clear all track state" operation so callers need only invoke one method to clear every contained track.
- Encapsulates the iteration over tracks and the expectation that each track implements a reset() method; avoids duplicating that logic wherever track clearing is required.

Behavior summary:
- Iterates over self.tracks and calls reset() on each element.
- Does not alter the self.tracks list itself (no addition/removal), only triggers each track's own reset behavior.

## Args:
This method takes no arguments.

## Returns:
None.

## Raises:
- TypeError: If self.tracks is not iterable (e.g., None or a non-iterable object) the iteration will raise TypeError.
- AttributeError: If any element in self.tracks does not provide a reset() method, calling t.reset() will raise AttributeError.
- Exceptions raised by individual track.reset() calls: any exception propagated from the concrete track.reset implementation will surface to the caller.

## State Changes:
Attributes READ:
- self.tracks

Attributes WRITTEN:
- No attributes of self are modified by this method.

Indirect modifications (mutations to objects inside self.tracks):
- For a Mingus MidiTrack instance: track.track_data is set to b"" and track.delta_time is set to b"\x00" (i.e., the per-track MIDI buffer and current delta-time are cleared).
- For other track implementations: whatever their reset() method defines — typically clearing per-track buffers and timing state.

## Constraints:
Preconditions:
- self.tracks must be an iterable of objects that implement a reset() method.
- Each track.reset() must be safe to call in the current lifecycle (e.g., not concurrently modified from other threads unless externally synchronized).

Postconditions:
- For every element t in the original self.tracks iterable, t.reset() has been invoked exactly once (subject to exceptions interrupting the loop).
- For Mingus MidiTrack elements, after successful completion:
  - t.track_data == b""
  - t.delta_time == b"\x00"

## Side Effects:
- Mutates the state of objects held in self.tracks (see "Indirect modifications" above).
- No file I/O, network I/O, or external resource usage performed by this method itself.
- If an exception occurs while resetting a track, later tracks may not be reset (exception propagation stops the iteration unless the caller handles exceptions).

### `mingus.midi.midi_file_out.MidiFile.write_file` · *method*

## Summary:
Writes the serialized MIDI file bytes produced by the MidiFile to a filesystem path and returns a boolean success flag; does not modify the MidiFile object.

## Description:
This method serializes the current MidiFile by calling self.get_midi_data() and attempts to write that bytes object to the filesystem at the given path. Typical usage is the final persistence step after constructing or populating MidiFile.tracks and related track objects; call this method when you want to persist the assembled MIDI file to disk.

Known callers and lifecycle stage:
- No internal callers are recorded inside the library; this method is intended to be invoked by external application code or end-user scripts after building/assembling the MidiFile content.
- Lifecycle: serialization -> persistence. The normal pipeline is: create/populate Track/MidiTrack objects -> add them to a MidiFile -> call write_file(...) to produce a .mid file on disk.

Why this logic is its own method:
- Separates concerns: assembling the MIDI bytes (get_midi_data/header/track serialization) is decoupled from file I/O and error reporting. This keeps serialization reusable (in-memory use) and centralizes the filesystem write behavior and user-visible error messages in a single place.

## Args:
    file (str | os.PathLike): Path to the output file. The method calls open(file, "wb"), so this must be a path-like object acceptable to Python's open() and refer to a location where the process has permission to create/write a file.
    verbose (bool): Optional; defaults to False. When True, prints a success line stating how many bytes were written and the path.

## Returns:
    bool: True if the method successfully opened the file, wrote all bytes returned by self.get_midi_data(), closed the file, and printed the verbose message if requested. Returns False if an exception occurred while opening or while writing the file (these failure cases are caught and result in a printed error message and False).

    Edge cases:
    - If open(file, "wb") raises any exception (e.g., FileNotFoundError, PermissionError, TypeError for an invalid path), the method catches the exception, prints an error message, and returns False.
    - If f.write(dat) raises any exception, the method catches it, prints an error message and returns False. The file may have been created and may contain partial data in this case.

## Raises:
    - Exceptions raised by self.get_midi_data(): get_midi_data is invoked before any try/except in write_file. Any exception thrown while assembling the MIDI bytes (for example AttributeError, TypeError, or custom exceptions from track serialization) will propagate to the caller.
    - Exceptions raised after the write try/except block (for example errors from f.close() or from evaluating len(dat) in the verbose branch) are not caught by the method and will propagate.

    Note: open() and write() exceptions are intentionally caught by broad except clauses and handled by printing an error and returning False; they are not re-raised.

## State Changes:
Attributes READ:
    - Indirectly reads whatever self.get_midi_data() reads. Concretely, get_midi_data() reads self.tracks and calls each track.get_midi_data(), and header() reads self.tracks and self.time_division. Therefore this method depends on:
        * self.tracks
        * self.time_division (via header)
        * any attributes accessed by individual track.get_midi_data()

Attributes WRITTEN:
    - None. This method does not modify self or its attributes.

## Constraints:
Preconditions:
    - self.get_midi_data() must return a bytes-like object (the implementation expects to write a bytes object to a binary file). If it returns a non-bytes object that is not acceptable to f.write(), write() may raise and the method will catch or propagate depending on where it occurs.
    - The provided file path must be valid and writable by the running process (permission and filesystem constraints).
    - The caller should be prepared to handle exceptions from get_midi_data() (these are not caught here).

Postconditions:
    - On return True:
        * The file at the provided path has been opened in binary write mode, the bytes returned from get_midi_data() have been written, and the file has been closed.
        * If verbose=True, a line was printed to stdout reporting the number of bytes written and the path.
    - On return False:
        * An error message was printed to stdout describing the inability to open or write the target file.
        * The file may not exist or may contain partial data if the write failed after the file was created.

## Side Effects:
    - Performs filesystem I/O: opens (creates/truncates) the target file path, writes data, and closes the file.
    - Emits user-visible messages via print():
        * On open failure: "Couldn't open '<path>' for writing."
        * On write failure: "An error occured while writing data to <path>."
        * On success when verbose=True: "Written <N> bytes to <path>."
    - No in-memory mutation of the MidiFile object itself, but called serialization helpers (track.get_midi_data()) may have side effects if their implementations mutate track state.

## `mingus.midi.midi_file_out.write_Note` · *function*

## Summary:
Creates a single-track MIDI file that plays a given note (repeat + 1 times) at the specified tempo and writes the resulting .mid file, returning whether the file write succeeded.

## Description:
This convenience function:
- Constructs a new MidiFile and a single MidiTrack configured with the provided bpm.
- For each iteration (total iterations = repeat + 1), sets an immediate delta time, issues a play_Note for the supplied note, sets a fixed delta time (b"\x48") to represent the note duration, and then issues stop_Note.
- Delegates serialization and file writing to MidiFile.write_file and returns its boolean result.

Known callers:
- No internal callers were found in the inspected codebase. Intended for external use (tests, quick exports) to produce a minimal single-note MIDI file.

Responsibility boundary:
- Encapsulates the simple sequence of creating a MidiFile/MidiTrack, emitting play/stop events for a single note repeatedly, and writing the file. It does not perform note validation or low-level MIDI formatting — those responsibilities belong to MidiTrack and MidiFile respectively.

## Args:
    file (str or path-like):
        Destination path for the .mid file. Passed directly to MidiFile.write_file.
    note (any):
        Note identifier forwarded verbatim to MidiTrack.play_Note(note) and MidiTrack.stop_Note(note).
        Acceptable types/values depend on the MidiTrack implementation (for example, note-name strings like "C-4" or Note objects). This function performs no validation.
    bpm (int, optional):
        Tempo in beats per minute passed to MidiTrack(bpm). Defaults to 120.
    repeat (int, optional):
        Number of additional repetitions beyond the first. Because the loop condition is while repeat >= 0, the total number of plays equals repeat + 1. Defaults to 0 (play once). If repeat < 0 the loop body is skipped and no note events are emitted.
    verbose (bool, optional):
        Passed through to MidiFile.write_file; when True, that method may print status messages. Defaults to False.

Interdependencies:
- Requires that MidiTrack(bpm) implements set_deltatime(bytes), play_Note(note), and stop_Note(note).
- Requires MidiFile.write_file(file, verbose) to accept the provided file argument and return a boolean indicating success.

## Returns:
    bool:
        The boolean result returned by MidiFile.write_file(file, verbose).
        - True: write_file reported success and the file was written.
        - False: write_file reported failure (for example, it caught an I/O error and returned False).
    Exceptions are not converted to booleans by this function: if an exception occurs before write_file returns (for example from MidiTrack.play_Note or MidiFile.get_midi_data), that exception will propagate and no boolean is returned.

## Raises:
    Exceptions raised by MidiTrack methods or MidiFile.get_midi_data:
        - AttributeError, TypeError, ValueError, or other exceptions may be raised if MidiTrack.play_Note / stop_Note / set_deltatime or MidiFile.get_midi_data encounter invalid inputs or internal errors. These exceptions are not caught here and will propagate to the caller.
    MidiFile.write_file I/O failures:
        - Per the MidiFile implementation, file open/write errors are caught inside MidiFile.write_file and result in that method returning False; they do not raise out of write_Note under the normal MidiFile.write_file behavior.

## Constraints:
Preconditions:
- The caller should supply a file path writable on the host system.
- The note argument must be recognized by the project's MidiTrack implementation.
- bpm should be a reasonable integer tempo.

Postconditions:
- If True is returned, the specified file path contains the serialized MIDI file built from one MidiTrack with the emitted note events.
- If False is returned, the write failed as reported by MidiFile.write_file (commonly due to I/O errors); partial writes depend on MidiFile.write_file behavior.
- If an exception is raised, no guarantee is made about filesystem changes.

## Side Effects:
- Writes to the filesystem via MidiFile.write_file.
- Allocates in-memory MidiFile and MidiTrack objects.
- May print to stdout/stderr if verbose=True and the underlying write_file implementation prints status or error messages.
- No modification of global variables or external services is performed by this function itself.

## Control Flow:
flowchart TD
    A[Start write_Note] --> B[Create MidiFile instance m]
    B --> C[Create MidiTrack t with bpm]
    C --> D[Set m.tracks = [t]]
    D --> E{repeat >= 0?}
    E -- Yes --> F[set_deltatime(b"\x00") — immediate]
    F --> G[play_Note(note)]
    G --> H[set_deltatime(b"\x48") — fixed duration]
    H --> I[stop_Note(note)]
    I --> J[repeat -= 1]
    J --> E
    E -- No --> K[Call m.write_file(file, verbose)]
    K --> L[Return boolean result from write_file]

Notes:
- The loop condition implies total plays = repeat + 1.
- If repeat < 0 the loop is never entered, and the created track remains empty; the resulting file may therefore contain no note events (behavior depends on MidiFile/MidiTrack implementations).

## Examples:
1) Basic usage — write a single "C-4" note once:
    result = write_Note("single_c4.mid", "C-4")
    if result:
        print("Written single_c4.mid successfully")
    else:
        print("Failed to write single_c4.mid (I/O error or write_file failure)")

2) Play a note 3 times in sequence (repeat=2):
    # This will play the note 3 times because repeat + 1 iterations occur
    success = write_Note("three_clicks.mid", "C-4", bpm=100, repeat=2)
    if not success:
        raise RuntimeError("MIDI file write failed")

3) Handling unexpected exceptions from MidiTrack or MIDI construction:
    try:
        ok = write_Note("out.mid", some_note_object, bpm=120, repeat=0, verbose=True)
        if not ok:
            # write_file returned False (I/O error handled internally by MidiFile)
            handle_io_failure()
    except Exception as exc:
        # An unexpected error occurred during MIDI data construction (invalid note, missing methods, etc.)
        handle_unexpected_error(exc)

Implementation hints:
- The function directly supplies raw delta-time bytes b"\x00" (immediate) and b"\x48" (duration) to the MidiTrack via set_deltatime; these constants are part of the function's simple timing model and are not adjusted by bpm within this code path.
- Rely on MidiTrack for note validation and encoding. This function intentionally avoids duplicating those concerns.

## `mingus.midi.midi_file_out.write_NoteContainer` · *function*

## Summary:
Creates a one-track MIDI file from the given NoteContainer by rendering note-on events, waiting a fixed delta, emitting note-off events, optionally repeating the rendering, and writing the resulting .mid file to disk.

## Description:
This is a small convenience exporter that wraps the MIDI construction and file I/O steps required to persist a single NoteContainer as a standalone MIDI file. It creates a new MidiFile and a single MidiTrack (initialized with the provided bpm), renders the supplied notecontainer onto that track (using MidiTrack.play_NoteContainer and MidiTrack.stop_NoteContainer), optionally repeats that render sequence multiple times, and then writes the assembled MIDI file using MidiFile.write_file.

Known callers within the codebase:
- No internal callers were found in the repository memory for this function. It is intended as a public convenience function for application code or examples that want to write a NoteContainer to disk directly.

Why this is factored out:
- Orchestrates object creation (MidiFile, MidiTrack), the precise sequencing of play/stop events for a NoteContainer (including delta-time setup), and the final file write step. Extracting these steps into one function gives callers a simple single-call API for persisting NoteContainer content without duplicating the orchestration logic across the codebase.

## Args:
    file (str | os.PathLike):
        - Path where the MIDI file will be written. This argument is forwarded directly to MidiFile.write_file which opens the path with open(file, "wb").
        - Must be a valid writable path on the host filesystem (permission/exists constraints apply).
    notecontainer (NoteContainer | Sequence of Note-like objects):
        - A sized, iterable container of note-like objects accepted by MidiTrack.play_NoteContainer and MidiTrack.stop_NoteContainer.
        - Each element must support int(element) to obtain a MIDI note number and must expose .channel and .velocity attributes (see MidiTrack.play_NoteContainer / stop_NoteContainer requirements).
        - The function does not validate container contents itself; type/attribute errors raised during rendering will propagate from the MidiTrack methods.
    bpm (int, optional, default=120):
        - The tempo used to initialize the MidiTrack (passed to MidiTrack(bpm)). Should be a positive integer (typical musical BPM > 0). Extremely large or non-integer values may cause unexpected behavior in tempo encoding inside MidiTrack.
    repeat (int, optional, default=0):
        - Controls how many times the play/stop sequence is executed.
        - Semantics: the loop executes while repeat >= 0, decrementing repeat each iteration. Therefore:
            * repeat == 0 → the sequence is executed exactly once.
            * repeat == n (n >= 0) → the sequence is executed n + 1 times.
            * repeat < 0 → the loop body is skipped and no play/stop events are emitted.
        - Must be an integer; non-integers may raise TypeError at runtime.
    verbose (bool, optional, default=False):
        - Passed through to MidiFile.write_file. When True, write_file prints a success message with the number of bytes written.

Notes on interdependencies:
    - The function relies on MidiTrack.set_deltatime accepting bytes (it passes b'\x00' and b'\x48' directly) and on MidiTrack.play_NoteContainer / stop_NoteContainer to append appropriate note-on/note-off events into the track's internal buffer. It relies on MidiFile.write_file to perform serialization and actual filesystem I/O.

## Returns:
    bool:
        - The boolean result returned by MidiFile.write_file(file, verbose).
        - True: the MIDI bytes were successfully written and the file closed.
        - False: an error occurred while opening or writing the file (open/write failures are caught inside MidiFile.write_file and cause it to return False).
    Edge-case returns:
        - If repeat < 0 or notecontainer is empty, the function still calls MidiFile.write_file; the resulting file may contain only a header and an empty track chunk. write_file will still return True on successful write of that header-only data.

## Raises:
    - Any exception raised during track rendering (before the write_file open/write try block) will propagate:
        * Typical examples: AttributeError or TypeError if notecontainer elements are missing required attributes (.channel, .velocity) or cannot be converted to int().
        * AssertionError raised by lower-level MIDI helpers if note/channel/velocity ranges are violated (e.g., invalid channel or velocity out of 0..127).
    - MidiFile.write_file itself catches open/write I/O exceptions and returns False; these exceptions are not re-raised by this function. However, exceptions from MidiFile.get_midi_data() that occur before the write's try/except may propagate (depending on the MidiFile.write_file implementation).

## Constraints:
Preconditions:
    - notecontainer must be a sized iterable of note-like objects compatible with MidiTrack.play_NoteContainer / stop_NoteContainer.
    - The caller must provide a writable filesystem path for file.
    - bpm should be a valid tempo integer (positive).

Postconditions:
    - A file will have been created/truncated at the given path if MidiFile.write_file returned True (containing a format-1 MIDI file with one track assembled from the rendered events).
    - If write_file returned False, no guarantee exists about file contents (file may be missing or partially written).
    - No external mutable state in the repository is changed; the created MidiFile and MidiTrack are local to the function and discarded after return.

## Side Effects:
    - Filesystem I/O: opens (creates or overwrites) the target path via MidiFile.write_file and writes MIDI bytes.
    - In-memory mutation: the function creates a MidiTrack and mutates its internal state (track_data, delta_time) while rendering. These objects are local to the function and do not affect caller state.
    - No network I/O or global variable mutation is performed.

## Control Flow:
flowchart TD
    A[Start] --> B[Create MidiFile instance m]
    B --> C[Create MidiTrack t with start_bpm=bpm]
    C --> D[Assign m.tracks = [t]]
    D --> E{Is repeat >= 0?}
    E -- No --> I[Call m.write_file(file, verbose) → return result]
    E -- Yes --> F[set_deltatime(b'\x00')]
    F --> G[play_NoteContainer(notecontainer)]
    G --> H[set_deltatime(b'\x48')]
    H --> J[stop_NoteContainer(notecontainer)]
    J --> K[repeat -= 1]
    K --> E
    I --> L[End]

Notes:
    - The loop runs zero or more times depending on the initial repeat value; with repeat==0 it runs once.
    - Errors during play_NoteContainer/stop_NoteContainer will interrupt the loop and propagate out (no file I/O will be attempted if rendering fails before the final write call).
    - write_file handles file open/write exceptions internally and returns a boolean; these failures do not raise.

## Examples:
1) Basic usage — write a NoteContainer once at 120 BPM:
    - Prepare a NoteContainer nc populated with Note objects accepted by the track renderer.
    - Call: success = write_NoteContainer("solo.mid", nc)
    - If success is True, "solo.mid" contains a one-track MIDI file with the rendered events.

2) Play the container twice and print result:
    - Call: ok = write_NoteContainer("repeat.mid", nc, bpm=100, repeat=1, verbose=True)
    - Behavior: the play/stop sequence is executed 2 times (repeat + 1). The function prints a success message if verbose=True and write succeeds. Handle ok == False as a write failure.

3) Edge-case: empty container or negative repeat:
    - With an empty NoteContainer or repeat < 0, the function still writes a MIDI file (header + empty track) if write succeeds. Check the boolean return value to confirm successful write.

## `mingus.midi.midi_file_out.write_Bar` · *function*

## Summary:
Creates a minimal MIDI file that contains a single track which plays the given Bar a specified number of times, and writes the result using the MidiFile writer.

## Description:
This function constructs a new MidiFile with one MidiTrack (initialized with the provided bpm), instructs that track to play the supplied Bar repeatedly, and then delegates the actual file writing to MidiFile.write_file.

Known callers within the provided code snapshot:
    - No callers were discovered in the provided file-level snapshot. It is a top-level helper intended for simple one-bar MIDI export and is typically invoked by higher-level utilities, scripts, or examples that need to persist a single Bar to disk.

Why this logic is extracted into its own function:
    - It encapsulates the pattern of: create MidiFile -> create MidiTrack(bpm) -> add the Bar content to the track a specified number of times -> write the file. Separating this flow avoids duplicating MidiFile/MidiTrack creation and write-file error handling wherever a single-bar export is needed, and provides a small, well-defined utility for single-Bar MIDI exports.

## Args:
    file:
        - type: forwarded to MidiFile.write_file as-is
        - description: The destination identifier accepted by MidiFile.write_file. The exact accepted forms (filename string, file-like object, etc.) depend on MidiFile.write_file's implementation; this function passes the value through without modification.
    bar (mingus.containers.bar.Bar):
        - type: Bar (from mingus.containers.bar)
        - description: A Bar object (or another object accepted by MidiTrack.play_Bar) whose contents will be written into the track. If the object is incompatible with MidiTrack.play_Bar, an exception will propagate from that call.
    bpm (int, optional):
        - default: 120
        - description: Beats per minute passed to the MidiTrack constructor. This value is forwarded to MidiTrack(bpm) and controls tempo metadata in the created MidiTrack.
    repeat (int, optional):
        - default: 0
        - description: Number of additional repeats beyond the first play. Implementation detail: the function executes t.play_Bar(bar) while repeat >= 0, decrementing repeat each iteration. Therefore the Bar is played (repeat + 1) times when repeat is >= 0. If repeat is negative (< 0), the loop body is skipped and the Bar is not played at all.
    verbose (bool, optional):
        - default: False
        - description: Passed through to MidiFile.write_file as the verbosity flag. The precise effect is determined by MidiFile.write_file.

Interdependencies:
    - The accepted form of file and the semantics of verbose are determined entirely by MidiFile.write_file.
    - The function assumes that MidiTrack.play_Bar knows how to handle the provided bar object.

## Returns:
    - Returns whatever MidiFile.write_file(file, verbose) returns.
    - Common cases:
        * On success, MidiFile.write_file typically returns a success indicator (implementation-specific); this function forwards that value.
        * On failure, exceptions raised by MidiFile.write_file (or earlier by MidiTrack.play_Bar) will propagate to the caller.

## Raises:
    - Any exception raised by:
        * MidiTrack(bpm) (e.g., invalid bpm handling in MidiTrack.__init__)
        * MidiTrack.play_Bar(bar) (e.g., TypeError for incompatible bar)
        * MidiFile.write_file(file, verbose) (e.g., I/O errors, permission errors)
    - This function does not catch or wrap exceptions; they propagate directly to the caller.

## Constraints:
Preconditions:
    - The caller should supply a bar object acceptable to MidiTrack.play_Bar (normally a mingus.containers.bar.Bar).
    - bpm should be a value acceptable to MidiTrack; this function does not validate bpm.
    - The file argument must be compatible with MidiFile.write_file.

Postconditions:
    - A MidiFile object was created with a single MidiTrack and assigned to m.tracks.
    - If repeat >= 0, the track has had t.play_Bar(bar) invoked (repeat + 1) times; if repeat < 0, no play occurred.
    - The write operation was attempted via MidiFile.write_file(file, verbose), and its result was returned or its exception propagated.

## Side Effects:
    - I/O: Delegates to MidiFile.write_file to persist data; this typically writes to disk or to a provided file-like object.
    - No global variables are modified by this function itself.
    - External state changes and I/O semantics depend on MidiFile.write_file's implementation (file creation, truncation, permission checks, etc.).

## Control Flow:
flowchart TD
    Start --> Create_MidiFile[Create MidiFile()]
    Create_MidiFile --> Create_MidiTrack[Create MidiTrack(bpm)]
    Create_MidiTrack --> Assign_Tracks[Set m.tracks = [t]]
    Assign_Tracks --> Check_Repeat{repeat >= 0 ?}
    Check_Repeat -- Yes --> Play_Bar[Call t.play_Bar(bar)]
    Play_Bar --> Decrement[repeat -= 1]
    Decrement --> Check_Repeat
    Check_Repeat -- No --> Write_File[Call m.write_file(file, verbose)]
    Write_File --> Return[Return value from m.write_file]
    Return --> End

## Examples:
Example 1 — Write a single Bar once to "output.mid":
    try:
        result = write_Bar("output.mid", my_bar)
    except Exception as e:
        # handle error (I/O or data incompatibility)
        print("Failed to write MIDI:", e)
    else:
        print("Write result:", result)

Example 2 — Write a Bar three times (repeat=2) at 90 bpm:
    try:
        write_Bar("/tmp/looped_bar.mid", my_bar, bpm=90, repeat=2, verbose=True)
    except IOError:
        print("Unable to write file; check permissions and path.")
    except Exception as e:
        print("Unexpected error:", e)

Notes:
    - Because this function delegates both bar handling and file writing to MidiTrack.play_Bar and MidiFile.write_file respectively, examine those components for details on allowed Bar contents, tempo handling, and precise file I/O behavior.

## `mingus.midi.midi_file_out.write_Track` · *function*

## Summary:
Writes a Track-like object to a MIDI file on disk by creating a temporary MidiTrack, playing the Track into it (possibly repeated), and delegating serialization to MidiFile.write_file; returns the write success flag.

## Description:
This is a small convenience utility that converts a higher-level Track-like object (an iterable of Bar-like objects with instrument metadata) into a .mid file. It performs three responsibilities:
1. Instantiate a MidiFile and a single MidiTrack configured with the given tempo (bpm).
2. Instruct the MidiTrack to translate the provided Track into MIDI events, repeating that translation as requested.
3. Persist the assembled MidiFile bytes to disk via MidiFile.write_file(file, verbose).

Known callers within the codebase:
- No internal library callers were found in the provided source snapshots. This function is a public convenience helper intended for use by application code or examples that want a one-call path from mingus.containers.track.Track -> .mid file.

Context / when to call:
- Call when you have a populated Track (from mingus.containers.track.Track or any Track-like object) and want to persist it as a standard MIDI file on disk without manually constructing MidiTrack and MidiFile objects.

Why this logic is factored into its own function:
- It bundles the common orchestration steps (create MidiFile/MidiTrack, play the Track into the MidiTrack possibly multiple times, then write to disk) into a single helper so callers don't need to repeat that sequence. It enforces the boundary between high-level musical containers (Track/Bar/Notes) and low-level MIDI serialization (MidiTrack/MidiFile).

## Args:
    file (str | os.PathLike):
        Path to the output file to be created (passed through to MidiFile.write_file which opens the path with open(file, "wb")). Must be a path-like object acceptable to Python's open() and writable by the process.
    track (object):
        Required. A Track-like object. Requirements:
        - Iterable: yields Bar-like objects.
        - Exposes attribute 'instrument' (used unguarded by MidiTrack.play_Track).
        - Optionally exposes 'name' (if present, used for a track-name meta-event).
        The function does not validate types beyond relying on MidiTrack.play_Track; incompatible objects will cause exceptions from the called methods.
    bpm (int, optional):
        Tempo in beats-per-minute used to initialize the MidiTrack. Default: 120.
        Allowed values: positive integers; values <= 0 are not meaningful for tempo and may cause downstream errors when serializing/playing.
    repeat (int, optional):
        Number controlling how many times the Track is played into the single MidiTrack instance.
        Semantics: the function executes the play loop while repeat >= 0, decrementing repeat each iteration. Therefore the Track is processed (repeat + 1) times when repeat >= 0.
        Examples:
            - repeat = 0  => Track is played once
            - repeat = 1  => Track is played twice (original + one repeat)
            - repeat = -1 => Track is not played at all
        Default: 0.
    verbose (bool, optional):
        Passed through to MidiFile.write_file. When True, write_file may print a confirmation line describing how many bytes were written. Default: False.

Interdependencies:
- The bpm parameter is passed only to MidiTrack constructor; the correctness of tempo-related MIDI events depends on MidiTrack and its helpers (set_tempo, play_Bar).
- The repeat parameter affects how many times MidiTrack.play_Track is invoked and therefore how much MIDI data is appended to the temporary track before writing.

## Returns:
    bool:
        The boolean value returned by MidiFile.write_file(file, verbose).
        - True: file was successfully opened and written (write_file's success path).
        - False: write_file detected an I/O failure when opening or writing the file and returned False (write_file prints an error message in this case).
    Edge cases:
        - If repeat < 0, the Track will not be played at all, so the MidiFile will likely contain no non-empty track chunks (resulting in a header-only file or 0-track file depending on MidiFile implementation). write_file will still be invoked and may succeed (True) writing an essentially empty MIDI file.
        - If t.play_Track(track) or MidiFile.get_midi_data() raises, those exceptions propagate; write_Track does not catch exceptions raised during track processing or during serialization prior to file open/write (write_file catches open/write exceptions but not exceptions raised by get_midi_data()).

## Raises:
    AttributeError:
        - If the provided track is missing attributes or yields Bars incompatible with MidiTrack.play_Track, calls inside MidiTrack.play_Track may raise AttributeError (for example missing 'instrument' attribute). These propagate out of write_Track.
    UnicodeEncodeError:
        - If track.name exists and contains characters that cannot be encoded by MidiTrack.set_track_name (typically ASCII encoding), setting the track name may raise UnicodeEncodeError propagated up.
    Any exceptions raised by MidiTrack.play_Track, MidiTrack internals, or MidiFile.get_midi_data():
        - These will propagate to the caller. write_Track does not catch exceptions from play_Track or from MidiFile.get_midi_data(); write_file itself catches open/write IO exceptions internally and returns False instead of raising for those cases.
    Note:
        - I/O errors while opening or writing the file are handled inside MidiFile.write_file which returns False rather than raising; therefore write_Track will return False in those cases rather than raise.

## Constraints:
Preconditions:
    - The caller must supply a writable file path and a Track-like object satisfying the expectations above.
    - bpm should be a positive integer; non-positive or non-integer tempo values may produce undefined/malformed tempo events depending on MidiTrack implementation.
    - The environment must permit file creation at the given path (permissions, disk space).

Postconditions:
    - On normal completion (no exceptions and write_file returns True): a file has been created at the given path containing the MIDI data produced by playing the Track the requested number of times at the specified bpm.
    - The function does not mutate the provided Track object; it mutates an internal MidiTrack instance (appending to its track_data) and then writes the resulting MidiFile to disk.
    - Any MidiTrack or MidiFile objects created are local to the function and not returned.

## Side Effects:
    - Filesystem I/O: creates/truncates and writes to the specified file path (via MidiFile.write_file).
    - In-memory mutation: the temporary MidiTrack instance (internal to the function) is mutated by MidiTrack.play_Track (it accumulates track_data). The provided Track object is not modified by this function.
    - Console output: if verbose=True and write_file succeeds, MidiFile.write_file may print a success line; if write_file fails opening or writing the file it prints an error message and write_Track returns False.

## Control Flow:
flowchart TD
    Start --> CreateMidiFile[Create MidiFile() m]
    CreateMidiFile --> CreateMidiTrack[Create MidiTrack(bpm) t]
    CreateMidiTrack --> AssignTracks[m.tracks = [t]]
    AssignTracks --> CheckRepeat{repeat >= 0 ?}
    CheckRepeat -- Yes --> PlayOnce[t.play_Track(track)]
    PlayOnce --> Decrement[repeat -= 1]
    Decrement --> CheckRepeat
    CheckRepeat -- No --> CallWrite[return m.write_file(file, verbose)]
    CheckRepeat -- Initially No (repeat < 0) --> CallWrite

Notes:
- The loop runs (repeat + 1) times when repeat >= 0; if repeat < 0 the Track is not played.
- There is no try/except in this function: exceptions from play_Track or MidiFile.get_midi_data() propagate; write_file internally catches file open/write exceptions and returns False.

## Examples:
1) Basic usage — write a single play-through at default tempo:
    result = write_Track("output.mid", my_track)
    if result:
        print("Wrote output.mid")
    else:
        print("Failed to write output.mid")

2) Twice-played track with higher tempo and verbose output:
    # Plays the track twice (repeat=1 -> 2 iterations), tempo 140 BPM
    success = write_Track("repeat.mid", my_track, bpm=140, repeat=1, verbose=True)
    if not success:
        raise RuntimeError("Failed to persist MIDI")

3) Avoiding accidental empty output:
    # If you don't want to produce an empty file, ensure repeat >= 0 and the track yields content
    if len(list(my_track)) == 0:
        raise ValueError("Track is empty; nothing to write")
    ok = write_Track("nonempty.mid", my_track, repeat=0)
    if not ok:
        print("I/O problem while writing the MIDI file")

4) Error handling for play-time exceptions:
    try:
        write_Track("out.mid", possibly_invalid_track)
    except AttributeError as e:
        # Handle invalid Track-like object (missing attributes, incompatible Bars)
        print("Provided track is incompatible:", e)

## `mingus.midi.midi_file_out.write_Composition` · *function*

## Summary:
Assembles a format-1 MidiFile from a Composition by creating per-track MidiTrack objects (using the provided BPM), invoking per-track serialization the requested number of times (repeat semantics), and writing the resulting .mid file to disk; returns the boolean success flag produced by the file write.

## Description:
This function orchestrates converting a high-level Composition into a persisted MIDI file:
- Creates a new MidiFile instance and constructs one MidiTrack(bpm) for each element in composition.tracks.
- Assigns the list of MidiTrack instances to m.tracks.
- For each iteration while repeat >= 0 (so the loop runs repeat + 1 times when repeat >= 0), calls MidiTrack.play_Track(composition.tracks[i]) for each track index i to append that Track's MIDI events to the corresponding MidiTrack.
- Delegates persistence to MidiFile.write_file(file, verbose) and returns its boolean result.

Known callers / typical usage:
- Used by application-level export routines that persist a Composition to a .mid file. It is the bridge between Composition (container of Track objects) and the MidiFile/MidiTrack serialization layer.

Why this logic is isolated:
- Centralizes the composition-to-file export workflow: construction of MidiTrack objects with consistent BPM, repeat-handling (concatenation of material), and the final write to disk. This prevents duplication of orchestration across different export callers.

## Args:
    file (str | os.PathLike):
        Filesystem path for the output .mid file. Passed directly to MidiFile.write_file which opens the path in binary write mode.
    composition (object):
        Required. A Composition-like object that must expose a public attribute `tracks` which is a sequence (supports len() and indexing via __getitem__). Each element composition.tracks[i] must be compatible with MidiTrack.play_Track:
            - Be a Track-like object that is iterable over Bar-like objects.
            - Provide an attribute `instrument` (and optionally `name`).
        Note: The function indexes composition.tracks (uses len() and composition.tracks[i]) rather than only iterating; supplying a plain iterator without __len__/__getitem__ will raise TypeError/AttributeError.
    bpm (int, optional, default=120):
        Tempo in beats-per-minute forwarded to MidiTrack(bpm). No validation is performed here; typical values are positive integers.
    repeat (int, optional, default=0):
        Controls how many times the composition is processed. The function executes the play loop while repeat >= 0 and decrements repeat each pass. Therefore:
            - repeat = 0 -> the composition is processed once
            - repeat = 1 -> the composition is processed twice (original + 1 repeat)
        If repeat < 0 on entry, the play loop is skipped entirely and no per-track events are produced.
    verbose (bool, optional, default=False):
        Passed to MidiFile.write_file. When True and the file write succeeds, the write method may print a success line.

Interdependencies:
- The exported MIDI content depends on the compatibility of composition.tracks elements with MidiTrack.play_Track and on the BPM value passed to MidiTrack.
- The function assumes composition.tracks is stable (not concurrently modified) between creating the MidiTrack list and invoking play_Track; mutating composition.tracks during execution can cause IndexError.

## Returns:
    bool:
        The boolean result returned by MidiFile.write_file(file, verbose):
            - True: write_file reports success (file opened, bytes written, file closed).
            - False: write_file encountered an open/write error, printed an error message, and returned False.
        Exceptions from assembling MIDI bytes (for example AttributeError raised by MidiTrack.play_Track or MidiFile.get_midi_data()) will propagate and prevent a boolean return.

## Raises:
    AttributeError / TypeError:
        - If composition has no `tracks` attribute, or composition.tracks does not support len() or indexing, accessing len(composition.tracks) or composition.tracks[i] will raise AttributeError or TypeError.
        - If a track object does not expose required attributes or yields Bars incompatible with MidiTrack.play_Track, the invoked play_Track may raise AttributeError (propagated).
    Any exceptions raised by MidiFile.get_midi_data():
        - MidiFile.write_file calls get_midi_data() before performing file I/O; exceptions from assembling the MIDI bytes (e.g., AttributeError, ValueError) will propagate through this function.
    Note on I/O errors:
        - Errors raised by open() or f.write() inside MidiFile.write_file are caught by that method; write_file will return False instead of raising for those error cases.

## Constraints:
Preconditions:
    - composition.tracks must be a sequence (supports len() and indexing) and must not be modified concurrently during this function's execution.
    - Each track in composition.tracks must be compatible with MidiTrack.play_Track (iterable over Bars and provide instrument).
    - bpm should be a value acceptable to the MidiTrack constructor (typical positive integer).

Postconditions:
    - The internally created MidiFile instance `m` will have m.tracks set to a list of newly-created MidiTrack instances, and each MidiTrack will have had play_Track invoked for each processing pass (repeat + 1 times if repeat >= 0).
    - The function does not mutate the provided composition object.
    - On returning True, the file at the given path contains the written MIDI bytes; on False, write_file printed an error and the file may be absent or partially written.

## Side Effects:
    - Filesystem I/O: writes to the specified path via MidiFile.write_file (open, write, close). Any file open/write messages (success or error) are printed by MidiFile.write_file.
    - In-memory mutation: the newly created MidiTrack objects are populated (their track_data bytes are mutated) by calls to play_Track.
    - No mutation of the input composition object is performed by this function.

## Control Flow:
flowchart TD
    Start --> CreateMidiFile[MidiFile()]
    CreateMidiFile --> BuildTrackList[For i in 0..len(composition.tracks)-1: create MidiTrack(bpm)]
    BuildTrackList --> AssignTracks[Assign m.tracks = created list]
    AssignTracks --> RepeatCheck{repeat >= 0 ?}
    RepeatCheck -- No --> Write[Call m.write_file(file, verbose)]
    RepeatCheck -- Yes --> ForEachTrack[For i in 0..len(composition.tracks)-1: m.tracks[i].play_Track(composition.tracks[i])]
    ForEachTrack --> Decrement[repeat = repeat - 1]
    Decrement --> RepeatCheck
    Write --> ReturnResult[return result of m.write_file(file, verbose)]
    ReturnResult --> End

Notes:
- The outer loop executes while repeat >= 0; therefore an initial repeat of N >= 0 results in N+1 total processing passes.
- If an exception occurs during any play_Track call or during MIDI assembly, that exception propagates and the write is not performed.

## Examples:
Typical usage (textual example):
- Ensure you have a Composition-like object where composition.tracks is a list of Track objects, each populated with Bars/Notes and having an instrument.
- Call:
    result = write_Composition("output.mid", composition, bpm=120, repeat=0, verbose=True)
- If result is True, "output.mid" was written successfully. If False, inspect stdout for file I/O error messages. If an exception was raised, check the composition and its tracks for compatibility with MidiTrack.play_Track.

Repeat example (textual):
- To export the composition twice back-to-back, call with repeat=1; the function will process the composition two times (repeat + 1).

