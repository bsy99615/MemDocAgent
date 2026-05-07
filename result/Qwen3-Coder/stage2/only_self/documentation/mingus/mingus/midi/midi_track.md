# `midi_track.py`

## `mingus.midi.midi_track.MidiTrack` · *class*

*No documentation generated.*

### `mingus.midi.midi_track.MidiTrack.__init__` · *method*

## Summary:
Initializes a MidiTrack object with empty track data and sets the initial tempo.

## Description:
The __init__ method initializes a MidiTrack instance by setting up the basic track structure with empty track data and establishing an initial tempo. This method serves as the constructor for MidiTrack objects, preparing them for subsequent MIDI operations like note playing and track manipulation.

This logic is separated into its own method rather than being inlined because it provides a clean initialization pattern and allows for easy extension in the future. It also ensures that all MidiTrack instances start with consistent initial state.

## Args:
    start_bpm (int): The initial beats per minute tempo for the track. Defaults to 120.

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

## Side Effects:
    None: This method does not perform any I/O operations or mutate external objects.

### `mingus.midi.midi_track.MidiTrack.end_of_track` · *method*

## Summary:
Returns the standard MIDI end-of-track meta event byte sequence that terminates a MIDI track.

## Description:
This method returns the fixed byte sequence that represents a MIDI end-of-track meta event. This event is required at the end of every MIDI track to properly signal the end of the track data. The returned sequence consists of a delta time of zero, followed by the meta event identifier, end-of-track command, and length field.

## Args:
    self: The MidiTrack instance (implicit)

## Returns:
    bytes: The MIDI end-of-track event byte sequence `b"\x00\xff\x2f\x00"`

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: None
    Postconditions: The returned bytes represent a valid MIDI end-of-track meta event

## Side Effects:
    None: This method has no side effects and is purely a data-returning utility.

### `mingus.midi.midi_track.MidiTrack.play_Note` · *method*

## Summary:
Plays a MIDI note by generating a Note On event and appending it to the track's MIDI data stream.

## Description:
The play_Note method processes a musical note object by converting it into a MIDI Note On event and adding it to the track's data buffer. It handles instrument setup when needed and validates the note's velocity value before creating the MIDI event. This method is part of the core MIDI playback functionality for individual notes within a track.

Known callers include:
- `play_NoteContainer()` - called when playing individual notes from a container
- `play_Bar()` - called when playing notes within a musical bar context
- `play_Track()` - indirectly called when processing tracks with notes

This logic is separated into its own method to encapsulate the specific behavior of playing a single note, making it reusable across different musical contexts while maintaining clean separation of concerns between note processing and higher-level musical structures.

## Args:
    note (Note): A musical note object containing note information including channel, velocity, and pitch.

## Returns:
    None: This method does not return any value.

## Raises:
    AssertionError: Raised when the note's velocity is outside the valid MIDI range (0-127).

## State Changes:
    Attributes READ: self.change_instrument, self.instrument, self.track_data
    Attributes WRITTEN: self.track_data, self.change_instrument

## Constraints:
    Preconditions:
    - The note object must have valid channel and velocity attributes within MIDI ranges
    - The note object must be a valid Note instance from mingus.core.notes
    - The MidiTrack instance must be properly initialized
    
    Postconditions:
    - The note's MIDI data is appended to self.track_data
    - If instrument change was pending, it's marked as completed (self.change_instrument set to False)
    - The note's velocity is validated to be within 0-127 range

## Side Effects:
    - Modifies the track's MIDI data buffer by appending new MIDI events
    - May invoke the set_instrument method when instrument change is pending
    - Writes to the internal track_data attribute which affects the final MIDI file output

### `mingus.midi.midi_track.MidiTrack.play_NoteContainer` · *method*

## Summary:
Plays a container of MIDI notes with synchronized timing by processing the first note separately from the remainder.

## Description:
The play_NoteContainer method processes a collection of MIDI notes by playing them sequentially with proper timing synchronization. When the container has one or zero notes, all notes are played in a single operation. For containers with multiple notes, the first note is played, followed by a delta time reset to zero, then the remaining notes are played. This ensures proper timing alignment for simultaneous note playback while maintaining the ability to handle sequential note events.

Known callers include:
- `play_Bar()` - called during musical bar processing when notes need to be played with proper timing
- `play_Track()` - indirectly called through play_Bar when processing complete musical compositions

This logic is separated into its own method to provide a consistent interface for playing note collections while handling the timing synchronization that's critical for proper MIDI playback. The method implements a recursive-like pattern that avoids potential timing issues when playing multiple notes simultaneously.

