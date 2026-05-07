# `musicxml.py`

## `mingus.extra.musicxml._gcd` · *function*

## Summary:
Computes the greatest common divisor (GCD) of two integers, or of a sequence of integers when an iterable is provided.

## Description:
This helper implements the Euclidean algorithm for computing the greatest common divisor.

Known callers within the provided context:
- No direct callers are visible in the provided snippet. The function is written as a small utility likely intended for use by other functions that need integer GCD or LCM computations (for example, normalizing rhythm durations or combining fractional durations). A full repository search is recommended to find concrete callers.

Why this logic is extracted into its own function:
- Encapsulates the Euclidean algorithm in one place so other code can compute GCDs without duplicating the algorithm.
- Supports both the common two-argument form (a, b) and a variadic form (terms iterable) for convenience when reducing multiple numbers.
- Keeps numeric normalization and fraction-reduction logic separate from higher-level musicxml processing.

## Args:
    a (int or None): First integer operand for the two-argument form. If `terms` is not provided, `a` is the value returned when `b` is falsy (see postconditions). Default: None.
    b (int or None): Second integer operand for the two-argument form. The Euclidean loop runs while `b` is truthy. Default: None.
    terms (iterable[int] or None): Optional iterable (e.g., list or tuple) of integers. If provided (truthy), the function computes the GCD by reducing this iterable using the two-argument GCD implementation. If `terms` is provided, `a` and `b` are ignored.

Notes on parameter interdependencies:
- If `terms` is provided and truthy, `a` and `b` are ignored.
- If `terms` is provided but is an empty iterable, the underlying reduce call will raise a TypeError (see Raises).

Expected types:
- Intended for integers. Passing non-integer numeric types (floats) or non-numeric types may lead to TypeError or incorrect results due to modulo operation.

## Returns:
    int or None:
    - If called with `terms` (a truthy iterable): returns the integer GCD of all values in the iterable.
    - If called with `a` and `b` (or defaults): returns the integer GCD of `a` and `b`, computed with the Euclidean algorithm.
    - If both `a` and `b` are None and `terms` is not provided (or is falsy), the function returns the value of `a` (i.e., None).
    - The return value follows the routine's logic and may be negative if inputs are negative; the function does not explicitly normalize sign to positive.

All possible/edge-case return behaviors:
- _gcd(8, 12) -> 4
- _gcd(0, n) -> n (for non-zero n), because while b will evaluate and algorithm yields n
- _gcd(a=None, b=None) -> None
- _gcd(6, 0) -> 6 (the loop stops immediately and returns a)
- _gcd(8, -12) -> result depends on Python's modulo with negatives; may return a value whose sign matches implementation specifics (the function does not enforce abs())

## Raises:
    TypeError:
    - If `terms` is provided but is an empty iterable, functools.reduce will raise TypeError because no initial value is supplied.
    - If `terms` is not iterable, reduce will raise TypeError.
    - If non-integer / incompatible types are present in `terms` or supplied as `a`/`b` (for example, a string), operations like modulo (%) may raise TypeError.
    - Any TypeError raised originates from reduce or from invalid operations in the Euclidean loop; the function does not explicitly raise errors itself.

No other exceptions are raised intentionally by this implementation.

## Constraints:
Preconditions:
- Prefer passing integers. The algorithm expects integer operands for meaningful GCD results.
- If using `terms`, provide a non-empty iterable of integers to avoid reduce raising TypeError.
- Avoid passing both `terms` and intending to use `a`/`b`—`terms` takes precedence when truthy.

Postconditions:
- If valid integer inputs are given, the return value is an integer representing a greatest common divisor according to the Euclidean algorithm used.
- No global state is modified.
- No I/O is performed.

## Side Effects:
- None. The function performs pure computation without side effects: no file, network, stdout, global state, or external service interactions.

## Control Flow:
flowchart TD
    Start --> CheckTerms
    CheckTerms{terms provided and truthy?}
    CheckTerms -- Yes --> CallReduce[_call reduce(lambda a,b: _gcd(a,b), terms)_]
    CallReduce --> ReturnResult1[return reduced GCD result]
    CheckTerms -- No --> EnterLoop
    EnterLoop{while b truthy?}
    EnterLoop -- True --> LoopBody[(a,b) = (b, a % b)]
    LoopBody --> EnterLoop
    EnterLoop -- False --> ReturnA[return a]
    ReturnResult1 --> End[End]
    ReturnA --> End

## Examples:
- Typical two-argument usage:
    - _gcd(8, 12) returns 4
    - _gcd(6, 0) returns 6

- Variadic usage with an iterable:
    - _gcd(terms=[8, 12, 20]) returns 4

- Empty iterable triggers error (demonstrates error handling you should implement around calls):
    - Calling with an empty list: _gcd(terms=[]) will raise TypeError from functools.reduce. Example handling:
        try:
            result = _gcd(terms=some_list)
        except TypeError:
            # handle empty iterable or convert to default behavior
            result = None

- Edge-case:
    - _gcd() (no arguments) returns None because a defaults to None and b is falsy; wrap calls if a None is invalid in your context.

