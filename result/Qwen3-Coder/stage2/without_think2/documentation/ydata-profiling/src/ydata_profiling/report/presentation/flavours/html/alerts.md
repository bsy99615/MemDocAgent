# `alerts.py`

## `src.ydata_profiling.report.presentation.flavours.html.alerts.HTMLAlerts` · *class*

## Summary:
HTMLAlerts is an HTML-specific implementation that renders data quality alerts for profiling reports.

## Description:
The HTMLAlerts class extends the base Alerts class to provide HTML-specific rendering functionality for data quality alerts. It maps different alert types to Bootstrap-style CSS classes and uses a Jinja2 template to generate HTML output. This component is part of the HTML report generation pipeline and transforms alert data into visually styled HTML elements that can be embedded in profiling reports.

The class is instantiated during report generation when HTML-formatted alerts need to be displayed. It inherits alert data and styling configuration from its parent Alerts class while implementing the concrete render() method for HTML output.

## State:
- content: dict - Dictionary containing alert data and styling information inherited from the parent Alerts class. This contains the raw alert information that gets processed and rendered.
- styles: dict - Mapping of alert type strings to CSS style classes (warning, primary, info, default) that determines the visual appearance of different alert types in the rendered HTML.

## Lifecycle:
- Creation: Instantiated by the reporting system when HTML alerts need to be rendered. Requires the parent Alerts class to have properly initialized content with alert data.
- Usage: Called during report generation when the HTML template needs to display alert information. The render() method is invoked to produce HTML output.
- Destruction: Managed by Python's garbage collector; no explicit cleanup required.

## Method Map:
```mermaid
graph TD
    A[HTMLAlerts.render] --> B[templates.template("alerts.html")]
    B --> C[Jinja2 Template Rendering]
    C --> D[HTML Output]
```

## Raises:
- None explicitly raised by this method
- However, underlying template rendering may raise exceptions if the 'alerts.html' template is missing or malformed

## Example:
```python
# During report generation workflow
from ydata_profiling.report.presentation.flavours.html.alerts import HTMLAlerts

# Assuming alerts_data and style_config are properly initialized
alerts_renderer = HTMLAlerts(alerts_data, style_config)
html_output = alerts_renderer.render()

# Returns HTML string like:
# <div class="alert alert-warning">Constant value detected</div>
# <div class="alert alert-primary">High cardinality detected</div>
```

### `src.ydata_profiling.report.presentation.flavours.html.alerts.HTMLAlerts.render` · *method*

## Summary:
Renders HTML-formatted alerts using a Jinja2 template with predefined styling categories.

## Description:
This method implements the HTML-specific rendering logic for alert data by mapping alert types to CSS styles and rendering them using the 'alerts.html' template. It transforms the alert data stored in self.content into an HTML representation suitable for inclusion in profiling reports. This method overrides the abstract render method from the parent Alerts class to provide HTML-specific functionality.

The method uses a predefined style mapping to assign appropriate Bootstrap-style CSS classes to different alert types, ensuring consistent visual presentation of data quality warnings in profiling reports.

## Args:
    None

## Returns:
    str: HTML string containing the formatted alerts with appropriate styling

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must be a dictionary containing alert data that can be unpacked with ** operator
    - The 'alerts.html' template must exist in the template directory
    - All alert types referenced in the styles dictionary must be present in self.content
    - This method assumes the parent class has properly initialized content with alert data

    Postconditions:
    - Returns a properly formatted HTML string with styled alerts
    - The returned HTML maintains the structure defined by the 'alerts.html' template
    - The HTML includes proper styling classes mapped to alert types

## Side Effects:
    - Calls templates.template() which may involve filesystem or cache operations
    - Renders Jinja2 template which could involve string processing and formatting
    - Depends on the existence of 'alerts.html' template file in the template directory

