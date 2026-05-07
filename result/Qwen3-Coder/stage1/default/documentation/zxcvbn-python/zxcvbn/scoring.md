# `scoring.py`

## `zxcvbn.scoring.calc_average_degree` · *function*

## Summary:
Calculates the average degree of nodes in a graph structure by counting non-empty neighbors for each node.

## Description:
This function computes the average degree of nodes in a graph representation, where each node is connected to a set of neighbors. It's used in password strength estimation to analyze keyboard patterns and common sequences. The function processes a graph structure where nodes represent characters and edges represent adjacency relationships.

## Args:
    graph (dict): A dictionary-like structure where keys represent nodes and values are lists of neighboring nodes. Each neighbor value may be None or empty, which are filtered out during calculation.

## Returns:
    float: The average degree of all nodes in the graph, calculated as the total count of non-empty neighbors divided by the total number of nodes.

## Raises:
    ZeroDivisionError: When the input graph is empty (contains no items), causing division by zero.

## Constraints:
    Preconditions:
        - The graph parameter must be iterable with .items() method
        - Each value in the graph must be iterable (neighbors list)
        - Graph must contain at least one item to avoid division by zero
    
    Postconditions:
        - Returns a floating-point number representing average degree
        - The result is always non-negative for valid inputs

## Side Effects:
    None: This function has no side effects and is pure.

## Control Flow:
```mermaid
flowchart TD
    A[Start calc_average_degree] --> B{graph.items() empty?}
    B -- Yes --> C[ZeroDivisionError]
    B -- No --> D[Initialize average = 0]
    D --> E[Iterate through graph.items()]
    E --> F{neighbors list}
    F --> G[Count non-empty neighbors]
    G --> H[Add to average]
    H --> I[Loop for all items]
    I --> J[average /= len(graph.items())]
    J --> K[Return average]
```

## Examples:
    >>> calc_average_degree({'a': ['b', 'c'], 'b': ['a', 'd']})
    2.0
    
    >>> calc_average_degree({'x': [], 'y': ['z']})
    0.5

## `zxcvbn.scoring.nCk` · *function*

## Summary:
Computes the mathematical combination n choose k (nCk) using an efficient iterative algorithm.

## Description:
This function calculates the binomial coefficient C(n,k) = n!/(k!(n-k)!) without computing large factorials directly, which helps prevent overflow issues. It's used internally by the zxcvbn password strength estimator for calculating combinatorial values in entropy computations.

## Args:
    n (int): Total number of items in the set, must be non-negative
    k (int): Number of items to choose from the set, must be non-negative

## Returns:
    int: The number of ways to choose k items from n items, or 0 if k > n

## Raises:
    None: This function does not raise any exceptions

## Constraints:
    Preconditions: Both n and k must be non-negative integers
    Postconditions: Returns an integer value representing the combination count

## Side Effects:
    None: This function has no side effects

## Control Flow:
```mermaid
flowchart TD
    A[Start nCk(n,k)] --> B{Is k > n?}
    B -- Yes --> C[Return 0]
    B -- No --> D{Is k == 0?}
    D -- Yes --> E[Return 1]
    D -- No --> F[Initialize r = 1]
    F --> G[For d in range(1, k+1)]
    G --> H[r *= n]
    H --> I[r /= d]
    I --> J[n -= 1]
    J --> K[Return r]
```

## Examples:
    >>> nCk(5, 2)
    10
    >>> nCk(10, 0)
    1
    >>> nCk(3, 5)
    0

## `zxcvbn.scoring.most_guessable_match_sequence` · *function*

## Summary:
Computes the most guessable match sequence for a password by finding the optimal combination of pattern matches that minimizes total guess count using dynamic programming.

## Description:
This function implements a dynamic programming algorithm to determine the most guessable sequence of pattern matches for a given password. It evaluates all possible combinations of matches to find the one requiring the fewest guesses to crack, making it a core component of the zxcvbn password strength estimation system.

The function processes matches grouped by their ending position, then uses dynamic programming to build optimal sequences incrementally. It considers both direct matches and brute-force matches to construct the minimal guess sequence.

This logic is extracted into its own function to separate the complex optimization algorithm from the higher-level password analysis workflow, enabling reuse and clearer separation of concerns in the password strength estimation pipeline.

## Args:
    password (str): The password string to analyze
    matches (list[dict]): List of pattern match dictionaries, each containing at least 'i' and 'j' indices indicating match positions
    _exclude_additive (bool): Internal flag to control additive factor in guess calculation. Defaults to False.

