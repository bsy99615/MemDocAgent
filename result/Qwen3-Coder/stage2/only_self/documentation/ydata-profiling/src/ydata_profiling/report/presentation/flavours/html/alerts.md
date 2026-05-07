# `alerts.py`

## `src.ydata_profiling.report.presentation.flavours.html.alerts.HTMLAlerts` · *class*

## Summary:
HTMLAlerts is a presentation layer component that renders data quality alerts in HTML format with type-specific styling.

## Description:
HTMLAlerts extends the base Alerts class to provide HTML-specific rendering capabilities for data quality alerts generated during data profiling. This class transforms alert data into styled HTML markup using Jinja2 templating, applying different CSS styles based on alert types to visually distinguish between various data quality issues.

The component is part of the ydata-profiling report generation system and is specifically designed for HTML report output. It maps alert types to predefined Bootstrap-style CSS classes for consistent visual presentation.

## State:
- Inherits all attributes from Alerts parent class including:
  - alerts: Union[List[Alert], Dict[str, List[Alert]]], containing the alert data to be rendered
  - style: Style, styling configuration for the alert presentation
  - item_type: str, set to "alerts" indicating this is an alerts component
- The content attribute (inherited from ItemRenderer) contains the alert data and styling information
- styles dictionary: Maps alert type strings to Bootstrap CSS style classes for HTML rendering

## Lifecycle:
- Creation: Instantiated with alert data and style configuration via parent Alerts constructor
- Usage: Called by the report generation system when HTML rendering of alerts is required, typically through the render() method
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLAlerts.render] --> B[Create styles dictionary]
    B --> C[templates.template("alerts.html")]
    C --> D[Render with self.content and styles]
    D --> E[Return HTML string]
```

## Raises:
- None explicitly raised by HTMLAlerts.render() method
- May raise exceptions from parent class initialization or Jinja2 template rendering if templates are missing

## Example:
```python
# Typical instantiation (via parent class)
alerts = HTMLAlerts(
    alerts=[alert1, alert2],
    style=Style()
)

# Rendering to HTML
html_output = alerts.render()
# Returns HTML string with styled alerts
```

### `src.ydata_profiling.report.presentation.flavours.html.alerts.HTMLAlerts.render` · *method*

## Summary:
Renders HTML markup for data quality alerts with appropriate styling based on alert types.

## Description:
Generates HTML output for displaying data quality alerts in a web report. This method maps different alert types to CSS styles and uses a Jinja2 template to render the alerts with proper formatting. The method is part of the HTML presentation flavour implementation for alerts.

This logic is separated into its own method rather than being inlined because:
- It encapsulates the HTML rendering logic for alerts
- It provides a clear separation between data preparation (style mapping) and template rendering
- It allows for easy testing and maintenance of the rendering behavior
- It follows the template pattern where different presentation flavours can override this method independently

## Args:
    None: This method takes no parameters beyond the implicit self reference.

## Returns:
    str: HTML string containing the formatted alerts with appropriate styling classes.

## Raises:
    None: This method does not explicitly raise exceptions, though underlying template rendering may raise exceptions if the template is malformed or if required data is missing.

## State Changes:
    Attributes READ: 
    - self.content: Contains the alert data to be rendered (expected to include alerts and potentially other metadata)
    - self.item_type: Inherited from parent class, used for identification

    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain valid alert data that can be processed by the alerts.html template
    - The alerts.html template must exist in the template directory
    - Alert types in self.content must be compatible with the defined style mappings
    - The content dictionary should contain the necessary data structure expected by the template

    Postconditions:
    - Returns a properly formatted HTML string with styled alerts
    - The returned HTML is suitable for inclusion in larger HTML documents

## Side Effects:
    None: This method performs no I/O operations or external service calls. It only processes data and returns HTML string output.

