# `scoring.py`

## `zxcvbn.scoring.calc_average_degree` · *function*

## Summary:
Calculates the average degree of nodes in a graph structure by counting non-empty neighbors for each node and averaging across all nodes.

## Description:
This function computes the average degree of a graph by iterating through all nodes (keys) in the graph dictionary and counting their non-empty neighbors. It's designed to work with graph representations where keys are nodes and values are lists of neighboring nodes. The function filters out empty neighbor entries and calculates the arithmetic mean of degrees across all nodes.

## Args:
    graph (dict): A dictionary representing a graph structure where keys are nodes and values are lists of neighboring nodes. Each neighbor entry should be a string or other hashable type.

## Returns:
    float: The average degree of all nodes in the graph, calculated as the total count of non-empty neighbors divided by the total number of nodes.

## Raises:
    None explicitly raised in the function body.

## Constraints:
    Preconditions:
    - The graph parameter must be a dictionary-like object with iterable values
    - Each value in the graph should be iterable (supporting iteration and len() operations)
    
    Postconditions:
    - Returns a float value representing the average degree
    - The result is always non-negative (assuming valid graph input)

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start calc_average_degree] --> B{graph.items()}
    B --> C[Initialize average = 0]
    C --> D[For each key, neighbors in graph.items()]
    D --> E{neighbors}
    E --> F[Count non-empty neighbors]
    F --> G[Add to average]
    G --> H[Increment counter]
    H --> I[End loop]
    I --> J[average /= len(graph.items())]
    J --> K[Return average]
```

## Examples:
    # Example usage with a simple graph
    graph = {
        'a': ['b', 'c', ''],
        'b': ['a', 'd'],
        'c': ['a']
    }
    avg_degree = calc_average_degree(graph)
    # Result would be (2 + 2 + 1) / 3 = 1.666...
```

## `zxcvbn.scoring.nCk` · *function*

## Summary:
Calculates the binomial coefficient "n choose k" (nCk), representing the number of ways to choose k items from n items without regard to order.

## Description:
This function computes the mathematical combination formula C(n,k) = n!/(k!(n-k)!). It's optimized to avoid computing large factorials directly by using an iterative multiplication and division approach that maintains numerical stability. This implementation is used in password strength estimation algorithms to calculate combinatorial possibilities.

## Args:
    n (int): Total number of items, must be a non-negative integer
    k (int): Number of items to choose, must be a non-negative integer and less than or equal to n

## Returns:
    float: The binomial coefficient C(n,k), which represents the number of combinations of n items taken k at a time

## Raises:
    None explicitly raised, but may encounter overflow issues with very large values of n and k due to floating-point arithmetic limitations

## Constraints:
    Preconditions:
    - n must be a non-negative integer
    - k must be a non-negative integer
    - k must be less than or equal to n (though the function handles k > n gracefully by returning 0)
    
    Postconditions:
    - Returns 0 when k > n (invalid combination)
    - Returns 1 when k == 0 (one way to choose zero items)
    - Returns a positive float value for valid inputs

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[nCk(n,k)] --> B{Is k > n?}
    B -->|Yes| C[return 0]
    B -->|No| D{Is k == 0?}
    D -->|Yes| E[return 1]
    D -->|No| F[r = 1]
    F --> G[for d in range(1, k+1)]
    G --> H[r *= n]
    H --> I[r /= d]
    I --> J[n -= 1]
    J --> K[return r]
