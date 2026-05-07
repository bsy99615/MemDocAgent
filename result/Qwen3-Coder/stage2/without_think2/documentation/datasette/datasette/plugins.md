# `plugins.py`

## `datasette.plugins.get_plugins` · *function*

## Summary:
Retrieves metadata about installed Datasette plugins including their paths, hooks, and version information.

## Description:
This function enumerates all installed Datasette plugins and collects detailed metadata about each one. It determines whether plugins provide static assets or template directories, lists the hooks they implement, and retrieves version information from distribution metadata. The function is designed to be called during application initialization to build a registry of available plugins.

## Args:
    None

## Returns:
    list[dict]: A list of dictionaries containing plugin metadata with keys:
        - name (str): Plugin name or project name if available
        - static_path (str or None): Path to static directory if it exists
        - templates_path (str or None): Path to templates directory if it exists
        - hooks (list[str]): List of hook names implemented by the plugin
        - version (str or None): Plugin version if available from distribution info

## Raises:
    None explicitly raised, though KeyError and ImportError may occur internally during resource checking

## Constraints:
    Preconditions:
        - The pm variable must be initialized as a pluggy.PluginManager instance
        - DEFAULT_PLUGINS must be defined in the module scope
        - pkg_resources must be available for resource inspection
    
    Postconditions:
        - Returns a list of plugin metadata dictionaries
        - Each dictionary contains at least name, static_path, templates_path, and hooks keys

## Side Effects:
    - Calls pkg_resources.resource_isdir() and pkg_resources.resource_filename() functions
    - May raise KeyError or ImportError during resource inspection (caught and ignored)
    - Reads filesystem to check for static/templates directories

## Control Flow:
```mermaid
flowchart TD
    A[Start get_plugins()] --> B[Initialize plugins list]
    B --> C[Get plugin-to-distinfo mapping]
    C --> D[Iterate through plugins via pm.get_plugins()]
    D --> E{Plugin in DEFAULT_PLUGINS?}
    E -->|Yes| F[Skip resource checks]
    E -->|No| G[Try resource checks]
    G --> H{static dir exists?}
    H -->|Yes| I[Set static_path]
    H -->|No| J[Keep static_path=None]
    J --> K{templates dir exists?}
    K -->|Yes| L[Set templates_path]
    K -->|No| M[Keep templates_path=None]
    M --> N[Build plugin_info dict]
    N --> O[Get distinfo for plugin]
    O --> P{distinfo exists?}
    P -->|Yes| Q[Update name/version from distinfo]
    Q --> R[Append plugin_info to plugins]
    P -->|No| R[Append plugin_info to plugins]
    R --> S[Return plugins list]
```

## Examples:
```python
# Typical usage during application startup
plugins = get_plugins()
for plugin in plugins:
    print(f"Plugin: {plugin['name']}")
    print(f"Hooks: {plugin['hooks']}")
    if plugin['version']:
        print(f"Version: {plugin['version']}")
```

