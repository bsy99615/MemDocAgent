# `example.py`

## `print_sections` · *function*

## Summary:
Prints a hierarchical, indented listing of section titles with a short preview of each section's text to standard output by recursively traversing a sequence of section-like objects.

## Description:
Known callers within the codebase:
    - None found in the repository graph for example.print_sections.

Typical usage context:
    - Called after fetching a page's top-level sections (for example, from a Wikipedia API wrapper) when a developer or user wants a quick, human-readable overview of a page's section hierarchy and the first ~40 characters of each section's text. It is commonly invoked as a debugging or inspection helper in CLI tools, scripts, or interactive sessions.

Why this logic is extracted into its own function:
    - Responsibility boundary: encapsulates the traversal and formatted-printing of an arbitrarily nested section tree so callers can remain focused on data acquisition and higher-level processing.
    - Reusability: a single, small function provides consistent formatting and depth-aware indentation for any compatible section-like structure.
    - Separation of concerns: keeps I/O (printing) and traversal logic out of code that handles network requests, parsing, or business logic.

## Args:
    sections (iterable):
        An iterable (e.g., list, tuple, generator) of section-like objects. Each item must expose:
            - title (str): human-readable section title
            - text (str): section text; the function slices the first 40 characters (text[0:40])
            - sections (iterable): an iterable of child section-like objects (may be empty)
        Allowed values:
            - An empty iterable is allowed (function will print nothing).
            - Items may be instances from third-party libraries (for example, objects returned by a Wikipedia API) provided they present the three attributes above.
        Notes:
            - If sections is None or not iterable, iteration will raise TypeError.
            - If any item's text attribute is None or is not subscriptable, slicing will raise TypeError.
    level (int, optional):
        Integer defaulting to 0. Controls current recursion depth and the indentation level used when printing (the function prints "*" repeated (level + 1) times as a prefix).
        Allowed range:
            - Non-negative integers (0, 1, 2, ...). Negative values will still produce a string prefix but are not meaningful for depth tracking.
        Interdependencies:
            - level is an internal recursion parameter; callers normally omit it and pass only the top-level sections. When calling recursively (internal use), level increments by 1.

## Returns:
    None
    - The function does not return a value. Its purpose is to produce formatted output to standard output (stdout).
    - Edge cases:
        - When sections is empty: function completes without printing anything.
        - When any section's text is shorter than 40 characters: the slice returns the whole text (no error).
        - When an error occurs during iteration or attribute access: the function will raise the original exception (see Raises).

## Raises:
    AttributeError:
        - If an item in sections lacks any of the required attributes: title, text, or sections.
        - Trigger condition: attempting to access s.title, s.text, or s.sections on an object without that attribute.

    TypeError:
        - If sections is not iterable (e.g., None) and the for-loop attempts to iterate.
        - If s.text is None or not a sequence-like object and the slice s.text[0:40] is attempted.
        - Trigger condition examples present in code: for s in sections (if sections is not iterable) or s.text[0:40] (if s.text is not subscriptable).

    RecursionError:
        - If the nested section structure is so deep that Python's recursion limit is exceeded. The code uses direct recursion without tail-call elimination.

## Constraints:
Preconditions:
    - Caller should provide an iterable of section-like objects as described.
    - If using third-party objects (e.g., wikipediaapi objects), ensure they have populated text attributes if slicing is desired to succeed.
    - Prefer to start with level = 0 when calling for top-level sections.

Postconditions:
    - All visited sections are printed to stdout in depth-first order with one line per section containing:
        prefix (stars based on depth), section title, " - ", and up to the first 40 characters of section.text.
    - The input sections iterable and its items are not modified by this function.

## Side Effects:
    - I/O: writes to standard output via built-in print for every visited section.
    - No file, network, or database I/O is performed by this function.
    - No global variables are mutated by the function.
    - Possible interleaving with other stdout writes if used concurrently in multithreaded/multiprocess contexts.
    - Potential for deep recursion leading to RecursionError or high stack usage on deeply nested inputs.

