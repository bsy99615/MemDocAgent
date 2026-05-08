# `html.py`

## `src.ydata_profiling.report.presentation.flavours.widget.html.WidgetHTML` · *class*

## Summary:
WidgetHTML is a specialized HTML renderer that generates ipywidgets.HTML objects for use in Jupyter notebook environments.

## Description:
The WidgetHTML class extends the base HTML class to provide rendering functionality specifically tailored for Jupyter notebook environments using ipywidgets. It transforms HTML content into interactive widgets that can be displayed within Jupyter notebooks. This class acts as a bridge between static HTML content and interactive widget-based presentation in notebook contexts.

## State:
- Inherits all attributes from HTML parent class including content (dict with "html" key), item_type, and metadata fields
- The content dictionary must contain an "html" key with either a string value or an existing widgets.HTML object
- No additional instance attributes beyond those inherited from HTML
- The content["html"] field can be either a string containing HTML markup or an existing widgets.HTML widget instance

## Lifecycle:
- Creation: Instantiate with HTML content (string or widgets.HTML object) and optional metadata via parent HTML class constructor
- Usage: Call render() method to convert content into a widgets.HTML widget
- Destruction: Relies on Python's garbage collection; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[WidgetHTML.render] --> B[type check of content["html"]]
    B --> C{content["html"] is str?}
    C -->|Yes| D[widgets.HTML(content["html"])]
    C -->|No| E[return content["html"]]
```

## Raises:
- No explicit exceptions raised by WidgetHTML.__init__
- The parent HTML class constructor may raise exceptions for invalid arguments

## Example:
```python
# Create WidgetHTML with HTML string content
widget_html = WidgetHTML("<h1>Hello World</h1>")

# Render to ipywidgets.HTML object
widget = widget_html.render()

# Create WidgetHTML with existing widgets.HTML object
existing_widget = widgets.HTML("<p>Existing widget</p>")
widget_html2 = WidgetHTML(existing_widget)
widget2 = widget_html2.render()
```

### `src.ydata_profiling.report.presentation.flavours.widget.html.WidgetHTML.render` · *method*

## Summary:
Converts HTML content into a Jupyter widgets HTML component for display.

## Description:
This method transforms the HTML content stored in the instance into a proper ipywidgets.HTML object suitable for rendering in Jupyter notebooks. The method handles two cases: when the content is already a widget object (returns it directly) or when it's an HTML string (wraps it in a widgets.HTML component).

## Args:
    None

## Returns:
    widgets.HTML: A Jupyter widgets HTML component containing the rendered HTML content.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing an "html" key
    - The value of self.content["html"] must be either a string or a widgets.HTML object
    
    Postconditions:
    - Returns a widgets.HTML object ready for Jupyter display
    - If input was already a widget, returns the same widget object unchanged

## Side Effects:
    None

