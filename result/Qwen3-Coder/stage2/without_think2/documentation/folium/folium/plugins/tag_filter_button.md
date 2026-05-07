# `tag_filter_button.py`

## `folium.plugins.tag_filter_button.TagFilterButton` · *class*

## Summary:
TagFilterButton is a folium map component that creates an interactive tag filtering button for Leaflet maps, allowing users to filter map features by tags.

## Description:
TagFilterButton is designed to enhance Leaflet maps with a tag-based filtering interface. It inherits from JSCSSMixin and MacroElement to provide automatic JavaScript and CSS dependency management and proper map element integration. This component enables users to interactively filter map features based on tag categories through a visual button interface that appears on the map.

The component is particularly useful for maps with categorized data where users need to selectively display features based on their tags. It leverages external JavaScript libraries (leaflet-tag-filter-button and leaflet-easybutton) to provide the filtering functionality.

## State:
- _name (str): Set to "TagFilterButton" to identify the element type in the rendering pipeline
- _template (Template): Empty Jinja2 template that would be populated during rendering (inherited from MacroElement)
- options (dict): Configuration options processed by parse_options, containing data, icon, clear_text, filter_on_every_click, and open_popup_on_hover parameters
- default_js (list): List of JavaScript dependencies including leaflet-tag-filter-button and leaflet-easybutton libraries for the filtering functionality
- default_css (list): List of CSS dependencies including styles for the tag filter button and related UI elements

## Lifecycle:
- Creation: Instantiate with required data parameter and optional configuration options; automatically registers dependencies through inheritance
- Usage: Add to a folium.Map instance using add_child() method; rendering automatically handles JS/CSS inclusion via JSCSSMixin
- Destruction: Managed by folium's map rendering system; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[TagFilterButton.__init__] --> B[super().__init__()]
    B --> C[set _name to "TagFilterButton"]
    C --> D[parse_options with data and config params]
    D --> E[options set to parsed configuration]
    
    F[Map.add_child(TagFilterButton)] --> G[TagFilterButton.render()]
    G --> H[JSCSSMixin.render()]
    H --> I[Add JS/CSS dependencies to figure header]
    I --> J[Render HTML template with options]
```

## Raises:
- None explicitly raised by __init__
- May raise exceptions from parent classes during rendering if map context is invalid

## Example:
```python
import folium
from folium.plugins import TagFilterButton

# Create a sample map
m = folium.Map([40.7128, -74.0060], zoom_start=12)

# Sample data for tag filtering
data = {
    "Buildings": ["Office", "Residential", "Commercial"],
    "Transport": ["Bus Stop", "Train Station", "Airport"]
}

# Create and add tag filter button
tag_filter = TagFilterButton(
    data=data,
    icon="fa-filter",
    clear_text="Clear Filters"
)
m.add_child(tag_filter)

# The button will appear on the map allowing tag-based filtering
```

### `folium.plugins.tag_filter_button.TagFilterButton.__init__` · *method*

## Summary:
Initializes a TagFilterButton instance with configuration options for filtering map layers by tags.

## Description:
Configures the TagFilterButton widget by setting its name identifier and processing input parameters into a standardized options dictionary. This method establishes the foundational configuration that enables the button to control tag-based filtering functionality in folium maps.

## Args:
    data: The data to be filtered by tags, typically containing layer information.
    icon (str): CSS class name for the button icon, defaults to "fa-filter".
    clear_text (str): Text label for the clear filter button, defaults to "clear".
    filter_on_every_click (bool): Whether to apply filters immediately on each click, defaults to True.
    open_popup_on_hover (bool): Whether to show popups when hovering over the button, defaults to False.
    **kwargs: Additional keyword arguments passed to the parse_options utility function.

## Returns:
    None

## Raises:
    None

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: 
    - self._name: Set to "TagFilterButton" to identify the component type
    - self.options: Set to the processed dictionary from parse_options containing all configuration options in camelCase format with None values filtered out

## Constraints:
    Preconditions:
    - The data parameter must be provided and contain valid filterable information
    - All keyword arguments must be compatible with the parse_options function's expectations
    
    Postconditions:
    - The instance is properly initialized with a unique name identifier
    - The options dictionary contains all configuration parameters in camelCase format with None values filtered out
    - The parent class initialization is completed successfully

## Side Effects:
    None

