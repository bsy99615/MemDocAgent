# `win32midisequencer.py`

## `mingus.midi.win32midisequencer.Win32MidiSequencer` · *class*

## Summary:
A Windows-specific Sequencer adapter that delegates MIDI output operations to a Win32MidiPlayer; it prepares and manages a WinMM MIDI output device and forwards note, controller, and program-change events to that device.

## Description:
The Win32MidiSequencer is a platform adapter implementing the Sequencer backend for Microsoft Windows. Instantiate this class when you need a Sequencer that emits real-time short MIDI messages by delegating to the Win32MidiPlayer (which uses the WinMM API). Typical usage is within applications or higher-level playback pipelines that require immediate MIDI output on Windows. The class purpose is to separate sequencing/timing logic (in Sequencer) from platform-specific message emission: it performs device allocation and then forwards event requests to the Win32 MIDI layer.

Known callers/factories:
- Higher-level Sequencer frameworks that instantiate platform-specific sequencers.
- Application code that needs a concrete Sequencer on Windows may instantiate this class directly, call init(), then use Sequencer-facing functions that dispatch to the backend event methods.

Responsibility boundary:
- Manages a Win32MidiPlayer instance (device open/close) and forwards play_event, stop_event, cc_event, and instr_event calls.
- Does not implement scheduling, timing, or track parsing — those responsibilities belong to the Sequencer base class.

## State:
- output (Any)
  - Type: unspecified / placeholder (present in class for compatibility or external assignment)
  - Default: None
  - Valid values: any object or None. The class source does not read or write this attribute anywhere; it exists for external wiring and should be considered optional.
  - Invariant: No internal code depends on this attribute; it has no enforced invariants.

- midplayer (mingus.midi.win32midi.Win32MidiPlayer | None)
  - Type: Win32MidiPlayer instance or None
  - Default: None
  - Valid values: None (before initialization) or a Win32MidiPlayer with an opened device (after successful init())
  - Invariant: If non-None, midplayer is expected to have had openDevice() called successfully and therefore hold a valid WinMM output handle (hmidi). If midplayer is None, event methods will raise AttributeError when trying to call across the None reference.

Class invariants:
- Before init(): midplayer is None.
- After successful init(): midplayer is a Win32MidiPlayer and its device is opened.
- After close (via midplayer.closeDevice() in destructor or external cleanup): midplayer may remain as a Python object but the underlying device handle is expected to be closed by the player.
- The object is intended to be used only on Windows; init() enforces a platform check.

## Lifecycle:
Creation:
- Instantiate with no arguments:
  - sequencer = Win32MidiSequencer()
  - At this point midplayer is None and no device is opened.

Initialization:
- Call init() before any event-sending methods:
  - Purpose: enforce platform, construct Win32MidiPlayer, and open the device.
  - Preconditions: sys.platform must equal "win32"; caller must be prepared to handle Win32MidiPlayer/WinMM errors.
  - Postconditions: self.midplayer references a Win32MidiPlayer with an opened device if init() returns successfully.

Usage:
- After init(), call event methods in any order as needed during playback:
  - play_event(note, channel, velocity) -> forwards to midplayer.rawNoteOn(note, channel, velocity)
  - stop_event(note, channel) -> forwards to midplayer.rawNoteOff(note, channel)
  - cc_event(channel, control, value) -> forwards to midplayer.controllerChange(control, value, channel) (note the argument reordering)
  - instr_event(channel, instr, bank) -> forwards to midplayer.programChange(instr, channel) (bank is accepted but ignored by this Win32 adapter)
- There is no internal tracking of outstanding notes; caller (or Sequencer base class) should manage note lifetimes.

Destruction / Cleanup:
- The class defines a destructor (__del__) that calls self.midplayer.closeDevice().
  - This is intended to release OS-level MIDI handles when the Python object is finalized.
  - Because __del__ is executed during Python finalization, it may encounter partially torn-down state on interpreter shutdown (leading to AttributeError).
