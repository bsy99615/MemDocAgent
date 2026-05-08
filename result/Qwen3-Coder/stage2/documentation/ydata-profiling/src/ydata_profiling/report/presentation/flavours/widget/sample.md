# `sample.py`

### `src.ydata_profiling.report.presentation.flavours.widget.sample.WidgetSample.render` · *method*

## Summary:
Renders a data sample as a widget-based UI element displaying the sample data and its name in a structured layout.

## Description:
Creates a widget-based presentation of a data sample by combining a styled heading with the sample data displayed in an output widget. This method transforms the internal sample representation into a visual widget interface suitable for Jupyter notebook environments.

The render method is called during the report generation pipeline when widget-based presentation is selected, specifically during the rendering phase of sample items in the report. It constructs a vertical box layout containing the sample name as an HTML heading and the sample data in a displayable output widget.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container widget containing two elements in order:
    - An HTML widget displaying the sample name as a level-4 heading (<h4>)
    - An Output widget that displays the sample data when rendered

## Raises:
    KeyError: If self.content does not contain the required "sample" or "name" keys.
    Exception: Any exception that may occur during the display operation or widget creation process.

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing "sample" (data to display) and "name" (heading text) keys
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing both "sample" and "name" keys
    - The "sample" value should be compatible with IPython.display.display() function
    - The "name" value should be a string that can be formatted into HTML
    
    Postconditions:
    - Returns a properly constructed widgets.VBox widget with exactly two children
    - The returned widget maintains the sample data in a displayable format
    - The widget structure follows the expected pattern for widget-based report presentation

## Side Effects:
    I/O: Writes to standard output via IPython.display.display() when the output widget is rendered
    Widget creation: Creates new ipywidgets.Output and widgets.VBox objects

