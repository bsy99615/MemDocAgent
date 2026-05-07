# `midi_file_in.py`

## `mingus.midi.midi_file_in.MIDI_to_Composition` · *function*

## Summary:
Creates a MidiFile instance and converts the given MIDI input into a Composition by delegating the work to the MidiFile.MIDI_to_Composition method.

## Description:
This function is a thin module-level convenience wrapper that:
- Instantiates the MidiFile class defined in the same module.
- Calls the instance method MidiFile.MIDI_to_Composition(file) and returns its result.

Known callers within the provided code snapshot:
- No internal callers were found in the provided repository snapshot. This function is intended as a public convenience API for external code to convert MIDI data into mingus.containers.composition.Composition objects (or whatever type MidiFile.MIDI_to_Composition returns).

Why this logic is extracted into a separate function:
- Provides a simple, top-level functional API (MIDI_to_Composition(file)) that hides the MidiFile class instantiation and makes the conversion convenient to call from user code or higher-level utilities.
- Keeps responsibilities separated: the module-level function handles the public-facing call, while MidiFile contains the parsing and conversion logic.

## Args:
    file (object): The MIDI input to convert. This function does not inspect the value; it forwards it to MidiFile.MIDI_to_Composition(file). The exact accepted types and formats (for example: file path string, bytes, or a file-like object) are determined by MidiFile.MIDI_to_Composition and must be consulted there for precise allowed values.

## Returns:
    object: The value returned by MidiFile.MIDI_to_Composition(file). In typical usage this is a mingus.containers.composition.Composition instance created by the MidiFile parser, but the exact return type and structure are determined by the delegated method.

## Raises:
    Any exception raised by MidiFile() construction or by MidiFile.MIDI_to_Composition(file) is propagated to the caller. This function does not catch or translate exceptions.

