# `sequencer.py`

## `mingus.midi.sequencer.Sequencer` · *class*

*No documentation generated.*

### `mingus.midi.sequencer.Sequencer.__init__` · *method*

## Summary:
Initializes a Sequencer instance by creating the listeners container and invoking the instance initialization hook; ensures the object has a fresh, empty listeners list and then delegates further setup to the overrideable init() method.

## Description:
Known callers:
    - Constructing a Sequencer or any subclass instance (called automatically as part of object construction when Sequencer() or a subclass __init__ calls the base constructor).

Lifecycle / context:
    - This method runs as the first-phase construction logic for a Sequencer instance. It establishes the baseline attribute(s) the Sequencer expects (listeners) and then calls the init() hook so subclasses or backend implementations may perform additional, instance-specific initialization.
    - The ordering is important: listeners is created before init() is invoked, so any override of init() can safely assume self.listeners exists.

Why this is a separate method:
    - init() is provided as a separate, overrideable hook so subclasses or concrete MIDI backends can perform additional setup without replacing or duplicating the entire constructor logic. The base init() implementation is a no-op; subclasses override it to open devices, allocate resources, or set extra attributes.

## Args:
    None

## Returns:
    None

## Raises:
    - Any exception raised by init() will propagate out of __init__ (this constructor does not catch exceptions). For example, a subclass override of init() that fails while opening a MIDI device will cause object construction to fail with that exception.

## State Changes:
Attributes READ:
    - None in the base implementation.

Attributes WRITTEN:
    - self.listeners: set to a new empty list (overwrites any pre-existing attribute of the same name on the instance).

## Constraints:
Preconditions:
    - Called on a newly-allocated Sequencer (or subclass) instance as part of construction; no external preconditions or arguments are required.
    - Callers (or subclass init overrides) should not assume other Sequencer attributes besides listeners exist until they are explicitly set by init() or by other methods.

Postconditions:
    - After __init__ returns successfully:
        * self.listeners exists and is an empty list.
        * The instance has had its init() hook invoked; any additional attributes or resources established by an overridden init() will likewise be present (or an exception will have been raised).
    - If init() raises, object construction does not complete and the partially-initialized instance should not be relied upon.

## Side Effects:
    - Creates an in-memory empty list assigned to self.listeners.
    - Calls the instance method self.init(), which in the base class performs no side effects but may be overridden; any side effects produced by an override (I/O, opening MIDI devices, registering OS resources, etc.) occur as a direct consequence of this call.

### `mingus.midi.sequencer.Sequencer.init` · *method*

## Summary:
A no-op initialization hook invoked during Sequencer construction; provides a place for subclasses or concrete MIDI backends to perform instance-specific setup without overriding __init__.

## Description:
Known callers:
    - Sequencer.__init__: called immediately during object construction (self.init() in the constructor).

Lifecycle / context:
    - Invoked as part of the Sequencer instantiation lifecycle. It runs after basic instance fields set by __init__ (for example, listeners is created in __init__) and before the constructed object is returned to callers.
    - Intended as a clear, overrideable boundary where subclasses or backend implementations may perform initialization (e.g., open MIDI outputs, configure state, or allocate resources) while leaving the Sequencer.__init__ logic unchanged.

Why this is a separate method:
    - Separating initialization logic into its own method allows subclasses to customize initialization behavior by overriding init() rather than duplicating or shadowing the entire __init__ implementation. The base implementation is intentionally empty so that no default side effects occur unless a subclass provides them.

## Args:
    None

## Returns:
    None

## Raises:
    None — the base implementation does not raise any exceptions.

## State Changes:
    Attributes READ:
        - None (the base implementation performs no reads of self attributes)

    Attributes WRITTEN:
        - None (the base implementation does not modify any self attributes)

## Constraints:
    Preconditions:
        - An instance of Sequencer must exist (the method is intended to be called on a Sequencer instance).
        - No other preconditions are required by the base implementation.

    Postconditions:
        - After the call, the Sequencer instance is in the same state as before the call (no changes made by the base implementation).
        - If overridden, subclasses should document their own postconditions (e.g., what attributes they set or resources they allocate).

## Side Effects:
    - The base implementation has no side effects: it performs no I/O, makes no external service calls, and does not mutate objects outside self.
    - Subclass overrides may perform side effects (e.g., opening MIDI devices); those side effects are not present in the base implementation and must be documented by the overriding subclass.

### `mingus.midi.sequencer.Sequencer.play_event` · *method*

## Summary:
Hook that receives a single "note-on" event (note number, MIDI channel, velocity). In the base Sequencer this method is a no‑op; concrete sequencer backends should override it to emit a MIDI note-on (or equivalent) to the configured output. Calling it does not modify Sequencer internal state in the base implementation.

## Description:
Known callers and context:
- play_Note(note, channel=1, velocity=100): called during high-level note playback after converting a Note-like object to an integer MIDI note number.
- play_NoteContainer and play_Bar / play_Bars / play_Track / play_Tracks / play_Composition: transitively call play_Note which invokes play_event for each playing note.
- stop_Note and stop_NoteContainer use stop_event (the companion method) for note-off behavior; play_event is specifically the note-on hook.

Lifecycle stage:
- Invoked at "start of note" during the Sequencer playback pipeline. Higher-level functions manage timing, listener notifications, and stop logic; play_event is responsible only for the immediate emission of the play (note-on) event.

Why this is a separate method:
- Separation of concerns: the Sequencer implements timing, container traversal, and listener notifications; actual MIDI/back-end-specific I/O is backend responsibility. Making play_event a small overridable hook allows multiple concrete backends (e.g., real MIDI output, virtual backends for testing, file-based backends) to reuse Sequencer's playback logic.

## Args:
    note (int):
        - MIDI pitch number (integer). Callers typically pass an already-converted integer (e.g., play_Note does int(note) + 12).
        - Recommended/typical range: 0..127 (implementations should clamp or validate as appropriate).
    channel (int):
        - 1-based MIDI channel number (integer). Callers in this codebase use channels starting at 1.
        - Recommended/typical range: 1..16. Implementations that use 0-based APIs should convert accordingly.
    velocity (int):
        - Note velocity (integer). Typical MIDI range: 0..127.
        - A velocity of 0 is commonly used by many MIDI systems to indicate note-off; backends may choose to translate velocity==0 into a note-off message or emit a note-on with zero velocity depending on the target API.

All three arguments are expected to be integers. The Sequencer callers normally coerce values to int before calling.

## Returns:
    None by default.
    - The base implementation (pass) implicitly returns None.
    - Concrete implementations MAY return a boolean or other status indicator (True/False) to signal success/failure, but Sequencer callers do not depend on any return value.

## Raises:
    - The base method does not raise (it is a no-op).
    - Implementations that perform I/O may raise backend-specific errors (e.g., IOError, OSError, exceptions from a MIDI library). Implementers should document and handle those exceptions at the backend level if necessary.

## State Changes:
    Attributes READ:
        - base implementation: none.
        - recommended in implementations: may read self.output (Sequencer.output class/instance attribute) or other backend configuration fields to determine where to send MIDI messages.
    Attributes WRITTEN:
        - base implementation: none.
        - implementations should avoid mutating Sequencer playback state; any mutable state changes (e.g., tracking active notes) must be documented and kept local to the backend if required.

## Constraints:
    Preconditions:
        - note, channel, velocity should be integers (callers normally ensure this).
        - channel should be in the valid MIDI channel range (1..16) for this codebase; if the backend uses 0-based channels, convert (channel - 1).
        - Implementations should handle out-of-range values gracefully (clamp, raise a clear ValueError, or ignore the event) — choose one consistent behavior and document it.
    Postconditions:
        - After a successful implementation call, a "note-on" message corresponding to the supplied args has been emitted to the backend/output or an equivalent action has been taken.
        - No Sequencer internal timing state is changed by this method (timing/state is managed by callers). If an implementation needs to track active notes, it must do so explicitly and document the side effects.

## Side Effects:
    - The base method: none.
    - Concrete implementations typically have external side effects:
        - Send a MIDI "note on" message (or library-specific equivalent) to a MIDI device, virtual port, or software synthesizer.
        - May perform I/O (blocking or non-blocking) and may raise exceptions originating from the MIDI library or OS.
        - May need to convert channel numbering (1-based to 0-based) and clamp/validate note/velocity values.
    - Implementations intended for testing can override this method to record events in-memory instead of performing I/O.

Implementation guidance (for reimplementers):
- Keep the method small and side-effect focused: do not implement timing, listener notification, or scheduling here — those are handled elsewhere in Sequencer.
- Typical steps in an override:
    1. Validate/coerce note, channel, velocity to ints.
    2. Optionally validate/clamp ranges (note and velocity to 0..127, channel to 1..16) or translate and raise a ValueError for invalid values.
    3. Convert channel to backend's expected form (e.g., channel - 1 for 0-based APIs).
    4. Emit a "note on" via the MIDI library or write to self.output if that attribute holds a backend object.
    5. Do not modify Sequencer timing state; if you need to track active notes for later note-off, keep that tracking in the backend implementation or in stop_event.

Examples of acceptable override behaviors:
- Real MIDI backend: send a MIDI note-on packet to a port with the given channel and velocity.
- Test backend: append (note, channel, velocity, timestamp) to an in-memory list for assertions in unit tests.
- File backend: write a note-on event to a MIDI file structure.

### `mingus.midi.sequencer.Sequencer.stop_event` · *method*

## Summary:
Ends a sounding MIDI note on a given channel. In the Sequencer base class this is a no-op; concrete backends should implement sending a MIDI Note-Off (or equivalent) so the specified note stops sounding. The method itself does not change Sequencer-internal state in the base implementation.

## Description:
This method is the backend hook that actually performs the "stop note" action for a given (note, channel) pair. The Sequencer base provides the playback timing and higher-level orchestration; stop_event isolates backend-specific I/O so different MIDI output implementations can provide the correct low-level message.

Known callers and exact calling contexts:
- stop_Note(note, channel): Calls stop_event(int(note) + 12, int(channel)) and then notifies listeners (MSG_STOP_INT and MSG_STOP_NOTE). That is, stop_event is invoked first; listener notifications occur after the call returns.
- stop_NoteContainer(nc, channel): Iterates over notes in the NoteContainer and calls stop_Note for each one.
- stop_everything(): Iterates over a range of note numbers and channels and calls stop_Note for each combination.
- Playback control flows (play_Bar, play_Bars, play_Track, play_Tracks, play_Composition): When a note's scheduled duration completes, these routines call stop_NoteContainer or stop_Note which ultimately invoke stop_event.

