# `sequencer_observer.py`

## `mingus.midi.sequencer_observer.SequencerObserver` · *class*

## Summary:
SequencerObserver is an abstract observer interface that receives sequencer events and provides no-op handler methods for each event type; notify(msg_type, params) dispatches incoming events to the matching handler.

## Description:
SequencerObserver is intended to be subclassed by components that need to react to events emitted by a Sequencer. A Sequencer (or any producer that uses the same message constants) calls observer.notify(msg_type, params). The base class implements the routing logic; concrete observers override the specific handler methods they need.

Responsibility boundary:
- This class performs only event dispatch from message tuples (msg_type, params) to handler methods.
- It does not perform scheduling, timing, validation of parameter ranges, or resource management.
- Subclasses are responsible for handler behavior, thread-safety, and cleanup.

Scenarios to instantiate:
- Implementing an audio output that turns sequencer events into MIDI messages.
- Implementing a GUI updater that reflects current notes/controls.
- Logging or recording sequencer activity.
- Any other consumer of Sequencer event vocabulary.

## State:
This class defines no instance attributes in its implementation and is stateless by design.

Constructor:
- No explicit __init__ is defined; instantiate without arguments.

Class invariants:
- No invariants are enforced by the base class.
- Implementers should assume handlers can be invoked in any sequence and may be invoked repeatedly.

## Lifecycle:
Creation:
- Instantiate SequencerObserver directly (result is a no-op observer) or instantiate a subclass that overrides handler methods.

Usage:
1. Create an observer instance (usually a subclass overriding selected handlers).
2. Register the observer with a Sequencer using the Sequencer's observer registration API (Sequencer-specific method names are external to this class).
3. The Sequencer will call observer.notify(msg_type, params) for each event.
4. The base notify will synchronously call the corresponding handler method with arguments extracted from params.

Destruction:
- The base class defines no destruction or cleanup API.
- If a subclass allocates resources, it must provide and invoke its own cleanup and ensure it is unregistered from the Sequencer to avoid retained references.

Threading:
- notify is a synchronous dispatcher. The caller of notify (Sequencer) controls the thread context. Handlers should avoid long-running/blocking work and should offload heavy tasks to worker threads or queues as appropriate.

## Method Map:
graph TD
    notify(("notify(msg_type, params)"))
    notify -->|Sequencer.MSG_PLAY_INT| play_int_note_event[play_int_note_event(int_note, channel, velocity)]
    notify -->|Sequencer.MSG_STOP_INT| stop_int_note_event[stop_int_note_event(int_note, channel)]
    notify -->|Sequencer.MSG_CC| cc_event[cc_event(channel, control, value)]
    notify -->|Sequencer.MSG_INSTR| instr_event[instr_event(channel, instr, bank)]
    notify -->|Sequencer.MSG_SLEEP| sleep[sleep(seconds)]
    notify -->|Sequencer.MSG_PLAY_NOTE| play_Note[play_Note(note, channel, velocity)]
    notify -->|Sequencer.MSG_STOP_NOTE| stop_Note[stop_Note(note, channel)]
    notify -->|Sequencer.MSG_PLAY_NC| play_NoteContainer[play_NoteContainer(notes, channel)]
    notify -->|Sequencer.MSG_STOP_NC| stop_NoteContainer[stop_NoteContainer(notes, channel)]
    notify -->|Sequencer.MSG_PLAY_BAR| play_Bar[play_Bar(bar, channel, bpm)]
    notify -->|Sequencer.MSG_PLAY_BARS| play_Bars[play_Bars(bars, channels, bpm)]
    notify -->|Sequencer.MSG_PLAY_TRACK| play_Track[play_Track(track, channel, bpm)]
    notify -->|Sequencer.MSG_PLAY_TRACKS| play_Tracks[play_Tracks(tracks, channels, bpm)]
    notify -->|Sequencer.MSG_PLAY_COMPOSITION| play_Composition[play_Composition(composition, channels, bpm)]

## Methods and parameter contracts:
All handler methods are instance methods that perform no action in the base class and return None. Subclasses override handlers as needed.

- play_int_note_event(int_note, channel, velocity)
  - int_note: int. Integer representation of a note (producer-defined encoding).
  - channel: int. Channel identifier supplied by the Sequencer.
  - velocity: int. Velocity or similar intensity metric.

- stop_int_note_event(int_note, channel)
  - int_note: int.
  - channel: int.

- cc_event(channel, control, value)
  - channel: int.
  - control: int.
  - value: int.

- instr_event(channel, instr, bank)
  - channel: int.
  - instr: int.
  - bank: int.

- sleep(seconds)
  - seconds: float or int. Duration value supplied by the Sequencer for timing.

- play_Note(note, channel, velocity)
  - note: object. A Note-like object as used by the producer (type not enforced here).
  - channel: int.
  - velocity: int.

- stop_Note(note, channel)
  - note: object.
  - channel: int.

- play_NoteContainer(notes, channel)
  - notes: iterable. Iterable of Note-like objects or a NoteContainer-like object.
  - channel: int.

- stop_NoteContainer(notes, channel)
  - notes: iterable.
  - channel: int.

- play_Bar(bar, channel, bpm)
  - bar: object.
  - channel: int.
  - bpm: int or float.

- play_Bars(bars, channels, bpm)
  - bars: iterable of bar objects.
  - channels: iterable of channel identifiers or a single channel value.
  - bpm: int or float.

- play_Track(track, channel, bpm)
  - track: object.
  - channel: int.
  - bpm: int or float.

- play_Tracks(tracks, channels, bpm)
  - tracks: iterable of track objects.
  - channels: iterable of channel identifiers or a mapping.
  - bpm: int or float.

- play_Composition(composition, channels, bpm)
  - composition: object representing the composition/container.
  - channels: iterable of channel identifiers or a mapping.
  - bpm: int or float.

notify(msg_type, params)
- msg_type: event type identifier. Expected to match Sequencer message constants imported from mingus.midi.sequencer (for example, Sequencer.MSG_PLAY_INT, Sequencer.MSG_PLAY_NOTE, etc.).
- params: mapping (dict-like) containing string keys. notify uses direct key access (params["..."]) and will raise KeyError for missing keys.

Exact param keys required by msg_type:
- Sequencer.MSG_PLAY_INT: "note", "channel", "velocity"
- Sequencer.MSG_STOP_INT: "note", "channel"
- Sequencer.MSG_CC: "channel", "control", "value"
- Sequencer.MSG_INSTR: "channel", "instr", "bank"
- Sequencer.MSG_SLEEP: "s"
- Sequencer.MSG_PLAY_NOTE: "note", "channel", "velocity"
- Sequencer.MSG_STOP_NOTE: "note", "channel"
- Sequencer.MSG_PLAY_NC: "notes", "channel"
- Sequencer.MSG_STOP_NC: "notes", "channel"
- Sequencer.MSG_PLAY_BAR: "bar", "channel", "bpm"
- Sequencer.MSG_PLAY_BARS: "bars", "channels", "bpm"
- Sequencer.MSG_PLAY_TRACK: "track", "channel", "bpm"
- Sequencer.MSG_PLAY_TRACKS: "tracks", "channels", "bpm"
- Sequencer.MSG_PLAY_COMPOSITION: "composition", "channels", "bpm"

Return values:
- In the base class, all methods return None. The Sequencer does not use return values produced by handlers.

## Raises:
- notify will raise KeyError if params is missing any required string key for the given msg_type.
- notify will raise TypeError if params does not support keyed access with strings.
- Any exception raised inside an overridden handler propagates to the caller of notify unless the handler catches it.

## Edge cases and implementer notes:
- notify does not validate parameter types or ranges; handlers should perform validation if needed.
- Unknown msg_type: notify does nothing (no-op).
- params is not copied; mutations by handlers affect the original mapping.
- Handlers run synchronously in the caller's thread context. Avoid blocking operations inside handlers.