## Control Flow:
flowchart TD
    Start[Start: call print_sections(sections, level)]
    HasSections{sections is iterable?}
    ForEach[For each s in sections]
    PrintLine[Print line: prefix, s.title, s.text[0:40]]
    HasChildren{s.sections is non-empty?}
    Recurse[Call print_sections(s.sections, level + 1)]
    NextItem[Continue to next item]
    End[End: return None]

    Start --> HasSections
    HasSections -- No --> ErrorType[TypeError raised during iteration]
    HasSections -- Yes --> ForEach
    ForEach --> PrintLine
    PrintLine --> HasChildren
    HasChildren -- Yes --> Recurse --> NextItem
    HasChildren -- No --> NextItem
    NextItem --> ForEach
    ForEach --> End

## Examples:
Typical (described steps, realistic usage):
    1) Acquire a page object and its top-level sections using a Wikipedia API client or other source that yields section-like objects.
    2) Call print_sections(top_level_sections). This will print a depth-first, indented list of sections and short previews of their text.

Error-handling pattern (recommended when input may be malformed):
    - Validate items before calling or wrap the call in try/except to preserve the calling program if malformed input appears.
    - Example handling strategy (described in prose):
        * Before calling, if you expect some sections to have missing text, iterate once to coerce or replace missing text with an empty string.
        * Alternatively, call print_sections inside a try block and catch AttributeError and TypeError; on exception, log the offending item and continue or abort gracefully using logging.exception or similar.

Notes:
    - Because the function prints directly, use it where console output is acceptable. For programmatic consumption, prefer a traversal that returns structured data rather than printing.
    - To avoid RecursionError on very deep trees, consider converting to an explicit stack-based traversal and a non-recursive printer if needed.

## `print_langlinks` · *function*

## Summary:
Prints the language links of a wikipedia-like Page object to standard output, one line per language link formatted as "<langcode>: <language> - <title>: <fullurl>".

## Description:
This function expects an object representing a page (commonly a wikipediaapi.Page) that exposes a langlinks mapping. It reads that mapping, iterates its keys in sorted order, and prints a single formatted summary line for each language link entry.

Known callers within this codebase:
    - None found in the provided repository snapshot. Typical usage is in debugging, CLI tools, or short scripts after retrieving a Page from a wikipediaapi.Wikipedia instance (i.e., immediately after fetching page data).

Why this logic is extracted into its own function:
    - Responsibility separation: isolates presentation/printing of language-link data from page-fetching and processing logic.
    - Reusability: allows multiple callers (debugging tools, REPL sessions, small utilities) to reuse a consistent, human-readable print format without repeating formatting code.
    - Testability: keeps formatting and iteration logic in one place so it can be swapped or adapted (for logging, different output formats) without changing fetching code.

## Args:
    page (object): Required. An object that must provide a .langlinks attribute.
        - Expected shape of page.langlinks: a mapping-like object (e.g., dict) where:
            * keys are language codes (strings) used for sorting and display,
            * values are objects exposing at least the attributes: language, title, fullurl.
        - No explicit type is enforced; the function will access these attributes at runtime.
        - Interdependencies: the function depends on page.langlinks.keys() being iterable and the values having the listed attributes.

## Returns:
    None
    - Behavior: The function does not return a value; it prints lines directly to standard output.
    - Possible observable outcomes:
        * If langlinks contains N entries, the function prints N lines, one per entry, in ascending lexicographic order of the keys.
        * If langlinks is empty or has no keys, the function prints nothing and simply returns.

## Raises:
    AttributeError:
        - If page is None or does not have a .langlinks attribute.
        - If an entry value (v) does not have one of the accessed attributes: v.language, v.title, or v.fullurl.
    TypeError:
        - If page.langlinks.keys() is not iterable (for example, if langlinks is None or a non-mapping object without keys()).
    Any exception raised by the __str__ or printing machinery may propagate (rare).

