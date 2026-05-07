# `tablature.py`

## `mingus.extra.tablature.begin_track` · *function*

*No documentation generated.*

## `mingus.extra.tablature.add_headers` · *function*

## Summary:
Produces a list of centered text lines that form the ASCII header section for tablature output (title, subtitle, author/email, wrapped description, and instrument tuning entries).

## Description:
This helper formats and returns the header block as a list of strings suitable for printing above tablature. It centralizes presentation logic for title, subtitle, author/email, multi-line description wrapping, and a numbered list of instrument tunings.

Known callers within the codebase:
- No direct call sites were discovered during static analysis of the local repository. The function is intended to be used by tablature rendering/export routines that need a printable header for songs or arrangements.

Why extracted into its own function:
- The function encapsulates all textual/formatting rules for tablature headers so rendering code can request a formatted header as a list of lines without duplicating wrapping, centering, and instrument-list logic. This keeps presentation concerns separate from tablature layout and I/O.

## Args:
    width (int): The target line width used for centering strings. Defaults to 80.
        - Expected to be a positive integer; values <= 0 are unsupported and will produce unpredictable layout.
    title (str): Primary title text. Defaults to "Untitled".
        - The function will convert this to a string and then to uppercase. Each character of the title is separated by two spaces when centered (the code uses "  ".join(title)), which intentionally expands the visual spacing in the result.
    subtitle (str): Optional subtitle (e.g., album or movement). Defaults to "".
        - When provided (non-empty), it is converted with str.title() and centered.
    author (str): Author/creator name. Defaults to "".
    email (str): Optional email address to show alongside author. Defaults to "".
        - If both author and email are empty, no author line is emitted. If email is provided and author is empty, the output will still show "Written by:  <email>" (author empty).
    description (str): Freeform descriptive text to appear under the author section. Defaults to "".
        - The description is split into words and wrapped into lines with an internal max width of (width - 10) characters per line (so each description line will be shorter than the centering width and then centered).
    tunings (iterable or None): Sequence of tuning objects describing instruments. Defaults to None.
        - If None, it is treated as an empty list (no instrument section).
        - Each element must be an object with attributes:
            * instrument (str): Short instrument name shown with a 1-based index (e.g., "Guitar").
            * description (str): A short description shown on the next centered line.
        - The function does not validate types of elements beyond accessing these attributes; missing attributes raise AttributeError at runtime.

## Returns:
    list[str]: Ordered lines (strings) representing the header. The list contains blank strings as separators where the function inserts spacing. The last two items in the list are always two blank strings appended before returning.

    Possible return shapes/edge cases:
    - For default call (no subtitle/author/description/tunings), returns a short list with a centered title and trailing blank lines.
    - If provided width is smaller than some composed lines, those lines will not be truncated by this function — str.center returns the original string if the supplied width <= len(the string). Long title spacing (due to "  ".join(title)) can produce lines longer than width.

## Raises:
    - No explicit exceptions are raised by the function itself.
    - Runtime exceptions that may occur:
        * AttributeError: If an item in tunings does not have .instrument or .description.
        * TypeError: If tunings is not iterable (and not None) when iterated with enumerate, or if non-string types are used where string operations are performed (though many values are coerced to str in places).
    - These are not caught internally; callers should validate inputs if necessary.

## Constraints:
    Preconditions:
    - width should be an integer greater than zero to produce meaningful centered output.
    - description and other textual parameters should be UTF-8-safe strings (or convertible to str).
    - Elements of tunings must provide .instrument and .description attributes.

    Postconditions:
    - Returns a list of strings representing a header block.
    - The returned list always ends with two blank string elements as separators.
    - If tunings is None, the function treats it as an empty list and emits no Instruments section.

