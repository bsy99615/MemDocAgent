# `midi_track.py`

## `mingus.midi.midi_track.MidiTrack` · *class*

*No documentation generated.*

### `mingus.midi.midi_track.MidiTrack.__init__` · *method*

## Summary:
Initializes a MIDI track with empty data and sets the starting tempo.

## Description:
The `__init__` method prepares a MidiTrack object for MIDI data generation by initializing the track's data buffer and setting up the initial tempo. This method is called automatically when creating a new MidiTrack instance and ensures the track starts with a defined tempo value.

## Args:
    start_bpm (int): The initial beats per minute for the track. Defaults to 120.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.track_data: Set to empty byte string b""
    - self.bpm: Set to the provided start_bpm value

## Constraints:
    Preconditions: None
    Postconditions: 
    - self.track_data is initialized to an empty byte string
    - self.bpm is set to the provided start_bpm value
    - The track contains a tempo event for the initial tempo

## Side Effects:
    None: This method does not perform I/O operations or mutate external objects.

### `mingus.midi.midi_track.MidiTrack.end_of_track` · *method*

## Summary:
Returns the byte sequence representing a MIDI end-of-track event.

## Description:
This method returns the standard MIDI end-of-track event marker that signifies the conclusion of a MIDI track. It is used internally by the MidiTrack class to properly terminate MIDI tracks when generating MIDI data. The returned byte sequence is commonly used in MIDI files to indicate the end of a track's data.

## Args:
    None

## Returns:
    bytes: A byte sequence `b"\x00\xff\x2f\x00"` representing a MIDI end-of-track event, where:
           - `\x00` is the delta time (0)
           - `\xff` indicates this is a meta event
           - `\x2f` is the end-of-track meta event command
           - `\x00` indicates the event has no parameters

## Raises:
    None

## State Changes:
    - Attributes READ: None
    - Attributes WRITTEN: None

