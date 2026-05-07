# `wikipediaapi`

## Tree:
```
wikipediaapi/
└── __init__.py
```

## Role:
Provides a Python interface for accessing Wikipedia content through the MediaWiki API, enabling programmatic retrieval of page content, metadata, and related information.

## Description:
The wikipediaapi module serves as a comprehensive client for interacting with Wikipedia's MediaWiki API. It offers a clean, object-oriented interface for fetching and processing Wikipedia content, supporting features like page content retrieval, metadata access, language links, backlinks, categories, and section navigation. The module is designed with lazy-loading principles to optimize performance by fetching data only when explicitly requested.

This module is organized around two primary classes: `Wikipedia` (the main API client) and `WikipediaPage` (representing individual Wikipedia pages). It also includes supporting classes and enums for handling different content formats and Wikipedia namespaces.

## Components:
*   `Wikipedia` - Main client class for API interactions
*   `WikipediaPage` - Represents individual Wikipedia pages with lazy-loaded properties
*   `WikipediaPageSection` - Represents hierarchical sections within Wikipedia pages
*   `ExtractFormat` - Enumeration for specifying content extraction formats (WIKI or HTML)
*   `Namespace` - Enumeration for Wikipedia namespace identifiers
*   `namespace2int` - Utility function for converting namespace identifiers to integers

## Public API:
*   `Wikipedia(user_agent, language="en", extract_format=ExtractFormat.WIKI, headers=None, **kwargs)` - Constructor for the main Wikipedia client
*   `Wikipedia.page(title, ns=Namespace.MAIN, unquote=False)` - Creates a WikipediaPage object for a specific title
*   `Wikipedia.article(title, ns=Namespace.MAIN, unquote=False)` - Alias for `page()` method
*   `Wikipedia.extracts(page, **kwargs)` - Fetches extracts/summaries for a page
*   `Wikipedia.info(page)` - Fetches metadata for a page
*   `Wikipedia.langlinks(page, **kwargs)` - Fetches language links for a page
*   `Wikipedia.links(page, **kwargs)` - Fetches links from a page
*   `Wikipedia.backlinks(page, **kwargs)` - Fetches backlinks to a page
*   `Wikipedia.categories(page, **kwargs)` - Fetches categories for a page
*   `Wikipedia.categorymembers(page, **kwargs)` - Fetches members of a category page
*   `WikipediaPage` - Class representing individual Wikipedia pages
*   `WikipediaPageSection` - Class representing sections within Wikipedia pages
*   `ExtractFormat` - Enum for content extraction formats
*   `Namespace` - Enum for Wikipedia namespace identifiers
*   `namespace2int(namespace)` - Converts namespace identifiers to integers

## Dependencies:
*   Internal: None
*   External: `requests` library for HTTP communication, `logging` for informational messages

## Constraints:
*   The `user_agent` parameter in `Wikipedia` constructor must be a non-empty string with length greater than 5 characters
*   The `language` parameter in `Wikipedia` constructor must be a non-empty string
*   All API methods require a properly initialized `Wikipedia` instance with a valid session
*   The module is not thread-safe for concurrent access to the same Wikipedia instance
*   Network connectivity is required for all API interactions

---

## Files

- [`__init__.py`](wikipediaapi/__init__.md)

