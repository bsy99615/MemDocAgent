# `fluidsynth.py`

## `mingus.midi.fluidsynth.FluidSynthSequencer` · *class*

*No documentation generated.*

### `mingus.midi.fluidsynth.FluidSynthSequencer.init` · *method*

## Summary:
Creates and assigns a fluidsynth Synth instance to the object's self.fs attribute, preparing the sequencer to perform audio operations.

## Description:
- Known callers / usage context:
    - This method is intended to be called during initialization of a FluidSynthSequencer object (either immediately after construction or before any audio operations).
    - Methods in this class that expect init to have been run include: __del__, start_audio_output, load_sound_font, play_event, stop_event, cc_event, instr_event, and sleep — each of these methods directly uses self.fs.
    - Typical lifecycle: call init to create the Synth, then call load_sound_font/start_audio_output/play_event/etc. to operate on the synthesizer; when the sequencer is destroyed, __del__ will call delete on the Synth instance.

- Rationale for separate method:
    - Instantiating the underlying Synth is kept separate from object construction so callers can control when native/audio resources are allocated (for example, delaying allocation until an audio device or soundfont is available).
    - Separation also makes re-initialization or manual control of resource lifetime explicit rather than implicit in __init__.

## Args:
    None

## Returns:
    None

## Raises:
    Propagates any exception raised by the underlying fs.Synth() constructor. The method does not catch or wrap such exceptions; callers should handle errors coming from the fluidsynth binding (for example, failures to allocate native resources).

## State Changes:
- Attributes READ:
    - None (this method does not read any self.<attr> attributes)
- Attributes WRITTEN:
    - self.fs: set to the object returned by fs.Synth()

## Constraints:
- Preconditions:
    - The module-level name fs must refer to a module/object exposing a Synth constructor (i.e., calling fs.Synth() is valid). In this codebase, other methods assume such an alias is available.
    - The caller should not rely on self.fs being present prior to this call.
- Postconditions:
    - On successful return, self.fs exists and references the new Synth instance created by fs.Synth().
    - Subsequent instance methods that use self.fs can be called (e.g., start_audio_output, load_sound_font, play_event).
    - If the constructor raises, self.fs will not be set (exception propagates).

## Side Effects:
    - Allocates and returns a Synth object from the fluidsynth binding which may allocate native/audio resources (memory, handles, threads, connections to audio drivers).
    - No file I/O or network I/O is performed by this method itself, but the created Synth may perform such operations later through other methods.
    - Calling init multiple times will overwrite self.fs with a new Synth instance; the previous instance will no longer be referenced by this object and its native resources may remain until explicitly deleted or garbage collected (this method does not delete or clean up any prior Synth instance).

### `mingus.midi.fluidsynth.FluidSynthSequencer.__del__` · *method*

## Summary:
Invokes the synthesizer object's cleanup method to release underlying FluidSynth resources when the sequencer instance is being destroyed.

## Description:
This destructor is invoked by the Python garbage collector when the FluidSynthSequencer instance is finalized, or when client code explicitly deletes the instance (for example via del instance) and no other references remain. It centralizes cleanup of the external synthesizer handle so native/audio resources are released at object teardown rather than left to leak.

Known callers and lifecycle context:
- Python interpreter finalization / garbage collector when the object is unreachable.
- Explicit caller code that executes del instance or removes the last reference to the instance.
This method belongs to the object-finalization stage of the sequencer lifecycle (cleanup / resource release).

Why this logic is its own method:
- __del__ is the standard destructor hook in Python used for finalization. Placing the single resource-release call here ensures cleanup always occurs on object destruction and keeps cleanup logic out of higher-level control flows (start/stop functions), preventing duplication and making resource release deterministic when the object is collected.

## Args:
None.

## Returns:
None. The method returns implicitly with None.

## Raises:
- AttributeError: If self.fs does not exist or has no delete attribute (for example if initialization failed or init was not called), accessing self.fs or calling self.fs.delete() will raise AttributeError.
- Any exception raised by the underlying delete implementation (self.fs.delete()) may occur; such exceptions originate in the FluidSynth binding and are not handled here.

Note on exception handling behavior:
- Exceptions raised inside a __del__ method are handled by the Python runtime (typically printed to stderr) and are not propagated back to the code that triggered object deletion. They may appear as unhandled exception traces during program execution or interpreter shutdown.

## State Changes:
Attributes READ:
- self.fs

Attributes WRITTEN:
- None (the method does not assign to any self.<attr> fields)

## Constraints:
Preconditions:
- The instance should have been initialized so that self.fs references a valid synthesizer object with a callable delete() method (typically created in init()).
- It is expected that no other code will attempt to use the synthesizer after object finalization; callers should stop audio operations before allowing the sequencer to be garbage-collected.

Postconditions:
- The synthesizer object's delete() method has been invoked; native/audio resources managed by that object are expected to be released by the underlying FluidSynth binding.
- The attribute self.fs is not modified by this method itself (it remains referencing the same object until the instance memory is reclaimed), but the underlying synthesizer handle is considered released and further use of self.fs may fail.

## Side Effects:
- Calls out to an external/native cleanup routine (self.fs.delete()), which may:
    - Close audio drivers or device handles.
    - Free native memory or other system resources.
    - Perform I/O or block while tearing down the audio subsystem.
- Any exceptions or I/O produced by the underlying delete call will occur during object finalization and will be observed as runtime output (e.g., error traces printed to stderr) but not re-raised to caller code.

### `mingus.midi.fluidsynth.FluidSynthSequencer.start_audio_output` · *method*

## Summary:
Invokes the Synth object's start method stored on the instance to request that the underlying audio subsystem be started; the method itself only delegates and does not perform audio logic.

## Description:
This is a thin delegating method that calls self.fs.start(driver) and returns. It exists to provide an explicit public API for starting audio output separate from synthesizer creation and configuration.

Known callers and lifecycle context:
- No internal methods in mingus.midi.fluidsynth call start_audio_output. Sequencer.__init__ calls the class init method, and the FluidSynthSequencer.init implementation (in this module) sets self.fs = fs.Synth(), so client code should call start_audio_output after the object has been constructed.
- The class also provides load_sound_font (which calls self.fs.sfload(...)) and __del__ (which calls self.fs.delete()). Those methods demonstrate that self.fs is expected to be a Synth-like object supporting start, sfload, and delete.

Why this is its own method:
- Separates resource acquisition (opening/starting the audio device) from synthesizer instantiation/configuration. The wrapper delegates to the underlying binding so callers can decide when to acquire audio resources.

## Args:
    driver (optional): Passed through exactly to self.fs.start.
        - Type/values: Implementation-defined; forwarded unchanged to the underlying Synth.start method.
        - Default: None

## Returns:
    None
    - The wrapper does not return any value. Any return value from the underlying self.fs.start call (if any) is ignored.

## Raises:
    - AttributeError: if self.fs is not present on the object.
    - Any exception raised by the underlying self.fs.start(driver) call is propagated unchanged.

## State Changes:
    Attributes READ:
        - self.fs
    Attributes WRITTEN:
        - None (no attributes on self are modified by this method)

## Constraints:
    Preconditions:
        - self.fs must be initialized and must implement a start(driver) method. The module's init implementation sets self.fs = fs.Synth().
    Postconditions:
        - If the call completes normally, self.fs.start(driver) has been invoked. No further guarantees about return values or external audio state are made by this wrapper.

## Side Effects:
    - Calls into the underlying FluidSynth binding via self.fs.start(driver); effects on the host (device handles, threads, audio output) are produced by that binding and are not implemented in this wrapper.
    - The wrapper performs no file I/O and does not alter other attributes of the instance.

### `mingus.midi.fluidsynth.FluidSynthSequencer.start_recording` · *method*

## Summary:
Open a new WAV file for recording and attach the Wave_write object to the instance, preparing the sequencer to receive and store stereo 16-bit PCM at 44.1 kHz.

## Description:
This method creates and configures a wave.Wave_write file object and stores it on the instance so subsequent audio samples can be written to disk. It is typically invoked at the start of a recording session — e.g., by user code or higher-level sequencing/transport logic just before routing synthesized audio data to the recorder. The logic is encapsulated here so file creation and the canonical recording audio-format parameters (stereo, 16-bit, 44.1 kHz) are centralized and reused wherever recording is initiated.

Known callers and context:
- No callers are referenced inside this file. In practice, it is called by client code or a recording control routine to begin capturing audio before writing frames via the instance's wav attribute.

Why this is a separate method:
- File creation and format parameter setup are a single responsibility that should be performed atomically; keeping this as a dedicated method avoids duplicating the same setup steps and makes starting a recording a single, simple call.

## Args:
    file (str): Path to the output WAV file. Must be a filesystem path or path-like object accepted by the built-in open. Defaults to "mingus_dump.wav".
        - Behavior: opened with mode "wb" (write, binary). If the file already exists it will be truncated/overwritten.

## Returns:
    None: The method does not return a value. It assigns the opened wave.Wave_write object to self.wav for later use.

## Raises:
    OSError / IOError: Propagated if the underlying file cannot be created or written to (e.g., permission denied, invalid path, disk full). These originate from the built-in open called by wave.open.
    ValueError: Possible if wave.open is called with an invalid mode string (not expected when using the default "wb").

Note: The method itself does not explicitly raise exceptions; exceptions will propagate from wave.open or lower-level I/O calls.

## State Changes:
    Attributes READ:
        - None (this method does not read any self.<attr> attributes)

    Attributes WRITTEN:
        - self.wav: set to the wave.Wave_write object returned by wave.open configured as below.

    In-object state after the call:
        - self.wav is an open wave.Wave_write instance configured with:
            * nchannels = 2 (stereo)
            * sampwidth = 2 (2 bytes per sample = 16-bit)
            * framerate = 44100 (samples per second)

## Constraints:
    Preconditions:
        - The caller must have permission to create or overwrite the given file path.
        - The instance must be writable (i.e., assigning self.wav must be valid).
        - No other open writer should be writing to the same file path (to avoid races/overwrites).

    Postconditions:
        - An open wave.Wave_write object with the specified audio format is attached to self.wav.
        - The file on disk exists (or is created) and will be written to when frames are sent to self.wav.
        - The method does not close the file; the file remains open until explicitly closed.

## Side Effects:
    - File I/O: creates or truncates the specified file on disk and opens it for binary writing.
    - Resource allocation: leaves an open file handle attached to self.wav; callers are responsible for closing it (e.g., call self.wav.close() when recording is finished).
    - No network or external service calls are made.

### `mingus.midi.fluidsynth.FluidSynthSequencer.load_sound_font` · *method*

## Summary:
Loads a SoundFont file into the FluidSynth engine and stores the returned soundfont id on the sequencer instance, enabling subsequent instrument selection to reference that SoundFont.

## Description:
This method invokes the FluidSynth engine's sfload function to load the specified .sf2 soundfont file and records the returned soundfont id on the instance (self.sfid). It is typically called during sequencer setup after the FluidSynth Synth object has been created (self.fs initialized) and before any instrument/program selection events that use the soundfont (instr_event / program_select). No error handling is performed here; any exceptions from the underlying FluidSynth binding are propagated to the caller.

Why this is a separate method:
- Encapsulates the single responsibility of loading a soundfont and saving the resulting id.
- Centralizes the mapping between a loaded soundfont and the sequencer's stored soundfont id so other methods (e.g., instr_event) can assume self.sfid is the id of a previously-loaded soundfont.
- Keeps file I/O and FluidSynth interaction out of higher-level playback code.

Known callers and lifecycle stage:
- No direct callers are present in this module's source code besides external user code. In typical usage the sequence is:
  1. Construct the sequencer and initialize the FluidSynth engine (self.fs).
  2. Call load_sound_font(...) to load a .sf2 file and set self.sfid.
  3. Start audio output (start_audio_output) and play events that rely on the soundfont (instr_event / program_select).
- Called during initialization/setup of playback pipeline, before issuing program_select/instr_event calls that reference self.sfid.

## Args:
    sf2 (str): Path to the SoundFont file (usually a .sf2 file) to load. Must be a filesystem-accessible path (absolute or relative) that the process can read.

## Returns:
    bool: True if the soundfont was loaded successfully (the underlying sfload returned a non -1 id), False if sfload returned -1 indicating failure to load.