```

## Examples:
    >>> nCk(5, 2)
    10.0
    
    >>> nCk(10, 0)
    1.0
    
    >>> nCk(3, 5)
    0

## `zxcvbn.scoring.most_guessable_match_sequence` · *function*

## Summary:
Finds the most guessable sequence of pattern matches for a password using dynamic programming to determine the optimal combination of matches that would be most likely for an attacker to discover.

## Description:
This function implements a dynamic programming algorithm to compute the minimum number of guesses required to crack a password by identifying the most probable sequence of pattern matches. It considers all possible ways to partition the password into pattern matches and selects the sequence that minimizes the total guessing effort.

The function processes pattern matches sorted by their ending position and builds an optimal solution incrementally. It handles both direct matches from the input and brute-force matches for all substrings, using a recursive approach to build sequences of increasing length. The function modifies match dictionaries in-place by adding 'guesses' and 'guesses_log10' keys through calls to estimate_guesses.

## Args:
    password (str): The password string to analyze for pattern matches
    matches (list[dict]): A list of pattern match dictionaries, each containing at least 'i' and 'j' indices indicating the match position in the password, and other pattern-specific fields
    _exclude_additive (bool): Internal flag to control whether to apply an additive penalty term in the dynamic programming calculation. When True, skips the MIN_GUESSES_BEFORE_GROWING_SEQUENCE addition. Defaults to False.

## Returns:
    dict: A dictionary containing:
        - 'password' (str): The input password
        - 'guesses' (Decimal): The minimum number of guesses required to crack the password using the optimal match sequence
        - 'guesses_log10' (float): The base-10 logarithm of the guess count
        - 'sequence' (list[dict]): The optimal sequence of pattern matches that would be most likely for an attacker to discover

## Raises:
    None explicitly raised - though TypeError may occur if matches contains non-dict elements due to the try/except block around the iteration.

## Constraints:
    Preconditions:
        - password must be a string
        - matches must be iterable (though the function handles TypeError gracefully)
        - Each match in matches must be a dictionary with at least 'i' and 'j' keys
    Postconditions:
        - Returns a dictionary with all required keys populated
        - The sequence represents a valid partitioning of the password
        - Guesses value is always positive (at least 1 for empty passwords)
        - Match dictionaries in the input list are modified in-place with 'guesses' and 'guesses_log10' keys

## Side Effects:
    - Modifies match dictionaries in-place by adding 'guesses' and 'guesses_log10' keys (via estimate_guesses function calls)
    - Uses logarithmic computation via math.log()

## Control Flow:
```mermaid
flowchart TD
    A[Start most_guessable_match_sequence] --> B[Initialize matches_by_j array]
    B --> C[Sort matches by ending position j]
    C --> D[Initialize optimal DP arrays]
    D --> E[Process each position k in password]
    E --> F{For each match m ending at k}
    F --> G{If match starts after 0}
    G -- Yes --> H[For each previous sequence length l]
    H --> I[Update with new sequence length l+1]
    G -- No --> J[Update with sequence length 1]
    J --> K[Call bruteforce_update(k)]
    K --> L[Unwind optimal sequence]
    L --> M[Calculate final guesses]
    M --> N[Return result dictionary]