Why this method is separate:
- Backends differ in how to express "note off" (explicit Note-Off message or a Note-On with velocity 0), and in what I/O handle they use. Providing a single overridable hook keeps playback logic independent from device/protocol specifics and centralizes message formatting and delivery in backend subclasses.

## Args:
    note (int):
        MIDI note number to stop. Expected to be integer-like. Typical MIDI note range is 0..127 inclusive. Note: some Sequencer callers (e.g., stop_Note and play_Note) add an offset (int(note) + 12) before calling stop_event; implementations should therefore accept already-offset note numbers.
    channel (int):
        MIDI channel for the note. The Sequencer methods use integer channels; many public APIs in the class default to 1-based channels (e.g., play_Note defaults to channel=1), but some internal loops (e.g., stop_everything) iterate channels 0..15. Do not assume a single convention — treat channel as an integer passed-through by callers and document backend expectations (0-based vs 1-based) in the subclass.

## Returns:
    None
    The base method returns nothing (implicitly None). Backend implementations should perform side effects (send messages) and likewise need not return a value.

## Raises:
    Base implementation:
        - Does not raise any exceptions.
    Backend implementations:
        - May raise I/O or device-specific exceptions (e.g., device closed, write errors). Those exceptions are backend-specific and should be documented by the subclass.

## State Changes:
    Attributes READ:
        - None by the base (pass) implementation.
        - Backend implementations commonly read:
            - self.output (class attribute defined on Sequencer) or any backend-specific handle stored on self that references the MIDI device/port.
    Attributes WRITTEN:
        - None by the base implementation.
        - Backend implementations should avoid mutating unrelated Sequencer state; they may update backend-specific fields (e.g., last_sent_message) if useful, but Sequencer playback logic does not require such mutations.

## Constraints:
    Preconditions:
        - The Sequencer instance should be properly initialized.
        - If a backend depends on an open MIDI handle (e.g., self.output), that handle must be present and ready; otherwise the backend implementation should check and raise appropriate errors.
        - Callers should pass integer-like note and channel values (the Sequencer higher-level methods already cast to int).
    Postconditions:
        - After a correct backend implementation runs, the specified (note, channel) will no longer be sounding on the MIDI output (either via an explicit Note-Off or the common Note-On-with-zero-velocity idiom).
        - The base Sequencer makes no guarantees about internal attribute mutation; playback-level notifications (MSG_STOP_INT, MSG_STOP_NOTE) are sent by callers after stop_event returns.

## Side Effects:
    - Intended: emit a MIDI "note off" action to the selected output (device, virtual port, or file). This is I/O and may block or fail.
    - No listener notification is performed inside this method in the base class — higher-level Sequencer callers handle MSG_STOP_* notifications after calling stop_event.
    - Implementations may perform logging, error handling, or metadata updates; any such side effects should be documented by the backend subclass.

### `mingus.midi.sequencer.Sequencer.cc_event` · *method*

## Summary:
A backend hook that performs a MIDI Control Change (CC) action for the sequencer. The default implementation is a no-op; subclasses or concrete backends should override this to send the CC message to the MIDI output. Does not change Sequencer state by itself.

## Description:
- Known callers:
    - control_change(channel, control, value) — validates ranges then calls this method.
    - modulation(channel, value) — convenience wrapper that calls control_change(channel, 1, value).
    - main_volume(channel, value) — convenience wrapper that calls control_change(channel, 7, value).
    - pan(channel, value) — convenience wrapper that calls control_change(channel, 10, value).

  These callers invoke cc_event during playback or when the application requests a control change. control_change handles validation and listener notification; cc_event is intended to perform the actual I/O side-effect (sending the message to hardware or a MIDI backend).

- Why this is a separate method:
  - It isolates backend-specific MIDI I/O from sequencing and validation logic. Sequencer implements high-level control flow (validation, listener notification); cc_event is the extensibility point for different MIDI backends (e.g., ALSA, PortMidi, a software synth, or a test double). This keeps sequencing code backend-agnostic and makes testing easier.

## Args:
    channel (int): MIDI channel number. Sequencer convention uses 1..16 channels; callers (e.g., play_Note) pass channel numbers starting at 1. This method should accept an int-like channel (castable to int).
    control (int): Controller number. Sequencer.control_change enforces 0 <= control <= 128; typical MIDI controllers are 0..127. Implementations should assume the caller has already validated this range when called from control_change.
    value (int): Controller value. Sequencer.control_change enforces 0 <= value <= 128; typical MIDI values are 0..127. Implementations should assume the caller has already validated this range when called from control_change.

## Returns:
    None
    - The method is intended for side-effects (sending a MIDI message). The Sequencer API does not expect a return value from cc_event; control_change ignores any return.

## Raises:
    - The base implementation does not raise any exceptions (it is a no-op). Implementations may raise exceptions if the backend I/O fails (for example, if self.output is set but the backend refuses the message). If raising, prefer raising concrete exceptions from the backend or IOError/RuntimeError to signal I/O failure.

## State Changes:
    Attributes READ:
        - self.output : implementations will typically read this attribute to obtain the backend/output object (if set) to send the control-change message.
        - (indirect) self.listeners are not read by this method; listener notification is handled by control_change prior to calling cc_event.
    Attributes WRITTEN:
        - None by default. The base method does not modify Sequencer attributes. Implementations should avoid mutating Sequencer state unless intentionally required.

## Constraints:
    Preconditions:
        - If called from control_change, control and value have already been validated to be within 0..128 (control_change returns False and does not call cc_event otherwise).
        - channel is expected to be an int-like value representing a MIDI channel (1..16 by convention). No channel bounds check is enforced here by the base method.
        - self.output may be None. Implementations should handle a missing output gracefully (no-op or a logged warning) unless a stricter policy is desired.

    Postconditions:
        - After returning, the Sequencer object is unchanged by the default implementation.
        - If overridden to perform I/O, the corresponding control-change message will have been emitted to the backend (subject to backend success). control_change will still handle listener notification.

## Side Effects:
    - Default implementation: none (no I/O).
    - Typical implementation side effects:
        - Send a MIDI Control Change message to external hardware/software via self.output (for example, calling an API such as output.control_change(channel, control, value) or sending the appropriate MIDI bytes).
        - Possible I/O errors or backend-specific exceptions if the output is unavailable or the backend fails.
    - This method should not perform long blocking work beyond what is necessary to emit the MIDI message; sequencing timing is handled elsewhere (Sequencer.sleep), and listener notification is already performed by control_change.

### `mingus.midi.sequencer.Sequencer.instr_event` · *method*

## Summary:
Hook for handling an instrument/program change (and optional bank) for a given MIDI channel; in the base Sequencer this is a no-op, and subclasses should implement device-specific behavior that updates playback output or device state.

## Description:
Known callers and call sites:
- Sequencer.set_instrument(channel, instr, bank=0): primary caller — set_instrument invokes this method immediately before notifying listeners about the instrument change.
- Sequencer.play_Tracks(...) during playback: play_Tracks examines each track's MidiInstrument and calls set_instrument(...) for the corresponding playback channel; that call in turn invokes this method.
Typical lifecycle / pipeline stage:
- Invoked when a track or user requests a program/bank change prior to or during playback (track initialization, track switch, or explicit instrument set).
Why this is a separate method:
- The base Sequencer must expose a stable hook that concrete subclasses (real MIDI backends, synth drivers, or test doubles) can override to perform the actual I/O or internal state update. Keeping the logic in a dedicated instr_event method isolates device-specific code (sending program-change and bank-select messages, configuring soft-synth presets, updating internal device state) from the higher-level sequencing and listener-notification logic.

## Args:
    channel (int):
        MIDI channel identifier as passed by callers. Callers in this codebase typically use 1..16 channels (Sequencer methods use channel numbers like 1 by default). The method accepts any integer-like value convertible to int; concrete backends may enforce the 1..16 constraint.
    instr (int):
        Program/instrument number as passed by callers. The Sequencer passes the value through unchanged to listeners; the MidiInstrument helper class in this codebase uses a convention of 1-based instrument numbers, but callers may pass 0-based values. Concrete implementations should document which convention they require. Typical MIDI program range: 0..127 (or 1..128 when using 1-based convention).
    bank (int):
        Optional bank number (passed by callers such as set_instrument with default 0). Typical MIDI bank numbers are non-negative integers; concrete backends decide valid ranges. This signature requires an explicit bank argument (no default here), but higher-level helpers call it with bank=0 when omitted.

## Returns:
    None
    - The base implementation does not return a value. Subclasses may return a boolean success flag or raise on error, but the Sequencer core (set_instrument) does not inspect any return value from instr_event.

