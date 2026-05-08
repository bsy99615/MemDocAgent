# `pyfluidsynth.py`

## `mingus.midi.pyfluidsynth.cfunc` · *function*

## Summary:
Returns a Python-callable ctypes function object bound to a C symbol in the module's loaded library, using the provided return type and per-parameter specifications.

## Description:
This function builds two lists from the supplied parameter descriptors and uses them to construct a CFUNCTYPE-based callable bound to a symbol looked up on the module-level library handle named `_fl`.

Steps performed (exactly as in source):
    1. Collects the ctypes type for each parameter from arg[1] into a list named `atypes`.
    2. Builds a sequence of per-parameter flag tuples as (arg[2], arg[0]) + arg[3:] and appends each to `aflags`.
    3. Calls CFUNCTYPE(result, *atypes) to produce a ctypes function type, then immediately instantiates it with the tuple (name, _fl) and tuple(aflags), returning the resulting callable.

Known callers (in the provided context):
    - None in the provided snippet. The caller set is not present in the single-function source given.

Why this is a separate helper:
    - Encapsulates the exact assembly of the signature types list and the per-parameter flag tuples needed for CFUNCTYPE binding; the function returns a ready-to-call, library-bound callable.

## Args:
    name (str or bytes)
        The symbol name to look up on the `_fl` library handle. This value is passed unchanged to the CFUNCTYPE instance during instantiation.
    result (ctypes type)
        The ctypes type object to use as the function return type (e.g., c_int, c_void_p). This is passed as the first argument to CFUNCTYPE.
    *args (sequence of indexable parameter descriptors)
        Each positional vararg must be an indexable sequence (tuple or list). For each parameter descriptor `arg`, the function performs these exact index accesses:
            - arg[1]: required — appended into `atypes` and becomes the ctypes type for this parameter in the function signature.
            - arg[2]: required — becomes the first element of the per-parameter flag tuple.
            - arg[0]: required — becomes the second element of the per-parameter flag tuple.
            - arg[3:]: optional — any additional elements (zero or more) are appended after (arg[2], arg[0]) in the per-parameter flag tuple.
        Therefore, each parameter descriptor must contain at least three elements (indexes 0, 1, and 2).

## Returns:
    callable
        The CFUNCTYPE-instantiated callable bound to the symbol `name` on the `_fl` library handle. It uses `result` as the return type and the collected `atypes` as the positional argument types.
        - If no parameter descriptors are provided, CFUNCTYPE(result) is created and the returned callable expects no arguments.
        - The returned object is a Python-callable that invokes the underlying C function when called.

## Raises:
    IndexError
        If any parameter descriptor has fewer than three elements, access to arg[1] or arg[2] will raise IndexError.
    NameError
        If the module-level name `_fl` is not defined when this function executes, the instantiation step that uses `_fl` will raise NameError.
    TypeError
        If `result` or any arg[1] is not a valid ctypes type object, CFUNCTYPE(...) may raise TypeError.
    Any exception raised by ctypes during CFUNCTYPE construction or during the instantiation call (for example ValueError or AttributeError) will propagate unchanged.

## Constraints:
    Preconditions:
        - The caller must ensure `_fl` exists in the module namespace and is a loaded ctypes library handle if symbol binding is required.
        - Each parameter descriptor must be indexable and contain at least three elements.
        - `result` and each arg[1] should be valid ctypes types.

    Postconditions:
        - Returns a callable that is bound to `_fl`'s `name` symbol and uses the declared ctypes signature.
        - The function does not mutate module-level state (it only reads `_fl`).

## Side Effects:
    - Reads the module-level `_fl` variable during the CFUNCTYPE instantiation step.
    - May trigger ctypes-driven symbol lookup and validation on the shared library; any errors from those operations propagate as exceptions.
    - Performs no file, network, or stdout I/O.

## Control Flow:
flowchart TD
    Start --> init_atypes_aflags
    init_atypes_aflags --> iterate_args
    iterate_args --> |has next arg| append_arg1_to_atypes
    append_arg1_to_atypes --> build_flag_tuple
    build_flag_tuple --> append_to_aflags
    append_to_aflags --> iterate_args
    iterate_args --> |no more args| construct_cfunctype
    construct_cfunctype --> instantiate_with_name__fl_and_aflags
    instantiate_with_name__fl_and_aflags --> return_callable
    return_callable --> End

## Examples:
    Minimal example (assumes a module-level `_fl` variable exists and exposes "c_symbol"):
        from ctypes import c_int, c_double

        # parameter descriptors: (tag, ctype, flag, *optional_flag_args)
        p1 = ("idx", c_int, 0)
        p2 = ("value", c_double, 0)

        # create a callable bound to `_fl`'s "c_symbol"
        fn = cfunc("c_symbol", c_int, p1, p2)

        # call the bound function (may raise ctypes errors if symbol/type mismatches)
        try:
            out = fn(1, 2.0)
        except IndexError:
            # parameter descriptor malformed
            raise
        except NameError:
            # _fl not defined in module
            raise
        except Exception:
            # other ctypes-related errors
            raise

## `mingus.midi.pyfluidsynth.fluid_synth_write_s16_stereo` · *function*

## Summary:
Allocates a buffer, calls the low-level renderer to write stereo 16-bit PCM samples into it using interleaved layout, and returns the samples as a 1-D NumPy array of dtype numpy.int16.

## Description:
This function prepares a raw byte buffer sized for 'len' audio frames (stereo, 16-bit), calls the C-level function fluid_synth_write_s16 to render audio into that buffer, and converts the buffer contents to a NumPy int16 array.

Key visible behavior from the implementation:
    - A ctypes buffer of size len * 4 bytes is allocated via create_string_buffer(len * 4).
    - The function fluid_synth_write_s16 is invoked with these exact arguments:
        fluid_synth_write_s16(synth, len, buf, 0, 2, buf, 1, 2)
      which passes the same buffer pointer twice with start offsets 0 and 1 and a stride/increment of 2 for each — the intent (as implemented here) is to have fluid_synth_write_s16 write interleaved stereo samples into 'buf'.
    - The entire buffer (buf[:]) is converted to a NumPy array of dtype numpy.int16 via numpy.fromstring and returned.

Known callers in the provided snapshot:
    - None found. Typical call sites are audio-rendering loops or playback code that request a fixed number of frames from a FluidSynth synthesizer.

Why this function exists:
    - Encapsulates buffer allocation and conversion to NumPy so callers receive a ready-to-use numpy.int16 array of interleaved stereo samples without repeating the boilerplate.

## Args:
    synth:
        - Type: opaque (passed through to fluid_synth_write_s16)
        - Notes: Must be a value acceptable to the underlying C function. The function does not validate or inspect the handle.
    len:
        - Type: int
        - Meaning: number of audio frames (samples per channel) to render.
        - Notes: This parameter shadows the builtin name 'len' in Python. It is used to compute the buffer size as len * 4 bytes.

## Returns:
    numpy.ndarray
        - dtype: numpy.int16
        - Shape/length: 1-D array whose length equals (len * 4) / 2 = len * 2 elements, i.e., two int16 values per frame (interleaved L,R).
        - Interpretation: samples are interleaved as [L0, R0, L1, R1, ..., L(n-1), R(n-1)] where n == len.

## Raises:
    NameError
        - If fluid_synth_write_s16 is not defined in the module namespace, the call will raise NameError.
    TypeError, ValueError, or other exceptions from ctypes.create_string_buffer
        - If 'len' is not an integer or is otherwise invalid for buffer sizing, create_string_buffer(len * 4) may raise a TypeError or ValueError.
    Any exception raised by fluid_synth_write_s16
        - If the underlying binding raises a Python exception (e.g., due to an internal binding error), it will propagate.

## Constraints:
Preconditions:
    - 'len' should be an integer representing frames and non-negative to make sense (the function does not explicitly check this).
    - 'synth' must be a valid handle for the C binding used by fluid_synth_write_s16.
Postconditions:
    - On successful return, a numpy.int16 1-D array is produced containing len * 2 elements representing interleaved stereo samples.
    - No module-level globals are modified by this function.

## Side Effects:
    - Allocates a ctypes string buffer of size len * 4 bytes.
    - Calls the external function fluid_synth_write_s16, which writes into that buffer.
    - Allocates and returns a NumPy array created from the buffer contents.
    - No file, network, or stdout/stderr I/O is performed in this function.

## Control Flow:
flowchart TD
    A[Start] --> B[Compute size = len * 4]
    B --> C[create_string_buffer(size)]
    C --> D[Call fluid_synth_write_s16(synth, len, buf, 0, 2, buf, 1, 2)]
    D --> E[numpy.fromstring(buf[:], dtype=numpy.int16)]
    E --> F[Return numpy.int16 1-D array]
    C -- If invalid len --> G[create_string_buffer raises TypeError/ValueError]
    D -- If fluid_synth_write_s16 undefined --> H[NameError raised]
    D -- If fluid_synth_write_s16 raises --> I[Propagate exception]

## Examples:
    # Render 512 frames (512 frames -> 1024 int16 samples interleaved)
    samples = fluid_synth_write_s16_stereo(synth, 512)
    # samples.dtype == numpy.int16
    # samples.size == 512 * 2
    stereo = samples.reshape(-1, 2)  # shape (512, 2)
    left_channel = stereo[:, 0]
    right_channel = stereo[:, 1]

    # Basic error handling for missing binding
    try:
        samples = fluid_synth_write_s16_stereo(synth, 256)
    except NameError:
        raise RuntimeError("fluid_synth_write_s16 binding is not available; ensure FluidSynth is initialized")

## `mingus.midi.pyfluidsynth.str_binary` · *function*