```

## Examples:
    >>> password = "p@ssw0rd"
    >>> matches = [
    ...     {'pattern': 'bruteforce', 'token': 'p', 'i': 0, 'j': 0},
    ...     {'pattern': 'dictionary', 'token': 'pass', 'i': 1, 'j': 4}
    ... ]
    >>> result = most_guessable_match_sequence(password, matches)
    >>> print(result['guesses'])
    # Returns the minimum number of guesses for cracking the password
    
    >>> # With empty password
    >>> result = most_guessable_match_sequence("", [])
    >>> print(result['guesses'])
    # Returns 1 (minimum possible guesses)

## `zxcvbn.scoring.estimate_guesses` · *function*

## Summary:
Estimates the number of guesses required to crack a password pattern match using pattern-specific algorithms with minimum threshold enforcement.

## Description:
This function calculates the computational effort needed to guess a matched password pattern by applying specialized estimation algorithms based on the pattern type. It serves as a core component in password strength estimation systems, providing quantitative measures of password vulnerability. The function caches previously computed guesses and enforces minimum guess thresholds based on token length to ensure realistic estimates.

The function delegates to specialized estimation functions based on the match pattern type ('bruteforce', 'dictionary', 'spatial', 'repeat', 'sequence', 'regex', 'date') and applies minimum thresholds to prevent underestimation of guess counts for short tokens.

## Args:
    match (dict): A dictionary containing pattern matching information with keys:
        - 'pattern' (str): The type of pattern matched (e.g., 'bruteforce', 'dictionary')
        - 'token' (str): The matched password substring
        - 'guesses' (str, optional): Cached guess count if already computed
        - Additional keys required by specific estimation functions based on pattern type
    password (str): The full password string being analyzed

## Returns:
    Decimal: The estimated number of guesses required to crack the matched pattern, with a minimum threshold applied based on token length

## Raises:
    KeyError: If match dictionary lacks required keys for the specific pattern type
    TypeError: If match is not a dictionary or token is not a sequence
    KeyError: If match['pattern'] is not one of the supported pattern types

## Constraints:
    Preconditions:
        - match must be a dictionary containing at least 'token' and 'pattern' keys
        - match['pattern'] must be one of: 'bruteforce', 'dictionary', 'spatial', 'repeat', 'sequence', 'regex', 'date'
        - match['token'] must be a sequence (string, list, etc.)
        - If 'guesses' key exists, it must be convertible to a numeric type
    Postconditions:
        - Returns a Decimal value representing the minimum number of guesses
        - The returned value is at least the appropriate minimum threshold based on token length
        - The match dictionary is updated with 'guesses' and 'guesses_log10' keys

## Side Effects:
    - Modifies the input match dictionary by adding 'guesses' and 'guesses_log10' keys
    - Uses logarithmic computation via math.log()

## Control Flow:
```mermaid
flowchart TD
    A[estimate_guesses called] --> B{match has 'guesses'?}
    B -- Yes --> C[Return Decimal(match['guesses'])]
    B -- No --> D[Set min_guesses = 1]
    D --> E{len(match['token']) < len(password)?}
    E -- No --> F[Skip min_guesses adjustment]
    E -- Yes --> G{len(match['token']) == 1?}
    G -- Yes --> H[Set min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR]
    G -- No --> I[Set min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR]
    F --> J[Select estimation function by match['pattern']]
    H --> J
    I --> J
    J --> K[Call estimation function with match]
    K --> L[Set match['guesses'] = max(guesses, min_guesses)]
    L --> M[Set match['guesses_log10'] = log(match['guesses'], 10)]
    M --> N[Return Decimal(match['guesses'])]
```

## Examples:
    >>> match = {'pattern': 'bruteforce', 'token': 'a'}
    >>> password = 'password123'
    >>> estimate_guesses(match, password)
    # Returns Decimal value representing brute force guesses for token 'a'
    
    >>> match = {'pattern': 'dictionary', 'token': 'admin', 'rank': 100}
    >>> password = 'admin123'
    >>> estimate_guesses(match, password)
    # Returns Decimal value representing dictionary guesses for token 'admin'

## `zxcvbn.scoring.bruteforce_guesses` · *function*

## Summary:
Calculates the minimum number of brute force guesses required to crack a password token based on its length and character set.

## Description:
This function estimates the computational effort required for a brute force attack on a matched password token. It computes potential combinations using exponential growth based on character set size and token length, then applies minimum thresholds to ensure realistic estimates for both single-character and multi-character tokens. This function is used in password strength estimation algorithms to quantify the difficulty of guessing a particular token.

## Args:
    match (dict): A dictionary containing at least a 'token' key with the matched password substring

## Returns:
    int: The estimated number of brute force guesses required to crack the token, ensuring a minimum threshold is met

## Raises:
    KeyError: If the match dictionary doesn't contain a 'token' key
    TypeError: If match is not a dictionary or token is not a sequence

## Constraints:
    Preconditions:
        - match must be a dictionary containing a 'token' key
        - match['token'] must be a sequence (string, list, etc.)
    Postconditions:
        - Returns an integer >= 1
        - Returns at least the minimum guesses threshold for the token length

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start bruteforce_guesses] --> B{len(token) == 1?}
    B -->|Yes| C[Set min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR + 1]
    B -->|No| D[Set min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR + 1]
    E[Calculate guesses = BRUTEFORCE_CARDINALITY ^ len(token)]
    C --> F[Return max(guesses, min_guesses)]
    D --> F
    E --> F
```

## Examples:
    >>> match = {'token': 'a'}
    >>> bruteforce_guesses(match)
    # Returns max(character_set_size^1, minimum_single_char_guesses)
    
    >>> match = {'token': 'ab'}
    >>> bruteforce_guesses(match)
    # Returns max(character_set_size^2, minimum_multi_char_guesses)