## Constraints:
    - Preconditions: None
    - Postconditions: Always returns the same fixed byte sequence

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.play_Note` · *method*

## Summary:
Plays a MIDI note by adding a note-on event to the track's data buffer.

## Description:
This method processes a Note object to generate and append a MIDI note-on event to the track's data. It handles instrument changes when needed and validates the note's velocity before creating the MIDI event. The method is part of the MIDI track playback pipeline and integrates with the broader music composition system.

## Args:
    note (Note): A Note object containing note information including pitch, channel, and velocity.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: When the note's velocity is outside the valid MIDI range (0-127).

## State Changes:
    Attributes READ: self.change_instrument, self.instrument, self.delta_time
    Attributes WRITTEN: self.track_data

## Constraints:
    Preconditions: 
    - The note parameter must be a valid Note object with proper channel and velocity attributes
    - The note's velocity must be between 0 and 127 (inclusive)
    - The track must have a valid instrument assigned if change_instrument is True
    
    Postconditions:
    - The track_data attribute is updated with the new note-on event
    - If change_instrument was True, the instrument is set and change_instrument is set to False

## Side Effects:
    - Modifies the track_data attribute by appending MIDI events
    - May call set_instrument() which could modify track_data further
    - No external I/O or service calls

### `mingus.midi.midi_track.MidiTrack.play_NoteContainer` · *method*

## Summary:
Plays a collection of notes from a NoteContainer with proper timing synchronization.

## Description:
This method handles the playback of a sequence of musical notes contained in a NoteContainer. It manages timing by setting deltatime to zero between consecutive notes, ensuring proper sequential playback. The method has optimized handling for containers with 1 or fewer notes versus containers with multiple notes.

Known callers:
- `MidiTrack.play_Bar()` - Called when processing musical bars containing note sequences
- The method is part of the standard MIDI playback pipeline for handling note collections

This logic is separated into its own method rather than being inlined because it provides reusable logic for playing note collections with proper timing control, and it mirrors the complementary `stop_NoteContainer` method for consistency.

## Args:
    notecontainer: A collection of musical note objects to be played sequentially

## Returns:
    None

## Raises:
    AssertionError: If note velocity values are outside the valid range (0-127)

## State Changes:
    Attributes READ: 
        - self.delta_time
        - self.track_data
        - self.change_instrument
        - self.instrument
    
    Attributes WRITTEN:
        - self.track_data (appended with MIDI events)
        - self.delta_time (modified via set_deltatime calls)

## Constraints:
    Preconditions:
        - notecontainer must be iterable and contain valid note objects
        - Each note in the container must have valid channel and velocity attributes
        - Note velocities must be in the range 0-127
    
    Postconditions:
        - All notes in the container are added to the track_data as MIDI events
        - Delays between notes are properly managed with zero deltatime between consecutive notes

## Side Effects:
    - Appends MIDI events to self.track_data
    - Modifies self.delta_time through set_deltatime calls
    - May trigger instrument change if self.change_instrument is True

### `mingus.midi.midi_track.MidiTrack.play_Bar` · *method*

## Summary:
Processes a musical bar by setting up timing, meter, and key information, then plays the notes contained within the bar according to their durations.

## Description:
This method takes a Bar object and translates its musical content into MIDI events. It handles tempo changes, meter signatures, key signatures, and note playback while properly managing timing delays between musical events. The method is designed to be called as part of the MIDI track generation process, specifically within the context of playing a complete musical track.

The bar parameter is expected to be iterable, where each item represents a musical event in the format [beat_position, duration, note_container]. Beat positions are relative to the bar's time signature, durations specify note lengths, and note_containers hold the actual musical notes to be played. This separation allows for modular processing of musical content, where each bar can be processed independently while maintaining proper timing relationships.

## Args:
    bar (Bar): A Bar object containing musical content including meter, key, and note containers arranged by beat position and duration. The bar must be iterable where each element follows the pattern [beat_position, duration, note_container].

## Returns:
    None: This method operates by modifying the MidiTrack's internal state and track_data attribute. It does not return any value.

## Raises:
    None explicitly raised, but may propagate exceptions from underlying methods like play_NoteContainer or set_tempo.

## State Changes:
    Attributes READ: 
        - self.delay
        - self.bpm
    
    Attributes WRITTEN:
        - self.delay (accumulated timing delays for subsequent events)
        - self.track_data (appended with MIDI events for meter, key, tempo, and note playback)
        - self.delta_time (updated via set_deltatime calls during event generation)

## Constraints:
    Preconditions:
        - The bar parameter must be a valid Bar object with proper meter and key attributes
        - The bar must be iterable, yielding elements in the form [beat_position, duration, note_container]
        - Each note_container should be compatible with play_NoteContainer method (can be None for rests)
        - Duration values must be valid beat durations that can be converted to MIDI ticks
        
    Postconditions:
        - The MidiTrack's track_data will contain MIDI events representing the bar's musical content
        - The delay attribute will be reset to 0 after processing
        - Tempo, meter, and key information will be properly set in the track data
        - All notes in the bar will be played with appropriate timing

## Side Effects:
    - Modifies the MidiTrack's internal track_data buffer by appending MIDI events
    - May modify the MidiTrack's delta_time attribute during event generation
    - Calls methods that may trigger external MIDI playback or file writing operations
    - Sets tempo, meter, and key information in the MIDI track

### `mingus.midi.midi_track.MidiTrack.play_Track` · *method*

## Summary:
Processes a track object by setting up track metadata, instrument configuration, and playing each bar sequentially.

## Description:
This method serves as the main entry point for converting a high-level track representation into MIDI events. It handles track naming, instrument setup, and delegates bar-by-bar processing to the play_Bar method. This separation allows for clean organization of MIDI track creation logic.

## Args:
    track: A track object containing musical data with potential name and instrument attributes

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
        - self.delay
        - self.change_instrument
        - self.instrument
    
    Attributes WRITTEN:
        - self.delay (reset to 0)
        - self.change_instrument (set to True if instrument_nr found)
        - self.instrument (set to instrument_nr if found)

## Constraints:
    Preconditions:
        - The track parameter must be iterable (supporting for bar in track)
        - The track may optionally have a "name" attribute
        - The track may optionally have an "instrument" attribute with "instrument_nr" attribute
    
    Postconditions:
        - The delay attribute is reset to 0
        - Instrument change flags are properly set if applicable
        - All bars in the track are processed via play_Bar method

## Side Effects:
    - Modifies self.track_data through calls to play_Bar and related methods
    - May modify tempo settings through play_Bar calls
    - May modify key and meter settings through play_Bar calls

### `mingus.midi.midi_track.MidiTrack.stop_Note` · *method*

## Summary:
Stops a MIDI note by sending a note-off event for the specified note.

## Description:
This method sends a MIDI note-off event for the given note, effectively stopping the sound. It extracts the channel and velocity from the note object and uses the note-off MIDI event to update the track data. This method is the counterpart to `play_Note` and is typically called during the playback process to terminate notes.

## Args:
    note: A note object with the following attributes:
        - channel (int): The MIDI channel number (typically 0-15)
        - velocity (int): The release velocity (typically 0-127)
        - int(note) (int): The MIDI note number (typically 0-127)

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: 
        - self.track_data
    Attributes WRITTEN:
        - self.track_data: Appended with the note-off MIDI event data

## Constraints:
    Preconditions:
        - The note object must have channel and velocity attributes
        - The note object must be convertible to an integer (MIDI note number)
        - The note object's channel must be in the valid range (0-15)
        - The note object's velocity must be in the valid range (0-127)
    Postconditions:
        - The track_data attribute is updated with a note-off MIDI event
        - The note-off event corresponds to the note's channel, adjusted note number, and velocity

## Side Effects:
    None: This method only modifies the internal track_data attribute.

### `mingus.midi.midi_track.MidiTrack.stop_NoteContainer` · *method*

## Summary:
Stops all notes in a note container by generating MIDI note-off events, with optimized handling for single vs. multiple notes to ensure proper timing synchronization.

## Description:
This method generates MIDI note-off events for all notes in a container, designed to properly terminate musical phrases during MIDI playback. When processing a single note or empty container, it stops all notes sequentially. For containers with multiple notes, it stops the first note, resets the delta time to zero, then stops the remaining notes. This special handling prevents timing issues when stopping multiple simultaneous notes.

The method is called during the playback lifecycle in `MidiTrack.play_Bar()` at the end of musical phrases to properly terminate MIDI events and prevent stuck notes.

## Args:
    notecontainer: An iterable container (list-like) of note objects that must have channel and velocity attributes

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.track_data (appended with MIDI note-off events), self.delta_time (modified via set_deltatime call)

## Constraints:
    Preconditions: notecontainer must be iterable and contain valid note objects with channel and velocity attributes; notecontainer should support len() and indexing operations
    Postconditions: All notes in the container will have their corresponding MIDI note-off events appended to self.track_data

## Side Effects:
    Mutates self.track_data by appending MIDI note-off events for each note in the container
    Modifies self.delta_time by calling set_deltatime(0) when processing multi-note containers to synchronize timing

### `mingus.midi.midi_track.MidiTrack.set_instrument` · *method*

## Summary:
Sets the instrument for a specified MIDI channel by sending a bank selection and program change event.

## Description:
This method configures a MIDI channel to use a specific instrument by first selecting the appropriate bank and then sending a program change event. It's typically called during the playback setup phase when preparing to play notes on a specific channel with a particular instrument. The method is used internally by the MidiTrack class when setting up instrument changes for musical playback.

## Args:
    channel (int): The MIDI channel number (0-15) to configure.
    instr (int): The instrument number (0-127) to assign to the channel.
    bank (int): The bank number (0-127) to select. Defaults to 1.

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: If channel, instr, or bank values are outside their valid ranges (0-15 for channel, 0-127 for instr/bank).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.track_data

## Constraints:
    Preconditions: 
    - Channel must be between 0 and 15
    - Instrument number must be between 0 and 127
    - Bank number must be between 0 and 127
    
    Postconditions:
    - The track_data attribute is updated with MIDI events for bank selection and program change

## Side Effects:
    None: This method only modifies the internal track_data attribute and doesn't perform any I/O or external service calls.

### `mingus.midi.midi_track.MidiTrack.header` · *method*

## Summary:
Returns the MIDI track header chunk containing the track identifier and size information.

## Description:
Generates the header portion of a MIDI track by combining the track identifier with the calculated chunk size. This method is called during MIDI file construction to create the proper header structure for the track data.

## Args:
    None

## Returns:
    bytes: A byte string containing the MIDI track header with the format "MTrk" followed by the 4-byte big-endian chunk size.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.track_data, self.end_of_track()
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.track_data must be a bytes object
    - self.end_of_track() must return a bytes object
    - The total size calculation must fit within 4 bytes
    
    Postconditions:
    - Returns a properly formatted MIDI track header chunk
    - The returned bytes represent a valid MIDI track header structure

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.get_midi_data` · *method*

