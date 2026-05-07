# `matching.py`

## `zxcvbn.matching.build_ranked_dict` · *function*

## Summary:
Create a one-based ranking dictionary from an ordered sequence by mapping each item to its 1-based index (position) in the sequence.

## Description:
This utility converts an ordered iterable of items (typically words from a frequency-ordered list) into a dictionary that maps each item to its rank (position), where ranks start at 1 for the first element.

Known callers:
- No specific callers were identified from the provided context. Conceptually, this function is typically used by modules that need an O(1) lookup of an element's rank derived from an ordered frequency list (for example, constructing frequency/ranked dictionaries used in password-strength estimation pipelines).

Why this is extracted into its own function:
- Encapsulates the common transformation "ordered sequence -> rank lookup dictionary" as a single, well-named utility.
- Keeps calling code focused on higher-level logic (scoring/matching) rather than on the mechanics of enumerating and building dictionaries.
- Centralizes behavior for handling duplicates and iterables so callers do not need to reimplement this pattern.

## Args:
    ordered_list (iterable[Hashable]):
        An iterable that yields items which will become dictionary keys.
        - Items must be hashable (so they can be used as keys in the result dictionary).
        - The iterable can be any iterable type (list, tuple, generator, etc.).
        - The order of the iterable defines the ranking: the first yielded item is rank 1, the second is rank 2, and so on.
        - Duplicate items are permitted in the iterable; the final mapping will reflect the rank of the last occurrence of each duplicate (i.e., later occurrences overwrite earlier ones).

## Returns:
    dict[Hashable, int]:
        A dictionary mapping each item from ordered_list to an integer rank >= 1 representing its 1-based position in the input sequence.

        Possible return scenarios:
        - Normal non-empty input: returns a dict whose keys are the unique items from ordered_list and whose values are integers 1..N (where N is the position of the last occurrence for that key).
        - Empty iterable: returns an empty dict.
        - If ordered_list is a generator/iterator, it will be consumed while building the result.

## Raises:
    TypeError:
        - If ordered_list is not iterable (e.g., None), enumerate will raise a TypeError indicating the object is not iterable.
        - If an element of ordered_list is unhashable (for example, a list or dict), attempting to use it as a dictionary key will raise a TypeError (e.g., "unhashable type: 'list'").

## Constraints:
    Preconditions:
        - The caller must provide an iterable object.
        - Elements yielded by the iterable must be hashable if they are intended to be used as keys.

    Postconditions:
        - The returned dictionary contains at most one entry per unique element present in ordered_list.
        - For each key in the returned dictionary, the value equals the 1-based index (position) of that key's last occurrence in the input iterable.