## Returns:
    dict: A dictionary containing:
        - 'password' (str): The input password
        - 'guesses' (Decimal): The total number of guesses required for the most guessable sequence
        - 'guesses_log10' (float): Logarithm base 10 of the guess count
        - 'sequence' (list[dict]): The optimal match sequence as a list of match dictionaries

## Raises:
    None explicitly raised - handles TypeError in match processing gracefully

## Constraints:
    Preconditions:
        - password must be a string
        - matches must be iterable (though handles TypeError gracefully)
        - Each match in matches must be a dictionary with 'i' and 'j' keys
    Postconditions:
        - Returns a dictionary with all required keys
        - The sequence represents a valid partition of the password
        - Guesses value is a positive Decimal

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start most_guessable_match_sequence] --> B[Initialize matches_by_j]
    B --> C[Group matches by ending position j]
    C --> D[Initialize optimal DP arrays]
    D --> E[Process each position k from 0 to n-1]
    E --> F[For each match ending at k]
    F --> G{Match starts at 0?}
    G -->|Yes| H[Update with l=1]
    G -->|No| I[For each previous optimal sequence l]
    I --> J[Update with l+1]
    J --> K[Call bruteforce_update(k)]
    K --> L[Unwind optimal sequence]
    L --> M[Calculate final guesses]
    M --> N[Return result dictionary]
```

## Examples:
    # Basic usage with matches
    matches = [
        {'pattern': 'bruteforce', 'token': 'abc', 'i': 0, 'j': 2},
        {'pattern': 'dictionary', 'token': 'password', 'i': 3, 'j': 9}
    ]
    result = most_guessable_match_sequence("abcpassword", matches)
    print(result['guesses'])  # Estimated guess count
    print(result['sequence'])  # Optimal match sequence

## `zxcvbn.scoring.estimate_guesses` · *function*

## Summary:
Estimates the number of guesses required to crack a password pattern match by applying pattern-specific calculations and enforcing minimum guess thresholds.

## Description:
This function serves as the central estimator in the zxcvbn password strength analysis system, computing the computational effort needed to brute-force a matched password pattern. It routes to specialized estimation functions based on pattern type while enforcing minimum guess thresholds to prevent underestimation of weak patterns.

The function is extracted from inline calculations to provide a clean separation of concerns, allowing the password strength estimation to modularly compute different pattern types independently while maintaining a unified interface for guess calculation. This design enables the system to handle various password patterns (brute force, dictionary, spatial, etc.) with appropriate estimation methods.

## Args:
    match (dict): A dictionary containing pattern matching information with keys:
        - 'pattern' (str): The type of pattern matched (one of: 'bruteforce', 'dictionary', 'spatial', 'repeat', 'sequence', 'regex', 'date')
        - 'token' (str): The matched substring from the password
        - 'guesses' (int, optional): Pre-computed guess count (if present, function returns early)
        - Additional pattern-specific keys required by the respective estimation functions
    password (str): The full password string being analyzed

## Returns:
    Decimal: The estimated number of guesses required to crack the matched pattern, ensuring a minimum threshold is met

## Raises:
    KeyError: If match dictionary lacks required keys for the selected estimation function
    TypeError: If match is not a dictionary or token is not a string/sequence
    KeyError: If match dictionary lacks required keys for pattern-specific estimations

## Constraints:
    Preconditions:
        - match must be a dictionary with required keys for the pattern type
        - match['token'] must be a sequence (string, list, etc.) with a defined length
        - match['pattern'] must be one of the supported pattern types
        - password must be a string
    Postconditions:
        - Returns a Decimal value representing the estimated guess count
        - match dictionary will have 'guesses' and 'guesses_log10' keys added
        - The returned value is at least the minimum threshold based on token length

## Side Effects:
    - Modifies the input match dictionary by adding 'guesses' and 'guesses_log10' keys
    - Uses logarithmic calculations via math.log function

## Control Flow:
```mermaid
flowchart TD
    A[Start estimate_guesses] --> B{match has 'guesses'?}
    B -->|Yes| C[Return Decimal(match['guesses'])]
    B -->|No| D[Set min_guesses = 1]
    D --> E{len(match['token']) < len(password)?}
    E -->|Yes| F{len(match['token']) == 1?}
    F -->|Yes| G[Set min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR]
    F -->|No| H[Set min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR]
    E -->|No| I[Skip min_guesses adjustment]
    G --> J[Select estimation function by match['pattern']]
    H --> J
    I --> J
    J --> K[Call estimation function with match]
    K --> L[Set match['guesses'] = max(guesses, min_guesses)]
    L --> M[Set match['guesses_log10'] = log(match['guesses'], 10)]
    M --> N[Return Decimal(match['guesses'])]
