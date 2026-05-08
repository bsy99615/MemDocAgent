# `guess.py`

## `trailscraper.guess._guess_actions` · *function*

## Summary:
Return a flattened list of alternative Action objects produced by each input action's matching_actions call, expanded using the provided allowed_prefixes.

## Description:
- Known callers within the repository snapshot:
    - No direct callers were found in the provided repository snapshot.
    - Typical callers / contexts: policy-guessing or normalization pipelines that need to enumerate alternate/canonical IAM Action objects for a set of input actions (for example, a stage that expands actions to alternate allowed-prefix variants before building or validating policy statements).
- Why this logic is extracted:
    - Encapsulates the simple but repeated responsibility of "aggregate all matching/alternative actions for a collection of actions" into a single utility. This keeps callers free of the iteration and flattening logic and centralizes error propagation behavior for easier testing and reasoning.

## Args:
    actions (iterable[object]):
        - Iterable of objects that implement matching_actions(allowed_prefixes) -> list[Action].
        - Typically instances of trailscraper.iam.Action but any object providing the matching_actions method is acceptable.
        - Precondition: the iterable itself must be iterable (else a TypeError will be raised).
    allowed_prefixes (iterable[str] or falsy):
        - Iterable of strings that will be passed through to each action.matching_actions call.
        - If falsy (None, empty list/tuple), the callee (matching_actions) will typically fall back to its own default prefixes.
        - This function does not validate elements of allowed_prefixes; invalid types will raise exceptions inside matching_actions.

## Returns:
    list[Action]:
        - A flattened list containing every element returned by action.matching_actions(allowed_prefixes) for each action in actions.
        - Possible return values:
            * Empty list: when actions is empty or every matching_actions call returns an empty list.
            * Non-empty list: concatenation of the per-action matching lists.
        - Ordering:
            * The overall order is the concatenation of inner lists in the order actions are iterated.
            * The order of elements produced by each action.matching_actions call is implementation-defined (unspecified); callers should not rely on a stable global ordering.
        - Duplicates:
            * Duplicates are preserved as returned by the matching_actions calls; this function does not deduplicate results.

## Raises:
    - TypeError:
        * If actions is not iterable (iteration raises TypeError).
        * If matching_actions internally expects allowed_prefixes to be iterable and it's not (propagated).
        * If elements of allowed_prefixes are not strings and matching_actions performs string concatenation (propagated).
    - AttributeError:
        * If any element in actions has no matching_actions attribute (attempting to call action.matching_actions will raise AttributeError).
        * Or if matching_actions internally accesses expected attributes that are missing (propagated).
    - FileNotFoundError, OSError, UnicodeDecodeError:
        * Propagated from matching_actions if it (or helpers it calls, such as known_iam_actions) performs file I/O that fails.
    - IndexError, ValueError:
        * Any parsing or lookup errors raised inside matching_actions (propagated).
    - Any other exception raised by action.matching_actions will propagate unchanged.

## Constraints:
    - Preconditions:
        * Each item in actions must be an object exposing a callable matching_actions(allowed_prefixes).
        * If allowed_prefixes is provided and truthy, it should be an iterable of strings to avoid TypeError during concatenation inside matching_actions.
    - Postconditions:
        * The function returns a list (possibly empty) and does not mutate the input iterable or the action objects.
        * No guarantees are made about uniqueness or ordering beyond concatenation semantics described above.

## Side Effects:
    - Direct I/O: None performed by this function itself.
    - Indirect side effects:
        * matching_actions may perform read-only file I/O (e.g., reading canonical action lists) and may raise file I/O related exceptions; those effects are side effects visible to callers.
    - No writes to disk, no network calls, and no global state mutation are performed by this function itself.
    - No logging or stdout/stderr output is performed here (but matching_actions may do so indirectly if implemented to do so).

## Control Flow:
flowchart TD
    Start([Start]) --> CheckIterable{Iterate over actions}
    CheckIterable --> |iteration proceeds| ForEachAction[For each action in actions]
    ForEachAction --> CallMatch[Call action.matching_actions(allowed_prefixes)]
    CallMatch --> |returns list| ExtendResult[Append each returned item to results list]
    CallMatch --> |raises exception| Propagate[Propagate exception to caller]
    ExtendResult --> ForEachAction
    ForEachAction --> End([Return concatenated list])