```

## `zxcvbn.scoring.dictionary_guesses` · *function*

## Summary
Calculates the total number of dictionary-based guesses required for a password token by combining base rank with various transformation variations.

## Description
This function computes the total number of possible guesses needed to brute-force a dictionary word token by accounting for multiple transformation variants including case variations, l33t-speak substitutions, and reversal patterns. It serves as a core component in the zxcvbn password strength estimation algorithm, quantifying the computational effort required to crack dictionary-based passwords.

The function integrates with other variation calculation functions (`uppercase_variations` and `l33t_variations`) to provide a comprehensive estimate of guessable combinations for dictionary matches. It's typically called during the password strength analysis phase when evaluating dictionary-based patterns.

## Args
    match (dict): A dictionary containing password matching information with the following required keys:
        - 'rank' (int): The position of the token in the dictionary (used as base_guesses)
        - 'reversed' (bool, optional): Indicates if the token was found in reverse order (defaults to False)
        - Additional keys required by `uppercase_variations` and `l33t_variations` functions

## Returns
    int: The total number of possible guess combinations for the dictionary token, calculated as:
        base_guesses × uppercase_variations × l33t_variations × reversed_variations

## Raises
    KeyError: If the 'rank' key is missing from the match dictionary
    TypeError: If match is not a dictionary or contains incompatible data types

## Constraints
    Preconditions:
    - The match parameter must be a dictionary containing at least the 'rank' key
    - The 'rank' value must be a numeric type (int or float)
    - The 'reversed' key, if present, must be a boolean value
    
    Postconditions:
    - Returns a positive integer representing total guess combinations
    - The result accounts for all applicable transformations (case, l33t, reversal)

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[dictionary_guesses(match)] --> B[Set base_guesses = match['rank']]
    B --> C[Set uppercase_variations = uppercase_variations(match)]
    C --> D[Set l33t_variations = l33t_variations(match)]
    D --> E[Set reversed_variations = 2 if match.get('reversed', False) else 1]
    E --> F[Return base_guesses × uppercase_variations × l33t_variations × reversed_variations]
```

## `zxcvbn.scoring.repeat_guesses` · *function*

## Summary:
Calculates the total number of guesses required for a repeated character pattern by multiplying base guesses with the repeat count.

## Description:
This function computes the guess count for repeated character patterns in password strength estimation. It's used in the zxcvbn algorithm to quantify how many attempts an attacker would need to make to guess a repeated character sequence.

## Args:
    match (dict): A dictionary containing pattern matching information with the following keys:
        - 'base_guesses' (numeric): The base number of guesses required for the pattern type
        - 'repeat_count' (numeric): The number of times the character is repeated

## Returns:
    Decimal: The total number of guesses required for the repeated pattern, calculated as base_guesses multiplied by repeat_count

## Raises:
    KeyError: If the match dictionary is missing either 'base_guesses' or 'repeat_count' keys
    TypeError: If base_guesses or repeat_count cannot be converted to numeric values for multiplication

## Constraints:
    Preconditions:
        - The match parameter must be a dictionary containing both 'base_guesses' and 'repeat_count' keys
        - Both 'base_guesses' and 'repeat_count' must be convertible to numeric values
    Postconditions:
        - Returns a Decimal value representing the total guess count for the repeated pattern

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[repeat_guesses called] --> B{match dict has keys?}
    B -- No --> C[KeyError raised]
    B -- Yes --> D[Convert repeat_count to Decimal]
    D --> E[Multiply base_guesses × Decimal(repeat_count)]
    E --> F[Return result]
