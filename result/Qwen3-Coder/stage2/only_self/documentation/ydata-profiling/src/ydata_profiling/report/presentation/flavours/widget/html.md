# `html.py`

## `src.ydata_profiling.report.presentation.flavours.widget.html.WidgetHTML` · *class*

## Summary:
WidgetHTML is a concrete implementation of HTML rendering that produces ipywidgets.HTML objects for interactive widget-based report presentations.

## Description:
The WidgetHTML class serves as a specialized renderer for HTML content within the widget-based presentation flavour of ydata-profiling reports. It extends the base HTML class to provide concrete implementation for rendering HTML content as ipywidgets.HTML objects, enabling interactive visualizations in Jupyter environments.

This class is typically instantiated by report generators or presentation layer components that need to render HTML content specifically for widget-based interfaces. It acts as a bridge between raw HTML content and the ipywidgets rendering system, ensuring HTML content is properly formatted for interactive notebook environments.

## State:
- Inherits all attributes from HTML parent class:
  - content (dict): Dictionary containing HTML content under the "html" key and optional metadata (name, anchor_id, classes)
  - item_type (str): Set to "html" by parent constructor
  - name (str): Optional name identifier for the item
  - anchor_id (str): Optional anchor ID for linking
  - classes (str): Optional CSS classes to apply
- The content["html"] field can be either:
  - str: Raw HTML string content to be wrapped in widgets.HTML
  - widgets.HTML: Already constructed widget object to be returned directly

## Lifecycle:
- Creation: Instantiate with HTML content string and optional metadata parameters (name, anchor_id, classes) via parent HTML constructor
- Usage: Called by widget-based presentation renderers when processing HTML content items
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetHTML Constructor] --> B[HTML.__init__]
    B --> C[Renderable.__init__]
    C --> D[Set content with html key]
    D --> E[Set item_type to "html"]
    E --> F[render() called by widget renderer]
    F --> G{content["html"] is str?}
    G -->|No| H[Return content["html"] directly]
    G -->|Yes| I[Create widgets.HTML(content["html"])]
    I --> J[Return widgets.HTML object]
    H --> J
```

## Raises:
- No explicit exceptions raised by WidgetHTML.__init__
- The parent HTML class raises NotImplementedError when render() is called directly (but WidgetHTML overrides this)

## Example:
```python
# Create WidgetHTML content with basic HTML string
widget_html = WidgetHTML("<h1>Hello World</h1>", name="welcome_header")

# Create WidgetHTML with existing widgets.HTML object
existing_widget = widgets.HTML("<p>Existing widget content</p>")
widget_html_from_widget = WidgetHTML(existing_widget, name="existing_widget")

# In a widget-based rendering context:
# renderer = WidgetRenderer()
# widget_output = widget_html.render()  # Returns widgets.HTML object
```

### `src.ydata_profiling.report.presentation.flavours.widget.html.WidgetHTML.render` · *method*

## Summary:
Converts HTML content into an interactive ipywidgets.HTML widget for display in Jupyter environments.

## Description:
The render method transforms raw HTML content stored in the WidgetHTML instance into a proper ipywidgets.HTML widget object. This method is specifically designed for widget-based rendering environments such as Jupyter notebooks, where interactive HTML components are preferred over plain HTML strings.

This method serves as a concrete implementation of the render interface required by the presentation layer. It provides a bridge between raw HTML content and the interactive widget system, enabling rich HTML rendering capabilities within notebook environments.

The method checks if the HTML content is already a widget object (to avoid redundant conversion) or creates a new ipywidgets.HTML widget from the HTML string content.

## Args:
    None

## Returns:
    widgets.HTML: An ipywidgets.HTML widget instance containing the HTML content. If the content was already a widget object, it returns that widget directly without conversion.

## Raises:
    None

## State Changes:
    Attributes READ: 
    - self.content: Reads the "html" key from the content dictionary to access the HTML content
    - self.content["html"]: Direct access to the HTML content stored in the content dictionary

## Constraints:
    Preconditions:
    - The WidgetHTML instance must have been properly initialized with valid content
    - The content dictionary must contain an "html" key
    - The HTML content should either be a string or an existing widget object
    
    Postconditions:
    - The returned value is always a widgets.HTML object (or the original widget if already provided)
    - The HTML content is preserved exactly as provided during initialization

## Side Effects:
    None