## Example (step-by-step, no code):
1. Create a subclass of SequencerObserver and override methods you need, for example override play_Note to send the Note object to an audio engine and cc_event to update UI controls.
2. Instantiate your subclass with no constructor arguments.
3. Register the instance with a Sequencer using the Sequencer's observer registration interface.
4. When the Sequencer emits an event, it will call notify(msg_type, params). For example, a "play note" event will reach notify with msg_type equal to Sequencer.MSG_PLAY_NOTE and params containing keys "note", "channel", and "velocity"; notify will then call the observer's play_Note(note, channel, velocity) method.
5. If your observer allocates resources, implement and call cleanup logic and unregister the observer from the Sequencer to prevent resource leaks.

## Purpose recap:
This class centralizes event-to-handler routing so observers implement only the handlers they require; it standardizes the message protocol between Sequencer producers and consumer observers.

### `mingus.midi.sequencer_observer.SequencerObserver.play_int_note_event` · *method*

## Summary:
A hook invoked when an integer-based "play note" event is emitted by the sequencer; the base implementation is a no-op and does not modify the observer's state.

## Description:
Known callers:
    - SequencerObserver.notify — when msg_type == Sequencer.MSG_PLAY_INT, notify calls this method with params["note"], params["channel"], params["velocity"] (see notify mapping in the class).

Context / lifecycle:
    - Called during sequencer playback when the Sequencer emits a "play integer note" event. This method represents the observer-side handler for that event and is invoked at the point in the playback pipeline where a note-on (play) should be acted upon.

Why this method exists:
    - This method is a dedicated hook so subclasses or concrete observer implementations can perform the platform-specific action required to play a note (for example: send a MIDI NOTE ON message to an output device, update UI state, log the event, or synthesize audio). Keeping it as a separate method makes the notify logic generic and allows different observers to implement different behaviors without changing the sequencer core.

## Args:
    int_note (int):
        - Description: The MIDI note number or integer note identifier supplied by the Sequencer.
        - Expected type: int
        - Typical/expected MIDI range: 0..127 (implementations may accept a wider range but should handle out-of-range values appropriately).
    channel (int):
        - Description: MIDI channel index to which the note pertains.
        - Expected type: int
        - Typical/expected MIDI range: 0..15
    velocity (int):
        - Description: Note velocity (attack velocity) supplied by the Sequencer.
        - Expected type: int
        - Typical/expected MIDI range: 0..127

Note: The base implementation does not perform validation; concrete overrides may validate and raise errors or clamp values.

## Returns:
    None
    - The base method does not return a value.

## Raises:
    - The base implementation raises nothing.
    - Subclasses may raise ValueError, TypeError, or I/O-related exceptions if they validate inputs or perform external operations; such exceptions are not raised by the base no-op implementation.

## State Changes:
    Attributes READ:
        - None in the base implementation (the method body is pass).
    Attributes WRITTEN:
        - None in the base implementation.
    - Implementations overriding this method may read or modify observer instance attributes (for example, tracking currently playing notes).

## Constraints:
    Preconditions:
        - The observer instance should be properly constructed/initialized before calling this method.
        - Callers (e.g., Sequencer.notify) supply three positional arguments matching the signature: int_note, channel, velocity.
        - Arguments are expected to be integers; callers originating from the Sequencer should follow that convention.
    Postconditions:
        - For the base class: no changes are made to self (no state change) and no value is returned.
        - For overrides: implementers should document and guarantee any state changes or side effects they introduce.

## Side Effects:
    - Base implementation: none (no I/O, no external calls).
    - Common side effects for overrides (examples of intended use):
        - Sending a MIDI NOTE ON message to an external MIDI output.
        - Starting synthesis of audio for the given note.
        - Updating UI/playback state or internal tracking of active notes.
        - Logging or emitting higher-level events.
    - Because the base method is a hook, side effects are entirely determined by overriding implementations.

### `mingus.midi.sequencer_observer.SequencerObserver.stop_int_note_event` · *method*

## Summary:
Handle a sequencer-issued "stop" event for an integer-represented note on a given channel; the base implementation performs no action — subclasses should override to stop sounding notes and update any bookkeeping.

## Description:
Known callers and context:
    - Called by SequencerObserver.notify when the sequencer dispatches a Sequencer.MSG_STOP_INT message. notify forwards params["note"] and params["channel"] to this method.
    - Invoked during sequencer playback when a scheduled stop event is processed (i.e., when the sequencer intends the note to cease).

Why this method exists separately:
    - Separating stop logic from the dispatch flow allows backends (MIDI output, synthesizer, test harnesses, UI) to override note-off behavior without modifying the sequencer dispatch code. It centralizes stop semantics (sending note-off messages, clearing active-note tables, logging, etc.) and improves testability and extensibility.

## Args:
    int_note (int):
        - The integer representing the pitch to stop (the method accepts an integer argument).
        - Typical MIDI semantics treat this as a 0..127 pitch value, but the base method does not enforce ranges — range validation is a subclass responsibility if required.
    channel (int):
        - The integer representing the channel on which the note should stop.
        - Typical MIDI channels are 0..15, but the base method does not enforce this; subclasses should validate if necessary.

## Returns:
    None
    - The base implementation returns nothing. Subclasses should follow this convention; no return value is expected.

## Raises:
    - Base implementation: does not raise exceptions.
    - Subclass implementers: may raise TypeError or ValueError if they choose to validate inputs; such exceptions are not part of the base contract.

## State Changes:
    Attributes READ:
        - None in the base class implementation.
        - Implementations commonly read attributes such as self.active_notes, self.output_port, or self.logger (but these are not required by the base class).
    Attributes WRITTEN:
        - None in the base class implementation.
        - Typical subclass behavior: remove the (channel, int_note) entry from an active-note registry, update counters, or mutate output-related attributes.

## Constraints:
    Preconditions:
        - The caller should supply integers for both arguments. The base method does not validate types or ranges.
        - The sequencer is expected to call this during playback; implementers should ensure their overrides are safe to call from the sequencer's execution context (threading considerations).
    Postconditions:
        - Base method: no changes guaranteed.
        - Recommended for overrides: after execution, the specified pitch on the specified channel should no longer be considered active by the observer's bookkeeping, and any output backend should have been instructed to stop the note.

## Side Effects:
    - Base implementation: none.
    - Common side effects in concrete implementations:
        * Emitting MIDI output to a port (NOTE OFF or NOTE ON velocity 0), calling a synthesizer API to release a voice, updating an active-note registry, logging, or updating UI state.

## Recommended implementation guidance (advice for subclass authors — not required by the base class):
    - Input handling: validate types and ranges if your backend requires them; otherwise accept integers and treat out-of-range values according to your policy (clamp, ignore, or raise).
    - Emitting note-off:
        * Option A (explicit): send a NOTE OFF message to the output backend for the given channel and pitch.
        * Option B (widely compatible): send a NOTE ON with velocity 0 (many MIDI devices treat this as note-off).
      These behaviors are backend conventions; choose the one appropriate for your output device.
    - Bookkeeping: if you keep an active-note registry (recommended for accurate handling of overlapping notes and idempotency), remove or mark the (channel, int_note) entry atomically.
    - Idempotence: make stop operations safe to call multiple times for the same note — repeated calls should not raise errors if the note is already stopped.
    - Thread-safety: if the sequencer invokes this from a playback thread, synchronize access to shared resources or marshal output operations into a dedicated I/O thread.
    - Logging and testing: consider emitting a log entry or appending a record to a test-visible list to support debugging and unit tests.

## Example behaviors for subclasses (non-code):
    - MIDI backend: send NOTE OFF (or NOTE ON vel=0) to the configured MIDI port for the specified channel and note; remove the note from self.active_notes[channel].
    - Synthesizer backend: find allocated voices producing the pitch on the channel and trigger their release; update voice-allocation tables.
    - Test stub: append (int_note, channel, timestamp) to self._received_stop_events for later assertions.

### `mingus.midi.sequencer_observer.SequencerObserver.cc_event` · *method*

## Summary:
Handle a MIDI Control Change (CC) message delivered to this observer; the base implementation performs no action, but subclasses should override it to update observer state or produce side effects when a controller value changes.

## Description:
This method is invoked by Sequencer.notify when the sequencer dispatches a control-change event (Sequencer.MSG_CC). notify calls this method with the mapping keys "channel", "control", and "value".

Known caller:
    - mingus.midi.sequencer.Sequencer.notify — called during sequencer playback or event processing whenever a CC message is encountered.