- Best practice: ensure the underlying player's device is closed deterministically (for instance, by calling midplayer.closeDevice() if you have a direct reference) rather than relying solely on __del__.

## Method Map:
graph TD
    A[instantiate Win32MidiSequencer] --> B[init()]
    B --> C[midplayer created: Win32MidiPlayer() ]
    C --> D[midplayer.openDevice()]
    D --> E[play_event(note, channel, velocity) -> midplayer.rawNoteOn(...)]
    D --> F[stop_event(note, channel) -> midplayer.rawNoteOff(...)]
    D --> G[cc_event(channel, control, value) -> midplayer.controllerChange(control,value,channel)]
    D --> H[instr_event(channel, instr, bank) -> midplayer.programChange(instr,channel)]
    H --> I[__del__() -> midplayer.closeDevice()]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style B fill:#bbf,stroke:#333,stroke-width:1px
    style E fill:#bfb,stroke:#333,stroke-width:1px

Typical invocation order: instantiate -> init -> event methods (many repeats) -> allow object destruction or explicitly close device (via midplayer.closeDevice()).

## Raises:
- init()
  - RuntimeError: raised immediately if sys.platform != "win32" with message "Intended for use on win32 platform".
  - Any exceptions raised by Win32MidiPlayer() construction or by Win32MidiPlayer.openDevice() (for example Win32MidiException on WinMM failures, OSError, AttributeError). These exceptions propagate without being wrapped.

- play_event(), stop_event(), cc_event(), instr_event()
  - AttributeError: if self.midplayer is None or does not expose the expected method (this happens when init() has not been called or midplayer was not successfully constructed).
  - Any exception raised by the corresponding Win32MidiPlayer methods (rawNoteOn/rawNoteOff/controllerChange/programChange) — typically Win32MidiException on WinMM error codes. These exceptions propagate unchanged.

- __del__()
  - AttributeError: possible if midplayer is None or has been torn down by interpreter shutdown; such exceptions may occur during finalization.
  - Any exception raised by midplayer.closeDevice(); these propagate out of __del__ (but note that exceptions in __del__ behave differently during interpreter shutdown).

## Example:
1) Instantiate the sequencer:
   sequencer = Win32MidiSequencer()

2) Initialize the platform device (must run on Windows):
   sequencer.init()

3) Send a note-on, later stop it:
   sequencer.play_event(60, 0, 100)    # note=60, channel=0, velocity=100
   sequencer.stop_event(60, 0)

4) Change a controller and instrument:
   sequencer.cc_event(0, 7, 100)       # channel=0, control=7 (main volume), value=100
   sequencer.instr_event(0, 10, 0)     # channel=0, instr=10 (bank ignored)

5) Cleanup:
   del sequencer
   # or ensure the underlying player is closed via sequencer.midplayer.closeDevice() if you manage it directly

Notes:
- Always call init() before issuing event methods. init() enforces platform and opens the device; event methods will raise AttributeError if called beforehand.
- cc_event reorders its arguments when forwarding to the underlying player: it receives (channel, control, value) but calls controllerChange(control, value, channel).
- Bank parameter passed to instr_event is unused by this Win32 adapter; only programChange(instr, channel) is sent.

### `mingus.midi.win32midisequencer.Win32MidiSequencer.init` · *method*

## Summary:
Allocate and open the Windows MIDI output for this sequencer by instantiating a Win32MidiPlayer and calling its device-open routine, leaving the sequencer ready to send MIDI events.

## Description:
- Invocation context:
    - This method is intended to be called during setup/initialization of a Win32MidiSequencer instance and must be invoked before any of the sequencer's event-sending methods (play_event, stop_event, cc_event, instr_event) are used, because those methods call self.midplayer to send MIDI messages.
- Rationale for a separate method:
    - The method performs a platform check and performs OS-level resource allocation (opening a WinMM MIDI output). Keeping this logic in a distinct init method avoids performing platform-specific I/O in object construction and makes initialization explicit so callers can handle failures and resource allocation timing.

## Args:
    None

## Returns:
    None