## Raises:
    - The base implementation raises no exceptions (it's a no-op).
    - Subclasses may raise exceptions for invalid arguments or I/O errors; such behavior must be documented by the subclass. The Sequencer core does not perform argument validation before calling instr_event.

## State Changes:
Attributes READ:
    - None in the base implementation.
    - Implementers commonly read:
        - self.output (backend/port handle) if forwarding a MIDI message to an output device.
        - self.listeners is read indirectly by set_instrument after this call when notify_listeners is invoked.
Attributes WRITTEN:
    - None in the base implementation.
    - Implementations may update backend-specific state on self (for example, an internal mapping of channel → current program/bank) or write to external output handles.

## Constraints:
Preconditions:
    - channel, instr, and bank should be integer-like (convertible to int) and meaningful for the concrete backend (e.g., channel in 1..16 for many MIDI devices).
    - If callers rely on MidiInstrument conventions, callers may pass 1-based instrument numbers; implementations must document which convention they expect.
Postconditions:
    - Base: no state changes are guaranteed.
    - When overridden, a correct implementation should ensure the device/backend reflects the requested program and bank for the specified channel after the call (for example, after implementation returns, subsequent notes on that channel should be played using the new program).

## Side Effects:
    - Base: none.
    - Intended implementations: send MIDI Program Change and (optionally) Bank Select messages to an output port or synth; update any cached mapping of channel → program/bank; perform logging. Any I/O, blocking operations, or errors caused by device access are the responsibility of the subclass implementation.

### `mingus.midi.sequencer.Sequencer.sleep` · *method*

## Summary:
A playback timing hook: in the base Sequencer this method is a no-op; subclasses should override it to pause execution for the requested duration so playback timing between events is enforced.

## Description:
Known callers:
- Direct: play_Bar, play_Bars
- Indirect (via those): play_Track, play_Tracks, play_Composition

Context:
- Invoked inside the sequencer's playback loops between note containers/events to advance time by the specified duration (the caller computes the time interval in seconds).
- The base-class implementation intentionally does nothing (pass). This class-level hook separates timing strategy from playback logic so different backends (blocking sleep, event-loop scheduling, real-time midi output) or tests can provide their own timing behavior by overriding this method.

Why this is a separate method:
- Playback functions compute timing intervals but should not assume a single mechanism for delaying execution. Extracting the wait into a dedicated method allows subclasses or external integrations to replace the blocking behavior with non-blocking scheduling, mockable no-op behavior for fast tests, or system-specific timing (e.g., high-precision timers, GUI event loops, or realtime MIDI frameworks).

## Args:
    seconds (float or int): Duration to wait in seconds. Expected to be non-negative. The callers pass a floating-point number (computed from bpm and note length). No default — required positional argument.

## Returns:
    None

## Raises:
    Base implementation: does not raise.
    Subclass implementations: may raise TypeError or ValueError if the provided seconds cannot be interpreted as a non-negative numeric value. Implementations should document and enforce their own error behavior.

## State Changes:
    Attributes READ:
        - None (base implementation does not read any Sequencer attributes)
    Attributes WRITTEN:
        - None (base implementation does not modify Sequencer state)

## Constraints:
    Preconditions:
        - self must be a valid Sequencer instance.
        - seconds should represent seconds as a numeric value (float or int). Callers compute seconds from bpm and note lengths; they expect the argument to be in seconds, not milliseconds.
    Postconditions:
        - Base implementation: no change to self and no blocking — returns immediately.
        - Well-behaved override: after the method returns at least approximately `seconds` seconds of real time have elapsed (subject to scheduler resolution), and playback timing advances accordingly.

## Side Effects:
    Base implementation: none.
    Typical override side effects:
        - Blocking the current thread for the requested duration (e.g., calling time.sleep(seconds)).
        - If integrated with a MIDI output/timer system, may schedule or drive external timers and cause MIDI events to be emitted according to elapsed time.
        - Implementations may interact with external services, event loops, or testing harnesses; callers rely on the chosen implementation to enforce timing.

### `mingus.midi.sequencer.Sequencer.attach` · *method*

## Summary:
Adds a listener object to the sequencer's listener list if it is not already present, thereby updating the Sequencer's set of observers used for playback notifications.

## Description:
This method performs a simple deduplicating registration of a listener that will later receive event notifications via the Sequencer.notify_listeners method. There are no internal callers in this class; attach is intended to be invoked by external setup or initialization code (for example, when wiring UI components, MIDI output/bridge adapters, or other observer objects to a Sequencer before playback). Keeping this logic in a single method centralizes listener registration and the "no-duplicates" semantics so other code does not need to manage listener list invariants.

## Args:
    listener (object): Any object intended to receive sequencer events. The Sequencer expects listeners to implement a notify(msg_type, params) method (used later by notify_listeners), but attach does not enforce this. Allowed values: any Python object. Default: no default; argument is required.

## Returns:
    None: The method returns None implicitly and does not produce a value.

## Raises:
    None: attach itself does not raise exceptions. However, adding an invalid listener (for example None or an object without a notify method) will not raise here but will cause errors later when notifications are dispatched (AttributeError when notify_listeners calls listener.notify).

## State Changes:
    Attributes READ:
        - self.listeners: membership is checked with "if listener not in self.listeners".
    Attributes WRITTEN:
        - self.listeners: the listener is appended (self.listeners.append(listener)) when not already present.

## Constraints:
    Preconditions:
        - self.listeners must exist and support membership testing and append (i.e., be a list or list-like). The Sequencer.__init__ initializes this to an empty list, so Sequencer must be initialized before calling attach.
        - If the caller expects the listener to receive notifications later, the listener must implement notify(msg_type, params). attach does not validate this.
    Postconditions:
        - After the call, listener is present in self.listeners.
        - If a listener equal (by ==) to the provided listener was already present, the list is unchanged (no duplicate is appended).
        - The method never creates duplicate listeners according to Python's membership (equality) semantics.

## Side Effects:
    - Mutates the Sequencer instance by appending to the self.listeners list when appropriate.
    - No I/O is performed and no external services are invoked.
    - Not thread-safe: concurrent calls from multiple threads may produce race conditions (e.g., duplicates or lost updates) unless the caller synchronizes externally.

### `mingus.midi.sequencer.Sequencer.detach` · *method*

## Summary:
Removes a previously attached listener from the sequencer's listener registry if it is present, mutating the internal listeners list.

## Description:
- Known callers and context:
    - There are no internal callers of this method elsewhere in the sequencer class besides external client code. Typical callers are external components that previously subscribed to sequencer events via the attach method and now wish to unsubscribe (for example, UI widgets, MIDI output adapters, or other observer objects).
    - This method is invoked during the lifecycle stage when a consumer no longer needs event notifications (tear-down, object disposal, or when switching output targets).
- Why this is a dedicated method:
    - Encapsulates listener-management behavior (paired with attach) so callers do not manipulate the internal listeners list directly.
    - Provides a single override point for subclasses that might need custom detach behavior (logging, resource cleanup, thread-safety wrappers).
    - Keeps attach/detach semantics consistent and centralized, improving maintainability and enabling future extension (e.g., event filtering or safe removal in multithreaded contexts).

## Args:
    listener (object): The listener instance to remove. Expected to be the same object instance previously passed to attach. There is no type enforcement in code, but listeners are expected to implement a notify(msg_type, params) method (as used by notify_listeners).

## Returns:
    None: The method performs in-place mutation of self.listeners and returns None implicitly.

## Raises:
    None: The method guards membership before removal, so it will not raise ValueError for a missing listener. It does not raise any exceptions itself under normal conditions. (Note: if self.listeners has been reassigned to a non-list object or mutated concurrently in another thread, non-standard exceptions may occur — the implementation does not provide thread-safety guarantees.)

## State Changes:
- Attributes READ:
    - self.listeners (membership checked using the membership test)
- Attributes WRITTEN:
    - self.listeners (the list is mutated by removing an element when present)

## Constraints:
- Preconditions:
    - self.listeners must be a sequence supporting membership testing and the remove operation (the Sequencer constructor initializes this as a list).
    - The caller should pass the exact listener object instance that was previously attached; equality semantics (==) are used for membership testing.
- Postconditions:
    - If the specified listener object was present in self.listeners, one occurrence of that object has been removed from the list.
    - If the listener was not present, self.listeners is unchanged.
    - The method returns None.

## Side Effects:
- Mutates the sequencer's internal listeners list (in-memory state of self).
- No I/O, no external service calls, and no direct notifications are sent by this method itself. Subsequent operations (e.g., future notify_listeners calls) will no longer include the detached listener.
- Not thread-safe: concurrent modifications to self.listeners by other threads may cause race conditions or exceptions; callers requiring thread-safety should serialize access externally or override this method.

### `mingus.midi.sequencer.Sequencer.notify_listeners` · *method*

## Summary:
Iterates the sequencer's registered listeners and delivers an event to each by calling their notify(msg_type, params), causing no internal state mutation of the Sequencer itself.

## Description:
This method is the central dispatch point for broadcasting sequencer events to external observers (listeners). It is called throughout playback and control paths whenever the sequencer needs to inform interested parties about events (for example, note-on, note-off, control changes, instrument changes, sleep/timing events, and higher-level playback lifecycle events). Known callers within the Sequencer class include:
- set_instrument — when an instrument/bank is set for a channel
- control_change — when a controller value is changed
- play_Note / stop_Note — when individual notes are started or stopped
- play_NoteContainer / stop_NoteContainer — when NoteContainers begin or end
- play_Bar / play_Bars / play_Track / play_Tracks / play_Composition — various playback stages
- places that report timing/sleep use MSG_SLEEP via notify_listeners

This logic is extracted into its own method to centralize notification behavior (single place to change how listeners are called), to keep callers concise, and to allow reuse and potential future enhancements (e.g., logging, filtering, exception handling, or asynchronous dispatch) without changing many call sites.

## Args:
    msg_type (int):
        An integer code identifying the message type. Typically one of the Sequencer.MSG_* constants (e.g., MSG_PLAY_INT, MSG_STOP_NOTE, MSG_CC, MSG_INSTR, MSG_SLEEP, MSG_PLAY_BAR, MSG_PLAY_TRACK, MSG_PLAY_COMPOSITION, etc.). No validation is performed here — callers are expected to pass a meaningful constant.
    params (dict or any):
        A mapping or object containing event-specific parameters. Commonly a dict with keys such as "channel", "note", "velocity", "control", "value", "bank", "bars", "tracks", "s" (seconds), etc. The method forwards this object unchanged to the listener.notify method.

## Returns:
    None
    The method does not return a value.

## Raises:
    Any exception raised by a listener's notify method is propagated.
    - If a listener's notify implementation raises an exception (e.g., RuntimeError, TypeError, IOError), notify_listeners does not catch it; the exception will exit notify_listeners and propagate to the caller.
    - If self.listeners is not an iterable (unexpected mutation of object state), a TypeError may be raised by the for-loop before any notify calls occur.

## State Changes:
    Attributes READ:
        self.listeners
    Attributes WRITTEN:
        None (the Sequencer's attributes are not modified by this method)

## Constraints:
    Preconditions:
        - self.listeners must be an iterable of listener objects (Sequencer.__init__ initializes this to a list).
        - Each listener object in self.listeners must provide a callable notify(msg_type, params) method that accepts two arguments.
        - msg_type is expected to be one of the Sequencer.MSG_* constants (not enforced here).
    Postconditions:
        - Every listener that was iterated over has had its notify(msg_type, params) method invoked, unless an exception occurred which interrupted the loop.
        - The Sequencer's internal state (attributes) remains unchanged by this call.

## Side Effects:
    - Delegates to listener.notify(msg_type, params). Those notify implementations may perform arbitrary side effects: send MIDI output, write to I/O, update UI, log, modify shared state, register/deregister listeners, etc.
    - Because this method does not catch exceptions, a failing listener can abort the notification sequence and prevent remaining listeners from being notified.
    - Mutating the self.listeners list (adding/removing listeners) while iterating may lead to unpredictable notification behavior (listeners may be skipped or additional listeners may not receive the message). The method does not make a defensive copy of the listeners list.

### `mingus.midi.sequencer.Sequencer.set_instrument` · *method*

## Summary:
Sets the MIDI instrument for a channel on this Sequencer by emitting the low-level instrument-change event and notifying all attached listeners; updates no internal state beyond invoking those side-effecting calls.

## Description:
Known callers and context:
- Sequencer.play_Tracks: invoked prior to playback to configure each track's MIDI program (instrument) for its assigned channel. This is the only internal caller present in the Sequencer implementation.
- Typical lifecycle: called during track setup or when a client wants to change the instrument on a channel before or during playback.

Why this is a separate method:
- Encapsulates the two-step operation of notifying the underlying MIDI layer (instr_event) and broadcasting the change to any observers (notify_listeners) in a single, reusable place.
- Allows subclasses or concrete Sequencer implementations to override instr_event or notify_listeners independently while preserving the consistent external behavior of an instrument change.

## Args:
    channel (int-like): Channel identifier. Values convertible to int are accepted; no explicit range checks are performed here.
    instr (int-like): Program/instrument number. Values convertible to int are accepted; no explicit range checks are performed here.
    bank (int-like, optional): Bank number for the instrument. Defaults to 0. Values convertible to int are accepted.

## Returns:
    None: The method does not return a value. Its effect is side-effectual (calls instr_event and notifies listeners).

## Raises:
    ValueError: If any of channel, instr, or bank cannot be converted to int when notify_listeners attempts int(...) on them, a ValueError may be raised (e.g., int("abc")).
    TypeError: If any of channel, instr, or bank are of a type that int(...) cannot handle (e.g., int(None)), int(...) may raise TypeError.
    Any exception raised by instr_event or any listener's notify method will propagate out of this method (types depend on those implementations).

## State Changes:
Attributes READ:
    self.MSG_INSTR — the message type constant used when notifying listeners.
    self.listeners — read indirectly by notify_listeners when iterating and calling each listener.notify.

Attributes WRITTEN:
    None — the method does not assign to any self.<attr> fields.

## Constraints:
Preconditions:
    - The caller should supply values for channel, instr, and optional bank that are meaningful to the underlying MIDI layer; although not enforced here, typical valid ranges are:
        * channel: 1..16 (Sequencer does not enforce this)
        * instr: 0..127 (MIDI program numbers)
        * bank: non-negative integer (implementation dependent)
    - Listeners previously attached via attach(listener) should expose a notify(msg_type, params) method; otherwise notify_listeners will raise at runtime.

Postconditions:
    - instr_event(channel, instr, bank) has been invoked (so any low-level instrument-change behavior executed by subclasses/implementations will have run).
    - notify_listeners has been invoked with msg_type self.MSG_INSTR and params {"channel": int(channel), "instr": int(instr), "bank": int(bank)}; as a result, all attached listeners have been asked to handle the instrument-change event (or an exception propagated if a listener raises).

## Side Effects:
    - Calls instr_event(channel, instr, bank) — this may perform I/O (send MIDI program-change messages) or mutate external MIDI device state depending on the Sequencer implementation.
    - Calls notify_listeners(self.MSG_INSTR, params) which iterates self.listeners and calls each listener.notify(msg_type, params). Those listener.notify calls may perform arbitrary side effects (I/O, logging, state mutation) and may raise exceptions that propagate.
    - No direct I/O is performed by this method itself, but side-effecting behaviors occur via the called methods.

### `mingus.midi.sequencer.Sequencer.control_change` · *method*

## Summary:
Performs a MIDI control change operation after validating parameters, delegates the low-level event to the sequencer backend, and notifies attached listeners; returns True on success and False when parameter validation fails.

## Description:
This method is invoked when the application or convenience helper methods request a control change to be sent on a given channel. Known internal callers include:
    - modulation(channel, value): maps to control number 1
    - main_volume(channel, value): maps to control number 7
    - pan(channel, value): maps to control number 10

Typical lifecycle: called during playback or when an external API/client requests a controller update. The method centralizes input validation, delegates the actual output to cc_event (the backend hook) and then broadcasts the change to any attached listeners via notify_listeners. Having this logic in a single method prevents duplicated validation and notification logic across helpers and ensures a consistent notify payload.

## Args:
    channel (int-like): The MIDI channel for the control change. The method does not enforce a channel range; callers typically use 1..16 but this is not validated here.
    control (int-like): Controller number. Allowed (per implementation check): 0 through 128 inclusive. Typical MIDI controllers use 0..127; this method permits 128 because the code checks > 128 (not >= 128).
    value (int-like): Controller value. Allowed (per implementation check): 0 through 128 inclusive. Typical MIDI values use 0..127; 128 is permitted here for the same reason as above.

Notes on types: The method accepts values that can be compared with integers and later uses int(...) when building the notify payload. Non-integer numeric types (e.g., floats) will be cast to int in the notification payload; the original (un-casted) values are passed to cc_event.

## Returns:
    bool: True if the control and value passed validation and the method proceeded to call cc_event and notify_listeners; False when validation failed (control or value out of allowed range).

## Raises:
    No exceptions are explicitly raised by control_change itself.
    Note: notify_listeners will call listener.notify(...) for each attached listener without internal exception handling — exceptions raised by listeners (or by cc_event) will propagate out of control_change.

## State Changes:
    Attributes READ:
        - self.MSG_CC: used as the message type identifier in the notify_listeners call.
        - self.listeners: read indirectly by notify_listeners when iterating attached listeners.
    Attributes WRITTEN:
        - None directly within control_change's body.
        - Side-effect: it calls self.cc_event(channel, control, value) which may mutate internal state depending on the Sequencer subclass/implementation.

## Constraints:
    Preconditions:
        - The caller should supply control and value in the numeric range 0..128 inclusive (per code checks). If this precondition is violated, the method returns False and does not call cc_event or notify_listeners.
        - channel should be an integer-like value appropriate for the backend; typical valid MIDI channel numbers are 1..16 but the method does not enforce this.

    Postconditions:
        - On return True: cc_event(channel, control, value) has been invoked, and notify_listeners has been called with msg_type self.MSG_CC and a params dict containing integer-casted values for "channel", "control", and "value".
        - On return False: neither cc_event nor notify_listeners is invoked and no state changes are made by control_change itself.

## Side Effects:
    - Calls self.cc_event(channel, control, value). In concrete Sequencer implementations this is the hook that should send or queue the actual MIDI Control Change message; it may perform I/O or mutate internal send queues.
    - Calls self.notify_listeners(self.MSG_CC, {"channel": int(channel), "control": int(control), "value": int(value)}), which will invoke notify(...) on each attached listener. Those listener callbacks may perform I/O, update UI, log events, or raise exceptions that propagate out of this method.
    - The notify payload casts channel, control, and value to ints for the listener notification, but cc_event receives the original arguments unchanged.
    - No internal try/except is used, so any exception from cc_event or a listener will not be swallowed by control_change.

### `mingus.midi.sequencer.Sequencer.play_Note` · *method*

## Summary:
Starts playback of a single note: determines channel/velocity (optionally from the note object), issues the low-level play_event (transposed up one octave), notifies attached listeners about both the integer MIDI event and the high-level note object, and returns True on success.

## Description:
Known callers and typical context:
- play_NoteContainer: iterates a NoteContainer and calls this method for each contained note during playback.
- play_Bar, play_Bars, play_Track, play_Tracks, play_Composition: higher-level playback loops that eventually invoke play_Note (directly or indirectly) as they expand bars/tracks into note events.
Lifecycle stage:
- Invoked during the playback pipeline when a note should begin sounding; this method centralizes the "start note" action for both internal MIDI output and external listener notification.

Why this is a separate method:
- Encapsulates the repeated logic of extracting channel and velocity from either parameters or a note object, performing a consistent transposition (+12 semitones), calling the backend play_event, and broadcasting two distinct notifications. Keeping this logic in one method avoids duplication across the various playback loops.

## Args:
    note (int or object): The note to play. Must be convertible with int(note). If `note` has attribute `velocity`, that value overrides the velocity argument. If `note` has attribute `channel`, that value overrides the channel argument. The integer value used with the MIDI event is int(note) + 12 (one octave up).
    channel (int, optional): MIDI channel to use if `note` does not define .channel. Default is 1. Value is converted with int(channel) before use.
    velocity (int, optional): Note velocity if `note` does not define .velocity. Default is 100. Value is converted with int(velocity) before use.

## Returns:
    bool: Always returns True on successful completion of the method body. Note that this does not guarantee the note was heard; it only indicates that this method completed its call sequence (play_event and listener notifications) without raising an exception.

## Raises:
    TypeError or ValueError: Raised if int(note), int(channel), or int(velocity) fail (for example, note is None or not int-convertible, or channel/velocity are invalid types).
    Any exception raised by self.play_event(...): this method does not catch exceptions from play_event.
    Any exception raised by listener.notify(...) called inside notify_listeners: exceptions from listeners propagate outwards (this method does not catch them).

## State Changes:
Attributes READ:
    self.MSG_PLAY_INT
    self.MSG_PLAY_NOTE
    self.listeners (indirectly via notify_listeners)
    self.play_event (method invoked)
    self.notify_listeners (method invoked)

Attributes WRITTEN:
    None (this method does not modify attributes on self).

## Constraints:
Preconditions:
    - `note` must be convertible to an integer via int(note).
    - If relying on implicit channel/velocity, note.channel and/or note.velocity (if present) should be valid and int()-convertible.
    - No internal validation is performed for MIDI ranges; callers should supply channel/velocity in appropriate MIDI ranges if required (typical MIDI channel: 1–16, velocity: 0–127), but the method will attempt to convert and use whatever ints are supplied.

Postconditions:
    - self.play_event is invoked with the integer note value transposed by +12: play_event(int(note) + 12, int(channel), int(velocity))
    - self.notify_listeners is called twice:
        1) MSG_PLAY_INT with a dict: {"channel": int(channel), "note": int(note) + 12, "velocity": int(velocity)}
        2) MSG_PLAY_NOTE with a dict: {"channel": int(channel), "note": note, "velocity": int(velocity)}
    - The method returns True if the above calls complete without raising an exception.

