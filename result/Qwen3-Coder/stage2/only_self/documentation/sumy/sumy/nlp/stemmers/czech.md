# `czech.py`

## `sumy.nlp.stemmers.czech.stem_word` · *function*

## Summary:
Stems Czech words by removing grammatical inflections and morphological endings to produce base word forms.

## Description:
Processes Czech words through a multi-stage stemming pipeline that removes case endings, possessive forms, and optional comparative, diminutive, augmentative, and derivational suffixes. The function handles various Czech grammatical cases and maintains proper capitalization in the output. This logic is extracted into its own function to separate the core stemming algorithm from the validation and case handling logic, enabling reuse and testing of the stemming process.

## Args:
    word (str): The Czech word to be stemmed. Must be a string that can be decoded to UTF-8.
    aggressive (bool): When True, applies additional aggressive stemming rules including comparative, diminutive, augmentative, and derivational suffix removal. Defaults to False.

## Returns:
    str: The stemmed version of the input word. Returns the original word unchanged if it doesn't match the WORD_PATTERN or contains mixed case.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input word must be a string or bytes that can be decoded to UTF-8
    - Word must match the WORD_PATTERN regex for further processing
    - Word must be entirely lowercase, title case, or uppercase (mixed case is skipped)
    
    Postconditions:
    - Output is always a string
    - Capitalization is preserved according to the original word's case pattern
    - If aggressive=True, additional morphological transformations are applied

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start stem_word] --> B{isinstance(word, unicode)?}
    B -- No --> C[word.decode(utf-8)]
    B -- Yes --> D[Continue]
    D --> E{WORD_PATTERN.match(word)?}
    E -- No --> F[Return word]
    E -- Yes --> G{word.islower() OR word.istitle() OR word.isupper()?}
    G -- No --> H[warn("skipping word with mixed case")]
    H --> I[Return word]
    G -- Yes --> J[stem = word.lower()]
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
    "student"
    >>> stem_word("příkladu", aggressive=True)
    "příklad"
    >>> stem_word("KNIHY")
    "KNIH"
    >>> stem_word("Studentov")
    "student"
```

## `sumy.nlp.stemmers.czech._remove_case` · *function*

## Summary:
Removes Czech case endings from words by applying length-based suffix matching and palatalization rules.

## Description:
Processes Czech words to strip case inflections by examining word length and ending patterns. This function is part of the Czech stemming pipeline, specifically designed to handle various Czech grammatical case endings while maintaining morphological accuracy through palatalization transformations.

## Args:
    word (str): The Czech word to process, represented as a Unicode string.

## Returns:
    str: The word with case endings removed. Returns the original word unchanged if no matching case ending patterns are detected.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string
    - String must be non-empty
    
    Postconditions:
    - Output is always a string
    - Function is deterministic and idempotent for the same input

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_case] --> B{len(word) > 7 AND ends with "atech"?}
    B -- Yes --> C[Return word[:-5]]
    B -- No --> D{len(word) > 6}
    D -- Yes --> E{ends with "ětem"?}
    E -- Yes --> F[Return _palatalize(word[:-3])]
    E -- No --> G{ends with "atům"?}
    G -- Yes --> H[Return word[:-4]]
    G -- No --> I{len(word) > 5}
    I -- Yes --> J{ends with 3-char in ("ech","ich","ích","ého","ěmi","emi","ému","ete","eti","iho","ího","ími","imu")?}
    J -- Yes --> K[Return _palatalize(word[:-2])]
    J -- No --> L{ends with 3-char in ("ách","ata","aty","ých","ama","ami","ové","ovi","ými")?}
    L -- Yes --> M[Return word[:-3]]
    L -- No --> N{len(word) > 4}
    N -- Yes --> O{ends with "em"?}
    O -- Yes --> P[Return _palatalize(word[:-1])]
    O -- No --> Q{ends with 2-char in ("es","ém","ím")?}
    Q -- Yes --> R[Return _palatalize(word[:-2])]
    Q -- No --> S{ends with 2-char in ("ům","at","ám","os","us","ým","mi","ou")?}
    S -- Yes --> T[Return word[:-2]]
    S -- No --> U{len(word) > 3}
    U -- Yes --> V{last char in "eiíě"?}
    V -- Yes --> W[Return _palatalize(word)]
    V -- No --> X{last char in "uyůaoáéý"?}
    X -- Yes --> Y[Return word[:-1]]
    X -- No --> Z[Return word]
```

## Examples:
    >>> _remove_case("studentech")
    "student"
    >>> _remove_case("příkladu")
    "příklad"
    >>> _remove_case("knihy")
    "knih"
    >>> _remove_case("stav")
    "stav"

## `sumy.nlp.stemmers.czech._remove_possessives` · *function*

## Summary:
Removes possessive endings from Czech words by stripping specific suffixes like "ov", "ův", and "in".