## Side Effects:
    - None. The function performs pure string processing and returns the result. It does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start --> InitTunings{"tunings is None?"}
    InitTunings -- yes --> SetTuningsEmpty
    InitTunings -- no --> UseGivenTunings
    SetTuningsEmpty --> BuildResult
    UseGivenTunings --> BuildResult
    BuildResult --> ProcessTitle
    ProcessTitle --> CheckSubtitle{"subtitle != ''?"}
    CheckSubtitle -- yes --> AddSubtitle
    CheckSubtitle -- no --> AfterSubtitle
    AddSubtitle --> AfterSubtitle
    AfterSubtitle --> CheckAuthorEmail{"author != '' or email != ''?"}
    CheckAuthorEmail -- yes --> AddAuthorEmail
    CheckAuthorEmail -- no --> AfterAuthorEmail
    AddAuthorEmail --> AfterAuthorEmail
    AfterAuthorEmail --> CheckDescription{"description != ''?"}
    CheckDescription -- yes --> WrapDescriptionLoop
    CheckDescription -- no --> AfterDescription
    WrapDescriptionLoop --> AfterDescription
    AfterDescription --> CheckTunings{"tunings != []?"}
    CheckTunings -- yes --> AddInstrumentsHeader
    AddInstrumentsHeader --> ForEachTuningLoop
    ForEachTuningLoop --> AfterTunings
    CheckTunings -- no --> AfterTunings
    AfterTunings --> AppendTrailingBlankLines
    AppendTrailingBlankLines --> ReturnResult
    ReturnResult --> End

## Examples (usage sketch):
- Typical usage flow:
    1. Prepare title, subtitle, author/email, optional description.
    2. Build a list of tuning objects; each object must have attributes 'instrument' and 'description' (for example, lightweight objects created in calling code or domain model instances).
    3. Call add_headers(width=80, title="Song", subtitle="Live", author="A. Composer", email="a@example.com", description="This is a long description ...", tunings=my_tunings).
    4. Receive a list[str] and join or print each element to render the header above generated tablature.

- Example considerations and error handling:
    * If tunings may contain dictionaries rather than objects, convert them to suitable objects (or simple wrappers) before calling, because the function accesses attributes, not keys.
    * Validate width to be large enough to accommodate the visual title expansion created by the "  ".join(title) step if you want the title centered within the requested width.

## `mingus.extra.tablature.from_Note` · *function*

*No documentation generated.*

## `mingus.extra.tablature.from_NoteContainer` · *function*

*No documentation generated.*

## `mingus.extra.tablature.from_Bar` · *function*

*No documentation generated.*

## `mingus.extra.tablature.from_Track` · *function*

*No documentation generated.*

## `mingus.extra.tablature.from_Composition` · *function*

## Summary:
Render a Composition into a multi-track ASCII tablature string suitable for printing or saving.

## Description:
Converts a Composition-like object (an ordered collection of Track-like objects plus metadata) into a single string containing an ASCII tablature representation. The function:

- Collects each track's tuning (falling back to the module-scoped default_tuning when a track's get_tuning() returns falsey).
- Builds a centered textual header (title, subtitle, author/email, description, instrument list) by calling add_headers(width, ...). add_headers is a pure formatter that returns a list of strings; from_Composition extends those returned header lines into its internal result list (no I/O is performed).
- Splits the composition into horizontal blocks determined by a computed column width w = _get_width(width) and a derived blocks-per-row value bars = width / w.
- For each block, iterates tracks and for each bar within the block calls from_Bar(bar, w, tuning, collapse=False) to obtain per-bar ASCII fragments (a sequence of strings). It uses the bar fragment contents to stitch multiple bars horizontally into running ASCII rows.
- Concatenates header and track rows, inserting three blank-line separators (three empty strings) between bar-blocks, and returns the final multi-line string joined with the platform newline (os.linesep).

Known callers:
- No internal callers were identified in the provided repository snapshots. This function is a public export/printing helper intended to be called by user code or external utilities that need an ASCII tablature representation of a Composition (for display, debugging, console output, or saving to a .txt file).

Why this logic is extracted:
- Centralizes composition-level layout and flow control for tablature rendering: header generation, columnization, per-bar rendering, and multi-track stitching. This keeps per-bar rendering (from_Bar) and header formatting (add_headers) focused, reusable, and free of composition-level concerns.

