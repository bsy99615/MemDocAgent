# `win32midisequencer.py`

## `mingus.midi.win32midisequencer.Win32MidiSequencer` · *class*

## Summary:
Windows-specific MIDI sequencer that interfaces with the Win32 MIDI API to play musical events.

## Description:
The Win32MidiSequencer is a platform-specific implementation of the Sequencer abstract base class designed exclusively for Windows systems. It provides low-level MIDI event playback capabilities by utilizing the Windows multimedia MIDI API through the Win32MidiPlayer wrapper. This class serves as a bridge between higher-level music composition objects and the Windows-specific MIDI hardware or software synthesizer.

This class should be instantiated when MIDI playback is required on Windows platforms. It is typically created by factory methods or constructors that select platform-appropriate sequencer implementations.

## State:
- `output`: None (class attribute, likely unused or inherited)
- `midplayer`: Instance of Win32MidiPlayer used for actual MIDI communication
  - Type: Win32MidiPlayer
  - Valid range: Initialized Win32MidiPlayer instance
  - Invariant: Must be initialized via `init()` before use

## Lifecycle:
- Creation: Instantiate with `Win32MidiSequencer()` constructor, but the actual MIDI device initialization happens in the `init()` method
- Usage: Call `init()` to initialize the Windows MIDI device, then use event methods (`play_event`, `stop_event`, `cc_event`, `instr_event`) to send MIDI messages
- Destruction: Automatically closes the MIDI device when the object is garbage collected via `__del__` method

## Method Map:
```mermaid
graph TD
    A[Win32MidiSequencer] --> B[init()]
    A --> C[play_event]
    A --> D[stop_event]
    A --> E[cc_event]
    A --> F[instr_event]
    A --> G[__del__]
    B --> H[Win32MidiPlayer.openDevice()]
    C --> I[Win32MidiPlayer.rawNoteOn()]
    D --> J[Win32MidiPlayer.rawNoteOff()]
    E --> K[Win32MidiPlayer.controllerChange()]
    F --> L[Win32MidiPlayer.programChange()]
    G --> M[Win32MidiPlayer.closeDevice()]
```

## Raises:
- RuntimeError: Raised in `init()` method when the platform is not Windows (sys.platform != "win32")

## Example:
```python
# Create and initialize the sequencer
sequencer = Win32MidiSequencer()
sequencer.init()  # Initializes Windows MIDI device

# Play a note (C4, channel 1, velocity 100)
sequencer.play_event(60, 1, 100)

# Change instrument on channel 1
sequencer.instr_event(1, 40, 0)  # Piano instrument

# Stop the note
sequencer.stop_event(60, 1)

# Clean up
del sequencer  # Automatically closes MIDI device
```

### `mingus.midi.win32midisequencer.Win32MidiSequencer.init` · *method*

## Summary:
Initializes a Windows-specific MIDI sequencer by creating and opening a MIDI player device.

## Description:
This method sets up the MIDI playback functionality for Windows platforms by instantiating a Win32MidiPlayer and opening the default MIDI device. It is intended to be called during the initialization phase of a Win32MidiSequencer object and should only be used on Windows systems.

## Args:
    None

## Returns:
    None

## Raises:
    RuntimeError: When called on a non-Windows platform (sys.platform != "win32")

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self.midplayer: Assigned a new Win32MidiPlayer instance

## Constraints:
    Preconditions: 
    - Must be running on a Windows platform (sys.platform == "win32")
    - The Win32MidiPlayer class must be available and functional
    
    Postconditions:
    - self.midplayer is initialized as a Win32MidiPlayer instance
    - The MIDI device is opened and ready for playback operations

## Side Effects:
    - Creates a new Win32MidiPlayer instance
    - Opens the default MIDI device through the Windows multimedia API
    - May cause system-level I/O operations related to MIDI device access

### `mingus.midi.win32midisequencer.Win32MidiSequencer.__del__` · *method*

## Summary:
Cleans up MIDI device resources when the Win32MidiSequencer object is destroyed.

## Description:
This special destructor method is automatically called by Python's garbage collector when a Win32MidiSequencer instance is being destroyed. It ensures proper cleanup of the underlying Windows MIDI device by closing the midplayer connection.

## Args:
    None

## Returns:
    None

## Raises:
    AttributeError: If self.midplayer is None (when the object was not properly initialized)
    Exception: Any exception raised by the underlying win32midi.closeDevice() implementation

## State Changes:
    Attributes READ: self.midplayer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have been initialized (midplayer should be set)
    Postconditions: The MIDI device connection is closed and resources are released

## Side Effects:
    I/O operation: Calls win32midi.closeDevice() which closes the Windows MIDI device handle
    Resource cleanup: Releases system resources associated with the MIDI player

### `mingus.midi.win32midisequencer.Win32MidiSequencer.play_event` · *method*

## Summary:
Plays a MIDI note event by sending a raw note-on message to the Windows MIDI player.

## Description:
This method implements the abstract play_event interface defined in the Sequencer base class. It serves as a Windows-specific implementation that forwards note-on commands to the underlying MIDI player. This method is typically called during the playback of musical sequences when individual notes need to be triggered.