## Raises:
    RuntimeError
        - If sys.platform != "win32". Exact message raised: "Intended for use on win32 platform".
    Win32MidiException (propagated)
        - May be raised by win32midi.Win32MidiPlayer.openDevice() when the underlying WinMM call fails (openDevice documents that it raises this exception on non-zero WinMM return codes).
    AttributeError / OSError / other low-level exceptions (propagated)
        - If constructing Win32MidiPlayer or calling its methods touches OS-level ctypes objects that are unavailable or fail. Note: the explicit platform check guards typical non-Windows hosts that report sys.platform != "win32".

## State Changes:
- Attributes READ:
    - (none) — the method does not read any self.<attr> fields.
- Attributes WRITTEN:
    - self.midplayer — assigned to a new win32midi.Win32MidiPlayer() instance; subsequently openDevice() is invoked on that instance.

## Important implementation-order detail:
- The method first assigns self.midplayer = win32midi.Win32MidiPlayer() and then calls self.midplayer.openDevice().
    - Consequence: if openDevice() raises, self.midplayer will still reference the created Win32MidiPlayer object (potentially partially initialized). Callers who observe an exception can inspect or attempt to clean up that object (for example by calling its closeDevice() if present), but behavior depends on Win32MidiPlayer's internal state when openDevice failed.

## Constraints:
- Preconditions:
    - Caller should only call this method on a system where sys.platform == "win32".
    - Caller must be prepared to handle the listed exceptions.
- Postconditions:
    - On successful return, self.midplayer is a Win32MidiPlayer with its device opened (the underlying hmidi handle allocated) and the sequencer is ready to use its event methods.
    - On exception, no guarantee is provided about the opened state of any device or the internal state of self.midplayer; callers should treat initialization as failed and perform cleanup as appropriate.

## Side Effects:
- Performs OS-level I/O by allocating a WinMM MIDI output device via Win32MidiPlayer.openDevice(). This acquires a system MIDI handle and may interact with device drivers and system MIDI mapper.
- Overwrites any previous value of self.midplayer without closing it first. If init is called multiple times without closing the previous player, the prior player instance may be left to be cleaned up by its destructor or by the caller; repeated calls can therefore leak the previous device handle until it is closed.

### `mingus.midi.win32midisequencer.Win32MidiSequencer.__del__` · *method*

## Summary:
Calls the attached midplayer's closeDevice method to release the sequencer's underlying MIDI device when the object is being finalized, ensuring native/OS-level MIDI resources are released.

## Description:
This destructor is invoked automatically by Python's finalization mechanisms (for example: when the object is garbage-collected, when Python's del statement deletes the last reference, or during interpreter shutdown). It performs the object's cleanup step that closes the underlying MIDI device handle by delegating to the midplayer.

Known callers and lifecycle stage:
- Python garbage collector (object finalization).
- Code that explicitly deletes the sequencer instance or lets it go out of scope.
- Interpreter shutdown sequence (objects are finalized as the interpreter exits).

Why this logic is a dedicated destructor:
- Ensures deterministic cleanup of an external/native resource (the MIDI device) tied to the object's lifetime.
- Centralizes resource-release logic so callers of the sequencer need not remember to call a separate cleanup function.
- Keeps cleanup separate from runtime control methods (e.g., play/stop), making resource management explicit at object finalization.

## Args:
- None.

## Returns:
- None.

## Raises:
- AttributeError:
    - Trigger: self.midplayer is None (or the attribute does not exist) at call time; attempting to access self.midplayer.closeDevice will raise because NoneType or missing attribute has no such method.
    - Note: this can commonly occur during interpreter shutdown or if init was never called.
- Any exception raised by self.midplayer.closeDevice:
    - Trigger: the underlying closeDevice implementation can raise (for example, on I/O/OS failure). Such exceptions propagate unchanged from this method.

## State Changes:
- Attributes READ:
    - self.midplayer — the method reads this attribute to call its closeDevice method.
- Attributes WRITTEN:
    - None — the method does not assign to any self.<attr> attributes.