Implementation note for callers:
- If you need a non-negative gcd, call abs() on the result or on inputs before calling.
- To compute least common multiple (LCM) for integers, you can use: lcm(a,b) = abs(a // _gcd(a,b) * b) when _gcd(a,b) is non-zero and inputs are integers.

## `mingus.extra.musicxml._lcm` · *function*

## Summary:
Computes the least common multiple (LCM) of two integers, or of a sequence of integers when an iterable is provided; returns the numeric result of (a * b) / gcd(a, b) (division semantics follow the running Python version).

## Description:
Known callers within the provided context:
- No direct callers are visible in the provided snippet of mingus.extra.musicxml.py. The function is a local numeric utility likely intended for normalizing or combining integer durations or other integer-based musical values inside higher-level MusicXML export routines. A repository-wide search may find concrete call sites.

Why this logic is extracted into its own function:
- Encapsulates LCM computation and variadic reduction logic in one place so other code can compute least-common-multiple values without duplicating the arithmetic and reduction code.
- Provides a single responsibility: canonical LCM computation for two values and a convenience variadic form for many values (via the terms iterable).
- Keeps numeric combination logic separate from higher-level MusicXML formatting and composition code.

## Args:
    a (int or None): First operand for the two-argument form. Default: None.
    b (int or None): Second operand for the two-argument form. Default: None.
    terms (iterable[int] or None): Optional iterable of integers. If provided and truthy, the function ignores a and b and computes the LCM of all values in this iterable by reducing pairwise with _lcm. Default: None.

Interdependencies:
- If terms is provided and truthy, a and b are ignored.
- If terms is an empty iterable, functools.reduce will raise a TypeError (no initial value supplied).
- Intended inputs are integers. Passing None, non-integers, or incompatible types will raise TypeError at runtime.

## Returns:
    int or float or None:
    - When called with a and b (terms falsy): returns the result of (a * b) / _gcd(a, b).
      * On Python 3 this uses true division ("/") and will return a float when the division produces a non-integer numeric type (even when mathematically integral, Python 3 yields a float if operands are ints and "/" is used).
      * On Python 2 (if running under Python 2 semantics and no future division import), "/" between integers yields integer division and the return will be an int.
    - When called with a non-empty iterable via terms: returns the iteratively reduced LCM of all elements (the pairwise _lcm results described above). The numeric type follows the same Python-version division semantics described above.
    - If neither terms nor a/b are provided (a is None and terms is falsy), the function will attempt to compute using the defaults and will effectively return (None * None) / _gcd(None, None) which will raise TypeError; practically callers should not call with no meaningful numeric inputs.

All possible/edge-case return behaviors illustrated:
- _lcm(8, 12) -> mathematical LCM 24; on Python 3 this is 24.0 (float), on Python 2 this is 24 (int) if using integer division.
- _lcm(0, n) where n != 0 -> 0 (division is well-defined because _gcd(0,n) == abs(n) typically), result type per Python division rules.
- _lcm(0, 0) -> attempts to compute 0/0 and raises ZeroDivisionError at runtime.
- _lcm(terms=[3,4,5]) -> 60 (or 60.0 on Python 3 due to "/").

## Raises:
    TypeError:
    - If terms is provided but is an empty iterable, functools.reduce raises TypeError (no initial value).
    - If terms is not iterable, reduce will raise TypeError.
    - If a, b, or elements of terms are incompatible types for numeric multiplication or for _gcd (for example None, strings, or other non-numeric types), operations will raise TypeError.
    ZeroDivisionError:
    - If _gcd(a, b) returns 0 (for example when a == 0 and b == 0), the division (a * b) / _gcd(a, b) raises ZeroDivisionError.
    Any exception raised by _gcd (e.g., TypeError for invalid types) will propagate.

## Constraints:
Preconditions:
- Prefer passing non-None integers. For correct/expected behavior callers should ensure inputs are integers (or at least numeric types where multiplication, modulo and division behave as expected).
- Avoid calling with a == b == 0 (or a sequence whose pairwise gcd reduces to 0) unless you intentionally handle the resulting ZeroDivisionError.
- If using terms, ensure it is a non-empty iterable.

Postconditions:
- When inputs are valid and gcd != 0, the returned numeric value equals the mathematical LCM computed by the formula (a*b) / gcd(a,b) (subject to the language-level division semantics).
- No global state or external resources are modified.

## Side Effects:
- None. The function performs purely local arithmetic and recursion; it does not perform I/O, modify global variables, write to disk, make network calls, or print to stdout.

## Control Flow:
flowchart TD
    Start --> CheckTerms
    CheckTerms{terms provided and truthy?}
    CheckTerms -- Yes --> CallReduce[Call functools.reduce with lambda a,b: _lcm(a,b) over terms]
    CallReduce --> ReturnReduced[Return reduced LCM result]
    CheckTerms -- No --> ComputeLCM[Compute (a * b) / _gcd(a, b)]
    ComputeLCM --> CheckGCDZero{_gcd(a,b) == 0?}
    CheckGCDZero -- True --> RaiseZeroDiv[ZeroDivisionError raised by division]
    CheckGCDZero -- False --> ReturnLCM[Return computed LCM numeric value]
    ReturnReduced --> End
    ReturnLCM --> End

## Examples:
- Two-argument usage:
    try:
        # Mathematical LCM of 8 and 12 is 24.
        r = _lcm(8, 12)
        # On Python 3, r will be 24.0 because "/" yields a float; on Python 2 it will be 24 (int).
    except Exception as e:
        # handle TypeError / ZeroDivisionError
        raise

- Zero-handling:
    # LCM of 0 and 5 -> 0
    _lcm(0, 5)  # returns 0 or 0.0 depending on Python version

    # LCM of 0 and 0 -> raises ZeroDivisionError
    try:
        _lcm(0, 0)
    except ZeroDivisionError:
        # expected for this invalid input, handle accordingly
        pass

- Variadic usage:
    # Compute LCM of multiple integers
    _lcm(terms=[3, 4, 5])  # returns 60 (or 60.0 on Python 3)

Implementation note for callers:
- To guarantee integer (int) return values across Python versions, consider using integer-division where appropriate (e.g., (a // _gcd(a, b)) * b or int((a * b) / _gcd(a, b))) and normalize inputs with abs() if you want non-negative LCM.

## `mingus.extra.musicxml._note2musicxml` · *function*

## Summary:
Converts a single note (or a rest) into an xml.dom.minidom Element representing a MusicXML <note> node.

## Description:
This helper builds a minidom node for one musical note or a rest suitable for insertion into a MusicXML document. It is intended for internal use by MusicXML serialization routines in this module to convert the lightweight note representation used by the rest of the library into the XML structure expected by MusicXML.

Known callers within the codebase:
- No direct callers were discovered in the immediate scan. Conceptually this function is called by higher-level MusicXML export functions that iterate notes in a measure/track and assemble complete MusicXML documents. It is extracted as a separate function to encapsulate the mapping from the library's Note object (or None for rest) to the precise MusicXML node structure, keeping XML node construction isolated from measure/part-level logic.

Responsibility boundary:
- This function's single responsibility is to produce and return a minidom Element for the note; it does not attach the returned node into any document other than the small Document used to create nodes, nor does it manage durations, voice, type, ties, articulations, notations, or other MusicXML elements.

## Args:
    note (object or None):
        - Allowed values:
            * None — interpreted as a rest; the returned <note> node will contain a single <rest/> child.
            * An object representing a note with the following attributes:
                - name (str): pitch name string where the first character is the step letter 'A'..'G' and any following characters are accidentals represented by '#' for sharp and 'b' for flat (e.g. 'C', 'C#', 'Db', 'F##' is interpreted as two sharps).
                - octave (int or str-convertible to int): octave number to place inside <octave>.
        - Interdependencies:
            * If note is not None, both note.name and note.octave must be present and usable as described. The function reads note.name[0] (step) and iterates name[1:] to count accidentals.

## Returns:
    xml.dom.minidom.Element
        - A <note> element (xml.dom.minidom.Element) with one of two shapes:
            1. Rest:
                <note>
                  <rest/>
                </note>
            2. Pitch:
                <note>
                  <pitch>
                    <step>{single-letter A-G}</step>
                    <octave>{octave as string}</octave>
                    (optional) <alter>{integer}</alter>
                  </pitch>
                </note>
        - alter: omitted if there are no accidental symbols after the step; otherwise an integer string is produced where each '#' increases the integer by 1 and each 'b' decreases it by 1 (e.g., 'C#' -> alter 1; 'Dbb' -> alter -2).
        - The returned node is created by a new xml.dom.minidom.Document and is safe to import/adopt into another minidom Document if needed.

## Raises:
    - No exceptions are explicitly raised by the function.
    - Implicit exceptions that may occur:
        * AttributeError if note is not None but lacks .name or .octave attributes.
        * IndexError if note.name is an empty string (because name[0] is accessed).
        * TypeError/ValueError if note.octave is of a type that cannot sensibly be converted to str (rare).
    - Callers should validate note objects (or catch these exceptions) if their provenance is uncertain.

## Constraints:
    Preconditions:
        - If note is not None:
            * note.name is a non-empty string whose first character is the step (A-G). The function does not validate that the step is within A-G.
            * Characters after the first in note.name are interpreted only as '#' or 'b'; other characters are ignored by the counting loop (they do not change alter).
            * note.octave must be convertible to string (typically an integer).
    Postconditions:
        - The returned Element is always an xml.dom.minidom.Element named "note".
        - For note is None, the returned <note> contains exactly one child element named "rest".
        - For note not None, the returned <note> contains a <pitch> child with at least <step> and <octave>, and an <alter> child only if accidentals were present.

## Side Effects:
    - Creates a temporary xml.dom.minidom.Document instance and DOM nodes; no file, network, stdout, or global state is modified.
    - No external services are called.

## Control Flow:
flowchart TD
    Start --> CreateDoc[Create new minidom Document]
    CreateDoc --> CreateNoteNode[Create <note> node]
    CreateNoteNode --> IsNone{note is None?}
    IsNone -->|Yes| CreateRest[Create <rest> node]
    CreateRest --> AppendRest[Append <rest> to <note>]
    AppendRest --> ReturnNote[Return <note> node]
    IsNone -->|No| CreatePitch[Create <pitch> node]
    CreatePitch --> CreateStep[Create <step> node with note.name[0]]
    CreateStep --> CreateOctave[Create <octave> node with note.octave]
    CreateOctave --> CountAccidentals[Iterate note.name[1:] counting '#' and 'b']
    CountAccidentals --> HasAlter{count != 0?}
    HasAlter -->|Yes| CreateAlter[Create <alter> with count]
    CreateAlter --> AppendAlter[Append <alter> to <pitch>]
    HasAlter -->|No| SkipAlter[Do not create <alter>]
    AppendAlter --> AppendPitch[Append <pitch> to <note>]
    SkipAlter --> AppendPitch
    AppendPitch --> ReturnNote

## Examples:
1) Producing a rest node
    # Create a rest
    note_node = _note2musicxml(None)
    # note_node.toxml() -> '<note><rest/></note>'

2) Producing a C#4 pitch node using a minimal mock note object
    class MockNote:
        def __init__(self, name, octave):
            self.name = name
            self.octave = octave
    n = MockNote('C#', 4)
    note_node = _note2musicxml(n)
    # note_node.toxml() -> '<note><pitch><step>C</step><octave>4</octave><alter>1</alter></pitch></note>'

3) Producing an Eb3 pitch node
    n = MockNote('Eb', 3)
    note_node = _note2musicxml(n)
    # note_node.toxml() -> '<note><pitch><step>E</step><octave>3</octave><alter>-1</alter></pitch></note>'

