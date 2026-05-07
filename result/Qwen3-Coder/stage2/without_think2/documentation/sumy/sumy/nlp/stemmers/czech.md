# `czech.py`

## `sumy.nlp.stemmers.czech.stem_word` · *function*

## Summary:
Stems Czech words by removing morphological affixes and normalizing capitalization according to linguistic rules.

## Description:
Performs Czech word stemming by applying a series of morphological transformations to reduce words to their base forms. The function handles case endings, possessives, and optional aggressive stemming transformations including comparative, diminutive, augmentative, and derivational suffix removal. It preserves proper capitalization patterns based on the original word's case.

This logic is extracted into its own function to encapsulate the entire Czech stemming pipeline, separating the core stemming algorithm from the specific morphological processing steps. This modular approach enables easier testing, maintenance, and extension of the Czech stemmer functionality.

## Args:
    word (str): The Czech word to stem. Must be a string that can be decoded as UTF-8.
    aggressive (bool): When True, applies additional aggressive stemming transformations including comparative, diminutive, augmentative, and derivational suffix removal. Defaults to False.

## Returns:
    str: The stemmed version of the input word. Returns the original word unchanged if it doesn't match the WORD_PATTERN regex or contains mixed case.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input word must be a string or bytes object that can be decoded as UTF-8
        - Input word must match the WORD_PATTERN regex to undergo stemming
        - Input word must not contain mixed case (combination of upper and lowercase letters)
    Postconditions:
        - Output word is normalized according to Czech morphological rules
        - Capitalization is preserved according to the original word's case pattern
        - If aggressive=True, additional morphological transformations are applied

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start stem_word] --> B{isinstance(word, unicode)?}
    B -- No --> C[word = word.decode("utf-8")]
    B -- Yes --> D[Continue]
    D --> E{WORD_PATTERN.match(word)?}
    E -- No --> F[Return word]
    E -- Yes --> G{not word.islower() AND not word.istitle() AND not word.isupper()?}
    G -- Yes --> H[warn("skipping word with mixed case: " + word)]
    H --> I[Return word]
    G -- No --> J[stem = word.lower()]
    J --> K[_remove_case(stem)]
    K --> L[_remove_possessives(L)]
    L --> M{aggressive?}
    M -- Yes --> N[_remove_comparative(L)]
    N --> O[_remove_diminutive(N)]
    O --> P[_remove_augmentative(O)]
    P --> Q[_remove_derivational(P)]
    M -- No --> R[L]
    R --> S{word.isupper()?}
    S -- Yes --> T[Return stem.upper()]
    S -- No --> U{word.istitle()?}
    U -- Yes --> V[Return stem.title()]
    U -- No --> W[Return stem]
```

## Examples:
    >>> stem_word("studentech")
    'student'
    >>> stem_word("přátelům")
    'přítel'
    >>> stem_word("nejlepší", aggressive=True)
    'nejlep'
    >>> stem_word("králiček", aggressive=True)
    'králič'

## `sumy.nlp.stemmers.czech._remove_case` · *function*

## Summary:
Removes Czech case endings from words by applying morphological rules based on word length and suffix patterns.

## Description:
This function implements Czech morphological case ending removal for stemming purposes. It systematically strips case-specific suffixes from Czech words according to predefined patterns and word length thresholds. The function is designed to work as part of a larger Czech stemmer pipeline, specifically handling case inflections that would interfere with standard stemming algorithms.

The logic is extracted into its own function to separate the case-ending removal responsibility from the main stemming algorithm, improving modularity and testability. This approach allows the stemmer to handle various Czech grammatical cases consistently while maintaining clean separation of concerns.

## Args:
    word (str): The Czech word to process. Must be a string with at least 1 character.

## Returns:
    str: The word with case endings removed. Returns the original word unchanged if no matching pattern is found.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input word must be a string
        - Input word must have at least 1 character
    Postconditions:
        - Output word length is less than or equal to input word length
        - Returned word has case endings appropriately stripped according to Czech morphology rules

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_case] --> B{len(word) > 7 AND ends with "atech"?}
    B -- Yes --> C[Return word[:-5]]
    B -- No --> D{len(word) > 6?}
    D -- Yes --> E{ends with "ětem"?}
    E -- Yes --> F[Return _palatalize(word[:-3])]
    E -- No --> G{ends with "atům"?}
    G -- Yes --> H[Return word[:-4]]
    D -- No --> I{len(word) > 5?}
    I -- Yes --> J{ends with 3-char in ("ech","ich","ích","ého","ěmi","emi","ému","ete","eti","iho","ího","ími","imu")?}
    J -- Yes --> K[Return _palatalize(word[:-2])]
    J -- No --> L{ends with 3-char in ("ách","ata","aty","ých","ama","ami","ové","ovi","ými")?}
    L -- Yes --> M[Return word[:-3]]
    I -- No --> N{len(word) > 4?}
    N -- Yes --> O{ends with "em"?}
    O -- Yes --> P[Return _palatalize(word[:-1])]
    O -- No --> Q{ends with 2-char in ("es","ém","ím")?}
    Q -- Yes --> R[Return _palatalize(word[:-2])]
    Q -- No --> S{ends with 2-char in ("ům","at","ám","os","us","ým","mi","ou")?}
    S -- Yes --> T[Return word[:-2]]
    N -- No --> U{len(word) > 3?}
    U -- Yes --> V{ends with char in "eiíě"?}
    V -- Yes --> W[Return _palatalize(word)]
    V -- No --> X{ends with char in "uyůaoáéý"?}
    X -- Yes --> Y[Return word[:-1]]
    U -- No --> Z[Return word]
```