Lifecycle/context:
    - Executed during playback/event processing of a MIDI sequence. Each invocation corresponds to a single MIDI Control Change message tied to a channel and controller index/value pair.
    - It is implemented as a separate hook so observers can implement isolated handling for CC messages without modifying the central dispatch logic in notify.

Why this is a separate method:
    - Keeps message routing (notify) distinct from specific handling of message types (cc_event), making subclassing, testing, and maintenance simpler.
    - Allows observers to selectively implement only the handlers they need (note events, CCs, program changes, etc.).

## Args:
    channel (int): MIDI channel index for the message as delivered by the Sequencer. Typical MIDI convention: 0–15 (some systems use 1–16). The base implementation does not validate the range.
    control (int): Controller number/index. Typical MIDI convention: 0–127. The base implementation does not validate the range.
    value (int): Controller value. Typical MIDI convention: 0–127. The base implementation does not validate the range.

## Returns:
    None — the base method returns nothing. Any return value provided by an override will be ignored by Sequencer.notify.

## Raises:
    - The base implementation does not raise exceptions.
    - Important: exceptions raised by subclass overrides will propagate back to the caller (Sequencer.notify) because notify performs direct calls without internal exception handling. Implementations should either avoid raising or handle exceptions locally if they must not interrupt sequencer processing.

## State Changes:
    Attributes READ:
        - None in the base implementation.
        - Subclass implementations may read any observer attributes (e.g., self.state, self.last_cc) as needed.

    Attributes WRITTEN:
        - None in the base implementation.
        - Subclass implementations commonly update observer attributes (for example, caching the last controller value or toggling flags). Those mutations are responsibility of the subclass.

## Constraints:
    Preconditions:
        - The caller supplies integer values for channel, control, and value via the params mapping. The method assumes those keys are present (Sequencer.notify enforces this contract).
        - If subclass logic depends on MIDI-standard ranges, callers should provide values within those ranges (channel 0–15, control 0–127, value 0–127); the base class does not enforce them.

    Postconditions:
        - After calling the base implementation, there is no change to the observer's state.
        - After calling a subclass override, any side effects or state changes are solely determined by that override; there is no additional framework-level guarantee.

## Edge cases and recommended override patterns:
    - Validate inputs if your implementation assumes strict ranges. For example, explicitly clamp or reject control/value outside 0–127 if your logic cannot handle them.
    - Avoid long-running synchronous work in the handler; if processing is expensive, delegate to a worker thread or queue to prevent blocking sequencer processing.
    - Catch and handle exceptions inside the override unless you intentionally want playback to stop on error.
    - If your observer will emit MIDI or other events in response, consider debouncing or rate-limiting if the sequencer produces many CC messages in quick succession.

## Side Effects:
    - Base implementation: none.
    - Subclass implementations may perform side effects such as mutating observer state, sending MIDI or network messages, logging, or updating user interfaces. Any such side effects are the responsibility of the override and should follow the guidelines above to avoid disrupting the sequencer.

### `mingus.midi.sequencer_observer.SequencerObserver.instr_event` · *method*

## Summary:
Called when an instrument (program) change message is dispatched for a channel; intended as an override hook so an observer can react to or record the channel's instrument and bank change. By default this base implementation does nothing.

## Description:
Known callers and context:
- SequencerObserver.notify: when notify receives a Sequencer.MSG_INSTR message it calls this method with params["channel"], params["instr"], params["bank"].
- The Sequencer (or any message dispatcher that uses Sequencer.MSG_INSTR) will be the usual origin of the notify call that leads here.

Lifecycle / pipeline stage:
- Invoked during message dispatch when the sequencer processes/forwards an instrument-change (program-change / bank select) event for a track/channel. Typically occurs while a sequence is being played or when the sequencer's state is being synchronized.

Why this is a separate method:
- This method is a small, clearly named hook intended to be overridden by subclasses that implement concrete behaviour (e.g., sending a MIDI Program Change to a synth, updating UI state, or recording the assignment). Keeping it separate allows notify to remain a simple dispatcher and keeps instrument-change handling pluggable.

## Args:
    channel: value passed by the Sequencer in params["channel"] (typically an integer channel identifier supplied by the sequencer implementation)
    instr: value passed by the Sequencer in params["instr"] (the instrument/program identifier supplied by the sequencer implementation)
    bank: value passed by the Sequencer in params["bank"] (the bank identifier supplied by the sequencer implementation)

Notes on types:
- The base implementation does not enforce types; the actual runtime types and ranges come from the Sequencer's message creation. Implementations overriding this method should document and validate expected types/ranges if necessary.

## Returns:
    None: the base implementation returns None (no explicit return). Subclasses may return values if they provide a reason, but notify() does not use any return value from this method.

## Raises:
    The base implementation does not raise. Subclasses may raise exceptions for invalid arguments or I/O failures; callers (e.g., Sequencer.notify) should handle or propagate such exceptions as appropriate.

## State Changes:
Attributes READ:
    - None in the base implementation (this method body is a no-op).
Attributes WRITTEN:
    - None in the base implementation.
Implementers overriding this method may read or mutate observer instance attributes (for example, to store per-channel instrument state), and should document those mutations in their overrides.

## Constraints:
Preconditions:
    - The caller (notify) is expected to supply three positional arguments in the order (channel, instr, bank).
    - The method assumes it is invoked as part of the Sequencer/observer message-dispatch pipeline; callers should ensure the arguments come from a Sequencer.MSG_INSTR message as shown in SequencerObserver.notify.

Postconditions:
    - Base implementation: no state changes and returns None.
    - Overridden implementations should guarantee any documented postconditions (for example, updating an internal mapping of channel->instrument) and remain robust to unexpected types if they may be fed unvalidated messages.

## Side Effects:
    - Base implementation: none.
    - Typical implementations will perform side effects such as:
        - Sending a MIDI Program Change / Bank Select to an external synthesizer or MIDI output
        - Updating UI or internal state that maps channels to instruments
        - Logging or recording the change
    - Any I/O or external interactions must be performed by subclasses; the base method does not perform I/O itself.

### `mingus.midi.sequencer_observer.SequencerObserver.sleep` · *method*

## Summary:
A no-op placeholder that represents a pause in sequencer time; the base implementation performs no action and returns immediately.

## Description:
Known callers:
    - SequencerObserver.notify: called when the sequencer emits a sleep event (Sequencer.MSG_SLEEP) with params["s"].

Lifecycle/context:
    - Invoked during sequencer playback between MIDI events to indicate a pause or time advancement.
    - The method exists as an override point: concrete subclasses implement how the observer should handle the passage of time (for example, blocking for real-time playback, advancing an internal timestamp for simulated playback, or scheduling a non-blocking callback in an event loop).
    - The base class intentionally does nothing so that observers that do not need to handle timing can ignore sleep events without side effects.

Why this is a separate method:
    - Centralizes timing behavior in a single overridable hook rather than inlining timing logic in notify. This makes it easy to adapt timing behavior for different environments (tests, real-time playback, GUIs, async systems) by overriding this method.

## Args:
    seconds (any): The value supplied by the sequencer for the required pause duration.
        - The base implementation does not inspect, validate, or convert this parameter.
        - Subclasses that override this method should document the expected type/range (commonly float or int, >= 0.0).

## Returns:
    None
    - The base implementation returns immediately and does not convey timing information.

## Raises:
    None in the base implementation.
    - Any validation errors or exceptions are the responsibility of overriding implementations.

## State Changes:
    Attributes READ:
        - None (the base implementation does not read any self attributes).
    Attributes WRITTEN:
        - None (the base implementation does not modify any self attributes).

## Constraints:
    Preconditions:
        - None enforced by the base method. Callers may pass any value as seconds; subclasses may require numeric, finite, non-negative values and should validate accordingly.
    Postconditions:
        - After the base method returns, no state related to timing has changed by the base implementation.

## Side Effects:
    - Base implementation: none.
    - Subclasses may introduce side effects (blocking the current thread, updating playback time fields, scheduling callbacks). Such behavior must be documented by the subclass.

### `mingus.midi.sequencer_observer.SequencerObserver.play_Note` · *method*