```

## Examples:
    >>> match = {'base_guesses': 10, 'repeat_count': 3}
    >>> repeat_guesses(match)
    Decimal('30')
    
    >>> match = {'base_guesses': 5, 'repeat_count': 1.5}
    >>> repeat_guesses(match)
    Decimal('7.5')

## `zxcvbn.scoring.sequence_guesses` · *function*

## Summary:
Calculates the number of possible guesses for sequential character patterns in password strength estimation.

## Description:
This function computes the base guess count for sequential character patterns based on the first character of the sequence and whether the sequence is ascending. It's used in password strength estimation algorithms to determine how many attempts an attacker would need to make to guess a sequential pattern.

The function is typically called during the password strength analysis phase when sequential patterns (like 'abc', '123', 'zyx') have been identified in a password.

## Args:
    match (dict): A dictionary containing pattern match information with keys:
        - 'token' (str): The sequential character string being analyzed
        - 'ascending' (bool): Whether the sequence is in ascending order

## Returns:
    int: The estimated number of possible guesses for the sequential pattern

## Raises:
    KeyError: If 'token' or 'ascending' keys are missing from the match dictionary

## Constraints:
    Preconditions:
        - The match dictionary must contain 'token' and 'ascending' keys
        - The token must be a non-empty string
    Postconditions:
        - Returns a positive integer representing guess count
        - The result accounts for both ascending and descending sequences

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start sequence_guesses] --> B{first_chr in ['a','A','z','Z','0','1','9']}
    B -- Yes --> C[base_guesses = 4]
    B -- No --> D{first_chr is digit}
    D -- Yes --> E[base_guesses = 10]
    D -- No --> F[base_guesses = 26]
    C --> G{not match['ascending']}
    E --> G
    F --> G
    G -- Yes --> H[base_guesses *= 2]
    G -- No --> I[base_guesses unchanged]
    H --> I
    I --> J[return base_guesses * len(match['token'])]
```

## Examples:
    >>> match = {'token': 'abc', 'ascending': True}
    >>> sequence_guesses(match)
    78
    
    >>> match = {'token': 'cba', 'ascending': False}
    >>> sequence_guesses(match)
    52
```

## `zxcvbn.scoring.regex_guesses` · *function*

## Summary:
Computes the number of possible guesses needed to crack a regex-matched token in password strength estimation.

## Description:
This function calculates the entropy (guess count) for a matched token based on its regex pattern classification. It's used in the zxcvbn password strength estimator to quantify how difficult a particular pattern is to guess. The function specifically handles character class patterns and recent year patterns.

## Args:
    match (dict): A dictionary containing match information with the following expected keys:
        - 'regex_name' (str): Name of the regex pattern matched
        - 'token' (str): The matched string token
        - 'regex_match' (re.Match): The regex match object (for recent_year pattern)

## Returns:
    int: The estimated number of guesses needed to crack the matched token.
         For character class patterns: base^length where base is the character set size.
         For recent year patterns: calculated year space from reference year.

## Raises:
    KeyError: If match dictionary is missing required keys.
    AttributeError: If regex_match doesn't have group() method (for recent_year case).
    ValueError: If regex_match.group(0) cannot be converted to integer (for recent_year case).

## Constraints:
    Preconditions:
        - match dictionary must contain 'regex_name', 'token', and 'regex_match' keys
        - For recent_year pattern, regex_match must be a valid re.Match object with group(0) returning a parseable integer
    Postconditions:
        - Returns a positive integer representing guess count
        - For character classes, result is at least 1 (even for empty tokens)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start regex_guesses] --> B{regex_name in char_class_bases?}
    B -- Yes --> C[Return base^len(token)]
    B -- No --> D{regex_name == 'recent_year'?}
    D -- Yes --> E[Calculate year_space]
    D -- No --> F[Raise KeyError or return None]
    C --> G[End]
    E --> G
    F --> G
```

## Examples:
    # Character class example
    match = {'regex_name': 'digits', 'token': '123', 'regex_match': None}
    result = regex_guesses(match)  # Returns 10^3 = 1000
    
    # Recent year example  
    match = {'regex_name': 'recent_year', 'token': '2023', 'regex_match': re.match(r'\d{4}', '2023')}
    result = regex_guesses(match)  # Returns calculated year space value