Notes:
- The examples use a tiny mock object to demonstrate the required attributes; in real usage, pass the library's Note object or an equivalent object with .name and .octave attributes.
- The function does not append duration, type, voice or other MusicXML elements — those must be added by the caller.

## `mingus.extra.musicxml._bar2musicxml` · *function*

*No documentation generated.*

## `mingus.extra.musicxml._track2musicxml` · *function*

## Summary:
Converts a Track-like object into an XML DOM <part> element suitable for inclusion in a MusicXML document by transforming each bar into MusicXML and attaching instrument clef information when available.

## Description:
This helper builds an xml.dom.minidom.Element representing a MusicXML <part> consisting of the track's bars. For each bar in track.bars it calls a helper that converts a single bar to MusicXML and appends the returned bar nodes into the part; it also sets an incremental "number" attribute on each bar element. If the track has an associated instrument with a textual clef description, the function attempts to map that description to a MusicXML clef (sign and line) and inserts a <clef> element into every <attributes> element found inside the bar node(s).

Known callers within the codebase:
- No explicit callers are present in the provided snippet. This function is intended to be invoked by higher-level MusicXML serialization code that converts a Track or a Composition into a complete MusicXML Document (for example, a module-level exporter that iterates tracks/parts).

Why this is a separate function:
- Responsibility separation: this function focuses strictly on converting a single Track to a <part> element (bar iteration, numbering, and clef insertion). Extracting it keeps per-track logic isolated from composition-level assembly and from the lower-level bar-to-XML conversion (_bar2musicxml), making the code easier to test and reuse.

## Args:
    track (Track-like): An object representing a musical track.
        - Required attributes:
            * bars: an iterable (e.g., list) of bar objects. Each bar is passed to _bar2musicxml(bar) and must be accepted by that function.
            * instrument: optional. If present and truthy, it is expected to expose a clef attribute that is a string (e.g., "treble", "Bass", "alto", etc.). If instrument is falsy (None/False), no clef insertion is attempted.
        - Type note: The function does not enforce a concrete Track class type; it relies on attribute presence/shape described above.

## Returns:
    xml.dom.minidom.Element: A DOM Element representing the MusicXML <part> node for this track.
        - Structure guarantees:
            * The returned element is created via a fresh Document().createElement("part").
            * The element has an "id" attribute set to str(id(track)).
            * Each appended bar element (produced by _bar2musicxml) receives a "number" attribute with values "1", "2", ... in iteration order.
            * If a clef was determined from the instrument, a <clef> element (containing <sign> and <line> children) will be appended into each <attributes> element found inside the bar node(s).
        - Edge cases:
            * If track.bars is empty, the returned <part> element will contain no child bar elements (still has the "id" attribute).
            * The returned Element's ownerDocument is the new Document created inside the function (doms created with createElement are owned by that Document).

## Raises:
    AttributeError:
        - If track does not have the expected attributes (e.g., missing bars or instrument present but missing a clef attribute), attempting to access them will raise AttributeError.
    TypeError:
        - If track.bars is not iterable, iterating will raise TypeError.
    NameError / UnboundLocalError:
        - If the helper _bar2musicxml is not defined in the runtime module scope, calling it will raise NameError (or related).
    Any exception raised by _bar2musicxml:
        - Errors originating from the bar-to-XML conversion helper propagate unchanged.

## Constraints:
    Preconditions:
        - Caller must supply a track-like object with:
            * an iterable attribute `bars` whose elements are valid inputs for _bar2musicxml.
            * if instrument-based clef mapping is desired, `track.instrument` must be truthy and expose a string attribute `clef`; otherwise, no clef is inserted.
        - The module must define the helper function _bar2musicxml in the same namespace; otherwise the call will fail.
    Postconditions:
        - The returned xml.dom.minidom.Element represents a <part> element:
            * part.getAttribute("id") == str(id(track))
            * child elements correspond to the sequence of bar nodes returned by _bar2musicxml, each with a "number" attribute in ascending 1-based order
            * if a clef was determined, each <attributes> element in each bar node contains a <clef> child with <sign> and <line> text nodes populated according to the mapping rules

## Side Effects:
    - No external I/O is performed (no file, network, or stdout/stderr operations).
    - Local DOM state: the function creates a new xml.dom.minidom.Document and several DOM Elements; these are returned (part element) or attached to that Document; no global state is modified.
    - Uses built-in id(track) to compute the "id" attribute value — this leaks object identity into the XML string but does not mutate the track.

## Clef mapping logic (from instrument.clef.lower()):
    - "treble" -> sign: "G", line: "2"
    - "bass" -> sign: "F", line: "4"
    - "french" -> sign: "G", line: "1"
    - "baritone" -> sign: "F", line: "3"
    - "subbass" -> sign: "F", line: "5"
    - "alto" -> sign: "C", line: "3"
    - "tenor" -> sign: "C", line: "4"
    - "mezzo-soprano" -> sign: "C", line: "2"
    - "soprano" -> sign: "C", line: "1"
    - Matching is substring-based and case-insensitive (the function checks whether those keywords appear in instrument.clef.lower()).
    - If none of the keywords match, no clef element is inserted.

## Control Flow:
flowchart TD
    Start["Start: call _track2musicxml(track)"]
    Start --> CreateDoc["Create Document() and <part> element"]
    CreateDoc --> SetID["Set part@id = str(id(track))"]
    SetID --> CheckInstrument{"track.instrument truthy?"}
    CheckInstrument -- Yes --> DetermineClef["Inspect instrument.clef.lower() and map to (sign,line)"]
    CheckInstrument -- No --> NoClef["clef = None"]
    DetermineClef --> LoopBars["Iterate over track.bars (counter starts at 1)"]
    NoClef --> LoopBars
    LoopBars --> CallBar2XML["bar = _bar2musicxml(b)"]
    CallBar2XML --> SetNumber["bar.setAttribute('number', str(counter))"]
    SetNumber --> HasClef{"clef is not None?"}
    HasClef -- Yes --> FindAttributes["attrs = bar.getElementsByTagName('attributes')"]
    FindAttributes --> ForEachAttr["for each attr in attrs: create <clef><sign>...</sign><line>...</line></clef> and append to attr"]
    HasClef -- No --> SkipClef["skip clef insertion"]
    ForEachAttr --> AppendBar["append bar to part"]
    SkipClef --> AppendBar
    AppendBar --> IncrementCounter["counter += 1"]
    IncrementCounter --> LoopBars{"more bars?"}
    LoopBars --> End["Return part element"]

