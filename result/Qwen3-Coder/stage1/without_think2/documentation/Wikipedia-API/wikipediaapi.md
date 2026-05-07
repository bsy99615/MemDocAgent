# `wikipediaapi`

## Tree:
- wikipediaapi/
  - __init__.py

## Role:
Provides a Pythonic interface for accessing Wikipedia content through the MediaWiki API, enabling developers to retrieve page summaries, sections, links, categories, and translations with minimal boilerplate code.

## Description:
The wikipediaapi module serves as a high-level abstraction layer for interacting with Wikipedia's MediaWiki API. It encapsulates the complexity of API communication, providing clean interfaces for fetching page content, metadata, and related information. The module is designed to be used by developers who want to programmatically access Wikipedia data without dealing with low-level HTTP requests or API intricacies.

Primary consumers of this module include:
- Data processing pipelines that extract Wikipedia content for analysis
- Applications that need to display Wikipedia summaries or sections
- Tools that build multilingual knowledge bases using Wikipedia data
- Educational software that incorporates Wikipedia articles

The module is organized around two core classes: Wikipedia (the API client) and WikipediaPage (representing individual Wikipedia pages). These classes work together to provide lazy-loaded access to Wikipedia data, minimizing unnecessary API calls while maintaining a consistent interface.

## Components:
- Wikipedia: Main API client class for creating page objects and making queries
- WikipediaPage: Represents individual Wikipedia pages with lazy-loaded content and metadata
- WikipediaPageSection: Models hierarchical sections within Wikipedia articles
- ExtractFormat: Enumeration defining supported extraction formats (WIKI/HTML)
- Namespace: Enumeration of standard Wikipedia namespace identifiers
- namespace2int: Utility function for converting namespace identifiers to integers

## Public API:
- Wikipedia(user_agent, language="en", extract_format=ExtractFormat.WIKI, headers=None, **kwargs)
  - Creates a Wikipedia API client instance
  - Parameters:
    - user_agent (str): Required HTTP User-Agent string
    - language (str): Language code for Wikipedia instance (default: "en")
    - extract_format (ExtractFormat): Content extraction format (default: WIKI)
    - headers (dict, optional): Additional HTTP headers
    - kwargs: Additional arguments for requests library
- Wikipedia.page(title, ns=Namespace.MAIN, unquote=False)
  - Creates a WikipediaPage object for a specific title
  - Parameters:
    - title (str): Page title
    - ns (WikiNamespace): Namespace identifier (default: MAIN)
    - unquote (bool): Whether to URL-decode title (default: False)
- Wikipedia.article(title, ns=Namespace.MAIN, unquote=False)
  - Alias for Wikipedia.page() method
- Wikipedia.extracts(page, **kwargs)
  - Retrieves page summary text
- Wikipedia.info(page)
  - Fetches page metadata
- Wikipedia.langlinks(page, **kwargs)
  - Retrieves language links
- Wikipedia.links(page, **kwargs)
  - Retrieves linked pages
- Wikipedia.backlinks(page, **kwargs)
  - Retrieves backlinks
- Wikipedia.categories(page, **kwargs)
  - Retrieves page categories
- Wikipedia.categorymembers(page, **kwargs)
  - Retrieves category members
- WikipediaPage(title, ns=Namespace.MAIN, language="en", url=None)
  - Constructor for WikipediaPage objects
- WikipediaPageSection(title, level=0, text="", wiki=None)
  - Constructor for section objects

## Dependencies:
- requests: Used for HTTP communication with Wikipedia API
- urllib.parse: For URL encoding/decoding operations
- logging: For API request logging
- enum: For namespace and format enumerations
- typing: For type hints

## Constraints:
- All API requests must include a valid user_agent string (minimum 5 characters)
- Wikipedia language parameter must be a valid language code
- WikipediaPage objects must be created through the Wikipedia client
- API calls are lazy-loaded and cached after first access
- Thread safety: The module is not thread-safe due to shared session state

---

## Files

- [`__init__.py`](wikipediaapi/__init__.md)

