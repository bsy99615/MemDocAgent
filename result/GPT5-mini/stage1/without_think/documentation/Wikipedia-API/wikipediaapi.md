# `wikipediaapi`

## Tree:
wikipediaapi/
└── __init__.py

## Role:
Provide the MediaWiki HTTP client, page/section models, and small enums/helpers needed to request, parse, and represent Wikipedia (MediaWiki) content. The module owns the client-side API surface for fetching page extracts, metadata, and related lists and for representing that data in-memory with lazy-loading semantics.

## Description:
Where and when this module is used:
- Primary consumers: application code that needs to read or inspect Wikipedia/MediaWiki content. Typical flow:
  1. Construct a Wikipedia client for a language: Wikipedia(user_agent="...", language="en")
  2. Obtain a page model: page = wiki.page("Title")
  3. Use either the Wikipedia client methods to perform eager fetches (wiki.extracts(page), wiki.links(page), etc.) or access page properties that lazily fetch data on first use (page.summary, page.links, page.categories, ...).
- Why grouped: the module groups the HTTP client (session and API plumbing), the parsing logic that understands MediaWiki JSON and extract formats, and the in-memory page/section models. These pieces are tightly cohesive: the Wikipedia client performs network I/O and parsing, while WikipediaPage and WikipediaPageSection expose a convenient, cached view of page data.

Related component docs (refer to component-level documentation for full reimplementation details):
- wikipediaapi.__init__.ExtractFormat
- wikipediaapi.__init__.Namespace
- wikipediaapi.__init__.namespace2int
- wikipediaapi.__init__.Wikipedia and all of its helpers (_query, _common_attributes, _build_extracts, _create_section, _build_links, _build_backlinks, _build_langlinks, _build_categories, _build_categorymembers)
- wikipediaapi.__init__.WikipediaPage and its members (constructor, __getattr__, _fetch, lazy properties)
- wikipediaapi.__init__.WikipediaPageSection

## Components:
Public classes, functions, and constants (signatures and one-line role each):

- USER_AGENT: str
  - Role: module-level string appended to the HTTP User-Agent header performed by Wikipedia instances.

- RE_SECTION: dict[ExtractFormat, re.Pattern]
  - Role: regex patterns keyed by ExtractFormat used to find section headings in extract text.

- log: logging.Logger
  - Role: module logger for informational/debug messages.

- class ExtractFormat(enum.IntEnum)
  - Members: WIKI = 1, HTML = 2
  - Role: indicate the output/parse format for extracts (wikitext-like subsection semantics vs. HTML).

- class Namespace(enum.IntEnum)
  - Role: canonical MediaWiki namespace identifiers; a pure mapping of names → integer ids. It contains only identifiers and does not perform lookups, localization, or title-to-namespace mapping.

- def namespace2int(namespace: Union[int, Namespace]) -> Union[int, Any]
  - Role: small helper that converts a Namespace enum member to its integer .value; otherwise returns the input unchanged. Boundary: this function only normalizes Enum→int and does not attempt to validate arbitrary inputs.

