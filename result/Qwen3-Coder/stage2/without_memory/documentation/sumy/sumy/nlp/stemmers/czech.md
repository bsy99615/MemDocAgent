# `czech.py`

## `sumy.nlp.stemmers.czech.stem_word` · *function*

## Summary:
Stems Czech words by removing inflectional suffixes while preserving capitalization patterns.

## Description:
Performs Czech word stemming by applying a series of morphological transformations to reduce words to their base form. The function handles various case patterns and can apply aggressive stemming rules to remove additional derivational suffixes. It is designed to work with Czech language morphology and preserves the original capitalization style of the input word.

## Args:
    word (str): The Czech word to be stemmed. Must be a string that can be decoded as UTF-8.
    aggressive (bool): When True, applies additional aggressive stemming rules to remove comparative, diminutive, augmentative, and derivational suffixes. Defaults to False.

## Returns:
    str: The stemmed version of the input word, maintaining the original capitalization pattern. Returns the original word unchanged if:
    - The word doesn't match the expected WORD_PATTERN regex pattern
    - The word contains mixed case (neither all lowercase, title case, nor all uppercase)

## Raises:
    UnicodeDecodeError: If the word parameter cannot be decoded as UTF-8.

## Constraints:
    Preconditions:
    - Input word must be a string or bytes that can be decoded as UTF-8
    - WORD_PATTERN must match the input word for processing to occur
    - Word must be either all lowercase, title case, or all uppercase
    
    Postconditions:
    - Output maintains the original capitalization pattern (uppercase, title case, or lowercase)
    - If word doesn't match WORD_PATTERN, original word is returned unchanged
    - If word has mixed case, warning is issued and original word is returned unchanged

## Side Effects:
    - Issues a warning via Python's warnings module when encountering mixed-case words
    - No external I/O or state mutations

## Control Flow:
```mermaid
flowchart TD
    A[Start stem_word] --> B{isinstance(word, unicode)?}
    B -- No --> C[word.decode("utf-8")]
    B -- Yes --> C
    C --> D{WORD_PATTERN.match(word)?}
    D -- No --> E[return word]
    D -- Yes --> F{word.islower() OR word.istitle() OR word.isupper()?}
    F -- No --> G[warn("skipping word with mixed case")] 
    G --> H[return word]
    F -- Yes --> I[stem = word.lower()]
    I --> J[_remove_case(stem)]
    J --> K[_remove_possessives(stem)]
    K --> L{aggressive?}
    L -- Yes --> M[_remove_comparative(stem)]
    M --> N[_remove_diminutive(stem)]
    N --> O[_remove_augmentative(stem)]
    O --> P[_remove_derivational(stem)]
    P --> Q[Check word.isupper()]
    Q -- Yes --> R[return stem.upper()]
    Q -- No --> S[Check word.istitle()]
    S -- Yes --> T[return stem.title()]
    S -- No --> U[return stem]
```

## Examples:
    # Basic stemming
    stem_word("písně") -> "písn"
    
    # Aggressive stemming
    stem_word("písně", aggressive=True) -> "písn"
    
    # Capitalization preservation
    stem_word("PÍSNĚ") -> "PÍSN"
    stem_word("Písně") -> "Písn"
    
    # Mixed case handling
    stem_word("PiSnE") -> "PiSnE"  # Warning issued, returns original
    
    # Non-matching pattern
    stem_word("123") -> "123"  # Returns unchanged if WORD_PATTERN doesn't match

## `sumy.nlp.stemmers.czech._remove_case` · *function*

## Summary:
Removes Czech case endings from words to facilitate stemming by applying length-based suffix removal and palatalization when appropriate.

## Description:
This function implements Czech-specific case ending removal logic for word stemming. It systematically examines word length and suffix patterns to remove grammatical case endings while applying palatalization transformations when required. The function is part of a larger Czech stemmer implementation and handles various Czech case endings according to linguistic rules.

## Args:
    word (str): The Czech word to process, represented as a string containing Unicode characters.