## Description:
This private function implements a morphological transformation for Czech words by removing possessive endings. It specifically targets common Czech possessive suffixes such as "-ov" and "-ův" (for masculine and neuter nouns) and "-in" (for feminine nouns). The function applies these transformations only to words longer than 5 characters to avoid affecting shorter words that don't typically carry possessive endings.

The function is part of a Czech stemming pipeline and helps normalize possessive forms to their base forms for effective text processing and summarization tasks. It's designed to be called internally by other functions in the Czech stemmer module.

## Args:
    word (str): The Czech word to process. Must be a string representing a Czech word.

## Returns:
    str: The word with possessive endings removed if applicable, otherwise returns the original word unchanged.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string
    - Function operates only on words with length greater than 5 characters
    
    Postconditions:
    - Output is always a string
    - If possessive endings are removed, the resulting word will be shorter than the input
    - If no possessive endings match, the original word is returned unchanged

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_possessives] --> B{len(word) > 5?}
    B -- No --> C[Return word]
    B -- Yes --> D{word ends with "ov" or "ův"?}
    D -- Yes --> E[Return word[:-2]]
    D -- No --> F{word ends with "in"?}
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
    >>> _remove_possessives("kniha")
    "kniha"
```

## `sumy.nlp.stemmers.czech._remove_comparative` · *function*

## Summary:
Removes comparative suffixes from Czech words by stripping "ejš" or "ějš" endings when applicable.

## Description:
This function implements a morphological transformation for Czech words by removing comparative suffixes. It specifically targets words longer than 5 characters that end with the comparative suffixes "ejš" or "ějš". When these conditions are met, it applies palatalization to the root portion of the word before returning it. This function is part of the Czech stemming process, helping normalize word forms by removing comparative inflections.

## Args:
    word (str): A Czech word to process. Must be a string with at least one character.

## Returns:
    str: The word with comparative suffix removed if conditions are met, otherwise the original word unchanged.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string
    - String must have at least one character
    
    Postconditions:
    - Output is always a string
    - If the word is 5 characters or shorter, it's returned unchanged
    - If the word ends with "ejš" or "ějš", it's processed through palatalization

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_comparative] --> B{len(word) > 5?}
    B -- No --> C[Return word]
    B -- Yes --> D{word ends with "ejš" or "ějš"?}
    D -- No --> E[Return word]
    D -- Yes --> F[Call _palatalize(word[:-2])]
    F --> G[Return result]
```

## Examples:
    >>> _remove_comparative("nejlepší")
    "nejlep"
    >>> _remove_comparative("dobrý")
    "dobrý"
    >>> _remove_comparative("příliš")
    "příliš"
```

## `sumy.nlp.stemmers.czech._remove_diminutive` · *function*

## Summary:
Removes diminutive suffixes from Czech words to normalize them for stemming.

## Description:
This function processes Czech words to remove common diminutive suffixes, which are often added to nouns and adjectives to express smallness or endearment. The function implements a set of rules based on word length and specific suffix patterns to identify and remove these diminutive forms. It is typically called as part of the Czech text preprocessing pipeline before stemming operations.

The logic is extracted into its own function to separate the concern of diminutive removal from the broader stemming algorithm, making the code more modular and testable.

## Args:
    word (str): A Czech word string that may contain diminutive suffixes

## Returns:
    str: The word with diminutive suffixes removed, or the original word if no diminutive pattern matches

## Raises:
    None explicitly raised

## Constraints:
    Preconditions:
    - Input must be a string
    - Function assumes Czech language patterns
    
    Postconditions:
    - Returned string is either the original word or a modified version with diminutive suffixes removed
    - All returned words are valid Unicode strings

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_diminutive] --> B{Word length > 7 AND ends with "oušek"}
    B -- Yes --> C[Return word[:-5]]
    B -- No --> D{Word length > 6}
    D -- Yes --> E{Ends with 4-letter suffix in special list}
    E -- Yes --> F[Call _palatalize(word[:-3])]
    E -- No --> G{Ends with 4-letter suffix in another special list}
    G -- Yes --> H[Call _palatalize(word[:-4])]
    G -- No --> I{Word length > 5}
    I -- Yes --> J{Ends with 3-letter suffix in special list}
    J -- Yes --> K[Call _palatalize(word[:-3])]
    J -- No --> L{Ends with 3-letter suffix in another special list}
    L -- Yes --> M[Return word[:-3]]
    L -- No --> N{Word length > 4}
    N -- Yes --> O{Ends with 2-letter suffix in special list}
    O -- Yes --> P[Call _palatalize(word[:-1])]
    O -- No --> Q{Ends with 2-letter suffix in another special list}
    Q -- Yes --> R[Return word[:-1]]
    Q -- No --> S{Word length > 3 AND ends with "k"}
    S -- Yes --> T[Return word[:-1]]
    S -- No --> U[Return original word]
```

## Examples:
    >>> _remove_diminutive("pesek")
    "pes"
    >>> _remove_diminutive("maminka")
    "mama"
    >>> _remove_diminutive("oušek")
    "ouš"
    >>> _remove_diminutive("krásný")
    "krásný"

