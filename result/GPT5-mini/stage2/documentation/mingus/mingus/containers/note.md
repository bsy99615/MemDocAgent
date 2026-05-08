# `note.py`

## `mingus.containers.note.Note` · *class*

*No documentation generated.*

### `mingus.containers.note.Note.__init__` · *method*

## Summary:
Initializes a Note instance by accepting multiple input forms (note-name string, integer code, or a name-bearing object), preparing a dynamics mapping (merging velocity and channel), and delegating actual population of the instance to helper methods.

## Description:
This constructor centralizes the parsing and normalization of different note input formats and the merging of dynamics-related keyword arguments before delegating to lower-level setters.

Behavioral overview:
- Always ensures a dynamics mapping exists: if the caller passed None, an empty dict is created.
- Immediately (before type-dispatch) inserts/overwrites "velocity" and "channel" keys in the local dynamics mapping when the corresponding keyword args are provided.
- Dispatches by input type:
  * If name is a string (six.string_types): calls self.set_note(name, octave, dynamics) — the local dynamics mapping (possibly mutated above) is passed to set_note.
  * Else if the object has attribute "name" (hasattr(name, "name") is True): calls self.set_note(name.name, name.octave, name.dynamics) — the object's own dynamics mapping is passed (the local dynamics mapping prepared above is not passed here).
  * Else if name is an int: calls self.from_int(name) — the local dynamics mapping is not used.
  * Otherwise: raises NoteFormatError with the message "Don't know what to do with name object: %r" % name.

Known callers and context:
- Invoked whenever a Note object is constructed (Note(...)). It is the canonical initialization path for new Note instances, used by application code and library-level reconstruction routines.

Why this logic belongs in the constructor:
- It centralizes creation-time responsibilities (normalizing inputs and merging dynamics parameters) so all Note instances are initialized consistently, and delegates the actual attribute-setting logic to set_note/from_int to keep responsibilities separated.

## Args:
    name (str | int | object), default "C"
        - Accepted forms:
            * string (six.string_types): interpreted as a note name (e.g., "C", "F#", "Bb"). Used with the octave and the local dynamics mapping.
            * integer: treated as an integer-encoded note and decoded by from_int.
            * object with attribute 'name' (hasattr(name, "name") == True): treated as a Note-like object; its name, octave and dynamics attributes are read and used.
        - Any other type triggers NoteFormatError.
    octave (int), default 4
        - Used only for the string-name branch; ignored for integer input and for name-bearing objects (which supply their own octave).
    dynamics (mapping | None), default None
        - If None, the constructor creates a new empty dict.
        - The constructor will mutate this mapping (or the newly-created dict) by assigning "velocity" and/or "channel" keys if those kwargs are provided.
        - The mutated mapping is passed to set_note only in the string-name branch; it is NOT passed when name is a name-bearing object.
    velocity (any), default None
        - If not None, assigned into dynamics["velocity"] during constructor preprocessing.
        - No validation of value type or numeric range is performed here.
    channel (any), default None
        - If not None, assigned into dynamics["channel"] during constructor preprocessing.
        - No validation is performed here.

## Returns:
    None
    - As a constructor, it does not return a value; its effect is to set up the Note instance by calling set_note or from_int.

## Raises:
    NoteFormatError
        - Raised when name is not a string, not an int, and does not have a 'name' attribute.
        - Exact message: "Don't know what to do with name object: %r" % name
    TypeError
        - May be raised when the provided dynamics argument (or the newly-created mapping, if a custom mapping type is used) does not support item assignment and the constructor attempts dynamics["velocity"] = ... or dynamics["channel"] = ....
        - This assignment happens before the type-dispatch and therefore can occur irrespective of which branch later runs.
    AttributeError
        - May be raised when name is detected as a name-bearing object (hasattr(name, "name") is True) but lacks name.octave or name.dynamics; accessing these attributes will raise AttributeError.
    Any exception from delegated methods
        - Exceptions raised by self.set_note(...) or self.from_int(...) propagate to the caller and are not caught here.

## State Changes:
Attributes READ:
    - Reads the following attributes from the provided name object when the name-bearing-object branch is taken: name.name, name.octave, name.dynamics.
    - Does not read any existing self.<attr> fields in the constructor body itself.

Attributes WRITTEN:
    - Mutates the local `dynamics` mapping (the dict passed in or the newly-created dict) by setting keys "velocity" and/or "channel" when the respective kwargs are provided. This mutation happens regardless of which dispatch branch is taken.
    - Delegated calls then mutate the Note instance:
        * self.set_note(name_str, octave, dynamics) — expected to write the instance's pitch/name, octave, and dynamics attributes (the exact attribute names are defined by set_note).
        * self.from_int(name_int) — expected to write the instance's internal numeric-decoded representation.
    - Note: In the name-bearing-object branch, the constructor passes name.dynamics (the object's mapping) to set_note; the local dynamics mapping mutated earlier is not forwarded to set_note in that branch.

## Constraints:
Preconditions:
    - Caller must supply `name` in one of the accepted forms (string, int, or object with attribute 'name').
    - If the caller expects the constructor to set velocity/channel into a provided dynamics mapping, the provided dynamics must support item assignment (i.e., be a mutable mapping).

Postconditions:
    - On successful completion:
        * String-name branch: the Note instance reflects the provided note name and octave, and the dynamics mapping passed to set_note includes any velocity/channel inserted by this constructor.
        * Name-bearing-object branch: the Note instance reflects the object's name, octave, and the object's own dynamics mapping (the local dynamics mapping prepared by the constructor is not forwarded).
        * Integer branch: the Note instance reflects the note decoded by from_int; the dynamics mapping is not used by the constructor to set pitch in this branch.
    - The local `dynamics` mapping (if created or provided) will have "velocity" and/or "channel" keys added when corresponding kwargs are provided; however, whether that mapping influences the final Note state depends on the dispatch branch as described above.

## Side Effects:
    - Mutates the provided or newly-created dynamics mapping by inserting/updating "velocity" and "channel" keys.
    - Delegates to self.set_note or self.from_int; those methods mutate the Note instance (and may perform additional actions) but any external I/O or side effects performed by them are outside the scope of this constructor.
    - No direct I/O or network activity occurs in this constructor itself.

### `mingus.containers.note.Note.dynamics` · *method*

## Summary:
Returns a small dictionary that exposes the Note's MIDI dynamics (channel and velocity) without modifying the Note.

## Description:
Known caller(s) and context:
- Note.__init__: when constructing a Note from another Note-like object, the constructor reads the other object's dynamics property and passes it to set_note (i.e., other_note.dynamics is used as the dynamics argument to set_note).

Purpose and rationale:
- Encapsulates the Note's dynamics (MIDI channel and velocity) in a single, predictable structure for consumers (other code that needs to read or forward a Note's MIDI parameters).
- Implemented as a separate property-style method to provide a stable, discoverable representation of dynamics that keeps construction/serialization logic decoupled from direct attribute access.

## Args:
- None

## Returns:
- dict[str, int or None]: A mapping with two keys:
    - "channel": the current MIDI channel value for this Note (expected integer in 0–15 when set; may be the class default otherwise).
    - "velocity": the current MIDI velocity value for this Note (expected integer in 0–127 when set; may be the class default otherwise).
  Edge-case return values:
    - If channel or velocity were not explicitly set and the class defaults are used, the returned values will reflect those defaults.
    - If an external actor has assigned non-standard values (not recommended), those exact values are returned; this method does not validate or coerce them.

## Raises:
- None. This accessor simply reads attributes and returns a dict; it does not raise exceptions.

## State Changes:
- Attributes READ:
    - self.channel
    - self.velocity
- Attributes WRITTEN:
    - None (no mutations performed)

## Constraints:
Preconditions:
- The Note instance must be a properly initialized object (i.e., channel and velocity attributes exist). The class defines defaults for these attributes at the class level, and methods set_channel and set_velocity enforce the valid ranges 0–15 and 0–127 respectively when those setters are used.

Postconditions:
- After calling this method, the Note instance is unchanged.
- The caller receives a dictionary snapshot of the current dynamics values; subsequent changes to the Note's attributes are not reflected in previously returned dict objects.

## Side Effects:
- None. No I/O, no external calls, and no mutations to objects outside self.

### `mingus.containers.note.Note.set_channel` · *method*

## Summary:
Sets the Note object's MIDI channel after validating the provided value is within the valid MIDI channel range (0 through 15). This updates the instance's channel attribute on success.

## Description:
Centralizes channel-range validation and assignment for a Note instance so callers can rely on a single place enforcing the allowed MIDI channel values. Typical callers are parts of the codebase that prepare Note objects for MIDI output or routing (e.g., before generating MIDI messages). Keeping this check as a dedicated method prevents duplication of the 0..15 range check across the codebase.

Example:
    note.set_channel(2)
    # After this call, note.channel == 2

## Args:
    channel (int): MIDI channel number to assign to the note.
        - Allowed values: integers from 0 up to and including 15.
        - Required; no default.

## Returns:
    None. The method performs an in-place update of the Note instance and does not return a value.

## Raises:
    ValueError: If the provided channel is not in the inclusive range 0..15.
        - Exact message: "MIDI channel must be 0-15"
        - Trigger condition: the boolean expression (0 <= channel < 16) evaluates to False.

## State Changes:
    Attributes READ:
        - None

    Attributes WRITTEN:
        - self.channel is assigned the provided channel value when validation passes