## Summary:
Converts a text/unicode string to a binary bytes object using the string's default encoding; returns non-text inputs unchanged.

## Description:
A tiny normalization helper used before passing string-like values to lower-level APIs (for example, ctypes calls or C bindings) that expect binary/bytes inputs. It centralizes the policy: only convert text (six.text_type) to bytes; do not alter already-binary or other non-text objects.

Known callers within the current code snapshot:
- No direct callers found in the provided memory snapshot. Typical use sites (in this module) are functions preparing file paths, soundfont names, or C API string arguments before calling ctypes-based functions that require bytes (e.g., when constructing c_char_p or calling C functions).

Why this is a separate function:
- Prevents duplication of the isinstance-and-encode pattern across the module.
- Makes the text→binary conversion policy explicit and easy to change (for example, to supply a specific encoding or error handling strategy).
- Ensures a single point for tests and documentation about how textual inputs are treated.

## Args:
    s (any): Value to normalize.
        - If s is an instance of six.text_type (unicode in Py2, str in Py3) it will be encoded.
        - Any other value (bytes, bytearray, None, numbers, custom objects, etc.) is returned unchanged.
        - Note: subclasses of six.text_type are treated as text and will be encoded; subclasses of bytes are not encoded.

## Returns:
    bytes | same-as-input:
        - If input is six.text_type:
            * In Python 3: returns a bytes object (result of s.encode(), default encoding 'utf-8').
            * In Python 2: returns a str object (which is the bytes type in Py2; result of s.encode(), default encoding 'ascii').
        - If input is not six.text_type: returns the original object reference unchanged (e.g., bytes, bytearray, None).
    Edge cases:
        - Passing a bytearray returns the same bytearray (not converted to bytes).
        - Passing an already-bytes object returns it as-is.

## Raises:
    UnicodeEncodeError: If s is six.text_type and s.encode() fails with the default encoding and 'strict' error handler, the exception propagates.
    Any exception raised by s.encode() (e.g., TypeError from a custom object overriding encode) is propagated to the caller.

## Constraints:
Preconditions:
    - None strict — the function accepts any Python object.
    - For the success of the text→bytes conversion, the text must be encodable with the string's default encoding (see Python version differences below).

Postconditions:
    - If input was six.text_type, the returned value is the bytes/str result of s.encode() using default encoding and strict error handling.
    - If input was not six.text_type, the returned value is the identical object that was passed in (identity preserved).

Python version notes (important):
    - Python 3: six.text_type is 'str'. str.encode() defaults to encoding='utf-8', errors='strict'. So textual inputs are encoded to UTF-8 bytes by default.
    - Python 2: six.text_type is 'unicode'. unicode.encode() defaults to encoding='ascii', errors='strict'. ASCII-only unicode will encode fine; non-ASCII characters will raise UnicodeEncodeError unless the caller supplies a unicode already encoded or the code is changed to specify a different encoding.

## Side Effects:
    - None visible: no I/O, no global state mutation, no external service calls.
    - The only observable effect is the return value; exceptions from encode() are propagated.

## Control Flow:
flowchart TD
    A[Start: receive s] --> B{isinstance(s, six.text_type)?}
    B -- Yes --> C[Call s.encode() with default encoding/errors]
    C --> D[Return encoded bytes (Py3) or str-bytes (Py2)]
    C -- encode raises exception --> E[Propagate exception (UnicodeEncodeError or others)]
    B -- No --> F[Return s unchanged]

## Examples:
- Typical success (Python 3):
    Input: s = "soundfont.sf2"           # str (text)
    Call:  result = str_binary(s)
    Result: result == b"soundfont.sf2"  # bytes

- Typical pass-through:
    Input: s = b"already-binary"         # bytes
    Call:  result = str_binary(s)
    Result: result is s                  # same bytes object returned

- Bytearray preserved (caller may convert if needed):
    Input: s = bytearray(b"data")
    Call:  result = str_binary(s)
    Result: result is s                  # still a bytearray

- None preserved:
    Input: s = None
    Call:  result = str_binary(s)
    Result: None

- Handling encoding failure (example pattern):
    try:
        result = str_binary(possibly_unicode)
    except UnicodeEncodeError:
        # handle or log the encoding error and decide an alternate encoding or abort
        # e.g., fallback = possibly_unicode.encode('utf-8', errors='replace')
        raise

- Cross-version note:
    In Python 2, non-ASCII unicode will raise UnicodeEncodeError when encoded with default 'ascii'. If a caller needs robust encoding across Python versions, they should perform explicit encoding before calling lower-level APIs or replace this helper to use a specified encoding (for example, s.encode('utf-8')).

## `mingus.midi.pyfluidsynth.Synth` · *class*

## Summary:
A thin, Python wrapper around FluidSynth C bindings exposing a synth instance, settings, and common MIDI/soundfont operations (load/unload soundfonts, select programs, send MIDI events, render audio). It manages the lifecycle of FluidSynth settings, the synth handle, and an optional audio driver.

## Description:
Use this class when you need a programmatic, low-level interface to a FluidSynth synthesizer from Python: create settings, instantiate a synth, start an audio driver (optionally), load soundfonts, send MIDI-like events (note on/off, CC, program change, pitch bend), and retrieve rendered PCM samples.

This class centralizes the C-binding calls and setting manipulations so callers can work with a concise, Pythonic API. It calls module-level FluidSynth binding functions (for example: new_fluid_settings, fluid_settings_setnum, new_fluid_synth, new_fluid_audio_driver, and deletion functions) and a string-normalization helper (str_binary). Those helpers must be available in the module namespace (defined in the same module or imported). If they are absent, invoking the corresponding methods will raise NameError.

Typical callers/factories:
- Application code that needs direct control over FluidSynth instances.
- Higher-level playback or MIDI-dispatching code that instantiates Synth, loads soundfonts, and issues MIDI events.

Responsibility boundary:
- This class is responsible only for creating and manipulating the FluidSynth settings, synth, and optional audio driver through C-bindings. It does not manage event queuing, threading, or provide a context manager — callers must manage concurrency and ensure delete() is called to free native resources.

## State:
Attributes
- settings
    - Type: opaque C binding handle (value returned by new_fluid_settings)
    - Valid range/values: a valid settings handle until delete() is called
    - Invariant: created in __init__; should not be used after delete()
- synth
    - Type: opaque C binding handle (value returned by new_fluid_synth)
    - Valid range/values: a valid synth handle until delete() is called
    - Invariant: created in __init__; should not be used after delete()
- audio_driver
    - Type: opaque C binding handle or None
    - Valid values: None (driver not started) or a driver handle returned by new_fluid_audio_driver
    - Invariant: None until start() creates a driver; delete() will release it if present

Constructor (__init__) parameters
- gain (float, default 0.2)
    - Passed to fluid_settings_setnum(st, b"synth.gain", gain)
    - No local validation; invalid types or out-of-range values may cause the underlying binding to raise.
- samplerate (int, default 44100)
    - Passed to fluid_settings_setnum(st, b"synth.sample-rate", samplerate)
    - No local validation; binding may raise for invalid values.

Class invariants
- After successful __init__, settings and synth are expected to be valid native handles. Methods operate on those handles.
- Once delete() has been called, the underlying handles are freed; subsequent method calls may raise exceptions or produce undefined behavior. Callers must avoid using the instance after delete().

## Lifecycle:
Creation:
- Instantiate with Synth(gain=..., samplerate=...). __init__:
    - Calls new_fluid_settings() to obtain a settings handle.
    - Sets synth.gain and synth.sample-rate via fluid_settings_setnum.
    - Sets synth.midi-channels to 256 via fluid_settings_setint.
    - Creates the synth handle via new_fluid_synth(st).
    - Initializes self.audio_driver = None.

Starting audio output:
- Call start(driver=None) to start and attach the native FluidSynth audio output driver to this Synth instance.
    - If driver is provided, it is normalized with str_binary(driver) (text -> bytes) and checked against known identifiers. The implementation asserts membership in the driver list; passing an unsupported driver will raise AssertionError.
    - The method sets the "audio.driver" setting (via fluid_settings_setstr) when a driver is specified, then calls new_fluid_audio_driver(self.settings, self.synth) to attach audio output.
    - After start(), audio_driver holds the native driver handle and system audio output will be routed to it (subject to the chosen driver and system configuration).

Usage / typical method order:
1. Create Synth(...)
2. Optionally call start(...) to open real-time audio output
3. Load soundfonts: sfload(filename)
4. Configure channels/presets: program_select, sfont_select, bank_select, program_change
5. Send MIDI events: noteon, noteoff, cc, pitch_bend
6. For non-realtime rendering: call get_samples(len=...) to retrieve rendered frames as a numpy.int16 array
7. Clean up: call delete() to release native resources

Destruction / cleanup:
- Call delete() to free native resources:
    - If audio_driver is not None, delete_fluid_audio_driver(self.audio_driver) is invoked.
    - delete_fluid_synth(self.synth) is invoked.
    - delete_fluid_settings(self.settings) is invoked.
- No automatic destructor or context manager is provided by the class; callers should ensure delete() runs (for example, in a finally block or a higher-level context manager).

## Method Map:
flowchart LR
    INIT[__init__(gain, samplerate)] --> START[start(driver=None)]
    START --> AUDIO[new_fluid_audio_driver(...)]
    INIT --> SF[sfload / sfunload]
    SF --> PROGRAM[program_select / sfont_select / bank_select]
    PROGRAM --> MIDI[noteon / noteoff / cc / program_change / pitch_bend]
    MIDI --> SAMPLES[get_samples(len)]
    ANY[any method] --> DELETE[delete()]
    DELETE --> CLEANUP[delete_fluid_audio_driver / delete_fluid_synth / delete_fluid_settings]

