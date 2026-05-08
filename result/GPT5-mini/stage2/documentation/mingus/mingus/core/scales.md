# `scales.py`

## `mingus.core.scales.determine` · *function*

## Summary:
Returns the names of scale types (as strings) whose note collections contain all of the supplied notes; a scale matches if every supplied note appears in either its ascending or its descending sequence.

## Description:
- Known callers within the current codebase:
    - No direct internal callers were found in the provided memory snapshot. This function is a public helper intended for use by analyzer or discovery code that must infer candidate scales from a set or list of pitch identifiers.
- Typical calling context:
    - Called when a caller has an unordered collection (or list) of pitch identifiers (note name strings) and wants to know which named scales could contain those pitches (for example, when suggesting keys/scales that fit a melody fragment).
- Why this logic is extracted:
    - Encapsulates the matching policy (subset test against ascending() and descending() sequences of every known scale type and musical key) so callers don't need to iterate keys and scales and perform the same subset checks themselves.
    - Keeps concerns separated: scale classes provide sequences (ascending/descending), keys provides key descriptors, determine focuses on matching notes against those sequences and producing human-friendly scale names.

## Args:
    notes (iterable[str]):
        - An iterable of pitch identifier strings (for example: 'C', 'G#', 'Bb').
        - The function converts this parameter to a set, so elements must be hashable (strings are expected).
        - Allowed values: any iterable of note-name-like strings. Supplying an empty iterable is allowed (see Returns / edge cases).
        - Interdependencies: the exact format of each note string must be compatible with the _Scale subclasses' constructors and with get_notes() used for minor-key lookup; invalid formats may cause exceptions to propagate.

## Returns:
    list[str]:
        - A list of scale name strings (the value of each matched scale instance's .name attribute) for every scale where all provided notes are contained in either that scale's ascending() sequence or its descending() sequence.
        - If no scales match, returns an empty list [].
        - If the input notes set is empty, the empty set is a subset of every scale's note set; thus the function will append the name for every (key, scale subclass) combination tested and may return many names (including duplicates if the same name is appended multiple times across keys).
        - The list preserves the iteration order of keys and of _Scale.__subclasses__(): for each key in keys, for each concrete scale subclass, the function may append a matching scale name. Duplicate names are not deduplicated by this function.

## Raises:
    - Any exception raised by:
        * instantiating a scale subclass (scale(tonic)), or
        * calling scale(...).ascending() or scale(...).descending(), or
        * get_notes(key[1])[0]
      These exceptions are not caught and therefore propagate to the caller.
    - Typical propagated exception types (examples, not exhaustively created here) include:
        * NoteFormatError, FormatError, RangeError (may be raised by scale constructors or degree/notes utilities)
        * TypeError or AttributeError if `notes` is not iterable or contains non-hashable elements
        * IndexError if get_notes(...) returns an unexpected structure (e.g., empty list) and [0] is out of range

## Constraints:
- Preconditions:
    - keys (module-level variable) must be an iterable of indexable key descriptors such that key[0] yields the major-key tonic string and key[1] is usable with get_notes(...).
    - _Scale subclasses must implement ascending() and descending() and set .type (expected values include "major" and "minor") and .name.
    - Each note in the input must be in a format compatible with the scale implementations (typically normalized note-name strings).
- Postconditions:
    - The return value is a list of strings; no in-place mutation of the input iterable occurs (the input is converted to a set locally).
    - No global module state is changed by this function.

## Side Effects:
    - None performed directly by this function: it performs no I/O, does not modify global variables, and has no network or file interactions.
    - Any side effects are indirect and only occur if the invoked scale constructors or their ascending()/descending() implementations have side effects — such side effects are not caused by determine itself.

## Control Flow:
flowchart TD
    Start --> ConvertNotes[notes := set(notes)]
    ConvertNotes --> IterateKeys[for key in keys]
    IterateKeys --> IterateScales[for scale in _Scale.__subclasses__()]
    IterateScales --> IsMajor{scale.type == "major"?}
    IsMajor -- Yes --> MajorCheck[if notes <= set(scale(key[0]).ascending())\nor notes <= set(scale(key[0]).descending())]
    MajorCheck -- True --> AppendMajor[append(scale(key[0]).name)]
    MajorCheck -- False --> Continue1[continue]
    IsMajor -- No --> IsMinor{scale.type == "minor"?}
    IsMinor -- Yes --> MinorCheck[if notes <= set(scale(get_notes(key[1])[0]).ascending())\nor notes <= set(scale(get_notes(key[1])[0]).descending())]
    MinorCheck -- True --> AppendMinor[append(scale(get_notes(key[1])[0]).name)]
    MinorCheck -- False --> Continue2[continue]
    IsMinor -- No --> Continue3[continue (skip scale types not "major" or "minor")]
    Continue1 --> IterateScales
    Continue2 --> IterateScales
    Continue3 --> IterateScales
    IterateScales --> IterateKeys
    IterateKeys --> Return[return res]

## Examples:
- Basic usage (happy path):
    - Input: a melody fragment as a list of pitch names, e.g., ['C', 'E', 'G'].
    - Call: determine(['C', 'E', 'G'])
    - Behavior: returns a list of scale names where every of C, E, and G appears in the scale's ascending or descending note list. Example result might include names such as "C major" and other scale names that contain the triad notes, depending on the installed _Scale subclasses and the module-level keys mapping.

- Handling invalid note formats (error propagation):
    - If the provided note strings are invalid for the scale constructors (for example, malformed accidental syntax), determine(...) will re-raise the underlying exception (for example, NoteFormatError or FormatError). Caller should catch these if they wish to handle malformed input:
        - try:
            candidates = determine(['Cb', 'E##'])
          except NoteFormatError as e:
            handle_bad_notes(e)

- Empty input:
    - Because the function treats the input as a set and tests subset relation, determine([]) (or determine([]) where the empty iterable becomes an empty set) will be a subset of every tested scale sequence and therefore will collect many names; callers who want "no input => no matches" should treat the empty input specially before calling determine.

- Avoiding duplicate results:
    - If the caller desires a unique set of candidate scale names, wrap the result with set() or use an ordered deduplication after calling determine:
        - unique_candidates = list(dict.fromkeys(determine(notes)))

## Notes for implementers / reimplementing from scratch:
    - Iterate over the module-level keys and the concrete scale subclasses (by querying _Scale.__subclasses__()). For each combination:
        - If the subclass indicates it is a major-type scale, construct it with the major tonic (key[0]) and test whether the provided note set is a subset of that scale's ascending or descending note set.
        - If the subclass indicates it is a minor-type scale, determine the correct minor tonic with get_notes(key[1])[0], construct the scale with that tonic, and run the same subset checks.
    - Append the scale instance's .name to the result list whenever a match is found.
    - Do not swallow exceptions originating from scale construction or sequence generation — propagate them to the caller.

## `mingus.core.scales._Scale` · *class*

## Summary:
A minimal abstract base-class representing a musical scale anchored at a tonic note and spanning a number of octaves. _Scale encapsulates shared state and behavior used by concrete scale implementations.

## Description:
_Scale is intended to be subclassed by concrete scale types (major, minor, modal, etc.). It stores the tonic (root) note and the number of octaves the scale spans, and provides common operations used by callers: string/repr formatting, equality comparison, length, retrieving a specific scale degree, and a default descending ordering.

Typical callers
- Concrete scale classes in the same module or package (they call the _Scale constructor via super()).
- Client code that queries scale notes and degrees through a uniform interface.

Motivation and responsibility boundary
- Responsibility: declare and enforce the shared interface and minimal validation used across all scale implementations (tonic normalization check and degree lookup semantics).
- Not responsible for: producing the concrete note sequence for a particular scale type. That is the subclass's responsibility via implementing ascending().

Abstract contract for subclasses (important)
- Subclasses MUST implement ascending() to return a sequence (list-like) of note name strings ordered from the tonic upward.
- The returned ascending() sequence MUST include the final tonic at the top octave (i.e., the top-of-scale duplicate). This convention is relied upon by degree() which slices off the final element before indexing.
- ascending() must not mutate instance state (it should be a pure accessor that computes or returns a sequence).
- Subclasses should set self.name (str) so __repr__ is meaningful.
- Implementers may assume self.tonic is a valid note string according to the library's conventions (the base __init__ only rejects fully lowercase strings).

## State:
- tonic (str)
    - Description: the tonic (root) note for the scale (e.g., 'C', 'G#', 'F').
    - Set in __init__ from the note parameter.
    - Constraint: __init__ raises NoteFormatError when the provided note string is all-lowercase (note.islower() is True).
    - Invariant: remains equal to the constructor-supplied note unless mutated externally.

- octaves (typically int)
    - Description: how many octaves the scale should span.
    - Set in __init__ from the octaves parameter.
    - Constraint: the base class does not validate type or numeric range; subclasses should treat it as an integer and validate or interpret it appropriately.
    - Invariant: remains equal to the constructor-supplied value unless mutated externally.

- name (str, expected)
    - Description: human-readable name for the scale (e.g., "C major"). Not defined in the base class; subclasses should define it.
    - If absent, __repr__ may raise AttributeError.

Class invariants
- ascending() returns a list-like sequence of note strings ordered tonic-upward and including the top-octave tonic duplicate.
- Methods that query notes (degree, __len__, comparisons, __str__) rely on ascending()/descending() but must not change tonic/octaves.

## Lifecycle:
Creation
- Instantiate via a concrete subclass that calls super(...).__init__(note, octaves).
- Required: note (str) and octaves (usually int). If note.islower() is True, __init__ raises NoteFormatError.

Usage (typical order)
1. Instantiate a concrete subclass (e.g., MajorScale) with an uppercase tonic string and a sensible octaves value.
2. Call ascending() to obtain the ordered list of notes (must include final tonic duplicate).
3. Call descending() to get the reversed ordered list (base class returns list(reversed(ascending())) by default).
4. Use degree(n, direction) to fetch a specific degree (1-based). direction defaults to 'a' (ascending); use 'd' for descending.
5. Use len(instance) to obtain the number of elements returned by ascending().
6. Compare instances with == or !=; equality compares both ascending() and descending() sequences.

Destruction / cleanup
- No external resources allocated; no cleanup or context-manager protocol required.

## Method Map:
- __init__(note, octaves)
  -> sets tonic, octaves, may raise NoteFormatError

- ascending()
  -> abstract; subclasses MUST implement and return a list-like sequence of note strings ordered upward and including the final tonic duplicate; must not mutate self

- descending()
  -> default: returns list(reversed(self.ascending()))

- degree(degree_number, direction='a')
  -> validates degree_number >= 1 (raises RangeError otherwise)
  -> For direction == 'a': uses ascending()[:-1] (the ascending degrees excluding the final duplicate) and returns the element at index degree_number-1
  -> For direction == 'd': uses list(reversed(self.descending())[:-1]) (equivalent ordering for descending-degree lookup) and returns element degree_number-1
  -> direction defaults to 'a'; specifying any other value raises FormatError
  -> Note: callers should ensure degree_number is within 1..(len(ascending())-1) to avoid IndexError; the method does not explicitly check an upper bound.

- __len__() returns len(self.ascending())

- __eq__(other)
  -> Compares the ascending() sequences; if they match, compares the descending() sequences; returns True only if both match.

- __ne__(other)
  -> Implemented separately and returns not self.__eq__(other). This explicit implementation ensures Python's inequality semantics remain consistent and allows subclasses to only override __eq__ if desired.

- __repr__() uses self.name (subclasses should define name)
- __str__() formats ascending() and descending() sequences into readable text

Mermaid diagram (method call dependencies and typical invocation order):
graph TD
    A[__init__(note, octaves)] --> B[tonic, octaves set]
    B --> C[ascending()]:::abstract
    C --> D[descending()]
    D --> C
    C --> E[degree(...)]
    D --> E
    C --> F[__len__]
    F --> G[__eq__]
    H[__ne__] --> G
    classDef abstract fill:#f9f,stroke:#333,stroke-width:1px;

## Raises:
- NoteFormatError
    - Trigger: __init__ when provided note.islower() is True
    - Message: "Unrecognised note '%s'" % note

- NotImplementedError
    - Trigger: calling ascending() on the base class implementation (it raises NotImplementedError). Subclasses must override it.

- RangeError
    - Trigger: degree(degree_number, ...) when degree_number < 1

- FormatError
    - Trigger: degree(..., direction) when direction is not 'a' or 'd'

- IndexError (possible)
    - Trigger: degree(...) when degree_number exceeds the available degrees (no explicit upper-bound check is performed)

- AttributeError (possible)
    - Trigger: __repr__ if self.name is not defined in the subclass

## Example (prose)
1. Implement a concrete subclass (e.g., MajorScale) that:
    - defines self.name (str),
    - implements ascending() to return the ordered list of notes across the requested number of octaves, including the final tonic duplicate,
    - does not mutate instance state when generating the sequence.

2. Typical usage:
    - Instantiate the concrete subclass with a valid (non-lowercase) tonic and an octaves value.
    - Call ascending() to receive the ascending list of notes.
    - Call descending() to get the reversed list.
    - Call degree(1) to get the tonic, degree(5) to get the fifth degree; use direction='d' to query descending degrees.
    - Use len(instance) to learn the number of notes returned by ascending().

Developer tips
- Because the base class does not validate octaves, validate or coerce it in the subclass before building sequences.
- To provide clearer errors than raw IndexError from degree(), subclasses may override degree() or validate degree_number against len(ascending())-1.
- Define self.name in subclasses to make __repr__ robust and helpful.

### `mingus.core.scales._Scale.__init__` · *method*

## Summary:
Initializes the scale's core state by storing the supplied tonic note and octave span on the instance after performing minimal format validation on the tonic.

## Description:
Known callers and context:
- Concrete scale subclasses call this constructor via super(...) during object creation (e.g., MajorScale.__init__(...) will call super(MajorScale, self).__init__(note, octaves)).
- It is invoked at the construction/lifecycle stage when a caller creates a new scale instance; it performs the base-class validation and sets shared state used by other base- and subclass methods (ascending(), degree(), __len__(), etc.).

Why this logic is a dedicated method:
- Centralizes minimal validation and storage of the two fundamental pieces of scale state (tonic and octaves) so all concrete scale implementations share consistent behavior and invariants.
- Keeps subclasses focused on generating scale note sequences (ascending) rather than repeating tonal validation and state assignment.

## Args:
    note (str): The tonic/root note for the scale (e.g., 'C', 'G#', 'F'). Must not be an all-lowercase string; if note.islower() is True the constructor raises NoteFormatError. The method expects a string-like object that implements the islower() method.
    octaves (int or numeric): The number of octaves the scale should span. The base constructor stores this value verbatim and does not validate numeric range or type; subclasses are expected to interpret or validate it (typically an int >= 1).

## Returns:
    None: This is an initializer; it does not return a value.

## Raises:
    NoteFormatError:
        - Condition: raised when the provided note argument is a string and note.islower() returns True.
        - Message: "Unrecognised note '%s'" % note
    AttributeError (possible):
        - Condition: raised if the provided note argument does not support islower() (e.g., note is None or not a string-like object). This is not explicitly raised by the constructor but will occur because the code directly calls note.islower().
    (No other exceptions are explicitly raised by this method. Subclasses may raise additional exceptions during their own initialization.)

## State Changes:
    Attributes READ:
        - None of self.<attr> fields are read by this method.
    Attributes WRITTEN:
        - self.tonic: set to the provided note argument.
        - self.octaves: set to the provided octaves argument.

## Constraints:
    Preconditions:
        - The caller must supply a note argument that implements islower() (typically a str).
        - The caller must supply an octaves value; the base class does not provide a default.
    Postconditions:
        - If no exception is raised:
            * self.tonic == note
            * self.octaves == octaves
        - If note.islower() is True, the object is not constructed and NoteFormatError is raised.
        - No additional normalization or validation is performed on note or octaves by the base class.

## Side Effects:
    - No I/O, logging, or external service calls are performed.
    - The method only mutates the newly-created instance (sets two attributes). It does not mutate objects external to self or global state.
    - If a non-string note is supplied, an AttributeError may be propagated from calling note.islower().

### `mingus.core.scales._Scale.__repr__` · *method*

## Summary:
Returns a concise, human-readable representation of the Scale instance showing its name.

## Description:
This method produces the textual representation used by Python's built-in repr() and by default string-formatting operations that request an object's “official” representation (for example, the interactive interpreter, logging, or when repr() is explicitly called). It is invoked at the point in the runtime or developer workflow where a short, unambiguous description of the Scale object is required for debugging, display in collections, or logging.

This logic is provided as a dedicated __repr__ method to override Python's default object identity representation and to ensure consistent, readable output (a single-line string containing the scale's name) whenever an object's representation is requested. Keeping this logic in its own method follows Python conventions and allows other components to rely on a stable textual form without inlining formatting logic wherever a Scale is displayed.

## Args:
    None

## Returns:
    str: A single-line string in the form "<Scale object ('{name}')>" where {name} is the current value of self.name as formatted by Python's format mechanism. Example: "<Scale object ('C major')>".

    Edge cases:
    - If self.name contains special characters or quotes, those characters will appear verbatim inside the returned string.
    - If self.name's type defines a custom __format__ or __str__, that formatting will be used.

## Raises:
    AttributeError: If the instance does not have a 'name' attribute (attempting to access self.name).
    Any exception raised by evaluating or formatting self.name (for example, a custom __format__ or __str__ implementation on the name object that raises) will propagate.

## State Changes:
    Attributes READ:
        - self.name

    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The object must have a 'name' attribute that is readable.
        - No other invariants are required by this method.

    Postconditions:
        - The method returns a new string and does not mutate the Scale instance or any external state.
        - self.name remains unchanged.

## Side Effects:
    - None. The method performs no I/O and does not modify objects other than reading self.name.

### `mingus.core.scales._Scale.__str__` · *method*

## Summary:
Return a two-line, human-readable string that shows the scale's ascending notes on the first line and descending notes on the second.

## Description:
Constructs a canonical textual representation by calling the instance methods that produce the scale note sequences, joining each sequence with single spaces, and inserting them into the fixed template:
"Ascending:  {ascending-notes}\nDescending: {descending-notes}"
(Note: there are two spaces after "Ascending:" and one space after "Descending:" in the literal template.)

Known callers and contexts:
- Implicitly invoked by Python's str() built-in, print(), formatting operations, logging, or any code that converts a Scale instance to text for display, debugging, or user output.
- Typically used during REPL inspection, debugging output, command-line interfaces, or when generating textual reports that list scale degrees.

Why this is a separate method:
- Centralizes presentation formatting so all textual representations of a Scale are consistent.
- Keeps presentation concerns out of data-producing methods (ascending() and descending()).

## Args:
None.

## Returns:
str: A two-line string containing:
- Line 1: "Ascending:  " followed by the ascending notes joined by single spaces (e.g., "Ascending:  C D E F").
- Line 2: "Descending: " followed by the descending notes joined by single spaces (e.g., "Descending: E D C").

Edge cases:
- If self.ascending() or self.descending() yields an empty iterable, the corresponding line will end immediately after the label (e.g., "Ascending:  ").
- The returned string always contains a single newline character separating the two lines.

## Raises:
- TypeError: If any element returned by self.ascending() or self.descending() is not a str, the call to " ".join(...) will raise TypeError. This method does not convert non-str elements.
- Any exception raised by self.ascending() or self.descending() (for example, exceptions caused by invalid internal state) will propagate unchanged to the caller.

## State Changes:
- Attributes READ: None directly. The method invokes self.ascending() and self.descending(); any attributes those methods read are accessed indirectly but are not referenced by name here.
- Attributes WRITTEN: None. The method does not mutate the instance.

## Constraints:
Preconditions:
- The instance must implement ascending() and descending() methods that return iterables of str.
- The iterables must be finite and iterable; their elements must be strings.

Postconditions:
- The Scale instance remains unchanged.
- The caller receives a deterministic string that reflects the current outputs of ascending() and descending().

## Side Effects:
- None. No I/O, no external service calls, and no mutation of objects outside self.

### `mingus.core.scales._Scale.__eq__` · *method*

## Summary:
Returns True when the other object represents the exact same scale structure by having identical ascending and descending note sequences; otherwise returns False.

## Description:
This method implements Python's equality protocol for _Scale instances and is invoked when the == operator is used on scale objects. Within the same class, __ne__ delegates to this method to compute inequality. The equality test is structural: it compares the two objects' ascending() sequences first and, only if those are equal, compares their descending() sequences.

This logic is defined as a dedicated __eq__ method so that scale equality is centrally specified (sequence-level equality for both directions) rather than relying on object identity or ad-hoc comparisons.

## Args:
    other (object): Any object on which the method can call:
        - ascending() -> sequence
        - descending() -> sequence
    There is no static type checking; the method expects these callables to exist at runtime.

## Returns:
    bool:
        - True if self.ascending() == other.ascending() and self.descending() == other.descending().
        - False otherwise.
    Notes:
        - The implementation evaluates self.ascending() == other.ascending() first. If that comparison is False, the method returns False without calling descending() on either object.
        - Sequence equality uses Python's standard ordered, element-wise equality.

## Raises:
    AttributeError:
        - If 'other' does not provide ascending() or descending(), an AttributeError will be raised when attempting to access the missing attribute.
    NotImplementedError:
        - If self.ascending(), self.descending(), or the corresponding methods on other raise NotImplementedError (e.g., a subclass left ascending() unimplemented), that exception will propagate.
    Any other exception:
        - Any exception raised by ascending() or descending() (for either object) will propagate unchanged.

## State Changes:
    Attributes READ:
        - None directly by __eq__. The method does not access self.<attribute> fields itself.
        - Indirectly, __eq__ calls ascending() and descending(), which in concrete subclasses may read attributes such as self.tonic or self.octaves.
    Attributes WRITTEN:
        - None. __eq__ does not mutate self or other.

## Constraints:
    Preconditions:
        - self and other should expose callable ascending() and descending() methods that return sequences whose elements are comparable with ==.
    Postconditions:
        - No mutation of self or other.
        - The return value accurately reflects structural equality of ascending and descending sequences at the time of the call.

## Side Effects:
    - The method itself performs no I/O or external interactions.
    - Any side effects are solely those caused by the invoked ascending()/descending() implementations; __eq__ does not introduce additional side effects.

## Minimal behavioral examples (descriptive):
    - If both ascending() and descending() sequences match element-wise: returns True.
    - If ascending() sequences differ: returns False and descending() is not consulted.
    - If ascending() sequences match but descending() sequences differ: returns False.
    - If other lacks required methods: AttributeError is raised.

### `mingus.core.scales._Scale.__ne__` · *method*

## Summary:
Returns the logical negation of the scale equality test; determines inequality without mutating the object.

## Description:
This method implements Python's inequality protocol for _Scale instances and is invoked when the != operator is used on scale objects. It is a thin wrapper that delegates to the class's __eq__ implementation and returns its logical negation.

Known callers and context:
    - The primary caller is Python's interpreter when code evaluates `a != b` where a is an instance of _Scale (or a subclass).
    - Any library or application code that compares scale objects using != will invoke this method.
    - It is also indirectly used by container or collection operations that rely on inequality comparisons.

Why this is a separate method:
    - Defining __ne__ explicitly and delegating to __eq__ centralizes the equality semantics and ensures consistent behavior for both == and !=. It also avoids relying on Python's default fallback behavior and makes the intent explicit.

## Args:
    other (object): Any object to compare with self. There is no static type requirement, but __eq__ expects `other` to provide callable methods used by equality (see __eq__ documentation):
        - ascending() -> sequence
        - descending() -> sequence (may not be called if ascending() differs)

## Returns:
    bool:
        - True if the equality test (self.__eq__(other)) returns False.
        - False if the equality test returns True.
    Edge cases:
        - If __eq__ raises an exception, this method does not catch it; the exception propagates and no boolean is returned.

## Raises:
    Any exception raised by self.__eq__(other) will propagate unchanged. Common possibilities include:
        - AttributeError: if `other` lacks required methods (e.g., ascending()) that __eq__ attempts to call.
        - NotImplementedError: if ascending()/descending() on self or other are unimplemented in a subclass and raise this.
        - Any other exception raised during execution of ascending() or descending() (from either object).

## State Changes:
    Attributes READ:
        - None directly by __ne__ itself.
        - Indirectly, the delegated call to __eq__ (and the ascending()/descending() methods it calls) may read instance attributes such as:
            - self.tonic
            - self.octaves
        - Concrete subclasses of _Scale may read additional attributes when producing sequences.

    Attributes WRITTEN:
        - None. __ne__ does not modify self or other.

## Constraints:
    Preconditions:
        - self must implement __eq__ (this is true for _Scale).
        - For meaningful results, both self and other should expose ascending() (and, when reached by __eq__, descending()) and those methods must return comparable sequences.
    Postconditions:
        - No mutation of self or other.
        - A boolean result is returned unless an exception is raised by the delegated equality logic.

## Side Effects:
    - This method performs no I/O and makes no external service calls.
    - Any side effects originate solely from the operations performed inside __eq__ or the ascending()/descending() implementations called by __eq__; __ne__ introduces no additional side effects.

## Implementation note:
    - Correct reimplementation is a single expression: return not self.__eq__(other)

### `mingus.core.scales._Scale.__len__` · *method*

## Summary:
Returns the number of pitch entries in the scale's ascending representation as an integer (so built-in len(scale) reflects the size of ascending()).

## Description:
This method delegates to the instance's ascending() method and returns the length of the sequence returned by ascending(). Typical callers:
- The Python built-in len(scale_instance) (i.e., len(...) invokes this method).
- Any code that queries the scale's size for validation, display, or iteration logic.

Lifecycle/context:
- Invoked whenever a consumer needs the size of the scale (for example, UI display, validation, or algorithmic checks).
- It is intentionally small and delegative so that the scale size is always computed from the canonical ascending representation implemented by subclasses.

Why this is its own method:
- Exposing __len__ enables Pythonic usage (len(scale_instance)) and keeps sizing logic consistent: all callers use the same canonical source (ascending()) rather than duplicating length-calculation logic across the codebase.

## Args:
This method takes no arguments.

## Returns:
int
    - The integer length of the sequence returned by ascending().
    - Typical value: non-negative integer (0 or greater).
    - Important detail: the returned count is exactly len(self.ascending()). In many scale implementations ascending() includes the terminal/upper tonic (duplicate of the first degree at the next octave), so the reported length will include that element unless ascending() omits it.

## Raises:
- NotImplementedError
    - If the current class has not implemented ascending(), the call to ascending() will raise NotImplementedError (this is the base-class contract).
- TypeError
    - If ascending() returns a value that does not support the built-in len() operation (for example, a generator or an object without __len__), len(self.ascending()) will raise TypeError.
- Any other exception that ascending() may raise is propagated unchanged.

## State Changes:
Attributes READ:
    - None directly. This method only calls self.ascending(); any attributes read are those accessed inside ascending().

Attributes WRITTEN:
    - None. This method does not modify self or any of its attributes.

## Constraints:
Preconditions:
    - self must be a properly-initialized Scale instance.
    - ascending() should be implemented by the concrete subclass and should return a sized sequence (an object for which len(...) is valid) for predictable behavior.

Postconditions:
    - No mutation of self or external state.
    - The returned integer equals len(result) where result is the value returned by ascending().

## Side Effects:
    - None performed by __len__ itself.
    - Any side effects originate from ascending() (if a subclass implementation has side effects, those will occur because __len__ calls ascending()).

### `mingus.core.scales._Scale.ascending` · *method*

## Summary:
Declare the abstract contract for producing the scale's ascending sequence; in the base class this method is not implemented and must be implemented by subclasses to return the scale's notes (including the final octave duplicate) as a list of note name strings.

## Description:
Known callers and contexts:
- __str__: uses " ".join(self.ascending()) to render an ascending textual representation when printing the scale.
- __eq__: compares two scales by comparing their ascending() lists (and descending()) for equality.
- __len__: returns len(self.ascending()), so ascending() determines the length of the scale object.
- descending: implemented as list(reversed(self.ascending())), so descending() relies on ascending() to provide the full ascending sequence.
- degree: slices self.ascending()[:-1] to obtain the scale degrees (omitting the final duplicated tonic) and selects a degree by index.

Lifecycle stage / pipeline:
- This method is invoked any time the scale's notes are needed for display, comparison, indexing or retrieval of a specific degree. It is part of the public interface of a Scale object and therefore defines the canonical representation of the scale's notes.

Why this logic is a separate method:
- Different scale types (major, minor, modal, custom) compute the ascending pitch sequence using different interval patterns and octave spans. Placing this behavior in an overridable ascending() method provides a clear, testable contract for subclasses to implement while keeping common consumers (printing, degree lookup, equality) generic and unchanged.

## Args:
- None.

## Returns:
- list[str]: A sequence (list) of note names (strings). The sequence MUST be ordered from the tonic upward.
  - The returned list is expected to include the final tonic at the top of the highest octave (i.e., the octave-duplicated tonic). For example, a single-octave major-like scale for tonic 'C' commonly appears as ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C'].
  - Consumers in this class expect that removing the last element of the returned list yields exactly one representative of each scale degree per octave (see degree()).
  - The concrete element format should match the codebase's note string conventions (e.g., 'C', 'C#', 'Db', etc.) used elsewhere in mingus.core.notes.

## Raises:
- NotImplementedError: Always raised by the base class implementation to indicate that subclasses must implement this method.
- Implementers' guidance: a subclass implementation MAY raise RangeError (imported in the module) if its configuration (for instance, an octaves attribute) is out of an acceptable range. The base method itself does not perform such checks.

## State Changes:
Attributes READ:
- self.tonic: the tonic/starting note provided at construction; implementations will read this to seed scale generation.
- self.octaves: the number of octaves requested at construction; implementations will read this to determine how many octaves to generate.
- (Optional) self.name or other subclass attributes: subclass implementations may read additional attributes that describe the scale (e.g., interval pattern).

Attributes WRITTEN:
- None. The base method does not modify object state. Implementations should avoid mutating persistent object state when generating and returning the list; they should produce and return a new list.

## Constraints:
Preconditions:
- The instance must be properly constructed: __init__ already enforces that the tonic is not a lowercase string (it raises NoteFormatError if it is). Implementers should assume self.tonic is a valid note string according to the library's conventions.
- The octaves attribute should represent an integer octave count. The base class does not validate octaves; subclass implementations should validate octaves and raise RangeError for invalid values (for example, octaves < 1) if appropriate.

Postconditions:
- After successful return, self state is unchanged.
- The returned list:
  - Contains note name strings ordered from lowest (tonic) to highest.
  - Includes the final tonic at the topmost octave (duplicate of the first element transposed up by the number of octaves).
  - Has a length consistent with the chosen scale formula and number of octaves (consumers rely on len() and indexing into the list).

## Side Effects:
- None for the base implementation. Subclass implementations should avoid I/O, network access, or mutation of shared structures while producing the returned list.
- Implementations may use helper functions from mingus.core (for example, interval/notes helpers imported at module level) to compute transpositions or normalize accidentals, but those should not produce external side effects.

## Implementation guidance (enough to reimplement):
- Subclasses should:
  1. Validate self.octaves and raise RangeError if it's not a positive integer (recommended).
  2. Choose the interval sequence that defines the scale (intervals and repeated pattern across octaves).
  3. Starting from self.tonic, apply successive intervals to generate each degree; repeat for the requested number of octaves.
  4. Normalize note spellings as needed using the project's note utilities (augment/diminish/reduce_accidentals are available in this module).
  5. Return a new list of strings that begins with self.tonic and ends with the tonic transposed up by the requested octave span (i.e., the duplicated top tonic).

Example expected behavior (illustrative, not code):
- For a typical 1-octave heptatonic scale on tonic 'C', ascending() should return 8 elements where the final element is 'C' an octave higher than the first.

### `mingus.core.scales._Scale.descending` · *method*

## Summary:
Returns a new list of this scale's notes in descending order by reversing the sequence produced by the ascending() method. Does not modify the object's state.

## Description:
This method is a small convenience accessor used whenever a consumer needs the scale notes from highest to lowest pitch. Known internal callers in the _Scale class:
- __str__ — used when printing the scale to include a "Descending:" line.
- __eq__ — used when comparing scales for equality; both ascending and descending lists are compared.
- degree(direction="d") — used when retrieving a degree in descending order (degree constructs a reversed slice of the descending list).

Why this logic is its own method:
- It centralizes the descending-order view of the scale so subclasses can override descending() if they need a different descending algorithm or representation (for example, omitting the final octave duplication). Keeping it separate avoids duplicating reversed(list) calls throughout the codebase and provides a clear, testable contract.

## Args:
None.

## Returns:
list[str]
- A new list containing the notes of the scale in descending order.
- Typically this is the ascending() sequence with element order reversed.
- If ascending() returns an empty sequence, returns an empty list.
- The method always returns a concrete list object (not a lazy iterator).

## Raises:
- Propagates any exception raised by ascending(), for example:
    - NotImplementedError: if ascending() is not implemented by the concrete scale class.
    - Any other exception raised by ascending() (e.g., NoteFormatError) will propagate.
- TypeError: if ascending() returns a value that reversed() cannot consume (reversed() requires a sequence supporting __reversed__ or random access). In that case, the TypeError originates from the built-in reversed() call.

## State Changes:
Attributes READ:
- The method calls self.ascending(), so any attributes read by ascending() (commonly self.tonic and self.octaves) are read indirectly. The descending() method itself does not access any self.<attr> directly.
Attributes WRITTEN:
- None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
- self.ascending() must be implemented on the concrete instance and must return a reversible sequence of note tokens (e.g., list or tuple of strings) or an object that implements __reversed__.
- The returned elements from ascending() are expected to be note strings in the project's note format.

Postconditions:
- Returns a new list whose element order is the reverse of the sequence returned by self.ascending().
- The original object state (attributes and the value returned by ascending()) is not modified by this call.

## Side Effects:
- No I/O or external service calls.
- No mutation of objects outside self (a new list is created and returned).
- Any side effects from ascending() (if implemented to have side effects) will occur because descending() calls ascending(); descending() itself introduces no additional side effects.

### `mingus.core.scales._Scale.degree` · *method*

## Summary:
Return the note at the specified scale degree from this scale, selecting from the ascending form by default or the descending form when requested; does not modify the scale object.

## Description:
This method is the central accessor for retrieving a single degree (note) from the scale represented by this _Scale instance. It is intended to be used by callers that need a specific scale degree (for example, building chords, analysis, display, or transposition utilities).

Known callers and invocation context:
- Typical callers are external utilities or user code that query an instantiated scale for a particular degree when constructing chords, analyzing harmonic functions, or formatting scale information for display. There are no explicit internal callers referenced here; this is a public-facing convenience method on the _Scale type.
- It is typically invoked after a scale object has been constructed/populated (i.e., after initialization of a _Scale instance) and when a consumer needs the nth degree relative to the scale's tonic.

