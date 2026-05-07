# `plugins.py`

## `datasette.plugins.get_plugins` · *function*

## Summary
Collects and returns metadata about installed Datasette plugins, including their static and template directories, available hooks, and version information.

## Description
This function serves as the central registry for Datasette plugin information, aggregating metadata from the pluggy plugin manager to provide a unified view of all installed plugins. It enables Datasette's plugin system to discover and utilize plugin assets (static files, templates), understand available hook points, and manage plugin versions.

The function is extracted into its own component to encapsulate the complex logic of plugin metadata collection, resource discovery, and version resolution. This separation allows other parts of Datasette to reliably query plugin information without duplicating the resource-checking and metadata assembly logic.

## Args
None

## Returns
A list of dictionaries, where each dictionary contains metadata about a single plugin:
- "name" (str): The plugin's name
- "static_path" (str or None): Path to the plugin's static directory, or None if not found
- "templates_path" (str or None): Path to the plugin's templates directory, or None if not found
- "hooks" (list[str]): List of hook names this plugin implements
- "version" (str or None): Plugin version if available, or None
- "name" (str): Updated to project name if available from distribution info

## Raises
- KeyError: When accessing resources that don't exist in a plugin package
- ImportError: When importing plugin modules fails

## Constraints
Preconditions:
- The pluggy PluginManager instance `pm` must be initialized and available in scope
- The `DEFAULT_PLUGINS` constant must be defined and contain plugin names to exclude
- Plugin packages must be properly installed and accessible via pkg_resources
- The function must be called within a module context where `pm` and `DEFAULT_PLUGINS` are defined

Postconditions:
- Returns a list of plugin metadata dictionaries
- Each plugin dictionary contains at least "name", "static_path", "templates_path", and "hooks" keys
- Version information is only included when available from distribution metadata

## Side Effects
- File system I/O operations to check for static and template directories
- Resource access via pkg_resources to locate plugin assets
- Potential ImportError or KeyError exceptions when accessing plugin resources

## Control Flow
```mermaid
flowchart TD
    A[Start get_plugins()] --> B[Initialize plugins list]
    B --> C[Get plugin-to-distinfo mapping from pm]
    C --> D[Iterate through plugins from pm]
    D --> E{Plugin in DEFAULT_PLUGINS?}
    E -->|Yes| F[Skip resource checks]
    E -->|No| G[Check static directory]
    G --> H{static dir exists?}
    H -->|Yes| I[Set static_path]
    H -->|No| J[Keep static_path=None]
    J --> K[Check templates directory]
    K --> L{templates dir exists?}
    L -->|Yes| M[Set templates_path]
    L -->|No| N[Keep templates_path=None]
    N --> O[Build plugin_info dict]
    O --> P[Get distribution info from plugin_to_distinfo]
    P --> Q{Distribution info exists?}
    Q -->|Yes| R[Update name and version from distinfo]
    Q -->|No| S[Keep original name]
    S --> T[Add plugin_info to plugins list]
    T --> U[Return plugins list]
```

## Examples
```python
# Basic usage
plugins = get_plugins()
for plugin in plugins:
    print(f"Plugin: {plugin['name']}")
    print(f"Static path: {plugin['static_path']}")
    print(f"Templates path: {plugin['templates_path']}")
    print(f"Available hooks: {plugin['hooks']}")
    if 'version' in plugin:
        print(f"Version: {plugin['version']}")
```

