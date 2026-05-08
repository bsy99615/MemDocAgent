# `win32midi.py`

## `mingus.midi.win32midi.Win32MidiException` · *class*

*No documentation generated.*

## `mingus.midi.win32midi.Win32MidiPlayer` · *class*

## Summary:
A thin Windows (winmm) MIDI output player that opens a MIDI output device and sends short MIDI messages (note on/off, program change, controller change) using ctypes.windll.winmm.

## Description:
Win32MidiPlayer is a small OS-specific abstraction for sending MIDI short messages on Microsoft Windows via the WinMM library (windll.winmm). Instantiate this class when you need to enumerate MIDI output devices and send simple MIDI events (single notes, raw note on/off, program changes, controller changes) using the system MIDI mapper or a specific device.

Typical scenarios:
- A caller that wants to play short test notes or simple MIDI events from Python on Windows.
- A higher-level sequencer/player that delegates single-note sends or channel changes to this class.

Responsibility boundary:
- This class is responsible only for opening/closing a WinMM MIDI output device and sending synchronous short messages via midiOutShortMsg. It does not provide timing/scheduling beyond a blocking sleep in sendNote, nor does it implement MIDI streaming, buffered SysEx, or asynchronous event handling.

Known callers/factories:
- Users or higher-level MIDI playback modules will instantiate this class directly. No factory functions are defined here.

## State:
- midiOutOpenErrorCodes (dict[int, str])
  - Purpose: Human-readable mapping for error codes returned by midiOutOpen.
  - Contents: Integer keys (return codes) mapped to explanatory strings.
  - Invariant: Read-only after __init__.

- midiOutShortErrorCodes (dict[int, str])
  - Purpose: Human-readable mapping for error codes returned by midiOutShortMsg.
  - Contents: Integer keys (return codes) mapped to explanatory strings.
  - Invariant: Read-only after __init__.

- winmm (ctypes library handle)
  - Type: object (ctypes windll module returning a WinMM DLL interface)
  - Value: windll.winmm (bound at construction)
  - Constraint: Only valid on Windows where windll.winmm exists. Methods call functions exposed on this object:
    - midiOutGetNumDevs() -> int
    - midiOutOpen(hMidiOut*, deviceID, callback, instance, flags) -> rc
    - midiOutClose(hMidiOut) -> rc
    - midiOutShortMsg(hMidiOut, message) -> rc

- hmidi (ctypes.c_void_p) — created in openDevice
  - Type: ctypes.c_void_p
  - Initialization: Not present until openDevice() is called; openDevice sets self.hmidi = c_void_p() and passes a pointer to winmm.midiOutOpen.
  - Valid range: Represents an opaque WinMM handle when openDevice succeeds. Do not use send/other methods before openDevice; they expect a valid hmidi attribute.
  - Invariant: After openDevice returns successfully, self.hmidi must point to an open device handle until closeDevice() is called. After closeDevice(), the handle is no longer valid.

Class invariants:
- winmm must be available (implies running on Windows). If windll.winmm is not available, operations will raise attribute or OS-related errors (not wrapped by this class).
- openDevice() must be called successfully before invoking any send* methods or closeDevice(); otherwise attribute or runtime errors will occur.
- Every call that invokes a WinMM function checks the returned result code and raises Win32MidiException on non-zero return codes with a message derived from the appropriate error-code dictionary.

## Lifecycle:
Creation:
- Instantiate with no arguments:
  - player = Win32MidiPlayer()

Usage (typical sequence):
1. Optionally check device count:
   - count = player.countDevices()
   - countDevices returns the integer returned by winmm.midiOutGetNumDevs().
2. Open a MIDI output device:
   - player.openDevice(deviceNumber=-1)
   - deviceNumber default -1 selects the system MIDI mapper (typical default). You may pass an integer device index returned by countDevices() - 1, but exact device indices depend on the host.
   - On failure openDevice raises Win32MidiException.
3. Send events:
   - player.sendNote(pitch, duration=1.0, channel=1, volume=60)
     - Synchronously sends NOTE ON then sleeps for duration seconds then sends NOTE OFF.
   - Alternatively call lower-level methods without sleep:
     - player.rawNoteOn(pitch, channel=1, v=60)
     - player.rawNoteOff(pitch, channel=1)
   - Control the instrument and controllers:
     - player.programChange(program, channel=1)
     - player.controllerChange(controller, val, channel=1)
   - All send methods require a previously opened device (hmidi) and will raise Win32MidiException on WinMM error return codes.
4. Close device:
   - player.closeDevice()
   - Always close when finished to free system resources.

Destruction / cleanup:
- There is no context-manager support implemented. Callers should ensure closeDevice() is invoked (for example, in a try/finally block). If the Python process exits without closing, the OS should clean up resources, but relying on that is discouraged.

Sequencing requirements:
- openDevice must be called before any raw/send methods or closeDevice.
- closeDevice should be called exactly once after usage; calling closeDevice twice may cause WinMM to return an error (and will raise Win32MidiException).