## Constraints:
    Preconditions:
        - The caller should pass a non-None object with a .langlinks attribute.
        - page.langlinks must be a mapping-like object with iterable keys() and values exposing language, title, and fullurl attributes.
    Postconditions:
        - After return, stdout contains one formatted line per language-link entry (unless langlinks was empty).
        - The page object is not mutated by this function.

## Side Effects:
    - I/O: Writes to standard output using the built-in print() function; no files or network operations are performed by this function itself.
    - State mutations: None. The function only reads attributes; it does not modify global variables, the page object, or external services.
    - External service calls: None (the function assumes the page object was already populated by any external calls performed elsewhere).

## Control Flow:
flowchart TD
    Start --> GetLanglinks[Get page.langlinks]
    GetLanglinks --> CheckAttr{Does page.langlinks exist and have keys()?}
    CheckAttr -- No --> RaiseAttrError[Raise AttributeError]
    CheckAttr -- Yes --> GetKeys[Obtain keys iterator via langlinks.keys()]
    GetKeys --> SortKeys[sorted(keys)]
    SortKeys --> ForEach[For each key in sorted keys]
    ForEach --> GetValue[Retrieve v = langlinks[key]]
    GetValue --> PrintLine[Print formatted line: "<key>: <v.language> - <v.title>: <v.fullurl>"]
    PrintLine --> LoopBack{More keys?}
    LoopBack -- Yes --> ForEach
    LoopBack -- No --> End[Return None]

## Examples:
Example 1 — typical usage (assuming page is a wikipediaapi.Page already fetched):
    - Context: page.langlinks contains two entries: keys "de" and "fr".
    - Call: print_langlinks(page)
    - Example output (each on its own line, order determined by sorted key order):
        de: German - Berlin: https://de.wikipedia.org/wiki/Berlin
        fr: français - Berlin: https://fr.wikipedia.org/wiki/Berlin

Example 2 — empty langlinks:
    - If page.langlinks is an empty mapping, calling print_langlinks(page) will print nothing and return None.

Example 3 — defensive usage example (error handling):
    - If you are not certain the page object is populated, guard before calling:
        If page is None or not hasattr(page, "langlinks"):
            handle_missing_page()
        else:
            print_langlinks(page)
    - This avoids AttributeError raised when page or langlinks are missing.

Notes:
    - The exact attribute names (language, title, fullurl) are accessed verbatim; if the page implementation uses different attribute names, adapt the reader or transform objects before calling this function.
    - For unit testing, provide a stub object with a langlinks mapping containing simple objects that implement the required attributes; assert printed output via captured stdout.

## `print_links` · *function*

## Summary:
Prints every link referenced from a wikipedia-like page object to standard output, one per line, with the link title followed by the printed representation of the linked object.

## Description:
This utility iterates over the page.links mapping, sorts the link titles, and prints each pair "title: value" to stdout. It is intended for quick inspection or debugging of the links contained in a page retrieved from the wikipediaapi library (or any page-like object with a links mapping).

Known callers within the codebase:
    - None discovered in the provided codebase. Typical usage is ad-hoc from REPL sessions, debugging scripts, or small utilities that display link relationships for a wikipediaapi.WikipediaPage.

Why this logic is extracted:
    - Printing the link list is a single, well-scoped responsibility that is useful in multiple places (debugging, tooling). Extracting it avoids duplicating the iteration, sorting, and printing logic and centralizes formatting decisions (the "%s: %s" pattern).

## Args:
    page (wikipediaapi.WikipediaPage or any object with .links mapping): 
        - Required. Expected to have a .links attribute that behaves like a mapping/dict where keys() yields the link titles (typically strings) and values are objects representing the linked pages.
        - Interdependencies: None. However, the function depends on .links supporting .keys() and indexing via links[title].
        - Passing None or an object without .links will raise AttributeError.