## Args:
    notecontainer (list-like): A container of note objects that supports indexing and iteration. Each note object must be compatible with the play_Note method and contain required attributes like channel and velocity.

## Returns:
    None: This method operates on the instance's state and does not return a value.

## Raises:
    AttributeError: If notecontainer doesn't support len(), indexing, or iteration operations
    AssertionError: If individual notes in the container have invalid velocity values when processed by play_Note
    TypeError: If notecontainer is not iterable or contains incompatible note objects

## State Changes:
    Attributes READ: self.track_data
    Attributes WRITTEN: self.track_data, self.delta_time

## Constraints:
    Preconditions:
    - The notecontainer parameter must be iterable and support indexing operations
    - Each note in the container must be compatible with the play_Note method
    - The MidiTrack instance must be properly initialized
    - Individual notes must have valid channel and velocity attributes within MIDI ranges
    
    Postconditions:
    - All notes in the container are processed and added to the track's MIDI data
    - Timing synchronization is maintained through delta time management
    - The instance's track_data is updated with appropriate MIDI events for all notes

## Side Effects:
    - Modifies the track's MIDI data buffer by appending new MIDI events for each note
    - May invoke set_deltatime to manage timing synchronization
    - Calls play_Note for each note in the container, which may trigger additional MIDI operations

### `mingus.midi.midi_track.MidiTrack.play_Bar` · *method*

## Summary:
Processes and plays a musical bar by setting timing context, meter, key, and executing note events with proper timing synchronization.

## Description:
The `play_Bar` method handles the playback of a complete musical bar by processing its constituent events. It establishes the timing context for the bar, sets the meter and key signatures, then iterates through each musical event in the bar. For each event, it calculates the appropriate timing based on note duration and either accumulates delay time or plays the associated note container. This method is responsible for maintaining proper MIDI timing and musical structure when converting a bar of musical data into playable MIDI events.

This method is typically called during sequential playback of musical compositions where bars are processed one at a time, such as when playing a complete track through the `play_Track` method.

## Args:
    bar (object): A musical bar object that must support iteration and have the following attributes:
        - `meter`: Time signature information for the bar (used with `set_meter`)
        - `key`: Musical key information for the bar (used with `set_key`)
        Each item yielded by iterating over the bar must be a tuple of the form (event_type, duration, note_container) where:
        - `event_type`: Identifier for the type of musical event
        - `duration`: Relative duration value used to calculate timing ticks (typically a fraction like 1/4, 1/8)
        - `note_container`: Container of notes to play, or None/empty for timing-only events

## Returns:
    None: This method operates on the instance's state and does not return a value.

## Raises:
    AttributeError: If the bar object lacks required attributes (meter, key) or methods (iteration)
    TypeError: If bar is not iterable or contains incompatible data structures
    AssertionError: If internal MIDI validation fails during note processing
    IndexError: If iteration items don't have sufficient elements for indexing

## State Changes:
    Attributes READ: 
    - self.delay
    - self.bpm
    - self.track_data
    
    Attributes WRITTEN:
    - self.delay: Accumulated delay time for timing synchronization
    - self.track_data: Appended with MIDI events for meter, key, tempo, and note playback

## Constraints:
    Preconditions:
    - The bar parameter must be iterable and yield tuples with at least 3 elements
    - Each event tuple must be in the form (event_type, duration, note_container)
    - The bar must have meter and key attributes that can be processed by set_meter and set_key
    - Note containers must be compatible with play_NoteContainer and stop_NoteContainer methods
    - Duration values must be valid for timing calculations
    
    Postconditions:
    - The instance's track_data contains properly formatted MIDI events for the bar
    - The delay attribute reflects accumulated timing for subsequent events
    - Meter and key information are properly encoded in the MIDI track
    - All musical events in the bar are processed with appropriate timing

## Side Effects:
    - Modifies self.track_data by appending MIDI events
    - May modify self.delay for timing management
    - Calls various MIDI event generation methods that could produce I/O or external state changes
    - Invokes play_NoteContainer and stop_NoteContainer which may trigger additional MIDI operations
    - May call set_tempo when tempo information is detected in note containers

### `mingus.midi.midi_track.MidiTrack.play_Track` · *method*

## Summary:
Processes a musical track by setting track metadata, configuring instrument, and playing each bar sequentially.

## Description:
This method converts a musical track object into MIDI events by processing its constituent bars. It handles track-level metadata like name and instrument configuration, then delegates to `play_Bar` for each individual bar in the track. This method serves as the main entry point for playing complete musical tracks through the MIDI system.

## Args:
    track: A musical track object that must be iterable and contain musical bars. The track object should have:
        - Optional `name` attribute for track naming
        - Optional `instrument` attribute with `instrument_nr` property for instrument setup
        - Iterable interface to allow looping through musical bars

