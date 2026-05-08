# `czech.py`

## `sumy.nlp.stemmers.czech.stem_word` · *function*

## Summary
Stems Czech words by removing morphological endings and applying case normalization to produce base word forms for text processing.

## Description
Performs Czech word stemming with optional aggressive morphological processing. This function serves as the main entry point for Czech text stemming, applying basic case removal and possessive ending stripping by default, with additional aggressive stemming options available. The function handles case preservation for uppercase and title-cased words while normalizing mixed-case words with a warning.

## Args
    word (str): A Czech word to be stemmed, which may be encoded as bytes or Unicode string
    aggressive (bool): When True, applies additional morphological transformations including comparative, diminutive, augmentative, and derivational suffix removal. Defaults to False

## Returns
    str: The stemmed version of the input word, with appropriate case preservation. Returns the original word unchanged if it doesn't match the WORD_PATTERN or contains mixed case

## Raises
    None explicitly raised, though mixed-case words trigger a warning via the warnings module

## Constraints
    Preconditions:
    - Input word must be a string or bytes object that can be decoded as UTF-8
    - Word should contain only characters that match the WORD_PATTERN regex (typically Czech alphabetic characters with diacritics)
    
    Postconditions:
    - Output is always a string representing a normalized Czech word form
    - Case information is preserved appropriately for uppercase and title-cased words
    - Mixed-case words are skipped with a warning but returned unchanged

## Side Effects
    - Issues a warning via Python's warnings module when encountering mixed-case words
    - No external state mutations or I/O operations

## Control Flow
```mermaid
flowchart TD
    A[Start stem_word] --> B{isinstance(word, unicode)?}
    B -- No --> C[word.decode("utf-8")]
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

## Examples
    >>> stem_word("přátelích")
    "přátel"
    >>> stem_word("studentovi", aggressive=True)
    "student"
    >>> stem_word("NEJLEPŠÍ", aggressive=True)
    "NEJLEP"
    >>> stem_word("Příliš")
    "příliš"
    >>> stem_word("MixedCaseWord")
    "MixedCaseWord"  # Warning issued, unchanged

## `sumy.nlp.stemmers.czech._remove_case` · *function*

## Summary:
Removes Czech case endings from words to prepare them for stemming by applying morphological rules based on word length and suffix patterns.

## Description:
This private helper function implements Czech-specific morphological case ending removal for text stemming. It processes Czech words by identifying and stripping common case endings according to predefined patterns, reducing words to their base forms for consistent stemming across different grammatical cases. The function handles various word lengths and endings typical in Czech morphology, with special handling for palatalization through the `_palatalize` helper function.

## Args:
    word (str): A Czech word represented as a Unicode string that may contain case endings to be removed.

## Returns:
    str: The word with case endings removed, potentially palatalized for consistent stemming. Returns the original word unchanged if no matching case endings are detected.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Function assumes the word contains sufficient characters for pattern matching
    
    Postconditions:
    - Output is always a string of equal or shorter length than input
    - Function preserves the semantic meaning of the word while normalizing its form for stemming

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
    U -- Yes --> V{last char in "eiíě"?}
    V -- Yes --> W[Return _palatalize(word)]
    V -- No --> X{last char in "uyůaoáéý"?}
    X -- Yes --> Y[Return word[:-1]]
    U -- No --> Z[Return word]
```

## Examples:
    >>> _remove_case("přátelích")
    "přátel"
    >>> _remove_case("studentovi")
    "student"
    >>> _remove_case("větě")
    "vět"
    >>> _remove_case("krásný")
    "krásný"

## `sumy.nlp.stemmers.czech._remove_possessives` · *function*

## Summary:
Removes possessive endings from Czech words for stemming purposes.

## Description:
This private helper function applies Czech-specific possessive ending removal rules to normalize words for stemming. It targets common possessive suffixes like "ov" and "ův" (as in "studentov" → "student"), and handles the "in" ending by applying palatalization rules. The function is part of the Czech stemmer's preprocessing pipeline to ensure consistent word normalization.