```

## `zxcvbn.scoring.date_guesses` · *function*

*No documentation generated.*

## `zxcvbn.scoring.spatial_guesses` · *function*

*No documentation generated.*

## `zxcvbn.scoring.uppercase_variations` · *function*

## Summary
Calculates the number of possible uppercase/lowercase variations for a given word token in password strength estimation.

## Description
This function determines the combinatorial possibilities of different uppercase and lowercase letter arrangements within a word token. It's used in the zxcvbn password strength estimation algorithm to compute the number of guesses required to brute-force a password containing the given token.

The function categorizes tokens into different patterns and applies appropriate calculation methods:
1. All lowercase tokens return 1 variation (no uppercase changes possible)
2. Tokens matching specific patterns (start upper, end upper, all upper) return 2 variations
3. Other tokens use combinatorial mathematics to calculate all possible arrangements

## Args
    match (dict): A dictionary containing at least a 'token' key with the word string to analyze

## Returns
    int: The number of possible uppercase/lowercase variations for the token

## Raises
    None explicitly raised

## Constraints
    Preconditions:
    - The match parameter must be a dictionary containing a 'token' key
    - The token value must be a string
    
    Postconditions:
    - Returns a positive integer representing variation count
    - For tokens with no uppercase letters, returns 1
    - For tokens with predictable patterns, returns 2
    - For complex mixed-case tokens, returns calculated combinatorial value

## Side Effects
    None

## Control Flow
```mermaid
flowchart TD
    A[uppercase_variations(match)] --> B{ALL_LOWER.match(word) OR word.lower() == word?}
    B -->|Yes| C[return 1]
    B -->|No| D[for regex in [START_UPPER, END_UPPER, ALL_UPPER]]
    D --> E{regex.match(word)?}
    E -->|Yes| F[return 2]
    E -->|No| G[U = sum(isupper)]
    G --> H[L = sum(islower)]
    H --> I[variations = 0]
    I --> J[i = 1 to min(U,L)+1]
    J --> K[variations += nCk(U+L, i)]
    K --> L[return variations]
```

## Examples
    >>> uppercase_variations({'token': 'password'})
    1
    
    >>> uppercase_variations({'token': 'Password'})
    2
    
    >>> uppercase_variations({'token': 'PASSWORD'})
    2
    
    >>> uppercase_variations({'token': 'PassWord'})
    15
```

## `zxcvbn.scoring.l33t_variations` · *function*

## Summary:
Calculates the number of possible variations for l33t-speak substitutions in a password token.

## Description:
This function computes the combinatorial possibilities of l33t-speak character substitutions (like replacing 'a' with '@') within a matched password token. It's used in the zxcvbn password strength estimation algorithm to quantify how many different ways a given token could be written using various character substitutions.

The function analyzes each substitution pair in the match's 'sub' dictionary and calculates how many ways the substituted and unsubstituted characters can appear in the token, considering all possible combinations of positions.

## Args:
    match (dict): A dictionary containing password matching information with keys:
        - 'l33t' (bool): Flag indicating if the match involves l33t-speak substitutions
        - 'sub' (dict): Dictionary mapping substituted characters to their original forms
        - 'token' (str): The original password token being analyzed

## Returns:
    int: The total number of possible variation combinations for all l33t substitutions in the token. Returns 1 if no l33t substitutions are present.

## Raises:
    None explicitly raised, but may encounter issues with very large computations due to the nature of combination calculations.

## Constraints:
    Preconditions:
    - The match parameter must be a dictionary with required keys ('l33t', 'sub', 'token')
    - The 'sub' key must be a dictionary mapping characters to their substitutes
    - The 'token' key must be a string
    
    Postconditions:
    - Returns an integer value >= 1
    - If 'l33t' is False, returns 1 without processing further

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start l33t_variations] --> B{match['l33t'] is False?}
    B -->|Yes| C[Return 1]
    B -->|No| D[Initialize variations = 1]
    D --> E[For each subbed, unsubbed in match['sub'].items()]
    E --> F[Get token characters as lowercase list]
    F --> G[Count occurrences of subbed character]
    G --> H[Count occurrences of unsubbed character]
    H --> I{S == 0 OR U == 0?}
    I -->|Yes| J[variations *= 2]
    I -->|No| K[Calculate p = min(U,S)]
    K --> L[Initialize possibilities = 0]
    L --> M[For i in range(1, p+1)]
    M --> N[possibilities += nCk(U+S, i)]
    N --> O[variations *= possibilities]
    O --> P[Next substitution]
    P --> Q[Return variations]
```

## Examples:
    >>> match = {'l33t': True, 'sub': {'@': 'a'}, 'token': 'p@ssw0rd'}
    >>> l33t_variations(match)
    # Calculates variations for '@' -> 'a' substitution in 'p@ssw0rd'
    
    >>> match = {'l33t': False, 'sub': {}, 'token': 'password'}
    >>> l33t_variations(match)
    1
```