## Raises:
- NameError: If required module-level binding functions (e.g., new_fluid_settings, new_fluid_synth, fluid_synth_sfload, fluid_synth_write_s16_stereo) or helper str_binary are not present in the module namespace when a method that references them is called.
- AssertionError: start(driver) will raise AssertionError if a provided driver (after normalization via str_binary) is not one of the accepted byte-string identifiers.
- Binding-specific exceptions: Underlying C-binding wrappers may raise TypeError, ValueError, or other exceptions for invalid arguments; these propagate to callers.
- noteon/noteoff: These wrappers perform input checks and return False for invalid channel/key/velocity values instead of raising exceptions.

## Example:
# Pseudocode usage (assumes the FluidSynth bindings and str_binary are available)
synth = Synth(gain=0.3, samplerate=44100)     # create synth
synth.start()                                 # attach native audio driver (system audio output)
sfid = synth.sfload("example_soundfont.sf2")  # load a soundfont (filename str or bytes)
synth.program_select(0, sfid, 0, 0)           # set program on channel 0
synth.noteon(0, 60, 100)                      # play middle C on channel 0
# later...
synth.noteoff(0, 60)                          # stop the note
frames = synth.get_samples(1024)              # non-realtime rendering: returns numpy.int16 array of interleaved stereo samples
synth.delete()                                # free native resources

### `mingus.midi.pyfluidsynth.Synth.__init__` · *method*

## Summary:
Initializes a Synth instance by creating and configuring a FluidSynth settings object, creating a FluidSynth synthesizer using those settings, and setting the audio driver attribute to None.

## Description:
This constructor prepares the Synth object to be used for audio synthesis by:
- Creating a new FluidSynth settings object via new_fluid_settings().
- Setting numeric settings for synth gain and sample rate.
- Setting the integer setting for MIDI channel count.
- Creating a new FluidSynth synthesizer bound to those settings via new_fluid_synth().
- Initializing the audio_driver attribute to None.

Known callers and lifecycle context:
- No specific callers were discovered in the inspected code. Typical usage is direct instantiation by application code when a new synthesizer is required (for example, s = Synth()).
- It is invoked at object construction time and establishes the minimal native state required for later operations (loading soundfonts, starting audio drivers, sending MIDI events).

Why this logic is its own method (constructor):
- The logic is placed in __init__ so that a Synth instance is ready to use immediately after construction with consistent attributes (settings, synth, audio_driver).
- Grouping setup calls in the constructor centralizes resource allocation and default configuration and avoids requiring callers to perform additional initialization steps.

## Args:
    gain (float): Synth gain value passed to the underlying settings object via fluid_settings_setnum with key b"synth.gain". Defaults to 0.2. The method does not validate the numeric range; the argument is forwarded directly to the settings call.
    samplerate (int): Sample rate passed to the underlying settings object via fluid_settings_setnum with key b"synth.sample-rate". Defaults to 44100. The method does not validate that this is positive or conforms to sample-rate constraints; the value is forwarded directly.

## Returns:
    None: As a constructor, it returns None implicitly and initializes instance attributes. No explicit return value is produced.

## Raises:
    No exceptions are explicitly raised by this method in the source. However, any exception raised by the called wrapper functions (new_fluid_settings, fluid_settings_setnum, fluid_settings_setint, new_fluid_synth) will propagate out of __init__. Additionally, if those names are not defined in the module scope, a NameError will be raised when attempting to call them.

## State Changes:
Attributes READ:
    - None (the constructor does not read any pre-existing self.<attr> attributes)

Attributes WRITTEN:
    - self.settings: assigned the result of new_fluid_settings() (after setting numeric/int options on that settings object)
    - self.synth: assigned the result of new_fluid_synth(self.settings)
    - self.audio_driver: assigned None

## Constraints:
Preconditions:
    - The module must expose the wrapper functions new_fluid_settings, fluid_settings_setnum, fluid_settings_setint, and new_fluid_synth at call time (they must be importable/defined in module scope). The constructor does not perform feature detection or fallback logic.
    - The provided gain and samplerate arguments should be appropriate numeric types (float/int). No internal type coercion or validation is performed in this method.

Postconditions:
    - After successful return:
        * self.settings references the settings object created and configured via the fluid_settings_* calls.
        * The settings contains at least three configured keys:
            - b"synth.gain" set to the gain argument,
            - b"synth.sample-rate" set to the samplerate argument,
            - b"synth.midi-channels" set to 256.
        * self.synth references the synthesizer object created by new_fluid_synth(self.settings).
        * self.audio_driver is set to None.
    - If any underlying call returns an invalid/falsy value (for example, if new_fluid_synth returns NULL-equivalent), this method does not validate or replace those values — such invalid state may be visible on the instance.

## Side Effects:
    - Calls into native/C wrapper functions (new_fluid_settings, fluid_settings_setnum, fluid_settings_setint, new_fluid_synth). These calls may allocate native resources, configure internal state in a native library, or raise exceptions; none of that is handled here.
    - Mutates the newly constructed Synth instance by setting three attributes (settings, synth, audio_driver).
    - No file I/O or network I/O is performed directly in this method.

### `mingus.midi.pyfluidsynth.Synth.start` · *method*

## Summary:
Starts and attaches the native FluidSynth audio output driver to this Synth instance, updating the object's audio_driver attribute so the synth's audio is routed to the system audio backend.

## Description:
This method performs the final step of enabling audio output for a Synth previously initialized by Synth.__init__. It optionally sets the audio.driver setting (when a driver argument is provided) and then calls into the native FluidSynth wrapper to create/start an audio driver bound to this synth.

Known callers and lifecycle context:
- Intended to be called by application code after constructing a Synth and before issuing real-time playback calls (noteon/noteoff/cc/etc).
- Typical lifecycle: create Synth (which allocates settings and synth) -> optionally configure settings -> call start(driver=...) to open audio -> perform playback operations -> call delete() to free native resources.
- It is designed as a separate explicit step (not done inside __init__) because opening an audio device is an I/O/resource operation that callers may want to defer or configure beforehand.

Why this is a separate method:
- Starting the audio driver interacts with native audio backends and may fail for environmental reasons (missing backend, device busy). Keeping this out of __init__ enables callers to control when and how audio resources are allocated and to handle failures cleanly.

## Args:
    driver (str | bytes | None, optional): A driver name to set before opening the audio device.
        - If str/text is provided, it is converted via the module's str_binary helper to bytes (may raise UnicodeEncodeError).
        - Allowed exact byte values (after conversion). Matching is exact (including case and spaces):
            b"alsa"
            b"oss"
            b"jack"
            b"portaudio"
            b"sndmgr"
            b"coreaudio"
            b"Direct Sound"
            b"dsound"
            b"pulseaudio"
        - If driver is None (default), the method does not modify the audio.driver setting and the previously configured/default backend is used.

## Returns:
    None
    - The method does not return a value. Its observable result is that self.audio_driver is assigned to the handle returned by new_fluid_audio_driver.
    - Note: If the underlying native call returns None or a falsy handle, self.audio_driver will be set accordingly (callers should check if they require a truthy driver handle).

## Raises:
    AssertionError:
        - Raised if a non-None driver (after conversion with str_binary) is not exactly one of the allowed byte values. Note: assertions can be disabled when Python runs with optimization flags (python -O); see the "Important caveat" below.
    UnicodeEncodeError (or other exception from str_binary):
        - If converting a text driver name to bytes fails, that exception propagates.
    Any exception/ctypes error raised by fluid_settings_setstr or new_fluid_audio_driver:
        - Errors from the native FluidSynth wrappers (for example, failures to open the audio backend) propagate out of this method.

Important caveat about assert:
- The method uses an assert to validate driver membership. If Python is started with optimizations (python -O), assert statements are skipped and invalid driver values will not trigger AssertionError; they will be passed directly to fluid_settings_setstr and may then cause native errors or undefined behavior. If robust runtime validation is required, callers should validate the driver string prior to calling start.

## State Changes:
Attributes READ:
    - self.settings: read to set the "audio.driver" setting when driver is provided.
    - self.synth: read/passed to new_fluid_audio_driver to bind the synth to the audio driver.

Attributes WRITTEN:
    - self.audio_driver: assigned the handle returned by new_fluid_audio_driver(self.settings, self.synth).

## Constraints:
Preconditions:
    - self.settings and self.synth must be valid (typically created by Synth.__init__). Calling start on an incompletely initialized Synth may cause underlying API errors.
    - If providing a textual driver name, it must be encodable by str_binary (commonly UTF-8 on Python 3); otherwise encoding errors propagate.
    - The driver value (after conversion to bytes) should match one of the allowed values; otherwise an AssertionError will be raised unless assertions are disabled.

Postconditions:
    - On normal return (no exception), self.audio_driver holds the native audio-driver handle returned by new_fluid_audio_driver and the audio backend is expected to be active according to the native library's semantics.
    - If an exception occurs before assignment, self.audio_driver remains unchanged.
    - Calling start repeatedly will overwrite self.audio_driver with a newly-created handle without automatically freeing the previous one; callers must call delete() to avoid leaking native audio-driver resources.

## Side Effects:
    - Mutates the FluidSynth settings by calling fluid_settings_setstr(self.settings, b"audio.driver", driver) when driver is provided.
    - Calls new_fluid_audio_driver(self.settings, self.synth), which performs native I/O/resource allocation with the underlying FluidSynth library (opening audio streams, allocating OS/audio resources). Failures are environment-dependent.
    - No direct file I/O from this Python method, but native calls may interact with system audio devices; such interactions can block or fail depending on device availability and permissions.

