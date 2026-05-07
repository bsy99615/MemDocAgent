# `src.ydata_profiling.report.presentation.flavours.html`

## Tree:
```
html/
├── alerts.py
├── collapse.py
├── container.py
├── correlation_table.py
├── dropdown.py
├── duplicate.py
├── frequency_table.py
├── frequency_table_small.py
├── html.py
├── image.py
├── root.py
├── sample.py
├── table.py
├── templates.py
├── toggle_button.py
├── variable.py
└── variable_info.py
```

## Role:
Renders data profiling reports in HTML format by implementing concrete presentation components that transform structured data into HTML markup.

## Description:
This module provides the HTML-specific implementations of presentation components used in data profiling reports. It contains concrete classes that extend abstract base classes from the core presentation layer to generate HTML output for various report elements like tables, variables, alerts, and visualizations.

The module is organized around the concept of HTML presentation flavours, where each component is responsible for rendering a specific type of report element in HTML format. These components work together to create complete, styled HTML reports that can be viewed in web browsers.

Primary consumers of this module include:
- Report generation pipeline components that need to produce HTML output
- Presentation layer factories that instantiate appropriate HTML renderers
- Template rendering systems that require HTML-specific implementations

The cohesion of this module is based on the shared requirement of generating HTML output for data profiling reports, with each component specializing in a particular type of report element while maintaining consistent interfaces through inheritance from abstract base classes.

## Components:
* `HTMLAlerts` - Renders data quality alerts in HTML format with type-specific styling
* `HTMLCollapse` - Renders collapsible UI components using Jinja2 templates
* `HTMLContainer` - Renders structured content using HTML templates based on sequence type
* `HTMLCorrelationTable` - Renders correlation matrix data as HTML tables
* `HTMLDropdown` - Renders dropdown interface elements in HTML format
* `HTMLDuplicate` - Renders duplicate data findings as HTML tables with Bootstrap styling
* `HTMLFrequencyTable` - Renders frequency distribution data as HTML content
* `HTMLFrequencyTableSmall` - Renders small frequency tables as HTML for compact displays
* `HTMLHTML` - Renders raw HTML content from a content dictionary
* `HTMLImage` - Renders image elements using HTML templates
* `HTMLRoot` - Renders complete profiling reports as HTML documents
* `HTMLSample` - Renders data samples as HTML tables with Bootstrap styling
* `HTMLTable` - Renders tabular data as HTML strings using templates
* `HTMLToggleButton` - Renders toggle button UI components in HTML format
* `HTMLVariable` - Renders variable content using HTML templates
* `HTMLVariableInfo` - Renders variable information as HTML content

```mermaid
graph TD
    A[HTMLAlerts] --> B[templates.template("alerts.html")]
    A --> C[Alerts]
    A --> D[ItemRenderer]
    A --> E[Renderable]
    
    B --> F[alerts.html template]
    
    A --> G[HTMLRoot]
    
    A --> H[HTMLCollapse]
    H --> I[templates.template("collapse.html")]
    I --> J[collapse.html template]
    
    A --> K[HTMLContainer]
    K --> L[templates.sequence.*.html]
    
    A --> M[HTMLCorrelationTable]
    M --> N[templates.template("correlation_table.html")]
    N --> O[correlation_table.html template]
    
    A --> P[HTMLDropdown]
    P --> Q[templates.template("dropdown.html")]
    Q --> R[dropdown.html template]
    
    A --> S[HTMLDuplicate]
    S --> T[templates.template("duplicate.html")]
    T --> U[duplicate.html template]
    
    A --> V[HTMLFrequencyTable]
    V --> W[templates.template("frequency_table.html")]
    W --> X[frequency_table.html template]
    
    A --> Y[HTMLFrequencyTableSmall]
    Y --> Z[templates.template("frequency_table_small.html")]
    Z --> AA[frequency_table_small.html template]
    
    A --> AB[HTMLHTML]
    AB --> AC[Direct content return]
    
    A --> AD[HTMLImage]
    AD --> AE[templates.template("diagram.html")]
    AE --> AF[diagram.html template]
    
    A --> AG[HTMLRoot]
    AG --> AH[templates.template("report.html")]
    AH --> AI[report.html template]
    
    A --> AJ[HTMLSample]
    AJ --> AK[templates.template("sample.html")]
    AK --> AL[sample.html template]
    
    A --> AM[HTMLTable]
    AM --> AN[templates.template("table.html")]
    AN --> AO[table.html template]
    
    A --> AP[HTMLToggleButton]
    AP --> AQ[templates.template("toggle_button.html")]
    AQ --> AR[toggle_button.html template]
    
    A --> AS[HTMLVariable]
    AS --> AT[templates.template("variable.html")]
    AT --> AU[variable.html template]
    
    A --> AV[HTMLVariableInfo]
    AV --> AW[templates.template("variable_info.html")]
    AW --> AX[variable_info.html template]
```