## Side Effects:
    - None. The function performs no I/O, network access, global state mutation, or external service calls.
    - The only observable effect is allocation of the returned dictionary and the consumption of the iterable (if it's a one-time iterator).

## Control Flow:
flowchart TD
    Start --> CheckIterable
    CheckIterable["Attempt to iterate over ordered_list (enumerate)"]
    CheckIterable --> ForEachItem["For each (index, item) from enumerate(ordered_list, 1)"]
    ForEachItem --> Insert["Insert or overwrite mapping: dict[item] = index"]
    Insert --> MoreItems{"More items?"}
    MoreItems -->|Yes| ForEachItem
    MoreItems -->|No| ReturnResult
    ReturnResult --> End

Notes on control flow:
- There are no explicit conditional branches in the code besides the natural loop over the iterable.
- Duplicate items result in repeated inserts; later inserts overwrite earlier ranks.
- Errors (TypeError) occur when ordered_list is not iterable or when an element is unhashable; those exceptions propagate out of this utility.

## Examples:
- Example 1 (basic):
  Input: an ordered list of words ["the", "be", "to", "of"]
  Output: {"the": 1, "be": 2, "to": 3, "of": 4}

- Example 2 (duplicates — last occurrence wins):
  Input: ["a", "b", "a"]
  Output: {"b": 2, "a": 3}
  Explanation: "a" appears twice; the returned rank for "a" is 3 (its last position).

- Example 3 (empty iterable):
  Input: []
  Output: {}

- Example 4 (generator input):
  Input: generator yielding ["x","y","z"]
  Output: {"x":1,"y":2,"z":3}
  Note: the generator is consumed.

- Example 5 (error case — unhashable item):
  Input: ["ok", ["not", "hashable"]]
  Behavior: raises a TypeError when attempting to use the inner list as a dict key (propagates to caller). To handle this, callers should validate or transform elements into hashable types before calling.

Implementation hints for reimplementation:
- Use enumerate(ordered_list, 1) to obtain 1-based indices.
- Use a dict comprehension or an explicit loop assigning dict[item] = idx.
- Ensure no special-case handling for duplicates (letting later entries overwrite earlier ones).

## `zxcvbn.matching.add_frequency_lists` · *function*

## Summary:
Populate the module-level RANKED_DICTIONARIES mapping by converting each provided ordered frequency list into a one-based rank lookup dictionary.

## Description:
- Known callers within the provided snapshot:
    - No direct callers of this function were identified in the provided code context. The function is a utility intended to be invoked by initialization or setup code that needs to register named frequency lists into the module's ranked-dictionary registry.
- Typical invocation context:
    - Called during module initialization or an application setup step to register multiple named frequency lists (for example, common wordlists) so other components can perform O(1) rank lookups.
- Responsibility boundary:
    - This function is responsible only for iterating over a mapping of named ordered lists and storing the result of build_ranked_dict(lst) under each name into the global RANKED_DICTIONARIES mapping. It does not validate the contents of lists beyond relying on build_ranked_dict for conversion semantics or perform any further processing on the ranked dictionaries.
- Why this is a separate function:
    - Centralizes the logic of registering multiple frequency lists at once and keeps callers from duplicating the iteration-and-conversion pattern. It encapsulates the side effect (mutating RANKED_DICTIONARIES) in a single place.

## Args:
    frequency_lists_ (mapping[str, Iterable[Hashable]]):
        A mapping (e.g., dict) from a name (commonly a string) to an ordered iterable of items (words/tokens).
        - The iterable for each name defines the order used to build ranks (first item -> rank 1, etc.).
        - Items in each iterable must be hashable because build_ranked_dict will use them as dictionary keys.
        - Interdependencies:
            * The function expects the top-level object to implement .items(); passing a non-mapping object that lacks items() will raise an AttributeError.
            * Each mapped value is passed directly to build_ranked_dict and therefore must meet that function's preconditions (iterable of hashable items).

## Returns:
    None
    - This function returns nothing (implicitly returns None). Its effect is entirely via side effects on the global RANKED_DICTIONARIES mapping.

## Raises:
    AttributeError:
        - If frequency_lists_ does not provide an .items() method (for example, if None or a plain list is passed), attempting to call frequency_lists_.items() will raise AttributeError.
    TypeError:
        - If one of the value iterables is not actually iterable or contains unhashable items, build_ranked_dict (called for each list) may raise a TypeError which will propagate out of this function.
    NameError:
        - If the global name RANKED_DICTIONARIES or the helper build_ranked_dict is not defined in the module's scope at call time, a NameError will be raised.

## Constraints:
- Preconditions:
    - The caller must provide a mapping-like object with .items() that yields (name, lst) pairs.
    - Each lst must be an iterable of hashable items acceptable to build_ranked_dict.
    - The module-level symbol RANKED_DICTIONARIES must exist and be a mutable mapping (e.g., dict) if the caller expects population to succeed.
- Postconditions:
    - For every (name, lst) pair in frequency_lists_.items(), RANKED_DICTIONARIES[name] will be assigned the dictionary returned by build_ranked_dict(lst).
    - Any existing entry in RANKED_DICTIONARIES with the same name will be overwritten by the new ranked dictionary.
    - No other global state is modified by this function.

## Side Effects:
- Mutates the module-global mapping RANKED_DICTIONARIES by adding or overwriting entries for each provided name.
- Calls the helper build_ranked_dict for every list value; any exceptions or side effects of that helper will propagate.
- Does not perform any I/O, network access, or stdout/stderr writes itself.

## Control Flow:
flowchart TD
    Start --> ValidateInput
    ValidateInput["Call frequency_lists_.items()"]
    ValidateInput --> ForEach["For each (name, lst) in items"]
    ForEach --> BuildRanked["Call build_ranked_dict(lst)"]
    BuildRanked --> Assign["Set RANKED_DICTIONARIES[name] = result"]
    Assign --> More{"More items?"}
    More -->|Yes| ForEach
    More -->|No| End
    End["Return None"]

## Examples:
- Example 1 — basic registration (assumes build_ranked_dict and RANKED_DICTIONARIES behave as expected):
    Initial state:
        RANKED_DICTIONARIES = {}
    Call:
        add_frequency_lists({'common': ['the', 'be', 'to']})
    Resulting effect:
        RANKED_DICTIONARIES == {'common': {'the': 1, 'be': 2, 'to': 3}}

- Example 2 — overwriting an existing entry:
    Initial state:
        RANKED_DICTIONARIES = {'common': {'the': 1}}
    Call:
        add_frequency_lists({'common': ['a', 'b', 'c']})
    Resulting effect:
        RANKED_DICTIONARIES['common'] == {'a':1, 'b':2, 'c':3}
    Note: the prior value is overwritten.

- Example 3 — propagation of conversion errors:
    If one of the provided lists contains an unhashable element (e.g., a list), build_ranked_dict will raise TypeError; this exception propagates and no further registrations after the failing item are performed unless the caller catches and handles the exception.

## `zxcvbn.matching.omnimatch` · *function*

## Summary:
Aggregate all individual matcher results for a password into a single sorted list of match descriptors, by invoking each registered matcher and returning their combined matches ordered by start and end indices.

## Description:
omnimatch is the top-level aggregator for the per-pattern matcher functions in the matching pipeline. For a given password it calls, in this fixed order, the following matcher functions:
- dictionary_match
- reverse_dictionary_match
- l33t_match
- spatial_match
- repeat_match
- sequence_match
- regex_match
- date_match

Each matcher is invoked as matcher(password, _ranked_dictionaries=_ranked_dictionaries), and the lists they return are concatenated into one master list which is then sorted by the tuple (match['i'], match['j']).

Known callers within this codebase:
- repeat_match (as part of base-token analysis, repeat_match calls omnimatch(base_token) when analyzing repeated substrings).
- Other higher-level scoring/sequence-building routines (not listed here) that need a unified list of matches will typically call omnimatch to obtain that list before constructing match sequences or computing guessability.

Why this logic is extracted:
- Responsibility separation: omnimatch centralizes the orchestration of many independent matchers so the individual matcher implementations can focus on discovering their particular pattern types. This keeps the pipeline modular: add/remove matcher implementations without changing aggregation/sorting behavior.
- Deterministic output: omnimatch enforces a consistent ordering of aggregated matches and provides a single point for future instrumentation (e.g., profiling or parallelization) of the matching stage.

## Args:
    password (str):
        - The password to analyze. Must be a string-like value usable by the individual matcher functions (they typically assume str and call string methods or regex operations).
    _ranked_dictionaries (Mapping[str, Mapping[str, int]], optional):
        - Forwarded keyword argument passed unchanged to each matcher.
        - Default: module-level RANKED_DICTIONARIES (a constant expected to be a mapping from dictionary name to a mapping of lowercased words -> rank ints).
        - Note: some matchers ignore this parameter, but it is provided so all matchers share a compatible signature.

Interdependencies / parameter behavior:
- omnimatch simply forwards _ranked_dictionaries to each matcher. Matchers that require ranked dictionaries (e.g., dictionary_match, l33t_match) will use it; others (e.g., sequence_match) will accept it but may not use it.

## Returns:
    list[dict]:
        - A list containing every match descriptor produced by the invoked matchers, sorted ascending by (match['i'], match['j']) where:
            - 'i' (int) is the inclusive start index of the matched token in password.
            - 'j' (int) is the inclusive end index of the matched token in password.
        - Each element is a dictionary formatted by its producing matcher (see per-matcher documentation). Typical keys across matchers include 'pattern', 'token', 'i', 'j' and matcher-specific metadata (for example, 'matched_word' and 'rank' for dictionary matches, 'l33t' and 'sub' for l33t matches, 'graph' for spatial matches, etc.).
        - Edge-case returns:
            - If no matcher finds any matches, an empty list [] is returned.
            - The list may contain overlapping matches, duplicates (same i/j but produced by different matchers or different dictionaries), and exact-equal dictionaries if produced by the underlying matchers.
            - Descriptors are returned exactly as produced (or mutated) by the matchers; omnimatch does not deep-copy or normalize fields beyond concatenation and sorting.

## Raises:
    - omnimatch does not raise new exceptions itself, but it will propagate any exception raised by the invoked matcher functions.
    - Examples of propagated exceptions:
        - TypeError / AttributeError if password is not suitable for a matcher (e.g., not a str when a matcher performs str or regex operations).
        - KeyError or other runtime errors that arise inside a matcher implementation.
        - TypeError if a matcher does not return an iterable of match descriptors (the code calls .extend() on the matcher result).
    - Because exceptions are not caught, callers should wrap omnimatch in try/except if they need to recover from individual-matcher failures.

## Constraints:
Preconditions:
    - password should be a string (or at least satisfy the expectations of all matchers: indexing/slicing, lower(), regex operations).
    - Each matcher referenced must be defined in the module scope and accept the forwarded keyword argument _ranked_dictionaries.
    - Each match descriptor returned by matchers must include integer 'i' and 'j' keys for sorting to work correctly.

Postconditions:
    - The returned list is sorted in ascending order by (match['i'], match['j']).
    - Every item in the returned list is a match descriptor produced by one of the listed matchers.
    - omnimatch will not remove overlaps or deduplicate matches; these responsibilities belong to downstream sequence-building or scoring code.

## Side Effects:
    - omnimatch itself performs no I/O, network operations, or global state mutation.
    - It calls other matcher functions which may perform internal mutations or return descriptors that were mutated in-place (for example, reverse_dictionary_match mutates descriptors returned by dictionary_match). Therefore:
        - The returned descriptors may be references to objects created or mutated by the underlying matchers.
        - Callers that need immutable snapshots should deep-copy the returned list/dictionaries after receiving the result.

## Control Flow:
flowchart TD
    Start --> Init[Initialize matches = []]
    Init --> ForEach[For each matcher in ordered matcher list]
    ForEach --> Call[Call matcher(password, _ranked_dictionaries=_ranked_dictionaries)]
    Call --> Extend[Extend matches with matcher's returned list]
    Extend --> Next{More matchers?}
    Next -- Yes --> ForEach
    Next -- No --> Sort[Sort matches by (x['i'], x['j'])]
    Sort --> Return[Return sorted matches]
    Return --> End

## Examples:
Example 1 — typical pipeline usage (conceptual):
    - Caller intent: gather all pattern matches in a password to then build non-overlapping match sequences and compute guessability.
    - Steps:
        1. Call omnimatch with a password and (optionally) a custom ranked-dictionary mapping.
        2. Receive a list of match descriptor dicts produced by many matchers (dictionary, l33t, spatial, etc.).
        3. Pass that sorted match list into sequence-building and scoring routines which expect descriptors with 'i' and 'j' keys and other matcher-specific metadata.
    - Notes: If you require that descriptors are not mutated later, deep-copy the result immediately because some matchers may have mutated descriptor objects in-place.

Example 2 — using a restricted dictionary set to limit dictionary matches:
    - Caller intent: restrict dictionary-based matches to a small custom dictionary while still collecting other match types.
    - Steps:
        1. Build a small mapping like {'custom': {'admin': 1, 'root': 2}} and pass it as _ranked_dictionaries.
        2. Call omnimatch(password, _ranked_dictionaries=your_mapping).
        3. omnimatch forwards this mapping to dictionary_match and l33t_match; other matchers ignore it.
    - Result: returned list will contain matches from all matchers, but any dictionary-derived entries reflect only the supplied custom mapping.

Example 3 — defensive error handling:
    - If a caller needs to be robust to malformed inputs or a failing matcher, catch exceptions around omnimatch:
        - Wrap the call in try/except, log or handle exceptions coming from underlying matchers, and decide whether to fallback to an empty match list or re-raise.

Notes:
    - The exact contents and fields of match descriptors are defined by each matcher; refer to individual matcher documentation (dictionary_match, reverse_dictionary_match, l33t_match, spatial_match, repeat_match, sequence_match, regex_match, date_match) for the structure of their returned descriptor dicts.
    - Because omnimatch enforces only aggregation and sorting, adding or reordering matchers in the list is the primary way to change the matching pipeline's discovery behavior and relative prioritization of match sources.

## `zxcvbn.matching.dictionary_match` · *function*

## Summary:
Finds all substrings of the given password that exactly match entries in one or more ranked dictionaries and returns a sorted list of match descriptors describing where each dictionary word occurs in the password.

## Description:
This function enumerates every contiguous substring of the input password, compares each substring (case-insensitive) against the provided ranked dictionaries, and collects a match record for every exact dictionary hit. Typical usage is as a low-level matcher in a password-strength pipeline where discovered dictionary substrings are later scored and composed into an overall guessability estimate.

Known callers within the repository:
- This file does not explicitly call or reference callers; the function is intended to be invoked by higher-level password analysis routines (for example, routines that assemble match sequences and compute guessability using match lists).

Why this logic is extracted:
- Responsibility separation: it isolates the purely lexical task of finding exact dictionary substrings from later scoring and sequence-building logic. That keeps substring discovery simple, testable, and reusable by different scoring or composition strategies.

## Args:
    password (str):
        - The password to search for dictionary substrings.
        - Must be a string; the function calls len(password) and password.lower(), so non-string values will raise an exception.
    _ranked_dictionaries (Mapping[str, Mapping[str, int]], optional):
        - Mapping from dictionary name (str) to a ranked dictionary (mapping word -> rank int).
        - Each ranked dictionary maps lowercased words to a positive integer rank (1 is most frequent).
        - Default: RANKED_DICTIONARIES (a module-level constant in the codebase).
        - Interdependencies: the function assumes keys and lookup in each ranked dictionary use lowercased words.

## Returns:
    list[dict]:
        - A list of match descriptor dictionaries, sorted by start index then end index (by the pair (i, j)).
        - Each descriptor has the following keys:
            - 'pattern' (str): always 'dictionary' for these matches.
            - 'i' (int): start index (0-based) of the match in the original password.
            - 'j' (int): end index (0-based, inclusive) of the match in the original password.
            - 'token' (str): the substring of the original password exactly as in the password (preserves original case).
            - 'matched_word' (str): the matched dictionary word in lowercased form (the dictionary-key matched).
            - 'rank' (int): the rank retrieved from the matched ranked dictionary (lower is more common).
            - 'dictionary_name' (str): the key name of the ranked dictionary where the word was found.
            - 'reversed' (bool): always False for this exact-match lookup.
            - 'l33t' (bool): always False for this exact-match lookup.
        - Edge-case return values:
            - If no substrings match any dictionary, the function returns an empty list [].
            - If the same substring is found in multiple ranked dictionaries, there will be one descriptor per dictionary (duplicates across dictionaries are expected).
            - Overlapping matches and multiple occurrences are returned as distinct entries (different i/j pairs).

## Raises:
    - No exceptions are raised explicitly by the function.
    - Implicit exceptions:
        - TypeError: if password is not a type supporting len() and lower() (e.g., None), a TypeError or AttributeError will be raised by those calls.

## Constraints:
    Preconditions:
        - password must be a str (or at least support len() and lower()).
        - _ranked_dictionaries must be a mapping whose values are mappings from lowercased words to integer ranks.
    Postconditions:
        - Returned list is sorted by start index then end index.
        - Every returned descriptor corresponds to password[i:j+1] such that password_lower[i:j+1] is a key in the corresponding ranked dictionary.

## Side Effects:
    - This function performs no I/O, does not mutate global state, and makes no external service calls.
    - It does not modify the input password or the supplied ranked dictionaries.

## Control Flow:
flowchart TD
    Start --> ComputeLength[Compute length = len(password)]
    ComputeLength --> Lowercase[password_lower = password.lower()]
    Lowercase --> ForEachDict{For each dictionary_name, ranked_dict in _ranked_dictionaries}
    ForEachDict --> ForI[For i from 0 to length-1]
    ForI --> ForJ[For j from i to length-1]
    ForJ --> Substr[substr = password_lower[i:j+1]]
    Substr --> InDict{substr in ranked_dict?}
    InDict -- Yes --> BuildDescriptor[Create descriptor with keys pattern,i,j,token,matched_word,rank,dictionary_name,reversed=False,l33t=False]
    BuildDescriptor --> Append[Append descriptor to matches]
    InDict -- No --> Skip
    Append --> ForJ
    Skip --> ForJ
    ForJ --> ForI
    ForI --> ForEachDict
    ForEachDict --> Sort[Sort matches by (i,j)]
    Sort --> ReturnMatches[Return sorted matches]
    ReturnMatches --> End

## Complexity:
    - Time complexity: O(D * N^2) where D is the number of dictionaries and N is len(password) (because every substring is tested against each dictionary).
    - Space complexity: O(M) where M is the number of matches found (plus O(1) temporary variables).

## Examples:
    Example 1 — simple exact match:
        Inputs:
            password = "Password123"
            _ranked_dictionaries = {"english": {"password": 2, "pass": 5}}
        Behavior:
            - The function lowercases the password to "password123".
            - It finds "password" at indices i=0, j=7 and "pass" at i=0, j=3 (if present in the dictionary).
        Result:
            - A list with descriptor(s) for the "password" hit (and for "pass" if present), each including the matched rank and dictionary name.

    Example 2 — duplicates across dictionaries:
        Inputs:
            password = "admin"
            _ranked_dictionaries = {"english": {"admin": 10}, "names": {"admin": 1}}
        Behavior:
            - Both dictionaries contain "admin", so two descriptors will be produced with the same i/j but different dictionary_name and rank.
        Result:
            - Two match descriptors representing the same substring matched in two separate ranked dictionaries.

    Example 3 — no matches:
        Inputs:
            password = "qzxvbn"
            _ranked_dictionaries = {"english": {"password": 1}}
        Result:
            - The function returns an empty list [].

Notes:
    - The function performs exact (non-l33t, non-reversed) matching only. Variant matching (reversed words, l33t substitutions) is handled by other matchers in the complete matching pipeline.
    - To integrate into a scoring pipeline, pass the returned list of descriptors into subsequent scoring/sequence-building components that expect descriptors with the keys documented above.

## `zxcvbn.matching.reverse_dictionary_match` · *function*

## Summary:
Find dictionary words that appear reversed inside the given password, convert those reversed-match descriptors back to refer to the original password (fixing tokens and indices), mark them as reversed, and return the sorted list of resulting descriptors.

## Description:
This wrapper calls the lower-level dictionary_match on the reversed password and then maps each resulting descriptor back into the coordinate system and tokenization of the original password. It is intended as one of several matcher functions in a password-analysis pipeline: callers aggregate matches from many matchers (dictionary, reversed dictionary, l33t, spatial, date, etc.) and then pass the combined matches to scoring/sequence-building code.

Known callers and typical usage:
- There are no direct repository-local callers discovered; it is a low-level matcher meant to be invoked by higher-level analysis routines that collect match lists before scoring. Typical trigger: when a password should be analyzed for dictionary words that appear spelled backwards (a common user pattern).

Why this is a separate function:
- Responsibility separation: dictionary_match performs pure substring-to-dictionary lookups. This function isolates the logic that (1) runs that lookup on the reversed password and (2) transforms the dictionary_match descriptors so they correctly reference the original password. Separating these concerns improves testability and reusability.

## Args:
    password (str):
        - The input password; must be a sequence-like object supporting len() and reversed() (commonly a Python str).
        - The function calls len(password) and reversed(password); passing values lacking these operations will raise exceptions.
    _ranked_dictionaries (mapping[str, mapping[str, int]], optional):
        - Mapping from dictionary name to ranked dictionary (word -> rank int). Default: RANKED_DICTIONARIES.
        - Forwarded unchanged to dictionary_match; must satisfy dictionary_match's expectations (lowercased keys mapping to integer ranks).

## Returns:
    list[dict]:
        - A sorted list (ascending by start index then end index: sorted(matches, key=lambda x: (x['i'], x['j']))) of match descriptor dictionaries. The descriptors are the same dict objects returned by dictionary_match but mutated in-place.
        - Expected keys on each returned descriptor (after transformation):
            - 'pattern' (str): inherited from dictionary_match (typically 'dictionary').
            - 'i' (int): start index in the original password (0-based).
            - 'j' (int): end index in the original password (0-based, inclusive).
            - 'token' (str): substring of the original password corresponding to password[i:j+1] (the token returned by dictionary_match is reversed back to original).
            - 'matched_word' (str): the lowercased dictionary key that matched (inherited from dictionary_match).
            - 'rank' (int): frequency rank from the matched ranked dictionary (inherited).
            - 'dictionary_name' (str): which ranked dictionary matched (inherited).
            - 'reversed' (bool): set to True by this function (overwriting any previous value).
            - 'l33t' (bool): inherited from dictionary_match (typically False for exact dictionary matches).
        - Edge cases:
            - Returns [] when no reversed substrings match any dictionary.
            - If dictionary_match produced multiple descriptors for the same substring (e.g., different dictionaries), multiple transformed descriptors are returned.
            - Overlapping matches are preserved as separate descriptors.
        - Concrete example of a single returned descriptor:
            {
                'pattern': 'dictionary',
                'i': 0,
                'j': 7,
                'token': 'drowssap',
                'matched_word': 'password',
                'rank': 2,
                'dictionary_name': 'english',
                'reversed': True,
                'l33t': False
            }

## Raises:
    - The function does not explicitly raise new exceptions.
    - Implicit exceptions that may propagate:
        - TypeError or AttributeError: if password does not support reversed() or len() (e.g., None).
        - Any exception raised by dictionary_match when called with the supplied _ranked_dictionaries (propagated).
        - KeyError: if dictionary_match returns descriptor dicts missing required keys 'token', 'i', or 'j'. The function accesses and mutates those keys directly and will raise KeyError if they are absent.

## Constraints:
    Preconditions:
        - password supports len() and reversed() (use a string for normal operation).
        - _ranked_dictionaries is compatible with dictionary_match (mapping of lowercased words to ranks).
        - dictionary_match must produce descriptors containing at least 'token', 'i', and 'j' keys.
    Postconditions:
        - Each returned descriptor's 'token' equals the substring password[i:j+1] (original orientation).
        - Each returned descriptor contains 'reversed': True.
        - The returned list is sorted by (i, j) ascending.

## Side Effects:
    - In-place mutation: the function mutates each match descriptor object returned by dictionary_match:
        - It overwrites match['token'] with the reversed token.
        - It sets match['reversed'] = True (overwriting any previous value).
        - It reassigns match['i'] and match['j'] to the translated indices.
      The mutated descriptor objects are returned to the caller (they are not deep-copied).
    - No I/O, network calls, or global-state mutations are performed.

## Control Flow:
flowchart TD
    Start --> ReversePassword[reversed_password = ''.join(reversed(password))]
    ReversePassword --> CallDictionaryMatch[matches = dictionary_match(reversed_password, _ranked_dictionaries)]
    CallDictionaryMatch --> ForEachMatch[for each match in matches]
    ForEachMatch --> ReverseToken[match['token'] = ''.join(reversed(match['token']))]
    ReverseToken --> SetReversed[match['reversed'] = True]
    SetReversed --> AdjustIndices[old_i = match['i']; old_j = match['j']; match['i'] = len(password)-1-old_j; match['j'] = len(password)-1-old_i]
    AdjustIndices --> MoreMatches{more matches?}
    MoreMatches -- Yes --> ForEachMatch
    MoreMatches -- No --> SortMatches[return sorted(matches, key=lambda x: (x['i'], x['j']))]
    SortMatches --> End

## Complexity:
    - Dominant cost is dictionary_match(reversed_password, ...). Overall complexity is O(D * N^2 + M log M) where:
        - N = len(password), D = number of ranked dictionaries (dictionary_match is O(D * N^2)),
        - M = number of matches returned by dictionary_match (sorting cost O(M log M) with the final sort).
    - Space: O(M) for the list of matches (plus descriptors returned by dictionary_match).

## Examples:
    Example 1 — reversed whole-word match:
        Input:
            password = "drowssap"
            _ranked_dictionaries = {"english": {"password": 2}}
        Behavior:
            - reversed_password = "password"
            - dictionary_match finds {'token': 'password', 'i': 0, 'j': 7, 'matched_word': 'password', 'rank': 2, 'dictionary_name': 'english', 'pattern': 'dictionary', 'l33t': False}
            - This function transforms that descriptor to the example returned descriptor shown above, setting 'token' to 'drowssap', 'reversed': True, and mapping indices back to the original password.
        Return:
            - A list containing the transformed descriptor.

    Example 2 — no reversed dictionary hits:
        Input:
            password = ""
            _ranked_dictionaries = RANKED_DICTIONARIES
        Return:
            - []

Notes:
    - The index translation is exact and intentionally inclusive on 'j' (0-based inclusive end index): new_i = len(password) - 1 - old_j; new_j = len(password) - 1 - old_i.
    - Because descriptors are mutated in-place, if callers need to preserve the original descriptors returned by dictionary_match, they must copy them before calling this function.

## `zxcvbn.matching.relevant_l33t_subtable` · *function*

## Summary:
Returns a filtered mapping of canonical letters to only those leetspeak substitution characters from the provided substitution table that actually appear in the given password.

## Description:
This helper isolates, from a full l33t-substitution table, only the substitution characters that are present in the provided password. Typical use is in a l33t (leetspeak) matching stage of a password-matching pipeline: before attempting to enumerate and test substitution combinations, callers call this function to reduce the substitution search space to only substitutions that could apply to the current password.

Why this logic is its own function:
- It encapsulates the responsibility of filtering the l33t table by presence in the password, keeping callers focused on substitution enumeration and match scoring.
- Extracting this step makes intent clear, avoids duplicate code, and improves testability of the filter operation.

Known callers within a typical password-matching pipeline:
- L33t/dictionary-match generation code that needs to know which substitutions are relevant for a specific password prior to enumerating substitution mappings (the function itself does not perform enumeration or scoring).

## Args:
    password (str):
        The password to inspect. Expected to be a sequence of characters (typically a Python str).
        Only character-level presence is considered: each character from the password is recorded and used for membership tests.
    table (dict[str, Iterable[str]]):
        A mapping whose keys are canonical letters (e.g., 'a', 'o') and whose values are iterables (commonly lists) of substitution strings (e.g., ['4', '@']).
        Each substitution is tested for presence in the password by membership against characters collected from `password`.

Interdependencies:
- The function treats membership of substitution entries against individual characters from `password`. Therefore, substitution entries longer than one character will only be considered present if they exactly equal a key in the password-character set (which normally contains single characters). In practice, the table should contain single-character substitution strings for correct behavior.

## Returns:
    dict[str, list[str]]:
        A new dictionary mapping each canonical letter (from the input `table`) to a list of substitution strings that were found to appear in `password`.
        Only letters with at least one matching substitution are included.
        Examples of possible returns:
        - {} if no substitution characters from `table` appear in `password` or if `table` is empty.
        - {'a': ['4','@'], 'o': ['0']} when those substitution characters are present in `password`.

Edge-case return values:
- If `password` is empty or contains none of the substitution characters, an empty dict is returned.
- If `table` is empty, an empty dict is returned.

## Raises:
    This function does not explicitly raise exceptions.
    However, passing non-iterable types for `table` (e.g., None) will raise a TypeError when `.items()` is called by the caller's runtime environment.
    Similarly, if `password` is not iterable, iterating over it will raise a TypeError.

## Constraints:
Preconditions:
- `password` should be an iterable of characters (preferably a str).
- `table` should be a mapping whose values are iterables of substitution strings.

Postconditions:
- The returned dictionary contains only keys present in the input `table`.
- For each returned key, its value is a list containing only those substitutions that were present in `password`.
- No mutation of input arguments occurs.

## Side Effects:
- None. The function performs no I/O and does not mutate global state or the input `table` or `password`. It returns a newly constructed dictionary.

## Control Flow:
flowchart TD
    Start --> BuildPasswordChars
    BuildPasswordChars --> IterateTable
    IterateTable --> ForEachLetter
    ForEachLetter --> FilterSubs
    FilterSubs --> HasRelevantSubs{relevant_subs non-empty?}
    HasRelevantSubs -->|yes| AddToSubtable
    HasRelevantSubs -->|no| Skip
    AddToSubtable --> NextLetter
    Skip --> NextLetter
    NextLetter --> IterateTable
    IterateTable --> End

## Examples:
Example 1 — basic usage:
Given a password and a substitution table where substitutions are single characters:
- password: "p4ssw0rd"
- table: {'a': ['4', '@'], 'o': ['0'], 's': ['$', '5']}

Call returns:
- {'a': ['4'], 'o': ['0'], 's': ['5']}

Example 2 — empty or no matches:
- password: "hello"
- table: {'a': ['4'], 'o': ['0']}

Call returns:
- {'o': ['0']} if '0' exists in "hello" (it does not), otherwise {}. In this example, returns {}.

Notes and recommendations:
- Ensure substitution entries in `table` are single characters for intended behavior. Multi-character substitution strings will not be detected unless they exactly match a single character key from `password`.
- Because the function only records presence, repeated occurrences in `password` do not affect the output beyond indicating presence.

## `zxcvbn.matching.enumerate_l33t_subs` · *function*

## Summary:
Generates every distinct mapping from observed leetspeak characters to their canonical characters given a substitution table, returning a list of possible substitution dictionaries.

## Description:
This function accepts a substitution table (mapping canonical character -> list of leetspeak characters that can represent it) and enumerates all distinct ways those leetspeak characters could map back to canonical characters. It is typically used in password analysis pipelines to test alternate interpretations of leetspeak within candidate passwords so that dictionary-based matchers can find matches after applying plausible substitutions.

Known callers within the codebase:
    - Higher-level matching logic that needs to try candidate substitution mappings before attempting dictionary matches (used in leetspeak-handling stages of the matching pipeline).
    - Called whenever the system identifies that a password contains characters that could be leetspeak variants of dictionary characters; the caller uses the returned list to apply each substitution to the input and re-run match detection.

Why this is extracted to a separate function:
    - The logic enumerates combinatorial alternatives, deduplicates equivalent mappings, and converts combinations into dicts. Extracting it keeps the enumeration and deduplication responsibilities isolated so callers can remain focused on substitution application and match scoring. It enforces a clear responsibility boundary: enumerate and canonicalize substitution possibilities given a canonical->leets list.

## Args:
    table (dict[str, list[str]]):
        Required. A mapping from canonical character (string) to an iterable (list) of leetspeak character strings that can represent that canonical character.
        - Example shape: {'a': ['4','@'], 'o': ['0']}
        - Interdependencies: If the same leetspeak character appears in multiple lists, the function will generate alternatives reflecting the different possible canonical mappings for that single leetspeak character.

## Returns:
    list[dict[str, str]]:
        A list of substitution dictionaries. Each dictionary maps a leetspeak character (key) to the canonical character (value) that it stands for.
        - Each returned dict contains at most one mapping per leetspeak character (unique keys).
        - If the input table is empty, the function returns a single empty dict ([{}]) representing the identity/no-substitution mapping.
        - All returned dicts are distinct with respect to the set of (leets_char -> canonical_char) pairs they contain (the function deduplicates equivalent mappings regardless of pair insertion order).

## Raises:
    - The function does not explicitly raise any exceptions.
    - If the caller passes a malformed argument (for example, a non-mapping or non-iterable values), Python built-in exceptions (TypeError, AttributeError) may be raised during iteration or key access. These are not raised intentionally by the function but can occur for invalid inputs.

## Constraints:
    Preconditions:
        - table must be an object supporting .keys() and indexing (i.e., dictionary-like).
        - Values in table must be iterable sequences of leetspeak character strings.
        - Elements used as leetspeak characters should be hashable (they become dictionary keys in the outputs).

    Postconditions:
        - The return value is a list of one or more dictionaries (at least the empty mapping if table empty).
        - No returned dictionary contains duplicate keys.
        - Equivalent mappings that differ only by ordering are collapsed to a single dictionary in the result.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and does not call external services. It only computes and returns data structures.

## Control Flow:
flowchart TD
    Start --> BuildKeysAndInitSubs
    BuildKeysAndInitSubs --> HelperCall
    HelperCall -->|keys empty?| ReturnSubs
    HelperCall -->|keys non-empty| IterateFirstKey
    IterateFirstKey --> ForEachLeetChar
    ForEachLeetChar --> ForEachExistingSub
    ForEachExistingSub -->|leet not in sub| AppendNewPair
    ForEachExistingSub -->|leet already in sub| CreateTwoAlternatives
    AppendNewPair --> CollectNextSubs
    CreateTwoAlternatives --> CollectNextSubs
    CollectNextSubs --> DeduplicateNextSubs
    DeduplicateNextSubs --> RecurseHelperWithRestKeys
    RecurseHelperWithRestKeys --> HelperCall
    ReturnSubs --> ConvertListsToDicts
    ConvertListsToDicts --> End

    %% Node labels
    BuildKeysAndInitSubs[Build keys list and initialize subs = [[]]]
    HelperCall[helper(keys, subs)]
    ReturnSubs[Return current subs list]
    IterateFirstKey[Take the first canonical key from keys]
    ForEachLeetChar[For each leetspeak char mapped to that canonical key]
    ForEachExistingSub[For each partial sub-association in subs]
    AppendNewPair[Add [leet_char, canonical] to partial sub]
    CreateTwoAlternatives[Keep existing mapping and also create alternative that replaces it]
    CollectNextSubs[Accumulate next_subs]
    DeduplicateNextSubs[Remove label-duplicates based on sorted associations]
    RecurseHelperWithRestKeys[Recurse with remaining keys]
    ConvertListsToDicts[Convert pair-lists into dicts and return]

## Examples:
    Example 1 — simple table:
    Input table: {'a': ['4', '@'], 'o': ['0']}
    Typical return: a list containing dictionaries such as:
    - {'4': 'a', '0': 'o'}
    - {'@': 'a', '0': 'o'}
    Order of dicts in the list is not significant; all distinct mappings are present.
    If a leetspeak character appears for multiple canonical chars (e.g., '1' listed for both 'l' and 'i'), the result will include alternatives reflecting both mappings (and combinations thereof).

    Example 2 — empty table:
    Input table: {}
    Return: [{}]  (single empty mapping — no substitutions)

    Example 3 — malformed input handling:
    If a caller passes a non-mapping (for example, None or a list), Python will raise a built-in exception when the function attempts to call .keys() or index into table; the function itself does not perform explicit argument validation or raise custom errors.

## `zxcvbn.matching.translate` · *function*

## Summary:
Performs a character-by-character substitution on an input string using a provided mapping and returns the transformed string.

## Description:
This utility walks each character of the input and, when the mapping reports a truthy value for that character via chr_map.get(char, False), replaces the character with chr_map[char]; otherwise it preserves the original character. It is typically used to normalize strings (for example, converting leetspeak or symbol substitutions back to canonical alphabetic characters) before matching or scoring steps in password analysis.

Known callers within the codebase:
- Not explicitly present in the provided snippet. In the zxcvbn project, this function is used by matching/normalization routines that must convert substituted characters to canonical forms prior to dictionary lookups or scoring.

Reason for extraction:
- Encapsulates the character-level translation logic in a single place so callers do not repeat the loop/conditional, ensuring consistent handling of mapping lookup and result concatenation across the codebase.

## Args:
    string (str):
        Input sequence to translate. Expected to be a Python str (text). The function iterates over this value character-by-character; a non-iterable (e.g., None) will raise a TypeError.
    chr_map (mapping-like):
        A mapping-like object that supports .get(key, default). For each character, the function evaluates chr_map.get(char, False):
        - If this returns a truthy value, the function uses chr_map[char] as the replacement and appends it to the output list.
        - If this returns a falsy value (e.g., '', 0, False, None), the function treats the character as unmapped and appends the original character.
        Requirements and recommendations:
        - It must implement .get(key, default). If it lacks .get, an AttributeError will occur.
        - Replacement values should be non-empty strings (truthy str). If replacement values are empty strings or other falsy values they will be ignored by the truthiness check and the original character will be kept.
        - Replacement values must be str (or convertible to str before joining). If they are not str, the final join will raise a TypeError.

Interdependencies:
    - The function uses chr_map.get(char, False) for the presence check but accesses the replacement via chr_map[char]; for standard dicts this is consistent. If a custom mapping's get returns a truthy value for a key but __getitem__ (chr_map[char]) raises an exception, that exception will propagate.

## Returns:
    str:
        A new string made by concatenating replacements or original characters in order.
        - If no character gets a truthy mapping, the returned string equals the input string content-wise (but is a new str object).
        - Replacement values may change the output length: the returned string can be shorter or longer than the input depending on replacement lengths.
        - If mapping values are non-str, a TypeError will be raised at join time.

## Raises:
    TypeError:
        - If `string` is not iterable when the function attempts to iterate over it.
        - If any mapped replacement value is not a str (or otherwise incompatible with ''.join), ''.join(...) will raise a TypeError.
    AttributeError:
        - If `chr_map` does not provide a .get attribute.
    KeyError or other exceptions:
        - If chr_map.get(...) returns a truthy value but chr_map[char] access fails (e.g., custom mapping with inconsistent behavior), that exception will propagate.

## Constraints:
Preconditions:
    - `string` should be a sequence of characters (str is expected).
    - `chr_map` must be mapping-like with .get and should return replacement values that are non-empty strings if they are intended to be applied.

Postconditions:
    - The returned value is a str where each position is either the original character (when the mapping returned falsy) or the mapping's value (when chr_map.get returned a truthy value).
    - The function does not modify the input `string` or mutate `chr_map`.

Important behavior note:
    - The presence test uses truthiness (chr_map.get(char, False)) rather than membership (char in chr_map). Therefore, any mapping value that is falsy (for example, empty string '', 0, False, None) will be treated as "no mapping" and the original character will remain in the output.

## Side Effects:
    - None. Pure in-memory transformation; no I/O, network, or global-state modifications.

## Control Flow:
flowchart TD
    Start --> Iterate[Iterate characters of input string]
    Iterate --> Check{chr_map.get(char, False) is truthy?}
    Check -- Yes --> Access[append chr_map[char] to output list]
    Check -- No --> Keep[append original char to output list]
    Access --> NextChar
    Keep --> NextChar
    NextChar --> Iterate{more characters?}
    Iterate --> Join[after loop: ''.join(output list)]
    Join --> Return[return joined string]
    Return --> End

## Examples:
Example 1 — basic substitution:
    Input: string = "p@ssw0rd", chr_map = {"@": "a", "0": "o"}
    Result: "password"

Example 2 — mapping value is empty string (falsy) and thus ignored:
    Input: string = "a*b", chr_map = {"*": ""}
    Behavior: chr_map.get('*', False) -> '' (falsy) so original '*' is preserved
    Result: "a*b"

Example 3 — mapping value is non-str (will cause join error):
    Input: string = "x@y", chr_map = {"@": 1}
    Behavior: chr_map.get('@', False) -> 1 (truthy), append 1 to output list; ''.join([...]) then raises TypeError
    Recommended fix: ensure replacement values are strings, e.g., {"@": "at"} resulting in "xaty".

Example 4 — missing .get on chr_map:
    If chr_map does not implement .get, calling translate will raise AttributeError immediately; use a dict or mapping-like object with .get.

## `zxcvbn.matching.l33t_match` · *function*

## Summary:
Finds dictionary matches within a password by trying plausible leetspeak (l33t) substitutions, and returns match descriptors for substrings that only match after applying at least one substitution.

## Description:
This function is a l33t-aware wrapper around exact dictionary matching. It:
- Determines which leetspeak substitutions are relevant for the given password.
- Enumerates distinct mappings from observed leet characters back to canonical characters.
- For each mapping, translates the password and runs exact dictionary matching on the translated string.
- From each dictionary match on the translated password, constructs a match descriptor referring to the original (untranslated) token only when the original token is not identical (case-insensitive) to the matched dictionary word — i.e., it reports true l33t matches only.

Known callers (typical usage within the codebase):
- The top-level password-matching pipeline that aggregates matches from multiple matcher functions (dictionary, l33t, reversed, spatial, sequence, etc.) and then passes the combined matches into sequence-building and scoring routines. In that pipeline this function is invoked at the stage where variant/dictionary matches that rely on character substitutions must be discovered before scoring.

Why this is extracted into its own function:
- It encapsulates the control flow that (1) filters relevant leet substitutions for a password, (2) enumerates alternative substitution mappings, and (3) orchestrates translation + dictionary matching + match decoration. This keeps substitution enumeration, translation, and dictionary lookup decoupled and testable as separate units.

## Args:
    password (str):
        The input password to analyze. Expected to be a string (supports len(), iteration and lower()).
    _ranked_dictionaries (mapping[str, mapping[str, int]], optional):
        Mapping of dictionary name -> ranked dictionary (word (lowercased) -> rank int).
        Defaults to the module constant RANKED_DICTIONARIES. Each ranked dictionary is used for exact matching against the translated password.
    _l33t_table (mapping[str, Iterable[str]], optional):
        The global leetspeak table mapping canonical letters to possible leet character representations (e.g., 'a' -> ['4','@']).
        Defaults to the module constant L33T_TABLE.
Notes on interdependencies:
- The function relies on a small set of helper responsibilities. Implementations should follow these roles to ensure consistent behavior:
    - relevant_l33t_subtable(password, _l33t_table): filter the full l33t table to only substitutions whose leet characters appear in `password`.
    - enumerate_l33t_subs(subtable): enumerate all distinct mappings from observed leet characters to canonical characters, deduplicating equivalent mappings (returns at least one mapping — possibly the empty dict).
    - translate(password, sub): perform a character-by-character substitution using `sub` (mapping from leet char -> canonical char) and return the translated string.
    - dictionary_match(translated_password, _ranked_dictionaries): find exact dictionary substring matches in the translated password and return match descriptors with indices referencing the original string positions.
- If these helpers deviate from the above responsibilities, the behavior and results of this function will differ accordingly.

## Returns:
    list[dict]:
        A list of match descriptor dictionaries describing l33t-based dictionary hits. The list is sorted by (i, j) where i is the start index and j is the inclusive end index in the original password.

        Each returned descriptor is originally produced by dictionary_match and then augmented with:
            - 'l33t' (bool): True (the match required applying a non-empty substitution mapping).
            - 'token' (str): the substring of the original password matched (preserves original characters/case) — computed as password[i:j+1].
            - 'sub' (dict[str, str]): the subset of mappings from the substitution dict that actually appear in the token; maps the leet character found in token -> canonical character.
            - 'sub_display' (str): a human-readable comma-separated display of the sub mapping entries, formatted "leet -> canonical" for each pair present in 'sub'.

        Additional details and edge cases:
            - The function excludes any dictionary-match where token.lower() == match['matched_word'] (i.e., after translation the matched word equals the original token ignoring case). This prevents reporting non-l33t matches produced by an identity or no-op substitution.
            - Matches whose final 'token' length is 1 or less are filtered out (only tokens with length > 1 are returned).
            - If no relevant l33t substitutions exist for the password (the filtered subtable is empty), enumeration of substitutions will yield an empty mapping and the function breaks early — resulting in an empty returned list.
            - The returned descriptor preserves all keys provided by dictionary_match (for example: 'pattern', 'i', 'j', 'matched_word', 'rank', 'dictionary_name', 'reversed' etc.), with 'l33t' set to True and the added keys above.

## Raises:
    - The function itself does not explicitly raise exceptions, but it will propagate exceptions raised by its helper functions or by incorrect argument types:
        - TypeError / AttributeError: If `password` is not a string-like object (no iteration, no .lower()), or if `_l33t_table` or `_ranked_dictionaries` are malformed such that helper functions attempt invalid operations.
        - AttributeError: If translate is called with a mapping that lacks .get or the mapping access semantics expected by translate.
        - Any exceptions raised by dictionary_match (for example, if it assumes a string but receives a non-string) will propagate.

    Exact conditions in the code that lead to exception propagation:
        - The call relevant_l33t_subtable(password, _l33t_table) will iterate over `password` and `table` values; if these are not iterable/mapping-like, Python built-ins will raise TypeError/AttributeError.
        - translate(password, sub) will call mapping.get(...) internally; if sub is not mapping-like the call will raise AttributeError.
        - dictionary_match(subbed_password, _ranked_dictionaries) expects subbed_password to be a string and _ranked_dictionaries to be a mapping of mappings; violations will raise standard Python exceptions from inside those helpers.

## Constraints:
Preconditions:
    - `password` must be a string (or at least support iteration, len(), and .lower()).
    - `_l33t_table` must be a mapping whose values are iterables of substitution strings (typically single-character strings).
    - `_ranked_dictionaries` must be a mapping of dictionary name -> mapping of lowercased words -> rank ints.

Postconditions:
    - The returned list contains only matches that required at least one applied substitution (true l33t matches), each with 'l33t' == True.
    - Every returned descriptor's indices (i, j) refer to the original password and satisfy 0 <= i <= j < len(password).
    - No returned descriptor has token length <= 1.
    - The returned list is sorted by ascending (i, j).

## Side Effects:
    - None intrinsic to l33t_match: it performs no I/O (no filesystem, network, or stdout), does not mutate global variables, and does not change the input password value.
    - It does rely on and propagate side effects from helper functions (if any), but the documented helpers are pure in-memory and side-effect free.

## Control Flow:
flowchart TD
    Start --> ComputeRelevantSubtable[Call relevant_l33t_subtable(password, _l33t_table)]
    ComputeRelevantSubtable --> EnumerateSubs[Call enumerate_l33t_subs(relevant_subtable)]
    EnumerateSubs --> ForEachSub{For each sub in enumerated substitutions}
    ForEachSub --> CheckEmptySub{Is sub empty dict?}
    CheckEmptySub -- Yes --> BreakLoop[break out of loop]
    CheckEmptySub -- No --> TranslatePwd[Call translate(password, sub) -> subbed_password]
    TranslatePwd --> DictMatches[Call dictionary_match(subbed_password, _ranked_dictionaries)]
    DictMatches --> ForEachMatch{For each match returned}
    ForEachMatch --> ComputeToken[token = password[i:j+1]]
    ComputeToken --> CompareLower{token.lower() == match['matched_word']?}
    CompareLower -- Yes --> SkipMatch[continue (do not record match)]
    CompareLower -- No --> BuildMatchSub[Build match_sub only for subbed_chrs present in token]
    BuildMatchSub --> AugmentMatch[Set match['l33t']=True; set 'token','sub','sub_display']
    AugmentMatch --> AppendMatches[Append augmented match to matches list]
    AppendMatches --> ForEachMatch
    ForEachMatch --> ForEachSub
    BreakLoop --> FilterShortTokens[Remove matches with token length <= 1]
    FilterShortTokens --> SortMatches[Sort matches by (i, j)]
    SortMatches --> ReturnMatches[Return sorted matches]
    ReturnMatches --> End

## Examples:
Example 1 — basic l33t match:
    Inputs:
        password = "p4ssw0rd"
        _l33t_table includes {'a': ['4'], 'o': ['0'], 's': ['5','$']}
        _ranked_dictionaries contains an entry 'english' where 'password' (lowercased) exists.
    Behavior:
        - relevant_l33t_subtable reduces the table to substitutions present in "p4ssw0rd" (e.g., {'a': ['4'], 'o': ['0']}).
        - enumerate_l33t_subs yields mappings such as {'4': 'a', '0': 'o'}.
        - translate produces "password".
        - dictionary_match finds "password" at i=0, j=7, with matched_word "password".
        - token = password[0:8] == "p4ssw0rd"; token.lower() != matched_word -> match is recorded.
        - Returned descriptor includes 'l33t': True, 'token': "p4ssw0rd", 'sub': {'4': 'a', '0': 'o'}, and 'sub_display': "4 -> a, 0 -> o".

Example 2 — no relevant substitutions:
    Inputs:
        password = "hello"
        _l33t_table contains substitutions that do not appear in "hello"
    Behavior:
        - relevant_l33t_subtable returns empty dict; enumerate_l33t_subs yields an empty mapping (first item).
        - The function breaks early and returns [].

Example 3 — avoidance of false positives for identity translations:
    Inputs:
        password = "Password"
        If a substitution mapping exists that leaves the token unchanged when lowercased (for example mapping 'P' -> 'p' but token.lower() == matched_word),
    Behavior:
        - The function will skip any dictionary_match for which token.lower() equals the dictionary 'matched_word', avoiding reporting matches that are not true l33t transformations.

Notes:
    - The helper functions' responsibilities are intentionally separated:
        - relevant_l33t_subtable: filter l33t_table by characters present in password.
        - enumerate_l33t_subs: enumerate and deduplicate candidate leet->canonical mappings.
        - translate: apply a single mapping to produce a translated password string.
        - dictionary_match: perform exact substring matches on the translated string and return match descriptors.
    - To obtain consistent results, reimplementations should preserve these responsibilities (enumeration/deduplication, filtering by presence, character-level translation, and exact matching) rather than inlining or merging their logic in ways that change their contracts.

## `zxcvbn.matching.repeat_match` · *function*

## Summary:
Detects repeated-substring patterns within a password and returns match objects describing each repeated run and its minimal base token analysis.

## Description:
This function scans a password for contiguous repeated substrings (for example "abcabcabc" or "1111"), extracts the repeated token and its minimal repeating unit (the base token), and runs the base token through the library's match/guessability analysis to produce a rich match record.

Known callers within this codebase:
- zxcvbn.matching.omnimatch — omnimatch iterates a set of matcher functions (including this one) to collect matches for a password. repeat_match is invoked by omnimatch as part of the overall match-detection pipeline.

Why this logic is a separate function:
- Detecting repeat patterns is a distinct responsibility (pattern recognition + base-token analysis) that is reused by the aggregator (omnimatch). Separating this enables focused unit testing, clear behavior for repeat detection, and reuse by the broader matching pipeline without inlining complex regex and base-token analysis.

## Args:
    password (str):
        The password string to search for repeated substrings. Must be a Python str; passing non-string values will raise a TypeError from the regex calls.
    _ranked_dictionaries (any, optional):
        Kept for API compatibility with other matcher signatures and the omnimatch caller. Default is RANKED_DICTIONARIES. This parameter is not used inside repeat_match itself, but is accepted so callers can pass the same signature to all matchers.

## Returns:
    list[dict]: A list of match dictionaries, one per detected repeated run. Each match dictionary contains the following keys:
        - 'pattern' (str): Literal string 'repeat'.
        - 'i' (int): Start index (inclusive) of the match in the original password.
        - 'j' (int): End index (inclusive) of the match in the original password.
        - 'token' (str): The full substring that is repeated (the contiguous run matched by the regex), e.g. "abcabcabc".
        - 'base_token' (str): The minimal repeating unit inside token, e.g. "abc" for "abcabcabc".
        - 'base_guesses' (int or numeric): The guesses estimate returned by most_guessable_match_sequence for the base_token (value originates from that function's 'guesses' return entry).
        - 'base_matches' (list): The sequence of matches returned by most_guessable_match_sequence for the base_token (value originates from that function's 'sequence' return entry).
        - 'repeat_count' (float): The repeat factor computed as len(token) / len(base_token). Although logically an integer for exact repeats, the code produces a float.

    Edge cases for return values:
    - Returns an empty list when no repeated runs are found.
    - Each match is appended in left-to-right order; matches do not overlap because the scan advances past each found run.

## Raises:
    AttributeError:
        If an internal regex search that the code assumes will succeed returns None and .group(...) is invoked on it (for example, in the rare case lazy_anchored.search(match.group(0)) returns None). This would indicate an unexpected regex match structure.
    KeyError:
        If the imported most_guessable_match_sequence does not return the expected dictionary keys ('sequence' and 'guesses') and the code tries to index them.
    TypeError:
        If password is not a str (e.g., None or a non-string), the regex search calls will raise a TypeError.

## Constraints:
Preconditions:
    - password must be a Python str.
    - The module-level name most_guessable_match_sequence must be a callable that returns a dict containing keys 'sequence' and 'guesses' when passed (base_token, omnimatch(base_token)).
    - The global/outer context must provide omnimatch (the function used to produce submatches for base_token) and RANKED_DICTIONARIES (for default _ranked_dictionaries parameter).

Postconditions:
    - The returned list contains zero or more well-formed repeat match dictionaries (per the Returns section).
    - The scanning progresses left-to-right and the function will not produce overlapping repeat matches (each returned match's j < next match's i).

## Side Effects:
    - No I/O (no files, network, stdout).
    - No mutation of global state inside this function.
    - Calls into most_guessable_match_sequence and omnimatch (external functions) which themselves may perform analysis; any side effects those functions have are not introduced by repeat_match directly.

## Control Flow:
flowchart TD
    Start[Start: last_index = 0]
    A{last_index < len(password)?}
    B[greedy.search(password,pos=last_index)]
    C[lazy.search(password,pos=last_index)]
    D{greedy_match exists?}
    E{len(greedy.group(0)) > len(lazy.group(0))?}
    F[match = greedy; base_token = lazy_anchored.search(match.group(0)).group(1)]
    G[match = lazy; base_token = lazy.group(1)]
    H[i = match.span()[0]; j = match.span()[1]-1]
    I[base_analysis = most_guessable_match_sequence(base_token, omnimatch(base_token))]
    J[append repeat match dict with fields: pattern,i,j,token,base_token,base_guesses,base_matches,repeat_count]
    K[last_index = j + 1]
    L[Return matches]
    Start --> A
    A -->|no| L
    A -->|yes| B
    B --> C
    C --> D
    D -->|no| L
    D -->|yes| E
    E -->|yes| F
    E -->|no| G
    F --> H
    G --> H
    H --> I
    I --> J
    J --> K
    K --> A

Notes on the regex and selection:
- greedy (r'(.+)\1+') finds the longest repeated-run starting at/after last_index.
- lazy (r'(.+?)\1+') finds the shortest repeating-run.
- If the greedy match's whole token is longer than the lazy match's whole token, the code uses the greedy match but extracts the minimal base_token via lazy_anchored (r'^(.+?)\1+$') applied to the matched token.
- Otherwise the lazy match is used and its group(1) is the base_token.
- This logic favors finding the longest repeated-run but always attempts to compute the minimal repeating unit for base analysis.

## Examples:
1) Simple repeated unit
>>> repeat_match("abcabcabc")
Returns (conceptual):
[{
  'pattern': 'repeat',
  'i': 0,
  'j': 8,
  'token': 'abcabcabc',
  'base_token': 'abc',
  'base_guesses': <numeric guesses for 'abc'>,
  'base_matches': <list of match entries for 'abc'>,
  'repeat_count': 3.0
}]

2) Single-character repeat
>>> repeat_match("aaaa")
Returns (conceptual):
[{
  'pattern': 'repeat',
  'i': 0,
  'j': 3,
  'token': 'aaaa',
  'base_token': 'a',
  'base_guesses': <numeric guesses for 'a'>,
  'base_matches': <list of match entries for 'a'>,
  'repeat_count': 4.0
}]

3) No repeats
>>> repeat_match("password123")
Returns:
[]

Usage notes:
- Because repeat_match delegates base_token analysis to most_guessable_match_sequence( base_token, omnimatch(base_token) ), ensure those functions are present and return the expected structure before relying on base_guesses/base_matches values.
- If integrating into a pipeline of matchers, call via omnimatch which will aggregate repeat_match with other matchers in a consistent, sorted order.

## `zxcvbn.matching.spatial_match` · *function*

## Summary:
Aggregates spatial (keyboard-layout) matches for a password across all configured keyboard graphs and returns them sorted by their start and end indices.

## Description:
This function orchestrates per-layout spatial scanning: it iterates every keyboard/graph provided in the _graphs mapping, calls the per-graph scanner to detect contiguous keyboard-key chains (spatial patterns), gathers all matches, and returns them in a deterministic order.

Known callers within this codebase:
- No direct internal callers were discovered in the provided source context. Typical usage in this codebase is from a higher-level password matching or scoring pipeline that collects matches from multiple matchers (dictionary, sequence, spatial, etc.) before computing guessability. In the repository, spatial_match is the canonical entrypoint to gather spatial matches across all known graphs.

Reason this logic is in its own function:
- Responsibility separation: the low-level detection of a contiguous keyboard run is implemented in spatial_match_helper (per single graph). spatial_match encapsulates the orchestration across multiple graphs (different keyboard layouts), aggregation of per-graph results, and consistent ordering. This avoids duplicating the scanning logic for each graph and centralizes the multi-graph behavior (aggregation + sorting).

## Args:
    password (str)
        The password to analyze. Must be indexable and sliceable (standard Python string). Empty string is allowed and yields an empty result.
    _graphs (Mapping[str, Any], optional)
        Mapping of graph-name -> graph-structure used to detect adjacency. Default: the module-level GRAPHS constant.
        Each value is passed directly to spatial_match_helper. The function does not validate graph shapes beyond forwarding them.
    _ranked_dictionaries (Any, optional)
        Present for API compatibility; default: module-level RANKED_DICTIONARIES constant.
        Note: In this implementation the parameter is unused by the function body. It is accepted so callers can pass the same signature used across other matchers.

Interdependencies:
- The function delegates detection and per-match metadata computation to spatial_match_helper; correctness depends on that helper's behavior and on the shape/semantics of each graph in _graphs.

## Returns:
    list[dict]
        A list (possibly empty) of spatial match dictionaries aggregated from all graphs, sorted by (start index 'i', end index 'j').
        Each dict has the structure produced by spatial_match_helper and includes at least:
            - 'pattern' (str): 'spatial'
            - 'i' (int): start index (inclusive)
            - 'j' (int): end index (inclusive)
            - 'token' (str): password[i : j+1]
            - 'graph' (str): the graph name (key from _graphs)
            - 'turns' (int): number of direction changes
            - 'shifted_count' (int): count of shifted characters detected for the token
        Edge cases:
            - If no graph yields matches, returns an empty list.
            - Matches are returned sorted by start then end index so overlapping/ordering decisions are deterministic for downstream processing.

## Raises:
    Propagated exceptions from spatial_match_helper or from malformed inputs:
        - NameError: may propagate if spatial_match_helper triggers a NameError (e.g., missing module-level symbol SHIFTED_RX referenced by the helper).
        - TypeError: may propagate if graph structures are malformed (non-iterable or adjacency entries not supporting membership/indexing) and cause operations in the helper to fail.
        - Any other exception raised by spatial_match_helper will propagate unchanged.

    Notes:
        - spatial_match does not explicitly raise exceptions itself; it only forwards errors raised while iterating graphs or calling the helper.

## Constraints:
Preconditions:
    - password must be a string or sequence supporting indexing/slicing.
    - _graphs must be a mapping from graph name (string) to graph structure compatible with spatial_match_helper.
    - The caller should ensure _graphs contains the graphs they expect; an empty mapping will yield an empty result.

Postconditions:
    - The returned list is sorted by (match['i'], match['j']).
    - Every returned match is produced by spatial_match_helper for some graph in _graphs, and thus satisfies the helper's guarantees (e.g., token length >= 3).

## Side Effects:
    - No I/O (no file, network, or stdout/stderr).
    - Does not mutate the provided _graphs mapping or RANKED_DICTIONARIES argument.
    - Calls spatial_match_helper which may read module-level symbols (e.g., SHIFTED_RX) — any such read does not mutate global state.

## Control Flow:
flowchart TD
    Start --> InitMatches[Initialize matches = []]
    InitMatches --> ForEachGraph{For each graph_name, graph in _graphs.items()}
    ForEachGraph --> CallHelper[Call spatial_match_helper(password, graph, graph_name)]
    CallHelper --> ExtendMatches[Extend matches with helper results]
    ExtendMatches --> NextGraph[Proceed to next graph or exit loop]
    NextGraph --> AfterLoop[After all graphs processed]
    AfterLoop --> SortMatches[Sort matches by (i, j)]
    SortMatches --> Return[Return sorted matches]
    Return --> End

## Examples:
Example A — basic successful aggregation (descriptive)
- Given:
    - password = "qwe123"
    - _graphs contains at least a 'qwerty' graph such that spatial_match_helper finds a contiguous chain for "qwe".
- Behavior:
    - spatial_match calls spatial_match_helper for 'qwerty' (and any other graphs present). If only 'qwerty' yields a match for the "qwe" substring, spatial_match returns a one-element list containing that match dict, sorted trivially:
        [{'pattern':'spatial', 'i':0, 'j':2, 'token':'qwe', 'graph':'qwerty', 'turns':N, 'shifted_count':M}]
      (N and M are integers computed by the helper.)

Example B — no matches
- Given:
    - password = "abcdef" and _graphs that do not contain adjacency relations forming runs in this substring
- Behavior:
    - spatial_match returns an empty list.

Example C — errors propagate to caller
- If a supplied graph structure is malformed (e.g., adjacency entries do not support membership tests or index), spatial_match_helper may raise TypeError; spatial_match does not catch this and the exception propagates to the caller, who should validate graph shapes when using non-standard graphs.

Usage note:
- Call this function as part of the wider match-detection pipeline to obtain spatial matches across every configured keyboard layout; pass the defaults to use the repository's built-in graphs.

## `zxcvbn.matching.spatial_match_helper` · *function*

## Summary:
Finds and returns all contiguous spatial-keyboard chains of length three or more within a password for a single keyboard graph, including metadata (start/end indices, substring token, number of direction changes, and shifted-character count).

## Description:
This helper scans the given password for runs of adjacent keys according to a single keyboard/graph mapping. It follows adjacent-key links in the provided graph until adjacency breaks, then, if the run length is at least 3, records a match dictionary describing that spatial sequence.

Known callers:
- spatial_match — iterates over all available graphs and calls this helper once per graph to collect per-graph spatial matches; spatial_match then sorts/merges results.

Reason for extraction:
- The per-graph scanning algorithm is isolated so that caller code can iterate over multiple graphs (different keyboard layouts) without duplicating scanning logic. This function's responsibility is the low-level detection of spatial chains for one graph and the computation of derived metadata (turns and shifted_count).

Important external dependency:
- SHIFTED_RX — a compiled regular expression expected to be present in the same module namespace. It is used only when graph_name is 'qwerty' or 'dvorak' to determine initial shifted_count based on the first character.

## Args:
    password (str)
        The password to analyze. Must be a sequence supporting indexing and slicing.
    graph (Mapping[str, Sequence])
        Mapping from single-character keys (strings of length 1) to an iterable (typically a list/tuple)
        of adjacency entries. For a given prev_char, graph[prev_char] should produce an iterable of
        adjacency entries (each adjacency is typically a short sequence or string). Each adjacency entry is
        expected to support:
            - membership testing: (cur_char in adj)
            - index lookup: adj.index(cur_char)
        The function uses "adj and cur_char in adj" to guard membership checks against falsy adjacency entries.
        Concrete shape expectation: graph[prev_char] -> ['adj_entry_0', 'adj_entry_1', ...]
        where each adj_entry is indexable.
    graph_name (str)
        Identifier of the keyboard layout (e.g., 'qwerty', 'dvorak'). Controls a small initialization
        path: if graph_name is in ['qwerty', 'dvorak'] and the regex SHIFTED_RX matches the starting character,
        shifted_count is initialized to 1.

Interdependencies:
- The correctness of shifted_count depends on adjacency entries placing shifted characters at positions for which
  adj.index(cur_char) == 1. The graph encoding must be consistent with that convention for shifted detection to be meaningful.

## Returns:
    list[dict]
        A list (possibly empty) of match dictionaries. Each dictionary contains:
            - 'pattern' (str): the literal 'spatial'
            - 'i' (int): start index in password (inclusive)
            - 'j' (int): end index in password (inclusive)
            - 'token' (str): the matched substring; equals password[i: j_exclusive] where j_exclusive == stored 'j' + 1.
                            Equivalently: token == password[i : match['j'] + 1]
            - 'graph' (str): the graph_name passed to the function
            - 'turns' (int): number of direction changes detected while following adjacency links
            - 'shifted_count' (int): number of characters in the matched token that are classified as "shifted"
                                according to adjacency-position logic

Notes:
- Only chains with length >= 3 are reported. The function ignores chains of length 1 or 2.
- Matches are produced in the order discovered while scanning this single graph. The caller is responsible for combining and sorting matches from multiple graphs.

## Raises:
    NameError
        If graph_name is 'qwerty' or 'dvorak' and SHIFTED_RX is not defined in the module namespace, the code
        attempts to call SHIFTED_RX.search(...) and a NameError will be raised.

Implicit/possible exceptions (indicate caller errors or malformed inputs):
    TypeError
        May occur if graph[prev_char] returns a non-iterable or adjacency entries are of types that do not
        support membership (cur_char in adj) or index lookup (adj.index(cur_char)). These represent malformed
        graph structures and are not raised intentionally by the function.
    (No KeyError is propagated from graph access because the function handles KeyError by treating adjacents as [].)

## Constraints:
Preconditions:
    - password must be a string (or sequence) with length >= 0. The function performs no explicit type checking.
    - graph must be a mapping keyed by single-character strings. For any key prev_char referenced during scanning,
      graph[prev_char] should either be present and yield an iterable of adjacency entries, or the mapping should
      raise KeyError (which the function treats as no adjacents).
    - If correct shifted detection is required, adjacency entries must encode shifted characters at positions checked
      by adj.index(cur_char) == 1.

Postconditions:
    - The returned list contains zero or more dictionaries describing non-overlapping spatial chains found in password
      for the provided graph. For each returned match:
          token == password[match['i'] : match['j'] + 1]
          len(token) >= 3

## Side Effects:
    - No file, network, or stdout/stderr I/O.
    - Does not mutate the provided graph mapping or other global state.
    - Reads external module-level symbol SHIFTED_RX (may raise NameError if missing).

## Control Flow:
flowchart TD
    Start --> OuterWhile{i < len(password) - 1?}
    OuterWhile -- No --> ReturnMatches[Return matches]
    OuterWhile -- Yes --> Init[j=i+1; last_direction=None; turns=0]
    Init --> ShiftInit{graph_name in ['qwerty','dvorak'] and SHIFTED_RX.search(password[i])?}
    ShiftInit -- True --> shifted_count = 1
    ShiftInit -- False --> shifted_count = 0
    ShiftInit --> InnerLoop[Loop: inspect adjacency from prev_char = password[j-1]]
    InnerLoop --> TryAdj[Try: adjacents = graph[prev_char] or [] (KeyError -> adjacents=[])]
    TryAdj --> CheckJ{j < len(password)?}
    CheckJ -- No --> found = False
    CheckJ -- Yes --> cur_char = password[j]
    cur_char --> ForAdj[for adj in adjacents: increment cur_direction; if adj and cur_char in adj -> found=True; found_direction=cur_direction; if adj.index(cur_char)==1 -> shifted_count+=1; if last_direction != found_direction -> turns+=1; last_direction=found_direction; break]
    ForAdj --> IfFound{found?}
    IfFound -- Yes --> j = j + 1; InnerLoop
    IfFound -- No --> LengthCheck{(j - i) > 2?}
    LengthCheck -- Yes --> AppendMatch[append {'pattern':'spatial','i':i,'j':j-1,'token':password[i:j],'graph':graph_name,'turns':turns,'shifted_count':shifted_count}]; i = j; OuterWhile
    LengthCheck -- No --> i = j; OuterWhile

## Examples (descriptive):
Example 1 — straightforward 3-key run:
- Context: password contains "qwe" and the graph is encoded such that:
    - graph['q'] includes an adjacency entry that contains 'w',
    - graph['w'] includes an adjacency entry that contains 'e'.
- Behavior:
    - The helper starts at i=0, follows q -> w -> e via adjacency entries, records computed turns and shifted_count,
    - It appends a single match dict with 'i' == 0, 'j' == 2, 'token' == "qwe", and appropriate 'turns' and 'shifted_count'.

Example 2 — shifted-character accounting:
- Context: For a graph where adjacency entries place shifted variants at the second position of each adjacency entry (so adj.index(cur_char) == 1 denotes a shifted character),
  and graph_name is 'qwerty'. If the starting character matches SHIFTED_RX, shifted_count starts at 1 and increments for each adjacency step where adj.index(cur_char) == 1.
- Behavior:
    - The returned match's 'shifted_count' equals the total number of shifted characters observed in the matched token according to adj.index(...) logic (including the possible initial shifted flag set by SHIFTED_RX).

Usage notes:
- To detect spatial patterns across multiple keyboard layouts, call this helper once per graph and aggregate results (spatial_match in this codebase performs that orchestration).
- Ensure graph adjacency entries are well-formed (iterable and indexable) to avoid TypeError during scanning.

## `zxcvbn.matching.sequence_match` · *function*

## Summary:
Detects runs of characters in the input string that form monotonic sequences (constant character-step progressions) and returns a list of match objects describing each detected sequence.

## Description:
This function scans the provided password string and groups contiguous characters whose Unicode codepoint differences (ord deltas) are constant. Each maximal run whose length and step meet the configured thresholds is reported as a match object.

Known callers within the current code snapshot: none discovered in the provided source. In typical password-strength pipelines this logic is extracted as a dedicated matcher used by higher-level match-aggregation logic (e.g., functions that enumerate matches and compute guessability). The function is kept separate to encapsulate sequence-detection rules and keep the matching pipeline modular (so other matchers can be composed without duplicating sequence-detection code).

Why this is a separate function:
- It isolates the heuristics that decide which contiguous character runs constitute a sequence (length threshold, step-size threshold, token classification).
- It returns a normalized match shape (dict with fixed keys) that higher-level code can consume for scoring and ranking.
- Keeping it separate simplifies tests for sequence behavior and makes different sequence-detection heuristics easy to swap.

## Args:
    password (str):
        The input string to scan. Must be a Python str (text). Characters will be examined with ord(), so passing non-str types may raise TypeError.
    _ranked_dictionaries (any, optional):
        A defaulted parameter present in the signature (defaults to RANKED_DICTIONARIES at module level). It is not used by this function's body; it exists so callers can pass the same argument list as other matchers without changing call sites.

## Returns:
    list[dict]:
        A list of zero or more match dictionaries. Each match dictionary has the following keys:
        - 'pattern' (str): always the literal 'sequence' for these matches.
        - 'i' (int): start index (inclusive) of the matched token within password.
        - 'j' (int): end index (inclusive) of the matched token within password.
        - 'token' (str): substring password[i:j+1] that forms the sequence.
        - 'sequence_name' (str): one of:
            * 'lower'  — token matches regex ^[a-z]+$ (all lowercase ASCII letters)
            * 'upper'  — token matches regex ^[A-Z]+$ (all uppercase ASCII letters)
            * 'digits' — token matches regex ^\d+$ (all ASCII digits)
            * 'unicode'— anything else (fallback classification)
        - 'sequence_space' (int): the estimated character-space for the detected sequence:
            * 26 for 'lower' and 'upper' and 'unicode'
            * 10 for 'digits'
        - 'ascending' (bool): True if the delta (ord difference between adjacent characters) is positive; False if negative

    Edge / special return cases:
    - If password is empty or of length 1, an empty list is returned.
    - If no contiguous runs meet the sequence-length and delta constraints, an empty list is returned.

## Raises:
    TypeError:
        If password is not a str (e.g., passing a bytes object in Python 3 can lead to ord() being applied to an int and thus raising TypeError). The function itself does not explicitly raise exceptions; errors arise from misuse of Python string indexing/ord() on incompatible types.

## Constraints:
    Preconditions:
    - password should be a Python str. Each element password[k] must be a single-character string for ord() to work as intended.
    - The module-level constant MAX_DELTA must be defined as a positive integer to bound recognized step sizes. If absent at module import time, this function will fail with a NameError.

    Postconditions:
    - Returned list contains only match dictionaries that satisfy:
        * token length >= 2, and either token length > 2 or abs(delta) == 1 (two-character sequences are only reported when their step is exactly +/-1).
        * 0 < abs(delta) <= MAX_DELTA.
    - For consecutive segments in the password, matches may overlap by one character at the boundary (see Control Flow notes).

## Side Effects:
    - None. The function performs pure computation: no I/O, no global mutation, no network or filesystem access.
    - It does compile and use a small number of regular expressions at runtime to classify tokens (these are ephemeral and local to the function).

## Control Flow:
flowchart TD
    A[Start: receive password] --> B{len(password) == 1?}
    B -- yes --> Z[return []]
    B -- no --> C[init result, i=0, last_delta=None]
    C --> D[for k from 1 to len(password)-1]
    D --> E[delta = ord(password[k]) - ord(password[k-1])]
    E --> F{last_delta is None?}
    F -- yes --> G[last_delta = delta]
    F -- no --> H{delta == last_delta?}
    H -- yes --> D (continue loop)
    H -- no --> I[j = k-1; call update(i,j,last_delta)]
    I --> J[i = j; last_delta = delta]
    J --> D (next iteration)
    D --> K[after loop: call update(i,len(password)-1,last_delta)]
    K --> L[return result list of matches]
    subgraph UpdateLogic
        U1[update(i,j,delta)]
        U1 --> U2{(j - i > 1) or (delta and abs(delta) == 1)?}
        U2 -- no --> U3[do nothing]
        U2 -- yes --> U4{0 < abs(delta) <= MAX_DELTA?}
        U4 -- no --> U3
        U4 -- yes --> U5[classify token as lower/upper/digits/unicode; append match]
        U5 --> U3
    end

Notes on indexing: i and j are inclusive indices. When a segment ends at j, the next segment's start index is set to j (so adjacent segments share the boundary character at index j).

## Implementation details (sufficient to reimplement):
- Iterate over adjacent character pairs to compute delta = ord(current) - ord(previous).
- Maintain last_delta, initially None. When last_delta is None set it to the first encountered delta and continue iteration (the first delta initializes the current step).
- When the current delta changes (delta != last_delta), finalize the previous run which spans indices [i, j] where j = k - 1, by applying the update checks:
    * Only consider reporting the run if either its length is > 2 (j - i > 1) or the run has length == 2 and abs(delta) == 1.
    * Only consider runs whose 0 < abs(delta) <= MAX_DELTA.
    * Classify the run token: use regex ^[a-z]+$ => 'lower', ^[A-Z]+$ => 'upper', ^\d+$ => 'digits', else 'unicode'.
    * Use sequence_space 26 for letter/unicode classes, 10 for digits.
    * ascending flag is delta > 0.
    * Append a dict with keys listed in Returns.
- After the loop, call update for the final run spanning [i, len(password)-1] using the last_delta captured; this finalizes any trailing run.

## Examples:
Example 1 — simple lowercase ascending run:
    Input: "abcd"
    Behavior: detected as a single lowercase ascending sequence covering indices 0..3.
    Returned match (conceptual):
        [{'pattern':'sequence', 'i':0, 'j':3, 'token':'abcd', 'sequence_name':'lower',
          'sequence_space':26, 'ascending':True}]

Example 2 — two-character adjacent step:
    Input: "ab"  # ord difference == 1
    Behavior: reported because two-character sequences are allowed when abs(delta) == 1.
    Returned match:
        [{'pattern':'sequence', 'i':0, 'j':1, 'token':'ab', 'sequence_name':'lower',
          'sequence_space':26, 'ascending':True}]

Example 3 — two-character non-adjacent step:
    Input: "aC"  # ord difference not equal to 1
    Behavior: not reported (token length == 2 but abs(delta) != 1).
    Returned: []

Example 4 — empty or single-character input:
    Input: "", "x"
    Returned: []

Example 5 — digit descending run:
    Input: "43210"
    Behavior: single digits sequence, sequence_name 'digits', ascending False, sequence_space 10.

## Additional notes:
- The function deliberately tolerates and reports sequences that overlap by one character at segment boundaries (this is intentional: segments are defined by constant deltas; adjacent segments share the boundary character).
- The module-level constant MAX_DELTA sets the maximum absolute step size considered a meaningful sequence (e.g., typical implementations set MAX_DELTA to a small integer so very large jumps are ignored).
- The _ranked_dictionaries parameter is retained in the signature for API compatibility; it is not used by this function.

## `zxcvbn.matching.regex_match` · *function*

## Summary:
Scans a password for occurrences of a set of named regular expressions and returns a sorted list of normalized match records describing every match found.

## Description:
This function iterates over a mapping of named regular expressions and uses each regex to find all non-overlapping or overlapping occurrences (as yielded by the regex engine) in the provided password. Each occurrence is converted into a normalized match dictionary used by downstream sequence-assembly and scoring logic.

Known callers:
- Not present in the supplied snippet. In the typical zxcvbn pipeline, this function is invoked during the "matching" phase: after preliminary tokenization and dictionary lookups, regex_match is used to detect pattern-based matches (e.g., recent years, dates, repeated character classes) which are then passed along to the sequence-building routines for scoring.

Why this is a separate function:
- Encapsulates scanning and normalization for regex-based match detection.
- Provides a stable, consistent match-record format that other matching functions and scoring routines expect.
- Allows swapping or testing different regex sets without touching higher-level orchestration code.

## Args:
    password (str):
        The password string to scan. Must be a string (or a string-like sequence supporting indexing/slicing). Passing None or a non-string will result in a TypeError or AttributeError when regex.finditer is invoked.
    _regexen (mapping[str, re.Pattern], optional):
        Mapping of name -> compiled regular-expression-like object. Each value must implement finditer(password) which yields match objects with .group(), .start(), and .end() methods/attributes. Default: module-level REGEXEN.
    _ranked_dictionaries (any, optional):
        Present for API parity with other matching functions but intentionally unused by this implementation. Default: module-level RANKED_DICTIONARIES.

Interdependencies:
- Each value of _regexen must be compatible with the Python re.Pattern interface (or otherwise provide a finditer method with the same semantics). If values are plain strings or otherwise lack finditer, an AttributeError will occur.

## Returns:
list[dict]: A list (possibly empty) of match record dictionaries. Each dict contains:
    - 'pattern' (str): The literal value 'regex'.
    - 'token' (str): The substring of password matched by the regex (match.group(0)).
    - 'i' (int): Inclusive start index of the match within password (match.start()).
    - 'j' (int): Inclusive end index of the match within password (match.end() - 1).
    - 'regex_name' (str): The key from _regexen whose regex produced the match.
    - 'regex_match' (re.Match): The underlying regex match object returned by the regex engine.

Ordering:
- The returned list is sorted ascending by (i, j) — first by start index, then by end index.
- All matches yielded by each regex.finditer call are included; overlapping matches reported by the regex engine are preserved (the function does not deduplicate or suppress overlaps beyond what the regex engine yields).

Edge cases:
- If no matches are found, returns an empty list [].
- If password is the empty string "", finditer yields no matches and the result is [].
- If password is None or a non-string incompatible with the regex engine, an exception will be raised when attempting to call finditer.

## Raises:
- AttributeError: If _regexen is not a mapping or if a value in _regexen does not provide finditer.
- TypeError: If password is of a type incompatible with the regex engine (e.g., None).
- Any exceptions thrown by the regex engine or by methods accessed on the match object (rare for compiled, correct patterns). The function itself does not explicitly raise errors; exceptions originate from these operations.

## Constraints:
Preconditions:
    - Caller must supply a valid string for password.
    - Caller must supply a mapping whose values have finditer; typically compiled re.Pattern objects.
Postconditions:
    - Returned list contains only dicts matching the documented fields.
    - Returned list is sorted by (i, j) and contains one entry per regex-produced match.

## Side Effects:
    - None. The function performs no I/O, does not mutate global state, and does not call external services.
    - It returns raw regex match objects (which may internally reference the input string); if callers persist results long-term or serialize them, they should extract serializable fields (token, i, j, regex_name) rather than relying on the match object.

## Control Flow:
flowchart TD
    A[Start] --> B{_regexen is iterable?}
    B -- No --> X[AttributeError/TypeError raised when iterating]
    B -- Yes --> C[Initialize matches = []]
    C --> D[For each (name, regex) in _regexen]
    D --> E[Call regex.finditer(password)]
    E --> F{rx_match yielded?}
    F -- Yes --> G[Append normalized record {pattern,token,i,j,regex_name,regex_match}]
    G --> E
    F -- No --> H[Continue to next regex]
    H --> I[After all regexes processed]
    I --> J[Sort matches by (i, j)]
    J --> K[Return sorted matches]

## Examples (concrete illustration):
- Example returned value (JSON-like) for a hypothetical regex set that detects 4-digit years and repeated digits:
    [
      {
        "pattern": "regex",
        "token": "1999",
        "i": 3,
        "j": 6,
        "regex_name": "recent_year",
        "regex_match": <re.Match object>
      },
      {
        "pattern": "regex",
        "token": "111",
        "i": 8,
        "j": 10,
        "regex_name": "repeat_digits",
        "regex_match": <re.Match object>
      }
    ]
  - Interpretation: Two matches were found. The first match spans indices 3–6, matched by the regex named "recent_year"; the second spans 8–10, matched by "repeat_digits". The actual match objects are included under 'regex_match' but are not serializable as-is — extract token, i, j, and regex_name for persistence.

- Practical usage guidance:
    1. Compile or otherwise prepare your named regex map (e.g., {"recent_year": re.compile(r"\b(19|20)\d{2}\b"), ...}).
    2. Call the function with the password string and the map.
    3. Use 'i' and 'j' to place matches into a sequence assembler and use 'token' for pattern-conditional scoring.
    4. If you need to store or transmit match results, convert each dict to a serializable form by omitting or transforming 'regex_match'.

Notes:
- The third parameter _ranked_dictionaries exists for API symmetry only and does not affect behavior.
- Because the function preserves each match produced by the regex engine, callers implementing higher-level deduplication or prioritization should perform that work after receiving the sorted list.

## `zxcvbn.matching.date_match` · *function*

## Summary:
Finds and returns structured date matches (year, month, day, matched substring and indices) for date-like substrings inside a password, handling both contiguous-digit and single-separator date formats.

## Description:
This function performs a two-form scan over the input password to detect candidate dates:

1) Contiguous-digit tokens (token lengths 4 through 8)
   - For each substring token whose characters are all digits and whose length is between 4 and 8 inclusive, the function consults DATE_SPLITS[len(token)] to obtain an iterable of split-index pairs (k, l).
   - For each (k, l), it builds three integer parts by converting:
       - int(token[0:k]), int(token[k:l]), int(token[l:])
     and passes that three-element list to map_ints_to_dmy to test/normalize into a canonical date dict {'year': int, 'month': int, 'day': int}.
   - All successful candidate dicts for that token are collected. If at least one candidate is found, the function selects the candidate whose |candidate['year'] - scoring.REFERENCE_YEAR| is minimal. If multiple candidates tie for minimal distance, the earliest candidate (first in the candidates list) is chosen (stable first-winner behavior).
   - A match dictionary is appended for the chosen candidate with 'separator' set to ''.

