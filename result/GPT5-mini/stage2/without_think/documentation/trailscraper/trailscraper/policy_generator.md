# `policy_generator.py`

## `trailscraper.policy_generator._combine_statements_by` · *function*

## Summary:
Returns a higher-order function that groups and merges an iterable of Statement objects by a user-provided grouping key, producing a list of merged Statement instances (one per distinct key).

## Description:
This function factory creates and returns a function that accepts a sequence (or any iterable) of Statement instances and performs grouping + reduction using the provided key extractor. For each Statement s, the provided key callable is invoked as key(s); its result is converted to a tuple and used as the grouping key. All Statements that map to the same grouping key are combined using Statement.merge via toolz.reduceby, and the merged Statement values are returned as a list.

Known callers and typical usage:
- De-duplication / normalization steps in policy generation pipelines that need to collapse multiple Statement instances sharing some identifying attributes (for example, the same Effect, same Action set, or same Resource).
- Any higher-level routine that constructs a PolicyDocument and wishes to group/merge statements before producing the final document.
- Typical trigger: invoked when preparing the final Statement list for an output policy or when normalizing/compacting statements after parsing or aggregation.

Why this is extracted:
- Encapsulates a reusable grouping-and-merge pattern so callers can supply different grouping keys (e.g., group by Effect only, by (Effect, Resource), or by a normalized Action signature) without duplicating reduceby/merging logic.
- Keeps policy_generator codebase concise and explicit about the grouping contract (convert key result to tuple, then reduce by Statement.merge).

## Args:
- key (callable(statement: Statement) -> Iterable[hashable]):
    - Description: A callable that receives a Statement and returns an iterable (e.g., list/tuple/generator) of values that together define the group key for that statement.
    - Allowed values: Any callable. Each element produced by the iterable must be hashable (so the tuple(key(statement)) can be used as a dict key).
    - Notes / interdependencies:
        - The returned iterable's items must be stable and deterministic across calls (no side-effectful values).
        - If you intend statements to only be merged when Effects match, the key should include the Effect (or otherwise ensure Statement.merge preconditions hold).

## Returns:
- A callable result(statements: Iterable[Statement]) -> list[Statement]
    - Semantics: When the returned function is called with an iterable of Statement instances:
        - It groups statements by tuple(key(statement)).
        - For each group, it reduces/merges the group's Statement objects using Statement.merge.
        - It returns a list containing the merged Statement for each group.
    - Order of results:
        - The returned list preserves the insertion order of first-seen grouping keys (i.e., the group for the key seen first in the input appears earlier in the returned list). This follows toolz.reduceby/dict insertion order semantics.
    - Edge-case return values:
        - If the input iterable is empty, returns an empty list.
        - If the input contains only a single Statement for a key, that Statement (or a merge result equivalent to it) is returned for that key.

## Raises:
- TypeError:
    - If the provided statements argument to the returned function is not iterable (raised when attempting to iterate).
    - If key(statement) returns a non-iterable object (e.g., None or an integer), converting it with tuple(...) will raise a TypeError.
    - If the elements yielded by key(statement) are unhashable (e.g., lists), attempting to use the tuple as a dict key may raise a TypeError.
- ValueError:
    - May be raised by Statement.merge if two grouped Statement instances violate merge preconditions (for example, differing Effect values). This function does not catch or translate that exception.
- Any exceptions raised by the key callable or by Statement.merge (e.g., from action json_repr misuse, unhashable action elements) will propagate to the caller.

## Constraints:
Preconditions:
- The provided key callable must accept a Statement and return an iterable of hashable elements (or the caller must wrap a scalar into an iterable).
- Input statements must be Statement instances (or at least compatible with Statement.merge behavior and the key callable).
- If Statement.merge requires equal Effect for the two statements it merges (as Statement.merge does), the grouping produced by key must ensure only mergeable statements appear in the same group (for example, include Effect in the key if necessary).

Postconditions:
- For each distinct tuple(key(statement)) observed in the input, there will be exactly one Statement in the returned list representing the merge of all input statements in that group.
- The function does not mutate input Statement objects (Statement.merge returns new Statement objects according to Statement contract); no I/O or global state is modified.

## Side Effects:
- None intrinsic: No file, network, or stdout I/O occurs.
- No global state is modified by this function.
- Any side effects will originate from the key callable or Statement.merge implementation; those side-effects (if present) will propagate.

## Control Flow:
flowchart TD
    A[Call _combine_statements_by(key) -> returns _result] --> B[Call _result(statements)]
    B --> C[Iterate over statements]
    C --> D[For each statement: compute key(statement)]
    D --> E[Convert key result to tuple (group_key)]
    E --> F[toolz.reduceby groups by group_key, reducing with Statement.merge]
    F --> G[After processing all statements, reduceby has mapping group_key -> merged_statement]
    G --> H[Collect mapping values in insertion order]
    H --> I[Return list of merged_statements]

