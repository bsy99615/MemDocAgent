# `czech.py`

## `sumy.nlp.stemmers.czech.stem_word` · *function*

## Summary:
Normalize and stem a single Czech word token: decode bytes to text, validate token shape, lower and strip common Czech inflectional and derivational endings (optionally more aggressively), and then restore the original capitalization form.

## Description:
This function is the per-token entry point for the Czech stemming rules in this module. It performs lightweight input normalization, guards non-word tokens and mixed-case tokens, applies a sequence of suffix-removal helpers, and finally restores the original word's capitalization.

Known callers and usage context:
- Called by higher-level Czech stemming pipelines that iterate tokens and produce stems for indexing, search, or linguistic analysis. Typical callers call this once per token after tokenization and prior to indexing.
- Also usable directly by external code that needs to stem a single Czech token (for example, unit tests, text preprocessing utilities, or token-level analyzers).

Responsibility boundary (why this is a separate function):
- Encapsulates input decoding and validation, the high-level orchestration of the ordered suffix-removal steps, and capitalization restoration. Lower-level language-specific rules are delegated to helper functions (_remove_case, _remove_possessives, _remove_comparative, _remove_diminutive, _remove_augmentative, _remove_derivational and the palatalizer they call). This keeps per-word orchestration separate from the detailed suffix/palatalization logic and makes the pipeline easier to test.

## Args:
    word (unicode or bytes):
        - The token to be stemmed.
        - If it is the module's unicode/text type (the variable named `unicode` imported from _compat), it is used as-is.
        - If it is not an instance of that unicode type, the function calls word.decode("utf-8") to convert it to text. Therefore bytes containing a UTF-8 encoded Czech word are supported.
        - Caller responsibility: prefer passing already-decoded text (unicode/str) to avoid decode errors.
    aggressive (bool, optional): default False
        - When False (default), only basic normalization is applied: case removal and possessive removal.
        - When True, additional and more aggressive suffix-removal passes are performed in this order: comparative, diminutive, augmentative, derivational (each implemented by a helper function). Use True when you want a smaller/more aggressive stem at the cost of more aggressive conflation.

Interdependencies:
    - The `aggressive` flag only affects additional stripping steps after the basic normalization (it does not change input decoding, pattern matching, or mixed-case checking).

