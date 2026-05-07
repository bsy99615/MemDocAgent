# `Wikipedia-API`

## Tree:
Wikipedia-API/
    wikipediaapi/               # Primary package: HTTP client, parsing logic, page and section models
        __init__.py             # Public API surface for constructing clients and page models
    example.py                  # Small example/debug utilities that format/print page data (print_links, print_sections, print_categories, print_langlinks, print_categorymembers, etc.)
    setup.py                    # Packaging helpers (including setup.fix_doc used to sanitize long descriptions before publishing)

## Purpose:
- What it solves:
    - Provides a lightweight, client-side Python API for reading and representing content from MediaWiki-powered sites (notably Wikipedia). It wraps the MediaWiki JSON API, parses common response shapes (extracts, links, categories, langlinks, backlinks, categorymembers, info), and exposes an in-memory, lazy-loading page model so callers can access page text, sections, and related lists with minimal boilerplate.

- Why it matters:
    - Makes it simple to fetch and inspect Wikipedia content programmatically with consistent, cached objects and helpers for common inspection/printing tasks. Useful for scripts, data extraction, tests, and small applications that need reliable read-only access to wiki content.

- Target users and scenarios:
    - Developers building tools or scripts that read Wikipedia/MediaWiki content (extractors, bots, documentation generators, research tooling).
    - REPL and CLI users who want quick inspection helpers (via example.py utilities).
    - Integrations that need a simple wrapper around MediaWiki API without adopting a heavy dependency.

- Positioning in the ecosystem:
    - A standalone client library (importable package) intended to be embedded in applications or used interactively. Not a hosted service or server — it performs direct HTTP calls to configured MediaWiki endpoints.

## Architecture:
- Key abstractions:
    - Wikipedia (client): encapsulates an HTTP session, API parameter handling, and builder functions that populate page model fragments (extracts, links, categories, etc.).
    - WikipediaPage (model): in-memory, mutable page object with attribute caching and lazy fetch semantics; maps accessors to Wikipedia methods.
    - WikipediaPageSection: tree node representing a page section (title, level, text, child sections) and formatting according to extract format.
    - Small enums/helpers: ExtractFormat (WIKI vs HTML), Namespace enum, namespace2int conversion helper, module-level constants (USER_AGENT), and RE_SECTION regex patterns to parse extracts.

- End-to-end data flow (Mermaid flowchart):
flowchart TD
    User[User code] -->|import & construct| WikipediaClass[Wikipedia(user_agent, language, ...)]
    WikipediaClass -->|wiki.page(title)| PageObj[WikipediaPage(title)]
    User -->|access lazy prop| PageObj
    PageObj -->|on first access call| WikipediaClass
    WikipediaClass -->|_query -> HTTP GET| Requests[requests.Session]
    Requests -->|JSON response| WikipediaClass
    WikipediaClass -->|parsing/builders| Builders[_build_extracts/_build_links/_build_categories/_build_langlinks/_build_backlinks/_build_categorymembers/_common_attributes]
    Builders -->|instantiate nodes| PageSection[WikipediaPageSection]
    Builders -->|populate caches| PageObj
    PageObj -->|cached reads| User

- Architectural patterns:
    - Lazy loading / cache-on-first-access: WikipediaPage properties map to grouped wiki calls; the first access triggers the corresponding network call and subsequent accesses read cached fields.
    - Builder pattern: Wikipedia methods parse API JSON and use focused builder functions (_build_extracts, _create_section, _build_links, etc.) to construct objects and attach them to WikipediaPage instances.
    - Session-per-client: Wikipedia owns a requests.Session for connection reuse; no explicit thread-safety guarantees.

## Entry Points:
- Importable API (primary):
    - from wikipediaapi import Wikipedia, WikipediaPage, WikipediaPageSection, ExtractFormat, Namespace, namespace2int
    - Usage:
        - Wikipedia(user_agent: str, language: str = "en", extract_format: ExtractFormat = ExtractFormat.WIKI, headers: Optional[dict] = None, **kwargs)
            - Create a client. user_agent must be a descriptive string (> 5 characters). kwargs commonly include network parameters (timeout, proxies) and are stored for requests.
        - wiki.page(title: str, ns: Union[int, Namespace] = Namespace.MAIN, unquote: bool = False) -> WikipediaPage
            - Construct a page object bound to the client (no network I/O).
        - wiki.extracts(page, **api_kwargs), wiki.links(page, **api_kwargs), wiki.langlinks(page,...), wiki.backlinks(...), wiki.categories(...), wiki.categorymembers(...), wiki.info(...)
            - Methods that perform the corresponding MediaWiki API calls, populate page caches, and return extracted data. See module-level documentation for call-specific semantics and params merging behavior.
        - Page lazy properties:
            - page.summary, page.sections, page.text, page.links, page.langlinks, page.backlinks, page.categories, page.categorymembers
            - Accessing each may trigger a single corresponding wiki.* call which then caches results on the page object.