## Args:
    word (str): A Czech word represented as a string that may contain possessive endings.

## Returns:
    str: The word with possessive endings removed, or the original word if no possessive endings match the criteria.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Word length must be greater than 5 characters to trigger possessive ending removal logic
    
    Postconditions:
    - Output is always a string of equal or shorter length than input
    - Function preserves the semantic meaning of the word while normalizing its form for stemming

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
    "student"
    >>> _remove_possessives("učitelův")
    "učitel"
    >>> _remove_possessives("příliš")
    "příliš"
    >>> _remove_possessives("čtení")
    "čtení"
```

## `sumy.nlp.stemmers.czech._remove_comparative` · *function*

## Summary:
Removes comparative suffixes from Czech words by stripping "ejš" or "ějš" endings when applicable.

## Description:
This private helper function implements a specific rule for Czech word stemming by identifying and removing comparative suffixes. It targets words longer than five characters that end with the comparative suffixes "ejš" or "ějš", replacing them with a palatalized version of the root word. This function is part of the Czech stemmer's morphological processing pipeline, specifically designed to normalize comparative forms for consistent stemming.

## Args:
    word (str): A Czech word represented as a string that may contain comparative suffixes.

## Returns:
    str: The word with comparative suffix removed if conditions are met, otherwise returns the original word unchanged.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Word length must be greater than 5 characters to qualify for comparison
    
    Postconditions:
    - Output is always a string of equal or shorter length than input
    - Function preserves the semantic meaning of the word while normalizing its form for stemming

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_comparative] --> B{len(word) > 5?}
    B -- No --> C[Return word]
    B -- Yes --> D{word[-3:] in ("ejš", "ějš")?}
    D -- Yes --> E[Call _palatalize(word[:-2])]
    D -- No --> C
    E --> F[Return result]
```

## Examples:
    >>> _remove_comparative("nejlepší")
    "nejlep"
    >>> _remove_comparative("příliš")
    "příliš"
    >>> _remove_comparative("největší")
    "největ"
```

## `sumy.nlp.stemmers.czech._remove_diminutive` · *function*

## Summary:
Removes diminutive suffixes from Czech words to facilitate proper stemming by normalizing word forms.

## Description:
This private helper function applies Czech-specific rules to strip diminutive endings from words, which helps standardize word forms for effective stemming. The function handles various diminutive suffix patterns commonly found in Czech morphology, including those ending in "-oušek", "-ek", "-ek", "-k", and others, with special handling for palatalized forms.

## Args:
    word (str): A Czech word represented as a string that may contain diminutive suffixes.

## Returns:
    str: The word with diminutive suffixes removed, or the original word if no diminutive pattern matches.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Function assumes the word contains sufficient characters for pattern matching
    
    Postconditions:
    - Output is always a string of equal or shorter length than input
    - Function preserves the semantic meaning of the word while normalizing its form for stemming

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_diminutive] --> B{len(word) > 7 AND ends with "oušek"?}
    B -- Yes --> C[Return word[:-5]]
    B -- No --> D{len(word) > 6?}
    D -- Yes --> E{word[-4:] in ("eček","éček","iček","íček","enek","ének","inek","ínek")?}
    E -- Yes --> F[Call _palatalize(word[:-3])]
    E -- No --> G{word[-4:] in ("áček","aček","oček","uček","anek","onek","unek","ánek")?}
    G -- Yes --> H[Call _palatalize(word[:-4])]
    G -- No --> I{len(word) > 5?}
    I -- Yes --> J{word[-3:] in ("ečk","éčk","ičk","íčk","enk","énk","ink","ínk")?}
    J -- Yes --> K[Call _palatalize(word[:-3])]
    J -- No --> L{word[-3:] in ("áčk","ačk","očk","učk","ank","onk","unk","átk","ánk","ušk")?}
    L -- Yes --> M[Return word[:-3]]
    L -- No --> N{len(word) > 4?}
    N -- Yes --> O{word[-2:] in ("ek","ék","ík","ik")?}
    O -- Yes --> P[Call _palatalize(word[:-1])]
    O -- No --> Q{word[-2:] in ("ák","ak","ok","uk")?}
    Q -- Yes --> R[Return word[:-1]]
    Q -- No --> S{len(word) > 3 AND word[-1] == "k"?}
    S -- Yes --> T[Return word[:-1]]
    S -- No --> U[Return word]
```

