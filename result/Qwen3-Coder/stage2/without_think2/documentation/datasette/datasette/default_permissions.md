# `default_permissions.py`

## `datasette.default_permissions.permission_allowed` · *function*

## Summary:
Determines whether a given actor has permission to perform a specific action on a resource within the Datasette application.

## Description:
This function serves as the central authorization mechanism for Datasette's permission system. It evaluates permissions based on action type, actor identity, and resource context by consulting metadata configurations and applying appropriate matching logic. The function returns an async inner function that performs the actual permission checking when awaited.

## Args:
    datasette (Datasette): The Datasette instance containing metadata and configuration settings
    actor (dict, optional): Dictionary representing the authenticated user/actor with properties like 'id' and other attributes
    action (str): The action being requested (e.g., "view-instance", "view-database", "execute-sql")
    resource (object): The resource being accessed, whose type depends on the action (e.g., database name, (database, table) tuple, etc.)

## Returns:
    callable: An async function that when called, returns either:
        - True: Permission granted
        - False: Permission denied
        - None: No explicit permission rule found, default behavior applies

## Raises:
    AssertionError: When attempting to view a query that doesn't exist (in view-query action)

## Constraints:
    Preconditions:
        - datasette must be a valid Datasette instance
        - actor must be a dictionary or None
        - action must be a recognized permission action string
        - resource must be appropriately formatted for the given action

    Postconditions:
        - The returned async function will always return one of {True, False, None}
        - No side effects occur during permission evaluation

## Side Effects:
    - May perform async database queries when accessing canned queries (view-query action)
    - No direct I/O operations or state mutations

## Control Flow:
```mermaid
flowchart TD
    A[permission_allowed] --> B{action in ("permissions-debug","debug-menu")}
    B -- Yes --> C{actor and actor.get("id") == "root"}
    C -- Yes --> D[return True]
    C -- No --> E[return None]
    B -- No --> F{action == "view-instance"}
    F -- Yes --> G{datasette.metadata("allow") is not None}
    G -- Yes --> H[return actor_matches_allow(actor, allow)]
    G -- No --> I[return None]
    F -- No --> J{action == "view-database"}
    J -- Yes --> K{resource == "_internal" and (actor is None or actor.get("id") != "root")}
    K -- Yes --> L[return False]
    K -- No --> M{datasette.metadata("allow", database=resource) is None}
    M -- Yes --> N[return None]
    M -- No --> O[return actor_matches_allow(actor, database_allow)]
    J -- No --> P{action == "view-table"}
    P -- Yes --> Q{tables.get(table) or {}}.get("allow") is None
    Q -- Yes --> R[return None]
    Q -- No --> S[return actor_matches_allow(actor, table_allow)]
    P -- No --> T{action == "view-query"}
    T -- Yes --> U[await datasette.get_canned_query(database, query_name, actor)]
    U --> V{assert query is not None}
    V --> W{query.get("allow") is None}
    W -- Yes --> X[return None]
    W -- No --> Y[return actor_matches_allow(actor, allow)]
    T -- No --> Z{action == "execute-sql"}
    Z -- Yes --> AA{datasette.setting("default_allow_sql") is True}
    AA -- Yes --> AB[return None]
    AA -- No --> AC[return False]
    Z -- No --> AD[return None]
```

## Examples:
```python
# Check if root actor can access debug menu
async def check_debug_access():
    permission_checker = permission_allowed(datasette, {"id": "root"}, "debug-menu", None)
    result = await permission_checker()
    # result = True

# Check if anonymous user can view instance
async def check_instance_view():
    permission_checker = permission_allowed(datasette, None, "view-instance", None)
    result = await permission_checker()
    # result = True if metadata allows unauthenticated access, else None or False
```

