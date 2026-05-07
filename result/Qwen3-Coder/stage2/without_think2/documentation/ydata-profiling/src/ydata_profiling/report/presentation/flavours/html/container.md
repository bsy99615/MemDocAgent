# `container.py`

## `src.ydata_profiling.report.presentation.flavours.html.container.HTMLContainer` · *class*

## Summary:
HTMLContainer is a concrete implementation that renders structured content sequences as HTML.

## Description:
HTMLContainer is a subclass of Container that provides HTML rendering functionality for structured content. It overrides the render method to generate HTML output by selecting and populating appropriate HTML templates based on the container's sequence_type. This class serves as the HTML presentation layer for container objects in the ydata-profiling report system.

The class is designed to be instantiated by the presentation layer during report generation when HTML output is required. It leverages template-based rendering to produce semantically correct HTML structures for different container types like lists, grids, tabs, and sections.

## State:
- sequence_type: str - Defines the semantic type of the container's sequence (e.g., "list", "grid", "tabs"). Required parameter that determines which HTML template to use.
- content: dict - Dictionary containing all configuration parameters and metadata inherited from Renderable parent class, including:
  * anchor_id: str - Unique identifier for HTML anchors
  * items: Sequence[Renderable] - Sequence of renderable items to display
  * nested: bool - Flag indicating nested structures (used in tabs/select templates)
  * full_width: bool - Flag for full-width sections (used in sections template)
  * batch_size: int - Size parameter for batch grid layouts (used in batch_grid template)
  * titles: bool - Flag for displaying titles in batch grids (default: True)
  * subtitles: bool - Flag for displaying subtitles in batch grids (default: False)

## Lifecycle:
- Creation: Instantiate with a sequence of Renderable items, required sequence_type parameter, and optional metadata. The constructor inherits from Container base class.
- Usage: Call render() method to generate HTML output. The method dispatches to appropriate HTML templates based on sequence_type.
- Destruction: No explicit cleanup required; relies on Python's garbage collection.

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
    B -->|other| J[ValueError]
    C --> K[Render list template]
    D --> L[Render named list template]
    E --> M[Render tabs template]
    F --> N[Render select template]
    G --> O[Render sections template]
    H --> P[Render grid template]
    I --> Q[Render batch grid template]
```

## Raises:
- ValueError: When the sequence_type is not recognized or supported by any of the available HTML templates

## Example:
```python
# Create an HTML container with list sequence type
items = [Text("Item 1"), Text("Item 2")]
container = HTMLContainer(items, sequence_type="list", name="my_list")

# Render HTML output
html_output = container.render()
# Returns HTML string for a list structure
```

### `src.ydata_profiling.report.presentation.flavours.html.container.HTMLContainer.render` · *method*

## Summary:
Renders HTML content for a container by selecting and populating appropriate HTML templates based on sequence type.

## Description:
This method implements the HTML rendering logic for container objects by dispatching to different HTML templates based on the container's sequence_type. It serves as the primary rendering entry point for HTML containers, providing a clean separation between container logic and presentation template rendering.

The method acts as a template dispatcher that routes rendering requests to specific HTML templates depending on the semantic type of the container's content. This approach enables consistent rendering behavior across different container types while allowing each template to handle its specific HTML structure and data requirements.

Known callers:
- Called by the presentation layer during report generation when HTML output is required
- Invoked as part of the standard rendering pipeline when processing container objects in HTML format

This logic is separated into its own method rather than being inlined because it handles multiple template selection cases and provides a centralized location for HTML rendering logic, making it easier to maintain and extend with new container types.

## Args:
    None - This is a method that operates on the instance's state

## Returns:
    str - The rendered HTML string containing the properly formatted content for the container's sequence type

## Raises:
    ValueError - When the sequence_type is not recognized or supported by any of the available templates

## State Changes:
    Attributes READ: 
    - self.sequence_type: Used to determine which template to render
    - self.content: Contains the data needed for template rendering including:
      * anchor_id: Unique identifier for HTML anchors
      * items: Sequence of renderable items to display
      * nested: Boolean flag for nested structures
      * full_width: Boolean flag for full-width sections
      * batch_size: Size parameter for batch grid layouts
      * titles: Boolean flag for displaying titles in batch grids
      * subtitles: Boolean flag for displaying subtitles in batch grids

## Constraints:
    Preconditions:
    - self.sequence_type must be one of the supported types: "list", "accordion", "named_list", "tabs", "select", "sections", "grid", "batch_grid"
    - self.content must contain the required keys for the selected template type
    - All items in self.content["items"] must be valid renderable objects that can be processed by the respective templates

    Postconditions:
    - Returns a valid HTML string that represents the container's content according to the specified sequence type
    - The returned HTML string is properly formatted and ready for inclusion in web pages

## Side Effects:
    None - This method performs no I/O operations or external service calls. It only processes internal state and returns a string.