## Public API:
* `HTMLAlerts(content)` - Renders data quality alerts in HTML format
* `HTMLCollapse(collapse)` - Renders collapsible UI components using Jinja2 templates
* `HTMLContainer(items, sequence_type, content)` - Renders structured content using HTML templates
* `HTMLCorrelationTable(name, correlation_matrix)` - Renders correlation matrix data as HTML tables
* `HTMLDropdown(name, id, items, item, anchor_id, classes, is_row)` - Renders dropdown interface elements in HTML format
* `HTMLDuplicate(name, duplicate)` - Renders duplicate data findings as HTML tables with Bootstrap styling
* `HTMLFrequencyTable(rows, redact)` - Renders frequency distribution data as HTML content
* `HTMLFrequencyTableSmall(rows, redact, **kwargs)` - Renders small frequency tables as HTML for compact displays
* `HTMLHTML(content)` - Renders raw HTML content from a content dictionary
* `HTMLImage(image, image_format, alt, caption)` - Renders image elements using HTML templates
* `HTMLRoot(name, body, footer, style)` - Renders complete profiling reports as HTML documents
* `HTMLSample(name, sample, caption)` - Renders data samples as HTML tables with Bootstrap styling
* `HTMLTable(rows, style, name, caption)` - Renders tabular data as HTML strings using templates
* `HTMLToggleButton(text, **kwargs)` - Renders toggle button UI components in HTML format
* `HTMLVariable(top, bottom, ignore)` - Renders variable content using HTML templates
* `HTMLVariableInfo(anchor_id, var_name, var_type, alerts, description, style)` - Renders variable information as HTML content

## Dependencies:
* Internal: `ydata_profiling.report.presentation.core` - Core presentation classes that define the abstract interfaces
* Internal: `ydata_profiling.report.presentation.flavours.html.templates` - Template loading utilities for HTML rendering
* External: `jinja2` - Templating engine for HTML generation
* External: `pandas` - Data manipulation for table rendering
* External: `typing` - Type hints for better code documentation

## Constraints:
* All HTML components must inherit from their respective abstract base classes in the core presentation layer
* Template files must exist in the template directory for proper rendering
* Content dictionaries must contain required keys expected by the corresponding templates
* HTML components should be instantiated with appropriate parameters matching their parent class constructors
* Thread safety: Components are stateless and can be safely used in multi-threaded environments
* Initialization: Template environment must be properly configured before using any HTML components

---

## Files

- [`alerts.py`](html/alerts.md)
- [`collapse.py`](html/collapse.md)
- [`container.py`](html/container.md)
- [`correlation_table.py`](html/correlation_table.md)
- [`dropdown.py`](html/dropdown.md)
- [`duplicate.py`](html/duplicate.md)
- [`frequency_table.py`](html/frequency_table.md)
- [`frequency_table_small.py`](html/frequency_table_small.md)
- [`html.py`](html/html.md)
- [`image.py`](html/image.md)
- [`root.py`](html/root.md)
- [`sample.py`](html/sample.md)
- [`table.py`](html/table.md)
- [`templates.py`](html/templates.md)
- [`toggle_button.py`](html/toggle_button.md)
- [`variable.py`](html/variable.md)
- [`variable_info.py`](html/variable_info.md)

