# `Wikipedia-API`

## WikipediaPage Class

### Summary:
The `WikipediaPage` class represents a single Wikipedia article and provides access to its content, metadata, and related information. It implements a lazy-loading mechanism to efficiently fetch data only when needed.

### Description:
This class serves as the primary interface for working with individual Wikipedia articles. It stores page metadata and provides properties that automatically trigger API calls to fetch content when accessed for the first time. The class supports navigation through article sections, links to other pages, and access to various metadata fields.

### Key Responsibilities:
- Stores and manages page metadata (title, language, namespace, etc.)
- Implements lazy loading for content retrieval
- Provides access to article text, sections, and structured content
- Manages relationships with linked pages (links, categories, language links)
- Handles attribute access with automatic API calls when needed

### Core Properties:
1. **`title`** - Title of the Wikipedia page
2. **`language`** - Language code of the Wikipedia edition
3. **`namespace`** - Namespace identifier for the page
4. **`summary`** - Article summary text
5. **`text`** - Full article text including sections
6. **`sections`** - List of article sections with hierarchy
7. **`links`** - Pages linked from this article
8. **`categories`** - Categories this article belongs to
9. **`langlinks`** - Links to equivalent articles in other languages
10. **`backlinks`** - Pages that link to this article

### Implementation Details:
- Uses `__getattr__` magic method for lazy loading of attributes
- Maintains `_called` dictionary to track which API calls have been made
- Stores content in private attributes (`_summary`, `_section`, etc.)
- Implements `_fetch` method to trigger API calls for specific data types
- Supports section navigation via `_section_mapping` dictionary

### Usage Example:
```python
import wikipediaapi

wiki = wikipediaapi.Wikipedia('MyApp/1.0')
page = wiki.page('Python_(programming_language)')

# These will trigger API calls only when accessed
summary = page.summary  # Fetches extracts
links = page.links      # Fetches links
sections = page.sections # Fetches extracts with section structure
```

---

## Modules

- [`wikipediaapi`](wikipediaapi.md)