## Returns:
    str: The word with case endings removed. Returns the original word unchanged if no matching case endings are found.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Function assumes the word contains valid Unicode characters
    
    Postconditions:
    - Output is always a string
    - Returned string is either the original word or a modified version with case endings removed
    - If palatalization occurs, the result follows Czech phonetic transformation rules

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_case] --> B{Word length > 7 AND ends with "atech"?}
    B -- Yes --> C[Return word[:-5]]
    B -- No --> D{Word length > 6?}
    D -- Yes --> E{Ends with "ětem"?}
    E -- Yes --> F[Return _palatalize(word[:-3])]
    E -- No --> G{Ends with "atům"?}
    G -- Yes --> H[Return word[:-4]]
    G -- No --> I{Word length > 5?}
    I -- Yes --> J{Ends with 3-char suffix in special list?}
    J -- Yes --> K[Return _palatalize(word[:-2])]
    J -- No --> L{Ends with 3-char suffix in another list?}
    L -- Yes --> M[Return word[:-3]]
    L -- No --> N{Word length > 4?}
    N -- Yes --> O{Ends with "em"?}
    O -- Yes --> P[Return _palatalize(word[:-1])]
    O -- No --> Q{Ends with 2-char suffix in special list?}
    Q -- Yes --> R[Return _palatalize(word[:-2])]
    Q -- No --> S{Ends with 2-char suffix in another list?}
    S -- Yes --> T[Return word[:-2]]
    S -- No --> U{Word length > 3?}
    U -- Yes --> V{Ends with vowel in "eiíě"?}
    V -- Yes --> W[Return _palatalize(word)]
    V -- No --> X{Ends with vowel in "uyůaoáéý"?}
    X -- Yes --> Y[Return word[:-1]]
    X -- No --> Z[Return word]
    N -- No --> U
    I -- No --> N
    D -- No --> I
    A --> Z
```

## Examples:
    >>> _remove_case("atech")
    "atech"
    >>> _remove_case("větětem")
    "větět"  # Palatalized result
    >>> _remove_case("větěm")
    "vět"  # Palatalized result
    >>> _remove_case("větě")
    "vět"  # Palatalized result
    >>> _remove_case("vět")
    "vět"

## `sumy.nlp.stemmers.czech._remove_possessives` · *function*

## Summary:
Removes possessive endings from Czech words by stripping specific suffixes like "ov", "ův", and "in".

## Description:
This function implements a rule-based approach to remove possessive morphological markers from Czech words. It specifically targets common possessive suffixes in Czech, such as "-ov" and "-ův" (which indicate possession), and the "-in" ending that often appears in possessive constructions. The function applies these transformations only to words longer than 5 characters to avoid affecting shorter words that don't typically carry possessive morphology.

## Args:
    word (str): A Czech word string to process for possessive ending removal

## Returns:
    str: The word with possessive endings removed if applicable, otherwise the original word unchanged

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Input must be a string
    - Function only processes words with length greater than 5 characters
    
    Postconditions:
    - Returns a string of equal or shorter length than input
    - If possessive endings are removed, the returned word will be shorter than the input
    - If no possessive endings are detected, the original word is returned unchanged

## Side Effects:
    None

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
    >>> _remove_possessives("studentin")
    "studentk"
    >>> _remove_possessives("předmět")
    "předmět"
```

## `sumy.nlp.stemmers.czech._remove_comparative` · *function*

## Summary:
Removes comparative suffixes from Czech words by stripping "ejš" or "ějš" endings and applying palatalization.

## Description:
This function processes Czech words to remove comparative morphological suffixes. It specifically targets words longer than 5 characters that end with the comparative suffixes "ejš" or "ějš". When such a pattern is detected, it strips the suffix and applies palatalization to the remaining stem. This is part of the Czech stemming process to normalize words for text analysis.

## Args:
    word (str): A Czech word to process for comparative suffix removal

## Returns:
    str: The word with comparative suffix removed if conditions are met, otherwise the original word unchanged

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Input must be a string
    - Word length must be greater than 5 to qualify for comparison
    
    Postconditions:
    - Returns either the original word or a modified version with comparative suffix removed
    - If palatalization occurs, the result follows Czech phonetic rules

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_comparative] --> B{Word length > 5?}
    B -- No --> C[Return word]
    B -- Yes --> D{Ends with "ejš" or "ějš"?}
    D -- No --> C
    D -- Yes --> E[Call _palatalize(word[:-2])]
    E --> F[Return palatalized result]
```

## Examples:
    >>> _remove_comparative("nejlepší")
    "nejlep"
    
    >>> _remove_comparative("rychlejší")
    "rychl"
    
    >>> _remove_comparative("krátký")
    "krátký"
```

## `sumy.nlp.stemmers.czech._remove_diminutive` · *function*

## Summary:
Removes diminutive suffixes from Czech words to normalize them for stemming.

## Description:
This function processes Czech words to remove common diminutive suffixes, which are often added to nouns and adjectives to express smallness or endearment. The function implements a series of pattern matching rules based on word length and ending patterns to identify and strip appropriate diminutive endings. It is designed to work as part of a larger Czech stemming pipeline.

The logic is extracted into its own function to separate the concern of diminutive removal from the main stemming process, allowing for easier testing and maintenance of this specific normalization step. This function typically runs as part of a preprocessing phase before applying the main stemming algorithm.

## Args:
    word (str): A Czech word string to process for diminutive removal

