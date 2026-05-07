# `tag_filter_button.py`

## `folium.plugins.tag_filter_button.TagFilterButton` · *class*

## Summary:
A Leaflet map plugin component that renders an interactive tag filtering button for filtering map features by tag values.

## Description:
The TagFilterButton class implements a specialized UI element for Leaflet maps that provides an interactive button for filtering map features based on tag values. It inherits from JSCSSMixin for JavaScript/CSS resource management and MacroElement for folium integration. This component leverages external JavaScript libraries (leaflet-tag-filter-button and leaflet-easybutton) to create a user-friendly tag filtering interface on maps.

## State:
- _name (str): Set to "TagFilterButton" to identify the element type in folium's rendering system
- _template (Template): Empty Jinja2 template object (likely intended for HTML rendering)
- options (dict): Processed configuration options for the tag filter button, converted from snake_case to camelCase format using parse_options utility
- default_js (list): List of tuples containing JavaScript library names and CDN URLs required for the tag filter functionality
- default_css (list): List of tuples containing CSS stylesheet names and CDN URLs required for styling the tag filter button

## Lifecycle:
- Creation: Instantiate with required data parameter and optional configuration parameters
- Usage: Add to a folium.Map instance using add_child() method; rendering automatically handles JS/CSS inclusion via JSCSSMixin
- Destruction: Managed by folium's element lifecycle; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[TagFilterButton.__init__] --> B[super().__init__()]
    B --> C[self._name = "TagFilterButton"]
    C --> D[self.options = parse_options(...)]
    D --> E[Returns initialized TagFilterButton instance]
```

## Raises:
- None explicitly raised by __init__ method
- Inherited exceptions from parent classes (JSCSSMixin, MacroElement) during rendering if not properly contained in a Figure context

## Example:
```python
import folium
from folium.plugins import TagFilterButton

# Create a sample map
m = folium.Map([45.5236, -122.6750], zoom_start=13)

# Sample data for tag filtering
data = [
    {"tag": "restaurant", "name": "Pizza Place"},
    {"tag": "cafe", "name": "Coffee Shop"},
    {"tag": "restaurant", "name": "Burger Joint"}
]

# Create and add tag filter button
tag_filter = TagFilterButton(
    data=data,
    icon="fa-filter",
    clear_text="Clear Filters"
)
m.add_child(tag_filter)

# The tag filter button will appear on the map allowing users to filter by tag
# The button will dynamically update based on the data provided
```

### `folium.plugins.tag_filter_button.TagFilterButton.__init__` · *method*

## Summary:
Initializes a TagFilterButton component that creates a filter button with configurable appearance and behavior for tagging systems.

## Description:
The TagFilterButton constructor sets up the component's configuration options and initializes its base class. This method prepares the button with customizable properties such as icon, clear text, and filtering behavior while ensuring proper integration with folium's rendering system through inheritance from MacroElement and JSCSSMixin.

## Args:
    data (any): The main data input required for the tag filter functionality. This is typically a collection of tags or filterable data items.
    icon (str, optional): Icon class name for the filter button. Defaults to "fa-filter".
    clear_text (str, optional): Text label for the clear filter button. Defaults to "clear".
    filter_on_every_click (bool, optional): Whether to apply filters immediately on every click. Defaults to True.
    open_popup_on_hover (bool, optional): Whether to open a popup when hovering over the button. Defaults to False.
    **kwargs: Additional keyword arguments that are processed through parse_options for camelCase conversion.

## Returns:
    None: This method initializes the object's state but does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TagFilterButton" to identify the component type
    - self.options: Set to the processed dictionary from parse_options containing all configuration options

## Constraints:
    Preconditions:
        - The data parameter must be provided for the component to function properly
        - All keyword arguments must be compatible with the parse_options processing
    Postconditions:
        - The component is initialized with proper name identification
        - Configuration options are stored in camelCase format for compatibility with JavaScript libraries
        - The component is ready for rendering within a folium Figure context

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only sets internal state attributes.

