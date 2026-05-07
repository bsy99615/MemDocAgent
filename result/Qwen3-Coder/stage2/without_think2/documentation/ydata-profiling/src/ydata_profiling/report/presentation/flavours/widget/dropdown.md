# `dropdown.py`

## `src.ydata_profiling.report.presentation.flavours.widget.dropdown.WidgetDropdown` · *class*

## Summary:
WidgetDropdown is a presentation component that renders an interactive dropdown widget using ipywidgets, allowing users to select from a list of items and dynamically control the display of nested content.

## Description:
WidgetDropdown implements the abstract Dropdown class to provide a concrete widget-based rendering solution for dropdown menus in Jupyter environments. It creates an interactive dropdown interface that synchronizes with a nested item component, enabling dynamic content switching based on user selection. This component is specifically designed for use in widget-based presentations and integrates with ipywidgets' event system for real-time updates.

The class serves as a bridge between the abstract dropdown presentation layer and concrete widget implementations, making it suitable for interactive data profiling reports in Jupyter notebooks. It's typically instantiated by the presentation rendering engine when processing dropdown-type content in report templates.

## State:
- content: dict - Dictionary containing dropdown configuration including "items" (list), "name" (str), and "item" (Container or None)
- self.content["items"]: list - Collection of selectable options for the dropdown menu
- self.content["name"]: str - Label text displayed next to the dropdown widget
- self.content["item"]: Container or None - Nested container whose selection state is controlled by the dropdown
- self.content["item"].content["items"]: list - Items contained within the nested container, used for title mapping
- self.content["item"].content["items"][i].name: str - Name attribute of each item in the nested container for selection mapping

## Lifecycle:
- Creation: Instantiate with a content dictionary containing "items", "name", and optional "item" keys. The content structure is inherited from the parent Dropdown class.
- Usage: Call the render() method to generate the ipywidgets.VBox containing the dropdown and nested item. The dropdown automatically observes value changes and updates the nested item's selection state.
- Destruction: No explicit cleanup required; relies on Python's garbage collection for widget disposal.

## Method Map:
```mermaid
graph TD
    A[WidgetDropdown.render] --> B[widgets.Dropdown]
    B --> C[dropdown.observe(change_view)]
    C --> D[change_view callback]
    D --> E[item.selected_index = index]
    A --> F[widgets.VBox]
    F --> G[dropdown]
    F --> H[item]
```

## Raises:
- None explicitly raised by WidgetDropdown itself
- May raise exceptions from ipywidgets.Dropdown construction if invalid parameters are passed
- May raise exceptions from widgets.VBox construction if invalid children are provided

## Example:
```python
# Create a dropdown with nested content
nested_container = Container([Text("Detail 1"), Text("Detail 2")], sequence_type="list")
dropdown = WidgetDropdown({
    "items": ["Option 1", "Option 2"],
    "name": "Select Option",
    "item": nested_container
})

# Render the widget
widget_box = dropdown.render()
# Displays a dropdown that controls the nested container's selection
```

### `src.ydata_profiling.report.presentation.flavours.widget.dropdown.WidgetDropdown.render` · *method*

## Summary:
Renders a dropdown widget that controls the selection of a nested item component, returning a vertical box containing the dropdown and the selected item.

## Description:
This method creates an interactive dropdown widget using ipywidgets that allows users to select from a list of items. When an item is selected, it updates the associated nested item component's selection state. The method is part of the WidgetDropdown class and integrates with the ipywidgets event system to synchronize the dropdown selection with the nested item's display state.

The render method constructs a dropdown widget populated with options from self.content["items"] and a description from self.content["name"]. It then processes the nested item to extract titles for mapping selections back to indices. When a user selects an option from the dropdown, the change_view callback updates the nested item's selected_index property accordingly.

## Args:
    None

## Returns:
    widgets.VBox: A vertical box container holding the dropdown widget and the rendered nested item, or just the dropdown if no nested item exists. The VBox contains widgets.Dropdown and potentially another rendered widget.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - self.content must contain keys "items" and "name"
    - self.content["item"] must be either None or have a content attribute with "items"
    - The nested item's content["items"] must contain objects with a "name" attribute
    Postconditions:
    - The returned VBox contains the dropdown widget and optionally the nested item
    - The dropdown's value changes will update the nested item's selected_index

## Side Effects:
    - Creates ipywidgets.Dropdown and widgets.VBox instances
    - Registers an observer on the dropdown widget for value changes
    - May modify the selected_index attribute of the nested item component