## Examples:
- Typical usage scenario (described in prose):
    1. Prepare a Track-like object with a sequence of bar objects accessible at `.bars`. Each bar must be compatible with the module-scoped helper `_bar2musicxml` (i.e., the helper must accept a bar and return an xml.dom.minidom Element representing a MusicXML bar).
    2. Optionally attach an instrument object to `track.instrument` with a textual `clef` attribute when you want automatic clef insertion (e.g., "Treble", "alto voice", "BASS clef").
    3. Call the function to obtain the <part> element. Integrate that element into a larger MusicXML Document by importing or adopting nodes into a shared ownerDocument as required by the XML library in use.
    4. Handle potential exceptions by validating `track.bars` is iterable and that `_bar2musicxml` is available before calling.

Notes:
- This function constructs DOM nodes with the minidom API; if you need the part node inserted into a different Document, use the target Document.importNode or recreate nodes under that Document to avoid ownerDocument mismatch issues.

## `mingus.extra.musicxml._composition2musicxml` · *function*

## Summary:
Converts a Composition-like object into an xml.dom.minidom Element representing a MusicXML <score-partwise> document fragment (the top-level score element) ready for inclusion in a MusicXML Document.

## Description:
This helper builds a MusicXML <score-partwise> element from a composition: it emits title/identification/encoding metadata, a <part-list> describing each track (score-part, instrument metadata, optional MIDI info), and then appends a <part> element for each track produced by the per-track converter.

Known callers within the codebase:
- No explicit callers are present in the provided snippet. This function is intended to be invoked by higher-level MusicXML export code that converts a Composition into a MusicXML file (for example, a public export routine that assembles the final Document and writes it to disk). It directly calls the module-scoped helper _track2musicxml(track) to obtain each track's <part> element.

Why this logic is extracted into its own function:
- Responsibility separation: composing the top-level score, global metadata, and part-list is a distinct concern from per-track and per-bar XML generation. Keeping composition-level assembly here allows _track2musicxml to focus on single-track conversion and lower-level helpers (e.g., _bar2musicxml) to focus on bars and notes. This makes testing, reuse, and maintenance easier.

## Args:
    comp (Composition-like): Required.
        - Type: An instance of mingus.containers.composition.Composition or a composition-like object.
        - Required attributes:
            * title: optional string-like; used for <movement-title> when truthy.
            * author: optional string-like; used to create a <creator type="composer"> child inside <identification> when truthy.
            * iteration capability: comp must be iterable; iterating yields track-like objects.
        - Each yielded track-like object `t` is expected to expose:
            * name (str-like): used as the textual content of <part-name>.
            * instrument: optional; if present, treated as an object with .name (string) and possibly .instrument_nr (int) if it's a MidiInstrument.
        - Interdependencies:
            * The function calls _track2musicxml(t). That helper must accept the provided track objects and return an xml.dom.minidom.Element (the <part> node). If _track2musicxml raises, the error propagates.

## Returns:
    xml.dom.minidom.Element
        - A DOM Element created from a fresh xml.dom.minidom.Document representing the MusicXML top-level <score-partwise> element.
        - Guarantees:
            * The returned element has tag name "score-partwise" and attribute version="2.0".
            * If comp.title is truthy, a child <movement-title> containing str(comp.title) is present as the first child.
            * An <identification> child always exists; if comp.author is truthy, it contains a <creator type="composer"> with str(comp.author).
            * An <encoding> child is included under <identification>, containing <software>mingus</software> and <encoding-date>YYYY-MM-DD</encoding-date> using today's date.
            * A <part-list> child is included listing one <score-part id="..."> per track. Each score-part contains <part-name> with the track's name and, if present, <score-instrument> with <instrument-name>. If the instrument is a MidiInstrument instance, a <midi-instrument> with <midi-channel>1</midi-channel> and <midi-program>{instrument.instrument_nr}</midi-program> is added (midi-channel is hard-coded to "1" here).
            * For each track `t`, the corresponding <part> element returned by _track2musicxml(t) is appended to the score, and its "id" attribute is set to str(id(t)).
        - Edge cases:
            * If comp yields no tracks, the returned <score-partwise> contains identification and an empty <part-list> but no <part> children.
            * If a track has no instrument, no <score-instrument> or <midi-instrument> nodes are emitted for that track.
            * If t.name is an empty string or falsy, the <part-name> will contain the string value (possibly empty) — missing attribute access will raise (see Raises).

## Raises:
    AttributeError
        - If `comp` lacks attributes accessed here (for example, if comp.title or comp.author access raises), or if a yielded track `t` does not have expected attributes (e.g., missing `name`) the attribute access will raise AttributeError.
    TypeError
        - If `comp` is not iterable, attempting to iterate over it will raise TypeError.
    Any exception raised by _track2musicxml
        - Errors from the per-track converter propagate unchanged (e.g., NameError if _track2musicxml is undefined, or DOM-related exceptions from that helper).
    (No deliberate internal exceptions are raised by this function itself.)

## Constraints:
    Preconditions:
        - Caller must pass a composition-like object that is iterable and exposes title/author attributes as described.
        - The module scope must define _track2musicxml and it must accept the track objects produced by comp.
        - The xml.dom.minidom API must be available (Document).
    Postconditions:
        - The returned Element is a detached <score-partwise> node owned by a new minidom Document created inside the function (score.ownerDocument is that Document).
        - For every track `t` yielded by comp:
            * A corresponding <score-part> entry exists in <part-list> with id == str(id(t)).
            * The appended <part> element has its id attribute set to str(id(t)).
            * If t.instrument is a MidiInstrument, there will be a <midi-program> child containing str(t.instrument.instrument_nr).

## Side Effects:
    - No external I/O: the function does not read or write files, network, or stdout/stderr.
    - Local DOM mutation: a new xml.dom.minidom.Document is created and multiple Element/Text nodes are created and returned as part of the <score-partwise> element. The returned Element's ownerDocument is that new Document.
    - Leaks Python object identity into XML: object ids are embedded using str(id(track)) and str(id(track.instrument)) for id attributes. This encodes runtime memory identity values into the XML but does not mutate the original track or instrument objects.
    - No global variables or external state are modified.

## Control Flow:
flowchart TD
    Start["Start: call _composition2musicxml(comp)"]
    Start --> CreateDoc["Create Document() and <score-partwise> element (version=2.0)"]
    CreateDoc --> TitleCheck{"comp.title truthy?"}
    TitleCheck -- Yes --> AddTitle["Create <movement-title> with str(comp.title) and append"]
    TitleCheck -- No --> SkipTitle["skip movement-title"]
    AddTitle --> CreateIdentification["Create <identification>"]
    SkipTitle --> CreateIdentification
    CreateIdentification --> AuthorCheck{"comp.author truthy?"}
    AuthorCheck -- Yes --> AddAuthor["Create <creator type='composer'> with str(comp.author) and append"]
    AuthorCheck -- No --> SkipAuthor["skip creator"]
    AddAuthor --> AddEncoding["Create <encoding>/<software>mingus</software>/<encoding-date>today and append"]
    SkipAuthor --> AddEncoding
    AddEncoding --> AppendIdentification["append <identification> to score"]
    AppendIdentification --> CreatePartList["Create <part-list> and append"]
    CreatePartList --> IterateTracks["for each track t in comp:"]
    IterateTracks --> CallTrack2XML["call _track2musicxml(t) -> part_element"]
    CallTrack2XML --> CreateScorePart["create <score-part id=str(id(t))>"]
    CreateScorePart --> AddPartName["create <part-name> with t.name and append"]
    AddPartName --> InstrumentCheck{"t.instrument truthy?"}
    InstrumentCheck -- Yes --> AddScoreInstrument["create <score-instrument id=str(id(t.instrument))> and <instrument-name>"]
    InstrumentCheck -- No --> SkipInstrument
    AddScoreInstrument --> MidiCheck{"isinstance(t.instrument, MidiInstrument)?"}
    MidiCheck -- Yes --> AddMidi["create <midi-instrument id=...> with <midi-channel>1 and <midi-program>instrument.instrument_nr and append"]
    MidiCheck -- No --> SkipMidi
    SkipInstrument --> AppendScorePart["append <score-part> to <part-list>"]
    AddMidi --> AppendScorePart
    AppendScorePart --> SetPartID["set part_element@id = str(id(t))"]
    SetPartID --> AppendPartToScore["append part_element to <score-partwise>"]
    AppendPartToScore --> NextTrack{"more tracks?"}
    NextTrack -- Yes --> IterateTracks
    NextTrack -- No --> ReturnScore["return <score-partwise> element"]
    ReturnScore --> End["End"]