## Args:
    composition (Composition-like):
        - Type: Object expected to be similar to mingus.containers.composition.Composition.
        - Requirements:
            * Iterable: iter(composition) must yield track-like objects.
            * Attribute 'tracks': composition.tracks must be a sequence/iterable of the same track-like objects and support len() and indexing (used in max([len(x) for x in composition.tracks])).
            * Each yielded track object is expected to support:
                - get_tuning() -> tuning-like-or-falsey
                - __len__() to report number of bars in the track (len(track))
                - __getitem__(index) to return a Bar-like object at the given index
        - Note: get_tuning() is called twice for each track in the normal flow — once when gathering instrument tunings for the header and again during per-block rendering.
    width (int, optional):
        - Default: 80
        - Description: Maximum output width used for layout. Passed to _get_width to compute a concrete per-block column width; also passed to add_headers to center text.
        - Constraints:
            * Should be a positive integer that makes sense for textual output.
            * Practical requirement: width and _get_width(width) should produce a bars value that is an integer accepted by range(). If bars is a float, range(bars) will raise TypeError in Python 3. To avoid this, either ensure width is chosen so width / _get_width(width) yields an integer (the default width=80 is compatible with typical _get_width behavior) or explicitly coerce bars to int before calling the function.

## Returns:
    str
        - A single string containing the ASCII tablature, including the header and per-track rows, with lines separated by os.linesep.
        - Structure:
            * Header lines (the list returned by add_headers) are extended into the result first.
            * For each horizontal block (bars per row), the function appends the ASCII rows for each track (multiple strings per track as returned by from_Bar).
            * After each full pass across all tracks for a block, the function appends three empty strings ["", "", ""] as separators before rendering the next block.
        - Edge-case behaviors:
            * If composition.tracks is empty, max([len(x) for x in composition.tracks]) will raise ValueError.
            * If add_headers returns an empty list and no bars are rendered, the function may return an empty string (os.linesep.join([]) -> "").

## Raises:
The function does not catch exceptions from its callees; the following errors can be raised due to conditions present in the source code:

    - AttributeError
        * If composition lacks the 'tracks' attribute or if any track object lacks get_tuning(), __len__(), or indexing (__getitem__).
        * If add_headers or from_Bar access attributes they expect that are missing on provided objects; those AttributeErrors propagate.
    - ValueError
        * Raised by max([len(x) for x in composition.tracks]) when composition.tracks is empty.
    - TypeError
        * If bars = width / _get_width(width) yields a non-integer (float) and that float is passed to range(), Python will raise TypeError.
        * If from_Bar returns a non-sequence or elements are not strings, concatenation/indexing operations may raise TypeError.
    - Any exception raised by from_Bar(bar, w, tuning, collapse=False) propagates unchanged (this may include domain-specific exceptions such as FingerError or RangeError if those originate downstream).

## Constraints:
Preconditions:
    - composition must be iterable and provide a composition.tracks sequence with at least one track (or the caller must handle ValueError).
    - Each track must implement get_tuning(), __len__(), and __getitem__().
    - Module-level helpers used must exist and follow expected contracts:
        * add_headers(width, ...) must return a list[str] (pure formatter).
        * _get_width(width) must return a numeric value; callers should ensure that width / _get_width(width) results in an integer usable by range().
        * from_Bar(bar, w, tuning, collapse=False) must return an indexable sequence of strings; r[1] must contain a substring "||" used as an alignment marker.
    - Module-scope default_tuning must be defined for fallback when get_tuning() returns falsey.

Postconditions:
    - On success, returns a single string with os.linesep separators representing the rendered ASCII tablature.
    - The input composition and tracks are not mutated by this function.