## Summary:
Handle a single-note "play" event dispatched by the sequencer. The base implementation performs no action (no-op); subclasses should override this method to produce output (for example sending a MIDI NOTE ON, triggering a synth, or logging) and may alter observer state.

## Description:
Known callers and context:
- SequencerObserver.notify calls this method when it receives a Sequencer.MSG_PLAY_NOTE message. The notify method invokes this method during sequencer playback whenever a scheduled note-on event is emitted.
- This method is intended to be a callback/hook in the observer pattern: the Sequencer (or any dispatcher that translates scheduled events into messages) triggers notify, which dispatches to this method.

Why this method exists separately:
- Separation allows concrete observer implementations to override a single focused hook for note-on events without duplicating message-dispatching logic.
- Keeping the behavior in a dedicated method improves testability and makes it easier to implement different output strategies (MIDI, synthesis, logging, UI feedback) in subclasses or concrete observers.

## Args:
    note: object
        The note payload passed through from the Sequencer. The base class does not impose any type checks or conversions; concrete observers decide how to interpret the payload (it might be an integer MIDI note number, a Note-like object, etc., depending on the Sequencer implementation).
    channel: int
        Channel identifier supplied by the Sequencer. The base implementation does not validate the value or range.
    velocity: int
        Velocity (intensity) supplied by the Sequencer. The base implementation does not validate the value or range.

## Returns:
    None
    The base implementation returns None and performs no action. Subclasses may return values if they choose, but notify and the Sequencer do not use any return value.

## Raises:
    None
    The base implementation does not raise exceptions. Subclasses may raise exceptions if their override performs I/O or validation; such exceptions will propagate to the caller (the dispatcher/Sequencer) unless handled.

## State Changes:
    Attributes READ:
        None (the base method does not read any attributes on self)
    Attributes WRITTEN:
        None (the base method does not modify any attributes on self)

## Constraints:
    Preconditions:
        - This method is expected to be called by the Sequencer.notify dispatcher with three positional arguments: note, channel, velocity.
        - The base class makes no assumptions about the types or ranges of these arguments; callers should supply appropriate values as required by concrete observers.
    Postconditions:
        - After calling the base implementation, the SequencerObserver instance remains unchanged (no attributes are modified).
        - Subclass overrides may perform side effects (MIDI output, state updates) and should document their own postconditions.

## Side Effects:
    - Base implementation: none (no I/O, no external service calls, no mutations outside self).
    - Overrides: likely to perform side effects (e.g., sending MIDI NOTE ON via an output device, starting a synth voice, logging). Such side effects are implementation-specific and not performed by the base method.

### `mingus.midi.sequencer_observer.SequencerObserver.stop_Note` · *method*

## Summary:
Stops the previously started note on the specified channel in response to a sequencer stop event. The base implementation is a no-op; subclasses override this hook to produce the concrete "stop" effect (e.g., send MIDI Note Off, update active-note bookkeeping, or update UI).

## Description:
This is an Observer-pattern callback invoked during sequencer playback when a note's duration ends. The Sequencer calls SequencerObserver.notify, which maps Sequencer.MSG_STOP_NOTE to this method and passes the event parameters from the message payload (params["note"] and params["channel"]). Typical invocation occurs inside the sequencer's real-time playback loop when it processes scheduled stop events.

This logic is a separate method to provide a stable, single-responsibility hook for subclasses to implement stop behavior without embedding event-dispatch logic inside notify. Subclasses override stop_Note to:
- Translate the note representation to the output device format (if necessary).
- Emit the appropriate stop command to the audio/MIDI layer.
- Update any internal bookkeeping that tracks active notes.

Known caller:
- SequencerObserver.notify (triggered when msg_type == Sequencer.MSG_STOP_NOTE and params contains "note" and "channel")

Why separate:
- Keeps notify as a simple dispatcher.
- Allows different observers to implement differing stop behaviors (MIDI output, software synthesizer, logging, UI) without changing Sequencer logic.

## Args:
    note: object
        The same note object that the Sequencer used when originally calling play_Note for this voice. The concrete type is sequencer-dependent (commonly an integer pitch or a Note/Note-like object). Implementations should accept the type delivered by the Sequencer and must not assume a concrete class unless the project explicitly defines it elsewhere.
    channel: object
        The channel identifier associated with the note. Typically an integer MIDI channel index (0..15) but may be any identifier used by the Sequencer and consuming observers.

## Returns:
    None
    The base implementation returns nothing and the caller (notify) ignores any return value. Subclasses may return diagnostic values if desired, but Sequencer/notify do not consume them.

## Raises:
    None in the base implementation.
    Subclasses may raise exceptions for I/O or internal errors, but because notify does not perform special exception handling, implementations should either:
    - Catch and handle expected exceptions inside stop_Note, or
    - Allow exceptions to propagate only if upstream code is prepared to handle them.

## State Changes:
Attributes READ:
    None in the base class implementation.
    (Subclasses commonly read attributes such as self.midi_out, self.active_notes, or threading primitives.)

Attributes WRITTEN:
    None in the base class implementation.
    (Subclasses commonly remove entries from active-note registries or update status fields. If you modify shared state, ensure correct synchronization.)

## Constraints:
Preconditions:
    - Called with exactly two positional arguments (note and channel).
    - The note and channel values are those supplied by Sequencer in MSG_STOP_NOTE payloads (params["note"], params["channel"]).

Postconditions:
    - Base class: object state and external systems are unchanged.
    - For overrides: the effective behavior expected by callers is that the note is no longer sounding or considered active by the observer. If the observer maintains an active-note registry, the entry for (note, channel) should be removed or marked inactive by the end of the method.

Idempotence:
    - Implementations should be safe to call multiple times for the same (note, channel) pair (i.e., stopping an already-stopped note should not raise an error).

Timing constraints:
    - This method is expected to be called in time-sensitive playback code. Keep implementations short and non-blocking; offload heavy or blocking I/O to worker threads or async queues.

Input validation:
    - Implementations should handle None or malformed arguments gracefully (e.g., ignore, log a warning, and return) rather than raising unhandled exceptions during playback.

## Side Effects:
    - Base class: none.
    - Typical override side effects:
        - Send a MIDI Note Off or Note On with velocity 0 to a MIDI output device.
        - Remove or mark a note as inactive in internal bookkeeping (e.g., self.active_notes).
        - Emit UI updates or logging entries.
    - Avoid performing blocking network or disk operations synchronously here to preserve playback timing.

## Implementation guidance and example actions for subclasses (non-code bullets):
    - If you map notes to MIDI pitches, convert the provided note to the pitch format your MIDI output expects, then issue a Note Off on the provided channel.
    - If you track active voices in a dict keyed by (note, channel), remove or mark the corresponding key to free the voice:
        * Safely handle the case where the key is absent (pop with default or check membership first).
    - If your stop operation may fail (I/O), catch exceptions and log a recoverable error instead of allowing the sequencer's real-time loop to fail.
    - If your observer is used concurrently by multiple threads, guard any shared mutable state with appropriate locks.
    - Keep the method fast and deterministic; defer non-critical work (detailed logging, metrics) to background tasks.

## Minimal recommended contract:
    - Signature: stop_Note(self, note, channel)
    - Behavior: ensure the note specified by (note, channel) is stopped from producing sound and removed from any active-note bookkeeping; return None; be safe to call multiple times for the same note.

### `mingus.midi.sequencer_observer.SequencerObserver.play_NoteContainer` · *method*

## Summary:
Handles a request from the sequencer to start a collection of notes (a NoteContainer or any iterable of note descriptors) on a specified MIDI channel. The base implementation is intentionally a no-op; concrete observers should override it to perform actual playback or emit MIDI events. This method does not modify any SequencerObserver state in the base class.

## Description:
This method is invoked by Sequencer.notify when the sequencer emits a play-note-container event (notify maps Sequencer.MSG_PLAY_NC to this method and passes params["notes"] and params["channel"]). It is executed during the sequencer's playback lifecycle at the moment a NoteContainer should begin sounding.

Why this is a separate method:
- It is an observer hook intended for overriding by concrete observer implementations (e.g., sending MIDI NOTE ON messages, forwarding events to a synth, or logging).
- Having a container-level hook allows observers to implement efficient or backend-specific behavior (for example, emitting a single optimized chord message versus many individual note-on messages) without changing the sequencer core.