## Returns:
    None: This method operates on the instance's state and does not return a value.

## Raises:
    AttributeError: If the track object lacks required attributes or methods
    TypeError: If the track is not iterable or contains incompatible data structures
    AssertionError: If internal MIDI validation fails during note processing

## State Changes:
    Attributes READ: 
    - self.delay (for resetting)
    - self.change_instrument (for checking instrument change flag)
    - self.instrument (for checking instrument number)
    
    Attributes WRITTEN:
    - self.delay: Reset to 0 at start of processing
    - self.change_instrument: Set to True when instrument change is needed
    - self.instrument: Updated with instrument number when instrument change is needed
    - self.track_data: Modified by appending MIDI events from play_Bar calls

## Constraints:
    Preconditions:
    - The track parameter must be iterable and yield musical bar objects
    - Each bar in the track must be compatible with the `play_Bar` method
    - The track may optionally have a `name` attribute for track naming
    - The track may optionally have an `instrument` attribute with `instrument_nr` property
    
    Postconditions:
    - The instance's track_data contains properly formatted MIDI events for the entire track
    - Instrument configuration is set if track specifies an instrument
    - Track name is set if track specifies a name
    - Delay counter is reset to 0 at start of processing

## Side Effects:
    - Modifies self.track_data by appending MIDI events from bar processing
    - May modify self.delay for timing management
    - May modify self.change_instrument and self.instrument for instrument configuration
    - Calls play_Bar for each bar in the track, which may trigger additional MIDI operations

### `mingus.midi.midi_track.MidiTrack.stop_Note` · *method*

## Summary:
Stops a MIDI note by generating and appending a note-off event to the track's data buffer.

## Description:
This method creates a MIDI note-off event for the specified note and appends it to the track's data buffer. It is typically called during playback operations when notes need to be terminated, such as when processing NoteContainer objects or during bar playback. The method extracts channel and velocity information from the note object and converts the note to its MIDI value by adding 12 to its integer representation.

## Args:
    note: A note-like object with the following attributes:
        - channel (int): MIDI channel number (0-15) specifying which channel to send the note-off event to
        - velocity (int): Velocity value (0-127) indicating how hard the note was released
        - int(note) (int): Integer representation of the note that gets converted to MIDI note number by adding 12

## Returns:
    None

## Raises:
    AssertionError: When parameter validation fails in the underlying note_off method:
        - channel must be between 0 and 15 inclusive
        - note must be between 0 and 127 inclusive
        - velocity must be between 0 and 127 inclusive

## State Changes:
    Attributes READ: self.track_data, self.note_off
    Attributes WRITTEN: self.track_data