## Side Effects:
    - Calls self.play_event(...): this is the backend hook where MIDI output or other sound generation is expected to occur.
    - Calls self.notify_listeners(...): iterates self.listeners and calls their notify(msg_type, params) method(s), which may trigger external callbacks, logging, UI updates, or further side effects.
    - No file I/O or network I/O happens directly in this method, but listeners or play_event implementations may perform such I/O.

### `mingus.midi.sequencer.Sequencer.stop_Note` · *method*

## Summary:
Stops (turns off) a single musical note: sends a low-level note-off event (using the sequencer's stop_event) for the integer MIDI note code (note converted to int and offset by 12), notifies registered listeners about the internal note-off and the high-level note object stop, and returns True on success.

## Description:
Known callers and usage contexts:
- stop_NoteContainer — iterates a NoteContainer and calls stop_Note for each contained note when the container should be released.
- stop_everything — calls stop_Note for a wide range of notes/channels when the sequencer must silence all notes.
- play_Bar / play_Bars / play_Track / play_Tracks — indirectly via higher-level playback logic when bars or tracks finish playing (these methods call stop_NoteContainer, which in turn calls stop_Note).
- It may also be called directly by external code to stop a single note.

Lifecycle stage:
- Invoked during playback teardown or when an individual note-off is required (end of a NoteContainer, explicit stop request, or global stop). It represents the sequencer's single-note "note-off" action.

Why this logic is its own method:
- Centralizes note-off behavior (conversion to integer MIDI note, low-level stop_event invocation, and listener notifications) so callers don't need to duplicate that sequence.
- Matches play_Note's structure (which encapsulates the corresponding "note-on" path) enabling consistent behavior, easier maintenance, and a single point to add logging or instrumentation for note-off behavior.

## Args:
    note (int or object):
        - Expected to be convertible to int (int(note) is called).
        - May be a domain object (e.g., a Note instance) that implements __int__ (or is coercible to int) and optionally has a channel attribute.
        - If the object has a .channel attribute, that value overrides the channel parameter.
    channel (int, optional):
        - Default: 1
        - Intended MIDI channel number to stop the note on. Typical valid values are 1..16 for MIDI, but the method does not enforce bounds; callers should pass valid channel numbers.

## Returns:
    bool:
        - Always returns True when execution reaches the final return statement.
        - Note: if conversion (int(note)) or listener notification raises an exception, this method will not return; such exceptions propagate.

## Raises:
    - No exceptions are explicitly raised by this method.
    - Exceptions that may propagate:
        * TypeError or ValueError: if int(note) cannot convert the provided note (e.g., note is a non-numeric object without __int__).
        * Any exception raised by self.stop_event(note, channel) — stop_event is called directly and any error it raises will propagate.
        * Any exception raised by a listener's notify(...) called via self.notify_listeners; notify_listeners does not catch listener exceptions, so they propagate up.

## State Changes:
    Attributes READ:
        - self.MSG_STOP_INT (class attribute constant used as msg_type)
        - self.MSG_STOP_NOTE (class attribute constant used as msg_type)
        - self.listeners (indirectly, via notify_listeners which iterates this list)
        - Note: the method calls self.stop_event and self.notify_listeners (reads those attributes/methods).

    Attributes WRITTEN:
        - None — this method does not modify Sequencer attributes directly.

## Constraints:
    Preconditions:
        - self must provide a stop_event(note, channel) method (callable) that accepts two integers.
        - self must provide notify_listeners(msg_type, params) which will forward events to registered listeners.
        - note must be convertible to int (or else int(note) will raise).
        - If the note is an object that carries a channel attribute, that attribute should be a valid channel value (the method will use it without validation).

    Postconditions:
        - If the call completes normally (no exceptions), the sequencer will have:
            * Invoked self.stop_event with the integer note value (int(note) + 12) and int(channel).
            * Called notify_listeners twice:
                - First with msg_type self.MSG_STOP_INT and params {"channel": int(channel), "note": int(note) + 12}
                - Second with msg_type self.MSG_STOP_NOTE and params {"channel": int(channel), "note": note}
            * Returned True.

## Side Effects:
    - Calls self.stop_event(int(note) + 12, int(channel)), which is expected to perform the low-level action of stopping the specified MIDI note (e.g., sending a MIDI NOTE_OFF). That method may perform I/O, mutate other state, or interact with external MIDI outputs depending on implementation.
    - Calls self.notify_listeners(...) twice. Each registered listener's notify(msg_type, params) is invoked and may perform arbitrary side effects (emit MIDI, update UI, write logs, alter shared state, attach/detach listeners, raise exceptions, etc.). Because errors from listeners are not caught here, a failing listener can abort the sequence and prevent subsequent notifications or the method's normal return.
    - The method converts the provided note to an integer and adds a fixed offset of 12 before passing it to stop_event and the MSG_STOP_INT notification; the high-level MSG_STOP_NOTE notification forwards the original note object/value unchanged (so listeners receive both the internal integer-coded note and the original note object).

### `mingus.midi.sequencer.Sequencer.stop_everything` · *method*

## Summary:
Silences the sequencer by invoking the note-stop path for every note index 0–117 on all 16 MIDI channels, causing the sequencer (and any listeners) to process stop events; the method does not return a value.

## Description:
This method performs a double loop over 118 note indices (0 through 117 inclusive) and 16 MIDI channels (0 through 15 inclusive), calling self.stop_Note(note_index, channel) for every combination. Each stop_Note call triggers the sequencer's single-note stop behavior (stop_event and listener notifications), so calling stop_everything results in a burst of stop operations across the sequencer and its listeners.

Known callers and context:
- No explicit callers are present in the provided repository snapshot. Typical call sites include:
  - An "panic" or "all notes off" UI button.
  - A shutdown/cleanup routine before closing MIDI output or resetting the sequencer.
  - An error handler that needs to ensure no notes remain sounding.
- Lifecycle stage: used as a cleanup/emergency reset operation rather than during normal per-note playback.

Why this is its own method:
- Centralizes and standardizes the "stop all notes" behavior so other parts of the system can request a global silence with a single call.
- Reuses existing single-note stop semantics (stop_Note) to ensure consistent behavior and notifications rather than duplicating code.

## Args:
This method takes no arguments.

## Returns:
None. The method implicitly returns None; it does not aggregate or return individual stop_Note results.

## Raises:
- This method does not catch exceptions; any exception raised by stop_Note, stop_event, notify_listeners, or a listener.notify call will propagate and interrupt further processing. No exceptions are raised directly by stop_everything itself.

## State Changes:
Attributes READ:
- self.stop_Note (callable) — invoked repeatedly for each note/channel pair.

Attributes WRITTEN:
- None on the Sequencer instance itself (the method does not assign to self.* attributes).

Note: although stop_everything only directly accesses self.stop_Note, the invoked stop_Note calls read and write additional attributes (e.g., notifying self.listeners). Those side effects are executed as part of stop_Note.

## Constraints:
Preconditions:
- The Sequencer instance must be properly initialized so that stop_Note exists and is callable.
- Registered listeners (self.listeners) should be able to accept stop notifications; otherwise listener.notify may raise exceptions that will propagate.

Postconditions:
- If the loop completes without exceptions, stop_Note was invoked for each (note, channel) pair where:
  - note ranged 0..117 and channel ranged 0..15 (total 118 * 16 = 1,888 invocations).
  - Because stop_Note adds 12 to the passed note when calling stop_event, stop_event receives note numbers in the range 12..129.
- If an exception occurs, only the calls performed before the exception will have taken effect.
- The method itself returns None.

## Side Effects:
- Calls stop_Note repeatedly, which invokes stop_event(int(note) + 12, int(channel)) and notifies listeners with MSG_STOP_INT and MSG_STOP_NOTE for each invocation. This typically results in sending MIDI "note off" messages or equivalent.
- Generates a high volume of operations and notifications (1,888 calls); this can produce heavy CPU load and a burst of external I/O (MIDI messages, listener callbacks).
- May cause downstream behavior if stop_event or listener.notify perform I/O, mutate external state, or raise exceptions.
- Potential out-of-range MIDI note values: because stop_Note adds 12, stop_event will be called with notes 12..129 — values above 127 are outside the standard 0–127 MIDI range and handling depends on the downstream implementation (they may be ignored, clamped, or produce errors).

## Practical guidance:
- If you need guaranteed completion despite listener errors, wrap the call in try/except and, if appropriate, continue the loop or retry failed stops.
- If your MIDI backend cannot handle notes >127, consider ensuring stop_Note/stop_event clamp or ignore out-of-range notes before calling this method.
- Use sparingly: invoking this frequently may overwhelm MIDI backends or produce undesirable audible artifacts.

### `mingus.midi.sequencer.Sequencer.play_NoteContainer` · *method*

## Summary:
Plays every note in the given NoteContainer (or iterable of notes) by delegating to play_Note for each element and notifies listeners that a NoteContainer is being played; updates no stored state on the Sequencer itself.

## Description:
Known callers and context:
- play_Bar: invoked for each NoteContainer found in a bar while stepping through its events during playback.
- play_Bars: used when synchronizing and launching multiple bars across tracks.
- play_Track / play_Tracks / play_Composition: indirectly invoked when higher-level playback routines iterate through bars and tracks.
These callers use this method during the runtime playback pipeline when a collection of simultaneous notes (a chord or NoteContainer) must be started at once.

Why this is a separate method:
- Encapsulates the common behavior of starting every note in a container (iterate + delegate to play_Note) and emitting a single MSG_PLAY_NC notification. This avoids duplicating iteration and listener-notification logic in multiple higher-level playback functions and centralizes the failure semantics (stop on first failed note).

## Args:
    nc (iterable or object or None): A NoteContainer-like object or any iterable of notes. Allowed values:
        - None: treated as "nothing to play" and results in an immediate True return.
        - Any iterable whose elements are valid inputs for Sequencer.play_Note (note numbers or note objects).
    channel (int, optional): MIDI channel to pass to play_Note for each element. Defaults to 1.
        - The method does not validate channel range itself (play_Note or downstream code may).
    velocity (int, optional): Default velocity to pass to play_Note for each element. Defaults to 100.
        - Individual note objects may override these values if they carry velocity/channel attributes; play_Note handles those overrides.

## Returns:
    bool:
        - True if nc is None, or the method successfully invoked play_Note for every element in nc and every play_Note call returned a truthy value.
        - False if iteration reaches an element for which play_Note returned a falsy value (the method stops iterating and returns False).
    Edge cases:
        - If nc is an empty iterable, the method returns True (no notes to play).
        - Any exceptions raised by iteration, notify_listeners, or play_Note propagate out (see Raises).

## Raises:
    - This method does not raise exceptions intentionally; however it will propagate any exception thrown by:
        * notify_listeners (e.g., if a listener.notify raises)
        * iteration over nc (e.g., TypeError if nc is not iterable)
        * play_Note (any error coming from translating/playing a single note)
    No particular exception types are raised by play_NoteContainer itself.

## State Changes:
Attributes READ:
    - self.MSG_PLAY_NC (class/instance message constant) — read to inform notify_listeners of the message type.
    - (indirect) self.listeners is read by notify_listeners when it iterates and calls listener.notify, but play_NoteContainer does not access listeners directly.

Attributes WRITTEN:
    - None. The method does not modify Sequencer attributes.

## Constraints:
Preconditions:
    - The Sequencer instance must have working notify_listeners and play_Note methods (i.e., be initialized).
    - nc must be either None or an iterable whose elements are acceptable to play_Note.
    - channel and velocity should be values acceptable to play_Note; they are passed through unchanged.

Postconditions:
    - If True is returned: every element of nc (if any) was passed to play_Note and each such call returned truthy; listeners were notified once with MSG_PLAY_NC before any play_Note calls.
    - If False is returned: notify_listeners was invoked, iteration stopped at the first element where play_Note returned falsy, and that falsy result caused the method to return False.

## Side Effects:
    - Calls notify_listeners(self.MSG_PLAY_NC, {"notes": nc, "channel": channel, "velocity": velocity}), which invokes each attached listener's notify(msg_type, params) and can therefore cause arbitrary external behavior (logging, UI updates, external message forwarding).
    - Calls play_Note for each element of nc; play_Note itself triggers playback-related side effects (calling play_event, notifying listeners with play/interrupt messages, and interacting with any configured MIDI output).
    - No file I/O or network I/O is performed directly by play_NoteContainer, but side effects may occur via listener implementations or the underlying MIDI output used by play_Note.

### `mingus.midi.sequencer.Sequencer.stop_NoteContainer` · *method*

## Summary:
Notify listeners that a NoteContainer is being stopped, then stop every note in the container; returns True if all notes were stopped successfully (or the container is None/empty), otherwise returns False and aborts early.

## Description:
This method performs two coordinated actions when asked to stop a NoteContainer:
1. Immediately notifies attached listeners of an MSG_STOP_NC event with the container and channel.
2. Iterates the NoteContainer and calls stop_Note for each contained note, aborting and returning False if any individual stop fails.

Known callers and calling context:
- play_Bar: after sleeping for the duration of the note(s) in a bar, play_Bar calls this method to stop the notes that were started for a NoteContainer.
- play_Bars: used in scheduling the playback of multiple bars/tracks; play_Bars calls this method when a NoteContainer's duration has expired.
- play_Tracks / play_Composition (indirect): these higher-level playback functions call play_Bars/play_Bar which in turn call this method during playback lifecycle.
Lifecycle stage: invoked during the playback lifecycle when a previously started NoteContainer must be turned off (usually after a sleep/delay corresponding to the note duration).

Why separate method:
- Encapsulates the common pattern of notifying listeners about a container stop and stopping all contained notes. This avoids duplicating the notify + iteration + aggregated success semantics across multiple playback routines (play_Bar, play_Bars, etc.).
- Keeps playback control code concise and centralizes failure handling (early abort on a stop failure).

## Args:
    nc (iterable or None): The NoteContainer to stop. Expected to be an iterable of note objects or integers. If None, the method will only notify listeners and return True.
    channel (int, optional): MIDI channel number to use when stopping notes. Default is 1. If a note object has a 'channel' attribute, stop_Note may override this value per-note.

Allowed values / notes:
- nc may be None → handled explicitly (method returns True after notifying).
- channel is passed through to stop_Note; the method does not validate its range (typical MIDI channels: 1–16), so callers should ensure a valid channel if required by their backend.

## Returns:
    bool: True if all notes in the container were stopped (or if nc is None or empty). False if any call to stop_Note returned a falsy value, causing early termination.

Edge-return cases:
- If nc is None: returns True (after notifying).
- If nc is an empty iterable: the method iterates zero times and returns True.
- If stop_Note returns a non-boolean but truthy/falsy value, Python truthiness is used (truthy -> success, falsy -> failure).

## Raises:
    Any exception raised by notify_listeners or stop_Note will propagate:
    - If notify_listeners raises (e.g., a listener's notify method raises), this method does not catch it.
    - If stop_Note raises an exception while stopping an individual note, the exception propagates and the method does not suppress it.

No exceptions are explicitly raised by this method itself.

## State Changes:
Attributes READ:
    - self.MSG_STOP_NC: used as the message type when notifying listeners.
    - self.listeners (indirectly): notify_listeners iterates self.listeners to send the notification.
    - any state read by stop_Note (e.g., stop_Note may consult note attributes).

Attributes WRITTEN:
    - None directly. This method does not assign to any self.<attr>. Side-effecting methods it calls (notify_listeners, stop_Note) may mutate external state or self via their own implementations.

## Constraints:
Preconditions:
    - self must define:
        * a notify_listeners(msg_type, params) method that accepts the MSG_STOP_NC message type,
        * a stop_Note(note, channel) method that returns a truthy value on success and falsy on failure,
        * the attribute MSG_STOP_NC.
    - nc must be either None or an iterable of note-like objects (objects convertible to int or expected by stop_Note).
    - channel should be an integer (the method will not coerce or validate the range).

Postconditions:
    - If this method returns True: every note in nc was passed to stop_Note and each call returned a truthy value (or nc was None/empty). Listeners were notified with MSG_STOP_NC before any note stopping occurred.
    - If this method returns False: iteration stopped at the first note for which stop_Note returned a falsy value; some earlier notes may have been stopped, later notes were not processed. Listeners were still notified at the start.
    - If an exception propagates: notification has already been attempted (it occurs before iteration); some notes may have been stopped prior to the exception.

## Side Effects:
    - Calls notify_listeners(self.MSG_STOP_NC, {"notes": nc, "channel": channel}), which in turn invokes notify(msg_type, params) on each attached listener. Those listener notify handlers may perform I/O, logging, GUI updates, or other side effects.
    - Calls stop_Note(note, channel) for each note. stop_Note invokes stop_event and further notifications (MSG_STOP_INT and MSG_STOP_NOTE) and may interact with MIDI output, so stopping notes may produce external effects (e.g., sending MIDI "note off" messages to an output device).
    - No file, network, or persistent-storage I/O occurs directly in this method, but side-effecting behavior may occur through listeners or the underlying MIDI event handlers.

## Implementation notes & edge cases to preserve:
    - Always call notify_listeners at the start, even if nc is None.
    - Return True immediately when nc is None (after notifying).
    - Use the truthiness of stop_Note's return value to decide continuation: if not stop_Note(...): return False.
    - Do not catch exceptions from notify_listeners or stop_Note; let them propagate to the caller.
    - Maintain ordering: stop notes in the same order as the container iteration.

### `mingus.midi.sequencer.Sequencer.play_Bar` · *method*

## Summary:
Plays each scheduled NoteContainer in a bar using the Sequencer's play/sleep/stop pattern, updates listeners about playback and sleep intervals, honors per-note-container bpm overrides, and returns the final bpm used (or an empty dict if playback was aborted).

## Description:
This method implements the bar-level playback loop. For each element in the provided bar it:
- Notifies listeners that the bar playback is starting (MSG_PLAY_BAR).
- Attempts to start the NoteContainer via self.play_NoteContainer(note_container, channel, 100).
- If starting succeeds, checks for a per-note-container bpm override (note_container.bpm) and updates timing.
- Computes the duration for that note using the active bpm and the element's duration specifier (element[1]).
- Pauses execution for that duration via self.sleep(duration_in_seconds) and notifies listeners of the sleep interval (MSG_SLEEP with payload {"s": duration_in_seconds}).
- Stops the NoteContainer via self.stop_NoteContainer(note_container, channel).
- If play_NoteContainer returns a falsey value for any element, the method aborts immediately and returns {}.

Known callers and context:
- Invoked by higher-level playback orchestration code (e.g., methods that play a sequence of bars or an entire track) or by user-level code to play a single bar. It handles only the single-bar lifecycle; coordination across bars is the caller's responsibility.

Reason for being a separate method:
- Encapsulates repeated playback logic (start, timed wait, stop) and listener notifications, keeping bpm handling and timing centralized and reusable across higher-level playback flows.

## Args:
    bar (iterable): Iterable of indexable elements. Each element must provide:
        - element[1] (numeric, non-zero): duration specifier used as a denominator in the formula (4.0 / element[1]).
        - element[2] (object): NoteContainer-like playable object that is passed to play_NoteContainer/stop_NoteContainer.
        The method only indexes element[1] and element[2]; other element fields are ignored.
    channel (int, optional): MIDI channel to use for play/stop calls. Default: 1.
    bpm (int|float, optional): Starting beats-per-minute for timing. Default: 120. Must be > 0.

## Returns:
    dict: On normal completion returns {"bpm": bpm}, where bpm is the numeric bpm active at the end of the bar (may have been updated by per-note-container overrides).
    dict (empty): Returns {} if any call to self.play_NoteContainer(note_container, channel, 100) returns a falsey value, indicating playback was aborted.

## Raises:
    IndexError: If elements in `bar` are not indexable to access element[1] or element[2] (e.g., too short).
    ZeroDivisionError: If bpm or element[1] is zero and a division occurs (the method computes 60.0 / bpm and 4.0 / element[1]).
    TypeError or other exceptions: If element[1] or element[2] types are incompatible with arithmetic or the called methods, or if the called methods raise; exceptions from:
        - self.play_NoteContainer(note_container, channel, velocity)
        - self.sleep(duration_in_seconds)
        - self.stop_NoteContainer(note_container, channel)
    are not caught and will propagate.

## State Changes:
Attributes READ:
    self.MSG_PLAY_BAR - used when notifying listeners at method start.
    self.MSG_SLEEP - used when notifying listeners after each sleep.
    self.notify_listeners(...) - invoked to send MSG_PLAY_BAR and MSG_SLEEP notifications.
    self.play_NoteContainer(...) - invoked to start each NoteContainer (with velocity 100).
    self.stop_NoteContainer(...) - invoked to stop each NoteContainer.
    self.sleep(...) - invoked to pause execution for computed durations.

Attributes WRITTEN:
    None — the method does not directly assign to any self.<attr>. Any state changes occur within the called methods (play_NoteContainer, stop_NoteContainer, notify_listeners).

## Constraints:
Preconditions:
    - `bar` must be an iterable of indexable elements where element[1] is a non-zero numeric duration specifier and element[2] is a NoteContainer-like object.
    - `bpm` must be numeric and greater than 0 (to avoid division by zero).
    - `channel` should be a valid MIDI channel for the environment (commonly 1–16), although the method does not enforce this.

Postconditions:
    - For every element whose play_NoteContainer returned truthy, stop_NoteContainer was called before the method proceeds to the next element.
    - If the method completes normally, it returns {"bpm": bpm} reflecting any per-note-container bpm overrides encountered.
    - If the method aborts because play_NoteContainer returned a falsey value, it returns {} immediately; no further note playback or stopping is performed for subsequent elements.

## Side Effects:
    - Calls notify_listeners(self.MSG_PLAY_BAR, {"bar": bar, "channel": channel, "bpm": bpm}) once at the start.
    - For each element in `bar`, the method:
        - Calls self.play_NoteContainer(element[2], channel, 100). The fixed velocity argument is 100.
        - If the NoteContainer has attribute `bpm`, assigns that value to the local bpm variable and recomputes timing.
        - Computes timing:
            * qn_length = 60.0 / bpm  (seconds per quarter note)
            * duration_in_seconds = qn_length * (4.0 / element[1])  (note duration in seconds)
          Note: The implementation names this variable ms, but the computed value is in seconds; implementations should treat it as seconds when calling sleep or reporting to listeners.
        - Calls self.sleep(duration_in_seconds). This is a blocking pause for the computed number of seconds.
        - Calls notify_listeners(self.MSG_SLEEP, {"s": duration_in_seconds}) with the sleep duration in seconds.
        - Calls self.stop_NoteContainer(element[2], channel).
    - If play_NoteContainer returns a falsey value for any element, the method immediately returns {} without calling stop_NoteContainer for that element or processing later elements.
    - The method itself performs no file or network I/O, but called methods (play_NoteContainer, stop_NoteContainer, notify_listeners) may have I/O or interact with external MIDI devices.

### `mingus.midi.sequencer.Sequencer.play_Bars` · *method*

*No documentation generated.*

### `mingus.midi.sequencer.Sequencer.play_Track` · *method*

*No documentation generated.*

### `mingus.midi.sequencer.Sequencer.play_Tracks` · *method*

## Summary:
Coordinates simultaneous playback of multiple tracks by setting per-track instruments, then iterating bar-by-bar to delegate actual playback to play_Bars; updates the local bpm from play_Bars and returns the final bpm (or {} on abort).

## Description:
Known callers and context:
- play_Composition calls this method to play all tracks of a Composition (when channels are not provided play_Composition builds a default channels list and forwards to play_Tracks).
- Intended to be used during the playback stage of the Sequencer lifecycle: prepare instruments for each track and then drive synchronized bar-wise playback across multiple tracks.

Why this logic is a separate method:
- It encapsulates the multi-track coordination concerns (per-track instrument selection and synchronized bar iteration) that are distinct from single-track or per-bar playback logic. It delegates lower-level timing and note playback to play_Bars and instrument-setting side-effects to set_instrument, keeping responsibilities separated and reusable.

## Args:
    tracks (sequence): Sequence (list/tuple) of Track-like objects. Each track must be subscriptable by bar index (tr[i]) and have a .instrument attribute. Each Track is expected to be a sequence of bars; len(tracks[0]) defines the number of bars iterated.
    channels (sequence): Sequence of channel identifiers (commonly ints) with one entry per track. channels[x] is used when setting the instrument and when calling play_Bars for the x-th track.
    bpm (int | float, optional): Initial beats-per-minute value used for timing. Defaults to 120.

## Returns:
    dict: On successful completion returns {"bpm": final_bpm} where final_bpm is the bpm possibly updated by play_Bars during playback.
    dict (empty): Returns {} immediately to indicate playback aborted if any call to play_Bars returns {} during the process.

## Raises:
    IndexError: If tracks is empty (accesses tracks[0]), if channels has fewer entries than tracks (channels[x]), or if any track is shorter than tracks[0] (accessing tr[current_bar]) — these index operations will raise IndexError.
    AttributeError: If a track element does not expose the required attributes or sequence behavior (for example, missing .instrument or not subscriptable), or if instr attribute access expects fields not present.
    TypeError: If tracks or channels are not subscriptable/indexable sequences (e.g., None or incompatible types).
    Any exception raised by called methods (self.set_instrument or self.play_Bars) will propagate unchanged; this method does not catch exceptions from those calls.

## State Changes:
Attributes READ:
    self.MSG_PLAY_TRACKS (class constant) — read to notify listeners of the playback start
    (Indirect reads through method calls) self.listeners via notify_listeners inside called methods

Attributes WRITTEN:
    None directly. This method does not assign to any self.<attr>. It does, however, call other methods (set_instrument, play_Bars, notify_listeners) that may mutate sequencer state or emit events.

## Constraints:
Preconditions:
    - tracks must be a non-empty sequence.
    - channels must be a sequence with length >= len(tracks); each channels[x] must be a valid channel identifier for set_instrument/play_Bars.
    - Each track must be a sequence of bars and support indexing by bar index up to len(tracks[0]) - 1.
    - Each track element must have an .instrument attribute. If the instrument is an instance of MidiInstrument, it is expected (but not guaranteed) to have .names and .name attributes; missing name index is handled by a fallback to instrument index 1.

Postconditions:
    - For every track x, set_instrument(channels[x], i) will have been called once before playback begins, where i is either the index of instr.name in instr.names (for MidiInstrument) or 1 as a fallback.
    - If playback completes without an abort, returns {"bpm": final_bpm} with final_bpm equal to the last bpm value returned by play_Bars.
    - If any play_Bars invocation returns {}, playback is aborted and {} is returned immediately.

## Side Effects:
    - Notifies listeners at start via notify_listeners(self.MSG_PLAY_TRACKS, {"tracks": tracks, "channels": channels, "bpm": bpm}).
    - Calls set_instrument for each track, which itself triggers instr_event and notifies listeners (MSG_INSTR). These calls may send instrument-change MIDI messages to the output.
    - Delegates the actual per-bar/per-note playback to play_Bars; play_Bars will in turn call play_NoteContainer, sleep, notify_listeners for sleep and play events, and stop_NoteContainer — resulting in emitted MIDI events and timing/sleep behavior.
    - No file I/O is performed by this method itself, but called methods may interact with external MIDI outputs/listeners.

### `mingus.midi.sequencer.Sequencer.play_Composition` · *method*

## Summary:
Delegates playback of a Composition to the sequencer: notifies observers of the composition-play event, determines a default channel mapping when none is provided, and starts playback by calling the track-level player. This method does not mutate Sequencer instance attributes.

## Description:
This method is the Sequencer-facing entry point to play an entire Composition object. It performs three responsibilities in order:
1. Broadcasts a MSG_PLAY_COMPOSITION notification to all registered listeners with the composition, channels (may be None), and bpm.
2. If no channels list is supplied, constructs a default one-to-one mapping from composition tracks to MIDI channels (1-based indexes).
3. Delegates actual playback to play_Tracks using the composition's tracks, the resolved channels list, and the bpm.

Known callers:
- Typically called by application code or higher-level playback controllers that want to start playback of a Composition. There are no internal Sequencer methods that call play_Composition in this class (it is a top-level API for starting playback).

Why this is a separate method:
- It encapsulates the common orchestration for starting composition playback (listener notification, default channel mapping) and then delegates the complex playback details to play_Tracks. Keeping this logic separate keeps callers simple and centralizes composition-level pre-processing.

## Args:
    composition (object): Required. An object representing a musical composition that must expose a tracks attribute:
        - composition.tracks (sequence): A sequence (list/tuple) of Track objects. Each Track will be consumed by play_Tracks.
    channels (list[int] or None): Optional. A list of MIDI channel numbers (integers) to use for each track. If None (default), a default mapping [1, 2, ..., N] is created where N == len(composition.tracks). If provided, its length should match len(composition.tracks). Channels are expected to be valid MIDI channels (commonly 1–16) but this method does not validate ranges — validation may occur downstream.
    bpm (int or float): Optional. Beats-per-minute tempo for playback. Defaults to 120. Expected to be a positive numeric value; negative or zero values are not explicitly checked here.

## Returns:
    dict: The return value is whatever play_Tracks returns. In the Sequencer implementation this is typically:
        - a dict containing at least {"bpm": bpm_value} when playback proceeds successfully (where bpm_value may be updated during playback), or
        - an empty dict {} to indicate playback was aborted/ended early.
    Edge cases:
        - If play_Tracks raises or propagates an exception, this method will not return — the exception propagates to the caller.

## Raises:
    AttributeError: If the provided composition has no tracks attribute (or tracks is not subscriptable/has no length), an AttributeError (or TypeError) may be raised when accessing composition.tracks or len(composition.tracks).
    Any exception raised by notify_listeners or play_Tracks: notify_listeners delegates to listener.notify and does not catch exceptions; play_Tracks may also raise its own exceptions. Those exceptions propagate unchanged to the caller.

## State Changes:
Attributes READ:
    - self.listeners (indirectly read by notify_listeners when broadcasting MSG_PLAY_COMPOSITION)
    - self.MSG_PLAY_COMPOSITION (constant read to identify message type)
Attributes WRITTEN:
    - None. This method does not modify any Sequencer attributes.

## Constraints:
Preconditions:
    - composition must be a composition-like object with a sequence attribute tracks (len(composition.tracks) must be defined).
    - If channels is provided, it should be a sequence of integers with a length equal to len(composition.tracks). The method will pass channels through to play_Tracks without additional validation here.
    - bpm should be a numeric tempo value (positive expected though not enforced here).

Postconditions:
    - notify_listeners has been invoked once with MSG_PLAY_COMPOSITION and params {"composition": composition, "channels": channels_or_default, "bpm": bpm}.
    - play_Tracks has been invoked with composition.tracks, the resolved channels list, and the bpm; the return value from play_Tracks is returned unchanged to the caller.
    - No Sequencer attributes are modified by this method.

## Side Effects:
    - Calls notify_listeners, which will synchronously call notify(msg_type, params) on each registered listener. Those listener notifications may produce external side effects (sending MIDI messages, updating UI, logging, I/O). Exceptions raised by listeners will propagate.
    - Calls play_Tracks, which has substantial side effects: it may set instruments, send note on/off messages via play_Note/play_NoteContainer, cause sleeps/timing, and otherwise interact with external MIDI subsystems. Any I/O and timing behavior originates from play_Tracks and its callees.
    - If channels is derived (when None), a new list object is created locally and passed to play_Tracks.
    - No file, network, or persistent state is directly modified by this method itself; such effects come from notify_listeners/listeners and play_Tracks.

### `mingus.midi.sequencer.Sequencer.modulation` · *method*

## Summary:
Forward a modulation controller update (MIDI controller number 1) to the sequencer's control-change handler and return its boolean success result; this may trigger backend output and listener notifications.

## Description:
This convenience wrapper maps the musical concept "modulation" (the modulation wheel / controller 1) to the sequencer's central control_change method. It exists to provide a clear, self-documenting API and to avoid scattering the literal controller number 1 throughout the codebase.

Known callers:
    - No direct internal callers were found in the repository snapshot; this method is intended as a public API for external code (applications, GUIs, scripts) or playback controllers to change modulation during runtime.
Lifecycle/context:
    - Typically invoked during playback or in response to user interaction (e.g., user moves a modulation wheel in a UI), at which point the sequencer should validate and propagate the controller change.

Why a separate method:
    - Encapsulates the semantic mapping (modulation -> controller 1).
    - Keeps higher-level code readable and prevents hard-coded controller numbers scattered across the project.

Example usage:
    Call sequencer.modulation(1, 64) to set modulation to 64 on channel 1. The call returns True on success or False if validation fails.

## Args:
    channel (int-like): MIDI channel to apply the modulation on. Typical valid MIDI channels are 1..16 but this method does not enforce that range; callers should pass an appropriate channel number.
    value (int-like): Controller value for modulation. Must be numeric/comparable to integers; validation is performed by control_change (control and value must be in 0..128 inclusive).

## Returns:
    bool: The boolean result returned by control_change(channel, 1, value).
    - True: control_change accepted the parameters, invoked cc_event, and notified listeners.
    - False: validation in control_change failed (control or value out of allowed range); no backend call or notification occurred.

## Raises:
    - This wrapper does not raise exceptions directly.
    - Exceptions raised by control_change, self.cc_event(channel, 1, value), or any attached listener.notify(...) will propagate through this method (no internal try/except).

## State Changes:
    Attributes READ:
        - None directly by this wrapper.
        - The delegated control_change may read self.MSG_CC and iterate self.listeners when notifying.
    Attributes WRITTEN:
        - None directly by this wrapper.
        - control_change/cc_event or listeners may mutate sequencer state or external state.

## Constraints:
    Preconditions:
        - channel and value must be numeric (int-like). Prefer integers to avoid surprising casts in notifications.
        - value should be within 0..128 inclusive to succeed.
        - The sequencer instance should be initialized; if listeners or a backend are used, they should be attached/configured beforehand.

    Postconditions:
        - If True is returned: cc_event(channel, 1, value) has been called and notify_listeners has been invoked with integer-cast "channel", "control" (1), and "value".
        - If False is returned: control_change rejected the request and no backend or notification side effects occurred.

## Side Effects:
    - Delegates to self.control_change(channel, 1, value), which:
        * May call self.cc_event(channel, 1, value) — backend hook that can perform I/O (send MIDI) or mutate internal state.
        * Will call self.notify_listeners(self.MSG_CC, {"channel": int(channel), "control": 1, "value": int(value)}) on success; each listener.notify(...) may perform I/O, update UI, log, or raise exceptions.
    - This wrapper itself performs no additional I/O or listener interaction beyond what control_change does.

### `mingus.midi.sequencer.Sequencer.main_volume` · *method*

## Summary:
Sets the MIDI "main volume" Control Change for a given channel by delegating to the sequencer's control change handler; updates internal listeners and triggers the sequencer's cc_event.

## Description:
This is a convenience wrapper that sends MIDI Control Change number 7 (Main Volume) for the specified channel and value. It is typically called when user code or higher-level playback logic wants to adjust a channel's overall volume during playback or setup. Within the Sequencer lifecycle, invoke this when you need to change a channel's master volume; it is separated into its own method to provide a named, semantic alias for the MIDI CC number 7 rather than inlining the numeric control code at each call site.

Known callers:
- Not used internally by other Sequencer methods in this class (no direct internal callers). Intended for external callers or user code controlling channel volume.

Why a separate method:
- Provides a readable, self-documenting API (main volume is a common MIDI CC) and avoids scattering the literal control number (7) throughout the codebase.

## Args:
    channel (int): The MIDI channel number to target. The method does not validate a channel range; typical MIDI channels are 1..16. The value is cast to int by downstream notifications.
    value (int): The volume value to set for the control. Must be in the inclusive range 0..128 according to the sequencer's validation (values outside this range cause the call to fail and return False).

## Returns:
    bool: True if the control change was accepted and dispatched; False if the input was rejected (e.g., value outside the permitted 0..128 range). No exceptions are raised by this method.

## Raises:
    None: The method does not raise exceptions itself. Underlying listener notify implementations or subclass overrides of cc_event may raise exceptions, but such exceptions are not produced by this wrapper directly.

## State Changes:
Attributes READ:
    self.listeners (indirectly via notify_listeners) — the method causes the listeners list to be iterated when notifying.
    self.MSG_CC (class attribute used as the message type when notifying) and other class constants are read as part of notification construction.

Attributes WRITTEN:
    None in the base implementation. The method does not alter Sequencer attributes. However, cc_event (called internally) or listener notify handlers may mutate state outside this method.

## Constraints:
Preconditions:
    - The Sequencer instance must be initialized and any attached listeners must implement a notify(msg_type, params) method if present.
    - channel and value should be convertible to int (channel is passed through; notify_listeners converts numeric values to int).
    - value must be in the inclusive range 0..128 for the operation to be accepted.

Postconditions:
    - If the method returns True, the sequencer's cc_event(channel, 7, value) was invoked and all attached listeners were notified with MSG_CC and parameters {"channel": int(channel), "control": 7, "value": int(value)}.
    - If the method returns False, no cc_event or listener notification is performed (the call was rejected due to out-of-range control or value).

## Side Effects:
    - Calls self.control_change(channel, 7, value), which in turn:
        - Invokes self.cc_event(channel, 7, value) (may perform I/O or send MIDI messages in subclasses).
        - Calls self.notify_listeners with MSG_CC and a parameter dict; listener notify handlers can perform arbitrary side-effects (I/O, state mutation).
    - The base method itself performs no I/O, but the indirect calls above commonly result in MIDI output or external interactions depending on subclass and listener implementations.

### `mingus.midi.sequencer.Sequencer.pan` · *method*

## Summary:
Send a MIDI pan control-change (controller number 10) for the specified channel and value by delegating to the sequencer's control_change routine; returns whether the change was accepted and processed.

## Description:
This method is a tiny convenience wrapper that issues a MIDI Control Change (CC) for the standard Pan controller (MIDI controller number 10). It simply calls control_change(channel, 10, value) so all validation, event dispatch, and listener notification are performed by the generic control_change implementation.

Known callers and lifecycle context:
- Called by client code, UI components, automation routines, or playback logic that need to set or automate stereo panning for a MIDI channel during composition editing, playback, or live performance.
- It is used at the control-change stage of the sequencer pipeline (i.e., when channel-level parameters are modified), not for note-on/note-off events.
- It parallels other convenience wrappers in the same class (e.g., modulation and main_volume) that map a named parameter to a fixed controller number.

Why this is a separate method:
- Pan is a commonly used controller; having a named method makes intent explicit and avoids repeating the hard-coded controller number (10) across callers.

## Args:
    channel (int or numeric): MIDI channel identifier to receive the pan change. Typical values are 1–16; this method does not enforce channel-range bounds.
    value (int or numeric): Controller value for pan. Valid numeric range is 0 through 128 inclusive. Non-numeric types may raise a TypeError during validation.

Notes on types and casting:
- control_change performs numeric comparisons for validation, so floats (e.g., 64.5) are accepted by comparison; however, values are cast to int when preparing the listener notification payload (int(channel), int(control), int(value)), so listeners will receive integer values.

## Returns:
    bool: True if the control change was validated and processed (i.e., control_change accepted the parameters, invoked cc_event, and notified listeners). False if the underlying control_change rejected the request (e.g., value outside 0..128).

Because pan fixes the controller to 10 (which is within the allowed controller range), the only likely reason for a False return is an out-of-range value argument.

## Raises:
    TypeError (possible): If non-numeric types are provided and Python cannot evaluate the numeric comparisons in control_change, a TypeError (or another builtin exception) may be raised. The method itself does not explicitly raise any exceptions.

## State Changes:
    Attributes READ (direct):
        - None directly by pan; pan solely delegates to control_change.
    Attributes READ (indirect, via control_change):
        - self.listeners: iterated when notify_listeners is invoked so attached listener objects will be queried/called.
        - self.MSG_CC: used as the message type passed to listeners.
    Attributes WRITTEN:
        - None by pan itself. The underlying cc_event or listener notify calls may perform external side-effects or modify external objects.

## Constraints:
    Preconditions:
        - value should be a numeric type and within 0..128 inclusive for the call to succeed.
        - channel should be a numeric channel identifier; the method does not enforce valid MIDI channel range (1–16), so callers should ensure a correct channel is provided.

    Postconditions:
        - If True is returned: cc_event(channel, 10, value) has been invoked and notify_listeners has been called with MSG_CC and the payload {"channel": int(channel), "control": 10, "value": int(value)}.
        - If False is returned: the underlying control_change exited early due to validation failure and neither cc_event nor listener notifications occurred.

## Side Effects:
    - Invokes self.control_change(channel, 10, value), which:
        - Calls self.cc_event(channel, control, value). Concrete subclasses or implementations of cc_event are responsible for sending the actual MIDI message to an output device or driver (this is where I/O may occur).
        - Calls self.notify_listeners(self.MSG_CC, {"channel": int(channel), "control": int(control), "value": int(value)}), causing each attached listener object's notify(msg_type, params) method to be invoked. Those listener callbacks may perform I/O or mutate external state.
    - pan itself performs no file or network I/O; all such effects occur in cc_event or in listener callbacks.