## Constraints:
    Preconditions:
        - Callers should provide a channel value intended to be an integer within 0..15.
        - The Note instance must be a valid object able to hold a channel attribute.

    Postconditions:
        - On normal return, self.channel equals the provided channel and is guaranteed to be in 0..15.
        - If a ValueError is raised, the Note's channel attribute is not modified by this method.

## Side Effects:
    - No I/O, network, or filesystem operations.
    - The only side effect is mutation of the Note instance's channel attribute on success.

### `mingus.containers.note.Note.set_velocity` · *method*

## Summary:
Validates and sets the note's MIDI velocity (an integer in the 0–127 range), updating the Note object's velocity attribute.

## Description:
This method centralizes the validation and assignment of the MIDI velocity for a Note instance. It is intended to be called by any code that prepares or mutates a Note prior to playback, MIDI export, or rendering (for example: user code constructing notes, sequencer/playback routines, or utilities that modify note performance parameters). There are no explicit callers inside this module; callers come from higher-level code that manipulates Note objects.

Keeping this logic in a dedicated method ensures velocity range checking is performed consistently in one place (rather than being duplicated at every call site) and isolates the mutation of the object's state behind a single, testable API.

## Args:
    velocity (int): Desired MIDI velocity. Allowed integer range is 0 through 127 inclusive.
        - If a numeric type comparable to int is provided (e.g., an int or a subclass), it will be tested against the range.
        - Non-comparable types are not explicitly handled and may raise a Python TypeError during comparison.

## Returns:
    None

## Raises:
    ValueError: If velocity is outside the valid MIDI range (not 0 <= velocity < 128).
    TypeError (implicit): If the provided velocity value cannot be compared with integers using <= and <, Python's comparison operators will raise a TypeError. This is not explicitly raised by the method but may occur at runtime for incompatible types.

## State Changes:
    Attributes READ:
        - (none) — the method does not read any existing Note attributes before assignment.
    Attributes WRITTEN:
        - self.velocity: updated to the provided velocity value when validation passes.

## Constraints:
    Preconditions:
        - self is a properly-initialized Note instance (has an attribute namespace where velocity may be stored).
        - velocity should be an integer (or int-comparable value) within 0..127. Passing non-numeric types is unsupported.
    Postconditions:
        - After a successful call, self.velocity is set to the provided velocity value and is guaranteed to be an integer-like value within 0..127.
        - If the argument is out-of-range, the method raises ValueError and self.velocity remains unchanged by this call (assuming no earlier side-effect during evaluation).

## Side Effects:
    - Mutates the Note instance by setting/overwriting the self.velocity attribute.
    - No I/O, no network calls, and no interactions with external systems occur.

### `mingus.containers.note.Note.set_note` · *method*

## Summary:
Sets this Note object's pitch (name and octave) and optional MIDI dynamics (velocity and channel), validating inputs and updating the object's state. Returns the Note instance to allow chaining.

## Description:
Known callers and contexts:
- Note.__init__: Called when constructing a Note from a string name (e.g., "C" or "C-4") or when copying another Note's name/octave/dynamics; used during object initialization.
- Note.from_shorthand: Called when parsing shorthand pitch representations to set the canonical name and octave.
- Any external code that needs to (re)initialize or update the pitch and MIDI dynamics of an existing Note.

Why this is a separate method:
- Centralizes parsing/validation of textual note representations, numeric octave coercion, and consistent handling of dynamics (velocity/channel).
- Keeps initialization logic and other parsing helpers concise by delegating name+octave+dynamics normalization and validation here.

## Args:
    name (str): Note name or combined name-octave string. Defaults to "C".
        - Allowed forms:
            * Simple note name like "C", "C#", "Db", etc. (accepted if mingus.core.notes.is_valid_note(name) returns True)
            * Combined form "NOTE-OCTAVE", e.g. "C-4", where NOTE is a valid note string and OCTAVE is an integer string.
        - If the combined form is used, the explicit octave argument is ignored.
    octave (int): Octave number to assign when name does not include an octave. Defaults to 4.
    dynamics (dict or None): Optional dict that may include keys "velocity" and/or "channel" (e.g., {"velocity": 90, "channel": 1}). If None, treated as an empty dict.
    velocity (int or None): Optional explicit MIDI velocity (0-127). If provided and valid, set on the Note. If omitted, the method will look for "velocity" in dynamics. Defaults to None.
    channel (int or None): Optional explicit MIDI channel (0-15). If provided, the method will set it and then (importantly) still check dynamics["channel"] — see precedence rules below. Defaults to None.

## Returns:
    Note: Returns self (the mutated Note instance) on success to allow method chaining.

