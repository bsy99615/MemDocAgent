# `toggle_button.py`

## `src.ydata_profiling.report.presentation.flavours.widget.toggle_button.WidgetToggleButton` · *class*

## Summary:
WidgetToggleButton renders a toggle button UI component using ipywidgets for interactive report presentations.

## Description:
The WidgetToggleButton class provides a concrete implementation of the ToggleButton abstract base class specifically designed for Jupyter notebook environments using ipywidgets. It creates interactive toggle buttons that can be used to expand/collapse sections in generated reports. This component is part of the widget-based presentation flavour in the ydata profiling system.

This class should be instantiated when creating interactive report elements that require toggle functionality in Jupyter notebooks. It is typically created by the report generation system when processing toggle button content elements.

## State:
- content: dict - Dictionary containing the button text under the key "text"
- name: Optional[str] - Human-readable name for the button, inherited from Renderable
- anchor_id: Optional[str] - Unique identifier for HTML anchors, inherited from Renderable  
- classes: Optional[str] - CSS classes for styling, inherited from Renderable

## Lifecycle:
- Creation: Instantiate with text content (required) and optional parameters for name, anchor_id, and classes
- Usage: Call render() method to generate the ipywidgets.HBox containing the toggle button
- Destruction: No special cleanup required; relies on Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[WidgetToggleButton.render()] --> B[widgets.ToggleButton]
    B --> C[widgets.HBox]
    C --> D[Return widgets.HBox]
```

## Raises:
- None explicitly raised by this implementation
- May raise exceptions from ipywidgets internals during widget creation

## Example:
```python
# Create a toggle button with text content
button = WidgetToggleButton(content={"text": "Show Details"})

# Render the widget for display in Jupyter
widget = button.render()

# The returned widget can be displayed in a Jupyter cell
display(widget)
```

### `src.ydata_profiling.report.presentation.flavours.widget.toggle_button.WidgetToggleButton.render` · *method*

## Summary:
Creates and configures a styled toggle button widget container for interactive report presentations.

## Description:
Generates a styled toggle button widget wrapped in a horizontal box container with specific layout properties. This method is responsible for creating the visual representation of a toggle button in the widget-based presentation flavour of ydata profiling reports.

The method constructs a toggle button with text content from the component's content dictionary and applies specific CSS layout properties to ensure proper alignment and sizing within the report interface. This logic is separated into its own method to encapsulate the widget creation and styling concerns, making the code more modular and testable.

## Args:
    None - This is an instance method that operates on self

## Returns:
    widgets.HBox: A horizontal box container containing a configured toggle button widget

## Raises:
    KeyError: If self.content does not contain a "text" key (accessed via self.content["text"])
    AttributeError: If self.content is not properly initialized as a dictionary or if the parent class attributes are not set

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing button text under "text" key
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing a "text" key with string value
    - The WidgetToggleButton instance must be properly initialized with required parent class attributes
    - The parent ToggleButton class must have been properly constructed with content
    
    Postconditions:
    - Returns a widgets.HBox instance with properly configured child toggle button
    - The returned HBox has specific flexbox layout properties applied (align_items, display, flex_flow, width)

## Side Effects:
    None - This method performs no I/O operations or external service calls

