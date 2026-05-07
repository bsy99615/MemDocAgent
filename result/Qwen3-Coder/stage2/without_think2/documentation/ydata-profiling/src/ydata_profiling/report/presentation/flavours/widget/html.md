# `html.py`

## `src.ydata_profiling.report.presentation.flavours.widget.html.WidgetHTML` · *class*

## Summary:
WidgetHTML is a concrete implementation of the HTML presentation component that renders HTML content as an interactive ipywidgets.HTML widget.

## Description:
WidgetHTML serves as a specialized renderer for HTML content within the ydata-profiling framework, specifically designed for environments that support ipywidgets (such as Jupyter notebooks). It extends the abstract HTML class and provides a concrete implementation of the render method that creates ipywidgets.HTML objects from raw HTML strings or reuses existing widget objects.

This class enables the integration of rich HTML content with interactive widget capabilities, making it suitable for creating dynamic, interactive reports in notebook environments. The class acts as a bridge between static HTML content and the interactive widget ecosystem.

## State:
- Inherits all attributes from HTML parent class:
  - content (dict): Dictionary containing the HTML content under the key "html"
  - item_type (str): Set to "html" by parent constructor
  - name (str): Optional identifier for the component
  - anchor_id (str): Optional anchor identifier for linking
  - classes (str): Optional CSS classes to apply
- No additional instance attributes beyond those inherited from parent

## Lifecycle:
- Creation: Instantiate with WidgetHTML(content: str, **kwargs) where content is the raw HTML string and kwargs can include name, anchor_id, and classes
- Usage: Called by the report generation framework during rendering phase to convert HTML content into ipywidgets.HTML objects
- Destruction: Relies on Python's garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[WidgetHTML.__init__] --> B[HTML.__init__]
    B --> C[Renderable.__init__]
    C --> D[Set content with html key]
    D --> E[Set item_type to "html"]
    E --> F[WidgetHTML.render]
    F --> G[Check if content['html'] is not str]
    G -->|True| H[Return content['html'] as widget]
    G -->|False| I[Create widgets.HTML(content['html'])]
    I --> J[Return widgets.HTML object]
```

## Raises:
- None explicitly raised by WidgetHTML.__init__
- The parent HTML class's render method raises NotImplementedError, but WidgetHTML overrides this with a concrete implementation that handles both string and widget content types

## Example:
```python
# Create a WidgetHTML component with raw HTML content
widget_html = WidgetHTML("<h1>Hello World</h1>")

# In a Jupyter environment, this would render as an interactive HTML widget
# widget_instance = widget_html.render()  # Returns widgets.HTML object
```

### `src.ydata_profiling.report.presentation.flavours.widget.html.WidgetHTML.render` · *method*

## Summary:
Converts HTML content into a widget-based HTML element for Jupyter notebook display, supporting both string and widget content types.

## Description:
This method transforms HTML content into an ipywidgets.HTML widget for proper rendering in Jupyter environments. It provides flexibility by handling two content types: when content["html"] is already a widget instance (returns it directly), or when it's a string (wraps it in widgets.HTML). This method is part of the WidgetHTML class that extends the base HTML presentation component for widget-based interfaces.

## Args:
    None

## Returns:
    widgets.HTML: An ipywidgets.HTML widget instance containing the HTML content. When content["html"] is already a widget, it returns that widget unchanged.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The object must have a content dictionary with an "html" key containing either a string or widget instance.
    Postconditions: Returns a widgets.HTML widget instance when content["html"] is a string, otherwise returns the original widget instance.

## Side Effects:
    None