## Usage notes and recommendations:
    - Prefer calling start only once per Synth instance or ensure you delete/free the previous audio_driver before starting again to prevent resource leaks.
    - If you need strict runtime validation of the driver argument regardless of interpreter flags, validate the driver string against the allowed list before calling start (do not rely on assert).
    - After start, use Synth.noteon/noteoff and other realtime methods to play sound; call Synth.delete() when finished to free native resources.
    - Because the method delegates to native wrappers, consult runtime logs or catch exceptions to diagnose backend-specific errors (missing backend libraries, permission issues, or device-in-use errors).

### `mingus.midi.pyfluidsynth.Synth.delete` · *method*

## Summary:
Performs cleanup of Fluidsynth-related native resources owned by the Synth object, releasing the audio driver (if present), the synth, and its settings; does not modify the Python-side attributes.

## Description:
- Known callers and context:
    - No internal callers were found in the module. This method is intended to be invoked by client code when the Synth instance is being torn down or when its native resources must be released (for example, at program exit or when replacing the synth).
    - Typical lifecycle stage: shutdown/cleanup step after start() or after using the Synth for playback/sound generation.

- Why this is a separate method:
    - Cleanup requires calling multiple low-level (ctypes-wrapped) delete/free functions in a specific sequence: audio driver (if any), then synth, then settings. Encapsulating that logic in one method centralizes resource-release behavior and avoids duplication across user code.

## Args:
    None

## Returns:
    None
    - The method has no explicit return statement; it implicitly returns None.

## Raises:
    - The method does not raise Python exceptions itself, but it calls ctypes-wrapped native functions:
        * Any exception or error thrown by delete_fluid_audio_driver, delete_fluid_synth, or delete_fluid_settings (for example, from ctypes or from invalid pointer use) will propagate to the caller.
        * If the underlying native code has undefined behavior (e.g., double-free or freeing an invalid pointer), that may crash the process; this method does no defensive checks beyond the audio_driver None check.

## State Changes:
- Attributes READ:
    - self.audio_driver
    - self.synth
    - self.settings
- Attributes WRITTEN:
    - None — the method does not assign to any self.<attr> fields. After calling delete, the Python attributes still reference the original values (typically opaque pointers), but the underlying native resources they pointed to have been released.

## Constraints:
- Preconditions:
    - The Synth object must have been initialized (Synth.__init__ sets self.settings and self.synth).
    - self.settings and self.synth are expected to be valid native handles; calling delete when they are missing or already freed may cause errors.
    - self.audio_driver may be None; the method checks for that before attempting to delete the audio driver.

- Postconditions:
    - If the calls succeed, the underlying native resources for the audio driver (if present), the synth, and the settings have been released via the corresponding delete_fluid_* functions.
    - The Python attributes self.audio_driver, self.synth, and self.settings remain unchanged (still reference the original handles), but those handles should be considered invalid/unsafe to use after this call.

## Side Effects:
    - Calls to native functions delete_fluid_audio_driver(self.audio_driver), delete_fluid_synth(self.synth), and delete_fluid_settings(self.settings) (ctypes calls into the Fluidsynth native library).
    - May close audio output or tear down audio-driver threads managed by the native library.
    - No file I/O or network I/O performed by this method itself, but native cleanup routines might perform OS-level resource release operations.

### `mingus.midi.pyfluidsynth.Synth.sfload` · *method*

## Summary:
Loads a SoundFont file into the underlying FluidSynth synth by converting the filename to binary and delegating to the C binding; returns the raw result from the underlying FluidSynth call and does not modify Python-side Synth attributes.

## Description:
A thin wrapper that normalizes the filename (ensures a bytes object when a text string is passed) and delegates the actual soundfont loading to the FluidSynth C function fluid_synth_sfload. Typical callsite: after constructing a Synth instance (so the internal synth handle exists) and before playing MIDI events — i.e., during initialization or setup of instrument resources.

Known callers and lifecycle stage:
- Called by client code that wants to load a .sf2 SoundFont into a Synth instance. No callers inside this module are present in the provided snapshot.
- Intended to be invoked after Synth.__init__ (which creates self.synth) and before generating audio or sending MIDI events that depend on the SoundFont.

Why this is a separate method:
- Centralizes the conversion of Python text filenames to the binary form expected by the underlying C API.
- Encapsulates the specific C binding call in one place so user code uses a clean high-level API (Synth.sfload) instead of repeatedly calling str_binary and the ctypes-bound function.

## Args:
    filename (str | bytes | any): Path or identifier of the SoundFont to load.
        - If a text string (six.text_type / str), it will be encoded using str_binary (module helper) before being passed to the C function.
        - If already bytes (or another non-text object), it is passed unchanged to the C binding.
    update_midi_preset (int, optional): Flag forwarded to the C API controlling whether MIDI presets are updated after loading.
        - Default: 0
        - Typical values are 0 or 1 (boolean-like), but no enforcement is performed in Python; the integer is forwarded directly.

## Returns:
    int | any: The raw value returned by the underlying C function fluid_synth_sfload.
        - The function does not interpret or convert this return value; callers should consult the FluidSynth API for semantic meaning (for example, success/failure codes or an sfont id).
        - Edge cases: if the C binding returns an error code or raises an exception, that behavior is propagated to the caller.

## Raises:
    UnicodeEncodeError: If filename is a text string that cannot be encoded by str_binary (for example, non-encodable characters given the encoding rules of str_binary), the exception from str_binary.encode() will propagate.
    AttributeError: If the Synth instance lacks a self.synth attribute (for example, if the instance was not initialized properly or attributes were removed), accessing self.synth will raise AttributeError.
    Any exception raised by the underlying C binding fluid_synth_sfload may propagate (e.g., TypeError if arguments are incompatible, OSError/ctypes errors if the native library is unavailable, or other runtime errors produced by the binding).

## State Changes:
Attributes READ:
    - self.synth: the C synth handle (pointer) is read and forwarded to the C binding.
Attributes WRITTEN:
    - None on the Python Synth object. The method does not assign to any self.* attributes.

## Constraints:
Preconditions:
    - self.synth must be a valid FluidSynth synth handle (set by Synth.__init__ via new_fluid_synth).
    - filename must be a path-like or string-like value acceptable to the underlying FluidSynth C function after conversion by str_binary.
    - The FluidSynth library must be loaded and the fluid_synth_sfload binding present.

Postconditions:
    - The method returns exactly what fluid_synth_sfload returns (no post-processing).
    - If fluid_synth_sfload succeeds (semantics defined by FluidSynth), the underlying synth state will reflect the loaded SoundFont (see FluidSynth documentation for precise behavior).
    - No Python-side Synth attributes are changed by this call.

## Side Effects:
    - Delegates to a native FluidSynth function which performs file I/O to read the SoundFont and mutates the native synth state (adds the SoundFont into the synth). These effects occur inside the C library, not as visible Python attribute changes.
    - No network I/O is performed by this method itself.
    - Exceptions from the native call or from encoding the filename may propagate to the caller.

### `mingus.midi.pyfluidsynth.Synth.sfunload` · *method*

## Summary:
Unloads a previously loaded SoundFont from the native FluidSynth synthesizer instance and returns the raw result produced by the underlying native call.

## Description:
This is a thin wrapper around the FluidSynth native function fluid_synth_sfunload. It delegates the unload operation to the native synth object stored on the Python Synth instance.

Known callers:
    - No internal callers are present in this module beyond external user code. Typical usage is:
        1. Call sfload(...) to load a SoundFont and obtain a soundfont id (sfid).
        2. Later call this method with that sfid to remove/unload the SoundFont from the synthesizer.

Lifecycle / pipeline stage:
    - Invoked when a user or application intends to free or remove a SoundFont previously loaded into the Synth instance (resource-management stage).

Why this is its own method:
    - Provides an explicit, discoverable Python-level API for unloading SoundFonts and mirrors the corresponding native FluidSynth API. Keeping the native delegation in its own method keeps the public Synth API consistent and avoids repeating the ctypes call site elsewhere.

## Args:
    sfid (int):
        - Identifier/handle for the SoundFont to unload.
        - Expected to be a soundfont id previously obtained from sfload(...).
    update_midi_preset (int, optional):
        - Controls whether MIDI presets are updated after unloading; default is 0.
        - The meaning and allowed values are determined by the underlying FluidSynth native API and are forwarded unchanged.

## Returns:
    int
        - The method returns whatever value the native function fluid_synth_sfunload returns.
        - The exact meaning of returned integers (success/failure codes or other values) is defined by the FluidSynth C API and is not interpreted or transformed by this wrapper.

## Raises:
    - This Python wrapper does not raise exceptions itself. Any errors or exceptional behavior must be handled by the caller and/or by the underlying native library.
    - Passing invalid Python types for arguments may cause a TypeError at the ctypes boundary or a different exception from the native layer; such behavior is a consequence of the ctypes call and not explicitly wrapped here.

## State Changes:
    Attributes READ:
        - self.synth (the native synthesizer handle is read and passed to the native function)
    Attributes WRITTEN:
        - None. This method does not modify any Python-visible attributes on self.

## Constraints:
    Preconditions:
        - self.synth must be a valid native synthesizer handle (it is set during Synth.__init__).
        - sfid should refer to a SoundFont currently known to the native synthesizer (typically obtained earlier from sfload).
    Postconditions:
        - No guarantees are made by this wrapper about Python-level state; the method returns the raw native result and may cause changes inside the native synthesizer (e.g., removal of the SoundFont) according to the FluidSynth implementation.

## Side Effects:
    - Calls into an external native library (FluidSynth) via ctypes.
    - May mutate internal/native state of the synthesizer (for example, removing the SoundFont and potentially updating MIDI presets depending on update_midi_preset). The exact side-effects are governed by the FluidSynth C library.

