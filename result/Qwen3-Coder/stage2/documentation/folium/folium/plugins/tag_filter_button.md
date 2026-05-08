# `tag_filter_button.py`

## `folium.plugins.tag_filter_button.TagFilterButton` · *class*

## Summary:
A Leaflet map control component that provides a tag filtering button interface for interactive map filtering.

## Description:
The TagFilterButton class implements a Leaflet map control that displays a filter button allowing users to filter map features by tags. It inherits from JSCSSMixin and MacroElement to integrate with folium's map rendering system and automatically manage JavaScript and CSS dependencies. This component leverages the leaflet-tag-filter-button plugin to provide an interactive filtering interface for map features based on their associated tags.

## State:
- _name: str, set to "TagFilterButton" - identifies this element type in the folium rendering system
- options: dict, populated by parse_options with configuration parameters including data, icon, clear_text, filter_on_every_click, and open_popup_on_hover
- default_js: list of tuples, specifies JavaScript dependencies loaded from CDN URLs for the tag filter button and easy-button plugins
- default_css: list of tuples, specifies CSS dependencies loaded from CDN URLs for styling the tag filter button, easy-button, and ripple effects

## Lifecycle:
- Creation: Instantiate with required data parameter and optional configuration parameters
- Usage: Add to a folium.Map instance using the add_child() method or similar
- Destruction: Automatically cleaned up when the containing Figure is destroyed

## Method Map:
```mermaid
graph TD
    A[TagFilterButton.__init__] --> B[super().__init__()]
    B --> C[parse_options()]
    C --> D[self.options = ...]
    D --> E[return]
```

## Raises:
- None explicitly raised by __init__, though parent class constructors may raise exceptions if used outside of a Figure context

## Example:
```python
import folium
from folium.plugins import TagFilterButton

# Create a map
m = folium.Map([45.5236, -122.6750], zoom_start=13)

# Sample data with tags
data = [
    {"name": "Location A", "tags": ["restaurant", "cafe"], "lat": 45.5236, "lon": -122.6750},
    {"name": "Location B", "tags": ["park", "recreation"], "lat": 45.5240, "lon": -122.6700}
]

# Create and add the tag filter button
tag_filter = TagFilterButton(
    data=data,
    icon="fa-filter",
    clear_text="Clear Filters"
)
m.add_child(tag_filter)

# The map now displays a filter button that allows users to filter by tags
```

### `folium.plugins.tag_filter_button.TagFilterButton.__init__` · *method*

## Summary:
Initializes a TagFilterButton control with configuration options for filtering map features by tags.

## Description:
Configures a Leaflet map control that displays a filter button allowing users to filter map features by associated tags. This method sets up the component's internal state by initializing parent classes, defining the component name, and processing configuration options through the parse_options utility function.

## Args:
    data (Any): Required data structure containing tag information for map features. Typically a list of dictionaries with tag metadata.
    icon (str): Optional icon class for the filter button. Defaults to "fa-filter".
    clear_text (str): Optional text label for the clear filter button. Defaults to "clear".
    filter_on_every_click (bool): Optional flag controlling whether filters apply on every click. Defaults to True.
    open_popup_on_hover (bool): Optional flag controlling popup display on hover. Defaults to False.
    **kwargs: Additional keyword arguments passed to the parse_options utility for further configuration.

## Returns:
    None: This method initializes the object's state and does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions, though parent class initialization may raise exceptions if used outside of a proper folium Figure context.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
        - self._name: Set to "TagFilterButton" to identify this element type
        - self.options: Populated with processed configuration options from parse_options

## Constraints:
    Preconditions:
        - The TagFilterButton must be instantiated within a folium Map context to render properly
        - The data parameter must contain valid tag information for the filtering functionality
    Postconditions:
        - The object's _name attribute is set to "TagFilterButton"
        - The object's options attribute contains a dictionary of processed configuration parameters
        - Parent class initialization is completed successfully

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only initializes internal object state.