## Examples (usage described in prose):
- Typical successful use:
    1. You have a collection of Action instances (for example, representing operations parsed from a policy).
    2. Call this function with that collection and a set of allowed prefixes (or None to let matching_actions choose defaults).
    3. The result is a flattened list of alternative/canonical Action objects that can be used for further normalization, presentation, or policy generation.

- Error handling example (prose):
    1. Callers that rely on file-based canonical action lists should catch FileNotFoundError / OSError / UnicodeDecodeError around this function call, because matching_actions may read those files internally.
    2. Callers that accept arbitrary inputs should validate that each item in actions exposes matching_actions before calling, or catch AttributeError to handle unexpected item types.

## Implementation guidance (how to reimplement):
- Implement as a simple nested iteration:
    - Initialize an empty list result.
    - For each action in actions:
        * Call matching = action.matching_actions(allowed_prefixes)
        * Extend result with the elements from matching in iteration order.
    - Return result.
- Do not attempt to deduplicate or sort results here — preserve the sequence semantics described above and let higher-level code perform deduplication if desired.
- Ensure exceptions from matching_actions are allowed to bubble up to preserve diagnostic information to callers.

## `trailscraper.guess._extend_statement` · *function*

## Summary:
Return a list containing the original statement and, when possible, an additional statement that re-exposes the same Effect for a set of expanded Action objects against all resources ("*").

## Description:
This helper is used during policy "guessing"/normalization stages to produce a supplemental statement that grants the same Effect over Resource="*" for each alternative/canonical Action derived from the input statement's Action list.

Known callers:
- No direct callers were discovered in the provided repository snapshot.
- Typical callers / contexts: stages of a policy-generation or policy-normalization pipeline that attempt to expand, canonicalize, or enumerate alternative Action variants for an existing Statement (for example, when generating a policy that should include wildcard-resource variants of equivalent actions). Callers will typically call this function for each Statement being examined and then merge or emit the returned statements.

Why this function is factored out:
- Encapsulates the two-step responsibility of (1) asking the action-expansion utility to enumerate alternative Action objects and (2) conditionally producing a new Statement that exposes those alternatives against Resource ["*"]. Extracting this logic keeps callers concise and centralizes the decision: whether to add a wildcard-resource statement based on whether any expanded actions exist.

## Args:
    statement (trailscraper.iam.Statement or object):
        - Expected shape: an object with at least the attributes:
            * Action: iterable of action-like objects (these are the same elements consumed by _guess_actions and ultimately by Statement).
            * Effect: a string describing the statement effect (commonly "Allow" or "Deny").
            * Resource: a list of resource identifier strings (unused by this function except for returning the original statement).
        - Typical concrete type: trailscraper.iam.Statement.
        - Preconditions: statement.Action must be iterable; statement.Effect must be a string (the function will copy it into the constructed Statement).
    allowed_prefixes (iterable[str] or falsy):
        - Pass-through parameter forwarded to _guess_actions; may be None or an iterable of prefix strings.
        - Interdependency: allowed_prefixes is only meaningful to the expansion performed by _guess_actions; this function does not interpret its contents.

## Returns:
    list[trailscraper.iam.Statement]:
        - If _guess_actions(statement.Action, allowed_prefixes) returns an empty list or other falsy value:
            * Returns a single-element list containing the original statement: [statement].
        - If _guess_actions returns a non-empty list of Action objects:
            * Returns a two-element list: [statement, new_statement]
              where new_statement is a Statement constructed with:
                - Action = the list returned by _guess_actions
                - Effect = statement.Effect (copied)
                - Resource = ["*"]
        - Ordering: the original statement is always the first element; the created wildcard-resource statement (if any) is second.
        - The function never returns None.

## Raises:
    - Any exception raised by _guess_actions will propagate unchanged (for example: TypeError, AttributeError, FileNotFoundError, OSError, ValueError).
    - AttributeError may be raised if the provided statement does not expose the required attributes (Action, Effect).
    - Exception may be raised by Statement(...) construction if the provided Action list or Effect violates Statement's expected invariants (propagated as whatever exception Statement.__init__ would raise).
    - This function does not catch or wrap exceptions — callers should handle errors from _guess_actions and Statement construction as appropriate.

## Constraints:
    Preconditions:
        - statement.Action must be an iterable of action-like objects acceptable to _guess_actions.
        - statement.Effect must be present and copyable into a new Statement.
        - allowed_prefixes, when provided, should be an iterable of strings expected by the matching/expansion implementation used by _guess_actions.
    Postconditions:
        - The input statement is not mutated.
        - Returned list length is either 1 or 2.
        - If a second Statement is returned, it will have Resource set to the single-element list ["*"] and Effect equal to the input statement.Effect.

