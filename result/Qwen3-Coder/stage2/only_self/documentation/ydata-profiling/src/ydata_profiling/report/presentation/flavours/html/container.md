# `container.py`

## `src.ydata_profiling.report.presentation.flavours.html.container.HTMLContainer` · *class*

## Summary:
HTMLContainer is a presentation layer component that renders HTML templates for various sequence-based UI layouts.

## Description:
HTMLContainer extends the base Container class to provide HTML-specific rendering capabilities for different sequence types. It serves as a bridge between structured data containers and their HTML presentation, supporting multiple layout patterns such as lists, grids, tabs, and accordions. This class is typically instantiated by the report generation system when creating HTML output and is responsible for converting container data into appropriate HTML markup.

## State:
- sequence_type: str - Defines the type of HTML layout to render (supported values: "list", "accordion", "named_list", "tabs", "select", "sections", "grid", "batch_grid")
- content: dict - Dictionary containing rendering parameters inherited from parent Container class, including items, anchor_id, nested flag, and other sequence-specific options
- items: Sequence[Renderable] - Collection of renderable components to be displayed within the container
- anchor_id: Optional[str] - HTML anchor ID for linking to this container section
- nested: bool - Flag indicating whether this container contains nested containers

## Lifecycle:
- Creation: Instantiated with a sequence of Renderable items and a sequence_type string
- Usage: Called via render() method to generate HTML output for the specified sequence type
- Destruction: No special cleanup required; relies on Python garbage collection

## Method Map:
```mermaid
graph TD
    A[HTMLContainer.render] --> B{sequence_type}
    B -->|list/accordion| C[templates.template("sequence/list.html")]
    B -->|named_list| D[templates.template("sequence/named_list.html")]
    B -->|tabs| E[templates.template("sequence/tabs.html")]
    B -->|select| F[templates.template("sequence/select.html")]
    B -->|sections| G[templates.template("sequence/sections.html")]
    B -->|grid| H[templates.template("sequence/grid.html")]
    B -->|batch_grid| I[templates.template("sequence/batch_grid.html")]
    B -->|unknown| J[ValueError]
    
    C --> K[Render list template with anchor_id and items]
    D --> L[Render named list template with anchor_id and items]
    E --> M[Render tabs template with tabs, anchor_id, nested]
    F --> N[Render select template with tabs, anchor_id, nested]
    G --> O[Render sections template with sections, full_width]
    H --> P[Render grid template with items]
    I --> Q[Render batch grid template with items, batch_size, titles, subtitles]
```

## Raises:
- ValueError: When an unsupported sequence_type is provided, with message "Template not understood" followed by the unknown sequence type

## Example:
```python
# Create an HTML container with a list sequence
items = [item1, item2, item3]
container = HTMLContainer(
    items=items,
    sequence_type="list",
    content={"anchor_id": "my-list", "items": items}
)

# Render the HTML output
html_output = container.render()
```

### `src.ydata_profiling.report.presentation.flavours.html.container.HTMLContainer.render` · *method*

## Summary:
Renders HTML content for a container based on its sequence type using Jinja2 templates.

## Description:
This method generates HTML markup for container components by selecting appropriate templates based on the container's sequence type. It processes the container's content dictionary and renders it using predefined HTML templates, supporting various presentation formats including lists, accordions, tabs, grids, and sections.

The method is designed to be called during the report generation pipeline when HTML output is required. It leverages the Jinja2 templating engine to dynamically generate HTML content based on the container's configuration.

## Args:
    None

## Returns:
    str: The rendered HTML string containing the formatted container content

## Raises:
    ValueError: When the sequence_type is not recognized or supported by any available template

## State Changes:
    Attributes READ: 
    - self.sequence_type: Determines which template to use
    - self.content: Provides data for template rendering including items, anchor_id, nested, full_width, batch_size, titles, and subtitles
    
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.sequence_type must be one of the supported types: "list", "accordion", "named_list", "tabs", "select", "sections", "grid", "batch_grid"
    - self.content must contain the required keys for the selected template type
    - All items in self.content["items"] must be renderable components
    
    Postconditions:
    - Returns a valid HTML string representation of the container content
    - The returned HTML is properly formatted according to the selected template

## Side Effects:
    - Template loading and rendering via Jinja2
    - Potential I/O operations when accessing template files
    - May raise ValueError if template configuration is invalid

