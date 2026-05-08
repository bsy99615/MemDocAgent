# `describe_categorical_pandas.py`

## `src.ydata_profiling.model.pandas.describe_categorical_pandas.get_character_counts_vc` · *function*

## Summary:
Aggregate per-character frequencies from a value-counts Series (index = observed categorical values, values = counts), returning a Series that maps each character to the total summed count across all observed values.

## Description:
This function converts a Series of value-count pairs (typically produced by pandas.Series.value_counts()) into character-level frequencies by:
1. Building a Series whose values are the original observed values and whose index are their counts.
2. Removing empty-string observed values.
3. Expanding each observed value into its individual characters.
4. Reconstructing a Series that maps each character to the contributing count(s) and summing those counts per character.

Typical call site / callers:
- Used in categorical-column profiling where a pipeline has computed value counts for a column and needs character-level frequency summaries (for example, to compute most common characters, visual badges, or character-based histograms).
- Typical pre-step: vc = some_series.value_counts(); then get_character_counts_vc(vc).

Why this logic is extracted:
- The transformation from (value -> count) to (character -> aggregated count) is a focused, multi-step data reshaping and aggregation. Extracting it keeps profiling orchestration code clearer, enables reuse for different display or metric computations, and isolates handling of edge cases around empty strings and exploding sequences.

## Args:
vc (pandas.Series)
    A one-dimensional pandas Series representing value counts:
    - Expected semantics: vc.index contains the observed categorical values (ideally strings or other iterable character sequences); vc.values are numeric counts (ints or floats).
    - The function uses vc.index as the sequence source and vc itself as the index when building an intermediate Series, therefore vc must expose an .index attribute.
    - The implementation tolerates non-unique numeric counts in vc (pandas Series index may be non-unique); those duplicate counts are preserved and aggregated appropriately.

## Returns:
pandas.Series
    - Index: characters (strings) obtained by iterating each observed value.
    - Values: numeric totals equal to the sum of the original counts from vc for each character.
    - Ordering: if the resulting aggregated Series is non-empty it is sorted in descending order by the numeric counts; otherwise, an empty Series is returned.
    - Empty result cases:
        * If vc is empty, returns an empty Series.
        * If all observed values are empty strings (or filtered out), returns an empty Series.
    - Type notes: index dtype is object (string-like); value dtype is numeric (int/float) as inferred by pandas when summing the incoming counts.

## Raises:
The function does not explicitly raise custom exceptions, but the following runtime errors can occur depending on input:
- AttributeError: If vc has no .index attribute (i.e., vc is not a pandas-like Series/object with .index).
- TypeError: If an item in vc.index is not iterable (for example, a numeric or None) then list(item) will raise TypeError.
- TypeError/ValueError/AttributeError: If non-string types appear as characters such that counts.index.str.len() is called on an index that does not support string methods, pandas may raise an AttributeError or TypeError. These errors indicate the input needs to be coerced to string-like values first.
- Any pandas-related errors from explode/groupby may surface for incompatible dtypes or unsupported pandas versions.

## Constraints:
Preconditions:
- vc must be a pandas.Series-like object with .index iterable entries representing values to be split into characters.
- Caller should ensure the observed values are of string-like type (or otherwise iterable in the intended character sense). Non-iterable index entries should be cleaned/coerced before calling.

Postconditions:
- The returned Series (possibly empty) maps each non-empty character to the total count aggregated from vc, and (when non-empty) is sorted descending by counts. The input vc is not mutated.

## Side Effects:
- None. All operations are in-memory pandas transformations; the input vc is not modified. There is no I/O or external interactions.

## Control Flow:
flowchart TD
    Start --> BuildSeries["pd.Series(vc.index, index=vc)"]
    BuildSeries --> FilterEmpty["Filter values: series != \"\""]
    FilterEmpty --> ToList["Apply list(...) to each remaining value"]
    ToList --> Explode["characters = characters.explode()"]
    Explode --> BuildCountsSeries["counts = pd.Series(characters.index, index=characters).dropna()"]
    BuildCountsSeries --> HasCounts{"len(counts) > 0 ?"}
    HasCounts -->|No| ReturnEmpty["Return counts (empty Series)"]
    HasCounts -->|Yes| GroupBy["counts.groupby(level=0, sort=False).sum()"]
    GroupBy --> Sort["counts.sort_values(ascending=False)"]
    Sort --> DropEmptyKey["counts[counts.index.str.len() > 0]"]
    DropEmptyKey --> Return["Return aggregated character counts"]
    Return --> End

## Examples:
- Example 1 (typical):
  - Input (conceptual): vc with index ["ab", "a"] and values [2, 1] (2 occurrences of "ab", 1 of "a").
  - Outcome: returned Series contains "a" -> 3 (2 from "ab" + 1 from "a"), "b" -> 2.