## Summary:
Assembles and returns complete MIDI track data by combining track header, event data, and end-of-track marker.

## Description:
This method constructs the complete MIDI track data by concatenating three components: the track header (which includes the chunk size), the actual MIDI event data stored in `track_data`, and the end-of-track marker. It serves as the primary interface for retrieving fully formatted MIDI track data for inclusion in MIDI files.

The method is separated from inline construction to ensure proper formatting and encapsulation of the track data assembly process, making it reusable and maintaining clean separation of concerns between header creation, event storage, and track termination logic.

## Args:
    None

## Returns:
    bytes: Complete MIDI track data including header, event data, and end-of-track marker

## State Changes:
    Attributes READ: 
        - self.track_data: Contains the MIDI event data
        - self.header(): Generates the track header with proper chunk size
        - self.end_of_track(): Provides the end-of-track marker
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The `track_data` attribute should contain valid MIDI event data
        - The `header()` method should return properly formatted header data
        - The `end_of_track()` method should return properly formatted end-of-track marker
    Postconditions:
        - Returns a complete, properly formatted MIDI track structure
        - The returned bytes represent a valid MIDI track segment

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.midi_event` · *method*

## Summary:
Constructs and returns a MIDI event byte sequence for a given event type, channel, and parameters.

## Description:
This method creates a MIDI event by combining a status byte with event parameters and prepending the current delta time. It serves as the foundational building block for all MIDI events in the track, ensuring proper formatting according to MIDI specifications. This method is typically called internally by other methods such as note_off, note_on, controller_event, and program_change_event.

## Args:
    event_type (int): The type of MIDI event (0-15). Values correspond to standard MIDI event types (e.g., 0x8 for Note Off, 0x9 for Note On, 0xB for Controller Change, 0xC for Program Change).
    channel (int): The MIDI channel number (0-15). Specifies which channel the event should be sent to.
    param1 (int): First parameter for the MIDI event (0-127). For note events, this is the note number; for controller events, this is the controller number.
    param2 (int, optional): Second parameter for the MIDI event (0-127). For note events, this is the velocity; for controller events, this is the controller value. Defaults to None.

## Returns:
    bytes: A byte sequence representing the complete MIDI event, including the current delta time and event data.

## Raises:
    AssertionError: If any of the parameter constraints are violated (event_type, channel, or parameters outside valid ranges).

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - event_type must be an integer between 0 and 15 inclusive
        - channel must be an integer between 0 and 15 inclusive  
        - param1 must be an integer between 0 and 127 inclusive
        - param2 must be None or an integer between 0 and 127 inclusive
    Postconditions:
        - Returns a properly formatted MIDI event byte sequence
        - The returned bytes include the current delta_time prefix

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.note_off` · *method*

