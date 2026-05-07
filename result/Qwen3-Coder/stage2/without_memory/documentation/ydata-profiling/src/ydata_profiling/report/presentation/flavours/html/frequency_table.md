# `frequency_table.py`

## `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable` · *class*

*No documentation generated.*

### `src.ydata_profiling.report.presentation.flavours.html.frequency_table.HTMLFrequencyTable.render` · *method*

## Summary:
Renders frequency table data into HTML format, handling both single and multiple row set structures.

## Description:
This method transforms frequency table content into HTML markup using a Jinja2 template. It supports two different data structures for the rows field: either a single list of rows or a list of lists representing multiple row sets. The method dynamically chooses the appropriate rendering strategy based on the structure of the first element in the rows collection.

When rows[0] is a list, the method iterates through multiple row sets, rendering each with a separate template call while preserving other content parameters. When rows[0] is not a list, it renders a single row set directly.

The method is called during the HTML report generation phase when frequency table content needs to be displayed in the final report. It's part of the HTML presentation flavour implementation and is invoked by the reporting pipeline when rendering frequency table components.

## Args:
    None (uses self instance attributes)

## Returns:
    str: HTML string representation of the frequency table

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
    - self.content must contain a "rows" key with valid data structure
    - The first element of self.content["rows"] must be either a list or non-list type
    - The "frequency_table.html" template must be available in the templates system
    - self.content must be a dictionary with proper structure
    
    Postconditions:
    - Returns properly formatted HTML string
    - Does not modify the original self.content structure
    - Template rendering succeeds without errors

## Side Effects:
    - Calls templates.template() to retrieve the Jinja2 template
    - Renders HTML content using Jinja2 templating engine
    - May perform I/O operations when accessing template files

