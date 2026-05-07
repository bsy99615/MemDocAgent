# `root.py`

## `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot` · *class*

## Summary:
WidgetRoot is a presentation layer class that renders content as a vertical box widget for Jupyter notebook interfaces.

## Description:
WidgetRoot is a concrete implementation of the Root class designed for widget-based user interfaces. It provides a render method that organizes content into a vertical layout using ipywidgets.VBox. This class is specifically intended for use in Jupyter notebook environments where widget-based visualizations are preferred.

## State:
- content: Dictionary-like structure containing "body" and "footer" keys that must have render() methods
- The content structure is inherited from the parent Root class

## Lifecycle:
- Creation: Instantiated with standard constructor from Root parent class
- Usage: Called via render() method to generate a widgets.VBox object containing body and footer content
- Destruction: No explicit cleanup required as ipywidgets handle their own lifecycle

## Method Map:
```mermaid
graph TD
    A[WidgetRoot.render] --> B[content["body"].render()]
    A --> C[content["footer"].render()]
    B --> D[widgets.VBox]
    C --> D
```

## Raises:
- KeyError: If content dictionary doesn't contain "body" or "footer" keys
- AttributeError: If content["body"] or content["footer"] don't have render() methods

## Example:
```python
# Create WidgetRoot instance (inherited from Root)
root = WidgetRoot()

# Render the content as a vertical widget layout
widget = root.render()

# The result is a widgets.VBox containing body and footer content
```

### `src.ydata_profiling.report.presentation.flavours.widget.root.WidgetRoot.render` · *method*

## Summary:
Renders the widget-based report interface by combining the body and footer components into a vertical box layout.

## Description:
This method constructs a widget-based user interface by rendering the body and footer components stored in the content dictionary and arranging them vertically using ipywidgets.VBox. It serves as the main entry point for generating the visual representation of a widget-based report.

## Args:
    **kwargs: Additional keyword arguments passed through to child render methods (not directly used in current implementation)

## Returns:
    widgets.VBox: A vertical box container widget containing the rendered body and footer components

## Raises:
    AttributeError: If self.content does not contain 'body' or 'footer' keys, or if these components lack a render method
    TypeError: If the rendered body or footer components do not return valid widget objects

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must be a dictionary containing 'body' and 'footer' keys
    - Both self.content['body'] and self.content['footer'] must have render() methods that return widget objects
    - The render() methods of body and footer components must be compatible with the ipywidgets framework
    
    Postconditions:
    - Returns a widgets.VBox instance containing two child widgets
    - The body widget appears before the footer widget in the vertical arrangement

## Side Effects:
    None