## Summary:
Creates and returns a MIDI Note Off event for the specified channel, note, and velocity.

## Description:
This method generates a MIDI Note Off event, which signals the end of a note playback. It delegates to the underlying midi_event method to construct the appropriate MIDI event structure. This is part of the MIDI track management system for creating musical events.

## Args:
    channel (int): The MIDI channel number (typically 0-15)
    note (int): The MIDI note number (typically 0-127) 
    velocity (int): The release velocity (typically 0-127)

## Returns:
    The result of calling self.midi_event with NOTE_OFF event type and provided parameters. The exact return type depends on the implementation of midi_event.

## Raises:
    None explicitly documented - depends on implementation of self.midi_event

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - channel should be a valid MIDI channel (typically 0-15)
    - note should be a valid MIDI note number (typically 0-127)
    - velocity should be a valid MIDI velocity value (typically 0-127)
    
    Postconditions: 
    - Returns a properly formatted MIDI event structure compatible with MIDI standards

## Side Effects:
    None - this method is pure and doesn't cause external mutations

### `mingus.midi.midi_track.MidiTrack.note_on` · *method*

## Summary:
Creates a MIDI note-on event by delegating to the midi_event method.

## Description:
This method serves as a convenience wrapper that creates a MIDI note-on event by calling the internal midi_event method with the NOTE_ON event type. It is used to signal the beginning of a musical note in a MIDI track.