## Returns:
    None
    - Always returns None (implicit). The observable effect is printed output to stdout.
    - Edge cases:
        * If page.links is an empty mapping, the function prints nothing and returns None.
        * If page.links contains titles but the values produce side effects when converted to string, those side effects occur during printing.

## Raises:
    AttributeError:
        - If the provided page object has no .links attribute (attempt to access page.links).
    TypeError:
        - If page.links.keys() returns an object that sorted() cannot iterate over, or if keys are of types that cannot be compared to each other during sorting.
        - If page.links is not subscriptable (i.e., links[title] fails).
    Any exception raised by:
        - the sorting operation (sorted),
        - indexing into the mapping (links[title]),
        - converting a value to string (str(links[title]) as used by print formatting),
        - or the print function (rare; e.g., broken stdout) will propagate.

## Constraints:
    Preconditions:
        - page must be a non-None object with a .links attribute.
        - page.links must be a mapping-like object with keys() that yields iterable keys that are mutually comparable by sorted().
    Postconditions:
        - Standard output will contain zero or more lines, each formatted "title: value" in ascending sorted order by title.
        - The function does not modify the input page or the page.links mapping.

## Side Effects:
    - I/O: Writes text to standard output using the print() function.
    - No network, file, or database writes are performed by this function itself.
    - Note: Evaluating the printed representation of linked values (via their __str__ or __repr__) may trigger arbitrary code in those objects; any such effects are side effects of the objects' string conversion.

## Control Flow:
flowchart TD
    Start --> GetLinks[Get page.links]
    GetLinks --> LinksIsMapping{links has keys() and is subscriptable?}
    LinksIsMapping -- No --> ErrorAttributeOrType[Raise AttributeError or TypeError]
    LinksIsMapping -- Yes --> GetTitles[Call links.keys()]
    GetTitles --> SortedTitles[sorted(titles)]
    SortedTitles --> ForEach[For each title in sorted list]
    ForEach --> PrintLine[print "title: links[title]"]
    PrintLine --> NextTitle{More titles?}
    NextTitle -- Yes --> ForEach
    NextTitle -- No --> End[Return None]
    ErrorAttributeOrType --> End

## Examples:
    Example 1 — Basic usage (happy path):
        from wikipediaapi import Wikipedia
        wiki = Wikipedia('en')
        page = wiki.page('Python_(programming_language)')
        try:
            print_links(page)
        except (AttributeError, TypeError) as e:
            # handle unexpected page shape or key ordering issues
            print("Unable to print links:", e)

    Example 2 — Defensive wrapper to avoid exceptions:
        def safe_print_links(page):
            try:
                print_links(page)
            except Exception as e:
                logging.getLogger(__name__).warning("print_links failed: %s", e)

    Notes:
        - If you are building a machine-readable list instead of human-readable output, collect the items in a list/dict and return that structure rather than printing.
        - For unit tests, pass a simple mock object with a .links dict to assert printed output.

## `print_categories` · *function*

## Summary:
Prints each category title and its associated value from a page-like object's categories mapping to standard output, one per line, with titles emitted in ascending sort order.

## Description:
This small utility reads the categories attribute from the provided page object, treats it as a mapping, and prints lines formatted as "<title>: <value>" for every category title found. It performs no network or file I/O and is intended for human-readable inspection or debugging output.

Known callers within the codebase:
    - None found in this repository. Typical usage is from CLI utilities, ad-hoc scripts, or REPL-based debugging that have already retrieved a wiki Page-like object.

Why this logic is a separate function:
    - Encapsulates presentation (formatting and printing) and sorting of a page's categories so callers do not duplicate code for ordering and display. Keeps retrieval/processing code separate from display concerns.

## Args:
    page (object):
        - Required. Any object that exposes a categories attribute.
        - The categories attribute is expected to be a mapping-like object supporting:
            * a callable keys() that returns an iterable of keys,
            * indexing by key: categories[title] to obtain the associated value.
        - Typical keys are strings (category titles). Keys must be mutually comparable so that Python's sorted(...) can order them.