## Constraints:
- Preconditions:
    - Preferably, the object's init() method was called earlier and successfully set self.midplayer to a valid Win32MidiPlayer instance and opened the device (init raises on non-win32 platforms).
    - The object should be in a valid runtime (not mid-teardown of interpreter) to avoid attribute teardown race conditions.
- Postconditions:
    - If the call completes without raising, the underlying midplayer's closeDevice implementation has been invoked and is expected to have released or closed any associated MIDI device resources.
    - If an exception is raised, no additional guarantees are made about resource state; the exception will propagate.

## Side Effects:
- Calls into the midplayer implementation (self.midplayer.closeDevice), which may perform OS-level I/O to close/free MIDI device handles or other native resources.
- May raise exceptions originating from underlying I/O or OS APIs.
- Does not modify attributes on self; it may, however, change state internal to self.midplayer or the OS device driver.

### `mingus.midi.win32midisequencer.Win32MidiSequencer.play_event` · *method*

## Summary:
Triggers a MIDI "note on" by delegating to the platform MIDI player; updates no internal state but causes an external MIDI output action.

## Description:
This method is the Win32-specific implementation used to perform a note-on event when the sequencer dispatches playback events. It is typically invoked by the sequencing/playback loop (the Sequencer superclass or a caller responsible for dispatching scheduled events) at the time a note should start sounding. The logic is factored into its own method to isolate the platform-specific call (the Win32 MIDI player) from generic sequencer logic and to allow subclassing/overriding for other platforms.

At runtime this method simply calls the underlying midplayer's rawNoteOn with the provided parameters, so any behavior, validation, or errors from the underlying player are propagated.

## Args:
    note (int):
        MIDI note number to play. Expected conventional MIDI range is 0–127 (octave and mapping depend on the rest of the system).
    channel (int):
        MIDI channel number to use. Conventional MIDI channel range is 0–15.
    velocity (int):
        Attack velocity for the note. Conventional MIDI range is 0–127.

## Returns:
    None

## Raises:
    AttributeError:
        If self.midplayer is None or does not exist (e.g., init() was not called or initialization failed), attempting to call rawNoteOn on None will raise AttributeError.
    Any exception raised by self.midplayer.rawNoteOn:
        This method does not catch exceptions from the underlying midplayer; such exceptions (I/O errors, device errors, invalid-argument errors thrown by the midplayer implementation) are propagated to the caller.

## State Changes:
    Attributes READ:
        self.midplayer
    Attributes WRITTEN:
        None (no attributes on self are modified)

## Constraints:
    Preconditions:
        - The Win32MidiSequencer.init() lifecycle method should have been called successfully so self.midplayer is initialized (and its device opened). If not, calling this method will result in an AttributeError or other lower-level error.
        - The process must be running on a platform where the Win32MidiPlayer is valid and its device is open (the class enforces platform intent in init()).
    Postconditions:
        - No internal object state is changed by this call.
        - A MIDI note-on message has been requested from the underlying midplayer; successful completion indicates the midplayer accepted the request, while exceptions indicate failure.

## Side Effects:
    - Delegates to self.midplayer.rawNoteOn(note, channel, velocity) which performs external I/O: sends a MIDI "note on" message to the OS/device via the Win32 MIDI API.
    - May cause audible sound on the configured MIDI output device and/or device-specific side effects managed by the underlying midplayer and OS.

### `mingus.midi.win32midisequencer.Win32MidiSequencer.stop_event` · *method*

## Summary:
Dispatches a MIDI Note-Off for a single note by delegating to the platform MIDI player held on the sequencer, causing the note to cease on the MIDI output device. This method does not alter sequencer state; it only issues the device-level command.

## Description:
This is the Win32-specific implementation of stopping a sounding note. It exists to isolate platform/device interaction behind the Sequencer interface so higher-level playback/scheduler logic can call a uniform stop_event method without handling platform details.

Known callers and lifecycle context:
- The sequencer playback scheduler or sequence-processing code calls this method when a scheduled note-off event is reached or when user/requested playback control requests a note to be stopped.
- It is invoked during the playback lifecycle (after init() has been called and before device close) and may be called repeatedly for many notes during normal playback.