## Args:
    note (int): MIDI note number (0-127), where 60 represents middle C
    channel (int): MIDI channel number (0-15), representing one of 16 available channels  
    velocity (int): Note velocity (0-127), indicating how hard the note was struck

## Returns:
    None: This method does not return any value

## Raises:
    AttributeError: If self.midplayer is not properly initialized or does not have a rawNoteOn method

## State Changes:
    Attributes READ: self.midplayer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.midplayer must be initialized and have a rawNoteOn method
    - note must be in the range [0, 127] (standard MIDI note range)
    - channel must be in the range [0, 15] (standard MIDI channel range)
    - velocity must be in the range [0, 127] (standard MIDI velocity range)
    
    Postconditions: 
    - The MIDI note-on message is sent to the underlying Windows MIDI device
    - No changes are made to the Win32MidiSequencer object's state

## Side Effects:
    - Direct interaction with the Windows MIDI subsystem via the midplayer
    - May cause audible sound output depending on system MIDI configuration
    - Potential blocking operation during MIDI message transmission

### `mingus.midi.win32midisequencer.Win32MidiSequencer.stop_event` · *method*

## Summary:
Stops a MIDI note by sending a note-off message to the MIDI player.

## Description:
This method implements the abstract stop_event interface defined in the parent Sequencer class. It sends a MIDI note-off message to stop a previously played note on the specified channel. This method is typically called as part of the MIDI playback lifecycle when a note needs to be terminated before its natural duration ends.

## Args:
    note (int): The MIDI note number (pitch) to stop, typically in the range 0-127
    channel (int): The MIDI channel number (1-16) on which to stop the note

## Returns:
    None: This method does not return a value

## Raises:
    Win32MidiException: Raised when the underlying MIDI system fails to send the note-off message, typically due to invalid device handles or hardware errors

## State Changes:
    Attributes READ: self.midplayer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The Win32MidiSequencer must have been properly initialized with a valid midplayer
    - The note parameter must be a valid MIDI note number (typically 0-127)
    - The channel parameter must be a valid MIDI channel (typically 1-16)
    - The MIDI device must be open and available for communication
    
    Postconditions:
    - A MIDI note-off message is sent to the hardware
    - The note stops playing on the specified channel

## Side Effects:
    - Sends a raw MIDI message to the Windows multimedia MIDI API
    - May raise Win32MidiException if MIDI communication fails
    - Direct interaction with Windows audio hardware through the winmm.dll

### `mingus.midi.win32midisequencer.Win32MidiSequencer.cc_event` · *method*

## Summary:
Sets a MIDI controller value on a specific channel, sending a controller change message to the MIDI device.

## Description:
This method provides a standardized interface for sending MIDI controller change messages. It wraps the underlying Win32 MIDI player's controllerChange method, reordering parameters to match the expected interface of the Sequencer base class. This method is part of the MIDI sequencing pipeline where controller events are processed and sent to the MIDI output device.

## Args:
    channel (int): The MIDI channel number (typically 1-16) to send the controller change on
    control (int): The controller number (0-127) to change
    value (int): The value to set the controller to (0-127)

## Returns:
    None: This method does not return a value

## Raises:
    Win32MidiException: Raised when the MIDI device fails to process the controller change message due to hardware errors or invalid parameters

## State Changes:
    Attributes READ: self.midplayer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The Win32MidiSequencer must be initialized (midplayer should be a valid Win32MidiPlayer instance)
    - Channel must be a valid MIDI channel number (typically 1-16)
    - Control and value must be within the valid MIDI controller range (0-127)
    Postconditions: 
    - The controller change message is sent to the MIDI output device
    - No changes are made to the Win32MidiSequencer object's state

## Side Effects:
    I/O: Sends a MIDI controller change message to the Windows MIDI output device via the Win32 multimedia API
    External service calls: Calls win32midi.Win32MidiPlayer.controllerChange() which interacts with the Windows multimedia subsystem

### `mingus.midi.win32midisequencer.Win32MidiSequencer.instr_event` · *method*

## Summary:
Sets the instrument for a specified MIDI channel by sending a program change message.

## Description:
This method sends a MIDI program change message to set the instrument for the specified channel. It is called internally by the `set_instrument` method when changing instruments in the sequencer. The method delegates to the underlying Win32 MIDI player to send the appropriate MIDI message.

## Args:
    channel (int): The MIDI channel number (typically 1-16) to set the instrument for.
    instr (int): The instrument program number to select (0-127).
    bank (int): The bank number (0-127), though this parameter is currently unused in the implementation.

## Returns:
    None: This method does not return any value.

## Raises:
    Win32MidiException: Raised when the underlying MIDI device fails to process the program change message.

## State Changes:
    Attributes READ: self.midplayer
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - The Win32MidiSequencer must be initialized (midplayer should be open)
    - Channel must be a valid MIDI channel number
    - Instrument must be a valid program number (0-127)
    
    Postconditions:
    - The specified MIDI channel will use the requested instrument
    - No changes to the Win32MidiSequencer object state beyond the MIDI message transmission

## Side Effects:
    - Sends a MIDI program change message to the connected MIDI device
    - May raise Win32MidiException if MIDI communication fails

