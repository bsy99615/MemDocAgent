# `default_menu_links.py`

## `datasette.default_menu_links.menu_links` · *function*

## Summary:
Returns an async function that generates debug menu links for Datasette when the actor has appropriate permissions.

## Description:
This function implements a Datasette hook that provides navigation links for debugging features in the admin interface. It returns an async inner function that checks if the actor has the "debug-menu" permission before returning a list of debug-related menu items. The menu items include links to databases, plugins, versions, metadata, settings, and various debug tools. This hook is typically used by Datasette's admin interface to display debug options.

## Args:
    datasette (Datasette): The Datasette instance providing URL generation and permission checking capabilities.
    actor (dict): The actor object containing identity and permission information for access control.

## Returns:
    callable: An async function that when called returns a list of menu link dictionaries or an empty list if permission is denied.

## Raises:
    None explicitly raised - the function delegates permission checking to datasette.permission_allowed() which may raise exceptions internally.

## Constraints:
    Preconditions:
    - The datasette parameter must be a valid Datasette instance with urls.path() method available
    - The actor parameter must be a valid actor object with appropriate structure for permission checking
    
    Postconditions:
    - If permission is granted, the returned async function will always return a list of menu link dictionaries
    - If permission is denied, the returned async function will return an empty list

## Side Effects:
    None - This function doesn't perform any I/O operations or mutate external state. It only performs permission checks and returns data structures.

## Control Flow:
```mermaid
flowchart TD
    A[menu_links called] --> B{Permission check: datasette.permission_allowed()}
    B -- False --> C[Return empty list]
    B -- True --> D[Return menu links list]
    C --> E[End]
    D --> E
```

## Examples:
```python
# Usage in a Datasette plugin hook implementation
async def get_menu_links(datasette, actor):
    # Get the menu links function
    menu_func = menu_links(datasette, actor)
    # Call it to get the actual menu links
    links = await menu_func()
    return links

# Typical result when permission is granted:
# [
#     {"href": "/-/databases", "label": "Databases"},
#     {"href": "/-/plugins", "label": "Installed plugins"},
#     # ... more links
# ]
```