## Constraints:
    Preconditions:
        - note must have channel attribute in range [0, 15]
        - note must have velocity attribute in range [0, 127]
        - int(note) must result in a value that when added 12 produces a valid MIDI note number (0-127)
    Postconditions:
        - self.track_data is updated with the note-off event byte sequence
        - The note-off event is properly formatted according to MIDI specifications

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.stop_NoteContainer` · *method*

## Summary:
Stops all notes in a note container by generating note-off events, with special handling for timing synchronization between notes.

## Description:
Processes a container of MIDI notes to generate note-off events for each note. For containers with one or zero notes, it processes all notes sequentially. For containers with multiple notes, it processes the first note, resets timing to zero, then processes the remaining notes. This method is typically called during MIDI playback operations to properly terminate notes in a musical phrase or bar.

The method is designed to handle timing synchronization between notes in a container, ensuring that subsequent notes in a chord or sequence are properly timed relative to the first note.

## Args:
    notecontainer: A collection-like object containing note objects to be stopped. Each note object should have channel and velocity attributes compatible with the stop_Note method.

## Returns:
    None

## Raises:
    AssertionError: When underlying stop_Note calls fail due to invalid note parameters (channel, velocity, or note value ranges).

## State Changes:
    Attributes READ: self.stop_Note, self.set_deltatime
    Attributes WRITTEN: self.track_data (through calls to stop_Note)

## Constraints:
    Preconditions:
        - notecontainer must be iterable and contain valid note objects
        - Each note in notecontainer must have valid channel and velocity attributes
        - Each note's integer representation must be compatible with MIDI note numbering
    Postconditions:
        - All notes in the container will have corresponding note-off events appended to self.track_data
        - Timing is properly synchronized between notes in multi-note containers

## Side Effects:
    None beyond modifications to the track's data buffer via stop_Note calls.

### `mingus.midi.midi_track.MidiTrack.set_instrument` · *method*

## Summary:
Sets the instrument and bank for a specified MIDI channel by appending MIDI bank selection and program change events to the track data.

## Description:
Configures a MIDI channel with a specific instrument and bank number for subsequent note playback. This method is typically called during the track initialization or playback setup phase when preparing to play notes on a particular channel. It combines two MIDI events: a bank selection controller event followed by a program change event to set the instrument. The method is part of the MIDI track management system used for generating MIDI files.

## Args:
    channel (int): The MIDI channel number (0-15) to configure for the instrument.
    instr (int): The instrument/program number (0-127) to assign to the channel.
    bank (int): The bank number (0-127) to select for the channel (default is 1).

## Returns:
    None: This method does not return a value.

## Raises:
    AssertionError: May be raised if parameter validation fails in the underlying helper methods (`select_bank` or `program_change_event`), particularly if channel or instrument numbers are out of valid ranges.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.track_data (modified by appending bank selection and program change events)

## Constraints:
    Preconditions:
        - Channel must be a valid MIDI channel number (0-15)
        - Instrument must be a valid program number (0-127)
        - Bank must be a valid bank number (0-127)
        - The MidiTrack instance must be properly initialized

    Postconditions:
        - The track_data attribute contains the bank selection and program change events for the specified channel
        - The specified channel is configured with the requested instrument and bank

## Side Effects:
    None: This method only modifies the internal track_data attribute and does not perform any I/O operations or external service calls.

### `mingus.midi.midi_track.MidiTrack.header` · *method*

## Summary:
Constructs and returns the MIDI track header for the current track data.

## Description:
Generates the standard MIDI track header that precedes the track data in a MIDI file. This method calculates the total size of the track data including the end-of-track event and formats it according to the MIDI file specification. The header consists of the track header identifier followed by the calculated chunk size in big-endian format.

This method is separated from other track operations to encapsulate the MIDI file format header construction logic, making it reusable and keeping the track data management concerns separate from the file format details.

## Args:
    self: The MidiTrack instance (implicit)

## Returns:
    bytes: A MIDI track header consisting of TRACK_HEADER identifier followed by 4-byte chunk size

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: self.track_data, self.end_of_track()
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.track_data should be a bytes object containing valid MIDI events
    - self.end_of_track() should return a valid end-of-track meta event
    Postconditions:
    - The returned bytes form a valid MIDI track header
    - The chunk size accurately reflects the total track data size

## Side Effects:
    None: This method performs no I/O or external service calls. It only processes internal state to construct a header.

### `mingus.midi.midi_track.MidiTrack.get_midi_data` · *method*

## Summary:
Returns the complete MIDI track data by combining the track header, track events, and end-of-track marker.

## Description:
Constructs and returns the complete MIDI track data by concatenating three components: the track header (which contains metadata about the track size), the track event data (containing all MIDI events), and the end-of-track marker. This method serves as the primary interface for retrieving the complete serialized MIDI track data for a given track.

This method is called during the MIDI file construction process when all track data needs to be assembled into a complete track structure. It's designed as a separate method rather than being inlined because it provides a clean abstraction for building the complete track data structure and makes testing easier by isolating this specific functionality.

## Args:
    self: The MidiTrack instance (implicit)

## Returns:
    bytes: A byte string containing the complete MIDI track data, consisting of:
        - Track header (including size information calculated from track data and end-of-track marker)
        - Track event data (all MIDI events recorded in the track)
        - End-of-track marker

## Raises:
    None: This method does not explicitly raise any exceptions.

## State Changes:
    Attributes READ: 
        - self.track_data (contains all MIDI events)
    Methods CALLED:
        - self.header() (returns track header with size calculation)
        - self.end_of_track() (returns end-of-track marker)
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
        - The MidiTrack instance must have been properly initialized
        - All MIDI events must have been added to self.track_data via methods like play_Note, play_NoteContainer, etc.
    Postconditions: 
        - Returns a properly formatted MIDI track structure
        - The returned data is ready for inclusion in a complete MIDI file

## Side Effects:
    None: This method has no side effects and is purely a data-returning utility.

### `mingus.midi.midi_track.MidiTrack.midi_event` · *method*

## Summary:
Constructs and returns a MIDI event byte sequence for a given event type, channel, and parameters.

## Description:
This method creates a MIDI event by combining a delta time with a status byte and parameter bytes. It's used internally by other methods in the MidiTrack class to build various MIDI events such as note on/off events, controller events, and program changes. The method ensures proper MIDI protocol formatting by constructing the status byte according to MIDI specifications.

## Args:
    event_type (int): MIDI event type (0-15). Valid values correspond to standard MIDI event types.
    channel (int): MIDI channel number (0-15). Specifies which channel the event should be sent to.
    param1 (int): First parameter for the MIDI event (0-127). Typically represents note number or controller number.
    param2 (int, optional): Second parameter for the MIDI event (0-127). Used for velocity values or controller values. Defaults to None.

## Returns:
    bytes: A byte sequence representing the complete MIDI event, consisting of delta time followed by status byte and parameter bytes.

## Raises:
    AssertionError: When any of the parameter validation conditions fail:
        - event_type must be between 0 and 15 inclusive
        - channel must be between 0 and 15 inclusive  
        - param1 must be between 0 and 127 inclusive
        - param2 must be None or between 0 and 127 inclusive

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - event_type must be in range [0, 15]
        - channel must be in range [0, 15]
        - param1 must be in range [0, 127]
        - param2 must be None or in range [0, 127]
    Postconditions:
        - Returns a properly formatted MIDI event byte sequence
        - The returned bytes include the delta time prefix

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.note_off` · *method*