- Example 2 (empty / filtered):
  - Input: empty vc or vc whose index entries are only empty strings -> function returns an empty Series.

- Example 3 (precondition violation):
  - If vc.index contains non-iterable entries (e.g., None or numeric types where list(item) is invalid), the function will raise a TypeError when attempting list(...) — callers should coerce non-string values before calling.

## `src.ydata_profiling.model.pandas.describe_categorical_pandas.get_character_counts` · *function*

## Summary:
Produces a frequency count of characters appearing across all values in a pandas Series by concatenating the series into a single sequence and counting each character with collections.Counter.

## Description:
The function concatenates all values of the provided pandas Series using the pandas string accessor (series.str.cat()) and constructs a collections.Counter over the concatenated result. It is a small helper intended for character-level analysis of categorical/string features (for example, to detect punctuation, digits, or rare Unicode characters) and is designed to be used by higher-level categorical profiling logic that handles preprocessing and null treatment.

Known callers:
- Located in the categorical description module; no concrete call sites were found in the provided snapshot. Typical callers are categorical-summary routines that need character-frequency statistics for a column.

Typical usage context:
- Invoked after any desired preprocessing (null handling, casting to string) to compute a distribution of characters across all entries of a column.

Why this is an extracted helper:
- Encapsulates the specific operation (concatenate then count) so callers can control preprocessing (e.g., how missing values are treated) and so the operation can be unit-tested independently.

## Args:
    series (pd.Series)
        The pandas Series to be analyzed.
        - Must be a pandas Series object (the implementation type-annotates pd.Series).
        - For predictable per-character counts, the series should contain string-like values or be converted to strings by the caller.
        - The function calls series.str.cat() with no arguments (no sep or na_rep supplied).

## Returns:
    collections.Counter
        A Counter mapping tokens to integer occurrence counts.

        Interpretation specifics:
        - Normal case (string result): If series.str.cat() returns a string, counters are per-character (each key is a single-character string); sum(counter.values()) equals len(concatenated_string).
        - Empty result: If the concatenated result is the empty string, the function returns an empty Counter().
        - Non-iterable scalar: If series.str.cat() yields a non-iterable scalar (for example numpy.nan when all elements are missing and no na_rep is used), collections.Counter(...) will raise a TypeError (see Raises). This function does not catch such errors.

## Raises:
    - TypeError:
        Raised when collections.Counter is called with a non-iterable argument (e.g., series.str.cat() returns a non-iterable scalar such as NaN). The function allows this exception to propagate to the caller.
    - Any exception raised by series.str.cat():
        Exceptions from pandas' string accessor or concatenation (e.g., AttributeError if the object is not a pandas Series, or internal pandas exceptions) will propagate.

## Constraints:
    Preconditions:
        - Input must be a pandas Series.
        - Callers are responsible for any preprocessing required to guarantee meaningful character-level counts (see Safe usage patterns).
    Postconditions:
        - The function returns a collections.Counter and does not modify the input Series.
        - When the concatenated result is a sequence (string), the total count equals the length of that sequence.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state or the input Series.
    - Any side effects or errors stem from pandas internals invoked via series.str.cat().

## Control Flow:
flowchart TD
    Start --> ReceiveSeries["Receive pd.Series 'series'"]
    ReceiveSeries --> CallStrCat["Call series.str.cat()"]
    CallStrCat --> IsIterable{"Is concatenated result iterable (e.g., str)?"}
    IsIterable -- Yes --> CounterCall["Call Counter(concatenated_result)"]
    IsIterable -- No --> TypeErrorRaise["collections.Counter raises TypeError"]
    CounterCall --> ReturnCounter["Return Counter"]
    TypeErrorRaise --> Propagate["Propagate TypeError to caller"]
    ReturnCounter --> End
    Propagate --> End

## Safe usage patterns and examples (textual):
Example A — typical string values
    Input series values: ["ab", "c", "a"]
    Concatenated result: "abca"
    Call: get_character_counts(series)
    Output: Counter({'a': 2, 'b': 1, 'c': 1})

Example B — empty series
    Input: empty Series
    Concatenated result: "" (empty string)
    Call: get_character_counts(series)
    Output: Counter()  (empty Counter)

Example C — avoid TypeError when series may be all-missing
    Problem: If the series contains only missing values and no na_rep is provided, series.str.cat() can produce a NaN scalar; Counter(NaN) raises TypeError.
    Safe approaches (choose one):
      - Fill missing values with an empty string before calling: apply series.fillna("") then call the function.
      - Cast to string after filling nulls to ensure string semantics: series.fillna("").astype(str) then call the function.
      - Perform concatenation with an explicit na_rep yourself and then call Counter on that concatenated string.
    Error handling:
      - If the caller cannot guarantee preprocessing, wrap the call in a try/except that catches TypeError and handles the non-iterable case explicitly (for example, treating a non-iterable concatenation as an empty result).