## Examples:
    >>> _remove_case("studentech")
    'student'
    >>> _remove_case("přátelům")
    'přítel'
    >>> _remove_case("většinou")
    'většina'
    >>> _remove_case("krásný")
    'krásný'
```

## `sumy.nlp.stemmers.czech._remove_possessives` · *function*

## Summary:
Removes possessive suffixes from Czech words to prepare them for stemming.

## Description:
This function strips possessive endings from Czech words that are longer than 5 characters. It specifically targets common possessive suffixes like "-ov" and "-ův" (used for masculine and neuter nouns) and the "-in" ending (used for feminine nouns). When these endings are detected, they are removed to normalize the word form for further processing in the Czech stemmer. The function delegates palatalization of "-in" endings to the `_palatalize` helper function.

## Args:
    word (str): A Czech word to process for possessive suffix removal. Must be a string.

## Returns:
    str: The word with possessive suffixes removed if applicable, otherwise returns the original word unchanged.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input word must be a string
        - Input word must have at least 1 character
    Postconditions:
        - Output word length is either equal to or two characters shorter than input (for "-ov"/"-ův" endings)
        - Output word length is either equal to or one character shorter than input (for "-in" endings)

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_possessives] --> B{len(word) > 5?}
    B -- No --> C[Return word]
    B -- Yes --> D{word[-2:] in ("ov", "ův")?}
    D -- Yes --> E[Return word[:-2]]
    D -- No --> F{word.endswith("in")?}
    F -- Yes --> G[Return _palatalize(word[:-1])]
    F -- No --> H[Return word]
```

## Examples:
    >>> _remove_possessives("studentov")
    'student'
    >>> _remove_possessives("učitelův")
    'učitel'
    >>> _remove_possessives("přítelina")
    'přítel'
    >>> _remove_possessives("královna")
    'královna'
```

## `sumy.nlp.stemmers.czech._remove_comparative` · *function*

## Summary:
Removes comparative suffixes from Czech words by stripping "ejš" or "ějš" endings and applying palatalization.

## Description:
This function processes Czech words to remove comparative morphological markers that indicate superlative or comparative forms. It specifically targets words ending in "ejš" or "ějš" (three-character endings) that are longer than five characters. When such patterns are detected, it removes the suffix and applies palatalization to the remaining stem. This is part of the Czech stemming process to normalize word forms for better matching in text analysis applications.

The function is extracted as a separate utility to encapsulate the specific logic for handling comparative suffix removal, maintaining clean separation between different morphological transformation stages in the Czech stemmer pipeline.

## Args:
    word (str): The Czech word to process. Must be a string with at least 3 characters to avoid index errors.

## Returns:
    str: The word with comparative suffix removed if applicable, otherwise the original word unchanged. The returned word may be modified through palatalization when suffix removal occurs.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input word must be a string
        - Input word must have at least 3 characters to avoid index errors
    Postconditions:
        - Output word length is either equal to or two characters shorter than input (when suffix is removed)
        - When suffix is removed, palatalization is applied to the remaining stem

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_comparative] --> B{len(word) > 5?}
    B -- No --> C[Return word]
    B -- Yes --> D{word[-3:] in ("ejš", "ějš")?}
    D -- Yes --> E[Call _palatalize(word[:-2])]
    D -- No --> F[Return word]
```

## Examples:
    >>> _remove_comparative("nejlepší")
    'nejlep'
    >>> _remove_comparative("největší")
    'největ'
    >>> _remove_comparative("dobrý")
    'dobrý'
    >>> _remove_comparative("nejkrásnější")
    'nejkrásn'