## Args:
    channel (int): The MIDI channel number where the note will be played.
    note (int): The MIDI note number representing the pitch of the note.
    velocity (int): The velocity (volume) of the note press.

## Returns:
    The return value of self.midi_event(NOTE_ON, channel, note, velocity).

## Raises:
    None explicitly documented, but may raise exceptions from the underlying midi_event method.

## State Changes:
    Attributes READ: None specific attributes are read.
    Attributes WRITTEN: None specific attributes are written directly by this method.

## Constraints:
    Preconditions: 
    - The channel parameter should be a valid MIDI channel.
    - The note parameter should be a valid MIDI note number.
    - The velocity parameter should be a valid velocity value.
    
    Postconditions: 
    - A note-on MIDI event is prepared for inclusion in the MIDI track.

## Side Effects:
    None directly observable side effects. The method may cause internal state changes in the MidiTrack object through the midi_event method call, but these are not explicitly documented.

### `mingus.midi.midi_track.MidiTrack.controller_event` · *method*

## Summary:
Sets a MIDI controller event on the specified channel with the given controller number and value.

## Description:
This method creates and returns a MIDI controller event message. It serves as a convenience wrapper around the more general midi_event method, specifically for controller events. Controller events are used to send control changes to MIDI devices, such as volume, pan, or modulation.

## Args:
    channel (int): The MIDI channel number (0-15) on which to send the controller event.
    contr_nr (int): The controller number (0-127) specifying which controller to change.
    contr_val (int): The controller value (0-127) specifying the new value for the controller.

## Returns:
    bytes: A byte sequence representing the complete MIDI controller event message, including delta time, status byte, and parameter bytes.

## Raises:
    AssertionError: If channel is not in range [0, 15], contr_nr is not in range [0, 127], or contr_val is not in range [0, 127].

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - channel must be an integer in the range [0, 15]
    - contr_nr must be an integer in the range [0, 127] 
    - contr_val must be an integer in the range [0, 127]
    Postconditions:
    - Returns a properly formatted MIDI controller event byte sequence
    - The returned bytes include the delta time, status byte, and controller parameters

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.reset` · *method*

## Summary:
Resets the MIDI track's data buffer and delta time counter to initial empty states.

## Description:
Clears the track data buffer and resets the delta time to its default zero value. This method is typically used when reinitializing a MidiTrack instance for reuse or when starting a fresh track recording.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.track_data: Set to empty bytes (b"")
    - self.delta_time: Set to null byte (b"\x00")

## Constraints:
    Preconditions: None
    Postconditions: 
    - self.track_data will be an empty bytes object
    - self.delta_time will be a null byte

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.set_deltatime` · *method*

## Summary:
Sets the delta time for MIDI events, converting integer values to MIDI variable-length byte format.

## Description:
Configures the delta time attribute of a MidiTrack object, which determines the time interval between MIDI events. When an integer is provided, it's converted to MIDI's variable-length quantity format using the int_to_varbyte method. This delta time is used in MIDI event construction to specify timing intervals between musical events.

Known callers:
- MidiTrack.play_NoteContainer: Sets delta time to 0 between notes in a container
- MidiTrack.play_Bar: Sets delta time to accumulated delay before playing bars
- MidiTrack.stop_NoteContainer: Sets delta time to 0 between stopping notes

This method exists separately to encapsulate the conversion logic and provide a clean interface for setting delta times throughout the MIDI track processing pipeline.

## Args:
    delta_time (int or bytes): The delta time value. If an integer, it will be converted to MIDI variable-length byte format. If bytes, it's used directly.

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.delta_time