Rationale for being a dedicated method:
- Encapsulates degree-indexing details (ascending vs descending behavior and removal of the duplicate final octave) in one place so callers do not need to replicate the logic.
- Centralizes validation of the degree index and direction parameter and ensures consistent error types are raised for invalid inputs.

## Args:
    degree_number (int): 1-based index of the desired degree in the scale. Must be >= 1. There is no explicit upper bound check in the method; requesting a degree beyond the available notes will raise an IndexError.
    direction (str, optional): Which form of the scale to use:
        - "a" — use the ascending form (default)
        - "d" — use the descending form
      Any other value triggers a FormatError.

## Returns:
    str: The note representation at the requested degree. The concrete type and formatting of the returned note follow the scale implementation (typically a string note name, e.g., "C", "G#", "Bb").
    Edge-case returns:
      - If degree_number is larger than the number of degrees available in the selected direction, the method will raise an IndexError (propagated from the list access) rather than returning a sentinel value.

## Raises:
    RangeError: If degree_number < 1 (message: "degree '<n>' out of range").
    FormatError: If direction is not "a" or "d" (message: "Unrecognised direction '<dir>'").
    IndexError: If degree_number is greater than the number of notes available in the chosen direction (this is not explicitly caught by the method and will propagate).
    Other exceptions: Any exceptions raised by self.ascending() or self.descending() (if those methods raise) will propagate.

## State Changes:
    Attributes READ:
        - Calls self.ascending() (reads scale structure via that method)
        - Calls self.descending() (reads scale structure via that method) when direction == "d"
    Attributes WRITTEN:
        - None. This method does not modify any attributes of self.

## Constraints:
    Preconditions:
        - self must be a valid _Scale instance with functioning ascending() and descending() methods that return sequences (lists) of notes.
        - degree_number must be an integer >= 1.
    Postconditions:
        - On successful return, a note (string) is provided corresponding to the 1-based degree_number in the requested direction (ascending by default).
        - The state of self is unchanged.

## Side Effects:
    - No I/O, no external service calls.
    - No mutation of objects outside self.
    - Exceptions may be propagated to the caller.

## Implementation notes / behavior details:
    - For direction "a", the method uses self.ascending()[:-1] to drop the final duplicated octave note (so the scale degrees are indexed without counting the octave repetition).
    - For direction "d", the method uses list(reversed(self.descending())[:-1]) to reverse the descending list, drop its final element (which corresponds to the duplicated octave in the reversed order), and then index into that list so degree 1 corresponds to the tonic and increments upward.
    - The method returns notes[degree_number - 1] (1-based to 0-based conversion).

## `mingus.core.scales.Diatonic` · *class*

*No documentation generated.*

### `mingus.core.scales.Diatonic.__init__` · *method*

## Summary:
Initializes a Diatonic scale object by delegating base initialization to the parent, storing the provided semitones descriptor, and constructing a human-readable name for the instance.

## Description:
This constructor is invoked when a Diatonic scale instance is created. It performs two focused tasks:
- Delegates core initialization (such as storing the tonic and octave-related setup) to the parent class via its __init__ method.
- Stores the semitones information passed by the caller and composes the instance name using the already-initialized tonic.

Known callers and context:
- Any code that creates a Diatonic scale will call this method implicitly by instantiating the Diatonic class. Typical lifecycle: object construction / setup of a scale object before it is queried for notes or interval structure.

Reason for separate method:
- Initialization logic is short and primarily composes instance-level state (delegation to parent + storing the semitones description). Keeping this logic in the constructor centralizes object setup and ensures the Diatonic-specific field (semitones) and descriptive name are initialized immediately on construction.

## Args:
    note: The tonic passed through to the parent initializer. (No type is enforced in this method; validation, if any, is handled by the parent initializer.)
    semitones: The semitones descriptor/value provided by the caller. This method stores the value exactly as received on self.semitones.
    octaves (int, optional): Number of octaves to initialize for the scale. Defaults to 1. This value is forwarded to the parent initializer.

## Returns:
    None. As a constructor, it does not return a value; it initializes instance state.

## Raises:
    This method contains no explicit raise statements. Any errors resulting from invalid note or octaves values would originate from the parent class __init__ (invoked with note and octaves) and propagate out.

## State Changes:
Attributes READ:
    self.tonic - read when composing self.name (the tonic value is assumed to be set by the parent initializer).

Attributes WRITTEN:
    self.semitones - assigned the semitones argument.
    self.name - assigned a formatted string: "{tonic} diatonic, semitones in {semitones}" where tonic is the value of self.tonic after the parent initializer runs.

## Constraints:
Preconditions:
    - No preconditions are enforced in this method itself. It assumes the parent initializer will validate 'note' and 'octaves' as necessary.

Postconditions:
    - After the call, self.semitones contains the provided semitones argument.
    - After the call, self.name is a string formed from the instance's tonic and the semitones value.
    - The parent class initialization side effects (such as setting self.tonic) will have been applied before this method formats self.name.

## Side Effects:
    - Calls the parent class __init__ (super(Diatonic, self).__init__(note, octaves)), which may perform additional state mutation or validation. No I/O or external service calls are made directly by this method.

### `mingus.core.scales.Diatonic.ascending` · *method*

## Summary:
Generate and return the ascending diatonic scale starting from the object's tonic across the configured number of octaves; the returned list is the sequence of spelled pitch-classes (the top tonic is appended as the final element).

## Description:
- Known callers and usage context:
    - No direct callers were found in the inspected snapshot. Conceptually this method is invoked by consumers of a Diatonic scale object when a concrete ordered list of scale tones is required (for example: rendering a scale, generating melodic lines, building chords from scale degrees, or exporting a scale to other APIs).
    - Typical lifecycle: After a Diatonic instance is constructed (giving it a tonic, a semitone-pattern, and octaves), clients call ascending() to obtain the scale tones in ascending order for one or more octaves.
- Rationale for a dedicated method:
    - The logic composes repeated interval steps (major or minor seconds) according to a semitone pattern. Extracting it into its own method keeps scale construction, representation, and higher-level consumers clean and avoids duplicating the interval-stepping logic multiple places.

## Args:
    None

## Returns:
    list[str]:
        - A list of spelled pitch-class strings (each element is a base letter A-G optionally with accidentals like '#' or 'b'; octave digits are not produced by the interval helpers).
        - Elements represent successive ascending scale degrees starting at self.tonic and proceeding stepwise (major or minor seconds) according to self.semitones.
        - Length: 7 * self.octaves + 1
            * Explanation: the per-octave pattern yields 7 distinct scale degrees (tonic + 6 steps). The method repeats that 7-note pattern self.octaves times, then appends the initial tonic again as the top tone, producing one extra final tonic.
        - Example values (illustrative, not literal code):
            * If tonic is "C", semitones corresponds to the major diatonic pattern and octaves == 1, the returned list will look like ["C", "D", "E", "F", "G", "A", "B", "C"].
            * If octaves == 2, the same core 7-note pattern is repeated twice and a final "C" appended: ["C","D","E","F","G","A","B","C","D","E","F","G","A","B","C"].

## Raises:
    - Propagates any exception raised by the interval helper functions intervals.minor_second(...) and intervals.major_second(...). In practice this may include:
        * IndexError: if self.tonic is an empty string (interval helpers access note[0]).
        * NoteFormatError / FormatError: if self.tonic contains an invalid or unrecognized note format accepted by the underlying note/interval utilities.
        * KeyError, ValueError, TypeError: if underlying helpers encounter invalid inputs or internal mapping lookups fail.
    - The method itself does no explicit validation and therefore does not raise bespoke exceptions; callers should validate Diatonic attributes beforehand if they require earlier error reporting.

## State Changes:
    - Attributes READ:
        * self.tonic
        * self.semitones
        * self.octaves
    - Attributes WRITTEN:
        * None. The method does not modify any attributes on self.

## Constraints:
    - Preconditions:
        * self.tonic must be a valid, non-empty pitch string whose first character is a letter A-G (this is required by the interval helpers, which expect note[0] to exist and be a valid base letter).
        * self.semitones must be an iterable collection (e.g., set, list, tuple) containing integers that identify which step indices (1..6) are to be treated as semitone steps. The method iterates n in 1..6 inclusive and checks membership (n in self.semitones). Values outside 1..6 are ignored by the loop but are not meaningful for scale definition.
        * self.octaves must be an integer (practically >= 1). The method uses self.octaves to repeat the 7-note pattern; non-integer or negative values will produce unintended results (TypeError for non-integer when used in sequence repetition, or logically incorrect lengths for negative/zero values).
    - Postconditions:
        * The returned list contains ascending, stepwise-spelled pitch-classes where each step is either a minor second or a major second above the previous element depending on whether the step index appears in self.semitones.
        * The first element equals self.tonic.
        * The last element equals the spelled tonic again (notes[0]), representing the tonic at the top of the final octave.
        * No attributes on self are changed by the call.

## Side Effects:
    - No I/O is performed.
    - No global state is modified by this method itself.
    - The only side effects possible are those originating from the called helpers intervals.minor_second and intervals.major_second; those helpers are documented as pure and typically raise on invalid input but do not perform I/O. Any internal caches modified by lower-level utilities would be their responsibility and not this method's direct effect.

## `mingus.core.scales.Ionian` · *class*

## Summary:
Represents the Ionian modal scale (a major scale mode) anchored at a given tonic and spanning a specified number of octaves. Provides an ascending() accessor that returns the ordered note names for the Ionian mode.

## Description:
Ionian is a concrete subclass of the library's _Scale base class. It delegates the actual scale-step generation to the Diatonic helper by requesting the diatonic scale pattern for the tonic and then reshaping that sequence to span the requested number of octaves.

When to instantiate:
- When you need an Ionian-mode (major-mode) scale for a given tonic note (for example, to query scale degrees, render the scale, or perform harmonic/melodic processing).
- Typical callers include user code building scales, higher-level utilities that enumerate modal scales, or any code that expects a _Scale-compatible object (so it can call ascending(), descending(), degree(), len(), etc.).

Motivation / responsibility:
- Encapsulates the Ionian (major-mode) pattern as a distinct subclass so clients can instantiate Ionian(note, octaves) and obtain a standard ascending() result.
- Responsibilities:
  - Set a human-readable .name for display and repr purposes.
  - Provide ascending() that returns the Ionian-mode notes built from Diatonic(tonic,(3,7)).
- Not responsible for: validating tonic format beyond what _Scale enforces, or for implementing low-level note-step calculation (that is delegated to Diatonic).

Dependency contract (expectations of Diatonic):
- Ionian constructs Diatonic(self.tonic, (3, 7)) and calls its ascending() method.
- Ionian expects Diatonic.ascending() to return a list-like sequence of note-name strings ordered tonic-upward and to include the final tonic duplicate at the top octave (consistent with the _Scale class contract).

## State:
- type (class attribute)
    - Type: str
    - Value: "ancient"
    - Role: metadata describing the historical/classification grouping for Ionian (does not affect behavior).

- tonic (inherited from _Scale)
    - Type: str
    - Description: the scale's root note (e.g., "C", "G#", "F").
    - Constraints: set by _Scale.__init__; _Scale raises NoteFormatError if the provided note string is all-lowercase (note.islower() is True).
    - Invariant: remains equal to the constructor-supplied note unless mutated externally.

- octaves (inherited from _Scale)
    - Type: typically int (but not enforced by Ionian)
    - Description: how many octaves the returned scale should span.
    - Usage: used as the multiplier for list repetition during ascending() construction (see Behavior).
    - Notes on valid values:
        - Must be an integer for list-multiplication to be valid; if a non-integer is passed, Python will raise a TypeError when multiplying the list.
        - Zero or negative integers are permitted by the implementation (list repetition semantics apply), but they produce results that may not be musically meaningful (see edge cases).

- name (set by Ionian.__init__)
    - Type: str
    - Value: "{tonic} ionian" (for example, "C ionian")
    - Role: used for human-readable representation (__repr__, __str__).