## Raises:
    AttributeError: If the FluidSynth Synth instance (self.fs) has not been initialized on this instance (e.g., init was not called), accessing self.fs will raise AttributeError.
    Any exception raised by the underlying FluidSynth binding (self.fs.sfload) is propagated unchanged. For example, if the binding raises OSError, IOError, or a binding-specific error when the file cannot be read or parsed, that exception will surface to the caller.

## State Changes:
    Attributes READ:
        self.fs
    Attributes WRITTEN:
        self.sfid

## Constraints:
    Preconditions:
        - self.fs must be a valid FluidSynth Synth-like object with a callable sfload method. Typically ensured by calling the class init method that creates self.fs before invoking this method.
        - The argument sf2 should be a valid path-like string pointing to an accessible .sf2 file.
    Postconditions:
        - self.sfid is set to the integer id returned by self.fs.sfload(sf2).
        - The method returns True if self.sfid != -1, otherwise returns False.
        - No additional cleanup or resource management is performed; the loaded soundfont remains registered in the FluidSynth engine until explicitly removed by the engine or the engine is deleted.

## Side Effects:
    - Performs file I/O via the FluidSynth binding (reads the .sf2 file content).
    - Calls into the FluidSynth engine (self.fs.sfload), which mutates the engine's global state by registering the loaded soundfont and returning an identifier.
    - Does not perform explicit logging, exception wrapping, or retries; all side-effecting errors are propagated.
    - No network I/O is performed.

### `mingus.midi.fluidsynth.FluidSynthSequencer.play_event` · *method*

## Summary:
Trigger the attached FluidSynth synthesizer to start (note-on) a single MIDI note by delegating to the underlying synth interface, updating no local state.

## Description:
This method delegates a MIDI note-on event to the FluidSynth backend stored on the instance (self.fs). It performs a single call to the synth's noteon method with the provided channel, note number, and velocity, causing the synth to begin sounding the specified note.

Known callers and context:
- Intended to be called from the sequencer/event-dispatch layer when a note-on event is scheduled or received. It centralizes the action of starting a note on the configured synth backend rather than inlining backend-specific calls across the sequencer logic.

Why this is a separate method:
- Encapsulates the backend call so higher-level sequencing logic does not directly reference the pyfluidsynth API, making it easier to mock, replace, or extend synth interactions in one place.

## Args:
    note (int):
        MIDI note number to play. Typical MIDI range is 0–127, where middle C is usually 60.
        The method does not validate the numeric range; values outside the synth's expected range are passed through to the backend.
    channel (int):
        MIDI channel on which to play the note. Typical channels are 0–15 (16 channels). Not validated by this method.
    velocity (int):
        MIDI velocity (note intensity) 0–127 is typical. A velocity of 0 is commonly interpreted by some systems as note-off; this method forwards the value as-is.

## Returns:
    None

## Raises:
    AttributeError:
        If the instance does not have an attribute self.fs, or self.fs is None, attempting to call noteon will raise AttributeError.
    Any exception raised by the underlying synth implementation's noteon method:
        Exceptions raised by self.fs.noteon (for example, TypeError for incorrect argument types or backend-specific errors) are not caught and will propagate to the caller.

## State Changes:
Attributes READ:
    self.fs

Attributes WRITTEN:
    None

## Constraints:
Preconditions:
    - self.fs must be set to an object that exposes a callable noteon(channel, note, velocity).
    - Caller should provide integers (or types accepted by the backend) for channel, note, and velocity.

Postconditions:
    - The synth referenced by self.fs has been instructed to play (start) the specified note on the given channel with the given velocity.
    - The method does not modify attributes on self.

## Side Effects:
    - Calls out to an external synth backend (self.fs.noteon) which typically produces audible sound or schedules sound generation in the synth process.
    - May interact with external audio resources managed by the backend; this method does not perform any I/O itself beyond invoking the backend API.

### `mingus.midi.fluidsynth.FluidSynthSequencer.stop_event` · *method*

## Summary:
Stops a sounding MIDI note on the FluidSynth synthesizer by issuing a note-off to the underlying Synth instance, changing the audible state of the synthesizer (stops the note if it is currently sounding).

## Description:
This method is a thin wrapper around the underlying pyfluidsynth Synth.noteoff call. It is intended to be invoked when the sequencer or client code needs to release/stop a note previously started with play_event (which calls Synth.noteon). Typical callers are the Sequencer's event processing logic or any external code controlling playback that schedules note-off events. Keeping this as a separate method centralizes the synth-specific call and preserves the Sequencer interface (so higher-level sequencer code can call stop_event without depending on pyfluidsynth directly).

## Args:
    note (int): MIDI note number to stop. Expected to be an integer representing pitch (conventional MIDI range is 0–127).
    channel (int): MIDI channel on which the note was played. Expected to be an integer (conventional range is 0–15).

## Returns:
    None

## Raises:
    AttributeError: If the FluidSynth Synth instance (self.fs) has not been initialized (e.g., init() not called) or has been deleted, attempting to access self.fs will raise AttributeError.
    Any exception raised by the underlying pyfluidsynth Synth.noteoff call may propagate unchanged (e.g., if pyfluidsynth validates arguments and raises).

## State Changes:
    Attributes READ:
        self.fs - used to call the underlying Synth.noteoff method
    Attributes WRITTEN:
        None (this method does not modify attributes on self)

## Constraints:
    Preconditions:
        - The instance must have been initialized such that self.fs exists and is a valid pyfluidsynth Synth object (FluidSynthSequencer.init sets self.fs).
        - note and channel should be integers; supplying values outside typical MIDI ranges may be ignored or cause errors in the underlying Synth implementation.
    Postconditions:
        - If call succeeds, the synthesizer will receive a note-off for (channel, note) and any currently sounding note matching those parameters will stop according to the synth's behavior.
        - No attributes on self are altered by this call.

## Side Effects:
    - Calls into the external pyfluidsynth Synth API (self.fs.noteoff), which affects audio output state (stopping the sounding note).
    - No file I/O is performed by this method itself.

### `mingus.midi.fluidsynth.FluidSynthSequencer.cc_event` · *method*

## Summary:
Sends a MIDI Control Change (CC) message to the underlying FluidSynth synth, causing the synth's controller state to update; this mutates the external synth (self.fs) but does not return a value.

## Description:
This method is the thin adapter that forwards a control-change command from the sequencer layer to the FluidSynth backend instance stored on the sequencer object.

Known callers and lifecycle context:
- Intended to be called by the sequencer's event-dispatching logic (or by external code using the Sequencer/FluidSynthSequencer API) whenever a MIDI Control Change (CC) message should be applied to the synth.
- Typical lifecycle: after the FluidSynthSequencer has been initialized (its init method created self.fs), this method is invoked during runtime to change synthesizer controller parameters (for example modulation, volume, pan, sustain pedal, etc.).

Why this logic is a separate method:
- Encapsulates the platform/backend-specific call to the FluidSynth API in one place so higher-level sequencer code can call a uniform API (cc_event) without knowing backend details.
- Keeps the sequencer's event-dispatch flow simple and testable and allows other backends to implement their own cc_event with the same signature.

## Args:
    channel (int):
        MIDI channel index for the control change. Expected MIDI range 0-15 (some systems use 1-16 user-facing); this method does not validate the range.
    control (int):
        Controller number (controller ID). Expected MIDI range 0-127; not validated here.
    value (int):
        Controller value. Expected MIDI range 0-127; not validated here.

## Returns:
    None

## Raises:
    AttributeError:
        If self.fs is not set or has been deleted (for example if init() was not called or the synthesizer was destroyed), accessing self.fs.cc will raise AttributeError.
    Exception (backend-specific):
        Any exception raised by the underlying FluidSynth backend's cc(...) call will propagate unchanged. The method does not catch or translate backend exceptions.

## State Changes:
Attributes READ:
    self.fs

Attributes WRITTEN:
    None on the FluidSynthSequencer instance itself.

Note: The underlying synth instance referenced by self.fs is mutated by this call (its controller state is changed), but no attributes on self are modified.

## Constraints:
Preconditions:
    - self.fs must be initialized and point to a synth object that exposes a cc(channel, control, value) method. In this class, init() sets self.fs (self.fs = fs.Synth()) — ensure init() has been called before invoking cc_event.
    - channel, control, and value should be integers (or types accepted by the fluid synth binding). The method does not coerce types.

Postconditions:
    - The underlying synth's controller state for the specified channel and controller will be updated according to the value passed (as implemented by the FluidSynth backend).
    - The method returns None.

## Side Effects:
    - Mutates external state: invokes the FluidSynth backend via self.fs.cc(...), which updates the synth's internal controllers and may immediately affect audio output.
    - No file or network I/O is performed by this method itself.

### `mingus.midi.fluidsynth.FluidSynthSequencer.instr_event` · *method*

## Summary:
Selects a SoundFont program (instrument) for a given output channel on the underlying FluidSynth instance, changing the synth's instrument mapping for that channel.

## Description:
This method is the handler that applies an instrument (program) and bank selection to the FluidSynth synthesizer instance stored on the object. It issues a single program_select call into the FluidSynth API so the synth will use the requested instrument on the specified channel.

Known callers / invocation context:
- Intended to be invoked when the sequencer processes an instrument-change (Program Change and/or Bank Select) MIDI event. In the class this method is the dedicated entry point for instrument-change events so higher-level sequencing logic can request instrument changes without dealing with FluidSynth API details.

Why this is a separate method:
- Encapsulates the mapping of sequencer-level instrument/bank/channel semantics to the FluidSynth program_select call.
- Keeps event-to-synth translation centralized and simple so callers (sequencer dispatch logic) do not need to interact with the FluidSynth API directly.

## Args:
    channel (int): MIDI output channel index to change. The method forwards this value directly to the FluidSynth program_select call.
    instr (int): Program (instrument) number to select; forwarded as the program argument to program_select.
    bank (int): Bank number to select; forwarded as the bank argument to program_select.

No default values; all three arguments are required.

## Returns:
    None. The method performs an action on the synthesizer; it does not return a value.

## Raises:
    AttributeError: If self.fs (the FluidSynth instance) or self.sfid (the loaded soundfont id) are not present on the instance, normal attribute access will raise AttributeError.
    Any exception raised by the underlying FluidSynth binding (self.fs.program_select) is not caught and will propagate to the caller.

## State Changes:
    Attributes READ:
        self.fs - the FluidSynth synthesizer instance used to execute program_select.
        self.sfid - the soundfont id previously returned by load_sound_font and passed to program_select.
    Attributes WRITTEN:
        None. This method does not modify any FluidSynthSequencer attributes.

## Constraints:
    Preconditions:
        - self.fs must be initialized (e.g., init() has been called which sets self.fs).
        - A soundfont should typically be loaded via load_sound_font(...) so self.sfid is present and valid; otherwise program_select will receive whatever value self.sfid holds (which may be missing or invalid).
        - channel, instr, and bank should be integers appropriate for the FluidSynth API (the method forwards them without validation).

    Postconditions:
        - After a successful call, the FluidSynth instance will have its program for the specified channel set to the requested bank/program combination.
        - The object’s attributes are unchanged by this method.

## Side Effects:
    - Makes a call into the FluidSynth native/binding API (self.fs.program_select), which instructs the synthesizer to change the instrument used for the given channel. This is an in-process native library call (no file I/O performed here).
    - No file I/O or external network I/O is performed by this method itself.

### `mingus.midi.fluidsynth.FluidSynthSequencer.sleep` · *method*

## Summary:
Pauses/advances playback for the requested duration; if a WAV recording is active, renders the corresponding number of audio frames from the FluidSynth synth and appends them to the open WAV file instead of sleeping.

## Description:
This method implements the sequencer's time-advancement behavior in two modes:
- Real-time mode: when no recording file is present, it blocks the current thread for the requested duration via time.sleep.
- Recording mode: when a WAV file has been opened (self.wav exists), it computes the number of frames for the requested duration at a fixed 44.1 kHz rate, asks the FluidSynth synth for that many frames, converts those frames into a raw byte string, and writes them to the WAV file. This advances the recorded audio output by the requested duration without relying on wall-clock sleeping.

