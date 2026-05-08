# `midi_track.py`

## `mingus.midi.midi_track.MidiTrack` · *class*

*No documentation generated.*

### `mingus.midi.midi_track.MidiTrack.__init__` · *method*

## Summary:
Initializes a new MidiTrack instance by allocating an empty track byte buffer and recording the initial tempo into the object's state and encoded track data.

## Description:
Known callers and context:
- Typical callers: library users or higher-level MIDI builders that create new tracks (e.g., when constructing a new MIDI file or adding a track to a song).
- Lifecycle stage: invoked when a MidiTrack object is constructed; it prepares the track for subsequent event encoding by establishing an initial tempo meta-event.
- Interaction with other methods: calls the instance method set_tempo(start_bpm) to both update the object's bpm field and append the corresponding MIDI tempo meta-event bytes to self.track_data.

Why this logic is a separate method:
- The actual encoding and placement of the tempo meta-event is handled by set_tempo so that tempo-setting logic is reused elsewhere (for in-track tempo changes) and all tempo-related state updates and byte-encoding are centralized. __init__ only performs minimal construction and delegates tempo-specific work to that method to avoid duplicating encoding logic.

## Args:
    start_bpm (int, optional): Starting tempo in beats per minute. Defaults to 120.
        - Allowed values: positive, non-zero integers typical for musical BPM (e.g., 40–300).
        - Note: No type coercion or strict validation is performed here; invalid values are forwarded to set_tempo and may cause exceptions.

## Returns:
    None

## Raises:
    ZeroDivisionError: If start_bpm == 0. This exception is raised by the underlying tempo encoding logic invoked by set_tempo (microseconds-per-quarter-note computation divides by bpm).
    Any exception raised by set_tempo or its helper functions (for example TypeError, ValueError, or exceptions from encoding functions) will propagate out of __init__ unchanged.

## State Changes:
Attributes READ:
    self.delta_time  (read indirectly by set_tempo when composing the tempo meta-event; may be required by the encoder)
Attributes WRITTEN:
    self.track_data  (initialized to an empty bytes object b"" here, then extended by set_tempo with the tempo meta-event bytes)
    self.bpm         (set to start_bpm by the call to set_tempo)

## Constraints:
Preconditions:
    - The class must provide a working set_tempo method and any helpers it relies on (e.g., set_tempo_event). These are invoked during initialization.
    - start_bpm should be a non-zero positive integer to avoid division-by-zero and to produce a valid MIDI tempo.

Postconditions (on successful return):
    - self.bpm == start_bpm
    - self.track_data begins as an empty bytes buffer and, after set_tempo completes, ends with the encoded tempo meta-event corresponding to start_bpm (the tempo event is appended at the current delta_time).
    - No external I/O has occurred; only the object's in-memory fields are updated.

## Side Effects:
    - Mutates only the newly constructed MidiTrack instance (initializes/overwrites self.track_data and sets self.bpm).
    - No file, network, or other external side effects.
    - Any exception raised during set_tempo prevents the object from completing initialization normally (the partially-initialized object may be left in memory if the exception propagates).

### `mingus.midi.midi_track.MidiTrack.end_of_track` · *method*

## Summary:
Returns the 3-byte MIDI "End of Track" meta-event preceded by a zero delta-time byte, leaving the MidiTrack object's state unchanged.

## Description:
Known callers and contexts:
- header(): called to compute the track chunk size (uses len(self.end_of_track()) when building the TRACK_HEADER).
- get_midi_data(): called when assembling the final track bytes; result is appended to track_data to terminate the track.
- Any external code that needs the canonical byte sequence that marks the end of a MIDI track before writing or streaming the track chunk.

Lifecycle stage:
- Invoked during track finalization when computing header size and when producing the final byte sequence for a MIDI track. It represents the final meta-event that must be present in every MIDI track chunk before writing the file.

Why this is a separate method:
- Centralizes the canonical End-of-Track byte sequence in one place so callers use a single authoritative representation; avoids duplication of literal bytes in multiple places and makes future changes (if any) trivial.

## Args:
- None

## Returns:
- bytes: Always returns the 4-byte sequence b"\x00\xff\x2f\x00".
  - Meaning of each byte:
    - 0x00: delta-time = 0
    - 0xFF: meta-event status byte
    - 0x2F: meta-event type = End of Track
    - 0x00: length = 0 (no payload)
  - Edge cases: none — the return value is constant and independent of object state.

## Raises:
- None — this method performs no checks and raises no exceptions.

## State Changes:
- Attributes READ: None (does not read any self.<attr> fields)
- Attributes WRITTEN: None (does not modify any self.<attr> fields)

## Constraints:
- Preconditions: None — can be called at any time; no required object state.
- Postconditions: No changes to the MidiTrack instance; caller receives the fixed End-of-Track byte sequence to use when finalizing a track.

## Side Effects:
- None — no I/O, no external service calls, and no mutations of objects outside self.

### `mingus.midi.midi_track.MidiTrack.play_Note` · *method*

## Summary:
Appends a MIDI Note On event (transposed up one octave) for the given note to the track buffer; if a pending instrument change is flagged, it first emits the instrument selection events and clears that flag.

## Description:
This method is called while converting higher-level musical objects into raw MIDI bytes stored in the MidiTrack instance. Typical callers and lifecycle stage:
- play_NoteContainer: emits events for all notes in a container; play_Note handles each individual note.
- play_Bar: when a bar's content requires emitting notes, it delegates to play_NoteContainer which calls this method.
- play_Track: while iterating bars of a track, play_Track → play_Bar → play_NoteContainer → play_Note produces Note On events.

Separation rationale:
- The method centralizes validation, optional instrument selection, and the exact byte-level emission sequence for a single Note On event. This keeps higher-level timing/structure logic separate from event emission.

## Args:
    note (object):
        - Expected protocol (duck-typed interface), required:
            * note.channel (int): MIDI channel number. Should be an integer in 0..15.
            * note.velocity (int): Note-on velocity. Must be an integer in 0..127 inclusive.
            * int(note) -> int: Converting the object to int yields the base MIDI note number (0..127).
        - No default; passing None or an object missing these attributes will raise an error.
        - Behavior: this method will compute the emitted MIDI note as int(note) + 12 (transposes the input up one octave).

## Returns:
    None
    - The method does not return a value. Its effect is to mutate self.track_data (and possibly self.change_instrument).

## Raises:
    AssertionError:
        - If velocity is outside 0..0x7F (127): raised directly by the assertion in this method.
        - If channel or transposed note violate midi_event constraints (checked in midi_event invoked via note_on). Concretely, midi_event asserts:
            * 0 <= channel < 16
            * 0 <= param1 <= 0x7F  (param1 is the transposed note number)
          Violations will raise AssertionError from midi_event.
    AttributeError:
        - If the passed note does not have the required attributes (channel or velocity), accessing note.channel or note.velocity will raise AttributeError.
    TypeError:
        - If note.channel, note.velocity, or int(note) are not convertible to integers (e.g., non-integer types without appropriate __int__), operations may raise TypeError.

## State Changes:
    Attributes READ:
        - self.change_instrument (bool): checked to determine if set_instrument should be invoked.
        - self.instrument (int): read when set_instrument is called.

    Attributes WRITTEN:
        - self.change_instrument (bool): set to False if it was True at invocation (clears the pending change).
        - self.track_data (bytes): appended with bytes for:
            * optionally: bank select and program change events (emitted by set_instrument(channel, self.instrument)),
            * the Note On event returned by self.note_on(channel, int(note) + 12, velocity).

## Constraints:
    Preconditions:
        - note implements the described protocol (channel, velocity, int conversion).
        - velocity in 0..127 inclusive.
        - channel in 0..15 inclusive.
        - int(note) + 12 must be within 0..127 inclusive (so int(note) must be in -12..115) to satisfy midi_event parameter bounds.

    Postconditions:
        - self.track_data contains the new bytes appended in order:
            1) If self.change_instrument was True: bytes emitted by set_instrument(channel, self.instrument) (which appends a bank select controller event and a program change event).
            2) The Note On event for (int(note) + 12) on the given channel with the given velocity (as produced by note_on).
        - If self.change_instrument was True at the start, it will be False after return.
        - No other attributes of the MidiTrack instance are modified.

## Side Effects:
    - Mutates in-memory state only (self.track_data and possibly self.change_instrument). No file, network, or external I/O.
    - Calls:
        * self.set_instrument(channel, self.instrument) when self.change_instrument is True — this method appends a bank select (controller) and a program change event to self.track_data.
        * self.note_on(channel, transposed_note, velocity) to produce the Note On bytes appended to self.track_data.
    - Any assertion failures will raise AssertionError and leave self.track_data unmodified by the failing step (exceptions propagate immediately).

## Implementation notes for reimplementation:
    - Implement the method to:
        1) Read channel = note.channel and velocity = note.velocity.
        2) If self.change_instrument is truthy:
            a) call self.set_instrument(channel, self.instrument) to append instrument selection events,
            b) set self.change_instrument = False.
        3) Assert 0 <= velocity <= 0x7F.
        4) Compute midi_note = int(note) + 12.
        5) Append the bytes returned by self.note_on(channel, midi_note, velocity) to self.track_data.
    - Ensure midi_event / note_on called by this method enforce the MIDI bounds for channel and midi_note (0..15 for channel, 0..127 for note).

### `mingus.midi.midi_track.MidiTrack.play_NoteContainer` · *method*

## Summary:
Appends MIDI "note on" events for every note in the given container to this track's internal data; when the container represents a chord (more than one note) the first note uses the current delta-time and all subsequent notes are emitted with a zero delta-time so they occur simultaneously.