## Args:
    notes (object): The value supplied by the Sequencer.notify params["notes"]. The base implementation does not inspect or enforce a particular type; it expects subclasses to handle the concrete format (e.g., a NoteContainer object, an iterable of note values, or another domain-specific structure).
    channel (int): The value supplied by the Sequencer.notify params["channel"]. The base implementation does not validate it; subclasses should validate according to their MIDI/backend expectations.

## Returns:
    None: The base implementation returns nothing. Sequencer.notify does not use any return value from this method.

## Raises:
    Base implementation: does not raise.
    Subclass implementations: may raise TypeError, ValueError, I/O errors, or backend-specific exceptions if inputs are invalid or if emitting events fails. Those exceptions are not raised by the base method and should be documented by the subclass that introduces them.

## State Changes:
    Attributes READ:
        - None in the base implementation. (Concrete subclasses may read observer-specific attributes such as an output port handle.)
    Attributes WRITTEN:
        - None in the base implementation. (Concrete subclasses may update bookkeeping such as a set of active notes.)

## Constraints:
    Preconditions:
        - Sequencer.notify supplies two positional parameters when calling this method: notes and channel. The base class imposes no further preconditions.
    Postconditions:
        - Base method: no state or side-effect guarantees.
        - Subclass implementations SHOULD document their own postconditions (for example, that corresponding note-on events have been emitted or that active-note bookkeeping has been updated).

## Side Effects:
    Base method: none.
    Typical subclass side effects (advisory):
        - Sending MIDI NOTE ON messages to an output port
        - Calling other instance methods like play_Note or play_int_note_event to handle individual notes
        - Logging or emitting events to other subsystems
        - Mutating external resources (MIDI ports, synth engines)

## Recommendations for implementers:
    - Treat 'notes' as opaque unless you control the caller; if you expect a particular structure, validate it early and raise a clear exception.
    - If your observer exposes play_Note or play_int_note_event helpers, consider iterating notes and delegating to them for consistent behavior.
    - Ensure symmetry with stop_NoteContainer: implementations that start notes here should provide corresponding stop behavior so notes are not left sounding indefinitely.
    - If your backend requires channel validation (e.g., MIDI 0..15), perform that validation in the subclass and document the behavior on invalid values.

## Known callers and context:
    - Sequencer.notify: calls this method when msg_type == Sequencer.MSG_PLAY_NC, passing params["notes"] and params["channel"]. This occurs during the sequencer playback loop when a NoteContainer playback event is reached.

### `mingus.midi.sequencer_observer.SequencerObserver.stop_NoteContainer` · *method*

## Summary:
Default no-op handler for stopping every note contained in a NoteContainer on a given MIDI channel. It exists so subclasses can implement channel-aware, container-wide note stop behavior without changing the sequencer.

## Description:
Known callers:
- SequencerObserver.notify when it receives Sequencer.MSG_STOP_NC (the sequencer signals that a NoteContainer should be stopped). This is the primary lifecycle context: the sequencer dispatches a stop request for a group of notes and calls this observer method so any attached observer can react.

Rationale:
- This method is provided as a separate overridable hook (instead of inlining container-handling into notify) so observers can implement optimized, device- or backend-specific behavior for stopping multiple notes at once (for example, sending a single MIDI "all notes off" message, batching per-channel stop messages, or calling other internal stop helpers). The default implementation is intentionally empty (no-op) so observers that do not need container-level handling need not override it.

## Args:
    notes (iterable): A NoteContainer-like object or any iterable representing multiple notes to stop. Each element is an individual "note" in whatever representation the observer expects (common representations include integer MIDI note numbers or Note objects). Implementations must document which element types they accept.
    channel (int): MIDI channel to stop the notes on. Typically an integer in the MIDI channel range (commonly 0–15), but the exact allowed range is determined by the observer/Sequencer integration.

## Returns:
    None. This method does not return a value. Observers should perform side-effects to stop notes.

## Raises:
    The default implementation does not raise. Concrete overrides may raise:
    - TypeError: if `notes` is not iterable or contains unsupported element types.
    - ValueError: if `channel` is out of the allowed range for the observer/backend.
    Implementations MUST document any raised exceptions and conditions that trigger them.

## State Changes:
Attributes READ :
    None in the default implementation.
Attributes WRITTEN :
    None in the default implementation.

Note: Implementations commonly call other observer methods (for example, self.stop_Note or self.stop_int_note_event) which may read or modify observer state; those side-effects should be documented on the concrete override.

## Constraints:
Preconditions:
    - The caller (usually the Sequencer via notify) must supply a non-None iterable for `notes`. An empty iterable is allowed and should be treated as a no-op.
    - `channel` must be the integer used by the Sequencer for routing messages to the desired MIDI channel; concrete observers should validate the channel if necessary.

Postconditions:
    - After a successful override, all notes represented in `notes` will have been requested to stop on the supplied `channel` (semantics depend on the observer implementation — e.g., each note may trigger an individual stop message or be handled in bulk).
    - The default implementation (as shipped) leaves the observer state unchanged.

## Side Effects:
    - No I/O or external calls occur in the default no-op implementation.
    - Typical overrides will have side effects: sending MIDI messages, invoking other observer methods (self.stop_Note or self.stop_int_note_event), mutating playback-related state, or interacting with an external MIDI backend. Any such side effects must be documented by the override.

Implementation guidance (recommended pattern for overrides):
    1. Validate inputs: ensure `notes` is iterable and `channel` is within your backend's valid range.
    2. If your observer exposes per-note stop helpers, iterate `notes` and delegate each element appropriately (for example, call self.stop_int_note_event(n, channel) for integer MIDI numbers, or self.stop_Note(n, channel) for Note objects).
    3. Consider optimizing for bulk stop if the backend supports it (e.g., an "all notes off" per-channel command) when `notes` contains multiple notes on the same channel.
    4. Keep the method idempotent: calling stop_NoteContainer with the same notes and channel multiple times should not cause undefined state in your observer.

### `mingus.midi.sequencer_observer.SequencerObserver.play_Bar` · *method*

## Summary:
Handles a request to play a single bar provided by the sequencer. In this base class the method is intentionally a no-op; subclasses override it to produce playback effects or update observer state.

## Description:
This is an observer callback invoked when an external driver forwards a play-bar message to the observer. Known caller:
- SequencerObserver.notify: when notify receives a message of type Sequencer.MSG_PLAY_BAR it invokes this method with parameters extracted from the message.

Lifecycle/context:
- Called during playback when the system wants an observer to process or render one bar of music.
- The method is separated from sequencer logic so different observer implementations (MIDI output, GUI visualizer, test doubles, etc.) can override it to implement backend-specific behavior without changing the sequencer.

Why this method exists separately:
- It defines a clear extension point for observers to handle bar-level playback events. The base class provides a stable interface (signature and intent) while leaving behavior to subclasses.

## Args:
    bar (object):
        The bar-like object supplied by the sequencer representing the musical content to be played.
        The concrete type and structure are determined by other parts of the library and by the Sequencer; this method does not enforce a specific type.
    channel (int):
        The output channel index associated with the bar (typical MIDI-style channel index). The method does not validate the numeric range.
    bpm (int | float):
        Tempo in beats-per-minute to be used when interpreting timing within the bar. Expected to be numeric; the base method does not validate or coerce the value.

## Returns:
    None: The base implementation returns None and performs no actions. Observer overrides typically also return None and use side effects to perform playback.

## Raises:
    The base implementation does not raise exceptions.
    Concrete overrides may raise implementation-specific exceptions (for example, I/O or device errors); such exceptions are not defined by this interface and must be documented by the overriding subclass.

## State Changes:
Attributes READ :
    - None in the base implementation.
Attributes WRITTEN :
    - None in the base implementation.
Note: Subclasses may read or write observer-specific state (device handles, note-tracking tables, timing cursors); those changes must be documented on the subclass.

## Constraints:
Preconditions (recommended, not enforced by this method):
    - The caller should supply a bar object appropriate for the rest of the library.
    - channel should be meaningful to the observer (for example a MIDI-style channel index).
    - bpm should be a positive numeric tempo value.