Known callers and context:
- Called by the Sequencer playback loop (or other playback/timing code) to wait/advance between MIDI events. It is expected to be invoked wherever the sequencer requests a pause for a specified interval.
- Kept as a method to separate real-time waiting from offline rendering-to-WAV so higher-level sequencer logic remains agnostic about live vs. recorded output.

Why this logic is a separate method:
- Encapsulates differing behaviors (blocking sleep vs. offline rendering) behind a single API used throughout the sequencer.

## Args:
    seconds (float or int): Duration in seconds to advance/ pause. Must be numeric and non-negative. Fractional seconds are supported; the number of frames rendered in recording mode is computed as int(seconds * 44100).

## Returns:
    None

## Raises:
    This method does not explicitly raise its own exceptions, but may propagate exceptions raised by underlying calls, including but not limited to:
    - Errors converting `seconds` to an integer frame count (TypeError, ValueError).
    - Attribute/access errors if expected attributes are missing (AttributeError).
    - I/O errors when writing to the WAV file.
    These exceptions originate from the synth wrapper, the module-level conversion helper, or the wave file object — they are not created by this method itself.

## State Changes:
Attributes READ:
    - self.wav: existence checked via hasattr(self, "wav"); when present, used as the destination for writeframes.
    - self.fs: used to request generated audio frames via self.fs.get_samples(frame_count).
    - module-level fs helper: used to convert returned samples to a raw byte string via fs.raw_audio_string(...).

Attributes WRITTEN:
    - None of self's attributes are assigned or mutated by this method.
    - External mutation: self.wav.writeframes(...) modifies the open WAV file associated with self.wav (appends audio data and advances file position).

## Constraints:
Preconditions:
    - If recording mode is intended:
        * start_recording (or equivalent) must have been called prior to this method so that self.wav exists and is a configured wave write object (channels, sampwidth, framerate set).
        * self.fs must be initialized and able to produce audio frames via get_samples(n).
        * A module-level FluidSynth helper (referenced as fs in the implementation) must provide raw_audio_string(...) compatible with the samples from self.fs.get_samples.
    - `seconds` must be numeric. Negative values are unsupported — passing a negative value will produce a negative frame count when computing int(seconds * 44100) and may produce undefined behavior from the synth backend.

Postconditions:
    - In real-time mode: the calling thread will be blocked for approximately `seconds` seconds.
    - In recording mode: int(seconds * 44100) frames (at 44.1 kHz) will have been rendered from the synth and appended to the open WAV file; no attributes on self are modified by this method itself.

## Side Effects:
    - Blocking: time.sleep(seconds) blocks the current thread in real-time mode.
    - File I/O: in recording mode, the method calls self.wav.writeframes(...) which writes bytes to the WAV file handle (affecting disk or in-memory buffer).
    - External library interaction: calls into the FluidSynth wrapper (self.fs.get_samples) and a module-level conversion utility (fs.raw_audio_string), which may interact with native libraries or audio resources.
    - The method does not open or close the WAV file; it will not create self.wav — that must be handled separately (e.g., by start_recording).

## `mingus.midi.fluidsynth.init` · *function*

## Summary:
Initializes the Fluidsynth backend for playback or recording: starts audio output or recording, loads the specified SF2 soundfont, resets synth programs, and marks the backend as initialized. Returns True on success (or if already initialized), and False only when soundfont loading explicitly fails.

## Description:
- Known callers / usage context:
    - No direct callers were discovered in the scanned repository metadata. This module-level helper is intended to be invoked once during application startup or before any MIDI playback/recording operations to prepare the Fluidsynth backend.
    - Typical flow: call this function before sending MIDI events or starting sequencer playback so the underlying synth is ready and the desired soundfont is loaded.

- Why this function is extracted:
    - Groups together backend startup responsibilities (choose audio output vs recording, load soundfont, reset synth state) in a single, idempotent entry point so higher-level code can initialize the audio subsystem with one call.
    - Centralizes side effects and resource allocation to one place, reducing duplication and making error handling and lifecycle management easier for callers.

## Args:
    sf2 (str)
        Path (string) to a SoundFont2 file (.sf2) or any identifier accepted by the backend's load_sound_font method.
        - Required. Must be accessible by the running process (filesystem permissions, valid path).
    driver (optional)
        Driver identifier forwarded to midi.start_audio_output(driver).
        - Allowed values depend on the backend implementation (e.g., driver name string, device index, or None for default).
        - Default: None (use backend default audio device if recording is not requested).
    file (str or None, default=None)
        If provided (non-None), treated as the filename to record audio output to. When non-None, this takes precedence over driver: the function will call midi.start_recording(file) and will not call midi.start_audio_output.
        - Typical: path to .wav or another file format supported by the backend's recording implementation.

## Returns:
    bool
    - True:
        - If the module-level initialized flag is already True (function is idempotent and performs no further actions).
        - If initialization ran (audio output or recording started and soundfont loaded successfully), and midi.fs.program_reset() was called.
    - False:
        - Only when midi.load_sound_font(sf2) returns a falsy value (indicating the soundfont failed to load). In this case the function does not call program_reset() and does not set initialized = True.

Notes on return semantics:
    - The function does not inspect or propagate return values from midi.start_recording(file) or midi.start_audio_output(driver); any success/failure from those calls is not converted into the return value of this function. Only the result of midi.load_sound_font(sf2) is checked and can force a False return.

## Raises:
    - NameError:
        - If the module-level globals midi or initialized are not defined in the module namespace, a NameError will be raised upon access. This function assumes those globals exist and conform to the expected interface.
    - Any exception raised by backend calls:
        - Exceptions from midi.start_recording(file), midi.start_audio_output(driver), midi.load_sound_font(sf2), or midi.fs.program_reset() are not caught and will propagate to the caller.
    - No exceptions are raised directly by this function beyond the propagation of the above errors.

## Constraints:
- Preconditions:
    - The module must define:
        - a global object midi implementing:
            - start_recording(file)
            - start_audio_output(driver)
            - load_sound_font(sf2) -> truthy/False semantics
            - fs attribute with program_reset() method (i.e., midi.fs.program_reset() is callable)
        - a module-level boolean initialized that this function reads and writes.
    - Caller must ensure paths (sf2 and file) are valid and accessible and that the process has permissions to open audio devices or write files.
- Interdependencies:
    - file and driver: if file is non-None, driver is ignored because recording is chosen over real-time audio output.
- Postconditions:
    - If the function returns True after performing initialization:
        - Either recording has started (file given) or audio output has been started (driver used or default).
        - The provided soundfont has been loaded via midi.load_sound_font(sf2).
        - midi.fs.program_reset() has been executed.
        - The module-level initialized flag is set to True.
    - If False is returned:
        - Soundfont loading failed; program_reset() is not called and initialized remains unchanged.
    - If an exception is raised:
        - Partial side effects may have occurred (e.g., recording started). The function makes no rollback; callers must handle cleanup.

## Side Effects:
- Calls out to backend methods that may have significant side effects:
    - midi.start_recording(file) — may open/create the specified file and begin writing audio data.
    - midi.start_audio_output(driver) — may open audio device(s), start threads, or allocate native buffers/handles.
    - midi.load_sound_font(sf2) — loads SF2 data into the backend and allocates native resources.
    - midi.fs.program_reset() — resets synth programs/state in the backend.
- Mutates module-level state:
    - Sets initialized = True after successful initialization.
- I/O:
    - May create/overwrite the recording file specified by file.
    - May open OS audio devices and allocate native resources through the backend.
- Important implementation behavior:
    - The function does not validate or check the results of start_recording or start_audio_output; any failures or errors from those functions will manifest as exceptions if they raise, otherwise they are not reflected in this function's boolean return (only load_sound_font influences a False return).

## Control Flow:
flowchart TD
    A[Call init(sf2, driver=None, file=None)] --> B{initialized is True?}
    B -- Yes --> C[Return True (no-op)]
    B -- No --> D{file is not None?}
    D -- Yes --> E[Call midi.start_recording(file)]
    D -- No --> F[Call midi.start_audio_output(driver)]
    E --> G[Call midi.load_sound_font(sf2)]
    F --> G
    G --> H{load_sound_font returned truthy?}
    H -- No --> I[Return False (soundfont load failed)]
    H -- Yes --> J[Call midi.fs.program_reset()]
    J --> K[Set initialized = True]
    K --> L[Return True]

## Examples and recommended usage patterns:
- Basic initialization (default audio output):
    - Call init('/path/to/soundfont.sf2') early in application startup. Expect True on success. If it returns False, the soundfont could not be loaded — do not proceed to play notes.
- Initialize and record to a WAV file:
    - Call init('/path/to/soundfont.sf2', file='out.wav'). The function will begin recording to 'out.wav', then load the soundfont and reset programs. If load_sound_font returns False, recording may have been started but initialization is considered unsuccessful (False).
- Robust calling with error handling:
    - Since backend calls may raise and partial side effects can occur, wrap calls when you need to manage resources:
        - Attempt to call init(...).
        - If init returns False, abort playback and close any recording resources according to your backend's API.
        - If an exception is raised, perform cleanup (stop recording, close audio devices) using the backend's control functions; this function itself does not perform rollback.
- Notes for implementers:
    - Ensure module-level midi and initialized are present before calling this function to avoid NameError.
    - If you want failures in start_recording/start_audio_output to translate into a False return rather than an exception, implement wrapper logic that checks their return values or catches their exceptions and returns False accordingly.

## `mingus.midi.fluidsynth.play_Note` · *function*

## Summary:
Forwards the given note, channel, and velocity to the lower-level MIDI implementation and returns that implementation's result; acts as a fluidsynth-facing alias for note playback.

## Description:
This is a thin delegating wrapper that calls midi.play_Note(note, channel, velocity) and returns whatever that call returns. It does not implement playback itself; it exists to expose a fluidsynth module-level API compatible with other backend wrappers so higher-level code can call a consistent function name.

Known callers within the codebase:
- No callers were discovered in the provided snapshot. Treat this as a public API function intended for user code or other modules that want to play a single note via the fluidsynth-related API.

Why this function is separate:
- Encapsulation: centralizes the fluidsynth module's public surface so backend-specific behavior can be changed or validated in one place later.
- Compatibility: provides a stable, top-level function name for consumers of the mingus.midi.fluidsynth module.

Important implementation note (source-level observation):
- The function body references the global name midi but the provided file-level imports do not include a binding for midi. In the current source, midi must be defined elsewhere in the module (e.g., assigned or imported later) for this wrapper to work. If it is not present at runtime, a NameError will be raised when this function is called.

## Args:
    note (any):
        - Description: Passed unchanged to the delegated function. Represents the note to play.
        - Type: Not specified in this wrapper; must match the expectation of the underlying midi.play_Note implementation (commonly an integer MIDI note number 0–127, or a library-specific Note object/string). This wrapper does not validate the type or range.
        - Required: yes
    channel (int, optional):
        - Description: MIDI channel to use for playback; forwarded as-is.
        - Default: 1
        - Typical valid range: 1–16 (not enforced by this wrapper).
    velocity (int, optional):
        - Description: MIDI velocity (loudness) forwarded to the player.
        - Default: 100
        - Typical valid range: 0–127 (not enforced by this wrapper).

Interdependencies:
- No inter-parameter logic occurs in this wrapper; arguments are forwarded in the same order to midi.play_Note.

## Returns:
- The exact return value produced by midi.play_Note(note, channel, velocity). This wrapper does not alter or wrap that return value.
- If the delegated function returns None, this wrapper also returns None.

## Raises:
The wrapper itself can raise the following Python errors directly due to how it calls the global symbol:
    - NameError: If the global name midi is not defined in the module at runtime.
    - AttributeError: If midi exists but has no attribute play_Note.
    - TypeError: If midi.play_Note exists but is not callable, or if calling it with the given arguments triggers a TypeError.
Additionally:
    - Any exception raised by the underlying midi.play_Note (ValueError, IOError, runtime errors, or backend-specific exceptions) will propagate unchanged to the caller.

## Constraints:
Preconditions:
- The module-level symbol midi must be defined and must expose a callable play_Note attribute that accepts three positional arguments (note, channel, velocity) or compatible parameters.
- Any runtime requirements of the underlying implementation must be satisfied before calling (for example, a synthesizer initialized, a soundfont loaded). This wrapper does not enforce those preconditions.