## Side Effects:
    - No external I/O: the function performs only in-memory computations and string assembly; it does not write files, print to stdout, or perform network I/O.
    - No mutation of global state: aside from reading module-scoped names (add_headers, _get_width, default_tuning, from_Bar), it does not change module-level variables.
    - Local allocations: builds temporary lists and a final string; memory usage grows with composition size.

## Control Flow:
flowchart TD
    Start --> BuildTunings["Iterate composition -> tun = track.get_tuning() (fallback default_tuning) -> instr_tunings list"]
    BuildTunings --> BuildHeader["Call add_headers(width, metadata..., instr_tunings) -> returns list[str] (pure)\nExtend result with returned header lines"]
    BuildHeader --> ComputeLayout["w = _get_width(width)\nbars = width / w\nmaxlen = max(len(x) for x in composition.tracks)"]
    ComputeLayout --> WhileLoop{"barindex < maxlen?"}
    WhileLoop -- Yes --> TracksLoop["for tracks in composition:"]
    TracksLoop --> InitAscii["ascii = [] ; tuning = tracks.get_tuning()"]
    InitAscii --> InnerFor{"for x in range(bars):"}
    InnerFor -- IfBar{"if barindex + x < len(tracks):"}
    IfBar -- Yes --> CallFromBar["bar = tracks[barindex+x]\nr = from_Bar(bar, w, tuning, collapse=False)\nbarstart = r[1].find('||') + 2"]
    CallFromBar --> Stitch["if notfirst: modify r[0] to insert '||' at barstart\nif ascii != []: append suffixes of r to ascii rows\nelse: ascii += r"]
    Stitch --> InnerFor
    IfBar -- No --> InnerFor
    InnerFor --> AfterTrack["After x-loop: if notfirst and ascii != [] -> pad = ascii[-1].find('||') -> append padding lines; else set notfirst=True; result += ascii"]
    AfterTrack --> NextTrack{"more tracks?"}
    NextTrack -- Yes --> TracksLoop
    NextTrack -- No --> AfterAllTracks["result += ['', '', '']\nbarindex += bars"]
    AfterAllTracks --> WhileLoop
    WhileLoop -- No --> JoinReturn["return os.linesep.join(result)"]
    JoinReturn --> End

## Examples:
- Basic usage (happy path):
    from mingus.containers.composition import Composition
    comp = Composition()
    # populate comp.tracks with Track objects and set comp.title, author, etc.
    try:
        ascii_tab = from_Composition(comp, width=80)
        with open("song_tab.txt", "w", encoding="utf-8") as f:
            f.write(ascii_tab)
    except (AttributeError, ValueError, TypeError, Exception) as e:
        print("Failed to render tablature:", e)

- Defensive caller (ensure bars is integer and tracks present):
    if not hasattr(comp, "tracks") or len(comp.tracks) == 0:
        raise ValueError("Composition must have a non-empty 'tracks' attribute")
    w = _get_width(80)
    bars = 80 / w
    # Coerce bars to int if needed to match range() expectations:
    if not isinstance(bars, int):
        bars = int(bars)
    ascii_tab = from_Composition(comp, width=80)

Notes and implementation hints:
    - from_Bar is expected to return a sequence of strings where r[1] contains "||" to mark a bar start; the function uses that index to horizontally stitch successive bars.
    - Because the source uses division (width / _get_width(width)) and passes the result to range(), ensure integer division or explicit int() conversion in a reimplementation to avoid TypeError in Python 3.
    - get_tuning() is called twice per track (header collection and rendering pass); if get_tuning() is expensive, consider caching tunings externally before calling this function.

## `mingus.extra.tablature.from_Suite` · *function*

## Summary:
Render an entire Suite (a collection of compositions plus suite-level metadata) into a single multi-composition ASCII tablature string suitable for printing or saving.

## Description:
- What it does:
  - Builds a centered header for the suite (via add_headers) and then appends the ASCII tablature representation of each composition in the suite (via from_Composition). It separates sections with horizontal rules and platform-newline separators, producing one long string ready to write to a text file or display.