## Examples:
- Typical usage (prose + minimal code-like steps):
    1. Construct a Composition, populate it with Track objects (each track having a `name` and optionally `instrument`).
    2. Ensure the module-scoped helper _track2musicxml is available and accepts those Track objects.
    3. Call _composition2musicxml(comp) to obtain the <score-partwise> Element.
    4. To serialize to a string, attach the returned element to its ownerDocument and use the Document serialization API:
        - score = _composition2musicxml(comp)
        - doc = score.ownerDocument
        - doc.appendChild(score)
        - xml_text = doc.toprettyxml(indent="  ")  # result is a string containing the full MusicXML document
    5. Handle errors: validate that comp is iterable and that each track has a `name` and acceptable structure before calling; be prepared to catch AttributeError or exceptions from _track2musicxml during conversion.

Notes:
- Because the returned element is owned by a new Document created inside the function, if you need to merge this element into another existing Document, use the target Document.importNode(...) API to adopt nodes safely.
- The function hard-codes midi-channel to "1" when emitting MIDI data for MidiInstrument instances; callers that require different channel assignment should adjust the exported DOM after conversion or provide a different exporter.

## `mingus.extra.musicxml.from_Note` · *function*

## Summary:
Create a minimal Composition containing a single provided note and return a pretty-printed MusicXML document string representing that composition.

## Description:
This is a small convenience exporter that wraps a note-like object into a new Composition, delegates adding the note to the Composition (which forwards to its selected tracks), converts the Composition into a MusicXML DOM structure, and returns the serialized, human-readable XML string.

Known callers:
- No direct callers were found in the scanned repository. This function is a public helper in the mingus.extra.musicxml module intended for callers that need a quick MusicXML representation of a single note (for example, interactive tools, tests, or small export utilities).

Why this is a separate function:
- It encapsulates the common one-liner pattern: create Composition, add a note, convert to MusicXML and serialize. Extracting it avoids duplicating the composition construction and serialization steps in client code and centralizes error propagation expectations (errors from adding the note or converting the composition propagate unchanged).

## Args:
    note (object):
        - Type: any "note-like" object accepted by Composition.add_note / Track.__add__.
        - Typical accepted forms (delegated to Track-level logic):
            * a string representing a pitch/duration (e.g., "C-4" or "C-4/4") or other string-like token the Track expects,
            * a Note instance (mingus Note-like object),
            * a NoteContainer or object exposing `notes` or `bar` semantics,
            * any object that Track.__add__ knows how to handle.
        - There is no validation in from_Note itself; the value is forwarded to Composition.add_note which in turn delegates to Track behavior. If the provided note is not acceptable to downstream code, an exception will propagate.

## Returns:
    str:
        - A pretty-printed MusicXML string produced by serializing the DOM node returned from the internal composition-to-MusicXML converter using xml.dom.minidom's toprettyxml serialization.
        - The returned XML will at minimum contain identification/encoding metadata (movement title, composer/info using Composition defaults) and a <part-list>. If the newly-created Composition contains no tracks (the default), the <part-list> will be empty and no <part> children will be present; nevertheless the returned string is still a valid MusicXML fragment/document serialization produced by the DOM serializer.
        - Example outcomes:
            * If Composition defaults are unchanged (title "Untitled"), the XML string will include a <movement-title>Untitled</movement-title>.
            * If tracks had been present and populated, the XML would include corresponding <score-part> and <part> elements — not applicable here unless the composition is modified before conversion.

## Raises:
    - Any exception raised by Composition.add_note (propagated). Possible examples:
        * IndexError: if Composition.selected_tracks contains invalid indices and the code attempts to index into tracks (not expected for a fresh Composition with no tracks, but possible if Composition implementation changes or selected_tracks are mutated externally).
        * TypeError / AttributeError: propagated from Track.__add__ if the provided note has an unexpected shape or missing attributes.
    - Any exception raised by _composition2musicxml (propagated). Possible examples:
        * AttributeError: if the converter expects attributes not present on the passed Composition-like object.
        * TypeError: if the converter tries to iterate or treat objects incorrectly.
    - Any DOM/serialization errors thrown by xml.dom.minidom when calling toprettyxml on the returned node will propagate.

## Constraints:
Preconditions:
    - No special preconditions are required by from_Note itself: it will create its own Composition instance and attempt to add the provided note.
    - If downstream conversion (Track addition or _composition2musicxml) requires certain attributes on `note` (for example, name/octave for Note-like objects), callers must provide a compatible object.

Postconditions:
    - The returned value is a unicode/str containing the pretty-printed MusicXML serialization of the DOM node produced from the Composition.
    - The input `note` object is not mutated by from_Note itself (the function creates a fresh Composition and does not retain references beyond conversion), but note: if Composition.add_note or Track.__add__ mutate the object (per their implementations), those mutations will occur and will be visible to the caller.

## Side Effects:
    - No external I/O: the function does not perform file, network, or stdout/stderr operations.
    - In-memory side-effects only:
        * Constructs a new Composition instance (transient).
        * Internally _composition2musicxml creates a new xml.dom.minidom.Document and Element nodes; those DOM objects are serialized and discarded by the caller when the returned string is used.
    - No global state or module-level mutable state is modified.

## Control Flow:
flowchart TD
    Start([Start])
    CreateComp[Create Composition instance c]
    AddNote{"Call c.add_note(note)"}
    AddNote -- selected_tracks empty --> NoTrackAdded[No tracks were selected; composition remains empty]
    AddNote -- selected_tracks non-empty --> TracksUpdated[Track objects mutated via Track.__add__]
    Convert["Call _composition2musicxml(c) -> musicxml_node"]
    Serialize["Call musicxml_node.toprettyxml() -> xml_string"]
    Return[/return xml_string/]
    Error[/propagate exception/]
    Start --> CreateComp --> AddNote
    AddNote --> Convert
    Convert --> Serialize
    Serialize --> Return
    AddNote --> Error
    Convert --> Error
    Serialize --> Error

(Decision branches denote that if the freshly-created Composition has no selected tracks, no notes will actually be appended to any track; the converter will emit an empty part-list but still return an XML serialization. Any exception during add, conversion, or serialization propagates to the caller.)

## Examples:
- Basic use (happy-path):
    xml_string = from_Note(my_note)
    # xml_string is a pretty-printed MusicXML string; handle or write it as desired.

- Example with error handling:
    try:
        xml_string = from_Note(maybe_invalid_note)
    except (AttributeError, TypeError, IndexError) as e:
        # handle or log conversion failure; underlying error details are preserved
        raise

Notes for implementers:
    - The original implementation performs exactly three steps: instantiate Composition, call add_note(note) on it, then call toprettyxml() on the DOM node returned by the composition-to-MusicXML converter. Reimplementations must preserve this call ordering and must not assume the composition contains any tracks unless tracks are explicitly added before conversion.
    - Because Composition.add_note delegates behavior to contained Track objects, this helper intentionally performs no validation of `note`. Any required validation should occur earlier in the pipeline or inside Track implementations.

