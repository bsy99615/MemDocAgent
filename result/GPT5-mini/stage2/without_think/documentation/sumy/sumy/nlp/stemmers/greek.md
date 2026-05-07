# `greek.py`

## `sumy.nlp.stemmers.greek.stem_word` · *function*

## Summary:
Returns a lowercase Greek stem for a single token by trying multiple part-of-speech tags with the external greek_stemmer and selecting the shortest valid stem; if no valid stem is found returns the original word lowercased.

## Description:
This function wraps the external greek_stemmer.stem_word API, performing:
- A lazy import of the external stemmer and raising a clear ValueError if the dependency is missing.
- An early return for short tokens (length < 4) to avoid unnecessary stemming.
- Iteration over a module-level tag list (_TOTAL_TAGS) and collection of candidate stems.
- Filtering candidate stems to those that are non-empty and whose last character (uppercased) appears in the module-level consonant set (_CONSONANTS).
- Selection of the shortest candidate (by length) and returning it lowercased; if no candidates survive the filter, returns the original word lowercased.

Known callers within the codebase:
- No direct callers were found in the provided context. Conceptually used by Greek-language token normalization or indexing pipelines where stable stems are required.

Why this logic is a separate function:
- Encapsulates dependency handling and error message for missing optional package.
- Centralizes tag-iteration, candidate filtering, and selection behavior for reuse and easier testing.
- Keeps the overall stemming pipeline codebase-agnostic to the particulars of the greek_stemmer API.

## Args:
    word (str): The token to stem.
        - Type: str (function expects typical string behavior; objects with len() and lower() may also work).
        - Constraint: length is checked with len(word); lowercasing is performed via word.lower().
        - Semantic: Intended to be a single token (no internal whitespace). Input is not normalized beyond lowercasing.

Notes on interdependencies:
    - _TOTAL_TAGS (iterable): Must be an iterable of tag values accepted by greek_stemmer.stem_word as the second argument. Example (illustrative): ['NOUN', 'VERB', 'ADJ', 'ADV'].
    - _CONSONANTS (collection): Must be a collection of single-character strings representing uppercase consonant letters so that stemmed[-1].upper() in _CONSONANTS performs the intended test. Example (illustrative): {'Β','Γ','Δ','Ζ','Θ','Κ','Λ','Μ','Ν','Ξ','Π','Ρ','Σ','Τ','Φ','Χ','Ψ'}.

## Returns:
    str: Always returns a lowercase string. Possible outcomes:
        - If len(word) < 4: returns word.lower() immediately.
        - Otherwise, returns the shortest string among candidate stems (each candidate lowercased at final return) that:
            * is truthy (not None or empty)
            * has its last character uppercased present in _CONSONANTS
          The final returned value is candidate.lower().
        - If no candidate passes the filters, returns word.lower().

    Determinism and tie-breaking:
        - Candidate stems are collected in a set to deduplicate; since sets are unordered, when multiple candidates have equal shortest length the chosen element is implementation-dependent (non-deterministic across runs/Python implementations).
        - The min(..., key=len) call selects by length only; ties are resolved by the iteration order of the set (not stable).

## Raises:
    ValueError: Raised if the optional dependency import fails. Exact message:
        "Greek stemmer requires greek_stemmer. Please, install it by command 'pip install greek-stemmer-pos'."

    Exceptions that may propagate:
        - TypeError or AttributeError can propagate if `word` does not support len() or lower().
        - Exceptions raised by greek_stemmer.stem_word other than TypeError or ValueError may propagate (the function explicitly catches TypeError and ValueError raised by the external call for each tag and ignores those for that tag).

    Exceptions swallowed (per-tag):
        - Within the per-tag loop, TypeError and ValueError raised by gr_stemmer.stem_word are caught and ignored (the function continues with the next tag).

## Constraints:
    Preconditions:
        - _TOTAL_TAGS and _CONSONANTS must be defined in the module namespace before calling this function.
        - The external package 'greek_stemmer' should be installable; otherwise the function raises the specified ValueError.
        - Input must be compatible with len() and lower().

    Postconditions:
        - The function returns a str that is lowercased.
        - No module-level variables are modified.

## Side Effects:
    - No explicit I/O (no file or network operations) occur.
    - Importing greek_stemmer will load that module in sys.modules (standard Python import side effect).
    - No global mutable state is changed by this function.

## Control Flow:
flowchart TD
    A[Start] --> B[Try: from greek_stemmer import stemmer as gr_stemmer]
    B --> |ImportError| C[Raise ValueError with installation message]
    B --> |Success| D[stem_candidates = empty set]
    D --> E{len(word) < 4?}
    E --> |Yes| F[Return word.lower()]
    E --> |No| G[For each tag in _TOTAL_TAGS]
    G --> H[Try: stemmed = gr_stemmer.stem_word(word.lower(), tag)]
    H --> |raises TypeError or ValueError| I[Ignore this tag, continue loop]
    H --> |raises other Exception| J[Exception propagates out of function]
    H --> |returns value| K{stemmed truthy AND stemmed[-1].upper() in _CONSONANTS?}
    K --> |Yes| L[Add stemmed to stem_candidates set]
    K --> |No| M[Ignore this stem, continue]
    G --> N[After loop: choose candidate = min(stem_candidates or [word], key=len)]
    N --> O[Return candidate.lower()]

## Examples:
- Dependency missing:
    Example usage:
        try:
            stem = stem_word("Καλημέρα")
        except ValueError as exc:
            # Handle missing dependency: notify user or log instructing to pip install
            print(str(exc))

    Behavior: raises ValueError with the precise installation instruction message.

- Short token (bypasses stemmer):
    Input: "για"  (len=3)
    Output: "για"  (lowercased). No calls to greek_stemmer are made.

- Typical use (with illustrative module constants and expected behavior):
    Suppose:
        _TOTAL_TAGS = ['NOUN','VERB','ADJ']
        _CONSONANTS = {'Β','Γ','Δ','Ζ','Θ','Κ','Λ','Μ','Ν','Ξ','Π','Ρ','Σ','Τ','Φ','Χ','Ψ'}
    Call: stem_word("Αγαπημένος")
    Steps:
        - Lowercase token -> "αγαπημένος"
        - For each tag, call gr_stemmer.stem_word("αγαπημένος", tag)
        - Collect returned stems that are non-empty and whose last letter uppercased is in _CONSONANTS
        - If candidates = {"αγαπημ","αγαπημν"}, min by length selects "αγαπημ"
        - Return "αγαπημ" (lowercased)

- Error propagation example:
    If gr_stemmer.stem_word raises RuntimeError for a specific tag, that RuntimeError will propagate out of stem_word (it is not caught).

Implementation notes for reproduction:
    - Use a local import inside the function and raise the exact ValueError message on ImportError to match behavior.
    - Use a set for stem_candidates to deduplicate stems.
    - For each tag, call gr_stemmer.stem_word(word.lower(), tag). If the returned value is truthy and stemmed[-1].upper() in _CONSONANTS, add it to the set.
    - Ignore (catch) TypeError and ValueError raised by gr_stemmer.stem_word for robustness against incompatible tags or unexpected returns.
    - Finally, return min(stem_candidates or [word], key=len).lower().