- Known callers within the codebase and typical usage:
  - No internal callers were found in the repository snapshot. Typical external callers are export utilities, CLI tools, or scripts that need a text (ASCII) tablature rendering of an entire Suite (e.g., converting a set of Composition objects into a combined .txt tablature file).
  - Typical trigger: user requests to export all compositions grouped as a Suite to a single textual tablature output.
- Why this is a separate function:
  - It centralizes the suite-level assembly logic (header creation, composition iteration, section separators) so per-composition rendering (from_Composition) and header formatting (add_headers) can remain focused and reusable. This enforces a clear responsibility boundary: from_Suite orchestrates high-level sequencing and separators; it does not perform per-bar layout or header formatting itself.

## Args:
    suite (object; Suite-like)
        - Required. Expected to be a Suite or any object exposing the following attributes and behaviors:
            * title (str): Suite title (used by add_headers).
            * subtitle (str): Suite subtitle. If an empty string, the function substitutes "<N> Compositions" computed from suite.compositions.
            * author (str): Suite author (used by add_headers).
            * email (str): Suite email/contact (used by add_headers).
            * description (str): Free-form suite description (used by add_headers).
            * compositions (sequence): Used to compute len(suite.compositions) when subtitle is empty.
            * Iterable semantics: The suite must be iterable (for comp in suite yields composition-like objects). Suite iteration is used to fetch composition objects to render.
        - Behavior notes:
            * suite.subtitle is tested for exact equality with "". If it is "", the function computes subtitle = str(len(suite.compositions)) + " Compositions".
            * If any of the required attributes are missing, an AttributeError will be raised at runtime.
    maxwidth (int, optional)
        - Default: 80
        - Maximum line width used for header centering and layout decisions passed to add_headers and from_Composition. Expected to be a positive integer; values <= 0 are unsupported and may lead to odd output.

## Returns:
    str
    - A single string containing:
        * A leading platform newline, a horizontal-rule line made of '=' repeated maxwidth times, the centered header block (the list returned by add_headers joined by os.linesep), another HR line, and a blank line.
        * For each composition in suite (iteration order): the string returned by from_Composition(comp, maxwidth), followed by a newline, an HR line, and two additional newlines.
    - Examples of returned-content structure (conceptual):
        <os.linesep>
        <====...====>            # maxwidth times '='
        <os.linesep>
        <header line 1>
        <header line 2>
        ...
        <os.linesep>
        <====...====>
        <os.linesep>
        <os.linesep>
        <composition 1 tablature string>
        <os.linesep>
        <====...====>
        <os.linesep>
        <os.linesep>
        <composition 2 tablature string>
        ...
    - Edge-case returns:
        * If suite is iterable but contains no compositions, the function still returns the header block and HR delimiters; the composition loop produces nothing further.
        * If add_headers returns an empty list, os.linesep.join(...) yields an empty string and the header-area between HRs will be empty (still with HR separators).
        * If suite.subtitle is empty and suite.compositions exists but is empty, the computed subtitle will be "0 Compositions".

## Raises:
    - AttributeError
        * If suite lacks any attribute accessed by the function (title, subtitle, author, email, description, compositions) or if suite is not iterable and iteration fails.
    - Any exception propagated from callees:
        * add_headers(maxwidth, ...) — may raise AttributeError or TypeError for invalid arguments.
        * from_Composition(comp, maxwidth) — may raise ValueError, TypeError, AttributeError or domain-specific exceptions originating from per-composition rendering.
    - Notes:
        * The function does not catch exceptions from add_headers or from_Composition; they propagate unchanged to the caller.

## Constraints:
- Preconditions:
    - suite must be a Suite-like object as described in Args; in particular, suite.compositions must exist when suite.subtitle == "" because len(suite.compositions) is used.
    - maxwidth should be a positive integer; non-positive or non-integer values may produce invalid layout output or errors in downstream helpers.
    - add_headers and from_Composition must be available in the module scope and accept the argument shapes used here:
        * add_headers(width, title, subtitle, author, email, description) -> list[str]
        * from_Composition(composition, maxwidth) -> str