Postconditions:
- If the call returns successfully (no exception), the delegated midi.play_Note has executed and any side effects it performs (audio output, state changes) have been applied; the wrapper returns the delegated result.

## Side Effects:
- The wrapper itself performs no I/O or state changes other than invoking the delegated function.
- Side effects come from midi.play_Note and may include:
    - Emitting audio to the system sound device or to an audio stream.
    - Mutating synthesizer/channel state in the midi backend.
    - Performing file or device I/O depending on the backend implementation.
- This wrapper does not log, cache, or persist any information itself.

## Control Flow:
flowchart TD
    Start --> CheckMidiDefined{Is global 'midi' defined?}
    CheckMidiDefined -- No --> RaiseNameError[NameError raised]
    CheckMidiDefined -- Yes --> HasAttribute{Has attribute 'play_Note'?}
    HasAttribute -- No --> RaiseAttributeError[AttributeError raised]
    HasAttribute -- Yes --> IsCallable{Is play_Note callable?}
    IsCallable -- No --> RaiseTypeError[TypeError raised when attempting to call]
    IsCallable -- Yes --> Call[midi.play_Note(note, channel, velocity)]
    Call -->|returns value| Return[Return value to caller]
    Call -->|raises exception| Propagate[Propagate exception to caller]

## Examples:
- Basic usage (assumes the module's midi binding and backend are correctly initialized elsewhere):
    from mingus.midi.fluidsynth import play_Note
    # Play MIDI note number 60 (middle C) on default channel 1 with default velocity
    try:
        result = play_Note(60)
    except NameError:
        print("Module-level 'midi' is not defined; ensure the midi backend is imported/initialized.")
    except Exception as e:
        # Errors from the underlying backend will propagate here
        print("Playback failed:", type(e).__name__, e)

- Defensive check before calling (explicit verification of the expected symbol):
    import mingus.midi.fluidsynth as fs
    if not hasattr(fs, "midi") or not hasattr(fs.midi, "play_Note"):
        raise RuntimeError("fluidsynth module midi.play_Note is not available")
    # Safe to call after verification
    fs.play_Note(60, channel=2, velocity=110)

## `mingus.midi.fluidsynth.stop_Note` · *function*

## Summary:
Delegates a request to stop a MIDI note to the package-level midi.stop_Note implementation and returns whatever that implementation returns.

## Description:
This function is a thin wrapper around the package/module-level function midi.stop_Note(note, channel). It does not implement any logic itself; it forwards the provided arguments to midi.stop_Note and returns its result.

Known callers within the analyzed codebase:
- No direct callers of mingus.midi.fluidsynth.stop_Note were discovered during analysis of the provided sources. The function exists to expose the midi.stop_Note functionality through the fluidsynth module namespace.

Typical usage context:
- Called when higher-level code (playback controls, sequencer, or user code) needs to stop/silence an individual MIDI note on a given channel. The actual stopping behavior, side effects, returned value, and exceptions are produced by the delegated midi.stop_Note implementation.

Why this logic is extracted into its own function:
- Provides a stable, module-level API on the fluidsynth module that forwards to the core midi implementation. This enables consumers to import and call stop_Note from mingus.midi.fluidsynth without referencing the underlying midi module directly, and keeps module-level API surfaces consistent across different backends or shims.

## Args:
    note (any):
        - Passed through to midi.stop_Note unchanged.
        - Typical expected values are integers (MIDI note numbers) or note-like objects convertible to int; exact accepted types depend on the delegated implementation.
    channel (int, optional):
        - Default: 1
        - Passed through to midi.stop_Note unchanged.
        - Typical MIDI channel numbers are 1..16, but no bounds are enforced by this wrapper.

## Returns:
    The return value is exactly the return value of midi.stop_Note(note, channel).
    - Because this wrapper does no post-processing, all possible return values and their meanings are determined by the delegated implementation.
    - If midi.stop_Note returns a boolean (e.g., True for success), this wrapper will return that boolean. If it returns None or any other type, this wrapper will return that same value.

## Raises:
    - NameError: If the name midi is not defined in the module's global scope, Python will raise NameError when attempting to evaluate midi.stop_Note.
    - Any exception raised by midi.stop_Note(note, channel) will propagate unchanged from this wrapper (for example TypeError, ValueError, IOError, or domain-specific exceptions raised by the underlying implementation).

## Constraints:
    Preconditions:
        - The global name midi must be defined and must expose a callable attribute stop_Note that accepts the provided (note, channel) arguments.
        - The caller should pass note and channel values valid for the delegated implementation (e.g., note convertible to int if the delegate requires that).
    Postconditions:
        - If the call completes normally, the wrapper returns the value returned by midi.stop_Note and does not otherwise mutate module-level or local state.

## Side Effects:
    - The wrapper itself introduces no additional side effects beyond those performed by midi.stop_Note.
    - Any I/O, MIDI output, logging, listener notifications, or state changes are performed by the delegated implementation and will occur as a consequence of calling this wrapper.
    - If midi is undefined, the NameError prevents any delegated side effects.

## Control Flow:
flowchart TD
    A[call fluidsynth.stop_Note(note, channel)] --> B{is name 'midi' defined?}
    B -- No --> C[raise NameError]
    B -- Yes --> D[call midi.stop_Note(note, channel)]
    D --> E{midi.stop_Note raises exception?}
    E -- Yes --> F[propagate exception to caller]
    E -- No --> G[return value from midi.stop_Note]

## Examples:
- Typical (descriptive) usage:
    1. Higher-level code decides a played note should stop (e.g., note duration elapsed, user action).
    2. Call mingus.midi.fluidsynth.stop_Note(note_value, channel_number).
    3. Handle exceptions that may arise from the underlying implementation (e.g., catch NameError if the environment is misconfigured, or other exceptions raised by the midi backend).

- Error-handling pattern (described):
    - Wrap the call in a try/except block to catch and handle NameError (missing backend) and any backend-specific exceptions, log or recover as appropriate, and avoid crashing the caller.

## `mingus.midi.fluidsynth.play_NoteContainer` · *function*

## Summary:
Forward the given NoteContainer to the configured MIDI backend for playback and return the backend's result.

## Description:
This function is a minimal forwarding wrapper: it calls the module-scope object named midi's play_NoteContainer method with the provided arguments and returns whatever that backend call returns.

Known callers within the codebase:
- No callers are declared inside this module file. Higher-level playback utilities or user code that wants to play a NoteContainer via the fluidsynth-facing API may call this wrapper.

Why this is a separate function:
- It exposes a stable API surface for playing NoteContainer objects through the fluidsynth-related module while leaving actual playback semantics (synchronous vs. asynchronous, return handle type, device I/O) to the selected midi backend implementation. Keeping this wrapper prevents call sites from depending on a specific backend and centralizes delegation logic.

Implementation note:
- The wrapper executes a single expression: it returns the result of midi.play_NoteContainer(nc, channel, velocity). Therefore every behavioral detail (validation, exceptions, return semantics, side effects) comes from that backend call.

## Args:
    nc (object):
        - Description: A NoteContainer-like value expected by the backend's play_NoteContainer (commonly an iterable or container of note events with timing, pitch, and duration).
        - Validation: This wrapper does not validate nc — any validation is performed by the backend.

    channel (int, optional):
        - Description: MIDI channel to use for playback.
        - Default: 1
        - Note: Conventional MIDI channels are in the 1–16 range; this wrapper does not enforce or normalize the value.

    velocity (int, optional):
        - Description: Default velocity (loudness) to apply to the notes.
        - Default: 100
        - Note: Conventional MIDI velocity ranges are 0–127; this wrapper does not enforce the range.

Interdependencies:
- The function assumes a module-level name midi exists and provides a callable attribute play_NoteContainer with the signature play_NoteContainer(nc, channel, velocity). The wrapper simply forwards arguments in the same order.

## Returns:
    - The exact value returned by midi.play_NoteContainer(nc, channel, velocity).
    - Common possibilities (backend-dependent):
        - None (typical for fire-and-forget / asynchronous playback)
        - A playback handle/object that can be used to stop/pause/resume playback
    - The wrapper does not modify or wrap the backend's return value.

## Raises:
    NameError:
        - Condition: The global name midi is not defined in this module's runtime namespace when the function is invoked.
    AttributeError:
        - Condition: The module-level midi object exists but does not have a callable attribute named play_NoteContainer.
    Any exception raised by the backend's play_NoteContainer:
        - Condition: The backend implementation raises runtime exceptions (TypeError, ValueError, IOError, OSError, etc.) during validation or I/O. These exceptions are not caught and will propagate.

## Constraints:
Preconditions:
    - The caller must ensure a correctly-constructed NoteContainer-like object is supplied as nc (shape and semantics expected by the configured backend).
    - The package or application must configure the module-level midi binding before calling this function; typically this happens during package initialization or by explicitly assigning a backend object to the name midi in the relevant module namespace.
    - channel and velocity should be integers; passing other types may produce backend TypeError or ValueError.

Postconditions:
    - If the function returns normally, the return value equals the backend's return value and any playback side effects produced by the backend have been initiated.
    - The wrapper does not modify module-local state.

## Side Effects:
    - The wrapper itself performs no I/O. All I/O and external effects occur inside the delegated backend:
        - Possible side effects include opening audio devices, sending MIDI events to a synthesizer, starting worker threads, writing temporary files, or other audio subsystem interactions depending on the selected backend.
    - The wrapper does not alter the midi binding or other module globals.

## Control Flow:
flowchart TD
    A[Start: play_NoteContainer(nc, channel, velocity) called] --> B{Is name 'midi' defined?}
    B -- No --> C[Raise NameError]
    B -- Yes --> D{Does midi.play_NoteContainer exist and is callable?}
    D -- No --> E[Raise AttributeError]
    D -- Yes --> F[Call midi.play_NoteContainer(nc, channel, velocity)]
    F --> G{Backend raises exception?}
    G -- Yes --> H[Propagate backend exception to caller]
    G -- No --> I[Return backend result]
    I --> J[End]

## Examples:
- Minimal safe call pattern (descriptive):
    1. Ensure the package has configured a backend and bound it to the module-level name midi (for example, during initialization).
    2. Construct a NoteContainer-like object compatible with your backend.
    3. Call the wrapper: play_NoteContainer(nc, channel=1, velocity=100).
    4. If backend returns a handle, use backend APIs to control playback; otherwise assume asynchronous fire-and-forget playback.

- Defensive usage pattern (conceptual):
    - Before calling, check that the backend is present and provides the required API:
        - If the check fails, initialize or select a suitable backend and retry.
    - Catch and handle backend errors (I/O errors, invalid NoteContainer) to present user-friendly diagnostics or to fallback to a different backend.

Notes:
- Because this function is only one line of delegation, consult the concrete midi backend implementation bound in your runtime for exact semantics: whether playback is synchronous or asynchronous, required NoteContainer structure, return types, and side-effect characteristics.

## `mingus.midi.fluidsynth.stop_NoteContainer` · *function*

## Summary:
Forwards the request to stop a NoteContainer to the active MIDI backend and returns the backend's boolean success result.

## Description:
This function is a thin wrapper that delegates stopping a NoteContainer to the project's MIDI implementation via midi.stop_NoteContainer(nc, channel). It does not implement stopping logic itself; it simply forwards arguments and returns whatever the backend returns.

Known callers and context:
- This wrapper is used where higher-level code needs to stop a previously started NoteContainer. See the Sequencer.stop_NoteContainer documentation for the typical call sites and playback lifecycle context (examples: play_Bar, play_Bars, play_Tracks, play_Composition). Those higher-level playback routines call a stop_NoteContainer implementation when a NoteContainer's playback duration ends; this function acts as the fluidsynth module's entry point that forwards to the configured midi backend.

Why this is a separate function:
- Provides a stable, module-level API in the fluidsynth module that other parts of the codebase can call without depending on a particular midi implementation symbol.
- Keeps backend selection or indirection in one place: callers call this function and the actual backend/midi module implements the concrete logic.

## Args:
    nc (iterable or None):
        - The NoteContainer to stop. Expected to be an iterable of note-like items (e.g., integers or note objects) or None.
        - If None, the delegated implementation typically handles it as a no-op (often returning True).
    channel (int, optional):
        - MIDI channel to use when stopping notes. Defaults to 1.
        - Typical range for MIDI channels is 1–16; this function does not validate the range and forwards the value to the backend.

## Returns:
    bool or backend-specific truthy/falsy value:
    - Returns whatever midi.stop_NoteContainer(nc, channel) returns.
    - In common backends (see Sequencer.stop_NoteContainer) this is a boolean:
        * True: all notes were stopped successfully or nc was None/empty.
        * False: stopping aborted because an individual note stop failed.
    - If the backend returns non-boolean values, Python truthiness is used by callers that treat the result as success/failure.

## Raises:
    Any exception raised by midi.stop_NoteContainer will propagate unchanged:
    - This wrapper does not catch exceptions. If the backend's implementation raises (e.g., due to a listener callback or MIDI I/O error), the exception passes through to the caller.

## Constraints:
Preconditions:
    - The module-level name midi must be defined and provide a callable stop_NoteContainer(nc, channel).
    - nc must be an iterable of notes or None; channel must be an integer (the function does not coerce types).
Postconditions:
    - After return, no additional work is performed by this wrapper; the final state is determined entirely by the backend's implementation and any side effects it produced.

## Side Effects:
    - No direct I/O or state mutation occurs within this wrapper itself.
    - Side effects come from the delegated implementation:
        * Notification to listeners (e.g., MSG_STOP_NC) and per-note stop operations.
        * MIDI output (sending "note off" events) or other listener-driven side effects (GUI updates, logging).
    - Exceptions from backend routines are not swallowed and will surface to the caller.

## Control Flow:
flowchart TD
    A[call stop_NoteContainer(nc, channel)] --> B{is midi.stop_NoteContainer defined?}
    B -- yes --> C[call midi.stop_NoteContainer(nc, channel)]
    C --> D{delegate returns value or raises}
    D -- returns --> E[return delegate value to caller]
    D -- raises --> F[exception propagates to caller]
    B -- no --> G[NameError at call time (Undefined midi.stop_NoteContainer)]

## Examples:
Example 1 — basic usage (happy path):
    try:
        success = stop_NoteContainer(my_note_container, channel=2)
        if not success:
            # backend signalled a failure stopping one or more notes
            handle_partial_failure()
    except Exception as exc:
        # An error from the underlying MIDI backend or listeners.
        log_error_and_recover(exc)

Example 2 — passing None (common pattern to notify listeners only):
    # Many backends treat nc=None as a valid no-op notification and return True.
    result = stop_NoteContainer(None)
    assert result is True  # depending on backend semantics; see backend docs

Notes and pointers:
- For full behavioral semantics (notification ordering, return value meaning, exceptions, and known callers), consult the Sequencer.stop_NoteContainer documentation which describes one concrete implementation of stop_NoteContainer used by the project.
- This function intentionally performs no validation or logic beyond delegation so backends remain authoritative for stopping semantics.

## `mingus.midi.fluidsynth.play_Bar` · *function*

## Summary:
Forwards a Bar playback request to a module-level MIDI implementation and returns whatever that implementation returns.

## Description:
This is a thin delegating wrapper that calls the module-level name midi.play_Bar with the provided arguments and returns its result. The wrapper itself performs no argument validation, transformation, or I/O; all behavior, side effects, and exceptions originate in the referenced midi.play_Bar implementation.

Known callers in this repository snapshot are not determined from the provided source. In typical usage this wrapper is invoked by higher-level playback utilities or application code that wants to play a Bar via the fluidsynth-facing API of the package.

The wrapper exists to expose midi.play_Bar through the mingus.midi.fluidsynth namespace so code using the fluidsynth API can call a canonical play_Bar function without referencing the lower-level midi module directly.

## Args:
    bar (object):
        - Type: opaque — the wrapper does not inspect the object.
        - Description: A Bar-like object expected by the underlying midi.play_Bar implementation (notes, durations, and any bar metadata as required by that implementation).
        - Constraints: Must conform to the shape/contract required by the underlying implementation; this wrapper will not validate it.
    channel (int, optional):
        - Default: 1
        - Description: MIDI channel number forwarded to midi.play_Bar.
        - Typical range: 1–16 (conventional MIDI channels). The wrapper does not enforce the range.
    bpm (int or float, optional):
        - Default: 120
        - Description: Tempo in beats per minute forwarded to midi.play_Bar.
        - Constraints: Should be a positive number (> 0). The wrapper does not validate this.

## Returns:
    Any: The exact return value produced by midi.play_Bar is returned unmodified. Possible return values and their meanings are defined by the underlying midi.play_Bar implementation; this wrapper makes no guarantees beyond direct propagation.

## Raises:
    NameError:
        - Condition: If the module-level name midi is not defined in this module, attempting to call midi.play_Bar will raise NameError.
    Any exception raised by midi.play_Bar:
        - Condition: Any exception thrown by the underlying implementation (for example, I/O errors, runtime errors, or custom exceptions) will propagate through this wrapper unchanged.

## Constraints:
Preconditions:
    - The module-level name midi must exist and must expose a callable attribute play_Bar.
    - The provided bar, channel, and bpm must be acceptable to midi.play_Bar (types and value ranges expected by that implementation).

Postconditions:
    - On success: the wrapper returns exactly the value returned by midi.play_Bar.
    - On failure: any exception raised by midi.play_Bar (including NameError if midi is undefined) propagates to the caller.

## Side Effects:
    - The wrapper itself has no direct side effects other than calling midi.play_Bar.
    - All observable side effects (audio playback, writing to devices or files, sleeping, stateful MIDI device interaction, etc.) are performed by the underlying midi.play_Bar implementation and are outside the wrapper's control.

## Control Flow:
flowchart TD
    Start --> CheckModule[Is module-level name 'midi' defined?]
    CheckModule -->|No| NameErrorNode[NameError raised]
    CheckModule -->|Yes| CallImpl[Call midi.play_Bar(bar, channel, bpm)]
    CallImpl -->|returns value| Return[Return that value]
    CallImpl -->|raises exception| Propagate[Propagate exception to caller]
    Return --> End
    Propagate --> End
    NameErrorNode --> End

## Examples:
- Typical usage pattern (described in prose):
    1) A caller assembles a Bar object in the shape expected by the underlying midi implementation.
    2) The caller invokes this wrapper with bar, optionally specifying channel and bpm.
    3) If the module-level midi is correctly configured to provide play_Bar, playback proceeds and the wrapper returns the underlying result; otherwise a NameError or other exception from the implementation will be raised.