## Raises:
    mingus.containers.mt_exceptions.NoteFormatError:
        - If the name has more than one "-" (e.g., "C-4-extra") or if the parsed note part is not a valid note according to mingus.core.notes.is_valid_note.
    ValueError:
        - Propagated from set_velocity if a velocity outside 0-127 is supplied (explicit velocity or dynamics["velocity"]).
        - Propagated from set_channel if a channel outside 0-15 is supplied (explicit channel or dynamics["channel"]).
        - Can also be raised by int(octave) when the second part of a "NOTE-OCTAVE" string is not a valid integer (this will raise Python's built-in ValueError).

## State Changes:
Attributes READ:
    - None of the Note.* attributes are read for decision-making inside this method (it consults the provided arguments and the external notes.is_valid_note function).
Attributes WRITTEN:
    - self.name: set to the validated note string (e.g., "C", "C#", "Db").
    - self.octave: set to the provided octave (int) or the integer parsed from a "NOTE-OCTAVE" name.
    - self.velocity: may be set via self.set_velocity(...) (see channel/velocity rules).
    - self.channel: may be set via self.set_channel(...).

## Constraints:
Preconditions:
    - name must be a string in one of the accepted forms described above.
    - If name is "NOTE-OCTAVE", the octave substring must be parseable as an integer (or a ValueError will be raised).
    - velocity, if provided (either as the explicit velocity argument or dynamics["velocity"]), must be an integer in 0..127 (validated by set_velocity).
    - channel, if provided (either as the explicit channel argument or dynamics["channel"]), must be an integer in 0..15 (validated by set_channel).

Postconditions:
    - On successful return, self.name contains a valid note string accepted by mingus.core.notes.is_valid_note.
    - On successful return, self.octave is an int representing the octave for the note.
    - If velocity and/or channel were provided (either explicitly or via dynamics), self.velocity and/or self.channel have been updated and validated.
    - The method returns self for chaining.

Precedence and nuanced behavior:
    - Velocity precedence: if the explicit velocity argument is not None, it is used and dynamics["velocity"] is ignored. If explicit velocity is None, the method uses dynamics["velocity"] if present.
    - Channel precedence: the method will set_channel(channel) if the explicit channel argument is not None and will then, if dynamics contains "channel", call set_channel(dynamics["channel"]). In practice this means that if both explicit channel and dynamics["channel"] are provided, dynamics["channel"] will override the explicit channel (the last set wins).
    - If name contains a dash and splits into exactly two parts, the provided octave parameter is ignored in favor of the octave parsed from the name.

## Side Effects:
    - Mutates the Note instance (self.name, self.octave, and possibly self.velocity/self.channel).
    - No I/O or external service calls.
    - May raise exceptions as described above; callers should handle NoteFormatError and ValueError where appropriate.

### `mingus.containers.note.Note.empty` · *method*

## Summary:
Resets the Note instance to an "empty" state by clearing the pitch name and octave and restoring MIDI-related fields to their module default values, effectively making the Note represent "no pitch" until reassigned.

## Description:
- Known callers and context:
    - No direct internal callers were found in the Note class source. This method is intended for use by client code that wants to reuse an existing Note object rather than allocate a new one, for example when clearing a note in a sequence editor, resetting a buffer, or initializing an object pool entry.
    - Typical lifecycle stage: invoked when a Note must be returned to a neutral/default state before being repopulated or discarded.
- Rationale for separate method:
    - Encapsulates the logic to clear pitch and restore MIDI/dynamics defaults in one place so callers do not need to know module-level default constants (_DEFAULT_CHANNEL, _DEFAULT_VELOCITY) or the precise fields to reset. Keeps resetting behavior consistent across the codebase and allows reuse of Note objects without repeating field assignments.

## Args:
    None

## Returns:
    None

## Raises:
    None raised directly by this method.
    Note: subsequent use of the Note after calling empty() may trigger exceptions in other methods (for example, __int__ expects a non-empty name and will raise an IndexError if invoked while name == ""), but those exceptions are raised outside of empty().

## State Changes:
- Attributes READ:
    - None (the method does not read existing attribute values).
- Attributes WRITTEN:
    - self.name (set to empty string "")
    - self.octave (set to integer 0)
    - self.channel (set to module default _DEFAULT_CHANNEL)
    - self.velocity (set to module default _DEFAULT_VELOCITY)

## Constraints:
- Preconditions:
    - No preconditions are required by empty() itself; it may be called in any object state.
    - Callers should be aware that other Note methods assume the note has a valid non-empty name and may fail if invoked before the Note is reinitialized (e.g., __int__ accesses self.name[0]).
- Postconditions:
    - After the call:
        - self.name == ""
        - self.octave == 0
        - self.channel == _DEFAULT_CHANNEL
        - self.velocity == _DEFAULT_VELOCITY
    - The Note should be considered "cleared" and not safe for operations that require a valid note name and octave until set_note, from_int, from_shorthand, or similar initializer is called.

## Side Effects:
- No I/O operations or interactions with external services.
- Only mutates the Note instance (self); does not mutate other objects or global state.
- Does not perform validation when assigning defaults (it assigns module defaults directly rather than calling set_channel/set_velocity). Callers relying on the channel and velocity being within MIDI ranges should ensure module defaults comply with the same constraints enforced by set_channel/set_velocity (channels: 0-15, velocities: 0-127).

### `mingus.containers.note.Note.augment` · *method*

## Summary:
Mutates the Note instance by replacing self.name with the result of applying the core accidental-adjustment function: remove a trailing flat ('b') if present, otherwise append a sharp ('#').

## Description:
This method performs a direct, in-place update of the note name by delegating to mingus.core.notes.augment and assigning its return value to self.name.

Known callers and invocation context:
- There are no references to Note.augment inside the mingus.containers.note module beyond its definition. Any calls to this method originate from external code or user code that operates on Note instances.

Why this logic is a separate method:
- Acts as a thin wrapper so external code can request accidental augmentation directly on a Note instance without calling the standalone notes.augment function and then reassigning the name.

## Args:
This method takes no arguments.

## Returns:
None. The method returns implicitly None; its effect is the mutation of self.name.

## Raises:
- IndexError: If self.name is an empty string, notes.augment will attempt to access note[-1] and raise IndexError.
- TypeError: If self.name is not a string (or otherwise not a sequence supporting indexing and concatenation), the operations in notes.augment may raise TypeError.
- Any exception raised by mingus.core.notes.augment will propagate unchanged; this method does not catch or translate exceptions.

## State Changes:
Attributes READ:
- self.name

Attributes WRITTEN:
- self.name

No other attributes of the Note instance are read or modified.

## Constraints:
Preconditions:
- To avoid exceptions, self.name should be a non-empty string (length >= 1). The method does not validate musical correctness of the string.

Postconditions:
- If the original self.name ended with 'b', the new self.name equals the original with the final character removed (one trailing flat removed). Examples: "Bb" -> "B", "Ebb" -> "Eb".
- Otherwise, the new self.name equals the original with a single '#' character appended (one additional sharp added). Examples: "C" -> "C#", "C#" -> "C##".
- Octave, velocity, channel, and other Note attributes remain unchanged.

## Side Effects:
- No I/O or external service interactions.
- The method mutates the Note instance (self.name) in-place; exceptions from mingus.core.notes.augment propagate to the caller.

## Examples (before -> after):
- "C" -> "C#"
- "C#" -> "C##"
- "Bb" -> "B"
- "Ebb" -> "Eb"
- "" -> raises IndexError

### `mingus.containers.note.Note.diminish` · *method*

## Summary:
Lower the accidental of this Note's name by one semitone and store the result back on the instance (mutates self.name). Does not change octave, channel, or velocity.

## Description:
Known callers and context:
- There are no recorded internal callers in the same module; this method is intended for direct use by application logic or utilities that need to adjust a Note object's accidental by a single semitone (for example, during enharmonic conversion, note editing, or interactive transformations).
- Typical lifecycle stage: called when a Note instance is being transformed in-place as part of editing/normalization operations.

Rationale for being a separate method:
- Serves as a thin instance-level wrapper around the core utility mingus.core.notes.diminish so callers can operate on Note objects without manipulating raw note-name strings.
- Provides symmetry with other mutating helpers on Note (e.g., augment, remove_redundant_accidentals, transpose), keeping note mutation logic discoverable and consistent on the Note API.

## Args:
None.

## Returns:
None. The method returns implicitly None; its observable effect is the mutation of self.name.

## Raises:
- IndexError: If self.name is an empty string, the underlying function accesses note[-1] and will raise IndexError.
Note: The implementation does not perform additional validation of self.name; callers should ensure the Note has a non-empty name if they wish to avoid this exception.

## State Changes:
Attributes READ:
- self.name

Attributes WRITTEN:
- self.name

(No other attributes—self.octave, self.channel, self.velocity—are modified by this method.)

## Constraints:
Preconditions:
- self.name should be a non-empty string representing the note name (e.g., "C", "C#", "Db", "C##"). The method assumes a string and will produce an IndexError for empty strings.
Postconditions:
- If self.name ends with the character '#', the final '#' is removed (examples: "C#" -> "C", "C##" -> "C#").
- If self.name does not end with '#', the character 'b' is appended (examples: "C" -> "Cb", "Cbb" -> "Cbbb").
- No change to octave or other Note attributes.
- The method completes with self.name set to the transformed string and returns None.

## Side Effects:
- No I/O or calls to external services.
- Mutates only the Note instance's name attribute (self.name). No other objects are altered.

## Examples:
- Before: self.name == "C#"  After: self.name == "C"
- Before: self.name == "C"   After: self.name == "Cb"
- Before: self.name == "C##" After: self.name == "C#"
- Before: self.name == ""    Behavior: IndexError raised by the underlying implementation

### `mingus.containers.note.Note.change_octave` · *method*

## Summary:
Adjusts the note's octave in-place by adding a signed integer offset and clamps the octave to a minimum of 0.

## Description:
Known callers:
- Note.octave_up — increments the octave by 1 using this method.
- Note.octave_down — decrements the octave by 1 using this method.
- External code may call this method directly when programmatically changing a Note's octave.

Context:
This method is invoked when the system needs to change a Note's octave (for example, user commands to move a note up/down an octave or programmatic adjustments). It exists as a small, reusable helper so that all octave changes go through a single place where clamping logic (no negative octaves) is enforced. Keeping the increment/clamp logic here avoids duplication (octave_up/octave_down) and centralizes future changes to octave-handling semantics.

Why separate:
- Encapsulates the business rule "octave must not be negative".
- Provides a single place to adjust octave-related invariants and side-effects, simplifying maintenance and testing.

## Args:
    diff (int): Signed integer offset to add to the current octave.
        - Positive values raise the octave.
        - Negative values lower the octave.
        - Any integer is accepted; the resulting octave is clamped to >= 0.
        - If a non-integer numeric type is supplied (e.g., float), behavior is the arithmetic result (but callers are expected to pass integers).

## Returns:
    None. The method performs an in-place mutation of self.octave and does not return a value.

## Raises:
    No exceptions are explicitly raised by this method.
    Possible runtime exceptions (not raised intentionally by the method):
    - AttributeError: if the object lacks self.octave.
    - TypeError: if diff cannot be added to self.octave (e.g., diff is a non-numeric type).
    These are side effects of Python operations and indicate incorrect caller usage or malformed object state.

## State Changes:
Attributes READ:
    - self.octave

Attributes WRITTEN:
    - self.octave (set to self.octave + diff, then possibly clamped to 0)

No other attributes of self are read or modified.

## Constraints:
Preconditions:
    - The Note instance must have an octave attribute that is numeric (typically an int).
    - Callers should pass an integer diff to preserve octave semantics used across the class.

Postconditions:
    - After the call, self.octave is guaranteed to be >= 0.
    - If no error occurs, self.octave == max(previous_octave + diff, 0).
    - The method mutates the Note instance in-place; no new Note is created.

## Side Effects:
    - Mutates the Note object by updating its octave attribute.
    - No I/O, no external service calls, and no mutation of objects other than self.

### `mingus.containers.note.Note.octave_up` · *method*

## Summary:
Increase this Note object's octave by one (mutates the note's octave attribute in place).

## Description:
This is a convenience wrapper that calls the Note.change_octave method with a diff of +1. By centralizing the single-step octave change in its own method, callers can express intent clearly (raise by one octave) without constructing numeric deltas. It is typically used by client code manipulating pitches or for interactive adjustments; there are no internal callers discovered within the mingus containers module — it serves as part of the public Note API.

Why it's a separate method:
- Improves readability at call sites (note.octave_up() is clearer than note.change_octave(1)).
- Keeps single-responsibility for single-step octave moves while more complex logic remains in change_octave or transpose.

## Args:
    None

## Returns:
    None

## Raises:
    TypeError: If self.octave is not a numeric type supporting addition with int (arises from executing self.octave += 1).
    Note: The method itself contains no explicit raise statements; any exception comes from change_octave or underlying Python arithmetic.

## State Changes:
    Attributes READ:
        self.octave (read by change_octave when computing the new value)
    Attributes WRITTEN:
        self.octave (incremented by +1; change_octave enforces a minimum of 0)

## Constraints:
    Preconditions:
        - self must be a valid Note instance whose octave attribute is an integer-like number.
    Postconditions:
        - self.octave will be increased by exactly 1 relative to its pre-call value, except that change_octave clamps negative results to 0.
        - No other attributes (name, dynamics, channel, velocity) are modified by this call.

## Side Effects:
    - Mutates the receiver (self.octave).
    - No I/O, no global state mutation, and no interaction with external services.

## Example:
    Given a Note with octave 4, calling note.octave_up() results in octave 5.
    If octave were 0 and note.octave_up() is called repeatedly, octave will grow without an upper bound (there is no enforced maximum), but negative values are prevented by change_octave's clamp behavior.

### `mingus.containers.note.Note.octave_down` · *method*

## Summary:
Decreases the Note instance's octave by one (mutating the instance) by delegating to the centralized octave-modification logic; the octave is never allowed to become negative.

## Description:
Known callers and context:
- This is a public instance method intended to be called by client code that needs a one-octave downward shift.
- Within the Note class, octave_up exists as the complementary operation; change_octave is the shared implementation used by both octave_up and octave_down.
- The method is typically invoked at the point in an editing or transformation pipeline where a discrete single-octave decrement is required; it intentionally delegates the actual arithmetic and clamping behavior to change_octave.

Why this is its own method:
- It provides an intention-revealing, single-purpose API for moving a note down one octave.
- By delegating to change_octave, it centralizes clamping and octave-adjustment invariants (specifically, preventing negative octaves) in one place and avoids duplicating that logic.

