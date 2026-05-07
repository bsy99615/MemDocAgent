# `__init__.py`

## `wikipediaapi.__init__.ExtractFormat` · *class*

*No documentation generated.*

## `wikipediaapi.__init__.Namespace` · *class*

*No documentation generated.*

## `wikipediaapi.__init__.namespace2int` · *function*

*No documentation generated.*

## `wikipediaapi.__init__.Wikipedia` · *class*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.__init__` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.__del__` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.page` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.article` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.extracts` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.info` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.langlinks` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.links` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.backlinks` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.categories` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia.categorymembers` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._query` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._build_extracts` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._create_section` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._build_info` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._build_langlinks` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._build_links` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._build_backlinks` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._build_categories` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._build_categorymembers` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.Wikipedia._common_attributes` · *method*

*No documentation generated.*

## `wikipediaapi.__init__.WikipediaPageSection` · *class*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPageSection.__init__` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPageSection.title` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPageSection.level` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPageSection.text` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPageSection.sections` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPageSection.section_by_title` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPageSection.full_text` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPageSection.__repr__` · *method*

*No documentation generated.*

## `wikipediaapi.__init__.WikipediaPage` · *class*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.__init__` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.__getattr__` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.language` · *method*

## Summary:
Returns the language code of the current Wikipedia page.

## Description:
This property provides access to the language identifier associated with the Wikipedia page. It retrieves the language from the internal attributes dictionary and returns it as a string. This is a simple getter method that exposes the language information stored during page initialization.

## Args:
    None

## Returns:
    str: The language code of the current page (e.g., "en", "fr", "de").