## Summary:
Turns off a MIDI note by creating and returning a note-off event byte sequence.

## Description:
This method constructs a MIDI note-off event for the specified channel, note, and velocity. It serves as a wrapper around the internal `midi_event` method to create standardized MIDI note-off messages. The method is typically called when stopping notes in musical sequences, such as when processing NoteContainer objects or during playback operations.

## Args:
    channel (int): MIDI channel number (0-15) specifying which channel to send the note-off event to.
    note (int): MIDI note number (0-127) representing the note to turn off.
    velocity (int): Velocity value (0-127) indicating how hard the note was released.

## Returns:
    bytes: A byte sequence representing the MIDI note-off event, including delta time prefix and properly formatted status byte.

## Raises:
    AssertionError: When parameter validation fails in the underlying midi_event method:
        - channel must be between 0 and 15 inclusive
        - note must be between 0 and 127 inclusive
        - velocity must be between 0 and 127 inclusive

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - channel must be in range [0, 15]
        - note must be in range [0, 127]
        - velocity must be in range [0, 127]
    Postconditions:
        - Returns a properly formatted MIDI note-off event byte sequence
        - The returned bytes include the delta time prefix

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.note_on` · *method*

## Summary:
Initiates a MIDI Note On event by calling the midi_event method with appropriate parameters.

## Description:
This method serves as a specialized interface for creating MIDI Note On events. It delegates the actual event creation and processing to the midi_event method, passing NOTE_ON as the event type along with the provided channel, note, and velocity parameters.

## Args:
    channel (int): The MIDI channel number where the note will be played.
    note (int): The MIDI note number representing the pitch of the note.
    velocity (int): The velocity value indicating the intensity or attack of the note.

## Returns:
    The return value is determined by the midi_event method implementation.

## Raises:
    Exceptions may be raised by the midi_event method if invalid parameters are provided.

## State Changes:
    Attributes READ: None explicitly mentioned
    Attributes WRITTEN: None explicitly mentioned (state changes depend on midi_event implementation)

## Constraints:
    Preconditions: 
    - Channel, note, and velocity parameters must be compatible with the midi_event method's expectations
    - Parameters should conform to standard MIDI value ranges
    
    Postconditions: 
    - A Note On MIDI event is processed through the midi_event mechanism

## Side Effects:
    This method may cause side effects such as writing MIDI data or modifying internal state through the midi_event method.

### `mingus.midi.midi_track.MidiTrack.controller_event` · *method*

## Summary:
Creates a MIDI controller event for the specified channel and controller parameters.

## Description:
This method generates a MIDI controller event by delegating to the underlying `midi_event` method with the appropriate event type constant. It's designed to simplify the creation of MIDI controller messages, which are commonly used to control various aspects of sound synthesis such as volume, pan, modulation, etc.

## Args:
    channel (int): The MIDI channel number (0-15) for the controller event.
    contr_nr (int): The controller number (0-127) specifying which controller to affect.
    contr_val (int): The controller value (0-127) specifying the controller setting.

## Returns:
    bytes: A byte string representing the complete MIDI controller event message.

## Raises:
    AssertionError: If any of the parameter constraints are violated (channel, controller number, or controller value out of valid range).

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Channel must be between 0 and 15 inclusive
    - Controller number must be between 0 and 127 inclusive
    - Controller value must be between 0 and 127 inclusive
    
    Postconditions:
    - Returns a properly formatted MIDI event byte sequence
    - The returned bytes include the delta time prefix

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.reset` · *method*

## Summary:
Resets the MIDI track's data and delta time to their initial empty states.