## Method Map:
graph TD
    A[countDevices()] -->|independent| B[openDevice(deviceNumber=-1)]
    B --> C[rawNoteOn(pitch, channel, v)]
    C --> D[rawNoteOff(pitch, channel)]
    B --> E[sendNote(pitch, duration, channel, volume)]
    B --> F[programChange(program, channel)]
    B --> G[controllerChange(controller, val, channel)]
    B --> H[closeDevice()]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style E fill:#bfb,stroke:#333,stroke-width:1px

(Note: countDevices is independent and safe to call any time. All send methods require that openDevice has been called successfully.)

## Raises:
- __init__:
  - Does not explicitly raise Win32MidiException or other exceptions within the constructor. However, attribute access to windll.winmm may raise on non-Windows platforms or if ctypes.windll is unavailable.

- openDevice(deviceNumber=-1):
  - Raises Win32MidiException if winmm.midiOutOpen returns a non-zero return code. The exception message is:
    - "Error opening device, " + midiOutOpenErrorCodes.get(rc, "Unknown error.")
  - Typical trigger conditions: device number out of range, device already allocated, invalid parameter, no device found (mapper), etc. Mapped codes are provided in midiOutOpenErrorCodes.

- closeDevice():
  - Raises Win32MidiException with message "Error closing device" if winmm.midiOutClose returns non-zero.

- sendNote(pitch, duration=1.0, channel=1, volume=60):
  - Raises Win32MidiException if the initial note-on call (midiOutShortMsg) returns non-zero. Message: "Error opening device, " + midiOutShortErrorCodes.get(rc, "Unknown error.")
  - Raises Win32MidiException if the subsequent note-off call returns non-zero. Message: "Error sending event, " + midiOutShortErrorCodes.get(rc, "Unknown error.")
  - Note: If openDevice has not been called, an AttributeError or NameError may occur when accessing self.hmidi; such errors are not wrapped by this class.

- rawNoteOn(pitch, channel=1, v=60), rawNoteOff(pitch, channel=1), programChange(program, channel=1), controllerChange(controller, val, channel=1):
  - Each raises Win32MidiException if winmm.midiOutShortMsg returns a non-zero code. The exception message is "Error sending event, " + midiOutShortErrorCodes.get(rc, "Unknown error.")

Edge-case notes on parameters and behavior:
- pitch: integer note number (caller responsibility to choose a MIDI note range, typically 0–127). The code performs no explicit bounds checking on pitch.
- duration: float seconds for sendNote; sendNote blocks for this duration using time.sleep.
- volume / v / val / program / controller: integers; no bounds checking in code (caller should use valid MIDI ranges: 0–127 where appropriate).
- channel: integer added directly to the status byte low nibble. The code default is 1. MIDI channels are represented in a 4-bit field (0–15). Callers should pass channels in the platform's expected convention (commonly 0–15 for 0-based or 1–16 for 1-based user conventions) — because the implementation adds channel directly to the base status byte, passing values outside 0–15 will produce an invalid status byte and may lead to device errors.

Platform constraint:
- This class binds to windll.winmm and therefore works only on Windows. Using it on other platforms will result in attribute/OS errors from ctypes.windll or missing WinMM functions.

## Example:
1) Basic usage pattern:
player = Win32MidiPlayer()
try:
    # Discover devices (optional)
    n = player.countDevices()
    # Open default mapper device (-1) or a specific device index
    player.openDevice(deviceNumber=-1)
    # Play a middle C (MIDI 60) for one second on channel 1 with volume 90
    player.sendNote(60, duration=1.0, channel=1, volume=90)
    # Change program (instrument) on channel 1
    player.programChange(10, channel=1)
    # Manually send a note-on and note-off without blocking sleep
    player.rawNoteOn(64, channel=1, v=100)
    player.rawNoteOff(64, channel=1)
finally:
    # Ensure the device is released
    player.closeDevice()

2) Error handling:
- Wrap calls in try/except to catch Win32MidiException for WinMM-related errors.
- Ensure closeDevice is called in finally to avoid leaking resources.

### `mingus.midi.win32midi.Win32MidiPlayer.__init__` · *method*

## Summary:
Initializes instance state for Windows MIDI integration by creating two explicit error-code lookup dictionaries and storing a ctypes handle to the WinMM native library on the instance.

## Description:
This constructor runs when a Win32MidiPlayer object is instantiated (i.e., when client code calls Win32MidiPlayer()). It prepares the instance for subsequent calls that interact with the Windows multimedia (WinMM) API by:
- Creating two integer-to-string dictionaries that map common WinMM/midi error and short-message error return codes to descriptive messages.
- Storing a reference to the loaded WinMM library via ctypes.windll.winmm so other instance methods can invoke native functions.

Known callers and lifecycle stage:
- Called directly as part of object construction whenever the application needs a Win32MidiPlayer (typically at the start of a MIDI output workflow, before opening devices or sending messages).
- Higher-level MIDI utilities or factories create this object to centralize WinMM access and error interpretation.