Why separate:
- The method is a thin adapter that centralizes the platform-specific call to the underlying MIDI engine (midplayer). Keeping it separate preserves a consistent Sequencer API across different platform implementations and prevents scattering device access logic through playback code.

## Args:
    note (int):
        MIDI note identifier forwarded to the underlying player. The method does not validate ranges — it forwards the value verbatim.
    channel (int):
        MIDI channel identifier forwarded to the underlying player. The method does not validate ranges — it forwards the value verbatim.

Notes on allowed values:
- Typical MIDI conventions use note values 0–127 and channel values 0–15, but those ranges are not enforced here. Callers should ensure values conform to their target device's expectations.

## Returns:
    None

## Raises:
    AttributeError:
        If self.midplayer is None (for example, init() was not called or the device was not opened), attempting to call rawNoteOff will raise an AttributeError at the attribute access step.
    Any exception raised by self.midplayer.rawNoteOff(note, channel):
        This method does not catch exceptions from the underlying player; any device-level or I/O error raised by the platform MIDI implementation is propagated to the caller.

## State Changes:
    Attributes READ:
        self.midplayer
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - init() should have been called on this Win32MidiSequencer instance so that self.midplayer is a valid, opened MIDI player object.
        - The caller is responsible for supplying appropriate integer values for note and channel; this method performs no sanitization or bounds checking.
    Postconditions:
        - A call to the underlying player's rawNoteOff(note, channel) has been issued.
        - No sequencer attributes are modified by this call.

## Side Effects:
    - Sends a MIDI Note-Off message to the external MIDI device via the platform MIDI player (I/O).
    - May interact with OS/device resources (e.g., open device handles) and can surface underlying device errors.
    - No filesystem, network, or other external services are used by this method beyond the MIDI device I/O performed by the player it delegates to.

### `mingus.midi.win32midisequencer.Win32MidiSequencer.cc_event` · *method*

## Summary:
Forwards a MIDI Control Change (CC) message to the backend midplayer, causing the backend/device state to update; does not return a value but mutates external MIDI state.

## Description:
This is a thin backend adapter method on the Win32 sequencer that receives a sequencer-level control-change request and forwards it to the platform-specific MIDI player instance stored on the object.

Known callers and lifecycle context:
- The Sequencer layer (for example Sequencer.control_change and convenience wrappers such as modulation, main_volume, pan) invokes this method as part of normal playback or when an external caller requests a control change. This occurs during runtime after the sequencer has been initialized.
- Typical lifecycle: init() must have been called to create and open self.midplayer (Win32MidiSequencer.init sets self.midplayer = win32midi.Win32MidiPlayer() and opens the device). cc_event is invoked repeatedly during playback to apply controller changes.

Why this logic is a separate method:
- It isolates backend-specific MIDI I/O from high-level sequencing and validation. Sequencer performs validation, listener notification, and timing; cc_event is the platform hook that emits the actual MIDI CC to the backend so other backends can implement the same Sequencer API without duplicating sequencing logic.

Important implementation note:
- The method accepts (channel, control, value) but forwards the arguments to the midplayer in the order (control, value, channel). This reordering is deliberate to match the backend midplayer API.

## Args:
    channel (int):
        MIDI channel identifier passed by the sequencer. Sequencer conventions typically use 1..16 (the Sequencer layer documents callers that provide integer channel values). This method does not validate the numeric range.
    control (int):
        Controller number (controller ID), expected in the MIDI range 0–127. Not validated here.
    value (int):
        Controller value, expected in the MIDI range 0–127. Not validated here.

## Returns:
    None
    - The method performs side effects only. It returns None implicitly.

## Raises:
    AttributeError:
        If self.midplayer is None or does not expose controllerChange (for example if init() was not called or the backend device was closed), attempting to call controllerChange will raise AttributeError.
    Exception (backend-specific):
        Any exception raised by the underlying midplayer.controllerChange(...) call (for example I/O errors from the Windows MIDI backend) will propagate unchanged. The method does not catch or translate backend exceptions.