## Description:
Clears the accumulated MIDI events and resets the time delta tracking for a MidiTrack instance. This method is typically called when reusing a MidiTrack object for processing new musical content, ensuring clean state before beginning new MIDI data generation.

## Args:
    None

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.track_data: Set to empty byte string (b"")
    - self.delta_time: Set to null byte string (b"\x00")

## Constraints:
    Preconditions: None
    Postconditions: 
    - self.track_data is an empty byte string
    - self.delta_time is a null byte string

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.set_deltatime` · *method*

## Summary:
Sets the delta time for MIDI events in the track, converting integer values to variable-length byte format.

## Description:
Configures the delta time value used for timing MIDI events within the track. When an integer is provided, it's converted to MIDI's variable-length byte format using the class's `int_to_varbyte` method. This ensures proper MIDI file format compliance for event timing.

The method is called during various MIDI track construction phases including note playback, tempo changes, meter setting, key signatures, and track naming operations to maintain proper timing between events.

## Args:
    delta_time (int or bytes): Delta time value in ticks (integer) or pre-encoded variable-length bytes. If integer, it will be converted to variable-length format.

## Returns:
    None

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.delta_time

## Constraints:
    Preconditions: The delta_time parameter should be a non-negative integer or valid bytes object.
    Postconditions: The self.delta_time attribute is updated with either the provided bytes or the variable-length encoded version of an integer.

## Side Effects:
    None beyond updating the instance's delta_time attribute.

### `mingus.midi.midi_track.MidiTrack.select_bank` · *method*

## Summary:
Selects a MIDI bank for the specified channel by sending a bank select controller event.

## Description:
This method sends a MIDI bank select controller event to the specified channel with the given bank number. It is a convenience method that wraps the generic controller_event method specifically for bank selection operations in MIDI tracks.

## Args:
    channel (int): The MIDI channel number to send the bank select event to.
    bank (int): The bank number to select.

## Returns:
    The return value of self.controller_event(BANK_SELECT, channel, bank).

## Raises:
    This method may raise any exceptions that self.controller_event may raise.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The channel parameter should be a valid MIDI channel number
    - The bank parameter should be a valid bank number
    - The MidiTrack instance must be properly initialized
    
    Postconditions:
    - A bank select controller event is sent to the specified channel
    - The method returns the result of the controller_event call

## Side Effects:
    This method likely generates MIDI output data that will be written to the MIDI file when the track is finalized.

### `mingus.midi.midi_track.MidiTrack.program_change_event` · *method*

## Summary:
Creates and returns a MIDI program change event byte sequence for the specified channel and instrument.

## Description:
This method generates a MIDI program change event, which is used to switch the instrument or sound patch on a specific MIDI channel. It serves as a specialized interface for creating program change messages by delegating to the internal `midi_event` method with the appropriate event type constant. Program change events are commonly used in MIDI sequences to change instruments during playback.

## Args:
    channel (int): The MIDI channel number (0-15) on which to change the program/instrument.
    instr (int): The instrument/program number (0-127) to select for the specified channel.

## Returns:
    bytes: A byte sequence representing the complete MIDI program change event, including delta time prefix and properly formatted status byte.

## Raises:
    AssertionError: When parameter validation fails in the underlying midi_event method:
        - channel must be between 0 and 15 inclusive
        - instr must be between 0 and 127 inclusive

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - channel must be in range [0, 15]
        - instr must be in range [0, 127]
    Postconditions:
        - Returns a properly formatted MIDI program change event byte sequence
        - The returned bytes include the delta time prefix

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.set_tempo` · *method*

## Summary:
Sets the tempo of the MIDI track and appends the corresponding tempo event to the track data.

## Description:
This method updates the track's tempo in beats per minute (BPM) and adds the appropriate MIDI tempo event to the track's data buffer. The tempo event is created using the `set_tempo_event` helper method and is prepended with the current delta time.

## Args:
    bpm (int): The tempo in beats per minute. Must be a positive integer.

## Returns:
    None: This method does not return a value.

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: self.bpm, self.track_data, self.delta_time
    Attributes WRITTEN: self.bpm, self.track_data

## Constraints:
    Preconditions: bpm must be a positive integer
    Postconditions: self.bpm is updated to the provided value, and self.track_data contains the tempo event

## Side Effects:
    None: This method only modifies internal state attributes and does not perform I/O or external service calls.

### `mingus.midi.midi_track.MidiTrack.set_tempo_event` · *method*

## Summary:
Creates a MIDI meta event for setting the tempo in microseconds per quarter note.

