# `default_permissions.py`

## `datasette.default_permissions.permission_allowed` · *function*

## Summary:
Produces an async permission-checker callable that, when awaited, returns True (allowed), False (denied), or None (no decision) for the given actor/action/resource according to Datasette metadata, settings, and canned-query definitions.

## Description:
This function builds and returns an inner asynchronous function (checker) that implements the permission rules encoded in the source. The checker consults:
- datasette.metadata(...) for per-instance, per-database, per-table, and allow_sql configuration,
- datasette.setting("default_allow_sql") to determine the default for SQL execution,
- await datasette.get_canned_query(...) to obtain canned-query definitions when checking "view-query",
- actor_matches_allow(actor, allow) (imported) to evaluate allow-rule dicts.

Note: actor_matches_allow behavior (as implemented in datasette.utils):
- If allow is True -> returns True.
- If allow is False -> returns False.
- If allow is None -> returns True.
- Otherwise, allow is a dict whose keys map to values or lists; actor_matches_allow returns True when any allow rule matches actor attributes, otherwise False.

This function is intentionally a factory that returns an awaitable checker: callers must call permission_allowed(...) to obtain the async checker and then await checker() to get the tri-state result.

## Args:
datasette (object)
    - Datasette application object. Required methods/properties used:
        * metadata(key, database=...) -> value or None
        * setting(name) -> configuration value (truthy/falsey)
        * async get_canned_query(database, name, actor) -> dict or None
    - No specific class type required, but these methods must exist and behave as above.

actor (dict | None)
    - The actor (authenticated identity) or None for anonymous requests.
    - Actor is expected to be a mapping supporting .get(key). Values may be scalars or lists.

action (str)
    - Permission action name. Explicitly handled values:
        * "permissions-debug", "debug-menu"
        * "view-instance"
        * "view-database"
        * "view-table"
        * "view-query"
        * "execute-sql"
    - Other action strings cause the checker to make no decision (return None).

resource (varies)
    - Interpreted according to action:
        * "view-instance": ignored (can be None).
        * "view-database": database name (str).
        * "view-table": tuple (database: str, table: str).
        * "view-query": tuple (database: str, query_name: str).
        * "execute-sql": database name (str).
    - Passing the wrong shape may raise errors or produce incorrect decisions.

## Returns:
async function
    - The returned async checker (call it checker). When awaited, checker() returns one of:
        * True — actor is explicitly allowed.
        * False — actor is explicitly denied.
        * None — this function makes no decision; callers should defer to other checks or defaults.
    - All return behaviors are determined by the specific action branches described below.

Per-action return semantics (directly derived from the code):
- "permissions-debug" / "debug-menu":
    * If actor is not None and actor.get("id") == "root": return True.
    * Otherwise: implicit return None.
- "view-instance":
    * allow = datasette.metadata("allow")
    * If allow is not None: return actor_matches_allow(actor, allow)
    * If allow is None: return None
- "view-database":
    * If resource == "_internal" and (actor is None or actor.get("id") != "root"): return False
    * database_allow = datasette.metadata("allow", database=resource)
        - If database_allow is None: return None
        - Else: return actor_matches_allow(actor, database_allow)
- "view-table":
    * Unpack resource into (database, table)
    * tables = datasette.metadata("tables", database=database) or {}
    * table_allow = (tables.get(table) or {}).get("allow")
        - If table_allow is None: return None
        - Else: return actor_matches_allow(actor, table_allow)
- "view-query":
    * Unpack resource into (database, query_name)
    * query = await datasette.get_canned_query(database, query_name, actor)
    * The code asserts query is not None (see Raises).
    * allow = query.get("allow")
        - If allow is None: return None
        - Else: return actor_matches_allow(actor, allow)
- "execute-sql":
    * default_allow_sql = None if datasette.setting("default_allow_sql") else False
    * database_allow_sql = datasette.metadata("allow_sql", database=resource)
      If database_allow_sql is None:
        database_allow_sql = datasette.metadata("allow_sql")
    * If database_allow_sql is None: return default_allow_sql
    * Else: return actor_matches_allow(actor, database_allow_sql)

## Raises:
AssertionError
    - Trigger: action == "view-query" and await datasette.get_canned_query(...) returns None (the code contains assert query is not None).