## State Changes:
Attributes READ:
    self.midplayer

Attributes WRITTEN:
    None on the Win32MidiSequencer instance.

Note: The external backend/device referenced by self.midplayer is mutated by the controllerChange call (its controller state is updated), but no attributes on the sequencer object are modified.

## Constraints:
Preconditions:
    - self.midplayer must be initialized and connected to an open device (Win32MidiSequencer.init must have been called). If self.midplayer is not set, calling this method will raise AttributeError.
    - channel, control, and value should be integers (or types accepted by the backend). The method does not coerce or validate types or ranges.

Postconditions:
    - The backend midplayer's controller state for the specified controller/channel will be updated according to midplayer.controllerChange(control, value, channel) (behavior and success depend on the backend implementation).
    - The method returns None.

## Side Effects:
    - Mutates external state: invokes self.midplayer.controllerChange(control, value, channel), which updates the backend/device controller state and may immediately affect audio output or MIDI device state.
    - No file, network I/O, or changes to other attributes of the sequencer object are performed by this method itself.

### `mingus.midi.win32midisequencer.Win32MidiSequencer.instr_event` · *method*

## Summary:
Forward a program/instrument-change request to the platform MIDI player, updating the active program on the given MIDI channel; this mutates no sequencer state but causes an external MIDI program change to be sent.

## Description:
This method is the Win32-specific handler for an "instrument" (program change) event in the sequencer pipeline. Typical callers are the sequencer's event-dispatch or playback loop when it encounters a program-change/instrument event in a track or incoming control stream. It belongs to the platform adapter layer so that higher-level sequencer logic can remain platform-agnostic while platform-specific message packing and sending are handled here.

Why this is a separate method:
- Keeps the Sequencer-to-player adapter thin and explicit: instrument-change semantics are a distinct MIDI action and are forwarded in one place.
- Encapsulates the platform-specific forwarding (including argument mapping and any platform limitations such as ignoring bank on Win32) so other code does not need to know about Win32MidiPlayer internals.

## Args:
    channel (int):
        MIDI channel forwarded to the player. This method does not validate the channel; it is forwarded as-is to Win32MidiPlayer.programChange.
        Note: Win32MidiPlayer expects a 1-based channel convention (1..16). Callers should follow the same convention to avoid malformed status bytes.
    instr (int):
        Program/instrument number to select (typically 0..127). No range checks are performed by this method; values are forwarded as-is.
    bank (int):
        Bank number parameter provided for API compatibility. In this Win32 implementation the bank parameter is ignored because Win32MidiPlayer.programChange only sends a Program Change short message and does not implement bank select.

## Returns:
    None

## Raises:
    Any exception raised by the underlying midplayer.programChange call:
        - Win32MidiException: if the WinMM call fails (propagated from Win32MidiPlayer.programChange).
        - AttributeError: if self.midplayer is not set (e.g., init() / openDevice() was not called).
    This method does not catch or wrap those exceptions.

## State Changes:
    Attributes READ:
        self.midplayer
    Attributes WRITTEN:
        None

## Constraints:
    Preconditions:
        - self.midplayer must be initialized and refer to a valid Win32MidiPlayer instance (typically after Win32MidiSequencer.init() has been called, which constructs the player and opens the device).
        - The caller should pass integers for channel and instr. Recommended ranges: channel 1..16 (1-based), instr 0..127; these are not enforced here.
    Postconditions:
        - The underlying player will have been asked to send a MIDI Program Change message for the given instrument and channel. If the underlying call returns an error, an exception will be raised and no silent failure occurs.

## Side Effects:
    - I/O: causes a synchronous call into the OS MIDI subsystem via self.midplayer.programChange, which ultimately calls the Win32 midiOutShortMsg API. This sends a Program Change message to the opened MIDI device.
    - No internal attributes of the sequencer object are modified by this method.
    - Any underlying errors from the OS/driver may raise exceptions that propagate to the caller.

