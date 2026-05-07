# `dropdown.py`

## `src.ydata_profiling.report.presentation.flavours.widget.dropdown.WidgetDropdown` · *class*

## Summary:
WidgetDropdown renders a dropdown widget interface that dynamically displays associated content based on selection.

## Description:
WidgetDropdown is a presentation layer component that creates an interactive dropdown widget using ipywidgets. It extends the base Dropdown class and provides a concrete implementation of the render method. The component displays a dropdown menu with configurable options and, when an option is selected, dynamically updates a nested content item to show the corresponding detailed view.

This class serves as a UI abstraction for creating interactive dropdown menus in Jupyter notebooks or other ipywidgets-compatible environments. It's particularly useful for organizing hierarchical content where selecting an option reveals related information.

## State:
- content: dict containing configuration data with keys:
  - "items": list of options for the dropdown
  - "name": string label for the dropdown
  - "item": Container object representing the nested content to display
- The content dictionary is inherited from the parent Dropdown class
- dropdown: widgets.Dropdown instance created during rendering
- item: rendered nested content widget
- titles: list of names extracted from the nested item's content

## Lifecycle:
- Creation: Instantiated with standard Dropdown constructor parameters
- Usage: Call render() method to create a vertical widget layout containing a dropdown menu and an associated content item that updates based on the dropdown selection
- Destruction: Managed by ipywidgets lifecycle; no explicit cleanup required

## Method Map:
```mermaid
graph TD
    A[WidgetDropdown.render()] --> B[widgets.Dropdown]
    A --> C[Extract titles from nested item]
    A --> D[nested_item.render()]
    A --> E[change_view callback]
    E --> F[Update nested item selection]
    B --> G[observe value changes]
    G --> E
```

## Raises:
- NotImplementedError: Inherited from parent class (though this is overridden)
- AttributeError: If content structure doesn't match expected format (e.g., missing "items", "name", or "item" keys)
- TypeError: If content["items"] is not iterable or content["item"] is not properly structured

## Example:
```python
# Create a dropdown with options and nested content
dropdown = Dropdown(
    name="Select Category",
    items=["Option 1", "Option 2", "Option 3"],
    item=nested_container
)

# Render as widget
widget_dropdown = WidgetDropdown(dropdown)
output_widget = widget_dropdown.render()
```

### `src.ydata_profiling.report.presentation.flavours.widget.dropdown.WidgetDropdown.render` · *method*

## Summary:
Creates and returns a vertical widget layout containing a dropdown menu and an associated content item that updates based on the dropdown selection.

## Description:
This method constructs a dropdown widget using ipywidgets and establishes an event handler that synchronizes the selected value with an associated content item. When a user selects an option from the dropdown, the associated item's selected index is updated accordingly. The method returns a VBox container that holds both the dropdown and the content item (if present).

The dropdown displays options from self.content["items"] with the description set to self.content["name"]. When an item is selected, the change_view callback function updates the associated content item's selected_index property to match the selected option.

## Args:
    None

## Returns:
    widgets.VBox: A vertical container widget containing the dropdown and optionally the associated content item. The container will have either one child (dropdown only) or two children (dropdown + content item) depending on whether self.content["item"] is None.

## Raises:
    None explicitly raised

## State Changes:
    Attributes READ: self.content["items"], self.content["name"], self.content["item"]
    Attributes WRITTEN: item.selected_index (during event handling, not directly in this method)

## Constraints:
    Preconditions:
    - self.content must contain keys "items", "name", and "item"
    - self.content["items"] must be iterable and suitable for ipywidgets.Dropdown options
    - self.content["item"] must be a valid Renderable object if not None
    - self.content["item"].content["items"] must be iterable with items having a "name" attribute
    
    Postconditions:
    - Returns a properly initialized widgets.VBox instance
    - The dropdown widget is properly configured with options and description
    - The event observer is attached to handle value changes
    - The associated content item's selected_index property can be modified during interaction

## Side Effects:
    - Creates ipywidgets.Dropdown and widgets.VBox instances
    - Attaches an event observer to the dropdown widget that modifies the associated content item's selected_index property during user interaction