Other exceptions
    - Underlying calls (datasette.metadata, datasette.setting, datasette.get_canned_query, or actor_matches_allow) may raise exceptions depending on their implementations; this function does not catch them.

## Constraints:
Preconditions
    - datasette must implement metadata, setting, and async get_canned_query with the semantics used above.
    - The caller must pass resource in the shape expected by the action.
    - actor must be a mapping or None.

Postconditions
    - Awaiting the returned checker will either return True/False/None or raise AssertionError for the missing canned-query case; no mutation of actor or datasette state occurs in this function.

## Side Effects:
- No direct file, network, or stdout I/O performed by this function itself.
- The checker invokes datasette.get_canned_query (async), datasette.metadata, and datasette.setting — these calls may perform I/O or access external state depending on their implementations.
- actor_matches_allow is pure (no side effects).

## Control Flow:
flowchart TD
    Start([start]) --> ActionCheck{action == one of handled actions?}
    ActionCheck --> |permissions-debug or debug-menu| Debug
    ActionCheck --> |view-instance| ViewInstance
    ActionCheck --> |view-database| ViewDatabase
    ActionCheck --> |view-table| ViewTable
    ActionCheck --> |view-query| ViewQuery
    ActionCheck --> |execute-sql| ExecSQL
    ActionCheck --> |other| NoDecision
    Debug --> IsRoot{actor and actor.get("id") == "root"}
    IsRoot --> |yes| ReturnTrue1([return True])
    IsRoot --> |no| ReturnNone1([return None])
    ViewInstance --> GetAllowInstance{allow = metadata("allow")}
    GetAllowInstance --> |not None| ReturnActorMatch1([return actor_matches_allow(actor, allow)])
    GetAllowInstance --> |None| ReturnNone2([return None])
    ViewDatabase --> CheckInternal{resource == "_internal" and (actor is None or actor.get("id") != "root")}
    CheckInternal --> |yes| ReturnFalse1([return False])
    CheckInternal --> |no| GetAllowDatabase{database_allow = metadata("allow", database=resource)}
    GetAllowDatabase --> |None| ReturnNone3([return None])
    GetAllowDatabase --> |not None| ReturnActorMatch2([return actor_matches_allow(actor, database_allow)])
    ViewTable --> Unpack[(database, table)]
    Unpack --> GetTables{tables = metadata("tables", database) or {}}
    GetTables --> GetTableAllow{table_allow = (tables.get(table) or {}).get("allow")}
    GetTableAllow --> |None| ReturnNone4([return None])
    GetTableAllow --> |not None| ReturnActorMatch3([return actor_matches_allow(actor, table_allow)])
    ViewQuery --> UnpackQ[(database, query_name)]
    UnpackQ --> GetQuery[await get_canned_query(database, query_name, actor)]
    GetQuery --> |None| RaiseAssert([AssertionError])
    GetQuery --> |query| GetQueryAllow{allow = query.get("allow")}
    GetQueryAllow --> |None| ReturnNone5([return None])
    GetQueryAllow --> |not None| ReturnActorMatch4([return actor_matches_allow(actor, allow)])
    ExecSQL --> ComputeDefault{default_allow_sql = None if setting("default_allow_sql") else False}
    ExecSQL --> GetDBAllow{database_allow_sql = metadata("allow_sql", database=resource) or metadata("allow_sql")}
    GetDBAllow --> |None| ReturnDefault([return default_allow_sql])
    GetDBAllow --> |not None| ReturnActorMatch5([return actor_matches_allow(actor, database_allow_sql)])
    NoDecision --> ReturnNone6([return None])

## Examples:
1) Obtain and await the checker for viewing a database:
    checker = permission_allowed(datasette, actor, "view-database", "my_db")
    result = await checker()
    # result is True, False, or None

2) Handling missing canned query for "view-query":
    checker = permission_allowed(datasette, actor, "view-query", ("my_db", "missing_query"))
    try:
        result = await checker()
    except AssertionError:
        # datasette.get_canned_query returned None -> code asserts and raises
        handle_missing_query()
    else:
        # result is True, False, or None
        pass

3) Understand execute-sql default behavior:
    # If datasette.setting("default_allow_sql") evaluates to truthy:
    #   default_allow_sql is None -> checker returns None when no allow_sql metadata found.
    # If datasette.setting("default_allow_sql") is falsy:
    #   default_allow_sql is False -> checker returns False when no allow_sql metadata found.