## Returns:
    None
    - The function always returns None and its observable effect is writing formatted lines to stdout.

## Raises:
    AttributeError
        - If the page object has no attribute named 'categories' (raised when evaluating page.categories).
        - If the categories object has no keys() attribute (raised when calling categories.keys()).
    TypeError
        - If categories.keys() does not return an iterable acceptable to sorted(), or if the keys contain types that cannot be mutually compared during sorting (sorted(...) raises TypeError).
    Any exception raised by indexing the mapping
        - The expression categories[title] may raise whatever exceptions the mapping's __getitem__ raises (for example, KeyError for mappings that no longer contain a key). Those exceptions are propagated unchanged.
    Any exception raised by converting values to string
        - The print formatting may propagate an exception raised by the value's __str__/__repr__.

## Constraints:
Preconditions:
    - Caller must pass a non-null object with a categories attribute.
    - categories.keys() must return an iterable of keys that can be sorted by Python's sorted().
Postconditions:
    - For each title yielded by sorted(categories.keys()), one line is written to stdout in the form "<title>: <value>" where <value> is the result of categories[title] stringified by Python's default formatting.
    - No return value is produced.

## Side Effects:
    - I/O: Writes to standard output using print().
    - No files, network, global variables, databases, or caches are modified by this function.

## Control Flow:
flowchart TD
    Start --> AccessCategories[Access page.categories]
    AccessCategories -->|missing attribute| RaiseAttrError[AttributeError]
    AccessCategories --> ExtractCategories[categories = page.categories]
    ExtractCategories --> CallKeys[Call categories.keys()]
    CallKeys -->|not present / not callable| RaiseAttrError2[AttributeError]
    CallKeys --> KeysIterable[Receive iterable of keys]
    KeysIterable -->|not iterable or unorderable| RaiseTypeError[TypeError from sorted()]
    KeysIterable --> SortKeys[sorted_keys = sorted(keys)]
    SortKeys --> Iterate[for each title in sorted_keys]
    Iterate --> IndexValue[value = categories[title]]
    IndexValue -->|indexing raises| PropagateIndexException[Propagate mapping exception]
    IndexValue --> PrintLine[print("%s: %s" % (title, value))]
    PrintLine --> LoopContinue{more titles?}
    LoopContinue -->|yes| Iterate
    LoopContinue -->|no| End[Return None]

## Examples:
    Example (basic):
        # Given a page-like object:
        page.categories == {'Category:A': 'A-info', 'Category:B': 'B-info'}
        Calling print_categories(page) will print:
            Category:A: A-info
            Category:B: B-info

    Example (with error handling):
        try:
            print_categories(page)
        except AttributeError:
            logging.error("Expected object with a 'categories' mapping attribute.")
        except TypeError:
            logging.error("Category titles are not sortable or categories.keys() is invalid.")
        except Exception as e:
            logging.exception("Error while printing categories: %s", e)

## `print_categorymembers` · *function*

## Summary:
Recursively prints a depth-limited, human-readable tree of Wikipedia category members, prefixing each printed line with a level-indicating asterisk string and showing each member's title and namespace number.

## Description:
Known callers within this repository:
    - None found. Intended for interactive use or small scripts that inspect or debug wikipediaapi Category Page objects.

Typical trigger / context:
    - After obtaining a Category Page via a wikipediaapi.Wikipedia instance, call this function with that page's .categorymembers mapping to print a readable, depth-limited view of the category and its subcategories.

Reason for extraction:
    - Encapsulates presentation and traversal concerns (formatting lines, iterating members, and enforcing depth limits) so client code only needs to supply the mapping and desired max depth. Keeps traversal logic separate from logic that fetches or filters category data.

