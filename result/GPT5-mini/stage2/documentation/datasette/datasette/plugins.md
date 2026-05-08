# `plugins.py`

## `datasette.plugins.get_plugins` · *function*

## Summary:
Returns a list of metadata dictionaries describing every plugin discovered by the global plugin manager, including each plugin's name, optional file-system paths for bundled static assets and templates, exposed hook names, and optional distribution metadata (version and project name).

## Description:
Scans the global plugin manager (pm) for registered plugin objects, queries optional package resources for each non-default plugin to discover bundled "static" and "templates" directories, gathers hook names exposed by each plugin, and augments the result with distribution metadata when available.

Known callers within this repository:
- No direct internal callers were discovered in the scanned codebase. (If code that uses this function exists elsewhere, it is not present in the available source snapshot.)
Typical usage context:
- Called when the application needs to enumerate installed/loaded plugins for an admin UI, diagnostic output, or CLI command that lists plugins.

Why this is a separate function:
- Centralizes the logic for transforming plugin manager state into a stable list-of-dicts representation suitable for consumption by UI or API layers.
- Keeps resource-inspection and mapping of distribution metadata separate from presentation code, making it reusable and testable.

## Args:
This function takes no arguments.

## Returns:
list[dict]:
    A list where each element corresponds to one plugin. Each plugin dictionary contains the following keys:
    - name (str): Primary textual name for the plugin. Default is plugin.__name__; if distribution metadata is available for that plugin, the name is overwritten with distinfo.project_name (str).
    - static_path (str | None): Absolute filesystem path to the plugin's bundled "static" directory when present and discoverable via pkg_resources.resource_isdir/resource_filename; otherwise None.
    - templates_path (str | None): Absolute filesystem path to the plugin's bundled "templates" directory when present; otherwise None.
    - hooks (list[str]): List of hook caller names returned by pm.get_hookcallers(plugin). Each entry is the .name attribute of a hookcaller object.
    - version (str) — optional: Present only when distribution metadata exists for the plugin (distinfo.version).

Edge-case return values:
- If no plugins are registered, returns an empty list [].
- static_path and templates_path are explicitly None if not found, rather than omitted.

## Raises:
- NameError or AttributeError: If required globals (pm, DEFAULT_PLUGINS) are not defined or do not expose the expected methods/attributes, those errors can propagate.
- Any exception raised by pm.get_plugins(), pm.get_hookcallers(plugin), or by pkg_resources functions that are not caught in the function may propagate; however, pkg_resources.resource_isdir and pkg_resources.resource_filename calls are guarded by a try/except that silences KeyError and ImportError raised during resource discovery for non-default plugins.

Note: The function itself catches KeyError and ImportError raised during package-resource discovery and suppresses them (treats as "no static/templates"). Other exceptions from the plugin manager are not explicitly caught.

## Constraints:
Preconditions:
- A global plugin manager object named pm must exist and implement at least:
    - list_plugin_distinfo(): iterable of (plugin_obj, distinfo) pairs (mapping conversion assumes plugin_obj is hashable/usable as a dict key)
    - get_plugins(): iterable of plugin objects; each plugin object must have a __name__ attribute (string)
    - get_hookcallers(plugin): iterable of hookcaller objects exposing a .name attribute (string)
- A global DEFAULT_PLUGINS iterable of plugin module-name strings must exist (used to skip resource discovery for built-in/default plugins).
- pkg_resources must be importable.

Postconditions:
- Returns a list where each element is a dict with keys name, static_path, templates_path, hooks, and optionally version.
- No plugin dictionaries will lack the "hooks" key; hooks will be an empty list if the plugin exposes no hookcallers.

## Side Effects:
- Reads package resources via pkg_resources.resource_isdir and pkg_resources.resource_filename for non-default plugins — this may perform file-system I/O to resolve package resource locations.
- Does not modify global state, files, or network resources.
- Calls into the plugin manager (pm) which may itself have side effects; these are not caused by get_plugins directly but by the pm methods invoked.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> BuildMap[plugin_to_distinfo = dict(pm.list_plugin_distinfo())]
    BuildMap --> Loop{for plugin in pm.get_plugins()}
    Loop --> InitVars[static_path=None; templates_path=None]
    InitVars --> IsDefault{plugin.__name__ in DEFAULT_PLUGINS?}
    IsDefault -- Yes --> SkipResourceChecks
    IsDefault -- No --> TryResourceChecks[try: check pkg_resources.resource_isdir for "static" and "templates"]
    TryResourceChecks -->|KeyError/ImportError| SkipResourceChecks
    TryResourceChecks --> ResourcePaths[set static_path/templates_path from resource_filename if present]
    ResourcePaths --> SkipResourceChecks[SkipResourceChecks]
    SkipResourceChecks --> HookNames[hooks = [h.name for h in pm.get_hookcallers(plugin)]]
    HookNames --> BuildDict[plugin_info = {...}]
    BuildDict --> LookupDist{distinfo = plugin_to_distinfo.get(plugin)}
    LookupDist -- None --> Append[plugins.append(plugin_info)]
    LookupDist -- found --> Augment[set plugin_info["version"], plugin_info["name"] = distinfo.project_name]
    Augment --> Append
    Append --> Loop
    Loop --> End([return plugins])

## Examples:
Example: iterate and print basic plugin info
    plugins = get_plugins()
    for p in plugins:
        print("Plugin:", p["name"])
        if p.get("version"):
            print("  version:", p["version"])
        if p["static_path"]:
            print("  static files at:", p["static_path"])
        if p["templates_path"]:
            print("  templates at:", p["templates_path"])
        print("  hooks:", ", ".join(p["hooks"]) or "(none)")

Example: use in an admin endpoint (pseudo-code)
    def plugins_endpoint():
        try:
            enumerated = get_plugins()
        except Exception as e:
            # Defensive: plugin manager may be misconfigured
            log.exception("Failed to enumerate plugins")
            return http_500("Unable to list plugins")
        return json_response({"plugins": enumerated})