## Constraints:
    Preconditions: None
    Postconditions: self.delta_time is set to either the original bytes value or the variable-length encoded bytes representation of an integer input

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.select_bank` · *method*

## Summary:
Selects a MIDI bank for a given channel by sending a bank select controller message.

## Description:
This method sends a controller event to select a specific bank for the specified MIDI channel. It is typically used as part of the instrument setup process, preceding a program change event to ensure the correct bank is selected before changing instruments. The method delegates to the controller_event method with the appropriate bank select controller number.

In standard MIDI, bank selection typically uses two controller messages:
- Controller 0 (MSB Bank Select) for the most significant byte
- Controller 32 (LSB Bank Select) for the least significant byte

## Args:
    channel (int): The MIDI channel number (0-15) for which to select the bank.
    bank (int): The bank number to select (typically 0-127, though exact range depends on MIDI implementation).

## Returns:
    bytes: The MIDI controller event data representing the bank selection command.

## Raises:
    AssertionError: If channel is not in the range [0, 15] or if bank value exceeds 0x7F (127).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Channel must be an integer between 0 and 15 inclusive
    - Bank must be an integer between 0 and 127 inclusive
    
    Postconditions:
    - The method returns valid MIDI controller event data for bank selection
    - The returned data can be added to the track's data stream

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.program_change_event` · *method*

## Summary:
Creates a MIDI program change event to switch the instrument on a specific channel.

## Description:
This method generates a MIDI program change event that changes the instrument assigned to a specific MIDI channel. It serves as a convenience wrapper around the general `midi_event` method, specifically for program change events. Program change events are used in MIDI to switch between different instruments or sounds available on a synthesizer or sound module.

## Args:
    channel (int): The MIDI channel number (0-15) on which to change the instrument.
    instr (int): The instrument number (0-127) to switch to.

## Returns:
    bytes: A byte string representing the formatted MIDI program change event.