2) Tokens with a single separator (space, slash, backslash, underscore, dot or hyphen)
   - The token is tested against the regular expression:
       ^(\d{1,4})([\s/\\_.-])(\d{1,2})\2(\d{1,4})$
     where group 1, group 3 and group 4 are the three numeric parts and group 2 is the separator character.
   - The function converts groups to integers in the order [int(group1), int(group3), int(group4)] and passes that list to map_ints_to_dmy; if it returns a dict, a match is appended with 'separator' equal to the captured separator.

Post-processing:
- After gathering matches from both scans, the function filters out strict submatches: a match M is removed if there exists another match O (O != M) with O['i'] <= M['i'] and O['j'] >= M['j'] (i.e., O strictly contains M). Important: if two match dictionaries are exactly equal (match == other), the equality check in the implementation causes the comparison to skip that other entry, so identical duplicates are not removed by the submatch filter; exact duplicates may therefore survive filtering.
- The filtered matches are returned sorted by ascending (i, j).

Why this is a separate function:
- Date detection requires split enumeration, integer conversion, date-normalization heuristics, candidate-ranking by proximity to a reference year, and containment-filtering — logic that is cohesive and sufficiently complex to warrant isolation from the general matching pipeline.

Known callers:
- No direct callers were discovered in the scanned snapshot for this task. Conceptually, this function is intended for use by the zxcvbn matcher pipeline (the component that invokes all matchers over a password).