## `src.ydata_profiling.model.pandas.describe_categorical_pandas.counter_to_series` · *function*

## Summary:
Convert a collections.Counter of item frequencies into a pandas.Series of counts indexed by the corresponding items, preserving the descending frequency order produced by Counter.most_common().

## Description:
This utility takes a Counter (mapping of hashable items to integer counts) and returns a pandas Series where the Series index are the Counter keys in descending frequency order and the values are the corresponding counts.

Known callers within the codebase:
- No direct callers were discovered during inspection of this file alone. Typical usage in this repository is within categorical/summary computation logic where frequency counts produced by Counter need to be represented as a pandas.Series for downstream analysis or rendering (for example, to compute category histograms, imbalance scores, or to create summary tables).

Why this is a separate function:
- Encapsulates the common transformation from Counter -> pandas.Series with consistent behavior for empty inputs and ordering; avoids repeating the empty-case guard and tuple-unpacking logic each time frequency counters are converted into Series.

## Args:
    counter (collections.Counter): A Counter mapping hashable items to numeric counts (typically ints >= 0).
        - Allowed values: any collections.Counter instance. The function also works with objects that behave like Counter and provide a most_common() method returning an iterable of (item, count) tuples.
        - Notes:
            * Keys must be hashable (requirement of Counter and pandas Index).
            * An empty Counter is handled explicitly and returns an empty Series with dtype object.

## Returns:
    pandas.Series: A Series whose index are the items from the Counter in the same order returned by counter.most_common() (descending frequency order) and whose values are the corresponding counts.
    - If the Counter is empty, returns pandas.Series([], dtype=object).
    - For a non-empty Counter, the returned Series will have an index type inferred from the item types and a dtype inferred from the count values (typically integer).
    - The length of the Series equals the number of distinct keys in the Counter.

## Raises:
    - No exceptions are explicitly raised by this function.
    - Possible exceptions propagated from callers or libraries:
        * AttributeError: If the provided object does not implement most_common() (e.g., passing a plain list).
        * ValueError or TypeError: If pandas.Series construction fails (e.g., items are unhashable for use as an Index, though Counter itself requires hashable keys).
    - These exceptions will surface only when the input is malformed or incompatible with expected Counter semantics.

## Constraints:
    Preconditions:
        - The input should be a collections.Counter or an object providing most_common() that yields an iterable of (item, count) pairs.
        - Counter keys must be hashable (requirement for Counter keys and pandas Index entries).
    Postconditions:
        - Returned Series index matches the order and items of counter.most_common().
        - Returned Series values correspond one-to-one with the counts from the Counter.
        - If input is empty or falsy (len == 0), an empty pandas.Series with dtype=object is returned.

## Side Effects:
    - None. The function performs no I/O, global state mutation, or external service calls. It returns a new pandas.Series and does not modify the input Counter.

## Control Flow:
flowchart TD
    A[Start] --> B{counter is falsy or empty?}
    B -- Yes --> C[Return empty pandas.Series(dtype=object)]
    B -- No --> D[Get counter.most_common() -> list of (item,count)]
    D --> E[Unzip into items, counts]
    E --> F[Create pandas.Series(counts, index=items)]
    F --> G[Return Series]

## Examples:
1) Typical usage with non-empty Counter
    from collections import Counter
    c = Counter({'apple': 5, 'banana': 2, 'cherry': 2})
    # counter_to_series(c) returns a pandas.Series with values [5, 2, 2] and index ['apple', 'banana', 'cherry']
    # Index order corresponds to Counter.most_common() (ties preserve arbitrary but deterministic order per Counter)

2) Empty Counter
    c = Counter()
    # counter_to_series(c) -> pandas.Series([], dtype=object)

3) Defensive note / error handling
    # Passing an object without most_common() raises AttributeError:
    bad = ['a', 'b', 'a']
    # counter_to_series(bad) -> AttributeError: 'list' object has no attribute 'most_common'
    # To avoid this, ensure you pass a Counter: Counter(bad)

## `src.ydata_profiling.model.pandas.describe_categorical_pandas.unicode_summary_vc` · *function*

## Summary:
Produce a comprehensive Unicode-character-level summary for a categorical value-counts Series, returning aggregated character frequencies and grouped counts by Unicode block, script, and category aliases.