## Args:
    categorymembers (mapping-like): A mapping (for example, dict) whose values are wikipediaapi Page-like objects. The function iterates over categorymembers.values() and expects each value object to have the following attributes:
        - title (str): The page title used in the printed output.
        - ns (int): Namespace number used for printing and for comparison to wikipediaapi.Namespace.CATEGORY.
        - categorymembers (mapping-like): Mapping of child members for category pages; used only when recursion descends into subcategories.
      Notes:
        - If categorymembers is None or does not implement .values(), attribute access will raise AttributeError.
        - The function does not mutate categorymembers.
    level (int, default=0): Current traversal depth used to compute the number of leading '*' characters. Defaults to 0. Intended as an internal recursion parameter; callers normally pass the default.
    max_level (int, default=2): Maximum recursion depth allowed relative to the initial level. Recursion into a member's .categorymembers occurs only when level < max_level and the member's ns equals wikipediaapi.Namespace.CATEGORY.

Interdependencies:
    - Recursion occurs only when both conditions are met: c.ns == wikipediaapi.Namespace.CATEGORY and level < max_level.
    - Supplying an initial level >= max_level will prevent any recursion.

## Returns:
    None
    - The function's observable effect is printing lines to stdout; it does not return a value.

## Raises:
    - AttributeError: Raised if categorymembers is None or lacks a values() attribute, or if a member object lacks .title, .ns, or .categorymembers when those attributes are accessed.
    - TypeError: Raised if c.ns is not an integer-compatible value when formatted with %d (this occurs at the print call).
    - RecursionError: If the category graph causes recursion deeper than Python's recursion limit (very large max_level or deeply nested categories), Python may raise RecursionError.
    - Any exceptions raised by property accessors on page objects will propagate (for example, network-backed lazy properties that raise on access).

## Constraints:
Preconditions:
    - categorymembers should be a mapping-like object with Page-like values having .title (str), .ns (int), and .categorymembers (mapping-like) when applicable.
    - For predictable formatting and comparisons, c.ns values should be integers compatible with python %d formatting and comparable to values in wikipediaapi.Namespace.
    - level and max_level should be integers; using negative values is not recommended (negative level produces fewer or no '*' characters and may be semantically confusing).

Postconditions:
    - Every value present in the provided categorymembers mapping is iterated and causes exactly one printed line during this function invocation (the function does not perform deduplication if the same Page object appears multiple times in the mapping or across sub-mappings).
    - No recursion will occur below the specified max_level relative to the initial level.
    - The function does not modify the input mappings or any Page objects.

## Side Effects:
    - Writes formatted lines to standard output using print().
    - No file, network, database, or global state mutations are performed by this function itself.
    - The Page objects passed in may have been created by code that performed network requests; this function only reads their attributes.

## Control Flow:
flowchart TD
    Start --> Iterate[Iterate over categorymembers.values()]
    Iterate --> PrintLine[Print "*"*(level+1) + " " + c.title + " (ns: " + str(c.ns) + ")"]
    PrintLine --> IsCategory{Is c.ns == wikipediaapi.Namespace.CATEGORY?}
    IsCategory -->|No| NextItem[Continue to next member]
    IsCategory -->|Yes| CheckDepth{Is level < max_level?}
    CheckDepth -->|No| NextItem
    CheckDepth -->|Yes| Recurse[Call print_categorymembers(c.categorymembers, level+1, max_level)]
    Recurse --> NextItem
    NextItem --> Iterate
    Iterate --> End[Return None]

## Examples:
Usage pattern (textual outline):
    - Obtain a wikipediaapi.Wikipedia instance and fetch a category page, e.g., via wiki.page('Category:SomeTopic').
    - Call this function with that page's .categorymembers to print a depth-limited tree of the category.

Example printed output (each line produced by one member):
    * Artificial intelligence (ns: 14)
    ** Machine learning algorithms (ns: 14)
    * Important research papers (ns: 0)

Error-handling guidance:
    - If the mapping may contain unexpected objects, validate input before calling:
        - Confirm categorymembers is a mapping and each value has the required attributes.
    - To avoid program termination on unexpected member objects, wrap the call in try/except catching AttributeError and TypeError and handle or log malformed entries.