- Error-handling guidance:
    - Wrap calls to this wrapper in exception handling appropriate to the application. Handle NameError specifically if there is any chance the midi binding was not initialized or imported in the running environment.
    - Consult the underlying midi.play_Bar implementation (not documented here) to learn which concrete exceptions may occur and how to interpret return values.

## `mingus.midi.fluidsynth.play_Bars` · *function*

## Summary:
Forwards a request to play a sequence of musical bars to the package-level playback implementation and returns that implementation's result.

## Description:
This function is a thin wrapper that calls midi.play_Bars(bars, channels, bpm) and returns whatever the delegated implementation returns. It exists to expose a play_Bars entry point under the mingus.midi.fluidsynth namespace while delegating actual playback, audio I/O, and sequencing logic to the package-level midi implementation.

Known callers:
    - No direct callers were found within the immediate file context. Typical callers are application code or other library modules that want to trigger playback via the fluidsynth-related namespace (for example, UI code or script-level playback utilities).

Why this is a separate function:
    - Namespace aliasing: provides a stable, module-level function in the fluidsynth module so other code can import or reference mingus.midi.fluidsynth.play_Bars.
    - Separation of concerns: retains fluidsynth.py as a thin façade while allowing the real playback logic to live in a centralized midi implementation.

## Args:
    bars (any):
        Forwarded unchanged to midi.play_Bars. This wrapper performs no validation or transformation.
    channels (any):
        Forwarded unchanged to midi.play_Bars. The expected structure and semantics are defined by the delegated implementation.
    bpm (int, optional):
        Beats per minute value forwarded unchanged. Defaults to 120 in this wrapper.

    Notes:
        - Any constraints, expected types, or structure for bars and channels are the responsibility of the delegated midi.play_Bars implementation. Callers should consult that implementation for precise contracts.

## Returns:
    The wrapper returns exactly the return value produced by midi.play_Bars. The type, meaning, and possible values are those defined by the delegated implementation and are not altered by this wrapper.

## Raises:
    NameError:
        If the name midi is not defined in the module namespace at call time, Python will raise a NameError.
    AttributeError:
        If the module-level midi object exists but does not expose a callable attribute named play_Bars, an AttributeError will be raised when the wrapper attempts to access that attribute.
    Any exception raised by midi.play_Bars:
        All exceptions thrown by the delegated implementation propagate through this wrapper unchanged.

## Constraints:
    Preconditions:
        - The module-level symbol midi must be present and must expose a callable attribute play_Bars.
        - Arguments passed must satisfy the expectations of the underlying midi.play_Bars (this wrapper does not validate them).
    Postconditions:
        - If the call returns successfully, any side effects performed by midi.play_Bars (audio playback, state changes, file writes, etc.) will have been executed.
        - The return value is the same object returned by midi.play_Bars.

## Side Effects:
    - This wrapper itself performs no direct I/O or state mutation aside from invoking midi.play_Bars.
    - All observable side effects (audio output, file or network I/O, global state changes) originate from the delegated implementation and therefore depend on that implementation.

## Control Flow:
flowchart TD
    A[Caller invokes play_Bars(bars, channels, bpm)] --> B{Is name 'midi' bound in module?}
    B -- No --> C[NameError raised at runtime]
    B -- Yes --> D{Does midi have attribute play_Bars?}
    D -- No --> E[AttributeError raised at runtime]
    D -- Yes --> F[Call midi.play_Bars(bars, channels, bpm)]
    F --> G{midi.play_Bars returns normally?}
    G -- Yes --> H[Return value from midi.play_Bars returned to caller]
    G -- No --> I[Exception from midi.play_Bars propagates to caller]

## Examples:
Illustrative usage patterns — actual behavior depends on the delegated implementation.

    # Simple forward call (result and side effects are implementation-defined)
    result = play_Bars(bars_obj, channel_map, bpm=140)

    # Call with default bpm
    result = play_Bars(bars_obj, channel_map)

    # Defensive caller: ensure the module-level midi symbol exists before calling
    try:
        # If your application sets up the package-level midi implementation, call through the fluidsynth wrapper:
        play_Bars(bars_obj, channel_map)
    except NameError:
        # The module-level midi symbol is missing
        raise RuntimeError("Playback backend not registered: set up package-level 'midi' before calling play_Bars")
    except AttributeError:
        # The bound object does not provide play_Bars
        raise RuntimeError("Registered 'midi' backend does not implement play_Bars")

Troubleshooting tips:
    - Ensure your application initializes or assigns a concrete midi implementation into the package/module namespace before calling this wrapper (for example, the package’s central midi implementation object).
    - If you need to inspect return values, call the underlying midi.play_Bars directly to learn its precise contract (types, return semantics, and error conditions).

## `mingus.midi.fluidsynth.play_Track` · *function*

## Summary:
Forwards the provided track, channel, and bpm parameters to the package-level midi.play_Track implementation and returns that implementation's result.

## Description:
This function is a minimal delegator: it calls midi.play_Track(track, channel, bpm) and returns whatever that call returns. It does not implement playback or perform validation itself.

Known callers within the inspected codebase:
    - None discovered in the inspected snapshot. This wrapper is intended for direct use by application code or higher-level modules that rely on the package-level midi playback facility.

Why this logic is extracted:
    - Responsibility boundary: the wrapper exposes a fluidsynth-module entry point that centralizes forwarding to the canonical midi.play_Track. This keeps the fluidsynth API surface stable while deferring playback implementation to the package-level midi object.

## Args:
    track (object): Opaque track object forwarded unchanged to the underlying midi.play_Track. The wrapper imposes no structure or type checks on this argument.
    channel (int, optional): MIDI channel index forwarded as-is. Defaults to 1.
    bpm (int or float, optional): Tempo in beats-per-minute forwarded as-is. Defaults to 120.