## Description:
This function consumes a pandas Series of value counts (typically the result of pandas.Series.value_counts()) and computes character-level statistics and groupings for profiling categorical data. It performs the following high-level work:
- Builds per-character aggregated counts from the value-counts Series (delegates to get_character_counts_vc).
- Maps each character to Unicode block, short category, long category alias, and script using tangled_up_in_unicode when available; otherwise falls back to unicodedata.category for short category and uses "(unknown)" placeholders for other mappings.
- Aggregates counts by block alias, script, and category alias and presents both summary counts and per-group character breakdowns.
- Returns a dictionary containing numeric summaries, pandas.Series objects, and dictionaries of pandas.Series for grouped character counts.

Known callers within the codebase and typical context:
- No single explicit caller was discovered during static analysis of this file alone. Typical/expected callers are categorical-column profiling routines that:
  - Compute value counts via pandas.Series.value_counts()
  - Call unicode_summary_vc(vc) to obtain character-level summaries used for visualization, badges, or further metrics (e.g., imbalance, histograms).
- Typical trigger: after computing value counts for a column and before rendering or computing character-based metrics.

Why this logic is extracted:
- The extraction isolates the multi-step character aggregation and Unicode classification logic from higher-level profiling orchestration. This keeps profiling pipelines concise, enables reuse, and centralizes fallback behavior for missing Unicode tooling.

## Args:
vc (pandas.Series)
    - A pandas Series representing value counts:
        * Index: observed categorical values (expected string-like or other iterable sequences whose elements should be treated as characters).
        * Values: numeric counts (ints or floats) corresponding to how often each observed value appears.
    - Requirements / interdependencies:
        * Each index element must be iterable (string-like). Non-iterable entries (e.g., None, plain numbers) will cause underlying character-splitting logic to raise a TypeError.
        * The function calls get_character_counts_vc(vc) internally, so vc must satisfy its preconditions (see get_character_counts_vc documentation): it must be a Series with .index iterable entries.

## Returns:
dict
    - A dictionary summarizing character-level and Unicode-grouped counts. Keys and value types:
        * "n_characters_distinct" (int): Number of distinct characters observed (length of character_counts Series index).
        * "n_characters" (numeric): Total count of characters aggregated across all observed values (sum of character_counts values).
        * "character_counts" (pandas.Series): Series mapping each character -> aggregated count (sorted descending when non-empty).
        * "category_alias_values" (dict[str, str]): Mapping character -> long category alias (human-friendly category name). Values come from category_long(...) if available; otherwise "(unknown)".
        * "block_alias_values" (dict[str, str]): Mapping character -> abbreviated block name (block_abbr(...) or "(unknown)").
        * "block_alias_counts" (pandas.Series): Aggregated counts per block alias (index: block alias, values: aggregated counts). Produced by converting a Counter to Series via counter_to_series.
        * "n_block_alias" (int): Number of distinct block aliases present (length of block_alias_counts).
        * "block_alias_char_counts" (dict[str, pandas.Series]): For each block alias key, a pandas.Series mapping characters in that block -> counts.
        * "script_counts" (pandas.Series): Aggregated counts per script name (index: script name, values: aggregated counts).
        * "n_scripts" (int): Number of distinct scripts present (length of script_counts).
        * "script_char_counts" (dict[str, pandas.Series]): For each script name, a pandas.Series mapping characters in that script -> counts.
        * "category_alias_counts" (pandas.Series): Aggregated counts per category alias (index: category alias, values: aggregated counts). Underscores in index labels are replaced with spaces where possible.
        * "n_category" (int): Number of distinct category aliases present (length of category_alias_counts).
        * "category_alias_char_counts" (dict[str, pandas.Series]): For each category alias, a pandas.Series mapping characters in that category -> counts.
    - Edge-case returns:
        * If get_character_counts_vc(vc) yields an empty Series (e.g., empty vc or only empty-string values), many returned Series will be empty. The function returns a dictionary with the same keys, but value Series/dicts may be empty.
        * If tangled_up_in_unicode is not installed, mapping functions for block, block_abbr, category_long, script become simple placeholders: short category still uses unicodedata.category; other mappings return "(unknown)". The function still returns a consistent dictionary structure.

## Raises:
- The function does not explicitly raise custom exceptions. Possible runtime exceptions (propagated from helpers or Python/Pandas) include:
    * TypeError: If an index element in vc is not iterable (get_character_counts_vc will raise when attempting to iterate characters).
    * AttributeError / TypeError: If get_character_counts_vc or counter_to_series return objects incompatible with operations in this function (e.g., unexpected types). These signal precondition violations.
    * Exceptions from Unicode mapping functions: if tangled_up_in_unicode functions (block, category, script, etc.) raise for certain inputs, those exceptions will propagate.
- ImportError for tangled_up_in_unicode is handled internally (fallback behavior applied), so an ImportError will not surface from this function.

## Constraints:
Preconditions:
    - vc must be a pandas.Series with .index entries that are iterable (string-like).
    - get_character_counts_vc and counter_to_series must be available in the environment (they are expected helper functions in the same module).