## Args:
    None

## Returns:
    None
    - Performs an in-place mutation of the Note instance; no value is returned.

## Raises:
    - This method does not raise exceptions itself.
    - Runtime errors may propagate from change_octave, for example:
        - AttributeError if self lacks an octave attribute.
        - TypeError if the octave cannot be adjusted with the internal arithmetic (e.g., non-numeric octave).
    These are not part of normal control flow and indicate incorrect usage or corrupted state.

## State Changes:
Attributes READ:
    - self.octave (read indirectly by change_octave)

Attributes WRITTEN:
    - self.octave (updated to previous_octave - 1, then clamped to >= 0 by change_octave)

No other attributes on self are accessed or modified by this method.

## Constraints:
Preconditions:
    - The Note instance must have a numeric octave attribute (the class uses integers for octave).
    - The caller must not provide any arguments (the method signature accepts none).

Postconditions:
    - After the call, self.octave == max(previous_octave - 1, 0).
    - The Note instance is mutated in-place; no new object is created.

## Side Effects:
    - Mutates only the Note instance's octave attribute.
    - No I/O, no external service interaction, and no mutation of other objects.

### `mingus.containers.note.Note.remove_redundant_accidentals` · *method*

## Summary:
Normalizes the note name by removing redundant accidentals and updates the Note's name in place.

## Description:
This is a thin wrapper that delegates normalization to the core utility notes.remove_redundant_accidentals and stores the normalized result back on the Note. It is intended to be called when a Note's name may contain multiple accidentals (for example "C##" or "Dbb") and you want to collapse them into the minimal canonical representation (e.g., augmenting or diminishing the base note as required).

Known callers and call contexts:
- No internal callers were found within the repository for this method; it is provided as a public convenience on the Note object for callers that mutate or construct note names and then want to normalize them as a separate step (for example, after programmatic transposition or direct string manipulation of Note.name).
- Typical lifecycle stage: called after constructing or mutating a Note.name when you need a normalized, human- or algorithm-friendly name before further processing (comparison, printing, conversion to MIDI number, etc).

Why this logic is a separate method:
- It encapsulates a common normalization operation that operates on the Note's internal state and delegates the core algorithm to mingus.core.notes; keeping it on Note makes it easier for callers to normalize state without importing utilities or reassigning attributes manually. It centralizes the state mutation (writing self.name) in one place.

## Args:
    None

## Returns:
    None
    - The method updates self.name in place and does not return a value.

## Raises:
    IndexError:
        - If self.name is an empty string, the underlying notes.remove_redundant_accidentals attempts to access note[0], which raises IndexError.
    TypeError:
        - If self.name is not a subscriptable text object (for example, None or a non-string type), the underlying function's slicing or indexing will raise TypeError.
    Note:
        - This method does not itself validate note format or raise NoteFormatError; such validation is performed elsewhere (e.g., in set_note). The exceptions above originate from the called core utility when the preconditions are not met.

## State Changes:
    Attributes READ:
        - self.name
    Attributes WRITTEN:
        - self.name

## Constraints:
    Preconditions:
        - self.name must be a non-empty, subscriptable string whose first character is a base note letter (typically A-G). The function expects typical note name strings like "C", "C#", "Db", "Ebb", "F##", etc.
    Postconditions:
        - After the call, self.name will be replaced with a canonicalized note name where redundant accidentals have been collapsed by repeatedly augmenting or diminishing the base note as required. The resulting name will start with the original base letter and have zero or more accidentals corresponding to the minimal representation produced by mingus.core.notes.

## Side Effects:
    - Mutates the Note instance by assigning a new value to self.name.
    - No I/O, no external service calls, and no mutation of objects other than self.

### `mingus.containers.note.Note.transpose` · *method*

## Summary:
Transpose this Note in-place by a shorthand interval string; updates the note name and, if the transposition crosses an octave boundary, adjusts the octave by ±1.

## Description:
Computes a new note name for this Note using mingus.core.intervals.from_shorthand and writes it into self.name. Then it compares the numeric pitch of the updated Note against the original (constructed as Note(old, o_octave)) to detect octave crossing:
- When transposing up (up truthy), if the post-transposition pitch is strictly lower than the original pitch, the octave is incremented by 1.
- When transposing down (up falsy), if the post-transposition pitch is strictly higher than the original pitch, the octave is decremented by 1.

Known callers / usage context:
- Intended to be called whenever a single Note must be transposed (e.g., by higher-level chord/melody transposition utilities or by user code). It encapsulates both the name change and octave-carry logic so callers need only supply the shorthand interval and direction.

Why this is a separate method:
- Transposition requires both computing a new note name (handling accidentals) and correctly handling octave carry; encapsulating this ensures consistent behavior and prevents duplication across call sites.

## Args:
    interval (str):
        Shorthand interval string consumed by mingus.core.intervals.from_shorthand.
        - Must be a non-empty string whose last character is one of '1'..'7' (the interval degree).
        - May include accidental characters '#' and 'b' (e.g., "3", "#4", "b7", "##2").
        - This method does not validate the format beyond passing it to intervals.from_shorthand.
    up (bool or truthy/falsy, optional):
        Direction of transposition. If truthy, transpose up; if falsy, transpose down. Defaults to True.

## Returns:
    None
    - The method mutates self and returns no value.

## Raises:
    - TypeError: If intervals.from_shorthand returns False (indicating an invalid interval or unhandled case), that boolean is assigned to self.name. Subsequent numeric comparison uses Note.__int__ which indexes self.name[0]; indexing a bool raises TypeError (e.g., "'bool' object is not subscriptable"). This method does not catch that error.
    - NoteFormatError: Not raised by this method in normal operation. A NoteFormatError could only occur if constructing the temporary Note(old, o_octave) somehow receives invalid components; this is unlikely for a well-formed existing Note instance.

## State Changes:
Attributes READ:
    - self.name (saved as old)
    - self.octave (saved as o_octave)

Attributes WRITTEN:
    - self.name (set to the value returned by intervals.from_shorthand(self.name, interval, up))
    - self.octave (may be incremented by 1 when transposing up and octave carry is detected; may be decremented by 1 when transposing down and octave carry is detected)

## Constraints:
Preconditions:
    - self.name must be a valid note string and self.octave must be an integer before calling (the code assumes a well-formed Note).
    - interval should be a shorthand interval string as described in Args. If it is invalid for intervals.from_shorthand, the method will assign False to self.name and a TypeError will likely follow during comparison.

Postconditions:
    - If intervals.from_shorthand returns a valid note-name string:
        - self.name contains that note-name string.
        - self.octave is adjusted by +1 (when up truthy and new pitch < original pitch) or -1 (when up falsy and new pitch > original pitch); otherwise octave is unchanged.
    - If intervals.from_shorthand returns False:
        - self.name becomes False and a TypeError is expected later during numeric comparisons; there is no rollback.

Notes on octaves:
    - This method does not clamp or bound the octave; it may become negative if decremented and there is no upper bound enforced here.

## Side Effects:
    - Mutates the Note instance (self.name and possibly self.octave).
    - Creates one temporary Note(old, o_octave) for comparison.
    - No I/O, no external service calls, and no other external object mutations.

## Example:
    # Transpose up a major third shorthand
    n = Note("C", 4)
    n.transpose("3", up=True)
    # n.name is updated to the third above "C" (e.g., "E"); octave increment occurs only if the new pitch is lower than original.

    # Transpose down a minor second shorthand
    m = Note("C", 4)
    m.transpose("2", up=False)
    # m.name now represents the note a second below; octave decremented only if the new pitch is higher than the original.

### `mingus.containers.note.Note.from_int` · *method*

## Summary:
Set this Note's pitch from an absolute integer pitch number by mapping the integer to a pitch-class (name) and octave, and return the Note instance.

## Description:
This method converts an integer pitch value into the Note object's textual pitch name and octave number. It is used when a Note is constructed from an integer (see Note.__init__, which calls this method when the constructor receives an int). Typical usage is to convert MIDI-style absolute note numbers or other integer-based pitch encodings into the Note representation used throughout the library.

This logic is implemented as a separate method to centralize the integer→Note conversion in one place so the constructor (and any other callers) can reuse the same behavior and maintain consistent handling of octave calculation and pitch-class mapping.

Known callers:
- Note.__init__: when the constructor receives an integer as the initial name argument (the constructor calls this method to initialize the note).

## Args:
    integer (int):
        - An absolute pitch number.
        - Expected to be an integer (Python int). Typical inputs are MIDI note numbers (0–127) but any integer is accepted.
        - If a non-integer is passed, behavior depends on Python arithmetic semantics and the notes.int_to_note function (see Raises).

## Returns:
    Note:
        - Returns self (the same Note instance), now updated so that:
            * self.name is a pitch-class string returned by notes.int_to_note(integer % 12) (e.g., "C", "C#", "D", ...).
            * self.octave is set to integer // 12 (floor division).