- Postconditions:
    - The function returns a non-mutating, aggregated string representation of the suite. It does not modify suite, its compositions, or any global state.

## Side Effects:
    - None on external state: the function performs only in-memory string processing and calls to helper functions. It does not perform filesystem or network I/O, print to stdout, or mutate the suite or its compositions.
    - Memory allocations: allocates intermediate strings and a final aggregated string whose size grows with the total rendered tablature content.

## Control Flow:
flowchart TD
    Start --> ComputeSubtitle{"suite.subtitle == '' ?"}
    ComputeSubtitle -- Yes --> SubtitleSet["subtitle = str(len(suite.compositions)) + ' Compositions'"]
    ComputeSubtitle -- No --> SubtitleSet["subtitle = suite.subtitle"]
    SubtitleSet --> CallAddHeaders["call add_headers(maxwidth, suite.title, subtitle, suite.author, suite.email, suite.description) -> list[str]"]
    CallAddHeaders --> JoinHeader["header_block = os.linesep.join(returned list)"]
    JoinHeader --> BuildTop["result = n + HR + n + header_block + n + HR + n + n"]
    BuildTop --> IterateComps["for comp in suite:"]
    IterateComps --> RenderComp["c = from_Composition(comp, maxwidth)"]
    RenderComp --> AppendComp["result += c + n + HR + n + n"]
    AppendComp --> IterateComps
    IterateComps --> Return["return result"]
    Return --> End

(where HR = "=" repeated maxwidth, and n = os.linesep)

## Examples:
- Typical usage (happy path described):
    1. Prepare a Suite instance containing multiple Composition objects and fill suite.title, suite.author, suite.email, and suite.description as desired.
    2. Call the function with the suite and optional maxwidth (default 80).
    3. The returned string can be written to a text file using a file write with encoding='utf-8' or printed to the console.

- Example outcome narrative:
    * If suite.title is "Collection", suite.subtitle is "", and suite.compositions contains 3 compositions, the header subtitle becomes "3 Compositions". The output begins with a HR line of '=' repeated maxwidth times, followed by centered header lines, and then each composition's ASCII tablature separated by HR blocks.

- Error-handling recommendations for callers:
    * Validate that the suite object exposes .compositions if suite.subtitle is empty, or ensure subtitle is explicitly set to avoid relying on compositions length.
    * Wrap the call if you want to handle per-composition rendering errors individually:
      - Iterate over suite manually and call from_Composition(comp, maxwidth) inside a try/except to skip or log problematic compositions instead of aborting the entire suite rendering.

Notes and implementation hints:
    - The function relies on add_headers returning a list of header lines; joining with os.linesep creates the header block.
    - Horizontal rule lines are generated by repeating the '=' character maxwidth times; ensure callers choose a sensible maxwidth to match terminal or file width.
    - Because the function simply iterates over suite, any custom Suite implementation must provide iteration (or __len__ and __getitem__) to be compatible.

## `mingus.extra.tablature._get_qsize` · *function*

## Summary:
Compute a non-negative integer "slot" count for tablature layout by comparing the tuning shorthand widths to an available character width and applying a fixed per-slot width heuristic.

## Description:
This small helper encapsulates the layout math used by the tablature renderer: it derives a base label width from the shorthand names of the tuning's strings, subtracts fixed padding from the available total width, divides the leftover space by a constant (4.5 characters per slot) and returns the truncated, clamped slot count.

Known callers:
- Internal consumers in the tablature rendering code that need a compact integer representing how many quarter-note (or equivalent) positions can be printed across a line, given the current viewport/line width and instrument tuning. (Call sites are within the tablature module responsible for composing textual tablature output.)

Why this function exists:
- Centralizes the layout constants and the exact arithmetic so callers can request a slot count without reimplementing padding math or duplicating the 4.5-character-per-slot heuristic. It isolates a layout decision (how many slots fit) from rendering logic.