- CLI / scripts:
    - No formal CLI shipping as part of the package. example.py contains a set of small, importable utilities intended for interactive use or inclusion in simple scripts:
        - print_links(page), print_sections(sections), print_categories(page), print_langlinks(page), print_categorymembers(categorymembers, level=0, max_level=2)
    - Packaging script:
        - setup.py includes a helper (setup.fix_doc) to sanitize long descriptions when preparing package metadata for PyPI.

## Core Features:
- Create per-language MediaWiki clients
    - Implements: wikipediaapi.__init__.Wikipedia
- Lazy, cached page model exposing summary, text, sections, links, categories, langlinks, backlinks, and categorymembers
    - Implements: wikipediaapi.__init__.WikipediaPage, wikipediaapi.__init__.WikipediaPageSection
- HTTP API plumbing with continuation handling and JSON parsing
    - Implements: wikipediaapi.__init__._query and continuation loops inside link/backlink/categorymembers methods
- Extract parsing into section trees (wikitext-like or HTML)
    - Implements: wikipediaapi.__init__._build_extracts, _create_section; controlled by ExtractFormat and RE_SECTION patterns
- Utility printers for human-oriented inspection
    - Implements: example.py functions (print_links, print_sections, print_categories, print_langlinks, print_categorymembers)
- Packaging helper to remove private PyPI sections from long descriptions
    - Implements: setup.fix_doc in setup.py

For implementation-level details of each core feature, consult the corresponding module/component documentation:
- wikipediaapi module-level documentation (contains full list of classes, methods, and builder function summaries)
- example.* helpers and setup.fix_doc component docs for operational contracts and edge cases

## Dependencies:
- External (runtime):
    - requests: Performs HTTP GETs via a persistent Session. Used by Wikipedia._query for all API requests and continuation fetching.
- Standard library:
    - enum, logging, re, urllib.parse, json: Enums and helpers for parsing and URL handling.
- Packaging-time:
    - setuptools (implied by setup.py) when packaging the project.

Version constraints:
- The repository snapshot does not declare strict version pins in the files provided here. Consumers should use a reasonably current requests release (e.g., requests >= 2.0). Ensure compatibility with your environment; tests or packaging metadata may specify tighter constraints in fuller project metadata.

## Configuration:
- Runtime parameters that affect behavior:
    - user_agent (required-ish): must be a descriptive string (module enforces > 5 chars). Alternatively, callers may supply a headers dict containing a "User-Agent".
    - language: ISO language code (string) used to build API hostnames or endpoints; normalized/stored by the Wikipedia client.
    - extract_format: ExtractFormat.WIKI or ExtractFormat.HTML — affects how page extracts are parsed into section trees.
    - kwargs on Wikipedia constructor: network-related settings (timeout, proxies, verify, etc.) are stored and applied to requests; provided defaults are used if not overridden (for example, a sensible timeout).
- No external config files are required. These parameters are set programmatically when constructing a Wikipedia client.

## Extension Points:
- Subclassing:
    - Wikipedia is the natural extension point. To adapt network behavior or parsing:
        - Override _query to change endpoint selection, authentication, or HTTP semantics.
        - Override builder methods (_build_extracts, _build_links, etc.) to change parsing, caching, or object construction behavior.
    - WikipediaPage/WikipediaPageSection may be subclassed to extend attributes or change lazy-fetch mapping behavior (ATTRIBUTES_MAPPING).
- Hooks and customization:
    - Provide custom headers via the Wikipedia constructor to inject auth tokens or alternative User-Agent strings.
    - Consumers can create page-like objects compatible with example.* utilities by exposing the minimal attributes expected (title, links, sections, categories, langlinks, ns, categorymembers, text).
- Notes:
    - The system is not architected around a plugin interface; extensibility is achieved through subclassing and overriding specific methods.

## Where to look next
- For reproduction of concrete behavior (exact parameter names, JSON-to-field mappings, regex group semantics, and side-effecting mutation points), read the module- and component-level documentation:
    - wikipediaapi module doc (contains precise class/method signatures and builder behaviors)
    - component docs for example.print_links, example.print_sections, example.print_categories, example.print_langlinks, example.print_categorymembers
    - setup.fix_doc component doc for packaging behavior

This repository-level document orients a developer to the project, highlights responsibilities of each top-level artifact, and points to per-module/component docs that contain reimplementation-level detail.

---

## Modules

- [`wikipediaapi`](wikipediaapi.md)