Postconditions:
    - The input vc is not modified.
    - The returned dict contains aggregated numeric summaries and pandas.Series/dict structures consistent with the character-level data derived from vc.
    - If non-empty, all returned per-character Series are sorted (character_counts is created from get_character_counts_vc which sorts descending).

## Side Effects:
    - None with respect to external I/O or global state. The function performs only in-memory computations and returns a new dictionary; it does not write files, call network services, or mutate global variables.

## Control Flow:
flowchart TD
    Start --> TryImport["Try import tangled_up_in_unicode"]
    TryImport -->|Success| UseTangled["Use block, block_abbr, category, category_long, script"]
    TryImport -->|Fail| Fallback["Use unicodedata.category; set other mappers to '(unknown)'"]
    UseTangled --> GetChars
    Fallback --> GetChars
    GetChars["Call get_character_counts_vc(vc) -> character_counts (Series)"] --> BuildSummary
    BuildSummary["Initialize summary with n_characters_distinct, n_characters, character_counts"] --> BuildMappings
    BuildMappings["Compute char_to_block, char_to_category_short, char_to_script mappings"] --> UpdateSummary
    UpdateSummary["Add category_alias_values and block_alias_values to summary"] --> PerBlockLoop
    PerBlockLoop["For each character,count: increment block_alias_counts and per_block_char_counts"] --> ComputeBlockSeries
    ComputeBlockSeries["Convert block_alias_counts -> series (counter_to_series), build block_alias_char_counts dict"] --> PerScriptLoop
    PerScriptLoop["For each character,count: increment script_counts and per_script_char_counts"] --> ComputeScriptSeries
    ComputeScriptSeries["Convert script_counts -> series, build script_char_counts dict"] --> PerCategoryLoop
    PerCategoryLoop["For each character,count: increment category_alias_counts and per_category_alias_char_counts"] --> ComputeCategorySeries
    ComputeCategorySeries["Convert category_alias_counts -> series, sanitize index (replace '_'), build category_alias_char_counts"] --> Finalize
    Finalize["Attempt to sanitize category_alias_counts.index in a suppressed AttributeError block"] --> ReturnSummary
    ReturnSummary["Return summary dict"] --> End

## Examples:
1) Typical usage (happy path)
    - Setup:
        * Suppose col is a pandas Series of strings. Compute value counts:
            vc = col.value_counts()
    - Call:
        summary = unicode_summary_vc(vc)
    - Expected outcome:
        * summary["character_counts"] is a pandas.Series mapping each character observed in col -> total occurrences (integer).
        * summary["n_characters"] equals the sum of summary["character_counts"] values.
        * summary["block_alias_counts"], summary["script_counts"], and summary["category_alias_counts"] are pandas.Series summarizing counts per Unicode block/script/category alias. Per-group character breakdowns are in the "*_char_counts" dictionaries.

2) Example when tangled_up_in_unicode is not installed
    - Behavior:
        * The function still returns the same dictionary structure.
        * "category_alias_values" will map characters to values produced by category(...) (unicodedata.category), and other alias/group mappings will be "(unknown)".
    - Use-case:
        * This allows profiling pipelines to remain robust even if optional Unicode tooling is absent.

3) Error handling example (precondition violation)
    - If vc.index contains non-iterable entries (e.g., integers or None), calling unicode_summary_vc(vc) will surface a TypeError originating from character-splitting inside get_character_counts_vc. To avoid this, coerce index entries to strings before calling:
        vc.index = vc.index.astype(str)
        summary = unicode_summary_vc(vc)

## `src.ydata_profiling.model.pandas.describe_categorical_pandas.word_summary_vc` · *function*

## Summary:
Aggregate word-level counts from a pandas Series of value-count pairs by splitting each index string into tokens, weighting each token by its source value's count, and returning a descending-sorted pandas Series of word frequencies wrapped in a dict (or an empty dict if no words remain).

## Description:
This function transforms a pandas Series that encodes counts per unique textual value (typical input: the result of pandas.Series.value_counts()) into a word-frequency summary where each token receives the full count weight of each value it appears in.

Step-by-step behavior (directly following implementation):
- Constructs a new Series whose values are the original unique values (vc.index) and whose index are the original counts (vc). This causes subsequent string operations to be applied to the textual values while preserving the numeric counts as the row index.
- Lowercases each textual value and splits it on whitespace into a list of tokens.
- Explodes the lists so each token becomes its own row; the row index remains the original count associated with the source value.
- Strips surrounding ASCII punctuation and whitespace from each token using string.punctuation + string.whitespace.
- Builds a Series (word_counts) where the index is the token and the value is the original count (from the row index). Non-token (null) entries are dropped.
- Groups word_counts by token (groupby(level=0, sort=False)) and sums the associated counts — this yields the total weight for each token across all source values.
- Sorts the aggregated token counts in descending order.
- If a non-empty stop_words list is provided, it lowercases the provided stop words and removes any matching tokens from the aggregated counts.
- Returns {"word_counts": word_counts} when the aggregated Series is non-empty; otherwise returns {}.