## Args:
    tuning (object)
        - Must have an attribute `tuning` that is an iterable of string-like string-description objects.
        - Each element in `tuning.tuning` must implement a method `to_shorthand()` that returns a value acceptable to Python's max() and len(); typically a string (e.g., "E2", "A2").
        - If `tuning.tuning` is empty, max(...) will raise ValueError (see Raises).
    width (int or float)
        - Numeric total available horizontal width measured in character units (or any numeric unit consistent with subtraction and division).
        - Negative or very small widths are allowed as inputs but will generally result in a returned 0 (the function clamps negative slot counts to 0).
        - No internal coercion/validation is performed beyond Python numeric operations; callers should pass a numeric type.

Interdependencies:
- basesize is computed from len(max(names)) where names are the results of to_shorthand(); thus the result depends both on the content and the lexicographic ordering of those shorthand strings.

## Returns:
    int
        - A non-negative integer representing the number of quarter-note slots that fit into the available width after accounting for label width and fixed paddings.
        - Exact computation (mirrors the source code):
            * names = [x.to_shorthand() for x in tuning.tuning]
            * basesize = len(max(names)) + 3
            * barsize = ((width - basesize) - 2) - 1    (equivalently width - basesize - 3)
            * raw_slots = barsize / 4.5
            * returned_value = max(0, int(raw_slots))
        - Behavior on edge values:
            * If barsize <= 0, raw_slots <= 0 and the function returns 0.
            * If 0 < barsize < 4.5, raw_slots is in (0,1) and int(raw_slots) -> 0, so the function returns 0.
            * For positive raw_slots, the fractional part is discarded via int() (truncated toward zero) before clamping to >= 0.

## Raises:
    ValueError
        - If `tuning.tuning` is empty, names is empty and max(names) raises ValueError.
    AttributeError
        - If `tuning` has no attribute `tuning`, or an element of `tuning.tuning` lacks a callable `to_shorthand()`, attribute access/call will raise AttributeError.
    TypeError
        - If elements' to_shorthand() return values that are not mutually comparable by max() (e.g., mixing types) or are not compatible with len() (e.g., returning an int), a TypeError or other exception from len()/max() may be raised.

## Constraints:
Preconditions:
    - `tuning.tuning` should be a non-empty iterable of objects with a working to_shorthand() returning a string-like value.
    - `width` should be a numeric value (int or float).

Postconditions:
    - The function returns an integer >= 0.
    - No mutation of the input `tuning` or its elements occurs.
    - No external side effects occur.

## Side Effects:
    - None. The function performs only pure in-memory computation and calls to each element's to_shorthand(); it does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    A[Start: receive tuning and width] --> B{Is tuning.tuning iterable and non-empty?}
    B -- No --> C[Call max(names) -> ValueError (empty sequence) or AttributeError when accessing to_shorthand()]
    B -- Yes --> D[Compute names = [x.to_shorthand() for x in tuning.tuning]]
    D --> E[Compute basesize = len(max(names)) + 3]
    E --> F[Compute barsize = ((width - basesize) - 2) - 1]
    F --> G[Compute raw_slots = barsize / 4.5]
    G --> H[slots = int(raw_slots)   (fractional part discarded)]
    H --> I[Return max(0, slots)]
    I --> J[End]

## Examples:
Typical successful case:
- Tuning shorthand names (example): ["E4", "B3", "G3", "D3", "A2", "E2"]
    * names = ["E4","B3","G3","D3","A2","E2"]
    * Note: max(names) uses Python's lexicographic max, not longest-string selection. The chosen element depends on lexicographic ordering, e.g., max(names) might be "G3".
    * basesize = len(max(names)) + 3 = 2 + 3 = 5
- width = 80:
    * barsize = ((80 - 5) - 2) - 1 = 72
    * raw_slots = 72 / 4.5 = 16.0
    * return = max(0, int(16.0)) = 16