Interdependencies:
    - The wrapper does not validate argument interdependencies; correct values and types are the caller's responsibility and must match what the underlying midi.play_Track expects.

## Returns:
    Any: Exactly the value returned by midi.play_Track(track, channel, bpm). The wrapper does not transform or wrap the result. In common implementations this may be None (for functions performing side effects), but the actual return type/meaning depends on the underlying implementation.

## Raises:
    NameError:
        - Condition: The module-global symbol midi is not defined in this module's global namespace at call time. Accessing midi will raise NameError before any playback attempt.
    AttributeError:
        - Condition: The module-global midi exists but does not have an attribute named play_Track. Accessing midi.play_Track will raise AttributeError.
    TypeError:
        - Condition: The module-global midi has an attribute play_Track but that attribute is not callable (e.g., not a function). Attempting to call it raises TypeError.
    Any exception raised by the underlying midi.play_Track:
        - Condition: The wrapper makes no attempt to catch errors from the delegated call; all exceptions raised by the underlying implementation are propagated to the caller.

## Constraints:
Preconditions:
    - The caller must ensure a module-global symbol midi exists and that midi.play_Track is a callable with a compatible signature.
    - The caller must supply a track and parameters acceptable to the underlying midi.play_Track.

Postconditions:
    - If the call returns normally, the wrapper returns the same result as the underlying midi.play_Track.
    - No additional mutation of inputs or module-level state is performed by the wrapper itself beyond what the underlying call does.

## Side Effects:
    - The wrapper does not directly perform I/O, file operations, or network access. Any such side effects are produced by the underlying midi.play_Track and are not modified by this wrapper.
    - The wrapper does not mutate the passed-in arguments; it only forwards references to the underlying call.

## Control Flow:
flowchart TD
    Start --> CheckMidiDefined
    CheckMidiDefined -->|midi defined| CheckHasAttribute
    CheckMidiDefined -->|midi not defined| RaiseNameError
    CheckHasAttribute -->|has play_Track attribute| CheckCallable
    CheckHasAttribute -->|no play_Track attribute| RaiseAttributeError
    CheckCallable -->|callable| CallUnderlying
    CheckCallable -->|not callable| RaiseTypeError
    CallUnderlying -->|returns normally| ReturnResult
    CallUnderlying -->|raises exception| PropagateError
    ReturnResult --> End
    PropagateError --> End
    RaiseNameError --> End
    RaiseAttributeError --> End
    RaiseTypeError --> End

## Examples:
Example — ensure binding and call (conceptual; avoid assuming module import behavior):
    1) Ensure the module-global 'midi' symbol in the fluidsynth module is bound to the package-level MIDI implementation (i.e., an object exposing a callable play_Track).
    2) Call the wrapper with an application Track and parameters:
        - Provide a track object prepared by your application or sequencer.
        - Use channel and bpm values appropriate for the underlying implementation.
    3) Handle errors that indicate misconfiguration or runtime failure:
        - If NameError, AttributeError, or TypeError are raised, inspect how 'midi' is bound in the fluidsynth module and correct the binding.
        - If other exceptions are raised, treat them as errors from the underlying midi implementation (e.g., audio backend failures) and handle or log accordingly.

Notes:
    - Because this wrapper performs no validation or error handling, callers who need robust behavior should verify the presence and type of fluidsynth.midi and may wrap the call in try/except to provide user-friendly messages or fallbacks.

## `mingus.midi.fluidsynth.play_Tracks` · *function*

## Summary:
Forwards a multi-track playback request to the configured MIDI backend and returns whatever result the backend's play_Tracks implementation returns.

## Description:
This function is a thin adapter that delegates to the repository's backend MIDI implementation (the module-level midi.play_Tracks) and does not add logic of its own.

Known callers and context:
- No direct callers of this wrapper were found in the provided memory snapshot. Higher-level playback routines (for example, the Sequencer.play_Tracks method in mingus.midi.sequencer) implement multi-track playback semantics in this codebase; those higher-level components expect backend implementations of play_Tracks that accept the same argument structure described below.
- Typical invocation context is during the playback stage of a sequencing pipeline when multiple tracks must be played simultaneously on specified channels at a given BPM.

Why this is a separate function:
- It provides a backend-specific entry point (fluidsynth backend module) which forwards to the backend's generic midi.play_Tracks implementation. Keeping this thin wrapper allows the codebase to present a consistent public API (e.g., mingus.midi.fluidsynth.play_Tracks) while the actual playback behavior is implemented by a pluggable midi backend module.

## Args:
    tracks (sequence): A sequence (list/tuple) of Track-like objects. Each track is expected to be indexable by bar number and to expose a per-track .instrument attribute. The wrapper passes this value through unchanged to the underlying backend.
    channels (sequence): A sequence of channel identifiers (commonly ints) with one entry per track. channels[x] is used by the backend when setting instruments or routing playback for the x-th track. The wrapper does not validate lengths — the backend will raise IndexError or similar if lengths mismatch.
    bpm (int | float, optional): Beats-per-minute used to control playback timing. Defaults to 120. Passed through unchanged.

Interdependencies:
- The wrapper does not transform arguments; any semantic constraints (e.g., channels length >= number of tracks, each track being non-empty and indexable) are the responsibility of the underlying backend implementation (midi.play_Tracks). In this codebase, Sequencer.play_Tracks documents and enforces the expectation that channels length must be at least the number of tracks and that each track is indexable by bar.

## Returns:
    Any: Returns exactly the value returned by midi.play_Tracks. Common/typical return values used by other playback implementations in this codebase include:
        - dict with {"bpm": final_bpm} on successful completion (where final_bpm is the last bpm used)
        - empty dict {} to indicate playback was aborted
    Because this function is purely a delegator, callers should handle return values according to the backend contract (see backend implementation or Sequencer.play_Tracks documentation for expected semantics).

## Raises:
    NameError: If the module-level name midi is not defined in this module at runtime (this wrapper directly references midi.play_Tracks).
    Any exception raised by the underlying midi.play_Tracks call will propagate unchanged. This includes (but is not limited to) IndexError, TypeError, AttributeError, or backend-specific exceptions.

## Constraints:
Preconditions:
    - The module-level symbol midi must be bound to an object that exposes a callable play_Tracks(tracks, channels, bpm).
    - tracks and channels must be in a form acceptable to the underlying backend (commonly: tracks is a non-empty sequence of indexable Track objects; channels is a sequence with one channel per track).
Postconditions:
    - No local state in this wrapper is modified.
    - Any side effects (MIDI messages, timing sleeps, listener notifications) are performed by the underlying backend and are not controlled by this wrapper.

## Side Effects:
    - None performed directly by this function other than calling the backend. All I/O, timing/sleeping, MIDI output, or listener notifications are side effects of the backend's midi.play_Tracks.
    - If midi.play_Tracks performs I/O (writing to MIDI device, stdout logging, etc.), those effects will occur as a result of calling this wrapper.

## Control Flow:
flowchart TD
    A[call play_Tracks(tracks, channels, bpm)] --> B{is midi defined?}
    B -- No --> C[raise NameError]
    B -- Yes --> D[call midi.play_Tracks(tracks, channels, bpm)]
    D --> E{midi.play_Tracks returns or raises}
    E -- raises --> F[propagate exception to caller]
    E -- returns --> G[return same value to caller]

## Examples:
Typical usage (caller handles backend return value and exceptions):

    try:
        result = play_Tracks(tracks_list, channel_list, bpm=100)
    except NameError:
        # Backend not configured: handle or reconfigure midi backend
        configure_midi_backend()
        result = play_Tracks(tracks_list, channel_list, bpm=100)
    except Exception as e:
        # Backend raised an error during playback (e.g., IndexError for bad channels)
        log_error(e)
        result = {}

    # Interpret backend-specific result:
    if isinstance(result, dict) and "bpm" in result:
        final_bpm = result["bpm"]
    elif result == {}:
        # Playback was aborted
        handle_abort()
    else:
        # Other backend-specific return; consult backend documentation
        handle_other_result(result)

## `mingus.midi.fluidsynth.play_Composition` · *function*

## Summary:
Forwards a Composition playback request to the package's core MIDI playback implementation and returns that implementation's result.

## Description:
This is a thin forwarding wrapper that calls midi.play_Composition(composition, channels, bpm) and returns its result unchanged. It does not implement playback logic, validation, or listener notification itself; all such behavior is performed by the delegated implementation.

Known callers:
- Intended to be called by application-level code that imports a fluidsynth-specific helper entrypoint to start playback. The wrapper exists to expose a backend-specific alias for the shared midi.play_Composition API.

Why this is a separate function:
- Provides a stable fluidsynth-module entrypoint that mirrors the core midi API. This keeps import sites consistent (users can import from mingus.midi.fluidsynth) while centralizing playback behavior in the core midi implementation.

## Args:
    composition (object)
        - Required.
        - A composition-like object; the wrapper does not inspect its internals but forwards it as-is. The delegated implementation commonly expects composition.tracks to be a sequence of Track objects.
    channels (list[int] or None, optional)
        - Defaults to None.
        - If provided, this sequence is forwarded unchanged. The wrapper performs no length or value validation.
    bpm (int or float, optional)
        - Defaults to 120.
        - Forwarded unchanged to the delegated implementation.

## Returns:
    Any
        - Exactly the value returned by midi.play_Composition. This wrapper does not alter or interpret the return value.
        - Because behavior is implementation-dependent, consult the core midi.play_Composition or a Sequencer-backed implementation (e.g., Sequencer.play_Composition) for typical return structures.

## Raises:
    NameError
        - If the name midi is not defined in the module namespace, a NameError will be raised when attempting to call midi.play_Composition.
    Any exception raised by midi.play_Composition
        - All exceptions raised by the delegated implementation (e.g., AttributeError, TypeError, backend I/O errors) propagate unchanged. The wrapper does not catch or translate exceptions.

## Constraints:
Preconditions:
    - The module-level symbol midi must be defined and expose a callable play_Composition.
    - The caller should provide a composition-like object appropriate for the delegated implementation (commonly exposing composition.tracks).
    - If channels is supplied, its semantics and constraints (length, valid MIDI channel numbers) are determined by the delegated implementation.

Postconditions:
    - midi.play_Composition has been invoked with the same composition, channels, and bpm arguments.
    - The wrapper returns the exact value returned by midi.play_Composition or propagates the exception raised by it.

## Side Effects:
    - The wrapper itself performs no I/O or state mutation aside from calling the delegated function.
    - Any side effects (MIDI output, sleeps/timing, listener notifications, file or device I/O) are produced by midi.play_Composition and its callees.

## Control Flow:
flowchart TD
    Start --> CheckMidiDefined{Is `midi` defined?}
    CheckMidiDefined -->|No| RaiseNameError[NameError raised]
    CheckMidiDefined -->|Yes| CallDelegated[midi.play_Composition(composition, channels, bpm)]
    CallDelegated -->|returns value| ReturnValue[Return delegated value]
    CallDelegated -->|raises exception| Propagate[Propagate exception to caller]
    ReturnValue --> End
    Propagate --> End

## Examples:
Typical usage with defensive error handling:

    # High-level usage — ensure the module-level `midi` binding exists in your runtime.
    try:
        result = mingus.midi.fluidsynth.play_Composition(composition, channels=None, bpm=110)
    except NameError as ne:
        # The fluidsynth module does not have a `midi` symbol configured
        configure_or_import_core_midi(ne)
    except Exception as e:
        # Handle playback/backend errors (missing attributes, I/O, etc.)
        handle_playback_error(e)
    else:
        # Use the returned playback info (structure depends on the underlying implementation)
        process_playback_result(result)

See also:
    - The core midi.play_Composition implementation for exact semantics.
    - mingus.midi.sequencer.Sequencer.play_Composition for an example Sequencer-backed implementation that documents expected composition.tracks usage and typical return structures.

## `mingus.midi.fluidsynth.control_change` · *function*

## Summary:
Delegates a MIDI Control Change request to the underlying MIDI backend and returns that backend's response.

## Description:
This function is a thin wrapper that forwards a MIDI Control Change operation to an underlying midi object's control_change callable.