```

## `zxcvbn.scoring.bruteforce_guesses` · *function*

## Summary:
Calculates the number of brute force guesses required to crack a password token based on cardinality and minimum guess thresholds.

## Description:
This function computes the brute force guess count for a matched token in password strength estimation. It calculates potential combinations based on the token's character set cardinality and applies minimum thresholds to ensure realistic guess estimates. The function is part of the zxcvbn password strength estimation algorithm.

## Args:
    match (dict): A dictionary containing match information with a 'token' key representing the matched password portion

## Returns:
    int: The estimated number of brute force guesses required to crack the token, ensuring a minimum threshold is met

## Raises:
    KeyError: If the match dictionary doesn't contain a 'token' key
    TypeError: If match is not a dictionary or token is not a string/sequence

## Constraints:
    Preconditions:
        - match must be a dictionary containing a 'token' key
        - match['token'] must be a sequence (string, list, etc.) with a defined length
    Postconditions:
        - Returns an integer >= 1
        - Returns at least the minimum guess threshold for the token length

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start bruteforce_guesses] --> B{len(token) == 1?}
    B -->|Yes| C[Set min_guesses = MIN_SUBMATCH_GUESSES_SINGLE_CHAR + 1]
    B -->|No| D[Set min_guesses = MIN_SUBMATCH_GUESSES_MULTI_CHAR + 1]
    C --> E[guesses = BRUTEFORCE_CARDINALITY ^ len(token)]
    D --> E
    E --> F[Return max(guesses, min_guesses)]
```

## Examples:
    >>> match = {'token': 'a'}
    >>> bruteforce_guesses(match)
    # Returns max(BRUTEFORCE_CARDINALITY^1, MIN_SUBMATCH_GUESSES_SINGLE_CHAR + 1)
    
    >>> match = {'token': 'ab'}
    >>> bruteforce_guesses(match)
    # Returns max(BRUTEFORCE_CARDINALITY^2, MIN_SUBMATCH_GUESSES_MULTI_CHAR + 1)

## `zxcvbn.scoring.dictionary_guesses` · *function*

## Summary:
Calculates the total number of dictionary-based guesses required for a password pattern match, accounting for various character variations.

## Description:
This function computes the total number of possible guesses needed to crack a dictionary-based password pattern by combining base dictionary rank with variations for uppercase letters, l33t substitutions, and reversed patterns. It serves as a core component in the zxcvbn password strength estimation algorithm, quantifying the computational effort required to brute-force dictionary-based passwords.

The function is extracted from inline calculations to provide a clean separation of concerns, allowing the password strength estimation to modularly compute different types of variations independently while maintaining a unified interface for guess calculation.

## Args:
    match (dict): A dictionary containing pattern matching information with the following keys:
        - 'rank' (int): The position of the matched word in the dictionary (base guesses)
        - 'token' (str): The matched string being analyzed
        - 'reversed' (bool, optional): Whether the pattern was found in reverse order
        - 'l33t' (bool, optional): Whether the match involves l33t substitutions
        - 'sub' (dict, optional): Mapping of substituted characters to their original forms

## Returns:
    int: The total number of possible guess combinations for the dictionary match, calculated as:
        base_guesses × uppercase_variations × l33t_variations × reversed_variations

## Raises:
    None: This function does not explicitly raise exceptions.

## Constraints:
    Preconditions:
        - The match parameter must be a dictionary with required keys ('rank', 'token')
        - The match dictionary must contain the keys that are accessed in the function
        
    Postconditions:
        - Returns a positive integer representing the total number of guess combinations

## Side Effects:
    - Calls external functions uppercase_variations and l33t_variations
    - May modify the input match dictionary by adding intermediate calculation results

## Control Flow:
```mermaid
flowchart TD
    A[Start dictionary_guesses(match)] --> B[Set base_guesses = match['rank']]
    B --> C[Calculate uppercase_variations = uppercase_variations(match)]
    C --> D[Calculate l33t_variations = l33t_variations(match)]
    D --> E[Calculate reversed_variations = 2 if match.get('reversed') else 1]
    E --> F[Return base_guesses × uppercase_variations × l33t_variations × reversed_variations]
```