## Args:
    password (str)
        - The string to scan. Must be a Python str (regex operations assume unicode/text). Non-str inputs may raise TypeError from the regex engine.
    _ranked_dictionaries (any, optional)
        - Present for API compatibility with other matchers. Defaults to RANKED_DICTIONARIES.
        - This parameter is unused by date_match and does not affect behavior.

## Returns:
    list[dict]
        - A list of zero or more match dictionaries. Each returned dict contains:
            - 'pattern' (str): 'date'
            - 'token' (str): substring of password that matched
            - 'i' (int): inclusive start index of the token in password
            - 'j' (int): inclusive end index of the token in password
            - 'separator' (str): '' for contiguous-digit matches, or the single captured separator character for separator matches
            - 'year' (int): canonical four-digit year (as produced/normalized by map_ints_to_dmy)
            - 'month' (int): integer month in 1..12
            - 'day' (int): integer day in 1..31
        - Guarantees:
            - Each returned match corresponds to a dict returned by map_ints_to_dmy (i.e., validated and normalized by that helper).
            - No returned match is a strict submatch of another returned match (strict containment defined as other['i'] <= match['i'] and other['j'] >= match['j'] with other != match).
            - Matches are sorted by ascending (i, j).
        - Note: Exact duplicate match dictionaries (value-equal) present in the initial collection are not removed by the submatch filter due to the equality guard in the implementation.

