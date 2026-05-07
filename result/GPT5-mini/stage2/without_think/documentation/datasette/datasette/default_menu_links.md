# `default_menu_links.py`

## `datasette.default_menu_links.menu_links` · *function*

## Summary:
Returns an async provider function that, when awaited, yields a list of debug/admin menu link dictionaries if the given actor is allowed to see the debug menu; otherwise yields an empty list.

## Description:
This factory function constructs and returns an async callable (inner) that the caller should await to obtain the menu links for the current actor. The returned callable performs a permission check via datasette.permission_allowed(actor, "debug-menu"); if that check fails it immediately returns an empty list, otherwise it returns a statically-defined list of link dictionaries whose href values are produced by calling datasette.urls.path(...).

Known callers within the codebase:
- No direct internal direct-call sites were found in the provided code snapshot. This function is intended to be used where the Datasette application or plugin system collects menu-link providers (i.e., the framework will call this factory to obtain a provider and then await it when rendering menus).

Why this logic is extracted:
- Separating the factory (menu_links) from the runtime provider (the returned async inner) isolates permission-check and link-generation behavior into a single reusable provider object. The framework can register or call the factory to obtain a per-request callable without inlining permission logic wherever menus are assembled.

## Args:
    datasette (object): A Datasette-like application instance. Required to implement:
        - permission_allowed(actor, permission_name): an awaitable that returns a truthy value if the actor has the named permission.
        - urls.path(path_str) -> str: used to produce href strings for each link.
        No specific concrete type is enforced in-code; callers must supply an object with the described methods.
    actor (any): The actor (current user/session) object passed through to permission_allowed. Can be None if that is accepted by the datasette.permission_allowed implementation.

Interdependencies:
    - The function assumes datasette.permission_allowed and datasette.urls.path exist and behave as described. If either is missing or raises, this function propagates those errors.

## Returns:
    callable: An async function inner() that when awaited returns list[dict].
    The awaited result is either:
      - [] (an empty list) when datasette.permission_allowed(actor, "debug-menu") resolves to a falsy value; or
      - A list of dictionaries describing menu links. Each dictionary has keys:
          - "href" (str): URL string returned by datasette.urls.path(...) for that route.
          - "label" (str): Human-readable label for the link shown in menus.
    The returned list is static and contains the following link targets (hrefs are produced via datasette.urls.path):
      - "/-/databases" -> "Databases"
      - "/-/plugins" -> "Installed plugins"
      - "/-/versions" -> "Version info"
      - "/-/metadata" -> "Metadata"
      - "/-/settings" -> "Settings"
      - "/-/permissions" -> "Debug permissions"
      - "/-/messages" -> "Debug messages"
      - "/-/allow-debug" -> "Debug allow rules"
      - "/-/threads" -> "Debug threads"
      - "/-/actor" -> "Debug actor"
      - "/-/patterns" -> "Pattern portfolio"

## Raises:
    Propagates exceptions raised by:
      - datasette.permission_allowed(actor, "debug-menu") (any exception this awaitable raises will bubble up)
      - datasette.urls.path(path_str) calls (any exceptions raised while constructing href values will bubble up)
    The function itself does not raise new exception types nor performs explicit validation that would raise ValueError/TypeError; failures come from dependencies.

## Constraints:
Preconditions:
    - The caller must provide a datasette object that implements:
        * an awaitable permission_allowed(actor, permission_name) method; and
        * a urls.path(path_str) method returning a string.
    - actor must be acceptable to datasette.permission_allowed (the function does not validate actor itself).

Postconditions:
    - The factory returns an async callable. After awaiting that callable:
        * If permission_allowed returned falsy -> the result is an empty list.
        * If permission_allowed returned truthy -> the result is a list of dicts as described above.
    - No mutations are performed on the datasette instance by this function itself.

## Side Effects:
    - No direct I/O, network, file, or stdout activity performed by this function.
    - Calls into the provided datasette object:
        * Invokes the awaitable permission_allowed(actor, "debug-menu") which may have side effects depending on that implementation.
        * Calls datasette.urls.path(...) multiple times to build href strings; these are expected to be pure mapping calls but may have side effects if the implementation does.
    - No global state, databases, caches, or external services are modified by this code directly.

## Control Flow:
flowchart TD
    Start([Start]) --> CallPermission[/"await datasette.permission_allowed(actor, 'debug-menu')"/]
    CallPermission -->|Falsy| ReturnEmpty[/"Return []"/]
    CallPermission -->|Truthy| BuildList[/"Construct static list of link dicts via datasette.urls.path(...)"/]
    BuildList --> ReturnList[/"Return list of link dicts"/]
    ReturnEmpty --> End([End])
    ReturnList --> End

## Examples:
Example — normal (permission granted):
    provider = menu_links(datasette, actor)
    # 'provider' is an async callable; await it to get the links list:
    links = await provider()
    # links will be a list of dicts with "href" and "label" keys (see Returns section).

Example — permission denied:
    provider = menu_links(datasette, actor)
    links = await provider()  # if permission_allowed returns falsy -> links == []

Example — error propagation (missing methods or failing permission check):
    # If datasette lacks permission_allowed or urls.path, awaiting provider() will raise the underlying AttributeError or any exception raised by those calls.
    provider = menu_links(broken_datasette, actor)
    try:
        links = await provider()
    except Exception as e:
        # Handle or log the propagated exception from datasette APIs
        handle(e)