```

## `sumy.nlp.stemmers.czech._remove_diminutive` · *function*

## Summary:
Removes diminutive suffixes from Czech words to normalize them for stemming.

## Description:
This function strips various diminutive suffixes from Czech words, returning a normalized base form suitable for further stemming operations. It handles multiple suffix patterns based on word length and ending combinations, with special handling for palatalized forms. The function is part of the Czech stemmer implementation and is designed to be called internally by the stemming pipeline.

## Args:
    word (str): The Czech word to process. Must be a string with at least 1 character.

## Returns:
    str: The word with diminutive suffixes removed, or the original word if no diminutive pattern matches.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input word must be a string
        - Input word must have at least 1 character
    Postconditions:
        - Output word length is less than or equal to input word length
        - Returned word is normalized for subsequent stemming operations

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_diminutive] --> B{len(word) > 7 AND ends with "oušek"?}
    B -- Yes --> C[Return word[:-5]]
    B -- No --> D{len(word) > 6?}
    D -- Yes --> E{word[-4:] in ("eček", "éček", "iček", "íček", "enek", "ének", "inek", "ínek")?}
    E -- Yes --> F[Return _palatalize(word[:-3])]
    E -- No --> G{word[-4:] in ("áček", "aček", "oček", "uček", "anek", "onek", "unek", "ánek")?}
    G -- Yes --> H[Return _palatalize(word[:-4])]
    G -- No --> I{len(word) > 5?}
    I -- Yes --> J{word[-3:] in ("ečk", "éčk", "ičk", "íčk", "enk", "énk", "ink", "ínk")?}
    J -- Yes --> K[Return _palatalize(word[:-3])]
    J -- No --> L{word[-3:] in ("áčk", "ačk", "očk", "učk", "ank", "onk", "unk", "átk", "ánk", "ušk")?}
    L -- Yes --> M[Return word[:-3]]
    L -- No --> N{len(word) > 4?}
    N -- Yes --> O{word[-2:] in ("ek", "ék", "ík", "ik")?}
    O -- Yes --> P[Return _palatalize(word[:-1])]
    O -- No --> Q{word[-2:] in ("ák", "ak", "ok", "uk")?}
    Q -- Yes --> R[Return word[:-1]]
    Q -- No --> S{len(word) > 3 AND word[-1] == "k"?}
    S -- Yes --> T[Return word[:-1]]
    S -- No --> U[Return word]
```

## Examples:
    >>> _remove_diminutive("ptáček")
    'ptáč'
    >>> _remove_diminutive("malý")
    'mal'
    >>> _remove_diminutive("králiček")
    'králič'
    >>> _remove_diminutive("přátelkou")
    'přátelk'

## `sumy.nlp.stemmers.czech._remove_augmentative` · *function*

## Summary:
Removes augmentative suffixes from Czech words to normalize them for stemming.

## Description:
This function processes Czech words to remove specific augmentative suffixes that indicate comparative or superlative forms. It handles three main patterns: "-ajzn" (for words ending in this sequence), "-izn"/"-isk" (which require palatalization after removal), and "-ák" (for words ending in this sequence). The function is part of the Czech stemmer's preprocessing pipeline to ensure consistent word normalization.

## Args:
    word (str): The Czech word to process. Must be a string with sufficient length to match the suffix patterns.

## Returns:
    str: The word with augmentative suffixes removed if patterns match, otherwise returns the original word unchanged.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input word must be a string
        - Word length must be sufficient to match the suffix patterns (at least 5 characters for "-izn"/"-isk", at least 6 characters for "-ajzn", at least 4 characters for "-ák")
    Postconditions:
        - Output word length is either equal to or shorter than input word
        - If transformation occurs, the result follows Czech morphological rules

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_augmentative] --> B{len(word) > 6 AND word.endswith("ajzn")?}
    B -- Yes --> C[Return word[:-4]]
    B -- No --> D{len(word) > 5 AND word[-3:] in ("izn", "isk")?}
    D -- Yes --> E[Return _palatalize(word[:-2])]
    D -- No --> F{len(word) > 4 AND word.endswith("ák")?}
    F -- Yes --> G[Return word[:-2]]
    F -- No --> H[Return word]
```

## Examples:
    >>> _remove_augmentative("veliký")
    'veliký'
    >>> _remove_augmentative("největší")
    'největ'
    >>> _remove_augmentative("přílišní")
    'příliš'
    >>> _remove_augmentative("čtenářský")
    'čtenář'
```

## `sumy.nlp.stemmers.czech._remove_derivational` · *function*

## Summary:
Removes derivational suffixes from Czech words to produce base forms for stemming.

## Description:
This function applies a series of morphological rules to strip derivational suffixes from Czech words, reducing them to their root forms. It handles various suffix patterns based on word length and ending combinations, with special handling for palatalization through the `_palatalize` helper function. The function is part of the Czech stemmer implementation and is typically called during the text preprocessing phase before further linguistic analysis.