## Raises:
- NameError: if module-level names required by the function (DATE_SPLITS, map_ints_to_dmy, scoring.REFERENCE_YEAR) are not defined.
- KeyError: if DATE_SPLITS exists but does not contain an entry for some token length encountered (e.g., DATE_SPLITS[len(token)] missing).
- TypeError: if password is not a string-like object usable by the regex engine.
- ValueError: may be raised by int(...) conversions if inputs are malformed (unlikely because regexes restrict digits), or by helper functions called.
- Any exception raised by map_ints_to_dmy or other helpers will propagate.

## Constraints:
Preconditions:
- DATE_SPLITS must map token lengths (int) to an iterable of (k, l) split index pairs where 0 < k < l < length. The implementation expects entries for token lengths 4..8 (for contiguous-digit tokens).
- map_ints_to_dmy must accept a sequence of length-3 integers and return either a dict {'year': int, 'month': int, 'day': int} or None.
- scoring.REFERENCE_YEAR must be an integer used for candidate selection.
- password must be a str.

Postconditions:
- Returned matches are valid dates according to map_ints_to_dmy.
- 'year' values reflect any normalization performed by map_ints_to_dmy (e.g., two-digit → four-digit conversion).
- No returned match is strictly contained within another returned match.

## Side Effects:
- None performed directly: no file I/O, no network, and no intentional mutation of module or global state. Side effects from called helpers (map_ints_to_dmy, scoring.*) will propagate.