## `mingus.extra.musicxml.from_Bar` · *function*

## Summary:
Converts a single Bar object into a pretty-printed MusicXML document string by wrapping the bar into a temporary Track and Composition and delegating conversion to the composition-level exporter.

## Description:
- Known callers and typical usage:
    * There are no internal callers recorded in the provided source snapshots. Typical external usage is a caller that needs a standalone MusicXML representation for a single Bar (for export, preview, testing or debugging). The function is usually invoked near the end of a conversion/export pipeline when a Bar has been constructed and the caller wants a serialized MusicXML string.
- Why this is a separate function:
    * This function encapsulates the small, repetitive task of converting a single Bar into the Composition -> MusicXML pipeline used elsewhere. It keeps the single-Bar conversion logic concise by reusing the existing composition-level converter (_composition2musicxml) rather than duplicating composition/track assembly and MusicXML emission code inline.

## Args:
    bar (object)
        - Type: A mingus.containers.bar.Bar instance or any Bar-like object.
        - Required: Yes — there is no default.
        - Semantics: The bar object is appended to a newly created Track via Track.add_bar and therefore must be compatible with Track and the downstream per-track MusicXML converter. At minimum, it must satisfy whatever invariants the Track-to-MusicXML converter expects (the function does not itself validate bar internals).

## Returns:
    str
        - A pretty-printed MusicXML document as a string. This is the return value of calling .toprettyxml() on the DOM node returned by the composition-level converter.
        - Edge cases:
            * If conversion succeeds but the composition contains no meaningful musical content, the function still returns a well-formed MusicXML string containing identification and any empty part(s) produced by the converter.
            * If the per-track or per-bar converter produces no <part> children (e.g., because the track/bar is empty), the returned XML will contain identification and an empty <part-list> and no <part> elements.

## Raises:
- Any exception raised by Track.add_bar (propagated). Possible conditions include:
    - AttributeError: if the newly created Track instance is malformed (for example, if its bars attribute is missing) such that add_bar cannot append to it (this is unlikely for a correctly-instantiated Track).
- Any exception raised by Composition.add_track (propagated). In particular:
    - mingus.containers.mt_exceptions.UnexpectedObjectError: if the object supplied to add_track does not expose a "bars" attribute. This will not occur with the function's own Track instance but can surface if Track implementation is broken.
- Any exception raised by _composition2musicxml (propagated). Typical examples:
    - AttributeError or TypeError: if the bar/track structure does not meet the expectations of the Track-to-MusicXML code path.
    - DOM-related exceptions if the minidom API fails (rare).
Note: from_Bar itself does not catch or wrap exceptions — all errors from called helpers propagate to the caller.

## Constraints:
- Preconditions:
    - The caller must provide a Bar-like object suitable for Track.add_bar and for subsequent per-track conversion. The function assumes the module-scoped helper _composition2musicxml is available and works with a Composition containing a Track whose bars list contains the provided bar.
    - The environment must provide the mingus Track and Composition implementations used here and the xml.dom.minidom API.
- Postconditions:
    - On successful return, a string containing a pretty-printed MusicXML document is returned.
    - No external state (files, global variables, network) is modified by this function.

## Side Effects:
- In-memory mutations only:
    - Creates a new Composition instance and a new Track instance and mutates those local objects (Track.add_bar appends the bar to the track; Composition.add_track appends the track to the composition and updates selected_tracks).
    - Creates DOM nodes inside the _composition2musicxml helper and uses the minidom API; these DOM nodes are local and returned as a serialized string.
- No I/O: the function performs no file, stdout, or network I/O.
- No global state or external resources are modified.

## Control Flow:
flowchart TD
    Start["Start"] --> CreateComp["Create Composition() -> c"]
    CreateComp --> CreateTrack["Create Track() -> t"]
    CreateTrack --> AddBar["t.add_bar(bar)"]
    AddBar --> AddTrack["c.add_track(t)"]
    AddTrack --> Convert["_composition2musicxml(c) -> dom_node"]
    Convert --> Serialize["dom_node.toprettyxml() -> xml_str"]
    Serialize --> Return["return xml_str"]
    Return --> End["End"]

## Examples:
- Typical end-to-end usage (prose steps):
    1. Construct or obtain a Bar instance (an object representing one musical bar) from the Mingus API or your application.
    2. Call from_Bar(bar) to get a MusicXML string:
        - xml_text = from_Bar(bar)
    3. Use xml_text for saving to disk, sending over a network, display in a UI, or further processing.
- Example with basic error handling (pseudocode):
    - Try to convert a bar and catch conversion problems:
        try:
            xml_text = from_Bar(bar)
            # proceed to write xml_text to a file or display it
        except (AttributeError, TypeError, Exception) as e:
            # handle the conversion failure (invalid bar structure, missing attributes, etc.)
            log("MusicXML conversion failed: %s" % e)

## `mingus.extra.musicxml.from_Track` · *function*

## Summary:
Creates an in-memory Composition from a single track and returns a pretty-printed MusicXML document string representing that composition.

## Description:
This convenience helper wraps a Track-like object in a new Composition, converts that Composition into a MusicXML DOM via the module helper _composition2musicxml, and returns the serialized, pretty-printed XML text.

Known callers within the codebase:
- No internal callers are present in the provided repository snapshot. This function is intended as a public exporter that library clients can call when they want to obtain a MusicXML string for a single Track instance.

Typical trigger / pipeline stage:
- Called when a caller has a Track-like object and wants an immediate MusicXML serialization (string) without manually creating a Composition and handling DOM serialization.

Why this logic is extracted into its own function:
- Encapsulates the common "wrap single track into a composition and serialize" pattern so callers do not need to recreate the same boilerplate (Composition creation, add_track, conversion, serialization).
- Keeps composition-level conversion responsibilities separate from lower-level track-to-XML conversion (_track2musicxml) and leave error handling/validation decisions to callers.

## Args:
    track (Track-like)
        - Type: An object expected to behave like mingus.containers.track.Track (i.e., have a `bars` attribute and any attributes _composition2musicxml expects such as `name` and optional `instrument`).
        - Required: yes (no default).
        - Interdependencies: The track must be acceptable to Composition.add_track (it must expose "bars") and to the per-track converter _track2musicxml (it must expose the attributes that helper reads, commonly `name` and optionally `instrument`).

## Returns:
    str (text)
        - A pretty-printed MusicXML document as produced by xml.dom.minidom.Document.toprettyxml().
        - In Python 3 this is a str; in Python 2 this will be a unicode object.
        - The returned string represents a complete, human-readable MusicXML serialization of a score containing one part corresponding to the provided track. The exact XML structure is determined by _composition2musicxml and the per-track helpers it invokes.

## Raises:
    mingus.containers.mt_exceptions.UnexpectedObjectError
        - Condition: If the provided `track` does not expose a `bars` attribute, Composition.add_track will raise this exception (the add operation validates presence of `bars`).

    AttributeError
        - Condition: If _composition2musicxml (or the helpers it calls) attempts to access track attributes that are missing (e.g., `name`), the attribute access will raise AttributeError; this propagates out of from_Track.

    TypeError
        - Condition: If _composition2musicxml expects iterable or other interfaces on the composition/track and those expectations are violated, a TypeError can be raised by those helpers and will propagate.

    Any exception raised by _composition2musicxml or the DOM API
        - Condition: Errors from the conversion/DOM creation (e.g., lower-level exceptions in _track2musicxml) are propagated unchanged.

## Constraints:
Preconditions:
    - The caller must pass a track-like object that:
        * exposes attribute `bars` (required by Composition.add_track), and
        * provides any attributes the conversion helpers require (commonly `name` and optional `instrument`).
    - The module-level helper _composition2musicxml must be available and accept the resulting Composition instance.