- class Wikipedia
  - __init__(user_agent: str, language: str = "en", extract_format: ExtractFormat = ExtractFormat.WIKI, headers: Optional[dict] = None, **kwargs)
    - Role: create a per-language MediaWiki client with a requests.Session, default headers (User-Agent must be > 5 chars) and stored request kwargs (timeout, proxies, etc.).
  - __del__() -> None
    - Role: close the requests.Session when the instance is finalized.
  - page(title: str, ns: Union[int, Namespace] = Namespace.MAIN, unquote: bool = False) -> WikipediaPage
    - Role: factory that constructs a WikipediaPage bound to this client (no network I/O).
  - article(...) -> WikipediaPage
    - Role: alias for page(...).
  - _query(page: WikipediaPage, params: dict) -> dict
    - Role: perform a single HTTP GET to the MediaWiki API for page.language; ensures "format"="json" and "redirects"=1 in params; returns parsed JSON. Raises network/JSON exceptions from requests.
  - _common_attributes(extract: dict, page: WikipediaPage) -> None
    - Role: copy shared fields (title, pageid, ns, redirects) from API dicts into page._attributes in-place.
  - extracts(page: WikipediaPage, **kwargs) -> str
    - Role: call MediaWiki prop=extracts, merge parameters (method's params overwrite kwargs of same name), call _build_extracts to populate page._summary and page._section trees, and return the summary string. If API indicates missing page (page id "-1"), sets page._attributes["pageid"] = -1 and returns "".
  - info(page: WikipediaPage, **kwargs) -> WikipediaPage
    - Role: call prop=info and copy returned per-page fields into page._attributes via _build_info; returns the mutated page.
  - links(page: WikipediaPage, **kwargs) -> dict[str, WikipediaPage]
    - Role: call prop=links, follow MediaWiki continuation tokens to aggregate results, and call _build_links to set page._links and return that mapping.
  - backlinks(page: WikipediaPage, **kwargs) -> dict[str, WikipediaPage]
    - Role: call list=backlinks, follow continuation tokens, and call _build_backlinks to set page._backlinks and return it.
  - langlinks(page: WikipediaPage, **kwargs) -> dict[str, WikipediaPage]
    - Role: call prop=langlinks, apply _build_langlinks to set page._langlinks and return it.
  - categories(page: WikipediaPage, **kwargs) -> dict[str, WikipediaPage]
    - Role: call prop=categories and use _build_categories to set page._categories and return it.
  - categorymembers(page: WikipediaPage, **kwargs) -> dict[str, WikipediaPage]
    - Role: call list=categorymembers, follow continuation, and call _build_categorymembers to set page._categorymembers and return it.

- class WikipediaPage
  - __init__(wiki: Wikipedia, title: str, ns: Union[int, Namespace] = Namespace.MAIN, language: str = "en", url: Optional[str] = None)
    - Role: in-memory model for a page; sets up caches, _attributes mapping (contains title, ns, language, optional fullurl) and _called flags for lazy fragments. Does not perform network I/O.
  - __getattr__(name: str)
    - Role: lazy attribute resolver. If name is mapped in ATTRIBUTES_MAPPING to one or more wiki method names, triggers the earliest un-called wiki call (via _fetch) to populate attributes and then returns value from _attributes[name] if present. Otherwise behaves like normal attribute lookup (raises AttributeError).
  - _fetch(call: str) -> WikipediaPage
    - Role: call getattr(self.wiki, call)(self) to have the Wikipedia instance populate this page; on successful return, set self._called[call] = True and return self. Propagates exceptions from the wiki call.
  - Properties and lazy accessors (all are read-only and may trigger network fetches on first access):
    - title -> str: returns str(self._attributes["title"]) (no network).
    - language -> str: returns str(self._attributes["language"]) (no network).
    - namespace -> int: returns int(self._attributes["ns"]) (no write-side effects).
    - summary -> str: ensures extracts are fetched (via _fetch("extracts") if needed), then returns self._summary.
    - sections -> List[WikipediaPageSection]: ensures extracts fetched, returns self._section.
    - sections_by_title(title: str) -> List[WikipediaPageSection]: ensures extracts fetched, returns list of sections matching title (may be empty).
    - section_by_title(title: str) -> Optional[WikipediaPageSection]: ensures extracts fetched, returns last matching section or None.
    - text -> str: composes summary + each top-level section.full_text(...) and returns trimmed string (may trigger extracts fetch).
    - links -> PagesDict: lazy property; if not loaded, calls _fetch("links") which causes self.wiki.links(self) to run and populate self._links; returns the cached mapping.
    - backlinks, langlinks, categories, categorymembers: analogous lazy properties delegating to _fetch with respective call names.
    - exists() -> bool: returns whether pageid != -1; may trigger lazy loading of pageid.
  - Note: ATTRIBUTES_MAPPING (internal mapping) defines which attribute names map to which wiki call groups; __getattr__ and _fetch consult this mapping.

- class WikipediaPageSection
  - __init__(wiki: Wikipedia, title: str, level: int = 0, text: str = "")
    - Role: node representing a page section: title, numeric level, plain-text body, and list of subsections.
  - Properties: title, level, text, sections (list)
  - section_by_title(title: str) -> Optional[WikipediaPageSection]
    - Role: return the last child whose title matches exactly, or None.
  - sections_by_title(title: str) -> List[WikipediaPageSection]
    - Role: return all child subsections with the given title (may be empty).
  - full_text(level: int = 1) -> str
    - Role: format and return this section and all subsections into one string according to wiki.extract_format. Raises NotImplementedError for unknown extract formats.

- PagesDict (type alias)
  - Role: mapping type used by link/category/backlink/langlink returns (title or language code → WikipediaPage). Concrete type in implementation is typically dict[str, WikipediaPage].

Mermaid dependency graph (internal relationships):
graph LR
    ExtractFormat
    Namespace
    USER_AGENT
    RE_SECTION
    namespace2int
    Wikipedia -->|creates| WikipediaPage
    Wikipedia -->|parses extracts via| _build_extracts
    _build_extracts --> _create_section
    _create_section --> WikipediaPageSection
    Wikipedia -->|performs HTTP| _query
    _query --> requests[requests.Session]
    Wikipedia --> _common_attributes
    Wikipedia -->|builds| _build_links & _build_backlinks & _build_langlinks & _build_categories & _build_categorymembers
    WikipediaPage -->|lazy-fetches via| self._fetch --> Wikipedia
    WikipediaPage -->|contains| WikipediaPageSection
    style Wikipedia fill:#e8f3ff,stroke:#333,stroke-width:1px

## Public API (concise, actionable):
- Wikipedia(user_agent: str, language: str = "en", extract_format: ExtractFormat = ExtractFormat.WIKI, headers: Optional[dict] = None, **kwargs)
  - Create a client. Must provide a descriptive user_agent (length > 5). kwargs default to timeout=10.0 unless overridden.
- wiki.page(title: str, ns: Union[int, Namespace] = Namespace.MAIN, unquote: bool = False) -> WikipediaPage
  - Create a page object; no HTTP I/O.
- wiki.extracts(page, **api_kwargs) -> str
  - Fetch extracts for page; merges api_kwargs but method-enforced params overwrite colliding keys; populates page._summary and page._section via _build_extracts.
- wiki.links(page, **api_kwargs) -> PagesDict
  - Fetch outgoing links and populate page._links (follows continuation).
- wiki.langlinks/backlinks/categories/categorymembers/info: similar semantics (see component docs).
- page.summary, page.sections, page.links, page.langlinks, page.backlinks, page.categories, page.categorymembers, page.text
  - Lazy properties on WikipediaPage. On first access each may call page._fetch(call) which invokes the corresponding wiki.<call>(page) method and marks that fragment as fetched. Subsequent accesses return cached values.

Usage notes:
- If deterministic session teardown is required, delete the Wikipedia instance (or let it go out of scope) to trigger __del__ closing the underlying requests.Session; no explicit close() is provided.
- When calling wiki.* methods that accept **kwargs (API parameters), be aware that the library merges caller kwargs and then updates with method defaults; defaults overwrite same-named caller keys. Continuation requests intentionally use the internal params dict (so caller kwargs are only included on the initial request).
- Callers should be prepared to catch network-related exceptions (requests.exceptions.RequestException) and JSON parsing errors (json.JSONDecodeError/ValueError) from wiki methods.
- Use namespace2int(Namespace.MAIN) when an API parameter requires an integer namespace id; the function only normalizes Enum→int and passes through other inputs.

## Dependencies:
Internal:
- This module composes the Wikipedia client (network + parsing) and the page model classes. See the component docs for exact builder behaviors and object mutation points.

External:
- requests: persistent Session for HTTP GET calls.
- re, logging, enum, urllib.parse: stdlib utilities used for parsing, logging, enums, and optional URL-unquoting.

## Constraints:
- Caller must provide a valid user_agent (non-empty and > 5 chars after construction logic) or a headers dict containing an adequate "User-Agent".
- language must be non-empty after strip().lower() or __init__ asserts.
- The Wikipedia instance stores a requests.Session; the module is not thread-safe by default—concurrent use across threads requires external synchronization.
- Many methods mutate the provided WikipediaPage (attach caches in-place). Callers should treat page objects as mutable and expect side effects.
- RE_SECTION patterns must match the capture-group expectations used by _create_section for each ExtractFormat; reimplementation must preserve those group semantics.

## Minimal example (pseudocode):
- Create a client and a page:
  wiki = Wikipedia(user_agent="myapp/1.0 (you@example.com)", language="en")
  page = wiki.page("Python_(programming_language)")
- Lazy fetch summary:
  summary = page.summary        # triggers wiki.extracts(page) on first access
- Eager fetch links:
  links = wiki.links(page)      # calls API immediately and populates page._links

For full implementation details (exact parameter names, error semantics, and builder behaviors), consult the component-level documentation referenced at the top of this doc. The component docs contain reimplementation recipes and exact mutation points needed to reproduce the module faithfully.

---

## Files

- [`__init__.py`](wikipediaapi/__init__.md)

