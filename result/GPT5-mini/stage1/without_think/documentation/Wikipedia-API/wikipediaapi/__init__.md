# `__init__.py`

## `wikipediaapi.__init__.ExtractFormat` · *class*

## Summary:
Represents the supported extraction output formats used by the library (semantic wiki text vs. HTML). It is an IntEnum so each member has an integer value suitable for comparisons and for use where integers are required.

## Description:
ExtractFormat provides a small set of named constants that callers and internal code use to signal how page extracts should be returned or parsed:
- WIKI (value 1): Request/indicate extraction in "wiki" (wikitext-like) format that preserves subsection semantics.
- HTML (value 2): Request/indicate extraction that preserves HTML tags.

When to instantiate:
- Library code that formats or parses page extracts will compare against or receive an ExtractFormat instance (for example: deciding whether to preserve HTML tags or to split into subsections).
- Callers can obtain a member via attribute access (ExtractFormat.WIKI), by integer value (ExtractFormat(1)), or by name lookup (ExtractFormat['WIKI']).

Motivation:
- Encodes a small, fixed vocabulary of output/parse modes as a typesafe enum rather than free-form strings or ints. Being an IntEnum allows direct interoperability with APIs or code paths that expect integer flags while preserving readable names.

## State:
This class does not hold per-instance mutable state beyond the standard Enum member attributes. Describe each public attribute and invariant:

- Class type: ExtractFormat (subclass of enum.IntEnum)
- Members:
    - WIKI: type ExtractFormat, .value == 1
        - Semantics: allows recognizing subsections (wikitext-style structure).
        - Example reference given in source documentation.
    - HTML: type ExtractFormat, .value == 2
        - Semantics: preserves/retrieves HTML tags.
        - Example reference given in source documentation.

Per-member attributes available at runtime:
- .name (str): the member name, e.g. "WIKI" or "HTML".
- .value (int): the integer value, 1 or 2 respectively.
- int(member) returns the integer value (because this is an IntEnum).

Valid values/constraints:
- Only the defined members (WIKI and HTML) are valid ExtractFormat instances.
- The integer domain accepted by the Enum constructor is the set {1, 2}. Other integers will produce a ValueError.

Class invariants:
- The set of members is fixed at class-definition time; no new members are introduced at runtime.
- For any ExtractFormat member m, m.name is a stable string and m.value is a stable integer.

## Lifecycle:
Creation:
- By attribute: ExtractFormat.WIKI or ExtractFormat.HTML
- From integer value: ExtractFormat(1) -> ExtractFormat.WIKI, ExtractFormat(2) -> ExtractFormat.HTML
- By name lookup: ExtractFormat['WIKI'] -> ExtractFormat.WIKI (raises KeyError for unknown names)

Typical usage order:
1. Obtain a member (attribute, value constructor, or name lookup).
2. Use it in conditionals, comparisons, or to control parsing/formatting logic.
3. When serializing for external systems, prefer .value (int) or .name (str) depending on protocol.

Destruction / cleanup:
- No explicit cleanup or resource management is required. Enum members are singletons for the lifetime of the program.

Usage notes:
- Because ExtractFormat is an IntEnum, it can be compared to integers (e.g., member == 1) and used in places that accept ints, but arithmetic or bitwise operations may return plain ints rather than Enum members — treat such operations with care.
- For JSON or other serialization that doesn't know how to encode Enums, export .value or .name explicitly.

## Method Map:
This enum defines no custom methods; the diagram below shows typical call/usage flows and conversions.

flowchart LR
    A[Acquire member] --> B{How to acquire?}
    B --> C[Attribute access: ExtractFormat.WIKI/HTML]
    B --> D[By value: ExtractFormat(1) / ExtractFormat(2)]
    B --> E[By name: ExtractFormat['WIKI']]
    C --> F[Use in logic: if fmt == ExtractFormat.WIKI]
    D --> F
    E --> F
    F --> G[Serialization: fmt.value or fmt.name]
    F --> H[Pass to APIs expecting int: int(fmt)]
    style A fill:#f9f,stroke:#333,stroke-width:1px

## Raises:
- ValueError:
    - Trigger: calling ExtractFormat(<int>) with an integer not equal to 1 or 2.
    - Example: ExtractFormat(3) raises ValueError("3 is not a valid ExtractFormat").
- KeyError:
    - Trigger: attempting name lookup with an unknown name, e.g. ExtractFormat['UNKNOWN'].
- TypeError:
    - Trigger: passing a value of an unsupported type to the Enum constructor (e.g. ExtractFormat(object())) — Python's Enum machinery may raise TypeError depending on the input.

Note: These exceptions are raised by the Enum/IntEnum base class machinery rather than by any code in ExtractFormat itself.

## Example:
# Acquire members
fmt1 = ExtractFormat.WIKI
fmt2 = ExtractFormat(2)          # -> ExtractFormat.HTML
fmt3 = ExtractFormat['WIKI']     # -> ExtractFormat.WIKI

# Use in control flow
if fmt1 == ExtractFormat.WIKI:
    # handle wiki-format extraction (subsection-aware)
    pass

# Serialization
payload = {"format": fmt2.value}   # send integer 2 to external API
log_name = fmt1.name               # "WIKI"

# Conversions and cautions
assert int(fmt1) == 1
# Bitwise or arithmetic operations may yield ints, not Enum members:
result = fmt1 | 0                  # result is an int; avoid unless intentional

## `wikipediaapi.__init__.Namespace` · *class*

## Summary:
A typed IntEnum that defines the canonical integer identifiers used by MediaWiki/Wikipedia for page namespaces (e.g., MAIN, TALK, USER, FILE, TEMPLATE). Use these members to represent and compare namespace IDs in a clear, type-safe way.

## Description:
This class centralizes the set of namespace identifiers that the MediaWiki API uses. Instantiate or reference members when parsing API responses (page metadata, links, categories), producing API requests that require namespace ids, or when storing/serializing namespace information.

Typical callers:
- Page and site model classes that read a page's namespace integer and need a stable symbolic name.
- Parsers that convert raw API JSON into typed objects.
- Business logic that branches on namespace (for example, skip FILE namespace contents).

Motivation and boundary:
- Purpose: provide a single authoritative mapping from human-readable names to MediaWiki integer namespace IDs.
- Boundary: It contains only identifiers and does not attempt to localize namespace titles, perform network lookups, or map titles to namespaces. It relies on standard Enum/IntEnum behavior for lookups and conversions.

## State:
This is an IntEnum subclass (immutable, class-level members). Each member:
- Type: Namespace (subclass of int via IntEnum)
- Behaviors:
  - .name: str, the enumerated identifier (e.g., "MAIN")
  - .value: int, the MediaWiki integer id (e.g., 0)
  - isinstance(member, int) is True (IntEnum preserves int behavior)
- Members (name = value):
  - MAIN = 0
  - TALK = 1
  - USER = 2
  - USER_TALK = 3
  - WIKIPEDIA = 4
  - WIKIPEDIA_TALK = 5
  - FILE = 6
  - FILE_TALK = 7
  - MEDIAWIKI = 8
  - MEDIAWIKI_TALK = 9
  - TEMPLATE = 10
  - TEMPLATE_TALK = 11
  - HELP = 12
  - HELP_TALK = 13
  - CATEGORY = 14
  - CATEGORY_TALK = 15
  - PORTAL = 100
  - PORTAL_TALK = 101
  - PROJECT = 102
  - PROJECT_TALK = 103
  - REFERENCE = 104
  - REFERENCE_TALK = 105
  - BOOK = 108
  - BOOK_TALK = 109
  - DRAFT = 118
  - DRAFT_TALK = 119
  - EDUCATION_PROGRAM = 446
  - EDUCATION_PROGRAM_TALK = 447
  - TIMED_TEXT = 710
  - TIMED_TEXT_TALK = 711
  - MODULE = 828
  - MODULE_TALK = 829
  - GADGET = 2300
  - GADGET_TALK = 2301
  - GADGET_DEFINITION = 2302
  - GADGET_DEFINITION_TALK = 2303

Class invariants:
- Members are unique and immutable.
- For any member m, m.value equals the specified integer and m.name equals the specified identifier.
- Only the listed integer values are valid members; any other integer is not a member and must be handled explicitly by callers.

## Lifecycle:
Creation:
- No custom constructor. Use standard Enum semantics:
  - Reference by attribute: Namespace.MAIN
  - Constructor lookup by value: Namespace(0) returns Namespace.MAIN or raises ValueError if the integer is unknown
  - Lookup by name: Namespace['MAIN'] returns Namespace.MAIN or raises KeyError if the name is not defined
- No factory methods or additional initialization required.

Usage (typical sequence):
1. Receive an integer namespace id from the MediaWiki API or persistent storage.
2. Convert to a Namespace via Namespace(integer_value). If ValueError occurs, handle it (unknown/future namespace).
3. Use the Namespace member for comparisons, switch logic, or serialization (use member.value to get the original integer).
4. Optionally iterate over Namespace to enumerate supported values (list(Namespace)).

Destruction / cleanup:
- None required. Enum members are singletons at class level and have no resources to free.

## Method Map:
flowchart LR
    API_INT[API returns integer namespace id] --> CHECK{Is integer defined in Namespace?}
    CHECK -- yes --> TO_ENUM[Namespace(integer) succeeds -> member]
    CHECK -- no --> ERROR[Namespace(integer) raises ValueError]
    TO_ENUM --> USE[Use member in comparisons / logic / serialize via member.value]
    NAME_LOOKUP[Lookup by name: Namespace['NAME']] -->|valid name| TO_ENUM
    NAME_LOOKUP -->|invalid name| KEYERR[raises KeyError]
    ATTR_ACCESS[Attribute access: Namespace.NAME] -->|valid| TO_ENUM
    ATTR_ACCESS -->|invalid| ATTRERR[raises AttributeError]

(Note: the class provides no custom methods; this map shows standard IntEnum usage and lookup paths.)

## Raises:
- ValueError
  - When calling Namespace(<int>) with an integer that is not one of the defined member values.
  - Typical trigger: parsing a page namespace integer that originates from a wiki with different namespaces or a newer/future namespace id.
- KeyError
  - When performing a name lookup using bracket syntax: Namespace['NON_EXISTENT_NAME'].
- AttributeError
  - When attempting attribute access with a non-existent member name using dot syntax: Namespace.NON_EXISTENT_NAME.