Postconditions:
    - Base implementation: no observable changes (no-op).
    - Subclass implementations: should document their own guarantees (e.g., emitted MIDI events scheduled, notes started/stopped, or visual updates performed).

## Side Effects:
    - Base implementation: none.
    - Typical overrides: may emit MIDI/events, mutate external device state, schedule timed callbacks or sleeps, or update observer-internal state. Any I/O or external resource use is implementation-specific and must be handled by the subclass.

### `mingus.midi.sequencer_observer.SequencerObserver.play_Bars` · *method*

## Summary:
Handle playback of multiple bars by invoking per-bar playback for the specified channels and tempo; intended to update external MIDI state or schedule events and to be overridden by concrete observers.

## Description:
This method is called by the Sequencer (via Sequencer.notify when handling MSG_PLAY_BARS) to instruct the observer to play a sequence of bar objects at the given tempo on one or more MIDI channels. Known caller: Sequencer.notify in response to Sequencer.MSG_PLAY_BARS; the call occurs during the sequencer's playback scheduling stage when it emits grouped bar playback messages.

This logic is factored out into its own method so subclasses can implement batch bar playback semantics (broadcasting a bar to many channels, mapping per-bar channels, scheduling, or direct immediate output) without duplicating the iteration and dispatch policy in the Sequencer. The base-class implementation should perform the canonical dispatch (iterate bars and call play_Bar for each target channel), while subclasses may override it to perform bulk MIDI writes, optimized scheduling, channel remapping, or other side effects.

## Args:
    bars (iterable): Iterable of Bar-like objects (objects representing a musical bar/measure). Each element will be passed to play_Bar. Implementations may accept any object understood by play_Bar.
    channels (int or iterable[int]): Either a single MIDI channel number (0-15 typical) to which every bar will be sent, or an iterable of channel numbers. If an iterable is provided and its length equals len(bars), each bar is sent to the corresponding channel. If an iterable is provided and its length is 1 or len != len(bars), see the "Behavior" rules below for how it should be interpreted.
    bpm (int | float): Beats per minute tempo for playback. Must be a positive number; fractional BPM is allowed.

## Returns:
    None
    The method does not return a value. Implementations perform I/O or state mutations (MIDI output, scheduling) instead.

## Raises:
    TypeError: If `bars` is not iterable.
    TypeError: If `channels` is neither an int nor an iterable of ints.
    ValueError: If `bpm` is not a positive number.
    ValueError: If `channels` is an iterable and contains values that are not valid integer channel numbers for the environment (e.g., negative numbers or out of allowed MIDI range) — concrete observers should document their channel constraints.

Note: The base-class (no-op) implementation itself does not raise; these are the recommended validation/contract checks an implementation should perform.

## State Changes:
    Attributes READ:
        None (base implementation does not require or read any SequencerObserver instance attributes)
    Attributes WRITTEN:
        None (base implementation does not modify any SequencerObserver instance attributes)

Concrete overrides may read or write observer-specific attributes (for example, an output device handle or scheduling queue); those must be documented on the subclass.

## Constraints:
    Preconditions:
        - `bars` must be an iterable of bar objects understood by play_Bar (or the subclass).
        - `channels` must be either a single integer channel or an iterable of integer channels.
        - `bpm` must be a positive number (> 0).
    Postconditions:
        - For every bar in `bars`, at least one play_Bar invocation ought to have been issued (directly or indirectly) for the intended channel(s) at the given `bpm`.
        - No return value is produced; side effects (MIDI output or scheduling) are the observable result.
        - If input validation fails, the method should raise the documented exception and perform no partial side effects.

## Behavior / Implementation guidance:
    Canonical (recommended) implementation:
        1. Validate inputs (raise documented errors on invalid types/values).
        2. Normalize channels:
            - If channels is a single int, treat it as broadcasting that channel to every bar.
            - If channels is an iterable:
                a. If len(channels) == len(bars): pairwise mapping — send bar[i] to channels[i].
                b. Otherwise, treat the channels iterable as a set of channels to which each bar should be broadcast (i.e., for each bar, iterate every channel in channels and call play_Bar(bar, channel, bpm)).
        3. For each determined (bar, channel) pair, call self.play_Bar(bar, channel, bpm).
        4. Do not swallow exceptions raised by play_Bar unless deliberately converting them; prefer failing early so upstream code can react.

    Concurrency / scheduling:
        - If your observer performs asynchronous scheduling (e.g., queues events for a background MIDI thread), ensure that play_Bars either enqueues all required tasks before returning, or documents that it may return before playback completes.
        - If per-event timing is important, use bpm to compute timing and schedule sleeps or timer events via the observer's scheduling mechanism (do not assume Sequencer will sleep for you unless notified otherwise).

    Edge cases:
        - Empty `bars`: do nothing and return None.
        - channels iterable length mismatch:
            * If channels length equals bars length, map one-to-one.
            * If channels length differs and is >1, broadcast channels to every bar (explicit mapping is preferred by callers if a per-bar channel is required).
        - bars containing None: implementations may either skip None entries or raise TypeError; be explicit in subclass docs.

## Side Effects:
    - Intended to cause MIDI output or scheduling of MIDI events (writes to MIDI devices, enqueuing events into a playback thread, logging, etc.), which are external to the SequencerObserver instance.
    - May perform I/O (device writes) and therefore may raise I/O-related exceptions (IOError, OSError) depending on the output backend used by the concrete observer.

## Why this method exists:
    - Provides a single point where grouped bar playback semantics (broadcasting, per-bar channel mapping, batch scheduling) are implemented. It keeps Sequencer responsible for timing and message generation while allowing observers to decide how to execute or optimize the actual sound/output operations.

### `mingus.midi.sequencer_observer.SequencerObserver.play_Track` · *method*

## Summary:
A no-op observer hook invoked to handle playback of a Track; intended to be overridden by subclasses to implement track-level playback behavior and may change the observer's state when implemented.

## Description:
Known callers:
    - SequencerObserver.notify: this method is invoked by notify when it receives a Sequencer.MSG_PLAY_TRACK message (notify passes params["track"], params["channel"], params["bpm"]).
Context of invocation:
    - Called during the Sequencer playback pipeline when the sequencer dispatches a "play track" event. It represents the step where an entire Track (a library-specific track container) should be processed for playback at a given tempo on a given MIDI channel.
Why this is its own method:
    - Separates the high-level "play track" event handling from lower-level playback details so observers can implement custom behavior (for example emitting MIDI events, scheduling bars, or delegating to other play_* methods) without modifying the generic notify dispatcher.
    - Provides a single override point for track-level behavior, keeping notify minimal and making subclassing simpler and more explicit.

## Args:
    track (object): The Track object to play. Type is implementation-defined by the surrounding library (typically a Track or similar container holding Bars/NoteContainers). The method expects a track-like object conforming to the library's Track API (iterable of bars or exposing the sequence of musical events).
    channel (int): MIDI channel target for playback. Typical range is 0–15 for standard MIDI channels; the base implementation does not enforce range but callers and subclasses should use a valid MIDI channel.
    bpm (int|float): Tempo in beats-per-minute to use when interpreting the Track's timing. Should be a positive number; the base implementation does not validate the value.

## Returns:
    None
    - The base implementation returns nothing. Subclasses may choose to return a playback handle, scheduled task identifier, or other value, but notify and the base class expect no return value.

## Raises:
    - The base implementation does not raise any exceptions (it is a no-op). Subclass implementations may raise exceptions, but callers of notify currently do not handle exceptions specially; exceptions will propagate to the caller of notify.

## State Changes:
Attributes READ:
    - None in the base implementation (the method body is pass).
Attributes WRITTEN:
    - None in the base implementation.
    - Note: subclasses will commonly modify observer state (e.g., scheduling tables, open MIDI ports, playback cursors), but those mutations are implementation-specific and not present in the base class.

## Constraints:
Preconditions:
    - notify (or another caller) should supply a track-like object appropriate for the rest of the playback pipeline.
    - channel should represent a valid MIDI channel for any downstream MIDI output (commonly 0–15).
    - bpm should be a positive numeric tempo value.