### `mingus.midi.pyfluidsynth.Synth.program_select` · *method*

## Summary:
Requests the underlying FluidSynth engine to assign a specific bank/preset (program) to a MIDI channel by forwarding the call to the native fluid_synth_program_select function using the synth handle stored on the Synth instance. This wrapper itself does not modify Python-level attributes.

## Description:
This is a thin forwarding method. The implementation calls:

    fluid_synth_program_select(self.synth, chan, sfid, bank, preset)

and returns that call's result unchanged. It provides a consistent, object-oriented API for program selection so callers do not need to call the native function directly.

Known callers and typical context:
- Called by client code after loading a SoundFont (for example, after calling Synth.sfload) and before sending note events, to ensure the desired preset is selected on a MIDI channel.
- Not used internally elsewhere in this module; it exists to expose FluidSynth's program-selection capability on the Synth object.

Why this is a separate method:
- Centralizes native synth interactions on the Synth object and matches other synth-control methods (note on/off, cc, etc.), simplifying the public API.

## Args:
    chan (int): MIDI channel index. Expected to be an integer. The Synth constructor configures "synth.midi-channels" to 256; channels are therefore commonly in the range 0..255 for this Synth instance.
    sfid (int): SoundFont identifier returned by Synth.sfload. Expected to be an integer that identifies a loaded SoundFont in the FluidSynth instance.
    bank (int): Bank number within the SoundFont to select. Expected to be an integer; this wrapper does not validate the range.
    preset (int): Program/preset number within the bank to select. Expected to be an integer; this wrapper does not validate the range.

## Returns:
    Any: The raw value returned by the underlying fluid_synth_program_select function (propagated as-is). Typically callers will receive a numeric status or result value from the FluidSynth API; consult FluidSynth documentation for exact meanings.

## Raises:
    - The method does not raise Python-level exceptions explicitly.
    - If self.synth is None/invalid or the native call cannot be performed, an exception from the binding layer (e.g., a TypeError or other runtime error) may be raised; this wrapper does not catch or translate such exceptions.

## State Changes:
    Attributes READ:
        self.synth
    Attributes WRITTEN:
        None (no Python attribute on self is modified)
    Native/external state:
        The underlying FluidSynth synth instance referenced by self.synth may be modified by the native call (for example, changing which program/preset is active on the specified channel). The exact native-side effects and audible results are determined by the FluidSynth engine.

## Constraints:
    Preconditions:
        - Synth.__init__ must have been called so self.synth is a valid native synth handle (the constructor creates the synth and sets midi-channels to 256).
        - sfid should refer to a SoundFont previously loaded into the synth (for example, a value returned by Synth.sfload).
        - Arguments should be integers; this wrapper performs no type or range validation.
    Postconditions:
        - An attempt is made to select the requested bank/preset on the given channel via the FluidSynth API.
        - The method returns the raw result from fluid_synth_program_select; no further Python-level guarantees about success codes are provided.

## Side Effects:
    - Calls the native FluidSynth function fluid_synth_program_select (exposed by this module) which may alter the synth's configuration and audible output.
    - No file or network I/O is performed by this wrapper and no Python attributes on the Synth instance are mutated.

## Usage example (illustrative):
    # Load a SoundFont, then assign bank 0, preset 0 to channel 0 and check result
    sfid = synth.sfload("example.sf2", update_midi_preset=1)
    status = synth.program_select(0, sfid, 0, 0)
    if status is None:
        # handle unexpected None from binding
        raise RuntimeError("program_select returned None")
    # For concrete success/failure codes, consult FluidSynth documentation for fluid_synth_program_select

### `mingus.midi.pyfluidsynth.Synth.noteon` · *method*

## Summary:
Start a note on the underlying FluidSynth engine after validating parameters; delegates to the FluidSynth C binding and does not modify Python-visible Synth attributes.

## Description:
This is a thin wrapper that performs defensive parameter checks and then calls the ctypes-bound function fluid_synth_noteon to trigger a note on the synth instance referenced by self.synth.

Known callers:
- No callers were found within the provided codebase. Typical callers are MIDI event handlers or playback routines which map NOTE ON events to synthesizer actions (for example, when processing incoming MIDI messages).

Why this is a separate method:
- Centralizes parameter validation for NOTE ON requests to avoid duplication across callers.
- Encapsulates the direct call to the C binding so tests and future changes to validation or the backend call are localized.

## Args:
    chan (numeric): MIDI channel index. The method checks only that chan >= 0; there is no upper bound check here. Synth.__init__ configures 256 MIDI channels, but the method does not enforce that limit.
    key (numeric): MIDI key (note number). Valid range according to this implementation: 0 through 128 inclusive. If key < 0 or key > 128 the method returns False and does not call the C API.
    vel (numeric): Note-on velocity. Valid range according to this implementation: 0 through 128 inclusive. If vel < 0 or vel > 128 the method returns False and does not call the C API.

Notes on types:
- The code performs numeric comparisons; callers should provide numeric types (typically int). If non-numeric values are passed, Python will raise a TypeError during the comparisons before the C call.

## Returns:
    - False (bool): returned immediately if any validation fails:
        * key < 0 or key > 128
        * chan < 0
        * vel < 0 or vel > 128
    - Otherwise: the raw return value from fluid_synth_noteon(self.synth, chan, key, vel). The documentation does not assume a specific type or meaning for that return value — it is whatever the ctypes binding exposes (commonly an int status code).

## Raises:
    - This wrapper does not explicitly raise exceptions. However:
        * Passing non-comparable/non-numeric arguments may raise TypeError during validation comparisons.
        * If the ctypes binding is misconfigured or the underlying C call fails in a way that propagates an exception, that exception will propagate; it is not caught here.

## State Changes:
Attributes READ:
    - self.synth

Attributes WRITTEN:
    - None (no assignments to self attributes in this method).

## Constraints:
Preconditions:
    - self.synth should be initialized (Synth.__init__ normally sets self.synth with new_fluid_synth). Calling noteon on an uninitialized Synth (e.g., before __init__ completes or after delete()) may cause the underlying call to fail.

Postconditions:
    - If validation fails, no call to the C binding is made and the method returns False.
    - If validation succeeds, the FluidSynth engine state (external to the Python object) will be changed by fluid_synth_noteon; the method returns that binding's result and Python-visible attributes remain unchanged.

## Side Effects:
    - Invokes the external C function fluid_synth_noteon via ctypes, which mutates the FluidSynth engine state (starts a sounding voice/note). This can lead to audible output depending on the configured audio driver.
    - No file, network, or direct Python-level I/O is performed by this method itself. Any I/O is performed by the underlying C library or audio driver.

## Example usage:
- Calling noteon(0, 60, 100) with a properly initialized Synth will validate the arguments and then ask FluidSynth to start middle C (MIDI key 60) on channel 0 with velocity 100; the method returns the underlying C binding result on success or False if a validation check fails.

### `mingus.midi.pyfluidsynth.Synth.noteoff` · *method*

## Summary:
Validate inputs and instruct the underlying native FluidSynth synth to stop a sounding note for the specified channel and key; returns False for invalid inputs or forwards the native binding's result.

## Description:
This method is the Synth wrapper for MIDI Note Off events. It performs simple, deterministic input validation on chan and key, and — only when validation passes — calls the external C binding fluid_synth_noteoff(self.synth, chan, key) to request the native FluidSynth engine to stop that note.

Known callers / calling contexts:
- No internal callers are present in this module (no references found). Typical external callers include:
  - MIDI event dispatchers or sequencers that translate NOTE_OFF messages into synth operations,
  - Application code that programmatically stops notes,
  - Playback controllers and voice managers during runtime audio playback.
- This method is invoked during playback/voice-management stages where an active note should be released/stopped.

Why this is a separate method:
- Encapsulates input validation (rejecting out-of-range values) and provides a stable public API for stopping notes without exposing the native binding.
- Mirrors the noteon method’s structure and keeps high-level API responsibilities separate from low-level native calls.

## Args:
    chan (int): MIDI channel index. Must be >= 0. There is no upper-bound check in this method.
    key (int): MIDI note/key number. Allowed integer range: 0 through 128 inclusive. Values outside this inclusive range cause the method to return False.

Notes on types:
    - The method expects integer-like values. It does not coerce types.
    - Passing non-numeric or otherwise non-comparable values (e.g., None, complex objects) will raise a Python TypeError at the point of comparison (key < 0 or chan < 0) before any native call.

## Returns:
    - False (bool): Returned immediately if validation fails (key < 0 or key > 128, or chan < 0). In this case the native binding is not invoked.
    - Otherwise: the raw return value from fluid_synth_noteoff(self.synth, chan, key). This wrapper does not interpret or transform that value; callers should consult the native FluidSynth binding documentation to interpret it.

## Raises:
    - TypeError: If chan or key are of types that cannot be ordered with integers (e.g., None or incompatible objects), the comparisons used for validation will raise TypeError.
    - Exceptions from the native binding: Any exceptions raised or propagated by fluid_synth_noteoff may surface to callers; this wrapper does not catch or translate those exceptions.

## State Changes:
    Attributes READ:
        self.synth — accessed and passed to the native binding.
    Attributes WRITTEN:
        None — this method does not modify attributes on self.

## Constraints:
    Preconditions:
        - self.synth must be an initialized/native FluidSynth synth handle (created e.g., by new_fluid_synth). Calling this method with an uninitialized or invalid self.synth may cause undefined behavior or errors from the native binding.
        - chan and key should be integers (or integer-like). chan must be >= 0. key must be in [0, 128].
    Postconditions:
        - If the method returns False, the native binding has not been called and no state on self has changed.
        - If the method returns the native binding's value, the native synth has been instructed to stop the specified note (behavior is subject to the native FluidSynth implementation).