Class invariants:
- ascending() must compute and return a list-like sequence of note strings (per the _Scale contract and Ionian's implementation).
- ascending() must not mutate instance state.

## Lifecycle:
Creation
- Constructor signature: Ionian(note, octaves=1)
    - note (str): required; passed to _Scale.__init__ which applies tonic-format validation.
    - octaves (optional, default 1): passed to _Scale.__init__ and used by ascending() to repeat the single-octave pattern.
- On creation Ionian calls super(Ionian, self).__init__(note, octaves), inheriting _Scale initialization (which sets tonic and octaves and may raise NoteFormatError for invalid tonic formatting). After that Ionian sets self.name = "{0} ionian".format(self.tonic).

Usage
- Primary method: ascending()
    - Typical usage sequence:
        1. Instantiate Ionian with a valid tonic (not all-lowercase).
        2. Call ascending() to obtain the ordered list of note strings for the Ionian mode spanning the requested number of octaves.
        3. Use other _Scale-provided operations (descending(), degree(), __len__(), etc.) that rely on ascending().
- There is no special ordering requirement beyond calling ascending() when the sequence is needed.

Destruction
- No resources to clean up. Ionian does not implement any context-manager or explicit close logic.

## Behavior (ascending implementation detail)
- Implementation summary:
    - Build a single-octave Ionian sequence by asking Diatonic(self.tonic, (3, 7)).ascending().
    - Remove the final duplicate tonic at the top octave from that sequence by slicing [:-1] to get the single-octave ascending degrees.
    - Repeat that single-octave list self.octaves times by list repetition (notes * self.octaves).
    - Append the first element of the single-octave list ([notes[0]]) to the end to add the final tonic duplicate at the top of the full multi-octave span.
    - Return the resulting list.

- Return type:
    - list of str: ordered tonic-upwards note names. The returned list includes a final tonic duplicate at the top octave, matching the _Scale contract.

- Examples of internal transformation (conceptual):
    - Let base = Diatonic(tonic,(3,7)).ascending()  # expected to include base[-1] == tonic at top octave
    - single_octave = base[:-1]
    - result = single_octave * octaves + [single_octave[0]]

Edge cases and error behavior:
- If Diatonic.ascending() returns an empty sequence, slicing and indexing notes[0] will raise IndexError.
- If octaves is not an integer, the list multiplication notes * self.octaves will raise TypeError.
- If octaves is 0 or a negative integer, standard Python list repetition semantics produce an empty list from notes * octaves; the final [notes[0]] append still occurs (so result will be [notes[0]] if octaves <= 0). This is allowed by the implementation but may be semantically unexpected for callers.
- Any exceptions raised by Diatonic construction or its ascending() method (FormatError, RangeError, NoteFormatError, or other library-specific exceptions) will propagate through Ionian.ascending() unchanged.

## Method Map:
- __init__(note, octaves=1)
  -> calls _Scale.__init__(note, octaves)
  -> sets self.name = "{tonic} ionian"

- ascending()
  -> Diatonic(self.tonic, (3, 7)).ascending()
  -> slice off final tonic duplicate ([:-1])
  -> repeat single-octave list octaves times and append top tonic
  -> return resulting list

Mermaid diagram (method call dependencies and typical invocation order):
graph TD
    A[Ionian.__init__(note, octaves)] --> B[_Scale.__init__ sets tonic, octaves]
    B --> C[self.name = "{tonic} ionian"]
    D[ascending()] --> E[Diatonic(self.tonic,(3,7)).ascending()]
    E --> F[single_octave = base[:-1]]
    F --> G[result = single_octave * self.octaves + [single_octave[0]]]
    G --> H[return result]
    A --> D

## Raises:
- NoteFormatError
    - Source: propagated from _Scale.__init__ when the provided note string is all-lowercase (note.islower() is True).
    - Trigger: constructing Ionian with an invalid tonic string.

- TypeError
    - Source: Python list repetition if octaves is not an integer (notes * self.octaves).
    - Trigger: passing a non-integer octaves to Ionian (e.g., 1.5).

- IndexError
    - Source: attempting to access notes[0] when the Diatonic-derived single-octave list is empty.
    - Trigger: Diatonic.ascending() returns an empty list (unexpected per Diatonic contract).

- Any exceptions raised by Diatonic(...) or by its ascending() method (such as FormatError or RangeError from the library) will be propagated unchanged.

## Example:
- Typical usage scenario (described; not code):
    1. Create an Ionian instance with a valid tonic (for example, "C") and an integer octaves value (e.g., 2). The constructor sets tonic and octaves via _Scale and assigns name "C ionian".
    2. Call ascending() to obtain the list of note names. Internally it builds a single-octave Ionian pattern by calling Diatonic("C",(3,7)).ascending(), removes the final tonic duplicate, repeats the single-octave pattern twice, then appends the tonic at the top octave. The returned list contains tonic-upwards notes spanning two octaves and includes the final tonic duplicate at the end.
    3. Use _Scale's provided helpers (descending(), degree(), len()) to query specific degrees or obtain the descending order.

Developer notes:
- Rely on Diatonic to provide a correct base single-octave pattern that includes its own final tonic duplicate; Ionian slices that off to form the correct per-octave building block.
- If you need stricter input validation (e.g., require octaves to be >= 1), validate octaves before calling super() or override ascending() to enforce the constraint.

### `mingus.core.scales.Ionian.__init__` · *method*

## Summary:
Initializes an Ionian scale instance by delegating tonic and octave setup to the shared Scale initializer and then setting a human-readable name attribute based on the resolved tonic.

## Description:
This constructor is invoked when creating an Ionian-mode scale object (Ionian(note, octaves=1)). Typical callers are user code building scales, utilities enumerating modal scales, or any code that instantiates a _Scale-compatible object before calling methods such as ascending(), descending(), or degree(). The constructor participates in object creation lifecycle: it delegates validation and storage of the tonic and octaves to the base _Scale.__init__ and then performs a small, Ionian-specific assignment of self.name.

This logic is a separate method because tonic/octave validation and baseline attribute initialization are common across many scale subclasses and are implemented by the shared _Scale initializer; the Ionian subclass only needs to record its display name after the shared initialization has completed.

## Args:
    note (str): The tonic/root note for the scale (e.g., "C", "G#", "F"). Must be a valid note string as expected by the library's note/key utilities; invalid formats may trigger a NoteFormatError from the base initializer.
    octaves (int, optional): How many octaves the scale should span when queried (used by ascending()/other methods). Defaults to 1. While not strictly type-checked here, downstream behavior assumes an integer (non-integers will cause errors when used in list-repetition contexts).

## Returns:
    None

## Raises:
    NoteFormatError
        - Condition: propagated from the base _Scale.__init__ when the provided note string fails library format validation (for example, when the string is all-lowercase per the library's tonic-format rule).
    Any exceptions raised by _Scale.__init__ may propagate unchanged. This constructor itself does not perform additional validation beyond delegating to the base initializer.

## State Changes:
    Attributes READ:
        - self.tonic: read to construct the human-readable name after the base initializer sets it.
    Attributes WRITTEN:
        - self.name: set to "{tonic} ionian" (a string) by this constructor.
        - self.tonic, self.octaves: initialized/validated by the invoked _Scale.__init__ call (written during the super() call).

## Constraints:
    Preconditions:
        - The note argument should be a valid note string per the library's conventions (otherwise _Scale.__init__ will raise NoteFormatError).
        - octaves should be an integer for meaningful subsequent use (no enforcement here; non-integers will surface errors later when methods expect integer repetition).
    Postconditions:
        - After return, self.tonic and self.octaves are set by the base initializer.
        - self.name is set to the string "{tonic} ionian", where {tonic} is the value of self.tonic determined by the base initializer.

## Side Effects:
    - No I/O or network calls.
    - No mutation of objects outside of self, other than the attributes set on this instance (via super() and the name assignment).
    - Any side effects are limited to those produced by _Scale.__init__ (e.g., propagation of its exceptions); the Ionian.__init__ body itself only assigns a string to self.name.

### `mingus.core.scales.Ionian.ascending` · *method*

## Summary:
Builds and returns the ascending pitch-class sequence of the Ionian (major) mode starting at the object's tonic across the configured number of octaves; it composes the Ionian semitone pattern via a Diatonic helper, repeats the 7-note per-octave pattern self.octaves times, and appends the top tonic.

## Description:
- Known callers and usage context:
    - No direct callers were found in the inspected snapshot. Typically this method is called by code that needs the spelled pitch-class sequence for the Ionian mode for rendering, melodic generation, chord construction from scale degrees, or exporting scales.
    - Lifecycle stage: After an Ionian instance is created with a tonic and optional octaves, clients call ascending() to obtain the ordered ascending scale tones for the requested number of octaves.
- Why this is a separate method:
    - Ionian is a specific diatonic mode (major scale). This method encapsulates the Ionian-specific semitone pattern by delegating to the general Diatonic scale generator with the semitone indices (3, 7) that mark the minor-second steps in the major scale, then applies the repetition and final-top-tonic logic. This keeps the intent explicit and avoids duplicating Diatonic repetition logic in callers.

## Args:
    None

## Returns:
    list[str]:
        - A list of spelled pitch-class strings (examples: "C", "G#", "Bb"). Octave numbers are not included.
        - Construction detail:
            * The method calls Diatonic(self.tonic, (3, 7)).ascending() which is expected to return a sequence that includes the tonic at the top (conventionally 8 items for a single-octave diatonic result: 7 distinct degrees plus the upper tonic). The code slices off the final element with [:-1] to produce a single-octave 7-note base pattern.
            * It then returns (base_pattern repeated self.octaves times) + [base_pattern[0]].
        - Length and examples:
            * If self.octaves is an integer >= 1, length == 7 * self.octaves + 1.
            * Example (tonic="C"):
                - octaves == 1 -> ["C","D","E","F","G","A","B","C"]
                - octaves == 2 -> ["C","D","E","F","G","A","B","C","D","E","F","G","A","B","C"]
            * If self.octaves <= 0 (e.g., 0 or a negative integer), the repetition yields an empty sequence and the method returns [base_pattern[0]] (a single tonic).
        - Note on types:
            * Non-integer self.octaves will cause a TypeError when list repetition is attempted; this method does not coerce or validate that octaves is an integer.

## Raises:
    - IndexError:
        * If Diatonic(self.tonic, (3, 7)).ascending() returns an empty sequence (or any sequence whose sliced result is empty), accessing notes[0] will raise IndexError.
    - Propagated exceptions from Diatonic constructor or Diatonic.ascending(), for example:
        * NoteFormatError, FormatError — if self.tonic is not a valid note representation for the note/interval helpers.
        * TypeError — if a non-integer is used in list repetition (self.octaves not an int).
        * Other lower-level exceptions raised by intervals/notes helpers (ValueError, KeyError) may propagate.
    - The method performs no explicit validation and therefore does not raise bespoke exceptions itself.

## State Changes:
    - Attributes READ:
        * self.tonic
        * self.octaves
    - Attributes WRITTEN:
        * None — this method does not modify the object's attributes.

## Constraints:
    - Preconditions:
        * self.tonic must be a valid, non-empty pitch string acceptable to the project's note/interval utilities (first character A-G with optional accidentals).
        * self.octaves should be an integer. For standard behavior, self.octaves >= 1.
        * Diatonic(self.tonic, (3, 7)).ascending() must return a sequence containing the tonic as its first element and (conventionally) the top tonic as its last element so the slicing [:-1] produces a 7-note base pattern.
    - Postconditions:
        * The returned list's first element equals the spelled tonic (base_pattern[0]).
        * If preconditions hold and self.octaves >= 1, the returned list ends with the tonic spelled as base_pattern[0], representing the tonic at the top of the final octave.
        * No attributes on self are modified by the call.

## Side Effects:
    - No I/O, network, or external service calls are performed.
    - The only side effects are those caused by the Diatonic constructor or its ascending() method (including any exceptions they may raise). This method itself is a pure composition of helper outputs and local list operations.

## `mingus.core.scales.Dorian` · *class*

## Summary:
Represents the Dorian modal scale anchored at a tonic. Provides the ascending note sequence for the Dorian mode across the requested number of octaves and a human-readable name.

## Description:
- Purpose: Encapsulates the Dorian mode (modal scale with semitone steps at scale step indices 2 and 6) for a given tonic and an octaves span. Consumers instantiate this class to get the spelled note sequence of the Dorian mode (ascending) or to use it interchangeably with other concrete _Scale subclasses.
- When to instantiate:
    - When you need the spelled Dorian scale for a given tonic (e.g., to generate melodies, construct chords by scale degree, or display the mode).
    - Typical callers: client code that manipulates scales, melodic/chord generators, or tools that present named scale objects.
- Motivation and responsibility:
    - Dorian is a small concrete adapter around a diatonic-step generator: it encodes the Dorian semitone pattern and uses the Diatonic helper to compute a single-octave step pattern, then repeats it to satisfy the instance's octaves parameter. It is responsible for furnishing an ascending() sequence conforming to the _Scale contract and for naming the scale instance.

## State:
- Attributes (inherited and defined)
    - tonic (str)
        - Source: set by _Scale.__init__(note, octaves)
        - Description: root pitch-class spelling (e.g., "D", "F#", "Bb")
        - Constraints: must not be a fully-lowercase string (base initializer raises NoteFormatError if note.islower() is True)
        - Invariant: remains equal to the constructor-supplied note (unless externally mutated)
    - octaves (int, typically)
        - Source: set by _Scale.__init__(note, octaves)
        - Description: how many octaves the Dorian scale instance should span
        - Constraints: should be a positive integer (>=1) for meaningful results; the base class does not enforce this, but Dorian multiplies lists by octaves so non-integer or unexpected values will raise at runtime (TypeError for non-int, unexpected empty results for 0 or negative)
        - Invariant: remains equal to the constructor-supplied value (unless externally mutated)
    - name (str)
        - Source: set in Dorian.__init__ to "{tonic} dorian"
        - Description: human-readable name used by __repr__ and debugging
        - Example: for tonic "D" => "D dorian"
    - type (str, class attribute)
        - Value: "ancient"
        - Description: descriptive tag used in the codebase to classify this scale

Class invariants:
- ascending() must return a list-like sequence of spelled pitch-classes starting at self.tonic and ending with the tonic repeated at the top octave (final element equals the first element).
- The number of elements returned by Dorian.ascending() equals 7 * self.octaves + 1 (seven distinct degrees per octave plus the final tonic duplicate).

## Lifecycle:
- Creation:
    - Call: Dorian(note, octaves=1)
        - note (str): required; must not be all-lowercase (otherwise NoteFormatError)
        - octaves (int, optional): defaults to 1; recommended to pass an integer >= 1
    - Effects:
        - Delegates core initialization to _Scale.__init__ which sets self.tonic and self.octaves and may raise NoteFormatError for lowercase note strings.
        - Sets self.name to a formatted string: "{tonic} dorian"
- Usage:
    - Typical method sequence:
        1. Instantiate the object.
        2. Call ascending() to obtain the spelled ascending Dorian scale across the requested octaves.
        3. Optionally use inherited helpers (degree(), descending(), __len__(), etc.) from _Scale to query degrees, get the reversed order, or compare scales.
    - Important sequencing:
        - No special ordering is required between methods; ascending() is stateless and pure with respect to instance mutation.
        - Methods from the _Scale base class (degree, descending) rely on ascending() returning the final tonic duplicate as described above.
- Destruction:
    - No explicit cleanup is required. Instances hold only in-memory strings/integers and do not implement context-management or close() semantics.

## Behavior (ascending):
- What it does:
    - Constructs a Diatonic helper with the instance tonic and the semitone step indices (2, 6) which encode the Dorian interval pattern (half-step after 2nd and 6th scale degrees).
    - Calls that Diatonic instance's ascending() and removes its final duplicate tonic (slicing off the last element) producing one octave's worth of seven distinct degree spellings.
    - Repeats this 7-note block self.octaves times (list repetition) to produce the requested multi-octave interior sequence.
    - Appends the original tonic (notes[0]) once at the end to provide the top-octave tonic duplicate (so the final sequence length is 7*self.octaves + 1).
- Return value:
    - list[str]: spelled pitch-class names in ascending order starting and ending with the tonic (final element is the tonic at the top octave).
    - Example length: if octaves == 1 => 8 elements; octaves == 2 => 15 elements.
- Notes about implementation choices:
    - Diatonic is constructed without passing the Dorian instance's octaves (Diatonic default octaves is used, typically 1). Dorian implements multi-octave repetition itself by list multiplication. This ensures the per-octave 7-note block is repeated exactly self.octaves times.
- Edge cases:
    - If self.octaves is 0 or negative, Python list repetition yields an empty list for the repeated block and the final returned list will contain a single tonic ([tonic]) — likely not meaningful. Prefer octaves >= 1.
    - If self.octaves is not an integer, list repetition will raise TypeError.
    - Diatonic.ascending() may raise exceptions for invalid tonic formats or other lower-level errors; these propagate up unchanged.

## Method Map:
(graph shows call dependencies and typical invocation order)
graph TD
    A[__init__(note, octaves)] --> B[set tonic, octaves via _Scale.__init__]
    B --> C[set name = "{tonic} dorian"]
    D[ascending()] --> E[construct Diatonic(self.tonic, (2,6))]
    E --> F[Diatonic.ascending() -> returns one-octave list with final tonic duplicate]
    F --> G[slice off last element: notes = F[:-1] (7 elements)]
    G --> H[repeat notes by self.octaves: notes * self.octaves]
    H --> I[append tonic: + [notes[0]]]
    I --> J[return final ascending list (7*self.octaves + 1 elements)]
    A --> D
    classDef default fill:#fff,stroke:#333,stroke-width:1px;

## Raises:
- NoteFormatError
    - Trigger: passed through from _Scale.__init__ if the provided note string is all-lowercase (note.islower() is True).
    - Message pattern (from _Scale): "Unrecognised note '%s'"
- TypeError
    - Trigger: if octaves is not an integer, the list repetition expression (notes * self.octaves) will raise TypeError.
- Exceptions from Diatonic.ascending()
    - Trigger: invalid tonic format, unexpected internal errors in interval helpers, or other propagated exceptions (e.g., IndexError if Diatonic helpers attempt to index into an empty string). These are not intercepted and will propagate to the caller.
- Note: Dorian itself does not explicitly raise RangeError, FormatError, or similar; such exceptions may arise from the inherited helpers (degree()) or the Diatonic utilities if called elsewhere.

## Example:
- Creation and typical usage (pseudocode style):
    - Instantiate: d = Dorian("D", octaves=1)
    - Inspect name: d.name  -> "D dorian"
    - Get ascending scale: notes = d.ascending()
        - Expected notes (one octave): a 8-element list starting and ending with "D" (e.g., ["D", "E", "F", "G", "A", "B", "C", "D"] for a typical Dorian spelling)
    - Multi-octave: d2 = Dorian("D", octaves=2); d2.ascending() -> 15-element list (7*2 + 1)
    - Use inherited helpers: d.degree(1) -> tonic, d.degree(5) -> 5th degree, d.descending() -> reversed sequence

## Implementation notes for reimplementation:
- Enforce the same public behavior:
    - Store tonic and octaves via a base initializer that raises NoteFormatError for all-lowercase tonic strings.
    - Set self.name exactly as "{0} dorian".format(self.tonic).
    - Implement ascending() to:
        1. Build a Diatonic helper for one octave using semitone indices (2, 6).
        2. Call its ascending(); slice off the final duplicate tonic.
        3. Multiply the 7-element block by self.octaves.
        4. Append the tonic once and return the result.
- Preserve purity: ascending() must not mutate instance attributes.
- Validate inputs at the class boundary if you want clearer errors (e.g., coerce or validate octaves is int >= 1 before using it).

### `mingus.core.scales.Dorian.__init__` · *method*

## Summary:
Initializes a Dorian scale instance by delegating base initialization to the scale superclass and setting a human-readable name based on the resolved tonic; does not return a value.

## Description:
- Known callers and lifecycle stage:
    - Called by client code and factory helpers when a Dorian scale object is created (e.g., Dorian("D", octaves=1)).
    - Invocation occurs at object construction time as part of the standard Python instantiation lifecycle (the __init__ step after __new__).
    - Typical contexts: melodic/chord generation, UI components showing named scales, tests constructing scale objects, or other code that constructs concrete _Scale subclasses.

- Why this logic is its own method:
    - The constructor must (1) delegate shared initialization (tonic, octaves validation and storage) to the shared _Scale.__init__ implementation and (2) apply Dorian-specific naming. Keeping this logic in __init__ centralizes object creation responsibilities and preserves the single-responsibility separation between base-class validation/assignment and subclass-specific metadata (the human-readable name).

## Args:
    note (str): The tonic (root) pitch-class spelling for the scale (e.g., "D", "F#", "Bb"). This string is handed to the base _Scale initializer which validates accepted note formats. Passing a fully-lowercase string is invalid and will cause a NoteFormatError.
    octaves (int, optional): How many octaves the scale instance should span when queried (used by methods like ascending()). Defaults to 1. Recommended to be an integer >= 1; non-integer values will cause downstream TypeError when list repetition is used.

## Returns:
    None: As with all constructors, __init__ does not return a value. On success the instance is ready for use (attributes set as documented in Postconditions).

## Raises:
    NoteFormatError: Raised by the delegated base initializer if the provided note string is in an unrecognized format (commonly when note.islower() is True). The exact error message originates from the base class (e.g., "Unrecognised note '%s'").
    TypeError: Can occur indirectly later if a non-integer octaves value is provided and subsequent operations expect an int (this method delegates octaves storage to the base initializer; list-multiplication usage elsewhere will raise TypeError).
    Propagated exceptions from _Scale.__init__ or other initialization helpers: any validation/formatting exceptions raised by the base initializer or utilities will pass through unchanged.

## State Changes:
- Attributes READ:
    - self.tonic (str): read to build the name string. Note: this attribute is populated by the base class call immediately prior to the read.
- Attributes WRITTEN:
    - self.tonic (str): set by the delegated _Scale.__init__(note, octaves) call.
    - self.octaves (int): set by the delegated _Scale.__init__(note, octaves) call.
    - self.name (str): assigned by this method to "{tonic} dorian" using the resolved tonic.

## Constraints:
- Preconditions:
    - The provided note should be a valid pitch-class string acceptable to the base _Scale initializer (notably: not a fully-lowercase string).
    - octaves should be an integer for meaningful multi-octave behavior; callers should pass an int >= 1 to avoid surprising results.
- Postconditions:
    - After successful return:
        - self.tonic is set to the normalized tonic value determined by the base initializer.
        - self.octaves is set to the provided octaves value (as stored by the base initializer).
        - self.name equals "{0} dorian".format(self.tonic).
        - The instance is ready to service other methods (e.g., ascending(), degree(), descending()) that rely on tonic and octaves.

## Side Effects:
    - No I/O or external service calls are performed.
    - Mutates the newly-created instance by setting attributes (tonic, octaves via the base initializer, and name here).
    - Any exceptions thrown by the base initializer surface to the caller; there is no exception handling in this method.

### `mingus.core.scales.Dorian.ascending` · *method*

## Summary:
Returns the ascending note sequence for a Dorian-mode scale spanning the instance's configured number of octaves, producing a list of note-name strings that starts on the tonic and includes the final tonic duplicate at the top octave.

## Description:
This method builds the Dorian scale by delegating to a diatonic-scale helper that provides a single-octave diatonic sequence, removes that helper's final top-octave tonic duplicate, repeats the remaining degrees for the requested number of octaves, and finally appends the tonic once more to form the top-octave duplicate.

Known callers and invocation context:
- The _Scale base-class methods and consumers call this method whenever the concrete scale's note sequence is required:
  - _Scale.__len__() to determine the number of notes in the scale.
  - _Scale.degree(...) when fetching a particular degree (degree() uses ascending() and expects the returned list to include the top-octave tonic duplicate).
  - _Scale.descending() and other presentation utilities that derive descending order from ascending().
- External client code also calls ascending() directly to obtain the ordered list of notes for display, playback, or analysis.

Why this is a separate method:
- The _Scale abstract contract requires each concrete scale class to implement ascending() because the concrete note sequence is scale-specific. Dorian.ascending contains only the Dorian-specific construction (delegating to a diatonic helper and arranging octaves) and keeps that logic encapsulated rather than inlined into callers or the base class.

## Args:
- None (instance method). Uses instance attributes described below.

## Returns:
- list[str]: A list of note-name strings ordered from the tonic upward, including the final tonic duplicate at the top octave.
  - Typical length: n * octaves + 1, where n is the number of distinct scale degrees returned by the diatonic helper after removing its final duplicate (commonly 7 for diatonic modes) and octaves is self.octaves.
  - For example, with a standard 7-degree diatonic base and octaves == 1, the returned list will contain 8 notes (7 distinct degrees plus the top tonic duplicate).

## Raises:
- IndexError:
  - Condition: if the diatonic helper returns an empty sequence such that extracting notes[0] fails.
- TypeError:
  - Condition: if self.octaves is not a type supported for sequence repetition (e.g., a non-integer or incompatible value causing the sequence multiplication notes * self.octaves to fail).
- Any exception raised by the underlying diatonic helper (propagated):
  - Condition: errors from note parsing/formatting or other validations performed by the diatonic helper are not caught here and will propagate (caller should expect those exceptions).

## State Changes:
- Attributes READ:
  - self.tonic: used as the root note for building the diatonic base sequence.
  - self.octaves: used to determine how many octaves-worth of degrees to repeat.
- Attributes WRITTEN:
  - None. This method does not modify instance attributes; it is a pure accessor in terms of object state.

## Constraints:
- Preconditions:
  - self.tonic must be a valid note-name string per the library's conventions; the _Scale base-class constructor enforces basic formatting rules (e.g., it rejects fully lowercased note strings).
  - self.octaves should be an integer-like value >= 1 for meaningful scale construction and to satisfy the _Scale contract (the method itself does not validate octaves; callers or subclasses should ensure a sensible value).
  - The diatonic helper must return a non-empty ascending() sequence that includes a final tonic duplicate (this method removes that final duplicate before repeating the degrees).
- Postconditions:
  - The returned list begins with the tonic (first element equals the instance tonic or the tonic-equivalent note string produced by the helper).
  - The returned list ends with the tonic duplicated at the top octave (final element equals the first element).
  - The instance's tonic and octaves attributes remain unchanged.

## Side Effects:
- No I/O, no external service calls.
- No mutation of objects outside self is performed by this method.
- The only observable effect is the creation and return of a new list object containing note-name strings.

## Implementation notes for reimplementation:
- Steps a reimplementation must follow:
  1. Obtain a single-octave diatonic ascending sequence anchored at the instance tonic (from whatever helper or algorithm your codebase uses); that sequence is expected to include the top-octave tonic duplicate.
  2. Remove the helper's final element (the top-octave tonic) to get the distinct scale degrees for one octave.
  3. Repeat that list self.octaves times (sequence repetition semantics).
  4. Append the first element of the one-octave-degree list (the tonic) to create the top-octave duplicate and return the resulting list.
- Be defensive when reimplementing: validate that the one-octave-degree list is non-empty before indexing [0], and ensure self.octaves is an integer >= 1 to avoid surprising TypeError/IndexError behavior.

## `mingus.core.scales.Phrygian` · *class*

## Summary:
Represents the Phrygian modal scale anchored at a tonic note. Provides construction-time naming and an ascending() accessor that returns the spelled Phrygian scale across the configured number of octaves.

## Description:
Phrygian is a concrete _Scale subclass that models the Phrygian mode. It is instantiated when client code or factories need the spelled, stepwise note sequence for the Phrygian mode starting from a given tonic (e.g., for rendering scales, deriving chords from degrees, or melodic generation).

Typical caller patterns:
- Client code creating a scale object directly: instantiate Phrygian(tonic, octaves).
- Higher-level code that selects a modal scale class by name and constructs it with a tonic and octave count.

Responsibility boundary:
- Phrygian is responsible for producing an ascending list of spelled pitch-classes that represent the Phrygian mode across a number of octaves.
- It delegates interval/step generation to the Diatonic helper: it uses a Diatonic instance with the Phrygian semitone-step indices (1 and 5) to obtain the single-octave diatonic pattern, then repeats that core pattern to cover multiple octaves and appends the top tonic.
- It does not validate tonic format beyond the base-class check, nor manage external resources.

Implementation summary (what the class does, not code-level how):
- On construction it records the tonic and octaves via the _Scale constructor and sets a human-readable name "{tonic} phrygian".
- ascending() builds the Phrygian sequence by:
  1. Creating a Diatonic scale configured to use semitone steps at indices 1 and 5 (the Phrygian pattern) anchored at the same tonic.
  2. Taking Diatonic.ascending() for one octave, removing the duplicate final tonic element to obtain the 7-note core for one octave.
  3. Repeating the 7-note core self.octaves times and appending the tonic once more to produce the final list.

## State:
- type (class attribute)
    - Type: str
    - Value: "ancient"
    - Invariant: constant across all instances; indicates scale family metadata.

- tonic (instance attribute)
    - Type: str
    - Description: the scale's root/pitch-class (e.g., "E", "C#", "F").
    - Source: set by _Scale.__init__(note, octaves).
    - Constraints: _Scale.__init__ will raise NoteFormatError if the provided note string is entirely lowercase (note.islower() == True). The tonic should otherwise follow the library's note-format conventions (first character A-G, optional accidentals).
    - Invariant: represents the tonic used by ascending() and other accessors.

- octaves (instance attribute)
    - Type: int (expected)
    - Description: how many octaves the ascending() result should span.
    - Source: set by _Scale.__init__(note, octaves).
    - Constraints: _Scale does not enforce numeric ranges. Consumers should pass a positive integer (>= 1) to obtain sensible musical output. Non-integer or non-positive values will produce unexpected results (for example, sequence repetition semantics).
    - Invariant: used by ascending() to repeat the core octave pattern; should remain stable for the object's lifetime unless intentionally mutated.

- name (instance attribute)
    - Type: str
    - Description: human-readable name for the scale instance, set in __init__ to "{tonic} phrygian".
    - Invariant: should always reflect the current tonic (implementation sets it at construction; external mutation could break this invariant).

Class invariants:
- name is a string that includes the tonic.
- ascending() returns a list of spelled pitch-class strings beginning with self.tonic and ending with the tonic spelled again (top-octave duplicate).
- ascending() does not mutate object state.

## Lifecycle:
Creation
- Constructor signature: Phrygian(note, octaves=1)
    - note (str): required. Must not be a completely lowercase string (otherwise _Scale.__init__ raises NoteFormatError).
    - octaves (int, default 1): recommended to be >= 1.
- Construction sequence:
    1. Phrygian.__init__ calls super(_Scale).__init__(note, octaves), which sets self.tonic and self.octaves and enforces the lowercase-note check.
    2. Phrygian.__init__ sets self.name = "{0} phrygian".format(self.tonic).

Usage
- Typical usage is to call ascending() to obtain the spelled Phrygian scale across the requested number of octaves.
- No specific call ordering is required beyond successful construction.
- Methods inherited from _Scale (degree(), descending(), __len__(), etc.) behave as documented by _Scale and operate on the sequence returned by ascending().

Destruction / cleanup
- No special cleanup; no context-manager or close() required.

## Method Map:
graph TD
    A[Phrygian.__init__(note, octaves)] --> B[_Scale.__init__ (sets tonic, octaves, may raise NoteFormatError)]
    B --> C[sets self.name = "{tonic} phrygian"]
    D[Phrygian.ascending()] --> E[Construct Diatonic(self.tonic, semitones=(1,5))]
    E --> F[call Diatonic.ascending() -> one-octave list ending with tonic duplicate]
    F --> G[slice off last element ([:-1]) to get 7-note core]
    G --> H[repeat core self.octaves times]
    H --> I[append core[0] (tonic) as final top tonic]
    I --> J[return final list]
    classDef default fill:#fefefe,stroke:#333,stroke-width:1px;

(Flow: construct -> use ascending() -> Diatonic -> build final list.)

## Raises:
- NoteFormatError
    - Origin: _Scale.__init__(note, octaves)
    - Trigger: if note.islower() is True (i.e., the caller supplied a fully-lowercase note string).
    - Effect: constructor fails; no instance is created.

- Exceptions propagated from Diatonic.ascending() and the underlying interval helpers:
    - FormatError, NoteFormatError
        * Trigger: invalid note formatting or unexpected direction/format in helper functions used by Diatonic.
    - RangeError, IndexError, ValueError, TypeError, KeyError (possible)
        * Trigger: invalid or out-of-range inputs seen by interval helper functions or misuse of sequence operations (for example, empty tonic, non-integer octaves, or malformed semitone pattern).
    - Behavior: ascending() does not catch these; they propagate to the caller. Callers who require guarded behavior should validate inputs (tonic format and octaves) before invoking ascending().

Notes on edge cases:
- If self.octaves is 0, ascending() will return a list containing only the tonic (because the repeated core is empty and the final tonic is appended). This is probably undesirable musically; callers should use octaves >= 1.
- If Diatonic construction/ascending() fails (e.g., because the tonic is empty or contains invalid characters), that exception will propagate unchanged.

## Example:
- Construction and expected behavior (described):
    - Instantiate: with tonic "E" and octaves=1, Phrygian sets name to "E phrygian".
    - ascending() builds the Phrygian core from Diatonic(self.tonic, semitones=(1,5)).ascending() which yields the single-octave spelled pattern ["E", "F", "G", "A", "B", "C", "D", "E"]. The class removes the last "E" to get the 7-note core ["E", "F", "G", "A", "B", "C", "D"], repeats it octaves times (once here), then appends "E" to produce the final list:
      ["E", "F", "G", "A", "B", "C", "D", "E"].
    - With octaves=2 the pattern becomes:
      ["E","F","G","A","B","C","D","E","F","G","A","B","C","D","E"].
    - These examples assume Diatonic implements the semitone pattern (1,5) as described and that tonic formatting follows the library conventions.

Implementation notes for reimplementation:
- When reimplementing, ensure Phrygian delegates the step-generation to a Diatonic-like helper that can be configured with semitone indices. The Phrygian ascending() must:
    1. Obtain the one-octave Diatonic ascending list (which includes the top tonic duplicate).
    2. Remove that final duplicate to obtain exactly 7 distinct scale degrees per octave.
    3. Repeat that 7-note core for self.octaves and then append the tonic (core[0]) once more to represent the top-of-scale tonic.
- Preserve immutability expectations: ascending() should not mutate instance attributes.

### `mingus.core.scales.Phrygian.__init__` · *method*

## Summary:
Initializes a Phrygian scale instance by delegating core initialization to the scale superclass and then setting a human-readable name that incorporates the resolved tonic.

## Description:
This constructor is invoked when client code or higher-level factories construct a Phrygian scale (e.g., Phrygian("E", 1) or via a mode-selection factory). It runs during the object's creation/lifecycle initialization stage and is responsible for:
- Ensuring the superclass performs standard scale initialization (setting self.tonic and self.octaves and performing format validation).
- Recording a readable name for the instance in the form "<tonic> phrygian".

This behavior is implemented as a dedicated constructor rather than inlined elsewhere because it:
- Must call the shared _Scale initialization logic to obtain canonical tonic and octave state and to reuse validation.
- Adds only a thin, subclass-specific augmentation (the name string) that logically belongs to class construction.

Known callers / call sites:
- Direct instantiation in client code: Phrygian(note, octaves)
- Factory or registry code that selects modal scale classes by name and constructs them with a tonic and octave count
- Any code that constructs scale objects as part of rendering, analysis, or melodic generation pipelines

## Args:
    note (str): Required. The tonic / root pitch-class for the scale (examples: "E", "C#", "F"). Must follow the library's note-format conventions; supplying a fully-lowercase string (note.islower() == True) will cause the superclass initializer to reject it.
    octaves (int, optional): Number of octaves the scale should span when accessed (e.g., via ascending()). Defaults to 1. Recommended to be an integer >= 1 for musically sensible output; the class does not enforce a strict upper/lower numeric bound here.

## Returns:
    None. As a constructor, it returns the newly-initialized instance (implicit). No explicit value is returned.

## Raises:
    NoteFormatError: Raised by the superclass _Scale.__init__ if the provided note fails the library's format checks — specifically when note.islower() is True (a fully-lowercase note string).
    Any exception raised by _Scale.__init__ will propagate; callers should validate note and octaves if they need guarded behavior.

## State Changes:
    Attributes READ:
        self.tonic - read when forming the human-readable name (this attribute is set by the superclass call immediately prior).
    Attributes WRITTEN:
        self.name - set to the string "{tonic} phrygian".
    Attributes set by the superclass call (side-effect of delegation):
        self.tonic - established by _Scale.__init__(note, octaves)
        self.octaves - established by _Scale.__init__(note, octaves)

## Constraints:
    Preconditions:
        - note should be a non-empty string following the library's note-format conventions (first character A-G with optional accidentals). Avoid supplying a fully-lowercase string.
        - octaves should be an integer (typical, expected >= 1). Non-integer or negative values are not validated here and may lead to unexpected behavior downstream.
    Postconditions:
        - After successful return, self.tonic and self.octaves are initialized (by the superclass) and self.name equals "<tonic> phrygian" using the resolved tonic string.
        - No other instance attributes are modified by this constructor.

## Side Effects:
    - Calls the superclass constructor (_Scale.__init__), which performs validation and sets instance attributes; no I/O, external network calls, or global state mutations are performed here.
    - No mutation of objects outside the newly-created instance is performed.

### `mingus.core.scales.Phrygian.ascending` · *method*

## Summary:
Returns the ascending sequence of note names for this Phrygian scale across the configured number of octaves, ending with the scale's tonic.

## Description:
This method builds the Phrygian ascending scale by delegating to a Diatonic scale constructor for the same tonic and a (1, 5) degree span, removing the final duplicate octave degree from that base sequence, then repeating that base pattern for the number of octaves configured on this instance and appending the tonic as the final note.

Known callers / usage context:
- Typically invoked by client code after constructing a Phrygian instance to obtain the scale degrees for playback, display, analysis, or further processing.
- Used at the "scale enumeration" stage in pipelines that enumerate notes for a scale object; left as a separate method to keep the scale object's public API consistent (each scale type exposes ascending and descending generators) and to enable reuse or overriding in subclasses.

Why this logic is in its own method:
- Produces the canonical "ascending" representation for this scale type as part of the scale object's public API.
- Keeps scale-construction concerns encapsulated so callers need not know how the scale is assembled from diatonic components.

## Args:
    None.

## Returns:
    list[str]: A list of note name strings. Let base_notes be the list produced by Diatonic(self.tonic, (1, 5)).ascending() with its last element removed; then the returned list equals base_notes repeated self.octaves times, followed by base_notes[0] as the final tonic. If base_notes has length N, the returned list length is N * self.octaves + 1.

    Examples of possible values:
    - For a valid tonic and octaves = 1: returns the base scale degrees plus the tonic as the final element.
    - For octaves > 1: returns consecutive octave repeats of the base degrees, then the tonic once more.

## Raises:
    - Any exception raised by Diatonic(...) construction or its ascending() call will propagate (for example, errors arising from an invalid tonic). The method does not catch these exceptions.
    - IndexError: If the underlying Diatonic(...).ascending() call returns an empty sequence, then accessing base_notes[0] will raise IndexError.
    - TypeError: If self.octaves is not an integer (or not a type usable for list repetition), the list multiplication operation may raise TypeError.

## State Changes:
    Attributes READ:
        - self.tonic
        - self.octaves
    Attributes WRITTEN:
        - None (method does not modify any self.<attr>)

## Constraints:
    Preconditions:
        - self.tonic must be a valid note representation accepted by the Diatonic constructor used here.
        - self.octaves should be an integer (semantically a positive integer >= 1). Supplying non-integer or negative values may produce TypeError or unexpected results (negative or zero values will cause the repeated portion to be empty).
    Postconditions:
        - No attributes of self are modified.
        - The return value is a list of note name strings whose length equals N * self.octaves + 1 where N is the length of the base_notes sequence produced by the Diatonic call after dropping its last element.

## Side Effects:
    - None external: no I/O, no network or filesystem access.
    - The only possible side-effects are exceptions propagated from Diatonic construction or operations, as described above.

## `mingus.core.scales.Lydian` · *class*

## Summary:
Represents the Lydian modal scale anchored at a tonic note and spanning a configurable number of octaves. Provides an ascending() accessor that returns the spelled pitch-classes for the Lydian scale (including the top-of-scale tonic duplicate).

## Description:
This concrete scale class is a subclass of _Scale and implements the Lydian mode by delegating step construction to the Diatonic helper with a fixed semitone pattern. Instantiate this class when you need the spelled (letter + accidental) pitch-class sequence for a Lydian scale (for rendering, degree lookup, chord-building, or melodic generation).

Typical callers
- Client code that requests the ordered notes of a Lydian scale (for example, a scale printer or a harmony generator).
- Any code that expects an _Scale-compatible object (i.e., offers ascending(), descending(), degree(), length, and equality semantics).

Validation and responsibilities
- Lydian delegates basic input validation to its base class _Scale. In particular, _Scale.__init__ raises NoteFormatError when the provided note string is all-lowercase (note.islower() is True). Callers should therefore provide a tonic string that is not all-lowercase.
- _Scale does not enforce numeric constraints on octaves; Lydian likewise does not perform additional numeric validation of octaves. Callers are expected to pass an integer >= 1; non-integer or non-positive values will produce Python sequence-repetition semantics or unintended results.

Motivation and responsibility
- Responsibility: create and expose the Lydian ascending note sequence for the requested tonic and number of octaves.
- Boundary: does not perform validation beyond what _Scale and Diatonic provide; it composes the Diatonic output to produce the Lydian ordering.

Implementation summary (what it does)
- Sets the class attribute type = "ancient".
- On construction, delegates basic validation and storage of tonic and octaves to _Scale, then creates a human-readable name ("<tonic> lydian").
- ascending() builds the Lydian modal notes by constructing a single-octave Diatonic pattern using semitones=(4, 7), removing the trailing tonic duplicate, repeating that per-octave chunk for self.octaves, and finally appending the tonic to produce the top duplicate. The final list length is 7 * octaves + 1.

## State:
- type (str, class attribute)
    - Value: "ancient"
    - Role: descriptive classification used by consumers/inspectors. Immutable at class-level.

- tonic (str)
    - Type: string representing a pitch-class (letter A-G optionally with accidentals, e.g., 'C', 'G#', 'F').
    - Source: provided as the note argument to __init__; assigned by _Scale.__init__.
    - Constraints: _Scale.__init__ raises NoteFormatError if note.islower() is True. The tonic should be non-empty and start with A-G for the underlying interval helpers to work correctly.
    - Invariant: remains equal to constructor-supplied value unless mutated externally.

- octaves (int, expected)
    - Type: integer (the code treats it as a repeat count).
    - Source: provided as the octaves argument to __init__; assigned by _Scale.__init__.
    - Constraints / recommendations: _Scale does not validate octaves; callers should pass an integer >= 1. Non-integer or negative values will cause Python sequence-repetition semantics (e.g., non-int may raise TypeError; 0 or negative values produce unexpected lengths).
    - Invariant: remains equal to constructor-supplied value unless mutated externally.

- name (str)
    - Type: string
    - Value set by Lydian.__init__: "{tonic} lydian" (tonic is self.tonic).
    - Use: used by __repr__ and debugging output.

Derived state / behavioral invariants
- ascending() must return a list-like sequence of spelled pitch-classes whose length is 7 * octaves + 1 and whose first element equals self.tonic and last element equals that tonic again (top-of-scale duplicate).
- The class relies on Diatonic.ascending() semantics: a per-octave diatonic chunk of length 7 is produced when Diatonic is called with default octaves=1; Lydian strips the top duplicate and reconstructs the requested number of octaves.

## Lifecycle:
Creation
- How to instantiate:
    - Required arguments: note (str) — the tonic pitch-class; octaves (int) optional, defaults to 1.
    - Example constructor signature (conceptual): Lydian(note, octaves=1)
- During __init__:
    - Calls _Scale.__init__(note, octaves) which validates the tonic is not all-lowercase (raises NoteFormatError otherwise) and stores tonic and octaves.
    - Sets self.name to "<tonic> lydian".

Usage
- Typical sequence:
    1. Create an instance: supply a valid tonic string and an integer octaves (>=1 recommended).
    2. Call ascending() to obtain the spelled ascending pitch-class list for the requested number of octaves. This method is pure (does not mutate instance state).
    3. Optionally call descending(), degree(n), len(instance), or equality operators inherited from _Scale which rely on ascending()/descending().
- Sequencing constraints:
    - ascending() may be called any time after construction; there is no required ordering among other read-only methods.
    - No explicit setup or teardown is required.

Destruction / cleanup
- No resources to release. Instances are plain objects; no context-manager support or close() method is provided.

## Method Map:
- __init__(note, octaves=1)
  -> delegates to _Scale.__init__ (validates tonic)
  -> sets self.name

- ascending()
  -> Instantiates Diatonic(self.tonic, (4, 7)) (default Diatonic octaves=1)
  -> calls Diatonic.ascending() to obtain a 1-octave diatonic list with a final tonic duplicate
  -> removes final tonic duplicate via slice [:-1] to obtain a 7-note per-octave chunk
  -> repeats that chunk self.octaves times (sequence multiplication)
  -> appends the initial tonic chunk[0] to form the final top duplicate and returns the combined list

Mermaid diagram (method call dependencies and typical invocation order)
graph TD
    A[__init__(note, octaves)] --> B[_Scale.__init__ (validate/store tonic, octaves)]
    B --> C[set self.name = "{tonic} lydian"]
    D[ascending()] --> E[Diatonic = Diatonic(self.tonic, (4,7))]
    E --> F[Diatonic.ascending() -> list_with_top_tonic]
    F --> G[per_octave_chunk = list_with_top_tonic[:-1]]
    G --> H[result = per_octave_chunk * self.octaves + [per_octave_chunk[0]]]
    H --> I[return result]
    A --> D

## Behavior details — ascending()
- Returns: list[str]
    - Each element: a spelled pitch-class string (letter A-G with optional accidentals).
    - Length: exactly 7 * self.octaves + 1 (7 distinct degrees per octave plus the final tonic duplicate).
    - Ordering: tonic upward stepwise through the Lydian mode; first element is the tonic; last element is the tonic at the top octave.
- Implementation notes for reimplementation:
    - Construct a Diatonic helper with (tonic, semitones=(4, 7)) and use its single-octave ascending() output.
    - Remove the final tonic duplicate from that single-octave list (slice up to but not including the last element) to obtain the 7-note octave chunk.
    - Repeat that chunk self.octaves times, then append the chunk[0] (the tonic) to end the sequence.
- Purity: ascending() does not modify instance attributes.

## Raises:
- NoteFormatError
    - Trigger: inherited from _Scale.__init__ when the provided note string is all-lowercase (note.islower() is True). Message originates from _Scale: "Unrecognised note '%s'" % note.
- Exceptions propagated from Diatonic.ascending() or the underlying interval helpers:
    - Possible exceptions include NoteFormatError / FormatError, IndexError, TypeError, ValueError depending on invalid tonic format, unexpected semitone descriptor, or invalid inputs to interval helper utilities.
- IndexError (possible)
    - Trigger: if Diatonic.ascending() unexpectedly returns an empty list and Lydian attempts to read notes[0]; such a result would indicate a deeper problem in the Diatonic helper or invalid input values.
- No new bespoke exceptions are raised by Lydian itself; it relies on its collaborators for validation.

## Example:
- Creation:
    - Create a one-octave Lydian scale on C: instantiate with tonic = "C" and octaves = 1.
    - Create a two-octave Lydian scale on G#: tonic = "G#", octaves = 2.
- Typical method sequence:
    1. Instantiate: instance = Lydian("C", 2)
    2. Retrieve notes: notes = instance.ascending()
       - For octaves=2 the returned list length will be 7*2 + 1 = 15.
       - The returned list begins with "C" and ends with "C" (top-of-scale tonic duplicate).
    3. Use inherited helpers: instance.degree(4) returns the 4th degree (ascending direction by default), instance.descending() returns the reversed ordering.
- Notes on proper usage:
    - Ensure tonic is not an all-lowercase string to avoid NoteFormatError.
    - Prefer passing an integer octaves >= 1. The base class does not enforce this and unusual values will yield Python sequence repetition semantics.

### `mingus.core.scales.Lydian.__init__` · *method*

## Summary:
Initializes a Lydian scale instance by delegating validation and storage of the tonic and octave count to the base scale constructor, then sets a human-readable name attribute describing the scale (e.g., "C lydian").

## Description:
Known callers and context:
- Typical callers are client code that constructs a scale object for printing, harmony generation, melodic generation, or any code that uses an _Scale-compatible object (calls ascending(), degree(), etc.).
- This constructor is invoked during object creation (scale lifecycle creation step) and runs before any public accessor (like ascending()) is used.

Why this logic is a separate method:
- This is the class constructor: it must call the superclass constructor to perform shared validation and state initialization (tonic, octaves) and then perform Lydian-specific initialization (setting the name). This keeps common validation in the base class and leaves mode-specific naming here.

## Args:
    note (str):
        The tonic pitch-class string (letter A–G optionally with accidentals, e.g., "C", "G#", "Fb").
        Expected to be in the format understood by the library's note utilities; must not be all-lowercase (see Raises).
    octaves (int, optional):
        Number of octaves the scale will span. Defaults to 1.
        Treated as a repeat count by scale logic; callers should supply an integer >= 1. The base class does not strictly enforce numeric bounds.

## Returns:
    None
    The constructor does not return a value; it initializes instance attributes.

## Raises:
    NoteFormatError
        Raised by the superclass constructor when the provided note string is invalid in a specific way: if note.islower() is True (i.e., the provided tonic is all-lowercase). The exact message originates from the base-class validation.
    (Propagated exceptions)
        Any exceptions raised by the base-class __init__ (such as other validation errors) will propagate. This constructor itself does not perform additional validation or raise new exception types.

## State Changes:
Attributes READ:
    self.tonic
        Read after the superclass initializer runs, to compose the human-readable name.

Attributes WRITTEN:
    self.tonic
        Assigned by the superclass constructor (super(...).__init__(note, octaves)).
    self.octaves
        Assigned by the superclass constructor.
    self.name
        Set here to the string "{tonic} lydian", where tonic is the stored self.tonic.

## Constraints:
Preconditions:
    - The provided note must be a non-empty string in the library's expected pitch-class format and should not be all-lowercase (passing a fully lowercase string will trigger NoteFormatError in the base class).
    - octaves should be an integer >= 1 for sensible behavior; non-integer or non-positive values are not validated here and may produce unintended results.

Postconditions:
    - After successful return, self.tonic contains the constructor-provided tonic (as set by the superclass), self.octaves contains the provided octaves count, and self.name equals "{tonic} lydian".
    - The instance is ready for use with other _Scale methods such as ascending(), descending(), and degree().

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside this instance beyond the instance attributes written above.
    - Any side-effects or exceptions originating from the base-class constructor (super(...).__init__) will occur during this initialization call.

### `mingus.core.scales.Lydian.ascending` · *method*

## Summary:
Returns the ascending pitch sequence for the Lydian scale based on this instance's tonic and octave count, repeating the scale pattern for the requested number of octaves and appending the top tonic to close the final octave.

## Description:
Known callers:
    - No internal callers were identified in the provided context. This method is intended to be called by client code or higher-level utilities that request the ascending notes for a Lydian scale instance (for example, code that renders scales, builds arpeggios, or performs theoretical analysis).
Lifecycle / pipeline stage:
    - Invoked when a caller needs the ordered ascending notes of this Lydian scale (usually as part of scale generation or music-processing pipelines).
Why this is its own method:
    - Each scale class in the library exposes a standard interface for generating scale notes (ascending/descending). This method implements the Lydian-specific behavior (delegating to a diatonic construction tuned to the Lydian mode) and constructs the repeated/octaved output; keeping it as a method preserves the polymorphic scale API and allows overrides or custom behavior per scale type.

## Args:
    None.

## Returns:
    list[str]: A list of note name strings representing the ascending Lydian scale across the requested number of octaves, with the final element being the top tonic.
    - If base_notes is the sequence computed from Diatonic(self.tonic, (4, 7)).ascending()[:-1] and n = len(base_notes), the returned list length is n * self.octaves + 1.
    - Typical values: e.g., for one octave it will contain the scale degrees for one octave followed by the tonic one octave above.
    - Edge-case returns:
        * If base_notes is non-empty and self.octaves == 0 the method returns [base_notes[0]] (single tonic) because notes * 0 yields [] and then [notes[0]] is appended.
        * If base_notes is empty, calling this method will raise an indexing error when attempting to access notes[0] (see Raises).

## Raises:
    - Any exception raised by constructing the Diatonic helper or calling its ascending() method will propagate unchanged. Typical examples (propagated from dependent code) include invalid tonic / format related errors from the underlying scale/note utilities.
    - If the sliced base note list (notes) is empty, an IndexError will occur when the method attempts to read notes[0].

## State Changes:
Attributes READ:
    - self.tonic
    - self.octaves
Attributes WRITTEN:
    - None. This method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.tonic must be a tonic value acceptable to the Diatonic constructor and its ascending() method (i.e., a properly formatted note name according to the library's note conventions).
    - self.octaves should be an integer. The method assumes self.octaves is set to the desired repetition count; negative or non-integer values are not validated here and may produce surprising results or errors.
Postconditions:
    - On successful return, the method yields a list of note name strings as described above. No attributes of self are changed.

## Side Effects:
    - None beyond calling the Diatonic constructor and its ascending() method (no I/O, no external service calls, no mutation of objects outside of local temporaries). Exceptions from those calls propagate to the caller.

## `mingus.core.scales.Mixolydian` · *class*

## Summary:
Represents the Mixolydian modal scale anchored at a given tonic and spanning a specified number of octaves. Provides an ascending() accessor that builds the Mixolydian note sequence by delegating generation to a Diatonic helper and then arranging octave repetition and final tonic duplication.

## Description:
Instantiate this class when you need the Mixolydian mode (the scale traditionally described as the dominant-mode) for a particular tonic note and a specified span in octaves. The class itself is a thin concrete subclass of the shared _Scale base class: it performs no tonic validation beyond what _Scale enforces, sets a human-friendly name string, and produces the concrete ascending note sequence by constructing a Diatonic instance with arguments (tonic, (3, 6)) and processing its ascending() output.

Known callers / factories
- Client code that constructs specific scale objects directly, e.g., Mixolydian('C') or Mixolydian('G#', 2).
- Any higher-level routines that enumerate modes by constructing concrete scale subclasses.

Motivation / responsibility boundary
- Responsibility: produce an ascending() list of note name strings that represents the Mixolydian scale across the requested number of octaves, set an informative name, and participate in the _Scale interface (degree lookup, descending, __len__, equality, etc.).
- Not responsible for: validating tonic format beyond _Scale, or implementing low-level interval logic. It delegates interval construction to Diatonic and simply arranges the returned sequence into the requested octave span.

## State:
- type (class attribute)
    - Type: str
    - Value: "ancient"
    - Purpose: classification metadata; constant for the class.

- tonic (instance attribute; inherited from _Scale)
    - Type: str
    - Description: the root note used to generate the scale (e.g., 'C', 'F#', 'Bb').
    - Constraints: provided note string must not be all-lowercase; _Scale.__init__ raises NoteFormatError when note.islower() is True.
    - Invariant: remains equal to the constructor-supplied tonic unless mutated externally.

- octaves (instance attribute; inherited from _Scale)
    - Type: typically int
    - Description: the number of octaves the returned ascending() sequence should span.
    - Default: 1 (when omitted from constructor).
    - Constraints and behavior:
        - The implementation uses octaves in list repetition (notes * self.octaves). As a result:
            - A non-integer value will likely raise a TypeError when used to multiply a list.
            - Zero or negative integers behave like Python list repetition (yielding an empty repeated section); negative integers will not raise but will produce an empty repetition.
        - Recommended: pass a positive integer; subclasses or callers should validate as needed.
    - Invariant: remains equal to constructor-supplied value unless mutated externally.

- name (instance attribute; set in Mixolydian.__init__)
    - Type: str
    - Value: constructed as "{tonic} mixolydian" (tonic substituted with self.tonic).
    - Purpose: used by __repr__ and human-readable diagnostics.

Class invariants
- ascending() must return a list-like of note name strings ordered from tonic upward and include the final tonic duplicate (the last element is the tonic at the upper octave). Mixolydian.ascending constructs such a sequence by using Diatonic(...).ascending() as its source and follows the _Scale contract by returning a top-octave tonic duplicate.

## Lifecycle:
Creation
- Call the constructor with:
    - note (str): tonic (required)
    - octaves (int, optional): number of octaves to span; default is 1
- Example constructor call (conceptual): Mixolydian('C', 2)
- Under the hood: __init__ delegates to _Scale.__init__(note, octaves) which sets tonic and octaves and performs its minimal validation (raises NoteFormatError if note.islower()) then Mixolydian.__init__ sets self.name.

Usage
- Typical sequence:
    1. Instantiate: scale = Mixolydian(tonic, octaves)
    2. Retrieve ascending note list: scale.ascending()
       - Implementation detail: this will create a Diatonic(self.tonic, (3, 6)) instance, call its ascending(), remove the final duplicated tonic element returned there (via [:-1]), then repeat that truncated pattern self.octaves times and append the pattern's first element once more to ensure the final top-octave tonic duplicate.
    3. Use _Scale-provided utilities: degree(n), descending(), __len__(), comparisons, etc., which rely on ascending() semantics.
- Ordering/sequencing: There is no required call ordering beyond constructing the instance before calling its accessors. ascending() is a pure accessor (it must not mutate instance state).

Destruction
- No special cleanup; there are no external resources or context-manager protocols.

## Method Map:
graph TD
    A[Mixolydian.__init__(note, octaves=1)] --> B[_Scale.__init__ sets tonic, octaves]
    B --> C[Mixolydian sets name = "{tonic} mixolydian"]
    D[ascending()] --> E[Construct Diatonic(self.tonic, (3, 6))]
    E --> F[Call Diatonic.ascending()]
    F --> G[Truncate final duplicate: notes = result[:-1]]
    G --> H[Repeat pattern: notes * self.octaves]
    H --> I[Append tonic of pattern: + [notes[0]]]
    I --> J[Return final ascending list]
    classDef default fill:#f2f2f2,stroke:#333,stroke-width:1px;

(Explanation: ascending() is the principal behavior; it depends on Diatonic.ascending() and then composes the final ascending sequence by truncation, repetition, and final tonic append.)

## Raises:
- NoteFormatError
    - Raised by: _Scale.__init__ invoked from Mixolydian.__init__
    - Condition: provided note string is all-lowercase (note.islower() is True).
- Propagated errors from Diatonic or its ascending()
    - Mixolydian.ascending() delegates to Diatonic(...).ascending(); any exceptions raised by Diatonic construction or its ascending() (e.g., FormatError, RangeError, NoteFormatError, IndexError) will propagate unless caught by the caller.
- IndexError (possible)
    - Scenario: if Diatonic.ascending() returns an empty list or shorter-than-expected list, notes[0] or slicing may raise IndexError when Mixolydian.ascending() attempts to access notes[0] after truncation.
- TypeError (possible)
    - Scenario: if octaves is not an integer-like value suitable for list repetition (e.g., a float or an incompatible type), the list repetition (notes * self.octaves) will raise TypeError.

## Example:
- Create a one-octave Mixolydian on C:
  - Construct with tonic 'C' and default octaves 1. The instance name will be "C mixolydian".
  - Call ascending() to receive a list of note names starting at 'C' and ending with the top-octave 'C' (the implementation delegates to Diatonic, truncates its duplicate, repeats by octaves, and appends the final tonic).
- Create a two-octave Mixolydian on G#:
  - Instantiate with octaves=2; ascending() will repeat the core step pattern twice and append the top tonic once more to provide the final top-octave tonic duplicate.
- Error cases:
  - Passing a lowercase tonic string will raise NoteFormatError at construction.
  - Passing a non-integer octaves value may raise TypeError when calling ascending().

Note:
- Because Mixolydian relies on Diatonic(...) to provide the scale step pattern, callers who need stronger guarantees about interval content, accidental normalization, or explicit error messages should inspect or wrap Diatonic's behavior. The Mixolydian class intentionally focuses on assembling the Mixolydian ordering from Diatonic's output rather than re-implementing interval logic.

### `mingus.core.scales.Mixolydian.__init__` · *method*

## Summary:
Initialize a Mixolydian scale instance by delegating construction and validation to the shared _Scale initializer and then setting a human-readable name based on the established tonic.

## Description:
This constructor is invoked when client code creates a Mixolydian object (for example, Mixolydian('C') or Mixolydian('G#', 2)) during the standard object construction lifecycle. It performs two steps:
1. Delegates to the common _Scale.__init__ to perform shared initialization (setting tonic and octaves and performing format validation).
2. Sets the instance's name attribute to a readable string "{tonic} mixolydian" using the tonic value populated by the super call.

Why this is a separate method:
- The Mixolydian class is a thin specialization of a shared _Scale base class; its constructor exists to reuse _Scale's validation and state setup while adding a single subclass-specific attribute (name). This keeps shared logic centralized in _Scale and keeps Mixolydian concise and explicit about its identity.

Known callers / usage contexts:
- Direct construction by user code or higher-level factory routines that instantiate concrete scale classes.
- Any module or routine that enumerates or manipulates named scale objects (e.g., for display, printing, or further scale operations).

## Args:
    note (str):
        The tonic / root note for the scale (e.g., 'C', 'F#', 'Bb').
        Constraint: must be a correctly formatted note string as required by _Scale (not all-lowercase; see Raises).
    octaves (int, optional):
        Number of octaves the scale should span when accessed (default: 1).
        Recommended: a non-negative integer; callers should pass an integer appropriate for later list-repetition usage.

## Returns:
    None

## Raises:
    NoteFormatError:
        Raised by the delegated _Scale.__init__ if the provided note string fails the format check (specifically when note.islower() is True in _Scale's validation).
    Any exception raised by _Scale.__init__:
        All exceptions from the base initializer (format, range, or other validation errors) propagate through this constructor unchanged.

## State Changes:
    Attributes READ:
        self.tonic
            - Read after the call to the superclass initializer to build the human-readable name.
    Attributes WRITTEN:
        self.name
            - Set to the string "{0} mixolydian".format(self.tonic).
        (Indirect / via super call) self.tonic, self.octaves
            - These are set by _Scale.__init__ invoked via super(Mixolydian, self).__init__(note, octaves).

## Constraints:
    Preconditions:
        - The caller must provide a note string in the expected format (not all-lowercase) to avoid NoteFormatError from _Scale.__init__.
        - octaves should be an integer suitable for later use (e.g., used for list repetition in accessors); providing an inappropriate type may cause errors elsewhere even though __init__ will accept and store the value.
    Postconditions:
        - self.tonic and self.octaves are initialized by the base class initializer.
        - self.name is present and equals "{tonic} mixolydian" (tonic substituted).
        - No I/O or external side effects occur as part of initialization.

## Side Effects:
    - No I/O, no network or filesystem access.
    - Mutates the instance by setting attributes as described above.
    - Any exceptions raised by _Scale.__init__ occur before self.name is set and propagate to the caller.

### `mingus.core.scales.Mixolydian.ascending` · *method*

## Summary:
Produce the ascending Mixolydian-mode pitch sequence for the object's tonic across the configured number of octaves and return it as a list of spelled pitch-class strings; the method does not mutate the Mixolydian object.

## Description:
- Known callers and usage context:
    - No internal callers were found in the inspected snapshot. This method is intended to be called by any consumer that needs the spelled sequence of the Mixolydian scale for rendering, melodic generation, chord extraction, analysis, or export.
    - Lifecycle: After instantiating a Mixolydian object (which stores a tonic and an octaves value), clients call ascending() to obtain the ascending mode tones across octaves.
- Why this is a separate method:
    - The Mixolydian mode is defined by a specific diatonic semitone pattern. This method composes behavior by instantiating a Diatonic scale with the Mixolydian semitone indices (3, 6), extracting the seven-tone single-octave pattern, repeating it across octaves, and appending the top tonic. Encapsulating this logic keeps mode-specific construction in one place and avoids duplicating the semitone-pattern handling.

## Implementation behavior (how the method computes its result):
1. Constructs a Diatonic object with the same tonic and the Mixolydian semitone indices: Diatonic(self.tonic, (3, 6)).
2. Calls that Diatonic object's ascending() to get a one-octave ascending list. Typical Diatonic.ascending() returns the 7 distinct degrees plus the top tonic (length 8).
3. Slices off the final tonic with [:-1] to produce a 7-note single-octave pattern (variable named notes).
4. Repeats that 7-note pattern self.octaves times via list repetition notes * self.octaves.
5. Appends the first element of notes (the tonic spelling) as the final top tonic, producing a list whose length is 7 * self.octaves + 1.
6. Returns the final list.

## Args:
    None

## Returns:
    list[str]:
        - Each element is a spelled pitch-class string (e.g., "C", "F#", "Bb").
        - Layout: (7-note single-octave pattern repeated self.octaves times) followed by the tonic spelled once more as the final element.
        - Length: 7 * self.octaves + 1 when preconditions are met.
        - Example:
            * If self.tonic == "C" and self.octaves == 1, return ["C", "D", "E", "F", "G", "A", "B", "C"].
            * If self.tonic == "C" and self.octaves == 2, return ["C","D","E","F","G","A","B","C","D","E","F","G","A","B","C"].

## Raises:
    - Propagates any exception thrown by Diatonic(...) or Diatonic.ascending(). Concretely this may include:
        * NoteFormatError or FormatError when the provided tonic string is invalid for the library's note/interval helpers.
        * Any ValueError, TypeError, or other exception raised by underlying utilities.
    - IndexError:
        * If the Diatonic.ascending() result used to compute notes yields an empty sequence (so notes = ...[:-1] is empty) then accessing notes[0] will raise IndexError.
        * This will commonly occur if the Diatonic helper returned an empty list or if self.octaves causes an empty repetition and the code attempts to index into notes.
    - TypeError:
        * If self.octaves is not an integer (for example, a float or None), Python will raise TypeError when attempting sequence repetition (notes * self.octaves).

## State Changes:
- Attributes READ:
    - self.tonic
    - self.octaves
- Attributes WRITTEN:
    - None. This method does not modify self or any external objects.

## Constraints:
- Preconditions:
    - self.tonic must be a valid, non-empty note string accepted by the library's note/interval utilities (typically a letter A-G with optional accidentals).
    - self.octaves must be an integer. Practical callers should use a positive integer (>= 1). If self.octaves <= 0 the method will either return an invalid sequence or raise IndexError when appending the tonic.
- Postconditions:
    - The returned list begins with a spelled tonic corresponding to the Diatonic helper's interpretation of self.tonic and ends with the same tonic spelled once as the final element.
    - The returned list length equals 7 * self.octaves + 1 when the preconditions hold.
    - No attributes on self are changed by the call.

## Side Effects:
    - Calls Diatonic(self.tonic, (3, 6)) and its ascending() method to derive the core single-octave pattern. Those calls are library-internal; this method itself performs no I/O, network calls, or mutation of global state.
    - Any side effects (errors or internal cache changes) originate from the Diatonic constructor or interval/note helper functions, not from this method directly.

## Notes and recommendations for callers:
- Validate tonic and octaves before calling if you require early, user-friendly error messages (e.g., raise a ValueError if octaves < 1).
- Avoid setting octaves to 0 or negative values; doing so will cause an IndexError when the method appends the tonic.
- If you need per-octave tonic spellings (e.g., explicit octave numbers), post-process the returned pitch-class strings — this method returns pitch-classes without octave numerals.

## `mingus.core.scales.Aeolian` · *class*

## Summary:
Represents the Aeolian (natural minor) musical scale rooted at a given tonic and spanning a configurable number of octaves.

## Description:
Aeolian is a concrete _Scale subclass that constructs the natural minor (Aeolian) scale by delegating the per-octave step construction to the Diatonic scale helper with the semitone-step pattern (2, 5). It is appropriate to instantiate when a caller needs the spelled pitch-class sequence of the Aeolian mode (natural minor) for rendering, analysis, chord construction, or degree lookup.

Known callers / usage patterns:
- Client code that builds or inspects modal scales (for example, melodic generation or chord extraction).
- Libraries or higher-level APIs that expect a _Scale-compatible object and call ascending(), descending(), degree(), or len().
- No special factories are required; instantiate directly.

Responsibility boundary:
- Aeolian is responsible only for producing the spelled note sequence for the Aeolian mode given a tonic and octaves.
- It relies on Diatonic for the core per-octave stepping algorithm and on the _Scale base-class for tonic/octaves storage and contract enforcement.
- It does not perform I/O, manage external resources, or mutate inherited state when computing sequences.

## State:
- type (class attribute)
    - Type: str
    - Value: "ancient"
    - Role: descriptive classification for the scale family; constant for all Aeolian instances.

- tonic (instance attribute; inherited from _Scale)
    - Type: str
    - Meaning: the root pitch-class of the scale (e.g., "A", "C#", "F").
    - Constraints: must not be given as a fully lowercase string (see Raises). Typically a letter A-G optionally with accidentals.
    - Invariant: remains equal to the constructor-supplied value for the lifetime of the instance unless mutated externally.

- octaves (instance attribute; inherited from _Scale)
    - Type: integer-like (the code treats it as a sequence repetition count)
    - Meaning: number of octaves the returned ascending() sequence should span.
    - Default: 1 when omitted in the constructor.
    - Valid values: intended to be a positive integer; the base class does not enforce positivity. Non-integer or non-positive values will produce unexpected results (e.g., sequence repetition semantics for 0 or negative/float values).
    - Invariant: remains equal to the constructor-supplied value for the lifetime of the instance unless mutated externally.

- name (instance attribute)
    - Type: str
    - Value set in __init__: "{tonic} aeolian" (e.g., "A aeolian")
    - Role: human-readable representation used by __repr__ and str utilities.

Class invariants:
- ascending() must return a list-like sequence of spelled pitch-classes starting at self.tonic, spanning 7 * self.octaves + 1 elements, and ending with the tonic repeated at the top octave.
- ascending() is a pure accessor and does not modify instance attributes.

## Lifecycle:
Creation
- Constructor signature: Aeolian(note, octaves=1)
    - note (str): required. The tonic/pitch-class string.
    - octaves (int, optional): how many octaves the scale should span (default 1).
- Behavior:
    - Calls _Scale.__init__(note, octaves) to set tonic and octaves.
    - Sets self.name to "{0} aeolian".format(self.tonic).
    - No further validation is performed on octaves by Aeolian.

Usage
- Typical sequence:
    1. Instantiate: s = Aeolian("A", 1)
    2. Retrieve ascending scale: s.ascending() → list of note strings (e.g., ["A","B","C","D","E","F","G","A"] for A Aeolian with octaves=1).
    3. Use inherited helpers: s.descending(), s.degree(n), len(s), comparisons, etc.
- Method sequencing: ascending() may be called repeatedly and is expected to be side-effect-free. There are no ordering constraints across methods; any public method may be invoked at any time after construction.

Destruction / cleanup
- No cleanup required. Aeolian does not hold external resources or implement context-manager or close semantics.

## Method Map:
graph TD
    A[__init__(note, octaves)] --> B[_Scale.__init__(note, octaves)]
    B --> C[name set -> "{tonic} aeolian"]
    D[ascending()] --> E[Diatonic(self.tonic, (2,5)).ascending()]
    E --> F[strip final tonic element ([:-1]) -> notes (7 elements)]
    F --> G[return notes * self.octaves + [notes[0]]]
    style A fill:#f9f,stroke:#333,stroke-width:1px
    style D fill:#ff9,stroke:#333,stroke-width:1px

(Explanation: __init__ delegates tonic/octaves storage to _Scale, then sets name. ascending() constructs a temporary Diatonic object configured with the Aeolian semitone indices (2 and 5), takes its single-octave degrees (excluding the final duplicate), repeats that 7-note pattern self.octaves times, and appends the top tonic.)

## Behavior details (ascending()):
- Implementation summary:
    - Creates a Diatonic instance for one octave with semitone indices (2, 5).
    - Calls that Diatonic instance's ascending() to get an 8-element list (7 distinct degrees + final tonic).
    - Drops the final tonic element to obtain the 7 distinct degrees for a single octave.
    - Repeats that 7-element pattern self.octaves times and finally appends the first degree (tonic) to produce a list of length 7*self.octaves + 1.
- Return type: list[str]
- Example length relationship:
    - For octaves == N, len(ascending()) == 7 * N + 1
- Purity: ascending() does not modify self; it constructs a transient Diatonic object and uses its result.

## Raises:
- NoteFormatError (propagated from _Scale.__init__)
    - Trigger: if the provided note argument is a fully lowercase string (note.islower() is True).
    - Message: "Unrecognised note '%s'" % note

- Exceptions propagated from Diatonic.ascending() or the underlying interval helpers:
    - Possible exceptions include NoteFormatError, FormatError, IndexError, KeyError, TypeError, etc., depending on the validity of self.tonic and the lower-level helpers' behavior.
    - These arise when the tonic is malformed (empty string, invalid characters) or when lower-level utilities encounter invalid inputs.

- No additional exceptions are raised explicitly by Aeolian itself. There is no explicit validation of octaves; misuse (e.g., non-integer octaves) may cause TypeError or logically unexpected results in sequence repetition.

## Example:
- Create a one-octave A Aeolian scale and fetch ascending notes:
    s = Aeolian("A", 1)
    print(s.name)            # "A aeolian"
    notes = s.ascending()    # ["A", "B", "C", "D", "E", "F", "G", "A"]
    print(len(notes))        # 8 (7 * 1 + 1)

- Two-octave example:
    s2 = Aeolian("A", 2)
    notes2 = s2.ascending()
    # len(notes2) == 15 (7*2 + 1)
    # notes2 begins with the 7-note pattern repeated twice and ends with the tonic.

Developer notes and constraints
- Provide an uppercase (or at least non-fully-lowercase) tonic string to avoid NoteFormatError.
- Prefer positive integer octaves. If you need to enforce bounds (e.g., octaves >= 1), validate before constructing Aeolian.
- The spelled accidentals and enharmonic choices are determined by the underlying Diatonic and interval helpers; Aeolian delegates musical spelling to them.

### `mingus.core.scales.Aeolian.__init__` · *method*

## Summary:
Initializes an Aeolian scale instance by delegating tonic and octave storage to the base _Scale constructor and then setting a human-readable name attribute of the form "<tonic> aeolian". The call modifies the instance state but returns None.

## Description:
Known callers and context:
- Instantiated directly by client code that needs a concrete Aeolian (natural minor) scale, for example:
    - melodic/algorithmic composition modules,
    - APIs that construct or inspect modal scales,
    - test code that verifies scale spelling or degree lookup.
- Lifecycle stage: called once at object construction time. After this returns, callers typically call instance methods such as ascending(), descending(), degree(), or len().

Why this is a separate method:
- The constructor is responsible for object initialization and must call the inherited _Scale initialization (which performs tonic/octave storage and validation). The small Aeolian-specific step of forming a readable name from the established tonic is scale-specific and belongs in the subclass constructor rather than in a separate factory or inlined elsewhere.

## Args:
    note (str):
        - The tonic / root pitch-class for the scale (example: "A", "C#", "F").
        - Must be a musical note string acceptable to the base _Scale initializer; provide non-fully-lowercase strings to avoid trivial format rejections.
        - No normalization is performed here; the base class handles parsing/validation.
    octaves (int, optional):
        - Number of octaves the scale object will represent when accessed via ascending()/descending().
        - Defaults to 1.
        - Intended/expected values: positive integers (>= 1). The subclass does not enforce positivity; invalid or non-integer values may lead to unexpected behavior downstream.

## Returns:
    None

## Raises:
    - Any exception raised by _Scale.__init__(note, octaves) will propagate unchanged.
        - In typical usage this includes NoteFormatError when the supplied note string is unrecognized (for example, if it is fully lowercase).
        - Other validation or range exceptions raised by the base class (e.g., RangeError, FormatError) may also propagate depending on base-class validation logic.
    - Aeolian.__init__ itself does not raise new exceptions beyond propagation from the base constructor.

## State Changes:
    Attributes READ:
        - self.tonic (read after the base constructor returns) to format the name string.
    Attributes WRITTEN:
        - self.tonic (written by the called _Scale.__init__; this constructor relies on that side-effect).
        - self.octaves (written by the called _Scale.__init__).
        - self.name (written here): set to the string "{tonic} aeolian" where {tonic} is the value of self.tonic after base initialization.

## Constraints:
    Preconditions:
        - The provided note must be acceptable to the base _Scale constructor (not a fully-lowercase string, non-empty, valid note tokens).
        - octaves should be an integer-like value; non-integer types may lead to TypeError elsewhere.
    Postconditions:
        - After successful return:
            - self.tonic is set to the parsed/normalized tonic value assigned by _Scale.__init__.
            - self.octaves is set to the provided octaves value (or default 1).
            - self.name equals "{0} aeolian".format(self.tonic).
        - The object is ready for use by other scale methods (ascending(), descending(), degree(), etc.).

## Side Effects:
    - No I/O operations or external service calls are performed.
    - Mutates the instance by setting attributes as listed above.
    - May indirectly cause exceptions or validation side-effects originating from the _Scale constructor (input validation, error-raising), but no external resources are modified.

### `mingus.core.scales.Aeolian.ascending` · *method*

## Summary:
Constructs and returns the ascending Aeolian (natural minor) scale starting from the instance's tonic across the configured number of octaves; the method does not modify the object but returns a list of spelled pitch-classes with the top tonic appended.

## Description:
- Known callers / usage context:
    - Called by any consumer that needs the ordered ascending tones of an Aeolian (natural minor) scale (for display, melodic generation, chord derivation, exporting, etc.).
    - Typical lifecycle: After an Aeolian instance is constructed (providing a tonic and an octaves count), clients call ascending() to obtain the scale tones in ascending order spanning the requested number of octaves.
- Why this is a separate method:
    - The Aeolian scale is implemented by delegating to a Diatonic scale with the Aeolian semitone pattern and then transforming that output into the expected per-octave repetition form. Packaging that logic into its own method keeps the mode-specific construction separate from generic Diatonic logic and avoids duplicating the post-processing steps elsewhere.

## Args:
    None

## Returns:
    list[str]:
        - A list of spelled pitch-class strings (e.g., "C", "G#", "Bb").
        - Construction rule:
            1. Construct a Diatonic scale for the same tonic using the semitone pattern that defines Aeolian (the code uses the pattern (2, 5) to indicate semitone steps).
            2. Obtain the Diatonic ascending sequence and drop its final tonic (so you have one 7-note octave pattern).
            3. Repeat that 7-note pattern self.octaves times, then append the first note of the pattern once more as the final top tonic.
        - Length: 7 * self.octaves + 1 (for example, with octaves == 1 you get 8 notes: 7 distinct scale degrees plus the top tonic).
        - Example:
            * If self.tonic == "A" and self.octaves == 1, the returned list will represent the A natural minor (Aeolian) scale, e.g. ["A", "B", "C", "D", "E", "F", "G", "A"] (spelling depends on underlying note utilities).

## Raises:
    - Propagates exceptions raised by constructing the Diatonic helper or by its ascending() method; possible exceptions include:
        - NoteFormatError / FormatError: if self.tonic is not a validly formatted pitch-string (invalid characters, empty string, or otherwise unacceptable format to the note utilities).
        - RangeError: if the octaves value or other numeric bounds used by Diatonic are out of an allowed range (as raised by lower-level validation).
        - TypeError: if self.octaves is not an integer (sequence repetition or arithmetic may fail), or if types passed to Diatonic are invalid.
        - IndexError: only if the Diatonic helper returns an unexpectedly empty sequence and the method attempts to access the first element; in normal, valid inputs this should not occur.
    - The method itself performs no explicit validation and therefore raises nothing beyond what its callees raise.

## State Changes:
- Attributes READ:
    - self.tonic
    - self.octaves
- Attributes WRITTEN:
    - None (the method does not modify any attributes of self)

## Constraints:
- Preconditions:
    - self.tonic must be a valid non-empty pitch string acceptable to the codebase's note/interval utilities (first character A-G; accidentals permitted per project conventions).
    - self.octaves must be an integer (practically >= 1). Non-positive, non-integer, or otherwise invalid values will lead to errors or logically incorrect results.
- Postconditions:
    - The returned list starts with self.tonic (as spelled by the underlying helpers) and ends with that tonic again (representing the top of the final octave).
    - No attributes of self are changed by the call.
    - The returned sequence consists of repeated 7-note Aeolian octave patterns followed by the tonic (total length 7 * self.octaves + 1) provided inputs met the preconditions.

## Side Effects:
    - No I/O is performed.
    - No global state is modified directly by this method.
    - Only side effects possible are those from the Diatonic constructor or Diatonic.ascending() (which may raise exceptions); those helpers are normally pure and do not perform I/O.

## `mingus.core.scales.Locrian` · *class*

## Summary:
Represents the Locrian modal scale anchored at a given tonic and spanning a specified number of octaves. Provides the spelled ascending sequence of scale degrees.

## Description:
The Locrian class is a concrete _Scale subclass implementing the Locrian modal pattern. Instantiate it when you need the ordered, spelled pitch-class names for the Locrian scale (for display, melodic generation, chord extraction, or exporting). Typical callers construct a Locrian instance (for example, Locrian("B", octaves=2)) and call ascending() to obtain the scale tones.

Motivation and responsibility:
- Encapsulates the Locrian-specific semitone pattern and repetition logic so callers do not reconstruct it each time.
- Responsibility: compute and return the spelled ascending note sequence for the Locrian scale based on the stored tonic and octaves.
- Boundary: delegates input validation and core state initialization to _Scale (which enforces a minimal tonic-format check and sets tonic and octaves) and delegates sequence construction to the Diatonic helper (constructed with the Locrian semitone descriptor). _Scale also expects subclasses to provide a human-readable name (self.name) used by __repr__; Locrian sets self.name = "{tonic} locrian" to satisfy this expectation. Locrian itself does not perform additional validation or I/O, nor does it mutate instance state.

## State:
- Class attributes:
    - type (str)
        - Value: "ancient"
        - Meaning: descriptive category for the scale class, constant.

- Instance attributes (set in construction):
    - tonic (str)
        - Source: provided note argument forwarded to _Scale.__init__
        - Example values: "C", "G#", "Bb"
        - Constraints: _Scale.__init__ raises NoteFormatError if note.islower() is True (i.e., purely lowercase input is rejected).
        - Invariant: remains equal to the constructor-supplied tonic unless mutated externally.

    - octaves (int-like)
        - Source: provided octaves argument forwarded to _Scale.__init__
        - Default: 1
        - Valid range: practically >= 1 (the code uses this for sequence repetition). The base class does not coerce or validate; non-integer or negative values will produce TypeError/logic errors when used for repetition.
        - Invariant: remains equal to the constructor-supplied value unless mutated externally.

    - name (str)
        - Value set in Locrian.__init__: "{tonic} locrian"
        - Example: if tonic == "B", name == "B locrian"
        - Purpose: human-readable name used by __repr__ / debugging; satisfying the _Scale expectation that subclasses define a human-readable name.

Class invariants:
- self.name equals "{0} locrian".format(self.tonic)
- ascending() returns a list-like sequence starting with the tonic and ending with the tonic as the final element.
- Methods must not mutate tonic, octaves, or name.

## Lifecycle:
- Creation
    - Call Locrian(note, octaves=1).
    - Required arguments:
        * note (str): tonic; must not be a purely-lowercase string (otherwise NoteFormatError).
        * octaves (int, optional): defaults to 1. Caller should pass an integer >= 1.
    - The constructor delegates to _Scale.__init__ which sets self.tonic and self.octaves and may raise NoteFormatError for invalid note format. Locrian.__init__ sets self.name to the canonical locrian name.

- Usage
    - Primary method: ascending()
        * Call ascending() to obtain the spelled ascending notes for the Locrian scale across self.octaves.
        * ascending() is pure with respect to instance state (reads self.tonic and self.octaves only).
    - Typical sequence:
        1. Instantiate Locrian.
        2. Call ascending() any number of times to retrieve the note list.
        3. Use the returned list for degree lookups, rendering, or further processing.
    - No required ordering between multiple method calls; ascending() can be called repeatedly.

- Destruction / cleanup
    - There are no external resources to release. No context-manager or close() required.

## Method Map:
graph TD
    A[Locrian.__init__(note, octaves=1)] --> B[set tonic, octaves via _Scale.__init__]
    B --> C[set name = "{tonic} locrian"]
    C --> D[Locrian.ascending()]
    D --> E[Diatonic.__init__(tonic, semitones=(1,4), octaves=1)]
    E --> F[Diatonic.ascending()]
    F --> G[intervals helpers (major/minor seconds)]
    style A fill:#f2f9ff,stroke:#333
    style D fill:#eef9f2,stroke:#333

(Note: Diatonic is constructed internally with semitones=(1,4) to represent the Locrian step pattern; ascending() uses Diatonic.ascending(), slices off the top tonic, repeats the 7-note pattern self.octaves times, and appends the tonic to close the scale.)

## Behavior of ascending():
- Implementation summary (behavioral, not code):
    - Construct a Diatonic instance with the same tonic and semitone descriptor (1,4).
    - Call its ascending() which returns a list of length 8 for a single octave (7 scale degrees + final tonic).
    - Remove the trailing final tonic (take all but the last element) to obtain the 7-degree per-octave pattern.
    - Repeat that 7-element pattern self.octaves times (sequence multiplication).
    - Append the first element of the per-octave pattern (the tonic) once to close the scale.
- Return:
    - list[str] of spelled pitch-class names.
    - Length: 7 * self.octaves + 1
    - First element: the tonic (as spelled by the helpers).
    - Last element: the tonic repeated as the final closing tone.

## Raises:
- NoteFormatError
    - Source: _Scale.__init__ when the provided note argument is a purely-lowercase string (note.islower() is True).
    - Trigger condition: passing a lowercase-only tonic string like "c" instead of "C".

- Exceptions propagated from Diatonic construction or Diatonic.ascending():
    - NoteFormatError / FormatError
        - Triggered when the underlying note/interval helpers cannot parse or format the tonic string.
    - RangeError
        - Triggered by degree/interval helpers if an invalid degree or index is requested (propagated; Locrian itself does not explicitly raise it).
    - TypeError / ValueError / IndexError
        - Possible when octaves is non-integer, negative, or when interval helpers encounter empty or malformed strings; these are not raised deliberately by Locrian but may propagate.

Notes on validation:
- _Scale performs minimal validation and core initialization (notably rejecting purely-lowercase tonic strings and assigning tonic and octaves). _Scale also documents that subclasses should define a human-readable name (self.name) used by __repr__; Locrian satisfies this by setting name = "{tonic} locrian". Diatonic is responsible for constructing the diatonic sequence for the provided semitone descriptor (1,4). Locrian does not add further validation or mutate inputs; callers should validate tonic and octaves if stricter checks are required.

## Example:
- Create a one-octave Locrian and get its ascending notes:
    - Instantiate: Locrian("B")  # tonic "B", octaves default to 1
    - Call: ascending() -> returns the 8-note spelled sequence: ["B", "C", "D", "E", "F", "G", "A", "B"] (accidentals depend on the library's spelling rules).
- Create a two-octave Locrian:
    - Instantiate: Locrian("B", octaves=2)
    - Call: ascending() -> returns 15 notes: the 7-note pattern repeated twice plus the final tonic, e.g. ["B","C","D","E","F","G","A","B","C","D","E","F","G","A","B"].

Developer notes:
- Because _Scale does not validate octaves, callers should pass an integer >= 1. Non-integer or negative values will likely raise TypeError or produce logically invalid output when the method repeats lists.
- ascending() is pure with respect to instance state; it can be called repeatedly without side effects.

### `mingus.core.scales.Locrian.__init__` · *method*

## Summary:
Initializes a Locrian scale instance by delegating base initialization to the Scale superclass and setting the human-readable scale name on the instance.

## Description:
This constructor is invoked when a caller creates a Locrian object (for example, Locrian("B") or Locrian("B", octaves=2)). It runs during object construction as part of the instance creation lifecycle. The method delegates note and octave validation plus core attribute initialization (tonic and octaves) to the superclass _Scale via super(Locrian, self).__init__(note, octaves), then records a human-readable name string for the instance (used by __repr__ and debugging).

Known callers and context:
- Typical callers: application code or library utilities constructing scale objects to obtain spelled degree lists (e.g., Locrian("B").ascending()).
- Lifecycle stage: constructor — executed immediately after memory allocation for the new Locrian instance, before other instance methods (like ascending()) are used.
- Rationale for separation: validation and core state setup are centralized in _Scale; Locrian.__init__ only supplies the Locrian-specific name so subclasses remain small and focused.

## Args:
    note (str):
        The tonic note for the scale (e.g., "C", "G#", "Bb"). Must be in the format accepted by the library's note/key helpers.
    octaves (int, optional):
        Number of octaves the scale should span when requested (used later by methods such as ascending()).
        Default: 1
        Recommended/expected values: positive integers (>= 1). The base class does minimal validation; non-integer or negative values may cause errors when used elsewhere.

## Returns:
    None
    (Constructors in Python do not return a value; the method initializes instance state. On successful completion, the instance will have attributes set by _Scale and Locrian: notably self.tonic, self.octaves (from _Scale) and self.name (set here).)

## Raises:
    NoteFormatError
        - Condition: propagated from _Scale.__init__ when the provided note string fails the base-format check (e.g., a purely-lowercase tonic like "c" that the library rejects).
    FormatError
        - Condition: may be propagated if underlying helpers invoked by _Scale (or subsequent initialization performed by super) encounter formatting problems with the note.
    RangeError
        - Condition: may be propagated from deeper helpers if an invalid range/index is requested during base initialization.
    Any exception raised inside _Scale.__init__ or by Python when invalid argument types are passed (TypeError, ValueError) may be propagated to the caller. If an exception is raised by the superclass, Locrian.__init__ does not set self.name.

## State Changes:
Attributes READ:
    self.tonic
        - Read implicitly when formatting the name; note that self.tonic is expected to have been set by the superclass call prior to this read.
Attributes WRITTEN:
    self.name
        - Written to the string "{tonic} locrian" where {tonic} is the value of self.tonic after superclass initialization.
Indirect (via super call):
    self.tonic, self.octaves
        - These are initialized by the superclass _Scale.__init__ called at the start of this method.

## Constraints:
Preconditions:
    - The provided note must be in a format accepted by the library (not purely lowercase, and parsable by the note/key helpers used by _Scale).
    - octaves should be an integer-like value appropriate for repetition logic (recommended >= 1).
Postconditions:
    - On successful return, self.tonic and self.octaves have been initialized by the superclass, and self.name equals "{0} locrian".format(self.tonic).
    - If the superclass raises, no guarantees about instance attribute values are provided (self.name will not be set).

## Side Effects:
    - No I/O, no global state mutation, no external service calls.
    - The only mutation performed by this method (beyond the superclass call) is setting the instance attribute self.name.
    - Exceptions raised by the superclass propagate to the caller; this method does not catch or suppress them.

### `mingus.core.scales.Locrian.ascending` · *method*

## Summary:
Return the ascending sequence of pitch-class names that form the Locrian scale starting at the object's tonic across the configured number of octaves. The method reads self.tonic and self.octaves but does not modify the object's state.

## Description:
- Known callers and usage context:
    - Consumers of the Locrian scale object call this when they need the ordered list of scale tones for display, melodic generation, chord extraction, or exporting. Typical usage is after constructing a Locrian instance (for example: Locrian("B", octaves=2)) and wanting the spelled notes for one or more octaves.
    - This method is invoked during the scale-to-notes stage of music-processing pipelines: instantiate a scale object, then call ascending() to obtain a concrete list of note names to iterate, render, or transform.
- Why this logic is a dedicated method:
    - The Locrian scale is a specific diatonic pattern (it uses a diatonic helper with a concrete semitone pattern). This method encapsulates the pattern and repetition logic (use of Diatonic with semitone pattern (1, 4), removal of the duplicate top tonic, repetition for multiple octaves, and appending the final tonic) so callers do not need to reconstruct the pattern each time. Separating it keeps the scale class focused and reuses the generic Diatonic generator.

## Args:
    None

## Returns:
    list[str]: 
        - A list of spelled pitch-class strings (letters A-G with accidentals like '#' or 'b' where applicable).
        - The sequence starts at the object's tonic (self.tonic), proceeds stepwise according to the Locrian semitone pattern, repeats the 7-note diatonic pattern self.octaves times, and ends with the tonic spelled again as the final closing note.
        - Length: 7 * self.octaves + 1 (each octave contributes seven distinct diatonic scale degrees; the final tonic is appended once).
        - Example (illustrative): If self.tonic == "B" and self.octaves == 1, return might look like ["B", "C", "D", "E", "F", "G", "A", "B"] (actual accidentals depend on the spelling rules used by the lower-level helpers).

## Raises:
    - Propagates exceptions raised by the Diatonic constructor or Diatonic.ascending(), typically when the provided tonic or internal helpers are invalid:
        * NoteFormatError / FormatError: if self.tonic uses an invalid note format.
        * RangeError: if an underlying helper detects an out-of-range value.
        * TypeError / ValueError: if self.octaves or other inputs have an inappropriate type or value.
    - The method performs no bespoke validation and therefore does not raise additional custom exceptions itself; callers should validate parameters if early checks are required.

## State Changes:
- Attributes READ:
    - self.tonic
    - self.octaves
- Attributes WRITTEN:
    - None. This method does not modify any attributes of self.

## Constraints:
- Preconditions:
    - self.tonic must be a valid, non-empty pitch string appropriate for the underlying note/interval helpers (typically a letter A-G with optional accidentals).
    - self.octaves should be an integer (practically >= 1). Non-integer or negative values will lead to TypeError or logically incorrect results when repeating sequences.
- Postconditions:
    - The returned list begins with self.tonic (or its spelled equivalent returned by the Diatonic helper) and ends with that tonic repeated as the final element.
    - No attributes of the Locrian instance are changed.
    - The internal Diatonic helper is constructed with the semitone-index pattern (1, 4) to produce the Locrian step pattern; the method then removes the trailing tonic from that helper's output, repeats the resulting 7-note pattern self.octaves times, and appends the first note to close the scale.

## Side Effects:
    - No I/O, logging, or external service calls are performed by this method.
    - The only side effects possible are those produced by called helpers (Diatonic constructor and Diatonic.ascending()); those helpers are expected to be pure (aside from raising exceptions) and not perform external I/O.

## `mingus.core.scales.Major` · *class*

## Summary:
Represents a major (Ionian) scale anchored at a tonic pitch-class and spanning a configurable number of octaves. Provides an ascending() accessor that returns the diatonic pitch-classes for the tonic repeated by octave and closed by the tonic one degree above the final octave.

## Description:
Instantiate this class when you need a concrete Scale object modeling the diatonic major scale for a given tonic (examples: "C", "G#", "Bb") and a specified number of octaves. Typical callers include notation/rendering code, exercise generators, transposition utilities, and any consumer that requires the ordered list of scale degrees for a major key.

Major is a minimal concrete subclass of _Scale. It:
- Sets the class attribute type = "major".
- Calls the _Scale constructor to initialize tonic and octaves.
- Sets a human-readable name ("{tonic} major").
- Implements ascending() by delegating to mingus.core.keys.get_notes(self.tonic) to obtain the canonical seven diatonic pitch-class names for the tonic, repeats that 7-note sequence self.octaves times, and appends the tonic once to close the final octave.

Major purposely delegates accidentals/tonic normalization to get_notes and does not reimplement key-signature logic.

## State:
- Class attributes:
    - type (str): constant "major".

- Instance attributes (set during __init__):
    - tonic (str)
        - Type: str
        - Description: the tonic pitch-class used by the scale.
        - Valid format: a pitch-class string accepted by mingus.core.keys.get_notes — specifically, a single uppercase letter A–G optionally followed by a single accidental symbol '#' or 'b' (examples: "C", "D#", "Bb"). Case and format must match what get_notes/is_valid_key expect; passing a lowercase-only string (e.g., "c") will cause _Scale.__init__ to raise NoteFormatError.
        - Invariant: remains equal to the constructor-supplied value unless mutated externally.
    - octaves (int)
        - Type: int (expected)
        - Description: the number of octaves to span.
        - Default: 1
        - Valid values: non-negative integers (0, 1, 2, ...). The implementation relies on integer list-repetition semantics. Non-integer values will cause runtime TypeError when ascending() is invoked.
        - Invariant: remains equal to the constructor-supplied value unless mutated externally.
    - name (str)
        - Type: str
        - Description: set to "{tonic} major" in Major.__init__ (for example: "C major").

Class invariants:
- ascending() returns a list-like sequence of pitch-class strings produced by get_notes(self.tonic) repeated octaves times and then appended with the tonic once; therefore its length equals 7 * octaves + 1 when get_notes returns the canonical seven notes.
- ascending() does not modify instance attributes.

## Lifecycle:
- Creation:
    - Instantiate via Major(note, octaves=1)
        * note (str): tonic pitch-class string in the format accepted by get_notes (uppercase letter A–G optionally with '#' or 'b'). _Scale.__init__ rejects fully-lowercase strings.
        * octaves (int, optional): non-negative integer number of octaves to span; defaults to 1.
    - __init__ behavior:
        * Delegates to _Scale.__init__(note, octaves) which sets self.tonic and self.octaves and raises NoteFormatError if the note string is fully lowercase.
        * Sets self.name to "{0} major".format(self.tonic).
- Usage:
    - Call ascending() to obtain the major scale pitch-class sequence across octaves.
    - Use inherited helpers from _Scale (descending(), degree(), len(), comparisons, __repr__) as needed. No special sequencing is required beyond constructing the instance before calling accessors.
- Destruction:
    - No cleanup necessary; no context-manager or close semantics.

## Method Map:
flowchart TD
    A[Major.__init__(note, octaves=1)]
    A --> B[_Scale.__init__ sets self.tonic and self.octaves]
    B --> C[Major sets self.name = "{tonic} major"]
    C --> D[ascending()]
    D --> E[get_notes(self.tonic) -> 7 pitch-classes]
    E --> F[repeat notes self.octaves times: notes * self.octaves]
    F --> G[append tonic once: + [notes[0]]]
    G --> H[return final list (length = 7 * octaves + 1)]

## Raises:
- From __init__:
    - mingus.core.mt_exceptions.NoteFormatError
        * Trigger: delegated from _Scale.__init__ when the provided note string is fully lowercase (note.islower() is True).
- From ascending() (propagated from collaborators or by incorrect octaves type):
    - mingus.core.mt_exceptions.NoteFormatError
        * Trigger: get_notes(self.tonic) raises this when self.tonic is not a recognized key string.
    - TypeError
        * Trigger: if self.octaves is not an integer (e.g., float or None), performing notes * self.octaves will raise TypeError.
    - ValueError, IndexError, or other exceptions from get_notes
        * Trigger: any inconsistency or error inside get_notes or its helpers will propagate.
- Notes about _Scale APIs:
    - When callers use degree(n, ...) on a Major instance, _Scale.degree may raise RangeError (n < 1) or FormatError (invalid direction); these are not raised by Major directly but are relevant to consumers.

## Example:
- One-octave C major:
    s = Major("C")               # tonic "C", octaves defaults to 1; name "C major"
    s.ascending()                # ["C", "D", "E", "F", "G", "A", "B", "C"]

- Zero-octave behavior (edge case):
    s = Major("C", octaves=0)
    s.ascending()                # ["C"]  (notes * 0 yields [] + [notes[0]] => single tonic)

- Two-octave G major:
    s = Major("G", octaves=2)
    s.ascending()                # ["G","A","B","C","D","E","F#","G","A","B","C","D","E","F#","G"]

- Error examples:
    Major("c")                   # __init__ raises NoteFormatError (tonic was all-lowercase)
    s = Major("C", octaves=1.5)  # ascending() raises TypeError when attempting notes * 1.5

Implementation notes for reimplementers:
- Delegate generation of the seven diatonic pitch-classes to get_notes(self.tonic); do not reproduce key-signature logic in this class.
- Accept and store octaves as provided, but consider validating/coercing to int >= 0 if stricter behavior is desired.
- ascending() should return a new list and must not mutate instance attributes.

### `mingus.core.scales.Major.__init__` · *method*

## Summary:
Initializes a Major scale instance by delegating tonic and octave setup to the scale base class and recording a human-readable name ("{tonic} major") on the instance, affecting the object's tonic, octaves, and name attributes.

## Description:
This constructor is called when creating a Major scale object (e.g., Major("C"), Major("G#", octaves=2)). It performs two responsibilities:
1. Delegates to the superclass constructor to validate and store the tonic and octaves (this is where tonic normalization/validation occurs).
2. Sets a user-facing name string derived from the normalized tonic.

Known callers and context:
- Typical callers are client code constructing scale objects for notation, analysis, transposition, exercise generation, or rendering pipelines. The constructor is invoked at object creation time — the beginning of the Major instance lifecycle.
- It exists as a separate method to keep scale-specific naming logic in the concrete subclass while centralizing tonic validation and core state initialization in the shared _Scale base class.

Why this logic lives here:
- Validation and canonicalization of the tonic and storage of octaves are shared across scale subclasses and therefore belong in the superclass.
- The Major subclass augments that shared initialization with a Major-specific human-readable name; separating this keeps responsibilities clear and avoids duplicating key logic.

## Args:
    note (str):
        The tonic pitch-class for the scale. Must be a string format accepted by the shared scale initializer (typically an uppercase letter A–G optionally followed by '#' or 'b', for example "C", "F#", "Bb"). The exact validation and normalization occur in the superclass constructor and may raise a NoteFormatError for invalid formats (for example, a wholly-lowercase string).
    octaves (int, optional):
        Number of octaves the scale instance should span. Defaults to 1. Expected to be a non-negative integer. The constructor stores the value as provided; invalid types or negative values may not be immediately rejected here (validation/coercion is performed by the superclass if implemented there). Passing a non-integer (e.g., float) will typically not raise at construction time but may cause errors later when consumers use octaves (for example, when replicating note lists).

## Returns:
    None

## Raises:
    mingus.core.mt_exceptions.NoteFormatError
        Raised by the delegated superclass constructor when the provided note string is not in an acceptable format (for example, when it is fully lowercase). This method itself does not explicitly raise exceptions but will propagate exceptions thrown by super(...).__init__.

## State Changes:
Attributes READ:
    - self.tonic
        * Read after the superclass initializer returns (used to build the human-readable name).
Attributes WRITTEN:
    - self.tonic
        * Written by the superclass constructor invoked via super(...).__init__(note, octaves).
    - self.octaves
        * Written by the superclass constructor invoked via super(...).__init__(note, octaves).
    - self.name
        * Written by this method and set to the string "{tonic} major" where tonic is the normalized tonic value stored by the superclass.

## Constraints:
Preconditions:
    - The caller must pass a note value that the superclass initializer can accept (commonly an uppercase A–G optionally followed by '#' or 'b'). Passing an unsupported format (e.g., fully-lowercase) will cause the superclass to raise NoteFormatError.
    - octaves should be an integer >= 0 for predictable behavior of other scale accessors; however, the constructor stores the value as given and relies on the superclass (or later consumers) to enforce strict numeric validation if required.

Postconditions (guarantees after the call completes without exception):
    - self.tonic is set to the normalized tonic value established by the superclass.
    - self.octaves is set to the stored octaves value established by the superclass.
    - self.name is set to the string "{tonic} major" using the normalized self.tonic.

## Side Effects:
    - No I/O or external service calls.
    - Mutates instance attributes (self.tonic, self.octaves via the superclass, and self.name directly).
    - May propagate exceptions from the superclass initializer; it does not catch them.

### `mingus.core.scales.Major.ascending` · *method*

## Summary:
Return the ascending pitch-class sequence for this major scale across the configured number of octaves, appending the tonic one degree above the final octave.

## Description:
- Known callers and context:
    - Public consumers of Scale objects (library users or higher-level utilities) that request the ordered pitch-class sequence of a major scale for display, analysis, transposition, or rendering.
    - Typical lifecycle stage: invoked when a Major scale object has been constructed and a caller needs the explicit, ordered list of note names spanning the requested octaves (for example, when rendering a scale to notation, generating exercises, or computing melodic intervals).
- Reason this logic is a separate method:
    - Encapsulates the simple but commonly-needed convention of repeating the seven diatonic degrees for each octave and appending the scale's tonic at the top to close the final octave.
    - Keeps the Major class API explicit (Major.ascending) and avoids duplicating this formatting logic in multiple places that consume scale objects.

## Args:
    None (method takes only self).

## Returns:
    list[str]: A list of pitch-class name strings (e.g., "C", "F#", "Bb") in ascending order.
    - Under normal conditions (self.octaves is a non-negative integer and get_notes succeeds), the returned list length is 7 * self.octaves + 1:
        * The first 7 * self.octaves elements consist of the major scale degrees repeated for each octave in order.
        * The final element is the tonic (the first degree) repeated once to represent the scale-degree above the last octave.
    - Examples:
        * If get_notes(self.tonic) -> ["C","D","E","F","G","A","B"] and self.octaves == 1, the return is ["C","D","E","F","G","A","B","C"].
        * If self.octaves == 2, the return is the seven-note sequence repeated twice followed by "C" (length 15).

## Raises:
    - mingus.core.mt_exceptions.NoteFormatError:
        * Propagated from get_notes(self.tonic) when self.tonic is not a recognized key string.
    - TypeError:
        * If self.octaves is not an integer type (for example, a float or None), Python list multiplication will raise a TypeError ("can't multiply sequence by non-int of type 'float'"), or other operations may raise TypeError.
    - ValueError, IndexError, or other exceptions:
        * Any exceptions raised by get_notes (see get_notes documentation) such as ValueError or IndexError will propagate.
    - No exceptions are raised explicitly in this method itself; it relies on its collaborators' validations.

## State Changes:
- Attributes READ:
    - self.tonic
    - self.octaves
- Attributes WRITTEN:
    - None — this method does not modify the Major instance's attributes.

## Constraints:
- Preconditions:
    - self.tonic must be a valid key string acceptable to get_notes; otherwise get_notes will raise NoteFormatError.
    - self.octaves should be an integer (the Major class constructor uses an integer octaves parameter). For the documented length formula and normal behavior, self.octaves is expected to be a non-negative integer.
- Postconditions:
    - On normal return, no attributes of self are changed.
    - The returned list contains only pitch-class name strings as produced by get_notes and follows the length/form described above, assuming self.octaves is an integer >= 0.

## Side Effects:
    - Calls get_notes(self.tonic). get_notes may mutate module-level state (it caches computed note lists), so calling ascending may indirectly populate or update that cache.
    - No I/O, network calls, or mutations to objects other than the potential module-level cache mutated by get_notes.

## `mingus.core.scales.HarmonicMajor` · *class*

## Summary:
Represents the Harmonic Major scale anchored at a tonic pitch-class. It is implemented by deriving the Major scale for the tonic, lowering (diminishing) the sixth degree, and then repeating the resulting 7-degree pattern for the requested number of octaves, closing each span with the tonic an octave above.

## Description:
Instantiate this class when you need a concrete Scale object modeling the harmonic major collection for a given tonic (for example, "C", "G#", "Bb") and a specified number of octaves. The class exists to provide a simple, consistent interface (matching other scale classes in the module) that returns the ordered list of pitch-class names for the harmonic major scale.

Behavior detail:
- HarmonicMajor constructs its ascending scale by:
  1. Delegating to Major(self.tonic).ascending() to obtain the canonical major scale pitch-classes (the Major implementation returns a list containing seven scale degrees plus a final tonic duplicate).
  2. Removing the final duplicate tonic (ascending()[:-1]) to obtain the 7-degree pattern.
  3. Applying the library's diminish() function to the sixth degree (index 5) of that 7-degree pattern to lower that degree (the harmonic-major alteration).
  4. Repeating the resulting 7-note pattern self.octaves times and appending the tonic (pattern[0]) to close the final octave.
- The class reuses the _Scale base-class contract: ascending() must return a list-like sequence and must not mutate persistent instance state beyond setting self.name in __init__.

Typical callers:
- Notation/printing code, scale-based exercises/generators, transposition utilities, or any consumer that needs the ordered pitch-classes for a harmonic major scale.

Motivation:
HarmonicMajor provides a named, reusable abstraction for the musical concept "harmonic major" (major scale with a lowered sixth). It centralizes the small alteration relative to Major and exposes the same _Scale API so callers can use degree(), descending(), len(), and comparisons uniformly.

## State:
- Class attributes:
    - type (str)
        - Value: "major"
        - Role: semantic classification consistent with other scale implementations in the module.

- Instance attributes (inherited from _Scale and set by __init__):
    - tonic (str)
        - Source: parameter passed to __init__, stored by _Scale.__init__.
        - Valid values / constraints: must follow the project's pitch-class naming convention; _Scale.__init__ raises NoteFormatError if the string is fully lowercase (note.islower() is True).
        - Invariant: remains equal to constructor-supplied value unless mutated externally.
    - octaves (int)
        - Source: parameter passed to __init__, stored by _Scale.__init__.
        - Default: 1
        - Expected values: non-negative integers (0, 1, 2, ...). The class relies on Python list repetition semantics (notes * octaves). The implementation does not coerce or explicitly validate the type or sign.
        - Invariant: remains equal to constructor-supplied value unless mutated externally.
    - name (str)
        - Set in HarmonicMajor.__init__ to "{tonic} harmonic major" (for example, "C harmonic major").
        - Used by __repr__/__str__ via the base class.

Class invariants:
- ascending() produces a list whose length equals 7 * octaves + 1 when Major.ascending() yields seven unique scale degrees. The final element is the tonic duplicated at the top octave.
- The sixth degree (submediant) of the 7-degree pattern is modified by diminish() before octave repetition.
- Methods must not mutate tonic or octaves.

## Lifecycle:
Creation
- Constructor signature: HarmonicMajor(note, octaves=1)
    - note (str): tonic pitch-class string (expected to be accepted by Major/_Scale conventions). If note.islower() is True, _Scale.__init__ will raise mingus.core.mt_exceptions.NoteFormatError.
    - octaves (int, optional): number of octaves to span; default 1. Although the code does not validate octaves, callers should pass an integer >= 0.
- On construction:
    - The constructor delegates to _Scale.__init__(note, octaves) to set self.tonic and self.octaves and to enforce the base-class note-format check.
    - It sets self.name to "{0} harmonic major".format(self.tonic).

Usage
- Primary accessor:
    - ascending() — returns the harmonic major ascending pitch-class list according to the algorithm described in Description.
    - Typical sequence:
        1. Instantiate: s = HarmonicMajor("C", octaves=1)
        2. Read notes: notes = s.ascending()
        3. Use other inherited helpers: s.descending(), s.degree(n), len(s), comparisons, etc.
- Ordering constraints: No special call ordering beyond constructing the instance before calling accessors.

Destruction
- No external resources are allocated; no explicit cleanup is required.

## Method Map:
flowchart TD
    A[HarmonicMajor.__init__(note, octaves=1)]
    A --> B[_Scale.__init__ sets tonic, octaves (may raise NoteFormatError)]
    B --> C[HarmonicMajor sets self.name = "{tonic} harmonic major"]
    C --> D[ascending()]
    D --> E[call Major(self.tonic).ascending() -> major_notes_with_top_duplicate]
    E --> F[slice off final duplicate: major_pattern = major_notes_with_top_duplicate[:-1]]
    F --> G[apply diminish() to major_pattern[5] (6th degree)]
    G --> H[repeat pattern: major_pattern * self.octaves]
    H --> I[append tonic: + [major_pattern[0]]]
    I --> J[return final list]

## Raises:
- From __init__:
    - mingus.core.mt_exceptions.NoteFormatError
        - Trigger: delegated from _Scale.__init__ when the provided note string is fully lowercase (note.islower() is True).
- From ascending():
    - Propagated exceptions from Major(self.tonic).ascending():
        * mingus.core.mt_exceptions.NoteFormatError (if Major/get_notes rejects the tonic string)
        * Other exceptions that Major.ascending() or the underlying get_notes() may raise.
    - TypeError
        - Trigger: if self.octaves is not an integer (e.g., float or None), performing list repetition (pattern * self.octaves) will raise TypeError.
    - IndexError
        - Trigger: if Major(self.tonic).ascending() does not return the expected 7-degree pattern (plus duplicate) — for example, if the list is shorter than 6 elements, the assignment to notes[5] will raise IndexError. The implementation assumes Major returns the standard seven degrees.
    - Any exceptions raised by diminish(note) will propagate (e.g., NoteFormatError if diminish validates its input).

Notes on error semantics:
- The class assumes Major.ascending() returns a canonical 8-element list (7 degrees + tonic duplicate). If that assumption is violated by changes elsewhere, ascending() may raise IndexError. Callers who require stricter validation should validate inputs or pre-check the Major scale output before constructing HarmonicMajor.

## Example:
- One-octave C harmonic major:
    s = HarmonicMajor("C")                 # default octaves == 1
    s.name                                  # "C harmonic major"
    s.ascending()                            # ["C", "D", "E", "F", "G", <diminished A>, "B", "C"]
                                            # Note: the literal representation of the diminished sixth depends on the library's diminish() output (e.g., "A" -> "A♭" or "G#" normalization) — the class applies diminish() to the sixth degree.

- Two-octave G harmonic major:
    s = HarmonicMajor("G", octaves=2)
    s.ascending()                            # (7-degree modified pattern repeated twice) + [tonic]
                                            # length == 7 * 2 + 1 == 15

- Edge-case: zero octaves
    s = HarmonicMajor("C", octaves=0)
    s.ascending()                            # returns [pattern[0]] i.e., a single tonic (pattern * 0 yields [] + [pattern[0]])

Implementation notes for reimplementers:
- Rely on the existing Major class and the diminish() helper from mingus.core.notes rather than reimplementing key-signature or accidental manipulation.
- Preserve the _Scale contract: ascending() must return a list-like, must not mutate persistent self attributes, and must include the final tonic duplicate.
- Consider validating or coercing octaves to an integer >= 0 if you want stricter error messages than the current implicit TypeError/IndexError behavior.

### `mingus.core.scales.HarmonicMajor.__init__` · *method*

## Summary:
Initializes a HarmonicMajor scale instance by delegating tonic and octave setup to the scale base class and setting a human-readable name that reflects the tonic and that this is a harmonic major scale.

## Description:
This constructor is invoked during object creation (the typical lifecycle stage where a new scale instance is allocated and initialized). Known callers are any code that constructs a HarmonicMajor instance (for example notation/rendering code, exercise generators, transposition utilities, or tests). The method's logic is kept in __init__ because these steps are part of object initialization: invoking the superclass initializer to establish the canonical _Scale attributes (tonic, octaves, and any base-class validation) and then recording the concrete subclass' display name.

Behavioral summary:
- Calls the immediate superclass __init__ with the provided note and octaves to perform base-class initialization and validation.
- Uses the tonic value established by the superclass to compose and store the instance name in the form "{tonic} harmonic major".

Keeping this logic in __init__ ensures that every HarmonicMajor instance has the same canonical state (tonic, octaves, and name) immediately after construction and that base-class invariants and validation are respected.

## Args:
    note (str): The tonic pitch-class string supplied by the caller (examples: "C", "G#", "Bb").
        - Requirements: must be acceptable to the project's scale/key conventions; the base-class initializer will raise NoteFormatError if the string is entirely lowercase.
    octaves (int, optional): Number of octaves the scale should span. Defaults to 1.
        - Expected values: non-negative integers (0, 1, 2, ...). The constructor does not coerce or strictly validate this value; non-integer or negative values will typically surface errors later when consumers call methods that depend on integer repetition semantics.

## Returns:
    None: As a constructor, it does not return a value. On successful completion the instance is fully initialized and ready for use.

## Raises:
    mingus.core.mt_exceptions.NoteFormatError
        - Condition: propagated from the superclass __init__ when the provided note string fails the base-class format check (for example, if the note string is fully lowercase).
    Any exceptions raised by the superclass __init__ or underlying helpers (propagated)
        - Condition: the superclass may raise other exceptions for invalid inputs (e.g., invalid key name) or for other validation logic that changes in future versions. Those exceptions are not handled here and will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.tonic (read after superclass initialization to compose the name)
    Attributes WRITTEN:
        - self.tonic (written/established by the superclass __init__)
        - self.octaves (written/established by the superclass __init__)
        - self.name (assigned in this method to the string "{tonic} harmonic major")

## Constraints:
    Preconditions:
        - The caller should pass a note string matching the project's pitch-class/key format expectations (uppercase letter A–G optionally followed by '#' or 'b' where applicable). Passing a fully-lowercase note will cause the base-class initializer to raise NoteFormatError.
        - octaves should be an integer >= 0 for predictable behavior of repeating scale-degree lists; the constructor does not enforce this but downstream methods assume integer repetition semantics.
    Postconditions:
        - After successful completion:
            * self.tonic is set to the value established by the superclass (typically equal to the constructor-supplied note, subject to base-class normalization).
            * self.octaves is set to the provided octaves value.
            * self.name equals the string produced by "{0} harmonic major".format(self.tonic).
        - No other instance attributes are mutated by this method.

## Side Effects:
    - No I/O is performed.
    - No external services are called.
    - Only the instance itself is mutated (via attributes written as described). Any exceptions from the superclass or from the formatting operation will propagate to the caller.

### `mingus.core.scales.HarmonicMajor.ascending` · *method*

## Summary:
Return the harmonic-major scale pitch-classes ascending from the instance tonic across the configured number of octaves, lowering the natural sixth degree by one semitone in every octave; does not modify the object.

## Description:
Known callers and context:
- Called by any consumer that needs the ordered pitch-classes of a HarmonicMajor scale for rendering, analysis, transposition, exercise generation, or exporting (typical call sites include notation/rendering code, scale utilities, and unit tests). 
- Lifecycle stage: invoked after constructing a HarmonicMajor instance (for example, HarmonicMajor("C", octaves=1).ascending()) when the caller requires the explicit list of scale degrees.
- The method is intended as the public accessor that returns the scale degrees in ascending order (closed by the tonic above the final octave).

Rationale for being a separate method:
- HarmonicMajor differs from a plain major scale only by lowering the sixth degree by one semitone. Implementing this transformation in ascending() keeps the specialization local to the HarmonicMajor class and avoids duplicating Major's generation logic. It delegates base-step generation to Major(self.tonic).ascending() and then applies the single, well-defined alteration (diminish the sixth), preserving separation of concerns and reusing key-signature/tonic normalization.

## Args:
None.

## Returns:
list[str]: A new list of pitch-class strings (e.g., "C", "G#", "Bb") representing the ascending harmonic-major scale across self.octaves octaves, followed by the tonic to close the final octave.
- Length and structure:
    - Let notes_base be the 7 distinct diatonic pitch-classes for the tonic (Major(self.tonic).ascending()[:-1]).
    - The return value equals notes_base repeated self.octaves times, plus [notes_base[0]] appended.
    - Therefore length == 7 * self.octaves + 1.
- Example (octaves=1): For tonic "C", returns ["C", "D", "E", "F", "G", "Ab", "B", "C"] (sixth degree "A" lowered to "Ab").
- Edge cases:
    - If self.octaves == 0, the repetition yields [] and the method returns [notes_base[0]] (a single tonic).
    - The elements are strings produced by Major/get_notes and then transformed by diminish; callers should expect canonical pitch-class names, not Note objects.

## Raises:
- mingus.core.mt_exceptions.NoteFormatError
    - Trigger: propagated from Major(self.tonic) or get_notes if self.tonic is not a recognized/valid key string (for example, when the tonic was constructed/validated and rejected).
- TypeError
    - Trigger: if self.octaves is not an integer (list repetition notes * self.octaves will raise TypeError).
- IndexError or TypeError
    - Trigger: theoretically possible if diminish receives an unexpected empty or non-indexable string; in practice Major/get_notes returns non-empty canonical note strings so this is unlikely, but these exceptions can propagate from the underlying diminish implementation if its preconditions are violated.

## State Changes:
Attributes READ:
- self.tonic (used to construct Major(self.tonic))
- self.octaves (used to repeat the base 7-note pattern)

Attributes WRITTEN:
- None. The method does not mutate the instance; it returns a newly created list.

## Constraints:
Preconditions:
- self.tonic must be a valid tonic string accepted by Major/get_notes (e.g., "C", "G#", "Bb"); otherwise Major or get_notes will raise NoteFormatError.
- self.octaves should be a non-negative integer. Non-integer or negative values will produce runtime errors or nonsensical results (TypeError for non-int; negative ints will produce a valid but unexpected list due to Python repetition semantics; callers should ensure octaves >= 0).
- The environment must provide the diminish(note: str) utility and Major class as expected.

Postconditions:
- The returned list:
    - Contains only strings (pitch-class names).
    - Has the sixth scale degree of the diatonic major pattern lowered by one semitone (implemented by diminish on the sixth element index 5 of the 7-note base).
    - Repeats that modified 7-note pattern self.octaves times and ends with the tonic once.
- No attributes on self are modified.

## Side Effects:
- None observable: no I/O, no external service calls, and no mutation of objects outside the method's local scope. The only mutation is to a local list object (notes) before it is used to build and return the result; self is unchanged.

## `mingus.core.scales.NaturalMinor` · *class*

## Summary:
Represents a natural minor scale anchored at a given tonic and spanning a configurable number of octaves. Provides an ascending() accessor that returns the scale degrees as a list of note name strings with a duplicated top-of-scale tonic.

## Description:
NaturalMinor is a concrete _Scale subclass modeling a "natural minor" scale instance (its type attribute is "minor"). It is instantiated by client code or factory code that needs a programmatic representation of a minor scale for lookups, rendering, or interval/degree calculations.

Typical instantiation scenarios
- A user-facing API that constructs a scale object from user input (e.g., "A" or "E#") to query its degrees or to render notation.
- Programmatic code that needs a uniform Scale interface (supported by _Scale) and specifically requires the natural minor naming/semantics.

Why this class exists
- Provides a compact implementation of a natural minor scale object that integrates with the _Scale interface (degree lookup, descending(), __len__, comparisons) while providing its own ascending() sequence.
- Responsibility boundary: produce the ordered ascending note-list for a natural minor scale (as implemented here) and expose the _Scale contract (tonic, octaves, name, ascending(), descending(), degree(), etc.). It does not manage I/O, caching, or external resource lifetimes.

Design notes
- ascending() relies on the library's get_notes() helper to obtain a canonical list of seven diatonic note names for the key derived from the tonic. The method repeats that 7-note pattern octaves times and appends the tonic note (the top-octave duplicate) as required by the _Scale contract.
- The class sets a readable name ("<tonic> natural minor") so that the inherited __repr__ is meaningful.

## State:
- type (class attribute)
    - Type: str
    - Value: the literal "minor"
    - Invariant: constant for the class; used to identify scale quality.

- tonic (inherited, str)
    - Description: the root note name provided to __init__ (e.g., "A", "C#", "Bb").
    - Source: provided by caller as the first __init__ argument and validated/normalized by _Scale.__init__.
    - Constraints: _Scale.__init__ enforces that tonic is not fully lowercase (if note.islower() is True it raises NoteFormatError). NaturalMinor does not further validate tonic.
    - Invariant: remains equal to the constructor-supplied value unless mutated externally.

- octaves (inherited, typically int)
    - Description: how many octaves the scale should span when producing ascending() (interpreted as the number of 7-note groups to repeat).
    - Default: 1 (as provided by NaturalMinor.__init__ default parameter)
    - Constraints and behavior:
        * Expected to be an integer. ascending() uses sequence repetition (list * octaves); if octaves is non-integer the multiplication may raise TypeError.
        * Values:
            - octaves >= 1 (typical and intended): yields 7 * octaves + 1 notes returned by ascending().
            - octaves == 0 or octaves < 0: Python list repetition semantics apply (list * 0 or list * negative yields the empty list), so ascending() will still append the final tonic duplicate and return a single-element list [top_tonic]; this class does not enforce a positive lower bound.
        * The class does not validate octaves; callers should pass a sensible integer >= 1 for expected musical behavior.

- name (inherited/assigned, str)
    - Description: human-readable name assigned in __init__: "<tonic> natural minor" (tonic formatted as stored in self.tonic).
    - Invariant: assigned during construction; expected to remain unchanged.

Class invariants
- ascending() must return a list-like sequence of note strings ordered tonic-upward and include the top-of-scale tonic duplicate as the final element (this class implements that convention).
- The instance does not allocate external resources and has no cleanup obligations.

## Lifecycle:
Creation
- How to instantiate: call NaturalMinor(note, octaves=1)
    - note (str): tonic/root note string. Must not be fully lowercase (otherwise base _Scale.__init__ raises NoteFormatError).
    - octaves (int, optional): number of octaves to span; default is 1.
- No factory methods are required; standard direct instantiation is used.

Usage
- Typical sequence:
    1. Instantiate: create the NaturalMinor object with a valid tonic and an octaves value.
    2. Query ascending degrees: call ascending() to get the upward-ordered list (the returned list includes the top duplicate tonic).
    3. Use inherited helpers: call descending(), degree(n), len(), compare equality with other scales, or use __repr__ for display.
- Order constraints:
    - No special ordering of method calls is required by this class beyond constructing the object before calling its accessors.
    - ascending() is a pure accessor and does not mutate instance state.

Destruction / cleanup
- No cleanup or context-manager protocol is required. Instances rely entirely on Python garbage collection.

## Method Map:
flowchart TD
    ctor[__init__(note, octaves=1)]
    ctor --> set_name[sets self.name = "<tonic> natural minor"]
    ascending --> call_get_notes[get_notes(self.tonic.lower())]
    call_get_notes --> notes_list[7-note list returned by get_notes]
    notes_list --> repeat[notes_list * self.octaves]
    repeat --> append_top[append notes_list[0]]
    append_top --> returned_list[return repeated list + [top tonic]]
    ctor --> ascending
    classAttr[type="minor"]

(Interpretation: __init__ sets up tonic/octaves/name. ascending() calls get_notes(tonic.lower()), repeats the 7-note list octaves times, appends the original tonic note (first element of the 7-note list), and returns the assembled list.)

## Raises:
- NoteFormatError
    - Trigger(s):
        * If the caller supplies a tonic string that _Scale.__init__ deems invalid because it is fully lowercase (note.islower() is True), the base constructor will raise NoteFormatError.
        * get_notes() may also raise NoteFormatError if it determines the passed key string is not a recognized key format; ascending() passes self.tonic.lower() to get_notes(), so get_notes's validation rules apply.
- TypeError
    - Trigger: if octaves is not an integer (or not a type supported by list repetition), performing notes * self.octaves may raise TypeError.
- Other exceptions propagated from get_notes()
    - get_notes may raise other exceptions described in its documentation (e.g., ValueError, IndexError, TypeError) if module-level data or inputs are inconsistent; ascending() does not catch these exceptions.
- Notes about RangeError / FormatError:
    - NaturalMinor itself does not explicitly raise RangeError or FormatError. Those may be raised by other _Scale methods (e.g., degree()) when used; documenters should consult _Scale for those behaviors.

## Example:
- Creation:
    - Provide a tonic string that is not fully lowercase (for example, "A" or "F#"). Choose octaves as an integer (1 is the default).
    - A successful instantiation sets self.tonic, self.octaves and self.name ("<tonic> natural minor").

- Typical usage scenario (described):
    1. Instantiate a NaturalMinor with tonic "A" and octaves 1. The object will have name "A natural minor".
    2. Call ascending(). The method calls get_notes("a") to obtain the library's canonical 7-note list for the key derived from the tonic, repeats that list self.octaves times (here once), and appends the first element of the 7-note list as the top tonic duplicate. The returned value is a list-like sequence of note-name strings suitable for degree lookup or rendering.
    3. Use inherited helpers: calling descending() will return the reversed ascending() list; calling degree(1) returns the tonic; degree(n) returns the nth scale degree (1-based) based on the ascending ordering.

Developer notes
- Because ascending() forwards a lowercased tonic to get_notes(), be aware of how get_notes validates key strings: if your tonic contains accidentals or nonstandard case, ensure get_notes accepts it. If you need stricter octaves validation (e.g., require octaves >= 1 and integer), perform that check before instantiation or subclass/override __init__ to enforce it.
- NaturalMinor follows the _Scale contract: ascending() returns a list that includes the top tonic duplicate, enabling correct behavior for degree() and __len__().

### `mingus.core.scales.NaturalMinor.__init__` · *method*

## Summary:
Initializes a NaturalMinor scale instance by delegating core initialization to the superclass and then setting a human-readable name "<tonic> natural minor" on the instance.

## Description:
Called during object construction (e.g., NaturalMinor("A", 1)). The method:
- Calls the superclass constructor with the provided note and octaves to perform core initialization and validation.
- Uses the instance tonic established by that initialization to build and assign a readable name.

Known callers and invocation contexts:
- Client code or factory functions that create a NaturalMinor object from user input or program logic.
- Lifecycle stage: executed at instantiation time as part of the normal Python __init__ lifecycle.

Why this logic is in __init__:
- The readable name depends on the canonical tonic value established by the superclass constructor; therefore setting the name must occur after delegating core initialization to super.

## Args:
    note (str): Tonic/root note string (for example, "A", "C#", "Bb"). Forwarded to the superclass constructor which performs format validation.
    octaves (int, optional): Number of octaves the scale should span for accessors like ascending(). Default is 1. The constructor forwards this value to the superclass; it does not coerce or strictly validate the type/value.

## Returns:
    None. The constructor initializes the object in place; on successful return the instance has been initialized and named.

## Raises:
    Any exception raised by the superclass constructor will propagate. In practice callers can expect:
    - NoteFormatError: if the provided note fails the superclass validation (for example, an all-lowercase note string).
    - FormatError, RangeError, TypeError, ValueError, or other exceptions produced by superclass validation/initialization, depending on input.

## State Changes:
Attributes READ:
    self.tonic - read after superclass initialization in order to format the readable name

Attributes WRITTEN:
    self.name - assigned the string "<tonic> natural minor" by this method
    self.tonic, self.octaves - initialized/written by the superclass constructor invoked here (the subclass delegates core attribute setup to super)

## Constraints:
Preconditions:
    - The note argument must be acceptable to the superclass constructor (format and allowed values).
    - octaves should be an integer for expected behavior elsewhere; this constructor does not enforce that.

Postconditions:
    - The instance has been initialized by the superclass and now has self.name set to "<tonic> natural minor".
    - The object is ready for use with other Scale methods (ascending(), descending(), degree(), etc.) unless initialization failed and an exception was raised.

## Side Effects:
    - No I/O or external service calls.
    - No mutations outside the instance; only instance attributes are set.
    - Exceptions raised during superclass initialization propagate to the caller.

### `mingus.core.scales.NaturalMinor.ascending` · *method*

## Summary:
Return the ascending sequence of pitch-class names for this natural minor scale across the configured number of octaves, starting at the tonic and terminating at the tonic one octave above the final repeated octave.

## Description:
- Known callers and context:
    - No internal callers are required by the class definition itself; this method is intended to be called by client code or higher-level utilities that need the ordered, displayable list of note names for a NaturalMinor scale (examples: rendering/notation modules, CLI/GUI scale display, MIDI/event generators, transposition helpers).
    - Typical lifecycle step: invoked when a caller requests the scale's ascending note sequence for playback, display, analysis, or serialization.

- Why this is a separate method:
    - Different scale types (major, natural minor, harmonic minor, melodic minor, modes, etc.) have distinct rules for constructing their ascending sequences. Encapsulating the logic in a per-scale ascending() method keeps implementations independent, enables overriding by subclasses, and provides a consistent public API (instance.ascending()) for consumers.

## Args:
- None (method takes only self).
- Implicit inputs read from self:
    - self.tonic (str): The scale's tonic/key name (e.g., "A", "C#", "Bb"). This implementation passes self.tonic.lower() into get_notes.
    - self.octaves (int): The number of octaves to span when repeating the seven-note pattern. Expected to be an integer (typical default is 1).

## Returns:
- list[str]: A list of pitch-class name strings (no octave numbers), in ascending order.
    - Each element format: uppercase letter A..G optionally followed by a single accidental symbol '#' or 'b' (as produced by get_notes).
    - Length: Exactly 7 * self.octaves + 1 elements in normal operation (seven notes per octave repeated self.octaves times, plus the tonic again to close the final octave).
    - Example (typical):
        - For tonic "A" with octaves=1, get_notes("a") might return ["A", "B", "C#", "D", "E", "F#", "G#"]; ascending() returns ["A", "B", "C#", "D", "E", "F#", "G#", "A"].
    - Edge-case returns:
        - If self.octaves is 0 or a negative integer, Python list repetition yields an empty list for notes * self.octaves, so the method returns a single-element list [notes[0]] (the tonic).
        - If self.octaves is not an integer (e.g., float or other non-int), Python will raise a TypeError when attempting list * self.octaves.

## Raises:
- mingus.core.mt_exceptions.NoteFormatError:
    - Propagated from get_notes(self.tonic.lower()) when the tonic string (after lowercasing) is not a recognized key format.
    - Message originates from get_notes and typically is "unrecognized format for key '%s'" % key.
- TypeError:
    - May be raised if self.octaves is not an integer (attempting to multiply a list by a non-int).
    - May also propagate from get_notes if internal helpers receive incompatible types.
- IndexError, ValueError, or other runtime exceptions:
    - These may propagate from get_notes (e.g., if module-level data is inconsistent). They are not raised directly by ascending(), but callers should be prepared to handle them.

## State Changes:
- Attributes READ:
    - self.tonic
    - self.octaves
- Attributes WRITTEN:
    - None — this method does not modify any attributes of self.

## Constraints:
- Preconditions:
    - self.tonic must be a string acceptable to get_notes when lowercased (i.e., a recognized key/tonic name). If it is not, get_notes will raise NoteFormatError.
    - self.octaves should be an integer. Non-integer values will cause a TypeError on list repetition.
    - Module-level prerequisites of get_notes (base_scale, key signature helpers, and cache) must be initialized and valid.
- Postconditions:
    - On successful return, the returned list contains the diatonic notes repeated by octave and ends with the tonic note one step above the last repeated octave.
    - self is unchanged (no attribute mutations).

## Side Effects:
- None external: the method performs no I/O, network access, or mutation beyond what get_notes may do internally (get_notes may mutate its module-level _key_cache).
- The only observable effect is returning the new list (and potential side effects of get_notes such as populating the get_notes cache).

## `mingus.core.scales.HarmonicMinor` · *class*

## Summary:
Represents a harmonic minor scale anchored at a given tonic and spanning a configurable number of octaves. Provides an ascending() accessor that returns the scale degrees (with the raised 7th) as a list of note-name strings including the top-of-scale tonic duplicate.

## Description:
HarmonicMinor is a concrete _Scale subclass modeling the harmonic minor scale. It exists so callers can request the harmonic-minor note sequence and use _Scale's uniform interface (degree lookup, descending(), __len__, comparisons, and human-readable name).

Typical instantiation scenarios
- When client code needs a scale object that represents a harmonic minor scale for a specific tonic (e.g., for rendering, interval calculations, or degree lookup).
- When a factory or higher-level API exposes multiple scale types and constructs a HarmonicMinor when the harmonic-minor quality is requested.

Design and implementation notes (why this class is distinct)
- HarmonicMinor derives a single-octave diatonic pattern from NaturalMinor(self.tonic) (NaturalMinor is constructed with its default octaves=1). It removes NaturalMinor's final duplicated tonic, raises the 7th degree by applying the augment utility, then repeats that modified 7-note pattern self.octaves times and appends the tonic as the top-of-scale duplicate.
- This approach isolates the harmonic-minor-specific alteration (raise the seventh degree) while reusing NaturalMinor's canonical note-order generation for the other degrees.
- Responsibility boundary: produce the ascending() harmonic-minor sequence and set a human-readable self.name; do not perform I/O or manage resources.

## State:
- type (class attribute)
    - Type: str
    - Value: the literal "minor"
    - Purpose: indicates scale quality (aligns with other minor-mode scale classes).

- tonic (inherited from _Scale)
    - Type: str
    - Description: the root note name used to derive the scale (e.g., "A", "C#", "Bb").
    - Constraints: _Scale.__init__ rejects tonic strings that are fully lowercase (note.islower() == True) by raising NoteFormatError.
    - Invariant: remains equal to constructor-supplied value unless mutated externally.

- octaves (inherited from _Scale; constructor parameter)
    - Type: typically int
    - Default (constructor): 1
    - Description: how many octaves the returned ascending() sequence should span. HarmonicMinor repeats a single-octave 7-note pattern this many times and then appends the top tonic.
    - Constraints & behavior:
        - Expected to be an integer >= 1 for typical musical behavior.
        - If octaves == 0 or negative, Python list-repetition semantics apply (list * 0 yields empty list), and the method still appends the top tonic, returning a single-element list [tonic_of_single_pattern]. The class does not enforce a positive bound.
        - If octaves is not an integer or a type unsupported by list repetition, multiplying the pattern list by octaves will raise TypeError.

- name (assigned in __init__)
    - Type: str
    - Value: "<tonic> harmonic minor" (tonic formatted as stored in self.tonic)
    - Purpose: Human-readable representation used by __repr__ and logging. Set at construction.

Class invariants
- ascending() must return a list-like sequence of note strings ordered tonic-upward and must include the top-of-scale tonic duplicate as the final element (this class implements that convention).
- The instance does not allocate external resources and has no special cleanup obligations.

## Lifecycle:
Creation
- How to instantiate: call HarmonicMinor(note, octaves=1).
    - note (str): required tonic note string. Must not be fully lowercase (otherwise _Scale.__init__ raises NoteFormatError).
    - octaves (int, optional): default 1. Should be an integer for predictable behavior.

Initialization side effects
- Calls the base-class constructor to set tonic and octaves; the base constructor may raise NoteFormatError on invalid note formatting.
- Assigns self.name = "<tonic> harmonic minor".

Usage
- Typical method sequence:
    1. Instantiate the HarmonicMinor with a valid tonic (and optional octaves).
    2. Call ascending() to obtain the harmonic-minor sequence. The method:
        - Builds a single-octave natural-minor pattern by calling NaturalMinor(self.tonic).ascending() (NaturalMinor uses its default octaves=1).
        - Strips NaturalMinor's final duplicate tonic (slice [:-1]) to get a 7-note single-octave pattern.
        - Raises the 7th degree of that single-octave pattern by assigning notes[6] = augment(notes[6]).
        - Repeats the modified 7-note pattern self.octaves times and appends the first element (the tonic) as the top duplicate, returning that list.
    3. Optionally call descending(), degree(n), len(), compare equality with other scale objects, or use __repr__.
- Required sequencing: None beyond constructing the instance before calling accessors.

Destruction
- No cleanup or context-manager protocol required.

## Method Map:
graph TD
    ctor[HarmonicMinor.__init__(note, octaves=1)] --> set_name[sets self.name = "<tonic> harmonic minor"]
    ascending --> make_single_octave[call NaturalMinor(self.tonic).ascending()]
    make_single_octave --> strip_top[strip final duplicate via [:-1]]
    strip_top --> raise_7th[notes[6] = augment(notes[6])]
    raise_7th --> repeat_pattern[return notes * self.octaves + [notes[0]]]
    ctor --> ascending

(Interpretation: ascending() depends on NaturalMinor.ascending() and augment(); it yields a repeated, modified 7-note pattern plus the top tonic duplicate.)

## Raises:
- NoteFormatError
    - Trigger(s):
        * If the supplied note is fully lowercase, _Scale.__init__ raises NoteFormatError on construction.
        * NaturalMinor(self.tonic) or its ascending() may call get_notes(self.tonic.lower()) and propagate NoteFormatError if the key string is not recognized.
- TypeError
    - Trigger: if self.octaves is not a type supported by list repetition (e.g., a float or None), the expression notes * self.octaves will raise TypeError.
- IndexError
    - Trigger(s):
        * If NaturalMinor(self.tonic).ascending() returns a sequence shorter than expected (fewer than 7 elements after slicing [:-1]), accessing notes[6] will raise IndexError. This is not expected for correct get_notes() behavior but is a possible propagation.
        * augment(notes[6]) may raise IndexError if notes[6] is an empty string (augment accesses the final character).
- Any exceptions raised by NaturalMinor.ascending() or get_notes() (propagated). HarmonicMinor does not catch these exceptions itself.

## Example:
- Creation and typical usage (described):
    1. Construct a HarmonicMinor with tonic "A" and default octaves (1). The instance has name "A harmonic minor".
    2. Call ascending(). Internally this:
        - Obtains NaturalMinor("A").ascending() (a single-octave 8-note list including the top tonic duplicate).
        - Removes the final duplicated tonic to get the 7-note pattern.
        - Raises the 7th degree by applying augment to the 7th element of that pattern.
        - Repeats the modified 7-note pattern self.octaves times (1 time here) and appends the tonic as the top duplicate.
    3. The resulting list is the harmonic-minor ascending sequence (tonic up to the raised 7th, ending with the tonic at the top octave), suitable for degree lookups and rendering.

Developer notes and tips
- HarmonicMinor intentionally reuses NaturalMinor to derive the unaltered six degrees and only modifies the seventh degree. This minimizes duplication and keeps consistency with NaturalMinor's canonical note naming.
- Validate octaves when constructing instances if you need to guarantee musical semantics (e.g., ensure octaves is an integer >= 1) to avoid TypeError or unexpected repetitive behavior.
- Because augment manipulates the textual accidental (removes trailing 'b' or appends '#'), the raised seventh may result in double-sharps or other textual accidentals depending on the NaturalMinor output; callers that expect normalized accidentals should run reduce_accidentals or other normalizers if available.

### `mingus.core.scales.HarmonicMinor.__init__` · *method*

## Summary:
Initializes a HarmonicMinor scale instance by delegating core initialization to the base scale class and setting a human-readable name that reflects the tonic and harmonic-minor quality.

## Description:
- Known callers / contexts:
    - Typical callers are client code or factory APIs that construct scale objects when a harmonic-minor quality is requested (e.g., HarmonicMinor("A"), or factory.build_scale("A", quality="harmonic_minor")).
    - It is invoked during object creation as part of normal lifecycle initialization; callers obtain a ready-to-use scale object after construction and then call accessors such as ascending(), descending(), or degree().
- Lifecycle stage:
    - This method runs at construction time (in __init__) and prepares the instance state required by all other instance methods.
- Why this is a separate method:
    - The method preserves single-responsibility: core validation/assignment of tonic and octaves is performed by the superclass constructor, while this subclass initializer performs only the harmonic-minor-specific naming. Keeping the naming logic here avoids duplicating base-class initialization and isolates the human-readable labeling of the specific scale quality.

## Args:
    note (str):
        - The tonic (root) note name used to derive the scale (examples: "A", "C#", "Bb").
        - Must be a valid note/key string accepted by the base class; the base class enforces formatting rules (e.g., a fully-lowercase note string is rejected).
    octaves (int, optional):
        - Number of octaves the scale should conceptually span; default is 1.
        - Expected to be an integer (typically >= 1 for musical semantics). The constructor stores the value but does not enforce a strictly positive bound; downstream methods that rely on list repetition (e.g., ascending()) may raise TypeError if octaves is not an integer.

## Returns:
    None
    - As a constructor initializer, the method returns None (the created instance is returned to the caller by Python's construction semantics).

## Raises:
    - NoteFormatError:
        - Raised by the superclass constructor if the provided note string violates expected formatting rules (for example, if it is fully lowercase or otherwise unrecognized by the key/note parsing logic).
    - Any exception propagated from the superclass constructor:
        - Since this __init__ directly calls super().__init__(note, octaves), any exceptions that occur during base-class validation or assignment (e.g., FormatError, RangeError if the base class enforces them) will propagate out of this method.
    - This initializer itself does not introduce new exception types beyond those raised or propagated by the superclass.

## State Changes:
- Attributes READ:
    - self.tonic — read implicitly when constructing the name string; the value is set by the called superclass initializer before it is read.
- Attributes WRITTEN:
    - self.tonic — set by the superclass constructor as part of super().__init__(note, octaves).
    - self.octaves — set by the superclass constructor as part of super().__init__(note, octaves).
    - self.name — explicitly assigned here to the string "<tonic> harmonic minor" (using the value of self.tonic produced by the superclass).
- Notes:
    - Any other attributes initialized by the superclass constructor (e.g., internal caches, normalized representations) are created/modified by that call but are not touched further by this subclass initializer.

## Constraints:
- Preconditions:
    - The provided note must be a valid tonic string for the codebase's key/note utilities (not fully lowercase and recognizable by get_notes/keys). If not, the superclass constructor will raise NoteFormatError.
    - octaves should be an integer for predictable behavior in other methods (the constructor does not coerce or validate type beyond what the superclass does).
- Postconditions:
    - After the call completes successfully:
        - self.tonic will contain the normalized tonic value established by the superclass constructor.
        - self.octaves will contain the stored octaves value established by the superclass constructor.
        - self.name will equal "<tonic> harmonic minor" (where <tonic> is the value of self.tonic).
    - The instance is ready for use by other methods (ascending(), descending(), degree(), etc.), subject to the invariants and constraints documented by the base class and the HarmonicMinor class.

## Side Effects:
- No I/O or external service calls are performed.
- The only observable side effects are in-memory mutations of the instance attributes (tonic, octaves via the superclass, and name).
- No global state is modified.

### `mingus.core.scales.HarmonicMinor.ascending` · *method*

## Summary:
Constructs and returns the ascending note sequence for the harmonic minor scale built on this instance's tonic, raising the seventh degree relative to the natural minor; does not modify the instance state.

## Description:
- Known callers and context:
    - Client code that needs the ordered pitch-class names of a harmonic minor scale for display, playback, analysis, or serialization (examples: rendering/notation modules, CLI/GUI scale display, MIDI/event generators, transposition helpers).
    - Typical lifecycle stage: invoked when a consumer requests the scale degrees (e.g., scale.ascending()) during UI rendering or music-processing pipelines.
- Why this is a separate method:
    - Harmonic minor differs from natural minor only by a raised seventh degree. Encapsulating the logic here allows HarmonicMinor to reuse NaturalMinor's construction for the diatonic degrees and apply the single alteration (augment the seventh) without duplicating the natural-minor assembly logic. This keeps per-scale rules isolated, readable, and easy to maintain.

## Args:
- None (method takes only self).
- Implicit inputs read from self:
    - self.tonic (str): the tonic/root note name used to derive the diatonic degrees.
    - self.octaves (int): how many octave groups to repeat when assembling the returned list.

## Returns:
- list[str]: An ascending list of pitch-class name strings (no octave suffixes), starting at the tonic and ending with the tonic one octave above the top repeated octave.
    - Normal length: 7 * self.octaves + 1 elements (seven diatonic notes per octave repeated self.octaves times, plus the tonic duplicate).
    - Element format: strings as produced by get_notes() and augment(), typically letters A..G optionally followed by accidental characters (e.g., "C", "G#", "Bb").
    - Edge-case returns:
        - If self.octaves <= 0 (e.g., 0 or a negative integer), Python list repetition semantics yield an empty repetition, and the method will return a single-element list containing the tonic [notes[0]].
        - If self.octaves is not an integer, a TypeError will be raised when attempting list repetition.

## Raises:
- mingus.core.mt_exceptions.NoteFormatError:
    - Condition: propagated from NaturalMinor(self.tonic).ascending() -> get_notes(self.tonic.lower()) when the tonic string (after lowercasing) is not recognized as a valid key/tonic name.
- TypeError:
    - Condition: if self.octaves is not an integer (attempting notes * self.octaves), or if augment() is called on an object that does not support the string operations it expects.
- IndexError:
    - Condition: if the sequence returned by NaturalMinor(...).ascending() is unexpectedly short so that indexing/index operations used here fail, or if augment() is called with an empty string (augment will access note[-1]).
- Any exceptions raised by NaturalMinor.ascending() or augment() (e.g., ValueError) are propagated unchanged; this method does not catch them.

## State Changes:
- Attributes READ:
    - self.tonic
    - self.octaves
- Attributes WRITTEN:
    - None — the method does not modify any attributes on self. It mutates only local variables.

## Constraints:
- Preconditions:
    - self.tonic must be a non-empty string acceptable to get_notes when lowercased; otherwise get_notes will raise NoteFormatError.
    - self.octaves should be an integer (typical expected value >= 1) to produce musically meaningful results; non-integer values will raise TypeError on list multiplication.
    - The code assumes NaturalMinor(self.tonic).ascending() returns at least seven diatonic notes plus the top tonic duplicate (the implementation uses slicing to obtain the seven base degrees). If NaturalMinor's contract is violated, IndexError may occur.
- Postconditions:
    - On successful return, the returned list contains the diatonic degrees for the harmonic minor scale with the seventh degree raised relative to the natural minor (index 6 of the base seven-note group), repeated for the configured number of octaves, and terminated by the tonic as the final element.
    - The HarmonicMinor instance (self) remains unchanged.

## Side Effects:
- No I/O or network activity.
- No mutations to objects outside the method scope (self is not modified). The method constructs and mutates a local list of note-name strings before returning a new list.
- Calls into NaturalMinor.ascending() and augment(); any side effects those functions have (e.g., populating a module-level cache in get_notes) may occur and are propagated.

## `mingus.core.scales.MelodicMinor` · *class*

## Summary:
A concrete _Scale subclass representing the melodic minor scale for a given tonic. It produces ascending and descending note sequences where the ascending form raises the 6th and 7th degrees while the descending form uses the natural minor pattern.

## Description:
MelodicMinor models the melodic minor scale as an object you can query for ordered pitch names, degree lookups, and comparisons using the _Scale interface. Use this class when you need programmatic access to a melodic-minor pitch collection (for rendering, analysis, or transformation).

Why this class exists and its responsibility boundary:
- Responsibility: compute and return correct melodic-minor note sequences (ascending and descending) across one or more octaves while exposing the standard _Scale helpers (degree(), descending(), __len__, __repr__, etc.).
- Not responsibility: perform low-level key-to-note mapping (delegated to NaturalMinor/get_notes) or to validate complex musical input beyond the very basic checks performed by _Scale.__init__.

Typical callers:
- User-facing APIs or utilities that need a scale object with melodic-minor semantics.
- Libraries or routines that work uniformly with any _Scale subclass and therefore rely on ascending()/descending() semantics.

## State:
Public attributes (set during or after construction):
- tonic (str)
    - Description: root note string supplied by the caller (examples: "A", "C#", "Bb").
    - Source: constructor parameter note; stored by _Scale.__init__.
    - Constraints: _Scale.__init__ rejects tonic strings that are fully lowercase (note.islower() is True) by raising NoteFormatError.
    - Invariant: remains equal to the constructor-supplied value unless mutated externally.

- octaves (int-like)
    - Description: how many octaves the ascending()/descending() sequences should span.
    - Default: 1 (from __init__ default).
    - Constraints:
        * Expected to be an integer for standard musical behavior.
        * If octaves is an integer n, the typical returned sequence length is 7 * n + 1 (seven scale degrees per octave repeated n times, plus the top tonic duplicate).
        * If octaves == 0 or a negative integer, Python list-repetition semantics produce an empty repetition of the 7-degree pattern; the implementation will still append the top tonic and return a single-element list [tonic] (length 1).
        * If octaves is non-integer (e.g., float, None, string), list repetition will usually raise TypeError.
    - Invariant: remains equal to the constructor-supplied value unless mutated externally.

- name (str)
    - Description: human-readable instance name.
    - Set in __init__: value is the string "<tonic> melodic minor" (tonic substituted from self.tonic).
    - Purpose: used by __repr__ and display routines.

- type (class attribute, str)
    - Value: "minor" (literal).
    - Purpose: identifies scale quality; read-only at class level.

Class invariants:
- ascending() must return a list-like sequence of note-name strings ordered tonic-upward and include the top-of-scale tonic duplicate as the final element (this class implements that convention).
- descending() must return a list-like sequence of the same length as ascending() representing the scale played downward (here, NaturalMinor's descending form is used).

## Lifecycle:
Creation:
- Constructor signature: __init__(self, note, octaves=1)
    - note (str): required. A tonic string. Must not be fully-lowercase (otherwise NoteFormatError is raised by _Scale.__init__).
    - octaves (optional, default 1): integer-like repetition count for octaves. Prefer a positive integer for expected musical output.
- What __init__ does:
    1. Calls super(MelodicMinor, self).__init__(note, octaves) to set tonic and octaves and perform base-class validation.
    2. Sets self.name = "{0} melodic minor".format(self.tonic).

Usage:
- No special ordering is required beyond constructing the instance before calling accessors.
- Typical usage:
    1. Instantiate MelodicMinor with a valid tonic and an octaves integer.
    2. Call ascending() to obtain the melodic-minor ascending list.
    3. Call descending() to obtain the melodic-minor descending list (natural-minor form).
    4. Use degree(n, direction) and other inherited helpers for targeted lookups.

Destruction:
- No cleanup is required. Instances are ordinary Python objects eligible for garbage collection.

## Method Map:
flowchart TD
    ctor[__init__(note, octaves=1)] --> set_name[set self.name = "<tonic> melodic minor"]
    set_name --> ready[instance ready]
    ready --> ascending[ascending()]
    ascending --> nm_asc_call[call NaturalMinor(self.tonic).ascending()]
    nm_asc_call --> strip_top1[notes = nm_asc[:-1]  # remove duplicate tonic]
    strip_top1 --> augment6[notes[5] = augment(notes[5])]
    augment6 --> augment7[notes[6] = augment(notes[6])]
    augment7 --> repeat_asc[notes * self.octaves]
    repeat_asc --> append_top_asc[+ [notes[0]]]
    append_top_asc --> return_asc[return result]
    ready --> descending[descending()]
    descending --> nm_desc_call[call NaturalMinor(self.tonic).descending()]
    nm_desc_call --> strip_top2[notes = nm_desc[:-1]]
    strip_top2 --> repeat_desc[notes * self.octaves]
    repeat_desc --> append_top_desc[+ [notes[0]]]
    append_top_desc --> return_desc[return result]

Notes on augment:
- augment(note) removes a trailing 'b' if present; otherwise appends a '#' to the string. This can produce single or double sharps or remove flats depending on the input.

## Behavior (precise algorithm and edge cases):
- ascending()
    - Algorithm (exact steps mirrored from the implementation):
        1. single_octave = NaturalMinor(self.tonic).ascending()  # expected length 8 (7 degrees + top tonic)
        2. notes = single_octave[:-1]  # take the 7-degree pattern (indices 0..6)
        3. notes[5] = augment(notes[5])  # raise the 6th degree
        4. notes[6] = augment(notes[6])  # raise the 7th degree
        5. result = notes * self.octaves + [notes[0]]  # repeat pattern, then append tonic
        6. return result
    - Return type: list[str]
    - Expected length for integer octaves n: 7 * n + 1
    - Edge cases and propagated errors:
        * If NaturalMinor(...).ascending() does not return at least 7 degrees before slicing, indexing notes[5] or notes[6] raises IndexError.
        * augment() performs string operations; if a degree string is empty or non-string, augment() may raise IndexError or TypeError.
        * If octaves is a non-integer type unsupported by list multiplication, a TypeError is raised when evaluating notes * self.octaves.
        * Any NoteFormatError or other exceptions raised by NaturalMinor/get_notes propagate unchanged.

- descending()
    - Algorithm (exact steps):
        1. single_desc = NaturalMinor(self.tonic).descending()  # expected 8 elements
        2. notes = single_desc[:-1]
        3. result = notes * self.octaves + [notes[0]]
        4. return result
    - Behavior: returns the natural-minor descending form repeated octaves times with the tonic appended (no augmentations applied).
    - Same edge cases for octaves repetition and underlying NaturalMinor/get_notes errors apply as for ascending().

## Raises:
- Exceptions raised directly by __init__:
    - NoteFormatError
        * Condition: _Scale.__init__ raises this when the provided note string is fully lowercase (note.islower() True) or when get_notes rejects the key during NaturalMinor usage called inside accessors.
- Exceptions that may be raised by ascending() or descending() (propagated from calls or produced by local operations):
    - IndexError
        * Conditions:
            - If NaturalMinor(...).ascending() or descending() returns a shorter-than-expected list so that notes[5] or notes[6] access fails.
            - If augment() is invoked on an empty string (augment inspects note[-1]).
    - TypeError
        * Conditions:
            - If octaves is not an integer-like value supported by Python list repetition (notes * self.octaves).
            - If note-name types passed to augment() are not strings.
    - Any other exceptions raised by NaturalMinor, get_notes, or augment propagate unchanged.

## Example (concise, descriptive):
- Typical creation and expected results (prose):
    - Instantiate: provide a tonic that is not fully-lowercase (for example, "A") and optionally octaves (default 1).
    - For MelodicMinor("A", octaves=1):
        * NaturalMinor("A").ascending() is expected to produce ["A","B","C","D","E","F","G","A"].
        * MelodicMinor.ascending() will take the seven-note pattern ["A","B","C","D","E","F","G"], apply augment to items at indexes 5 and 6 to produce ["A","B","C","D","E","F#","G#"], then append the tonic to produce ["A","B","C","D","E","F#","G#","A"].
        * MelodicMinor.descending() will mirror NaturalMinor.descending(), yielding the natural-minor descending sequence repeated per octaves and ending with the tonic.
- Defensive usage recommendations:
    - Pass a tonic accepted by get_notes and an integer octaves >= 1 for expected musical output.
    - If you expect to handle malformed inputs, validate note strings and octaves prior to constructing MelodicMinor to produce clearer error messages than raw IndexError/TypeError from internal operations.

### `mingus.core.scales.MelodicMinor.__init__` · *method*

## Summary:
Initializes the MelodicMinor scale instance by delegating core initialization to the _Scale superclass and setting a human-readable instance name of the form "<tonic> melodic minor". The call establishes the object's tonic and octaves (via the superclass) and records the display name.

## Description:
Known callers and context:
- Constructed by client code that needs a melodic-minor Scale object (user-facing utilities, renderers, analyzers, or any routine that uniformly instantiates _Scale subclasses).
- This constructor is invoked during the object-creation lifecycle (immediately when an instance is created). After __init__ returns the instance is ready for calls to ascending(), descending(), degree(), and other _Scale helpers.

Why this logic is a dedicated method:
- The method delegates shared validation and attribute initialization to the _Scale superclass (via super(...).__init__(note, octaves)) and performs the single subclass-specific action of setting a descriptive name. Keeping the subclass initialization separate maintains clear separation of concerns: base-class validation/assignment in _Scale, and subclass labeling/identity in MelodicMinor.

## Args:
    note (str):
        - The tonic/root note string for the scale (examples: "A", "C#", "Bb").
        - Must be in the format accepted by the base _Scale implementation (the base class will raise NoteFormatError for invalid formats such as fully-lowercase note names).
    octaves (int, optional):
        - Number of octaves the scale's accessors (ascending/descending) should span. Defaults to 1.
        - The constructor does not itself perform complex numeric validation; callers should pass an integer-like value for expected behavior. Non-integer values may cause errors later when scale sequences are generated.

## Returns:
    None
    - As a typical initializer, the method does not return a value. It returns None implicitly after having initialized the instance.

## Raises:
    NoteFormatError
        - Condition: raised by the superclass _Scale.__init__ if the provided note string fails the expected note format validation (for example, if the note string is fully lowercase and thus rejected by the base implementation).
    Any exception raised by _Scale.__init__
        - Condition: any validation or setup error that occurs inside the delegated superclass initialization is propagated unchanged (this can include other format or range-related exceptions thrown by the base class).

## State Changes:
Attributes READ:
    - self.tonic
        - Read in order to format the display name string after the superclass has established the tonic attribute.

Attributes WRITTEN:
    - self.name
        - Written by this method to the string "{0} melodic minor".format(self.tonic).
Attributes set indirectly (by the superclass call):
    - self.tonic
        - Established/validated by _Scale.__init__(note, octaves).
    - self.octaves
        - Established/validated by _Scale.__init__(note, octaves).

## Constraints:
Preconditions:
    - The caller must supply a note string accepted by _Scale.__init__ (avoid fully-lowercase note names and other formats the base class rejects).
    - Prefer passing an integer for octaves. The method does not coerce or deeply validate octaves itself.

Postconditions:
    - After return:
        * self.tonic holds the validated tonic value (as set by the superclass).
        * self.octaves holds the provided octaves value (as set by the superclass).
        * self.name equals the string "<tonic> melodic minor" where <tonic> is the post-validation tonic value stored on the instance.
    - The instance is ready for use with ascending(), descending(), degree(), and other inherited helpers.

## Side Effects:
    - Mutates the instance by setting self.name and (via superclass) self.tonic and self.octaves.
    - No I/O is performed; no external services are contacted; no global state is modified.

### `mingus.core.scales.MelodicMinor.ascending` · *method*

## Summary:
Return the ascending note-name sequence for this melodic minor scale (ascending form), producing the scale degrees with the 6th and 7th degrees raised and spanning the instance's configured number of octaves.

## Description:
Known callers:
- No specific internal callers are recorded in the repository memory. Typical callers are higher-level APIs or user code that request scale degrees for display, analysis, or melodic generation (for example: UI renderers, MIDI/notation exporters, or any code calling the generic _Scale.ascending() on a MelodicMinor instance).
- The method is invoked at the stage where a consumer needs the ordered ascending scale degrees (the "ascending" lifecycle stage of a scale object). It is an accessor that produces the textual note names composing the melodic minor scale ascending form.

Why this is a separate method:
- The melodic minor scale differs from the natural minor only by a raised 6th and 7th degree when ascending. Encapsulating this behavior in its own method keeps the melodic-specific alteration local and readable (create a natural-minor baseline, then apply the two augmentations). It avoids duplicating diatonic-generation logic and centralizes the melodic modification, making maintenance and musical intent explicit.

## Args:
    None.

## Returns:
    list[str]: A list of note-name strings representing the ascending melodic minor scale across the instance's octaves, with the top-of-scale tonic duplicated as the final element.
    - Typical length: 7 * self.octaves + 1 when preconditions hold (see Constraints).
        * Example, with self.octaves == 1: returns 8 notes (seven scale degrees with the final tonic duplicate).
    - The 6th and 7th scale degrees (indexes 5 and 6 within each 7-note group) will be adjusted by the augment utility:
        * If a degree's name ends with lowercase 'b' it will be shortened by removing that 'b' (e.g., 'Bb' -> 'B').
        * Otherwise a '#' is appended (e.g., 'F' -> 'F#', 'C#' -> 'C##').
    - The returned list is newly constructed; no internal list objects from the instance are exposed directly.

## Raises:
    NoteFormatError:
        - Condition: If NaturalMinor(self.tonic) construction or NaturalMinor.ascending() propagates a NoteFormatError (for example, if self.tonic is not a recognized key format).
    IndexError:
        - Condition A: If NaturalMinor(self.tonic).ascending() returns a shorter sequence than expected (the method relies on the one-octave NaturalMinor ascending list to have 8 elements before slicing), then indexing notes[5] or notes[6] may raise IndexError.
        - Condition B: If augment() is called with an empty string (which would occur only if NaturalMinor returned an empty note name), augment will raise IndexError when accessing note[-1].
    TypeError:
        - Condition: If self.octaves is not an integer (or not a type supported by Python list repetition), notes * self.octaves may raise TypeError.
    Any other exception raised by NaturalMinor.ascending(), get_notes(), or augment() will propagate unchanged.

## State Changes:
Attributes READ:
    - self.tonic (str): used to construct a NaturalMinor instance representing the diatonic names for the tonic.
    - self.octaves (int-like): used to determine how many times to repeat the 7-note pattern.

Attributes WRITTEN:
    - None. This method does not mutate self; it only builds and returns a new list.

## Constraints:
Preconditions:
    - self.tonic must be a valid tonic acceptable to NaturalMinor and get_notes() (NaturalMinor.__init__ / get_notes() may validate and raise NoteFormatError).
    - self.octaves should be an integer (typical, positive). If not an integer, list repetition semantics apply but may raise TypeError or produce unexpected results.
    - NaturalMinor(self.tonic).ascending() is expected to return the conventional single-octave ascending sequence (7 degrees plus a duplicate tonic, i.e., 8 elements) so that slicing [:-1] yields a 7-element base scale. The method relies on indexes 5 and 6 being valid in that 7-element list.

Postconditions:
    - Returns a list of note strings representing the ascending melodic minor scale where the 6th and 7th degrees are augmented (raised).
    - The returned list length equals 7 * self.octaves + 1 when the preconditions are satisfied.
    - self remains unchanged.

## Side Effects:
    - No I/O, no external services, and no mutation of objects outside the method scope.
    - Uses the pure string-transform utility augment() which returns new string values; augment does not mutate external state.
    - All side effects are limited to constructing and returning the resulting list.

## Implementation notes and examples:
Implementation approach (reconstructable description):
    1. Build a NaturalMinor scale for the same tonic with a single octave: call NaturalMinor(self.tonic).ascending(). That call is expected to return 8 items (7 scale degrees plus a final tonic duplicate).
    2. Drop the final duplicate tonic (slice [:-1]) to obtain exactly the 7 distinct diatonic degree names for one octave.
    3. Raise (augment) the 6th and 7th degrees by calling augment() on notes[5] and notes[6], respectively, and storing the results back into those positions.
    4. Repeat the resulting 7-note list self.octaves times (list multiplication) and append the first element (the tonic) as the final duplicate: return notes * self.octaves + [notes[0]].

Examples:
    - If self.tonic == "A" and self.octaves == 1:
        NaturalMinor("A").ascending() -> ['A','B','C','D','E','F','G','A']
        after slicing -> ['A','B','C','D','E','F','G']
        augment notes[5] ('F') -> 'F#'
        augment notes[6] ('G') -> 'G#'
        return -> ['A','B','C','D','E','F#','G#','A']

    - If a diatonic degree were a flat name, e.g. 'Bb':
        augment('Bb') -> 'B' (removes trailing 'b'), so the raised degree may become a natural instead of using an explicit sharp.

Developer caution:
    - The use of augment to "raise" degrees is a string-level accidental adjustment (remove trailing 'b' or append '#'); it does not perform enharmonic normalization or apply musical-spelling conventions beyond that transformation. The resulting names reflect this simple rule.
    - If you need strict octave or octaves >= 1 enforcement, validate self.octaves before calling this method or in the constructor; the current implementation relies on Python list repetition semantics.

### `mingus.core.scales.MelodicMinor.descending` · *method*

## Summary:
Returns the melodic minor scale's descending sequence as a list of note-name strings, repeating the descending pattern for the instance's octaves and appending the top-of-scale tonic duplicate. This is a read-only accessor that does not modify the object.

## Description:
- Known callers and context:
    - Public API consumers that request the scale degrees in descending order (for rendering, analysis, or degree lookups) will call this method on a MelodicMinor instance.
    - Higher-level code that implements display, export, or music-theoretic calculations (e.g., printing a scale, computing intervals against scale degrees) will call this method when they need the downward-ordered notes.
    - Typical pipeline stage: called after instantiation of a MelodicMinor object as a pure accessor; used wherever a stable, non-mutating descending representation is needed.
- Why this is a separate method:
    - Melodic minor scales are defined with distinct ascending and descending forms. The descending form for melodic minor is identical to the natural minor form; implementing descending() as its own method allows the class to (1) reuse NaturalMinor's descending sequence, (2) clearly express the melodic-minor contract (distinct ascending vs. descending), and (3) keep the ascending-specific adjustments localized to ascending().

## Args:
    None (method is called on self). Implicit expectations:
    - self.tonic (str): must be a valid tonic string validated by the base _Scale constructor.
    - self.octaves (int-like): determines how many times the core descending pattern is repeated.

## Returns:
    list[str]: A list of note-name strings in descending order.
    - Construction rule: take the NaturalMinor(self.tonic).descending() sequence, remove its final duplicate-top tonic (slice [:-1]) to obtain the 7-degree pattern, repeat that pattern self.octaves times, then append the pattern's first element as the top-of-scale duplicate.
    - Typical length: 7 * self.octaves + 1 (when self.octaves is a positive integer).
    - Edge-case returns:
        - If self.octaves == 0 (or a negative integer), Python list-repetition semantics produce an empty repeated segment; the method still appends [notes[0]] and returns a single-element list containing the tonic from the NaturalMinor pattern.
        - If self.octaves is not an integer (or not supported for list repetition), a TypeError is raised instead of returning a list.

## Raises:
    - NoteFormatError: propagated from NaturalMinor(...) constructor or from functions called by NaturalMinor.descending() (for example, if self.tonic is not a recognized/valid note/key string).
    - TypeError: if self.octaves is of a type that cannot be used to multiply a list (e.g., a float or incompatible object), the repetition expression notes * self.octaves will raise TypeError.
    - Any other exceptions raised by NaturalMinor(...).descending() (for example, exceptions propagated from get_notes()) will be propagated unchanged.

## State Changes:
    Attributes READ:
        - self.tonic
        - self.octaves
    Attributes WRITTEN:
        - None (the method does not mutate self or any of its attributes)

## Constraints:
    Preconditions:
        - The instance must have been initialized such that self.tonic is valid per the base _Scale validation (otherwise NaturalMinor(...) construction may raise NoteFormatError).
        - self.octaves should be an integer (or an object compatible with Python list repetition) to get the expected repeated pattern semantics.
    Postconditions:
        - The object remains unchanged after the call.
        - The returned list follows the melodic-minor-descending convention by delegating to the natural-minor descending pattern and repeating that pattern according to self.octaves, with a duplicate top tonic appended as the last element.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside self. The method allocates and returns a new list containing note-name strings.

## `mingus.core.scales.Bachian` · *class*

## Summary:
Represents the Bachian (a melodic-minor-like) scale for a given tonic and number of octaves. It is a thin concrete _Scale subclass whose ascending() implementation delegates to the MelodicMinor scale pattern and exposes the result using the _Scale interface.

## Description:
Instantiate this class when you need a scale object whose ascending pitch sequence follows the melodic-minor (Bachian) pattern for a given tonic and spans a specified number of octaves. The class exists as a semantic alias/variant of the melodic-minor behavior: its ascending() is implemented by obtaining a single-octave melodic-minor pattern from MelodicMinor, repeating that pattern according to this instance's octaves, and appending the tonic at the top octave.

Known callers / typical usage:
- Client code that constructs scale objects generically via concrete classes (e.g., for rendering or analysis).
- Code that specifically requests a "Bachian" scale for stylistic or naming reasons but expects melodic-minor ascending notes.

Motivation and responsibility boundary:
- Responsibility: produce an ordered list of note-name strings representing the Bachian (melodic-minor-like) ascending pitch collection across the requested octaves and provide the usual _Scale helpers (degree, descending, len, etc.).
- Not responsibility: low-level note-format validation beyond what _Scale provides, or key-to-note mapping (delegated to underlying helper classes such as MelodicMinor and get_notes).

Implementation note:
- The ascending() method delegates to MelodicMinor(self.tonic).ascending() to obtain a single-octave augmented pattern, removes the final tonic duplicate from that returned list to get the single-octave pattern, repeats it self.octaves times, then appends the pattern's tonic to close the final octave. This makes Bachian(self.tonic, octaves=n).ascending() equivalent (in result) to MelodicMinor(self.tonic, octaves=n).ascending() for well-formed inputs.

## State:
- tonic (str)
    - What: the root note string (e.g., "C", "F#", "Bb").
    - Source: Provided as the note argument to __init__ and set by _Scale.__init__.
    - Constraints: _Scale.__init__ raises NoteFormatError if note.islower() is True (fully lowercase strings are rejected).
    - Invariant: remains equal to the constructor-supplied note unless mutated externally.

- octaves (int-like)
    - What: how many octaves the scale spans.
    - Source: Provided as the octaves argument to __init__ and stored by _Scale.__init__.
    - Default: 1.
    - Valid values & behavior:
        * A positive integer n => expected ascending() length is 7 * n + 1 (seven degrees per octave repeated n times plus the top tonic).
        * Zero or negative integers follow Python list-repetition semantics (notes * 0 yields an empty list; the implementation will still append the tonic and thus return a single-element list [tonic]).
        * Non-integer types may raise TypeError when list repetition is attempted.
    - Invariant: remains equal to the constructor-supplied value unless mutated externally.

- name (str)
    - What: human-readable instance name set by the constructor.
    - Value: "{tonic} Bachian" (e.g., "A Bachian").
    - Purpose: used by __repr__ and display routines inherited from _Scale.

- type (class attribute, str)
    - What: scale quality identifier.
    - Value: "minor" (literal).

Class invariants:
- ascending() returns a list-like sequence of note-name strings ordered tonic-upward and includes the top-of-scale tonic duplicate as the final element (this class produces that convention through its implementation).
- ascending() must not mutate instance state; it computes and returns a new list on each call.
- descending() is provided by _Scale (default: list(reversed(self.ascending()))), so it will reflect the ascending() result.

## Lifecycle:
Creation
- Signature: __init__(self, note, octaves=1)
    - note (str): required. Must not be a fully-lowercase string (otherwise _Scale.__init__ raises NoteFormatError).
    - octaves (optional, default 1): integer-like repetition count.
- What __init__ does:
    1. Calls _Scale.__init__(note, octaves) to set self.tonic and self.octaves and perform basic validation.
    2. Sets self.name = "{0} Bachian".format(self.tonic).

Usage (typical sequence)
1. Instantiate: s = Bachian("A", octaves=1)
2. Inspect s.name, s.tonic, s.octaves as needed.
3. Call s.ascending() to get the ordered ascending note list (includes final tonic duplicate).
4. Call s.descending() (inherited) to get the reversed list.
5. degree(), __len__(), equality operators, and __repr__() behave per _Scale semantics.

Destruction / cleanup
- No external resources allocated. No explicit cleanup or context-manager protocol required.

## Method Map:
flowchart TD
    ctor[__init__(note, octaves=1)] --> set_name[set self.name = "{tonic} Bachian"]
    set_name --> ready[instance ready]
    ready --> ascending_call[ascending()]
    ascending_call --> mm_asc[call MelodicMinor(self.tonic).ascending()]
    mm_asc --> strip_final[notes = mm_asc[:-1]  # single-octave pattern]
    strip_final --> repeat_pattern[result = notes * self.octaves]
    repeat_pattern --> append_top[result = result + [notes[0]]]
    append_top --> return_asc[return list[str]]
    ready --> descending_inherited[descending() from _Scale -> reversed(ascending())]

Notes:
- ascending() depends on MelodicMinor returning at least one element (practically 8 elements for a normal melodic-minor single-octave result). The implementation treats MelodicMinor(...).ascending() as a list-like sequence and slices off its last element to obtain the single-octave pattern.

## Raises:
- NoteFormatError
    - Trigger: __init__ when the provided note string is fully lowercase; this exception originates in _Scale.__init__.
- IndexError
    - Possible triggers:
        * If MelodicMinor(self.tonic).ascending() returns a shorter-than-expected list so that slicing or later indexing (notes[0] when append occurs) fails.
        * Unlikely in normal operation, but possible if an underlying helper returns malformed data.
- TypeError
    - Possible triggers:
        * If octaves is not an integer-like value and list repetition (notes * self.octaves) is attempted.
        * If elements returned by MelodicMinor are not strings and subsequent operations assume string behavior.
- Any exceptions raised by MelodicMinor, get_notes, augment/diminish/reduce_accidentals or other underlying helpers will propagate unchanged.

## Example:
- Typical creation and usage (illustrative, not code-executed here):
    1. Create a Bachian scale for tonic "A":
        - s = Bachian("A")  # sets s.name == "A Bachian", s.octaves == 1
    2. Retrieve ascending notes:
        - notes = s.ascending()
        - Expected result (typical melodic-minor pattern): ["A", "B", "C", "D", "E", "F#", "G#", "A"]
    3. For multiple octaves:
        - s2 = Bachian("A", octaves=2)
        - s2.ascending() => ["A","B","C","D","E","F#","G#","A","B","C","D","E","F#","G#","A"]
    4. Notes:
        - For well-formed input, Bachian(...).ascending() is functionally equivalent to MelodicMinor(tonic, octaves=<same>).ascending() because Bachian composes the single-octave melodic-minor pattern produced by MelodicMinor(self.tonic).ascending() and repeats it according to self.octaves before appending the tonic.

### `mingus.core.scales.Bachian.__init__` · *method*

## Summary:
Initializes the Bachian scale instance by delegating base initialization to the parent _Scale and setting the instance's human-readable name to "{tonic} Bachian". This configures the object's tonic and octave span and records the class-specific name.

## Description:
This constructor is invoked when a Bachian scale object is created (e.g., s = Bachian("A", octaves=1)). Typical callers include client code that constructs concrete scale objects for rendering, analysis, or stylistic selection and factory routines that instantiate specific scale classes by name.

Lifecycle stage:
- Constructor / object-creation stage. It runs as part of standard instantiation and must complete successfully before the instance is used by other methods such as ascending(), descending(), degree(), or __repr__().

Reason this logic is factored into its own __init__:
- The class delegates generic validation and storage of the tonic and octaves to the common _Scale initializer (called via super). The remaining class-specific responsibility is to set a readable name that identifies this concrete scale type; keeping that in the constructor centralizes instance setup and preserves a clear separation between shared initialization and Bachian-specific labeling.

## Args:
    note (str): The tonic / root note for the scale (e.g., "C", "F#", "Bb"). Must be a note string accepted by the _Scale constructor (see _Scale.__init__ for exact allowed formats). There is no mutation of this argument; it is forwarded to the parent constructor which stores it as self.tonic.
    octaves (int, optional): Number of octaves the scale should span. Default is 1. This value is forwarded to the parent constructor and stored as self.octaves; it is expected to be an integer-like value appropriate for downstream methods (e.g., ascending()).

## Returns:
    None

## Raises:
    NoteFormatError:
        - Condition: Raised if the provided note string fails the format validation performed by the parent _Scale.__init__ (for example, a fully-lowercase note string is rejected).
        - Source: This exception originates from the call to super(Bachian, self).__init__(note, octaves).
    Any exception raised by the parent constructor:
        - Condition: Any error thrown by _Scale.__init__ (validation errors, FormatError, RangeError, TypeError, etc.) will propagate unchanged.
        - Note: This constructor does not catch or wrap exceptions from the parent.

## State Changes:
Attributes READ:
    - self.tonic
        - When: read after the parent constructor returns, to format the instance name.
        - Purpose: used to build the human-readable name string.

Attributes WRITTEN:
    - self.name
        - Value set: a string equal to "{0} Bachian".format(self.tonic)
        - When: immediately after the parent constructor call.
    - (Indirect / via parent) self.tonic and self.octaves
        - Effect: these attributes are assigned by the parent _Scale.__init__ invoked via super; they are therefore established as part of this method's execution although not directly assigned here.

## Constraints:
Preconditions:
    - The caller must supply a note value acceptable to the shared _Scale constructor (commonly a properly-formatted note string, not a completely lowercase token).
    - octaves should be an integer-like value appropriate for later list-repetition operations performed by other methods (e.g., ascending()); if octaves is an inappropriate type the parent constructor may still accept it but later operations may raise TypeError.

Postconditions:
    - self.tonic is set (by the parent constructor) to the normalized tonic derived from the note argument.
    - self.octaves is set (by the parent constructor) to the provided octaves argument (or a normalized equivalent).
    - self.name is set to the literal string "{tonic} Bachian" where {tonic} is the value of self.tonic at the time of assignment.

## Side Effects:
    - No external I/O, network access, or filesystem operations.
    - Mutates the instance by initializing state (self.tonic, self.octaves via parent; self.name directly).
    - May raise exceptions from the parent constructor which will propagate to the caller.

### `mingus.core.scales.Bachian.ascending` · *method*

## Summary:
Return the ascending pitch-name sequence for this Bachian (minor) scale by taking a single-octave melodic-minor ascending pattern (without its top tonic), repeating that 7-note pattern for the configured number of octaves, and appending the tonic as the final top duplicate. This method does not mutate the instance.

## Description:
Known callers and context:
- Typical callers are user code or higher-level utilities that request a scale object's ascending degree sequence for display, analysis, MIDI/notation export, or algorithmic composition. Examples include UI renderers, serializers, or any code that treats different _Scale subclasses uniformly and calls their ascending() accessor.
- This method is invoked at the "accessor" stage of a scale object's lifecycle when a consumer needs the ordered, tonic-upward note names for the Bachian scale across one or more octaves.

Why this is a separate method:
- The Bachian ascending form is a scale-specific accessor that composes behavior from an existing MelodicMinor scale. Encapsulating it in its own method keeps the scale's contract clear (how Bachian ascending sequences are produced) and avoids duplicating or mixing MelodicMinor-specific logic in callers. It expresses the scale-level policy (use MelodicMinor's single-octave pattern, drop its top duplicate, repeat per octaves, append tonic) in one place.

## Args:
    None.

## Returns:
    list[str]: Ordered note-name strings representing the Bachian ascending scale across the instance's octaves. Typical return properties:
    - When preconditions hold (see Constraints), the list length is 7 * self.octaves + 1 (seven distinct scale degrees repeated per octave, plus the final tonic duplicate).
    - The first element is the tonic (notes[0] from the single-octave MelodicMinor pattern); the final element is the same tonic repeated an octave above.
    - The returned list is a new Python list (no internal state objects are exposed).

## Raises:
    NoteFormatError:
        - Condition: If constructing MelodicMinor(self.tonic) or calling MelodicMinor.ascending() raises NoteFormatError (for example, because self.tonic is not a recognized note/key format).

    IndexError:
        - Condition A: If MelodicMinor(self.tonic).ascending() returns a sequence that is too short so that slicing to remove the top duplicate yields an empty list; attempting to access notes[0] when appending the final tonic will raise IndexError.
        - Condition B: If the MelodicMinor.ascending() result is malformed (contains empty strings) and subsequent uses expect non-empty strings (rare and would usually propagate from lower-level routines).

    TypeError:
        - Condition: If self.octaves is not an integer-like value supported by Python list repetition, evaluating notes * self.octaves may raise TypeError (for instance, if self.octaves is None or a non-integer string).

    Any other exception raised by MelodicMinor.ascending(), get_notes(), or underlying utilities will propagate unchanged.

## State Changes:
Attributes READ:
    - self.tonic (str): used to construct the MelodicMinor instance that provides the base single-octave pattern.
    - self.octaves (int-like): used to determine how many times to repeat the 7-note pattern.

Attributes WRITTEN:
    - None. This method does not modify self or other external objects; it only constructs and returns a new list.

## Constraints:
Preconditions:
    - self.tonic must be a valid tonic acceptable to MelodicMinor/NaturalMinor and get_notes(). If not, MelodicMinor.__init__ or MelodicMinor.ascending() will raise NoteFormatError.
    - MelodicMinor(self.tonic).ascending() is expected to return the conventional single-octave ascending list that ends with a duplicate tonic (commonly 8 elements, 7 distinct degrees plus the final tonic). The method slices off that final duplicate; therefore the sliced list should contain at least one element (the tonic) so indexing notes[0] is valid.
    - self.octaves should ideally be a non-negative integer. If self.octaves is zero, Python list repetition rules produce an empty repetition of the 7-note pattern and the method will still return a single-element list containing the tonic (notes[0]) — provided the sliced notes list is non-empty. If self.octaves is negative or non-integer, behavior follows Python list-repetition semantics and may raise or produce surprising results.

Postconditions:
    - The returned value is a list of note-name strings representing the Bachian ascending form repeated across octaves with the final tonic duplicate appended.
    - The instance (self) remains unchanged.

## Side Effects:
    - No file, network, or other external I/O is performed.
    - No mutation of objects outside the method or of self occurs.
    - The only external interactions are pure-function-style calls: constructing a MelodicMinor instance and calling its ascending() accessor; any side effects therefore originate in those calls and would propagate (but none are introduced here).

## Implementation steps (reconstructable):
    1. Call MelodicMinor(self.tonic).ascending() to obtain the melodic-minor ascending sequence for a single octave. This sequence is expected to include the top-of-scale tonic duplicate.
    2. Remove the final duplicate tonic from that single-octave list by slicing [:-1] to produce a 7-element base pattern (notes).
    3. Repeat that 7-note pattern self.octaves times using Python list multiplication: notes * self.octaves.
    4. Append the first element of the base pattern (notes[0], the tonic) as the final top duplicate: result = notes * self.octaves + [notes[0]].
    5. Return result.

Example (behavioral illustration):
    - If self.tonic == "A" and self.octaves == 1:
        MelodicMinor("A").ascending() -> ['A', 'B', 'C', 'D', 'E', 'F#', 'G#', 'A'] (example melodic-minor single-octave)
        slicing -> ['A', 'B', 'C', 'D', 'E', 'F#', 'G#']
        repeat and append -> ['A', 'B', 'C', 'D', 'E', 'F#', 'G#', 'A']
    - If self.octaves == 2 the 7-note group is repeated twice then final tonic appended: length 15 (7*2 + 1).

Developer notes and cautions:
    - This method composes behavior from MelodicMinor.augmentations are performed inside MelodicMinor.ascending(); Bachian.ascending only handles repetition and final-tonic duplication.
    - Validate self.octaves and self.tonic at construction or before calling this method if you require strict types/values to avoid raising TypeError/IndexError during list operations.

## `mingus.core.scales.MinorNeapolitan` · *class*

## Summary:
Represents a "minor Neapolitan" scale anchored at a tonic note. Provides ascending() and descending() accessors that return the scale degrees as lists of note-name strings across the configured number of octaves, applying the Neapolitan alteration (lowered 2nd in ascending, lowered 7th in descending) to the base minor patterns.

## Description:
MinorNeapolitan is a concrete _Scale subclass modeling the minor-Neapolitan scale (a minor-mode scale with a chromatically lowered degree producing the Neapolitan quality). Instantiate this class when you need a programmatic representation of the Minor Neapolitan scale for rendering, degree lookup, interval calculations, or analysis.

Design responsibilities and motivation:
- Encapsulates only the small degree alterations that distinguish the Minor Neapolitan from standard minor scales: the ascending form is derived from the harmonic minor pattern with the second degree lowered by one semitone; the descending form is derived from the natural minor pattern with the seventh degree lowered by one semitone.
- Reuses existing scale classes (HarmonicMinor and NaturalMinor) and the string-level utility diminish() to avoid duplicating note-generation logic and to preserve consistent note naming.
- Conforms to the _Scale contract: ascending() and descending() return list-like sequences of note-name strings and do not mutate instance state.

Known callers / typical usage:
- Any client code or library code that requests a minor-Neapolitan scale object for degree lookup or rendering.
- Factory functions or higher-level APIs that enumerate supported scales and construct MinorNeapolitan when the "minor Neapolitan" quality is requested.

## State:
- type (class attribute)
    - Type: str
    - Value: "minor"
    - Purpose: identifies the scale quality (used consistently across minor-mode scale classes).

- tonic (inherited from _Scale)
    - Type: str
    - Description: the root note name used to derive the scale (examples: "C", "F#", "Bb").
    - Constraints: _Scale.__init__ raises NoteFormatError if the supplied tonic string is fully lowercase (note.islower() == True). The class assumes tonic is otherwise acceptable to get_notes() / NaturalMinor / HarmonicMinor.
    - Invariant: remains equal to the constructor-supplied value for the life of the instance (unless external mutation occurs).

- octaves (inherited from _Scale)
    - Type: typically int
    - Default: 1 (constructor default)
    - Description: the number of octaves the returned sequence should span. Methods use Python list-repetition semantics (pattern * self.octaves).
    - Constraints and behavior:
        - Intended to be an integer >= 1 for musically expected behavior. The class does not coerce or validate it.
        - If octaves == 0 or negative, list repetition semantics apply (pattern * 0 => empty list); methods still append the pattern's first element and return a minimal list.
        - If octaves is not a repetition-compatible type (e.g., float or None), Python will raise a TypeError when attempting pattern * self.octaves.

- name (assigned in __init__)
    - Type: str
    - Value: "<tonic> minor Neapolitan" (tonic is the stored self.tonic)
    - Purpose: human-readable name used by __repr__ and logging.

Class invariants:
- ascending() and descending() must return lists of note-name strings and must not mutate the instance attributes (tonic, octaves, name).
- For a positive integer octaves, the nominal length of ascending()/descending() is 7 * self.octaves + 1 (seven-degree pattern repeated octaves times plus the top-of-pattern tonic duplicate). This follows the same pattern conventions used by the _Scale subclasses it composes.

## Lifecycle:
- Creation:
    - Instantiate with MinorNeapolitan(note, octaves=1)
        * note (str): required tonic string (must not be fully lowercase under _Scale rules).
        * octaves (int, optional): default 1. Should be an integer for expected behavior.
    - __init__ behavior:
        * Calls _Scale.__init__(note, octaves) which sets self.tonic and self.octaves and may raise NoteFormatError if the tonic is invalid (fully lowercase).
        * Sets self.name to "<tonic> minor Neapolitan".

- Usage:
    - Typical sequence:
        1. Construct the MinorNeapolitan instance.
        2. Call ascending() to get the ascending degree list (uses HarmonicMinor internally, then lowers the second degree).
        3. Call descending() to get the descending degree list (uses NaturalMinor internally, then lowers the seventh degree).
    - Methods are accessors only and do not require or perform any ordering constraints beyond constructing the instance before calling them.
    - Methods do not mutate instance attributes.

- Destruction / cleanup:
    - No explicit cleanup is required. Instances are regular Python objects managed by garbage collection.

## Method Map:
flowchart TD
    ctor[MinorNeapolitan.__init__(note, octaves=1)]
    ctor --> set_name[set self.name = "<tonic> minor Neapolitan"]
    ascending --> call_harmonic[call HarmonicMinor(self.tonic).ascending()]
    call_harmonic --> strip_top_asc[strip final duplicate via [:-1] => 7-element pattern]
    strip_top_asc --> lower_2nd[notes[1] = diminish(notes[1])  (lower 2nd degree)]
    lower_2nd --> repeat_asc[return notes * self.octaves + [notes[0]]]
    descending --> call_natural[call NaturalMinor(self.tonic).descending()]
    call_natural --> strip_top_desc[strip final duplicate via [:-1] => 7-element pattern]
    strip_top_desc --> lower_7th[notes[6] = diminish(notes[6])  (lower 7th degree)]
    lower_7th --> repeat_desc[return notes * self.octaves + [notes[0]]]

(Interpretation: ascending() composes HarmonicMinor.ascending(), lowers index 1, repeats pattern; descending() composes NaturalMinor.descending(), lowers index 6, repeats pattern. Both append the pattern's first element as the final top-octave tonic.)

## Behavior details (inputs, outputs, edge cases):
- ascending()
    - Inputs: none (uses instance self.tonic and self.octaves).
    - Process:
        1. Instantiate HarmonicMinor(self.tonic) with default octaves=1 and call its ascending().
        2. Take the returned list and slice off the final duplicate tonic via [:-1] to obtain a 7-element single-octave pattern.
        3. Lower the second scale degree: notes[1] = diminish(notes[1]).
        4. Repeat that 7-element pattern self.octaves times and append notes[0] (the pattern's tonic) as the final element.
    - Returns: list[str] — nominal length 7 * self.octaves + 1 for integer octaves >= 1.
    - Edge cases:
        - If HarmonicMinor(self.tonic).ascending() returns fewer than 2 elements, assigning notes[1] will raise IndexError (unexpected for correct upstream behavior).
        - If self.octaves is 0, returned list length will be 1 (only the appended notes[0]).
        - If self.octaves is not compatible with list repetition, a TypeError is raised.

- descending()
    - Inputs: none (uses self.tonic and self.octaves).
    - Process:
        1. Instantiate NaturalMinor(self.tonic) with default octaves=1 and call its descending().
        2. Strip the final duplicate tonic via [:-1] producing a 7-element pattern.
        3. Lower the seventh scale degree: notes[6] = diminish(notes[6]).
        4. Repeat that 7-element pattern self.octaves times and append notes[0] as the final element.
    - Returns: list[str] — nominal length 7 * self.octaves + 1 for integer octaves >= 1.
    - Edge cases: analogous to ascending() regarding IndexError, TypeError, and octaves semantics.

## Raises:
- NoteFormatError
    - When: during construction if the supplied tonic is rejected by _Scale.__init__ (e.g., tonic.islower() is True) or when HarmonicMinor/NaturalMinor or their get_notes helpers raise it for an unrecognized key format.
    - Propagation: Not caught by MinorNeapolitan; it bubbles to the caller.

- TypeError
    - When: evaluating pattern * self.octaves if self.octaves is not a repetition-compatible type (e.g., float, None).
    - When: if diminish or the underlying scale code is called with unexpected types.

- IndexError
    - When: if the single-octave pattern obtained from HarmonicMinor.ascending() or NaturalMinor.descending() is unexpectedly shorter than expected and an index assignment (notes[1] or notes[6]) is attempted; or if diminish is called with an empty string and it accesses note[-1].
    - Note: These are defensive notes — under normal operation with correct upstream scale implementations and valid tonics, IndexError should not occur.

- Any exceptions raised by HarmonicMinor, NaturalMinor, or diminish are propagated to the caller (e.g., other ValueError/FormatError variants from get_notes()).

## Example:
- Creation:
    - Construct a MinorNeapolitan for tonic "C" with the default single octave:
      Instantiate MinorNeapolitan("C") — this sets self.tonic == "C", self.octaves == 1 and self.name == "C minor Neapolitan".
- Typical method use:
    1. Call ascending():
       - Internally obtains HarmonicMinor("C").ascending(), removes its final tonic duplicate ([:-1]) to get a 7-note pattern, lowers the second degree (index 1) with diminish(), repeats the 7-note pattern self.octaves times, and appends the pattern's tonic as the final element; returns that list of strings.
    2. Call descending():
       - Internally obtains NaturalMinor("C").descending(), removes its final tonic duplicate ([:-1]), lowers the seventh degree (index 6) with diminish(), repeats the 7-note pattern self.octaves times, and appends the pattern's tonic as the final element; returns that list of strings.
- Cleanup:
    - No cleanup required. Instances are ordinary objects subject to normal garbage collection.

Developer notes:
- MinorNeapolitan deliberately delegates base pattern generation to HarmonicMinor and NaturalMinor to ensure consistent naming and reuse; it performs only the single-character degree alteration (via diminish) required for the Neapolitan quality.
- If your application requires strict validation of octaves (for example, requiring octaves >= 1 and integer), validate or coerce the octaves value before instantiating MinorNeapolitan to avoid TypeError or semantic surprises.
- If you need normalized accidentals (e.g., no double-flats/double-sharps), consider post-processing returned lists with reduce_accidentals or another normalizer after calling ascending()/descending().

### `mingus.core.scales.MinorNeapolitan.__init__` · *method*

## Summary:
Initializes a MinorNeapolitan scale instance by delegating base initialization to the scale superclass and setting a human-readable name that embeds the resolved tonic; updates the object's tonic, octaves, and name state.

## Description:
This constructor performs two responsibilities:
1. Delegates core validation and attribute initialization (tonic and octaves) to the superclass constructor so the instance conforms to the _Scale contract and reuses existing parsing/validation logic.
2. Sets self.name to a readable string of the form "<tonic> minor Neapolitan" using the tonic value established by the superclass.

Known callers and lifecycle context:
- Called by client code and factory functions when creating a MinorNeapolitan scale object (e.g., MinorNeapolitan("C", 1)).
- Invoked at object construction time as part of normal instantiation; it is the entry point that prepares the instance for subsequent calls to ascending() and descending().

Why this logic is its own method:
- Construction requires the standardized initialization behavior provided by the shared _Scale.__init__ (validation and base attribute setup). The small class-specific action (assigning a descriptive name) is kept in the constructor so the instance is fully usable immediately after instantiation.

## Args:
    note (str): The tonic/root note name used to build the scale (examples: "C", "F#", "Bb").
        - Requirements: must be a valid note/key string as accepted by the superclass initialization (not fully lowercase under the project's NoteFormatError rule).
    octaves (int, optional): Number of octaves the scale's accessors will span. Defaults to 1.
        - Recommended: integer >= 1 for expected musical behavior. The constructor does not coerce or strictly validate this value; non-integer or negative values may raise errors later when repeating note lists.

## Returns:
    None

## Raises:
    NoteFormatError: Propagated from the superclass __init__ when the supplied note string is invalid (for example, if the project enforces that fully-lowercase note names are rejected).
    Any exception raised by the superclass constructor: any validation or parsing error that occurs in _Scale.__init__ will bubble up unchanged.
    (No new exceptions are raised directly by this method beyond those produced by the superclass.)

## State Changes:
Attributes READ:
    self.tonic -- read after the superclass initializer completes, used to format the human-readable name.

Attributes WRITTEN:
    self.tonic -- set by the invoked superclass constructor (via super().__init__).
    self.octaves -- set by the invoked superclass constructor (via super().__init__).
    self.name -- set here to "<tonic> minor Neapolitan" after self.tonic is available.

## Constraints:
Preconditions:
    - The `note` argument must be acceptable to the superclass initializer (e.g., not fully lowercase if the project enforces that via NoteFormatError).
    - If the caller expects standard repetition semantics for octaves, `octaves` should be an int >= 1; the constructor does not enforce this.

Postconditions:
    - After return, self.tonic and self.octaves are initialized by the superclass.
    - self.name is set to the string "<self.tonic> minor Neapolitan".
    - The instance is ready for use by accessor methods (ascending(), descending()) which rely on tonic and octaves.

## Side Effects:
    - Calls the superclass __init__, which performs parsing/validation and may raise exceptions; there are no I/O operations or external service calls performed by this method.

### `mingus.core.scales.MinorNeapolitan.ascending` · *method*

*No documentation generated.*

### `mingus.core.scales.MinorNeapolitan.descending` · *method*

## Summary:
Produces the descending note sequence for this Minor Neapolitan scale instance: it constructs a Natural Minor descending pattern, lowers the seventh scale degree by one semitone (Neapolitan alteration), repeats the 7-note pattern for the configured octaves, and appends a duplicate of the pattern's first element as the final tonic.

## Description:
- Known callers / typical usage:
    - Consumer code that queries a scale object for its descending degrees (rendering, analysis, chord/degree lookup) will call this method as part of the public Scale interface. It is invoked when a user or library routine needs the Minor Neapolitan scale in descending order.
    - Lifecycle stage: accessor call after the MinorNeapolitan instance has been constructed (after __init__). It is read-only with respect to the instance state.
- Why this is a dedicated method:
    - The Minor Neapolitan scale differs from a plain natural minor only by a single altered degree in its descending form. Extracting this logic into a method centralizes the creation of the altered descending pattern (calling NaturalMinor.descending, applying the single-degree alteration via diminish, and assembling the repeated/octave-extended list). This keeps alteration logic localized and makes the behavior explicit and testable.

## Args:
    None.

## Returns:
    list[str]: A list of note name strings representing the descending Minor Neapolitan scale spanning the configured number of octaves, with a duplicated top-of-pattern tonic appended as the final element.
    - Nominal length: 7 * self.octaves + 1 when self.octaves is a positive integer.
    - The returned sequence is assembled as:
        1. Start with NaturalMinor(self.tonic).descending() with its final duplicate element stripped (via [:-1]) to produce a 7-element descending pattern.
        2. The item at index 6 of that 7-element list (the 7th element of the pattern) is replaced with diminish(original) — i.e., lowered by one semitone according to the library's diminish rule.
        3. That 7-element pattern is repeated self.octaves times (Python list repetition) and a final element equal to the pattern's first element is appended.
    - Edge-case returns:
        - If self.octaves == 0 or a negative integer, the repeated portion (pattern * self.octaves) becomes an empty list and the method returns a single-element list [pattern[0]] (the final appended element).
        - If self.octaves is not an integer or not compatible with list repetition, a TypeError is raised by Python list repetition semantics (propagated).

## Raises:
    - NoteFormatError: propagated from NaturalMinor(self.tonic) or from NaturalMinor.descending() / underlying get_notes() if the tonic is not a valid key/note format (for example, if the tonic is fully lowercase or otherwise rejected by the key/notes helpers).
    - TypeError: if self.octaves is of a type incompatible with list repetition (for example, a float or None) — raised when evaluating notes * self.octaves.
    - IndexError or TypeError: unlikely but possible if the NaturalMinor.descending() result contains an unexpected empty or non-indexable element and diminish(notes[6]) tries to index or slice it; such exceptions are propagated from diminish.
    - Any other exception raised by NaturalMinor.descending() or diminish will be propagated unchanged.

## State Changes:
- Attributes READ:
    - self.tonic
    - self.octaves
- Attributes WRITTEN:
    - None. The method does not mutate the instance; it constructs and returns a new list.

## Constraints:
- Preconditions:
    - self.tonic must be a valid tonic string accepted by NaturalMinor (typically non-empty and not fully lowercase; invalid input may cause NoteFormatError in NaturalMinor.__init__ or get_notes).
    - self.octaves should be an integer (typically >= 1 for musical use). The method does not validate octaves; callers should supply a sensible integer.
- Postconditions:
    - The MinorNeapolitan instance is unchanged.
    - The returned list is a sequences of note-name strings where the 7th element of the base descending pattern has been lowered by one semitone (per diminish's rule: remove trailing '#' if present, otherwise append 'b') and the pattern is repeated and terminated by a duplicate of the pattern's first element.

## Side Effects:
    - None external: no I/O, no network calls, no mutation of objects outside the method's local scope.
    - The only observable effects are the returned list and possible exceptions raised and propagated from called routines (NaturalMinor.descending, diminish).

## `mingus.core.scales.Chromatic` · *class*

*No documentation generated.*

### `mingus.core.scales.Chromatic.__init__` · *method*

## Summary:
Initializes a Chromatic scale object by recording the provided key, extracting its tonic note, storing the octave span, and composing a human-readable name reflecting the tonic and that it is a chromatic scale.

## Description:
This initializer is invoked when a Chromatic scale object is constructed. Typical callers are client code, factories, or higher-level scale-generation utilities that need a representation of a chromatic scale for a given key and number of octaves. The method's logic is isolated here to centralize object state setup (assigning key, tonic, octaves, and name) so that other methods can rely on a consistent, minimal object invariant immediately after instantiation.

## Args:
    key (any): Identifier for the scale key. The value is passed directly to get_notes(key); it must be acceptable to that function and result in an indexable sequence of note names. Typical usage is a string such as "C", "G#", "Fm", etc., as accepted by the project's key-parsing utilities.
    octaves (int, optional): Number of octaves the chromatic scale should span. Default is 1. The initializer does not enforce a type or range, but callers should pass a positive integer when intending to represent one or more octaves.

## Returns:
    None

## Raises:
    Any exception raised by get_notes(key) may propagate out of this initializer (for example, if the provided key is malformed or unsupported). The initializer itself contains no explicit raise statements.

## State Changes:
Attributes READ:
    None (the initializer does not read any pre-existing self attributes)

Attributes WRITTEN:
    self.key         : set to the provided key argument
    self.tonic       : set to the first element of get_notes(key)
    self.octaves     : set to the provided octaves argument
    self.name        : set to a string of the form "<tonic> chromatic"

## Constraints:
Preconditions:
    - get_notes(key) must return an indexable sequence (e.g., list or tuple) with at least one element so that get_notes(key)[0] is valid.
    - For meaningful semantics, octaves should be a positive integer (>= 1), although the method does not enforce this.

Postconditions:
    - After return, the instance will have attributes key, tonic, octaves, and name set as described above.
    - No further validation or normalization of the tonic or octaves is performed here; downstream code should perform additional checks if required.

## Side Effects:
    - No I/O or external service calls are made by this initializer.
    - The only side effect is mutation of the newly constructed object's attributes (self.key, self.tonic, self.octaves, self.name).

### `mingus.core.scales.Chromatic.ascending` · *method*

## Summary:
Constructs and returns an ascending chromatic scale starting at the instance tonic, expanded for the configured number of octaves; does not mutate the Chromatic instance.

## Description:
- Known callers and typical context:
    - Consumers that request the ascending note sequence for a Chromatic scale object (for rendering, playback, analysis, or further transformations).
    - Typical lifecycle: called after a Chromatic instance is constructed (Chromatic(key, octaves)), usually at the point where the library user or another library component needs the ordered pitches for the ascending chromatic scale.
- Purpose and rationale for being a separate method:
    - Encapsulates the algorithm that interleaves diatonic scale degrees with inserted chromatic steps (by augmenting the preceding diatonic note when a whole step occurs). Keeping this logic in its own method keeps scale construction isolated and reusable by different callers without duplicating the insertion logic.

## Behavior (what it does):
- Uses the instance's key to obtain the seven diatonic note names for that key (get_notes(self.key)).
- Iterates the diatonic notes (from the second degree through the tonic again) and, for each step:
    - If the interval between the last appended note and the current diatonic note is a major second (whole step), inserts an intermediate chromatic pitch by augmenting the previous note (augment(notes[-1])) before appending the current diatonic note.
    - Otherwise, appends the current diatonic note directly.
- Removes the extra trailing note produced by the iteration (notes.pop()) to avoid duplication.
- Repeats the constructed single-octave chromatic sequence self.octaves times (Python list repetition) and appends the starting pitch of the base sequence once more to close the final octave.
- Returns a flat list of note-name strings representing the ascending chromatic sequence across the requested octaves, ending on the tonic of the final octave.

## Args:
- None (this is an instance method that reads instance attributes).

## Uses / Reads:
- self.key (str): passed to get_notes(self.key) to obtain the diatonic degrees for the base key.
- self.tonic (str): initial note placed at the start of the sequence and used to name the scale.
- self.octaves (int): number of octaves to expand the base chromatic sequence across.

## Returns:
- list[str]: an ordered list of note-name strings (no octave numbers) representing the ascending chromatic pitches starting at self.tonic and ending at the tonic of the final octave.
    - Typical length: base_chromatic_len * self.octaves + 1, where base_chromatic_len is the number of distinct pitch steps produced for one octave (for a standard major-key implementation this is normally 12). Example for C major with octaves=1:
        ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C"]
    - Edge-case returns:
        * If self.octaves == 0, the returned list will be [base_first_note] (because list * 0 yields [] then + [notes[0]]). This is allowed by Python semantics but is likely not the intended usage.
        * If self.octaves is a negative integer, list repetition yields an empty list before the final tonic; the method returns [base_first_note]. If octaves is not an integer, Python will raise a TypeError when attempting list * self.octaves.

## Raises:
- mingus.core.mt_exceptions.NoteFormatError (or other exceptions propagated from get_notes):
    - Trigger: self.key is not a recognized key string or get_notes raises due to invalid key format.
- Any exceptions raised by intervals.determine:
    - Trigger: intervals.determine may validate its inputs and raise if notes are malformed or unsupported; such exceptions propagate.
- IndexError or TypeError from augment:
    - Trigger: augment(notes[-1]) expects a non-empty string; augment may raise IndexError for an empty string or TypeError if the value is not a string. In normal operation notes[-1] comes from get_notes and will be a valid, non-empty string.
- TypeError when multiplying the notes list by a non-integer self.octaves.

## State Changes:
- Attributes READ:
    - self.key
    - self.tonic
    - self.octaves
- Attributes WRITTEN:
    - None. The method does not modify the Chromatic instance's attributes.

## Preconditions (caller responsibilities):
- self.key must be a key string accepted by get_notes(self.key).
- self.tonic must be a non-empty note-name string (this is normally set during __init__ using get_notes(key)[0]).
- self.octaves should be an integer. For intended behavior, use a positive integer (>= 1). The method does not validate octaves; non-integer values cause TypeError, and non-positive integers produce results per Python list-multiplication semantics (e.g., 0 or negative integers collapse the repeated portion).

## Postconditions (guarantees after successful return):
- Returns a list whose first element equals the instance tonic (self.tonic) and whose final element equals the same tonic (the tonic of the final octave).
- The list contains the diatonic degrees and inserted chromatic steps such that between any two adjacent diatonic degrees that are a major second apart an augmented previous-degree note is present between them.
- The Chromatic instance attributes remain unchanged.

## Side Effects:
- Calls get_notes(self.key), which may mutate a module-level cache (this is a side effect of get_notes, not of this method directly).
- Calls intervals.determine and augment (pure/string transformations) — no I/O, network, or external resource use.
- No file I/O or external service calls are performed.

## Implementation notes / pitfalls for reimplementation:
- Detection of where to insert an intermediate chromatic pitch depends on intervals.determine(a, b) returning the exact string "major second" for whole-step diatonic jumps. If intervals.determine returns a different representation, the detection will fail and the chromatic insertion will not occur. Reimplementations must either match that string value or compare using an interval-coded representation.
- augment(note) is used to construct the chromatic pitch between whole-step diatonic neighbors. augment removes a trailing lowercase 'b' or appends '#' otherwise; this behavior produces sharps for intermediate chromatic steps or removes flats when appropriate. Be careful when keys use flats: augment may return a different enharmonic spelling than other code expects.
- The method uses a sentinel tonic appended to get_notes(...) iteration and then pops the final element; this pattern ensures the code examines the interval from the final diatonic degree back to the tonic when deciding whether to insert an intervening chromatic note. Preserve the append-then-pop behavior (or an equivalent loop that compares successive diatonic degrees including the tonic) to match original behavior.
- Multiplying the single-octave list by self.octaves is the intended way to produce multiple octaves; ensure repetition semantics match Python list repetition.

## Examples:
- Typical usage:
    chrom = Chromatic("C", octaves=1)
    chrom.ascending() -> ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C"]
- With octaves=2:
    chrom = Chromatic("C", octaves=2)
    chrom.ascending() -> (the sequence above repeated twice) + ["C"], length = 12*2 + 1 = 25

### `mingus.core.scales.Chromatic.descending` · *method*

## Summary:
Constructs and returns a descending chromatic sequence of note name strings based on the object's tonic and key, repeated across the configured number of octaves.

## Description:
This method builds a single descending pattern (stored in the local list `notes`) and then repeats that pattern according to self.octaves, finally appending the pattern's first element.

Algorithmic steps:
1. Start `notes` with the object's tonic (reads self.tonic).
2. Iterate over get_notes(self.key) in reverse order. For each note:
   - If intervals.determine(note, notes[-1]) equals the exact string "major second", insert an intermediate diminished form of the previously appended note (computed by diminish(notes[-1]) and canonicalized by reduce_accidentals) before appending the current note.
   - Otherwise, append the current note.
3. Remove the last element appended during the loop via notes.pop(). This removes the duplicate terminal element produced by iterating the reversed key-note list (the loop appends an element corresponding to the starting/ending boundary).
4. Return notes repeated self.octaves times, with the first element of notes appended once: notes * self.octaves + [notes[0]].

Known callers / context:
- Called when a descending chromatic note list is needed (e.g., scale rendering, exporting, or analysis pipelines). It isolates the descending construction logic so callers can obtain a ready-to-use list without duplicating interval-handling or diminished-note insertion logic.

Why this is a separate method:
- The method encapsulates a discrete piece of logic (constructing a descending chromatic pattern, handling whole-step gaps by inserting diminished notes, and assembling multiple octaves). Keeping it separate improves testability and readability.

## Args:
No explicit arguments. Relies on the following instance attributes:
- self.tonic (str): Starting note name. Must be a valid note string acceptable to the project's note utilities.
- self.key (str): Key name used with get_notes(self.key) to produce the sequence of key notes. Must be recognized by get_notes.
- self.octaves (int): Number of times to repeat the single-pattern `notes` list before appending the pattern's first element. Expected to be an integer; see Constraints for behavior with non-positive values.

## Returns:
list[str]
- The returned list equals notes * self.octaves + [notes[0]], where `notes` is the single-pattern list produced before repetition.
- If preconditions are satisfied, the returned list contains the constructed descending pattern repeated self.octaves times, followed by the first element of that pattern.
- Length formula (when preconditions hold): len(returned_list) == len(notes) * self.octaves + 1.
- Behavior for special self.octaves values:
  - self.octaves == 0: returns [notes[0]] (the single appended element).
  - self.octaves < 0: Python list repetition with a negative factor yields an empty list, so the method returns [notes[0]] as well. Negative octaves are permitted by Python semantics but usually indicate a caller error.

## Raises:
- IndexError: If get_notes(self.key) yields an empty sequence, the method performs notes.pop(), leaving `notes` empty and then attempts to access notes[0]; this will raise IndexError.
- Any exception raised by helper utilities (get_notes, intervals.determine, diminish, reduce_accidentals) will propagate unchanged. The method itself does not catch or translate helper exceptions.

## State Changes:
Attributes READ:
- self.tonic
- self.key
- self.octaves

Attributes WRITTEN:
- None. The method only mutates local variables and returns a new list; it does not modify self attributes.

## Constraints:
Preconditions:
- get_notes(self.key) must return a non-empty iterable of note strings; otherwise the method will raise IndexError as described above.
- self.tonic and the note strings returned by get_notes must be valid inputs for diminish and reduce_accidentals if those are invoked.
- self.octaves should be an integer. Non-integer numeric types may lead to TypeError when used for list repetition.

Postconditions:
- On successful return, the object is unchanged and the caller receives a list constructed as notes * self.octaves + [notes[0]].
- The returned list is composed solely of strings (the note names) produced or passed through the called helper functions.

## Side Effects:
- No I/O, logging, or network activity.
- No mutation of external objects other than returning a newly created list.
- Exceptions from helper functions may be raised and will propagate to the caller.

## `mingus.core.scales.WholeTone` · *class*

## Summary:
Represents a whole-tone scale built on a given tonic. Produces the sequence of spelled pitch names separated by successive major seconds, repeated across the requested number of octaves, and includes the top-of-scale tonic duplicate.

## Description:
WholeTone is a concrete _Scale subclass that constructs the six-step whole-tone scale (each step a major second) starting from a provided tonic pitch name. Instantiate this class when you need the spelled pitch-class sequence for a whole-tone scale for display, degree lookup or simple melodic generation.

Typical callers
- Client code that needs the scale's ascending() or degree() values.
- Factory or higher-level music-theory utilities that produce Scale objects for analysis or rendering.

Motivation and responsibility boundary
- Responsibility: compute the ascending sequence of spelled pitch classes for a whole-tone scale and provide a readable name.
- Not responsible for: validating or normalizing tonic strings beyond the checks performed by the _Scale base class, or transposing across octave-numbered pitch strings. It repeats the same spelled pitch classes for each octave rather than transposing by numeric octave markers.

## State:
- type (str)
    - Value: "other" (class attribute)
    - Purpose: categorizes this scale implementation; read-only at class level.
- tonic (str)
    - Source: provided to __init__, stored by _Scale.
    - Example values: "C", "F#", "Bb".
    - Constraint: must not be a fully-lowercase string (the base _Scale.__init__ raises NoteFormatError when note.islower() is True).
    - Invariant: remains equal to the constructor-supplied note unless mutated externally.
- octaves (int-like)
    - Source: provided to __init__, stored by _Scale.
    - Default: 1
    - Expected values: integer >= 1 for the usual musical interpretation. The implementation does not enforce the numeric range: passing 0 results in an empty repeated body (but the final tonic duplicate is still appended), negative or non-integer values may produce Python runtime errors when used in list repetition.
    - Invariant: remains equal to the constructor-supplied value unless mutated externally.
- name (str)
    - Set in WholeTone.__init__ to "{tonic} whole tone" (for example, "C whole tone").
    - Purpose: used by __repr__ and logging/printing helpers.

Class invariants
- ascending() returns a list-like sequence (Python list) of spelled pitch-class strings in tonic-upward order and includes the top-of-scale tonic duplicate as its final element.
- For this class, the underlying one-octave pattern contains exactly six distinct pitch-class strings; ascending() returns that six-element pattern repeated octaves times followed by the original tonic as the final duplicate.

## Lifecycle:
Creation
- Constructor: WholeTone(note, octaves=1)
    - note (str): the tonic pitch name. Must not be fully lowercase (else base class raises NoteFormatError).
    - octaves (int, optional): how many times to repeat the six-note pattern. Default is 1.
    - Instantiation calls super(WholeTone, self).__init__(note, octaves) to set tonic and octaves and perform base-class validation, then sets self.name.
Usage
1. Call ascending() to obtain the ordered list of spelled pitch classes.
   - Returned list length = (6 * octaves) + 1.
   - The first 6 elements form the basic whole-tone cycle starting at the tonic; these six are repeated octaves times (concatenation) and then the initial tonic is appended once more as the top duplicate.
2. Use base-class helpers:
   - degree(n) to fetch the nth degree (1-based) where valid degrees are 1..(6*octaves). (degree() is provided by _Scale and will raise IndexError if n is out of range.)
   - descending() to receive the reversed ordering (provided by _Scale as reversed(ascending())).
3. No cleanup or destruction required.
Destruction
- No external resources allocated; object deletion follows normal Python semantics, no close() or context-management API.

## Method Map:
graph TD
    A[WholeTone.__init__(note, octaves=1)] --> B[_Scale.__init__ (tonic, octaves set; may raise NoteFormatError)]
    B --> C[set self.name = "{tonic} whole tone"]
    C --> D[ascending()]
    D --> E[construct base 6-note pattern starting at tonic]
    E --> F[repeat pattern self.octaves times]
    F --> G[append tonic as final duplicate]
    classDef default fill:#f9f,stroke:#333,stroke-width:1px;

## Behavior details (ascending)
- Steps performed:
    1. Start a list notes = [self.tonic].
    2. Repeat 5 times: compute intervals.major_second(notes[-1]) and append that result to notes.
       - After this loop notes contains 6 elements: tonic followed by five successive major-second-spelled pitches.
    3. Return notes * self.octaves + [notes[0]].
       - This concatenates the 6-element pattern self.octaves times, then appends the original tonic from the start of the pattern as the final top duplicate.
- Result properties:
    - For octaves == 1: ascending() returns 7 elements: six distinct steps plus the tonic duplicate at the top.
    - For octaves == n: ascending() returns 6*n + 1 elements.
    - The method does not mutate instance attributes.

## Raises:
- NoteFormatError
    - Source: propagated from _Scale.__init__ when the provided note string is all-lowercase (note.islower() == True).
    - Condition: invalid tonic format per base-class check.
- Exceptions propagated from intervals.major_second
    - Common suspects:
        - IndexError if an empty string is passed into major_second (not expected for normal tonic values but could occur if tonic was an empty string).
        - KeyError, NoteFormatError, TypeError, or other exceptions raised by the helpers major_second delegates to (these will propagate up).
    - These occur during ascending() while computing successive major-second spellings.
- TypeError or ValueError from improper octaves usage
    - If octaves is not an integer-like value suitable for list repetition (for example, a float), Python will raise a TypeError when performing list * octaves. Negative integer octaves are allowed by Python list repetition semantics (resulting in an empty repeated body) but are semantically unusual.

## Example:
- Create a one-octave whole-tone scale on C and query its ascending notes:
    * Instantiate: WholeTone("C")  (uses default octaves=1)
    * ascending() returns a list with 7 items, for example: ["C", "D", "E", "F#", "G#", "A#", "C"]
    * degree(1) -> "C", degree(6) -> "A#", degree(7) would raise IndexError (valid degrees are 1..6 for a single octave; _Scale.degree() excludes the final duplicate when indexing)
- Create a two-octave whole-tone scale:
    * Instantiate: WholeTone("C", octaves=2)
    * ascending() returns 13 items: the 6-note pattern repeated twice, then the final tonic duplicate: 6*2 + 1 = 13
    * Valid degree() indices are 1..12 (6 * octaves)

Notes and developer tips
- Because ascending() calls intervals.major_second repeatedly, malformed tonic strings or unusual accidental formats can raise errors originating in the interval helper. Validate tonic inputs before constructing a WholeTone if you want clearer, earlier errors.
- The implementation repeats spelled pitch classes rather than transposing octave numbers. If you require octave-transposed pitch strings (e.g., "C4", "D4", "E4", "F#4", ... "C5"), perform explicit octave-aware transposition after obtaining ascending().

### `mingus.core.scales.WholeTone.__init__` · *method*

## Summary:
Initializes a WholeTone scale instance by delegating base initialization (tonic and octaves) to the _Scale parent and then setting a human-readable name on the instance based on the resolved tonic.

## Description:
This constructor is called when creating a WholeTone object (e.g., WholeTone("C") or WholeTone("F#", 2)). It performs two steps:
1. Calls the parent class constructor to validate and store the tonic and octaves and perform any base-class initialization or checks.
2. Sets self.name to a readable label of the form "{tonic} whole tone" using the tonic value established by the base class.

Known callers and context:
- Client code instantiating specific Scale implementations for analysis or rendering (e.g., factory functions, tests, UI code).
- Typical lifecycle stage: object construction/time-of-creation when a WholeTone scale representation is required.
- This method is separated from other logic so that name formatting is applied after the base-class initialization/validation has produced the canonical self.tonic value; the heavy lifting of validation/assignment belongs in the shared _Scale.__init__.

## Args:
    note (str): The tonic pitch name provided by the caller (examples: "C", "F#", "Bb").
        - Expected format: a conventional pitch-class string; must not be fully lowercase (the base-class validation will raise NoteFormatError when note.islower() is True).
    octaves (int, optional): Number of octaves of the six-note whole-tone pattern to represent. Defaults to 1.
        - Expected values: integer >= 1 for normal usage. The method forwards this value to the base class; the base class may validate or coerce it.

## Returns:
    None

## Raises:
    NoteFormatError
        - Condition: propagated from the _Scale (base class) constructor when the provided note string fails the base-class format checks (for example, if note.islower() is True).
    Any exception raised by _Scale.__init__
        - Condition: this constructor does not catch exceptions from the parent constructor; they propagate to the caller. Examples depend on base-class implementation (TypeError or ValueError if octaves is unacceptable, FormatError/RangeError if the base class enforces those).

## State Changes:
    Attributes READ:
        - self.tonic: read when formatting the name after the base-class __init__ has run.
    Attributes WRITTEN:
        - self.name: set to a string "{tonic} whole tone".
        - Additionally, attributes written by the base class (via super call) include at minimum:
            - self.tonic (set to a normalized/validated tonic)
            - self.octaves (set to the provided octaves value)
        Note: this method itself only directly assigns self.name; the call to super(...) is responsible for setting other instance state.

## Constraints:
    Preconditions:
        - The caller must supply a note argument acceptable to the shared _Scale constructor (commonly a non-empty pitch-class string; not fully-lowercase).
        - octaves should be an integer-like value suitable for downstream usage; non-integer or nonsensical values may raise errors in base-class initialization or later when repeating patterns.
    Postconditions:
        - After successful return:
            - self.tonic is set (by the base class) to the validated/normalized tonic.
            - self.octaves is set (by the base class) to the provided octaves value.
            - self.name equals the string "{self.tonic} whole tone".
        - The object is ready for use with Scale methods such as ascending(), degree(), and descending().

## Side Effects:
    - No I/O or external service calls are performed.
    - Mutates only the instance (self) via attributes set by the base class and the assignment of self.name.
    - Any exceptions raised during base-class initialization are propagated to the caller.

### `mingus.core.scales.WholeTone.ascending` · *method*

## Summary:
Builds and returns the ascending whole-tone scale starting from the object's tonic, repeating the 6-note whole-tone pattern for the configured number of octaves and appending the tonic at the end to close the final octave.

## Description:
This method constructs the ascending form of a whole-tone scale (a hexatonic scale made of successive major seconds) beginning at the instance's tonic. It:
1. Initializes a list with the tonic.
2. Applies an ascending major second five times to generate the remaining five scale degrees (yielding six unique pitch classes).
3. Repeats that 6-note pattern self.octaves times (list repetition) to span the requested number of octaves.
4. Appends the tonic (the first scale degree) once more to mark the upper octave boundary.

Known callers and invocation context:
- Typical callers are user code or library utilities that request scale pitch collections (for display, playback, chord derivation, set operations, or analysis).
- This method is invoked at the point in the lifecycle when an ascending list of pitch classes for the scale is required (for example, when a user calls scale.ascending() or when higher-level code generates melodic sequences from scale objects).

Why this logic is its own method:
- The whole-tone scale has a specific, compact construction rule (six notes formed by repeated major seconds). Encapsulating it keeps scale generation consistent and separates interval-generation concerns (major_second) from higher-level operations (formatting, rendering, transposition). It also allows overriding/extension for other scale types without duplicating repeated-step logic.

## Args:
This is an instance method and takes no explicit arguments beyond self. The behavior depends on two instance attributes:
    - self.tonic (str): The starting pitch name (base-letter plus optional accidentals). Must be a valid pitch string understood by intervals.major_second.
    - self.octaves (int): Number of octaves to span. Expected to be a positive integer (>= 1) for the intended musical semantics.

## Returns:
    list[str]: A list of spelled pitch-class strings (base letter plus accidentals) representing the ascending whole-tone scale across the requested octaves, with the final tonic appended.
    - Each element is produced either directly from self.tonic (first element) or from intervals.major_second applied repeatedly.
    - Length: 6 * self.octaves + 1 when self.octaves is a positive integer (six unique pitch classes per octave, repeated, plus one closing tonic).
    - Example (conceptual): if tonic == "C" and octaves == 1, returns ["C", "D", "E", "F#", "G#", "A#", "C"] (actual accidentals depend on intervals.major_second spelling rules).

Edge-case return behaviors:
    - If self.octaves == 0 or a negative integer, Python list repetition semantics produce fewer repetitions (e.g., notes * 0 yields []). The method will still append [notes[0]] and return a list containing only the tonic in that case. This is allowed by the implementation but typically violates the expected musical precondition (octaves >= 1).
    - If self.octaves is not an integer, Python will raise TypeError at the list repetition operation.

## Raises:
This method does not explicitly raise exceptions itself, but the following can propagate:
    - Any exception raised by intervals.major_second(notes[-1]) for invalid pitch input (examples: IndexError for empty strings, NoteFormatError or ValueError from upstream note parsing, KeyError from unexpected letter inputs).
    - TypeError: if self.octaves is a non-integer type not supported by list repetition.
    - AttributeError: if the instance does not have self.tonic or self.octaves attributes.
No new exceptions are created by this method; it simply forwards exceptions from the interval helper or from standard Python operations.

## State Changes:
Attributes READ:
    - self.tonic
    - self.octaves

Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.tonic must be a valid pitch string whose base-letter (first character) is A-G and is acceptable to intervals.major_second. Supplying an invalid tonic may cause exceptions from the interval helper.
    - self.octaves should be an integer and, for expected musical behavior, >= 1.

Postconditions:
    - The returned list contains a repeated sequence of the 6 whole-tone pitch classes derived from the tonic, repeated self.octaves times, followed by the tonic again.
    - self remains unchanged.

## Side Effects:
    - No I/O is performed.
    - No mutation of global state occurs within this method. Any side effects originate from called helper functions (intervals.major_second) or from attribute access depending on their implementations (e.g., caching inside helpers).

## `mingus.core.scales.Octatonic` · *class*

*No documentation generated.*

### `mingus.core.scales.Octatonic.__init__` · *method*

## Summary:
Initializes an Octatonic scale instance by delegating base initialization to the superclass and setting the human-readable scale name on the instance.

## Description:
This constructor is invoked during object construction (e.g., when a caller instantiates an Octatonic scale: Octatonic('C', octaves=1)). It performs two responsibilities:
1. Delegates the primary initialization (validation of the provided tonic/note and octaves, and setup of scale state) to the superclass initializer.
2. Sets the instance attribute that holds the printable name of the scale, incorporating the tonic established by the superclass.

Known callers and context:
- Called whenever an Octatonic object is created as part of normal usage of the scales API (construction/lifecycle stage).
- This method is its own initializer because initializing a scale requires both the generic setup handled by the common/base Scale constructor and a subclass-specific name assignment; keeping the name assignment here avoids duplicating base-initialization logic.

## Args:
    note (str):
        The scale tonic / root note to construct the scale from. Accepted formats and exact validation are performed by the superclass initializer; pass the same values you would for other scale types (examples: 'C', 'F#', 'Bb').
    octaves (int, optional):
        The number of octaves of scale notes to generate/represent. Defaults to 1. Exact allowed range and validation are performed by the superclass initializer.

## Returns:
    None
    This is an initializer; it does not return a value. On success the instance is fully initialized and ready for use.

## Raises:
    Any exception raised by the superclass initializer is propagated unchanged. Typical exceptions imported in this module and likely raised by validation in superclass code include:
    - FormatError: if the provided note or format is invalid.
    - NoteFormatError: if the note string cannot be parsed.
    - RangeError: if octaves is out of an allowed range.
    (The exact trigger conditions for these exceptions are implemented in the superclass and are not rechecked here.)

## State Changes:
Attributes READ:
    - self.tonic: read when formatting the printable name after the superclass initializer has established the tonic.

Attributes WRITTEN:
    - self.name: set to a string of the form "<tonic> octatonic" (for example, "C octatonic").

Additionally, the call to super().__init__(note, octaves) may read or write other instance attributes (such as notes lists, internal representation, validation state); those modifications are performed by the superclass initializer.

## Constraints:
Preconditions:
    - The provided note and octaves must satisfy the superclass's validation rules (e.g., properly formatted note string, octaves within allowed range). These preconditions are enforced by the superclass initializer.

Postconditions:
    - After return, self.name is guaranteed to be a string equal to "{tonic} octatonic", where tonic is the canonical tonic value established by the superclass.
    - The instance has completed the superclass initialization step (so other attributes the superclass sets are available).

## Side Effects:
    - No I/O, logging, or external service calls are performed by this method.
    - The method mutates the instance state (self.name) and relies on the superclass initializer to perform additional state mutations.

### `mingus.core.scales.Octatonic.ascending` · *method*

*No documentation generated.*