## Control Flow:
flowchart TD
    Start --> InitMatches[Init matches = []]
    InitMatches --> DigitsOuter[For i in 0 .. len(password)-4]
    DigitsOuter --> DigitsInner[For j in i+3 .. i+7]
    DigitsInner --> BreakIfOut{if j >= len(password) then break}
    BreakIfOut -- true --> Next_i_or_j
    BreakIfOut -- false --> tokenDigits[token = password[i:j+1]]
    tokenDigits --> CheckDigits{maybe_date_no_separator matches (^\d{4,8}$)?}
    CheckDigits -- no --> Next_j
    CheckDigits -- yes --> ForEachSplit[For each (k,l) in DATE_SPLITS[len(token)]: ints = [int(token[:k]), int(token[k:l]), int(token[l:])]; dmy = map_ints_to_dmy(ints)]
    ForEachSplit --> CandidatesCollected{candidates empty?}
    CandidatesCollected -- true --> Next_j
    CandidatesCollected -- false --> ChooseBest[Select candidate with min |year - REFERENCE_YEAR|; ties: first candidate]
    ChooseBest --> AppendDigitMatch[append match dict (separator='')]
    AppendDigitMatch --> Next_j
    Next_j --> DigitsInner

    DigitsDone --> SepOuter[For i in 0 .. len(password)-6]
    SepOuter --> SepInner[For j in i+5 .. i+9]
    SepInner --> BreakIfOut2{if j >= len(password) then break}
    BreakIfOut2 -- true --> Next_sep_j
    BreakIfOut2 -- false --> tokenSep[token = password[i:j+1]]
    tokenSep --> CheckSep{maybe_date_with_separator matches?}
    CheckSep -- no --> Next_sep_j
    CheckSep -- yes --> ints = [int(g1), int(g3), int(g4)]; dmy = map_ints_to_dmy(ints)
    Then --> IfDmy{if dmy truthy?}
    IfDmy -- false --> Next_sep_j
    IfDmy -- true --> AppendSepMatch[append match dict (separator = g2)]
    AppendSepMatch --> Next_sep_j
    Next_sep_j --> SepInner

    BothDone --> Filter[For each match M: remove if exists O != M with O.i <= M.i and O.j >= M.j]
    Filter --> Sort[sort by (i,j)]
    Sort --> ReturnMatches[return sorted list]