## Description:
Constructs a properly formatted MIDI meta event that specifies the tempo of the track. This method calculates the microseconds per quarter note (MPQN) from the provided BPM value and formats it according to the MIDI specification. The resulting event includes the delta time prefix, meta event type identifier, set tempo command, length indicator, and the 3-byte MPQN value. This method is primarily used internally by the `set_tempo` method to generate tempo events.

## Args:
    bpm (int): The tempo in beats per minute. Must be a positive integer greater than 0.

## Returns:
    bytes: A byte string representing the complete MIDI meta event for tempo setting, including:
        - Delta time prefix (from self.delta_time)
        - Meta event type identifier (META_EVENT constant)
        - Set tempo command (SET_TEMPO constant) 
        - Length byte (b"\x03")
        - 3-byte microseconds per quarter note value (mpqn)

## Raises:
    None explicitly raised by this method.

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None - this method is pure and doesn't modify object state

## Constraints:
    Preconditions: bpm must be a positive integer (> 0)
    Postconditions: Returns a properly formatted MIDI meta event with correct MPQN calculation

## Side Effects:
    None: This method is pure and only performs calculations and returns bytes without any side effects.

### `mingus.midi.midi_track.MidiTrack.set_meter` · *method*

## Summary:
Sets the time signature for a MIDI track by appending a time signature meta event to the track's data.

## Description:
This method configures the time signature of a MIDI track by creating and appending a time signature meta event to the track's data buffer. It's typically called during the playback of musical bars via the `play_Bar` method to establish the rhythmic structure for each bar. The method delegates the actual creation of the MIDI event to the `time_signature_event` helper method.

## Args:
    meter (tuple[int, int]): The time signature as a tuple of (numerator, denominator). Defaults to (4, 4). The denominator must be a power of 2 for proper conversion.

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: When the denominator in meter is not a power of 2, causing a logarithm error in the internal conversion.
    TypeError: When meter is not a tuple or contains non-numeric values.

## State Changes:
    Attributes READ: self.delta_time, self.track_data
    Attributes WRITTEN: self.track_data

## Constraints:
    Preconditions: The meter tuple must contain valid numeric values where the denominator is a power of 2 for proper conversion.
    Postconditions: The track_data attribute will contain the appended time signature meta event.

## Side Effects:
    Mutates the self.track_data attribute by appending new MIDI event data.

### `mingus.midi.midi_track.MidiTrack.time_signature_event` · *method*

## Summary:
Creates a MIDI time signature meta event for the specified meter and returns the encoded event bytes.

## Description:
Generates a MIDI time signature meta event that defines the rhythmic structure for a musical piece. This method is part of the MidiTrack class and is primarily used internally by the `set_meter` method to encode time signature information into the MIDI track data. The resulting event follows the standard MIDI meta event format for time signatures, specifying numerator, denominator (stored as power of 2), metronome pulse, and 32nd note divisions.

The method is called during playback when establishing the time signature for musical bars, particularly through the `play_Bar` method which invokes `set_meter` for each bar's time signature. The returned bytes represent a complete MIDI meta event ready to be appended to the track's data.

This method exists to encapsulate the complex process of converting a time signature tuple into the proper MIDI binary format, ensuring consistent and correct MIDI event generation throughout the music composition pipeline.

## Args:
    meter (tuple[int, int]): The time signature as a tuple of (numerator, denominator). Defaults to (4, 4). The denominator must be a power of 2 for proper conversion.

## Returns:
    bytes: A complete MIDI meta event containing the time signature information, formatted according to MIDI specifications. The structure follows: delta_time + META_EVENT + TIME_SIGNATURE + length + numerator + denominator + metronome + 32nd_notes.

## Raises:
    ValueError: When the denominator in meter is not a power of 2, causing a logarithm error in the internal conversion.
    TypeError: When meter is not a tuple or contains non-numeric values.

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The meter tuple must contain valid numeric values where the denominator is a power of 2 for proper conversion.
    Postconditions: The returned bytes represent a valid MIDI time signature meta event.

## Side Effects:
    None: This method is pure and does not cause any external side effects or mutations beyond returning the constructed MIDI event bytes.

### `mingus.midi.midi_track.MidiTrack.set_key` · *method*

## Summary:
Sets the key signature for a MIDI track by appending a key signature meta event to the track's data.

## Description:
Configures the musical key signature for the MIDI track. This method accepts either a string representation of a key (like "C", "a", "G#") or a Key object, converts it to the appropriate format, and adds the corresponding key signature meta event to the track's data stream. The method is typically called during the playback of musical bars to establish the tonal center for subsequent notes.

## Args:
    key (str or Key): Musical key specification. Can be a string representing a key (e.g., "C", "a", "G#") or a Key object. Defaults to "C" (C major).

## Returns:
    None: This method does not return a value.