## Raises:
    AssertionError: If channel is not in range [0, 15], or if instr is not in range [0, 127].

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Channel must be an integer between 0 and 15 (inclusive)
    - Instrument number must be an integer between 0 and 127 (inclusive)
    
    Postconditions:
    - Returns a properly formatted MIDI program change event byte sequence
    - The returned bytes include the appropriate status byte and parameter

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.set_tempo` · *method*

## Summary:
Sets the tempo of the MIDI track in beats per minute and updates the track data with a tempo change event.

## Description:
This method configures the playback speed of the MIDI track by setting the beats per minute (BPM) value. It updates the internal BPM attribute and appends the corresponding MIDI tempo event to the track's data buffer. This allows the MIDI track to be played back at the specified tempo.

## Args:
    bpm (int): The tempo in beats per minute. Must be a positive integer representing the number of beats per minute.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: self.bpm, self.track_data, self.delta_time
    Attributes WRITTEN: self.bpm, self.track_data

## Constraints:
    Preconditions: The bpm parameter must be a positive integer.
    Postconditions: The self.bpm attribute is updated to the provided value, and self.track_data contains the tempo change event.

## Side Effects:
    Mutates the self.track_data attribute by appending MIDI tempo event data.

### `mingus.midi.midi_track.MidiTrack.set_tempo_event` · *method*

## Summary
Creates a MIDI meta event for setting the tempo in microseconds per quarter note.

## Description
This method generates a properly formatted MIDI meta event that sets the tempo of a MIDI track. It's used internally by the `set_tempo` method to add tempo change events to the track data. The method calculates the microseconds per quarter note (MPQN) from the provided beats per minute (BPM) value and constructs a standard MIDI meta event with the SET_TEMPO type.

The method is part of the MidiTrack class and works with MIDI event constants imported from mingus.midi.midi_events module.

## Args
    bpm (int): Beats per minute value for the tempo setting. Must be a positive integer greater than 0.

## Returns
    bytes: A byte string representing a complete MIDI meta event for tempo setting, including:
        - Current delta_time value (from self.delta_time)
        - Meta event identifier (META_EVENT constant from midi_events)
        - Set tempo command (SET_TEMPO constant from midi_events)
        - Length byte (always b"\x03")
        - 3-byte value representing microseconds per quarter note (MPQN)

## Raises
    ZeroDivisionError: If bpm is zero
    ValueError: If bpm is negative or non-integer
    OverflowError: If bpm calculation results in overflow

## State Changes
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints
    Preconditions:
        - bpm must be a positive integer greater than 0
        - self.delta_time should be properly initialized (typically b"\x00")
    Postconditions:
        - Returns a properly formatted MIDI meta event bytes object
        - The returned bytes object represents a valid MIDI tempo change event

## Side Effects
    None

### `mingus.midi.midi_track.MidiTrack.set_meter` · *method*

## Summary:
Sets the time signature for a MIDI track by appending a time signature meta event to the track data.

## Description:
This method configures the time signature of a MIDI track, which defines how many beats are in each measure and what note value constitutes one beat. It is typically called during the construction of a MIDI track when setting up musical meter information. The method is used in the playback pipeline when processing bars in a track, specifically in the `play_Bar` method where it's called to set the meter for each bar.

This logic is separated into its own method to encapsulate the creation and application of time signature events, making the track building process more modular and readable.

## Args:
    meter (tuple[int, int]): A tuple representing the time signature in the form (numerator, denominator). Default is (4, 4) representing 4/4 time. The denominator is expected to be a power of 2 (e.g., 2, 4, 8, 16).

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.delta_time, self.track_data
    Attributes WRITTEN: self.track_data (appended with time signature event data)

## Constraints:
    Preconditions: The meter parameter should be a tuple where the second element is a power of 2 (2, 4, 8, 16, etc.) for valid MIDI time signatures.
    Postconditions: The track_data attribute will contain the time signature meta event for the specified meter.

## Side Effects:
    None: This method only modifies the internal state of the MidiTrack instance.

### `mingus.midi.midi_track.MidiTrack.time_signature_event` · *method*

## Summary:
Creates a MIDI time signature meta event for the specified meter.

## Description:
Generates a MIDI meta event that specifies the time signature for a track. This method is called internally by the `set_meter` method when setting the time signature of a musical piece. The time signature is represented as a tuple of (numerator, denominator) where the denominator is a power of 2.

## Args:
    meter (tuple[int, int]): Time signature as (numerator, denominator). Defaults to (4, 4).

## Returns:
    bytes: A complete MIDI meta event containing the time signature information.

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - meter must be a tuple of two integers
    - denominator must be a power of 2 (2, 4, 8, 16, 32, etc.)
    - meter[0] must be a positive integer
    Postconditions:
    - Returns properly formatted MIDI time signature meta event
    - The returned bytes follow standard MIDI format for meta events

## Side Effects:
    None.

### `mingus.midi.midi_track.MidiTrack.set_key` · *method*

## Summary:
Sets the key signature for a MIDI track by appending a key signature event to the track's data.

## Description:
This method configures the key signature for the MIDI track. It accepts either a string representing a musical key (like "C", "G#", "Am") or a Key object, and adds the appropriate key signature meta-event to the track's data stream. This method is typically called during the playback setup phase when defining the tonal center of a musical piece.

The method is separated from inline logic to maintain clean code organization and allow for reuse in different contexts where key signatures need to be set programmatically.

## Args:
    key (str or Key): The musical key to set. Can be a string representation like "C", "G#", "Am" or a Key object. Defaults to "C".

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: If the key string is not recognized as a valid major or minor key.

## State Changes:
    Attributes READ: self.track_data, self.delta_time
    Attributes WRITTEN: self.track_data

## Constraints:
    Preconditions: 
    - The key parameter must be either a string representing a valid musical key or a Key object
    - The key string must be a recognized major or minor key (e.g., "C", "G#", "Am")
    
    Postconditions:
    - The track_data attribute contains the key signature meta-event
    - The key signature event is properly formatted according to MIDI specification

## Side Effects:
    None: This method only modifies the internal track_data attribute and does not perform any I/O operations or external service calls.

### `mingus.midi.midi_track.MidiTrack.key_signature_event` · *method*

## Summary:
Creates a MIDI key signature meta-event for the specified key, returning a complete MIDI event bytes object.

## Description:
Generates a MIDI key signature meta-event that specifies the key signature for subsequent musical events in the track. This method is used internally by the `set_key` method to add key signature information to MIDI tracks. The method handles both major and minor keys by calculating appropriate key signature values according to MIDI specifications.

## Args:
    key (str): The key signature to set, defaults to "C". Should be a valid key name (e.g., "C", "G", "D", "A", "E", "B", "F#", "Db", etc.). Can be either uppercase (major) or lowercase (minor).

## Returns:
    bytes: A complete MIDI meta-event structured as: self.delta_time + META_EVENT + KEY_SIGNATURE + b"\x02" + key_bytes + mode_byte, where key_bytes represents the key signature value and mode_byte indicates major (0x00) or minor (0x01) mode.

## Raises:
    ValueError: When the key parameter is not found in the major_keys or minor_keys lists.

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The key parameter must be a valid key name present in either major_keys or minor_keys lists
    - The key parameter should be a string
    
    Postconditions:
    - Returns a properly formatted MIDI meta-event bytes object
    - The returned bytes follow MIDI specification for key signature events

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.set_track_name` · *method*