## Examples:
1) Separator date
    - Input: password = "x12/04/1985y"
    - Behavior: token "12/04/1985" (i=1, j=10) matches the separator regex. map_ints_to_dmy([12, 4, 1985]) returns {'year':1985,'month':4,'day':12}. Returned list contains:
      {'pattern':'date','token':'12/04/1985','i':1,'j':10,'separator':'/','year':1985,'month':4,'day':12}

2) Contiguous-digit date (8-digit)
    - Input: password = "id19900101!"
    - Behavior: token "19900101" (length 8) is split by DATE_SPLITS[8] into candidate triples; the valid triple that map_ints_to_dmy recognizes (e.g., [1990,1,1]) becomes a match. Returned example:
      {'pattern':'date','token':'19900101','i':2,'j':9,'separator':'','year':1990,'month':1,'day':1}

3) Submatch filtering behavior
    - If matches list contains {'i':2,'j':9,...} and also {'i':4,'j':7,...}, the shorter match is removed because it is strictly contained. If two matches are value-equal dictionaries (exact duplicates), the implementation's equality guard causes them not to be considered containment rivals; exact duplicates can therefore persist if produced.

4) Error examples
    - If DATE_SPLITS lacks an entry for a token length encountered, a KeyError is raised when indexing DATE_SPLITS[len(token)].
    - If password is not a str (e.g., None), regex matching will raise a TypeError; convert inputs to str before calling if needed.

Implementation notes for reimplementation:
- Precisely follow the loop bounds shown (first scan: token lengths 4..8 via j in range(i+3, i+8) with immediate break if j >= len(password); second scan: token lengths 6..10 via j in range(i+5, i+10) with same break).
- Use the exact regex patterns used above for digit-only and separator forms.
- Preserve the candidate-ranking procedure (minimum absolute year distance to scoring.REFERENCE_YEAR with stable first-winner ties) and the submatch removal semantics (skip equality, only remove strict containment).
- Do not attempt additional heuristics beyond what map_ints_to_dmy and DATE_SPLITS provide; this function delegates date validation/normalization and relies on those helpers.

## `zxcvbn.matching.map_ints_to_dmy` · *function*

## Summary:
Interpret a three-integer tuple/sequence as a day-month-year date candidate and, when the integers can be consistently mapped to a valid calendar date, return a dict with canonical year, month, and day; otherwise return None.

## Description:
This helper is used by date-matching logic that attempts to parse three adjacent numeric tokens (for example, substrings extracted from a password) into a date. It centralizes the rules that decide whether a 3-integer sequence can represent a valid day/month/year in one of the two common split orders.

Known callers within the codebase:
- No explicit callers were located during the scan provided for this task. Conceptually, it is intended to be invoked by higher-level date/datetime matching routines that iterate over numeric tokens extracted from input strings (passwords) and attempt to convert 3-number sequences into date matches.

Why this logic is a separate function:
- It encapsulates all date-interpretation heuristics (range checks, early rejections, two-orientation day/month checking via map_ints_to_dm, and normalization of 2-digit years via two_to_four_digit_year). This avoids duplicating the exact same validation and splitting order logic across multiple matchers and makes the heuristics easier to maintain and test.

## Args:
    ints (sequence[int]):
        - A sequence (typically a list or tuple) containing at least three integer values representing three numeric tokens in original order.
        - Required properties:
            - Indexable: function accesses ints[1], ints[2] and slices ints[0:2] and ints[1:3].
            - Elements should be numeric (integers) or types comparable with integers; otherwise comparison operations may raise TypeError.
        - Typical usage: ints contains exactly three integers representing numbers parsed from contiguous text (e.g., [15, 6, 1985]).

## Returns:
    dict or None:
        - If the function finds a valid date interpretation, it returns a dict with integer fields:
            - 'year': canonical four-digit year (may be returned unchanged if already in four-digit range, or converted from a 2-digit token using two_to_four_digit_year).
            - 'month': integer month in range 1..12 (obtained from map_ints_to_dm on the appropriate two-element slice).
            - 'day': integer day in range 1..31 (obtained from map_ints_to_dm).
        - If no valid interpretation is found, the function returns None (implicit).
        - Possible successful return paths:
            1. A candidate y (one element of the triple) lies within [DATE_MIN_YEAR, DATE_MAX_YEAR]; the corresponding other two integers produce a valid (day, month) via map_ints_to_dm → returns mapping using y unchanged.
            2. Neither candidate y is a 4-digit year in the accepted DATE_MIN_YEAR..DATE_MAX_YEAR range, but one of the two-element slices is a valid (day, month); that y is converted by two_to_four_digit_year and returned with the day/month mapping.
        - Note: The function may return None early if various validation heuristics fail (see "Control Flow" and examples).

## Raises:
    - The function itself does not explicitly raise exceptions, but Python runtime errors from improper inputs can occur:
        - IndexError: if ints has fewer than 3 elements (because ints[1] or ints[2] are accessed).
        - TypeError: if comparisons (e.g., ints[1] > 31) are attempted against non-comparable types (e.g., passing strings).
        - Any exceptions raised by map_ints_to_dm or two_to_four_digit_year propagate unchanged.