## Raises:
    KeyError: If the "language" key is missing from the internal _attributes dictionary (though this should not occur as it's initialized in __init__).

## State Changes:
    Attributes READ: self._attributes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The WikipediaPage object must have been properly initialized with a language value.
    Postconditions: The returned value is always a string representation of the language code.

## Side Effects:
    None

### `wikipediaapi.__init__.WikipediaPage.title` · *method*

## Summary:
Returns the title of the current Wikipedia page as a string.

## Description:
This property provides access to the title of the Wikipedia page represented by this object. The title is stored in the internal `_attributes` dictionary and is initialized during object construction. This property follows the lazy loading pattern used throughout the WikipediaPage class, where attributes are fetched from the Wikipedia API only when first accessed.

## Args:
    None

## Returns:
    str: The title of the current Wikipedia page. Always returns a string representation of the title.

## Raises:
    None

## State Changes:
    Attributes READ: self._attributes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The WikipediaPage object must be properly initialized with a title.
    Postconditions: The returned value is always a string, even if the underlying title value is not originally a string.

## Side Effects:
    None

### `wikipediaapi.__init__.WikipediaPage.namespace` · *method*

## Summary:
Returns the namespace identifier of the current Wikipedia page as an integer.

## Description:
This property provides access to the namespace of the Wikipedia page, which indicates the type or category of the page (e.g., main article, talk page, user page, etc.). The namespace is stored internally as an integer value and represents the page's classification within Wikipedia's namespace system.

## Args:
    None

## Returns:
    int: The namespace identifier of the current page. This corresponds to standard Wikipedia namespace values defined in the Namespace enum.

## Raises:
    KeyError: If the "ns" key is not present in the internal _attributes dictionary.
    ValueError: If the stored namespace value cannot be converted to an integer.

## State Changes:
    Attributes READ: self._attributes
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The WikipediaPage instance must have been initialized with a valid namespace value.
    Postconditions: The returned value is always an integer representing a valid Wikipedia namespace.

## Side Effects:
    None

### `wikipediaapi.__init__.WikipediaPage.exists` · *method*

## Summary:
Determines whether the current Wikipedia page exists by checking if its page ID is valid.

## Description:
This method provides a convenient way to check if a Wikipedia page exists without triggering additional API calls. It leverages the fact that the Wikipedia API returns a page ID of -1 for non-existent pages. The method accesses the pageid attribute, which is lazily fetched when first accessed, and returns True if the page ID is not -1.

## Args:
    None

## Returns:
    bool: True if the page exists (pageid != -1), False otherwise

## Raises:
    None

## State Changes:
    Attributes READ: self.pageid
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The WikipediaPage instance must be properly initialized
    Postconditions: Returns a boolean value indicating page existence status

## Side Effects:
    None

### `wikipediaapi.__init__.WikipediaPage.summary` · *method*

## Summary
Returns the summary text of the current Wikipedia page by fetching and caching extract data when needed.

## Description
This property provides access to the summary text of a Wikipedia page. It implements lazy loading behavior - the summary data is only fetched from the Wikipedia API when first accessed, and subsequently cached for future accesses. This approach optimizes performance by avoiding unnecessary API calls when the summary isn't needed.

The method checks if the "extracts" data has already been fetched (`self._called["extracts"]`). If not, it calls `self._fetch("extracts")` to retrieve the data from the Wikipedia API, which populates `self._summary` and other related attributes. Finally, it returns the cached summary text stored in `self._summary`.

This method is part of the WikipediaPage class's property-based interface for accessing page content, alongside other properties like `sections`, `text`, and various metadata properties.

## Args
None

## Returns
str: The summary text of the Wikipedia page. Returns an empty string if the page doesn't exist or if there's an error retrieving the summary.

## Raises
None explicitly raised, but may propagate exceptions from underlying API calls via `_fetch` and `_build_extracts` methods.

## State Changes
Attributes READ: 
- `self._called["extracts"]` - checks if extracts data has been fetched
- `self._summary` - returns the cached summary text

Attributes WRITTEN:
- `self._called["extracts"]` - set to True after successful fetch

## Constraints
Preconditions:
- The WikipediaPage instance must be properly initialized with a valid Wikipedia connection
- The page title must be valid (though existence is not required for this property)

Postconditions:
- After first access, `self._called["extracts"]` will be True
- The returned string will contain the page summary text or be empty if no summary exists

## Side Effects
- Makes an HTTP request to the Wikipedia API when first accessed (via `_fetch` method)
- Modifies internal state by setting `self._called["extracts"]` to True after first fetch
- May trigger additional API calls through the `_fetch` method chain

### `wikipediaapi.__init__.WikipediaPage.sections` · *method*

## Summary:
Returns all sections of the current Wikipedia page, fetching page data if necessary.

## Description:
This method provides access to all structured sections of a Wikipedia page. It ensures that the page's extract data is fetched before returning the sections, making it a lazy-loading mechanism for page sections. The method is commonly used when users want to access the hierarchical structure of a Wikipedia article's content.

The sections are populated during the initial fetch operation when the page data is retrieved from the Wikipedia API. This method serves as the primary interface for accessing the structured content of a Wikipedia page.

## Args:
    None

## Returns:
    List[WikipediaPageSection]: A list of WikipediaPageSection objects representing all sections of the current page. Returns an empty list if the page has no sections or if the page data hasn't been fetched yet.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._called, self._section
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The WikipediaPage instance must be properly initialized with a valid wiki connection
    Postconditions: The method guarantees that extract data is fetched before returning sections, ensuring the returned sections are up-to-date

## Side Effects:
    I/O: Makes HTTP requests to the Wikipedia API via the wiki connection when fetch is required
    External service calls: Calls the Wikipedia API to retrieve page extracts containing section information

### `wikipediaapi.__init__.WikipediaPage.section_by_title` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.sections_by_title` · *method*

## Summary:
Returns all sections of the current page that match the specified title.

## Description:
This method retrieves all sections from the current Wikipedia page that have the given title. It ensures the page content is fetched if not already available, then performs a lookup in the section mapping to find matching sections.

## Args:
    title (str): The title of the sections to retrieve

## Returns:
    List[WikipediaPageSection]: A list of WikipediaPageSection objects matching the given title, or an empty list if no sections are found

## Raises:
    None explicitly documented

## State Changes:
    Attributes READ: self._called, self._section_mapping
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The WikipediaPage instance must be properly initialized
    Postconditions: Returns a list of WikipediaPageSection objects or empty list

## Side Effects:
    I/O: May trigger network requests if content needs to be fetched via _fetch
    External service calls: Through _fetch method which likely makes HTTP requests to Wikipedia API

### `wikipediaapi.__init__.WikipediaPage.text` · *method*

## Summary:
Returns the complete textual content of a Wikipedia page by combining the summary with all section contents.

## Description:
This property provides access to the full text content of a Wikipedia page by concatenating the page summary with all hierarchical sections and their subsections. The method ensures proper formatting with appropriate spacing between different content segments.

## Args:
    None

## Returns:
    str: Complete text content of the Wikipedia page, including summary and all sections with their subsections formatted with proper indentation levels.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self.summary (accesses and potentially fetches data)
    - self.sections (accesses and potentially fetches data)
    - Each section's full_text method accesses section properties

## Constraints:
    Preconditions:
    - The WikipediaPage instance must be properly initialized
    - The page data must be fetchable from the Wikipedia API (page must exist)
    
    Postconditions:
    - Returns a string containing all page content
    - The returned string is stripped of leading/trailing whitespace

## Side Effects:
    - May trigger network requests to fetch page data if not already cached (via summary and sections properties)
    - Accesses external Wikipedia API through the associated Wikipedia client

### `wikipediaapi.__init__.WikipediaPage.langlinks` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.links` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.backlinks` · *method*

## Summary:
Returns all pages that link to the current Wikipedia page by fetching backlinks from the MediaWiki API.

## Description:
This method provides access to backlinks - pages that link to the current page. It implements lazy loading by only fetching data when first accessed, and caches the results for subsequent calls. The method acts as a wrapper around the MediaWiki API's backlinks functionality (https://www.mediawiki.org/wiki/API:Backlinks).

The method is called during the page lifecycle when accessing the backlinks property, typically in data extraction pipelines where relationships between pages are being analyzed.

## Args:
    None

## Returns:
    PagesDict: A dictionary mapping page titles to WikipediaPage objects representing pages that link to the current page. Returns an empty dictionary if no backlinks exist or if the page doesn't exist.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self._called["backlinks"], self._backlinks
    Attributes WRITTEN: self._called["backlinks"] is set to True after fetching

## Constraints:
    Preconditions: The WikipediaPage instance must be properly initialized with a valid Wikipedia connection
    Postconditions: After first call, self._called["backlinks"] is True and self._backlinks contains the backlink data

## Side Effects:
    Makes HTTP requests to the MediaWiki API endpoint for retrieving backlinks
    Modifies internal state by marking the backlinks as fetched

### `wikipediaapi.__init__.WikipediaPage.categories` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.categorymembers` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage._fetch` · *method*

*No documentation generated.*

### `wikipediaapi.__init__.WikipediaPage.__repr__` · *method*

*No documentation generated.*