Known callers within this codebase:
    - No internal call sites were found in the repository for this wrapper. It is exported by the fluidsynth module for external use (e.g., interactive control, UI callbacks, sequencer or MIDI input handlers).

Typical trigger/context:
    - Called when an application or user wants to change a controller parameter (volume, pan, modulation, sustain, custom controller) on a particular MIDI channel while using the Fluidsynth-based MIDI backend.
    - Commonly used in real-time control paths: UI slider events, external MIDI CC-to-parameter mappings, or sequencer/automation callbacks.

Rationale for extraction:
    - Enforces a consistent API surface for the fluidsynth module that delegates backend-specific behavior to a pluggable midi object.
    - Keeps higher-level code decoupled from the concrete MIDI implementation and centralizes the delegation logic in one place.

## Args:
    channel (int):
        - MIDI channel index. Conventional MIDI channels range 0–15 (representing channels 1–16 to end users).
        - The function does not validate this range; the underlying backend may enforce or clamp it.
    control (int):
        - Controller number (conventional range 0–127).
        - Represents which controller is being changed (e.g., 7 for main volume, 10 for pan).
        - No validation is performed here.
    value (int):
        - Controller value (conventional range 0–127).
        - No validation is performed here.

Interdependencies:
    - There are no direct inter-parameter dependencies enforced by this function; validity is determined by the caller or the underlying midi implementation.

## Returns:
    - Returns the exact value returned by midi.control_change(channel, control, value).
    - Commonly this will be None for backends that perform the operation and do not return data, but the concrete return type/value depends entirely on the underlying midi object's implementation.
    - No additional post-processing or wrapping is performed.

## Raises:
    - NameError:
        - If the module-level name midi is not defined in this module when the function is called.
    - AttributeError:
        - If the midi object exists but does not have a control_change attribute.
    - TypeError:
        - If the midi.control_change attribute exists but is not callable or is called with incompatible argument types.
    - Any exception raised by the underlying midi.control_change call will propagate unchanged.

## Constraints:
Preconditions:
    - A module-level object named midi must exist and expose a callable control_change attribute that accepts (channel, control, value).
    - Caller should pass integers for channel, control, and value; the function does not coerce types.

Postconditions:
    - If the call succeeds (no exception), the underlying midi backend has been invoked with the provided parameters and any backend-side effects (e.g., sending a MIDI CC message to a synthesizer) will have occurred.
    - The function returns whatever the backend returned.

## Side Effects:
    - No file, network, or stdout I/O is performed by this wrapper itself.
    - External state mutation depends on the midi implementation: typically sending a MIDI Control Change message to the configured synthesizer/output device or mutating backend-specific state.
    - Any side effects produced by the underlying midi.control_change call (such as scheduling audio events or altering synthesizer parameters) will occur.

## Control Flow:
flowchart TD
    Start --> CheckMidiDefined
    CheckMidiDefined{Is module-level 'midi' defined?}
    CheckMidiDefined -- No --> RaiseNameError[Raise NameError]
    CheckMidiDefined -- Yes --> HasAttr{Has attribute 'control_change'?}
    HasAttr -- No --> RaiseAttributeError[Raise AttributeError]
    HasAttr -- Yes --> IsCallable{Is midi.control_change callable?}
    IsCallable -- No --> RaiseTypeError[Raise TypeError]
    IsCallable -- Yes --> CallBackend[Call midi.control_change(channel, control, value)]
    CallBackend --> ReturnResult[Return backend result]
    RaiseNameError --> End
    RaiseAttributeError --> End
    RaiseTypeError --> End
    ReturnResult --> End

## Examples:
    # Example 1: Typical usage (happy path)
    try:
        # assumes control_change function is available in the current namespace
        result = control_change(0, 7, 100)  # set main volume on MIDI channel 1
    except Exception as e:
        # handle backend not configured or other runtime issues
        handle_error(e)

    # Example 2: Defensive caller that validates ranges before calling
    ch, ctrl, val = 0, 10, 64
    if 0 <= ch <= 15 and 0 <= ctrl <= 127 and 0 <= val <= 127:
        try:
            control_change(ch, ctrl, val)
        except (NameError, AttributeError) as e:
            # backend not available or misconfigured
            recover_or_warn(e)
    else:
        # invalid parameters; do not call the backend
        validate_and_correct_inputs()

## `mingus.midi.fluidsynth.set_instrument` · *function*

## Summary:
Delegates a channel/program (and optional bank) change to the configured MIDI backend and returns whatever that backend call returns.

## Description:
This function is a thin wrapper around the module-global backend object's set_instrument method; it invokes midi.set_instrument(channel, midi_instr, bank) and returns its result unchanged.

Known callers within the codebase:
- No direct internal callers were discovered in the scanned repository metadata for this function. Typical callers are application-level code or higher-level MIDI utilities that want to request a program (instrument) change on a particular channel using the Fluidsynth backend.

Typical context / trigger:
- Called when a client needs to change the MIDI program/patch for a channel before or during playback (for example, while preparing a track or in response to a UI control). This function is intended to be part of the Fluidsynth backend's public API surface so callers can set instruments without interacting with backend internals.

Why this logic is extracted into a separate function:
- Provides a stable, backend-agnostic entry point in the fluidsynth module that forwards instrument-change requests to the currently-configured midi backend. This keeps higher-level code decoupled from the concrete backend implementation and centralizes backend access in one place.

## Args:
    channel (int-like)
        - Identifier of the MIDI channel to change.
        - Values convertible to int are accepted by most backends; this wrapper does not validate ranges. Typical MIDI channel ranges are 0..15 or 1..16 depending on calling conventions.
    midi_instr (int-like)
        - Program/instrument number to select for the channel.
        - Values convertible to int are accepted; typical valid range is 0..127 for General MIDI program numbers.
    bank (int-like, optional, default=0)
        - Bank number for the instrument (used by some synths to select larger instrument sets).
        - Values convertible to int are accepted. When unspecified, defaults to 0.

Interdependencies:
- The meaning and valid ranges of channel, midi_instr, and bank depend on the configured backend's semantics. This wrapper does not coerce or enforce backend-specific constraints beyond forwarding the arguments.

## Returns:
- Whatever the module-global midi.set_instrument(channel, midi_instr, bank) call returns.
- Because this function merely delegates, possible return values, semantics, and success/failure indicators are backend-specific. Callers that rely on specific return semantics should consult the backend implementation referenced by the module-global midi object.

## Raises:
    NameError
        - If the module-global name midi is not defined in the fluidsynth module namespace, a NameError will be raised when the function attempts to access midi.
    Any exception raised by midi.set_instrument(...)
        - Any exception (ValueError, TypeError, OSError, backend-specific exceptions, etc.) raised by the backend's set_instrument will propagate unchanged through this wrapper.

## Constraints:
Preconditions:
    - The module-global midi must be configured and expose a callable set_instrument(channel, midi_instr, bank).
    - The backend may require prior initialization (for example, loading a soundfont or starting audio output); callers should ensure the backend is initialized according to the backend's lifecycle before calling this function.
    - Arguments should be values the backend expects (convertible to int where appropriate); the wrapper does not perform range validation.

Postconditions:
    - The backend's set_instrument has been invoked with the supplied arguments.
    - No local state in the fluidsynth module is modified by this function beyond any effects the backend call itself produces.

## Side Effects:
    - Delegates side effects to the configured backend. Typical side effects of the underlying call may include:
        - Sending a MIDI program-change message to a synthesizer or virtual instrument.
        - Changing internal synth state (selected program on a channel).
        - Emitting I/O (USB/MIDI device writes) or interacting with native audio subsystems depending on backend implementation.
    - No file I/O or other I/O is performed directly by this wrapper; all effects come from the backend call.