## Side Effects:
    - Calls the external native function fluid_synth_noteoff(self.synth, chan, key), which affects the native FluidSynth engine (audio playback, voice allocation, internal synth state).
    - No file, network I/O, or mutations to objects outside self are performed by this wrapper itself; side effects beyond Python are those of the native library call.

### `mingus.midi.pyfluidsynth.Synth.pitch_bend` · *method*

## Summary:
Requests a pitch-bend change on the underlying FluidSynth instance by converting a centered pitch-bend value into the synth's 0-based scale and forwarding it to the native FluidSynth binding.

## Description:
Known callers:
    - No internal callers found in this module. Intended to be called by external MIDI event handlers or application code when applying a pitch-bend event to the synth.
Lifecycle/context:
    - Called at runtime after a Synth instance has been constructed (after __init__) and before the instance is deleted.
Why this is a separate method:
    - Encapsulates the conversion (val + 8192) required to translate a centered pitch-bend value into the absolute value that the native FluidSynth binding expects, and centralizes the native API call.

## Args:
    chan (int): MIDI channel index. The method passes this value directly to the native binding; the Synth.__init__ sets the synth's "midi-channels" setting to 256, so valid channel indices are typically in the range 0..255, but this method performs no channel-range validation itself.
    val (int): Centered pitch-bend value (signed). The method computes (val + 8192) and passes the result to the native binding. The method does not validate val; callers should provide an integer appropriate for the native API.

## Returns:
    The raw return value from the underlying fluid_synth_pitch_bend native binding. The wrapper does not interpret or transform this value; treat it as an opaque status/return code from the native API (commonly an integer).

## Raises:
    - AttributeError: If self.synth is not present (for example, if __init__ was not called or the synth was deleted), accessing self.synth will raise AttributeError before the native call.
    - Errors originating from the native FluidSynth binding or ctypes layer may propagate, but are not raised explicitly by this wrapper.

## State Changes:
    Attributes READ:
        - self.synth
    Attributes WRITTEN:
        - None (this method does not modify Python-level attributes on self)

## Constraints:
    Preconditions:
        - Synth.__init__ must have been called so that self.synth exists.
        - chan and val should be integers appropriate for the native FluidSynth API; this method does not perform type or range checks.
    Postconditions:
        - fluid_synth_pitch_bend is invoked with arguments (self.synth, chan, val + 8192).
        - The method returns the native binding's return value unchanged.

## Side Effects:
    - Calls a ctypes-bound native function (fluid_synth_pitch_bend) which may mutate the internal state of the native FluidSynth synthesizer referred to by self.synth and affect subsequent audio output.
    - No file I/O or persistent Python-level state changes are performed by this method.

### `mingus.midi.pyfluidsynth.Synth.cc` · *method*

## Summary:
Sends a MIDI Control Change (CC) message to the underlying FluidSynth engine by forwarding the channel, controller number, and value to the C binding; this affects the synth's internal parameter/state.

## Description:
This method is a thin wrapper around the C binding fluid_synth_cc and exists to provide a Python-friendly API on the Synth object. It does not perform validation of the controller number or value; it forwards the values directly to the FluidSynth engine.

Known callers:
    - No internal callers were found in this module's codebase. It is intended to be invoked by external code that receives or generates MIDI control-change events (for example, a MIDI event dispatcher, a UI slider that maps to CC, or other application logic that manipulates synth parameters at runtime).

Why this is a separate method:
    - It encapsulates a single, common operation (sending a control-change message) as part of the Synth object's public API. Keeping this as a dedicated method centralizes access to the fluid_synth_cc binding, avoids duplicating the C-call in user code, and matches the other MIDI action wrappers (noteon, noteoff, pitch_bend, etc.) for a consistent interface.

## Args:
    chan (int): MIDI channel number. Commonly 0–15 for standard MIDI but the underlying synth may accept a wider range; the method does not validate the channel value.
    ctrl (int): Controller number (controller/CC index). Typical MIDI range is 0–127; the method forwards the value without range checking.
    val (int): Controller value / parameter. Typical MIDI range is 0–127; the method forwards the value without range checking.

## Returns:
    The raw return value from the underlying C binding fluid_synth_cc. The method does not inspect or reinterpret this value; callers should consult the FluidSynth C API for exact semantics. In code terms, the returned value is whatever fluid_synth_cc(self.synth, chan, ctrl, val) returns (commonly an integer or boolean-like status code depending on the binding).

## Raises:
    This Python wrapper does not explicitly raise exceptions. However, if self.synth is not a valid C synth pointer (for example, if the synth was not initialized or was already freed by delete()), calling into the C binding may cause a segfault or cause the interpreter to propagate a ctypes-related exception. No Python-level validation or specific exceptions are raised by this method itself.

## State Changes:
    Attributes READ:
        self.synth
    Attributes WRITTEN:
        None (this method does not assign or mutate Python attributes on self)

## Constraints:
    Preconditions:
        - self.synth must be initialized and still valid (set in Synth.__init__ via new_fluid_synth). If delete() has been called, self.synth may no longer be valid and calling cc can crash or behave unpredictably.
        - chan, ctrl, and val should be integers; the method performs no type coercion or validation beyond what ctypes will accept when calling the C binding.

    Postconditions:
        - The FluidSynth engine has been asked to process a control-change message with the provided parameters. The method returns immediately with the underlying binding's return value; no additional guarantees about the synth's internal state beyond the effect of processing the CC are provided by this wrapper.

## Side Effects:
    - Calls the external C function fluid_synth_cc through ctypes, which mutates the FluidSynth internal state (affecting ongoing or future sound generation).
    - May indirectly affect audio output (for example, changing filter cutoff, modulation, or other synth parameters) depending on which controller and value are sent.
    - Potential for low-level errors (segfaults or ctypes exceptions) if self.synth is an invalid pointer.

### `mingus.midi.pyfluidsynth.Synth.program_change` · *method*

## Summary:
Change the instrument (program) assigned to a MIDI channel on the synth by delegating to the underlying FluidSynth C API; this mutates the synth's internal channel-to-program mapping.

## Description:
This method is a thin wrapper that forwards the request to the underlying fluid_synth_program_change C function, using the Synth instance's native synth handle (self.synth).

Known callers and typical usage:
- No internal callers are recorded in the local class listing. Typical callers are:
    - MIDI message handling code that receives a Program Change message and applies it to the synth.
    - User code that wishes to switch instruments during playback or setup.
- Lifecycle stage: typically invoked during playback or configuration phases when an application needs to change the instrument assigned to a MIDI channel.

Why this is its own method:
- Provides a concise, Python-level API that mirrors FluidSynth functionality and keeps the Synth wrapper consistent (other FluidSynth operations are exposed similarly).
- Encapsulates access to the synth handle (self.synth) in a single place rather than requiring callers to call the ctypes binding directly.

## Args:
    chan (int): MIDI channel index to change. The Synth instance initializes FluidSynth with synth.midi-channels set to 256 by default, so valid channel indexes are typically in the range 0 <= chan < 256. This method does not perform explicit range validation itself.
    prg (int): Program (instrument) number to set on the channel. Typical General MIDI program numbers are in the range 0..127; this method does not enforce that range.

## Returns:
    The exact return value is the raw value returned by the underlying fluid_synth_program_change call. The wrapper does not transform or interpret that return value; callers should consult the FluidSynth documentation or treat the return as an opaque status code (commonly used as a success/failure indicator).

## Raises:
    This wrapper does not raise Python exceptions itself. If self.synth is not a valid synth handle (for example, if the synth was deleted externally), calling into the underlying C library may trigger low-level errors; such failures are not caught or converted by this method.

## State Changes:
    Attributes READ:
        self.synth
    Attributes WRITTEN:
        None on the Python object (no self.<attr> is modified). The underlying FluidSynth synth object pointed to by self.synth is mutated (its channel program mapping is updated).

## Constraints:
    Preconditions:
        - self.synth must be initialized (Synth.__init__ sets self.synth via new_fluid_synth). Calling this method after delete() has been called may result in undefined behavior.
        - chan and prg should be integers; non-integer types will be forwarded to the ctypes call and may cause a TypeError from ctypes or undefined behavior at the C level.
    Postconditions:
        - If the underlying call reports success (as encoded in its return value), the FluidSynth synth's program for the specified channel will have been changed. The method itself guarantees only that it returns the underlying call's return value.

## Side Effects:
    - Calls the external FluidSynth C API (fluid_synth_program_change) via the stored synth handle; this mutates state in the external synth object.
    - No file I/O or other Python-level I/O is performed.
    - No Python-level attributes of the Synth instance are modified by this method.

### `mingus.midi.pyfluidsynth.Synth.bank_select` · *method*

## Summary:
Selects the bank for a MIDI channel on the underlying FluidSynth synth by delegating to the native binding and returning that call's result. This mutates the native synth's channel bank state but does not change any Python attributes on the Synth object.

## Description:
This is a one-line wrapper around the FluidSynth C API binding fluid_synth_bank_select so callers can perform bank selection via the Synth object API rather than calling the ctypes binding directly.

Known callers and context:
- No internal callers were found in the module; this method is intended for external user code that controls MIDI channel configuration during setup or at playback time.
- Typical usage: after constructing a Synth (Synth.__init__) and before or while sending MIDI events, an application may call this to switch the bank associated with a channel.

Why this is a separate method:
- Provides a consistent, object-oriented API for FluidSynth operations (matching other Synth methods such as noteon, program_select).
- Encapsulates the native binding access and keeps client code free of direct ctypes calls.