Postconditions:
    - For the base class: no observable changes to self or other objects (no-op).
    - For overriding implementations: expected to result in scheduling or emitting the musical events contained in track according to channel and bpm; any stronger postconditions are implementation-dependent.

## Side Effects:
    - Base implementation: none.
    - Intended side effects for overrides:
        * Emitting MIDI events to an output device.
        * Scheduling playback of bars/notes via internal timers or a Sequencer instance.
        * Mutating observer state (playback queues, current position markers).
    - The method itself does not perform I/O or external calls in the base class; side effects occur only in subclass implementations.

## Implementation notes for subclasses:
    - Override this method to translate Track contents into the desired playback actions. Implementations commonly iterate bars/notes and call play_Bar, play_NoteContainer, or play_Note on the observer to keep behavior consistent with other event types.
    - Keep exceptions deliberate: if an override may raise, document and consider catching/logging within notify callers if needed.
    - Maintain compatibility with notify: expect to be invoked with exactly three parameters (track, channel, bpm).

### `mingus.midi.sequencer_observer.SequencerObserver.play_Tracks` · *method*

## Summary:
A placeholder hook for playing multiple tracks; currently a no-op in the shipped code but intended to dispatch playback requests for each track using the provided channels and bpm.

## Description:
Current behavior:
- The method body is empty (pass). Calling it has no effect in the present implementation.
- It is invoked by SequencerObserver.notify when the sequencer emits Sequencer.MSG_PLAY_TRACKS; notify forwards params["tracks"], params["channels"], and params["bpm"] to this method.

Known callers and lifecycle:
- SequencerObserver.notify handles sequencer messages and will call this method during sequencing playback when the sequencer requests that multiple tracks be played.
- It may also be called directly by external code that wants to request playback for several tracks at once.

Why this is its own method:
- Intentionally separated to provide a single place to implement batching logic (input normalization, validation, and per-track dispatch) instead of inlining that logic into notify or into play_Track. This separation keeps notify lightweight (message routing) and allows subclassing observers to override multi-track behavior independently from single-track playback.

Suggested contract for implementation (not enforced by current code):
- Normalize inputs, validate lengths/types, then invoke per-track playback (for example, call self.play_Track(track, channel, bpm) for each track).
- Handle the three forms for channels: a single int applied to all tracks, an iterable of ints matching the length of tracks, or None to indicate unspecified channels (passed through).
- Treat bpm as a positive numeric tempo value.

## Args:
    tracks (iterable): An iterable (e.g., list or tuple) of track-like objects. The method accepts an empty iterable (no-op). The concrete "track" interface expected by play_Track is not enforced here.
    channels (int | iterable[int] | None): Either:
        - a single integer channel to apply to every track,
        - an iterable of integers whose length matches tracks, or
        - None to indicate no channel information is provided.
      The current implementation does not validate or use this parameter.
    bpm (int | float): Tempo in beats per minute. Expected to be a positive number. The current implementation does not validate or use this parameter.

## Returns:
    None
    - Current implementation: returns None and performs no actions.
    - Recommended implementation: should still return None; side effects (calls to other methods) perform playback.

## Raises:
    Current implementation:
        - Does not raise any exceptions.
    Recommended implementation:
        - TypeError if tracks is not iterable or channels is of an unexpected type.
        - ValueError if channels is an iterable whose length does not match tracks, or if bpm is non-positive.
        - Any exceptions raised by delegated calls (e.g., self.play_Track) may propagate.

## State Changes:
    Attributes READ:
        - Current implementation: none (method is a no-op).
        - Suggested implementation: may read nothing from self by default; an implementation could read observer configuration (e.g., a default channel) if needed.
    Attributes WRITTEN:
        - Current implementation: none.
        - Suggested implementation: should not be required to modify persistent observer state; if it does (e.g., to record active tracks), that behavior must be documented by the overriding subclass.

## Constraints:
    Preconditions:
        - Callers should supply tracks as an iterable and bpm as a positive numeric value. These preconditions are recommendations; they are not enforced by the current pass implementation.
    Postconditions:
        - Current implementation: no postconditions (no-op).
        - Recommended implementation: for each element in tracks, a per-track playback operation is initiated (for example by calling self.play_Track for each track with the corresponding channel and bpm).

## Side Effects:
    Current implementation:
        - None.
    Recommended implementation:
        - Should delegate to per-track playback routines which may perform I/O, MIDI output, sleeping, or scheduling. Those side effects occur inside play_Track or related methods, not inside this dispatcher itself.

## Implementation guidance for reimplementing:
- Convert tracks to a concrete sequence to determine length.
- Normalize channels into a per-track sequence (repeat single-int channels as needed).
- Validate types and lengths, raising clear exceptions for invalid inputs.
- Iterate tracks and for each index call the single-track handler with the matched channel and bpm.
- Keep this method focused on dispatch; avoid implementing per-note timing or MIDI I/O directly here—those belong in play_Track, play_Bar, etc.

### `mingus.midi.sequencer_observer.SequencerObserver.play_Composition` · *method*

## Summary:
Handle delegated playback of a composition by mapping its constituent tracks to MIDI channels and invoking the observer's lower-level play_* methods; the base implementation is intended to traverse the composition and delegate but the concrete behavior is implementation-defined.

## Description:
Known callers and context:
- SequencerObserver.notify: the class's notify method maps Sequencer messages to observer methods and calls this method when it receives a MSG_PLAY_COMPOSITION message. Thus play_Composition is invoked during the Sequencer's playback dispatch phase when a complete composition should be handled by the observer.
- Typical lifecycle: called when starting or scheduling playback of a composition; responsibility is to translate a composition-level message into calls to per-track or per-bar playback routines implemented by the observer.

Why this is a separate method:
- A composition aggregates multiple tracks/bars and requires traversal and channel-assignment logic that would otherwise be duplicated. Centralizing traversal and delegation simplifies notify and lets subclasses override composition-level policies without altering low-level event emission.

## Args:
    composition (object):
        - Expected to be a composition-like object. Verifiable expectations from the codebase are minimal (the method exists but is unimplemented). Recommended contract:
            * Accept an object with a 'tracks' attribute that is iterable, or accept an iterable of tracks directly.
            * Each track should be a track-like object compatible with the observer's play_Track/play_Tracks implementations.
    channels (int | iterable[int] | dict | None):
        - The parameter is passed through to or used to produce per-track channel assignments. The base class does not enforce a concrete type; recommended forms:
            * int: same channel for all tracks.
            * iterable of ints: per-track channel list.
            * dict: explicit mapping from track index or identifier to channel number.
            * None: implies a default-per-track assignment policy (e.g., consecutive channels).
        - MIDI channel numbers are conventionally in 0..15.
    bpm (int | float):
        - Beats per minute used for playback timing. The base class places no restrictions, but implementations should treat bpm <= 0 as invalid.

## Returns:
    None
    - The method does not have a return value in the base class. Implementations may choose to perform synchronous delegation or schedule asynchronous playback; no value is returned to the caller.

## Raises:
    - The base class implementation (as shipped) is a no-op and does not raise. Implementers are encouraged to validate inputs and may raise:
        * TypeError for an unsupported composition type or malformed channels argument.
        * ValueError if bpm is non-positive or if channel numbers are out of the MIDI range.
    - These raises are recommendations for robust implementations rather than requirements enforced by the current stub.

## State Changes:
    Attributes READ:
        - The provided code for the base class contains no reads of specific self.<attr> attributes for this method. Subclasses that implement traversal may read observer state (for example, a playback queue or active session id) — those are not mandated here.
    Attributes WRITTEN:
        - The base stub does not modify any self.<attr> attributes. Concrete implementations may mutate observer state (e.g., registering an active playback session), but such mutations are implementation-defined.

## Constraints:
    Preconditions:
        - Caller should supply a composition-like object and a positive bpm. These are recommended preconditions for any non-trivial implementation.
    Postconditions (recommended contract for implementers):
        - For each track in the composition, the implementation will invoke an appropriate lower-level method such as:
            * self.play_Track(track, channel, bpm) for per-track invocation, and/or
            * self.play_Tracks(tracks, channels, bpm) for batched multi-track invocation.
        - No return value to the caller; side effects occur via delegated play_* methods.