## Examples:
Example 1 — Group by Effect only (safe when you want to merge all statements with the same Effect):
    # Prepare a combiner that groups by effect
    combiner = _combine_statements_by(lambda s: [s.Effect])

    # Use on an iterable of Statement objects
    try:
        merged_statements = combiner(list_of_statements)
    except ValueError as exc:
        # Statement.merge raised ValueError (e.g., if merge preconditions failed)
        handle_merge_error(exc)

Notes:
- If your key returns a scalar (e.g., a single string) be careful: returning a string will be iterated as characters when passed to tuple(...) (e.g., tuple("Allow") -> ('A','l','l','o','w')). To return a single-element grouping key, return a one-item iterable such as [value] or (value,).
- Example of grouping by (Effect, Resource) tuple:
    combiner = _combine_statements_by(lambda s: [s.Effect] + s.Resource[:1])  # group by effect and first resource
    results = combiner(statements_iterable)

Implementation notes for re-creation:
- Implement key_function as: def key_function(statement): return tuple(key(statement))
- Use toolz.reduceby(key_function, Statement.merge, statements) to perform grouping and reduction; return list(mapping.values()).
- Ensure you document and enforce in callers that key must produce hashable elements and must prevent incompatible Statement objects from being grouped together if Statement.merge expects invariants (e.g., same Effect).

## `trailscraper.policy_generator.generate_policy` · *function*

## Summary:
Produce an IAM PolicyDocument (Version "2012-10-17") from an iterable of CloudTrail Record objects by converting each Record to a Statement, filtering out ignored events, merging statements first by Resource then by Action, sorting the final statements, and packaging them into a PolicyDocument.

## Description:
This function implements the final consolidation step in the policy-generation pipeline. It converts each input Record into a trailscraper.iam.Statement (via Record.to_statement()), removes Records that do not map to a Statement (to_statement() -> None), merges/compacts overlapping statements using two successive grouping passes (resource-based then action-based), sorts the resulting Statement list deterministically, and returns a PolicyDocument containing those statements.

Known callers and context:
- Policy-building code that accumulates Record instances parsed from CloudTrail and needs a compact JSON-serializable policy output.
- Typical trigger: after parsing CloudTrail events and converting them into Record objects, call generate_policy(selected_records) to obtain the final PolicyDocument suitable for serialization (PolicyDocument.to_json()) or further output.

Why this is a separate function:
- The procedure implements a multi-step normalization/compaction pipeline (map -> filter -> two-stage grouping -> sort -> wrap) that is conceptually distinct and reused as the canonical "finalize policy" step. Extracting it avoids duplicating grouping and sorting logic at call sites and makes testing the pipeline easier.

## Args:
    selected_records (Iterable[trailscraper.cloudtrail.Record]):
        - An iterable (e.g., list, generator) of Record instances produced from CloudTrail events.
        - Each Record is expected to implement to_statement() which returns either a trailscraper.iam.Statement or None.
        - Preconditions:
            * selected_records must be iterable; attempting to iterate a non-iterable will raise TypeError.
            * Elements must be valid Record instances (or at least support Record.to_statement()).
        - Notes:
            * The function consumes the iterable by iteration; if a generator is passed it will be advanced to exhaustion.

## Returns:
    trailscraper.iam.PolicyDocument
        - A PolicyDocument with:
            * Version set to the literal "2012-10-17".
            * Statement set to the final list of Statement instances produced by the pipeline.
        - The Statement list:
            * Contains only Statement objects (no None entries).
            * Each Statement is the result of merging zero-or-more input Statements (Statement.merge is used by the grouping helper).
            * Ordering is deterministic: the pipeline applies a stable grouping order (first-seen group order preserved when merging) and a final sort step that orders Statement objects using their defined ordering (Statement.__lt__); the final list is the value placed into PolicyDocument.Statement.

## Behavior / Detailed pipeline steps:
1. Map: For each Record in selected_records call Record.to_statement() to obtain either a Statement or None.
2. Filter: Drop any None values returned by to_statement() (these represent events intentionally not mapped to a permission — e.g., sts:GetCallerIdentity).
3. Group & merge 1 (by Resource): Call the _combine_statements_by factory with key = lambda statement: statement.Resource. This groups statements by their Resource values (the key is converted to a tuple internally) and merges each group's Statements using Statement.merge.
4. Group & merge 2 (by Action): Take the list returned by step 3 and call _combine_statements_by with key = lambda statement: statement.Action. This groups/merges by Action (the list of action-like objects is converted to a tuple for the grouping key).
   - Rationale: First merging by Resource compacts statements that target identical resource sets; a subsequent merge by Action further compacts statements that have identical action sets across previously-merged resource groups.