## Args:
    chan (int):
        MIDI channel index. Must be an integer. The Synth instance is configured with a number of channels (default 256), so valid channel indices are typically in 0..(n-1); this method does not enforce that upper bound.
    bank (int):
        Bank number to select. Must be an integer. No additional validation (range, sign) is performed by this method.

## Returns:
    int or ctypes-compatible integer:
        The return value is the direct result of the underlying fluid_synth_bank_select binding. Exact semantics (meaning of numeric codes) depend on the FluidSynth C API and the ctypes binding; this method does not translate or interpret the value. Callers should consult the FluidSynth documentation or the binding initialisation to understand success/error codes.

## Raises:
    AttributeError:
        If the Synth instance does not have a synth attribute (e.g., if the instance is malformed or the attribute was removed), accessing self.synth will raise AttributeError.
    NameError:
        If the module-level binding symbol fluid_synth_bank_select is not defined (binding failed to load), attempting to call it will raise NameError at runtime.
    TypeError (or ctypes error):
        If chan or bank are of types that the ctypes binding cannot coerce to the expected C integer types, a TypeError or a ctypes-related exception may be raised by the binding.
    Native-level failures:
        If the native synth handle is invalid (for example, after calling delete on the synth), the call may result in undefined behavior at the C level (including crashes). This method does not guard against that.

## State Changes:
    Attributes READ:
        self.synth
    Attributes WRITTEN:
        None (no Python attribute on self is modified)
    Native (external) state:
        The native FluidSynth synth object referenced by self.synth is mutated to reflect the bank selection for the specified channel (affecting subsequent MIDI program/bank behavior and audio output).

## Constraints:
    Preconditions:
        - self.synth must reference a valid, initialized FluidSynth synth object (Synth.__init__ or equivalent).
        - chan and bank should be integer-compatible; callers are responsible for ensuring values are within desired ranges.
    Postconditions:
        - If the underlying C call succeeds, the native synth's channel bank will be set to the requested bank.
        - The method returns the raw status/result from the underlying binding with no additional guarantees.

## Side Effects:
    - Invokes the native FluidSynth binding via ctypes, which mutates native synth state (no file or network I/O).
    - If the native synth handle is invalid, the call may cause native-level errors (segfaults); the method performs no safety checks to prevent those.

## Example:
    # Typical usage pattern
    s = Synth()                     # creates self.synth via new_fluid_synth(...)
    s.sfload("example.sf2")         # load a soundfont (optional)
    # Select bank 0 on MIDI channel 0
    result = s.bank_select(0, 0)
    # Check result according to the FluidSynth binding's documented return codes
    if result != 0:
        # handle error based on binding/docs
        pass

### `mingus.midi.pyfluidsynth.Synth.sfont_select` · *method*

## Summary:
Selects which loaded SoundFont (sfont) a given MIDI channel will use by delegating the selection to the FluidSynth C library; changes the native synth's channel-to-sfont mapping without modifying Python-level attributes.

## Description:
This is a minimal wrapper that forwards the provided MIDI channel and SoundFont identifier to the FluidSynth C binding (fluid_synth_sfont_select). It is intended to be called during synth setup or instrument configuration — after creating a Synth instance (Synth.__init__) and after loading one or more SoundFonts via Synth.sfload. The method is separated into its own wrapper to maintain a consistent, high-level Python API over the ctypes-based FluidSynth bindings and to keep direct native calls centralized.

Known callers and usage stage:
- There are no higher-level call sites inside this module that further wrap this function; it is intended for application-level code that configures which SoundFont each MIDI channel should use.
- Typical lifecycle: create Synth -> load SoundFont(s) via sfload (which returns an sfid) -> call sfont_select(chan, sfid) to assign that soundfont to a channel -> send MIDI events (noteon/noteoff/etc).

Why this is a separate method:
- Keeps the thin ctypes boundary consistent and discoverable on the Synth object.
- Matches the existing wrapper pattern for other FluidSynth operations (sfload, program_select, etc.), making the API ergonomic for developers using the Synth class.

## Args:
    chan (int):
        MIDI channel index to configure. Expected to be a non-negative integer. By default Synth.__init__ configures 256 MIDI channels, so valid channel indices are typically 0 through 255 inclusive. This method does not perform range checking itself.
    sfid (int):
        SoundFont identifier returned by Synth.sfload when loading a .sf2 file. Must be an integer previously obtained from sfload; the method forwards the identifier directly to the native binding.

## Returns:
    int:
        The integer result produced by the underlying FluidSynth binding call. This wrapper does not interpret or convert the value; callers should consult the FluidSynth API documentation for the semantic meaning of specific return codes. Treat the returned integer as opaque status information from the native library.

## Raises:
    - This wrapper does not explicitly raise Python exceptions. If invalid Python types are passed (e.g., non-integers), ctypes may raise TypeError or raise errors when calling the native function — these originate from the ctypes/native layer, not from the wrapper.
    - Calling this method when self.synth is not a valid native synth handle (for example, before __init__ completes or after delete() has been called) results in undefined behavior; any errors produced are those of the native library and ctypes.

## State Changes:
    Attributes READ:
        self.synth
            The native synth handle read and passed into the C function.
    Attributes WRITTEN:
        None (no Python attributes of the Synth object are changed).
    Native state mutation:
        The underlying FluidSynth synth object is mutated: the channel-to-sfont mapping inside the native synth is changed as a result of the call.

## Constraints:
    Preconditions:
        - The Synth instance must be initialized (self.synth created by Synth.__init__).
        - The provided sfid must have been obtained from a prior call to Synth.sfload and should still be valid (i.e., not unloaded via sfunload).
        - The caller should ensure chan is within the intended MIDI channel range for the synth (default range 0–255); this method does not validate the range.
    Postconditions:
        - If the native call reports success, the native synth will use the requested SoundFont for the specified channel.
        - The method returns the native binding's integer status code; no Python-level state is otherwise modified.

## Side Effects:
    - Invokes a native FluidSynth function via ctypes (fluid_synth_sfont_select), which mutates the native synth state.
    - No file I/O, network I/O, or mutation of other Python objects occurs within this wrapper itself.

## When to use (practical guidance):
    1. Create a Synth instance: this initializes self.synth and default channel count.
    2. Load a SoundFont via Synth.sfload(filename) to obtain an sfid.
    3. Call sfont_select(chan, sfid) to assign that SoundFont to the desired MIDI channel.
    4. Begin sending MIDI events (noteon/noteoff) on that channel.

Example (prose):
    After calling sfload("example.sf2") and receiving an sfid, use sfont_select(0, sfid) to make channel 0 play sounds from that SoundFont. If you later unload the SoundFont with sfunload(sfid), the sfid becomes invalid and further calls that reference it will rely on FluidSynth's behavior for invalid identifiers.

### `mingus.midi.pyfluidsynth.Synth.program_reset` · *method*

## Summary:
Invoke the underlying FluidSynth C binding to perform a "program reset" operation on the synthesizer handle and return the binding's result.

## Description:
This method is a thin wrapper that forwards the Synth object's internal synth handle to the low-level fluid_synth_program_reset C binding and returns whatever that binding returns.

Known callers and usage context:
    - No callers were found in the provided code snapshot.
    - Typical use: called by client code that needs to request a program/instrument reset on the FluidSynth engine (for example, after loading/unloading soundfonts or before starting a new playback session). The exact semantics of "program reset" are determined by the underlying FluidSynth binding.

Why this is a separate method:
    - Encapsulates the C binding call behind a simple, high-level method on the Synth object, consistent with other convenience wrappers in this class (e.g., noteon, noteoff, sfload). Keeps the public Synth API small and uniform and centralizes access to the synth handle.

## Args:
    None.

## Returns:
    The exact value returned by the fluid_synth_program_reset C binding when called with the synth handle (i.e., fluid_synth_program_reset(self.synth)).
    - Type: opaque — typically a numeric status code in low-level bindings (often an int), but this method does not inspect or convert it.
    - Edge cases: If the binding itself returns an error code, that code is returned unchanged.

## Raises:
    - NameError: If fluid_synth_program_reset is not defined in the module namespace (i.e., the low-level binding was not loaded).
    - AttributeError: If the Synth instance does not have a 'synth' attribute (e.g., if __init__ was not called).
    - Any exception raised by the underlying C binding or ctypes layer (for example, TypeError/ValueError if the synth handle is invalid for the binding) will propagate unchanged.

## State Changes:
    Attributes READ:
        - self.synth
    Attributes WRITTEN:
        - None within the Python Synth object (this method does not assign to any self.<attr>).

Note: although no Python attributes are modified, the underlying C synth object referenced by self.synth may be mutated by the call (this is an external effect).

## Constraints:
    Preconditions:
        - self.synth must hold a valid handle/object acceptable to the fluid_synth_program_reset C binding. In the provided class this is normally set in Synth.__init__ via new_fluid_synth(self.settings).
    Postconditions:
        - The method returns immediately with the raw result from fluid_synth_program_reset.
        - No Python-level attributes of the Synth instance are changed by this method.

## Side Effects:
    - Calls the external C binding fluid_synth_program_reset(self.synth); that call may mutate internal state of the C-level synthesizer (e.g., program/patch assignments) or trigger other side effects inside FluidSynth.
    - No file, network, or standard I/O is performed by this method itself.

### `mingus.midi.pyfluidsynth.Synth.system_reset` · *method*

## Summary:
Calls the underlying FluidSynth C API to perform a system-level reset on the synthesizer and returns the raw status value produced by that call.

## Description:
This method is a thin Python wrapper around the ctypes binding fluid_synth_system_reset. It invokes the C function with the Synth instance's internal synth handle (self.synth) and returns whatever value the C function returns.