## Raises:
    - TypeError:
        - If the provided argument does not support the modulo (%) or floor-division (//) operations (for example, None or some unsupported object types), Python will raise a TypeError.
    - mingus.core.mt_exceptions.RangeError:
        - If a non-integer value reaches notes.int_to_note and that function rejects it (notes.int_to_note checks that its argument is an integer in 0..11 and will raise RangeError for invalid values). For normal integer inputs this will not occur because integer % 12 yields a value in 0..11.
    - mingus.core.mt_exceptions.FormatError:
        - Not expected for normal use here (notes.int_to_note can raise FormatError for invalid accidental parameters), but mentioned for completeness because int_to_note may raise it if its interfaces change.

## State Changes:
    Attributes READ:
        - None (this method does not read other Note attributes).
    Attributes WRITTEN:
        - self.name: overwritten with the pitch-class string corresponding to integer % 12.
        - self.octave: overwritten with integer // 12.

## Constraints:
    Preconditions:
        - self must be a valid Note instance.
        - integer should be a Python integer for deterministic, intended behavior. If integer is within the common MIDI range (0–127), octave will be within expected non-negative ranges.
    Postconditions:
        - After the call, self.name is a valid pitch-class string (using the default accidental style from notes.int_to_note, which uses sharps "#") corresponding to the pitch-class of the input integer.
        - After the call, self.octave equals the integer floor-divided by 12.
        - The method returns self to allow chaining.

## Side Effects:
    - No I/O or external service calls.
    - The only side effects are in-place mutation of the Note instance (self.name and self.octave).

### `mingus.containers.note.Note.measure` · *method*

## Summary:
Compute and return the signed semitone distance from this note to another pitch value; does not modify the Note instance.

## Description:
Converts both operands to their integer pitch encodings and returns int(other) - int(self). Typical callers are interval, transposition, or analysis code that needs the number of semitone steps between two pitches (for example, to compute an interval quality or to decide octave adjustments during transposition). This logic is factored into its own method to make this common operation explicit, reusable, and easier to read than repeating the int-conversion subtraction at each call site.

Example:
    If this Note represents C-4 (int(self) == 48) and other represents E-4 (int(other) == 52), the method returns 4.

## Args:
    other (object): An object convertible to an integer pitch via the built-in int() call.
        - Common valid inputs: another Note instance, an integer pitch value, or any object implementing __int__() that returns a compatible integer.
        - Not valid: arbitrary strings (int("A") will raise ValueError) or objects where int() is unsupported.

## Returns:
    int: The semitone difference computed as int(other) - int(self).
        - Positive: other is higher than self.
        - Zero: same pitch.
        - Negative: other is lower than self.

## Raises:
    TypeError: If int(other) cannot be computed (for example, other is None or lacks __int__).
    ValueError: If int(other) is attempted on an invalid string/format and the built-in int() raises ValueError.
    IndexError: If this Note's name is empty so that Note.__int__ attempts to index self.name[0].
    Any other exception raised by int(other) or by Note.__int__ (for example, errors from notes.note_to_int) will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.name
        - self.octave
    Attributes WRITTEN:
        - None (this method does not modify self or other)

## Constraints:
    Preconditions:
        - self.name should be a non-empty string whose first character is a valid note letter accepted by notes.note_to_int.
        - other must be convertible to an integer pitch in the same encoding used by Note.__int__.
    Postconditions:
        - self remains unchanged.
        - The returned integer equals int(other) - int(self).

## Side Effects:
    - The method itself performs no I/O and makes no external service calls.
    - Note: calling int(other) will execute other.__int__ (if present) and may produce side effects if that implementation mutates state; such side effects are not caused by this method but by the other object's __int__.

### `mingus.containers.note.Note.to_hertz` · *method*

## Summary:
Converts the note to a frequency in hertz by treating the note's integer representation relative to an internal reference integer 57 and scaling by a given standard pitch (default 440 Hz).

## Description:
This method obtains the note's integer representation (by calling the object's __int__() method), computes the semitone distance from the internal reference integer 57, and returns the frequency in hertz using the equal-tempered tuning formula: frequency = 2 ** (semitone_difference / 12.0) * standard_pitch.

Known callers and typical context:
- Commonly invoked by code that needs a numeric frequency for a note for synthesis, playback, DSP, display, or export to audio formats.
- Typically used in the stage where symbolic musical data (Note objects) are converted to real-valued frequencies for audio generation or analysis.
- No specific in-repository callers are asserted here; this method exists to encapsulate the conversion logic so callers simply request a frequency rather than implementing the formula themselves.

Why this is a dedicated method:
- Encapsulates the conversion from the object's internal integer pitch representation to a frequency so callers do not need to duplicate the equal-tempered frequency calculation.
- Isolates the mapping convention (reference integer 57 -> standard_pitch) in one place, allowing consistent behavior and easier changes if the reference or formula needs adjustment.

## Args:
    standard_pitch (float, optional): The frequency in Hz that corresponds to the note whose integer representation equals 57.
        - Default: 440
        - Expected: a finite numeric value. The implementation does not validate sign or zero; passing zero or negative values will produce zero or negative frequencies respectively.

## Returns:
    float: The computed frequency in hertz.
        - If self.__int__() == 57, returns exactly standard_pitch.
        - For typical integer semitone differences, returns 2 ** (diff / 12.0) * standard_pitch where diff = self.__int__() - 57.
        - The return value is a floating-point number; for very large magnitude differences the value may underflow/overflow to 0.0 or inf per IEEE floating-point behavior.

## Raises:
    This method does not explicitly raise any exceptions.
    - If self.__int__() raises, that exception will propagate unchanged.
    - No checks are performed on standard_pitch; invalid numeric inputs will not be intercepted here.

## State Changes:
    Attributes READ:
        - The method invokes self.__int__(), thereby reading whatever internal state __int__() uses to compute the integer pitch representation.
    Attributes WRITTEN:
        - None. The method does not modify self or any external objects.

## Constraints:
    Preconditions:
        - The object must implement __int__() and that method must return an integer-like value (or a numeric convertible to int) representing the note's pitch in the same integer scale where 57 is the reference.
        - standard_pitch should be a finite numeric value for meaningful results (positive for standard frequency semantics).

    Postconditions:
        - Returns a float computed as 2 ** ((int_value - 57) / 12.0) * standard_pitch.
        - Leaves the Note object and external state unmodified.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside self.
    - Any exceptions raised originate from self.__int__() or from Python numeric operations (e.g., OverflowError in unusual environments), not from this method itself.

### `mingus.containers.note.Note.from_hertz` · *method*

## Summary:
Convert a frequency in hertz into the note name and octave of this Note object, mutating the object and returning it.

## Description:
This method converts a frequency (hertz) into a musical note name (e.g., "C", "F#", "Bb") and an integer octave, updates self.name and self.octave accordingly, and returns self to allow chaining.

Known callers and context:
- No specific callers are present in the provided class memory snapshot. Conceptually, this method is used when a Note object must be created or adjusted from a physical frequency measurement (for example: reading audio analysis results, converting synthesized frequencies to notation, or parsing frequency input in an application pipeline). It is typically invoked during a conversion stage where frequency values are mapped to notation.

Why this is a separate method:
- The conversion involves several numeric steps (logarithm base 2, scaling, offsets, modular arithmetic and integer truncation) and mutates the Note's state. Encapsulating this logic in a dedicated method keeps conversion concerns isolated from other note creation and formatting methods (such as from_int, set_note, or to_hertz) and makes the conversion reusable and testable.

## Args:
    hertz (int|float|str): The input frequency in hertz. The value is converted to float internally.
        - Must be convertible to float.
        - Must be > 0 (math.log requires positive input).
    standard_pitch (int|float, optional): The reference pitch in hertz corresponding to A4. Defaults to 440.
        - Must be convertible to float and > 0 to produce meaningful results.

## Returns:
    self (Note): The same Note instance, after updating:
        - self.name: str, one of the note names returned by notes.int_to_note (e.g., "C", "C#", "Db", ...).
        - self.octave: int, computed from the scaled logarithmic value.
    Behavior on edge/rounding boundaries:
        - The method truncates the computed internal floating value with int() (floor toward zero for positive values), which can bias ties toward the lower integer step. This can produce off-by-one octave/name near exact pitch boundaries.

## Raises:
    ValueError (from math.log):
        - If hertz (after conversion to float) is <= 0, math.log will raise a ValueError ("math domain error").
    TypeError:
        - If hertz or standard_pitch cannot be converted to float (e.g., passing an unsupported object).
    (Notes module exceptions are not expected here because the code ensures the integer passed to notes.int_to_note is in 0..11 using modulo arithmetic.)
    Any exception produced by the underlying numeric operations (e.g., OverflowError) may also propagate.

## State Changes:
    Attributes READ:
        - None of self's attributes are read by this method.
    Attributes WRITTEN:
        - self.name: set to a note string from mingus.core.notes.int_to_note(int(value) % 12)
        - self.octave: set to int(value / 12) - 6

## Constraints:
    Preconditions:
        - hertz must be convertible to float and strictly positive.
        - standard_pitch must be convertible to float and strictly positive for meaningful musical results.
        - The Note instance may be in any state; the method does not require prior initialization beyond being a Note object.
    Postconditions:
        - self.name is a valid note name string as produced by notes.int_to_note for indices 0..11.
        - self.octave is an integer computed from the internal scaled logarithmic value; no bounds are enforced here (octave may be negative for very low frequencies).
        - The method returns the same Note instance (self), allowing chaining.

## Implementation details (behavioral summary, not code):
    - Computes an internal 'value' as:
        value = (log((float(hertz) * 1024) / standard_pitch, 2) + 1.0/24) * 12 + 9
      This formula aligns the numeric result so that the typical reference (standard_pitch == 440) yields A4 for 440 Hz.
    - Determines note name by converting int(value) modulo 12 into a note string using notes.int_to_note.
    - Determines octave by integer-dividing value by 12 and then subtracting 6.
    - Truncation of the floating 'value' with int() causes rounding toward the lower integer for positive values; noisy or boundary frequencies can map to either adjacent semitone depending on tiny differences.

## Side Effects:
    - Mutates the Note instance (self.name and self.octave).
    - No I/O, no external service calls, and no mutation of objects other than self.