## Args:
    word (str): The Czech word to be processed. Must be a string with at least 4 characters to ensure meaningful suffix removal.

## Returns:
    str: The word with derivational suffixes removed. Returns the original word unchanged if no applicable suffix patterns are matched.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input word must be a string
        - Word length should be at least 4 characters for effective suffix removal
    Postconditions:
        - Output word length is less than or equal to input word length
        - All returned words are properly stemmed according to Czech morphological rules

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_derivational] --> B{len(word) > 8 AND ends with "obinec"?}
    B -- Yes --> C[Return word[:-6]]
    B -- No --> D{len(word) > 7?}
    D -- Yes --> E{ends with "ionář"?}
    E -- Yes --> F[Return _palatalize(word[:-4])]
    E -- No --> G{word[-5:] in ("ovisk", "ovstv", "ovišt", "ovník")?}
    G -- Yes --> H[Return word[:-5]]
    G -- No --> I{len(word) > 6?}
    I -- Yes --> J{word[-4:] in ("ásek", "loun", "nost", "teln", "ovec", "ovík", "ovtv", "ovin", "štin")?}
    J -- Yes --> K[Return word[:-4]]
    J -- No --> L{word[-4:] in ("enic", "inec", "itel")?}
    L -- Yes --> M[Return _palatalize(word[:-3])]
    L -- No --> N{len(word) > 5?}
    N -- Yes --> O{ends with "árn"?}
    O -- Yes --> P[Return word[:-3]]
    O -- No --> Q{word[-3:] in ("ěnk", "ián", "ist", "isk", "išt", "itb", "írn")?}
    Q -- Yes --> R[Return _palatalize(word[:-2])]
    Q -- No --> S{word[-3:] in ("och", "ost", "ovn", "oun", "out", "ouš", "ušk", "kyn", "čan", "kář", "néř", "ník", "ctv", "stv")?}
    S -- Yes --> T[Return word[:-3]]
    S -- No --> U{len(word) > 4?}
    U -- Yes --> V{word[-2:] in ("áč", "ač", "án", "an", "ář", "as")?}
    V -- Yes --> W[Return word[:-2]]
    V -- No --> X{word[-2:] in ("ec", "en", "ěn", "éř", "íř", "ic", "in", "ín", "it", "iv")?}
    X -- Yes --> Y[Return _palatalize(word[:-1])]
    X -- No --> Z{word[-2:] in ("ob", "ot", "ov", "oň", "ul", "yn", "čk", "čn", "dl", "nk", "tv", "tk", "vk")?}
    Z -- Yes --> AA[Return word[:-2]]
    Z -- No --> AB{len(word) > 3 AND word[-1] in "cčklnt"?}
    AB -- Yes --> AC[Return word[:-1]]
    AB -- No --> AD[Return word]
```

## Examples:
    >>> _remove_derivational("přílišný")
    'příliš'
    >>> _remove_derivational("čtenářův")
    'čtenář'
    >>> _remove_derivational("zaměstnanec")
    'zaměstn'
    >>> _remove_derivational("kdybych")
    'kdyb'

## `sumy.nlp.stemmers.czech._palatalize` · *function*

## Summary:
Applies Czech palatalization rules to transform word endings for proper stemming.

## Description:
This function implements specific morphological transformations for Czech words, converting certain endings to their palatalized forms. It serves as a helper function in the Czech stemmer to normalize word forms before applying standard stemming algorithms. The function handles common Czech phonetic patterns where consonant clusters undergo palatalization.

## Args:
    word (str): The input Czech word to be transformed. Must be a string with at least 2 characters to avoid index errors.

## Returns:
    str: The transformed word with appropriate palatalization applied. Returns the original word unchanged if no matching pattern is found.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input word must be a string
        - Input word must have at least 2 characters to avoid index errors
    Postconditions:
        - Output word length is either equal to or one character shorter than input
        - Transformation follows established Czech linguistic rules for palatalization

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _palatalize] --> B{word[-2:] in ("ci","ce","či","če")?}
    B -- Yes --> C[Return word[:-2] + "k"]
    B -- No --> D{word[-2:] in ("zi","ze","ži","že")?}
    D -- Yes --> E[Return word[:-2] + "h"]
    D -- No --> F{word[-3:] in ("čtě","čti","čtí")?}
    F -- Yes --> G[Return word[:-3] + "ck"]
    F -- No --> H{word[-3:] in ("ště","šti","ští")?}
    H -- Yes --> I[Return word[:-3] + "sk"]
    H -- No --> J[Return word[:-1]]
```

## Examples:
    >>> _palatalize("příliš")
    'příl'
    >>> _palatalize("čtení")
    'čten'
    >>> _palatalize("náš")
    'ná'
    >>> _palatalize("kdybych")
    'kdyb'