Postconditions:
    - A new Composition instance has been created and mutated (the provided track appended to its tracks); that Composition is local to the function and not returned.
    - A string containing the full MusicXML document (pretty-printed) is returned.
    - No external files or network resources have been modified.

## Side Effects:
    - No external I/O (no file, network, stdout/stderr).
    - Creates a new xml.dom.minidom.Document and DOM nodes; the serialized string is returned, and the in-memory DOM objects are eligible for garbage collection after the function returns (caller receives only the string).
    - No mutation is performed on the provided track object itself by this function; however, Composition.add_track stores a reference to the track inside the newly created Composition (which is local and discarded on function exit).
    - No global variables or external state are changed.

## Control Flow:
flowchart TD
    Start["Start: call from_Track(track)"]
    Start --> CreateComp["Create Composition() -> c"]
    CreateComp --> AddTrack["Call c.add_track(track)"]
    AddTrack -->|success| Convert["Call _composition2musicxml(c) -> score_element"]
    Convert --> Serialize["Call score_element.ownerDocument.toprettyxml() -> xml_str"]
    Serialize --> Return["Return xml_str"]
    AddTrack -->|UnexpectedObjectError| Raise1["UnexpectedObjectError propagated"]
    Convert -->|AttributeError/TypeError/Other| Raise2["Exception propagated"]

## Examples:
- Basic usage (happy path):
    1. Ensure you have a Track-like object t (real Track from mingus.containers.track is expected).
    2. Call:
       xml_text = from_Track(t)
    3. xml_text now contains a pretty-printed MusicXML document (as a text string) describing a score with a single part for t.

- Example with error handling:
    try:
        xml_text = from_Track(possible_track)
    except mingus.containers.mt_exceptions.UnexpectedObjectError:
        # The object did not have a 'bars' attribute — handle or report to user
        handle_invalid_track()
    except (AttributeError, TypeError) as e:
        # Conversion failed because the track lacks attributes expected by the exporter
        handle_conversion_error(e)

Notes:
- If you need to write the XML to a file, write the returned string using the desired encoding; minidom.toprettyxml may include an XML declaration and encoding hint depending on the DOM configuration and Python version, so choose the file write mode/encoding accordingly.
- For more control (e.g., combining multiple tracks into one file), create a Composition yourself, add multiple tracks, and call the lower-level composition conversion helper (_composition2musicxml) followed by manual Document handling.

## `mingus.extra.musicxml.from_Composition` · *function*

## Summary:
Return a pretty-printed MusicXML string for the given composition by converting the composition into a MusicXML <score-partwise> element and serializing it to an indented XML string.

## Description:
- Known callers within the codebase:
    - No internal callers were identified in the provided repository snapshot. This function is a public convenience exporter intended to be used by external code or higher-level export utilities to produce a MusicXML string from a Composition object.
- Typical trigger / pipeline stage:
    - Called when a user or tool needs a textual MusicXML representation of a Composition for saving to a file, sending to an external renderer, or further processing.
- Why this function exists (responsibility boundary):
    - This function is a thin serialization wrapper: it delegates the structural conversion of the Composition to the module helper _composition2musicxml (which produces a DOM Element for <score-partwise>) and handles the final serialization step (producing human-readable, indented XML). Separating conversion from serialization keeps composition-to-DOM logic isolated from formatting/IO concerns.

## Args:
    comp (Composition-like)
        - Type: Expected to be an instance of mingus.containers.composition.Composition or any "composition-like" object.
        - Required shape / attributes:
            * Must be iterable: iterating yields track-like objects.
            * May expose metadata attributes used by the conversion helper (optional but commonly present):
                - title: optional string-like (used for movement-title)
                - author: optional string-like (used for creator/composer)
            * Track-like objects yielded by comp must be acceptable to _track2musicxml (module-scoped helper); typically each track exposes:
                - name (string-like)
                - instrument (optional; possibly a MidiInstrument with .instrument_nr)
        - No default. The function will immediately pass this object to _composition2musicxml.

## Returns:
    str
        - A pretty-printed (indented) XML string produced by calling xml.dom.minidom.Node.toprettyxml() on the <score-partwise> Element produced by _composition2musicxml.
        - Represents the <score-partwise> element and all its descendant nodes (parts, part-list, identification, encoding, etc.).
        - Notes / edge cases:
            * Because the function calls .toprettyxml() on an Element node (not on a Document), the returned string contains the serialized element and its children but typically does not include an XML declaration header (e.g., <?xml version="1.0" ?>). If a full document with declaration is required, callers can either:
                - Obtain the Element via _composition2musicxml, attach it to its owner Document and call Document.toprettyxml(...), or
                - Prepend an XML declaration string before the returned fragment.
            * If the composition contains no tracks, the returned XML string will represent a <score-partwise> element with identification and an empty <part-list> but no <part> children, serialized as an indented fragment.

## Raises:
    - Any exception raised by _composition2musicxml:
        * AttributeError: If comp lacks attributes accessed by the converter (e.g., missing track.name) or a track lacks required attributes.
        * TypeError: If comp is not iterable and cannot be iterated.
        * Other exceptions that may propagate from the internal conversion logic.
    - xml.dom exceptions or TypeError from toprettyxml:
        * If the DOM nodes contain objects that cannot be converted into text nodes, or if minidom serialization fails for some reason, the underlying DOM library may raise its own exception; these propagate unchanged.
    - No additional exceptions are raised explicitly by this wrapper itself.

## Constraints:
- Preconditions:
    - _composition2musicxml must exist in the module scope and accept the same comp object; it must return an xml.dom.minidom.Element representing the <score-partwise>.
    - The caller must provide a composition-like object that is iterable and contains track objects compatible with the module's per-track converter.
    - xml.dom.minidom must be available in the runtime environment.
- Postconditions:
    - The function returns a string. It does not mutate the input composition or its tracks.
    - Any DOM objects created by _composition2musicxml remain in memory until garbage-collected; this wrapper does not write files or perform network I/O.

## Side Effects:
- No external I/O: this function does not read from or write to files, network, or stdout.
- Memory and DOM allocation: creating the DOM Elements/Document within _composition2musicxml and generating the serialized string use memory and create Python objects; no global state is mutated.
- The XML output may embed runtime object identity values (e.g., str(id(track))) if _composition2musicxml encodes object ids; this leaks memory identity values into the produced XML but does not modify the original Python objects.

## Control Flow:
flowchart TD
    A[Start: call from_Composition(comp)] --> B[Call _composition2musicxml(comp)]
    B --> C{_composition2musicxml succeeded?}
    C -- No --> D[Propagate exception -> Exit]
    C -- Yes --> E[Receive Element (score-partwise)]
    E --> F[Call Element.toprettyxml() to produce string]
    F --> G{toprettyxml succeeded?}
    G -- No --> D
    G -- Yes --> H[Return pretty-printed XML string and Exit]

## Examples:
- Basic usage (happy path):
    try:
        xml_text = from_Composition(my_composition)
        # xml_text is a string containing the indented <score-partwise> fragment
        with open("output.musicxml", "w", encoding="utf-8") as f:
            # If you need an XML declaration, write it explicitly first:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(xml_text)
    except (AttributeError, TypeError) as e:
        # Handle invalid composition shape or serialization errors
        print("Export failed:", e)

- When you need a complete Document with declaration:
    # To ensure an XML declaration is included, get the element, attach to its ownerDocument,
    # and call Document.toprettyxml(...)
    score_elem = _composition2musicxml(my_composition)           # module helper
    doc = score_elem.ownerDocument
    doc.appendChild(score_elem)
    full_xml = doc.toprettyxml(indent="  ")                     # includes XML declaration
    # full_xml is now a complete document string