## Side Effects:
    - The base method is a delegation point; actual side effects (sending MIDI events, sleeping, scheduling callbacks, writing to a MIDI stream) are expected to occur in the lower-level play_* implementations (play_Track, play_Bar, play_Note, etc.).
    - Implementations should avoid performing external I/O directly in play_Composition and instead delegate to lower-level methods to keep concerns separated.

## Implementation Guidance (recommended steps to reimplement):
1. Resolve tracks:
    - If composition has a 'tracks' attribute that is iterable, use it; otherwise, if composition itself is iterable, treat it as the sequence of tracks. If neither, handle or reject the input.
2. Normalize channels:
    - Accept int, iterable, dict, or None and produce a mapping from track index to channel number. Choose and document a policy for:
        * wrapping a short channel list cyclically, or
        * using a default channel for remaining tracks.
    - Validate channel values are integers within the MIDI range (0..15) if validation is desired.
3. Dispatch per-track:
    - For each track (by index), determine its channel and delegate to self.play_Track(track, channel, bpm).
    - Optionally batch multiple tracks and call self.play_Tracks(tracks_slice, channels_slice, bpm) if the observer implements an optimized multi-track entry point.
4. Edge cases:
    - Empty composition: do nothing.
    - Single-track composition: behave as general case.
    - If channels is insufficient for all tracks, follow the implemented policy (wrap or default).
5. Keep low-level effects centralized:
    - Do not emit raw MIDI events here; use the observer's existing play_Note, play_NoteContainer, play_Bar, play_Bars, etc., so subclasses consistently control I/O behavior.

## Example usage note:
- SequencerObserver.notify will call this method when receiving a Sequencer.MSG_PLAY_COMPOSITION event with params {"composition": ..., "channels": ..., "bpm": ...}. The observer's notify implementation demonstrates the expected parameter keys but not how play_Composition should behave internally.

### `mingus.midi.sequencer_observer.SequencerObserver.notify` · *method*

## Summary:
Dispatches a sequencer message to the corresponding event handler on this observer, causing the appropriate playback/control method to be invoked and thereby affecting the observer's runtime behavior (for example triggering playback, stopping notes, or changing instrument/state).

## Description:
This method is an event-dispatch hub used by the sequencer subsystem to notify observer instances about sequencer events. Typical caller:
- mingus.midi.sequencer.Sequencer (or any sequencer component that emits events using Sequencer.MSG_* constants). It is invoked at runtime when the sequencer processes scheduled events (play/stop/cc/instrument changes/sleep and higher-level musical structures such as NoteContainer, Bar, Track, Composition).

Rationale for separation:
- Keeps a single, centralized mapping from sequencer-level message constants to observer handler methods. This decouples message encoding (used by the Sequencer) from handling logic implemented by subclasses of SequencerObserver, and avoids inlining repetitive branching logic wherever events are delivered.

## Args:
    msg_type (int or enum-like constant):
        One of the Sequencer.MSG_* constants. The method uses equality comparisons against these constants to select the handler.
        Known values handled in code:
            - Sequencer.MSG_PLAY_INT
            - Sequencer.MSG_STOP_INT
            - Sequencer.MSG_CC
            - Sequencer.MSG_INSTR
            - Sequencer.MSG_SLEEP
            - Sequencer.MSG_PLAY_NOTE
            - Sequencer.MSG_STOP_NOTE
            - Sequencer.MSG_PLAY_NC
            - Sequencer.MSG_STOP_NC
            - Sequencer.MSG_PLAY_BAR
            - Sequencer.MSG_PLAY_BARS
            - Sequencer.MSG_PLAY_TRACK
            - Sequencer.MSG_PLAY_TRACKS
            - Sequencer.MSG_PLAY_COMPOSITION

    params (dict):
        A mapping containing the keyword parameters required by the selected message type. Required keys per message type:

        - Sequencer.MSG_PLAY_INT:
            "note" (int): integer pitch value
            "channel" (int): MIDI channel or logical channel index
            "velocity" (int): velocity value

        - Sequencer.MSG_STOP_INT:
            "note" (int)
            "channel" (int)

        - Sequencer.MSG_CC:
            "channel" (int)
            "control" (int): control/change number
            "value" (int): control value

        - Sequencer.MSG_INSTR:
            "channel" (int)
            "instr" (implementation-specific instrument id/object)
            "bank" (implementation-specific bank id/object)

        - Sequencer.MSG_SLEEP:
            "s" (float or int): seconds to sleep

        - Sequencer.MSG_PLAY_NOTE:
            "note" (Note-like object): high-level Note object or representation
            "channel" (int)
            "velocity" (int)

        - Sequencer.MSG_STOP_NOTE:
            "note" (Note-like object)
            "channel" (int)

        - Sequencer.MSG_PLAY_NC:
            "notes" (iterable/list of Note-like objects)
            "channel" (int)

        - Sequencer.MSG_STOP_NC:
            "notes" (iterable/list of Note-like objects)
            "channel" (int)

        - Sequencer.MSG_PLAY_BAR:
            "bar" (Bar-like object)
            "channel" (int)
            "bpm" (int or float)

        - Sequencer.MSG_PLAY_BARS:
            "bars" (iterable/list of Bar-like objects)
            "channels" (iterable/list of int)
            "bpm" (int or float)

        - Sequencer.MSG_PLAY_TRACK:
            "track" (Track-like object)
            "channel" (int)
            "bpm" (int or float)

        - Sequencer.MSG_PLAY_TRACKS:
            "tracks" (iterable/list of Track-like objects)
            "channels" (iterable/list of int)
            "bpm" (int or float)

        - Sequencer.MSG_PLAY_COMPOSITION:
            "composition" (Composition-like object)
            "channels" (iterable/list of int)
            "bpm" (int or float)

        Notes:
            - Types named "*-like object" indicate library-specific objects (Bar, Track, Composition, Note) used elsewhere in the codebase; the method itself treats them opaquely and simply forwards them to the corresponding handler.
            - params must be a subscriptable mapping; the method accesses values with params["key"].

## Returns:
    None
    - The method does not return a value; it performs dispatch by calling other instance methods. If msg_type is not matched by any known Sequencer.MSG_* constant, the method performs no action (no-op) and returns None.

## Raises:
    KeyError:
        - Raised when params does not contain a required key for the matched msg_type (e.g., params["note"] missing). The implementation uses direct subscription params["key"] so absent keys raise KeyError.

    TypeError:
        - Raised if params is not a subscriptable mapping (e.g., None or a non-mapping object) when the method attempts to index into it.

    Other exceptions:
        - Any exception raised by the dispatched handler methods (e.g., play_Note, cc_event) will propagate out of notify unless those handlers catch them. notify itself does not wrap or translate exceptions from handlers.

## State Changes:
    Attributes READ:
        - None directly (the method does not read any self.<attr> fields). It does reference class-level constants on Sequencer, not attributes on self.

    Attributes WRITTEN:
        - None directly (the method does not assign to any self.<attr> fields). It invokes other instance methods which may mutate object state; those mutations are not performed in notify itself but are a direct consequence of its calls.

## Constraints:
    Preconditions:
        - msg_type should be one of the Sequencer.MSG_* constants the method recognizes if a handler is expected to run.
        - params must be a mapping containing all keys required by the selected msg_type.
        - The observer instance should implement the handler methods referenced by notify (for example, play_Note, stop_Note, play_Bar, cc_event, etc.). The base class provides those methods as stubs; subclasses are expected to override them.

    Postconditions:
        - If msg_type matches a known constant and params contains the required keys, the corresponding self.<handler>(...) method has been invoked with the mapped arguments.
        - No return value is produced (returns None).
        - If params lacked required keys, a KeyError will be raised and no handler will have completed successfully.

## Side Effects:
    - Calls instance handler methods (e.g., play_int_note_event, stop_Note, cc_event, play_Bar, play_Composition). Those handlers may:
        * Mutate observer internal state (e.g., track active notes).
        * Perform I/O or interact with external MIDI output libraries.
        * Schedule or cancel further sequencer events (depending on handler implementations).
    - notify itself does not perform I/O directly; all I/O effects arise from the invoked handlers.