## Returns:
    str: The word with diminutive suffixes removed, or the original word if no diminutive patterns match

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Input must be a string
    - Function assumes the input contains valid Czech characters
    
    Postconditions:
    - Returned string is either the original word or a modified version with diminutive suffixes removed
    - All returned strings are valid Czech words or normalized forms

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_diminutive] --> B{Word length > 7 AND ends with "oušek"}
    B -- Yes --> C[Return word[:-5]]
    B -- No --> D{Word length > 6}
    D -- Yes --> E{Ends with 4-char pattern in special set}
    E -- Yes --> F[Call _palatalize(word[:-3])]
    E -- No --> G{Ends with 4-char pattern in another set}
    G -- Yes --> H[Call _palatalize(word[:-4])]
    G -- No --> I{Word length > 5}
    I -- Yes --> J{Ends with 3-char pattern in special set}
    J -- Yes --> K[Call _palatalize(word[:-3])]
    J -- No --> L{Ends with 3-char pattern in another set}
    L -- Yes --> M[Return word[:-3]]
    L -- No --> N{Word length > 4}
    N -- Yes --> O{Ends with 2-char pattern in special set}
    O -- Yes --> P[Call _palatalize(word[:-1])]
    O -- No --> Q{Ends with 2-char pattern in another set}
    Q -- Yes --> R[Return word[:-1]]
    Q -- No --> S{Word length > 3 AND last char is "k"}
    S -- Yes --> T[Return word[:-1]]
    S -- No --> U[Return word]
```

## Examples:
    >>> _remove_diminutive("pesek")
    "pes"
    
    >>> _remove_diminutive("micek")
    "myš"
    
    >>> _remove_diminutive("malicka")
    "malick"
    
    >>> _remove_diminutive("kocka")
    "kočka"

## `sumy.nlp.stemmers.czech._remove_augmentative` · *function*

## Summary:
Removes augmentative suffixes from Czech words according to specific morphological patterns.

## Description:
This function applies morphological transformations to remove augmentative suffixes from Czech words. It handles three specific cases based on word length and ending patterns. The function is part of the Czech stemmer implementation and is designed to normalize words by removing these specific suffixes that indicate augmentative forms in Czech morphology.

Augmentative suffixes in Czech are morphological markers that indicate a particular grammatical or semantic relationship. This function specifically targets common augmentative endings to prepare words for proper stemming operations.

The function is called internally by the Czech stemmer to prepare words for further processing, particularly when dealing with words that have augmentative endings that should be stripped for proper stemming.

## Args:
    word (str): The Czech word to process, represented as a string of characters.

## Returns:
    str: The word with augmentative suffixes removed if applicable, otherwise returns the original word unchanged.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string representing a Czech word
    - Function assumes the word contains only ASCII characters or properly encoded Unicode characters
    
    Postconditions:
    - Returned string is either the original word or a modified version with specific suffixes removed
    - The returned word maintains proper Unicode encoding

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_augmentative] --> B{len(word) > 6 AND ends with "ajzn"?}
    B -- Yes --> C[Return word[:-4]]
    B -- No --> D{len(word) > 5 AND ends with "izn" OR "isk"?}
    D -- Yes --> E[Return _palatalize(word[:-2])]
    D -- No --> F{len(word) > 4 AND ends with "ák"?}
    F -- Yes --> G[Return word[:-2]]
    F -- No --> H[Return word]
```

## Examples:
    >>> _remove_augmentative("krásnajzn")
    "krásn"
    
    >>> _remove_augmentative("přátelisk")
    "přátel"
    
    >>> _remove_augmentative("učení")
    "učení"

## `sumy.nlp.stemmers.czech._remove_derivational` · *function*

## Summary:
Removes derivational suffixes from Czech words to produce their stem forms.

## Description:
This function implements a set of rules for removing derivational suffixes from Czech words. It examines the word's length and specific endings to determine which suffixes should be removed. The function is part of the Czech stemmer implementation and is designed to reduce words to their base forms for text processing tasks like information retrieval and text mining.

The logic is extracted into its own function to separate the suffix removal algorithm from the main stemming pipeline, making the code more modular and testable. This allows the palatalization process to be handled consistently across different suffix removal operations.

## Args:
    word (str): The Czech word to be stemmed, represented as a Unicode string.

## Returns:
    str: The stemmed version of the input word with derivational suffixes removed. If no suffix matches the removal criteria, the original word is returned unchanged.

## Raises:
    None: This function does not explicitly raise any exceptions.

## Constraints:
    Preconditions:
    - Input must be a string (Unicode)
    - Function assumes the input contains valid Czech characters
    
    Postconditions:
    - Output is always a string
    - If suffix removal occurs, the resulting word will be shorter than the input
    - If no suffix matches removal criteria, the original word is returned unchanged

