# `duplicate.py`

## `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.flavours.widget.duplicate.WidgetDuplicate.render` · *method*

## Summary:
Generates a widget-based UI representation showing duplicate data and its associated name in a vertically stacked layout.

## Description:
This method implements the widget presentation flavour for duplicate data visualization. It creates a vertical box container (VBox) that displays duplicate data within an Output widget and presents the name as an HTML heading. This follows the established pattern in the ydata-profiling widget framework for consistent UI rendering of report elements.

The method is part of the WidgetDuplicate class, which inherits from the abstract Duplicate class. While the parent class defines the interface and basic structure, this implementation provides the concrete widget-based rendering for Jupyter notebook environments.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container widget containing exactly two children in order:
        1. widgets.HTML widget displaying the name as an h4 heading
        2. widgets.Output widget displaying the duplicate content

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self.content["duplicate"]: The duplicate data to be displayed
    - self.content["name"]: The name/title to be displayed as heading
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content dictionary must contain both "duplicate" and "name" keys
    - The "duplicate" value must be compatible with IPython.display.display() function
    - The "name" value must be convertible to string for HTML rendering
    
    Postconditions:
    - Returns a properly structured widgets.VBox with exactly two children
    - The first child is an HTML heading element with the name
    - The second child is an Output widget containing the duplicate data

## Side Effects:
    - Creates ipywidgets.Output and widgets.HTML instances
    - Invokes IPython.core.display.display() function to render content within the Output widget
    - May trigger side effects from the underlying display() call on the duplicate content