## Side Effects:
    - None performed directly by this function.
    - Indirect side effects may occur because _guess_actions or Statement construction may perform read-only I/O, logging, or other side effects; those effects (and any exceptions they raise) propagate through this function.
    - No network calls, file writes, stdout/stderr writes, or global state mutations are performed by this function itself.

## Control Flow:
flowchart TD
    Start([Start]) --> CallExpand[_guess_actions(statement.Action, allowed_prefixes)]
    CallExpand --> |raises exception| PropagateError[Propagate exception to caller]
    CallExpand --> |returns falsy/empty| ReturnOriginal[Return [statement]]
    CallExpand --> |returns non-empty list| ConstructNew[Construct new Statement(Action=extended_actions, Effect=statement.Effect, Resource=["*"])]
    ConstructNew --> ReturnBoth[Return [statement, new_statement]]
    ReturnOriginal --> End([End])
    ReturnBoth --> End([End])
    PropagateError --> End([End])

## Examples (illustrative, end-to-end usage described in prose):
- Happy-path example:
    1. Suppose you have a Statement whose Action list contains action-like objects representing a set of parsed operations and Effect == "Allow".
    2. Call this helper with that Statement and an allowed_prefixes list.
    3. If the expansion utility (_guess_actions) returns a non-empty list of alternative Action objects (for example, canonical variants or prefix-expanded actions), the function returns:
        - First element: the original Statement (unchanged).
        - Second element: a new Statement that grants the same Effect for the expanded Action list against Resource ["*"].
      This allows a subsequent policy emitter to include both the original, resource-scoped statement and a broader wildcard-resource statement for the expanded actions.
- No-expansion example:
    1. If the action expansion returns an empty list (no alternatives found), the function returns a single-element list containing only the original Statement.
- Error handling guidance:
    - Because exceptions from _guess_actions propagate, callers that rely on file-backed canonical action lists should wrap calls in a try/except that handles FileNotFoundError / OSError if they want to degrade gracefully.
    - Callers that may pass non-Statement objects should validate that the object has the required attributes or be prepared to catch AttributeError.

## `trailscraper.guess.guess_statements` · *function*

## Summary:
Produce a new PolicyDocument by iterating every statement in the input policy, expanding each statement via the action-expansion helper, flattening the results, and returning a PolicyDocument that preserves the original Version and contains the flattened list of extended statements.

## Description:
This function is a small pipeline step used during policy normalization/guessing. It:
- Iterates over each element of policy.Statement (expected to be a sequence of Statement-like objects).
- Calls the helper _extend_statement(statement, allowed_prefixes) for each statement; that helper returns a list containing the original statement and optionally an additional wildcard-resource statement.
- Flattens the list-of-lists result into a single list (extended_statements) and constructs a PolicyDocument with Version copied from policy.Version and Statement set to extended_statements.

Known callers within the codebase:
- No direct callers were discovered in the provided repository snapshot.
- Typical callers / pipeline stage: a policy-building or normalization stage that needs to emit a fully expanded PolicyDocument for further serialization, comparison, or output.

Why this function is extracted:
- Responsibility boundary: centralizes the iteration + flattening pattern and the copy of the Version field into a new PolicyDocument. By factoring this out callers are freed from repeating the comprehension and the construction of PolicyDocument, and callers can treat guess_statements as the single step that produces an expanded PolicyDocument from an input policy object and expansion rules.

## Args:
- policy (object)
    - Type: object with attributes:
        * Statement: iterable[Statement-like]; each item should expose the attributes required by _extend_statement (typically an instance of trailscraper.iam.Statement).
        * Version: str; the policy language version to copy into the returned PolicyDocument.
    - Required: yes.
    - Notes:
        * The function accesses policy.Statement and policy.Version directly; if either attribute is missing an AttributeError will be raised.
        * policy.Statement may be empty; the function will still return a PolicyDocument with an empty Statement list.

- allowed_prefixes (iterable[str] | falsy)
    - Type: iterable of strings (or any falsy value such as None) forwarded to _extend_statement and ultimately to the action-expansion utility (_guess_actions).
    - Required: yes (the function forwards the provided value; callers can pass None if no prefix restriction is desired).
    - Interdependencies:
        * The meaning and validation of allowed_prefixes is defined by _extend_statement/_guess_actions; guess_statements simply forwards the value.

