# `default_permissions.py`

## `datasette.default_permissions.permission_allowed` · *function*

## Summary
Factory function that creates an asynchronous permission checker for evaluating whether a given actor has permission to perform a specific action on a resource within the Datasette application.

## Description
This function serves as a centralized permission control mechanism that determines access rights based on action type, resource context, and actor credentials. It is designed to be used as part of Datasette's security framework to enforce access controls across different operations like viewing databases, tables, queries, or executing SQL.

The function returns an async inner function that performs the actual permission checking when awaited. This design allows for lazy evaluation of permissions while maintaining clean separation between permission configuration and enforcement logic.

Known callers within the codebase would include various Datasette route handlers and middleware components that need to validate user permissions before allowing access to resources. The function is typically invoked during request processing when access control decisions need to be made.

This logic is extracted into its own function rather than being inlined because it encapsulates complex permission business logic that could vary significantly based on action type and resource context, making it reusable and testable.

## Args
*   datasette (object): Datasette application instance containing metadata and configuration
*   actor (dict or None): Actor information representing the user or client attempting the action, typically containing authentication details
*   action (str): The type of action being requested (e.g., "view-database", "execute-sql")
*   resource (tuple or str): Resource identifier specific to the action type (e.g., database name, (database, table) tuple)

## Returns
*   async function: An async function that when awaited returns:
    *   True if actor is permitted
    *   False if access is denied  
    *   None if no explicit permission rule applies and default behavior should be used

## Raises
*   AssertionError: When a view-query action is attempted but the canned query cannot be retrieved (query is None)

## Constraints
*   Preconditions: 
    *   The datasette object must have metadata and setting methods available
    *   The actor parameter should be a dictionary or None
    *   The resource parameter must match the expected format for the specific action type
*   Postconditions:
    *   The returned async function, when awaited, will return either True, False, or None

## Side Effects
*   None directly observable side effects, though the function may trigger asynchronous operations when retrieving canned queries

## Control Flow
```mermaid
flowchart TD
    A[permission_allowed called] --> B{Action type}
    B -->|permissions-debug or debug-menu| C{Actor ID == "root"}
    C -->|Yes| D[Return True]
    C -->|No| E[Continue]
    B -->|view-instance| F[Get datasette metadata "allow"]
    F -->|Not None| G[Check actor_matches_allow]
    F -->|None| H[Return None]
    B -->|view-database| I{Resource == "_internal"} 
    I -->|Yes| J{Actor is None or ID != "root"}
    J -->|Yes| K[Return False]
    J -->|No| L[Get database metadata "allow"]
    L -->|Not None| M[Check actor_matches_allow]
    L -->|None| N[Return None]
    B -->|view-table| O[Extract database, table from resource]
    O --> P[Get tables metadata for database]
    P --> Q[Get table allow setting]
    Q -->|Not None| R[Check actor_matches_allow]
    Q -->|None| S[Return None]
    B -->|view-query| T[Extract database, query_name from resource]
    T --> U[Get canned query async]
    U --> V{Query is None}
    V -->|Yes| W[Assertion Error]
    V -->|No| X[Get query allow setting]
    X -->|Not None| Y[Check actor_matches_allow]
    X -->|None| Z[Return None]
    B -->|execute-sql| AA[Get default_allow_sql setting]
    AA --> AB[Get database metadata "allow_sql"]
    AB -->|Not None| AC[Check actor_matches_allow]
    AB -->|None| AD[Get global metadata "allow_sql"]
    AD -->|Not None| AE[Check actor_matches_allow]
    AD -->|None| AF[Return default_allow_sql]
```

## Examples
```python
# Basic usage pattern
async def check_permission(datasette, actor, action, resource):
    permission_checker = permission_allowed(datasette, actor, action, resource)
    result = await permission_checker()
    if result is True:
        # Allow access
        pass
    elif result is False:
        # Deny access
        raise PermissionError("Access denied")
    else:
        # Use default behavior (likely deny)
        pass

# Example for view-database permission
checker = permission_allowed(datasette, {"id": "user123"}, "view-database", "my_database")
can_access = await checker()  # Returns True/False/None based on permissions
```