## Examples:
    >>> match = {
    ...     'rank': 1000,
    ...     'token': 'Password',
    ...     'reversed': False,
    ...     'l33t': True,
    ...     'sub': {'3': 'e'}
    ... }
    >>> dictionary_guesses(match)
    # Returns 1000 * uppercase_variations_result * l33t_variations_result * 1
    
    >>> match = {
    ...     'rank': 5000,
    ...     'token': 'hello',
    ...     'reversed': True
    ... }
    >>> dictionary_guesses(match)
    # Returns 5000 * uppercase_variations_result * 1 * 2

## `zxcvbn.scoring.repeat_guesses` · *function*

## Summary:
Calculates the number of guesses required for a repeated character pattern by multiplying base guesses with repeat count.

## Description:
This function computes the guess count for repeated character patterns in password strength estimation. It's used in the zxcvbn algorithm to quantify how many attempts an attacker would need to guess a repeated character sequence.

## Args:
    match (dict): A dictionary containing pattern matching information with keys:
        - 'base_guesses' (numeric): The base number of guesses required for the pattern type
        - 'repeat_count' (numeric): The number of times a character is repeated consecutively

## Returns:
    Decimal: The total number of guesses required for the repeated character pattern, calculated as base_guesses multiplied by repeat_count

## Raises:
    KeyError: If either 'base_guesses' or 'repeat_count' keys are missing from the match dictionary
    TypeError: If match is not a dictionary or if the values cannot be converted to numeric types

## Constraints:
    Preconditions:
        - match must be a dictionary containing 'base_guesses' and 'repeat_count' keys
        - Both 'base_guesses' and 'repeat_count' must be convertible to numeric types
    Postconditions:
        - Returns a Decimal value representing the total guess count for the repeated pattern

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[repeat_guesses called] --> B{match dict valid?}
    B -->|No| C[KeyError raised]
    B -->|Yes| D[Convert repeat_count to Decimal]
    D --> E[Multiply base_guesses × Decimal(repeat_count)]
    E --> F[Return result]
```

## Examples:
    >>> match = {'base_guesses': 10, 'repeat_count': 3}
    >>> repeat_guesses(match)
    Decimal('30')
    
    >>> match = {'base_guesses': 5, 'repeat_count': 1}
    >>> repeat_guesses(match)
    Decimal('5')

## `zxcvbn.scoring.sequence_guesses` · *function*

## Summary:
Calculates the number of possible guesses needed to crack a sequential character pattern in a password.

## Description:
This function estimates the brute-force search space for sequential character patterns such as keyboard sequences, numeric progressions, or alphabetical sequences. It's used in the zxcvbn password strength estimation algorithm to compute how many attempts an attacker would need to make to guess a sequential token.

The function analyzes the first character of a matched token to determine the base character set size (4, 10, or 26), then multiplies by the token length to estimate the total search space. For non-ascending sequences, it doubles the base guess count.

## Args:
    match (dict): A dictionary containing match information with:
        - 'token' (str): The sequential character pattern to analyze
        - 'ascending' (bool): Whether the sequence follows ascending order

## Returns:
    int: The estimated number of possible guesses needed to crack the sequential pattern, calculated as base_guesses * len(token) where:
        - base_guesses = 4 if first character is in ['a', 'A', 'z', 'Z', '0', '1', '9']
        - base_guesses = 10 if first character is a digit
        - base_guesses = 26 if first character is a letter (non-special case)
        - If not ascending, base_guesses is doubled before multiplication

## Raises:
    KeyError: If the match dictionary doesn't contain required keys ('token' or 'ascending').
    TypeError: If match is not a dictionary, or if 'token' is not a string, or if 'ascending' is not a boolean.

## Constraints:
    Preconditions:
    - The match parameter must be a dictionary containing 'token' and 'ascending' keys
    - The 'token' value must be a string
    - The 'ascending' value must be a boolean
    
    Postconditions:
    - Returns a positive integer representing the estimated guess count
    - The result is at least equal to the length of the token

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start sequence_guesses] --> B{First char in ['a','A','z','Z','0','1','9']}
    B -- Yes --> C[base_guesses = 4]
    B -- No --> D{First char is digit}
    D -- Yes --> E[base_guesses = 10]
    D -- No --> F[base_guesses = 26]
    C --> G{match['ascending'] is False}
    E --> G
    F --> G
    G -- Yes --> H[base_guesses = base_guesses * 2]
    G -- No --> I[Skip multiplier]
    H --> J[Return base_guesses * len(token)]
    I --> J
```