## Returns:
- Type: trailscraper.iam.PolicyDocument
- Semantics:
    * Version: copied verbatim from policy.Version.
    * Statement: a flattened list composed of all items returned by calling _extend_statement on each input statement, preserving the ordering where for each input statement the original statement appears first and any supplemental wildcard-resource statement (returned by _extend_statement) appears second.
- Possible return shapes / edge cases:
    * If policy.Statement is an empty iterable -> PolicyDocument(Version=policy.Version, Statement=[]).
    * If _extend_statement returns only the original statement for every input -> returned Statement list is the same length as input policy.Statement and contains the same statement objects in order (no deduplication).
    * If _extend_statement returns two items for some statements -> returned Statement list grows accordingly; duplicates between different input statements are not deduplicated by guess_statements.
    * The returned PolicyDocument does not perform validation of Statement contents; it relies on PolicyDocument semantics (which also do not validate structure).

## Raises:
- AttributeError
    - Condition: if the provided policy object does not expose .Statement or .Version attributes.
- Any exception raised by _extend_statement (propagated)
    - Examples: FileNotFoundError, OSError, TypeError, ValueError — _extend_statement documents that it forwards exceptions from its internals (such as _guess_actions or Statement construction).
- Any exception raised by PolicyDocument constructor (propagated)
    - In practice PolicyDocument does not raise on construction, but if a customized behavior is introduced in that class, exceptions would propagate.
- Note: guess_statements does not catch or wrap exceptions; callers should handle errors as appropriate.

## Constraints:
- Preconditions:
    * policy.Statement must be an iterable of objects acceptable to _extend_statement (typically trailscraper.iam.Statement instances).
    * policy.Version must be present and representable as a string.
    * Elements returned by _extend_statement must be compatible with PolicyDocument.Statement (i.e., JSON-serializable or objects implementing json_repr for the project's IAMJSONEncoder).
- Postconditions:
    * The input policy object is not mutated.
    * The returned PolicyDocument.Version equals policy.Version (copied verbatim).
    * The returned PolicyDocument.Statement is a list (possibly empty) containing each item yielded by _extend_statement for every input statement, preserving the ordering described above.

## Side Effects:
- Direct side effects: None. guess_statements itself performs no I/O and mutates no global state.
- Indirect side effects: exceptions or side effects raised or performed by _extend_statement and the utilities it uses (for example, _guess_actions may perform read-only file I/O or raise FileNotFoundError); those effects propagate to the caller.
- No network calls, file writes, stdout/stderr writes, or modifications to persistent storage are performed by guess_statements directly.

## Control Flow:
flowchart TD
    Start([Start]) --> GetStatements[Get policy.Statement iterable]
    GetStatements --> ForEach[For each statement in policy.Statement]
    ForEach --> CallExtend[_extend_statement(statement, allowed_prefixes)]
    CallExtend --> |raises exception| PropagateError[Propagate exception to caller]
    CallExtend --> |returns list| Accumulate[Append each returned item to extended_statements]
    Accumulate --> LoopEnd{More statements?}
    LoopEnd --> |yes| ForEach
    LoopEnd --> |no| BuildPD[Construct PolicyDocument(Version=policy.Version, Statement=extended_statements)]
    BuildPD --> ReturnPD[Return PolicyDocument]
    PropagateError --> End([End])

## Examples (usage and error-handling guidance, described in prose):
- Typical successful usage (conceptual):
    1. Provide a policy-like object that has a Version string and a Statement iterable (each element a Statement instance).
    2. Call guess_statements(policy, allowed_prefixes) to obtain a PolicyDocument that contains both the original statements and any supplemental wildcard-resource statements produced by the expansion helper.
    3. Use the returned PolicyDocument.to_json() or json_repr() to serialize or inspect the policy.

- Handling missing attributes:
    * If you cannot guarantee that the policy object has .Statement and .Version, validate or guard before calling:
        - If .Statement is missing, supply an empty list or raise a clear error to the caller.
        - If .Version is missing, set a default Version explicitly on the input policy object.

- Handling expansion-related failures:
    * Because _extend_statement (and the utilities it calls) may read external resources or raise IO-related errors, wrap calls in a try/except where graceful degradation is required. Typical exceptions to handle include FileNotFoundError, OSError, or ValueError propagated from _extend_statement.

- Deduplication / normalization note:
    * guess_statements does not perform deduplication across the flattened statement list. If callers require merged or deduplicated statements, run a normalization/merge pass (for example, using trailscraper.iam.Statement.merge or a custom deduplication step) after receiving the PolicyDocument.