Why this is a separate function:
- Encapsulates the non-trivial mapping from value-level counts to token-level weighted counts, including tokenization, cleaning, grouping, sorting, and optional stop-word filtering. This keeps higher-level reporting code focused on presentation rather than tokenization and aggregation details.

Typical callers / usage context:
- Called in pipelines that produce summaries for categorical or text columns after computing per-value frequencies (e.g., after pandas Series.value_counts()).
- Intended for generating word-level summaries for reporting, visualization, or further analysis.

## Args:
    vc (pandas.Series):
        - A pandas Series where:
            * vc.index contains the textual values (strings or other objects convertible to strings for .str operations).
            * vc.values (the Series values) are numeric counts or weights associated with each unique text value.
        - Typical origin: pandas.Series.value_counts() or equivalent.
        - Requirements:
            * vc must be a pandas.Series (or a Series-like object) with a valid .index and values; otherwise pandas operations may raise AttributeError/TypeError.
            * Index entries (the textual values) that are not strings will yield NaN during .str operations and will be filtered out later.
    stop_words (List[str], optional):
        - Default: [] (an empty list literal used as function default in the implementation).
        - If provided and non-empty, each entry is lowercased and any matching token (exact match) will be removed from the resulting counts.
        - Matching is case-insensitive because tokens are lowercased during tokenization.
        - Note: the implementation rebinds a local variable to a lowercased list; it does not modify any caller-supplied list in-place. However, because the default is a mutable empty list literal, callers should avoid relying on function-level mutation (the function itself does not mutate this default).

## Returns:
    dict:
        - If there are aggregated tokens after processing and optional filtering:
            {"word_counts": s} where s is a pandas.Series with:
                * s.index: tokens (strings), lowercased, with surrounding ASCII punctuation and whitespace removed.
                * s.values: numeric aggregated counts (sum of the original vc values for each token). Numeric dtype follows pandas' result of summing the input counts.
                * s is sorted in descending order by count (largest counts first).
        - If no tokens remain (e.g., empty input, all tokens were null, or all tokens filtered out by stop_words), returns an empty dict {}.

    Important concrete behavior:
        - The function returns {} exactly when word_counts.empty is True after all processing.
        - The returned Series values are produced by pandas groupby(...).sum() and thus follow pandas' aggregation semantics for the input dtypes.

## Raises:
    - The function does not raise custom exceptions explicitly.
    - Possible exceptions raised by underlying pandas operations (propagated):
        * AttributeError / TypeError: if vc is not a pandas.Series or if vc.index / vc values do not support the operations used (pd.Series(vc.index, index=vc), .str accessor, .explode(), .str.strip()).
        * Any pandas exceptions resulting from invalid operations (for example, if groupby or sum fails for the provided dtypes).
    - These exceptions will surface naturally from pandas; the function contains no try/except handling.

## Constraints:
    Preconditions:
        - vc must be a pandas.Series-like object.
        - vc.values should represent counts/weights to be used numerically; while non-numeric types may be accepted by pandas, aggregation results will follow pandas semantics (e.g., string concatenation for sums of strings) and will not be checked here.
        - Tokenization and cleaning operate on ASCII punctuation defined by string.punctuation; non-ASCII punctuation is not removed by this strip call.

    Postconditions:
        - When a non-empty dict is returned, the "word_counts" Series:
            * Has only non-null, lowercased token strings as its index.
            * Has aggregated counts as its values.
            * Is sorted in descending order by value.
        - No external state is modified.

## Side Effects:
    - None. The function performs only in-memory transformations and returns a new dict/Series. No file I/O, network access, or global state mutation occurs.

## Complexity and resource notes:
    - Time: tokenization and explode cost O(T) where T is the total number of tokens across all unique values; grouping also costs O(T log U) in practice where U is number of unique tokens.
    - Space: exploding tokens may create a temporary structure roughly proportional to T; for large vc inputs this can be memory-intensive.