## Raises:
    ValueError: If the key parameter is not found in either major_keys or minor_keys lists.
    IndexError: If the key parameter is not found in the major_keys or minor_keys lists (when using .index() method).

## State Changes:
    Attributes READ: self.track_data
    Attributes WRITTEN: self.track_data

## Constraints:
    Preconditions:
    - The key parameter must be a valid key name present in either major_keys or minor_keys lists
    - The method assumes proper MIDI event structure constants are available
    
    Postconditions:
    - The track_data attribute is updated with a key signature meta event
    - If a Key object is passed, it's converted to its string representation before processing

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.key_signature_event` · *method*

## Summary:
Generates a MIDI key signature meta event for the specified musical key.

## Description:
Creates a properly formatted MIDI meta event containing key signature information. This method encodes musical key signatures (major or minor) into MIDI tracks. The method determines whether the key is major or minor based on case, calculates an offset value from standard key indexing, handles negative values appropriately, and formats the result as a complete MIDI meta event.

## Args:
    key (str): Musical key name, defaults to "C". Should be a key present in major_keys or minor_keys lists. Major keys are uppercase (e.g., "C", "G"), minor keys are lowercase (e.g., "c", "g").

## Returns:
    bytes: A complete MIDI meta event containing key signature data, consisting of delta time, meta event identifier, key signature type, length field (2 bytes), key value (1 byte), and mode indicator (1 byte).

## Raises:
    ValueError: If the key parameter is not found in either major_keys or minor_keys lists.
    IndexError: If the key parameter is not found in the major_keys or minor_keys lists (when using .index() method).

## State Changes:
    Attributes READ: self.delta_time
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The key parameter must be a valid key name present in either major_keys or minor_keys lists
    - The method assumes proper MIDI event structure constants are available
    
    Postconditions:
    - Returns a properly formatted MIDI meta event bytes object
    - The key value calculation accounts for MIDI key signature standard where C major/A minor is represented as 0

## Side Effects:
    None

### `mingus.midi.midi_track.MidiTrack.set_track_name` · *method*

## Summary:
Sets the name of the MIDI track by appending a track name meta event to the track data.

## Description:
This method configures the MIDI track's name by creating and appending a properly formatted track name meta event to the track's data buffer. It is used to assign human-readable names to MIDI tracks, which is useful for identifying tracks in MIDI files. This method is typically called during the construction of a MIDI track when a track name is available.

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
    Preconditions: The name parameter must be a valid ASCII string.
    Postconditions: The track_data attribute will contain the track name meta event appended to existing data.

## Side Effects:
    None: This method only modifies the internal track_data attribute and has no external side effects.

### `mingus.midi.midi_track.MidiTrack.track_name_event` · *method*

## Summary:
Creates a MIDI meta event for setting the track name in a MIDI file.

## Description:
Generates a properly formatted MIDI meta event that sets the track name for the current MIDI track. This method is used internally by the `set_track_name` method to append track name events to the track data. The resulting event follows the standard MIDI meta event format with appropriate variable-length encoding for the event length.

## Args:
    name (str): The track name to set. Must be ASCII-compatible.

## Returns:
    bytes: A complete MIDI meta event containing the track name, formatted according to MIDI specifications with proper variable-length encoding for the event length.

## Raises:
    UnicodeEncodeError: If the name parameter contains non-ASCII characters that cannot be encoded.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The name parameter must be a string that can be encoded to ASCII.
    Postconditions: The returned bytes represent a valid MIDI meta event for track naming.

## Side Effects:
    None beyond computation and returning bytes.

### `mingus.midi.midi_track.MidiTrack.int_to_varbyte` · *method*

## Summary:
Converts an integer value to MIDI variable-length byte representation for use in MIDI event timing and metadata.

## Description:
This method transforms an integer into a variable-length byte sequence following the MIDI standard format. Each byte contains 7 bits of data with the most significant bit indicating if more bytes follow. This encoding is used in MIDI files for representing delta times and metadata lengths.

The method is called during MIDI track construction when encoding delta times (in `set_deltatime`) and metadata lengths (in `track_name_event`), ensuring proper MIDI file format compliance.

## Args:
    value (int): The integer value to convert to variable-length byte format. Must be non-negative.

## Returns:
    bytes: A byte string containing the variable-length encoded representation of the input value. Returns empty bytes for value=0.

## Raises:
    None explicitly raised, but may raise exceptions from underlying operations like log() or pack() with invalid inputs.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input value must be a non-negative integer.
    Postconditions: The returned bytes represent the input value in MIDI variable-length format with proper continuation bits set.

## Side Effects:
    None beyond computation and returning bytes.