## Examples:
    >>> sequence_guesses({'token': 'abc', 'ascending': True})
    78  # 26 * 3 (alphabetical sequence)
    
    >>> sequence_guesses({'token': '123', 'ascending': True})
    30  # 10 * 3 (numeric sequence)
    
    >>> sequence_guesses({'token': 'xyz', 'ascending': False})
    52  # 26 * 2 * 1 (non-ascending alphabetical)
    
    >>> sequence_guesses({'token': 'az', 'ascending': True})
    8   # 4 * 2 (special case first char 'a')
```

## `zxcvbn.scoring.regex_guesses` · *function*

## Summary:
Calculates the number of possible guesses needed to crack a password pattern matched by a regular expression.

## Description:
This function computes the entropy (guess count) for password patterns identified by regex matching in the zxcvbn password strength estimation algorithm. It handles two main categories of patterns: character class patterns that have predetermined base sizes, and recent year patterns that calculate guesses based on temporal distance from a reference year. The function expects specific regex patterns to be matched and will raise exceptions for unsupported patterns.

## Args:
    match (dict): A dictionary containing regex match information with the following required keys:
        - 'regex_name' (str): Name of the regex pattern matched (must be one of: 'alpha_lower', 'alpha_upper', 'alpha', 'alphanumeric', 'digits', 'symbols', 'recent_year')
        - 'token' (str): The matched string token
        - 'regex_match' (re.Match): The regex match object (for recent_year pattern)

## Returns:
    int: The estimated number of guesses required to crack the pattern. For character class patterns, returns base^length where base is the character set size from char_class_bases. For recent year patterns, returns the absolute difference from REFERENCE_YEAR, clamped to at least MIN_YEAR_SPACE.

## Raises:
    KeyError: If required keys ('regex_name', 'token', or 'regex_match') are missing from the match dictionary.
    ValueError: If 'regex_match' group 0 cannot be converted to an integer for recent_year pattern.
    AttributeError: If 'regex_match' is None or does not have a group() method.

## Constraints:
    Preconditions:
        - The match dictionary must contain 'regex_name', 'token', and 'regex_match' keys
        - For 'recent_year' patterns, 'regex_match' must be a valid regex match object with group(0) containing a numeric string
        - The 'regex_name' must be one of the supported pattern types ('alpha_lower', 'alpha_upper', 'alpha', 'alphanumeric', 'digits', 'symbols', 'recent_year')
    
    Postconditions:
        - Returns an integer representing the guess count or year space
        - For character class patterns, returns base^len(token) where base is the character set size from char_class_bases
        - For recent year patterns, returns the calculated year space (absolute difference from REFERENCE_YEAR) or MIN_YEAR_SPACE if smaller
        - For unsupported patterns, the behavior is undefined (function will implicitly return None)

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start regex_guesses] --> B{regex_name in char_class_bases?}
    B -- Yes --> C[Return char_class_bases[regex_name] ^ len(token)]
    B -- No --> D{regex_name == 'recent_year'?}
    D -- Yes --> E[Get year from regex_match.group(0)]
    E --> F[Calculate year_space = abs(year - REFERENCE_YEAR)]
    F --> G[year_space = max(year_space, MIN_YEAR_SPACE)]
    G --> H[Return year_space]
    D -- No --> I[Function returns None (undefined behavior)]
```

## Examples:
    # Character class pattern
    match = {'regex_name': 'digits', 'token': '1234'}
    guesses = regex_guesses(match)  # Returns 10^4 = 10000
    
    # Recent year pattern  
    match = {'regex_name': 'recent_year', 'token': '2023', 'regex_match': re.match(r'\d{4}', '2023')}
    guesses = regex_guesses(match)  # Returns abs(2023 - REFERENCE_YEAR) or MIN_YEAR_SPACE

## `zxcvbn.scoring.date_guesses` · *function*

## Summary:
Calculates the number of possible guesses needed to crack a date pattern in password strength estimation.

## Description:
This function estimates the computational effort required to brute-force a date pattern by calculating the number of potential year combinations. It's part of the zxcvbn password strength estimator that analyzes common patterns in passwords.

## Args:
    match (dict): A dictionary containing at least a 'year' key with an integer year value, and optionally a 'separator' key indicating if the date had a separator character.

## Returns:
    int: The estimated number of guesses required to crack the date pattern, calculated as year space multiplied by 365 days, with an optional multiplier of 4 if a separator was present.

