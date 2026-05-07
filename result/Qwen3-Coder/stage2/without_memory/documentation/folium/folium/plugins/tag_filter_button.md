# `tag_filter_button.py`

## `folium.plugins.tag_filter_button.TagFilterButton` · *class*

## Summary:
A Leaflet map plugin component that renders a tag filtering button with interactive filtering capabilities.

## Description:
The TagFilterButton class implements a UI control for filtering map features by tags using Leaflet's tag-filter-button plugin. It inherits from JSCSSMixin and MacroElement to integrate with folium's map rendering system. This component provides a user interface element that allows users to apply tag-based filters to map features, displaying a button that opens a filter interface when clicked.

## State:
- _name (str): Set to "TagFilterButton" to identify this component type in folium's rendering system
- options (dict): Processed configuration options containing data, icon, clear_text, filter_on_every_click, and open_popup_on_hover parameters
- default_js (list): List of JavaScript dependencies required for the tag filter functionality, including leaflet-tag-filter-button.js and leaflet-easybutton.js
- default_css (list): List of CSS dependencies required for styling the tag filter button, including tag-filter-button.css, easy-button.css, and ripples.min.css
- _template (Template): Empty Jinja2 template (likely populated by parent classes or external JS)

## Lifecycle:
- Creation: Instantiate with required data parameter and optional configuration parameters
- Usage: Add to a folium.Map instance using the add_child() method
- Destruction: Managed automatically by folium's rendering system through parent class mechanisms

## Method Map:
```mermaid
graph TD
    A[TagFilterButton.__init__] --> B[super().__init__()]
    B --> C[Set _name]
    C --> D[parse_options with data and config params]
    D --> E[Store processed options]
```

## Raises:
- AssertionError: May be raised by parent classes' validation mechanisms if invalid parameters are provided

## Example:
```python
import folium
from folium.plugins import TagFilterButton

# Create a map
m = folium.Map([45.5236, -122.6750], zoom_start=13)

# Sample data for tag filtering
data = [
    {'tag': 'restaurant', 'name': 'Pizza Place'},
    {'tag': 'cafe', 'name': 'Coffee Shop'}
]

# Create and add the tag filter button
tag_filter = TagFilterButton(
    data=data,
    icon="fa-filter",
    clear_text="Clear Filters"
)
m.add_child(tag_filter)

# Display the map
m
```

### `folium.plugins.tag_filter_button.TagFilterButton.__init__` · *method*

## Summary:
Initializes a TagFilterButton component for filtering map layers by tags.

## Description:
Configures the TagFilterButton widget that provides a filter interface for Leaflet map layers. This method sets up the component's name and processes initialization parameters through the parse_options utility function. The component integrates with Leaflet's tag filtering plugin to enable interactive filtering of map features based on their tags.

## Args:
    data (any): The data structure containing tag information for filtering map layers.
    icon (str): Font Awesome icon class for the button. Defaults to "fa-filter".
    clear_text (str): Text displayed on the clear filter button. Defaults to "clear".
    filter_on_every_click (bool): Whether to apply filters immediately on click. Defaults to True.
    open_popup_on_hover (bool): Whether to open popup on hover. Defaults to False.
    **kwargs: Additional keyword arguments passed to the parse_options function.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    AssertionError: If any option provided doesn't match the expected type or is not in the valid options list (when using the parent class's parse_options method).

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TagFilterButton"
    - self.options: Set to processed options dictionary from parse_options

## Constraints:
    Preconditions:
    - The data parameter must be compatible with the tag filtering functionality
    - All keyword arguments must be valid for the underlying Leaflet plugin
    
    Postconditions:
    - The component's name is set to "TagFilterButton"
    - The options dictionary contains properly formatted and validated configuration options

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only configures internal object state.