## Examples:
    >>> _remove_diminutive("malý")
    "malý"
    >>> _remove_diminutive("přílišek")
    "příliš"
    >>> _remove_diminutive("čteníček")
    "čten"
    >>> _remove_diminutive("učenýk")
    "učený"
```

## `sumy.nlp.stemmers.czech._remove_augmentative` · *function*

## Summary:
Removes augmentative suffixes from Czech words to facilitate proper stemming.

## Description:
This private helper function applies specific morphological rules to remove augmentative suffixes commonly found in Czech words. It processes words based on their endings and length to normalize them for consistent stemming across different morphological forms. The function handles three specific suffix patterns: "ajzn" (length > 6), "izn"/"isk" (length > 5), and "ák" (length > 4).

## Args:
    word (str): A Czech word to be processed for augmentative suffix removal.

## Returns:
    str: The word with augmentative suffixes removed if applicable, otherwise the original word unchanged.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Function assumes the word contains sufficient characters for pattern matching
    
    Postconditions:
    - Output is always a string of equal or shorter length than input
    - Function preserves the semantic meaning of the word while normalizing its form for stemming

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
    >>> _remove_augmentative("krásnajzn")
    "krásn"
    >>> _remove_augmentative("přílišizn")
    "příl"
    >>> _remove_augmentative("nášák")
    "náš"
    >>> _remove_augmentative("krásný")
    "krásný"

## `sumy.nlp.stemmers.czech._remove_derivational` · *function*

## Summary:
Removes derivational suffixes from Czech words to produce stem forms for text processing.

## Description:
Implements Czech-specific suffix removal rules to strip derivational affixes from words, reducing them to their base stem forms. This function is part of the Czech stemmer's preprocessing pipeline and handles various morphological patterns common in Czech language processing.

## Args:
    word (str): The Czech word to be processed, represented as a string of characters.

## Returns:
    str: The word with derivational suffixes removed, or the original word if no applicable suffixes are found.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Function assumes the word contains sufficient characters for pattern matching
    
    Postconditions:
    - Output is always a string of equal or shorter length than input
    - Function preserves the semantic meaning of the word while normalizing its form for stemming

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
    >>> _remove_derivational("příběžný")
    "příběž"
    >>> _remove_derivational("čtenářův")
    "čtenář"
    >>> _remove_derivational("zaměstnanec")
    "zaměstn"

## `sumy.nlp.stemmers.czech._palatalize` · *function*

## Summary:
Applies Czech palatalization rules to reduce word endings for stemming purposes.

## Description:
This private helper function implements Czech-specific phonetic rules for palatalization, transforming word endings according to established linguistic patterns used in Czech text processing and stemming algorithms. The function processes word endings to normalize them for consistent stemming across different Czech morphological forms.

## Args:
    word (str): The Czech word to be palatalized, represented as a string of characters.

## Returns:
    str: The palatalized version of the input word, with specific ending transformations applied based on Czech phonetic rules.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Function assumes the word contains sufficient characters for pattern matching
    
    Postconditions:
    - Output is always a string of equal or shorter length than input
    - Function preserves the semantic meaning of the word while normalizing its form for stemming

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
    "příl"
    >>> _palatalize("čtení")
    "čten"
    >>> _palatalize("náši")
    "náš"
```