## Side Effects:
    None: This function is pure and has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_derivational] --> B{Word length > 8 AND ends with "obinec"?}
    B -- Yes --> C[Return word[:-6]]
    B -- No --> D{Word length > 7?}
    D -- Yes --> E{Ends with "ionář"?}
    E -- Yes --> F[Return _palatalize(word[:-4])]
    E -- No --> G{Ends with "ovisk"|"ovstv"|"ovišt"|"ovník"?}
    G -- Yes --> H[Return word[:-5]]
    G -- No --> I{Word length > 6?}
    I -- Yes --> J{Ends with "ásek"|"loun"|"nost"|"teln"|"ovec"|"ovík"|"ovtv"|"ovin"|"štin"?}
    J -- Yes --> K[Return word[:-4]]
    J -- No --> L{Ends with "enic"|"inec"|"itel"?}
    L -- Yes --> M[Return _palatalize(word[:-3])]
    L -- No --> N{Word length > 5?}
    N -- Yes --> O{Ends with "árn"?}
    O -- Yes --> P[Return word[:-3]]
    O -- No --> Q{Ends with "ěnk"|"ián"|"ist"|"isk"|"išt"|"itb"|"írn"?}
    Q -- Yes --> R[Return _palatalize(word[:-2])]
    Q -- No --> S{Ends with "och"|"ost"|"ovn"|"oun"|"out"|"ouš"|"ušk"|"kyn"|"čan"|"kář"|"néř"|"ník"|"ctv"|"stv"?}
    S -- Yes --> T[Return word[:-3]]
    S -- No --> U{Word length > 4?}
    U -- Yes --> V{Ends with "áč"|"ač"|"án"|"an"|"ář"|"as"?}
    V -- Yes --> W[Return word[:-2]]
    V -- No --> X{Ends with "ec"|"en"|"ěn"|"éř"|"íř"|"ic"|"in"|"ín"|"it"|"iv"?}
    X -- Yes --> Y[Return _palatalize(word[:-1])]
    X -- No --> Z{Ends with "ob"|"ot"|"ov"|"oň"|"ul"|"yn"|"čk"|"čn"|"dl"|"nk"|"tv"|"tk"|"vk"?}
    Z -- Yes --> AA[Return word[:-2]]
    Z -- No --> AB{Word length > 3 AND last char in "cčklnt"?}
    AB -- Yes --> AC[Return word[:-1]]
    AB -- No --> AD[Return word]
```

## Examples:
    >>> _remove_derivational("příběhobinec")
    "příběh"
    
    >>> _remove_derivational("informační")
    "informač"
    
    >>> _remove_derivational("student")
    "student"

## `sumy.nlp.stemmers.czech._palatalize` · *function*

## Summary:
Applies Czech palatalization rules to normalize word endings for stemming purposes.

## Description:
This function transforms Czech words by applying specific morphological rules to handle palatalization patterns commonly found in Czech morphology. Palatalization refers to the phonological process where consonants change when followed by front vowels (i, í, e, é, ě). This function normalizes these patterns by replacing specific endings with their canonical forms, which is essential for proper stemming in Czech text processing pipelines.

The function processes words sequentially through specific ending patterns and applies appropriate transformations. It's designed to be used internally by Czech stemmer implementations.

## Args:
    word (str): The Czech word to be palatalized. Must be a non-empty string.

## Returns:
    str: The palatalized version of the input word. Returns the original word unchanged if no palatalization rules apply.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a non-empty string
    - Function assumes the input contains valid Czech characters
    
    Postconditions:
    - Output is always a string
    - If palatalization rules match, the returned string will have modified endings according to Czech morphological rules
    - If no rules match, the last character is simply removed from the input

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _palatalize] --> B{word ends with "ci", "ce", "či", "če"?}
    B -- Yes --> C[Return word[:-2] + "k"]
    B -- No --> D{word ends with "zi", "ze", "ži", "že"?}
    D -- Yes --> E[Return word[:-2] + "h"]
    D -- No --> F{word ends with "čtě", "čti", "čtí"?}
    F -- Yes --> G[Return word[:-3] + "ck"]
    F -- No --> H{word ends with "ště", "šti", "ští"?}
    H -- Yes --> I[Return word[:-3] + "sk"]
    H -- No --> J[Return word[:-1]]
```

## Examples:
    >>> _palatalize("čtení")  # ends with "ní" -> removes last char
    "čten"
    >>> _palatalize("čtenček")  # ends with "ček" -> replaces with "čk"
    "čtenk"
    >>> _palatalize("příliš")  # ends with "š" -> removes last char  
    "příl"
    >>> _palatalize("zelený")  # ends with "ný" -> removes last char
    "zelen"
```