## Control Flow:
flowchart TD
    A[Call set_instrument(channel, midi_instr, bank=0)] --> B{Is module-global midi defined?}
    B -- No --> C[Raise NameError when attempting to access midi]
    B -- Yes --> D[Call midi.set_instrument(channel, midi_instr, bank)]
    D --> E{Does backend raise?}
    E -- Yes --> F[Propagate backend exception to caller]
    E -- No --> G[Return backend's return value]

## Examples and usage notes:
- Typical usage pattern (conceptual):
    1. Ensure the fluidsynth backend is initialized and the module-global midi object is configured (for example, via the module's init or backend setup routines).
    2. Request an instrument change: set_instrument(channel=0, midi_instr=40, bank=0).
    3. Handle failures from backend calls (e.g., ValueError, TypeError, or backend-specific errors) and ensure any required cleanup if initialization was incomplete.

- Example guidance for robust callers:
    - Check or initialize the backend before calling this wrapper to avoid NameError or backend errors.
    - Surround calls with appropriate exception handling if your application must remain resilient to backend failures.

## `mingus.midi.fluidsynth.stop_everything` · *function*

## Summary:
Calls the configured MIDI adapter's global stop_everything method to request an immediate, global silence and returns the adapter's result.

## Description:
This function is a minimal delegation wrapper: it invokes midi.stop_everything() and returns whatever that call produces. In the repository snapshot for this module there are no recorded direct callers; typical application-level call sites include shutdown/cleanup logic, a user-facing "panic" / "all notes off" control, or error handlers that need to guarantee silence.

Why this is a separate function:
- It centralizes delegation to the runtime MIDI adapter behind a single, named entry point in the fluidsynth module. This keeps higher-level code independent of the concrete adapter binding and facilitates swapping or mocking the adapter for testing.

Important implementation note:
- The fluidsynth module's top-level imports do not define a symbol named midi. The global name midi must exist in this module's namespace at runtime (set by other initialization code or by test setup) and must expose a callable stop_everything attribute. The wrapper does not itself configure or import the adapter.

## Args:
- None.

## Returns:
- The return value of midi.stop_everything().
  - If the adapter follows common conventions, this will typically be None, but the wrapper makes no assumption: it returns whatever the adapter returns (could be None, a boolean status, or an adapter-defined object).
  - If the adapter's method raises an exception, that exception propagates (see Raises).

## Raises:
- NameError: if the module-level name midi is not defined when this function is called.
- AttributeError: if midi exists but has no attribute named stop_everything.
- TypeError: if midi.stop_everything exists but is not callable.
- Any exception raised by midi.stop_everything itself (I/O errors, backend-specific exceptions, or user-defined exceptions) will propagate unchanged to the caller.

## Constraints:
Preconditions:
- The caller (or module initialization) must ensure the module-level global midi refers to an object implementing a callable stop_everything method.
- Backend resources expected by the adapter (open MIDI device, running synth engine, etc.) should be in a valid state for a stop operation to succeed.

Postconditions:
- If the call returns normally, the adapter's stop_everything completed and performed its backend-defined effects (silencing voices, sending MIDI "all notes off", flushing internal state, etc.).
- If an exception was raised, no additional handling is performed by this wrapper and the exception propagates; side effects performed by the adapter before the exception may have already taken place.

## Side Effects:
- The wrapper itself performs no I/O and mutates no local state other than calling into the adapter.
- The underlying adapter call may perform extensive side effects: send MIDI messages, silence audio voices, call registered callbacks/listeners, or mutate global or process-level state. Those behaviors depend entirely on the bound adapter implementation.

## Control Flow:
flowchart TD
    Start --> CheckMidi["Is module-global 'midi' defined?"]
    CheckMidi -->|No| RaiseNameError["NameError raised"]
    CheckMidi -->|Yes| HasAttr["Does midi.stop_everything exist?"]
    HasAttr -->|No| RaiseAttrError["AttributeError raised"]
    HasAttr -->|Yes| CallableCheck["Is it callable?"]
    CallableCheck -->|No| RaiseTypeError["TypeError raised"]
    CallableCheck -->|Yes| CallAdapter["Call midi.stop_everything()"]
    CallAdapter -->|returns normally| ReturnValue["Return adapter result"]
    CallAdapter -->|raises exception| Propagate["Propagate adapter exception"]
    ReturnValue --> End["End"]
    Propagate --> End

## Examples (usage and testing guidance):
- Usage (prose): At application shutdown, call this wrapper to request a global stop of the currently configured MIDI adapter. Wrap the call if you need robust shutdown behavior:
  1. Try to call the function.
  2. If a NameError or AttributeError occurs, log a clear message indicating the adapter was not configured and continue other cleanup steps.
  3. If a backend-specific exception occurs, catch it to allow remaining subsystems to shut down gracefully.

- Testing (prose): For unit tests that exercise higher-level shutdown logic, set fluidsynth.midi to a test double (an object with a stop_everything method). The test double can:
  - Record that stop_everything was invoked.
  - Simulate successful completion by returning None.
  - Simulate failures by raising an exception to assert the caller's error-handling behavior.

Notes:
- Because this function is a thin delegating wrapper, the authoritative description of effects, performance characteristics, and return values resides in the implementation of the adapter assigned to midi.

## `mingus.midi.fluidsynth.modulation` · *function*

## Summary:
Forwards a modulation update to the lower-level MIDI backend and returns that backend's result.

## Description:
This function is a minimal wrapper that delegates the work to the module-level midi.modulation function and returns whatever value that function returns. It exists to provide a fluidsynth-facing API surface for changing modulation without duplicating backend logic.

Known callers within the repository snapshot:
    - No direct internal callers were found in the available project snapshot. This function is intended to be used by external application code, GUIs, or playback controllers that interact with the fluidsynth frontend.

Typical trigger/context:
    - Called when an application or UI wants to change the modulation (mod wheel) value on a specific MIDI channel during playback or live performance.

Why this function is separated:
    - Keeps the fluidsynth module's public API consistent and readable.
    - Encapsulates the delegation to the shared midi backend so higher-level code does not call midi.* functions directly.

Reference:
    - The exact semantics, validation rules, return values, and side effects are determined by midi.modulation. In this repository snapshot, the sequencer.modulation helper (if used by the backend) documents a common behavior mapping modulation to controller 1 and returning a boolean; consult the sequencer.modulation documentation for those details.

## Args:
    channel (int-like):
        - MIDI channel to apply modulation to.
        - No range checks are made here; allowed MIDI channel conventions are typically 1..16 but validation (if any) is performed by midi.modulation.
    value (int-like):
        - Controller value for modulation.
        - No range checks are performed here; backend code (e.g., a sequencer implementation) may require values in 0..128 (or 0..127) and will perform validation if applicable.

Notes on interdependencies:
    - channel and value are passed unchanged to midi.modulation. Any type casting, validation, or normalization occurs in the delegated function.

## Returns:
    - Returns the exact value returned by midi.modulation(channel, value).
    - Common/likely return (depends on backend): boolean indicating success (True) or validation failure (False) — for example, the Sequencer.modulation helper returns bool. Do not assume this type without consulting the specific midi backend implementation.

## Raises:
    - This wrapper does not raise exceptions itself.
    - Any exception raised by midi.modulation(channel, value) will propagate unchanged to the caller (no internal try/except).

## Constraints:
Preconditions:
    - The underlying midi backend (the object or module named midi) must be available and implement modulation(channel, value).
    - channel and value should be of numeric/int-like types appropriate for the backend.

Postconditions:
    - After return, no additional work is performed by this wrapper. Any side effects (sending MIDI, notifying listeners, mutating backend state) will already have been executed by midi.modulation if it returns successfully.

## Side Effects:
    - This function itself performs no I/O or state mutation beyond delegating to midi.modulation.
    - Any side effects originate in midi.modulation and may include:
        * Sending MIDI control-change messages to a synthesizer or sound backend.
        * Mutating backend/internal sequencer state.
        * Notifying listeners or triggering callbacks that may perform I/O.

## Control Flow:
flowchart TD
    Start[Start] --> CallBackend[Call midi.modulation(channel, value)]
    CallBackend -->|returns| ReturnResult[Return backend result to caller]
    CallBackend -->|raises exception| Propagate[Propagate exception to caller]
    ReturnResult --> End[End]
    Propagate --> End

## Examples:
    - Typical usage (assumes the fluidsynth module is imported and midi backend initialized):
        try:
            result = modulation(1, 64)
            if result is True:
                # modulation change accepted and processed by backend
                pass
            elif result is False:
                # backend rejected the values (validation failed)
                pass
            else:
                # backend returned a different type/value; handle accordingly
                pass
        except Exception as exc:
            # midi.modulation raised an error (e.g., backend not initialized)
            handle_error(exc)

    - Notes:
        * For precise validation rules and the meaning of True/False return values, consult the midi backend implementation (for example, sequencer.modulation describes a common behavior of mapping modulation to controller 1 and returning a boolean).

## `mingus.midi.fluidsynth.pan` · *function*

## Summary:
Forwards a stereo-pan control change to the configured MIDI backend and returns that backend's result.

## Description:
This module-level function is a tiny forwarding wrapper: it calls the pan method on a module-scoped midi backend object and returns whatever that backend returns. The function exists to expose a consistent fluidsynth-facing API surface while delegating validation, event dispatch, and side effects (MIDI I/O, listener notification) to the configured MIDI backend.

Known callers and lifecycle context:
- There are no recorded internal callers in this file. Typical external callers are:
    - UI components that let a user adjust channel panning
    - Automation or scripting code that programmatically sets pan during composition or playback
    - Playback logic or live-performance code that modifies channel CCs on the fly
- When the backend is an instance of mingus.midi.sequencer.Sequencer (or an API-compatible object), this corresponds to issuing MIDI Control Change number 10 (Pan) for the specified channel and value. In that implementation, Sequencer.pan validates the value and returns a boolean indicating acceptance.

Why this logic is in its own function:
- Provides a stable, fluidsynth-specific API to set channel pan without exposing or importing the backend directly across client code.
- Keeps backend dispatch centralized so the rest of the codebase can call fluidsynth.pan(...) regardless of which midi backend is configured.

## Args:
    channel (int or numeric)
        MIDI channel identifier to receive the pan control change. Typical channels are 1–16 but this function does not enforce that constraint — the backend handles or should handle channel validation.
    value (int or numeric)
        Pan controller value to apply for the channel. Typical MIDI pan values lie in the 0..128 inclusive range; this function does not validate or coerce the value — the backend determines allowed ranges, casting, and validation behavior.

Notes on interdependencies:
- There are no default values; both arguments are required and are forwarded unchanged to midi.pan(channel, value).
- Any type or range requirements are enforced by the backend; callers that require strict guarantees should validate before calling.

## Returns:
    The exact return value produced by the underlying midi.pan(channel, value) call.
    - Common case (e.g., when using mingus.midi.sequencer.Sequencer): bool
        - True: the control change was validated and processed (cc_event invoked and listeners notified).
        - False: the control change was rejected by validation (for example, value out-of-range).
    - If a different backend is configured, consult that backend's contract; this wrapper does not convert or interpret the backend return value.

## Raises:
    NameError
        If the module-level symbol midi is not defined in the fluidsynth module namespace, attempting to evaluate midi.pan raises a NameError.
    AttributeError
        If midi exists but has no attribute pan (or pan is not callable), accessing midi.pan or calling it will raise an AttributeError or TypeError.
    Any exception raised by the underlying midi.pan
        The function does not catch exceptions from the backend. Typical propagated exceptions include TypeError for invalid argument types and ValueError for invalid argument values, but backends may raise other exceptions.

## Constraints:
    Preconditions:
        - The fluidsynth module must have a module-level object named midi that exposes a callable pan attribute.
        - channel and value should be of types and ranges acceptable to the configured backend (commonly numeric).
    Postconditions:
        - If the function returns without raising: midi.pan(channel, value) was invoked and returned a value which is returned to the caller.
        - If the backend is a Sequencer and it returns True: a CC event (controller 10) was emitted and listeners were notified (listeners receive integer-casted payloads).

## Side Effects:
    - The function itself performs no I/O or global state mutation other than calling the backend.
    - Side effects (MIDI message emission, listener notifications, device I/O) are produced by the backend's pan implementation (for Sequencer, via cc_event and notify_listeners).
    - No files, network, stdout, or module-level state are modified by this wrapper beyond what the backend does.

## Control Flow:
flowchart TD
    A[Call fluidsynth.pan(channel, value)] --> B{Is 'midi' defined?}
    B -- no --> C[NameError raised]
    B -- yes --> D{Does midi have a callable pan?}
    D -- no --> E[AttributeError or TypeError raised]
    D -- yes --> F[Call midi.pan(channel, value)]
    F --> G{midi.pan returns or raises}
    G -- raises --> H[Exception propagates to caller]
    G -- returns --> I[Return backend's value to caller]

## Examples:
- Basic usage with error handling:
    try:
        result = pan(1, 64)  # delegates to backend's pan
    except NameError:
        # Backend not configured at module scope
        raise RuntimeError("MIDI backend not configured (module-level 'midi' is missing).")
    except AttributeError:
        # Backend misconfigured (missing pan method)
        raise RuntimeError("Configured MIDI backend does not implement pan(channel, value).")
    except Exception as exc:
        # Backend raised an error (e.g., TypeError for invalid types)
        raise

    # Handle backend-specific return values
    if isinstance(result, bool):
        if result:
            print("Pan change accepted and processed.")
        else:
            print("Pan change rejected by backend (likely validation failure).")
    else:
        print("Backend returned:", result)

- Defensive check to avoid NameError/AttributeError:
    midi_backend = globals().get('midi')
    if midi_backend is not None and hasattr(midi_backend, 'pan') and callable(midi_backend.pan):
        pan(2, 32)
    else:
        # Fallback: log, raise a clearer error, or no-op
        raise RuntimeError("MIDI backend with callable pan(channel, value) is required.")

## `mingus.midi.fluidsynth.main_volume` · *function*

## Summary:
Forwards a channel and volume change request to the core MIDI backend and returns its result.

## Description:
This function is a one-line wrapper that delegates the request to the package-level midi.main_volume function. It exists in the fluidsynth adapter module to provide a stable, backend-agnostic API surface matching other MIDI backend modules.

Known callers:
- External user code and higher-level playback / control logic that import this fluidsynth module and call main_volume to change a channel's master volume.
- No internal callers are mandated by this wrapper itself; it simply forwards to the underlying midi implementation.

Why extracted:
- Provides a consistent API (same function name and signature) across different MIDI backend modules (e.g., fluidsynth vs. other backends).
- Keeps module surface uniform so consumers can switch backends without changing call sites.

## Args:
    channel (any): Forwarded directly to midi.main_volume. Typical callers pass an int representing a MIDI channel (commonly 1..16), but this function does no validation itself.
    value (any): Forwarded directly to midi.main_volume. Typical callers pass an int volume value; the accepted range is determined by the underlying midi.main_volume implementation.

Interdependencies:
    - Both parameters are forwarded as-is; any casting or validation is the responsibility of midi.main_volume.

## Returns:
    The exact return value produced by midi.main_volume(channel, value). This wrapper does not transform the result.
    - Common patterns in this codebase: backends often return a boolean indicating success (True) or failure (False), but callers should consult the concrete midi implementation for precise semantics.

## Raises:
    Any exception raised by midi.main_volume will propagate through this wrapper unchanged.
    - No exceptions are raised explicitly by this function itself.

## Constraints:
Preconditions:
    - The package-level midi module must be importable and expose a callable attribute main_volume.
    - Callers should ensure channel and value are of the expected types/ranges required by the configured MIDI backend.

Postconditions:
    - If midi.main_volume returns normally, this function returns that same value.
    - If midi.main_volume raises, the exception bubbles up to the caller.

## Side Effects:
    - This function itself performs no I/O or state mutation beyond whatever the delegated midi.main_volume performs.
    - Any side effects (sending MIDI messages, mutating player state, notifying listeners) are entirely dependent on the underlying implementation.

## Control Flow:
flowchart TD
    Start --> CallBackend[midi.main_volume(channel, value)]
    CallBackend -->|returns value| ReturnResult[return that value]
    CallBackend -->|raises exception| Propagate[exception propagates to caller]

## Examples:
Typical usage (pseudocode, error handling left to caller):

- Simple call (assumes backend accepts ints and returns bool):
    result = main_volume(1, 100)
    if result is True:
        # volume change accepted
    elif result is False:
        # backend rejected the change (check backend docs)
    else:
        # handle other return types per backend

- With exception handling (if backend may raise on invalid input):
    try:
        retval = main_volume(2, 64)
    except Exception as e:
        # log or recover from backend error
        raise