### `mingus.containers.note.Note.to_shorthand` · *method*

## Summary:
Returns the note represented in "shorthand" notation by combining the note name (case chosen by octave) with commas (for lower octaves) or apostrophes (for higher octaves). Does not modify the Note object.

## Description:
Known callers and usage context:
- No internal callers within the Note class were found. This method is the canonical serializer to the shorthand form and is expected to be invoked by external code that needs a compact textual representation of a Note (for display, exporting to ABC/tablature-like formats, serialization, or to round-trip with from_shorthand).
- It is implemented separately because conversion to shorthand is a distinct responsibility (presentation/serialization) that should be symmetric with from_shorthand. Keeping it as its own method centralizes formatting rules and avoids duplicating the octave/punctuation logic elsewhere.

Behavior summary:
- Uses octave 3 as the baseline (no punctuation). For octaves >= 3 the note name is converted to lowercase; for octaves < 3 the name is used as-is. Then punctuation is appended:
  - For octave values > 3, each octave above 3 adds one apostrophe (') per octave.
  - For octave values < 2 (i.e., o = octave - 3 < -1) it appends one comma (,) for each step below octave 2, stopping when the internal offset reaches -1.
- The returned string is the note name (possibly lowercased) followed by zero or more commas or apostrophes.

## Args:
    None

## Returns:
    str: The shorthand representation.
    - Examples of mapping (illustrative, not exhaustive):
        * octave == 3 -> lowercased note name, no punctuation (e.g., "c", "f#", "Bb" -> "c", "f#", "bb" depending on name case/accidentals)
        * octave == 2 -> original note name (no punctuation)
        * octave == 1 -> original note name followed by one comma (e.g., "C,")
        * octave == 4 -> lowercased note name followed by one apostrophe (e.g., "c'")
    - Edge cases:
        * If name is an empty string and octave < 3, the method returns one or more commas (e.g., octave=0 -> ",,").
        * Accidentals (# or b) are preserved; lowercasing affects letters only (e.g., "C#" -> "c#").

## Raises:
    None. The method does not perform validation and will not raise even if self.name or self.octave are unexpected types; callers should ensure those attributes are valid if necessary.

## State Changes:
    Attributes READ:
        - self.name
        - self.octave
    Attributes WRITTEN:
        - None (the Note instance is not modified)

## Constraints:
    Preconditions:
        - self.name is expected to be a string containing the note name and optional accidentals (e.g., "C", "F#", "Bb"). The method does not enforce this.
        - self.octave is expected to be an integer. The method performs arithmetic on it; non-integer types may cause errors or unexpected behavior.
    Postconditions:
        - The Note object remains unchanged.
        - The returned value is a str representing the shorthand mapping described above.

## Side Effects:
    - None: no I/O, no external service calls, and no mutations of objects other than reading self.name and self.octave.

### `mingus.containers.note.Note.from_shorthand` · *method*

## Summary:
Parses a compact "shorthand" musician-style string (letters a-g/A-G, accidentals '#'/ 'b', and octave markers ',' / "'") and updates the Note's name and octave accordingly; returns the Note instance (self) on success.

## Description:
Parses a shorthand notation into a note name and octave and delegates validation and final assignment to the existing set_note(...) method. This function is the inverse of to_shorthand() (which emits this form) and keeps parsing logic localized so callers can convert human-friendly shorthand into a fully-validated Note in one step.

Known callers and typical context:
- No internal repository callers are required for this method to be useful; it is intended for use by higher-level parsing code, user code, tests, or any component that needs to convert the textual shorthand produced by to_shorthand() back into a Note.
- Typical lifecycle: used during input parsing or when reading compact textual note representations (e.g., user input, file formats, or REPL utilities), before the note is played, transposed, or serialized elsewhere.

Why this is its own method:
- Parsing shorthand is a distinct responsibility from validation and assignment (set_note). Isolating parsing here keeps the string-to-(name,octave) logic testable and symmetric with to_shorthand(), while reusing set_note for validation and actual state mutation.

## Args:
    shorthand (str): An iterable string containing:
        - base note letters: 'a'..'g' (lowercase) or 'A'..'G' (uppercase)
            * A lowercase base letter sets a baseline octave of 3 for that letter.
            * An uppercase base letter sets a baseline octave of 2 for that letter.
        - accidentals: '#' or 'b' appended to the base letter to form names like 'C#' or 'Db'
        - octave markers:
            * "," (comma) decreases octave by 1 per comma
            * "'" (apostrophe) increases octave by 1 per apostrophe
    Notes about allowed forms:
        - The method processes the string character-by-character and uses the last base letter (a-g/A-G) seen as the definitive note letter and baseline octave. Accidentals are only meaningful if they appear after that last base letter; accidentals occurring before the last base letter will effectively be overwritten (ignored) when a later base letter is encountered.
        - The shorthand must contain at least one base letter a-g or A-G for a meaningful result; otherwise validation will fail in set_note.

## Returns:
    Note (self): On success, returns the same Note instance (self) after delegation to set_note(...). The returned object has:
        - self.name: the uppercase base letter possibly followed by '#' or 'b' accidentals (e.g., 'C', 'F#', 'Eb')
        - self.octave: computed baseline (2 for uppercase base, 3 for lowercase base) plus/minus markers seen after the last base letter
    Edge-case returns:
        - If parsing produces an invalid name (for example empty name or not a valid note string), the method will not return; set_note will raise NoteFormatError instead.

## Raises:
    NoteFormatError: Raised when the computed name/octave pair is not a valid note representation as determined by set_note(...) (for example, when no base letter was present in shorthand or the name is not recognized by notes.is_valid_note).
    TypeError: If shorthand is not iterable (e.g., None or a non-iterable object), the for x in shorthand iteration will raise a TypeError before any validation occurs.
    (No other exceptions are generated by this method itself; set_note may raise NoteFormatError as described.)

## State Changes:
    Attributes READ:
        - None of self's attributes are read by this method prior to mutation. (All parsing is performed from the shorthand argument.)
    Attributes WRITTEN:
        - self.name (set by set_note)
        - self.octave (set by set_note)
    Notes:
        - This method delegates to set_note(name, octave, {}) which performs the actual assignment; because an empty dynamics dict is passed, velocity and channel are not modified here.

## Constraints:
    Preconditions:
        - shorthand should be an iterable of characters (typically a str).
        - shorthand must include at least one base letter in a-g or A-G to produce a valid name; otherwise set_note will raise NoteFormatError.
        - Accidentals intended to apply to the chosen base letter must appear after the last base letter in the string.

    Postconditions:
        - If the method returns successfully:
            * self.name is a valid note name (as accepted by notes.is_valid_note) consisting of an uppercase letter A-G optionally followed by accidentals ('#' or 'b').
            * self.octave equals the last base letter's baseline octave (2 if that letter was uppercase, 3 if lowercase) plus the net count of apostrophes "'" (each +1) and commas "," (each -1) that appear after that last base letter.
        - If the method does not return (an exception is raised), the Note's state may be unchanged or partially changed depending on where the exception was thrown inside set_note; callers should assume failure means no guarantee about state unless they inspect/catch the exception.

## Side Effects:
    - No I/O, no network access.
    - Mutates the Note instance (self) via set_note(...).
    - No external objects are mutated beyond self.
    - Does not modify velocity or channel because it always passes an empty dynamics dict to set_note.

### `mingus.containers.note.Note.__int__` · *method*

## Summary:
Return the absolute semitone index for this Note as an integer computed from its octave and name (including accidentals). This does not modify the Note.

## Description:
Converts the Note object's pitch into a single integer semitone count using the formula:
    semitone_index = (self.octave * 12) + base + accidental_adjustments

- The base is obtained by calling notes.note_to_int(self.name[0]) which maps the base letter (A–G) to 0..11.
- Each subsequent character in self.name is inspected: '#' increases the result by 1, 'b' decreases it by 1; any other characters are ignored by this method.
- The final value is returned directly (no modulo is applied here, so results can be negative if octave and accidentals produce a negative value).

Known callers / contexts:
- Comparison operators on Note (e.g., __lt__, __eq__) call int(self) to compare pitches numerically.
- Note.measure(other) computes the interval distance by subtracting int(self) from int(other).
- Note.to_hertz(standard_pitch) converts the semitone index to a frequency.
- Other numeric/pitch conversions (from_int, from_hertz, transposition logic) rely on this integer representation.

Why a separate method:
- Conflates a canonical numeric representation used across comparisons, interval math, and frequency conversions. Having a single implementation ensures consistent numeric semantics and allows Python's int() protocol to be used naturally.

## Args:
    None

## Returns:
    int: The computed semitone index = self.octave * 12 + base + accidental_adjustments.
    - base comes from notes.note_to_int(self.name[0]) and is effectively in 0..11 before accidental adjustments.
    - accidental_adjustments is the net count of '#' (+1) and 'b' (-1) characters found in self.name[1:].
    - The return value is an integer when preconditions are met (see Constraints). It may be negative for low octaves/flattened notes.

## Raises:
    NoteFormatError: If notes.note_to_int(self.name[0]) raises due to an invalid first character (i.e., self.name[0] is not a recognized base note).
    IndexError: If self.name is an empty string (accessing self.name[0] will raise IndexError).
    TypeError: If self.octave is not a numeric type that supports multiplication by 12 and addition with ints, Python may raise a TypeError; callers should ensure octave is an integer.

## State Changes:
    Attributes READ:
        self.name
        self.octave
    Attributes WRITTEN:
        None (this method does not modify the Note instance)

## Constraints:
    Preconditions:
        - self.name must be a non-empty string whose first character is a valid base note letter (A–G) as accepted by notes.note_to_int.
        - self.name may include accidentals in subsequent characters; only '#' and 'b' affect the computed value.
        - self.octave should be an integer (or integer-like numeric) representing the octave number.
    Postconditions:
        - Returns an integer semitone index consistent with the Note's pitch.
        - The Note object's attributes remain unchanged.

## Side Effects:
    - Calls notes.note_to_int(self.name[0]) (pure computation).
    - No I/O, no external services, and no mutation of objects outside of self.

### `mingus.containers.note.Note.__lt__` · *method*

## Summary:
Determine whether this Note represents a strictly lower pitch than another object by comparing their integer semitone indices; does not modify either operand.

## Description:
Compares self and other by converting both to integer semitone indices and returning the result of the numeric less-than comparison.

Known callers (present in this codebase):
- Note.transpose: uses this comparison to detect octave crossing when transposing (e.g., the code checks if self < Note(old, o_octave)).
- Other Note comparison methods in the same class (__gt__, __le__, __ge__, __ne__) depend on this implementation to provide full ordering semantics.

Typical uses (common but not explicitly listed in the source):
- Sorting or ordering collections of Note objects with Python's sorted() or list.sort(), and user code that compares Note instances.

Why a separate method:
- Implements Python's rich comparison protocol so Note instances can be compared and ordered consistently.
- Centralizes conversion-to-int then compare logic so other methods and external consumers rely on a single, well-defined behavior.

## Args:
    other (object): The right-hand operand to compare.
        - Allowed values:
            * None: explicitly handled (returns False).
            * Note instance or any object accepted by int(): int(other) is used.
        - No default value.

## Returns:
    bool: True if int(self) < int(other); False otherwise.
        - If other is None, returns False.
        - If int(other) succeeds and int(self) < int(other), returns True; otherwise False.

## Raises:
This method does not explicitly raise new exceptions; it propagates exceptions raised during conversion to integer values:

    - IndexError: If self.name is empty (self.__int__ accesses self.name[0]) or other.__int__ implementation raises it.
    - TypeError: If other is not None and int(other) fails because other is not an int-convertible object.
    - Any exceptions raised by notes.note_to_int or related helpers used by Note.__int__ (for example when the note name is invalid) — these propagate up unchanged.

Exact triggering conditions:
    - self.name == "" (empty string) causes IndexError when computing int(self).
    - self.name contains an invalid base note token such that notes.note_to_int raises an error.
    - other lacks an integer conversion and int(other) raises TypeError (or ValueError depending on other.__int__).

## State Changes:
    Attributes READ:
        - self.name (used indirectly via int(self))
        - self.octave (used indirectly via int(self))
    Attributes WRITTEN:
        - None.

## Constraints:
    Preconditions:
        - self.name should be a valid, non-empty note string recognized by notes.note_to_int (examples: "C", "C#", "Db").
        - self.octave should be a valid integer.
        - other must be None or convertible by int().

    Postconditions:
        - No mutation to self or other.
        - A boolean value reflecting the semitone ordering is returned.

## Side Effects:
    - None. The method performs no I/O, logging, network access, or mutations of external objects.

## Implementation details (behavioral mapping):
    - The integer semitone index used for comparison is computed by Note.__int__ as:
        * base = octave * 12 + notes.note_to_int(first_letter_of_name)
        * adjust by +1 for each '#' and -1 for each 'b' in the remaining characters of the note name
    - Therefore, comparison is by absolute semitone number: higher integer means higher pitch across octaves.

### `mingus.containers.note.Note.__eq__` · *method*

## Summary:
Compares this note's absolute pitch to another value and returns True when they represent the same pitch; does not modify the object.

## Description:
This equality operator determines whether two pitch representations refer to the same absolute semitone number by converting both operands to their integer pitch values and comparing them.

Known callers and contexts:
- Note.__lt__, Note.__gt__, Note.__le__, Note.__ge__, and Note.__ne__ call or rely on __eq__ when implementing other comparison semantics within the Note class.
- Note.transpose uses comparison operators (which in turn may call __eq__) when deciding whether to increment/decrement the octave after transposition.
- Any external code that compares Note instances (for equality checks, membership tests, or sorting helpers that test equality) will invoke this method.

Why this logic is a separate method:
- Centralizes the notion of equality between pitch-bearing objects as "same integer pitch" so all comparisons remain consistent and rely on the single canonical conversion implemented by __int__.
- Keeps comparison semantics simple and symmetric for interoperability with other objects that can be converted to integers (e.g., integer MIDI note numbers or other Note-like objects).

## Args:
    other (object): The value to compare against. Allowed values:
        - None: handled explicitly (returns False).
        - Note instances: handled via their __int__ implementation.
        - Integers or objects implementing __int__ / convertible by int(): compared by their integer representation.
    There is no default value.

## Returns:
    bool: True if both operands convert to the same integer pitch value (int(self) == int(other)); False if they differ or if other is None.
    Edge cases:
        - If other is None, returns False.
        - If conversion of either operand to int fails (see Raises), an exception propagates instead of returning False.

## Raises:
    TypeError: If int(other) cannot convert the provided other object (e.g., other has no __int__ and is not otherwise convertible).
    ValueError: If int(other) raises ValueError during conversion (for example, from an invalid string).
    IndexError: If self has an invalid/empty name (for example, name == ""), __int__ may index self.name[0] and raise IndexError. (Calling __eq__ on a Note with an empty name will therefore raise IndexError.)

## State Changes:
    Attributes READ:
        - self.name (via Note.__int__ which inspects name characters to compute accidentals)
        - self.octave (via Note.__int__)
    Attributes WRITTEN:
        - None (this method does not modify self or other)

## Constraints:
    Preconditions:
        - self.name must be non-empty and represent a valid/parsable note character sequence; otherwise __int__ may raise IndexError or other errors.
        - other must be either None or convertible to an integer via int(other) (or be a Note-like object providing __int__).
    Postconditions:
        - No mutation of self or other.
        - A boolean is returned when no conversion/validation errors occur.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of any object (no side-effecting operations on self or other).
    - Exceptions from integer conversion or from Note.__int__ may propagate to the caller.

### `mingus.containers.note.Note.__ne__` · *method*

## Summary:
Return the logical negation of the Note object's equality comparison with another object; this does not modify the Note instance.

## Description:
Implements Python's "!=" operator for Note by delegating to the class's equality comparison and negating its result. Known callers and contexts:
- The Python interpreter when user code writes "note_a != note_b".
- Any library or application code that performs inequality checks on Note instances (unit tests, validation routines, conditional guards).
- Indirect calls from higher-level operations that use inequality, e.g., filtering lists with a predicate that uses "!=".

This logic is its own method to provide a canonical, overridable implementation of inequality that is consistent with the class's __eq__ behavior. It centralizes "not-equal" semantics so subclasses or changes to __eq__ do not need to duplicate negation logic. The method intentionally does not attempt its own comparison logic; it relies on Python's equality resolution (including attempting reflected comparisons) to produce a boolean before applying negation.

## Args:
    self (Note): The left-hand Note instance participating in the comparison.
    other (object): Any Python object to compare against; typically another Note but may be any type.

## Returns:
    bool: True if the two operands are considered not equal; False if they are equal. The expression used internally is the interpreter-resolved result of "self == other" (which the interpreter converts to a boolean according to Python's rich comparison rules — for example, if __eq__ returns NotImplemented the interpreter will try the reflected comparison or fall back to default behavior). This method itself always returns a boolean and never returns NotImplemented.

## Raises:
    Any exception raised by the equality machinery (__eq__ on self or a reflected __eq__ on other) will propagate directly. This method does not catch exceptions.

## State Changes:
Attributes READ:
    - None directly within this method. It invokes the equality operation (self == other), so any attributes __eq__ reads are accessed there, not here.
Attributes WRITTEN:
    - None. No mutation of self or other occurs in this method.

## Constraints:
Preconditions:
    - None beyond those required by __eq__. self should be a properly initialized Note; other may be any object.
Postconditions:
    - self remains unchanged.
    - The call returns the boolean logical negation of the interpreter-resolved equality comparison between self and other.

## Side Effects:
    - None performed by this method itself (no I/O, no external service calls). Any side effects are the result of code executed inside __eq__ or other reflected comparison implementations invoked by the interpreter.

### `mingus.containers.note.Note.__gt__` · *method*

## Summary:
Return True if this Note represents a strictly higher pitch than the provided operand; does not modify the Note.

## Description:
This implements the rich comparison "greater-than" semantics for Note objects by delegating to the class's less-than and equality logic and negating their result. Known callers and contexts:
    - Note.transpose: used when adjusting octave after transposition to detect whether the note moved upward relative to a previous Note instance.
    - Any code that directly compares Note instances using the > operator (including user code and test suites).
    - Sorting or ordering code that explicitly uses > between Notes (though Python's sorting typically uses __lt__).

Why this is a separate method:
    - It provides the standard Python > operator for Note instances while keeping the comparison logic DRY by delegating to the already-implemented __lt__ and __eq__ methods. This avoids repeating integer-conversion and comparison logic and ensures consistent behavior across all comparison operators.

## Args:
    other: any object that is meaningful to compare with this Note.
        - Typically a Note instance, an integer (treated as MIDI-like semitone integer), or any object implementing __int__.
        - None is a valid input type (see edge-case behavior below).

## Returns:
    bool:
        - True if this Note is considered strictly greater (higher pitch) than other.
        - False if this Note is not strictly greater (i.e., it is less than or equal to other).
        - Edge-case: when other is None, __lt__ and __eq__ both return False, so this method returns True for any Note compared to None.

## Raises:
    Propagates exceptions raised by the underlying comparisons (__lt__ and __eq__), for example:
        - TypeError or ValueError when int(other) fails because other is not convertible to an integer or does not implement __int__.
    No exceptions are raised explicitly by this method itself.

## State Changes:
    Attributes READ:
        - self.name (accessed indirectly via int(self) in __lt__/__eq__)
        - self.octave (accessed indirectly via int(self) in __lt__/__eq__)
    Attributes WRITTEN:
        - None (this method does not modify self or other)

## Constraints:
    Preconditions:
        - self must be a properly-initialized Note instance (valid name and octave).
        - other should be a Note, an int, or an object implementing __int__ to avoid conversion errors.
    Postconditions:
        - The Note instance is unchanged.
        - A boolean result is returned describing the > relation according to integer pitch comparison.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside self.
    - Any exceptions from int() conversions on other will propagate to the caller.

### `mingus.containers.note.Note.__le__` · *method*

## Summary:
Return a boolean indicating whether this Note's pitch is less-than-or-equal-to another value; does not modify the Note.

## Description:
Implements the Python <= rich-comparison for Note by delegating to the class's < and == semantics (i.e., __lt__ and __eq__). This method is called whenever Python evaluates expressions using <= with a Note instance on the left-hand side.

Known callers / contexts:
    - Any user code that performs comparisons with <= on Note instances.
    - Built-in and library operations that use <= explicitly (for example, algorithms performing bound checks).
    - Sorting or selection code that may evaluate <= as part of complex comparisons (e.g., when user code or utilities use <= directly).
    - Note: many internal operations in this class use <, > or == (e.g., transpose uses < and >), but there are no internal callers of __le__ in the class shown.

Why this is a separate method:
    - Conforms to Python's data model for rich comparisons so expressions using <= invoke this method.
    - Keeps comparison semantics centralized and consistent with __lt__ and __eq__ rather than duplicating logic at call sites.

## Args:
    other (Note | int | object with __int__ | None):
        - Expected types:
            * Note instance: compared by integer pitch (via Note.__int__).
            * int (or any object convertible via int() / implementing __int__): compared to int(self).
            * None: handled specially by delegated comparisons (both __lt__ and __eq__ return False for other is None).
        - No default — supplied implicitly by the Python <= operator.

## Returns:
    bool
        - True if self < other or self == other according to the Note class semantics.
        - False otherwise.
        - Special-case: when other is None, returns False (because both delegated comparisons return False).

## Raises:
    - IndexError: If self.name is empty, int(self) accesses self.name[0] and will raise IndexError; thus calling <= on an "empty" Note will raise IndexError.
    - TypeError: If other is not None and cannot be converted to int (int(other) raises TypeError), that exception will propagate from the delegated comparisons.
    - ValueError: If conversion int(other) raises ValueError, that will propagate.
    Notes:
        - __le__ does not catch exceptions raised by __lt__ or __eq__; any exceptions coming from int(self) or int(other) will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.name (read indirectly via int(self))
        - self.octave (read indirectly via int(self))
    Attributes WRITTEN:
        - None (the method performs no mutations)

## Constraints:
    Preconditions:
        - self must be a Note with a valid non-empty name (calling __le__ on a Note whose name == "" will raise IndexError).
        - other must be None, a Note, or an object convertible to int (or else int(other) will raise and propagate).
    Postconditions:
        - No change to self or other.
        - The return value is a boolean consistent with the semantics of __lt__ and __eq__ on Note, or an exception is raised if conversion fails.

## Side Effects:
    - None external: no I/O, no network calls, no mutation of external objects.
    - Possible propagation of exceptions from integer conversion routines (see Raises).

## Examples (illustrative):
    - If self represents C-4 and other represents C-4, returns True.
    - If self represents C-4 and other represents C-5, returns True.
    - If other is None, returns False.
    - If other is an integer (or object where int(other) is defined), comparison uses int(self) compared to int(other); invalid conversions raise exceptions.

### `mingus.containers.note.Note.__ge__` · *method*

## Summary:
Returns True when this note is not strictly lower in pitch than the other operand; does not modify the object.

## Description:
This rich-comparison operator implements "greater than or equal" by delegating to the class's strict-less-than logic and negating its result (i.e., returns not (self < other)). Known callers and contexts:
- External user code that performs ordering checks using the >= operator on Note instances (for example, conditional checks, sorting helpers that explicitly test >=, or domain logic comparing pitches).
- Comparison-heavy algorithms or utilities that rely on all six comparison operators being defined for Note objects.
- Note.transpose and other internal methods may indirectly use comparison semantics during pitch manipulation (transpose itself uses < and > directly).

Lifecycle stage / pipeline:
- Invoked at runtime whenever a Note is compared to another pitch-like value (another Note, an integer MIDI pitch, or any object convertible via int()) using >=. Comparisons typically occur during pitch arithmetic, sorting, or logical checks.

Why this is a separate method:
- Delegating to __lt__ centralizes ordering semantics and avoids duplicating integer-conversion and pitch comparison logic. This keeps behavior consistent with other comparisons implemented in the class and reduces maintenance surface for subtle ordering rules (e.g., how None is handled).

## Args:
    other (object): The right-hand operand to compare against. Allowed values:
        - None: explicitly handled by __lt__ (see Returns / Edge cases).
        - Note instances: compared by their integer pitch via __int__().
        - int or any object supporting int(): compared by converting to int(other).
    There is no default value.

## Returns:
    bool: True if this object is not strictly less than other (i.e., greater than or equal in pitch), otherwise False.
    Edge-case behavior:
        - If other is None, __lt__ returns False, so this method returns True (i.e., a Note is considered >= None under the class's defined semantics).
        - If conversion of either operand to int raises an exception, that exception propagates (see Raises).

## Raises:
    TypeError: Propagated if int(other) is not possible because other lacks an __int__ or is otherwise non-convertible.
    ValueError: Propagated if int(other) raises ValueError during conversion.
    IndexError: Propagated if computing int(self) fails due to an invalid/empty self.name (e.g., name == "" causes indexing inside __int__ to fail).
    Any exception that __lt__ or Note.__int__ can raise will propagate unchanged.

## State Changes:
    Attributes READ:
        - self.name (accessed indirectly via Note.__int__)
        - self.octave (accessed indirectly via Note.__int__)
    Attributes WRITTEN:
        - None (this method does not modify self or other)

## Constraints:
    Preconditions:
        - No mutation prerequisites are required.
        - If other is not None, both operands must be suitable for integer conversion:
            * self.name must be a valid, non-empty note representation so that int(self) succeeds.
            * other must be either a Note-like object or convertible via int().
    Postconditions:
        - self and other remain unchanged.
        - A boolean value is returned if no conversion error occurs.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self.
    - Exceptions from integer conversion or from Note.__int__ may propagate to the caller.

### `mingus.containers.note.Note.__repr__` · *method*

## Summary:
Return a compact, developer-oriented textual representation of the Note showing its name and octave enclosed in single quotes and separated by a hyphen (for example: "'C-4'"). The method is read-only and does not modify the Note.

## Description:
This method defines the canonical object representation used by:
- repr(note) (explicit calls)
- the interactive REPL when a Note is evaluated
- implicit repr() when a Note appears inside container representations (e.g., repr([note]))
- debugging and logging code that prints object representations

It is implemented as __repr__ so Python's object model will use it automatically for representation purposes. The formatting logic is kept here (rather than in callers) to guarantee a single, consistent textual form for all introspection and debugging scenarios.

Implementation contract (how to reimplement exactly):
- Read self.name and self.octave.
- Convert name to its string form (equivalent to str(self.name)).
- Format octave as a decimal integer.
- Return a string that exactly matches the pattern: a single leading single-quote character, then the name string, then a single hyphen, then the decimal integer representation of octave, then a single trailing single-quote character.
- The original implementation uses old-style formatting with the format string "'%s-%d'" and the tuple (self.name, self.octave). Reimplementations may use equivalent formatting (f"'{str(self.name)}-{int(self.octave)}'" or format) provided the produced string is byte-for-byte identical for the same inputs.

## Args:
    None

## Returns:
    str: The representation string of the form "'{name}-{octave}'".
        - Example 1: If self.name == 'C' and self.octave == 4 → "'C-4'"
        - Example 2: If self.name == 'F#' and self.octave == -1 → "'F#--1'" (note the negative sign)
        - The returned string always contains the surrounding single-quote characters and exactly one hyphen separating the name and the octave part.

## Raises:
    AttributeError: Accessing self.name or self.octave will raise AttributeError if those attributes are missing or not accessible on the instance.
    TypeError: If self.octave is not an integer and cannot be formatted by the decimal integer formatter used (the '%d' specifier), Python's formatting will raise a TypeError. Any exception raised while converting self.name to str() will propagate.

## State Changes:
    Attributes READ:
        - self.name
        - self.octave
    Attributes WRITTEN:
        - None (the method does not mutate the Note or external state)

## Constraints:
    Preconditions:
        - The instance must have readable attributes name and octave.
        - name should be convertible to a string (i.e., str(self.name) must not raise).
        - octave should be an integer or a value acceptable to integer-formatting (so that formatting with '%d' or an explicit int(...) conversion succeeds).

    Postconditions:
        - The Note instance remains unchanged.
        - A string matching "'{name}-{octave}'" is returned when formatting succeeds.

## Side Effects:
    - None: no I/O, no network or external service calls, and no mutation of objects outside self.