## Control Flow:
flowchart TD
    Start([Start: word_summary_vc(vc, stop_words)]) --> MakeSeries[Make series = pd.Series(vc.index, index=vc)]
    MakeSeries --> Tokenize[Lowercase and split: .str.lower().str.split()]
    Tokenize --> Explode[Explode lists to single-token rows]
    Explode --> Strip[Strip ASCII punctuation/whitespace from tokens]
    Strip --> Build[Build word_counts = pd.Series(words.index, index=words)]
    Build --> DropNulls[Drop entries where token is null (index.notnull())]
    DropNulls --> Group[Group by token and sum counts (groupby(level=0).sum())]
    Group --> Sort[Sort values descending (sort_values(ascending=False))]
    Sort --> CheckStop{len(stop_words) > 0 ?}
    CheckStop -- Yes --> LowerStop[Lowercase stop_words list]
    LowerStop --> Filter[Remove tokens in stop_words via .loc[~index.isin(stop_words)]]
    CheckStop -- No --> SkipFilter[Skip filtering]
    Filter --> EmptyCheck[Is word_counts.empty ?]
    SkipFilter --> EmptyCheck
    EmptyCheck -- True --> ReturnEmpty[Return {}]
    EmptyCheck -- False --> ReturnDict[Return {"word_counts": word_counts}]
    ReturnEmpty --> End([End])
    ReturnDict --> End

## Examples (conceptual, non-executable description):
1) Basic aggregation:
    - Input vc: a Series with index ["Hello world", "Hello"] and values [2, 1] (i.e., "Hello world" occurred 2 times, "Hello" occurred 1 time).
    - Processing:
        * "Hello world" -> tokens "hello", "world"; each gets weight 2.
        * "Hello" -> token "hello" gets weight 1.
        * Aggregation: "hello": 2 + 1 = 3, "world": 2
    - Return: {"word_counts": Series(index=["hello","world"], values=[3,2])} sorted descending by value.

2) With stop words:
    - Same vc as above, stop_words=["hello"]
    - After lowercasing stop words and removing matches, return: {"word_counts": Series(index=["world"], values=[2])}

3) Edge cases:
    - If vc is empty or all index entries are non-string producing null tokens -> no tokens remain -> return {}.
    - If vc values are non-numeric, pandas' groupby.sum() behavior applies (no validation is performed in this function).

Implementation notes for re-implementation:
- Preserve the exact ordering of operations (build Series with index=vc, then .str.lower().str.split(), .explode(), .str.strip(), construct a Series with tokens as index and counts as values, drop null tokens, groupby(level=0, sort=False).sum(), sort_values(ascending=False), optionally filter by lowercased stop_words).
- Do not mutate the provided stop_words list in-place; the original implementation rebinds a local variable when lowercasing.

## `src.ydata_profiling.model.pandas.describe_categorical_pandas.length_summary_vc` · *function*

## Summary:
Produce length-based statistics and a length -> count histogram from a value-count Series: returns max, min, weighted mean, weighted median of lengths, and a histogram mapping each observed length to the total count of values with that length.

## Description:
Takes a pandas Series that represents value counts (index = unique values, values = counts) and summarizes the string lengths of those unique values. The function:
1. Reverses the mapping (index becomes values and values become index) to align lengths with counts,
2. Computes the length of each unique value,
3. Aggregates counts per length (length histogram),
4. Computes max/min/weighted mean/weighted median over observed lengths using counts as weights,
5. Returns these metrics plus the histogram.

Known callers:
- No direct callers were present in the supplied context. In the repository this helper is intended to be used by higher-level categorical summary routines (e.g., describe_categorical_1d or other categorical profiling functions) that operate on a Series produced by value_counts().

Why extracted:
- Encapsulates length-specific aggregation logic so other categorical summary code can reuse it and remain focused on higher-level concerns (imbalance, distinct counts, frequency tables). It isolates detail about how lengths are aggregated and weighted.

## Args:
    vc (pandas.Series):
        - A pandas Series representing counts per unique value.
        - Expected shape/semantics: index = unique values (labels), values = numeric counts (non-negative).
        - Required properties:
            * vc must support .index and .values.
            * Index entries should be string-like if meaningful length measurements are desired (pandas.Series.str.len is used).
        - Interdependencies:
            * The function computes lengths from vc.index and uses vc (the Series index and values) as the data and weights respectively for aggregation.

## Returns:
    dict with these keys:
    - "max_length" (int or float):
        Maximum observed length among vc.index (computed with numpy.max over the histogram index).
    - "mean_length" (float):
        Weighted mean of lengths where weights are the total counts per length (computed via numpy.average).
    - "median_length" (int or float):
        Weighted median of lengths computed by the helper weighted_median(data=lengths, weights=counts).
        Note: weighted_median (as implemented in the codebase) sorts data and weights independently and applies a heuristic; behavior follows that implementation exactly.
    - "min_length" (int or float):
        Minimum observed length among vc.index (computed with numpy.min over the histogram index).
    - "length_histogram" (pandas.Series):
        Series indexed by length values (numeric) with values equal to the summed counts for that length. This Series is sorted by count in descending order.