Known callers:
- No internal callers within this module/class; the method is intended to be called by external client code that uses the Synth object when a full synth reset is required (e.g., between patches or when reinitializing state).
- Typical lifecycle placement: called at runtime after a Synth has been constructed (Synth.__init__) and before/after audio operations or soundfont changes when an application needs to reinitialize or clear synthesizer state.

Why this is a separate method:
- The class provides many one-line wrappers around FluidSynth C functions (e.g., noteon, noteoff, sfload). system_reset follows the same wrapper pattern to expose the equivalent C operation to Python users without inlining C-binding calls throughout client code.

## Args:
    None

## Returns:
    int (or int-like): The raw return value produced by fluid_synth_system_reset(self.synth). The method makes no interpretation of this value — it simply returns it to the caller.

## Raises:
    None explicitly raised by this Python wrapper. (If the internal synth handle is invalid or the ctypes binding is unavailable/misconfigured, runtime errors from the ctypes call may occur; those originate from the underlying binding and are not raised directly by this wrapper.)

## State Changes:
Attributes READ:
    self.synth

Attributes WRITTEN:
    (none) — this method does not assign to any self.<attr> fields in Python.

## Constraints:
Preconditions:
    - The Synth instance must have been initialized so that self.synth holds the C synth handle created by new_fluid_synth (Synth.__init__ performs this assignment).
    - The module-level ctypes binding fluid_synth_system_reset must exist and be callable.

Postconditions:
    - The method returns the exact numeric value returned by the underlying fluid_synth_system_reset call.
    - The underlying FluidSynth C library may modify internal C-level synth state as a result of the call (the wrapper does not document or enforce specific C-side state changes).

## Side Effects:
    - Invokes an external C function via ctypes (fluid_synth_system_reset), which may mutate the internal C synth state and thereby affect subsequent audio generation. No Python-level I/O or attribute mutations are performed by this method.

### `mingus.midi.pyfluidsynth.Synth.get_samples` · *method*

## Summary:
Returns interleaved stereo 16-bit PCM samples for the synthesizer as a 1-D NumPy int16 array, leaving the Synth object's Python attributes unchanged.

## Description:
This method is a thin convenience wrapper that requests the C binding fluid_synth_write_s16_stereo to render a specified number of audio frames from the underlying FluidSynth synthesizer and returns the result as a NumPy array.

Known callers / call contexts:
- Typically invoked by an audio-rendering or playback loop that pulls a fixed number of frames from the Synth to send to an audio device or to write to disk.
- May be called after Synth.start() has been called (or even without the audio driver) whenever a caller needs raw PCM samples.
- No callers are defined in the local snapshot; common use is in user code that drives synthesis/frame rendering.

Why this is a separate method:
- Encapsulates buffer allocation, the exact calling convention for the C binding, and conversion to a NumPy array so callers receive ready-to-use int16 samples without duplicating boilerplate and pointer/ctypes logic.

## Args:
    len (int, optional):
        Number of audio frames to render (frames == samples per channel). Defaults to 1024.
        - Allowed values: non-negative integers (0 is allowed; results in an empty array).
        - Notes: This parameter shadows the builtin name 'len'. It is used to compute the internal buffer size as len * 4 bytes (2 bytes per sample × 2 channels).

## Returns:
    numpy.ndarray
        - dtype: numpy.int16
        - Shape/length: 1‑D array of length (len * 2) elements (two int16 values per frame, interleaved).
        - Interpretation: Interleaved stereo samples ordered as [L0, R0, L1, R1, ..., L(n-1), R(n-1)] where n == len.
        - Edge cases: If len == 0, returns an empty numpy.int16 array. If the underlying call fails, an exception is raised instead of returning.

## Raises:
    NameError
        - If the module-level binding fluid_synth_write_s16_stereo is not defined in the runtime environment.
    TypeError or ValueError
        - If 'len' is not an integer or is otherwise invalid for buffer allocation (ctypes.create_string_buffer may raise these).
    Any exception propagated from fluid_synth_write_s16_stereo
        - If the underlying C-level renderer or binding raises an exception, it will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.synth (read to pass to the C binding)
    Attributes WRITTEN:
        - None (no attributes on self are modified by this method)
    Note:
        - Although no Python attributes are written, the underlying C library call may mutate internal synthesizer state (voice envelopes, internal time, etc.). Those mutations occur inside the C synth handle and are not reflected as changes to Python attributes on self.

## Constraints:
    Preconditions:
        - self.synth must be a valid synth handle acceptable to the underlying binding.
        - 'len' must be an integer >= 0 (the method does not explicitly validate this; invalid values will raise when allocating or when the C binding is called).
    Postconditions:
        - On successful return, a numpy.int16 1-D array containing len * 2 interleaved samples is returned.
        - The Synth object's Python attributes remain unchanged.

## Side Effects:
    - Allocates a temporary ctypes byte buffer of size len * 4 bytes.
    - Calls the external C binding fluid_synth_write_s16_stereo(self.synth, len), which writes PCM data into the buffer.
    - Allocates and returns a NumPy array created from the buffer contents.
    - No file/network I/O or stdout/stderr output is performed by this method.

## Example:
    # Render 512 frames (512 frames -> 1024 int16 samples interleaved)
    samples = synth.get_samples(512)
    # samples.dtype == numpy.int16
    # samples.size == 512 * 2
    stereo = samples.reshape(-1, 2)  # shape (512, 2)
    left = stereo[:, 0]
    right = stereo[:, 1]

## `mingus.midi.pyfluidsynth.raw_audio_string` · *function*

## Summary:
Converts an array-like of numeric audio samples into a raw bytes sequence by casting the input to signed 16-bit integers and returning the result of the array's tostring() method.

## Description:
This helper prepares sample data for low-level audio consumers by performing a direct cast to numpy.int16 and returning the array's raw byte buffer. It is deliberately minimal: it only changes the element dtype and extracts the underlying bytes representation; it does not perform scaling, clipping, channel interleaving, endianness conversion, or write any files.

Known callers within the repository:
- No direct call sites were present in the provided snapshot. Typical callers (in audio output, synthesis, or file-writing code) would invoke this function immediately before passing PCM data to a native audio API, a soundfont synthesizer, or a raw data writer.

Responsibility boundary:
- Sole responsibility: convert sample containers into the in-memory int16 byte representation required by downstream native APIs.
- Upstream responsibilities: scaling/clipping, ensuring the correct sample layout (mono/stereo interleaving), sample-rate conversion, and explicit byte-order handling if required.

## Args:
    data (array-like):
        Any object that implements astype(dtype) and whose astype(numpy.int16) result implements tostring().
        - Expected content: numeric audio sample values. The function does not validate ranges.
        - Allowed input forms: numpy.ndarray is the intended input; other objects that provide compatible astype/tostring behavior are also accepted.
        - Interdependencies: the caller is responsible for scaling floating-point samples into an appropriate int16 range prior to calling if that is desired.

## Returns:
    bytes-like (Python built-in bytes on Python 3):
        The exact object returned is the value produced by calling tostring() on the array after casting to numpy.int16. For empty input arrays this will be an empty bytes-like object.

## Raises:
    ImportError:
        If the numpy module cannot be imported when the function executes (numpy is imported inside the function).
    AttributeError:
        If the provided data does not have an astype method, or if the object returned by astype does not have a tostring method.
    TypeError, ValueError:
        If numpy.ndarray.astype(numpy.int16) fails to convert the input elements to int16; the underlying numpy exception is propagated.
    Any exception raised by numpy.ndarray.tostring():
        If tostring() itself raises (for example, due to memory errors), that exception propagates.

## Constraints:
Preconditions:
    - numpy is available in the runtime (otherwise ImportError will be raised).
    - The caller provides an array-like containing numeric sample values or an object with astype/tostring behavior.
    - Callers who require particular numeric scaling, clipping, or byte order must perform those transformations before calling.

Postconditions:
    - The input object is not modified in-place (astype returns a new array copy by default).
    - The function returns the raw byte representation of the new numpy.int16 array, using numpy.int16's default (native) byte order.

## Side Effects:
    - Imports numpy at call time if not already imported in the environment.
    - No file, network, stdout/stderr I/O.
    - No mutation of external/global state.

## Control Flow:
flowchart TD
    Start --> ImportNumpy[Import numpy]
    ImportNumpy --> Cast[Call data.astype(numpy.int16)]
    Cast --> ToString[Call .tostring() on cast result]
    ToString --> Return[Return tostring() result]
    Cast -->|astype raises TypeError/ValueError| PropagateCastError[Propagate exception]
    ImportNumpy -->|import fails| PropagateImportError[Propagate ImportError]
    ToString -->|tostring missing/raises| PropagateToStringError[Propagate corresponding exception]

## Examples:
1) Using a numpy int16 array (already in int16 range)
    import numpy
    samples = numpy.array([0, -12345, 12345], dtype=numpy.int16)
    raw = raw_audio_string(samples)
    # `raw` is the bytes returned by the ndarray.tostring() call.

2) Converting floating-point samples (caller scales and clips)
    import numpy
    float_samples = numpy.array([0.0, -0.5, 0.5], dtype=numpy.float32)
    # Scale and clip to int16 range before calling
    scaled = numpy.clip(float_samples * 32767.0, -32768, 32767).astype(numpy.int16)
    raw = raw_audio_string(scaled)

3) Defensive usage with error handling
    try:
        raw = raw_audio_string(user_provided_samples)
    except ImportError:
        # numpy not available: handle or report accordingly
        handle_missing_numpy()
    except (AttributeError, TypeError, ValueError) as exc:
        # Invalid input type or conversion error
        handle_bad_samples(exc)