Why this logic is in __init__:
- Error-code maps and the native library handle are one-time initializations required by many instance methods; constructing them once at object creation avoids duplication and ensures a single failure point if the native library cannot be loaded.

## Args:
None.

## Returns:
None (implicit return of Python's __init__).

## Raises:
- OSError (or WindowsError on Python 2): Raised when resolving ctypes.windll.winmm fails because the WinMM library cannot be found or loaded. The exception originates from the ctypes loader. No explicit exceptions are raised by the dictionary construction itself.

## State Changes:
Attributes READ:
- Module-level windll (ctypes.windll) is accessed to obtain the WinMM library object.

Attributes WRITTEN:
- self.midiOutOpenErrorCodes (dict[int, str]):
    - 68: "MIDIERR_NODEVICE  No MIDI port was found. This error occurs only when the mapper is opened."
    - 4: "MMSYSERR_ALLOCATED  The specified resource is already allocated."
    - 2: "MMSYSERR_BADDEVICEID    The specified device identifier is out of range."
    - 11: "MMSYSERR_INVALPARAM    The specified pointer or structure is invalid."
    - 7: "MMSYSERR_NOMEM  The system is unable to allocate or lock memory."
- self.midiOutShortErrorCodes (dict[int, str]):
    - 70: "MIDIERR_BADOPENMODE     The application sent a message without a status byte to a stream handle."
    - 67: "MIDIERR_NOTREADY    The hardware is busy with other data."
    - 5: "MMSYSERR_INVALHANDLE     The specified device handle is invalid."
- self.winmm (ctypes.CDLL-like object): the object returned by ctypes.windll.winmm used to call WinMM functions.

## Constraints:
Preconditions:
- The object instance is being created normally (standard __init__ precondition).
- The runtime environment should provide the WinMM native library if native operations are required; otherwise the attempt to set self.winmm will raise when the library cannot be found.

Postconditions:
- After successful initialization, self.midiOutOpenErrorCodes and self.midiOutShortErrorCodes exist with the exact integer keys and message strings listed above.
- After successful initialization, self.winmm references the ctypes windll handle for the WinMM library (ctypes.windll.winmm), allowing subsequent instance methods to call native functions.

## Side Effects:
- Accessing ctypes.windll.winmm triggers the ctypes loader to probe and load the system WinMM shared library; this is the only external interaction performed during initialization and may raise an OSError/WindowsError if the library is unavailable.
- No file I/O, network calls, or long-running computations are performed by this method.

### `mingus.midi.win32midi.Win32MidiPlayer.countDevices` · *method*

## Summary:
Return the number of available MIDI output devices by delegating to the platform WinMM API via the player's winmm handle. This is a read-only query and does not modify the player's state.

## Description:
A thin wrapper that calls self.winmm.midiOutGetNumDevs() and returns its result. It centralizes the platform-specific query so callers do not need to access the raw winmm handle directly.

Known callers and context:
    - Typical callers invoke this during initialization, device enumeration, or when presenting a device-selection UI to determine how many MIDI outputs exist.
    - It is used at the stage of setup/inspection of MIDI capabilities (i.e., before opening a device or starting playback).

Why this is a separate method:
    - Encapsulates OS interop and keeps higher-level code independent of ctypes/windll details.
    - Makes it easier to add caching, logging, error handling, or platform-specific fallbacks later.
    - Simplifies testing by isolating the single point where the WinMM API is accessed.

## Args:
    None

## Returns:
    int
        The raw numeric value returned by self.winmm.midiOutGetNumDevs(), interpreted as the count of MIDI output devices. Under normal conditions this is a non-negative integer (0 if no devices are present). The exact type is a Python int (ctypes return values are converted into Python numeric types).

## Raises:
    AttributeError
        If the instance has no winmm attribute, or if winmm does not expose a midiOutGetNumDevs attribute, accessing self.winmm.midiOutGetNumDevs will raise AttributeError.
    TypeError
        If self.winmm.midiOutGetNumDevs exists but is not callable, attempting to call it will raise TypeError.
    Any exception raised by the underlying callable
        If the WinMM call itself fails and raises an exception (for example an exception propagated from ctypes bindings or the OS layer), that exception will propagate unchanged to the caller.

## State Changes:
    Attributes READ:
        - self.winmm
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - self.winmm must be set to an object (commonly a ctypes windll handle) that exposes a callable midiOutGetNumDevs.
        - This method is meaningful only on Windows platforms where the WinMM API is available; calling it on other platforms may result in AttributeError or other exceptions unless winmm has been provided by other means.

    Postconditions:
        - No fields on self are modified.
        - The return value equals whatever the underlying API returned at call time.

## Side Effects:
    - Performs a synchronous call into an external OS library (WinMM) via the winmm handle to query system state. This reads system-level MIDI configuration but does not change it.
    - No file, network, or persistent I/O is performed by this method itself.

## Usage notes:
    - Typical sequence: call countDevices(), then iterate indices from 0 to (result - 1) to query or open individual devices.
    - For unit testing or running on non-Windows platforms, replace or mock self.winmm with a test double that exposes midiOutGetNumDevs() to return a deterministic integer.

### `mingus.midi.win32midi.Win32MidiPlayer.openDevice` · *method*

## Summary:
Opens a Win32 MIDI output device and stores the native handle on the instance so subsequent send/close operations can use it.

## Description:
This method calls the Win32 multimedia API (midiOutOpen) via the windll.winmm binding to open a MIDI output device and capture the returned handle on self.hmidi. Typical callers are user code or higher-level MIDI playback routines that perform the lifecycle: instantiate Win32MidiPlayer -> openDevice(...) -> sendNote/rawNoteOn/rawNoteOff/programChange/controllerChange -> closeDevice(). It is separated into its own method to centralize the OS binding, resource allocation, and platform-specific error handling rather than duplicating this logic in every place that begins MIDI output.

## Args:
    deviceNumber (int, optional): Index of the MIDI output device to open. Defaults to -1.
        - -1: Use the system MIDI mapper (default, usually a reasonable choice).
        - >= 0: Open the device with that numeric device identifier (should be in range 0 .. countDevices()-1).
        - The value is passed directly to the native midiOutOpen call and therefore must be an integer.

## Returns:
    None.
    - On success the method returns normally (no explicit return). The instance will have self.hmidi set to a c_void_p containing the native handle.
    - On failure the method does not return; it raises a Win32MidiException.

## Raises:
    Win32MidiException:
        - Raised when the native midiOutOpen call returns a non-zero result code (rc != 0).
        - The exception message is constructed as "Error opening device, " followed by a human-readable string looked up from self.midiOutOpenErrorCodes using the returned rc; if rc is not present in that mapping the message uses "Unknown error.".
    Note: The method does not explicitly check or raise other Python exceptions, but attribute errors will occur if the instance lacks required attributes (e.g., self.winmm).

## State Changes:
    Attributes READ:
        - self.winmm
        - self.midiOutOpenErrorCodes
    Attributes WRITTEN:
        - self.hmidi (set to a new ctypes.c_void_p() which will be passed to the native API and, on success, contain the opened device handle)

## Constraints:
    Preconditions:
        - The instance must have been initialized so that self.winmm references the windll.winmm binding (normally set in __init__).
        - The caller should prefer a valid integer deviceNumber; if choosing a non-default device, deviceNumber should be within the range returned by countDevices().
        - This method targets Windows; windll.winmm must be available in the runtime environment.
    Postconditions:
        - On success: self.hmidi holds a native MIDI output handle (ctypes.c_void_p) that other methods (rawNoteOn/rawNoteOff/sendNote/programChange/controllerChange/closeDevice) can use to send events or close the device.
        - On failure: a Win32MidiException is raised and self.hmidi will have been assigned a c_void_p() but will not reference a valid open handle.

## Side Effects:
    - Calls into the system WinMM library (native I/O) via self.winmm.midiOutOpen; this allocates an OS-level MIDI output resource.
    - Mutates the instance by assigning self.hmidi.
    - If successful, the system reserves an output handle that must later be released by closeDevice() to avoid resource leakage.
    - If the native call fails, no cleanup is performed by this method; the caller should handle the exception and ensure proper state management.

### `mingus.midi.win32midi.Win32MidiPlayer.closeDevice` · *method*

## Summary:
Closes the Windows MIDI output handle held by the instance by calling the native midiOutClose function; raises an exception on native failure and does not modify the stored handle attribute.

## Description:
This method calls the winmm.midiOutClose function via ctypes with the handle stored in self.hmidi. It is intended to be invoked when the caller wants to release a MIDI output device opened previously by this player (i.e., after a successful call to openDevice). The operation is implemented as its own method to separate explicit resource release from playback operations.

Known callers / lifecycle stage:
- No internal callers in this class; intended to be called by client code or shutdown/cleanup logic after openDevice() and any playback calls (sendNote, rawNoteOn, etc.).

## Args:
    None

## Returns:
    None

## Raises:
    Win32MidiException
        Raised when the native call returns a non-zero result code. The raised exception is created with the literal message "Error closing device".
    AttributeError
        If closeDevice is called on an instance that has not had openDevice() called, self.hmidi will not exist and accessing it will raise AttributeError.

## State Changes:
Attributes READ:
    self.winmm (windll.winmm): the module used to call midiOutClose (set in __init__).
    self.hmidi (ctypes.c_void_p): the handle passed to midiOutClose (set by openDevice).

Attributes WRITTEN:
    None — the method does not assign to or clear any attributes on self.

## Constraints:
Preconditions:
    - The instance must have been constructed so that self.winmm exists (this is set in __init__).
    - openDevice() should have been called successfully so that self.hmidi exists and refers to a handle returned by midiOutOpen.

Postconditions:
    - If the call completes without raising Win32MidiException, the native midiOutClose call returned zero; the underlying platform was asked to close the handle identified by self.hmidi.
    - The method does not change self.hmidi; the attribute remains present on the instance after the call (it may refer to a handle that the native layer considers closed).

## Side Effects:
    - Performs a foreign function call into the Windows winmm DLL (midiOutClose) via ctypes.
    - No Python-level attributes are modified by this method.
    - No file or network I/O is performed by this method itself.

### `mingus.midi.win32midi.Win32MidiPlayer.sendNote` · *method*

## Summary:
Sends a MIDI Note On for the given pitch and volume on the specified channel, blocks for the given duration (seconds), then sends the corresponding Note Off. This changes no persistent object state but transmits two short MIDI messages to the underlying WinMM device.

## Description:
This method is the Win32-specific implementation of playing a single MIDI note for a fixed duration. It constructs two 32-bit short MIDI messages (Note On and Note Off), sends the Note On via the WinMM midiOutShortMsg API, sleeps for the specified duration to hold the note, then sends the Note Off.

Known callers and usage context:
- No internal callers exist in this module; it is intended to be invoked by higher-level playback code or directly by users of Win32MidiPlayer.
- Typical lifecycle: instantiate Win32MidiPlayer, call openDevice(...) to initialize self.hmidi, then call sendNote(...) one or more times to play notes, and finally closeDevice() to release resources.
- This method is separated because constructing/encoding the Win32 midiOutShortMsg DWORD and handling the two-step NoteOn->sleep->NoteOff sequence is a distinct responsibility that is reused by higher-level playback logic. Isolating it keeps device I/O, timing, and error-handling in one place.

## Args:
    pitch (int):
        MIDI note number. Expected integer in the MIDI range 0..127 (0 = C-1, 60 = middle C). Values outside 0..127 will produce an encoded message but are outside MIDI specification and may be ignored or produce device errors.
    duration (float, optional):
        How long, in seconds, to hold the note before sending Note Off. Default 1.0. Must be a non-negative number; a negative value will cause time.sleep to raise ValueError.
    channel (int, optional):
        Musical channel to send on. Default 1. This implementation adds the channel numeric value directly into the status byte; the intended channel range is 1..16 (logical MIDI channels 1–16). Supplying values outside this range will change the status nibble and can produce incorrect message types.
    volume (int, optional):
        Note-on velocity (0..127). Default 60. Values outside 0..127 are outside the MIDI spec and may produce undefined behavior on hardware.

## Returns:
    None
    - This method does not return a value. Successful execution implies that a Note On was sent, the thread slept for the requested duration, and a Note Off was sent.

## Raises:
    Win32MidiException:
        - If the initial midiOutShortMsg call (the Note On) returns a non-zero result code rc, this exception is raised with a message starting "Error opening device, " plus a lookup from self.midiOutShortErrorCodes.get(rc, "Unknown error.").
        - If the second midiOutShortMsg call (the Note Off) returns a non-zero result code rc, this exception is raised with a message starting "Error sending event, " plus a lookup from self.midiOutShortErrorCodes.get(rc, "Unknown error.").
    ValueError:
        - Propagated from time.sleep if duration is negative (time.sleep raises ValueError for negative durations).
    Any exceptions raised by the underlying WinMM binding:
        - If self.winmm or self.winmm.midiOutShortMsg behave unexpectedly (e.g., AttributeError if winmm was not initialized), those exceptions will propagate.

## State Changes:
    Attributes READ:
        - self.winmm: used to call the WinMM API function midiOutShortMsg.
        - self.hmidi: device handle passed to midiOutShortMsg; must be initialized (typically by openDevice()).
        - self.midiOutShortErrorCodes: used to create human-readable error messages when rc != 0.
    Attributes WRITTEN:
        - None. The method does not mutate any self.* attributes.

## Constraints:
    Preconditions:
        - self.winmm must be initialized (set in __init__ as windll.winmm).
        - self.hmidi must be a valid handle obtained by calling openDevice() successfully prior to invoking sendNote; otherwise midiOutShortMsg will likely return an error code (e.g., invalid handle).
        - pitch, channel, volume should be integers (or values coercible to integers); duration should be a numeric type acceptable to time.sleep.
    Postconditions:
        - If no exception is raised, a Note On message for the specified pitch/channel/volume has been transmitted, the method blocked for approximately duration seconds, and a corresponding Note Off message has been transmitted.
        - No attributes of the Win32MidiPlayer instance are modified by this call.

## Side Effects:
    - Calls into the system WinMM API via self.winmm.midiOutShortMsg twice, causing I/O to the configured MIDI output device (hardware/synth/mapper).
    - Blocks the calling thread for duration seconds via time.sleep.
    - Raises Win32MidiException on non-zero WinMM return codes, which callers should catch if they wish to continue operation.
    - No file I/O or network I/O is performed by this method beyond the WinMM device interaction.

### `mingus.midi.win32midi.Win32MidiPlayer.rawNoteOn` · *method*

## Summary:
Sends an immediate MIDI Note On message for the given pitch, channel, and velocity to the currently-opened Windows MIDI output device; does not modify the player's internal state.

## Description:
- Known callers and context:
    - No internal callers within this module reference this method directly. The class also provides sendNote (which sleeps and sends a Note Off); rawNoteOn is provided for callers that need to send a Note On without scheduling or sleeping for a Note Off.
    - Typical usage is from higher-level code that wants to start sounding a note immediately and manage note-off separately (for example, to implement sustain, arpeggiation, or external scheduling).
- Why this is a separate method:
    - Encapsulates the low-level packing of MIDI bytes and the direct call to the Win32 multimedia API (midiOutShortMsg). Keeping this logic separate avoids duplicating the native-call and error-handling code wherever an immediate note-on is required and makes raw sending available without the blocking behavior in sendNote.

## Args:
    pitch (int): MIDI note number to turn on. Conventionally 0–127. The method does not validate the numeric range; values outside the standard MIDI range will still be encoded into the message.
    channel (int, optional): MIDI channel number. Default is 1. Conventionally 1–16. The method does not enforce channel bounds.
    v (int, optional): Velocity (volume) for the Note On. Default is 60. Conventionally 0–127. The method does not validate this range.

## Returns:
    None

## Raises:
    Win32MidiException: Raised when the underlying winmm.midiOutShortMsg call returns a non-zero result code. The exception message is constructed as:
        "Error sending event, " + self.midiOutShortErrorCodes.get(rc, "Unknown error.")
    where rc is the integer return code from midiOutShortMsg.

## State Changes:
- Attributes READ:
    - self.winmm (ctypes windll.winmm): used to call midiOutShortMsg
    - self.hmidi (ctypes c_void_p handle): the device handle passed to the API; must be set (typically by openDevice)
    - self.midiOutShortErrorCodes (dict): used to map non-zero return codes to text for the exception message
- Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
- Preconditions:
    - self.winmm must be present (set in __init__ as windll.winmm).
    - self.hmidi must be initialized to a valid device handle (openDevice should be called successfully before calling rawNoteOn); otherwise midiOutShortMsg will likely return an error and trigger Win32MidiException.
    - Arguments should be integers; the method performs arithmetic and bit-packing assuming integer inputs.
- Postconditions:
    - If the function returns normally, the Note On message was passed to the OS via midiOutShortMsg (i.e., the message was submitted to the Win32 MIDI subsystem).
    - If midiOutShortMsg returns a non-zero code, a Win32MidiException is raised and no successful send is guaranteed.

## Side Effects:
- Calls the external Win32 multimedia API via self.winmm.midiOutShortMsg(self.hmidi, mm) where mm is a ctypes.c_int containing the packed MIDI message. This results in an outbound MIDI message being delivered to the OS/hardware associated with self.hmidi.
- No file or network I/O is performed by this method beyond the native OS/hardware interaction.
- Uses ctypes (c_int) to wrap the constructed 32-bit message; behavior is dependent on the underlying Win32 API and installed MIDI devices.

### `mingus.midi.win32midi.Win32MidiPlayer.rawNoteOff` · *method*

## Summary:
Sends a low-level MIDI "Note Off" short message for the given MIDI pitch on the given channel to the currently-open MIDI output device, raising a Win32MidiException if the native API returns an error.

## Description:
This method constructs a 32-bit integer representing a Windows MIDI short message with a Note Off status and forwards it to the Windows multimedia API via the midiOutShortMsg function exposed through ctypes.windll.winmm.

Known callers and context:
- There are no direct internal callers within this module that invoke this method (the class's sendNote method implements its own inline Note Off). Typical callers are:
  - External code that holds a Win32MidiPlayer instance and needs to immediately stop a sounding note.
  - Higher-level player code that uses platform-specific raw primitives to implement note-off behavior.
Lifecycle stage:
- Called after a note has previously been turned on (or to force-stop a note). This is a low-level I/O primitive and is intended to be used when the caller wants to send an immediate Note Off without built-in delay/timing.

Why this is a separate method:
- It encapsulates the precise construction and dispatch of a Windows MIDI short message for a Note Off so that other code can reuse the primitive without duplicating message-encoding or error handling logic. It pairs with rawNoteOn as a small, well-scoped interface to the native API.

## Args:
    pitch (int): MIDI note number, generally 0..127. The method does not validate the range; values outside the expected MIDI range will be encoded into the message as-is and passed to the native API.
    channel (int, optional): MIDI channel number, default 1. The method places this value into the status/low byte as used by the underlying message format. Typical MIDI channels are 1..16; the code does not enforce bounds and will accept any integer, relying on the native API or device to handle invalid channels.

## Returns:
    None
    - The method returns nothing (implicitly None) on success.
    - On error it does not return; it raises an exception as described below.

## Raises:
    Win32MidiException:
        - Raised when the call to self.winmm.midiOutShortMsg(self.hmidi, mm) returns a non-zero result code (rc != 0).
        - The exception message is constructed as: "Error sending event, " + self.midiOutShortErrorCodes.get(rc, "Unknown error.")
        - The mapping self.midiOutShortErrorCodes is consulted for a human-readable description for the returned code; if the code is not found, the literal "Unknown error." is appended.

## State Changes:
    Attributes READ:
        - self.winmm : expected to be the ctypes windll.winmm module used to call midiOutShortMsg
        - self.hmidi : handle to the opened MIDI output device passed to the native API
        - self.midiOutShortErrorCodes : dict used to map numeric error codes to messages when raising an exception
    Attributes WRITTEN:
        - None (the method does not modify any self.* attributes)

## Constraints:
    Preconditions:
        - The Win32MidiPlayer instance must have been initialized such that:
            * self.winmm is available (set to windll.winmm in the class __init__).
            * self.hmidi refers to an opened MIDI output handle (openDevice should have been called successfully).
        - This method relies on being run in an environment where windll.winmm is present (Windows platform with the multimedia API). If the platform does not provide windll.winmm, attribute errors will occur before the native call.
        - No validation of pitch or channel is performed; callers should ensure values are in sensible ranges if required.

    Postconditions:
        - If the native API returns rc == 0, a Note Off short message has been dispatched to the MIDI device and the method returns None.
        - If rc != 0, a Win32MidiException is raised and no successful send is guaranteed.

## Side Effects:
    - Calls into the native Windows multimedia API (self.winmm.midiOutShortMsg) using ctypes and performs I/O to the system MIDI output device indicated by self.hmidi. This typically results in the synthesizer or connected MIDI device receiving a Note Off message (causing sound to stop for the specified pitch/channel).
    - May raise an exception which should be handled by caller code; the exception message includes a mapped or fallback text describing the native error code.
    - No other global state is mutated by this method.

### `mingus.midi.win32midi.Win32MidiPlayer.programChange` · *method*

## Summary:
Sends a MIDI Program Change message to the currently opened MIDI output device, changing the instrument (program) on a given channel; this mutates no internal state but invokes the Win32 multimedia API.

## Description:
This method constructs a 32-bit MIDI short message encoding a Program Change (status 0xC0) and calls the Win32 midiOutShortMsg API through ctypes to transmit it to the device handle stored on the player.

Known callers and context:
- No internal callers in this module were discovered; this method is a public API on Win32MidiPlayer intended to be invoked by client code (playback controllers, MIDI sequence players, or interactive applications) when they need to change the active program/instrument for a channel.
- Typical lifecycle: call openDevice(...) to set up self.hmidi, then call programChange(...) at any time while the device is open (for example before or between sending notes). After finished, call closeDevice().

Why this is a separate method:
- A Program Change is a distinct MIDI message type used frequently; extracting it to its own method avoids duplicating message-packing and error-handling logic across callers and matches other single-purpose methods in this class (sendNote, controllerChange, rawNoteOn, rawNoteOff).

## Args:
    program (int):
        Program (instrument) number to select. Expected MIDI range 0..127 (inclusive).
        The method does not validate the range; values outside 0..127 will be packed into the message as given and may result in a Win32 error or undefined device behavior.
    channel (int, optional):
        1-based MIDI channel number. Default is 1.
        Expected range 1..16 (inclusive). The implementation adds the channel value to the status byte (so the method treats channels as 1-based). Values outside 1..16 are not checked and may produce malformed messages.

## Returns:
    None

## Raises:
    Win32MidiException:
        Raised when the underlying Win32 call midiOutShortMsg returns a non-zero return code (rc). The exception message is constructed as:
            "Error sending event, " + self.midiOutShortErrorCodes.get(rc, "Unknown error.")
        where rc is the integer return code received from midiOutShortMsg.
    AttributeError:
        May be raised indirectly if required attributes are missing (for example, if openDevice() has not been called and self.hmidi is not present, or if self.winmm is not initialized). This method does not catch attribute access errors.

## State Changes:
    Attributes READ:
        self.winmm               -- used to call the Win32 midiOutShortMsg function
        self.hmidi               -- the device handle passed to midiOutShortMsg
        self.midiOutShortErrorCodes -- used to map return codes to human-readable messages when raising exceptions
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - A MIDI device must be opened successfully (openDevice has been called and set self.hmidi to a valid handle). If self.hmidi is uninitialized, an AttributeError or Win32 error will occur.
        - self.winmm must be present (constructed from windll.winmm in the class constructor).
        - Caller should pass program and channel as integers (program typically 0..127, channel typically 1..16).
    Postconditions:
        - A MIDI Program Change short message has been submitted to the OS (via midiOutShortMsg).
        - If the OS call returns non-zero, a Win32MidiException is raised and the message is not silently ignored.

## Implementation details (message packing and behavior):
    - The message is encoded as a 32-bit integer whose bytes (from low to high) are:
        byte0 (status): 0xC0 + channel
            Note: this implementation treats channel as 1-based and adds it to 0xC0. (Typical MIDI status byte uses 0xC0 | (channel-1); this code adds channel directly, so callers should pass channels in the same 1-based convention.)
        byte1 (data1): program (p) placed in the second byte (shifted left by 8)
        byte2 (data2): 0 (unused for Program Change; set via v = 0 and shifted left by 16)
        byte3 (unused high byte): remains 0
    - Construction in code:
        midimsg = 0xC0 + (program * 0x100) + (0 * 0x10000) + channel
      then wrapped as a ctypes.c_int and passed as the second argument to midiOutShortMsg(self.hmidi, mm).
    - After calling midiOutShortMsg, the return value rc is checked:
        - If rc == 0: the call succeeded and the method returns None.
        - If rc != 0: raise Win32MidiException with a message that includes a lookup into self.midiOutShortErrorCodes for a human-readable explanation (falls back to "Unknown error.").

## Side Effects:
    - I/O: invokes the Win32 API midiOutShortMsg via ctypes (self.winmm.midiOutShortMsg). This sends data to an external MIDI device/driver.
    - Exceptions: may raise Win32MidiException on API error; may propagate AttributeError if the required attributes are missing.
    - No modification of the object's internal state (no attributes are assigned).

## Example usage (conceptual):
    - player.openDevice()
    - player.programChange(0, channel=1)  # set channel 1 to program 0 (Acoustic Grand Piano)
    - player.sendNote(60, duration=0.5, channel=1)
    - player.closeDevice()

### `mingus.midi.win32midi.Win32MidiPlayer.controllerChange` · *method*

## Summary:
Send a MIDI controller (Control Change / CC) message through the opened WinMM MIDI output device, updating the device state by transmitting a packed short MIDI message or raising an exception on failure.

## Description:
This method constructs a 32-bit (short) MIDI message representing a Control Change (status 0xB0) and sends it via the WinMM midiOutShortMsg API bound to this Win32MidiPlayer instance.

Known callers and context:
- Public API consumers (application code) send controller changes by calling this method directly.
- Higher-level MIDI playback or event dispatch code may call it when processing MIDI CC events.
- It is invoked after openDevice has successfully been called (the player must have an open midi handle) and before closeDevice.

Why this is a dedicated method:
- Packing and sending a controller-change message involves a standardized bit/byte layout and an external native call; extracting this into its own method avoids duplication (several different MIDI message types are sent elsewhere in the class) and isolates the error handling for short-message sends.

## Args:
    controller (int): MIDI controller number (typically 0–127 for standard MIDI controllers). The method does not validate the range — values are packed as provided.
    val (int): Controller value (typically 0–127). No clamping is performed; out-of-range values will be encoded as-is into the message.
    channel (int, optional): Logical MIDI channel used when forming the message. By convention callers use 1–16 (default 1). The method uses the integer verbatim when packing the message; the class elsewhere uses 1 as the default channel.

## Returns:
    None
    - On success the function returns normally (no value).
    - On failure it does not return; it raises a Win32MidiException.

## Raises:
    Win32MidiException:
    - Raised when the underlying WinMM call self.winmm.midiOutShortMsg(self.hmidi, mm) returns a non-zero result code.
    - The exception message begins with "Error sending event, " and includes an error description looked up from self.midiOutShortErrorCodes using the returned code; if the code is not in that dict, the text "Unknown error." is appended.

## State Changes:
    Attributes READ:
        - self.winmm (ctypes windll.winmm): used to call midiOutShortMsg
        - self.hmidi (ctypes c_void_p/int-like): the MIDI output handle passed to midiOutShortMsg
        - self.midiOutShortErrorCodes (dict): used to map error return codes to human-readable messages

    Attributes WRITTEN:
        - None. This method does not modify any self.<attr> fields.

## Constraints:
    Preconditions:
        - openDevice must have been called successfully and set self.hmidi to a valid handle; otherwise the native call will likely return an error code and the method will raise Win32MidiException.
        - The process must be running on Windows with the WinMM subsystem available (self.winmm is windll.winmm as initialized in __init__).
        - Arguments should be integers; non-integer types will be used in arithmetic/packing and may raise TypeError elsewhere (no explicit type checking is performed).

    Postconditions:
        - If the method returns normally, a Control Change message has been submitted to the MIDI output device (as passed to midiOutShortMsg). Exact delivery and hardware handling are determined by the OS/hardware.
        - If the method raises Win32MidiException, the message was not accepted by the WinMM API — the caller can catch the exception to handle the failure.

## Side Effects:
    - Calls the native WinMM function midiOutShortMsg (self.winmm.midiOutShortMsg) which performs I/O to the MIDI subsystem and device.
    - May raise a Win32MidiException (an exception type defined elsewhere in this module) when the native call reports an error.
    - No other global I/O, file, or network side-effects occur.

## Implementation notes (behavioral detail useful when reimplementing):
    - The packed message is built exactly as:
        midimsg = 0xB0 + (controller * 0x100) + (val * 0x10000) + channel
      then wrapped in a ctypes c_int and passed to midiOutShortMsg(self.hmidi, mm).
    - Do not assume the method validates controller/val/channel ranges — callers are responsible for providing sensible MIDI values.
    - Error mapping uses self.midiOutShortErrorCodes.get(rc, "Unknown error.") to include a readable message in the raised exception.