Edge-case return values:
- If vc contains only entries whose lengths convert to NaN via pandas' .str.len (e.g., non-string types), those NaNs will appear in the histogram index and will propagate into max/min calls possibly causing errors.
- If lengths exist but total weight is zero, mean_length may be NaN (numpy.average behavior); median_length behavior depends on weighted_median with zero or small weights.

## Raises:
The function does not explicitly raise custom exceptions, but the following exceptions can occur from operations used:
    - AttributeError / TypeError:
        If vc is not a pandas.Series or its elements do not support pandas.Series.str.len, calling series.str.len() will raise an AttributeError or TypeError.
    - ValueError:
        If the length histogram is empty (e.g., vc is empty), numpy reductions (np.max, np.min) will raise ValueError: "zero-size array to reduction operation ...".
    - IndexError:
        weighted_median will raise IndexError when invoked with empty arrays (it indexes s_weights[-1] and locates indices).
    - Other numeric issues:
        numpy.average may return NaN if the sum of weights is zero; callers should guard against or handle NaNs if that is relevant.

## Constraints:
Preconditions:
    - vc must be a pandas.Series where vc.index are the unique values to measure and vc.values are numeric counts.
    - For meaningful results, vc.index should be coercible to strings (or already strings) so pandas .str.len returns lengths.

Postconditions:
    - The result is a dict that always contains the five keys: "max_length", "mean_length", "median_length", "min_length", "length_histogram".
    - When vc is non-empty and index values yield finite lengths, max_length and min_length are finite numbers and satisfy max_length >= min_length.
    - length_histogram.index contains the distinct observed lengths and length_histogram.values sum to the sum of vc.values.

## Side Effects:
    - None. The function performs in-memory computations with pandas and numpy only; it does not perform I/O, mutate global state, or call external services.

## Control Flow:
flowchart TD
    Start[Start: receive vc (pd.Series)] --> Validate{vc empty?}
    Validate -- Yes --> EmptyError[Subsequent np.max / np.min or weighted_median will raise ValueError/IndexError]
    Validate -- No --> BuildSeries[series = Series(vc.index, index=vc)]
    BuildSeries --> ComputeLen[length = series.str.len()  (index=counts, values=lengths)]
    ComputeLen --> MapCounts[pd.Series(length.index, index=length)]
    MapCounts --> Group[groupby(level=0).sum() => length_counts (length -> total count)]
    Group --> Sort[length_counts.sort_values(descending)]
    Sort --> ComputeStats[Compute max/min via np.max/np.min on histogram index;
    mean via np.average(index, weights=values);
    median via weighted_median(index.values, weights=values)]
    ComputeStats --> Return[Return summary dict]
    style Start fill:#f9f,stroke:#333,stroke-width:1px

## Examples:

Example 1 — typical use and expected numeric outputs:
    vc = pandas.Series([10, 5, 2], index=["alpha", "bb", "see"])
    # Interpretations:
    #   "alpha" length = 5, count = 10
    #   "bb"    length = 2, count = 5
    #   "see"   length = 3, count = 2
    # length histogram (length -> total count):
    #   5 -> 10
    #   2 -> 5
    #   3 -> 2
    # mean_length = (5*10 + 2*5 + 3*2) / (10 + 5 + 2) = 66 / 17 ≈ 3.8823529411764706
    # median_length (per weighted_median implementation):
    #   weights = [10,5,2], total = 17, largest single weight 10 > 8.5 => median = corresponding data value 5
    # max_length = 5, min_length = 2
    # The returned dict:
    # {
    #   "max_length": 5,
    #   "mean_length": 3.8823529411764706,
    #   "median_length": 5,
    #   "min_length": 2,
    #   "length_histogram": pandas.Series([10,5,2], index=[5,2,3]).sort_values(ascending=False)
    # }

Example 2 — defensive pattern for empty or invalid input:
    if vc.empty:
        # Decide and document policy at caller level:
        # Option A: skip and set NaN/defaults
        summary = {
            "max_length": float("nan"),
            "mean_length": float("nan"),
            "median_length": float("nan"),
            "min_length": float("nan"),
            "length_histogram": pandas.Series(dtype=float),
        }
    else:
        summary = length_summary_vc(vc)

Implementation caveats:
    - The weighted_median helper in this codebase sorts data and weights independently before computing the midpoint and selecting the median; as a result, its behavior differs from canonical weighted-median implementations that sort data and carry weights along with their corresponding data points. The function here follows that helper exactly (so callers should not assume a canonical weighted median unless the helper is changed).
    - If vc.index contains non-string objects, pandas' .str.len may yield NaN; such NaNs will affect aggregation and may cause reduction calls to fail.

## `src.ydata_profiling.model.pandas.describe_categorical_pandas.pandas_describe_categorical_1d` · *function*

*No documentation generated.*