Notes:
- This function is intentionally minimal: it performs conversion + formatting only and does not perform file writing or choose MIDI channels. For more control over the DOM structure or MIDI metadata, work with _composition2musicxml and the per-track helpers directly before serializing.

## `mingus.extra.musicxml.write_Composition` · *function*

## Summary:
Write a Composition to disk as a MusicXML file (plain .xml) or as a compressed MusicXML archive (.mxl). The function serializes the composition to MusicXML text (via from_Composition) and persists it to the filesystem in the requested format.

## Description:
- Known callers within this codebase:
    - No internal callers were identified in the provided repository snapshot. This is a public export utility intended to be invoked by user code or higher-level export scripts when saving a Composition to disk.
- Typical trigger / pipeline stage:
    - Called when an application or script wants to persist an in-memory Composition into a MusicXML file for interchange, engraving, or further processing. It is typically the final step in an export pipeline: composition -> MusicXML string -> write_Composition -> file on disk.
- Why this logic is extracted into its own function:
    - This function isolates the I/O and persistence concerns (file and archive creation, file-permissions attributes inside archives) from the composition-to-DOM conversion and serialization implemented by from_Composition. Keeping file writing separate allows callers to obtain the MusicXML text directly (from_Composition) for other uses (in-memory processing, network transfer) and centralizes file-format-specific behaviors (plain XML vs. .mxl archive) in one place.

## Args:
    composition (Composition-like)
        - Type: Expected to be an instance of mingus.containers.composition.Composition or a composition-like object accepted by from_Composition.
        - Constraints: Must be acceptable to from_Composition (iterable of track-like objects and optionally exposing metadata attributes used by the converter). No validation is performed here; any problems will propagate from from_Composition.
    filename (str)
        - Type: Base filename or path (string). The function appends an extension:
            * If zip is False: writes to filename + ".xml"
            * If zip is True: creates an archive filename + ".mxl" and stores an entry named filename + ".xml" inside the archive
        - Notes: The supplied filename may contain directories; behavior follows standard filesystem semantics when opening files and when writing zip entries. Do not include the extension in filename (the function always appends .xml or .mxl).
    zip (bool, default False)
        - If False (default): write a plain text XML file.
        - If True: create a compressed .mxl ZIP archive containing:
            * A META-INF/container.xml entry (pointing to filename + ".xml")
            * An entry filename + ".xml" with the MusicXML content
        - Name collision: If a file with the target name already exists, the underlying open or ZipFile constructor semantics apply (open in write mode will overwrite; ZipFile(mode='w') creates/overwrites archive).

## Returns:
    None
    - The function's observable effect is the creation (or overwriting) of a file on disk:
        * When zip is False: a text file at path filename + ".xml" containing the string returned by from_Composition.
        * When zip is True: a ZIP archive at path filename + ".mxl" containing two entries:
            - META-INF/container.xml containing a rootfile reference to filename + ".xml"
            - filename + ".xml" containing the MusicXML text
    - There is no returned value; callers should inspect the filesystem to confirm success or catch exceptions.

## Raises:
    - Any exception raised by from_Composition will propagate unchanged (for example AttributeError or TypeError if the composition is malformed for the converter).
    - IOError / OSError (including subclasses such as FileNotFoundError, PermissionError) if opening or writing the output file fails.
    - UnicodeEncodeError may occur on platforms/encodings where the MusicXML text contains characters not representable by the default text encoding when opened in text mode (the function opens files using default system encoding).
    - zipfile.BadZipFile or other zipfile-related exceptions may be raised by ZipFile or writestr if archive creation fails or invalid parameters are given.
    - Any other exceptions raised by the standard library calls used (open, zipfile.ZipFile, ZipInfo, writestr) will propagate.

## Constraints:
- Preconditions:
    - from_Composition must be present in the same module and accept the provided composition object; it must return a Unicode/text string.
    - Caller must have filesystem write permission in the directory containing filename (or appropriate path components must exist).
    - Caller should not pass a filename that is already a directory; attempting to write a file with the same name as an existing directory will raise OSError.
- Postconditions:
    - On successful return, the file filename + ".xml" (if zip is False) or the archive filename + ".mxl" (if zip is True) exists and contains the serialized MusicXML content.
    - The original composition object is not modified by this function.
    - Open file handles used by the function are closed before the function returns.

## Side Effects:
- Filesystem writes:
    - Writes a text file (filename + ".xml") when zip is False.
    - Creates a ZIP archive (filename + ".mxl") containing at minimum:
        - META-INF/container.xml with a small XML wrapper referencing filename + ".xml"
        - filename + ".xml" entry containing the MusicXML text
    - In the archive case the function sets entry external attributes to 0o660 << 16 for the created entries (file permission bits encoded in the ZIP entry metadata).
- Memory allocation:
    - Calls from_Composition, which constructs DOM objects and returns a text string; those DOM objects and the returned string are allocated in memory.
- No network I/O, no global state mutation, and no stdout/stderr writes.

## Control Flow:
flowchart TD
    Start[Start] --> CallFromComp[Call from_Composition(composition)]
    CallFromComp --> |exception| Propagate1[Propagate exception -> Exit]
    CallFromComp --> ReceiveText[Receive MusicXML text]
    ReceiveText --> IsZip{zip is True?}
    IsZip -- No --> OpenXML[Open filename + ".xml" in text write mode]
    OpenXML --> |open failed| Propagate2[Propagate IOError/OSError -> Exit]
    OpenXML --> WriteText[Write text to file]
    WriteText --> CloseFile[Close file handle]
    CloseFile --> End[Return None]
    IsZip -- Yes --> CreateZip[Create ZipFile(filename + ".mxl", mode='w', compression=ZIP_DEFLATED')]
    CreateZip --> |zip creation failed| Propagate3[Propagate zipfile error -> Exit]
    CreateZip --> MakeMeta[Create ZipInfo for META-INF/container.xml and set external_attr]
    MakeMeta --> WriteMeta[writestr(META-INF/container.xml, container_xml_text)]
    WriteMeta --> MakeEntry[Create ZipInfo for filename + ".xml" and set external_attr]
    MakeEntry --> WriteEntry[writestr(filename + ".xml", text)]
    WriteEntry --> CloseZip[Close ZipFile]
    CloseZip --> End

## Examples:
- Typical (plain XML) usage:
    1) Prepare a Composition instance with tracks and metadata.
    2) Call the function with zip=False (or omit the argument): write_Composition(my_composition, "my_song")
    3) Result: a file "my_song.xml" is created in the current working directory containing the serialized MusicXML fragment.

- Typical (.mxl archive) usage:
    1) Prepare a Composition instance.
    2) Call the function with zip=True: write_Composition(my_composition, "my_song", zip=True)
    3) Result: "my_song.mxl" is created and contains:
        - META-INF/container.xml pointing to "my_song.xml"
        - "my_song.xml" with the MusicXML content

- Error handling guidance:
    - If you need to ensure that any Unicode characters are preserved reliably on Python 3, obtain the MusicXML text with from_Composition and write the file yourself with a specified encoding:
        * Use an explicit open(filename + ".xml", "w", encoding="utf-8") when manual writing is required (note: write_Composition itself uses the default text mode without an explicit encoding).
    - Wrap calls in try/except to surface and handle I/O and conversion problems:
        * from_Composition errors indicate malformed composition objects to fix before exporting
        * OSError/PermissionError indicate filesystem or permission problems to resolve before retry

Notes:
- The function appends the extension for you; do not include ".xml" or ".mxl" in the filename argument.
- Because from_Composition returns an XML fragment (not necessarily including an XML declaration), consumers who require an XML declaration should either prepend one when writing the file themselves or, in the archive case, accept the fragment as-is (many consumers of .mxl archives tolerate the fragment form).