(These are the standard behaviors of Python's Enum/IntEnum; the class itself defines no custom raise conditions.)

## Example:
- Scenario: validating whether a page is in the main article namespace.
  1. Receive page metadata with integer field 'ns' (e.g., 0).
  2. Resolve the integer to a Namespace member: Namespace(ns).
     - If Namespace(ns) returns a member, proceed.
     - If it raises ValueError, handle as an unknown namespace (log, ignore, or surface the error).
  3. Compare resolved member with Namespace.MAIN to decide behavior (e.g., process only main-namespace pages).
  4. When persisting or calling APIs, use member.value to get the integer id to send/stash.

Implementation hints:
- To reimplement: subclass IntEnum and declare each member exactly as shown with its integer value.
- Preserve exact names and values to maintain compatibility with MediaWiki numeric ids.
- Do not add side-effecting methods on the enum; keep it a pure mapping of identifiers to integers.

## `wikipediaapi.__init__.namespace2int` · *function*

## Summary:
Return a numeric namespace id when given a Namespace enum member; otherwise leave the input unchanged (pass-through).

## Description:
A minimal helper that centralizes the conversion policy for namespace values: if the input is an instance of the Namespace IntEnum, the function extracts and yields its integer .value; for any other input the function performs no conversion and returns the input as-is.

Known callers and typical usage contexts:
- No direct call-sites were present in the provided snapshot. Intended callers include:
  - Code preparing parameters for MediaWiki API requests (where 'ns' expects an integer).
  - Parsers/serializers that accept either typed Namespace members or raw integers and must produce an integer id for persistence or API calls.
  - Business logic that accepts mixed input types for convenience and needs a single place to normalize enum-to-int conversion.

Why this is a separate function:
- It encapsulates the single responsibility of converting a typed Namespace member to its primitive integer id without imposing validation or other coercions on other input types. This avoids repeating isinstance checks throughout the codebase and documents the intended lightweight conversion policy in one place.

## Args:
    namespace (WikiNamespace)
        - Expected forms:
            * A Namespace IntEnum member (the function will return namespace.value).
            * An integer already representing a MediaWiki namespace id (the function will return the integer unchanged).
        - Notes:
            * The concrete alias/name WikiNamespace was not available in the provided snapshot; the implementation treats Namespace instances specially and treats any other input as already-correct (no type enforcement is performed).
            * There is no default value.

## Returns:
    int
        - Declared return type: int (per the function signature).
        - Actual behavior:
            * If namespace is an instance of Namespace, the function returns namespace.value, which is an int (guaranteed).
            * Otherwise, the function returns the original namespace argument unchanged; callers should therefore not assume the return is an int unless they guarantee the input was a Namespace or an int.
        - Edge cases:
            * If a non-int, non-Namespace object (e.g., None or string) is supplied, that same object is returned unchanged. This may violate the declared type hint at runtime and will likely cause downstream type errors if consumers assume an int.

## Raises:
    - The function itself does not raise any exceptions.
    - Downstream errors may occur if callers assume the return is always an int but pass invalid inputs.

## Constraints:
    Preconditions:
        - Best practice: pass either a Namespace member or an integer.
        - If callers must enforce type correctness, validate input before calling or validate the return value after calling.

    Postconditions:
        - If input was a Namespace member, the return is guaranteed to be an int equal to that member's .value.
        - If input was not a Namespace member, the return equals the original input (no guarantees on type or value).

## Side Effects:
    - None. The function is pure and has no I/O or external state changes.

## Control Flow:
flowchart TD
    Start([Start: receive namespace])
    Start --> CheckEnum{isinstance(namespace, Namespace)?}
    CheckEnum -- Yes --> ReturnEnum[Return namespace.value (int)]
    CheckEnum -- No --> ReturnPass[Return namespace (unchanged)]
    ReturnEnum --> End([End])
    ReturnPass --> End

## Examples:
- Enum input (recommended usage):
  - Context: converting a typed enum before sending to an API.
  - Input: Namespace.MAIN
  - Outcome: yields the integer 0 (the Namespace.MAIN .value). Callers can safely pass this result into API parameters that expect an int.

- Integer input (pass-through convenience):
  - Context: caller already has a numeric namespace id from another source.
  - Input: 14
  - Outcome: the function yields 14 unchanged; no extra conversion occurs.

- Defensive usage when caller may receive unknown types:
  - Best practice: verify or coerce to int explicitly when the downstream code requires an int.
  - Example pattern (described in prose):
    * Validate before calling: ensure value is int or Namespace; if string, attempt to parse to int or raise a TypeError.
    * Or validate after calling: result = namespace2int(value); if not isinstance(result, int): raise TypeError('namespace id must be int or Namespace')

Implementation note:
- The implementation is intentionally minimal:
  - If isinstance(namespace, Namespace): return namespace.value
  - Else: return namespace
- Reimplement exactly this logic to maintain compatibility with callers that rely on the pass-through behavior.

## `wikipediaapi.__init__.Wikipedia` · *class*

## Summary:
A thin, stateful wrapper around the MediaWiki HTTP API that manages an HTTP session, request defaults, and high-level helpers to construct page objects and fetch page data (extracts, info, links, categories, backlinks, langlinks, category members).

## Description:
Wikipedia encapsulates network configuration and parsing choices required to interact with a particular language edition of Wikipedia (or any MediaWiki instance whose API endpoint follows the standard pattern). Typical usage:
- Create one Wikipedia instance per configuration (language, user agent, optional proxies or other requests parameters).
- Use Wikipedia.page (alias article) to obtain a WikipediaPage object for a title and then call Wikipedia methods (extracts, info, links, langlinks, categories, backlinks, categorymembers) to populate fields of that WikipediaPage or to retrieve related PagesDict mappings.

Responsibilities:
- Maintain a requests.Session with default headers and request-level kwargs (timeout, proxies, etc.).
- Centralize API request logic (_query) and common result handling (_common_attributes).
- Provide higher-level convenience methods that map to specific MediaWiki API "query" modules and convert raw JSON into WikipediaPage and related objects by delegating to _build_* helpers.

Boundaries:
- This class does not implement the page model; it constructs and returns WikipediaPage and WikipediaPageSection instances. The exact shape of those classes is expected by this class (WikipediaPage has attributes like title, language, and internal containers such as _attributes, _summary, _links, etc.).
- It does not provide a close() API; it relies on session.close() in __del__ and normal garbage collection for cleanup.

## State:
Public/important attributes created by __init__:
- language (str)
    - Type: str
    - Value: lowercased, whitespace-trimmed language code used to select the API host (e.g., "en", "fr").
    - Constraint: must be non-empty after strip() or __init__ raises AssertionError.
    - Invariant: used to build endpoints like "https://{language}.wikipedia.org/w/api.php".

- extract_format (ExtractFormat)
    - Type: ExtractFormat enum member
    - Purpose: controls how extracts are interpreted and parsed (WIKI or HTML).
    - Invariant: several internal parsing paths (e.g., _build_extracts, _create_section) branch on this attribute.

- _session (requests.Session)
    - Type: requests.Session
    - Purpose: long-lived HTTP session used for all API GET requests.
    - Behavior: headers are updated with default headers constructed in __init__ (including a required User-Agent). The session is closed in __del__ if present.

- _request_kwargs (Dict[str, Any])
    - Type: dict
    - Purpose: stored kwargs passed to requests.Session.get on each request (defaults to {"timeout": 10.0} unless overridden in constructor).
    - Notes: contains user-supplied requests parameters (proxies, verify, etc.). Values are passed through unchanged to requests.

Module-level / external values referenced (must exist in the module):
- USER_AGENT (str)
    - Purpose: module-level identifier appended to the supplied user_agent header in parentheses. __init__ appends " (" + USER_AGENT + ")" to the User-Agent header.
    - Constraint: must be a string.

- RE_SECTION (mapping)
    - Purpose: a mapping keyed by ExtractFormat used by _build_extracts to find section heading regex patterns for parsing page extracts. _build_extracts calls re.finditer(RE_SECTION[self.extract_format], extract["extract"]).

- log (logger)
    - Purpose: the module-level logger used for informational messages about requests and creation of the Wikipedia instance. (The code issues log.info calls.)

- PagesDict (type alias)
    - Purpose: logical return type for methods that map page titles to WikipediaPage instances (e.g., links, langlinks, categories). Expected to be a mapping from str to WikipediaPage.

- WikipediaPage and WikipediaPageSection (classes)
    - Purpose: models representing pages and page sections created and populated by this class' methods. Several helper methods call their constructors and populate their internal attributes (e.g., _attributes, _links, _categories, _summary, _section_mapping).

## Lifecycle:
Creation:
- Signature:
    - user_agent: str (required) — must be provided and result in a 'User-Agent' header longer than 5 characters; otherwise an AssertionError is raised.
    - language: str = "en" — trimmed and lowercased; must be non-empty after stripping.
    - extract_format: ExtractFormat = ExtractFormat.WIKI — choose parsing/format behavior (WIKI vs HTML).
    - headers: Optional[Dict[str, Any]] = None — base headers to use; if provided, must be a dict with optional 'User-Agent' key.
    - **kwargs: forwarded to requests.Session.get calls (default timeout 10.0 is set if not supplied).
- Behavior:
    - Ensures kwargs.setdefault("timeout", 10.0).
    - Builds default_headers from headers or {} and ensures a 'User-Agent' entry exists (user-supplied user_agent is set if present).
    - Validates the final used_user_agent (must exist and length > 5) or raises AssertionError instructing to provide a proper user agent per Wikimedia policy.
    - Appends the module USER_AGENT in parentheses to the header value.
    - Creates and stores a requests.Session in self._session and updates its headers with default_headers.
    - Stores request-level kwargs in self._request_kwargs.

Usage:
- Typical sequence:
    1. Instantiate: wiki = Wikipedia(user_agent="myapp/1.0", language="en")
    2. Get a page handle: page = wiki.page("Python_(programming_language)")
    3. Fetch summary text (wiki.extracts(page, exsentences=2)), or fetch metadata (wiki.info(page)), or related pages (wiki.links(page), wiki.langlinks(page), wiki.categories(page), wiki.backlinks(page), wiki.categorymembers(page)).
    4. The above methods call _query to perform HTTP requests, then pass JSON to builder helpers (_build_extracts, _build_info, _build_links, etc.) which populate page internal structures and return the requested data.

- Important behaviors to note:
    - Methods that accept **kwargs for API parameters merge those kwargs with required parameters for the specific API call. The implementation sets used_params = kwargs and then used_params.update(params) where params is the function's required parameters; as implemented, values from params will overwrite any same-named keys in kwargs.
    - Several methods transparently follow MediaWiki API continuation: when the JSON contains a "continue" key, the method repeatedly updates the continuation parameter (e.g., plcontinue, blcontinue, cmcontinue) and queries again, concatenating results across pages.
    - When a page is not found, many query handlers detect a page id of "-1" in the returned pages map and set page._attributes["pageid"] = -1 (and either return an empty mapping or the page object depending on the method).

Destruction / cleanup:
- __del__ closes the requests.Session when the Wikipedia instance is garbage-collected (if _session exists). There is no explicit close() method or context-manager support in the class; callers wanting deterministic shutdown should explicitly delete the instance or let the interpreter clean it up.

## Method Map:
flowchart LR
    Init[Wikipedia.__init__] --> Session[create requests.Session and update headers]
    Init --> StateSet[store language, extract_format, _request_kwargs]
    Page[page / article] --> WikipediaPageCtor[WikipediaPage(self, title, ns, language)]
    Extracts[extracts(page, **kwargs)] --> PrepareParams[merge kwargs with query params]
    PrepareParams --> _query[_query(page, params)]
    _query --> HTTP[session.get(base_url, params=params, **_request_kwargs)]
    HTTP --> JSON[r.json() -> raw JSON]
    JSON --> _common_attributes[_common_attributes(raw['query'], page)]
    JSON --> Builder[_build_extracts/_build_info/_build_links/_build_langlinks/_build_categories/_build_categorymembers/_build_backlinks]
    Links[links] --> ContinuationLoop{while 'continue' in raw} --> _query (loop)
    Backlinks[backlinks] --> ContinuationLoop2{while 'continue' in raw} --> _query (loop)
    CategoryMembers[categorymembers] --> ContinuationLoop3{while 'continue' in raw} --> _query (loop)
    Builder --> Return[return mapped data or populated page]
    style Init fill:#e8f3ff,stroke:#333,stroke-width:1px

Notes:
- Builders create and populate WikipediaPage and WikipediaPageSection instances and set page._attributes and other internal containers (e.g., _links, _langlinks, _categories, _categorymembers, _backlinks, _summary, _section_mapping).

## Raises:
Explicit raises visible in code:
- __init__:
    - AssertionError if the final User-Agent header is missing or shorter than or equal to 5 characters. Message instructs consumers to specify a proper user agent per Wikimedia policy.
    - AssertionError if the provided language (after strip().lower()) is empty.

Implicit/propagated exceptions callers must handle:
- requests.exceptions.RequestException (or its subclasses): network errors, timeouts, connection errors that may be raised by self._session.get(...).
- ValueError / JSONDecodeError: r.json() can raise when the response is not valid JSON.
- TypeError / AttributeError: if callers pass objects that are not of expected types (e.g., page argument missing expected attributes like title or language), the code may raise attribute errors or type errors during execution.
- ValueError / KeyError from downstream constructors: builder functions construct WikipediaPage instances and may raise if provided constructor arguments are invalid (depends on WikipediaPage implementation).

Behavioral edge cases:
- When the API indicates a non-existent page, many methods detect page id "-1" (string) in the returned pages mapping and set page._attributes["pageid"] = -1 before returning an empty mapping or the page.
- Methods that accept **kwargs for API parameters will have the final query parameters be the union of kwargs and the method's required params, with the required params taking precedence (i.e., they overwrite same-named keys in kwargs).

## Example:
Instantiation and simple usage examples (illustrative):

- Basic construction:
    Provide a descriptive user-agent string (must be longer than 5 chars). The USER_AGENT module constant is appended automatically.

    wiki = Wikipedia(user_agent="myapp-bot/1.2 (myemail@example.com)", language="en")

    # Get a page object (no network I/O at construction of page object itself)
    page = wiki.page("Python_(programming_language)")

    # Fetch short extract (summary) using the stored extract_format and default timeout
    summary = wiki.extracts(page, exsentences=2)

- Using request-level kwargs (proxies, verify):
    wiki = Wikipedia(user_agent="mybot/2.0", proxies={"http": "http://proxy:3128"}, timeout=20.0)

- Fetching links with automatic continuation:
    page = wiki.page("Artificial_intelligence")
    links = wiki.links(page)  # returns a mapping title -> WikipediaPage, automatically follows plcontinue tokens if the API returns them

Notes for implementers re-creating this component:
- Ensure the module defines USER_AGENT (string), RE_SECTION (regex patterns keyed by ExtractFormat), the logger variable log, and the WikipediaPage / WikipediaPageSection classes with the minimal attributes and constructors expected here.
- Preserve exact parameter merging semantics in methods that accept **kwargs (used_params = kwargs; used_params.update(params)) and the continuation loops that update params with the API-provided continuation tokens.
- Maintain the assertion checks described above for User-Agent length and non-empty language.

### `wikipediaapi.__init__.Wikipedia.__init__` · *method*

## Summary:
Initializes the Wikipedia client instance: validates and normalizes inputs, configures HTTP headers and timeout defaults, creates a requests.Session, and stores request options and extraction format on the object.

## Description:
This constructor is called when a consumer or internal code instantiates a Wikipedia object (i.e., when a developer calls Wikipedia(...)). It performs parameter validation and performs one-time setup needed for all subsequent API calls made through the instance (session creation, header configuration, and storing request kwargs).

Why this logic is its own method:
- Object construction contains multiple responsibilities (validation, normalization, network-client setup and configuration) that must be performed once and consistently for every Wikipedia instance; keeping them grouped in __init__ centralizes that initialization logic and prevents duplication across methods that perform API calls.

Known callers / lifecycle stage:
- Called by external users of the library when they create a client instance (e.g., wiki = Wikipedia(user_agent="...")).
- There are no internal callers that re-run __init__; it is invoked once per instance at construction time.

## Args:
    user_agent (str):
        HTTP User-Agent string to identify the caller to Wikimedia servers.
        - Required: The code performs a length check and will reject very short or missing values.
        - Expected: a non-empty string; practically must be longer than 5 characters to pass the guard.
        - Purpose: used to set the "User-Agent" HTTP header (and will be appended with the library's USER_AGENT).

    language (str, optional):
        Language code used to target a specific Wikipedia site (default "en").
        - Behavior: trimmed of surrounding whitespace and lowercased before storage.
        - Must not be empty after strip(); otherwise object construction fails.

    extract_format (ExtractFormat, optional):
        Enum value controlling how extracts are interpreted/parsed (default ExtractFormat.WIKI).
        - Stored on the instance as self.extract_format and used by methods that parse page extracts.

    headers (Optional[Dict[str, Any]], optional):
        Optional dictionary of HTTP headers to send with every request.
        - If provided, this dict is used (by reference) as the base headers and WILL be mutated:
            * A "User-Agent" key may be set via setdefault if missing.
            * The library appends " (USER_AGENT)" to the User-Agent header string.
        - If not provided, a fresh internal dict is used.

    **kwargs:
        Additional request options forwarded to requests.Session.get (stored on the instance).
        - A default timeout of 10.0 seconds is applied via kwargs.setdefault("timeout", 10.0) if not present.
        - These kwargs are stored as self._request_kwargs and used for all HTTP requests from the instance.

## Returns:
    None
    - As a constructor, it does not return a value; it configures the instance in place.

## Raises:
    AssertionError:
        - If no sufficiently long User-Agent is available after combining the provided user_agent and headers:
            Condition: not (used_user_agent and len(used_user_agent) > 5)
            Effect: raises with a message asking to specify a user agent per Wikimedia policy.
        - If the normalized language string is empty:
            Condition: language.strip().lower() == ""
            Effect: raises with a message asking to specify language.

## State Changes:
Attributes READ:
    - None of self.<attr> fields are read during initialization.

Attributes WRITTEN / created:
    - self.language (str): set to language.strip().lower().
    - self.extract_format (ExtractFormat): set to the extract_format argument.
    - self._session (requests.Session): new requests.Session() instance created and assigned.
    - self._request_kwargs (dict): the kwargs dict (with default timeout applied) stored for later HTTP requests.

Other observable instance mutations:
    - The session's headers are updated with the computed default_headers via self._session.headers.update(default_headers).

## Constraints:
Preconditions:
    - The caller must provide either:
        * a user_agent argument (non-empty), or
        * a headers dict containing a sufficiently long "User-Agent" value.
    - After trimming, the language parameter must not be empty.

Postconditions:
    - If the constructor returns normally (no exception):
        * self.language exists and is the trimmed, lowercased language code.
        * self.extract_format is assigned to the instance.
        * self._session is a live requests.Session with headers that include a "User-Agent" which starts with the provided user_agent (or provided header value) and has the library USER_AGENT appended in parentheses.
        * self._request_kwargs is a dict containing at least a "timeout" key (defaulted to 10.0 if not provided by caller).

## Side Effects:
    - Mutates the passed headers dict (if provided):
        * The constructor may call default_headers.setdefault("User-Agent", user_agent) and then append the module USER_AGENT string, thereby modifying the caller's headers dict in-place.
    - Creates a requests.Session object and updates its headers (no network requests are made during construction).
    - Logs an informational line via the module logger (log.info) indicating configured language, user-agent and extract format.
    - May raise AssertionError (synchronous control-flow exception) if validation checks fail.

## Implementation notes / edge cases to preserve:
    - The code asserts that the effective "User-Agent" string is present and longer than 5 characters; this prevents the subsequent concatenation from failing and enforces Wikimedia policy guidance.
    - The constructor appends the module-level USER_AGENT string in parentheses to the effective "User-Agent"; ensure USER_AGENT exists in the module scope when reimplementing.
    - kwargs.setdefault("timeout", 10.0) is applied before storing the dict; the instance stores the same dict object (with defaults applied) to use when making requests.
    - Do not perform network calls in __init__; only create and configure the session. Subsequent calls use self._session.get with self._request_kwargs.

### `wikipediaapi.__init__.Wikipedia.__del__` · *method*

## Summary:
If a requests.Session object exists on the instance, calls its close() to release underlying network resources during object finalization.

## Description:
This destructor is invoked by Python's object finalization (for example, when the garbage collector destroys the instance or an explicit del is used). It performs a minimal cleanup step: if the instance has a _session attribute and that attribute evaluates to True, it calls _session.close().

Known callers and invocation context:
    - The Python runtime (garbage collector / object finalization) — implicitly invoked when the instance is being finalized.
    - Client code may trigger the destructor by executing del on the instance (subject to Python's object lifetime rules).
    Typical lifecycle stage: cleanup / finalization.

Why this is a separate method:
    - Encapsulates the cleanup of the HTTP session in one place so callers or the runtime can trigger session cleanup without duplicating code.
    - Provides a safety net in case client code fails to explicitly close the session; note that __del__ is not a guaranteed timely cleanup mechanism.

## Args:
    None

## Returns:
    None

## Raises:
    - Any exception raised by self._session.close() will propagate out of this method during normal interpreter operation because there is no internal try/except.
    - Behaviour during interpreter shutdown can differ; exceptions raised at that time may be ignored, printed to stderr, or handled differently by the interpreter.

## State Changes:
    Attributes READ:
        - self._session (checked for existence with hasattr and evaluated for truthiness).
    Attributes WRITTEN:
        - None on self (the attribute is not reassigned or removed).
        - The requests.Session instance referenced by self._session is acted upon by calling its close() method, which mutates internal state of that Session (closing adapters/connection pools).

## Constraints:
    Preconditions:
        - No explicit preconditions required to call this method.
        - For expected behavior, self._session (if present) should be an object exposing a close() method (in this class, __init__ assigns requests.Session).
    Postconditions:
        - If self._session existed and supported close(), its close() method will have been invoked.
        - The _session attribute on self remains unchanged (still present and not reassigned).

## Side Effects:
    - Calls self._session.close(), which releases network resources (connection pools/adapters) managed by requests.Session.
    - No other I/O is performed by this method itself; any I/O or OS-level resource release is performed within requests.Session.close().
    - No exceptions are caught here; exceptions from close() may propagate to the caller or be handled by the interpreter depending on context.

### `wikipediaapi.__init__.Wikipedia.page` · *method*

## Summary:
Constructs and returns a new page model for the given title bound to this Wikipedia instance, optionally unquoting a percent-encoded title. This method does not modify the Wikipedia instance.

## Description:
- Known callers:
    - User code after creating a Wikipedia instance (typical lifecycle: create Wikipedia -> call page() -> call extracts/info/links/backlinks/categories/etc. with the returned page).
    - Wikipedia.article: an internal alias that calls page(...) and returns the same result.
    - Any client code that needs a WikipediaPage object pre-populated with the current Wikipedia.language (examples in-library show calling extracts(page) and other API helpers with the returned page).

- Lifecycle / context:
    - This is usually the first call a consumer makes for a particular page: obtain a WikipediaPage object and then pass it to other Wikipedia methods (extracts, info, links, etc.) to fetch content or metadata.
    - It is a factory/constructor helper that centralizes how WikipediaPage objects are created so the page always receives the correct wiki reference and language.

- Why this is a separate method:
    - Provides a concise, discoverable factory for page objects tied to this Wikipedia instance and language.
    - Keeps client code simple and avoids repeating the language and wiki reference when instantiating WikipediaPage objects.
    - Encapsulates optional unquoting of percent-encoded titles in a single place.

## Args:
    title (str): Page title as used in the Wikipedia URL or API. If unquote is True, the title will be passed through urllib.parse.unquote before constructing the page.
    ns (WikiNamespace | int, optional): Namespace identifier for the page. Default is Namespace.MAIN. Expected to be an IntEnum-like namespace value (e.g., members of Namespace).
    unquote (bool, optional): If True, percent-encoded sequences in title are unquoted (via urllib.parse.unquote) before the page object is constructed. Defaults to False.

## Returns:
    WikipediaPage: A newly constructed WikipediaPage instance bound to this Wikipedia instance.
    - The returned object's title will equal the title argument after optional unquoting.
    - The returned object's ns will equal the supplied ns argument.
    - The returned object's language will equal this Wikipedia.language.
    - If the WikipediaPage constructor raises an exception, that exception propagates to the caller (this method does not catch or convert such exceptions).

## Raises:
    - This method does not raise exceptions by itself in normal operation.
    - Exceptions raised by urllib.parse.unquote (very unlikely) or by WikipediaPage.__init__ will propagate to the caller.

## State Changes:
    Attributes READ:
        - self.language
    Attributes WRITTEN:
        - None (this method does not mutate self or any other attribute of this Wikipedia instance).

## Constraints:
    Preconditions:
        - self must be a properly initialized Wikipedia instance with a valid non-empty language attribute (the Wikipedia constructor ensures language is set).
        - title should be a str (the signature enforces this; passing other types may cause runtime TypeError in Python).
        - ns should be a namespace identifier compatible with the project's WikiNamespace/Namespace usage (typically a Namespace member or integer).

    Postconditions:
        - A new WikipediaPage instance is returned where:
            * page.title == title (after unquoting if requested)
            * page.ns == ns
            * page.language == self.language
        - The Wikipedia instance (self) remains unchanged.

## Side Effects:
    - Allocates and returns a new WikipediaPage object (memory allocation / object construction).
    - If unquote is True, calls urllib.parse.unquote on the title (pure string operation; no network I/O).
    - No network requests, file I/O, or mutation of global state are performed by this method.

### `wikipediaapi.__init__.Wikipedia.article` · *method*

## Summary:
Returns a WikipediaPage object for the given title by delegating to the page-construction routine; it does not modify the Wikipedia instance.

## Description:
This method is a thin alias that forwards the provided parameters to the object's page constructor and returns the resulting WikipediaPage. Typical callers include client code and examples that want to obtain a page object before performing lookups such as extracts(), info(), links(), categories(), etc. Example usage (from the module examples): constructing a Wikipedia instance for a language and then calling this method to obtain a page object (e.g., wiki_hi.article(title='%E0%A4%AA%E0%A4%BE...', unquote=True)).

Lifecycle stage / pipeline context:
1. Create a Wikipedia instance (initialization validates user agent and language).
2. Call article(...) to construct a WikipediaPage object for the target title.
3. Use the returned WikipediaPage with other Wikipedia methods (extracts, info, links, langlinks, etc.) which perform API requests.

Why this is a separate method:
- Backwards-compatibility / ergonomics: it provides an alternative name for the frequently-used page constructor so callers can use either article(...) or page(...). The method contains no unique logic and exists to improve API discoverability and naming preferences.

## Args:
    title (str):
        Page title as used in a Wikipedia URL. If percent-encoded and unquote is True, the underlying page constructor will decode it before creating the page object.
    ns (WikiNamespace | Namespace member, default Namespace.MAIN):
        Namespace identifier for the page. Expected to be a namespace enum/member (for example, Namespace.MAIN). The default is the main/article namespace.
    unquote (bool, default False):
        When True the underlying page() call will unquote percent-encoded titles (via urllib.parse.unquote) before constructing the WikipediaPage.

## Returns:
    WikipediaPage:
        The newly-constructed page object produced by delegating to self.page(...). The returned object represents the page identified by the title and namespace for the Wikipedia instance's language. Edge cases:
        - The method itself never returns None; it returns whatever self.page returns. If the underlying page constructor returns a WikipediaPage whose metadata indicates a missing page (for example pageid == -1 in later API calls), that is represented on the returned WikipediaPage but is not changed by this alias.

## Raises:
    Any exception raised by self.page(...):
        This method does not perform validation or exception handling itself; exceptions from the delegated page constructor propagate unchanged. Examples (originating from the page constructor or Wikipedia initialization) include:
        - AssertionError if the Wikipedia instance was not correctly constructed (for example, missing or insufficient User-Agent or language).
        - ValueError or other exceptions raised by lower-level operations invoked by self.page or by callable lookups.
    Note: this method does not raise new exceptions of its own.

## State Changes:
    Attributes READ:
        - None directly (the method does not read or mutate explicit self.<attr> fields). It does perform a method lookup for self.page to call it.
    Attributes WRITTEN:
        - None. The Wikipedia instance's attributes are not modified by this call. Any state changes occur inside the returned WikipediaPage object or inside self.page (not by this alias itself).

## Constraints:
    Preconditions:
        - self must be a fully-initialized Wikipedia instance (its constructor enforces user-agent and language sanity checks).
        - title must be a string (the method performs no type coercion).
        - ns should be a valid namespace member understood by the underlying page constructor; invalid namespace values may be handled or raise errors by that constructor.
    Postconditions:
        - A WikipediaPage object is returned (the same object that self.page(...) would return).
        - The Wikipedia instance (self) remains unchanged.

## Side Effects:
    - No network I/O is performed by this method itself. Any network activity typically happens later when using the returned WikipediaPage with methods that trigger API calls (for example, calling extracts(), info(), links(), etc.).
    - Allocates and returns a new WikipediaPage object (constructed by self.page).
    - Propagates any side effects or mutations performed by the delegated page constructor (self.page) or by subsequent use of the returned WikipediaPage.

### `wikipediaapi.__init__.Wikipedia.extracts` · *method*

## Summary:
Fetches and returns the textual extract (summary) for the given page from the MediaWiki API and records page-not-found state on the passed page object; it also updates page metadata via internal helpers.

## Description:
This method builds a query for the MediaWiki "extracts" API, issues the request through the Wikipedia instance's HTTP query helper, applies common response attributes to the page, and returns the prepared extract text.

Known callers and invocation context:
- Typical caller: user code that has a Wikipedia instance and a WikipediaPage object (example in upstream docstring shows usage like wiki.extracts(page, exsentences=1)). It is invoked at the point where a client wants a textual summary/extract of a page (presentation or data-retrieval step).
- It may be used internally by other higher-level helpers that need the page extract, but the public API usage is the primary scenario.

Why this is a dedicated method:
- It encapsulates the specific parameter preparation for the "extracts" API, the conditional handling required by the configured extract format, the API call, and the post-processing of the API response (including page attribute updates). Keeping this logic here avoids duplication and isolates the behavior so callers only supply desired extract-specific options.

## Args:
    page (WikipediaPage): The target page object whose title is used for the query. The page is expected to expose .title (string) and a mutable ._attributes mapping where metadata can be written.
    **kwargs: Additional query parameters for the MediaWiki "extracts" API. These are merged into the request parameters and are passed through to the underlying query helper. Note: the method mutates the kwargs mapping passed by the caller (see Side Effects).

Allowed/expected parameter patterns:
    - kwargs commonly includes MediaWiki "extracts" parameters such as exintro, exsentences, exlimit, explaintext, exsectionformat, etc. Behavior for exsectionformat may be influenced by this Wikipedia instance's configuration.

## Returns:
    str: The page extract returned by the API and post-processed by internal helpers. Possible return values:
      - Non-empty string: extracted summary text (format depends on instance configuration and API response).
      - Empty string (""): returned when the API indicates the page does not exist or no extract is available (this occurs when the API returns a pages entry with key "-1" or when no page extract could be built).

## Raises:
    - No exceptions are explicitly raised by this method. However, any exceptions raised by the underlying operations will propagate:
        * Exceptions from the instance's HTTP/query helper (self._query) such as network/requests-related errors.
        * Exceptions from response-processing helpers (self._common_attributes or self._build_extracts) if they raise.
    Callers should handle or let these exceptions propagate as appropriate.

## State Changes:
Attributes READ:
    - self.extract_format: used to decide whether to force plaintext/exsectionformat settings.

Attributes WRITTEN (on self):
    - None. This method does not assign to any self.<attr> fields.

Other object mutations (page-level; important side effects):
    - page._attributes["pageid"] is set to -1 when the API indicates the page was not found (pages entry key == "-1").
    - The method calls self._common_attributes(raw["query"], page) and self._build_extracts(v, page); these helpers may also modify page._attributes and other page internals (their exact mutations are performed by those helper implementations).

## Constraints:
Preconditions:
    - page.title must be a valid string suitable for the MediaWiki titles parameter.
    - page must expose a mutable mapping at page._attributes where page metadata can be stored.
    - self.extract_format should be a valid ExtractFormat member (code branches for ExtractFormat.HTML and ExtractFormat.WIKI are used).
    - The caller must expect that the kwargs mapping passed in may be mutated by this method.

Postconditions:
    - If the API indicates "page not found" (page id key "-1"), page._attributes["pageid"] is set to -1 and the method returns an empty string.
    - If a usable extract is available, the method returns the extract string produced by self._build_extracts and page attributes are updated via self._common_attributes and possibly self._build_extracts.
    - The kwargs mapping provided by the caller will have been updated (merged) with internal query params.

## Side Effects:
    - Network I/O: the method calls self._query(page, used_params) which issues the MediaWiki API request and therefore performs HTTP/network operations.
    - Mutation of caller-provided kwargs: the method assigns used_params = kwargs and then updates used_params with internal params, thus mutating the kwargs dictionary object that the caller passed in.
    - Mutates the passed page object:
        * Explicitly sets page._attributes["pageid"] = -1 when the API reports the page does not exist.
        * Invokes helpers (_common_attributes, _build_extracts) that may write additional metadata into page._attributes or alter page state.
    - No file or global external side-effects are performed directly by this method beyond the helper calls it makes.

### `wikipediaapi.__init__.Wikipedia.info` · *method*

## Summary:
Fetches MediaWiki "info" data for the provided page title, applies shared query-level attributes, and populates the page's internal attribute mapping in-place; returns the same WikipediaPage instance after mutation.

## Description:
This method:
- Builds the MediaWiki API parameters for action=query with prop=info and a comprehensive inprop list (protection, talkid, watched, watchers, visitingwatchers, notificationtimestamp, subjectid, url, readable, preload, displaytitle).
- Calls the instance HTTP helper self._query(page, params) to perform the API request and parse JSON.
- Applies common attributes from raw["query"] to the page via self._common_attributes(raw["query"], page).
- Iterates over raw["query"]["pages"] and immediately handles the first entry:
  - If the page key equals the string "-1", marks the page as missing by setting page._attributes["pageid"] = -1 and returns the page.
  - Otherwise delegates population of page._attributes to self._build_info(v, page) and returns its result.
- If no pages are present in the response (empty mapping), returns the original page unchanged.

Known callers and call context:
- Intended to be used by higher-level page-retrieval or refresh workflows in this library (for example, public routines that request a WikipediaPage's metadata). It is the dedicated internal step to obtain canonical metadata (IDs, namespace, URLs, protection and watch-related flags) for a single title.
- Placed as its own method to centralize the "info" endpoint parameter construction and the logic distinguishing a missing page ("-1") from a populated page entry.

Example usage (illustrative, not literal source):
- A page object with a title is passed in; after calling this method the page._attributes will contain API-provided metadata (or pageid == -1 if the page does not exist).

## Args:
    page (WikipediaPage):
        - Type: WikipediaPage
        - Required fields:
            * page.title (any string): the page title that will be sent to the MediaWiki API as the "titles" parameter. The method does not validate or normalize the title — whatever string is present is forwarded to the API.
            * page._attributes (mutable mapping, e.g., dict): writable mapping that will be mutated to store returned metadata.
        - No default value.

## Returns:
    WikipediaPage:
        - The same page instance passed in, after mutation.
        - Return cases:
            * Missing page: if the API includes a page entry with key "-1", the method sets page._attributes["pageid"] = -1 and returns page.
            * Normal page: returns the page after _build_info has copied all key/value pairs from the MediaWiki per-page dict into page._attributes (and _common_attributes has applied shared fields).
            * No pages returned: if raw["query"]["pages"] is empty, the original page is returned unchanged.

## Raises:
    - Any exception raised by self._query:
        * requests.exceptions.RequestException (network problems like timeouts, connection errors).
        * json.JSONDecodeError / ValueError when the response body cannot be parsed as JSON.
    - KeyError:
        * If the parsed JSON does not include the expected keys "query" or "pages", the code's raw["query"] or raw["query"]["pages"] indexing will raise KeyError.
    - AttributeError / TypeError:
        * If the supplied page object lacks required attributes (missing page.title or a writable page._attributes), or if page._attributes is not assignable, attempting to read/assign will raise AttributeError/TypeError.
    - Any exception propagated from self._build_info or self._common_attributes (for example TypeError if the per-page extract is not a mapping-like object).

## State Changes:
Attributes READ:
    - page.title: read to supply the "titles" API parameter.
    - (Indirectly) raw = self._query(...) return value is read for raw["query"] and raw["query"]["pages"].

Attributes WRITTEN:
    - page._attributes (mapping):
        * In the missing-page case, page._attributes["pageid"] is explicitly set to the integer -1.
        * In the normal case, self._build_info copies all key/value pairs from the API per-page dict into page._attributes (overwriting any existing keys with the same names). _common_attributes may also have written common keys (title, pageid, ns, redirects) before the full copy.
    - No attributes on the Wikipedia instance (self) are modified by this method.

## Constraints:
Preconditions:
    - page must be an object exposing:
        * .title (any string) — the method does not check for emptiness or sanitize the title.
        * ._attributes — a writable mapping (e.g., dict) where metadata will be stored.
    - The Wikipedia instance must expose working helpers: self._query, self._common_attributes, and self._build_info that conform to their expected contracts (see their own documentation).

Postconditions:
    - If the API returned a page key of "-1": page._attributes["pageid"] == -1.
    - If a normal per-page mapping was returned: page._attributes contains all key/value pairs from that mapping after the call.
    - If pages mapping was empty: page._attributes is left unchanged.
    - Only the first entry in raw["query"]["pages"] is processed; additional entries (if any) are ignored.

## Side Effects:
    - Network I/O: performs an HTTP request through self._query (which performs the actual GET and JSON parsing).
    - Mutates the supplied page object's internal state (page._attributes).
    - Relies on helper methods to perform logging; this method itself does not perform direct logging.
    - Behavior notes:
        * The method returns early while iterating pages.items(), so it will not aggregate or process multiple returned page entries — this is an intentional design assumption for single-title queries.
        * The method does not itself inspect or handle API-level "error" payloads present in the JSON; such payloads are surfaced via exceptions or via missing expected keys (KeyError) when indexing raw["query"].

### `wikipediaapi.__init__.Wikipedia.langlinks` · *method*

## Summary:
Fetches and returns the language links for the given page by calling the MediaWiki API and assembling the results; may update the provided page's metadata when the page is missing.

## Description:
This method issues a query to the MediaWiki API for the "langlinks" property of a page, merges user-supplied API parameters with a set of forced parameters, and returns the parsed language-links structure produced by the internal builder.

Known callers:
    - No callers discovered in the provided codebase snapshot. Typically invoked by application code or higher-level library functions when a developer requests cross-language links for a specific WikipediaPage instance.

When in the lifecycle this is called:
    - Used during data retrieval stage when a consumer needs language-specific redirects/links for an existing WikipediaPage object (after the page object has been created or populated with at least a title).

Why this is a separate method:
    - Encapsulates the exact API query parameters and the specific post-processing flow (query → normalize common attributes → build langlinks). Separating it keeps API-specific logic, pagination/defaults, and response-to-object conversion isolated and reusable.

## Args:
    page (WikipediaPage): The page whose language links are requested. The method expects:
        - page.title: a string title used as the API "titles" parameter.
        - page._attributes: a dict-like attribute used to store page metadata; the method may set page._attributes["pageid"] = -1 when the page is not found.
    **kwargs: Arbitrary keyword arguments representing additional or overriding API parameters.
        - Note: The implementation sets a base params dict and then updates it into used_params after copying kwargs. Because params are applied after kwargs, the forced parameters below will override any conflicting keys provided in kwargs.

Forced/Default API parameters (always applied and take precedence over kwargs):
    - action: "query"
    - prop: "langlinks"
    - titles: page.title
    - lllimit: 500
    - llprop: "url"

## Returns:
    PagesDict: The method returns the PagesDict value produced by the internal _build_langlinks call for the page data returned by the API.
    - If the API indicates the page is missing (pageid = "-1"), the method sets page._attributes["pageid"] = -1 and returns an empty mapping ({}).
    - If the pages collection is empty or no valid page entry is found, it returns {} (empty mapping).

Note: The concrete structure and types inside PagesDict are produced by self._build_langlinks and are not defined in this method; consumers should inspect or rely on _build_langlinks's contract for exact typing.

## Raises:
    - Any exception raised by the internal helper methods is propagated. In particular:
        - Exceptions from self._query (network, HTTP, or parsing exceptions) will bubble up.
        - Exceptions from self._common_attributes or self._build_langlinks will also propagate.
    - This method does not itself raise any new custom exceptions.

## State Changes:
Attributes READ:
    - The method does not read any direct self.<attr> fields (it calls instance methods).
    - It reads the following attributes of the provided page object:
        - page.title (used to populate the "titles" API parameter)
        - page._attributes (read implicitly when updating/setting metadata via helper methods)

Attributes WRITTEN:
    - The method does not assign to any self.<attr> fields.
    - It may modify the provided page object's attributes:
        - page._attributes["pageid"] is set to -1 when the API returns a page entry keyed by "-1".
    - The method also calls self._common_attributes(raw["query"], page), which may mutate page._attributes or other public attributes of page (behavior depends on that helper).

## Constraints:
Preconditions:
    - The page argument must have a title attribute (preferably a non-empty string). Supplying a page without a title will produce an API query with an invalid "titles" parameter and is likely to yield a missing-page result or an API error propagated from self._query.
    - The Wikipedia instance (self) must be properly initialized so that self._query can perform API requests.

Postconditions:
    - After a successful call, common page attributes will have been updated via self._common_attributes.
    - If the API indicates the page does not exist, page._attributes["pageid"] will be set to -1 and the method returns {}.
    - Otherwise, the method returns the PagesDict representation produced by self._build_langlinks for the first page entry returned by the API.

## Side Effects:
    - Network I/O: Calls self._query(page, used_params) which is expected to perform HTTP requests to the MediaWiki API (external I/O).
    - Mutates the provided page object (page._attributes) either via direct assignment in this method or via helper calls (self._common_attributes and self._build_langlinks).
    - Mutates the local kwargs dict (used_params) by inserting the forced parameters; because kwargs is a local dict created by Python for keyword arguments, this does not affect external caller state.

### `wikipediaapi.__init__.Wikipedia.links` · *method*

## Summary:
Fetches outgoing links for the provided page from the MediaWiki API, applies common page metadata to the page object, and returns the processed collection produced by the library's link-builder. If the API indicates the page does not exist, the method sets the page's pageid to -1 and returns an empty mapping.

## Description:
This method performs a MediaWiki "query" with prop=links to retrieve the links present on a single page title. Its responsibilities and behavior include:
- Preparing a default parameter set: action=query, prop=links, titles=page.title, pllimit=500.
- Merging caller-provided keyword arguments (kwargs) with those defaults such that the defaults overwrite any colliding caller-supplied keys.
- Making an initial API call via self._query(page, used_params) where used_params is the merged kwargs dictionary.
- Calling self._common_attributes(raw["query"], page) to apply common metadata from the API response to the supplied WikipediaPage instance before link extraction.
- Iterating over raw["query"]["pages"] but only processing the very first page entry encountered (the method returns inside the for-loop after the first iteration). This means if the API returns multiple page entries in the pages mapping, only the first one is used.
- Handling MediaWiki continuation: while the raw response contains a "continue" key, the method:
    - Sets params["plcontinue"] to the continuation token from the raw response.
    - Calls self._query(page, params) using the original params dict (note: this intentionally uses params, not the merged used_params).
    - Extends the in-memory v["links"] list by adding raw["query"]["pages"][k]["links"] from the continuation response.
  Important behavior: continuation requests use the original params dict rather than the merged used_params, so any caller-supplied kwargs included only in the merged used_params passed in the first request will NOT be included in subsequent continuation requests.
- After exhausting continuation tokens, returning self._build_links(v, page) for the processed page object v.

Known callers:
- Intended for client code that has a Wikipedia instance and a WikipediaPage object and needs that page's outgoing links. No internal callers are visible in the provided source.

Why this is a separate method:
- Encapsulates parameter preparation, API request logic, pagination handling (MediaWiki continuation), integration with page metadata application, and conversion of raw API link lists into the library's PagesDict representation.

## Args:
    page (WikipediaPage):
        The WikipediaPage instance whose outgoing links will be fetched.
        - Required: must provide page.title (string). The method reads page.title and writes into page._attributes.
    **kwargs:
        Arbitrary keyword parameters intended for the MediaWiki query API.
        - Behavior: kwargs is used as the base dict and then updated with the method's required defaults (action, prop, titles, pllimit). Because update is called with params after used_params is set to kwargs, the method's defaults overwrite any identically named keys provided by the caller.
        - Note: caller-provided parameters present only in the merged used_params are present in the initial request but — due to continuation requests using params instead of used_params — may be absent on subsequent continuation requests.

## Returns:
    PagesDict:
        The value returned by self._build_links(v, page) for the first page object v encountered in raw["query"]["pages"] after all continuations have been applied.
        - If the API response contains a page entry with key "-1", the method sets page._attributes["pageid"] = -1 and returns an empty dict.
        - If raw["query"]["pages"] is empty or no items are processed, the method returns an empty dict.

## Raises:
    KeyError / TypeError:
        If the API response lacks expected keys (for example, raw does not contain "query" or "query" lacks "pages", or continuation responses lack expected nested keys), indexing into the response will raise KeyError or TypeError.
    Any exception raised by helper methods:
        Exceptions propagated from self._query, self._common_attributes, or self._build_links (e.g., network errors, HTTP errors, JSON parsing errors, or library-specific exceptions) will propagate out of this method.

## State Changes:
    Attributes READ:
        page.title
    Attributes WRITTEN:
        page._attributes["pageid"] (set to -1 if pages mapping contains "-1")
        Additionally, self._common_attributes(raw["query"], page) is called and may write further attributes into page._attributes; those writes happen inside that helper.
    Local mutations:
        - The method mutates its local params dict (adds/updates "plcontinue") and the local used_params dict (result of kwargs updated by defaults). These mutations are internal to the call and do not modify any caller-side variables.

## Constraints:
    Preconditions:
        - page must be an object exposing a string title attribute and a dict-like _attributes attribute that is writable.
        - self._query must accept (page, params: dict) and return a mapping following the MediaWiki query structure: raw["query"]["pages"] and, when present, raw["continue"]["plcontinue"].
    Postconditions:
        - On successful completion, the method will either return the result of self._build_links for the processed page or return an empty dict if the page does not exist or no pages were processed.
        - page will have had self._common_attributes invoked with raw["query"], and page._attributes["pageid"] will be set to -1 when the API indicates a non-existent page.

## Side Effects:
    - Network I/O: calls to self._query which perform HTTP/API requests. One initial request is made; additional requests are made if the API returns continuation tokens.
    - Mutation of the provided page object via self._common_attributes and possibly setting page._attributes["pageid"] to -1.
    - In-place extension of the raw page object v's "links" list during continuation accumulation (v["links"] is extended by links from subsequent continuation responses).
    - Important practical note for implementers: because continuation requests use the original params dict (not the merged used_params), any caller-supplied kwargs used to filter or modify the initial request may be lost during continuation; reimplementations that must preserve caller-supplied parameters across continuation requests should intentionally replicate the code's behavior if exact parity is required, or change this behavior and update callers accordingly.

### `wikipediaapi.__init__.Wikipedia.backlinks` · *method*

## Summary:
Fetches all pages that link to the given page by querying the MediaWiki backlinks API, follows pagination to accumulate results, and populates the provided page object's backlink cache before returning it.

## Description:
This method issues a MediaWiki "backlinks" query for the given WikipediaPage and handles MediaWiki's continuation flow. It:
- Constructs the required API parameters for a backlinks list query.
- Merges caller-provided keyword parameters into the initial request parameters.
- Performs an initial HTTP request via the instance's internal _query method.
- Calls _common_attributes to copy common metadata from the API response into page._attributes.
- When the API response contains a continuation block, uses the blcontinue token to fetch subsequent pages; aggregates all backlinks into a single list.
- Delegates conversion of the aggregated raw backlinks to WikipediaPage instances to _build_backlinks, which sets page._backlinks and returns the mapping.

Known callers / typical invocation context:
- Invoked by application code that has a WikipediaPage and needs to discover which pages link to it (for crawling, backlink analysis, or display features).
- Lifecycle: after obtaining a WikipediaPage instance, call wiki.backlinks(page) to populate page._backlinks and receive the mapping.

Why this is a separate method:
- Encapsulates MediaWiki-specific parameter setup, JSON structure handling, pagination/continuation semantics, and object construction. Centralizing this avoids duplicating continuation logic and keeps the public API simple.

## Args:
    page (WikipediaPage): Target page whose backlinks are requested. Required attributes used by this method:
        - title (str): page title used as bltitle in the API call.
        - language (str): language code used to construct the API endpoint (https://{language}.wikipedia.org/w/api.php).
    **kwargs: Additional MediaWiki API parameters sent with the initial request (collected into the method-local kwargs dict). Notes:
        - The implementation uses the local kwargs dict and then updates it with enforced parameters; this local dict is mutated inside the function but this does not mutate any caller-side variables (because **kwargs creates a new dict for the call).
        - Extra kwargs are applied only to the initial request. Continuation requests use the internal params dict and do not carry forward caller-provided extra keys.

## Returns:
    dict[str, WikipediaPage]: Mapping from backlink page title to a WikipediaPage instance for each page that links to the input page.
    - If the API reports no backlinks, returns an empty dict.
    - The returned dict is the same object assigned to page._backlinks by _build_backlinks.

## Raises:
    - requests.exceptions.RequestException: Propagated from the underlying HTTP GET performed in _query on network errors, timeouts, etc.
    - ValueError (json decode error): If r.json() fails to parse the response body as JSON.
    - KeyError: If the response JSON lacks expected keys accessed by this implementation:
        * Access to raw["query"] is expected; absence raises KeyError.
        * During accumulation, raw["query"]["backlinks"] is expected; absence raises KeyError.
        * If a top-level "continue" exists but raw["continue"]["blcontinue"] is missing, KeyError will be raised.
    - Any exceptions raised by _common_attributes or _build_backlinks (e.g., during WikipediaPage construction) will propagate.

## State Changes:
Attributes READ (self):
    - self._session (used by _query to perform HTTP GET).
    - self._request_kwargs (used by _query for request options like timeout/proxies).

Attributes WRITTEN (self):
    - None (the Wikipedia instance itself is not modified by this method).

Mutations to the provided page object:
    - page._attributes: updated by self._common_attributes(raw["query"], page) with any of the common response keys present (commonly "title", "pageid", "ns", "redirects").
    - page._backlinks: created/assigned by self._build_backlinks(v, page) to a dict mapping backlink titles to WikipediaPage instances. This dict is returned.

Other parameter/object mutations:
    - The method mutates its local kwargs dict (the one created by **kwargs). This does not mutate any dict object in the caller's scope.

## Constraints:
Preconditions:
    - page.title must be a non-empty string.
    - page.language must be a valid Wikipedia language code.
    - The Wikipedia instance must have an active requests.Session in self._session and configured self._request_kwargs (set by the Wikipedia constructor).

Enforced parameters and continuation behavior:
    - The method enforces these API parameters (they take precedence in the initial request and cannot be overridden by caller kwargs):
        * action = "query"
        * list = "backlinks"
        * bltitle = page.title
        * bllimit = 500
    - Implementation detail: caller-supplied kwargs are included only in the first request (used_params). Subsequent continuation requests use the local params dict (which contains only the enforced parameters and the blcontinue token), therefore custom keys from kwargs are not sent with continuation requests.

Pagination and accumulation:
    - First response stored in raw; v = raw["query"] is used as the accumulator.
    - While raw contains a top-level "continue" key, the method reads raw["continue"]["blcontinue"], sets params["blcontinue"] = that token, issues a request with params, and extends v["backlinks"] with raw["query"]["backlinks"] from the response.
    - After the loop, v contains the aggregated backlinks, which are then processed by _build_backlinks.

Postconditions:
    - On success, page._backlinks is set to the mapping of backlinks and the same mapping is returned.
    - page._attributes may be updated with common metadata from the response.

## Side Effects:
    - Network I/O: performs one or more HTTPS GET requests to https://{page.language}.wikipedia.org/w/api.php.
    - Updates the provided page object (page._attributes and page._backlinks).
    - Does not perform filesystem I/O or mutate global state outside the Wikipedia instance and the passed page object.

## Example:
    - Typical usage: call wiki.backlinks(page) after creating a WikipediaPage to retrieve and cache backlinks; the return value is the same dict stored on page._backlinks.

### `wikipediaapi.__init__.Wikipedia.categories` · *method*

## Summary:
Fetches and returns the category information for the provided page by issuing a categories query to the MediaWiki API; may update the supplied page object's attributes to reflect a missing page.

## Description:
This method constructs a MediaWiki "query&prop=categories" API request for the provided page, merges it with any caller-supplied keyword parameters, executes the request via the instance query helper, applies common page-level attribute extraction, and returns the categories data parsed by a helper.

Typical usage context:
- Invoked when a client or higher-level routine needs the set of categories associated with a WikipediaPage object (for example, during page metadata enrichment or when a user requests category information).
- It is intentionally implemented as its own method to encapsulate the API-parameter assembly, the network/query invocation, and the post-processing steps (common attribute extraction and category parsing). This keeps the logic for categories separate from other page-property methods and allows reuse of the _query/_common_attributes/_build_categories helpers.

Known callers:
- External client code or higher-level module routines that need categories for a WikipediaPage instance. (Exact callers in the codebase were not available when this documentation was produced; typical call pattern is wiki.categories(page) or page.categories() delegating to this implementation.)

## Args:
    page (WikipediaPage): A page object whose title attribute will be used to construct the API request. Must expose a string attribute `title` and support writing to `page._attributes` (dictionary-like).
    **kwargs: Arbitrary keyword parameters to include in the API query. These are merged with internal defaults (see behavior below).

Notes on parameter merging and precedence:
- The method creates an internal params mapping:
    {
        "action": "query",
        "prop": "categories",
        "titles": page.title,
        "cllimit": 500,
    }
  It then merges the caller-supplied kwargs into a variable named used_params and calls used_params.update(params).
- Because update(params) is called after binding used_params to kwargs, any keys present in params overwrite keys supplied via kwargs. In other words, the method's internal parameters (action, prop, titles, cllimit) take precedence over conflicting keys in kwargs.

## Returns:
    PagesDict: The method returns either:
      - The return value of self._build_categories(v, page) for the first page entry returned by the API (when a page entry exists and is not the "-1" missing-page sentinel), or
      - An empty dict {} when the page is not found (the API page id key equals the string "-1") or when no pages are present.
    No other return shapes are produced by this method itself; the concrete structure of PagesDict is determined by the _build_categories helper.

## Raises:
    - This method does not explicitly raise exceptions. Exceptions raised by underlying helpers (self._query, self._common_attributes, self._build_categories) propagate to the caller. Typical sources include:
        - Network or HTTP errors from the query helper (e.g., requests-related exceptions)
        - Parsing or key-access errors if the API response does not contain expected fields
    Consumers should be prepared to handle propagated exceptions from those helpers.

## State Changes:
Attributes READ:
    - None of the instance's (self.<attr>) attributes are directly read by this method (only helper methods on self are invoked).

Attributes WRITTEN:
    - None of the instance's (self.<attr>) attributes are directly modified by this method.

Page object attributes accessed or mutated (important external-state changes):
    - READ: page.title is read to populate the "titles" API parameter.
    - WRITTEN: In the missing-page case (API returns a page entry key equal to the string "-1"), the method sets page._attributes["pageid"] = -1 before returning {}.
    - Additionally, the method calls self._common_attributes(raw["query"], page) and self._build_categories(v, page). Those helpers are expected to read from and/or write to the provided page object's attributes (for example, to populate page metadata and to attach category objects). The exact page attributes modified by those helpers are determined by their implementations.

## Constraints:
Preconditions:
    - page must be an object exposing a string attribute `title`.
    - page must support a dictionary-like attribute page._attributes for storing metadata (the method writes page._attributes["pageid"] in one branch).
    - kwargs must be valid keyword-parameter names expected by the MediaWiki categories API or by the instance _query helper.

Postconditions:
    - If the API indicates the page does not exist (page key "-1"), page._attributes["pageid"] will be set to -1 and the method returns {}.
    - Otherwise, self._common_attributes(...) is invoked (so page may have common metadata fields populated) and the return value is whatever self._build_categories(...) produces for the first page entry in the API response.

## Side Effects:
    - Performs a network/API request indirectly via self._query(page, used_params). The exact nature (HTTP method, endpoint, timeouts) depends on the _query implementation.
    - May mutate the provided page object via calls to self._common_attributes(...) and self._build_categories(...).
    - Sets page._attributes["pageid"] = -1 in the specific case when the API indicates the page is missing.
    - Does not perform file I/O or write to attributes of self directly (aside from invoking helper methods that might).

### `wikipediaapi.__init__.Wikipedia.categorymembers` · *method*

## Summary:
Fetches all pages contained in the supplied category by calling the MediaWiki "categorymembers" API, handling pagination, and returning a consolidated PagesDict. The supplied WikipediaPage is also passed to helpers and may be updated with metadata from the API response.

## Description:
This method builds and issues the MediaWiki categorymembers query for the category identified by page.title, collects results across any continuation pages returned by the API, and delegates response normalization to internal helpers.

Known callers / usage contexts:
- Library consumers or higher-level helpers that need to enumerate pages within a category (for example, code that inspects a category page and iterates its members).
- It is typically called after a WikipediaPage object representing a category has been created or retrieved; the method reads page.title and uses that as the API cmtitle value.

Why this logic is isolated:
- Pagination logic, parameter construction, and the combination of results are non-trivial and reused within category-member retrieval flows. Separating this behavior centralizes MediaWiki protocol handling (initial request, continuation loop, combining lists) and leaves callers free from API-specific details. Delegation to _common_attributes and _build_categorymembers keeps parsing and object-mapping responsibilities modular.

## Args:
    page (WikipediaPage):
        The WikipediaPage instance representing the category to query. The method reads page.title to set the API cmtitle and passes the page object to helper methods that may mutate it.

    **kwargs:
        Arbitrary additional API parameters supplied by the caller intended for the MediaWiki "categorymembers" module (examples: cmnamespace, cmtype, cmstartsortkey). Behavior specifics:
        - The method merges kwargs and its own defaults by doing used_params = kwargs; used_params.update(params). This means the method's default keys (action, list, cmtitle, cmlimit) override any identically-named keys in kwargs.
        - The merged parameter mapping (used_params) is used only for the initial API request. Continuation requests use the internal params dict (see Implementation notes), so caller-supplied kwargs are not re-sent on subsequent continuation requests.
        - kwargs is a local dict inside the function (created by the **kwargs mechanism). Mutating it inside the method does not mutate caller-scoped variables outside the call.

    Internal default parameter values set by this method (applied during the merge):
        action = "query"
        list = "categorymembers"
        cmtitle = page.title
        cmlimit = 500

## Returns:
    PagesDict:
        The aggregated category members as produced by self._build_categorymembers(v, page). This structure represents members combined from the initial API response and any continuation responses. For an empty category, the returned PagesDict will represent zero members (as produced by _build_categorymembers when no categorymembers are present in the payload).

## Raises:
    Exceptions propagated from helper methods:
        - Any exception raised by self._query will propagate (network errors, HTTP errors, timeouts, or custom exceptions raised by that method).
        - Any exception raised by self._common_attributes or self._build_categorymembers will propagate.

    KeyError:
        - If the API response does not contain the expected "query" key, accessing raw["query"] will raise KeyError.
        - If the API response contains a top-level "continue" key but that mapping does not contain "cmcontinue", accessing raw["continue"]["cmcontinue"] will raise KeyError.

    Note: The method does not explicitly catch or translate these exceptions; callers should expect and handle propagated errors.

## State Changes:
    Attributes READ:
        - page.title (reads the category title to set cmtitle)
        - self._query (method called)
        - self._common_attributes (method called)
        - self._build_categorymembers (method called)

    Attributes WRITTEN:
        - No self.<attribute> fields are assigned in this method.

    Other object mutations:
        - page (WikipediaPage): may be mutated indirectly because the method calls self._common_attributes(raw["query"], page). That helper typically writes metadata into the provided page object.
        - Local variables mutated: params and used_params are mutated during execution (params gets a "cmcontinue" key when continuing). These are local and do not persist beyond the call.

## Constraints:
    Preconditions:
        - page.title must be a valid category title string accepted by the MediaWiki API.
        - The process must have network access and correct API endpoint configuration for self._query to succeed.
        - If the caller relies on persistent inclusion of custom kwargs across all continuation requests, this method's behavior (caller kwargs applied only to the initial request) does not guarantee that; callers must re-invoke or modify behavior accordingly.

    Postconditions:
        - The returned PagesDict contains the combined set of categorymembers from the initial and any continuation responses aggregated in the v["categorymembers"] list prior to calling _build_categorymembers.
        - The supplied page object has been passed to _common_attributes and may now contain additional metadata extracted from the API response.
        - No attributes on self are changed by this method.

## Side Effects:
    - Network I/O: performs at least one HTTP/API call via self._query; may perform additional calls if the API returns a continuation token.
    - Mutation of the supplied page object via calls to _common_attributes.
    - Local mutation of parameter dictionaries (params and used_params) inside the method.
    - Possible propagation of exceptions raised by any helper or network layer.

## Implementation notes / behaviors to preserve when reimplementing:
    - Construct params = {"action": "query", "list": "categorymembers", "cmtitle": page.title, "cmlimit": 500}.
    - Merge caller kwargs into a local mapping using used_params = kwargs followed by used_params.update(params) so that the default keys in params override identically-named keys in kwargs.
    - Call raw = self._query(page, used_params) for the initial request.
    - Call self._common_attributes(raw["query"], page) immediately after the initial response to populate the page with any shared metadata.
    - Aggregate results: set v = raw["query"]; while "continue" in raw, set params["cmcontinue"] = raw["continue"]["cmcontinue"], call raw = self._query(page, params), and extend v["categorymembers"] with raw["query"]["categorymembers"].
    - After collecting all pages, return self._build_categorymembers(v, page).
    - Preserve the behavior that continuation requests use the params dict (which contains only the defaults plus cmcontinue) rather than reusing used_params; this means caller-supplied kwargs are only applied to the first request.

### `wikipediaapi.__init__.Wikipedia._query` · *method*

## Summary:
Performs a single HTTP GET against the Wikimedia API for the page's language variant, parses and returns the JSON response. Mutates the provided params dict to ensure JSON format and redirects handling.

## Description:
This internal helper centralizes the HTTP call used by the Wikipedia instance to query the MediaWiki API. It is called by the Wikipedia class public methods that fetch page data and lists:
- extracts
- info
- langlinks
- links
- backlinks
- categories
- categorymembers

Context / lifecycle: called during any page data-fetch operation to make one API request. Higher-level methods may call it repeatedly (in a loop) to follow pagination/continuation tokens returned by the API.

Why a separate method: centralizes common behavior (base URL construction, logging, default parameters, use of the persistent requests.Session and request kwargs), avoids duplicating network-call plumbing across many Wikipedia methods, and makes testing/mocking the HTTP layer easier.

## Args:
    page (WikipediaPage): Page object whose language determines the target Wikimedia subdomain. The method reads page.language (expected to be a non-empty language code string such as "en"). Other attributes of page are not required by this method.
    params (Dict[str, Any]): Mutable dictionary of query parameters for the MediaWiki API (e.g., action, prop, titles, list, continue tokens). This dict is mutated in-place: the method sets/overwrites keys "format" and "redirects".

## Returns:
    Dict[str, Any]: Parsed JSON response from the Wikimedia API (typically a mapping that contains keys such as "query" and possibly "continue"). The concrete schema follows the MediaWiki API JSON format. If the response body is valid JSON, the parsed object (usually a dict) is returned.

    Edge-case returns:
    - If the HTTP response body is valid JSON but indicates an error per MediaWiki (for example contains an "error" key), that JSON is returned verbatim and must be interpreted by the caller.
    - This method does not return HTTP status information separately; callers should inspect returned JSON for API-level errors.

## Raises:
    requests.exceptions.RequestException:
        - Any networking-level problem raised by requests.Session.get (connection errors, DNS failures, timeouts, etc.). Specific subtypes such as requests.exceptions.Timeout may be raised depending on self._request_kwargs.
    json.JSONDecodeError or ValueError:
        - If the response body is not valid JSON, r.json() will raise a JSON parsing exception which is propagated.
    AttributeError:
        - If self._session or self._request_kwargs is missing (i.e., the Wikipedia instance was not properly initialized), attribute access may raise AttributeError.

Note: The method does not call r.raise_for_status(), so HTTP error status codes do not raise by themselves; only network-level exceptions or invalid JSON will raise.

## State Changes:
Attributes READ:
    - self._session (requests.Session): used to perform the GET request.
    - self._request_kwargs (Dict[str, Any]): keyword arguments forwarded to requests (e.g., timeout, proxies).
    - page.language (str): used to build the base URL.

Attributes WRITTEN:
    - None on self (this method does not modify Wikipedia instance attributes).
    - params (Dict[str, Any]) — mutated in-place:
        - params["format"] is set to "json"
        - params["redirects"] is set to 1

## Constraints:
Preconditions:
    - page.language must be a non-empty, lowercase language code (the Wikipedia constructor enforces this; callers should not pass empty language).
    - self._session must be a valid, initialized requests.Session object.
    - params must be a mutable mapping (dict) of query parameters intended for the MediaWiki API.

Postconditions:
    - The returned object is the parsed JSON response from the Wikimedia API.
    - The params dict passed by the caller contains at least the keys "format"="json" and "redirects"=1 after the call.
    - No other attributes on self are modified.

## Side Effects:
    - Network I/O: performs a single HTTP GET to https://{language}.wikipedia.org/w/api.php with provided query parameters and self._request_kwargs forwarded to requests.Session.get.
    - Logging: writes an INFO-level log entry showing the constructed request URL and the parameter key/value pairs (note: values are stringified).
    - The params argument is mutated in place (adds/overwrites "format" and "redirects").
    - No file I/O or persistent state changes beyond the above.

Implementation notes for re-implementation:
    - Build base_url as "https://{page.language}.wikipedia.org/w/api.php".
    - Log the request URL for debugging; ensure values are stringified when formatting the query portion for the log.
    - Ensure to pass params to requests via the params= argument (requests will URL-encode them).
    - Forward any session-level kwargs stored on the Wikipedia instance (timeout, proxies, etc.).
    - Do not call raise_for_status() here — higher-level code inspects returned JSON and handles API-level errors; decide intentionally if you want to change this behavior when reimplementing.

### `wikipediaapi.__init__.Wikipedia._build_extracts` · *method*

## Summary:
Parses the raw extract text of a page, populates the page object with a trimmed one-paragraph summary and a hierarchical tree of section objects, and returns the summary string.

## Description:
This method converts a single API-derived "extract" string (extract["extract"]) into structured page content: it determines the summary (text before the first section header), identifies section headers with a regex chosen by the instance's extract_format, creates section objects for each header, assigns section body text to those objects, builds parent→child links between sections, and populates a mapping from section title to section instances.

Known callers / invocation context:
- Called internally after the library receives and deserializes a page response that includes an "extract" text. It runs during page construction or refresh to transform raw text into page/section objects.
- Kept as an instance method because it depends on instance configuration (self.extract_format), on the RE_SECTION mapping, and uses other instance helpers (self._common_attributes and self._create_section).

Why this is a separate method:
- The parsing and hierarchical assembly logic is non-trivial (regex scanning, stack-based nesting, multiple mutations) and is reused wherever the library must convert extract text to structured page content. Isolating it improves readability, testability, and reuse.

## Args:
    extract (dict[str, Any]):
        - Required key: "extract" (str) — the raw page text containing summary and section headers. The method accesses extract["extract"] directly.
        - Optional keys forwarded to page._attributes by _common_attributes: "title", "pageid", "ns", "redirects".
    page (WikipediaPage):
        - Mutable page object to populate. Required attributes/members that the method expects:
            - _attributes (dict-like): used/modified by _common_attributes; must support item assignment.
            - _summary (str): will be assigned.
            - _section_mapping (will be replaced): will be set to a defaultdict(list).
            - _section (list): list of child sections; page._section is used as the root's child list and must support .append().
        - Section objects created by self._create_section are expected to have: .title (str), .level (int), ._text (str, assignable), and ._section (list).

## Returns:
    str: The computed page summary (the same string assigned to page._summary).
        - If at least one section header is detected: the trimmed substring of extract["extract"] before the first header.
        - If no section headers are detected: the entire extract["extract"] string, trimmed.
        - If extract["extract"] contains only whitespace, returns an empty string.

## Raises:
    KeyError:
        - If the extract mapping does not contain the "extract" key (accessing extract["extract"]).
        - If self.extract_format is not a valid key in the module-level RE_SECTION mapping (RE_SECTION[self.extract_format]).
    TypeError:
        - If extract["extract"] is not a string (operations that expect string indices/slices will raise TypeError).
    AttributeError:
        - If the provided page object does not expose required attributes (e.g., missing page._attributes, page._section, or page._section_mapping cannot be assigned), attribute access/assignment will raise AttributeError.
    Any exception raised by:
        - self._common_attributes(extract, page) if it fails (for example, if page._attributes is missing).
        - self._create_section(match) if the regex groups are not the expected format or the constructor for the section raises.
    Note: The method does not raise custom exceptions directly; it lets underlying errors propagate to the caller.

## State Changes:
Attributes READ (self):
    - self.extract_format: used to select the regex from RE_SECTION.
    - Module-level RE_SECTION mapping: used to obtain the regex/pattern.

Attributes WRITTEN (self):
    - None. The method does not mutate self attributes directly.

Mutated page/section state (visible side effects):
    - page._summary: overwritten with the computed summary string.
    - page._section_mapping: replaced with a new defaultdict(list) and populated such that page._section_mapping[section.title].append(section) for every created section.
    - page._attributes: may be updated by _common_attributes for keys present in extract among ["title", "pageid", "ns", "redirects"].
    - Parent objects' _section lists (page._section and section._section): new section objects are appended to their parent's _section list to form the nested structure.
    - section._text: assigned the text belonging to that section:
        - For non-final sections: assigned the trimmed substring between section header start and the next header start.
        - For the final section (if any): assigned the trailing substring after the last header without trimming.

Local variables initialized (important for reimplementation):
    - section_stack: initialized to [page] and used as a stack of current ancestor nodes (root page at index 0, current top at last index).
    - section: initialized to None; holds the most recently created section object.
    - prev_pos: initialized to 0; tracks the end index of the previous matched header in extract["extract"].

## Exact section-nesting algorithm (step-by-step):
1. Prepare:
    - Set page._summary = "" and page._section_mapping = defaultdict(list).
    - Call self._common_attributes(extract, page) to copy basic scalar attributes.
    - Initialize section_stack = [page], section = None, prev_pos = 0.

2. Find headers:
    - Iterate matches from re.finditer(RE_SECTION[self.extract_format], extract["extract"]).
    - For the first match only (when page._section_mapping is empty), set page._summary to extract["extract"][0:match.start()].strip() (the text before the first header, trimmed).
    - For subsequent matches, if section (the previously created section) is not None, set section._text = extract["extract"][prev_pos:match.start()].strip() — assign the trimmed body text between the previous header end and the current header start.

3. Create the new section:
    - section = self._create_section(match)
    - Derive sec_level = section.level + 1 (sec_level corresponds to the header level as parsed from the regex/_create_section).

4. Adjust section_stack to reflect sec_level:
    - If sec_level > len(section_stack): the new section is a deeper child; push it onto section_stack.
    - Elif sec_level == len(section_stack): the new section is a sibling at the same depth; pop the current top and push the new section (replace current top).
    - Else (sec_level < len(section_stack)): the new section is higher up the tree; pop (len(section_stack) - sec_level + 1) times, then push the new section. This ensures after pushing, len(section_stack) == sec_level.

5. Attach new section to its parent:
    - The parent is the element one below the top: parent = section_stack[len(section_stack) - 2].
    - Append the new section to parent._section (parent._section.append(section)).
    - Record the section in the mapping: page._section_mapping[section.title].append(section).

6. Update prev_pos = match.end() and continue.

7. After loop:
    - If no headers were found (page._summary == ""), set page._summary = extract["extract"].strip() (entire extract trimmed).
    - If prev_pos > 0 and section is not None (i.e., at least one header existed), assign the trailing text after the last header to the last section without trimming:
        section._text = extract["extract"][prev_pos:]

## Constraints / Preconditions:
    - RE_SECTION[self.extract_format] must be a compiled regex or pattern usable by re.finditer and must produce the groups expected by self._create_section:
        - For the WIKI format, _create_section expects captured groups where group(1) is the header markup (length indicates level) and group(2) is the title text.
        - For the HTML format, _create_section expects group(1) to contain the numeric level string and group(5) to contain the title text.
    - extract["extract"] must be a string.
    - Provided page must implement/allow assignment to the attributes described above.

## Postconditions (guarantees after successful call):
    - page._summary is a string (possibly empty) containing the trimmed summary or entire extract when no sections exist.
    - page._section_mapping is initialized and contains entries for every detected section title mapping to lists of section objects.
    - A tree of section objects is attached under page via parent._section lists following the nesting implied by header levels.
    - The method returns page._summary.

## Side Effects:
    - Mutates the provided page object and newly created section objects as described.
    - Calls self._common_attributes and self._create_section (their side effects also apply).
    - No network, filesystem, or other external I/O occurs in this method itself.

### `wikipediaapi.__init__.Wikipedia._create_section` · *method*

## Summary:
Constructs and returns a WikipediaPageSection representing a single heading match from an extracts string; sets the section title and numeric depth (level) based on the current extract_format and the provided regex match, without mutating the Wikipedia instance.

## Description:
This method is invoked by the page-extraction parser while iterating over heading matches (known caller: Wikipedia._build_extracts). During the extract-build lifecycle it is called for each regex match produced by re.finditer(RE_SECTION[self.extract_format], extract["extract"]) to produce a section object that the parser will attach into the page/section tree.

The logic is factored into its own helper because it centralizes the mapping between the two supported extraction formats (ExtractFormat.WIKI and ExtractFormat.HTML) and the way title text and heading depth are extracted from different regex capture groups. Keeping this in a separate method improves readability of _build_extracts, isolates format-specific parsing, and makes it easier to test or extend parsing for additional formats.

## Args:
    match (re.Match): A regex match object produced by the RE_SECTION pattern for the current self.extract_format. Required capture groups:
        - If self.extract_format == ExtractFormat.WIKI:
            * group 1: the heading marker (string whose length equals heading level)
            * group 2: the raw heading/title text
        - If self.extract_format == ExtractFormat.HTML:
            * group 1: the numeric heading level as a string (e.g., "1", "2")
            * group 5: the raw heading/title text
    The match must not be None and must come from a regex that provides the expected numbered groups for the active extract_format.

## Returns:
    WikipediaPageSection: A newly constructed section instance with:
        - .wiki set to self (the parent Wikipedia instance)
        - .title set to the stripped title string extracted from the match (may be empty)
        - .level set to (sec_level - 1), where sec_level is derived from the match (see behavior).
    Edge-case return values:
        - If self.extract_format is neither ExtractFormat.WIKI nor ExtractFormat.HTML, returns a section with title "" and level 1 (because the method falls back to defaults sec_title = "" and sec_level = 2).
        - The returned object's .level may be 0 or greater depending on captured sec_level; negative levels are only possible if a captured sec_level equals 0 (unlikely given the expected patterns) — callers should not rely on negative values.

## Raises:
    AttributeError:
        - If match is None or match.group(...) returns None and code attempts to call .strip() on it (e.g., if a capture group exists but produced None).
    IndexError:
        - If the supplied match object does not define the numbered group(s) accessed (e.g., group(2) or group(5) is out of range for the pattern).
    ValueError:
        - If self.extract_format == ExtractFormat.HTML and the code attempts to convert match.group(1).strip() to int but the captured string is not a valid integer.
    Any exceptions raised by the WikipediaPageSection constructor if invalid constructor arguments are supplied (propagated as-is).

## State Changes:
    Attributes READ:
        - self.extract_format: used to select which regex groups to read and how to interpret them.
    Attributes WRITTEN:
        - None on self. The method does not mutate the Wikipedia instance.
    External object mutations:
        - Allocates a new WikipediaPageSection instance and returns it; it does not attach that section to any page or modify other state itself.

## Constraints:
    Preconditions:
        - self must be a valid Wikipedia instance with an extract_format attribute that is a member of ExtractFormat.
        - match must be a re.Match produced by the RE_SECTION pattern corresponding to self.extract_format and must include the expected numbered groups (1 and 2 for WIKI; 1 and 5 for HTML).
    Postconditions:
        - The returned WikipediaPageSection.wiki equals self.
        - The returned WikipediaPageSection.title equals the stripped string extracted from the appropriate group.
        - The returned WikipediaPageSection.level equals (sec_level - 1), where:
            * For WIKI: sec_level = len(match.group(1))
            * For HTML: sec_level = int(match.group(1).strip())
            * For unknown extract_format: sec_level defaults to 2 (so level == 1)

## Side Effects:
    - Allocates a new WikipediaPageSection instance (pure in-memory object creation).
    - No network IO, no HTTP requests, no file operations.
    - No mutation of self or any external global state.
    - May propagate exceptions from regex group access or integer conversion as described in Raises.

### `wikipediaapi.__init__.Wikipedia._build_info` · *method*

## Summary:
Copies all key/value pairs from a MediaWiki "page" API response into the given WikipediaPage object's internal attributes and applies common attribute extraction; returns the same page object.

## Description:
This method is invoked after an API response for the "info" query has been selected for a single page. Known caller:
- Wikipedia.info — when iterating over raw["query"]["pages"], Wikipedia.info calls this method to populate the WikipediaPage instance with the API-provided page dictionary.

This work is extracted into its own method because it encapsulates the generic step of applying the shared/common attributes (via _common_attributes) and copying the full set of returned page fields into the page object's attribute map. Separating it keeps the info() flow small and mirrors the pattern used by other _build_* helpers that populate specific page-related data.

## Args:
    extract (mapping-like): A mapping (typically the dict for a single page returned by MediaWiki under raw["query"]["pages"][<pageid>"]) containing page fields such as "title", "pageid", "ns", "redirects", "url", etc. Must support the .items() iterator.
    page (WikipediaPage): The WikipediaPage instance to populate. The method expects page to expose a mutable mapping attribute named _attributes (typically a dict).

## Returns:
    WikipediaPage: The same page instance that was passed in, after mutation. The page._attributes mapping will contain all key/value pairs present in extract (keys from extract overwrite any existing keys in page._attributes).

## Raises:
    AttributeError: If the provided page object does not have a writable _attributes attribute (attempting to index or assign page._attributes[k]).
    TypeError: If extract does not provide a .items() method (i.e., it is not a mapping or dict-like object), iteration over extract.items() will raise a TypeError.

## State Changes:
Attributes READ:
    - (self) No self.<attr> fields of the Wikipedia instance are read by this method (it only calls the helper method _common_attributes).

Attributes WRITTEN:
    - page._attributes: The method updates/sets entries in page._attributes for every (k, v) in extract.items(). In addition, _common_attributes may also have written specific common keys (title, pageid, ns, redirects) into page._attributes prior to the full copy.

## Constraints:
Preconditions:
    - page must be an initialized WikipediaPage instance that exposes a mutable _attributes mapping (e.g., dict).
    - extract must be a mapping-like object representing a single MediaWiki "page" dictionary (the element of raw["query"]["pages"]); it must support .items().

Postconditions:
    - After the call, page._attributes contains all key/value pairs from extract. If extract contained keys present in page._attributes already, those values are overwritten by the values from extract.
    - The method returns the same page object passed as input.

## Side Effects:
    - Mutates the external page object by writing into page._attributes (this is the primary side effect).
    - Calls self._common_attributes(extract, page), which itself may mutate page._attributes for the common attribute keys.
    - No network I/O, file I/O, or other external I/O occurs in this method.

### `wikipediaapi.__init__.Wikipedia._build_langlinks` · *method*

## Summary:
Create and attach a mapping of language-code -> WikipediaPage objects on the given page by parsing the "langlinks" list from an API extract, replacing any existing page._langlinks and returning the new mapping.

## Description:
This method is a focused step in the page-parsing pipeline that converts the "langlinks" portion of a MediaWiki API response into WikipediaPage objects and stores them on the target page. Typical callers are page-construction/parsing routines that take a parsed API JSON fragment for a single page and populate its fields. It is invoked after allocating a WikipediaPage and before that page is returned to callers; the method delegates shared attribute handling to self._common_attributes(extract, page).

Reasons this logic is factored out:
- Centralizes interpretation of the API "langlinks" array and WikipediaPage construction parameters.
- Ensures consistent initialization (page._langlinks is always created) and a single return value for callers.
- Allows reuse and testing of language-link population independently of other parsing logic.

Known callers / lifecycle stage:
- Invoked by page parsing functions when processing an API response for a single page (i.e., during page object construction). It runs as part of the pipeline that reads API fragments and fills page attributes, after the page object is created and when langlinks must be materialized.

## Args:
    extract (mapping-like): A mapping (typically a dict) representing the API response fragment for a page. It must support extract.get("langlinks", []) and, if present, extract["langlinks"] must be an iterable of mappings where each mapping contains:
        "*"   (str): The page title on the target-language wiki.
        "lang"(str): The language code (e.g., 'fr', 'es') identifying the target wiki.
        "url" (str): URL to the page on the target-language wiki.
    page (object): The page object to populate (expected to be a WikipediaPage instance or page-like object). The method assigns page._langlinks and passes the page to self._common_attributes(extract, page). The page must allow attribute assignment (page._langlinks = ...).

Notes:
- The method signature declares a return type PagesDict (alias not provided here). Practically, this is a dict-like mapping from language code (str) to WikipediaPage instance.
- Namespace referenced below is an IntEnum mapping of MediaWiki namespace identifiers; this method passes the Namespace.MAIN member to the WikipediaPage constructor for the ns parameter (see Implementation notes).

## Returns:
    dict (PagesDict-like): The mapping assigned to page._langlinks and returned by the method. Concretely:
        { language_code (str) : WikipediaPage(instance), ... }
    Behavior:
    - If extract contains no "langlinks" key or it maps to an empty list, an empty dict is returned.
    - The returned dict is the same object referenced by page._langlinks.
    - If multiple langlink entries share the same language code, the last encountered entry wins (overwrites previous).

## Raises:
    KeyError:
        - If a langlink item is missing any of the required keys ("*", "lang", or "url"), accessing that key will raise KeyError.
    AttributeError:
        - If extract does not provide a .get method (i.e., it's not mapping-like), calling extract.get will raise AttributeError.
        - If page disallows attribute assignment or is None, assignment to page._langlinks may raise AttributeError.
    TypeError / NameError / Exception:
        - The WikipediaPage constructor or Namespace may raise various exceptions (TypeError, NameError, ValueError, or custom exceptions) if they are misused or unavailable; these propagate from the constructor call. These are not raised by this method explicitly but can surface during object construction.

## State Changes:
Attributes READ:
    - self (indirect): The method invokes self._common_attributes(extract, page), which may read attributes on self. This method does not directly access named self.<attr> fields in its body, but the invoked helper may.

Attributes WRITTEN:
    - page._langlinks: Unconditionally overwritten at the start with a new empty dict, then populated with entries for each langlink. Any previous value stored in page._langlinks is discarded.

Ordering detail (important):
    - The method first assigns page._langlinks = {}.
    - Then it calls self._common_attributes(extract, page).
    - After that, it iterates extract.get("langlinks", []) and populates page._langlinks.

This ordering means self._common_attributes may observe an empty page._langlinks if it inspects that attribute.

## Constraints:
Preconditions:
    - extract must be mapping-like and, if it contains "langlinks", each entry must be a mapping with keys "*", "lang", and "url".
    - page must be an object that supports attribute assignment and is accepted by self._common_attributes.
    - The symbols WikipediaPage and Namespace must be defined and behave as constructors/classes in the current module scope.

Postconditions:
    - page._langlinks exists and is a dict mapping language codes to WikipediaPage instances.
    - Each WikipediaPage created uses these constructor arguments (as visible in the implementation):
        wiki=self
        title=langlink["*"]
        ns=Namespace.MAIN  (Namespace is an IntEnum; Namespace.MAIN is the member representing the canonical main/article namespace)
        language=langlink["lang"]
        url=langlink["url"]
    - The method returns the page._langlinks dict.

## Side Effects:
    - Calls self._common_attributes(extract, page). That helper may mutate page and/or read or modify attributes on self.
    - Instantiates WikipediaPage objects per langlink; the constructor may perform its own side effects (not shown here).
    - No network I/O or file I/O is performed by this method itself.

## Implementation notes / edge cases to preserve when reimplementing:
    - Use extract.get("langlinks", []) to tolerate a missing key and treat it as an empty list.
    - Overwrite page._langlinks before calling common/shared attribute logic (this is the exact ordering in the source).
    - The code passes the Namespace.MAIN IntEnum member as the ns constructor argument; do not replace it with a localized name or integer literal—use the enum member to preserve readability and compatibility.
    - Key collisions on language code should behave as last-wins during iteration.
    - Do not swallow exceptions from missing keys; allowing KeyError to propagate matches the original behavior.

### `wikipediaapi.__init__.Wikipedia._build_links` · *method*

## Summary:
Constructs and assigns the page's links mapping from a MediaWiki API "links" extract, setting page._links to a dictionary that maps link titles to newly-created WikipediaPage objects.

## Description:
- Known callers:
    - Wikipedia.links(page, **kwargs): after fetching and (if needed) paginating the API response for the "links" property, links() calls this method to convert the API payload for that page into WikipediaPage objects and attach them to the page object.
- Lifecycle / pipeline stage:
    - Invoked after an API query that returned a "links" list for a page. It runs during the response-processing step that transforms raw API JSON into in-memory WikipediaPage objects and page attributes.
- Reason for separation:
    - The logic converts a specific API property ("links") into WikipediaPage instances and updates the page state. Keeping it as a separate method isolates parsing/creation logic for the "links" property, avoids duplicating similar logic used by other property-builders (e.g., _build_categories, _build_backlinks), and centralizes calls to _common_attributes that populate shared page metadata.

## Args:
    extract (Mapping[str, Any]):
        - API response fragment for a single page (the "v" value from raw["query"]["pages"]).
        - Expected to be a mapping that may include a "links" key whose value is an iterable of mappings; each link mapping is expected to contain:
            * "title" (str): link target title as used on Wikipedia (required for each link).
            * "ns" (str|int): namespace identifier (string or integer convertible to int).
        - If "links" is absent, an empty list is assumed.
    page (WikipediaPage):
        - The WikipediaPage instance being populated. Must expose and accept these attributes:
            * language (str): language code used to create child WikipediaPage instances.
            * _links (dict-like): will be overwritten by this method.
            * _attributes (dict-like): may be modified indirectly by _common_attributes.
        - The function expects page to be a mutable object compatible with WikipediaPage produced by this module.

## Returns:
    PagesDict (Dict[str, WikipediaPage]):
        - A dictionary mapping link title (str) -> WikipediaPage instance created for that link.
        - Possible values:
            * Non-empty dict when extract contains links: newly-created WikipediaPage objects keyed by their title.
            * Empty dict when extract has no "links" or when the list is empty.
        - The returned object is the same object assigned to page._links.

## Raises:
    - No explicit exceptions are raised by the method itself.
    - The method may propagate:
        * KeyError if a link entry lacks the "title" or "ns" keys.
        * ValueError or TypeError if link["ns"] cannot be converted to int.
        * Any exceptions raised by the WikipediaPage constructor if invoked with invalid arguments.
    - These propagated errors indicate malformed API data or an unexpected WikipediaPage contract.

## State Changes:
    Attributes READ:
        - self (Wikipedia): no persistent attributes of self are read directly in this method (other than calling self._common_attributes).
        - page.language: used as the language argument for each created WikipediaPage.
    Attributes WRITTEN:
        - page._links: overwritten with a new dict mapping titles -> WikipediaPage objects.
        - page._attributes: may be modified by the invoked helper self._common_attributes(extract, page) (common attributes such as "title", "pageid", "ns", "redirects" are copied from extract to page._attributes when present).

## Constraints:
    Preconditions:
        - page must be a valid WikipediaPage-like object with at least the attributes specified above (language, _links, _attributes).
        - extract should be a mapping representing a single page's API response; if the mapping is malformed (missing expected keys or containing non-iterable "links"), the method may raise or propagate errors.
        - link entries are expected to contain "title" and "ns" keys; "ns" must be convertible to int.
    Postconditions:
        - page._links is guaranteed to be a dict (possibly empty).
        - For every element in extract.get("links", []), there will be an entry in page._links with key equal to link["title"] and value equal to a WikipediaPage constructed with:
            * wiki=self
            * title=link["title"]
            * ns=int(link["ns"])
            * language=page.language
        - The method returns the same dict object assigned to page._links.

## Side Effects:
    - Constructs one WikipediaPage object per link entry, which may run the WikipediaPage constructor and any logic it performs (no network I/O is performed by this method itself).
    - Calls self._common_attributes(extract, page), which mutates page._attributes to copy common metadata from the extract.
    - No HTTP calls or file I/O are executed here; all effects are in-memory object creation and attribute mutation.

### `wikipediaapi.__init__.Wikipedia._build_backlinks` · *method*

## Summary:
Parses a backlinks API response for a page, replaces the page's _backlinks mapping with WikipediaPage objects for each backlink, and returns that mapping.

## Description:
Known callers and context:
- Called by Wikipedia.backlinks after performing the HTTP API query and assembling a combined response object. It runs in the response-processing stage of the backlinks retrieval pipeline, i.e., after _query has returned the JSON and any "continue" pages have been concatenated.

Why this is a separate method:
- Parsing and constructing WikipediaPage objects is shared behavior across several "build_*" helpers (e.g., _build_links, _build_langlinks). Extracting the backlinks-specific conversion into its own method keeps the API-calling logic (HTTP, pagination) separate from the response-to-object conversion and improves reuse and testability.

## Args:
    extract (dict): The JSON-like dictionary containing the combined query results for backlinks. Expected shape:
        {
            # other fields used by _common_attributes, e.g. "title", "pageid", ...
            "backlinks": [
                {"title": "<page title>", "ns": "<namespace as str or int>", ...},
                ...
            ]
        }
        The "backlinks" key is optional; if missing or empty, no backlinks will be created.
    page (WikipediaPage): The WikipediaPage instance being populated. Must have at least:
        - language (str): language code used when constructing linked WikipediaPage objects.
        - _attributes (dict-like): used/modified by _common_attributes.
        - _backlinks attribute will be set/overwritten by this method.

## Returns:
    dict[str, WikipediaPage]: A mapping from backlink title to a WikipediaPage object representing that backlink.
    - If no backlinks are present in extract, an empty dict is returned and assigned to page._backlinks.
    - The returned dict is the same object assigned to page._backlinks.

## Raises:
    KeyError:
        - If an entry in extract["backlinks"] is missing the "title" key (backlink["title"]) or the "ns" key (backlink["ns"]), a KeyError will be raised when those keys are accessed.
    TypeError:
        - If extract is None or not a mapping (e.g., not supporting .get), calling extract.get("backlinks", []) may raise AttributeError/TypeError upstream.
        - If backlink["ns"] is not a type accepted by int() (e.g., a dict), int(backlink["ns"]) may raise TypeError.
    ValueError:
        - If backlink["ns"] contains a non-numeric string that cannot be converted by int(), int(backlink["ns"]) will raise ValueError.
    Notes:
        - No exceptions are explicitly raised by this method itself; the above exceptions are the natural errors callers should expect from malformed input.

## State Changes:
Attributes READ:
    - self: no internal attributes of self are read by this method beyond invoking the helper _common_attributes and constructing WikipediaPage objects with wiki=self.
    - page.language: read to pass into each created WikipediaPage as the language.
Attributes WRITTEN:
    - page._backlinks: overwritten with a new dict mapping titles to WikipediaPage instances.
    - page._attributes: may be modified by self._common_attributes(extract, page) (common attributes like "title", "pageid", "ns", "redirects" are copied into page._attributes).

## Constraints:
Preconditions:
    - extract must be a mapping (dict-like). If not, callers should not call this method.
    - Each item in extract.get("backlinks", []) should be a mapping containing at minimum the keys "title" and "ns".
    - page must be a valid WikipediaPage instance with a string .language attribute and a mutable ._attributes container.

Postconditions:
    - page._backlinks is set to a dict where each key is the backlink title (string) and each value is a WikipediaPage instance constructed with:
        - wiki=self
        - title equal to backlink["title"]
        - ns equal to int(backlink["ns"])
        - language equal to page.language
    - _common_attributes has been applied to page (page._attributes updated with any of "title", "pageid", "ns", "redirects" present in extract).
    - The returned value is the same object stored in page._backlinks.

## Side Effects:
    - Allocates WikipediaPage objects for every backlink and stores them in page._backlinks.
    - Mutates the passed-in page object (overwriting page._backlinks and potentially updating page._attributes via _common_attributes).
    - No network or filesystem I/O occurs in this method itself.

### `wikipediaapi.__init__.Wikipedia._build_categories` · *method*

## Summary:
Builds and attaches a mapping of category-title -> WikipediaPage objects to the provided page based on the API extract, and returns that mapping.

## Description:
This method is part of the page-construction pipeline that translates an API "extract" (parsed JSON/dict) into in-memory page-related objects. It performs three tasks:
1. Initializes page._categories to an empty mapping.
2. Delegates shared attribute extraction to self._common_attributes(extract, page).
3. Iterates the extract's "categories" list and creates a WikipediaPage object for each entry, keyed by the category title.

Known callers and lifecycle stage:
- Called during the process of constructing or refreshing a WikipediaPage from a raw API response (an "extract"). Typical callers are higher-level page-building routines that aggregate categories, links, revisions, etc. It should be invoked after obtaining an "extract" dict for a page and before the page is returned to callers that expect category objects to be available.

Why this is a separate method:
- Category handling is a discrete concern (parsing, object creation, and attaching to the page). Separating it keeps the overall page-building logic modular, makes unit testing easier, and isolates potential parsing errors related to categories.

## Args:
    extract (dict[str, Any]):
        The parsed API response for a page. Expected to be a mapping that may contain a "categories" key whose value is a list of category entries. Each category entry is expected to be a mapping containing at least:
            - "title": str  (category title, used as the dictionary key)
            - "ns": str or int  (namespace; will be coerced to int)
        If "categories" is absent, the method treats it as an empty list.

    page (WikipediaPage-like object):
        The in-memory page object being populated. Expected surface attributes and behaviors:
            - language (str): used as the language argument when creating each WikipediaPage.
            - _categories (mapping attribute): will be overwritten with a new dictionary by this method.
        The object will be mutated in-place.

## Returns:
    dict[str, WikipediaPage]:
        A dictionary mapping each category's title (string) to a newly-created WikipediaPage instance representing that category.
        - If no categories are present in extract, an empty dict is returned.
        - The returned dict is the same object assigned to page._categories.

## Raises:
    KeyError:
        - If a category entry in extract["categories"] does not contain the "title" key or the "ns" key, a KeyError will be raised when the method attempts to access category["title"] or category["ns"].

    ValueError:
        - If category["ns"] cannot be converted to an int (e.g., contains non-numeric characters), int(category["ns"]) will raise ValueError.

    TypeError:
        - If extract is not a mapping type that supports get(...), or if extract["categories"] is present but is not iterable (e.g., None or a non-iterable), a TypeError may be raised when iterating.
        - If page does not have a writable attribute _categories or a readable attribute language, attribute access will raise an AttributeError (documented here as a common failure mode).

    Any exception raised by self._common_attributes(extract, page):
        - This method delegates some work to self._common_attributes which may raise its own exceptions; those will propagate.

## State Changes:
Attributes READ:
    - page.language (reads the language to pass into each WikipediaPage constructor)
    - extract (reads extract.get("categories", []))
Attributes WRITTEN:
    - page._categories (assigned to a new dict object mapping title -> WikipediaPage)

Note about self attributes:
    - This method does not directly read or write any self.<attr> attributes in its body, but it calls self._common_attributes(extract, page), which may read or write attributes on self or page. Implementers should ensure that _common_attributes is invoked and its side effects are expected.

## Constraints:
Preconditions:
    - extract must be a mapping type (supporting get) and, if present, extract["categories"] must be iterable and contain mappings with "title" and "ns" keys.
    - page must be a mutable object with a writable _categories attribute and a readable language attribute.
    - WikipediaPage constructor (used below) must accept at least the named parameters: wiki, title, ns, language.

Postconditions:
    - page._categories is guaranteed to be a dict after the call (possibly empty).
    - For every (title, category_entry) in extract["categories"]:
        - page._categories[title] is a WikipediaPage instance constructed with:
            wiki=self, title=title, ns=int(category_entry["ns"]), language=page.language
    - The returned value is that same dict assigned to page._categories.

## Side Effects:
    - Mutates the provided page object by overwriting page._categories.
    - Allocates new WikipediaPage objects for each category entry.
    - Calls self._common_attributes(extract, page), which may perform additional mutations to page or read/write self attributes (and may raise exceptions).
    - No I/O (network, disk) is performed directly by this method.

## Implementation notes / reimplementation recipe:
1. Set page._categories = {}.
2. Call self._common_attributes(extract, page) to apply shared attribute extraction (preserve any exceptions).
3. Retrieve the categories sequence: categories = extract.get("categories", []).
4. For each category in categories:
    a. Read title = category["title"] (will raise KeyError if missing).
    b. Read ns_raw = category["ns"] and coerce ns = int(ns_raw) (may raise ValueError).
    c. Create a new WikipediaPage instance with wiki=self, title=title, ns=ns, language=page.language.
    d. Assign it into the dict: page._categories[title] = newly_created_page.
5. Return page._categories.

This description provides the exact semantics, expected failures, and the minimal interface required from WikipediaPage and self._common_attributes to reimplement the method.

### `wikipediaapi.__init__.Wikipedia._build_categorymembers` · *method*

## Summary:
Populates the given WikipediaPage object's _categorymembers mapping by creating WikipediaPage objects for each entry in the API "categorymembers" extract; the method mutates the page to attach that mapping and returns it.

## Description:
This method is called (directly observed) by Wikipedia.categorymembers after the Wikimedia API query/aggregation step has produced an extract containing a "categorymembers" list. It converts that API fragment into in-memory WikipediaPage instances and attaches them to the page object.

This functionality is separated into its own helper because it follows the same pattern used by other _build_* helpers (for links, categories, langlinks, etc.): isolating the conversion from API JSON to WikipediaPage objects keeps parsing logic consistent, reusable, and easier to test or replace without changing the request/query logic or higher-level call flow.

Known callers and context:
- Wikipedia.categorymembers: invoked after _query has returned JSON for the "categorymembers" list and, if necessary, after the calling method has aggregated additional pages across continuation tokens. The calling routine expects this method to finalize the conversion into page._categorymembers.

## Args:
    extract (dict): A mapping representing the API response fragment (usually raw["query"] or equivalent) that may contain a key "categorymembers" whose value is a list of member mappings. Each member mapping is expected to contain at least:
        - "title" (str): page title
        - "ns" (str or int): namespace value (convertible to int)
        - "pageid" (int): numeric page id
    page (WikipediaPage): The target WikipediaPage object to populate. The method reads page.language and writes page._categorymembers; it also relies on page supporting _attributes mutation via _common_attributes.

## Returns:
    PagesDict (dict[str, WikipediaPage]): The dictionary assigned to page._categorymembers mapping member titles (str) to newly-created WikipediaPage instances.
    - If no "categorymembers" key is present or it is empty, an empty dict is assigned and returned.

## Raises:
    - KeyError: If an expected key like "title", "ns", or "pageid" is missing from a member mapping, a KeyError may be raised by dictionary access.
    - TypeError: If `extract` is not a mapping (so extract.get is not available) or a member mapping is not a mapping, TypeError can occur.
    - ValueError or TypeError from int conversion: If member["ns"] is present but cannot be converted to int, int(member["ns"]) will raise ValueError or TypeError.
    Note: The method does not explicitly raise these exceptions; they are implicit outcomes of invalid input data.

## State Changes:
Attributes READ:
    - page.language: used as the language argument when creating WikipediaPage instances.
    - extract (via extract.get): reads the "categorymembers" list if present.
    - self._common_attributes is called and reads from extract and page as that helper requires.

Attributes WRITTEN:
    - page._categorymembers: set to a fresh dict at the start and populated with entries title -> WikipediaPage.
    - page._attributes: indirectly written if _common_attributes copies common fields (e.g., "title", "pageid", "ns", "redirects") from the extract into page._attributes.
    - For each created WikipediaPage instance `p`, the attribute p.pageid is set from member["pageid"].

## Constraints:
Preconditions:
    - `page` must be an object implementing the expected WikipediaPage interface: having a mutable _categorymembers attribute (or allowing assignment), a language attribute, and _attributes writable by _common_attributes.
    - `extract` must be a mapping (supporting .get) containing, if present, a "categorymembers" key whose value is an iterable of mappings with "title", "ns", and "pageid".
    - member["ns"] must be convertible to int.

Postconditions:
    - page._categorymembers is a dict mapping each member's title to a WikipediaPage instance constructed with:
        (wiki=self, title=member["title"], ns=int(member["ns"]), language=page.language)
      and with p.pageid set to member["pageid"].
    - The returned value is the same dict assigned to page._categorymembers (possibly empty if no members were present).
    - page._attributes may contain common metadata copied from `extract` due to the call to _common_attributes.

## Side Effects:
    - Mutates the passed-in `page` object (assigns/updates page._categorymembers and indirectly page._attributes).
    - Constructs new WikipediaPage instances (memory allocation).
    - No network or file I/O is performed by this method itself.

### `wikipediaapi.__init__.Wikipedia._common_attributes` · *method*

## Summary:
Copy a small set of standard MediaWiki fields from an API response fragment into the page object's internal attribute mapping, updating the page's metadata in-place.

## Description:
This helper is called by Wikipedia response-processing routines immediately after receiving and parsing a MediaWiki API JSON response and before the page-specific builder runs. It centralizes extraction of fields that are common across multiple API endpoints so response handlers do not duplicate identical assignment logic.

Known callers (exact method names in this module):
- Wikipedia.extracts (passes raw["query"], then per-page dicts into _build_extracts)
- Wikipedia.info (passes raw["query"])
- Wikipedia.langlinks (passes raw["query"])
- Wikipedia.links (passes raw["query"])
- Wikipedia.backlinks (passes raw["query"])
- Wikipedia.categories (passes raw["query"])
- Wikipedia.categorymembers (passes raw["query"])
- Internal builders that operate on a per-page extract dict: _build_extracts, _build_info, _build_langlinks, _build_links, _build_backlinks, _build_categories, _build_categorymembers

Call context:
- Some callers pass the top-level "query" mapping from the API response (e.g., raw["query"]).
- Other callers pass a per-page extract mapping (a dict representing one page's fields).
- This separation allows each API-path to call a single helper for consistent assignment of common attributes.

Why a separate method:
- Avoids repeating the same assignment code in many places.
- Ensures consistent behavior for the canonical attributes ("title", "pageid", "ns", "redirects") across different API responses.
- Keeps per-endpoint builder methods focused on endpoint-specific parsing.

## Args:
- extract (dict[str, Any]):
    - A mapping-like object (typically the parsed JSON dict produced by requests.json()) that may contain any of the keys: "title", "pageid", "ns", "redirects".
    - The function performs membership tests ("key in extract") and indexing (extract[key]).
- page (WikipediaPage):
    - A WikipediaPage instance that must expose a mutable mapping attribute named _attributes (expected type: dict[str, Any]).
    - The method writes into this mapping.

## Returns:
- None
    - The function performs in-place updates to page._attributes and does not return a value.

## Raises:
- No explicit exceptions are raised by the implementation.
- Observable runtime errors that can occur when preconditions are violated:
    - AttributeError: if the page object does not have an attribute named _attributes.
    - TypeError: if page._attributes does not support item assignment (for example, if it is None or an immutable mapping), or if extract is not a mapping that supports membership and indexing.

## State Changes:
- Attributes READ:
    - extract (membership tests and value reads for keys "title", "pageid", "ns", "redirects")
    - page._attributes (the mapping object is accessed to assign items)
- Attributes WRITTEN:
    - page._attributes["title"] — set when "title" exists in extract
    - page._attributes["pageid"] — set when "pageid" exists in extract
    - page._attributes["ns"] — set when "ns" exists in extract
    - page._attributes["redirects"] — set when "redirects" exists in extract
    - Existing values for these keys are overwritten by assignment.

## Constraints:
- Preconditions:
    - extract must be a mapping supporting "in" and __getitem__ semantics for the keys of interest.
    - page must provide a mutable mapping attribute named _attributes (e.g., initialized as an empty dict) before this function is called.
- Postconditions:
    - For each of the keys "title", "pageid", "ns", "redirects" present in extract, page._attributes will contain the same key with the same value after the call.
    - No other attributes on page are modified by this function.

## Side Effects:
- Mutates the page object's internal state by updating page._attributes.
- No network I/O, file I/O, or creation of new WikipediaPage instances occurs within this routine.

## `wikipediaapi.__init__.WikipediaPageSection` · *class*

## Summary:
Represents a single section (heading + body + subsections) of a Wikipedia page as parsed by the library. It models the section title, indentation level, plain/text content, and child subsections and provides utilities to retrieve and render the combined text of the section tree.

## Description:
WikipediaPageSection is an internal data container used by the library to store the structure of page extracts that contain headings and subsections. Typical instantiation occurs when the Wikipedia parser builds a page's section tree (see Wikipedia._create_section and Wikipedia._build_extracts). A developer may also construct instances directly for tests or manual assembly of section trees.

Responsibility boundary:
- Encapsulates metadata for one heading-level block: title, numeric level, textual content, and list of child sections.
- Provides read-only accessors for these attributes and utility methods to retrieve subsections by title or to get the concatenated text for the section and all subsections (full_text).
- It does not perform network IO, parsing of raw API strings, or manage page-level attributes; those responsibilities belong to Wikipedia and WikipediaPage.

Known callers / factories:
- Wikipedia._create_section constructs WikipediaPageSection during parsing of extracts.
- Wikipedia._build_extracts creates and organizes sections into the page._section_mapping and into parent._section lists.
- Consumers of the public API rarely need to create sections directly; the library will produce them when extracts are requested.

## State:
Attributes (public view vs internal storage):
- wiki (Wikipedia)
    - Type: Wikipedia
    - Description: Reference to the parent Wikipedia instance that controls extract formatting and has network/session configuration. Used by full_text to decide rendering format.
    - Constraints: Must be a valid Wikipedia instance; full_text reads wiki.extract_format and expects it to be an ExtractFormat member.

- _title -> visible via .title
    - Type: str
    - Description: Section heading text (the text shown as the heading).
    - Valid values: Any string (may be empty). Titles produced by the parser are typically non-empty; library code will strip surrounding whitespace.
    - Invariant: .title == self._title

- _level -> visible via .level
    - Type: int
    - Description: Indentation / heading depth relative to the page root. The library sets this such that a top-level heading typically has level 0 (the value used in Wikipedia._create_section is sec_level - 1).
    - Valid values: integer (library expects non-negative integers). Code does not strictly enforce non-negativity but uses level for presentation.
    - Invariant: .level == self._level

- _text -> visible via .text
    - Type: str
    - Description: Plain text body for this section (not including subsections). May be empty.
    - Valid values: Any string. When set by parser, content is trimmed of surrounding whitespace.
    - Invariant: .text == self._text

- _section -> visible via .sections
    - Type: List[WikipediaPageSection]
    - Description: Ordered list of child WikipediaPageSection instances (subsections).
    - Valid values: list containing only WikipediaPageSection instances.
    - Invariants:
        - Each element of _section is an instance of WikipediaPageSection.
        - A child's .wiki should point to the same Wikipedia instance as the parent (library code constructs children with the same wiki).
        - The order of elements reflects document order.

Class invariants:
- The `.wiki` attribute and `.sections` children form a tree (acyclic) representing subsections; the library constructs this tree without cycles.
- Titles and levels reflect the original extract structure produced by the parser; the numeric .level increases with deeper subsections.
- full_text relies on wiki.extract_format being a member of ExtractFormat; unsupported values cause a NotImplementedError.

## Lifecycle:
Creation:
- Direct constructor:
    - Required args: wiki (Wikipedia), title (str)
    - Optional args: level (int) default 0, text (str) default ""
    - Example: WikipediaPageSection(wiki_instance, "History", level=1, text="...")

- Primary factory in library:
    - Wikipedia._create_section(match) -> constructs WikipediaPageSection(self, sec_title, sec_level - 1)
    - Wikipedia._build_extracts orchestrates creation and attaches sections into the parent page and section stacks.

Usage:
- Typical sequence when parsing a page:
    1. Library calls Wikipedia._create_section for each heading match.
    2. Each created section is appended to its parent._section list by the parser logic.
    3. Parser sets a child's _text after subsequent heading matches or at the end of the extract.
    4. Consumers call section.full_text() to obtain the combined textual representation, or use properties (.title, .level, .text, .sections) to inspect structure.

- Direct usage patterns (manual construction):
    1. Instantiate root = WikipediaPageSection(wiki, "Root", level=0, text="root text")
    2. Create child = WikipediaPageSection(wiki, "Child", level=1, text="child text")
    3. Attach: root.sections.append(child)
    4. Call root.full_text() to render the combined content.

Destruction:
- No special cleanup or resource management is required. The class holds only pure-Python references; normal GC semantics apply. There is no close()/__enter__/__exit__ protocol.

Sequencing considerations:
- Methods that read child data (full_text, section_by_title) expect that children and their _text have been populated. If you construct sections manually, ensure children are appended and their ._text is set before calling full_text if you want complete results.

## Method Map:
flowchart LR
    A[Instantiate WikipediaPageSection] --> B{Attributes set}
    B --> C[.title/.level/.text (properties)]
    B --> D[.sections list (empty initially or appended to)]
    D --> E[section_by_title(title) --> scans ._section and returns last match or None]
    C --> F[full_text(level=1)]
    F --> G{checks wiki.extract_format}
    G --> H[ExtractFormat.WIKI -> prepend plain title]
    G --> I[ExtractFormat.HTML -> prepend <h{level}>title</h{level}>]
    G --> J[other -> raise NotImplementedError]
    F --> K[append self._text and spacing]
    F --> L[for each child in .sections call child.full_text(level+1) recursively]
    L --> M[concatenate and return the combined string]
    style A fill:#f2f8ff,stroke:#333,stroke-width:1px

## Raises:
- __init__: does not explicitly raise exceptions. Caller must provide a valid Wikipedia instance for correct later behavior.
- full_text:
    - Raises NotImplementedError if wiki.extract_format is not one of the supported ExtractFormat members (ExtractFormat.WIKI or ExtractFormat.HTML). This occurs because the implementation branches only on the two known formats and raises for anything else.
- Properties (.title, .level, .text, .sections) are safe accessors and do not raise on normal stored values.

## Example:
# Using the library's parser (typical):
wiki = Wikipedia(user_agent="myapp/1.0")   # Wikipedia instance used by parser
# Parser code (Wikipedia._create_section / _build_extracts) will create sections like:
# section = WikipediaPageSection(wiki, "History", level=1, text="...") and attach to parents.

# Manual construction (for testing or ad-hoc assembly)
root = WikipediaPageSection(wiki, "Root title", level=0, text="Intro text")
child = WikipediaPageSection(wiki, "Details", level=1, text="Detail paragraph.")
root.sections.append(child)

# Render as wiki-format or HTML depending on wiki.extract_format
wiki.extract_format = ExtractFormat.WIKI
print(root.full_text())   # "Root title\nIntro text\n\nDetails\nDetail paragraph.\n\n"

wiki.extract_format = ExtractFormat.HTML
print(root.full_text())   # "<h1>Root title</h1>\nIntro text\n\n<h2>Details</h2>\nDetail paragraph.\n\n"

### `wikipediaapi.__init__.WikipediaPageSection.__init__` · *method*

## Summary:
Initializes a WikipediaPageSection instance by storing the parent Wikipedia instance, heading metadata (title and numeric level), the section's plain text body, and creating an empty list to hold child subsections. After this call the object is ready to have children appended and its text inspected or updated.

## Description:
This constructor is called when constructing a single section node in the page section tree. Known callers and contexts:
- Wikipedia._create_section: invoked during parsing of page extracts to create a new section node for each matched heading.
- Wikipedia._build_extracts: orchestrates creation and attachment of section nodes into the page's tree structure.
- Tests or manual assembly code may instantiate this class directly to build section trees.

The logic is separated into its own constructor to encapsulate section-level state initialization (wiki link, title, level, body text, children list) in one place so parser code and tests can create section nodes consistently and rely on the same field layout. Keeping initialization here avoids duplicating attribute setup throughout parser/factory routines.

## Args:
    wiki (Wikipedia):
        Reference to the parent Wikipedia instance that configures rendering and contains network/session settings.
        Required. Must be a valid Wikipedia object for later operations (e.g., full_text rendering which reads wiki.extract_format).
    title (str):
        The heading text shown for this section. May be an empty string; parser typically strips surrounding whitespace before passing.
        Required.
    level (int, optional):
        Numeric depth of the heading relative to the page root. Defaults to 0.
        Expected to be a non-negative integer in normal use (parser passes sec_level - 1), but the constructor does not enforce non-negativity.
    text (str, optional):
        Plain-text body for this specific section (does not include subsections). Defaults to the empty string.
        The parser typically provides a trimmed string.

## Returns:
    None

## Raises:
    None explicitly raised by this method.
    (Note: later methods that rely on the stored wiki may raise errors if wiki is not a valid Wikipedia instance or if wiki.extract_format is an unsupported value.)

## State Changes:
Attributes READ:
    - None (constructor does not read existing instance attributes)

Attributes WRITTEN:
    - self.wiki: set to the supplied wiki argument
    - self._title: set to the supplied title argument
    - self._level: set to the supplied level argument
    - self._text: set to the supplied text argument
    - self._section: initialized to a new empty list intended to hold child WikipediaPageSection instances

## Constraints:
Preconditions:
    - Caller should supply a valid Wikipedia instance for the wiki parameter if later rendering (full_text) or wiki-dependent logic is expected to work correctly.
    - title must be a string (constructor expects this; non-string values are not explicitly checked).

Postconditions:
    - The instance will have the five attributes written above set deterministically from the arguments.
    - self._section will be an independent empty list (safe to append children without affecting other instances).
    - Public-facing properties (e.g., .title, .level, .text, .sections) should reflect the internal values assigned here.

## Side Effects:
    - No I/O, no network calls, and no interaction with global state.
    - Mutates only the new instance by setting attributes described above.
    - No shared mutable defaults are used (self._section is created per-instance).

### `wikipediaapi.__init__.WikipediaPageSection.title` · *method*

## Summary:
Returns the section's stored title as a read-only property without modifying the object's state.

## Description:
Known callers and contexts:
- WikipediaPageSection.full_text: used when composing the section heading into the aggregated text output.
- WikipediaPageSection.section_by_title: used when comparing subsection titles to locate a subsection by name.
- External consumer code: read whenever clients iterate sections, build outlines, or perform title-based lookups.

Lifecycle stage:
- Called any time after a WikipediaPageSection instance has been constructed. Typical invocation happens after page parsing/extraction, or later during rendering, searching, or UI display.

Rationale for being a separate property:
- Encapsulates access to the underlying _title attribute and exposes a stable, attribute-like API (via @property).
- Allows future changes (normalization, lazy computation, validation, logging) to be added centrally without changing call sites.
- Keeps client code from directly depending on the internal attribute name.

## Args:
None.

## Returns:
str (annotated/expected)
- By design and annotation, the property represents and returns the title string stored on the instance (the value of self._title).
- In typical/expected usage this is a Python str (including possibly the empty string) supplied at construction.
- Practical note: Python type annotations are not enforced at runtime—if external code mutates self._title to a non-str value, this property will return that value as-is.

## Raises:
- AttributeError: if self._title does not exist on the instance (for example, if __init__ was not run or the attribute was deleted). This is a runtime error raised by attribute access and not explicitly raised by the property implementation.
- No other exceptions are raised by this method itself.

## State Changes:
Attributes READ:
- self._title
Attributes WRITTEN:
- None (the property does not modify any attributes)

## Constraints:
Preconditions:
- The instance must have been initialized with WikipediaPageSection.__init__ so that self._title exists.
- Callers should expect self._title to be a str according to the constructor's annotation; correctness of callers may depend on that convention.

Postconditions:
- No change to object state.
- The returned value equals the current value of the instance's _title attribute at the time of the call.

## Side Effects:
- None. This property performs no I/O, external service calls, or mutations of objects outside self.
- Note: Because self._title is a plain attribute (not protected from external mutation), external code can change it; subsequent calls to this property will reflect such changes.

## Complexity:
- Time: O(1)
- Space: O(1)

### `wikipediaapi.__init__.WikipediaPageSection.level` · *method*

## Summary:
Read-only property that returns the stored integer indentation (depth) level for this section object.

## Description:
This @property exposes the internal attribute that holds the section's indentation depth so callers can read a section's numeric nesting level without accessing private state directly.

Known callers and context:
- The class __init__ assigns the attribute (see __init__(..., level: int = 0) which sets self._level).
- Within this class, __repr__ references the internal attribute self._level directly; the property itself is not referenced elsewhere in the provided class source.
- No other callers are present in the provided source; external code may read this property to inspect section depth but such callers are not shown.

Why this is a separate property:
- Encapsulates access to the internal _level attribute behind a stable public API (read-only), allowing future changes to storage or computation of level without changing external call sites.

## Args:
None — accessed as an attribute (section.level).

## Returns:
int
    The exact integer value currently stored in self._level.
    - By default this is 0 because __init__ sets level: int = 0.
    - The implementation does not validate or coerce the value; the returned value is whatever integer (or other value, if incorrectly mutated) is stored in self._level.

## Raises:
None. Accessing the property does not raise exceptions.

## State Changes:
Attributes READ:
    - self._level

Attributes WRITTEN:
    - None. The property does not modify object state.

## Constraints:
Preconditions:
    - The instance should be a properly initialized WikipediaPageSection (its __init__ sets self._level).
    - The intended type for the value is int per the __init__ signature, but this property does not enforce typing.

Postconditions:
    - The object's state is unchanged.
    - The return value equals the current value of self._level.

## Side Effects:
None. There is no I/O, external calls, or mutations of objects outside self.

### `wikipediaapi.__init__.WikipediaPageSection.text` · *method*

## Summary:
Return the plain-text body of this section as a string; this is a read-only accessor that does not modify the section.

## Description:
A simple property accessor that exposes the section's private storage for its textual content (self._text). The class __init__ initializes this attribute to a string (default ""), so callers can rely on receiving a str. Internal class methods (full_text and __repr__) read self._text directly rather than invoking this property; external code that consumes WikipediaPageSection objects should use this property when it needs the section content.

Typical usage scenarios:
- Rendering or displaying a section's content in a UI or console output.
- Extracting or indexing the plain-text body for search, storage, or analysis.
- Reading the text while iterating over a page's sections (e.g., for summarization or export).

This logic exists as a separate property to present a stable, public, read-only API for section content and to centralize any future logic (validation, transformation, or lazy-loading) that may be added without changing callers.

## Args:
    None

## Returns:
    str: The current text for the section. Under normal construction this is the same string assigned to self._text in __init__ (defaults to the empty string "").

## Raises:
    None: The accessor does not raise exceptions.

## State Changes:
    Attributes READ:
        - self._text
    Attributes WRITTEN:
        - None (no modifications performed)

## Constraints:
    Preconditions:
        - The instance must have been constructed so that self._text exists. The class __init__ sets self._text to a str by default, satisfying this precondition for all properly constructed instances.
    Postconditions:
        - No mutation of the instance or external state.
        - The return value equals the current value of self._text at the time of the call.

## Side Effects:
    - None. No I/O, network activity, or mutation of objects outside this instance occurs.

### `wikipediaapi.__init__.WikipediaPageSection.sections` · *method*

## Summary:
Returns the list of subsections for this section as the section's internal list (may be empty). This exposes the section's child nodes so callers can inspect or iterate them.

## Description:
Known callers and typical usage:
- Called by WikipediaPageSection.full_text during rendering to iterate through and render all subsections.
- Commonly used by client code that traverses the section tree (e.g., to find, inspect, or aggregate content from child sections).

Lifecycle/context:
- Invoked after a WikipediaPageSection instance has been constructed and its subsection tree populated (typically by the page-parsing logic).
- Used during read/traversal phases of the section tree; it does not perform parsing or mutation itself.

Why this is a separate method/property:
- Provides an explicit, stable accessor for the subsection list instead of exposing the internal attribute name directly. It centralizes the contract for how subsections are retrieved and makes the intent (read/iterate subsections) clearer than direct attribute access.
- Keeps the responsibility of managing the subsection container inside the class while allowing consumers to traverse the tree.

## Args:
This property takes no arguments.

## Returns:
List[WikipediaPageSection]
- The actual internal list object used to store subsections (self._section).
- May be an empty list if the section has no subsections.
- Important: the returned list is the internal list instance (no defensive copy is made). Mutating the returned list (append, remove, clear, etc.) will mutate the WikipediaPageSection's internal state.

## Raises:
- This accessor does not raise any exceptions itself.
- If the instance is improperly initialized (i.e., __init__ was not called), attribute access could raise AttributeError, but in the normal lifecycle this does not occur.

## State Changes:
Attributes READ:
- self._section (reads and returns this attribute)

Attributes WRITTEN:
- None (the method does not modify any attributes)

## Constraints:
Preconditions:
- The WikipediaPageSection instance must have been constructed (so self._section exists). The class __init__ initializes self._section to an empty list, satisfying this precondition under normal use.

Postconditions:
- The returned value is exactly self._section (same object identity).
- The method guarantees no mutation of the section object itself while executing; however, callers that mutate the returned list will change the object's state afterward.

## Side Effects:
- No I/O or external network/service calls.
- Exposes the internal list object to callers. Because the internal list is returned by reference, callers can mutate it, which will change the state of the WikipediaPageSection instance (this is a potential indirect side effect).
- Not thread-safe: concurrent mutations by other threads to the returned list or to the section's structure may cause race conditions.

### `wikipediaapi.__init__.WikipediaPageSection.section_by_title` · *method*

## Summary:
Return the last child subsection whose title exactly matches the provided string; does not modify the section object.

## Description:
This is a small, read-only accessor used to find a single subsection by its exact title among the current section's direct children. Typical callers are external client code or utilities that traverse a page/section tree and need a convenient way to fetch one matching subsection (for example, UI code, CLI tools, tests, or simple content-extraction helpers). There are no internal callers within this class that require it; it exists as a convenience to avoid duplicating the common pattern "filter children by title and take the last match".

This logic is its own method because:
- It encapsulates a repeated lookup pattern (filtering subsections by title and selecting the most recently appended match).
- It keeps callers simple and expressive (single-call lookup instead of inline list comprehensions).
- It centralizes behavior for handling multiple matches (explicitly returning the last match), making the intent and behavior consistent across the codebase.

## Args:
    title (str): Exact title to match against each child subsection's title.
        - Allowed values: any string.
        - There is no normalization (no trimming or case folding); comparison is exact equality.
        - Required — no default.

## Returns:
    Optional[WikipediaPageSection]:
        - The last WikipediaPageSection instance in self._section whose .title equals the provided title.
        - If multiple child subsections share the same title, the method returns the most recently appended one (the last in iteration order).
        - If no matching subsection exists, returns None.

## Raises:
    - This method does not explicitly raise exceptions.
    - Indirect exceptions that could propagate:
        * AttributeError if items in self._section do not expose a .title attribute (unlikely when subsections are instances of the same class).
        * Any exception raised during evaluation of the equality comparison (very rare).
    - Under normal use with correct object invariants, no exception is raised for "not found" cases; absence is signaled by returning None.

## State Changes:
Attributes READ:
    - self._section: the list of child subsections is iterated to find matches.
    - For each child s in self._section, s.title is read (which accesses s._title via the title property).

Attributes WRITTEN:
    - None. The method does not modify any attributes of self or its children.

## Constraints:
Preconditions:
    - self must be an initialized WikipediaPageSection with a populated self._section list (may be empty).
    - title must be provided as a value that can be compared to subsection titles (string expected).
    - Child items in self._section are expected to be WikipediaPageSection instances (or at least objects exposing a .title attribute that yields a comparable value).

Postconditions:
    - No mutation to self or children.
    - The return value is either the last matching subsection instance or None.
    - The ordering and contents of self._section are unchanged by this call.

## Side Effects:
    - None: there is no I/O, no network activity, and no modification to external state.
    - Only read operations on self and its child objects occur.

### `wikipediaapi.__init__.WikipediaPageSection.full_text` · *method*

## Summary:
Return a single string representing this section and all of its subsections, formatted according to the page's configured extract format (wiki-style headings or HTML headings). The method does not modify the section or page state.

## Description:
Known callers and typical lifecycle:
- WikipediaPage.text (property) calls this method for each top-level section to construct the full text of a page; in that usage it passes level=2 to start section headings at <h2> when HTML output is requested.
- Recursive calls: each section calls full_text on its subsections (sec.full_text(level + 1)) to assemble nested content.
- Consumers of the library may call full_text on any WikipediaPageSection after the page's "extracts" data has been fetched and sections have been populated.

Why this is its own method:
- Responsibility separation: formatting and recursive traversal of a section tree is encapsulated here so page-level logic can remain simple (e.g., WikipediaPage.text merely iterates top-level sections and concatenates results).
- Recursion and format-dependent behavior (wiki vs HTML) are non-trivial and are reused for each section; isolating them enables clear recursion, easier testing, and reuse.
- Centralizing the formatting logic avoids duplicating heading/spacing rules across the codebase.

## Args:
    level (int): The current heading/indentation level used for HTML formatting. Defaults to 1.
        - Expected domain: positive integers (1, 2, 3, ...). For HTML output, values 1..6 map to standard HTML heading tags <h1>.. <h6>; values outside 1..6 will still be inserted into the tag but may be non-standard HTML.
        - The method does not validate the numerical range beyond using the value in formatting.

## Returns:
    str: A concatenation of:
        - A representation of this section's title (plain title string for wiki-format, or an HTML heading element for HTML-format) followed by a single newline,
        - The raw section text (self._text),
        - If self._text is non-empty, two newline characters are appended after the text,
        - The full_text outputs of each subsection appended in order, each invoked with level + 1.
    Edge cases:
        - If this section has empty title, empty text, and no subsections, the returned string may be empty or consist only of whitespace/newline characters.
        - The string is returned as-is (untrimmed); callers that need trimmed results should call .strip() themselves (WikipediaPage.text calls .strip() after assembling page text).

## Raises:
    NotImplementedError:
        - Condition: self.wiki.extract_format is neither ExtractFormat.WIKI nor ExtractFormat.HTML.
        - Trigger: the code explicitly raises NotImplementedError("Unknown ExtractFormat type") in that case.
    Notes on implicit exceptions:
        - If self or self.wiki lacks the expected attributes/properties (e.g., wiki without extract_format), Python may raise AttributeError; these are not raised explicitly by this method.
        - If recursion depth is extremely large, Python may raise RecursionError; this is a consequence of recursive traversal and not an explicit check in the method.

## State Changes:
    Attributes READ:
        - self.wiki.extract_format (to decide between WIKI and HTML formatting)
        - self.title (property — accesses self._title)
        - self._text (directly read for body content)
        - self.sections (property — reads the list of subsection objects from self._section)
    Attributes WRITTEN:
        - None. The method does not mutate any attribute of self or of subsections; it only reads state and returns a string.

## Constraints:
    Preconditions:
        - The section object should have been constructed correctly (self._title is a string, self._text is a string, and self._section is a list of WikipediaPageSection instances).
        - For meaningful output, the page's "extracts" data should have been fetched so that sections and _text contain the content expected by callers (this is normally ensured by calling _fetch("extracts") before accessing sections at the page level).
        - self.wiki.extract_format must be a valid ExtractFormat member (ExtractFormat.WIKI or ExtractFormat.HTML) to avoid NotImplementedError.
    Postconditions:
        - The method leaves the section and page objects unchanged.
        - The returned string contains this section's title and text and then the recursively obtained contents of all subsections, formatted according to the extract_format and with nesting indicated by incrementing the level value for subsections.

## Side Effects:
    - No I/O or network calls are performed.
    - No mutation of global state or attributes of self/subsections is performed.
    - The only runtime effect is the construction and return of a potentially large string; for deeply nested section trees this may consume significant memory and may trigger RecursionError if recursion depth exceeds Python's limit.

### `wikipediaapi.__init__.WikipediaPageSection.__repr__` · *method*

## Summary:
Produce a multi-line string representation of the section that includes its title, level, text, and the repr() output of each immediate subsection. The call does not mutate the object.

## Description:
This is the special-method implementation that defines the object's representation returned by Python's built-in repr() for this instance. The method formats four pieces of data from the object and concatenates a newline-separated list of repr() results for items in the section container.

This logic is placed in the __repr__ method so that calling repr(instance) or printing an interactive representation yields a consistent textual summary produced by this object's own implementation.

## Args:
None.

## Returns:
str: A multi-line string with the exact structure produced by the format call in the source:
    Section: {self._title} ({self._level}):
    {self._text}
    Subsections ({len(self._section)}):
    {joined_child_reprs}
Where:
- {self._title} is converted via str() inside format.
- {self._level} is converted via format (typically an int or value with a string representation).
- {self._text} is converted via str().
- {len(self._section)} is the integer length of the section container.
- {joined_child_reprs} is the string result of "\n".join(map(repr, self._section)).
Edge cases:
- If self._section is empty, the "Subsections (0):" line appears and the joined_child_reprs portion is an empty string.
- If any attribute is None, its string "None" appears in the corresponding slot.

Example:
For an instance with
    self._title = "Overview"
    self._level = 2
    self._text = "Summary text"
    self._section = []
the returned string will be:
    Section: Overview (2):
    Summary text
    Subsections (0):

## Raises:
The method does not explicitly raise exceptions, but the following errors can propagate from operations it performs:
- AttributeError: if the instance lacks any of the attributes _title, _level, _text, or _section.
- TypeError: if len(self._section) is not supported because _section is not sized, or if self._section is not iterable such that map(repr, self._section) cannot iterate.
- Any exception raised by repr() called on an element of self._section will propagate.

## State Changes:
Attributes READ:
    - self._title
    - self._level
    - self._text
    - self._section
Attributes WRITTEN:
    - None. The method performs no assignments and does not mutate self.

## Constraints:
Preconditions:
    - The instance must have attributes named _title, _level, _text, and _section.
    - _section should be an iterable (and preferably sized) to produce a meaningful subsection count and to iterate child elements.

Postconditions:
    - Returns a str matching the format described above.
    - The instance remains unchanged.

## Side Effects:
    - None intrinsic to this method. It performs no I/O or network operations. Note: calling repr() on subsection elements executes those objects' __repr__ implementations, which may have side effects if those implementations perform them; such side effects are not caused directly by this method's logic beyond invoking repr().

## `wikipediaapi.__init__.WikipediaPage` · *class*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.__init__` · *method*

## Summary:
Initializes a WikipediaPage instance by attaching the parent Wikipedia client and creating empty in-memory containers, flags, and the attribute map containing the page's identifiers (title, namespace value returned by namespace2int, language, and optional full URL).

## Description:
This constructor prepares a newly-created page object for later population by API-driven methods. It centralizes the creation of internal empty caches and boolean flags so other code can assume a consistent object shape immediately after construction.

Known callers and lifecycle context:
- Typically invoked when higher-level code (for example, a Wikipedia client factory method such as a page() helper) constructs a page object.
- May also be called directly by user code that instantiates a page object.
- Runs once during object construction and establishes the initial instance state before any population methods (e.g., fetching extracts, links, categories) are invoked.

Why this logic is a dedicated constructor:
- Groups initialization of multiple internal containers, boolean flags, and the attribute map in one place to ensure uniform object shape and predictable initial state.
- Delegates any namespace normalization to the helper function namespace2int rather than implementing parsing/normalization logic in the constructor itself.

Behavioral boundaries (important):
- This constructor only records identifiers and initializes in-memory structures. It does not perform title localization, map titles to namespaces, execute network lookups, or perform other external I/O or parsing beyond calling namespace2int.
- The precise interpretation of the ns argument is delegated to namespace2int; the constructor stores whatever value that helper returns under the "ns" key.

## Args:
    wiki (Wikipedia):
        Parent Wikipedia client instance to associate with this page. Stored directly on the instance.
    title (str):
        Page title string stored under self._attributes["title"].
    ns (WikiNamespace | Namespace, optional):
        Namespace identifier passed to namespace2int; the value returned by namespace2int is stored in self._attributes["ns"]. Defaults to Namespace.MAIN.
    language (str, optional):
        Language code (e.g., "en"). Stored in self._attributes["language"]. Defaults to "en".
    url (str | None, optional):
        If provided (non-None), stored verbatim in self._attributes["fullurl"]. No validation or normalization is performed. Defaults to None.

## Returns:
    None
    The constructor does not return a value; it initializes instance state and returns implicitly.

## Raises:
    - Any exception raised by namespace2int(ns) will propagate out of this constructor (for example, if ns is an unacceptable input to that helper).
    - The constructor itself contains no explicit raise statements.

## State Changes:
Attributes READ:
    - No existing instance attributes are read; the constructor only assigns initial values.

Attributes WRITTEN:
    - self.wiki: set to the provided wiki argument.
    - self._summary: initialized to an empty string.
    - self._section: initialized to an empty list.
    - self._section_mapping: initialized to an empty dict.
    - self._langlinks: initialized to an empty dict (PagesDict).
    - self._links: initialized to an empty dict (PagesDict).
    - self._backlinks: initialized to an empty dict (PagesDict).
    - self._categories: initialized to an empty dict (PagesDict).
    - self._categorymembers: initialized to an empty dict (PagesDict).
    - self._called: initialized to a dict of boolean flags for "extracts", "info", "langlinks", "links", "backlinks", "categories", "categorymembers", all set to False.
    - self._attributes: initialized to a dict with keys:
        - "title": title (str)
        - "ns": value returned by namespace2int(ns)
        - "language": language (str)
      If url is not None, additionally:
        - self._attributes["fullurl"]: set to url (str)

## Constraints:
Preconditions:
    - Caller should supply a Wikipedia-like client for wiki and a title string.
    - The ns argument must be acceptable to namespace2int; otherwise namespace2int may raise.

Postconditions:
    - The instance contains empty caches and mappings for summary, sections, links, categories, backlinks, and related structures.
    - All _called flags are False, indicating the page has not yet been populated from the API.
    - self._attributes contains at least "title", "ns" (value from namespace2int), and "language"; "fullurl" exists only if url was provided.

## Side Effects:
    - No network requests, file I/O, or external service calls are performed by this constructor.
    - Only the new instance (self) is mutated; global state or external objects are not modified.

### `wikipediaapi.__init__.WikipediaPage.__getattr__` · *method*

## Summary:
Performs attribute access for lazily-populated page attributes: if the requested attribute is defined in the page's attribute-to-API-call mapping, return the cached value if present or trigger the minimal API fetch needed to populate it; otherwise delegate to normal attribute lookup.

## Description:
This method is Python's attribute fallback invoked when normal attribute lookup fails. It implements the WikipediaPage lazy-loading mechanism that maps certain attribute names (e.g., pageid, fullurl, displaytitle) to one or more API call groups (e.g., "info", "extracts", "langlinks") using ATTRIBUTES_MAPPING. On first access, when the attribute value is not cached in self._attributes, the method triggers the first unmade API call associated with that attribute via self._fetch(call) and then returns the value read from self._attributes[name].

Known callers and usage contexts:
- Any code that accesses attributes on a WikipediaPage instance (for example, page.pageid, page.fullurl, page.displaytitle) and which does not find the attribute via normal attribute lookup will call this method automatically.
- It participates in the lazy-loading pipeline for page metadata; properties and methods that access attributes sometimes call self._fetch directly (e.g., summary, sections, langlinks) but arbitrary attribute access that relies on ATTRIBUTES_MAPPING uses __getattr__ to trigger the first needed fetch.

Why this is a separate method:
- Centralizes attribute-to-API-call mapping logic and avoids duplicating lazy-fetch semantics across many properties.
- Keeps attribute access concise and supports on-demand population of _attributes from multiple possible API call groups in a predictable order.

## Args:
    name (str): The attribute name being accessed. Expected to be one of:
        - any key in self.ATTRIBUTES_MAPPING for dynamic/lazy attributes, or
        - any regular attribute name for normal lookup (in which case this method delegates to __getattribute__).
    Allowed values: keys of self.ATTRIBUTES_MAPPING (strings); other strings are allowed but will be handled by normal attribute lookup.

## Returns:
    Any: The value returned depends on the lookup path:
        - If name is not present in self.ATTRIBUTES_MAPPING: returns whatever self.__getattribute__(name) returns (or raises AttributeError if absent).
        - If name is in self._attributes: returns self._attributes[name] immediately (cached value).
        - If name is in ATTRIBUTES_MAPPING but not in self._attributes:
            * If an associated API call group exists whose `_called` flag is False, the method triggers that call (via self._fetch(call)) and then returns self._attributes[name] (value set by the fetch).
            * If all associated call groups are already marked called and they did not populate the attribute, the method completes without an explicit return, which results in returning None.

    Edge-case returns:
        - None is returned when name is a mapped attribute but no further fetch is possible (either mapping is empty or all mapped calls have already been performed and none populated the attribute).
        - The normal attribute-path may raise AttributeError (see Raises).

## Raises:
    AttributeError:
        - Triggered when name is not present in ATTRIBUTES_MAPPING and self.__getattribute__(name) cannot find the attribute (normal Python attribute error behavior).
        - Also possible indirectly if self._fetch or the delegated getattr(self.wiki, call) raises AttributeError (see below).
    KeyError:
        - If an entry in self.ATTRIBUTES_MAPPING[name] refers to a call key that is missing in self._called, the expression self._called[call] will raise KeyError.
    Any exception raised by self._fetch or the underlying wiki call:
        - self._fetch(call) calls getattr(self.wiki, call)(self). If the wiki object lacks the method named call, getattr(self.wiki, call) raises AttributeError.
        - Exceptions thrown by the wiki call implementation propagate up (e.g., network exceptions or custom errors raised by the API wrapper).

## State Changes:
    Attributes READ:
        - self.ATTRIBUTES_MAPPING (to determine whether the attribute is managed lazily and to iterate associated call groups)
        - self._attributes (to check if the requested name is already cached)
        - self._called (to determine whether a particular API call group has already been executed)

    Attributes WRITTEN (indirectly via self._fetch):
        - self._called[call] is set to True by self._fetch after performing the call
        - self._attributes may be populated or updated by the wiki call that self._fetch invokes
    Note: __getattr__ itself does not directly assign to these dictionaries, but calling self._fetch produces these mutations.

## Constraints:
    Preconditions:
        - self.ATTRIBUTES_MAPPING must be a mapping from attribute-name (str) to an iterable/list of call-group names (str).
        - self._called must be a mapping that contains boolean flags for the call-group names referenced in ATTRIBUTES_MAPPING (otherwise KeyError may occur).
        - self._fetch must be present and must perform the required side-effect of populating self._attributes for certain attributes and marking self._called[call] True.
        - name should be hashable and comparable to the keys in ATTRIBUTES_MAPPING (typically a str).

    Postconditions:
        - If a previously-unmade call-group was found and _fetch was invoked, then for that call-group call: self._called[call] is True after the call; self._attributes[name] may be present if the wiki call populated it.
        - If an attribute value is already cached in self._attributes, it is returned unchanged and no fetch is triggered.
        - If no fetch is possible (mapping empty or all mapped calls were already marked called) and no value exists in self._attributes, the method returns None (it does not raise AttributeError in this path).

## Side Effects:
    - May trigger network or I/O operations indirectly: self._fetch(call) calls getattr(self.wiki, call)(self), which typically performs API requests to the MediaWiki API.
    - Mutates self._called for the invoked call-group to True (via self._fetch).
    - May cause self._attributes to be populated or updated by the wiki call implementation (mutation of in-object cache visible to callers).
    - May raise exceptions originating from the underlying wiki object's call implementation (network errors, HTTP errors, or custom exceptions).

### `wikipediaapi.__init__.WikipediaPage.language` · *method*

## Summary:
Return the page's language code as a string; does not modify the page object.

## Description:
- Purpose and placement:
    - Provides a typed, read-only accessor for the language value stored in the page's internal attributes mapping.
    - Implemented as a property to present language as a stable metadata attribute alongside other properties such as title and namespace.
- Known callers and context:
    - There are no internal callers of this property inside the WikipediaPage class in the provided implementation.
    - Intended for external callers that need the page language (for display, routing, or serialization) after a WikipediaPage instance has been constructed.
- Why this is a separate property:
    - Encapsulates access to the underlying _attributes mapping and keeps the public API consistent with other page metadata properties.

## Args:
    None

## Returns:
    str: The language value converted to a string via str(self._attributes["language"]).
    - Typical values: ISO language codes like 'en', 'de', 'fr', etc., if the stored attribute is such a string.
    - Edge cases:
        - If the stored attribute is None, returns 'None' (because str(None) == 'None').
        - If the stored attribute is a non-string value (e.g., an int), its string representation is returned.

## Raises:
    KeyError: If self._attributes does not contain the "language" key. In the provided class, the constructor sets this key (default 'en'), so KeyError would only occur if _attributes has been mutated after construction.

## State Changes:
- Attributes READ:
    - self._attributes["language"]
- Attributes WRITTEN:
    - None

## Constraints:
- Preconditions:
    - The instance must be a properly initialized WikipediaPage with an _attributes dictionary present.
    - Preferably, self._attributes contains the "language" key (the constructor assigns it).
- Postconditions:
    - No mutation to the instance or external state.
    - Caller receives a string representation of the stored language attribute.

## Side Effects:
    - None: the property performs no I/O, network access, or mutation of objects outside self.

### `wikipediaapi.__init__.WikipediaPage.title` · *method*

## Summary:
Returns the page title as a string by reading the stored "title" entry from the page's internal attributes mapping. This does not modify the object.

## Description:
This accessor retrieves the value stored under the "title" key in the instance's internal _attributes mapping and converts it to a Python string with str(...). No additional computation or I/O is performed.

Known callers and invocation context:
- No internal callers were identified in the provided source for this method. In typical usage this method is called by client code or higher-level library utilities that need the human-readable title of a WikipediaPage instance (for display, logging, or export).
- Lifecycle stage: usually invoked after a page object has been created and populated (for example, after fetching page data from the API) when callers want a stable string representation of the page title.

Why this is a separate method:
- Encapsulates access to the internal _attributes mapping so callers do not need to know the storage layout.
- Ensures that the returned title is consistently a str (via str(...)) even if the stored value is not already a string.

## Args:
This is an instance method and takes no explicit parameters besides self.

- self: instance of WikipediaPage (expected to have a mapping-like attribute `_attributes`).

## Returns:
- type: str
- value: the string representation of whatever value is stored at self._attributes["title"].
- edge-case return values:
    - If the stored value is None, returns the string "None".
    - If the stored value is a non-string object (number, list, bytes, custom object), returns str(value), i.e., Python's conversion representation.
    - If the stored value is already a str, returns that string (possibly the same object or an equal string).

## Raises:
- AttributeError: if the instance has no attribute named _attributes (accessing self._attributes raises AttributeError).
- TypeError: if self._attributes does not support indexing with ["title"] (for example, if _attributes is None or not a mapping/subscriptable object).
- KeyError: if self._attributes is a mapping but does not contain the key "title".
These exceptions come directly from attempting to evaluate self._attributes["title"] and then calling str(...) on the result.

## State Changes:
- Attributes READ:
    - self._attributes (reads the mapping and the "title" entry)
- Attributes WRITTEN:
    - none (the method does not modify self or any external object)

## Constraints:
- Preconditions:
    - The caller should ensure that self._attributes exists and is a mapping-like object.
    - Preferably, the mapping should contain a "title" key whose value is set (but the method will raise KeyError if it is absent).
- Postconditions:
    - No mutations occur on self or on self._attributes.
    - The method returns a str corresponding to the stored title value's string representation.

## Side Effects:
- None: the method performs no I/O, no network calls, and does not mutate external objects.

### `wikipediaapi.__init__.WikipediaPage.namespace` · *method*

## Summary:
Returns the page's MediaWiki namespace index as an integer, providing a stable, typed view of the underlying 'ns' attribute.

## Description:
This property reads the internal _attributes mapping and converts the stored 'ns' value to an int so callers get a consistent numeric namespace index for the page.

Known callers and contexts:
- External consumers typically read this property after constructing or fetching a WikipediaPage when they need to decide logic by namespace (for example: skip non-main namespaces, route processing for talk pages, etc.). This occurs in the metadata/inspection stage of page processing.
- Internal class usage: the class exposes the raw 'ns' entry via attribute-access (`page.ns`) through __getattr__, and __repr__ uses that raw attribute. The typed property exists as the documented, explicit API for consumers who prefer a named property over the raw attribute key.
- Lifecycle: invoked any time callers need the namespace information (after instantiation or after a lazy fetch that populates _attributes).

Why this is a separate property:
- Centralizes the conversion to int and documents the intended meaning (namespace index) in one location instead of duplicating conversion logic across callers.
- Provides a stable, explicit API (page.namespace) that abstracts away the internal storage key ('ns').

## Args:
This is a read-only property; it takes no arguments.

## Returns:
int
- The namespace index derived from the page's internal 'ns' attribute (value produced by int(self._attributes["ns"])).
- Typical values: integer namespace identifiers as provided by MediaWiki (e.g., 0 for main namespace). The method does not validate semantic ranges — it simply converts and returns the integer value found in the attribute.
- Edge-case return behavior:
  - If the attribute exists and is convertible to int (e.g., numeric string, int), that integer is returned.
  - No special sentinel values are introduced by this property itself.

## Raises:
- KeyError: if the internal _attributes mapping does not contain the key "ns". This will happen if the object was mutated or constructed without providing an 'ns' entry.
- ValueError: if the value in _attributes["ns"] is a string that cannot be parsed as an integer (e.g., "invalid").
- TypeError: if the value is of a type not accepted by int() (e.g., None in some Python versions will raise a TypeError).

These exceptions come directly from performing int(self._attributes["ns"]) and from standard dict access semantics.

## State Changes:
Attributes READ:
- self._attributes (specifically self._attributes["ns"])

Attributes WRITTEN:
- None. This property performs no mutation to self or external objects.

## Constraints:
Preconditions:
- self._attributes must exist and be a mapping-like object containing the key "ns".
- The value stored at self._attributes["ns"] should be convertible to int for a successful, non-exceptional return.

Postconditions:
- No mutation of self is performed; after the call the object's state is unchanged.
- If the call completes normally, the caller receives the integer namespace index derived from the underlying attribute.

## Side Effects:
- None. The property performs no I/O, network access, or modification of external objects.

### `wikipediaapi.__init__.WikipediaPage.exists` · *method*

## Summary:
Return whether the represented page has a valid MediaWiki page id (pageid != -1). The result reflects the current value of the pageid attribute and may trigger the class's lazy-loading to resolve that value.

## Description:
This accessor answers the question "does this page exist on the wiki?" by checking the pageid stored on the object. Callers typically use it as a validation step before attempting content access (summary, sections, links, etc.).

Why this is a separate method:
- The existence check is a common, well-defined predicate used by clients; centralizing it avoids duplicating the sentinel check (pageid != -1).
- Accessing pageid can invoke the class's lazy-loading (__getattr__ and _fetch), so encapsulating the semantics and side effects in one method clarifies caller expectations.

Known callers / lifecycle context:
- External client code that inspects or filters WikipediaPage instances (for example, before requesting page.text or page.summary).
- Higher-level flows that enumerate titles and want to skip non-existent pages early.
- It is not used internally by other methods in this class (the class relies on attribute access and properties rather than calling exists()).

## Args:
    None

## Returns:
    bool
        - True if the resolved pageid is not equal to -1 (conventionally meaning the page exists).
        - False if the resolved pageid equals -1 (conventionally meaning the page does not exist).

    Important edge cases:
        - If pageid is not yet present in self._attributes, attribute access triggers the class's lazy-loading via __getattr__ which attempts to call the mapped API fetches. The boolean reflects the pageid value after that resolution attempt.
        - If no fetch is attempted because the mapped fetch flags are already marked True and the pageid is still absent, __getattr__ returns no explicit value (implicitly None). In that case the comparison None != -1 evaluates to True, so exists() will return True even though pageid is absent — this is a direct consequence of the current __getattr__ implementation.
        - If a fetch is attempted and fails (network error, API error, or internal exception), that exception propagates and no boolean value is returned.

## Raises:
    - Any exception raised during lazy-loading/fetch:
        * Trigger: accessing self.pageid when it is not present may cause __getattr__ to call self._fetch(call), which calls self.wiki.<call>(self). Any exception raised there (for example network errors from requests, API errors, or exceptions in the Wikipedia wrapper) will propagate through exists().
    - No exception is raised just by the boolean comparison itself.

## State Changes:
    Attributes READ:
        - self.pageid (via attribute access)
        - Implicitly may read self._attributes and self._called while resolving attributes in __getattr__
    Attributes WRITTEN:
        - If a fetch occurs, the fetch call may populate self._attributes["pageid"] (and other attributes).
        - If a fetch occurs, the corresponding self._called[call] flag(s) are set to True by _fetch.
    Note: If pageid is already present in self._attributes, no fetch occurs and no attributes are modified.

## Constraints:
    Preconditions:
        - self must be an initialized WikipediaPage instance (self.wiki and internal dicts set by __init__).
        - No parameters are required.

    Postconditions:
        - If attribute resolution ran and completed successfully, self._attributes will contain a pageid value (possibly -1) and the corresponding self._called[...] flags will be True.
        - If attribute resolution raised an exception, that exception will have propagated and no boolean is returned.
        - If no resolution was possible (pageid absent and no fetch attempted because mapped calls were already marked called), the method returns True due to Python semantics of comparing None to -1 (see Edge cases above).

## Side Effects:
    - May perform network I/O: resolving pageid can trigger self._fetch(call) which calls self.wiki.<call>(self) and typically results in HTTP requests to the MediaWiki API.
    - May mutate the page object by populating self._attributes (including pageid) and marking self._called[...] flags True.
    - No other external state is modified by this method itself.

## Usage note:
    - Prefer calling exists() before requesting page contents to avoid unnecessary fetch attempts for non-existent pages.
    - Be prepared to handle exceptions from network or API failures when calling exists(), since failed fetch attempts are propagated.

### `wikipediaapi.__init__.WikipediaPage.summary` · *method*

## Summary:
Returns the page's lead/introductory extract as a string. If the extract data has not yet been retrieved, triggers a lazy fetch of the 'extracts' data which will mark the extracts as loaded and populate the page's summary and related extract-derived attributes.

## Description:
This property is a lazy accessor for the page summary. When accessed it ensures the page's "extracts" data has been loaded, calling the page's internal fetch mechanism if necessary, and then returns the cached summary text.

Known callers and contexts:
- The page.text property calls this property to obtain the lead summary when assembling the full page text.
- Other page-level accessors and external consumer code may read this property directly to get a brief description/lead of the page.
- It is invoked at the point in a consumer workflow when a readable summary/lead is required (e.g., UI previews, searches, or text aggregation).

Why this is a separate method/property:
- Implements lazy-loading and caching for the extracts API call so that the expensive fetch is performed only when needed.
- Centralizes the logic that ensures the "extracts" API has been requested and the resulting data populated, avoiding duplication across multiple properties that depend on extracts.
- Maintains a clear separation of concerns: this accessor handles retrieval/caching semantics while the wiki-extraction implementation lives on the Wikipedia client object.

## Args:
None.

## Returns:
str: The summary (introductory extract) of the current page. Possible values:
- Non-empty string: the lead extract returned by the wiki's extracts API.
- Empty string: when the page has no extract available or the extracts API returned no summary. Note that the attribute is initialized to an empty string in the constructor, so an empty value is a valid return.

Edge-case return values:
- No value is returned if an exception is raised during the fetch; in that case the exception propagates and no string is returned.

## Raises:
None explicitly by this property. However, this property may propagate any exception raised by the internal fetch routine (self._fetch) or by self.wiki.extracts, for example network errors, API errors, or any other exceptions originating from the wiki client. Callers should be prepared to handle such exceptions if connectivity or API reliability is a concern.

## State Changes:
Attributes READ:
- self._called (reads self._called["extracts"] to determine whether to fetch)
- self._summary (read implicitly when returning it)

Attributes WRITTEN (via internal fetch):
- self._called["extracts"] is set to True by self._fetch once the extracts call completes.
- self._summary may be updated/overwritten by the wiki.extracts handler invoked through self._fetch.
- Other extract-derived attributes that the extracts handler populates may be modified as well (common ones include self._section and self._section_mapping).

Note: summary itself does not directly assign to attributes; mutations occur as side effects of calling self._fetch, which delegates to self.wiki.extracts(self).

## Constraints:
Preconditions:
- The WikipediaPage instance must be initialized (its __init__ sets up _called and _summary).
- The _called mapping must contain the "extracts" key (this is established by the constructor).
- The underlying wiki client must implement an extracts(page) callable; otherwise self._fetch will raise an AttributeError when attempting to call the method on the wiki object.

Postconditions:
- After successful completion, self._called["extracts"] == True.
- After successful completion, self._summary contains the latest summary text provided by the wiki client (possibly empty).
- The method returns the value currently stored in self._summary (type str).

## Side Effects:
- May perform I/O and API interaction: calling this property can trigger self._fetch("extracts"), which calls self.wiki.extracts(self). That delegate typically performs network requests to the MediaWiki API.
- May mutate the page object beyond _summary: the extracts handler may populate sections, section mappings, and other attributes derived from the extracts response.
- May raise exceptions originating from network/API calls or from the wiki client's extracts implementation; these are not caught here and will propagate to the caller.

### `wikipediaapi.__init__.WikipediaPage.sections` · *method*

## Summary:
Returns the page's list of section objects, lazily triggering the page's extracts fetch if the extracts have not yet been loaded; this may populate the page's internal section list and mark the extracts call as completed.

## Description:
Known callers and contexts:
- Client code that needs the page's section tree (e.g., documentation tools, rendering code, tests) will call this property to obtain the top-level sections.
- The WikipediaPage.text property iterates over this list to append each section's full_text when producing the page's combined text.
- Other consumers include tools that search or display section headings and subsections for a page.

Lifecycle / pipeline stage:
- This method is a lazy-loading accessor used at read-time. It ensures that the "extracts" data (which includes section headings and bodies) are available before returning the sections list. If extracts have already been fetched earlier in the page lifecycle, it simply returns the cached list.

Why this is its own method:
- The method centralizes the lazy-fetch-and-return pattern used for multiple page-level data pieces (the class uses the same pattern for summary, links, etc.). Keeping this logic in the property avoids duplicating the "check _called then _fetch" pattern and ensures consistent caching semantics for extracts across the class.

## Args:
- None

## Returns:
- List[WikipediaPageSection]: A reference to the internal list of top-level section objects for this page.
    - May be an empty list when the page contains no sections or when the fetched extracts contained no sections.
    - The returned list is the internal storage (self._section); mutating the returned list or its items will mutate the page's state.

## Raises:
- This method does not explicitly raise its own exceptions.
- It may propagate any exception raised by the underlying fetch machinery called via self._fetch (for example, network or parsing exceptions thrown by the wiki.extracts implementation). Those exceptions will bubble up to the caller.

## State Changes:
Attributes READ:
- self._called["extracts"] — to determine whether extracts must be fetched.
- self._section — read to return the current cached list.
- self.wiki — read indirectly when calling _fetch (used by _fetch to invoke the wiki method).

Attributes WRITTEN (directly or as a result of the fetch):
- self._called["extracts"] — set to True by self._fetch if a fetch occurs.
- Potentially self._section and self._section_mapping (and other extract-related attributes such as self._summary) when the underlying wiki.extracts implementation populates parsed data. The exact attributes populated are determined by the wiki.extracts implementation, but the library's parsing routines are responsible for filling self._section and self._section_mapping when extracts are fetched.

## Constraints:
Preconditions:
- self must be a fully-initialized WikipediaPage instance with a valid self.wiki reference (the page constructor establishes these).
- No particular argument validation is required (no args).

Postconditions:
- After returning, either:
    - If extracts were already fetched, the method returns the existing self._section value unchanged; or
    - If extracts had not been fetched, self._fetch("extracts") has been invoked, self._called["extracts"] is set to True, and the page's extract-related attributes (including self._section) reflect the latest data produced by the wiki.extracts implementation.
- The returned list object is the internal list stored on the page (not a defensive copy).

## Side Effects:
- May perform network or IO work indirectly by invoking self._fetch("extracts"), which calls the corresponding method on the parent Wikipedia instance (e.g., wiki.extracts(self)).
- Mutates page-level cache state when a fetch occurs (marks extracts as fetched and allows the wiki.extracts implementation to populate internal structures such as self._section and self._section_mapping).
- Any exceptions raised by the underlying fetch or wiki methods propagate to the caller.

### `wikipediaapi.__init__.WikipediaPage.section_by_title` · *method*

## Summary:
Return the last section object on this page whose title equals the provided string, performing lazy loading of extract data if necessary.

## Description:
This method is a public accessor used when callers (typically client code using the wikipediaapi library) need the most recent section matching a specific title from a WikipediaPage. It is invoked during the "read" phase of the page lifecycle — after a WikipediaPage has been constructed but before all API-backed fragments (extracts) have necessarily been fetched.

Known callers and contexts:
- External client code that inspects page structure and wants a single section by title (most common).
- Library consumers implementing features such as extracting a subsection's content, building search/highlight functionality, or CLI/tools that navigate a page's sections.
Note: There are no internal callers within this class that rely on section_by_title; internal code typically uses sections or sections_by_title. This method exists to provide a convenient single-section lookup with lazy-loading behavior.

Why this logic is its own method:
- Encapsulates a common read pattern: ensure extracts are loaded, lookup by title in the internal mapping, and return the last matching section.
- Keeps lazy-loading behavior and mapping lookup centralized so the rest of the codebase and callers do not need to replicate the extract-fetching guard.
- Provides a concise, user-facing API that complements sections_by_title (which returns all matches) and the sections property (which returns all sections).

## Args:
    title (str): The exact title to match against section titles stored on the page.
        - Allowed values: any string. Matching is done by exact equality of the stored title strings.
        - There is no special normalization performed by this method (e.g., no trimming or case normalization).
        - Must be provided; no default.

## Returns:
    Optional[WikipediaPageSection]:
        - If one or more sections with the given title exist in the page's internal section mapping, returns the last (most recently appended) WikipediaPageSection in that list.
        - If no matching sections exist, returns None.
        - Edge cases:
            * If a matching key exists but the associated list is empty, returns None (empty lists are treated as "no match").
            * If extracts have not been fetched, the method first attempts to fetch them; if that fetch populates matching sections, those are considered when determining the return value.

## Raises:
    - Propagated exceptions from the lazy-load operation:
        * AttributeError: if the underlying Wikipedia controller does not expose the expected fetch method (e.g., self.wiki.extracts missing) — raised by _fetch/getattr.
        * TypeError: if the resolved attribute on self.wiki exists but is not callable — raised by _fetch when attempting to call it.
        * Any exception raised by the invoked wikipedia fetch routine (for example network/HTTP errors, JSON parsing errors, or other runtime errors) will propagate unchanged.
    - This method does not raise its own exceptions for lookup misses; absence of a section is indicated by returning None.

## State Changes:
Attributes READ:
    - self._called: checked at key "extracts" to decide whether to lazy-load extracts.
    - self._section_mapping: consulted with .get(title) to retrieve any list of sections for the given title.
Indirectly READ (via _fetch):
    - self.wiki: resolved and invoked by _fetch when extracts must be fetched.

Attributes WRITTEN:
    - This method does not directly assign to any self.<attr>.
    - Indirect writes performed by the invoked self._fetch("extracts") (when called) may include:
        * self._called["extracts"] is set to True by _fetch after a successful fetch.
        * self._section and self._section_mapping may be populated/updated by the underlying Wikipedia fetch routine.
        * self._summary and other _attributes may be modified as a side-effect of the extracts fetch.

## Constraints:
Preconditions:
    - self must be an initialized WikipediaPage instance with:
        * a valid _called dict containing the "extracts" key (initialized in __init__).
        * a _section_mapping mapping (initialized in __init__).
    - title must be a string (the method signature enforces this via type annotation; callers should pass str).
Postconditions:
    - If _fetch("extracts") was invoked and completed without raising, self._called["extracts"] will be True.
    - If the method returns a WikipediaPageSection, it is the last element of the list stored at self._section_mapping[title] at the time of the lookup.
    - If the method returns None, no non-empty list of sections keyed by the provided title existed at lookup time.

## Side Effects:
    - Potential network I/O: If extracts are not yet loaded (self._called["extracts"] is False), this method will call self._fetch("extracts"), which delegates to the Wikipedia controller and typically performs HTTP requests to populate extracts. This can introduce latency and network-related exceptions.
    - Mutations outside the method's body: the invoked fetch may modify internal page state (see Attributes WRITTEN).
    - No file I/O or external side effects beyond those performed by the underlying Wikipedia fetch implementation.

### `wikipediaapi.__init__.WikipediaPage.sections_by_title` · *method*

## Summary:
Return the list of all section objects on this page that have the given section title, fetching section data first if necessary.

## Description:
This method is a convenience accessor used to look up every WikipediaPageSection for a given section title on the page. Typical callers:
- Client code that needs to inspect or iterate all sections with a specific title (e.g., to aggregate content or find duplicates).
- Other WikipediaPage helpers that need to operate on all sections with the same title.

It is implemented as its own method to encapsulate the common pattern of ensuring the page's "extracts" data is loaded before accessing the internal title→sections mapping, and to keep callers from duplicating the fetch-and-lookup logic.

The method will lazily trigger data loading for the "extracts" API call (via self._fetch("extracts")) if that call has not been performed for this page yet. That underlying fetch may perform network I/O and populate internal section-related attributes.

## Args:
    title (str): Section title to look up. Must be a string; exact match is used (case-sensitive as stored in self._section_mapping).

## Returns:
    List[WikipediaPageSection]: The list of WikipediaPageSection objects associated with the given title.
    - If sections exist for that title, returns the actual list object stored in self._section_mapping[title].
    - If no sections exist, returns a new empty list [].
    - The returned list is the internal list from the page's mapping when present (i.e., it is not a defensive copy). Mutating the returned list will mutate the page's internal state if the title exists.

## Raises:
    Any exception raised by the underlying fetch logic (self._fetch or the wiki.extracts implementation), for example network-related exceptions or API errors originating from the Wiki client. 
    Note: The method itself does not explicitly raise exceptions, but a KeyError will occur if the page object lacks the expected _called dictionary (this should not happen for properly constructed WikipediaPage instances).

## State Changes:
Attributes READ:
    - self._called (reads self._called["extracts"] to decide whether to fetch)
    - self._section_mapping (reads mapping to retrieve sections for the title)

Attributes WRITTEN (directly or indirectly via fetch):
    - self._called (self._fetch sets self._called["extracts"] = True if a fetch occurs)
    - self._section_mapping (may be populated or updated by the underlying extracts fetch; the method may cause this indirect write)
    - other section-related attributes (e.g., self._section) may also be populated by the extracts fetch

## Constraints:
Preconditions:
    - The WikipediaPage instance must be properly initialized (it must have _called and _section_mapping attributes as set in WikipediaPage.__init__).
    - title should be a string. Non-string values will be used as dictionary keys but are outside the expected contract.

Postconditions:
    - After the call, self._called["extracts"] will be True (if it was False before, because the method triggers a fetch).
    - If the underlying fetch succeeds, self._section_mapping will contain up-to-date section lists for the page and the returned value will reflect the mapping for the requested title.
    - If no sections exist for the given title, the method returns a fresh empty list [] and does not insert that empty list into self._section_mapping.

## Side Effects:
    - May perform network I/O indirectly by calling self._fetch("extracts"), which delegates to the wiki client's extracts handler.
    - Mutates self._called["extracts"] (set to True) and may mutate other internal attributes when the fetch populates data.
    - Because an internal list is returned when sections exist, callers mutating the returned list will mutate the page's internal state.

### `wikipediaapi.__init__.WikipediaPage.text` · *method*

## Summary:
Return the complete page text by concatenating the page summary and the rendered text of each top-level section; the property itself does not perform parsing but may trigger the page's lazy extract fetch.

## Description:
Known callers and lifecycle stage:
- Called by library consumers who access the page.text property to obtain readable page content for display, indexing, or analysis.
- Internally used after or during metadata access; it is typically invoked after a WikipediaPage has been constructed and possibly before extracts have been fetched.
- The property accesses the summary and sections properties; if extracts are not yet loaded, those properties call self._fetch("extracts") which delegates to the associated Wikipedia instance and sets the corresponding _called flag.

Why this is a separate property:
- It composes page-level content (summary + top-level sections) while delegating formatting and recursive traversal to WikipediaPageSection.full_text. Separating composition from per-section formatting keeps responsibilities clear and enables reuse of section rendering.

## Args:
    None (read-only property; no parameters).

## Returns:
    str: The assembled page text. Construction steps performed in order:
        1. Read page.summary and assign to a local variable txt.
        2. If txt is non-empty (len(txt) > 0), append two newline characters ("\n\n") to txt.
        3. Iterate over each section in page.sections in document order and append sec.full_text(level=2) to txt.
        4. Return txt.strip() (leading and trailing whitespace removed).
    Possible return values / edge cases:
        - "" (empty string) when summary is empty and there are no sections or all section outputs are empty/whitespace.
        - A trimmed string containing the summary and concatenated section texts in document order otherwise.

## Raises:
    - This property does not explicitly raise application-specific exceptions itself. However it may propagate exceptions originating from:
        - self.summary and self.sections property access, which may call self._fetch("extracts") and thereby raise network, parsing, or implementation-specific exceptions from the underlying Wikipedia methods.
        - section.full_text(level=2), which may raise NotImplementedError for unsupported extract_format or other exceptions (AttributeError, RecursionError, etc.).
    - In short: any exception raised by the lazy fetch or by section rendering will propagate; the property does not catch these exceptions.

## State Changes:
Attributes READ:
    - self.summary (property) — this property is read directly by the implementation.
    - self.sections (property) — this property is read directly by the implementation.
    - For each section: methods called on the section (sec.full_text) read section state.

Attributes WRITTEN (direct or indirect):
    - self._called["extracts"] is set to True by self._fetch("extracts") when summary or sections triggers a lazy fetch. (The _fetch method calls getattr(self.wiki, "extracts")(self) and then sets the flag.)
    - This property does not itself assign to self._summary or self._section; those internal attributes may be populated by the wiki.extracts implementation that _fetch delegates to, but such population is performed by the Wikipedia implementation, not by this property.

## Constraints:
Preconditions:
    - The WikipediaPage object should be validly constructed (it must have a working wiki reference and valid title/namespace).
    - Each element returned by self.sections must be a WikipediaPageSection instance with a functioning full_text method; otherwise sec.full_text(level=2) may raise exceptions.
    - If extracts have not been loaded, the associated Wikipedia instance must be able to handle the extracts call; otherwise the lazy fetch will raise errors.

Postconditions:
    - The returned string is the trimmed concatenation of the current summary and the full_text of top-level sections.
    - The page's _called["extracts"] flag will be True if a lazy fetch occurred; other internal attributes may be populated by the underlying Wikipedia.extracts implementation.

## Side Effects:
    - May trigger network I/O and parsing by causing a lazy call to the associated Wikipedia.extracts via self._fetch("extracts").
    - Allocates a new (potentially large) string containing the full page text — this can increase memory usage for large pages.
    - Does not perform file I/O, logging, or modify global state; it only reads properties and may cause the wiki-backed fetch to mutate the page's extract-related internals via the wiki implementation.

### `wikipediaapi.__init__.WikipediaPage.langlinks` · *method*

## Summary:
Return the page's language-links mapping; if language links have not been loaded yet, trigger a fetch that may populate the mapping and mark that fragment as fetched.

## Description:
This property provides lazy access to language-link data for the page. It checks the _called registry for the "langlinks" fragment; if that flag is False, it invokes the page's internal fetch mechanism to populate language links, then returns the page's internal container for language links.

Known callers and contexts:
- Any code that inspects or enumerates cross-language equivalents of a Wikipedia page, e.g., building multilingual references or resolving alternate-language page objects.
- Lifecycle stage: invoked on-demand during read-only inspection or data-collection workflows when language-link information is required for a WikipediaPage instance.

Why this logic is its own property:
- Encapsulates the simple lazy-loading pattern for the "langlinks" fragment so consumers can access an attribute without handling fetch bookkeeping.
- Maintains consistency with other page fragments (summary, links, categories) that use the same fetch-if-needed approach.

## Args:
    None

## Returns:
    PagesDict
    - The current value of self._langlinks (a mapping representing language links).
    - Possible values:
        - A mapping with language-link entries if language links exist and a successful fetch populated them.
        - An empty mapping if there are no language links or if a successful fetch found none.
    - Edge cases:
        - If a fetch is required but raises an exception, this property will not return a value; the exception propagates to the caller.
        - The concrete mapping object returned is exactly whatever is stored in self._langlinks at the moment of return; the fetch routine may either mutate the existing mapping or replace it with a new object.

## Raises:
    - Any exception raised by the invoked fetch path will propagate unchanged. Concretely:
        - AttributeError: if the Wikipedia controller lacks the expected fetch routine (raised by getattr inside _fetch).
        - TypeError: if the resolved attribute on the Wikipedia controller is not callable.
        - Any network, parsing, or application-level exception raised by the Wikipedia controller while performing the API request.
    - KeyError: if self._called does not contain the "langlinks" key (this is unlikely for a normally constructed WikipediaPage, because __init__ initializes this key).

## State Changes:
Attributes READ:
    - self._called["langlinks"]: inspected to decide whether to fetch.
    - self._langlinks: read to return the current mapping.
    - self._fetch (method): invoked if the _called flag is False.

Attributes WRITTEN:
    - This accessor does not assign attributes directly.
    - Indirect writes performed by self._fetch and the invoked Wikipedia controller (only occur on successful fetch):
        - self._called["langlinks"] will be set to True.
        - self._langlinks may be populated or replaced with fetched data.
        - Additional page state (e.g., entries in self._attributes, self._summary, sections, or other fragment containers) may be updated by the invoked fetch routine depending on its implementation.

## Constraints:
Preconditions:
    - self is a properly constructed WikipediaPage with:
        - an initialized _called mapping containing the "langlinks" key (initialized by __init__).
        - an initialized _langlinks container (initialized by __init__).
        - a working self.wiki controller that implements the fetch routine expected for "langlinks".

Postconditions:
    - If no fetch was required (self._called["langlinks"] is True at entry), the method returns immediately and no state is changed.
    - If a fetch was required and completes successfully:
        - self._called["langlinks"] will be True.
        - self._langlinks will reflect the fetched language-link data (possibly an empty mapping).
    - If a fetch was required and raises an exception:
        - The exception propagates to the caller.
        - self._called["langlinks"] will remain in its pre-call state (typically False).
        - self._langlinks may be unchanged or partially modified depending on what the invoked fetch routine did before failing.

## Side Effects:
    - May perform network I/O via the Wikipedia controller when a fetch is triggered.
    - May mutate internal page state (self._langlinks and self._called, plus any other fields the invoked fetch routine updates).
    - Does not catch or translate exceptions from the fetch machinery; errors propagate to the caller.

### `wikipediaapi.__init__.WikipediaPage.links` · *method*

## Summary:
Returns the cached mapping of pages linked from this page, lazily fetching the data from the wiki API on first access.

## Description:
This property is the public accessor for the links discovered on the current Wikipedia page. When accessed it ensures the links have been loaded (lazy-loading) by calling the page's internal fetch mechanism if necessary, then returns the stored PagesDict.

Known callers and call context:
- External callers (library users) that inspect or iterate links for a WikipediaPage instance (for example: to analyze outgoing links, build link graphs, or follow links programmatically). It is invoked at the point in a client workflow where the caller needs the set of pages referenced by the page.
- Internal callers: none in the class itself; the property is intended to be used by consumers of the WikipediaPage object rather than other internal methods.

Why this is a separate method/property:
- Implements lazy loading and caching: the actual API request and parsing are performed only on first access, avoiding unnecessary network calls and reducing latency for code that does not need links.
- Keeps API-access logic separate from simple attribute access: the property delegates fetching to _fetch("links") and then returns stored data, keeping the external interface simple while encapsulating side effects.

## Args:
- None (accessed as a property).

## Returns:
- PagesDict: the value of self._links after ensuring it is loaded.
  - Typical content: a mapping representing pages linked from this page (structure is the repository's PagesDict type).
  - Edge cases: may be an empty mapping if the page contains no links or if the wiki API returns no link data for the page.

## Raises:
- Any exception raised by the underlying fetch or wiki API call is propagated to the caller. In practice this includes:
  - Exceptions raised by self._fetch (for example, exceptions from getattr(self.wiki, "links")(self)).
  - Network or HTTP-related exceptions (e.g., requests exceptions) triggered by the wiki client's implementation.
- The property itself does not raise its own new exception types; it only triggers the underlying fetch when needed.

## State Changes:
Attributes READ:
- self._called (reads the "links" boolean flag to decide whether to fetch)
- self._links (the stored cached links mapping is returned)

Attributes WRITTEN (directly or indirectly via _fetch):
- self._called["links"] is set to True by self._fetch when a fetch occurs.
- self._links may be populated/modified by the wiki.links(self) implementation invoked during _fetch.

## Constraints:
Preconditions:
- self.wiki must be a valid Wikipedia client object with a callable links method (i.e., getattr(self.wiki, "links") must be callable and accept the page instance).
- The object must be a properly initialized WikipediaPage (self._called and self._links exist; this is true after __init__).

Postconditions:
- After the call completes successfully:
  - self._called["links"] == True (if the fetch was executed).
  - self._links contains the fetched PagesDict (possibly empty).
  - The returned value is exactly self._links (cached for subsequent accesses).

## Side Effects:
- May trigger a network/API call the first time it is accessed: self._fetch("links") calls getattr(self.wiki, "links")(self), which performs the actual API request and parsing.
- Causes modification of the page instance's internal state as noted in Attributes WRITTEN (caching).
- No other I/O or global side effects are performed by the property itself; any additional side effects depend on the implementation of the wiki.links(...) routine (e.g., logging, retries, rate-limiting).

### `wikipediaapi.__init__.WikipediaPage.backlinks` · *method*

## Summary:
Returns the mapping of pages that link to this page, lazily populating that mapping by delegating to the associated Wikipedia controller if it has not already been fetched.

## Description:
This property accessor implements a lazy-loading getter for the backlinks fragment of page data. When accessed, it ensures the page's backlinks have been retrieved from the Wikipedia instance (self.wiki) and then returns the stored mapping.

Known callers and call contexts:
- External callers (library users or other modules) that need the set of pages linking to this page will access page.backlinks. This is the primary entry point for clients requesting backlinks.
- Internal lazy-loading flow: the property is part of the WikipediaPage lazy-loading API alongside other properties such as summary, links, and categories. It is invoked during the normal lifecycle when code inspects or processes link relationships for a page (for example, when building link graphs, computing inbound references, or displaying "What links here" lists).

Why this is its own method/property:
- Separates the lazy-fetch pattern from consumers of backlinks: callers simply access the attribute without handling API calls, retries, or caching semantics.
- Keeps the property consistent with other lazy properties (links, langlinks, categories), centralizing when and how the associated Wikipedia controller is invoked (via WikipediaPage._fetch).

## Args:
    None.

## Returns:
    PagesDict: The in-memory mapping representing pages that link to this page. Exact structure is the repository's PagesDict type (documented elsewhere). Possible runtime values:
        - An empty mapping (the default initial state) when backlinks are absent or when the page has no inbound links.
        - A populated mapping after a successful fetch performed by the associated Wikipedia instance.
    Edge cases:
        - If the underlying fetch completes successfully but no backlinks exist, the returned mapping will be an empty mapping (not None).
        - If the fetch has not yet been performed, the property triggers the fetch and then returns whatever value the fetch populated.

## Raises:
    Any exception raised while attempting to fetch backlinks via the associated Wikipedia instance will propagate unchanged to the caller. Concrete examples include:
        - AttributeError: if the Wikipedia controller lacks a callable attribute named "backlinks" (raised by getattr in _fetch).
        - TypeError: if the resolved attribute exists but is not callable (raised when attempting to call it).
        - Network or parsing exceptions raised by the Wikipedia controller's implementation (e.g., HTTP errors, JSON decoding errors) — these propagate out of this property via the delegated _fetch call.

## State Changes:
Attributes READ:
    - self._called["backlinks"]: checked to determine whether a fetch is necessary.
    - self._backlinks: read to return the current value (or returned after _fetch populates it).

Attributes WRITTEN (direct):
    - None directly by this getter.

Attributes WRITTEN (indirect via _fetch):
    - self._called["backlinks"] is set to True after a successful delegated fetch.
    - The delegated fetch (self.wiki.backlinks(self)) may update internal page state, commonly including:
        - self._backlinks: populated with the fetched PagesDict
        - potentially other internal fields updated by the Wikipedia controller (see _fetch documentation)

## Constraints:
Preconditions:
    - The WikipediaPage instance must be properly constructed (self._called mapping exists and self.wiki references a valid Wikipedia controller).
    - Prefer that the Wikipedia controller implements a callable attribute named "backlinks"; otherwise an AttributeError/TypeError will occur when the property triggers a fetch.

Postconditions:
    - If the property returns normally (no exception), then either:
        - No fetch was needed and the previously cached self._backlinks is returned, or
        - A fetch was performed and self._called["backlinks"] is True and self._backlinks contains the fetched mapping (possibly empty).
    - If an exception is raised during fetching, self._called["backlinks"] will remain unchanged and the exception propagates.

## Side Effects:
    - May trigger network I/O and the full fetch lifecycle implemented by the Wikipedia controller (indirect effect via WikipediaPage._fetch).
    - May mutate the page's internal state (populate self._backlinks and set self._called["backlinks"] to True) as a result of the delegated fetch.
    - Does not perform logging, retries, or error wrapping itself; all such behavior (if any) is implemented by the invoked Wikipedia controller method.

### `wikipediaapi.__init__.WikipediaPage.categories` · *method*

## Summary:
Lazily loads and returns the cached mapping of categories associated with this page, triggering a fetch from the underlying Wikipedia instance on first access.

## Description:
This property is a lazy accessor used when client code or internal consumers request the categories for a page. On the first access it delegates to the page's wiki instance (via self._fetch which calls the underlying self.wiki.categories(self)) to populate and cache category data; subsequent accesses return the cached result without additional fetches.

Known callers and context:
- Client code that inspects page metadata (for example, scripts that enumerate a page's categories).
- Any higher-level utilities that traverse categories or build page metadata summaries.
In the typical lifecycle this property is invoked during data-extraction or analysis steps where category membership is required; it is intentionally implemented as a property to provide a convenient, attribute-like access pattern while performing lazy loading.

Why this logic is a separate method/property:
- Encapsulates lazy-loading and caching semantics in one place so callers do not need to manage network calls or caching.
- Keeps API-specific fetch logic separate (delegated to self.wiki and self._fetch), enabling reuse and single-point control of when the network call is made.

## Args:
None.

## Returns:
PagesDict
- A repository-specific alias (PagesDict) representing the mapping returned for categories. The exact shape of PagesDict is defined elsewhere in the codebase and is the same alias used by other page collection properties (links, langlinks, backlinks, etc.).
- Possible values:
  - A mapping object (commonly a dict-like type). If the page has no categories, this mapping may be empty.
  - The cached mapping from a previous access, in which case no network call is performed.

## Raises:
- The property itself does not explicitly raise exceptions. However, any exception raised by the underlying fetch (the call delegated through self._fetch -> self.wiki.categories(self)) will propagate to the caller. Typical causes include network errors or errors thrown by the wiki adapter implementation.

## State Changes:
Attributes READ:
- self._called["categories"] — checked to determine whether a fetch is required.
- self._categories — read to return the cached value.

Attributes WRITTEN:
- self._called["categories"] — set to True by self._fetch after the underlying wiki call completes.
- self._categories — populated/updated by the underlying wiki.categories implementation invoked via self._fetch.

## Constraints:
Preconditions:
- The WikipediaPage instance must be properly initialized (self.wiki present, self._called contains the "categories" key, and self._categories exists).
- The underlying wiki adapter must implement a categories(self_page) callable that populates the page's _categories.

Postconditions:
- After the property access completes (successfully), self._called["categories"] will be True.
- self._categories will reflect the result returned/populated by the underlying wiki.categories call (may be an empty mapping if there are no categories).
- The returned PagesDict is the same object stored in self._categories (i.e., subsequent modifications to the returned mapping may affect the cached value).

## Side Effects:
- May perform I/O: triggers the underlying wiki.categories call (via self._fetch) which typically makes API/network requests.
- Mutates state on the page object (sets the called flag and populates the cached categories mapping).
- No external state is modified by this property other than through the underlying wiki adapter (which may perform its own side effects, such as network traffic or logging).

### `wikipediaapi.__init__.WikipediaPage.categorymembers` · *method*

## Summary:
A read-only property that returns the page's internal mapping of category member pages; triggers a lazy API fetch to populate that mapping on first access if it is not already loaded.

## Description:
This property provides access to the PagesDict that represents pages belonging to this WikipediaPage when it denotes a category. It is implemented as a lazy-loading accessor: on first access it checks an internal flag and, if necessary, delegates to WikipediaPage._fetch("categorymembers") which calls the associated Wikipedia controller to perform the API query and populate the cache.

Known callers and contexts:
- Any external consumer that inspects category membership (for example, scripts or application code that traverse category trees, collect pages by category, or display members to users) will call this property.
- It participates in the class's lazy-loading lifecycle along with the other properties that fetch data on demand (summary, sections, langlinks, links, backlinks, categories).

Why this is a separate property:
- Encapsulates the standard lazy-fetch pattern (check cache flag → fetch → return cached data) so callers need not manage fetch logic.
- Keeps network/API concerns inside the Wikipedia controller and fetch orchestration inside _fetch, preserving a simple synchronous accessor interface on the page object.

Note:
- The implementation returns the internal container object (self._categorymembers) directly — it does not return a shallow or deep copy.

## Args:
None. This is accessed as a parameterless property.

## Returns:
PagesDict
- The internal mapping object self._categorymembers (initially set to an empty dict in __init__).
- After a successful lazy fetch, this mapping is populated with the fetched category members. It may still be an empty mapping if the category has no members.
- The returned object is the same dictionary stored on the page (i.e., the caller receives a reference to the internal cache).

Edge-case returns:
- If a fetch is attempted but fails (raises an exception), the accessor does not return a value; the exception propagates to the caller and self._categorymembers remains as it was before the call.

## Raises:
- AttributeError: If self.wiki has no attribute named "categorymembers" (raised by getattr in _fetch). In this case self._called["categorymembers"] is not modified.
- TypeError: If self.wiki.categorymembers exists but is not callable (raised when attempting to call it). In this case self._called["categorymembers"] is not modified.
- Any exception raised by the invoked Wikipedia controller method (for example network/HTTP errors, JSON parsing errors, or errors inside the controller). These exceptions propagate unchanged; when they occur, self._called["categorymembers"] will not be set to True.

## State Changes:
Attributes READ:
- self._called["categorymembers"]: consulted to determine whether to trigger a fetch.
- self._categorymembers: read and returned to the caller (when no fetch is required).

Attributes WRITTEN:
- This accessor performs no direct writes itself. However, if a lazy fetch is triggered:
  - WikipediaPage._fetch sets self._called["categorymembers"] = True after a successful delegated call.
  - The delegated Wikipedia controller method is responsible for writing/populating self._categorymembers with the fetched data.
  - Other fields the controller touches (e.g., self._attributes, self._summary, self._section, etc.) may be modified depending on the controller's implementation.

## Constraints:
Preconditions:
- The WikipediaPage instance must have been initialized via __init__ so that:
  - self._called contains the "categorymembers" key (initialized to False),
  - self._categorymembers exists (initialized to an empty dict {}),
  - self.wiki references a Wikipedia controller instance.

Postconditions:
- If the accessor returns normally after initiating a fetch, then:
  - self._called["categorymembers"] will be True,
  - self._categorymembers will hold the data populated by the Wikipedia controller (possibly an empty mapping).
- If the accessor returns without triggering a fetch (because self._called["categorymembers"] was already True), self._categorymembers will be returned unchanged.

## Side Effects:
- May trigger network I/O indirectly via WikipediaPage._fetch → self.wiki.categorymembers(self).
- May mutate internal page state as a result of the delegated fetch (notably self._categorymembers and self._called["categorymembers"]; other fields may also be updated by the controller).
- Exceptions from the underlying controller or network stack propagate to the caller; this accessor does not catch or wrap those exceptions.

### `wikipediaapi.__init__.WikipediaPage._fetch` · *method*

## Summary:
Ensure a particular fragment of page data is populated by delegating to the Wikipedia controller and, if the delegated call completes successfully, mark that fragment as fetched; returns the same page instance.

## Description:
A tiny helper encapsulating the common lazy-loading pattern: resolve a named fetch routine on the associated Wikipedia controller (self.wiki), invoke it with this page as the single argument, and then mark that fragment as fetched in the page's internal registry.

Known callers and contexts:
- WikipediaPage.__getattr__: triggered during attribute access when an attribute is mapped to API calls but not yet present in _attributes; __getattr__ calls this method to populate the attribute.
- Lazy-loading properties and accessors:
  - summary, sections, section_by_title, sections_by_title — invoke call "extracts"
  - langlinks — "langlinks"
  - links — "links"
  - backlinks — "backlinks"
  - categories — "categories"
  - categorymembers — "categorymembers"

Why this logic is a separate method:
- Centralizes the pattern of (1) delegating the fetch to the Wikipedia controller and (2) recording that the fetch was completed, avoiding duplicated call/mark logic across properties and __getattr__ paths.

## Args:
    call (str): Name of the method to call on self.wiki. Common/expected names (present in the page's initial _called mapping) are:
        "extracts", "info", "langlinks", "links", "backlinks", "categories", "categorymembers".
    Any other string will be looked up on the Wikipedia object; behavior depends on whether that attribute exists and is callable.

## Returns:
    WikipediaPage: Returns self (the same WikipediaPage instance). Any value returned by the invoked self.wiki.<call> is ignored by this method.

## Raises:
    AttributeError: If self.wiki does not have an attribute with the name given by call (raised by getattr). In this case, self._called is not modified.
    TypeError: If self.wiki.<call> exists but is not callable (raised when attempting to call the resolved attribute). In this case, self._called is not modified.
    Any exception raised by the invoked Wikipedia method (for example network errors, JSON parsing errors, or application-level errors inside Wikipedia._build_* helpers) will propagate unchanged; if such an exception occurs, self._called[call] is not set to True.

## State Changes:
Attributes READ:
    - self.wiki: consulted to resolve the attribute/method named by call.

Attributes WRITTEN:
    - self._called[call]: set to True only after the getattr succeeds and the invoked self.wiki.<call>(self) returns without raising an exception.
    - Indirect writes performed by the invoked Wikipedia method (depending on call) may include updates to:
        - self._attributes (e.g., title, pageid, ns, and other info fields)
        - self._summary
        - self._section and self._section_mapping
        - self._langlinks, self._links, self._backlinks
        - self._categories, self._categorymembers

Notes:
    - If call is not present in the initial _called mapping, this method will create or update the key only after a successful call (i.e., assignment to self._called[call] occurs only on successful completion).
    - The method does not examine or return the result of the invoked Wikipedia method.

## Constraints:
Preconditions:
    - self must be a properly constructed WikipediaPage with an associated Wikipedia instance accessible at self.wiki.
    - The page's _called mapping should exist (it is initialized in __init__).
    - Prefer passing a call name implemented by the Wikipedia object to avoid AttributeError/TypeError.

Postconditions:
    - If the method returns normally (no exception), self._called[call] will be True.
    - If the method raises before completing (either getattr failure, non-callable attribute, or error inside the wiki method), self._called will be unchanged with respect to this call.
    - Page state may be updated by the invoked method as appropriate for that call (see Attributes WRITTEN).

## Side Effects:
    - Network I/O: The invoked Wikipedia method commonly performs HTTP requests via Wikipedia._query, so calling _fetch may trigger network activity and associated latency.
    - Mutations: Updates internal page state and may add a new key to self._called only after a successful call.
    - Error propagation: This method does not catch or wrap exceptions from getattr or the invoked method; they bubble up to the caller.

### `wikipediaapi.__init__.WikipediaPage.__repr__` · *method*

## Summary:
Return a concise, human-readable representation of the WikipediaPage that includes the page title, namespace, and either the numeric pageid (if any page-data fetches have occurred) or a placeholder "??" when the id is not known.

## Description:
This method is the object's representation used by Python's built-in repr() (and by printing, logging, REPL inspection when __str__ is not provided). Typical callers and contexts:
- repr(page) or f"{page!r}" in client code, tests, or interactive shells.
- Logging or debugging code that formats WikipediaPage instances.
- Containers (e.g., lists or dicts) that display contained WikipediaPage objects.

Lifecycle context:
- It is invoked whenever a developer or library code needs a compact, human-readable summary of the page object for diagnostics or display.
- It is not part of the lazy-fetch pipeline's core data-fetching logic, but its attribute accesses can trigger lazy fetches (see Side Effects).

Why this is a separate method:
- Provides a compact, stable textual summary useful for debugging and logging.
- Keeps presentation logic out of core fetching methods and avoids duplicating the formatting used across the codebase.

## Args:
This method accepts no arguments.

## Returns:
str: A formatted string in one of two forms:
- If any of the page's fetch flags are True (i.e., some data has been fetched for this page):
    "<title> (id: <pageid>, ns: <ns>)"
  where <pageid> is the numeric id (as provided by the page attributes) and <ns> is the namespace integer.
- If none of the fetch flags are True:
    "<title> (id: ??, ns: <ns>)"
  where the id is replaced with "??" to indicate the page id is not yet known.

Edge-case return values:
- If attribute access to pageid or ns returns values other than expected (e.g., None), those values will be stringified in the returned representation.
- The returned string always includes the title and an ns representation; id is either numeric (stringified) or the literal "??".

## Raises:
This method does not directly raise exceptions, but may propagate exceptions raised during attribute access:
- If accessing self.pageid or self.ns triggers the lazy loader (__getattr__ → _fetch), those underlying fetch calls may perform network I/O and can raise network-related exceptions (for example, exceptions from requests or errors raised by the Wikipedia fetch routines). Such exceptions are not caught here and will propagate to the caller.

## State Changes:
Attributes READ:
- self._called (reads its values via any(self._called.values()) to decide which form to return)
- self.title (accesses the title; implemented as a property that reads self._attributes["title"])
- self.pageid (accesses page id; may invoke __getattr__ and lazy fetch if not present)
- self.ns (accesses namespace; may invoke __getattr__ and lazy fetch if not present)

Attributes WRITTEN (indirect / possible):
- None directly in this method. However, because attribute access may trigger __getattr__ and the internal _fetch(call) call:
    - self._called[call] may be set to True for the call(s) executed by _fetch
    - self._attributes[...] may be populated with fields such as "pageid" and "ns"
  Therefore, calling __repr__ can indirectly modify self._called and self._attributes.

## Constraints:
Preconditions:
- self._attributes must contain a valid "title" value (the class constructor sets this). If "title" is missing, accessing self.title may raise KeyError from the property implementation.
- The object should be a properly-initialized WikipediaPage (i.e., wiki, _called, and _attributes set up by __init__). Calling __repr__ on a partially-constructed object may produce unexpected results.

Postconditions:
- The returned string will always include the title and namespace representation.
- After the call, one or more entries in self._called may be True and corresponding entries in self._attributes may be filled if attribute access triggered lazy fetches. There is no guarantee that pageid will be available after the call (it depends on which fetches ran and whether they populated pageid).

## Side Effects:
- Implicit I/O: Evaluating expressions inside the returned string (self.pageid, self.ns) can invoke __getattr__, which may call self._fetch(call). That in turn calls the corresponding method on self.wiki and typically performs network I/O to the MediaWiki API.
- Mutations: As a consequence of implicit fetching, self._called entries may be changed from False to True and new keys may be inserted into self._attributes (for example, "pageid" or "ns").
- Exceptions from underlying fetch/network operations may propagate out of __repr__ to the caller.

## Implementation Notes (for reimplementation):
- Evaluate any(self._called.values()) first to choose whether to show the real id or "??".
- Build and return an f-string (or equivalent formatted string) that includes title, pageid (or "??"), and namespace.
- Do not catch exceptions from attribute access/fetching in __repr__; let them propagate as in the original design.
- Be aware that attribute access order in the formatted string will determine which lazy fetches run and when state is modified.