Small-width case (returns 0):
- Same basesize = 5, width = 10:
    * barsize = ((10 - 5) - 2) - 1 = 2
    * raw_slots = 2 / 4.5 ≈ 0.444...
    * int(raw_slots) -> 0, return = 0

Empty-tuning error:
- If tuning.tuning == [], calling this helper raises ValueError due to max([]). Callers should validate that tuning contains at least one string before calling, or catch ValueError.

Notes for callers:
- Because max(names) is lexicographic, if you intend to base basesize on the longest shorthand string, compute that explicitly (e.g., max(names, key=len)) before calling this helper or modify inputs accordingly.

## `mingus.extra.tablature._get_width` · *function*

## Summary:
Map an input maximum width to a concrete column width using a three-tier rule: unchanged for small maxima (<= 60), halved for medium maxima (61–120), and reduced to one-third for larger maxima (> 120).

## Description:
This small pure function centralizes the policy for converting a requested or available maximum width into a width value used for layout (for example, tablature column width). It is intended for internal use inside the tablature-related code in this module.

Known callers:
- No direct call sites were present in the provided snippet. In the module context, this helper is expected to be invoked by rendering/layout functions that need to compute a practical column width from an available maxwidth.

Why this is a separate function:
- Encapsulates the tiered scaling policy in one place so callers need only request the computed width rather than reproduce conditional logic.
- Makes the scaling rules easier to test and change without modifying rendering code.

## Args:
    maxwidth (int | float):
        - Numeric value describing the available or requested maximum width (unit is module-specific).
        - Expected to be a numeric type that supports comparison with numbers and division.
        - Typical values are non-negative; zero is accepted. Negative values are accepted by the implementation (see edge cases).

## Returns:
    int | float:
        - The computed width according to these exact rules implemented in the code:
            * If maxwidth <= 60: returns maxwidth
            * Else if 60 < maxwidth <= 120: returns maxwidth / 2
            * Else (maxwidth > 120): returns maxwidth / 3
        - Boundary examples:
            * maxwidth == 60 -> returns 60
            * maxwidth == 120 -> returns 60 (120 / 2)
        - The concrete Python type of the result follows the runtime's numeric division semantics (e.g., under Python 3 division produces a float).

## Raises:
    - The function does not explicitly raise exceptions.
    - If maxwidth is not a type that supports the used comparisons or division, the Python interpreter will raise a runtime exception (for example, TypeError). That exception originates from the attempted comparison or arithmetic, not from explicit checks inside this function.

## Constraints:
    Preconditions:
        - Caller should pass a numeric value for maxwidth appropriate to the module's unit system.
    Postconditions:
        - Returned value is numeric and is always <= maxwidth (truthfully reflecting scaling).
        - For maxwidth > 0, returned value will be > 0; for non-positive maxwidth, the returned value equals the input (if <= 60) or follows the same arithmetic reduction rules.

## Side Effects:
    - None. The function is pure: it performs no I/O and does not mutate external state.

## Control Flow:
flowchart TD
    Start --> CompareSmall
    CompareSmall{maxwidth <= 60?}
    CompareSmall -- Yes --> ReturnMaxwidth[/return maxwidth/]
    CompareSmall -- No --> CompareMedium
    CompareMedium{60 < maxwidth <= 120?}
    CompareMedium -- Yes --> ReturnHalf[/return maxwidth / 2/]
    CompareMedium -- No --> ReturnThird[/return maxwidth / 3/]

## Examples:
    - Example (small):
        Input: maxwidth = 50
        Output: 50
    - Example (medium):
        Input: maxwidth = 90
        Output: 45.0 (or 45 depending on interpreter and numeric types)
    - Example (large):
        Input: maxwidth = 360
        Output: 120.0 (or 120)
    - Example (boundary):
        Input: maxwidth = 120
        Output: 60.0 (120 / 2)
    - Example (invalid input):
        Input: maxwidth = "100"
        Behavior: the comparison maxwidth <= 60 raises a runtime exception (e.g., TypeError). Callers should validate or coerce inputs to numeric types before calling.