## Raises:
    KeyError: If the match dictionary doesn't contain a 'year' key.
    TypeError: If match is not a dictionary or if the 'year' value is not numeric.

## Constraints:
    Preconditions:
        - The match parameter must be a dictionary containing a 'year' key with a numeric value
        - REFERENCE_YEAR and MIN_YEAR_SPACE constants must be defined in the module scope
        - The match dictionary may optionally contain a 'separator' key with boolean value
    Postconditions:
        - Returns a positive integer representing the estimated guess count for the date pattern
        - The returned value is at least 365 (MIN_YEAR_SPACE * 365) due to the min constraint

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start date_guesses] --> B{match has 'year'?}
    B -- No --> C[Raise KeyError]
    B -- Yes --> D[Calculate year_space = max(abs(match['year'] - REFERENCE_YEAR), MIN_YEAR_SPACE)]
    D --> E[Calculate guesses = year_space * 365]
    E --> F{match.get('separator', False)?}
    F -- Yes --> G[guesses *= 4]
    F -- No --> H[Return guesses]
    G --> H
```

## Examples:
    >>> match = {'year': 2020}
    >>> date_guesses(match)
    # Returns year_space * 365 where year_space = max(abs(2020 - REFERENCE_YEAR), MIN_YEAR_SPACE)
    
    >>> match = {'year': 2020, 'separator': True}
    >>> date_guesses(match)
    # Returns (year_space * 365) * 4 where year_space = max(abs(2020 - REFERENCE_YEAR), MIN_YEAR_SPACE)
    
    >>> match = {'year': 2000, 'separator': False}
    >>> date_guesses(match)
    # Returns year_space * 365 where year_space = max(abs(2000 - REFERENCE_YEAR), MIN_YEAR_SPACE)

## `zxcvbn.scoring.spatial_guesses` · *function*

*No documentation generated.*

## `zxcvbn.scoring.uppercase_variations` · *function*

*No documentation generated.*

## `zxcvbn.scoring.l33t_variations` · *function*

## Summary:
Calculates the number of possible variations for l33t (leet) speak character substitutions in a password pattern match.

## Description:
This function computes the combinatorial possibilities for l33t substitutions within a matched password pattern. It's used in the zxcvbn password strength estimation algorithm to quantify how many different ways a leet speak pattern could have been constructed from the original character set.

The function analyzes each character substitution in the match and calculates the mathematical combinations of possible arrangements. When a character has been substituted (like '3' for 'e'), it determines how many different ways that substitution could have occurred based on the frequency of both the substituted and original characters in the token.

## Args:
    match (dict): A dictionary containing pattern matching information with keys:
        - 'l33t' (bool): Indicates if the match involves l33t substitutions
        - 'sub' (dict): Mapping of substituted characters to their original forms
        - 'token' (str): The matched string being analyzed

## Returns:
    int: The total number of possible variation combinations for the l33t substitutions in the match. Returns 1 if no l33t substitutions are present.

## Raises:
    None: This function does not explicitly raise exceptions.

## Constraints:
    Preconditions:
        - The match parameter must be a dictionary with required keys ('l33t', 'sub', 'token')
        - The 'sub' key must be a dictionary mapping substituted characters to original characters
        - The 'token' key must be a string
    
    Postconditions:
        - Returns a positive integer representing the number of possible variations
        - If 'l33t' is False, returns 1 without processing further

## Side Effects:
    None: This function has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start l33t_variations(match)] --> B{match['l33t'] is False?}
    B -- Yes --> C[Return 1]
    B -- No --> D[Initialize variations = 1]
    D --> E[For each subbed, unsubbed in match['sub'].items()]
    E --> F[Convert match['token'] to lowercase]
    F --> G[Count occurrences of subbed character]
    G --> H[Count occurrences of unsubbed character]
    H --> I{S == 0 OR U == 0?}
    I -- Yes --> J[variations *= 2]
    I -- No --> K[Calculate p = min(U, S)]
    K --> L[Initialize possibilities = 0]
    L --> M[For i in range(1, p+1)]
    M --> N[possibilities += nCk(U+S, i)]
    N --> O[variations *= possibilities]
    O --> P[Return variations]
```

## Examples:
    >>> match = {'l33t': True, 'sub': {'3': 'e'}, 'token': 'p@ssw0rd'}
    >>> l33t_variations(match)
    # Calculates variations for '3' -> 'e' substitution in the token
    
    >>> match = {'l33t': False, 'sub': {}, 'token': 'password'}
    >>> l33t_variations(match)
    1