5. Sort: Apply a deterministic sort (sortedz) on the merged statements (sorting uses Statement ordering rules).
6. Wrap: Construct and return PolicyDocument(Version="2012-10-17", Statement=statements).

Assumptions about local helper functions (mapz, filterz, sortedz):
- These helpers are pipeline-compatible variants of the familiar map/filter/sorted operations and behave as follows:
    * mapz(f): applies f to each element of the input iterable (like built-in map), preserving iteration semantics.
    * filterz(pred): retains only items where pred(item) is truthy.
    * sortedz(): performs a deterministic sort on the iterable using Python ordering semantics (here relying on Statement.__lt__).
- If your implementation uses different helper names, replace them with equivalent operations preserving the same semantics and stability.

## Raises:
- TypeError:
    - If selected_records is not iterable (raised on first attempt to iterate).
    - If statement.Resource or statement.Action contain unhashable elements such that _combine_statements_by cannot form tuple(key(statement)) (tuple creation or dict key usage may raise TypeError).
- ValueError:
    - May be raised indirectly by Statement.merge if two grouped statements violate merge preconditions (Statement.merge raises ValueError when Effects differ). In practice Record.to_statement() produces Statements with Effect="Allow", so merges should not fail on Effect mismatch unless custom Statement instances are supplied.
- Any exception thrown by:
    - Record.to_statement() (e.g., upstream helper errors, sorting resource_arns inside to_statement()).
    - _combine_statements_by internals (toolz.reduceby) or Statement.merge (as above).
    - The final sorting operation (if Statement ordering logic raises).
  All such exceptions propagate to the caller; generate_policy does not catch or translate them.

## Constraints:
Preconditions:
- Each element in selected_records must be a Record-like object with a to_statement() method returning either a Statement or None.
- Statement.Action elements must be hashable and provide a deterministic json_repr() (Statement.merge and ordering rely on these properties).
- Statement.Resource elements must be hashable (strings are expected).

Postconditions:
- Returned PolicyDocument.json_repr() is a dict with:
    - 'Version' == "2012-10-17"
    - 'Statement' == the final, sorted list of Statement instances generated by the pipeline.
- Input Record objects are not mutated by generate_policy; only new Statement and PolicyDocument objects are allocated.

## Side Effects:
- None direct: generate_policy performs no file, network, or stdout I/O.
- It constructs new Statement and PolicyDocument objects.
- Any side effects originate from called helpers (Record.to_statement(), _combine_statements_by / Statement.merge) and will propagate if present.

## Control Flow:
flowchart TD
    A[selected_records iterable] --> B[map: Record.to_statement() for each Record]
    B --> C[filter: drop None statements]
    C --> D[_combine_statements_by(lambda s: s.Resource) -> list of merged Statements]
    D --> E[_combine_statements_by(lambda s: s.Action) -> further-merged list]
    E --> F[sortedz() -> sorted list of Statement]
    F --> G[PolicyDocument(Version="2012-10-17", Statement=sorted_statements)]
    G --> H[return PolicyDocument]

## Examples (usage notes, non-executable description):
- Typical happy-path:
    * You have parsed CloudTrail events into a list or generator of Record objects.
    * Call generate_policy(records_iterable).
    * The function returns a PolicyDocument whose Statement field contains merged, deduplicated statements suitable for JSON serialization with PolicyDocument.to_json().

- Error-handling guidance:
    * If a Record has malformed resource_arns (elements not mutually comparable) its to_statement() may raise TypeError during sorting — catch exceptions around the record-building stage or validate resource_arns before creating Records.
    * If you accept non-Record objects in selected_records, ensure they implement to_statement() that returns Statement or None and that any returned Statement meets the hashability and json_repr() expectations of Statement.merge; otherwise Statement.merge or grouping may raise TypeError or ValueError.

Notes and implementation hints for re-creation:
- Implement the mapping + filtering with any pipeline you prefer; the important semantics to preserve are:
    1. Remove None statements returned by Record.to_statement().
    2. Group/merge statements first by Resource (tuple(statement.Resource)), then by Action (tuple(statement.Action)). Use Statement.merge to combine grouped statements.
    3. Sort the final Statement list using Statement ordering (i.e., rely on Statement.__lt__).
    4. Place the sorted list into PolicyDocument.Statement and set Version to "2012-10-17".
- Because _combine_statements_by and Statement.merge preserve deterministic ordering of keys and produce deduplicated lists, the final policy will be compact and stable across runs for the same input ordering.