## Constraints:
    Preconditions:
        - The caller should pass a sequence of at least three numeric values (ideally exactly three integers).
        - The constants DATE_MIN_YEAR and DATE_MAX_YEAR must be defined in the module scope; they establish the inclusive allowed full-year range.
        - The helper map_ints_to_dm must be available and must return either a dict {'day': int, 'month': int} on success or None on failure.
        - The helper two_to_four_digit_year must be available to normalize 2-digit year tokens.

    Postconditions:
        - If a dict is returned, then:
            - 'day' is in 1..31
            - 'month' is in 1..12
            - 'year' is an integer (either unchanged if already a full year within DATE_MIN_YEAR..DATE_MAX_YEAR or produced by two_to_four_digit_year)
        - If None is returned, at least one validation rule failed, so the input should not be considered a valid date according to the function's heuristics.

## Side Effects:
    - None. The function performs no I/O, does not mutate its input sequence, and does not alter external/global state.
    - It calls map_ints_to_dm and two_to_four_digit_year; any side effects of those functions (none expected in typical implementations) would propagate.

## Control Flow:
flowchart TD
    Start --> CheckMiddle[(Check ints[1] valid: 1..31?)]
    CheckMiddle -- False (<=0 or >31) --> ReturnNoneEarly[Return None]
    CheckMiddle -- True --> InitCounters[Init counters over_12, over_31, under_1 = 0]
    InitCounters --> ForEachInt[For each n in ints]
    ForEachInt --> CheckYearRange{Is 99 < n < DATE_MIN_YEAR or n > DATE_MAX_YEAR?}
    CheckYearRange -- True --> ReturnNoneRange[Return None]
    CheckYearRange -- False --> UpdateCounters[Update over_31/over_12/under_1 as needed]
    UpdateCounters --> LoopEnd{All ints processed?}
    LoopEnd -- No --> ForEachInt
    LoopEnd -- Yes --> CountersCheck{over_31>=2 or over_12==3 or under_1>=2?}
    CountersCheck -- True --> ReturnNoneCounters[Return None]
    CountersCheck -- False --> BuildSplits[Build possible_four_digit_splits = [(ints[2], ints[0:2]), (ints[0], ints[1:3])]]
    BuildSplits --> FirstForLoop[For each (y,rest) in splits (first pass)]
    FirstForLoop --> CheckYRange{DATE_MIN_YEAR <= y <= DATE_MAX_YEAR?}
    CheckYRange -- Yes --> CallMapDM[dm = map_ints_to_dm(rest)]
    CallMapDM --> DmTrue{dm is truthy?}
    DmTrue -- Yes --> ReturnFullYear[Return {'year': y, 'month': dm['month'], 'day': dm['day']}]
    DmTrue -- No --> ReturnNoneIfFail[Return None (stop — do not check other split)]
    CheckYRange -- No --> ContinueFirstLoop[Continue to next split]
    ContinueFirstLoop --> EndFirstForLoop[Finish first pass]
    EndFirstForLoop --> SecondForLoop[For each (y,rest) in splits (second pass)]
    SecondForLoop --> CallMapDM2[dm = map_ints_to_dm(rest)]
    CallMapDM2 --> DmTrue2{dm is truthy?}
    DmTrue2 -- Yes --> NormalizeYear[y = two_to_four_digit_year(y)]
    NormalizeYear --> ReturnNormalized[Return {'year': y, 'month': dm['month'], 'day': dm['day']}]
    DmTrue2 -- No --> ContinueSecondLoop[Continue to next split]
    ContinueSecondLoop --> EndSecondForLoop[Finish]
    EndSecondForLoop --> ReturnNoneFinal[Return None]

Notes on flow:
- The first loop prefers an interpretation where one element is already a 4-digit-year inside DATE_MIN_YEAR..DATE_MAX_YEAR; if such a candidate y is found but the corresponding day/month slice fails map_ints_to_dm, the function returns None immediately and does not examine the other split. This is a deliberate behavior in the code (it does not fall back to trying the alternate split when a full-year candidate exists but the day/month slice fails).
- The second loop implements the fallback: if neither y was an accepted four-digit year (or the first loop didn't return earlier), it will try map_ints_to_dm for each rest and, if successful, normalize y via two_to_four_digit_year and return the mapping.

## Examples:
These examples assume DATE_MIN_YEAR = 1900 and DATE_MAX_YEAR = 2050 for illustration only.

1) Input already contains a full four-digit year and a valid day/month:
    - ints = [15, 6, 1985]
    - Middle check: ints[1] = 6 is within 1..31 → continue
    - Per-int checks: no invalid year-range values; counters pass
    - Splits tried first: (y=1985, rest=[15,6]) → 1985 in [1900,2050]; map_ints_to_dm([15,6]) returns {'day':15,'month':6} → function returns {'year':1985,'month':6,'day':15}

2) Two-digit year fallback:
    - ints = [15, 6, 85]
    - First pass: y=85 is not in [1900,2050] → skipped in first loop
    - Second pass: for rest=[15,6], map_ints_to_dm returns {'day':15,'month':6}; two_to_four_digit_year(85) -> 1985 → returns {'year':1985,'month':6,'day':15}

3) Early rejection due to middle number invalid:
    - ints = [12, 0, 1990] -> ints[1] = 0 (<= 0) → immediate return None

4) Early rejection due to out-of-range intermediate value:
    - If DATE_MIN_YEAR = 1900 and ints = [12, 5, 150] then during per-int checks: 99 < 150 < DATE_MIN_YEAR holds (150 < 1900) → return None

5) Subtle behavior when a full-year candidate's day/month slice fails:
    - ints = [99, 99, 2000]
    - First split tries y=2000, rest=[99,99]; 2000 in DATE_MIN_YEAR..DATE_MAX_YEAR, but map_ints_to_dm([99,99]) likely returns None (99 is not a valid month/day) → function returns None immediately and does NOT attempt the alternate split (ints[0] as year). This early return is an explicit behavior of the function.

Implementation notes for reimplementation:
- Be precise with all early-return conditions in the same order as shown: the middle-element check, per-element year-range checks, counter-based heuristics, first-pass four-digit-year preference (with immediate None if day/month fails), and only then the fallback pass that converts two-digit years.
- Do not attempt to "try both splits then select"; the original logic short-circuits if a candidate full-year exists but its day/month rest fails.

## `zxcvbn.matching.map_ints_to_dm` · *function*

## Summary:
Return a day/month mapping when a two-integer sequence can be interpreted as a valid (day, month) pair in either order.

## Description:
This helper inspects a two-element integer sequence and attempts to interpret the values as (day, month). It tests the sequence both in its original order and reversed; on the first orientation that satisfies day ∈ [1,31] and month ∈ [1,12], it returns a mapping with keys 'day' and 'month'. If neither orientation is valid, it returns None (implicit).

Known callers within this repository:
- None are enumerated in this file. This is a small utility intended for date/datetime matching logic in the password-matching pipeline; it is implemented as a separate function to centralize the day/month interpretation logic so callers do not duplicate the two-orientation checks and validation.

Why this is a separate function:
- It encapsulates the specific responsibility of deciding whether two integers can represent a valid day/month combination (including trying both possible orders). Extracting this prevents duplication and isolates the validation rules (allowed day and month ranges) in one place.

## Args:
    ints (sequence[int]): A sequence of exactly two integers (for example, a tuple or list of length 2).
        - Required properties:
            - Must be indexable/iterable to produce two values for unpacking into (d, m).
            - Must be reversible via reversed(ints) (i.e., a sequence or object implementing __reversed__), because the function tries both the original and reversed order.
        - Behavior if these properties are not met:
            - If the sequence does not contain exactly two elements, unpacking (d, m) will raise a ValueError.
            - If the object is not reversible, reversed(ints) will raise a TypeError.

## Returns:
    dict or None:
        - If a valid interpretation is found, returns a dict with two integer keys:
            - 'day': int in the inclusive range 1..31
            - 'month': int in the inclusive range 1..12
        - If neither ordering yields a valid (day, month) pair, returns None (implicit return at end of function).
        - Examples of possible return values (described in prose):
            - Given ints = (15, 6) -> returns {'day': 15, 'month': 6}
            - Given ints = (6, 15) -> returns {'day': 15, 'month': 6} (because reversed order is checked)
            - Given ints = (0, 13) -> returns None (neither 0 as day nor 13 as month are within allowed ranges)

## Raises:
    ValueError: If 'ints' does not unpack into exactly two values (e.g., length != 2).
    TypeError: If reversed(ints) is called on an object that does not support the reversed() protocol.
    Note: These exceptions are raised by the underlying Python operations (unpacking, reversed) rather than explicit checks in the function.

## Constraints:
    Preconditions:
        - Caller should pass a length-2 sequence (list or tuple) of integers.
        - Elements should be integer types (or at least comparable to integers using <= and >=); otherwise comparisons may raise TypeError.
    Postconditions:
        - If the function returns a dict, its 'day' and 'month' values satisfy 1 <= day <= 31 and 1 <= month <= 12.
        - If the function returns None, no valid day/month mapping exists for either ordering of the provided integers.

## Side Effects:
    - None. The function performs no I/O, does not mutate its inputs, and does not modify external state.

## Control Flow:
flowchart TD
    Start --> UnpackOriginal[(Unpack ints into d,m)]
    UnpackOriginal --> CheckOriginal{Is 1 <= d <= 31 and 1 <= m <= 12?}
    CheckOriginal -- Yes --> ReturnOriginal[Return {'day': d, 'month': m}]
    CheckOriginal -- No --> BuildReversed[Construct reversed(ints) and unpack into d,m]
    BuildReversed --> CheckReversed{Is 1 <= d <= 31 and 1 <= m <= 12?}
    CheckReversed -- Yes --> ReturnReversed[Return {'day': d, 'month': m}]
    CheckReversed -- No --> End[Return None]

## Examples (usage described in prose):
    - Typical successful input:
        Passing ints = (31, 12) yields {'day': 31, 'month': 12} because the original order is valid.
    - Successful due to reversed order:
        Passing ints = (12, 31) yields {'day': 31, 'month': 12} because the reversed ordering matches day/month constraints.
    - No valid mapping:
        Passing ints = (0, 13) yields None because 0 is not in 1..31 and 13 is not in 1..12, in either order.
    - Error cases:
        Passing a single-integer sequence or a sequence with three integers causes a ValueError from the unpacking operation.
        Passing a non-reversible iterator (like a generator) causes reversed(ints) to raise TypeError.

## `zxcvbn.matching.two_to_four_digit_year` · *function*

## Summary:
Normalize an integer representing a 2- or 4-digit year into a canonical four-digit year integer suitable for date-matching logic.

## Description:
This function maps a numeric year value that may be expressed as 2 digits (e.g., 85) or already as 3–4+ digits (e.g., 1985 or 2023) into a normalized integer year value according to the common two-digit-year heuristic:
- Values > 99 are treated as already full-year values and returned unchanged.
- Values in 51..99 are interpreted as 1951..1999.
- Values in 0..50 are interpreted as 2000..2050.

Known callers within the provided scan:
- No direct callers were discovered in the scanned inputs for this task. Conceptually, this function is intended for use by date-extraction and date-matching routines (such as those that parse substrings of passwords into numeric tokens) to convert short year tokens into a canonical 4-digit year before further scoring or pattern matching.

Reason for extraction:
- Centralizes the two-to-four-digit year conversion rule so all date-matching code uses the same mapping logic. This keeps date parsing code small and avoids duplicating the heuristic across multiple places.

## Args:
    year (int): Integer representing a year value to normalize.
        - Typical values: 0..99 for two-digit years, or 100..9999 for three- or four-digit years.
        - The function compares numeric ranges; passing non-numeric types (e.g., str, None) will raise a TypeError during comparison.
        - Interdependencies: none.

## Returns:
    int: A normalized year as an integer.
        - If input year > 99: returns the input value unchanged.
        - If 51 <= input year <= 99: returns input + 1900 (maps 51->1951, 99->1999).
        - If 0 <= input year <= 50: returns input + 2000 (maps 0->2000, 50->2050).
        - For negative inputs the function returns (input + 2000) because it falls through to the final branch; such behavior is an artifact of the simple numeric comparisons and is not the intended use.

## Raises:
    TypeError: If the provided year is not a type that supports numeric comparison with integers (for example, a str or None). The function contains no explicit raise statements — any exception arises from Python comparison semantics.

## Constraints:
Preconditions:
    - Caller should provide an integer value representing a year (preferably non-negative).
    - The value should typically be in the range 0..99 for two-digit inputs or >=100 for already full-year values.

Postconditions:
    - The return value is an integer.
    - If the input was a conventional 2-digit year (0..99), the return will be a value in either 1951..1999 or 2000..2050 according to the rule above.
    - If the input was >99, the return equals the input.

## Side Effects:
    - None. The function performs pure computation and does not perform I/O or mutate external state.

## Control Flow:
flowchart TD
    Start --> IsGT99{year > 99?}
    IsGT99 -- yes --> ReturnInput[Return input year unchanged]
    IsGT99 -- no --> IsGT50{year > 50?}
    IsGT50 -- yes --> Return1900[Return year + 1900]
    IsGT50 -- no --> Return2000[Return year + 2000]
    ReturnInput --> End
    Return1900 --> End
    Return2000 --> End

## Examples:
- Typical two-digit mapping:
    - Input 85  => Output 1985  (85 > 50 → 85 + 1900)
    - Input 05  => Output 2005  (5 <= 50 → 5 + 2000)
    - Input 50  => Output 2050  (50 <= 50 → 50 + 2000)
    - Input 99  => Output 1999  (99 > 50 → 99 + 1900)

- Already full-year or larger numeric values:
    - Input 1985 => Output 1985  (1985 > 99 → returned unchanged)
    - Input 100  => Output 100   (100 > 99 → returned unchanged — callers should normally pass realistic 4-digit years)

- Edge cases and error handling:
    - Passing a non-integer like "85" (string) will lead to a TypeError during comparison; callers should validate or coerce inputs first.
    - Passing a negative integer (e.g., -1) returns 1999 (-1 + 2000) due to the final else branch; negative inputs are outside the intended input domain and should be validated by the caller if necessary.