## `sumy.nlp.stemmers.czech._remove_augmentative` · *function*

## Summary:
Removes augmentative suffixes from Czech words to normalize their stems for text processing applications.

## Description:
This function applies morphological rules to remove specific augmentative suffixes commonly found in Czech words. It handles three main patterns: "-ajzn" (length > 6), "-izn"/"-isk" (length > 5), and "-ák" (length > 4). The function is designed to be part of a larger Czech stemming pipeline, specifically targeting augmentative morphemes that modify word meaning or grammatical form.

The logic is extracted into its own function rather than being inlined because it represents a distinct morphological transformation step that can be reused and tested independently. This separation allows for clearer code organization and makes it easier to modify or extend the stemming rules without affecting other parts of the system.

## Args:
    word (str): The Czech word to process. Must be a string with at least one character.

## Returns:
    str: The word with augmentative suffixes removed if applicable, otherwise the original word unchanged.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string
    - String must have at least one character
    
    Postconditions:
    - Output is always a string
    - If no matching suffix is found, the original word is returned unchanged
    - The function preserves the original word when no transformation is applied

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
    >>> _remove_augmentative("učeníák")
    "učení"
    >>> _remove_augmentative("krásný")
    "krásný"
```

## `sumy.nlp.stemmers.czech._remove_derivational` · *function*

## Summary:
Removes derivational suffixes from Czech words to produce their stem forms.

## Description:
This function applies a series of rules to remove derivational suffixes from Czech words, reducing them to their base stem form. It handles various suffix patterns based on word length and ending characters, with special handling for palatalization through the `_palatalize` helper function. The function is designed to be part of a larger Czech stemming pipeline that normalizes word forms for text processing applications.

## Args:
    word (str): A Czech word to be stemmed. Must be a string containing valid Czech characters.

## Returns:
    str: The stemmed version of the input word with derivational suffixes removed. Returns the original word unchanged if no applicable suffix removal rules match.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string
    - String should contain valid Czech characters
    
    Postconditions:
    - Output is always a string
    - The returned word is a reduced form of the input word
    - Function is deterministic and idempotent for the same input

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start _remove_derivational] --> B{len(word) > 8 AND ends with "obinec"?}
    B -- Yes --> C[Return word[:-6]]
    B -- No --> D{len(word) > 7}
    D -- Yes --> E{ends with "ionář"?}
    E -- Yes --> F[Return _palatalize(word[:-4])]
    E -- No --> G{word[-5:] in ("ovisk", "ovstv", "ovišt", "ovník")?}
    G -- Yes --> H[Return word[:-5]]
    G -- No --> I{len(word) > 6}
    I -- Yes --> J{word[-4:] in ("ásek", "loun", "nost", "teln", "ovec", "ovík", "ovtv", "ovin", "štin")?}
    J -- Yes --> K[Return word[:-4]]
    J -- No --> L{word[-4:] in ("enic", "inec", "itel")?}
    L -- Yes --> M[Return _palatalize(word[:-3])]
    L -- No --> N{len(word) > 5}
    N -- Yes --> O{ends with "árn"?}
    O -- Yes --> P[Return word[:-3]]
    O -- No --> Q{word[-3:] in ("ěnk", "ián", "ist", "isk", "išt", "itb", "írn")?}
    Q -- Yes --> R[Return _palatalize(word[:-2])]
    Q -- No --> S{word[-3:] in ("och", "ost", "ovn", "oun", "out", "ouš", "ušk", "kyn", "čan", "kář", "néř", "ník", "ctv", "stv")?}
    S -- Yes --> T[Return word[:-3]]
    S -- No --> U{len(word) > 4}
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
    >>> _remove_derivational("čtení")
    "čten"
    >>> _remove_derivational("příliš")
    "příl"
    >>> _remove_derivational("kniha")
    "knih"
    >>> _remove_derivational("obinec")
    "obinec"

## `sumy.nlp.stemmers.czech._palatalize` · *function*

## Summary:
Applies Czech palatalization transformations to word endings by replacing specific suffixes with their palatalized equivalents.

## Description:
This function implements morphological transformations for Czech words by applying palatalization rules based on word endings. It handles common Czech phonetic patterns where certain consonant clusters undergo palatalization. The function serves as a helper in Czech stemming operations, normalizing word forms according to linguistic rules.

## Args:
    word (str): The Czech word to be transformed. Must be a string with at least one character.

## Returns:
    str: The transformed word after applying the appropriate palatalization rule. Returns the original word with last character removed if no matching pattern is found.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - Input must be a string
    - String must have at least one character
    
    Postconditions:
    - Output is always a string
    - If input has length 1, output will be empty string (since it returns word[:-1])
    - Function is deterministic and idempotent for the same input

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
    >>> _palatalize("čtení")
    "čten"
    >>> _palatalize("příliš")
    "příl"
    >>> _palatalize("kniha")
    "knih"
    >>> _palatalize("kniha")
    "knih"