## Description:
Known callers and context:
- Called by MidiTrack.play_Bar when rendering the notes of a Bar (play_Bar passes the Bar element's note container). That occurs while building a track's MIDI event stream during track rendering (the play_Track → play_Bar → play_NoteContainer pipeline).
- Can also be invoked directly by external code that has a sequence-like "note container" and wants to append its notes to the current track.

Why this logic is a separate method:
- The method centralizes the logic required to render a container of notes as either a single note or a chord (simultaneous notes). It encapsulates the delta-time adjustment needed so that when multiple notes are part of the same musical event only the first uses the existing delta-time and the rest are emitted with zero delta-time. Centralizing this avoids duplicating that delta-time handling in callers.

## Args:
    notecontainer (sequence): A sequence-like container of note-like objects. Requirements for each element:
        - Must be indexable/iterable and the container must support len() and indexing (used as notecontainer[0] and notecontainer[1:]).
        - Each element must support:
            - attribute `channel` (int): MIDI channel (expected 0..15).
            - attribute `velocity` (int): 0..127 (0x00..0x7F).
            - integer conversion via int(element) yielding the note number (an integer that, after any internal transposition, must be within MIDI note value constraints when used by underlying methods).
    No default allowed; must be provided.

## Returns:
    None

## Raises:
    AssertionError:
        - If a note's velocity is outside 0..127, raised by play_Note's assertion.
        - If an underlying MIDI event assertion fails (for example, invalid channel, event-type or parameter ranges) these will surface as AssertionError from midi_event / note_on.
    TypeError / AttributeError:
        - If elements in notecontainer do not expose the required attributes (channel, velocity) or cannot be converted to int, Python will raise TypeError or AttributeError accordingly.
    (These exceptions are raised by the helper methods invoked; this method does not itself perform additional explicit range checks.)

## State Changes:
Attributes READ (directly or via invoked helpers):
    - self.delta_time (read implicitly when building each note_on event for the first note)
    - self.change_instrument (read by play_Note)
    - self.instrument (read by play_Note if change_instrument True)
Attributes WRITTEN (directly or via invoked helpers):
    - self.track_data (appended with note_on bytes for each note; may also receive bank/program-change or tempo/meta events if invoked helper methods do so)
    - self.delta_time (set to zero by set_deltatime(0) when notecontainer has more than one note)
    - self.change_instrument (may be modified to False by play_Note if an instrument-change was applied)
Other fields indirectly affected:
    - Any other fields modified by play_Note or set_instrument (e.g., additional event bytes appended to track_data).

## Constraints:
Preconditions:
    - notecontainer must be a sequence-like object (supporting len(), indexing and iteration).
    - Each element must be a note-like object with attributes and behavior described in Args.
    - The caller should ensure note/channel/velocity values are sensible for MIDI (channels 0–15, velocities 0–127). If not, assertions in helper methods will fail.

Postconditions:
    - For an empty container: no changes to track_data or delta_time.
    - For a single-element container: that element's note_on event is appended to self.track_data and self.delta_time is left unchanged.
    - For a multi-element container: the first element's note_on event is appended using the pre-call delta_time; self.delta_time is set to the varbyte encoding of 0 (b'\x00') and the remaining elements' note_on events are appended using that zero delta-time so they are simultaneous with the first. The final value of self.delta_time after the call will be the encoding for zero when len(notecontainer) > 1.
    - No return value is produced.

## Side Effects:
    - Mutates self.track_data by appending binary MIDI events (note_on events for each element). Because play_Note may trigger an instrument change, additional events (bank select, program change) may also be appended.
    - Mutates self.delta_time (set to the variable-byte representation of 0 when emitting chords of two or more notes).
    - No I/O (file, network) is performed by this method itself; it only mutates in-memory track state.

### `mingus.midi.midi_track.MidiTrack.play_Bar` · *method*

## Summary:
Converts a single Bar-like object into MIDI bytes appended to this track, emitting time-signature, key, tempo (when present), note-on and note-off events, and updating internal timing state (delta_time, delay, and bpm).

## Description:
This method translates one Bar into low-level MIDI events and appends them to self.track_data. Known caller:
- MidiTrack.play_Track: iterates over Track bars and calls play_Bar for each bar during MIDI export/construction.

Lifecycle/context:
- Called during MIDI file construction after track-level setup (e.g., track name, instrument) has been applied.
- Isolated because it encapsulates bar-level concerns: inserting meter/key meta-events, handling rests via delay accumulation, applying tempo changes that occur inside the bar, and sequencing note on/off pairs for each time-slice.

Operational sequence (explicit):
1. set_deltatime(self.delay) — the current accumulated delay (from previous trailing rests) is applied so the upcoming time-signature event is placed after prior rests.
2. self.delay = 0 — clear the accumulated delay since it has been applied.
3. set_meter(bar.meter) — emits the time-signature meta-event using the delta_time set above.
4. set_deltatime(0) — ensure the next meta-event (key) uses zero delta time relative to the time-signature event.
5. set_key(bar.key) — emits the key-signature meta-event.
6. For each slice x in bar:
   - Compute tick = int(round((1.0 / x[1]) * 288)) (288 ticks per whole note).
   - If x[2] is None or len(x[2]) == 0: accumulate a rest by adding tick to self.delay.
   - Else (there is a NoteContainer-like object):
     a. set_deltatime(self.delay) — apply accumulated rest before these notes.
     b. self.delay = 0
     c. If the NoteContainer has a bpm attribute: set_deltatime(0) then set_tempo(x[2].bpm) to emit an immediate tempo meta-event.
     d. play_NoteContainer(x[2]) — emits note-on events for notes in the container.
     e. set_deltatime(self.int_to_varbyte(tick)) — set delta_time for the slice duration before note-offs.
     f. stop_NoteContainer(x[2]) — emits note-off events for the container.

Why separate:
- Keeps bar-level timing semantics and meta-event insertion isolated from track and note-level helpers; simplifies reading and testing of bar-to-MIDI translation.

## Args:
    bar (Bar-like object):
        - Required attributes:
            * meter (tuple[int,int]): (numerator, denominator), e.g., (4, 4).
            * key (str or mingus.core.keys.Key): key signature or Key instance.
        - Iterability: iter(bar) must yield slice-tuples x of length >= 3 where:
            * x[0]: reserved/unused by play_Bar (present in Bar slice structure).
            * x[1]: int > 0 — denominator representing note length (e.g., 4 for quarter note).
            * x[2]: None, empty sequence, or a NoteContainer-like object.
                - NoteContainer-like requirements:
                    - Supports len() and iteration.
                    - When non-empty, contains Note-like objects acceptable to play_Note/stop_Note.
                    - Optionally has a numeric attribute bpm to indicate an immediate tempo change for that slice.

## Returns:
    None

## Raises:
    ZeroDivisionError:
        - If any slice x has x[1] == 0 (division by zero when computing tick).
    TypeError:
        - If x[2] is not None but does not support len() or iteration (len() or iter() will raise).
    AttributeError / ValueError:
        - If bar lacks required attributes (meter, key) or key value is not acceptable to set_key/key_signature_event.
    AssertionError:
        - May be raised indirectly by play_Note/stop_Note if contained Note objects violate their assertions (e.g., invalid velocity or channel).

## State Changes:
Attributes READ:
    - self.delay: read to set the delta_time before emitting events.
    - (indirectly) x[2].bpm via hasattr to detect tempo changes.

Attributes WRITTEN / MUTATED:
    - self.delta_time: updated via calls to set_deltatime throughout the method (affects subsequent emitted event bytes).
    - self.delay: reset to 0 when applied; incremented when encountering rests.
    - self.track_data: appended to by set_meter, set_key, set_tempo, play_NoteContainer, stop_NoteContainer, and other helper methods invoked here.
    - self.bpm: updated by set_tempo when a NoteContainer provides a bpm attribute.

## Constraints:
Preconditions:
    - bar.meter must be a two-integer tuple with a positive denominator that is a power of two (as expected by time signature logic).
    - For each slice x: x must be indexable and x[1] must be a positive integer.
    - int_to_varbyte must accept the computed tick value (non-negative integer) and return a bytes object suitable for set_deltatime.
Postconditions:
    - All events for the bar have been appended to self.track_data in chronological order (with delta-time bytes set appropriately).
    - self.delay contains the accumulated tick count of any trailing rests remaining after processing the bar (0 if the bar ended on notes).
    - self.bpm reflects the last tempo set inside the bar (unchanged if no bpm attribute encountered).

## Side Effects:
    - Appends MIDI meta- and channel-event bytes to self.track_data (no file or network I/O).
    - Mutates in-memory state (self.delta_time, self.delay, self.track_data, and possibly self.bpm).
    - Calls helper methods (set_deltatime, set_meter, set_key, set_tempo, play_NoteContainer, stop_NoteContainer, int_to_varbyte) that rely on and further mutate track state.

## Examples / Illustrative behavior (prose):
    - If the bar begins with a rest slice of quarter-note length (x[1] == 4), that slice contributes 72 ticks (288/4) to self.delay; when the next non-rest slice arrives the accumulated delay is emitted as the delta-time immediately preceding that slice's note-on events.
    - If a NoteContainer within a slice has a bpm attribute, a tempo meta-event is emitted with delta-time 0 immediately before playing the container's notes.

### `mingus.midi.midi_track.MidiTrack.play_Track` · *method*

## Summary:
Translate a Track-like object into MIDI events appended to this MidiTrack by applying optional track metadata (name and instrument hints), resetting per-track delay, and invoking play_Bar for every Bar in the track. This method mutates the MidiTrack's internal MIDI state (notably delay, change_instrument, instrument, and track_data via called helpers).

## Description:
This public method accepts a Track-like object and processes it into the MidiTrack's internal byte stream by:
- If the track has a name attribute, invoking set_track_name(track.name) to append a track-name meta-event.
- Resetting this MidiTrack's per-track delay counter to zero.
- Reading track.instrument and, if that instrument object exposes instrument_nr, setting flags so a program change will occur on the next note (change_instrument=True and instrument assigned).
- Iterating over the track (for bar in track) and delegating bar-level processing to play_Bar(bar).

Known callers:
- None identified inside the provided file; this is a public instance method expected to be called by code that converts higher-level Track objects into MidiTrack instances prior to serializing MIDI data.

Why this is a separate method:
- It encapsulates track-scoped orchestration (name, instrument hint, per-track delay reset, bar iteration) while delegating detailed timing, meter, key, and note handling to play_Bar and lower-level helpers. Keeping orchestration separate prevents duplication of track-level setup across other code paths.

Minimal usage example:
    m = MidiTrack()
    # track is any Track-like iterable of Bar-like objects with .instrument and optional .name
    m.play_Track(track)
    data = m.get_midi_data()

## Args:
    track (object): Required. A Track-like object that must:
        - Be iterable (yields Bar-like objects).
        - Provide an attribute 'instrument' (accessed unguarded: track.instrument).
        - Optionally provide 'name' (if present, passed to set_track_name).
      The method does not validate types beyond attribute checks / iteration; callers must supply compatible objects.

## Returns:
    None — the method performs in-place mutation of this MidiTrack instance.

## Raises:
    AttributeError:
        - If track does not have an 'instrument' attribute, direct access to track.instrument will raise AttributeError.
        - If Bars yielded by track are incompatible with play_Bar, play_Bar may raise AttributeError (propagated).
    UnicodeEncodeError:
        - If track.name is present but contains characters that cannot be encoded to ASCII when set_track_name calls name.encode('ascii'), UnicodeEncodeError will be raised.
    Any exception raised by called methods (set_track_name, play_Bar, and their downstream helpers such as set_tempo, play_NoteContainer, etc.) will propagate.

## State Changes:
Attributes READ:
    - None of this MidiTrack instance's attributes are read by play_Track.

Attributes WRITTEN (direct):
    - self.delay: set to 0 at the start of processing.
    - self.change_instrument: set to True if track.instrument has attribute instrument_nr.
    - self.instrument: set to instr.instrument_nr when instrument_nr exists on track.instrument.

Attributes WRITTEN (indirect, via invoked methods):
    - self.track_data: appended-to by self.set_track_name and by events produced while processing each Bar (via play_Bar and its callees).
    - self.delta_time, self.bpm and other MIDI-related state: may be modified by play_Bar and nested helpers (set_deltatime, set_tempo, set_meter, set_key, play_Note*, stop_Note*, etc.).

## Constraints:
Preconditions:
    - track must be iterable and yield Bar-like objects compatible with self.play_Bar.
    - track must expose an 'instrument' attribute; the method does not guard against its absence.
    - If present, track.name should be a str (or object with .encode) encodable to ASCII to avoid UnicodeEncodeError.
    - If instrument.instrument_nr is present it should be an integer appropriate for MIDI program numbers; this method only stores it and relies on play_Note and set_instrument to handle emission.

Postconditions:
    - self.delay is 0 immediately after this method sets it (though play_Bar may alter it during iteration; at the very start self.delay is assigned 0).
    - If track.instrument has attribute instrument_nr:
        - self.change_instrument == True and self.instrument == instr.instrument_nr (so the next play_Note call will emit a program change before the note).
      If instrument.instrument_nr is absent:
        - self.change_instrument and self.instrument are unchanged except for the explicit assignment above (i.e., no instrument change is scheduled).
    - The MidiTrack's track_data contains the track-name meta-event if track.name existed, and all MIDI events produced by processing each Bar.

## Side Effects:
    - Mutates this MidiTrack instance (appends bytes to track_data, updates delta_time, bpm, etc., via nested calls).
    - Does not perform file or network I/O.
    - Does not mutate the provided track object (reads attributes and iterates it only).
    - Exceptions from nested calls propagate to the caller.

### `mingus.midi.midi_track.MidiTrack.stop_Note` · *method*

*No documentation generated.*

### `mingus.midi.midi_track.MidiTrack.stop_NoteContainer` · *method*

## Summary:
Stops (emits MIDI note-off events for) every Note in the provided container and updates the track's timing so that, for multi-note containers, the first note-off keeps the current delta-time and all subsequent note-offs are emitted with a zero delta-time (simultaneous subsequent offs). Mutates the track's MIDI data and, in the multi-note case, the current delta-time.

## Description:
This method is used while rendering a track to MIDI bytes to terminate sounding notes contained in a NoteContainer (an ordered collection of Note-like objects). Known callers and context:
    - MidiTrack.play_Bar: Called after emitting corresponding note-on events and advancing time for a note's duration; invoked at the end of a note's lifetime to emit its note-off events.
    - Indirectly part of the rendering pipeline invoked by MidiTrack.play_Track -> play_Bar.

Why this is a separate method:
    - The logic mirrors play_NoteContainer and centralizes the subtle timing behavior required for multi-note containers (emit first note-off with the current delta-time, then set delta-time to zero for simultaneous subsequent note-offs). Keeping this logic in a dedicated method avoids duplication and ensures consistent delta-time handling for both play and stop paths.

## Args:
    notecontainer (Sequence[Note]-like): A sized iterable (supports len() and iteration) of Note-like objects. Each element must:
        - expose .channel (int, expected 0..15)
        - expose .velocity (int, expected 0..127)
        - support int(element) to obtain the MIDI note number (the implementation uses int(note) + 12 when composing the MIDI event)

    Notes:
        - The method requires that len(notecontainer) be valid (i.e., notecontainer implements __len__).
        - An empty container is allowed and results in no emitted events.

## Returns:
    None (implicit). The method's purpose is to append MIDI note-off bytes to self.track_data and update self.delta_time as a side effect.

## Raises:
    - TypeError: If notecontainer does not support len() or is not iterable.
    - AttributeError: If an element in notecontainer lacks the required attributes or int() behavior (missing .channel, .velocity, or __int__).
    - AssertionError: Propagates from lower-level MIDI helpers (midi_event) when MIDI parameter ranges are violated, for example:
        * if note.channel is not in 0..15
        * if note.velocity is not in 0..127
        * if int(note) + 12 is not in 0..127
      These assertions occur during composition of the MIDI event and are not caught here.

## State Changes:
Attributes READ:
    - None directly. (The method itself does not read any self.<attr> fields directly; it delegates to other methods.)

Attributes WRITTEN:
    - self.track_data: appended with one note-off MIDI event per Note in notecontainer (order preserved).
    - self.delta_time: set to the varbyte representation of 0 (b'\x00') when len(notecontainer) > 1 via self.set_deltatime(0). When len(notecontainer) <= 1, self.delta_time is not modified by this method.

## Constraints:
Preconditions:
    - self must be a properly-initialized MidiTrack.
    - notecontainer must implement __len__ and be iterable.
    - Each element of notecontainer must be a Note-like object as described in Args.

Postconditions:
    - For each element in notecontainer, a corresponding note-off MIDI event has been appended to self.track_data in the same order.
    - If len(notecontainer) > 1:
        - The first note-off is emitted using the delta-time that was current at the time of the call.
        - self.delta_time is set to the varbyte encoding of 0 (b'\x00') before emitting the second and subsequent note-offs, so those events record zero delta-time (simultaneous with the first note-off).
    - If len(notecontainer) <= 1:
        - No change to self.delta_time is performed by this method; the single note-off uses the current delta-time.

## Side Effects:
    - Mutates self.track_data by appending MIDI note-off event bytes for each Note in notecontainer.
    - Mutates self.delta_time to b'\x00' when notecontainer contains more than one note.
    - No I/O or external service calls are performed.
    - The method uses list comprehensions for iteration and side-effects; the temporary lists returned by those comprehensions are discarded immediately.

### `mingus.midi.midi_track.MidiTrack.set_instrument` · *method*

## Summary:
Appends a bank-select controller event followed by a program-change event to this track's MIDI data, causing the channel's instrument (and bank) to change when the MIDI is played.

## Description:
Known callers and context:
- play_Note: invoked during playback when the track requests an instrument change before emitting a note (play_Note checks change_instrument and calls set_instrument).
- play_Track: indirectly triggers calls to set_instrument by setting change_instrument and instrument on the MidiTrack; the actual call occurs later in play_Note before the first note.
- External callers: can be used directly by code constructing or modifying MidiTrack contents to set a channel's instrument and bank.

Why this is a separate method:
- Changing an instrument in MIDI requires two related events in sequence (bank select via a controller event, then a program change). This method encapsulates that two-step sequence, ensures consistent ordering, and centralizes the logic that builds and appends the required MIDI event bytes to track_data rather than duplicating the sequence at each call site.

## Args:
    channel (int): MIDI channel number. Required range: 0 <= channel <= 15.
    instr (int): Program (instrument) number. Required range: 0 <= instr <= 127.
    bank (int, optional): Bank select value sent as a controller parameter. Required range: 0 <= bank <= 127. Default: 1

Notes on types:
- All three arguments must be integers. Passing non-integers will either fail the internal numeric comparisons or produce an AssertionError/TypeError.

## Returns:
    None

The method appends bytes to self.track_data and does not return a value.

## Raises:
    AssertionError: if the underlying midi_event/controller_event argument assertions fail, specifically:
        - if channel is not an integer in 0..15
        - if instr (program number) is not in 0..127
        - if bank (controller value) is not in 0..127
    TypeError: if arguments are of incompatible types for the numeric comparisons performed by midi_event/controller_event (for example, passing None or a non-numeric object).
    AttributeError: if select_bank or program_change_event methods are missing on the instance (not the case in the provided class implementation).

## State Changes:
    Attributes READ:
        self.delta_time
            - Both select_bank and program_change_event call midi_event, which prefixes the returned bytes with the current self.delta_time. Thus the current delta_time affects the bytes appended.
    Attributes WRITTEN:
        self.track_data
            - Two byte sequences are appended (bank-select controller event bytes, then program-change event bytes). The method mutates track_data in-place via concatenation.

## Constraints:
    Preconditions:
        - self.track_data must be an initialized bytes-like object (the class __init__ ensures this).
        - channel must be an integer in [0, 15].
        - instr must be an integer in [0, 127].
        - bank must be an integer in [0, 127].
    Postconditions:
        - After calling, self.track_data ends with the bytes returned by select_bank(channel, bank) followed by the bytes returned by program_change_event(channel, instr).
        - self.delta_time is unchanged by this method.
        - No return value; method completes without error when argument ranges and types are valid.

## Side Effects:
    - No I/O or external service calls.
    - Mutates only the MidiTrack instance's in-memory state (self.track_data).
    - Both appended events include the current self.delta_time value as a prefix; if the caller expects only the first of multiple consecutive events to carry the delta-time, the caller must set self.delta_time appropriately between events (e.g., set to zero after the first event).

### `mingus.midi.midi_track.MidiTrack.header` · *method*

## Summary:
Constructs and returns the MIDI track chunk header bytes by concatenating TRACK_HEADER with a chunk-size byte sequence derived from formatting the track body length with "%08x" and converting that hex string to bytes via a2b_hex. The method is read-only and does not modify the object.

## Description:
Known callers and context:
- MidiTrack.get_midi_data calls this method when assembling the complete track bytes for file serialization; get_midi_data returns header() + track_data + end_of_track().
- Any code that needs the serialized bytes for a single MIDI track (via get_midi_data or similar) will indirectly depend on this header being correct.
- This method is invoked during the final stage of MIDI track assembly (serialization), not during incremental event construction.

Why this is a separate method:
- Centralizes the low-level MIDI chunk-header construction and chunk-size calculation in one place so higher-level assembly code can remain simple and avoid duplicating formatting/encoding logic.
- Isolates the details of how the chunk-size is encoded (string formatting + a2b_hex) making the behavior easier to test and update.

## Args:
None.

## Returns:
bytes
- The returned value equals TRACK_HEADER + chunk_size.
- chunk_size is produced by: a2b_hex("%08x" % (len(self.track_data) + len(self.end_of_track()))).
  - The format string "%08x" zero-pads the hexadecimal representation of the integer to at least 8 hex digits.
  - For integer lengths in the range 0 .. 0xFFFFFFFF, the formatted hex string has exactly eight hex digits and chunk_size is 4 bytes representing the big-endian 32-bit length.
  - For larger integer lengths (> 0xFFFFFFFF) the formatted hex string will contain more than eight hex digits; chunk_size will then be longer than 4 bytes (or may cause an error — see Raises).
- Example (typical empty track using this class implementation): with self.track_data == b"" and end_of_track() returning b"\x00\xff\x2f\x00" (4 bytes), the computed integer length is 4, "%08x" produces "00000004", a2b_hex yields b"\x00\x00\x00\x04", and the method returns TRACK_HEADER + b"\x00\x00\x00\x04".

## Raises:
- binascii.Error: If a2b_hex is passed an odd-length hex string. Although "%08x" produces at least eight hex digits, lengths that require more than eight hex digits can produce strings with odd-length (e.g., a 9-hex-digit value like "100000000"), which will cause a2b_hex to raise an error such as "Odd-length string".
- TypeError: If TRACK_HEADER is not a bytes-like object or if self.track_data / self.end_of_track() are not bytes, concatenating TRACK_HEADER + chunk_size may raise TypeError.

## State Changes:
Attributes READ:
- self.track_data (used to compute the length of the track body)
- self.end_of_track() is invoked (reads whatever state that method uses; in this class it returns a fixed bytes sequence)

Attributes WRITTEN:
- None. This method does not modify any attributes of the object.

## Constraints:
Preconditions:
- self.track_data must be a bytes-like object (so len(self.track_data) yields the byte length).
- self.end_of_track() must return bytes (the class implementation returns b"\x00\xff\x2f\x00").
- TRACK_HEADER (from mingus.midi.midi_events) must be a bytes object for the concatenation to succeed.
- For standard MIDI chunk semantics and to avoid a2b_hex errors, the combined body length (len(self.track_data) + len(self.end_of_track())) should be representable within 32 bits (<= 0xFFFFFFFF). Under this condition, chunk_size will be exactly 4 bytes.

Postconditions:
- No object attributes are changed.
- The returned bytes begin with TRACK_HEADER and are followed by the chunk_size bytes intended to equal the length of the subsequent track body (track_data + end_of_track()).

## Side Effects:
- None. The method performs no I/O, does not call external services, and does not mutate external objects; it only reads object state and returns a newly created bytes object.

### `mingus.midi.midi_track.MidiTrack.get_midi_data` · *method*

## Summary:
Returns the complete serialized bytes for this single MIDI track by concatenating the track header, the accumulated track event data, and the end-of-track marker. Does not modify object attributes.

## Description:
This method produces a single track chunk suitable for inclusion in a MIDI file by calling the track's header generation, appending the current track_data (the binary event stream built by other methods on this object), and then appending the standard end-of-track meta-event.

Known callers and lifecycle stage:
- MidiFile.get_midi_data and consumers that serialize or write MIDI files invoke this method when assembling the full file. Typical lifecycle: after building or populating a MidiTrack via play_*/set_* methods (which append bytes into self.track_data), call get_midi_data to obtain the final bytes for writing to disk, sending over a network, or embedding in another container.
- External code that needs the serialized bytes for a specific track (for testing or inspection) may call this method.

Why this logic is a separate method:
- Serializing a track (header + body + terminator) is a distinct responsibility from building track events; keeping it separate centralizes format-specific concatenation and avoids duplicating header/terminator assembly throughout the codebase.
- header() calculates the chunk size based on the current track_data and end_of_track(), so assembling the final chunk in one place guarantees size consistency.

## Args:
This method takes no arguments (only self).

## Returns:
bytes: A bytes object containing:
    - The track chunk header (as returned by self.header()).
    - The current track body (self.track_data), which is the sequence of MIDI events and meta-events previously appended by the track's methods.
    - The end-of-track marker (as returned by self.end_of_track()).
Edge cases:
    - If self.track_data is empty (b""), the method still returns a valid track chunk consisting of a header and an end-of-track marker.
    - The header() implementation computes the chunk size using the current length of self.track_data plus the terminator size, so the returned header will correctly reflect the bytes returned by this method when track_data is unchanged during the call.

## Raises:
This method does not explicitly raise exceptions itself. It may propagate exceptions raised by:
    - header() or end_of_track() if those methods raise.
    - TypeError from attempting to concatenate non-bytes (for example, if self.track_data is not a bytes-like object).
    - Any other exception raised while computing the header or concatenating bytes.

## State Changes:
Attributes READ:
    - self.track_data: read and included in the returned bytes.
    - self.header() (method call): invoked to produce the track header bytes (which internally reads track-related properties to compute chunk size).
    - self.end_of_track() (method call): invoked to produce the standard terminator bytes.

Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.track_data should be a bytes object (or bytes-like) representing the accumulated MIDI events for this track.
    - header() and end_of_track() must be defined and return bytes-compatible values.
    - The caller should not mutate self.track_data concurrently during this call; concurrent mutation would make the header's computed size potentially inconsistent with the final concatenation.

Postconditions:
    - Returns a bytes object that is a complete, self-contained MIDI track chunk (header + body + terminator).
    - Leaves the MidiTrack instance unchanged (no attributes are modified).

## Side Effects:
    - No I/O is performed.
    - No external services are contacted.
    - The only observable actions are the calls to header() and end_of_track(); if those methods have side effects (they do not in the current implementation), those side effects would occur as part of this call.

### `mingus.midi.midi_track.MidiTrack.midi_event` · *method*

## Summary:
Constructs a MIDI channel/voice event byte sequence (delta-time prefix + status byte + 1 or 2 data bytes) and returns it without mutating the track; used to build low-level MIDI messages appended to the track data.

## Description:
This method is the low-level builder for MIDI channel (voice/real-time) events. It is called by higher-level helpers that represent specific MIDI messages (for example, note_on, note_off, controller_event, program_change_event) and by methods that construct instruments and playback actions (e.g., set_instrument, select_bank, play_Note, stop_Note). It is invoked during track assembly when the MidiTrack instance is converting musical objects (notes, controllers, program changes) into the raw bytes that make up a MIDI file track.

Separating this logic into its own method centralizes:
- Validation of the numeric ranges for event type, channel and parameters
- Construction of the MIDI status byte from event type and channel
- Packaging of the variable-length delta-time prefix with the message bytes

This avoids duplicating status-byte construction and range checks across multiple message-specific methods.

## Args:
    event_type (int): MIDI event type nibble (0 <= event_type < 16). This becomes the high 4 bits of the status byte.
    channel (int): MIDI channel (0 <= channel < 16). This becomes the low 4 bits of the status byte.
    param1 (int): First data byte (0 <= param1 <= 0x7F). Typical meanings: note number, controller number, program number, etc.
    param2 (int or None, optional): Second data byte when required by the event (0 <= param2 <= 0x7F). If None, the event is encoded with only one data byte. Defaults to None.

Parameter types must be integers (or types that behave like ints when used in integer operations). Values outside the documented ranges trigger an assertion failure.

## Returns:
    bytes: A bytes object composed of:
        - self.delta_time (bytes): a variable-length delta-time prefix previously set on the MidiTrack (defaults to b'\x00' if not changed),
        - one status byte: (event_type << 4) | channel,
        - one or two data bytes: param1 and optionally param2.

Possible lengths:
    - len(self.delta_time) + 2 when param2 is None (delta + status + 1 data byte)
    - len(self.delta_time) + 3 when param2 is provided (delta + status + 2 data bytes)

Edge cases:
    - If self.delta_time is the default b'\x00' or a multi-byte varlen encoding produced by int_to_varbyte, it is concatenated unchanged.
    - No on-the-fly conversion of non-integer params is performed; callers should pass ints.

## Raises:
    AssertionError: If any argument violates the allowed ranges:
        - event_type < 0 or event_type >= 16
        - channel < 0 or channel >= 16
        - param1 < 0 or param1 > 0x7F
        - param2 is not None and (param2 < 0 or param2 > 0x7F)
    TypeError: May occur if arguments are of types that cannot be used to form bytes([...]) (e.g., non-integer objects that cannot be converted to ints), though the implementation relies on callers to provide ints.

## State Changes:
    Attributes READ:
        - self.delta_time: read and prefixed to the returned bytes (expected to be a bytes object holding a variable-length MIDI delta-time).
    Attributes WRITTEN:
        - None. This method does not modify any MidiTrack attributes; it only returns the constructed bytes.

## Constraints:
    Preconditions:
        - self.delta_time must be a bytes instance representing a valid MIDI variable-length delta-time (the class provides set_deltatime and int_to_varbyte for this).
        - event_type, channel, param1, param2 (if provided) must be integers within the ranges documented above.
    Postconditions:
        - The returned value is a bytes object that begins with the exact bytes of self.delta_time followed by a single status byte and one or two data bytes.
        - No attribute on self is modified by this call.

## Side Effects:
    - None external: there is no I/O, no file or network access, and no mutation of objects outside self.
    - Typical usage appends the returned bytes to self.track_data (callers such as note_on/note_off do this), but this method itself does not perform the append.

### `mingus.midi.midi_track.MidiTrack.note_off` · *method*

## Summary:
Constructs and returns the MIDI bytes for a Note-Off channel event using the track's current delta-time prefix; does not modify MidiTrack state.

## Description:
This is a thin, semantic wrapper that builds a MIDI Note-Off (channel voice) message by delegating to the internal midi_event builder. It is invoked during track assembly when a previously-playing note is to be stopped and the resulting bytes appended to the track data.

Known callers and contexts:
    - MidiTrack.stop_Note: called when stopping a single Note object; the returned bytes are appended to self.track_data.
    - MidiTrack.stop_NoteContainer: used indirectly when stopping multiple notes in a container (it calls stop_Note for each note).
    - Other external code may call this directly when constructing raw MIDI events for a track.

Why this is a separate method:
    - Provides a clear, expressive API for creating Note-Off messages (improves readability compared to calling midi_event with raw constants everywhere).
    - Encapsulates the semantic intent (note off) while reusing the centralized validation and byte-construction logic in midi_event.

## Args:
    channel (int): MIDI channel index. Allowed range: 0 <= channel < 16.
    note (int): MIDI note number. Allowed range: 0 <= note <= 127 (0x7F).
    velocity (int): Release velocity. Allowed range: 0 <= velocity <= 127 (0x7F).

## Returns:
    bytes: A bytes object containing:
        - the current self.delta_time prefix (variable-length MIDI delta-time),
        - one status byte encoding the NOTE_OFF event type combined with the channel,
        - two data bytes: note and velocity.

    Notes:
        - Because velocity is provided, the returned message always contains two data bytes after the status byte, so the returned length is len(self.delta_time) + 3.
        - The exact binary contents depend on the value of the NOTE_OFF constant (imported from mingus.midi.midi_events) and the current self.delta_time.

## Raises:
    AssertionError: If any numeric argument violates midi_event's range checks:
        - channel is not in [0, 15]
        - note is not in [0, 127]
        - velocity is not in [0, 127]
    TypeError: If non-integer-like arguments are supplied such that bytes([...]) cannot be constructed (e.g., passing objects that cannot be converted to integers). The implementation relies on callers to pass ints.

## State Changes:
    Attributes READ:
        - self.delta_time: read and prefixed to the returned bytes.
    Attributes WRITTEN:
        - None. This method does not modify any attributes on the MidiTrack instance.

## Constraints:
    Preconditions:
        - self.delta_time should be a bytes object containing a valid MIDI variable-length delta-time encoding (use set_deltatime or int_to_varbyte to set it).
        - channel, note, velocity must be integers within the ranges documented above.

    Postconditions:
        - The MidiTrack instance is left unchanged.
        - The returned bytes represent a syntactically-correct MIDI Note-Off channel event (delta-time + status + note + velocity).

## Side Effects:
    - No I/O, no network access, and no mutation of objects outside self.
    - Typical usage appends the returned bytes to self.track_data (callers such as stop_Note perform that append), but this method itself only constructs and returns the bytes.

### `mingus.midi.midi_track.MidiTrack.note_on` · *method*

## Summary:
Builds and returns the raw MIDI bytes that represent a "note on" channel event (delta-time prefix + status byte + note and velocity) without mutating the track; intended to be appended to the track's byte stream to start a sounding note.

## Description:
Known callers and contexts:
    - play_Note: called when converting a Note object into MIDI bytes during track assembly; play_Note converts the musical note to a MIDI note number (int(note) + 12) and appends the returned bytes to self.track_data.
    - play_NoteContainer / play_Bar / play_Track: indirectly call note_on through play_Note while iterating containers/bars/tracks to build an entire track's bytes.
    - External code may call note_on directly when manually constructing MIDI messages for a track.

Why this is a separate method:
    - Encapsulates the mapping of the high-level "note on" concept to the low-level MIDI event encoding.
    - Keeps callers concise and delegates validation + byte construction to the shared midi_event implementation (status byte composition, delta-time prefix, and parameter-range checks).
    - Prevents duplication: multiple message types (note_on, note_off, controller_event, program_change_event) share midi_event logic, so note_on is a small, expressive wrapper.

## Args:
    channel (int): MIDI channel index (0 <= channel <= 15). This occupies the low 4 bits of the status byte.
    note (int): MIDI note number (0 <= note <= 127). Typical values are 0..127; musical callers may add an octave offset (e.g., play_Note adds +12).
    velocity (int): Note on velocity (0 <= velocity <= 127). Velocity 0 is commonly interpreted as note-off in some MIDI contexts, but this method encodes it as a NOTE_ON with velocity 0.

No default values — all three arguments are required.

## Returns:
    bytes: A bytes object composed of:
        - the current self.delta_time prefix (a variable-length MIDI delta-time encoding, often b'\x00' if no delay),
        - one status byte: (NOTE_ON << 4) | channel,
        - two data bytes: note and velocity.

Length: len(self.delta_time) + 3 bytes (delta + status + note + velocity).

Edge-case returns:
    - If self.delta_time encodes a multi-byte variable-length value, that sequence appears unchanged at the start of the returned bytes.
    - The method never returns None.

## Raises:
    AssertionError: Raised indirectly by midi_event when any numeric argument is outside its valid range:
        - if channel < 0 or channel >= 16
        - if note < 0 or note > 0x7F (127)
        - if velocity < 0 or velocity > 0x7F (127)
    TypeError or ValueError: May be raised by underlying operations (e.g., building bytes from non-integer values) if non-integer types or otherwise invalid objects are passed; the implementation expects integers.

## State Changes:
    Attributes READ:
        - self.delta_time (bytes): read by midi_event and prefixed to the returned bytes.
    Attributes WRITTEN:
        - None. This method does not modify any MidiTrack attributes. Typical callers append the returned bytes to self.track_data, but the append is performed by the caller (e.g., play_Note), not by note_on itself.

## Constraints:
    Preconditions:
        - self.delta_time should be a bytes instance containing a valid MIDI variable-length delta-time (use set_deltatime or int_to_varbyte to set it).
        - channel, note, and velocity must be integers within their documented ranges.
    Postconditions:
        - The returned bytes begin exactly with the bytes in self.delta_time, followed by one status byte (with the NOTE_ON nibble and the provided channel), and then two data bytes: the note and the velocity.
        - No attribute on self is changed by calling this method.

## Side Effects:
    - No I/O, no file or network access.
    - No mutation of objects outside self by this method itself.
    - Conventional side effect for callers: the returned bytes are normally appended to self.track_data by the caller to include the event in the track's byte stream. This append is performed outside this method (e.g., play_Note does: self.track_data += self.note_on(...)).

### `mingus.midi.midi_track.MidiTrack.controller_event` · *method*

## Summary:
Creates and returns a MIDI Controller event message (bytes) for this track by delegating to the generic MIDI event encoder; does not modify the track state.

## Description:
This method is a thin convenience wrapper that produces a controller-type MIDI event by calling the track's generic midi_event encoder with the CONTROLLER event type. It is used while assembling track data during MIDI generation whenever a controller message (for example, bank select) must be emitted.

Known callers and contexts:
- select_bank(channel, bank) — directly calls this method to emit a bank select controller message when changing instrument banks.
- set_instrument(channel, instr, bank) — calls select_bank(...) before program change when an instrument/bank change is required.
- play_Note(...) — may indirectly cause a controller_event to be emitted via set_instrument when change_instrument is set on the track.
These calls occur during track/score rendering (track construction) — i.e., when generating the sequence of MIDI bytes that represent a track.

Why this is a separate method:
- Encapsulates the event-type constant (CONTROLLER) so callers supply only controller-specific parameters (controller number and value) and the channel.
- Avoids duplicating the event-type argument at every call site and provides a clearer, intention-revealing API for emitting controller events.

## Args:
    channel (int):
        MIDI channel number (0–15). Corresponds to the lower 4 bits of the status byte.
    contr_nr (int):
        Controller number (0–127). Encoded as the first data byte of the controller message.
    contr_val (int or None):
        Controller value (0–127) encoded as the second data byte. If None is passed, the resulting MIDI message will contain only one data byte (some controller messages may be valid with a single parameter).

## Returns:
    bytes:
        A bytes object representing the MIDI event. Structure:
        - Prefix: self.delta_time (variable-length delta time bytes as stored on the track).
        - Status byte: (CONTROLLER << 4) | channel
        - Data bytes: contr_nr followed (if contr_val is not None) by contr_val
        Example layout: delta_time + [status_byte, contr_nr, contr_val]
        Edge cases:
        - If contr_val is None, returned bytes contain only one data byte (contr_nr).
        - The returned bytes are not appended to self.track_data by this method; callers must append them where appropriate.

## Raises:
    AssertionError:
        - If channel is outside the range 0..15.
        - If contr_nr is outside the range 0..127.
        - If contr_val is not None and is outside the range 0..127.
        These checks originate from the delegated midi_event method's assertions.
    TypeError/Other:
        - If provided arguments are of incompatible types (e.g., non-integer types that do not support the integer comparisons used by the assertions), Python may raise TypeError during the checks or when forming byte values.

## State Changes:
    Attributes READ:
        - self.delta_time : read to prefix the returned event with the current delta time bytes.
    Attributes WRITTEN:
        - None. This method does not modify any attributes (it only returns a bytes object).

## Constraints:
    Preconditions:
        - self.delta_time must be a bytes-like object (the MidiTrack uses bytes for delta_time); typically initialized to b"\x00" or set via set_deltatime.
        - The track instance must be a properly-initialized MidiTrack (so that CONTROLLER and midi_event are defined and valid).
        - Caller must ensure numeric argument ranges described above to avoid AssertionError.
    Postconditions:
        - No change to the MidiTrack instance state.
        - The caller receives a bytes object representing the controller MIDI event ready to be appended to track_data.

## Side Effects:
    - No I/O or external service calls.
    - Does not mutate objects outside self.
    - Does not append to self.track_data; callers are responsible for appending the returned bytes to the track's data stream when desired.

### `mingus.midi.midi_track.MidiTrack.reset` · *method*

## Summary:
Resets the track's in-memory MIDI data for reuse by clearing all accumulated track bytes and restoring the delta-time buffer to a single zero byte.

## Description:
This method zeroes the mutable state that represents the MIDI track's serialized content so the MidiTrack instance can be reused to build or write a fresh track. No external resources are accessed.

Known callers and lifecycle context:
- No specific callers are provided in the supplied source. Typically, this method is invoked:
  - After writing or exporting a track to disk or a stream, when the same MidiTrack instance should be reused to construct a new track.
  - Before beginning to append events to a newly-created track object if a reset/reuse path is required by higher-level code.
- It exists as a separate method to centralize and document the two-step reset operation (clearing accumulated bytes and reinitializing the delta-time buffer). Keeping this logic in a single place avoids duplication and makes reuse and testing straightforward.

Why this is a dedicated method:
- Clearing both the track data buffer and the delta-time buffer is an atomic semantic operation for reinitializing a MidiTrack instance. Encapsulating it avoids subtle bugs where one field might be reset but the other not, and makes intent explicit.

## Args:
- None

## Returns:
- None (implicitly returns None). The method's effect is entirely on the object's state.

## Raises:
- None. This implementation does not raise exceptions. It performs simple attribute assignments and assumes the caller provides a valid MidiTrack instance (self).

## State Changes:
- Attributes READ:
  - None (the method does not read prior attribute values).
- Attributes WRITTEN:
  - self.track_data: set to an empty bytes object (b"").
  - self.delta_time: set to a single zero byte (b"\x00").

## Constraints:
- Preconditions:
  - self must be a MidiTrack instance (or an object that supports assignment to .track_data and .delta_time).
  - No assumptions are made about previous values of these attributes.
- Postconditions:
  - After the call, self.track_data equals b"".
  - After the call, self.delta_time equals b"\x00".
  - No other attributes are modified.

## Side Effects:
- No I/O, network, or external service interactions.
- Only mutates the two attributes on the instance (see "Attributes WRITTEN").
- Safe to call repeatedly; repeated calls will produce the same postconditions.

## Implementation notes for reimplementation:
- Use byte strings for the fields to match typical MIDI byte-buffer handling in Python 3.
- The reset operation should be performed via direct assignment (no in-place mutation required).
- Keep the two assignments together so the operation remains atomic from a readability/maintainability perspective.

### `mingus.midi.midi_track.MidiTrack.set_deltatime` · *method*

## Summary:
Sets the delta-time prefix used for the next MIDI event on the track object; accepts an integer (which is encoded to VLQ bytes) or a pre-encoded bytes value and stores it to self.delta_time.

## Description:
This method is invoked during MIDI track construction whenever the code needs to set the time delay that will prefix the next event emitted into track_data. It centralizes conversion from an integer tick count to the MIDI variable-length quantity (VLQ) format so event-producing methods can supply either raw integers or already-encoded bytes.

Known direct callers within this class:
- play_NoteContainer — sets delta-time to 0 between simultaneous notes or to an encoded tick value when scheduling subsequent notes.
- play_Bar — sets delta-time before writing bar-level events and when scheduling notes or tempo/meter/key changes.
- stop_NoteContainer — sets delta-time when sequencing note-off events for containers.

This logic is a separate method so that: (1) integer → VLQ conversion is implemented in one place (via int_to_varbyte), (2) callers remain concise, and (3) representation of delta_time on the object is uniform.

## Args:
    delta_time (int or bytes):
        - If int: a non-negative integer tick count which will be encoded to VLQ bytes using int_to_varbyte.
            - Allowed range: integer >= 0. For MIDI-conformant values prefer <= 0x0FFFFFFF (fits in up to 4 VLQ bytes).
        - If bytes: the value is taken as-is and stored directly into self.delta_time. The method does not validate that the bytes are a correct VLQ.
        - The parameter is required.

## Returns:
    None — the method only updates object state (self.delta_time) and does not return a value.

## Raises:
    - The method itself contains no explicit raise statements.
    - Indirect exceptions may propagate from int_to_varbyte when delta_time is an int:
        - TypeError: if the provided value is of an incompatible type for numeric operations used by int_to_varbyte.
        - struct.error: if struct.pack inside int_to_varbyte receives invalid arguments (unlikely for valid non-negative integers).
    - If a non-bytes non-int is supplied (for example, a str), no exception is raised here but later attempts to concatenate self.delta_time with bytes (when building track_data) will raise a TypeError.

## State Changes:
    Attributes READ:
        - None (this method does not read any self.<attr> attributes).
        - It calls self.int_to_varbyte when needed; int_to_varbyte itself does not read object attributes.
    Attributes WRITTEN:
        - self.delta_time — replaced with either the VLQ-encoded bytes (if an int was given) or the supplied non-int value.

## Constraints:
    Preconditions:
        - If delta_time is an int: it should be >= 0. Negative integers are unsupported and will produce undefined/incorrect VLQ encodings.
        - For strict MIDI compliance, use values <= 0x0FFFFFFF so VLQ encodings remain within the usual 1–4 byte MIDI representation.
        - If delta_time is not an int: callers should provide a bytes object (a proper VLQ) appropriate for concatenation into track_data; this method does not validate that.
    Postconditions:
        - After the call, self.delta_time equals:
            - self.int_to_varbyte(delta_time) if an int was provided (a bytes object), or
            - the original delta_time object if it was not an int.
        - No other attributes are modified.

## Side Effects:
    - No I/O or external service interaction.
    - No mutation of objects other than self.
    - May cause exceptions from int_to_varbyte to propagate.
    - Providing non-bytes values may later cause TypeError when self.delta_time is concatenated into track_data.

### `mingus.midi.midi_track.MidiTrack.select_bank` · *method*

*No documentation generated.*

### `mingus.midi.midi_track.MidiTrack.program_change_event` · *method*

## Summary:
Returns the MIDI Program Change message bytes (current delta-time prefix + status byte + one program data byte) without mutating the MidiTrack; intended to be appended to the track by callers to change a channel's instrument.

## Description:
Known callers and context:
- set_instrument(channel, instr): directly calls this method to obtain the Program Change message and then appends it to self.track_data.
- play_Track and play_Note (indirect): play_Track may mark change_instrument/instrument on the MidiTrack and play_Note will invoke set_instrument when change_instrument is true. This places Program Change messages into the track during the track-building phase.
This method exists to provide a clear, named helper for the Program Change MIDI message and to reuse the centralized midi_event logic for validation and byte construction.

Why this is a separate method:
- Centralizes the semantics of a Program Change (a channel voice event with exactly one data byte) while delegating status-byte construction and range validation to midi_event.
- Keeps higher-level operations (set_instrument, track playback) simple and readable.

## Args:
    channel (int): MIDI channel number. Allowed range: 0 <= channel < 16.
    instr (int): Program (instrument) number. Allowed range: 0 <= instr <= 0x7F (0..127).

## Returns:
    bytes: Concatenation of:
        - self.delta_time (bytes): the current MIDI delta-time prefix,
        - one status byte: (PROGRAM_CHANGE << 4) | channel,
        - one data byte: instr.
    Length: len(self.delta_time) + 2 bytes.
    Example: If self.delta_time is the default b'\x00' (one byte), the returned value has length 3 bytes.

## Raises:
    AssertionError: Raised (by midi_event) when any numeric argument is outside its allowed range:
        - channel < 0 or channel >= 16,
        - instr < 0 or instr > 0x7F.
    TypeError: May be raised by underlying byte construction if provided arguments are of incompatible types (e.g., non-integer objects that cannot be converted to ints for bytes()).

## State Changes:
    Attributes READ:
        - self.delta_time: read and prefixed to the returned bytes.
    Attributes WRITTEN:
        - None. This method does not modify any MidiTrack attributes.

## Constraints:
    Preconditions:
        - self.delta_time should be a bytes instance representing a valid MIDI variable-length delta-time (use set_deltatime or int_to_varbyte to set it).
        - channel and instr must be integers within the ranges documented above.
    Postconditions:
        - The MidiTrack instance remains unchanged.
        - The returned bytes represent a valid MIDI Program Change message that callers can append to self.track_data.

## Side Effects:
    - No I/O, no file or network access.
    - No mutation of objects outside self.
    - Note: Typical usage appends the returned bytes to self.track_data (e.g., set_instrument does this), but that append is performed by the caller, not by this method.

### `mingus.midi.midi_track.MidiTrack.set_tempo` · *method*

## Summary:
Sets the track's beats-per-minute value and appends the corresponding MIDI tempo meta-event bytes to the track_data, mutating the object's tempo state.

## Description:
Known callers and context:
- MidiTrack.__init__(start_bpm=120): initializes a new track by calling this method to record the starting tempo.
- MidiTrack.play_Bar: when a bar contains an object with a .bpm attribute, play_Bar calls set_tempo to emit an in-track tempo change while building the sequence of events.

Typical lifecycle: used during MIDI track construction to record tempo changes and keep the MidiTrack.bpm field in sync with the tempo encoded in the track byte stream.

Separation of concern:
- This method performs state mutation (updating self.bpm and appending bytes). The lower-level byte encoding is implemented in set_tempo_event; splitting these responsibilities allows reuse of the encoding logic and keeps state changes localized.

## Args:
    bpm (int): New tempo in beats per minute. The implementation expects a positive, non-zero integer typical for MIDI tempos (e.g., 60, 120). The method does not perform type coercion or full validation.

## Returns:
    None

## Raises:
    ZeroDivisionError: Raised when bpm == 0 because set_tempo_event computes microseconds-per-quarter-note using integer division by bpm (60000000 // bpm).
    Any exception raised by set_tempo_event will propagate unchanged. Because set_tempo does not validate types, passing non-integer or otherwise invalid values may cause exceptions during formatting inside set_tempo_event.

## State Changes:
Attributes READ:
    self.delta_time (read indirectly by set_tempo_event when composing the tempo meta-event)
Attributes WRITTEN:
    self.bpm (set to the provided bpm)
    self.track_data (extended by appending the bytes returned from set_tempo_event(self.bpm))

## Constraints:
Preconditions:
    - bpm should be a non-zero positive integer. Supplying 0 will raise ZeroDivisionError; supplying non-integer numeric types may produce formatting errors inside the encoder.
    - self.track_data must be a bytes object (the class initializes it to b"") and self.set_tempo_event must be present on the instance.

Postconditions:
    - self.bpm == bpm after the method returns.
    - self.track_data ends with the bytes produced by set_tempo_event(bpm), which (per set_tempo_event) is composed of the current delta_time followed by a MIDI meta-event header for SET_TEMPO and a 3-byte MPQN value computed from 60000000 // bpm.

## Side Effects:
    - Mutates only the MidiTrack instance: updates self.bpm and appends bytes to self.track_data.
    - No file, network, or other external I/O.
    - No mutation of objects outside self.

## Usage example (conceptual, not executable here):
- After constructing a MidiTrack, calling set_tempo(90) updates the object's bpm to 90 and appends a tempo meta-event so that the resulting MIDI data reflects the tempo change at the current delta_time.

### `mingus.midi.midi_track.MidiTrack.set_tempo_event` · *method*

## Summary:
Constructs and immutable bytes sequence for the MIDI Set Tempo meta-event (prefixed by the track's current delta-time) and returns it without modifying the MidiTrack instance.

## Description:
Known callers and context:
    - Called directly by MidiTrack.set_tempo immediately after set_tempo updates self.bpm; set_tempo appends the returned bytes to self.track_data. This occurs when a track initially sets tempo or when tempo changes are emitted during track building (for example, at the start of a track or when a tempo change object is encountered while rendering bars).
    - The method is a pure helper that builds the raw event bytes; it is separated from set_tempo so callers can obtain the exact bytes for the tempo event without duplicating state mutation or MIDI-stream assembly logic.

Why this is a separate method:
    - Keeps IO/mutation (appending to track_data and updating self.bpm) in set_tempo while providing a reusable, testable routine that only constructs the event bytes. This separation makes it easier to generate, inspect, or reuse tempo event bytes in different contexts.

## Args:
    bpm (int):
        - Tempo in beats per minute.
        - Must be a positive, non-zero integer (bpm > 0).
        - The method computes microseconds-per-quarter-note (MPQN) using integer floor division: MPQN = 60000000 // bpm.
        - Passing a float or non-integer will typically raise a TypeError during formatting; negative or otherwise invalid integers may lead to additional errors described below.

## Returns:
    bytes:
        - A bytes object representing the complete MIDI Set Tempo meta-event, structured as:
            self.delta_time + META_EVENT + SET_TEMPO + b"\x03" + mpqn
        - Where:
            - self.delta_time is the current delta-time bytes (type: bytes) from the MidiTrack instance,
            - META_EVENT and SET_TEMPO are one-byte constants imported from mingus.midi.midi_events (meta-event prefix and set-tempo type),
            - b"\x03" is a single length byte (value 3) indicating the MPQN payload length,
            - mpqn is the 3-byte big-endian representation of MPQN (microseconds per quarter note).
        - Total added bytes for the event (excluding variable-length delta_time) are 1 (META_EVENT) + 1 (SET_TEMPO) + 1 (length) + 3 (MPQN) = 6 bytes.

    Example (conceptual):
        If self.delta_time == b"\x00" and MPQN computed to b"\x07\xa1\x20", returned value will look like:
            b"\x00" + b"\xff" + b"\x51" + b"\x03" + b"\x07\xa1\x20"

## Raises:
    ZeroDivisionError:
        - If bpm == 0 (division by zero when computing MPQN).
    TypeError:
        - If bpm is not an integer type (for example, passing a float like 120.0 causes floor-division with an int to produce a float during formatting, and the "%x" integer hex formatter then raises TypeError).
    binascii.Error (from binascii.a2b_hex):
        - If the formatted hex string is not a valid even-length hexadecimal string (this can occur for negative bpm values because the formatted string will contain a '-' sign).
    Note:
        - These exceptions are direct consequences of the implementation (string formatting and a2b_hex conversion); the method does not explicitly validate bpm before use.

## State Changes:
    Attributes READ:
        - self.delta_time: read and prefixed to the returned bytes.
    Attributes WRITTEN:
        - None. This method does not modify self or any external state.

## Constraints:
    Preconditions:
        - self.delta_time must be a bytes object (the class initializes it to b"\x00" and set_deltatime converts ints to bytes).
        - bpm must be a positive integer (bpm > 0) to produce a valid, non-negative MPQN.
    Postconditions:
        - No attributes on self are changed.
        - The returned bytes encode a valid MIDI Set Tempo meta-event with a 3-byte MPQN payload computed as floor(60000000 / bpm).

## Side Effects:
    - None beyond computing and returning bytes. There is no I/O, no external service calls, and no mutation of objects outside self.
    - Caller responsibility: callers who want the tempo event emitted into the track must append the returned bytes to self.track_data (set_tempo performs this append).

### `mingus.midi.midi_track.MidiTrack.set_meter` · *method*

## Summary:
Appends the MIDI time signature meta-event bytes for the given meter to the track's accumulated binary data, updating the track state by extending self.track_data.

## Description:
This method delegates construction of the time signature meta-event to time_signature_event(meter) and concatenates the returned bytes onto self.track_data.

Known callers and context:
- MidiTrack.play_Bar(bar): Called at the beginning of processing a Bar to emit that Bar's meter as a MIDI time signature event. This occurs during conversion of high-level musical Bar objects into MIDI track bytes (track serialization/playback pipeline).

Why this is a separate method:
- Encapsulates the common operation "build time signature meta-event and append it to the track buffer" so playback code does not need to handle low-level byte construction or concatenation.
- Improves readability and reusability by isolating the event-emission step.

## Args:
    meter (tuple[int, int], optional): Two-element tuple (numerator, denominator). Default: (4, 4).
        - numerator: integer beats per bar; must be representable in one unsigned byte (0 <= numerator <= 255).
        - denominator: integer representing the note value that receives one beat (commonly a power of two, e.g., 1, 2, 4, 8, 16). The implementation encodes the denominator as its base-2 exponent: int(log(denominator, 2)).
        - Typical valid examples: (3, 4), (6, 8), (4, 4).

## Returns:
    None
    - The method returns no value. Its observable effect is that self.track_data is extended with the bytes representing the time signature meta-event.

## Raises:
    - TypeError: If meter is not an indexable two-element sequence (e.g., not subscriptable) or its elements are non-numeric in operations (e.g., cannot be formatted/used with math.log). This can occur before time_signature_event is able to process the values.
    - ValueError: If meter[1] <= 0 (math.log requires a positive argument) or if an invalid numeric causes math.log to raise ValueError.
    - binascii.Error: If the formatted hex string for numerator or denominator exponent produces an odd-length string or other hex-format issues when calling a2b_hex. In practice this can occur when numerator or computed exponent are outside the 0..255 byte range that the code encodes as "%02x".
    - TypeError (concatenation): If self.track_data is not a bytes-like object, the concatenation self.track_data += <bytes> will raise a TypeError.

Note: set_meter itself does not catch exceptions; exceptions raised by time_signature_event propagate to the caller.

## State Changes:
Attributes READ:
    - self.track_data (read for concatenation; the current delta time used inside time_signature_event is read when constructing the event)
    - self.delta_time (read indirectly by time_signature_event, which prefixes the event with the current delta time)

Attributes WRITTEN:
    - self.track_data (extended/appended with the time signature meta-event bytes)

## Constraints:
Preconditions:
    - self.track_data must be bytes (the class initializes it to b"" by default).
    - meter must be a two-element sequence: meter[0] (numerator) and meter[1] (denominator) must be numeric.
    - numerator must fit in one byte (0..255) because the implementation encodes it with a two-hex-digit format.
    - denominator must be positive; to avoid unexpected encoding, it should be a power of two. If it is not a power of two, the code computes int(log(denominator, 2)) which effectively encodes floor(log2(denominator)) — i.e., the encoded denominator corresponds to 2**int(log2(denominator)).

Postconditions:
    - self.track_data is extended by the exact byte sequence returned from time_signature_event(meter), which has the structure:
        self.delta_time + META_EVENT + TIME_SIGNATURE + b"\x04" + <numerator_byte> + <denominator_exponent_byte> + b"\x18\x08"
      where <numerator_byte> is a single byte derived from meter[0] and <denominator_exponent_byte> is int(log(meter[1], 2)) encoded as a single byte.
    - No other attributes are modified.

## Side Effects:
    - Mutates only the in-memory buffer self.track_data.
    - No file I/O, network calls, or external service interactions.
    - No mutation of objects outside of self.

### `mingus.midi.midi_track.MidiTrack.time_signature_event` · *method*

## Summary:
Constructs and returns the raw MIDI meta-event bytes representing a time-signature change (using the instance's current delta-time as a prefix) without mutating the MidiTrack object.

## Description:
Encodes a time signature tuple into the MIDI meta-event format and returns the complete byte sequence ready to be appended to a track. The returned bytes follow the MIDI meta-event structure:
self.delta_time + META_EVENT + TIME_SIGNATURE + length_byte + numerator_byte + denominator_byte + clocks_per_click_byte + thirtysecond_notes_per_quarter_byte.

Known callers and context:
- MidiTrack.set_meter — calls this method and appends the returned bytes to self.track_data when a track's meter must be emitted.
- MidiTrack.play_Bar — calls set_meter while rendering a bar, so this method is invoked during track rendering.
- MidiTrack.play_Track — indirectly triggers a call when rendering a whole track that contains bars with meter changes.

Why this is a separate method:
- It localizes byte-level encoding of the standard MIDI time-signature meta-event (including specifying the meta-event type, payload length, and its subfields). This separation keeps the encoding logic reusable and testable independently of where and when track_data is mutated.

Note on constants:
- META_EVENT and TIME_SIGNATURE are constants imported from mingus.midi.midi_events and represent the MIDI meta-event status byte and the time-signature meta-event type byte, respectively. Their exact byte values are defined elsewhere in the codebase.

## Args:
    meter (tuple[int, int], optional):
        - Description: (numerator, denominator) of the time signature.
        - numerator (meter[0]): integer, typically 1..255 (common: 2, 3, 4, 6, 12). Defaults to 4.
        - denominator (meter[1]): integer that should be a power of two (common: 1, 2, 4, 8, 16, 32, 64). Defaults to 4.
        - Default value: (4, 4).
        - Constraints: numerator should be non-negative and small enough to encode as a single byte (0..255) to avoid hex-length issues; denominator must be positive. For correct MIDI semantics, denominator should be a power of two.

## Returns:
    bytes: A bytes object containing the full MIDI meta time-signature event:
        - Prefix: self.delta_time (variable-length delta-time in bytes, prepared by the MidiTrack instance).
        - META_EVENT (1 byte): the meta-event indicator.
        - TIME_SIGNATURE (1 byte): the time-signature meta-event type.
        - Length (1 byte): b'\x04' (four following data bytes).
        - Numerator (1 byte): meter[0] formatted as a two-digit hex byte (a2b_hex("%02x" % meter[0])).
        - Denominator (1 byte): int(log(meter[1], 2)) formatted as a two-digit hex byte (a2b_hex("%02x" % int(log(meter[1], 2)))).
        - Clocks per metronome click (1 byte): b'\x18' (decimal 24).
        - Thirty-second notes per quarter note (1 byte): b'\x08' (decimal 8).
    Edge-case returns:
        - If inputs are valid, a bytes object in the format above is always returned.
        - The method does not return None or modify self.

## Raises:
    TypeError:
        - If meter is not indexable (no meter[0] / meter[1]) or elements are not integers; any operation that treats meter elements as numbers may raise TypeError.
    ValueError:
        - If meter[1] <= 0, math.log(meter[1], 2) will raise a ValueError (domain error).
    binascii.Error (or binascii-related exceptions):
        - If the formatted hex string passed to a2b_hex is invalid. Practical triggers:
            * meter[0] produces a hex string with odd length (for example meter[0] >= 256 produces "%02x" with length 3 -> odd), causing a2b_hex to raise an Error.
            * Other malformed numeric inputs that lead to non-hex characters (unlikely when using "%02x").
    Notes:
        - The function does minimal validation and relies on the behavior of log(...) and a2b_hex; callers should validate inputs if they cannot guarantee proper integer ranges.

## State Changes:
    Attributes READ:
        - self.delta_time: read and used as the delta-time prefix. Expected to be a bytes object representing a variable-length MIDI delta-time.
    Attributes WRITTEN:
        - None. The method does not mutate any attribute of self. (set_meter and other callers append the returned bytes to self.track_data.)

## Constraints:
    Preconditions:
        - self.delta_time must be a bytes-like object already containing a properly encoded variable-length delta-time.
        - meter must be indexable with two numeric elements.
        - meter[1] must be positive; for correct MIDI semantics it should be a power of two.
        - meter[0] should be 0..255 to ensure "%02x" yields exactly two hex digits and a2b_hex receives an even-length hex string.
    Postconditions:
        - Returns a bytes object representing a valid MIDI time-signature meta-event (subject to the correctness of meter values).
        - No mutation of self occurs.

## Side Effects:
    - No file, network, or external I/O.
    - No external services are contacted.
    - Only returns bytes; mutation (appending to track_data) is left to the caller (e.g., set_meter appends the result to self.track_data).

## Implementation notes and example usage:
- Implementation uses:
    - a2b_hex("%02x" % value) to convert a small integer into a single byte.
    - int(log(denominator, 2)) to compute the denominator as MIDI expects (log2).
- Example usage (described, not code-exec):
    - A caller wanting to set a 3/4 meter would call set_meter((3, 4)), which calls this method and appends the returned bytes to self.track_data. The returned bytes will include the current self.delta_time prefix provided by the MidiTrack instance.
- Recommendations:
    - Validate meter before calling this method: confirm denominator is a positive power of two and numerator in 0..255 to avoid binascii errors and to ensure correct MIDI semantics.
    - Do not rely on this method to append to track_data — it only returns the bytes.

### `mingus.midi.midi_track.MidiTrack.set_key` · *method*

## Summary:
Append a MIDI key-signature meta-event to the track's binary data for the specified musical key, updating the track_data buffer to reflect the new key signature.

## Description:
This method converts the provided key identifier into the form expected by the MidiTrack.key_signature_event() helper and appends that meta-event to the track's internal MIDI byte buffer.

Known callers and contexts:
- MidiTrack.play_Bar calls this method as part of preparing a bar for playback/export; it is invoked at the beginning of a bar to encode the bar's key signature into the MIDI track.
- Other code that wants to set or change the track-level key signature before adding notes can call this method directly.

Why this is a separate method:
- Creating and appending the key-signature meta-event is a discrete step (parsing/normalizing the key token, delegating construction of the meta-event, and mutating the track buffer). Keeping it separate improves readability of higher-level playback functions (e.g., play_Bar) and centralizes the handling of Key objects vs. raw string tokens so the encoding logic is not duplicated.

## Args:
    key (mingus.core.keys.Key | str, optional): The musical key to encode. Defaults to "C".
        - If a Key instance is provided, its display name is used (method accesses key.name[0]; see behavior below).
        - If a str is provided, it must be a key token that MidiTrack.key_signature_event can accept:
            * Uppercase tokens (e.g., "C", "F#", "Bb") are treated as major keys.
            * Lowercase tokens (e.g., "c", "f#", "bb") are treated as minor keys.
        - Valid string values are the entries present in the module-level major_keys and minor_keys lists imported from mingus.core.keys. Passing a string not present in those lists will cause a lookup failure when creating the meta-event.

## Returns:
    None
    - The method returns nothing. Its effect is to mutate self.track_data by appending the bytes returned by key_signature_event(key).

## Raises:
    IndexError
        - Condition: A Key instance is passed whose key.name attribute is an empty string (accessing key.name[0] raises IndexError).
    ValueError
        - Condition: After conversion to a string token, the token is not found in the major_keys or minor_keys lists; the underlying key_signature_event uses list.index() which raises ValueError for missing tokens.
    TypeError or AttributeError
        - Condition: If a non-string, non-Key object is passed and key_signature_event attempts to call string methods (e.g., islower()) or indexing, these operations may raise TypeError or AttributeError.
    Any exceptions raised by key_signature_event propagate unchanged.

Note: The method does not validate that the provided Key instance encodes accidentals or mode correctly; it uses exactly key.name[0] when a Key is passed (see Constraints for implications).

## State Changes:
Attributes READ:
    - self.delta_time (indirectly; key_signature_event reads self.delta_time when forming the meta-event)
    - (method reads the passed `key` or the Key object's name attribute when key is a Key instance)

Attributes WRITTEN:
    - self.track_data (bytes): the method appends the key-signature meta-event bytes to this attribute.

## Constraints:
Preconditions:
    - self must be a fully initialized MidiTrack instance with a bytes-like self.track_data attribute.
    - key must be either:
        * a mingus.core.keys.Key instance with a non-empty name attribute, or
        * a str token that appears in the module-level major_keys (for uppercase tokens) or minor_keys (for lowercase tokens) lists.
    - The caller should expect that key_signature_event uses self.delta_time when encoding the meta-event; set self.delta_time appropriately before calling if timing matters.

Postconditions:
    - self.track_data is extended by the exact bytes returned by self.key_signature_event(token), where token is:
        * key.name[0] if key is a Key instance, or
        * key itself if key is a str.
    - No other attributes on self are modified.

Important behavioral note (implementation-observable):
    - If a Key instance is passed, the method uses key.name[0] to derive the string token. Key.name is a human-readable string created by the Key class (e.g., "C major", "C minor", "F sharp major"). Taking name[0] yields only the first character (the tonic letter, always capitalized by Key), discarding any accidental or mode information. Consequently:
        * Passing a Key instance will usually pass only an uppercase tonic letter (e.g., "C"), which key_signature_event will treat as a major key even if the original Key represented a minor key. This is the exact behavior of the current implementation and callers that rely on correct mode/accidental preservation should pass a string token (correctly cased) instead of a Key instance.

## Side Effects:
    - No I/O or external service calls.
    - Mutates self.track_data by appending bytes; this is the only side effect visible outside the object.
    - Exceptions from the internal key_signature_event (including lookup failures) may propagate to callers.

## Implementation Notes (for reimplementation):
    - Behavior to preserve exactly:
        1. If isinstance(key, Key): set token = key.name[0]
        2. Else: set token = key (assumed to be a string)
        3. Call self.key_signature_event(token) and append its return value to self.track_data
    - Do not attempt to infer accidentals or mode when given a Key instance; the original implementation intentionally (but imperfectly) uses only the first character of key.name.
    - Ensure track_data is a bytes-like object and that concatenation uses bytes (i.e., self.track_data += returned_bytes).

### `mingus.midi.midi_track.MidiTrack.key_signature_event` · *method*

## Summary:
Constructs and returns the bytes for a MIDI "Key Signature" meta-event (including the current delta-time), encoded for direct appending to the track's track_data. Does not modify object state.

## Description:
This method encodes a musical key name into the 2-byte MIDI key-signature payload (number of sharps/flats, mode) and returns the full event prefix: delta-time + meta-event header + length + payload.

Known callers and call-stage:
- MidiTrack.set_key calls this method to build the key-signature event and append it to the track data. 
- High-level flows that produce track contents (e.g., MidiTrack.play_Bar → set_key, MidiTrack.play_Track → play_Bar) invoke set_key during track assembly, so this method is invoked during the track-construction stage (before note events are finalized).
- It is its own method because encoding a MIDI key-signature meta-event (including modality and signed-to-unsigned byte conversion) is a discrete, reusable piece of logic used whenever the track's key must be written; separating it keeps the event-format specifics centralized and reusable by higher-level setters.

## Args:
    key (str): Key name string. Default "C".
        - Interpretation:
            * If key.islower() returns True, the method treats the key as a minor key (mode = 1).
            * Otherwise (uppercase or not all-lowercase), the method treats the key as a major key (mode = 0).
        - Allowed values: a string that is present in the corresponding list imported from mingus.core.keys:
            * For major keys: must be an element of major_keys (used when key is not all-lowercase).
            * For minor keys: must be an element of minor_keys (used when key is all-lowercase).
        - Typical examples: "C", "G", "F" for major; "a", "e", "d" for minor (exact valid names come from major_keys and minor_keys).

## Returns:
    bytes: A bytes object representing the complete MIDI meta-event for key signature:
        - Structure: self.delta_time + META_EVENT + KEY_SIGNATURE + b"\x02" + <key_byte> + <mode_byte>
        - <key_byte> is a single byte encoding the number of sharps (0..7) or flats (-1..-7) mapped into an unsigned byte (negative values are wrapped by adding 256).
        - <mode_byte> is b'\x00' for major, b'\x01' for minor.
        - The returned bytes are ready to be appended to MidiTrack.track_data.

## Raises:
    ValueError: If the provided key string is not found in the selected key list (major_keys or minor_keys). This comes from using list.index(key).
    AttributeError: If the provided key does not support .islower() (e.g., None or an incompatible type), the initial key.islower() call will raise AttributeError.
    (No other explicit exceptions are raised by this method; underlying utilities such as a2b_hex expect valid hex formatting, which the method ensures.)

## State Changes:
    Attributes READ:
        - self.delta_time: read and prepended to the returned bytes.
    Attributes WRITTEN:
        - None. The method does not modify self or any external state.

## Constraints:
    Preconditions:
        - self.delta_time must already be set to a valid bytes object representing the desired variable-length delta-time (set via set_deltatime or left as default).
        - key must be a string that is present in the corresponding keys list (major_keys for non-lowercase, minor_keys for lowercase). If this is not true, ValueError will be raised.
    Postconditions:
        - The method returns a correctly-formed MIDI Key Signature meta-event as bytes; no side effects on object state.
        - The returned event encodes the key as a single unsigned byte and the mode as the final byte (0 major, 1 minor).

## Side Effects:
    - No I/O, no network calls, and no mutation of objects outside self.
    - Purely constructs and returns a bytes object (reads self.delta_time only).

## Implementation notes (useful for reimplementation):
    - Determine mode byte: b'\x01' if key.islower() else b'\x00'.
    - Find the key offset value: use index(key) on the appropriate (major or minor) list and subtract 7 to obtain a signed offset in range [-7, +7].
    - Convert negative offsets to unsigned byte form by adding 256 when value < 0.
    - Format the numeric byte as two-hex-digit string "%02x", convert to a single raw byte via a2b_hex, producing the single <key_byte>.
    - Return concatenation: self.delta_time + META_EVENT + KEY_SIGNATURE + b'\x02' + <key_byte> + <mode_byte>.

### `mingus.midi.midi_track.MidiTrack.set_track_name` · *method*

## Summary:
Appends a MIDI "track name" meta-event to this track's raw MIDI byte buffer, updating the object's track_data.

## Description:
Known callers and context:
- MidiTrack.play_Track(track): called when a Track object with a name attribute is being recorded into the MidiTrack. This is invoked early in the track serialization pipeline, before notes and other events are appended, to store the track's human-readable name in the MIDI stream.
- May also be called externally by client code that wants to insert or change the track name while building or modifying a MidiTrack.

Why this logic is its own method:
- Encapsulates the creation and appending of the standard MIDI meta-event for a track name (encoding the length and ASCII bytes) so callers don't need to know the binary format details.
- Keeps event-creation logic separate from higher-level control flow (e.g., play_Track), improving reuse and testability.

## Args:
    name (str): The track name string to encode into the MIDI stream.
        - Must be a Python str (text) object.
        - Must contain only characters encodable to ASCII. Empty strings are allowed.

## Returns:
    None: The method does not return a value; it mutates self.track_data in-place by appending bytes representing the track name meta-event.

## Raises:
    UnicodeEncodeError: Raised when name is a str but contains characters outside ASCII; happens during name.encode("ascii").
    AttributeError: Raised when name does not provide an encode method (for example, if a bytes object or None is passed), because the implementation calls name.encode("ascii").
    (These exceptions originate from the called methods; this method does not explicitly raise its own exceptions.)

## State Changes:
Attributes READ:
    - None of the object's attributes are read by this method (the implementation calls self.track_name_event(name) which does not depend on instance attributes).

Attributes WRITTEN:
    - self.track_data: appended with the bytes returned by self.track_name_event(name). After the call, track_data is extended by one track-name meta-event.

## Constraints:
Preconditions:
    - self.track_data must be a bytes-like object already initialized on the instance (the class constructor initializes it to b"").
    - name must be a str and ASCII-encodable; passing non-str types or non-ASCII text will raise as noted above.

Postconditions:
    - self.track_data ends with the track name meta-event bytes created for the provided name.
    - The object retains other state unchanged (e.g., delta_time, bpm remain unaffected).

## Side Effects:
    - No I/O or external service calls.
    - Mutates only the MidiTrack instance's track_data attribute (no global state).

### `mingus.midi.midi_track.MidiTrack.track_name_event` · *method*

## Summary:
Constructs and returns the MIDI "Track Name" meta-event bytes for the given textual name, leaving the MidiTrack object's state unchanged.

## Description:
This method builds a MIDI meta-event that names a track. It is typically called during track construction when a human-readable name should be embedded in the MIDI stream. Known callers in this class:
- MidiTrack.set_track_name(name): appends the returned bytes to self.track_data.
- MidiTrack.play_Track(track): calls set_track_name(track.name) when a track object exposes a name attribute.

This logic is isolated into its own method because creating a meta-event requires several small, specific pieces (a zero delta-time prefix for immediate event, the META_EVENT and TRACK_NAME event bytes, a variable-length length field, and ASCII encoding of the name). Extracting it keeps event-construction consistent and reusable across callers.

## Args:
    name (str): The track name to encode. Must be a Python str. The method encodes the string using ASCII encoding; characters outside the ASCII range will trigger a UnicodeEncodeError.

## Returns:
    bytes: A bytes object containing the complete MIDI meta-event for the track name, composed as:
        - a single 0 delta-time byte (b'\x00'),
        - the META_EVENT constant,
        - the TRACK_NAME constant,
        - the variable-length length encoding of the name (produced by self.int_to_varbyte(len(name))),
        - the ASCII-encoded name bytes (name.encode('ascii')).
    Edge cases:
        - For an empty string name == "", the returned bytes include a zero-length varbyte field (i.e., length encoded as a single zero byte), followed by no name payload bytes.
        - The return value is always a bytes object; it never mutates self.

## Raises:
    UnicodeEncodeError: If name contains non-ASCII characters (raised by name.encode('ascii')).
    TypeError or AttributeError: If a non-str object without an encode method is passed, attempts to call encode('ascii') may raise these errors.
    (No other exceptions are raised directly by this method; errors from self.int_to_varbyte would surface if an unexpected integer length is supplied, but for len(name) this is not expected to fail.)

## State Changes:
    Attributes READ:
        - (calls) self.int_to_varbyte — uses this helper method but does not read any self.<attribute> fields.
    Attributes WRITTEN:
        - None. This method does not modify any self.<attribute> fields.

## Constraints:
    Preconditions:
        - self must implement int_to_varbyte(int) and return a bytes object representing the variable-length quantity for the provided integer.
        - name must be a str whose length fits into the MIDI variable-length encoding (practically unbounded for normal track names).
    Postconditions:
        - After the call, self remains unchanged.
        - The returned bytes represent a syntactically-correct MIDI Track Name meta-event with delta-time zero.

## Side Effects:
    - No I/O, no filesystem or network activity.
    - No mutation of objects outside the method (it returns a new bytes object).
    - Any appending of the returned bytes into the track's data buffer is performed by callers (e.g., set_track_name), not by this method.

### `mingus.midi.midi_track.MidiTrack.int_to_varbyte` · *method*

## Summary:
Encodes a non-negative integer into the MIDI variable-length quantity (VLQ) format and returns the packed bytes for that VLQ. This method does not modify object state.

## Description:
This routine converts an integer into the minimal sequence of bytes used by MIDI for variable-length quantities: each output byte carries 7 data bits; every byte except the last has the continuation bit (0x80) set. No callers are provided in the supplied source; in a MIDI library this function is intended to be used by serialization routines that write delta-times, event lengths, or other VLQ-encoded fields. The logic is factored out because VLQ encoding is a small, self-contained transformation needed in multiple places when constructing MIDI byte streams.

## Args:
    value (int):
        The integer to encode into VLQ form.
        - Type: int (Python integer)
        - Allowed values: >= 0 for meaningful VLQ encoding.
        - Notes: The implementation will accept any numeric-like input for which bit-shifts and math.log make sense, but behavior for negative integers is not meaningful for MIDI: negative inputs are not supported and will produce an incorrect/undefined encoding. Callers that must strictly conform to the MIDI spec should ensure value <= 0x0FFFFFFF (fits in 4 VLQ bytes).

## Returns:
    bytes:
        A bytes object containing the VLQ encoding (packed unsigned bytes).
        - Single-byte examples:
            - value == 0  -> b'\x00'
            - 1 <= value <= 0x7F -> b'\xXX' where XX is value (high bit cleared)
        - Multi-byte:
            - Encoded as N bytes (most-significant 7-bit group first). All bytes
              except the final one have the continuation bit (0x80) set.
        - The returned sequence is minimal (no leading zero groups).

## Raises:
    TypeError:
        If value is of a type that does not support the numeric operations used (e.g., math.log or right-shift), Python may raise a TypeError. This is raised indirectly by the underlying operations rather than explicitly in this method.
    struct.error:
        If struct.pack receives values outside the 0..255 range or an inconsistent count. Given the implementation masks to 0x7F and ORs 0x80 where appropriate, this should not happen for valid non-negative integer inputs.

## State Changes:
    Attributes READ:
        None — the method does not read any self.<attr> attributes.
    Attributes WRITTEN:
        None — the method does not modify any self.<attr> attributes.

## Constraints:
    Preconditions:
        - value should be an integer >= 0. Negative integers are unsupported and will produce undefined/incorrect encodings.
        - To conform to the MIDI file format, callers should ensure value <= 0x0FFFFFFF (so the VLQ fits within 4 bytes). This function will produce more bytes for larger values but such encodings may not be MIDI-conformant.
    Postconditions:
        - The returned bytes represent the minimal VLQ for the input value.
        - The final byte in the returned sequence has its high bit (0x80) cleared.
        - Any preceding bytes have their high bit (0x80) set.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside self.

## Behavior details and reimplementation steps:
    1. Determine the number of 7-bit groups required:
        - Compute length = int(log(max(value, 1), 0x80)) + 1
          (this gives the count of bytes needed; max(value,1) ensures zero maps to length 1).
    2. Extract 7-bit groups (least-significant group first):
        - For i in range(length): extract (value >> (i * 7)) & 0x7F
    3. Reverse the extracted groups so the most-significant group is first.
    4. Set the continuation bit (0x80) on every byte except the last (final) byte.
    5. Pack the integer byte values into a bytes object (for example, using struct.pack with the "%sB" % len(bytes) format).

## Examples (byte values shown in hex):
    - value = 0x00000000 -> returns b'\x00'
    - value = 0x00000040 (64) -> returns b'\x40'
    - value = 0x00000080 (128) -> returns b'\x81\x00'  (0x81 = continuation + high 7 bits, 0x00 = low 7 bits)
    - value = 0x001FFFFF -> returns b'\xFF\xFF\x7F'   (three-byte VLQ, final byte 0x7F has high bit cleared)

## Notes:
    - The algorithm guarantees minimal encoding (no extra leading zero groups).
    - The use of math.log with base 128 computes how many 7-bit groups are necessary; implementations may alternatively compute length by repeatedly right-shifting value by 7 until zero.
    - This method returns a packed bytes object; if a consumer needs a list of integer byte values, it can be derived from the returned bytes.