## Summary:
Sets the name of the MIDI track by appending a track name meta event to the track data.

## Description:
This method configures the MIDI track's name by creating a track name meta event and appending it to the existing track data. It is typically called during the construction of a MIDI track to assign a descriptive name to the track, which can be useful for identification in MIDI editors or playback applications.

## Args:
    name (str): The name to assign to the MIDI track. Must be a valid ASCII string.

## Returns:
    None: This method does not return a value.

## Raises:
    UnicodeEncodeError: If the name contains non-ASCII characters that cannot be encoded.

## State Changes:
    Attributes READ: self.track_data
    Attributes WRITTEN: self.track_data

## Constraints:
    Preconditions: The name parameter must be a string containing only ASCII characters.
    Postconditions: The track_data attribute will contain the original data plus the new track name meta event.

## Side Effects:
    None: This method only modifies the internal track_data attribute and has no external side effects.

### `mingus.midi.midi_track.MidiTrack.track_name_event` · *method*

## Summary:
Creates a MIDI meta event for setting a track's name.

## Description:
This method generates a properly formatted MIDI meta event that encodes a track name. It takes a string name and converts it into a byte sequence suitable for inclusion in MIDI track data. The method uses the class's `int_to_varbyte` method to encode the length of the name in variable-length format, following MIDI specification conventions.

## Args:
    name (str): The track name to set. Must be ASCII-compatible.

## Returns:
    bytes: A complete MIDI meta event containing the track name, formatted as:
           [delta_time][meta_event_type][track_name_type][length][name_bytes]
           where delta_time is always 0 (b"\x00"), meta_event_type is the MIDI meta event identifier,
           track_name_type is the meta event type for track names, length is encoded using variable-byte format,
           and name_bytes are the ASCII-encoded name.

## Raises:
    UnicodeEncodeError: If the name contains non-ASCII characters that cannot be encoded.
    AttributeError: If self.int_to_varbyte is not available (though this would indicate a class design issue).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The name parameter must be a string that can be encoded to ASCII
    - The method assumes `self.int_to_varbyte` is available and working correctly
    - The method assumes appropriate MIDI meta event constants are defined in the class scope
    
    Postconditions:
    - Returns properly formatted MIDI meta event bytes
    - The returned bytes represent a valid MIDI track name event

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.int_to_varbyte` · *method*

## Summary:
Converts an integer into MIDI variable-length byte representation for encoding delta times and event data.

## Description:
Implements MIDI's variable-length quantity (VLQ) encoding format, where integers are encoded as a sequence of 7-bit values with continuation bits. Each byte contains 7 bits of data and the most significant bit (MSB) indicates if more bytes follow. This encoding is essential for MIDI files where quantities like delta times, event lengths, and meta-event parameters can vary in size.

The method is used internally by the MidiTrack class when constructing MIDI events that require variable-length encoding, particularly in the `set_deltatime` method for timing information and in `track_name_event` for encoding track name lengths.

## Args:
    value (int): Non-negative integer to encode. Values of 0 are handled correctly.

## Returns:
    bytes: Variable-length byte sequence following MIDI VLQ format. The length of the returned bytes depends on the magnitude of the input value, with larger numbers requiring more bytes.

## Raises:
    None explicitly raised, though invalid inputs may cause underlying math or struct operations to fail.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: Input value must be a non-negative integer.
    Postconditions: Output bytes follow MIDI VLQ specification where all but the final byte have MSB set to 1.

## Side Effects:
    None