## Constraints:
Preconditions:
    - The caller must provide a `file` argument acceptable to MidiFile.MIDI_to_Composition (see that method's documentation/implementation for exact preconditions).
    - The environment must be able to construct a MidiFile instance (no special initialization is performed here).

Postconditions:
    - If the function returns normally, it returns exactly the value produced by MidiFile.MIDI_to_Composition(file).
    - No local cleanup or mutation is performed by this wrapper beyond the lifetime of the temporary MidiFile instance (which becomes unreachable after return unless referenced by the returned value).

## Side Effects:
    - This wrapper itself performs no I/O, global state mutation, or external service calls beyond whatever side effects occur within MidiFile.MIDI_to_Composition(file) (for example, reading files or logging) — those side effects are forwarded from the delegated call.

## Control Flow:
flowchart TD
    A[Call MIDI_to_Composition(file)] --> B[Instantiate MidiFile()]
    B --> C[Call m.MIDI_to_Composition(file)]
    C --> D[Return result of delegated call]
    C --> E{Delegated call raises exception}
    E --> F[Exception propagates to caller]

## Examples:
Typical usage (error handling included):

    try:
        comp = MIDI_to_Composition("path/to/song.mid")
    except Exception as e:
        # Handle parse/open errors coming from the underlying MidiFile implementation
        print("Failed to convert MIDI to Composition:", e)
    else:
        # Use the returned object (typically a Composition)
        print("Converted MIDI into composition:", type(comp), comp)

Notes:
- For exact accepted input forms (file path vs. bytes vs. file-like object), specific return value details, and any parsing errors, consult the implementation and documentation of MidiFile.MIDI_to_Composition in this module.

## `mingus.midi.midi_file_in.HeaderError` · *class*

## Summary:
HeaderError is a specialized exception type used to signal problems encountered while parsing or interpreting the header of a MIDI file in the mingus.midi.midi_file_in module.

## Description:
This class exists solely to provide a distinct, catchable exception when the MIDI file header is malformed, missing required fields, uses an unsupported format, or otherwise fails validation during MIDI input parsing. It should be instantiated and raised by the MIDI file input/parser code (the midi_file_in module) at the point where header validation fails so callers can distinguish header-related failures from other parsing or I/O errors.

Typical scenarios for instantiation:
- The MIDI file header chunk is missing or has an unexpected identifier.
- The declared header length or format fields are invalid or inconsistent with the file contents.
- The number of tracks or time-division values are out of acceptable ranges for the parser.

Motivation and responsibility:
- Provides a clear semantic signal specific to header-related parsing errors (rather than using a generic Exception or ValueError).
- Allows calling code to catch and handle header errors differently from other errors (for example, to skip the file, prompt the user, or attempt a fallback parsing strategy).

## State:
This class does not define additional attributes beyond those provided by the base Exception class. Relevant inherited state and invariants:

- args (tuple): Inherited from Exception. Contains the positional arguments passed to the constructor. Common usage is a single string message: HeaderError("reason").
  - Valid values: any tuple of Python objects; typical callers supply a single str describing the problem.
  - Invariant: instance.args is a tuple (possibly empty). str(instance) yields a string representation typically derived from args.

No module-level or class-level attributes are introduced by HeaderError; there are no extra invariants beyond those of Exception.

## Lifecycle:
Creation:
- Instantiate by calling HeaderError() or HeaderError(message, *other_args).
- Required args: none. Recommended: provide a descriptive message (str) as the first argument.

Usage:
- Raise the exception at the point of header validation failure inside the parser:
  raise HeaderError("Human-readable explanation of the header problem")
- Typical handling pattern for client code:
  - Surround MIDI file loading/parsing call with try/except HeaderError to detect header-specific failures.
  - After catching, inspect the exception message through str(exc) or exc.args for diagnostics or user-facing messages.

Destruction / cleanup:
- No special cleanup or context-manager behavior is associated with HeaderError. It follows normal Python exception object lifecycle and requires no explicit destruction.

## Method Map:
flowchart LR
  A[Create HeaderError(message?)] --> B[raise HeaderError]
  B --> C[Exception propagates to caller]
  C --> D{Caller catches HeaderError?}
  D -->|yes| E[Handle header error (log, abort, fallback)]
  D -->|no| F[Unhandled -> propagate further / terminate]

(This diagram describes the typical create -> raise -> catch -> handle flow. There are no HeaderError-specific methods beyond those inherited from Exception.)

## Raises:
- Instantiating HeaderError does not add new exception types; the constructor delegates to Exception.__init__ and will accept any positional arguments. Under normal use it does not raise.
- Typical trigger points where HeaderError is raised (by the parser):
  - Detecting malformed or missing MIDI header fields.
  - Inconsistencies in declared header length, format, or track count.
  - Unsupported header format/version for the parser implementation.

Note: The above are usage-triggered raises (i.e., raised by parser code using HeaderError). The class constructor itself does not intentionally raise exceptions.

## Example:
# Typical use in a MIDI parsing context
try:
    # midi_parser.parse_header(file_like)  # parser code would raise HeaderError on failure
    raise HeaderError("MIDI header chunk missing 'MThd' identifier")
except HeaderError as e:
    print("Failed to read MIDI header:", str(e))
    # handle the malformed-header case: abort, attempt recovery, or notify user

## `mingus.midi.midi_file_in.TimeDivisionError` · *class*

## Summary:
TimeDivisionError is a dedicated Exception subclass used to represent errors or exceptional conditions related to MIDI time division within the MIDI file input processing module.

## Description:
This class exists solely as a distinct exception type so callers and the midi_file_in module can raise or catch errors specifically involving MIDI time division handling. It has no custom behavior beyond normal Exception semantics; it provides a meaningful, type-safe way to signal "time division" problems (for example, an unsupported or malformed time division value) without relying on generic Exception types.

Scenarios for instantiation:
- A MIDI file parser detects a time-division field it cannot interpret and raises this exception to signal that condition to the caller.
- Client code that validates MIDI file metadata may raise this exception when encountering invalid or unsupported time division values.

Note: The source defines the class but does not attach any attributes or custom logic; callers are free to supply an explanatory message when raising it.

## State:
- No instance attributes are defined by this class.
- Inherited state:
  - args (tuple): standard Exception attribute containing any positional arguments passed when instantiated (commonly a single string message).
- Valid values/invariants:
  - There are no class-specific invariants beyond normal Exception invariants (instances are immutable with regard to their class-defined behavior).
  - Any semantic constraints about the time-division value itself (range, format) are enforced by calling code and are not enforced by this class.

## Lifecycle:
- Creation:
  - Instantiate by calling TimeDivisionError([message]) or by raising it directly:
    - raise TimeDivisionError("description of the time-division error")
  - No required constructor arguments; the message is optional and passed to the base Exception.
- Usage:
  - Typical usage is raising the exception at the point of error in MIDI parsing:
    - raise TimeDivisionError("Unsupported time division value: 0")
  - Consumers may catch this specific exception to handle time-division-related errors distinctly:
    - try: ...
      except TimeDivisionError as e: ...
- Destruction:
  - No cleanup responsibilities. Instances follow normal Python exception object lifecycle and are garbage-collected when no longer referenced.

## Method Map:
flowchart TD
    A[Create / raise TimeDivisionError] --> B[Propagate to caller]
    B --> C[Optional: caller catches TimeDivisionError]
    C --> D[Handle error or re-raise]

(There are no methods defined on the class beyond those inherited from Exception.)

## Raises:
- The class definition itself does not raise exceptions.
- Instantiating TimeDivisionError does not raise any new exception; however, raising it with incorrect parameters would follow normal Python rules (e.g., passing unpicklable objects may affect serialization but is unrelated to this class).

## Example:
- Raising the exception in a MIDI parser:
    raise TimeDivisionError("Unsupported time division format: ticks-per-beat value is zero")

- Catching and handling it:
    try:
        parse_midi_file(path)
    except TimeDivisionError as e:
        log.error("MIDI time division error while parsing %s: %s", path, e)
        # fallback, notify user, or abort processing

## `mingus.midi.midi_file_in.FormatError` · *class*

## Summary:
A dedicated exception type defined in mingus.midi.midi_file_in that represents format-related errors; it is a direct subclass of the built-in Exception and adds no extra behavior.

## Description:
This class exists to provide a named, module-scoped exception that callers and the midi parsing code can raise or catch to indicate errors pertaining to MIDI file format or structure. The class definition contains no methods or attributes beyond those inherited from Exception; therefore all behavior follows standard Python Exception semantics.

Notes:
- The source defines the class in the mingus.midi.midi_file_in module. The implementation does not include any parser logic or explicit raising sites in this snippet.
- Use this type when you need to signal or handle format-specific errors distinctly from other exception types (for example, to differentiate format problems from I/O or runtime errors).

## State:
- The class defines no custom instance attributes.
- Inherited attributes (from Exception):
    - args (tuple): the positional arguments passed at construction. Typical use is a single message string but any tuple of values is allowed.
- Valid values and invariants:
    - There are no additional constraints enforced by this class. Any invariants are those of standard Exception objects (e.g., args is a tuple).

## Lifecycle:
- Creation:
    - Constructor signature is the same as Exception: FormatError(*args)
    - Examples:
        - FormatError("Invalid MIDI header")
        - FormatError()  (no arguments)
        - FormatError("msg", {"offset": 128})
    - No required parameters; an empty instantiation is valid.
- Usage:
    - Typical usage is to raise an instance when detecting a format problem:
        - raise FormatError("Unexpected track length")
    - Catching is done as with any exception:
        - try: ... except FormatError as e: ...
    - The class provides no extra methods; callers rely on Exception behavior (stringification, .args).
- Destruction / cleanup:
    - No cleanup methods or context-manager behavior are defined. Exception objects follow normal object lifetime and garbage collection.

## Method Map:
flowchart LR
    A[Create FormatError(*args)] --> B[raise FormatError]
    B --> C[Propagates up stack like any exception]
    C --> D[Caught by except FormatError]
    D --> E[Handle format-specific recovery/logging]

## Raises:
- The class definition itself does not raise exceptions.
- Constructing FormatError(...) follows Exception semantics and does not raise under normal usage.

## Example:
- Raising with a message:
    raise FormatError("Unexpected MIDI header chunk")

- Catching and handling:
    try:
        # call into a MIDI-importing routine (not shown here)
        import_midi("file.mid")
    except FormatError as fe:
        print("MIDI format error:", fe)
        # handle, report, or log the format error

## `mingus.midi.midi_file_in.MidiFile` · *class*

*No documentation generated.*

### `mingus.midi.midi_file_in.MidiFile.MIDI_to_Composition` · *method*

## Summary:
Converts a parsed MIDI file into a mingus Composition (collection of Tracks and Bars), producing a Composition and the tempo in BPM when available; it populates new Track and Bar objects and places Note, instrument and meta information into them, affecting only the returned Composition and newly created Track/Bar/Note objects (no persistent mutation of self).

## Description:
This method is a high-level translator that takes the output of parse_midi_file and builds a mingus Composition representing the musical content of the MIDI file. Known callers and lifecycle:
- Typically invoked by user code or file-loading utilities after obtaining or opening a MIDI file to obtain a mingus Composition representing the file's music.
- Pipeline stage: input parsing → MIDI_to_Composition → further processing/arrangement/export (e.g., playback, editing, or export via other mingus components).

Why this is a separate method:
- The conversion from low-level MIDI events (delta-times, raw event bytes) to mingus containers (Composition, Track, Bar, Note) is a multi-step, logically-cohesive operation that requires many local variables (meter, key, tempo, current bar state). Keeping it as a dedicated method isolates parsing-to-domain-model mapping, improves readability, and allows reuse whenever a parsed MIDI stream must be converted to a Composition.

## Args:
    file (any): Passed through directly to self.parse_midi_file(file). Accepts the same inputs that parse_midi_file accepts (commonly a filesystem path, binary stream, or bytes representing a MIDI file). The method does not inspect or validate the type itself; parse_midi_file performs the actual parsing.

## Returns:
    tuple or Composition:
    - Normal successful case when a tempo meta-event (MPQN) is encountered:
        (Composition, int) — a 2-tuple where the first element is a mingus.containers.composition.Composition instance containing one Track per MIDI track and the second element is bpm (beats per minute) computed from the MIDI MPQN tempo meta-event.
    - Edge / early-return case when the MIDI header indicates 'fps' timing:
        Composition — if header[2]["fps"] is truthy the method prints a message and returns an empty (or partially-populated) Composition directly (no bpm value).
    Notes:
    - If no tempo (MPQN / meta event 0x51) is present in the parsed MIDI events, the function attempts to return (Composition, bpm) but bpm will not have been defined, which will raise an UnboundLocalError (see Raises). This is how the current implementation behaves.

## Raises:
    UnboundLocalError (or NameError equivalent): If no tempo meta-event (meta_event == 81 / 0x51) is encountered for any track, the local variable bpm is never set and returning (Composition, bpm) will raise an UnboundLocalError.
    UnicodeDecodeError: If a track name (meta_event == 3) contains bytes that cannot be decoded with ASCII, decoding event["data"].decode("ascii") may raise UnicodeDecodeError.
    Any exception propagated from self.parse_midi_file(file) or self.bytes_to_int(...) (these are delegated calls and may raise exceptions defined by those implementations).

## State Changes:
Attributes READ:
    - self.parse_midi_file (method): called to obtain header and track data from the provided file
    - self.bytes_to_int (method): called to decode multi-byte integers from meta-event data
Notes: these are method calls on self; no persistent attributes of self are read or modified directly.

Attributes WRITTEN:
    - None on self: the method does not assign or mutate attributes on self. It constructs and returns new Composition, Track, Bar, Note, and MidiInstrument objects and mutates those new objects only.

## Detailed Behavior and Implementation Notes (sufficient to reimplement):
- Call self.parse_midi_file(file). Expect a tuple (header, track_data) where:
    * header[2] is a dictionary with keys "fps" (truthy if SMPTE timing) and "ticks_per_beat" (int).
    * track_data is an iterable (list) of tracks; each track is an iterable of events where each event is a (deltatime, event_dict) pair.
- If header[2]["fps"] is truthy, print "Don't know how to parse this yet" and return a new Composition() immediately (no bpm).
- Use ticks_per_beat = header[2]["ticks_per_beat"] to convert MIDI delta times to musical durations.
- For each MIDI track:
    * Create a new Track() and a new Bar(). Initialize local state:
        - metronome = 1 (a tick per quarter note; used to derive metronome info from meta-event 88)
        - thirtyseconds = 8 (number of 32nd subdivisions in a quarter note; updated from meta-event 88)
        - meter = (4, 4) default time signature
        - key = "C" default key
    * Iterate events in the track:
        - Each event is a tuple (deltatime, event) where event is a dict expected to contain:
            "event" (int) – MIDI event code (e.g., 8 note_off, 9 note_on, 12 program change, 0x0F meta),
            channel, param1, param2 for some events, and for meta events: "meta_event" (int) and "data" (bytes).
        - Compute duration:
            duration = float(deltatime) / (ticks_per_beat * 4.0)
            If duration != 0.0:
                duration = 1.0 / duration
                If the current Bar has entries (b.bar non-empty):
                    - current_length = b.bar[-1][1]  # length of the last placed item
                    - Update that last placed item's stored length to the newly computed duration
                    - If current_length != duration, adjust b.current_beat accordingly:
                        b.current_beat -= 1.0 / current_length
                        b.current_beat += 1.0 / duration
                - Try to place a rest/empty NoteContainer of the computed duration:
                    if not b.place_notes(NoteContainer(), duration):
                        # bar is full or cannot place: add bar to track and start a new bar
                        t + b  # appends b into t (Track.__add__ or Track.__iadd__ semantics)
                        b = Bar(key, meter)
                        b.place_notes(NoteContainer(), duration)
        - Handle event["event"] cases:
            * 8 (note_off): no-op except a special-case if deltatime == 0 (ignored)
            * 9 (note_on):
                - Create a Note with:
                    name = notes.int_to_note(event["param1"] % 12)
                    octave = event["param1"] // 12 - 1
                - Set n.channel = event["channel"] and n.velocity = event["param2"]
                - If the current Bar has entries (b.bar non-empty), add the note into the last item container: b.bar[-1][2] + n (assumes that the tuple/list stored there has a NoteContainer at index 2)
                - Else append the note to the bar: b + n
            * 10 and 11: ignored (no processing)
            * 12 (program change):
                - Create MidiInstrument(), set i.instrument_nr = event["param1"] and assign t.instrument = i
            * 0x0F (meta events): inspect event["meta_event"]:
                - meta_event == 1: ignore
                - meta_event == 3: track name — set t.name = event["data"].decode("ascii")
                - meta_event == 6 or 7 or 47: ignore (no-op)
                - meta_event == 81 (0x51): tempo — compute mpqn = self.bytes_to_int(event["data"]); set bpm = 60000000 // mpqn
                - meta_event == 88 (time signature): parse 4 bytes in event["data"]:
                    d = event["data"]
                    thirtyseconds = self.bytes_to_int(d[3])
                    metronome = self.bytes_to_int(d[2]) / 24.0
                    denom = 2 ** self.bytes_to_int(d[1])
                    numer = self.bytes_to_int(d[0])
                    meter = (numer, denom)
                    b.set_meter(meter)
                - meta_event == 89 (key signature): parse 1+ bytes in event["data"]:
                    d = event["data"]
                    sharps = self.bytes_to_int(d[0])
                    minor = self.bytes_to_int(d[0])  # original code uses same byte for both; retains that behavior
                    if minor: key = "A" else key = "C"
                    Apply sharps/accidentals by shifting key up/down using intervals.major_fourth / major_fifth:
                        for i in range(abs(sharps)):
                            if sharps < 0:
                                key = intervals.major_fourth(key)
                            else:
                                key = intervals.major_fifth(key)
                    b.key = Key(key)
                - Any other meta_event: prints "Unsupported META event", meta_event
            * Any other event["event"] value: prints "Unsupported MIDI event", event
    * After processing all events in the track, append the final bar to the track (t + b) and append the track to the composition (c.tracks.append(t)).
- After processing all tracks, return (c, bpm) (unless the early-return fps case was hit). Note: bpm is only defined if a tempo meta-event (0x51) was encountered; otherwise attempting to return (c, bpm) will fail.

## Constraints:
Preconditions:
    - file must be acceptable to self.parse_midi_file(file). The method does not validate file format itself.
    - The parsed header must be indexable such that header[2]["fps"] and header[2]["ticks_per_beat"] exist.
    - The parsed track_data must be iterable and yield (deltatime, event) pairs where event is a dict with the keys used above.

Postconditions:
    - Returns a Composition containing one Track per parsed MIDI track (each Track contains Bars with Note and rest placements corresponding to input events).
    - If a tempo meta-event is present, the returned tuple includes bpm computed as integer beats-per-minute.
    - The method does not modify attributes on self.

## Side Effects:
    - Writes to stdout via print() in these situations:
        * If header[2]["fps"] is true: prints "Don't know how to parse this yet"
        * For unsupported meta events and unsupported MIDI events: prints diagnostic messages
    - Constructs and mutates new mingus objects (Composition, Track, Bar, Note, MidiInstrument) and returns them; it does not mutate objects passed in or attributes of self.
    - May decode byte strings from meta events with ASCII which can raise UnicodeDecodeError.

### `mingus.midi.midi_file_in.MidiFile.parse_midi_file_header` · *method*

*No documentation generated.*

### `mingus.midi.midi_file_in.MidiFile.bytes_to_int` · *method*

## Summary:
Convert either a bytes object or an integer into a Python int; when given bytes, interpret them as a big-endian unsigned integer.

## Description:
A small utility used throughout the MIDI file parsing logic to normalize numeric values read from the file. It accepts either a raw bytes object (six.binary_type) or an int; bytes are converted to their unsigned integer value via hex decoding.

Known callers and context:
- parse_midi_file_header: converts header fields read from the file (chunk size, format type, number of tracks).
- parse_time_division: converts the 2-byte time division field into an int for further interpretation.
- parse_track_header: converts the 4-byte track chunk size read from the file.
- parse_midi_event: converts single-byte fields (event code, meta-event type) and multi-byte parameters read from the track.
- parse_varbyte_as_int: converts each byte read from the variable-length quantity loop.
- MIDI_to_Composition: used to interpret meta-event data bytes (for example, tempo MPQN, time signature parts, key signature values) when building the Composition.

Why this is a separate method:
- Centralizes the conversion and consistent type-checking for all places that need numeric values from bytes, preventing duplicated binascii + int patterns and providing a single point for error reporting.

## Args:
    _bytes (six.binary_type | int):
        - If six.binary_type: a bytes object representing an unsigned integer in big-endian order (for example, b'\x00\x01' -> 1).
          Note: six.binary_type is imported from six in this module (in Python 3 this is bytes).
        - If int: an integer value already in numeric form; it will be returned unchanged.
        - No default; required.

## Returns:
    int:
        - For bytes input: the non-negative integer represented by the bytes sequence (big-endian).
        - For int input: the identical integer passed in.
        - Large byte sequences return correspondingly large Python ints (arbitrary precision).

## Raises:
    TypeError:
        - If _bytes is neither six.binary_type nor int.
        - Exact message raised by the method: "Unexpected type: %s" % type(_bytes)
    ValueError:
        - If _bytes is a bytes object but its conversion to hex yields an empty string (for example b''), int(binascii.b2a_hex(_bytes), 16) will raise ValueError.
        - This ValueError is not caught inside bytes_to_int and thus will propagate to callers.

## State Changes:
    Attributes READ:
        - None. The method does not access any attributes on self.
    Attributes WRITTEN:
        - None. The method does not modify self.

## Constraints:
    Preconditions:
        - The caller must supply either six.binary_type or int.
        - When supplying bytes, the caller must ensure the bytes represent the intended unsigned big-endian integer.
    Postconditions:
        - Returns an int representing the numeric value of the input; no object state is changed.

## Side Effects:
    - None: there is no I/O, no external calls, and no mutation of objects outside the return value.

### `mingus.midi.midi_file_in.MidiFile.parse_time_division` · *method*

## Summary:
Parse a 2-byte MIDI time-division value (or equivalent int) and return a structured dictionary describing either ticks-per-beat (musical timing) or SMPTE-based frames-per-second timing. This method does not modify object state.

## Description:
Known callers and context:
- parse_midi_file_header: invoked when parsing the 4-byte MIDI header chunk; this method is used to interpret the 2-byte time division field from the header and convert it into a usable timing description for subsequent track/event parsing.
- Any other internal parser routine that needs to interpret a MIDI time-division field before building timing-related structures.

Why this is its own method:
- The MIDI time-division field can represent two distinct schemes (ticks-per-beat or SMPTE-based frame timing) that require bit-level interpretation. Encapsulating that logic in a single method centralizes the bit-masking, validation, and returned data structure so callers receive a normalized representation without duplicating low-level parsing code. It improves readability, testability, and reuse.

## Args:
    bytes (six.binary_type | int):
        - Type: six.binary_type (bytes) or int.
        - If bytes: expected to contain the MIDI time-division field in big-endian order (typically exactly 2 bytes as read from the MIDI header).
        - If int: expected to be the numeric value of the 16-bit time-division field (0 <= int <= 0xFFFF).
        - No default; required.

## Returns:
    dict:
        - If the MSB (0x8000) of the parsed 16-bit value is clear:
            Returns {"fps": False, "ticks_per_beat": n}
            - "ticks_per_beat" is computed as value & 0x7FFF (an integer in range 0..0x7FFF).
        - If the MSB (0x8000) is set (SMPTE-based format):
            Returns {"fps": True, "SMPTE_frames": f, "clock_ticks": c}
            - "SMPTE_frames" is computed as (value & 0x7F00) >> 2 and must be one of [24, 25, 29, 30].
            - "clock_ticks" is computed as (value & 0x00FF) >> 2 (an integer).
        - The returned dict always contains the boolean "fps" key indicating which timing mode was parsed.

## Raises:
    TimeDivisionError:
        - Raised when the parsed SMPTE_frames value (computed as (value & 0x7F00) >> 2) is not one of the accepted frame rates [24, 25, 29, 30].
        - The raised message matches the implementation: "'%d' is not a valid value for the number of SMPTE frames" % SMPTE_frames

    TypeError:
        - May propagate from self.bytes_to_int if the provided bytes argument is not six.binary_type or int.

    ValueError:
        - May propagate from self.bytes_to_int if converting the provided bytes to an integer fails (for example, empty bytes).

## State Changes:
    Attributes READ:
        - None (the method calls self.bytes_to_int but does not read or mutate self.<attr> instance attributes).

    Attributes WRITTEN:
        - None (no instance attributes are modified).

## Constraints:
    Preconditions:
        - Caller should supply a bytes object representing the big-endian 16-bit time-division field (commonly 2 bytes) or an integer in range 0..0xFFFF.
        - The module expects the time-division encoding to follow MIDI file conventions (MSB selects SMPTE mode when set).

    Postconditions:
        - Returns a dictionary describing the timing mode:
            * For musical timing: {"fps": False, "ticks_per_beat": int}
            * For SMPTE timing: {"fps": True, "SMPTE_frames": int (one of 24,25,29,30), "clock_ticks": int}
        - No object state is modified.

## Side Effects:
    - No I/O or external service calls are performed.
    - The method may propagate exceptions raised by self.bytes_to_int (TypeError, ValueError).

### `mingus.midi.midi_file_in.MidiFile.parse_track` · *method*

## Summary:
Parses one MIDI track chunk from the given binary file-like object, returning an ordered list of [delta_time, event] entries. The method advances the file pointer past the track header and its declared data bytes and (indirectly) increments self.bytes_read as bytes are consumed.

## Description:
This method handles the complete parsing of a single MTrk chunk:
1. Read the 4-byte track header and 4-byte chunk size (delegated to parse_track_header).
2. Repeatedly read a variable-length delta-time (parse_varbyte_as_int) and the following MIDI event (parse_midi_event) until the declared number of bytes for this chunk are consumed.
3. Collect each parsed event as a two-element list [delta_time, event] and return the ordered list.

Known callers and lifecycle:
- MidiFile.parse_midi_file calls this method once per track chunk when reading a MIDI file. Higher-level flows such as MIDI_to_Composition obtain parsed tracks by calling parse_midi_file, so parse_track is used during the file-reading/parsing stage.

Why this is a separate method:
- Parsing a track is a self-contained operation (header + a sequence of delta-time/event pairs whose lengths are declared up front). Encapsulating it keeps file-level orchestration (parse_midi_file) separate from low-level parsing and error handling, and allows reuse and clearer testing of track parsing behavior.

## Args:
    fp (file-like object): Binary file-like object positioned at the start of a track chunk header. Must implement read(n) and return bytes. The method will consume:
        - 4 bytes for the track header (should be b"MTrk"),
        - 4 bytes for the chunk size,
        - chunk_size bytes of event data (variable-length delta-times and event bytes).
    No default values.

## Returns:
    list[list[int, dict]]: A list of parsed events in file order. Each element is a two-element list:
        - index 0 (int): delta_time — the delta-time for that event, parsed from a MIDI variable-length quantity (number of ticks since previous event).
        - index 1 (dict): event — the event dictionary produced by parse_midi_event. Possible shapes include:
            * Meta event: {"event": int, "meta_event": int, "data": bytes}
            * Two-parameter events (event types 12 or 13): {"event": int, "channel": int, "param1": int}
            * Regular events (other event types >= 8 and not 12/13): {"event": int, "channel": int, "param1": int, "param2": int}
    Edge cases:
        - On a well-formed track and no exceptions, the method returns all events and the internal chunk counter reaches zero.
        - If the cumulative sizes reported by parse_varbyte_as_int and parse_midi_event exceed the declared chunk_size, the method will print a diagnostic and still return the events parsed so far; chunk_size will be negative in that case.

## Raises:
    HeaderError: If the 4-byte track header is not b"MTrk". (Raised by parse_track_header immediately.)
    IOError: If any required read operation fails (file end-of-file, underlying read error). This can originate from:
        - parse_track_header when reading header/size,
        - parse_varbyte_as_int when reading delta-time bytes,
        - parse_midi_event when reading event type or parameters.
    FormatError: If parse_midi_event detects an invalid MIDI event type or other format violation (for example, event_type < 8). This originates in parse_midi_event.
    TypeError: If an internal bytes-to-int conversion receives an unexpected type (propagated from bytes_to_int).
    Notes:
        - This method does not catch these exceptions; they propagate to the caller.
        - The method itself prints a diagnostic instead of raising when the parsed data consumes more bytes than the declared chunk_size.

## State Changes:
    Attributes READ:
        - self.bytes_read: read when the method prints the diagnostic "yikes." and can be referenced in error messages created by helper methods.
    Attributes WRITTEN:
        - self.bytes_read: incremented by the helper methods called (parse_track_header, parse_varbyte_as_int, parse_midi_event) as they consume bytes from fp. After a successful parse of the track, self.bytes_read has been increased by 8 (header + size) plus the number of bytes read while parsing events.

## Constraints:
    Preconditions:
        - fp must be a binary file-like object with read(n) behavior (returns bytes). It must be positioned at the start of a track chunk (next bytes: b"MTrk" then 4-byte big-endian chunk size).
        - The MidiFile instance should be initialized properly; bytes_read may be nonzero if prior reads occurred and is used for diagnostics and error messages.
        - parse_varbyte_as_int is called with its default behavior (returning both the integer value and the number of bytes consumed).
    Postconditions:
        - If parsing completes without exceptions and the file is well-formed, the file pointer is advanced exactly past the track header (8 bytes) plus the declared chunk_size bytes, and the method returns a list of all events within that chunk.
        - If parsed event lengths exceed the declared chunk_size, the method prints a diagnostic ("yikes.", self.bytes_read, chunk_size) and returns the events parsed; chunk_size will be negative in this case.
        - If an exception is raised during reading, the file pointer may be left at an intermediate location corresponding to the point of failure, and the exception propagates to the caller.

## Side Effects:
    - Reads bytes from fp (I/O) and advances its read position.
    - Triggers increments of self.bytes_read by helper functions as bytes are consumed.
    - May print a diagnostic to standard output if the parsed event bytes exceed the declared chunk size: prints the literal string "yikes.", the current self.bytes_read, and the (negative) chunk_size.
    - No other external I/O, network calls, or global mutations are performed by this method.

## Implementation notes and gotchas:
    - The local name "bytes" is assigned to chunk_size early in the method but never used; this shadows the built-in bytes name and is harmless at runtime but may confuse readers—avoid reproducing this in a new implementation.
    - Correct behavior depends on accurate byte-counting by parse_varbyte_as_int and parse_midi_event; those helpers must return both the parsed value/object and the exact number of bytes they consumed so parse_track can decrement the remaining chunk_size correctly.
    - Typical successful loop invariant: chunk_size is decreased by chunk_delta values until it reaches exactly 0. Any divergence indicates malformed data or a bug in the helpers.
    - Usage example (conceptual):
        - Caller (parse_midi_file) opens the file and, for each track, calls events = self.parse_track(fp). The returned events list is then processed into higher-level structures (e.g., MIDI_to_Composition).

### `mingus.midi.midi_file_in.MidiFile.parse_midi_event` · *method*

## Summary:
Parses a single MIDI event from the current file position and returns a structured event dictionary plus the number of bytes consumed from the stream; updates the parser's bytes_read counter to reflect bytes consumed.

## Description:
This routine is called while iterating through a track's event stream to decode one MIDI event record that follows a delta-time. It reads the event code byte, interprets the event type and channel, then consumes the correct number of following bytes depending on the event kind:

- For meta-events (event type == 0x0F) it reads the meta-type byte, a variable-length quantity (VLQ) length, then that many data bytes.
- For single-parameter events (event types 12 and 13) it reads one parameter byte.
- For all other valid MIDI channel events it reads two parameter bytes.

Known callers / lifecycle stage:
- Invoked from the track parsing loop when processing a track chunk to decode the next event after reading the delta-time for that event. It is intentionally a separate method to encapsulate the byte-level branching logic for different MIDI event formats (meta vs. single-parameter vs. two-parameter) and to centralize updating of parser state (bytes_read).

Why this is a separate method:
- Keeps low-level MIDI event parsing logic isolated and reusable.
- Ensures consistent bookkeeping of consumed bytes and error handling for all event kinds.
- Simplifies higher-level track parsing logic by returning a normalized event representation.

## Args:
    fp (file-like object): Readable binary stream positioned at the event byte.
        - Required method: read(n) -> bytes (or six.binary_type).
        - Caller must position fp to the first byte of the event (i.e., immediately after the delta-time).

## Returns:
    tuple(dict, int):
        - dict: Structured information about the parsed event. Possible keys:
            - "event" (int): event type nibble ((event_code_byte & 0xF0) >> 4).
            - "channel" (int): low 4 bits of the event code byte (present for channel events; absent for meta events).
            - "meta_event" (int): meta-event type byte (only for meta-events, event == 0x0F).
            - "data" (bytes): raw data bytes for meta-events (only for meta-events).
            - "param1" (int): first parameter byte (present for most channel events and single-parameter events).
            - "param2" (int): second parameter byte (present for two-parameter channel events).
        - int: chunk_size — the number of bytes consumed from fp while parsing this event (includes the initial event byte, parameter bytes, VLQ bytes, and meta data bytes).
    Edge cases:
        - Meta-events with length 0 return data as b'' and chunk_size accounts for the VLQ length bytes only.
        - If fp.read returns fewer bytes than requested, callers will receive an IOError (see Raises).

## Raises:
    IOError:
        - "Couldn't read event type and channel data from file."
            - Trigger: the initial fp.read(1) to obtain the event code fails (raises) or returns data that causes bytes_to_int to fail.
        - "Couldn't read meta event from file."
            - Trigger: when parsing a meta-event, failure occurs while reading the meta-event type byte, parsing the VLQ length (parse_varbyte_as_int), or reading the declared data bytes.
        - "Couldn't read MIDI event parameters from file."
            - Trigger: when a channel event requires one or two parameter bytes but fp.read fails while attempting to read them or bytes_to_int fails on the returned data.
        - Note: underlying helper methods (bytes_to_int, parse_varbyte_as_int) can also raise TypeError/ValueError/IOError that will propagate if not caught by those helpers.
    FormatError:
        - Trigger: When the decoded event_type < 8 (i.e., the high nibble of the event code byte indicates an invalid/unknown MIDI event type).
        - Raised with message: "Unknown event type %d. Byte %d." % (event_type, self.bytes_read)
            - event_type is the decoded type (int)
            - self.bytes_read is the current bytes read counter at the time of raising

## State Changes:
    Attributes READ:
        - self.bytes_read: read when used in the FormatError message and used implicitly by parse_varbyte_as_int behavior.
    Attributes WRITTEN:
        - self.bytes_read: incremented to reflect bytes consumed:
            - +1 after reading the initial event code byte.
            - For meta-events: parse_varbyte_as_int will increment self.bytes_read by the VLQ byte count; then this method adds (1 + length) where 1 is the meta-type byte and length is the data length, so net effect increases self.bytes_read by 1 + length in addition to the VLQ increments.
            - For single-parameter events (types 12 or 13): +1 for the single parameter byte.
            - For other channel events: +2 for the two parameter bytes.
        - Note: parse_varbyte_as_int itself updates self.bytes_read for the VLQ bytes; parse_midi_event increments self.bytes_read further for the meta-type and data bytes.

## Constraints:
    Preconditions:
        - fp must be a readable binary stream; calling code must ensure fp is positioned at the start of an event (the byte read by this method is the event code byte).
        - bytes_to_int and parse_varbyte_as_int must be available on self and behave according to their documented contracts (bytes_to_int converts a 1-byte result to int; parse_varbyte_as_int reads VLQ and returns (value, bytes_read)).
    Postconditions:
        - On success: self.bytes_read has been increased by the total number of bytes consumed while parsing this event (including the initial event byte, VLQ bytes, meta-type byte, data bytes, or parameter bytes).
        - The returned chunk_size equals the count of bytes consumed from fp for this event (same accounting as the increments to self.bytes_read performed by this function, except that VLQ byte increments performed inside parse_varbyte_as_int are included in chunk_size via the returned chunk_delta).
        - The returned event dictionary contains exactly the keys appropriate to the event kind as described in Returns.

## Side Effects:
    - Reads from fp (fp.read calls).
    - Mutates self.bytes_read (parser-wide counter).
    - No network I/O or filesystem writes are performed by this method itself.
    - No other attributes of self or external objects are modified.

## Implementation notes (for reimplementation):
    - Read one byte, convert to int with self.bytes_to_int; compute event_type = (ec & 0xF0) >> 4 and channel = ec & 0x0F.
    - Validate event_type >= 8; otherwise raise FormatError with the current self.bytes_read.
    - If event_type == 0x0F (15):
        - Read one byte for meta_event (convert to int).
        - Call self.parse_varbyte_as_int(fp) to obtain (length, chunk_delta); parse_varbyte_as_int will already advance self.bytes_read by chunk_delta.
        - Read exactly length bytes into data (may be b'' if length is 0).
        - Update local chunk_size to include 1 (meta type) + chunk_delta + length, and add 1 + length to self.bytes_read (the VLQ bytes were already accounted by parse_varbyte_as_int).
        - Return ({"event": event_type, "meta_event": meta_event, "data": data}, chunk_size)
    - If event_type in [12, 13]:
        - Read one parameter byte, convert to int, increment chunk_size and self.bytes_read by 1, and return event dict with param1.
    - Else (other channel events):
        - Read two parameter bytes, convert both to int, increment chunk_size and self.bytes_read by 2, and return event dict with param1 and param2.
    - On any read/convert failure, raise the corresponding IOError messages shown above.

### `mingus.midi.midi_file_in.MidiFile.parse_track_header` · *method*

## Summary:
Reads and validates a MIDI track chunk header from a binary file-like object, updates the parser's byte counter for the bytes attempted, and returns the parsed chunk size.

## Description:
This method performs the low-level parsing step that consumes a track chunk header: it attempts to read a 4-byte chunk header tag, verifies it equals the MIDI track tag, then reads the next 4 bytes and converts them to an integer chunk size. The method isolates header/tag validation, byte-count bookkeeping, and error handling so that higher-level track-body parsing can proceed using the returned chunk size.

Call context:
- The code does not enforce who calls this method; it is intended for use by the MIDI file parsing logic at the point where a track chunk header is expected (i.e., immediately prior to reading a track's body).

Why separate:
- Encapsulates the exact sequence and error handling of the two reads (header tag and chunk-size field).
- Centralizes updates to self.bytes_read and the conversion of the size field via self.bytes_to_int.

## Args:
    fp (file-like object): A readable, binary-oriented file-like object (it must implement read(n)). The method calls fp.read(4) twice: once to obtain the 4-byte header tag, then to obtain the 4-byte chunk-size field. The method does not verify that read() returned the requested number of bytes — it only reacts to exceptions or to the header tag value.

## Returns:
    int: The integer chunk size produced by calling self.bytes_to_int on the 4-byte value read for the chunk-size field. The method returns this integer on success.

    Edge cases:
    - If the second read returns fewer than 4 bytes but does not raise, the bytes_to_int call determines the outcome and may raise an exception if it requires exactly 4 bytes. Such exceptions are not caught by this method and will propagate.

## Raises:
    IOError:
        - Raised if an exception is thrown while attempting to read the first 4 bytes (header tag). Message: "Couldn't read track header from file. Byte %d." where %d is the current self.bytes_read value.
        - Raised if an exception is thrown while attempting to read the 4-byte chunk-size field. Message: "Couldn't read track chunk size from file."
    HeaderError:
        - Raised when the 4 bytes read for the header tag are not equal to the ASCII bytes b"MTrk". Message: "Not a valid Track header. Byte %d." where %d is the current self.bytes_read value.
    Any exception raised by self.bytes_to_int:
        - If bytes_to_int fails (for example due to incorrect input length or invalid bytes), that exception will propagate out of this method.

## State Changes:
    Attributes READ:
        - self.bytes_read: Its prior value is read implicitly for use in error messages constructed in the raised exceptions.
    Attributes WRITTEN:
        - self.bytes_read: Incremented by 4 immediately after the first fp.read(4) call (inside the try block) and incremented by 4 again immediately after the second fp.read(4) call. Therefore, on a successful call, self.bytes_read increases by 8. If an exception occurs during the first read, self.bytes_read is not incremented; if an exception occurs during/after the second read, self.bytes_read may already have been incremented by 4.

## Constraints:
    Preconditions:
        - self.bytes_to_int must exist and accept the bytes object returned by the second read; otherwise exceptions may propagate.
        - fp.read must be callable and should not block indefinitely; the method does not enforce a specific mode (text vs binary) but callers should supply a binary-oriented stream consistent with MIDI file bytes.
    Postconditions:
        - On success: self.bytes_read increased by 8 and an integer chunk size (converted via self.bytes_to_int) is returned.
        - On failure: an exception (IOError or HeaderError or payload conversion error) is raised; self.bytes_read may have been incremented by 0 or 4 depending on where the failure occurred.

## Side Effects:
    - Mutates self.bytes_read as described above.
    - Calls self.bytes_to_int to convert the 4-byte chunk-size field; any side effects or exceptions from bytes_to_int propagate.
    - Reads from fp via fp.read(4) twice; no other I/O or external services are used by the method.

### `mingus.midi.midi_file_in.MidiFile.parse_midi_file` · *method*

## Summary:
Parses a MIDI file from disk and returns a tuple containing the parsed header and a list of track event lists; resets the parser byte counter and advances it while reading the file.

## Description:
Known callers:
- MIDI_to_Composition(self, file) — used as the first parsing step in the pipeline that converts raw MIDI on-disk data into mingus container objects (Composition, Track, Bar, Note, etc.). MIDI_to_Composition immediately calls this method to obtain the file header and per-track event lists before transforming them into container objects.

Role and rationale:
- This method encapsulates the high-level flow of opening a MIDI file, delegating header parsing and per-track parsing to dedicated helper methods (parse_midi_file_header and parse_track), and assembling their results into a single (header, tracks) return value.
- Keeping this logic in a single method centralizes file-level I/O, initialization of parser state (self.bytes_read), and the loop over tracks; it avoids duplicating file-open/close and track-iteration logic in multiple callers.

## Args:
    file (str or os.PathLike): Path to the MIDI file on disk. Must be readable by the running process.

## Returns:
    tuple:
        header: (int, int, dict) — the header object returned by parse_midi_file_header, expected to be a 3-tuple:
            * format_type (int): MIDI format (0, 1, or 2).
            * number_of_tracks (int): number of MTrk tracks declared in the header.
            * time_division (dict): time-division info as returned by parse_time_division (e.g., {"fps": False, "ticks_per_beat": N} or SMPTE variants).
          Note: parse_midi_file_header may return False for malformed headers; this method assumes a header tuple and will raise a runtime error if header is not indexable.
        result: list[list[list]] — a list with one element per track; each track is a list of events where each event is a two-element list [delta_time, event]:
            * delta_time (int): elapsed ticks since previous event (value returned by parse_varbyte_as_int).
            * event (dict): event dictionary produced by parse_midi_event. Typical shapes:
                - Meta-event: {"event": 15, "meta_event": <int>, "data": <bytes>}
                - Program/Aftertouch (12/13): {"event": 12|13, "channel": <int>, "param1": <int>}
                - Most other channel events: {"event": <int>, "channel": <int>, "param1": <int>, "param2": <int>}

    If the MIDI header declares zero tracks, result will be an empty list.

## Raises:
    IOError("File not found"):
        - If the file cannot be opened for reading (open(file, "rb") fails).

    Any exceptions raised by helper/parser methods invoked while reading:
        - parse_midi_file_header(fp) may raise:
            * IOError(...) for read failures,
            * HeaderError(...) if header magic is invalid,
            * FormatError(...) for invalid format values or unsupported chunk sizes.
        - parse_track(fp) / parse_track_header(fp) / parse_midi_event(fp) / parse_varbyte_as_int(fp) may raise:
            * IOError(...) for read failures,
            * HeaderError(...) for invalid track headers,
            * FormatError(...) for unknown MIDI event types or malformed data,
            * TypeError from bytes_to_int(...) if unexpected types are encountered.
    Notes on exception propagation:
        - Exceptions from parse_midi_file_header or the per-track parsing are not caught here and propagate to the caller.
        - If any of these exceptions is raised before the method reaches f.close(), the file handle is not explicitly closed by this method (i.e., file closure is only performed on the normal, non-exceptional path).

## State Changes:
Attributes READ:
    - None directly read-only in this method (it immediately resets bytes_read and defers file byte accounting to called parsers).

Attributes WRITTEN:
    - self.bytes_read: set to 0 at method start; subsequently incremented by parse_midi_file_header and parse_track (and nested parsers) as bytes are read.
    - No other self.<attr> fields are modified directly by this method.

## Constraints:
Preconditions:
    - file must be a valid path to a readable file.
    - The file should contain a valid MIDI file header; parse_midi_file_header is expected to return a 3-tuple (format_type, number_of_tracks, time_division). If parse_midi_file_header returns False (e.g., for a malformed header with chunk_size < 6), this method will attempt to index header[1] and will raise an exception (TypeError), so callers should expect header validity.

Postconditions:
    - On successful completion (no exceptions), the returned tuple (header, result) contains:
        * header as returned by parse_midi_file_header,
        * result is a list with length equal to header[1] (declared number of tracks); each element is the event list returned by parse_track for the corresponding track.
    - The file opened inside this method is closed (f.close()) on normal completion.
    - self.bytes_read reflects the total bytes the parser observed while reading header and track chunks (as updated by helper methods).

## Side Effects:
    - Opens the file at the provided path for binary reading; reads bytes from disk; closes the file on the normal execution path.
    - No writes to disk, no network or external service calls.
    - Mutates parser state via self.bytes_read (and any other internal counters updated by nested parser methods).
    - Because exceptions from nested parsers are propagated, callers must handle file-related and parse-related errors; also, in exceptional cases the file descriptor may remain open if an error occurs before f.close() is reached.

### `mingus.midi.midi_file_in.MidiFile.parse_varbyte_as_int` · *method*

## Summary:
Read a MIDI variable-length quantity (VLQ) from the provided file-like object and return its integer value; optionally also return the number of bytes consumed. Advances the file pointer and updates the object's cumulative bytes_read counter.

## Description:
This method implements the standard MIDI variable-length quantity (VLQ) decoding loop. It is called while parsing MIDI track data to read:
- delta-times in parse_track (used to compute event timing), and
- length fields for META events in parse_midi_event (to know how many data bytes to read).

Lifecycle / call context:
- Invoked repeatedly during MIDI file parsing when the parser expects a VLQ at the current file position (for example, immediately before an event or before reading meta-event data).
- It runs during the parsing phase of reading a MIDI file (parse_midi_file -> parse_track -> parse_varbyte_as_int).

Why a separate method:
- The VLQ decoding logic is non-trivial, used in multiple places (delta-times, meta-event lengths), and needs to report both the decoded integer and how many bytes were consumed. Encapsulating it avoids duplication and centralizes error handling and the self.bytes_read accounting.

## Args:
    fp (file-like object):
        - A readable file-like object supporting read(n) -> bytes (for example a file opened in 'rb' mode).
        - Precondition: the fp must be positioned at the first byte of the VLQ to decode.
    return_bytes_read (bool, default=True):
        - If True (default): return a tuple (value, bytes_consumed).
        - If False: return only the integer value.

## Returns:
    If return_bytes_read is False:
        int
            - The integer value decoded from the VLQ.
    If return_bytes_read is True:
        tuple (int, int)
            - (value, bytes_consumed)
            - value: decoded non-negative integer represented by the variable-length quantity.
            - bytes_consumed: number of bytes read from fp to decode the value (>=1).

Edge-case return behavior:
- The method never returns partial results on read failure; instead it raises IOError (see Raises).
- A VLQ of zero will return 0 with bytes_consumed at least 1 (if the file contained a single zero byte).

## Raises:
    IOError:
        - Raised with message "Couldn't read variable length byte from file." if any read or conversion during the VLQ loop fails.
        - This includes EOF (fp.read(1) returning an empty bytes object) or bytes_to_int raising TypeError/ValueError when given the read value. The method catches any exception from the read/convert step and converts it into this IOError.

## State Changes:
    Attributes READ:
        - self.bytes_read (read as part of the read-modify-write when incrementing)
    Attributes WRITTEN:
        - self.bytes_read (incremented by the number of bytes successfully read while decoding the VLQ)

Additionally:
    - The fp file pointer is advanced by bytes_consumed bytes (side effect on the external object).

## Constraints:
    Preconditions:
        - fp must be readable (support read(1)) and positioned at a valid VLQ start.
        - return_bytes_read must be a boolean (the method treats truthiness; non-bools will behave like booleans).
    Postconditions:
        - On successful return, fp has been advanced by N bytes where N is bytes_consumed.
        - self.bytes_read has been incremented by the same N.
        - The returned integer equals the VLQ value decoded by concatenating the lower 7 bits of each read byte, in order, where each byte with the MSB=1 indicates continuation and the final byte has MSB=0.

## Algorithm / Behavior details:
    - Initialize an accumulator result = 0 and counter bytes_read = 0.
    - Read bytes one at a time from fp.
    - For each byte b:
        - Convert b to an int via self.bytes_to_int(b).
        - Increment self.bytes_read by 1.
        - If the byte's MSB (0x80) is set, add the low 7 bits (b & 0x7F) to result after left-shifting result by 7 bits, and continue loop.
        - If the MSB is clear, add the full byte value to result after left-shifting result by 7 bits, break the loop.
    - Return either result or (result, bytes_read) based on return_bytes_read.

## Side Effects:
    - Reads from fp (I/O): advances the file pointer by the number of bytes consumed.
    - Mutates the caller object's self.bytes_read by incrementing it for every byte read.
    - No external network or filesystem writes occur, and no other object attributes are mutated.

