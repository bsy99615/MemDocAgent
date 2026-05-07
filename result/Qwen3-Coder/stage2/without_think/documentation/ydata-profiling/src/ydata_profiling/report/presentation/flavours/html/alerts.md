# `alerts.py`

## `src.ydata_profiling.report.presentation.flavours.html.alerts.HTMLAlerts` · *class*

## Summary:
HTMLAlerts is a presentation layer component that renders data quality alerts in HTML format with type-specific styling.

## Description:
The HTMLAlerts class implements the HTML-specific rendering of data quality alerts generated during data profiling. It extends the core Alerts class and provides the concrete implementation of the render() method for HTML output. This component transforms alert data into styled HTML elements for inclusion in profiling reports.

This class is typically instantiated by the profiling system when data quality issues are detected and needs to be displayed in an HTML report. It leverages Jinja2 templating to generate the final HTML output, applying appropriate CSS styling based on alert types.

## State:
- styles: dict - Maps alert category names to CSS style classes for visual differentiation
- content: dict - Inherited from parent Alerts class, contains the alert data and configuration to be rendered
- item_type: str - Inherited from ItemRenderer, set to "alerts" to identify this component type
- name: Optional[str] - Inherited from Renderable, human-readable identifier for the alerts section
- anchor_id: Optional[str] - Inherited from Renderable, unique identifier for HTML anchors
- classes: Optional[str] - Inherited from Renderable, CSS classes for additional styling

## Lifecycle:
- Creation: Instantiated with alert data and styling configuration, inheriting from Alerts parent class
- Usage: Implements the abstract render interface from the parent Alerts class to produce HTML output for displaying data quality alerts in profiling reports
- Destruction: Managed automatically by Python's garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLAlerts.render] --> B[templates.template("alerts.html")]
    B --> C[alerts.html template rendering]
    C --> D[self.content + styles]
```

## Raises:
- No explicit exceptions raised by HTMLAlerts.__init__
- Template rendering errors may occur if the "alerts.html" template is missing or malformed
- Inherited exceptions from parent Alerts class if improperly initialized

## Example:
```python
from ydata_profiling.report.presentation.flavours.html.alerts import HTMLAlerts

# Assuming self.content contains alert data
html_alerts = HTMLAlerts(content={"alerts": [...]})
html_output = html_alerts.render()
# Returns HTML string with styled alerts
```

### `src.ydata_profiling.report.presentation.flavours.html.alerts.HTMLAlerts.render` · *method*

## Summary:
Generates HTML markup for data quality alerts with type-specific styling by rendering the alerts.html template.

## Description:
This method implements the abstract render interface from the parent Alerts class to produce HTML output for displaying data quality alerts in profiling reports. It applies CSS styling categories to different alert types and renders them using the alerts.html Jinja2 template. The method is invoked during the HTML report generation phase when formatted alerts need to be embedded in the final output.

The separation of this logic into its own method allows for consistent styling and templating of alerts while maintaining clean separation between data processing and presentation concerns.

## Args:
    None

## Returns:
    str: HTML string containing formatted alerts with appropriate CSS styling classes applied to each alert type

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: 
    - self.content: Dictionary containing alert data that is unpacked and passed to the template
    - self.style: Style configuration (inherited from parent class, though not directly used in this method)

    Attributes WRITTEN: 
    - None

## Constraints:
    Preconditions:
    - self.content must be a dictionary that can be unpacked with ** operator
    - The alerts.html template must exist in the template directory
    - Alert category keys in self.content must match those defined in the styles dictionary
    - All alert data in self.content should be compatible with the alerts.html template structure

    Postconditions:
    - Returns a properly formatted HTML string with styled alerts
    - All alert types in self.content are mapped to appropriate CSS classes from the predefined styles dictionary

## Side Effects:
    None