## Returns:
    unicode (str): the stemmed token as text (the module's unicode/text type).
    - Possible return behaviors:
        - If the input is bytes, the return is the stem of the decoded UTF-8 text.
        - If WORD_PATTERN.match(word) returns False (word does not match the module's word-regex), the input is returned unchanged (after decoding if necessary).
        - If the token has mixed case (neither all-lower, titlecase, nor all-upper), a warning is emitted and the original token (decoded to text) is returned unchanged.
        - Otherwise, a lowercase candidate stem is computed by:
            1. lowercasing the token,
            2. applying _remove_case,
            3. applying _remove_possessives,
            4. if aggressive is True, applying _remove_comparative, _remove_diminutive, _remove_augmentative, and _remove_derivational in that order.
        - After deriving the stem, the original capitalization form is restored:
            - If the original token was all-uppercase: return stem.upper()
            - Else if the original token was titlecase (istitle() True): return stem.title()
            - Else: return the lowercase stem unchanged.
    - Edge-case returns:
        - Empty string -> returns empty string (after the decode step, if any).
        - If the WORD_PATTERN gate fails or mixed-case gate triggers, the (decoded) original is returned without stemming.
        - The returned string is the module's text type (unicode/str) — callers can expect a text object, not raw bytes.

## Raises:
    - AttributeError: If `word` is not an instance of the module's unicode type and does not implement a .decode method, the code will attempt word.decode("utf-8") and Python will raise AttributeError.
    - UnicodeDecodeError: If `word` is bytes but contain invalid UTF-8 sequences, word.decode("utf-8") will raise UnicodeDecodeError.
    - TypeError or other implicit errors from helpers: helper functions (_remove_case, _remove_possessives, etc.) assume string-like input and may raise TypeError or other builtin exceptions if they receive unexpected types. These are not explicitly raised by stem_word but can propagate if non-string values pass earlier checks.

## Constraints:
Preconditions:
    - Prefer passing a text string (the module's unicode/str type). If passing bytes, they must be UTF-8 encoded.
    - The function expects a single token (no surrounding whitespace/punctuation) for meaningful stems; callers should perform tokenization and basic normalization (e.g., trimming) before calling.
    - The module-level WORD_PATTERN variable must be defined (a compiled regex) to correctly gate which tokens are considered words; if it rejects a token, no stemming occurs.

Postconditions:
    - The return value is a unicode/text string (module's unicode type).
    - If stemming rules matched, the returned string will be the input with zero or more suffixes removed/normalized; otherwise it may be identical to the decoded input.
    - No external state is modified by the function beyond emitting a warning for mixed-case tokens.

## Side Effects:
    - Emits a warnings.warn call when a token contains mixed case (neither .islower(), .istitle(), nor .isupper()); this is a soft diagnostic and does not raise an exception.
    - No I/O is performed. The function does not write files, access the network, or mutate global data structures (aside from the standard warnings machinery).

## Control Flow:
flowchart TD
    Start([start]) --> IsUnicode{isinstance(word, unicode)?}
    IsUnicode -- yes --> TextWord[use word as text]
    IsUnicode -- no --> DecodeAttempt[call word.decode("utf-8")]
    DecodeAttempt --> TextWord
    TextWord --> PatternCheck{WORD_PATTERN.match(text)?}
    PatternCheck -- no --> ReturnOriginalDecoded[return text]
    PatternCheck -- yes --> CaseCheck{text.islower() or text.istitle() or text.isupper()?}
    CaseCheck -- no --> WarnAndReturn[warn("skipping word with mixed case: " + text) / return text]
    CaseCheck -- yes --> Lower[stem = text.lower()]
    Lower --> RemoveCase[_remove_case(stem)]
    RemoveCase --> RemovePossessives[_remove_possessives(stem)]
    RemovePossessives --> AggressiveCheck{aggressive?}
    AggressiveCheck -- yes --> Comp[_remove_comparative(stem)]
    Comp --> Dim[_remove_diminutive(stem)]
    Dim --> Aug[_remove_augmentative(stem)]
    Aug --> Deriv[_remove_derivational(stem)]
    AggressiveCheck -- no --> Deriv
    Deriv --> RestoreCase{original was isupper? istitle?}
    RestoreCase -- isupper --> ReturnUpper[return stem.upper()]
    RestoreCase -- istitle --> ReturnTitle[return stem.title()]
    RestoreCase -- else --> ReturnLower[return stem]

## Examples:
- Basic (non-aggressive) usage:
    from sumy.nlp.stemmers.czech import stem_word
    # assume token is text
    stem = stem_word("Přátelům")          # returns "přátel" (then titlecased -> "Přátel")
    stem = stem_word("PŘÁTELŮM")         # returns "PŘÁTEL" (uppercase restored)

- Byte input (UTF-8):
    stem = stem_word(b"p\u0159atel\u016fm")  # bytes containing UTF-8; decode to text and stem -> "přátelům" -> "přátel"

- Aggressive mode:
    # Aggressive applies more suffix removals; results depend on helper rules (comparative, diminutive, augmentative, derivational).
    stem = stem_word("krásnějšími", aggressive=True)  # applies comparative removal and palatalization helpers to yield a shorter root

- Non-word or mixed-case behavior:
    stem = stem_word("1234")                 # if WORD_PATTERN does not match digits-only token -> returns "1234" unchanged
    stem = stem_word("MiXeDcase")            # emits a warning and returns "MiXeDcase" unchanged

- Error handling:
    try:
        stem_word(None)        # None is not unicode and has no .decode; AttributeError raised
    except AttributeError:
        # normalize input to a text type before calling
        handle_invalid_input()

## `sumy.nlp.stemmers.czech._remove_case` · *function*

## Summary:
Remove Czech grammatical case endings from a single token by applying ordered suffix-stripping rules and language-specific palatalization where required, returning the candidate stem.

## Description:
This function is a focused helper in the Czech stemmer: given one token it attempts to strip common Czech case (declensional) suffixes in a sequence of length-guarded checks and, when appropriate, delegates to the palatalization normalizer to produce the final stem form.

Known callers:
- The internal Czech stemming pipeline in the same module (other stemming functions) invoke this during morphological normalization when trying to remove case endings before further suffix stripping or returning the stem. Callers typically call this after tokenization and lowercasing/normalization, as part of the per-word stemming sequence.

Why this is a separate function:
- The logic encodes a compact ordered set of language-specific endings and palatalization decisions. Extracting it isolates these case-removal rules from the rest of the stemmer, makes control flow easier to follow and test, and centralizes where palatalization is triggered.

## Args:
    word (str): A single token (expected Unicode/str) to be stemmed for case removal.
        - Allowed values: any Python str (including empty string).
        - Interdependencies: None between parameters (single-argument function).
        - Caller expectations: the token should already be tokenized and reasonably normalized (e.g., lowercased) by the caller; punctuation or non-word characters may produce unexpected stems.

## Returns:
    str: A candidate stem with common Czech case endings removed where matched.
    - Possible return behaviors:
        - If the word length is greater than 7 and it ends with "atech", the final 5 characters ("atech") are removed.
        - If length > 6 and the word ends with "ětem", the function removes three characters and then applies palatalization to the shorter form (delegates to _palatalize(word[:-3])).
        - If length > 6 and ends with "atům", the final 4 characters are removed.
        - If length > 5 and the last 3 characters are in the first 3-char palatalizable list (e.g., "ech","ich","ích","ého","ěmi","emi","ému","ete","eti","iho","ího","ími","imu"), the function removes the last 2 characters and then applies palatalization to that result (delegates to _palatalize(word[:-2])).
        - If length > 5 and the last 3 characters are in the non-palatalizing 3-char list (e.g., "ách","ata","aty","ých","ama","ami","ové","ovi","ými"), the final 3 characters are removed.
        - If length > 4 and the word ends with "em", the function removes the final character from the word[:-1] slice and applies palatalization to that slice (delegates to _palatalize(word[:-1])).
        - If length > 4 and the final 2 characters are in ("es", "ém", "ím"), the function removes the final 2 characters and applies palatalization to the result (delegates to _palatalize(word[:-2])).
        - If length > 4 and the final 2 characters are in ("ům", "at", "ám", "os", "us", "ým", "mi", "ou"), the final 2 characters are removed.
        - If length > 3 and the final single character is in "eiíě", the function applies palatalization to the whole word (delegates to _palatalize(word)).
        - If length > 3 and the final single character is in "uyůaoáéý", the final character is removed.
        - If none of the above patterns are matched, the original word is returned unchanged.
    - Edge cases:
        - Empty string returns empty string (no matches, function falls through to return word).
        - Short strings (length <= 3) are frequently returned unchanged because most guarded rules require length > 3 or more.
        - Where palatalization is delegated, the returned value reflects _palatalize behavior (see _palatalize documentation): it may replace suffixes (like "ci" -> "k") or drop the last character when no palatalizing pattern matches.

## Raises:
    - TypeError: Not explicitly raised in the function, but operations (len(), slicing, membership tests, endswith()) assume a str-like input. Passing a non-string (e.g., None or an int) will typically raise a TypeError before or during execution.
    - No other exceptions are explicitly raised by this function.

## Constraints:
    Preconditions:
    - Input must support string operations (len, slicing, endswith, indexing). Practically: pass a Python str/unicode.
    - Token should be already tokenized and normalized by caller (no surrounding punctuation) for meaningful stems.

    Postconditions:
    - The returned value is a str and its length is <= len(word).
    - If a case suffix matched, the returned value is the original with that suffix removed or replaced according to palatalization rules.
    - No global state or external resources are modified.

## Side Effects:
    - None. The function performs pure string transformations and delegates to the pure helper _palatalize when needed. No I/O, no global mutations, no network or database calls.

## Control Flow:
flowchart TD
    Start([start]) --> CheckA{len(word) > 7 and endswith "atech"?}
    CheckA -- yes --> A[Return word[:-5]]
    CheckA -- no --> CheckB{len(word) > 6?}
    CheckB -- yes --> B1{endswith "ětem"?} 
    B1 -- yes --> B1a[Return _palatalize(word[:-3])]
    B1 -- no --> B2{endswith "atům"?}
    B2 -- yes --> B2a[Return word[:-4]]
    B2 -- no --> CheckC{len(word) > 5?}
    CheckB -- no --> CheckC
    CheckC -- yes --> C1{word[-3:] in palatalize-3-list?}
    C1 -- yes --> C1a[Return _palatalize(word[:-2])]
    C1 -- no --> C2{word[-3:] in remove-3-list?}
    C2 -- yes --> C2a[Return word[:-3]]
    C2 -- no --> CheckD{len(word) > 4?}
    CheckC -- no --> CheckD
    CheckD -- yes --> D1{endswith "em"?}
    D1 -- yes --> D1a[Return _palatalize(word[:-1])]
    D1 -- no --> D2{word[-2:] in ("es","ém","ím")?}
    D2 -- yes --> D2a[Return _palatalize(word[:-2])]
    D2 -- no --> D3{word[-2:] in ("ům","at","ám","os","us","ým","mi","ou")?}
    D3 -- yes --> D3a[Return word[:-2]]
    D3 -- no --> CheckE{len(word) > 3?}
    CheckD -- no --> CheckE
    CheckE -- yes --> E1{last char in "eiíě"?}
    E1 -- yes --> E1a[Return _palatalize(word)]
    E1 -- no --> E2{last char in "uyůaoáéý"?}
    E2 -- yes --> E2a[Return word[:-1]]
    E2 -- no --> EndReturn[Return word]
    CheckE -- no --> EndReturn

## Examples:
- Basic removals:
    - Input: "formatech" (len > 7, endswith "atech") -> returns "form" (final 5 characters removed).
    - Input: "přátelům" (len > 4, endswith "ům") -> returns "přátel" (final 2 characters removed).

- Cases involving palatalization (delegation to _palatalize):
    - Input: "luci" (len > 3, last char 'i' is in "eiíě"): the function calls _palatalize("luci") which returns "luk"; thus _remove_case("luci") -> "luk".
    - Input: "auto" (len > 3, last char 'o' in "uyůaoáéý"): returns "aut" (final character removed).

- Short or unchanged cases:
    - Input: "" -> returns "" (empty input unchanged).
    - Input: "kdo" (length == 3) -> returns "kdo" (no length-guarded rule applies).

- Error handling:
    - Caller should validate input type. Example:
        try:
            _remove_case(None)  # invalid type
        except TypeError:
            # handle invalid input: ensure token is a str before calling
            handle_invalid_token()

## `sumy.nlp.stemmers.czech._remove_possessives` · *function*

## Summary:
Removes Czech possessive suffixes from a token when appropriate: strips trailing "ov" or "ův" for sufficiently long words, and for words ending in "in" delegates to palatalization normalization on the stem (the word without the final 'n').

## Description:
This helper encapsulates a small, language-specific step of the Czech stemming pipeline: removal and normalization of common possessive suffixes. It is intended to be invoked by the Czech stemmer at the stage where morphological suffixes are stripped and stems are normalized.

Known callers and pipeline context:
- Called by the Czech stemming logic during the suffix-stripping / normalization stage of token stemming. Typical use: after tokenization and lowercasing, the stemmer inspects candidate suffixes and calls this function to remove or normalize possessive endings before applying other suffix-stripping rules.
- The function itself delegates palatalization handling to a separate helper when encountering "in" endings (it calls _palatalize(word[:-1])).

Why this is a separate function:
- Possessive removal is a narrowly-scoped, language-specific rule that the stemmer may apply at multiple points. Extracting it keeps the main stemming flow simple, centralizes the possessive-handling logic, and allows independent testing of possessive removal rules.

## Args:
    word (str): A Unicode/str token representing a single Czech word.
        - Allowed values: any str. The function expects a token that is already normalized for case and stripped of surrounding punctuation by the tokenizer/stemmer pipeline.
        - Interdependencies: None. The function only uses the provided string and does not consult external state.

## Returns:
    str: The resulting token after conditional possessive removal or normalization.
    - If len(word) <= 5: returns the original word unchanged.
    - If len(word) > 5 and the final two characters are "ov" or "ův": returns the word with those two characters removed (word[:-2]).
    - If len(word) > 5 and the word ends with "in": returns the result of calling _palatalize on the word with its final character removed (i.e., _palatalize(word[:-1])). This allows palatalization rules to convert stems like "...i" to their non-palatalized forms.
    - Otherwise (len(word) > 5 but none of the suffix conditions match): returns the original word unchanged.
    - Edge-case returns:
        - For non-string inputs, a TypeError will typically be raised implicitly by Python slicing/str operations.
        - The returned string's length is guaranteed to be less than or equal to the input's length.

## Raises:
    TypeError: Implicitly raised if the provided word does not support string operations (for example, passing None or an int). There are no explicit raise statements in the implementation.

## Constraints:
    Preconditions:
    - The caller should supply a str (Unicode) token that represents a single word (tokenization and punctuation removal should already have occurred).
    - The function does not perform case normalization or punctuation stripping; callers must perform any required normalization (lowercasing, trimming) before calling if consistency is required across the pipeline.
    - This function only attempts possessive removal for words strictly longer than 5 characters; shorter words are returned unchanged.

    Postconditions:
    - No external state is modified.
    - If a possessive suffix was matched, it will have been removed or transformed (via _palatalize) and the resulting string returned.
    - The returned value is a str whose length is <= len(word).

## Side Effects:
    - None. The function performs no I/O and does not mutate global state or call external services. It only returns a derived string.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckLen{len(word) > 5 ?}
    CheckLen -- No --> ReturnOriginal[Return original word]
    CheckLen -- Yes --> CheckOV{word[-2:] in ("ov","ův") ?}
    CheckOV -- Yes --> ReturnStripOV[Return word[:-2]]
    CheckOV -- No --> CheckIN{word.endswith("in") ?}
    CheckIN -- Yes --> ReturnPalatalize[Return _palatalize(word[:-1])]
    CheckIN -- No --> ReturnOriginal2[Return original word]

## Examples:
- Remove trailing "ov":
    - Input: "novakov" (len > 5, ends with "ov")
    - Output: "novak"  (returned value: word[:-2])

- Remove trailing "ův":
    - Input: "hradcův" (len > 5, ends with "ův")
    - Output: "hradc" (returned value: word[:-2])

- Handle trailing "in" by palatalization:
    - Given _palatalize("velkaluci") -> "velkaluk"
    - Input: "velkalucin" (len > 5, ends with "in")
    - Operation: call _palatalize("velkaluci") and return its result
    - Output: "velkaluk"

- No change for short words:
    - Input: "malin" (len == 5)
    - Output: "malin" (unchanged because len <= 5)

- No change for longer words without target suffixes:
    - Input: "program" (len > 5, but does not end with "ov","ův","in")
    - Output: "program" (unchanged)

- Error handling:
    - Calling with a non-string:
        try:
            _remove_possessives(None)
        except TypeError:
            # Caller must ensure input is a str-like token
            handle_invalid_input()

Notes for implementers:
- The length cutoff (> 5) is intentional to avoid over-stripping short tokens that are unlikely to be possessive forms.
- The function relies on an external helper _palatalize for the "in" case; ensure that helper is available and follows the expected contract (accepts a string and returns a normalized string).

## `sumy.nlp.stemmers.czech._remove_comparative` · *function*

## Summary:
If a Czech comparative-like suffix is present on a sufficiently long token, strip the suffix (by removing the final two characters) and return the palatalization-normalized stem; otherwise return the original token unchanged.

## Description:
This helper implements a single stemming rule: detect 3-character comparative endings "ejš" or "ějš" on tokens longer than five characters, remove the last two characters from the token, then pass the truncated token to the centralized palatalization normalizer (_palatalize) and return its result. It is used by the Czech stemming pipeline when candidate comparative forms are being normalized into stems.

Known callers:
- Internal Czech stemming routines in the same module that perform morphological normalization and suffix-stripping. Call sites typically invoke this function when a token has been identified as a candidate comparative and the stemmer needs to normalize palatalization effects after removing the comparative ending.

Why this is a separate function:
- It encapsulates a narrowly-scoped decision (length + specific suffix check) and the subsequent palatalization call. Keeping this behavior separate avoids duplicating the conditional and the palatalization-call pattern across the stemmer and centralizes the comparative-removal rule.

## Args:
    word (str): The input token to inspect and possibly transform.
        - Expected type: str (unicode). The function performs length checks and suffix slicing.
        - Accepted values: any object supporting len() and slicing (word[-3:], word[:-2]); however, non-str sliceable types (e.g., list) will be processed at the Python level but the function semantics assume string tokens. Callers should ensure the token is a str.
        - No default values.

## Returns:
    str: The resulting token after applying the rule, or the original token.
    - If both conditions are met:
        * len(word) > 5
        * word[-3:] is exactly "ejš" or "ějš"
      then the function returns the result of _palatalize(word[:-2]).
        - Note: word[:-2] removes the final two characters from the input before palatalization.
        - The exact returned string depends on _palatalize's logic (e.g., it may replace final sequences or drop the final character).
    - Otherwise, the function returns the original word object unchanged.
    - Return type: the same type returned by _palatalize when the rule triggers (normally str). If a non-str type was passed and supports slicing, the function returns whatever _palatalize returns for that type (but _palatalize is intended to operate on strings).

## Raises:
    - TypeError: May be raised implicitly by built-in operations if the provided argument does not support len() or slicing (for example, passing None or an integer). There are no explicit raise statements in the function.
    - Note: Passing a non-str object that supports slicing (for example, a list) will not raise here, but will likely produce semantically incorrect results; callers should validate input type before calling.

## Constraints:
    Preconditions:
    - The caller should pass a properly tokenized, str-like Czech word (preferably normalized to the expected case/whitespace by the pipeline).
    - The function assumes no leading/trailing punctuation; tokenization and cleanup are the caller's responsibility.

    Postconditions:
    - If the comparative rule matched, the returned value equals _palatalize(word[:-2]).
    - If the rule did not match, the returned value is the original word (identity).
    - No global state or external resources are modified.

## Side Effects:
    - None. The function performs only in-memory string operations and a call to _palatalize, which itself is pure string transformation. No I/O or global mutations occur.

## Control Flow:
flowchart TD
    Start --> LenCheck{len(word) > 5?}
    LenCheck -- No --> ReturnOriginal[Return word]
    LenCheck -- Yes --> SuffixCheck{word[-3:] in ("ejš","ějš")?}
    SuffixCheck -- No --> ReturnOriginal
    SuffixCheck -- Yes --> Truncate[Compute truncated = word[:-2]]
    Truncate --> Palatalize[Call _palatalize(truncated)]
    Palatalize --> ReturnPal[Return result of _palatalize]

## Examples:
- End-to-end example combining the truncation with known _palatalize behavior:
    - Input: "abcejš"
      - len("abcejš") == 6 (>5) and "abcejš"[-3:] == "ejš" → condition true
      - Truncated: "abcejš"[:-2] -> "abce"
      - _palatalize("abce") -> "abk" (because "ce" -> "k" per palatalization rules)
      - Output: "abk"

    - Input: "xyvějš"
      - len("xyvějš") == 6 and last 3 == "ějš" → condition true
      - Truncated: "xyvějš"[:-2] -> "xyvě"
      - _palatalize("xyvě") -> depends on ending of "xyvě"; if no palatalizing ending, _palatalize will drop last character -> e.g., "xyv"
      - Output: result produced by _palatalize("xyvě")

- Non-triggering examples:
    - Input: "kratší" (does not end with "ejš" or "ějš") -> returns "kratší" unchanged.
    - Input: "abcěš" (len <= 5) -> returns "abcěš" unchanged.

- Edge cases:
    - Input: "" (empty string) -> len == 0 -> returns "" unchanged.
    - Input: None -> len(None) raises TypeError; callers should validate the input type.
    - Input: a list like ['a','b','c','e','j','š'] supports slicing, but this function and _palatalize expect strings; passing such values may not raise here but will yield semantically incorrect results.

- Usage pattern with validation:
    try:
        token = ensure_str(token)   # caller-side helper to validate/normalize
        stem = _remove_comparative(token)
    except TypeError:
        # handle invalid input
        handle_invalid_token(token)

## `sumy.nlp.stemmers.czech._remove_diminutive` · *function*

## Summary:
Removes common Czech diminutive suffixes from a word, returning the shortened stem; applies palatalization normalization where language rules require.

## Description:
This function implements suffix-stripping rules specific to Czech diminutives. It inspects the end of the provided token and, when a known diminutive suffix is present and length preconditions are met, returns a shortened form of the token. Some removals require a follow-up palatalization normalization; in those cases the function delegates to the module's palatalization helper.

Known callers and context:
- Internal Czech stemming logic within the same module (the Czech stemmer pipeline) — invoked when performing morphological normalization/stemming of tokens and specifically when the pipeline reaches the diminutive-removal step.
- Typically called as part of a sequence of suffix-stripping steps (e.g., after lowercasing and token cleanup and before removing other derivational/inflectional suffixes).

Why this is a separate function:
- Diminutive removal is a focused, language-specific set of rules. Extracting it keeps the main stemming flow modular, improves readability, enables targeted testing, and centralizes suffix patterns and their preconditions.

## Args:
    word (str): Input token (expected to be a Python str / Unicode string) representing a Czech word.
        - Allowed values: any str. Empty string is accepted.
        - Not allowed / will error implicitly: non-string types (e.g., None, int), because slicing and suffix checks expect a str.
        - No other parameters.

## Returns:
    str: The token after diminutive removal (or the original token unchanged if no matching diminutive rule applies).
    - If the token ends with "oušek" and length > 7: returns word[:-5] (drops "oušek").
    - If length > 6 and the last 4 characters are in the first palatalizing group ("eček","éček","iček","íček","enek","ének","inek","ínek"): returns _palatalize(word[:-3]) (drops 3 chars then palatalizes).
    - If length > 6 and the last 4 characters are in the second palatalizing group ("áček","aček","oček","uček","anek","onek","unek","ánek"): returns _palatalize(word[:-4]) (drops 4 chars then palatalizes).
    - If length > 5 and last 3 are in ("ečk","éčk","ičk","íčk","enk","énk","ink","ínk"): returns _palatalize(word[:-3]).
    - If length > 5 and last 3 are in ("áčk","ačk","očk","učk","ank","onk","unk","átk","ánk","ušk"): returns word[:-3] (drops 3 chars without palatalization).
    - If length > 4 and last 2 are in ("ek","ék","ík","ik"): returns _palatalize(word[:-1]) (drops final char then palatalizes).
    - If length > 4 and last 2 are in ("ák","ak","ok","uk"): returns word[:-1] (drops final char without palatalization).
    - If length > 3 and final character is "k": returns word[:-1] (drops the final "k").
    - If none of the above conditions match, returns the original word unchanged.

Edge / special cases:
    - Empty string ("") -> returns "" (no matches).
    - Very short strings: strings shorter than the length thresholds will bypass corresponding rules and often return the original string.
    - Non-str inputs raise implicit TypeError when string operations are attempted.

## Raises:
    TypeError: Implicitly raised if `word` is not a string-like object that supports slicing, endswith, and indexing (for example, passing None or an int). The function does not explicitly raise any exceptions.

## Constraints:
Preconditions:
    - `word` must be a str/unicode object containing the token to analyze.
    - Preferably the token is pre-normalized (lowercased, stripped of surrounding punctuation) by the caller — this function does not perform case normalization or punctuation stripping.

Postconditions:
    - The returned value is a str whose length is less than or equal to the input `word`'s length.
    - If a diminutive suffix was detected and removed, the returned string reflects that removal; if palatalization was required by the matched suffix, the returned value is the result after passing the truncated token to the module's palatalization helper.
    - No global state is changed.

## Side Effects:
    - None. The function performs in-memory string operations only. It does not perform any I/O, network calls, or mutate external/global state.

## Control Flow:
flowchart TD
    Start[Start] --> L7{len(word) > 7?}
    L7 -- no --> L6{len(word) > 6?}
    L7 -- yes --> S1{word endswith "oušek"?}
    S1 -- yes --> R1[Return word[:-5]]
    S1 -- no --> L6
    L6 -- no --> L5{len(word) > 5?}
    L6 -- yes --> C4{word[-4:] in first palatalizing 4-char group?}
    C4 -- yes --> R2[Return _palatalize(word[:-3])]
    C4 -- no --> C5{word[-4:] in second 4-char group?}
    C5 -- yes --> R3[Return _palatalize(word[:-4])]
    C5 -- no --> L5
    L5 -- no --> L4{len(word) > 4?}
    L5 -- yes --> C6{word[-3:] in first 3-char palatalizing group?}
    C6 -- yes --> R4[Return _palatalize(word[:-3])]
    C6 -- no --> C7{word[-3:] in second 3-char non-palatalizing group?}
    C7 -- yes --> R5[Return word[:-3]]
    C7 -- no --> L4
    L4 -- no --> L3{len(word) > 3?}
    L4 -- yes --> C8{word[-2:] in 2-char palatalizing group ("ek","ék","ík","ik")?}
    C8 -- yes --> R6[Return _palatalize(word[:-1])]
    C8 -- no --> C9{word[-2:] in non-palatalizing 2-char group?}
    C9 -- yes --> R7[Return word[:-1]]
    C9 -- no --> L3
    L3 -- no --> EndNoMatch[Return original word]
    L3 -- yes --> C10{word[-1] == "k"?}
    C10 -- yes --> R8[Return word[:-1]]
    C10 -- no --> EndNoMatch

## Examples:
- Typical usage in a stemming pipeline:
    - _remove_diminutive("domeček")
      - Reasoning: "domeček" ends with "eček" and len > 6 -> function calls _palatalize("dome") -> palatalization yields "dom" -> final result "dom".
    - _remove_diminutive("karloušek")
      - Reasoning: ends with "oušek" and len > 7 -> returns "karl" (drops "oušek").
    - _remove_diminutive("malý")
      - Reasoning: no matching diminutive suffix -> returns "malý" unchanged.

- Error handling:
    try:
        _remove_diminutive(None)  # invalid type
    except TypeError:
        # The caller should ensure the token is a str/unicode before calling
        handle_invalid_input()

## `sumy.nlp.stemmers.czech._remove_augmentative` · *function*

## Summary:
Remove Czech augmentative suffixes from a token when present, returning a shortened or normalized stem; leaves the input unchanged if no augmentative rule applies.

## Description:
This helper encapsulates a small set of Czech augmentative-suffix stripping rules used by the Czech stemmer. It examines the end of the provided word and applies one of the following transformations (in order): remove the 4-character "ajzn" suffix; for 3-character suffixes "izn" or "isk", remove the final two characters and then apply palatalization normalization; remove the 2-character suffix "ák". If none of the rules match, the original word is returned unchanged.

Known callers:
- Internal Czech stemming logic in the same module (the module's morphological normalization / suffix-stripping pipeline). Call sites invoke this function when an augmentative suffix candidate has to be stripped as part of deriving a stem.

Why this logic is a separate function:
- Augmentative removal is a focused language-specific rule set that may be used in multiple places of the Czech stemmer. Extracting it isolates suffix-specific checks and keeps the main stemming flow concise and easier to test. It also centralizes the decision order and guarantees a deterministic priority between suffix rules.

## Args:
    word (str): The input token (expected to be a Unicode/str).
        - Allowed values: any str. The function performs length checks, suffix comparisons, and slicing.
        - Note: Passing non-string values (None, int, etc.) will generally raise a TypeError when string operations are attempted.
        - No other parameters or interdependencies.

## Returns:
    str: The resulting token after augmentative removal or normalization.
        - If len(word) > 6 and word.endswith("ajzn"): returns word[:-4] (drops the final 4 characters).
        - Else if len(word) > 5 and word[-3:] in ("izn", "isk"): returns _palatalize(word[:-2]) — the function drops the last 2 characters and delegates palatalization normalization to _palatalize (which applies Czech palatalization rules or drops the final character if no palatalizing pattern matches).
        - Else if len(word) > 4 and word.endswith("ák"): returns word[:-2] (drops the final 2 characters).
        - Else: returns the original word unchanged.
    Edge cases:
        - Very short words or words not matching the suffix tests are returned unchanged.
        - For empty string input (""), returns "".
        - If the "izn"/"isk" branch invokes _palatalize, the final output depends on _palatalize's rules (see _palatalize documentation); that may shorten the token further (for example by removing a final character if no palatalizing sequence matches).

## Raises:
    TypeError: Not raised explicitly but may occur implicitly if the provided word does not support string operations (e.g., calling endswith or slicing on None or an int). The function contains no explicit raise statements.

## Constraints:
    Preconditions:
        - Caller must pass a string-like token (str/unicode). The token should already be tokenized and normalized (e.g., trimmed of surrounding whitespace) by the upstream pipeline if desired.
    Postconditions:
        - The return value is a str.
        - The returned token is either identical to the input or shorter than the input.
        - No global state is modified.

## Side Effects:
    - None. The function performs pure string inspection and returns a new string. It performs no I/O, no global mutations, and no external service calls.

## Control Flow:
flowchart TD
    Start([Start]) --> C1{len(word) > 6 and word.endswith("ajzn")?}
    C1 -- yes --> R1[Return word[:-4]]
    C1 -- no --> C2{len(word) > 5 and word[-3:] in ("izn","isk")?}
    C2 -- yes --> R2[Return _palatalize(word[:-2])]
    C2 -- no --> C3{len(word) > 4 and word.endswith("ák")?}
    C3 -- yes --> R3[Return word[:-2]]
    C3 -- no --> R4[Return word (unchanged)]

## Examples:
- Augmentative "ajzn" removal:
    Input: "xyzajzn" (length 7, ends with "ajzn")
    Output: "xyz"
    Explanation: len>6 and endswith "ajzn" -> drop last 4 chars.

- "izn" branch (delegates to palatalization):
    Input: "autorizn"
    Intermediate: word[:-2] -> "autori"
    _palatalize("autori") -> "autor" (palatalize drops last char when no special palatalizing suffix matches)
    Output: "autor"
    Explanation: len>5 and last 3 chars "izn" matched, so the function removes two chars then runs palatalization normalization.

- "isk" branch (example):
    Input: "mimoriadisk" (ends with "isk", len>5)
    Intermediate: word[:-2] -> "mimoriadi"
    Assume _palatalize("mimoriadi") removes the final character (no palatalizing suffix) -> "mimoriad"
    Output: "mimoriad"

- "ák" removal:
    Input: "knihák" (length > 4, ends with "ák")
    Output: "knih"
    Explanation: len>4 and endswith "ák" -> drop last 2 chars.

- No rule applies (too short or no matching suffix):
    Input: "dom" (short, no matching suffix)
    Output: "dom" (unchanged)

- Error handling:
    Input: None
    Behavior: implicit TypeError raised when trying to evaluate len(None) or call endswith on None; callers should validate input types before calling.

Notes:
- Because the "izn"/"isk" branch calls _palatalize on word[:-2], the caller should consult _palatalize's behavior to understand the exact transformation in that branch (palatalization may replace character sequences like "ci"/"ce" with "k", "zi"/"ze" with "h", replace 3-character sequences like "čti"/"čtě" with "ck", "šti"/"ště" with "sk", or drop a final character when no palatalizing pattern matches).

## `sumy.nlp.stemmers.czech._remove_derivational` · *function*

## Summary:
Strips Czech derivational suffixes from a token to produce a shorter stem; when required, delegates palatalization-specific normalization to the palatalization helper.

## Description:
This helper implements the derivational-suffix removal stage of the Czech stemming pipeline. It checks the input token against an ordered set of length-gated suffix patterns (longest patterns first) and removes or transforms matching suffixes to produce a candidate stem. For several suffix classes the function invokes the palatalization helper to perform language-specific replacement on the truncated stem.

Known callers within the codebase and typical context:
- Other functions inside the same Czech stemmer module that implement the full stemming algorithm call this function as the derivational-suffix stripping step after shorter affix-removal stages (i.e., as part of a multi-step normalization/stemming pipeline).
- It is intended to be invoked on already-tokenized, normalized tokens (lowercased, without surrounding punctuation) when deriving stems for indexing or analysis.

Why this logic is factored into its own function:
- The mapping from derivational suffixes to stems is language-specific and sizable; isolating it keeps the overall stemmer implementation modular and testable.
- Delegating palatalization to a dedicated helper centralizes complex character-replacement rules and keeps suffix-matching logic straightforward.

## Args:
    word (str): Input token expected to be a Unicode/str representing a single Czech word.
        - Allowed values: any str. The function performs suffix checks and slicing; callers should pass strings.
        - Empty strings are accepted and handled (no exception).
        - No default value; positional single parameter.
        - Interdependencies: The function assumes the token has been pre-normalized by the caller (e.g., trimmed and lowercased if required). It does not perform trimming or case normalization.

## Returns:
    str: The token after derivational suffix removal (a candidate stem).
    - If a matching suffix pattern is found, returns a shorter token obtained by removing the suffix and, in some cases, applying palatalization normalization via _palatalize.
    - If no pattern matches, returns the original input token unchanged.
    - All possible outcomes:
        - Removal by fixed-length slicing (e.g., word[:-6], word[:-5], word[:-4], word[:-3], word[:-2], word[:-1]).
        - Return value produced by _palatalize on a truncated substring when patterns require palatalization-aware normalization.
        - Original token returned when no suffix conditions match.
    - Length guarantee: the returned string length is always less than or equal to the input length (never longer).

## Raises:
    TypeError: Implicitly raised if the provided `word` is not a string-like object that supports indexing/slicing and .endswith (for example, passing None or an int will typically raise a TypeError). The function contains no explicit raise statements.

## Constraints:
    Preconditions:
    - Caller must provide a str/unicode token. The function uses len(), slicing, membership tests, and endswith(); non-string objects will fail.
    - Token should be an individual word without adjacent punctuation if accurate stems are required; the function does not strip punctuation.
    - The function assumes UTF-8/Unicode strings so that accented Czech characters are compared correctly.

    Postconditions:
    - Returned token is a candidate stem derived by deterministic suffix rules described by the function.
    - No external state is modified; the function is pure with respect to program state.
    - If a palatalization helper is invoked, its documented transformations (replacement of palatalized endings) are applied to the truncated form before return.

## Side Effects:
    - None. The function performs no I/O and does not mutate global state or external services.

## Control Flow:
flowchart TD
    Start([Start]) --> L1{len(word) > 8?}
    L1 -- no --> L2{len(word) > 7?}
    L1 -- yes --> C1{endswith "obinec"?}
    C1 -- yes --> R1[Return word[:-6]]
    C1 -- no --> L2
    L2 -- no --> L3{len(word) > 6?}
    L2 -- yes --> C2{endswith "ionář"?}
    C2 -- yes --> R2[Return _palatalize(word[:-4])]
    C2 -- no --> C3{word[-5:] in ("ovisk","ovstv","ovišt","ovník")?}
    C3 -- yes --> R3[Return word[:-5]]
    C3 -- no --> L3
    L3 -- no --> L4{len(word) > 5?}
    L3 -- yes --> C4{word[-4:] in ("ásek","loun","nost","teln","ovec","ovík","ovtv","ovin","štin")?}
    C4 -- yes --> R4[Return word[:-4]]
    C4 -- no --> C5{word[-4:] in ("enic","inec","itel")?}
    C5 -- yes --> R5[Return _palatalize(word[:-3])]
    C5 -- no --> L4
    L4 -- no --> L5{len(word) > 4?}
    L4 -- yes --> C6{endswith "árn"?}
    C6 -- yes --> R6[Return word[:-3]]
    C6 -- no --> C7{word[-3:] in ("ěnk","ián","ist","isk","išt","itb","írn")?}
    C7 -- yes --> R7[Return _palatalize(word[:-2])]
    C7 -- no --> C8{word[-3:] in ("och","ost","ovn","oun","out","ouš","ušk","kyn","čan","kář","néř","ník","ctv","stv")?}
    C8 -- yes --> R8[Return word[:-3]]
    C8 -- no --> L5
    L5 -- no --> L6{len(word) > 3 and word[-1] in "cčklnt"?}
    L5 -- yes --> C9{word[-2:] in ("áč","ač","án","an","ář","as")?}
    C9 -- yes --> R9[Return word[:-2]]
    C9 -- no --> C10{word[-2:] in ("ec","en","ěn","éř","íř","ic","in","ín","it","iv")?}
    C10 -- yes --> R10[Return _palatalize(word[:-1])]
    C10 -- no --> C11{word[-2:] in ("ob","ot","ov","oň","ul","yn","čk","čn","dl","nk","tv","tk","vk")?}
    C11 -- yes --> R11[Return word[:-2]]
    C11 -- no --> L6
    L6 -- yes --> R12[Return word[:-1]]
    L6 -- no --> R13[Return word (unchanged)]

## Examples:
- Typical usage (illustrative, demonstrates suffix removal and palatalization delegation):
    - Input: "spisovatelnost"
      - Matching branch: suffix "nost" (len > 6 branch)
      - Output: "spisovatel" (returned by removing last 4 chars)
    - Input: "elektronický" (hypothetical ending matched by two-letter pattern "ický" is not in table; no match)
      - Output: original token "elektronický" (unchanged)
    - Input: "matkyni" (example where palatalization may apply depending on matched suffix)
      - If a suffix match triggers _palatalize on a truncated token, the returned value will be the truncated token with palatalization rules applied (see _palatalize for specifics).
- Edge cases:
    - Empty string "" -> returned unchanged "".
    - Short tokens:
        - "k" -> len <= 3, no suffix match -> returns "k".
        - "most" -> may match a 3- or 4-letter suffix depending on content; otherwise returned unchanged or shortened according to matched rule.
- Error handling:
    - Passing None or an int will typically raise a TypeError from Python built-ins (len(), slicing, or .endswith). Callers should validate input types before calling.

## `sumy.nlp.stemmers.czech._palatalize` · *function*

## Summary:
Transforms Czech palatalized word endings into their non-palatalized stem forms by applying a small set of language-specific suffix replacement rules; otherwise removes the final character.

## Description:
This helper encapsulates Czech palatalization rules used during stemming. It detects specific palatalized suffixes and returns the corresponding non-palatalized form:
- If the word ends with the 2-character palatalizing sequences "ci", "ce", "či", or "če", these two characters are replaced by "k".
- If the word ends with "zi", "ze", "ži", or "že", they are replaced by "h".
- If the word ends with the 3-character sequences "čtě", "čti", or "čtí", these three characters are replaced by "ck".
- If the word ends with "ště", "šti", or "ští", these three characters are replaced by "sk".
- If none of the above patterns match, the last character of the word is dropped.

Known callers:
- Internal Czech stemming logic (within the same module) that performs morphological normalization and suffix-stripping will call this function at the point where palatalization-specific normalization is required. Call sites typically invoke this after stripping or detecting candidate suffixes and before returning a final stem.

Why this is a separate function:
- Palatalization is a narrowly-scoped, language-specific transformation applied in multiple places in the Czech stemmer. Extracting it isolates the rule-set, makes the main stemming flow simpler and easier to test, and centralizes maintenance of palatalization rules.

## Args:
    word (str): Input token (expected to be a Unicode/str) representing a Czech word or token. The function performs suffix inspection and slicing on this value.
    - Allowed values: any str. Empty strings are accepted; non-string inputs will typically raise a TypeError when operations incompatible with str are attempted.
    - Interdependencies: None. The function does not modify external state and only uses the provided word.

## Returns:
    str: The transformed token representing the word after palatalization normalization.
    - If a 2-character palatalizing suffix is matched ("ci","ce","či","če"), returns word[:-2] + "k".
    - If a 2-character palatalizing suffix is matched ("zi","ze","ži","že"), returns word[:-2] + "h".
    - If a 3-character palatalizing suffix is matched ("čtě","čti","čtí"), returns word[:-3] + "ck".
    - If a 3-character palatalizing suffix is matched ("ště","šti","ští"), returns word[:-3] + "sk".
    - If no rule matches, returns word with its last character removed (word[:-1]).
    - Edge-case outputs:
        - For empty input (""), returns "".
        - For single-character input (e.g., "a"), returns "" (since word[:-1] yields "").

## Raises:
    TypeError: Raised implicitly if the provided word does not support slicing and string concatenation operations (for example, passing None or an int). The function contains no explicit raise statements.

## Constraints:
    Preconditions:
    - The caller should pass a string-like token (str/unicode). The function does not trim whitespace or normalize case; callers should pre-normalize (strip, lower) if required by the stemming pipeline.
    - The word is assumed to be already tokenized and not contain surrounding punctuation (the stemmer pipeline typically ensures this).

    Postconditions:
    - The returned value is a str whose length is less than or equal to the input word's length.
    - If a palatalizing suffix was matched, that suffix will be replaced by the corresponding non-palatalized sequence ("k","h","ck","sk") as described above.
    - No external state is modified.

## Side Effects:
    - None. The function does not perform I/O, does not modify global variables, and does not call external services.

## Control Flow:
flowchart TD
    A[Start] --> B{word[-2:] in ("ci","ce","či","če")?}
    B -- yes --> C[Return word[:-2] + "k"]
    B -- no --> D{word[-2:] in ("zi","ze","ži","že")?}
    D -- yes --> E[Return word[:-2] + "h"]
    D -- no --> F{word[-3:] in ("čtě","čti","čtí")?}
    F -- yes --> G[Return word[:-3] + "ck"]
    F -- no --> H{word[-3:] in ("ště","šti","ští")?}
    H -- yes --> I[Return word[:-3] + "sk"]
    H -- no --> J[Return word[:-1]]

## Examples:
- Typical usage:
    - _palatalize("luci") -> "luk"
      Explanation: ends with "ci" -> drop last 2 chars ("lu") + "k" -> "luk"
    - _palatalize("muzi") -> "muh"
      Explanation: ends with "zi" -> drop last 2 chars ("mu") + "h" -> "muh"
    - _palatalize("pečti") -> "peck"
      Explanation: ends with "čti" -> drop last 3 chars ("pe") + "ck" -> "peck"
    - _palatalize("místi") -> "misk"
      Explanation: ends with "šti" -> drop last 3 chars + "sk"
    - _palatalize("auto") -> "aut"
      Explanation: no palatalizing suffix matched -> drop final character

- Edge cases:
    - _palatalize("") -> ""
    - _palatalize("a") -> ""

- Error handling example:
    try:
        _palatalize(None)  # invalid input type
    except TypeError:
        # Caller should ensure a str-like token is passed
        handle_invalid_input()

