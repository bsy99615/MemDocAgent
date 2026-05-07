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
Provides HTML-specific rendering capabilities for data profiling reports by implementing concrete presentation layer components that transform structured data into HTML markup using Jinja2 templates.

## Description:
This module implements the HTML presentation flavour of the ydata-profiling report generation system. It contains concrete implementations of various presentation components that extend base classes from the parent presentation layer, providing HTML-specific rendering logic for different types of data visualization and report elements.

The module serves as the bridge between structured data components and their HTML representation in generated reports. It leverages Jinja2 templating to ensure consistent styling and layout across different HTML report elements while maintaining separation between data models and presentation logic.

## Components:
*   `HTMLAlerts` - Renders data quality alerts with type-specific styling using Jinja2 templates
*   `HTMLCollapse` - Implements collapsible UI components for HTML reports using Jinja2 templates
*   `HTMLContainer` - Renders various sequence-based layouts (lists, grids, tabs) as HTML using appropriate templates
*   `HTMLCorrelationTable` - Converts correlation matrices into styled HTML tables with Bootstrap classes
*   `HTMLDropdown` - Generates HTML dropdown UI elements using Jinja2 templates
*   `HTMLDuplicate` - Renders duplicate data findings as HTML tables with appropriate styling
*   `HTMLFrequencyTable` - Displays frequency distribution data as HTML tables with support for grouped data
*   `HTMLFrequencyTableSmall` - Renders small frequency tables with simplified structure
*   `HTMLHTML` - Directly returns raw HTML content for HTML output format
*   `HTMLImage` - Renders image elements using diagram.html templates for HTML reports
*   `HTMLRoot` - Processes report structure and renders complete HTML reports with navigation
*   `HTMLSample` - Presents data samples as styled HTML tables for report display
*   `HTMLTable` - Renders tabular data as HTML tables using Jinja2 templates
*   `create_html_assets` - Prepares and organizes CSS and JavaScript assets for HTML reports
*   `template` - Centralized accessor for retrieving Jinja2 templates from the global environment
*   `HTMLToggleButton` - Implements interactive toggle buttons for HTML reports using templates
*   `HTMLVariable` - Renders variable data elements as HTML using variable.html templates
*   `HTMLVariableInfo` - Transforms variable metadata into HTML markup for report display

```mermaid
graph TD
    A[HTMLAlerts] --> B[Alerts]
    A --> C[templates.template("alerts.html")]
    D[HTMLCollapse] --> E[Collapse]
    D --> F[templates.template("collapse.html")]
    G[HTMLContainer] --> H[Container]
    G --> I[templates.template("sequence/*.html")]
    J[HTMLCorrelationTable] --> K[CorrelationTable]
    J --> L[templates.template("correlation_table.html")]
    M[HTMLDropdown] --> N[Dropdown]
    M --> O[templates.template("dropdown.html")]
    P[HTMLDuplicate] --> Q[Duplicate]
    P --> R[templates.template("duplicate.html")]
    S[HTMLFrequencyTable] --> T[FrequencyTable]
    S --> U[templates.template("frequency_table.html")]
    V[HTMLFrequencyTableSmall] --> W[FrequencyTableSmall]
    V --> X[templates.template("frequency_table_small.html")]
    Y[HTMLHTML] --> Z[HTML]
    Y --> AA[Direct content return]
    AB[HTMLImage] --> AC[Image]
    AB --> AD[templates.template("diagram.html")]
    AE[HTMLRoot] --> AF[Root]
    AE --> AG[templates.template("report.html")]
    AH[HTMLSample] --> AI[Sample]
    AH --> AJ[templates.template("sample.html")]
    AK[HTMLTable] --> AL[Table]
    AK --> AM[templates.template("table.html")]
    AN[create_html_assets] --> AO[Asset management]
    AP[template] --> AQ[Global template access]
    AR[HTMLToggleButton] --> AS[ToggleButton]
    AR --> AT[templates.template("toggle_button.html")]
    AU[HTMLVariable] --> AV[Variable]
    AU --> AW[templates.template("variable.html")]
    AX[HTMLVariableInfo] --> AY[VariableInfo]
    AX --> AZ[templates.template("variable_info.html")]
```

## Public API:
*   `HTMLAlerts` - Renders data quality alerts in HTML format with type-specific styling
*   `HTMLCollapse` - Renders collapsible HTML components using Jinja2 templates
*   `HTMLContainer` - Renders various sequence layouts (lists, grids, tabs) as HTML
*   `HTMLCorrelationTable` - Converts correlation matrices to styled HTML tables
*   `HTMLDropdown` - Generates HTML dropdown UI elements
*   `HTMLDuplicate` - Renders duplicate data findings as HTML tables
*   `HTMLFrequencyTable` - Displays frequency distribution data as HTML tables
*   `HTMLFrequencyTableSmall` - Renders small frequency tables with simplified structure
*   `HTMLHTML` - Returns raw HTML content for HTML output format
*   `HTMLImage` - Renders image elements using diagram templates
*   `HTMLRoot` - Processes report structure and renders complete HTML reports
*   `HTMLSample` - Presents data samples as styled HTML tables
*   `HTMLTable` - Renders tabular data as HTML tables
*   `create_html_assets` - Creates and organizes HTML assets (CSS/JS) for reports
*   `template` - Retrieves Jinja2 templates from the global environment
*   `HTMLToggleButton` - Implements interactive toggle buttons for HTML reports
*   `HTMLVariable` - Renders variable data elements as HTML
*   `HTMLVariableInfo` - Transforms variable metadata into HTML markup

## Dependencies:
*   Internal imports:
    *   `ydata_profiling.report.presentation.abstract` - Base classes for presentation components
    *   `ydata_profiling.config` - Configuration classes for styling and report settings
    *   `ydata_profiling.utils` - Utility functions for data processing
    *   `ydata_profiling.report.presentation.flavours.html.templates` - Template access and asset creation utilities
*   External imports:
    *   `jinja2` - Templating engine for HTML generation
    *   `pandas` - Data manipulation for frequency tables and correlation matrices
    *   `pathlib` - File system path handling for asset management

## Constraints:
*   All components must be instantiated with proper parent class parameters
*   Templates must exist in the Jinja2 environment for successful rendering
*   Content dictionaries must contain required keys expected by templates
*   Asset creation requires proper configuration of HTML settings and output paths
*   Thread safety: Components are stateless and can be safely used in multi-threaded environments
*   Initialization prerequisites: Global Jinja2 environment must be properly configured before using template-based components

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

