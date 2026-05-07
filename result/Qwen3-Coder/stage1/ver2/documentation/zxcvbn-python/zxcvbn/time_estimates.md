# `time_estimates.py`

## `zxcvbn.time_estimates.estimate_attack_times` · *function*

## Summary:
Calculates estimated time to crack a password using various attack scenarios based on the number of guesses required.

## Description:
This function computes the time required to crack a password using different attack methodologies, including online attacks with and without throttling, and offline attacks with slow and fast hashing. It provides a comprehensive view of password security strength across multiple threat models. The function extracts this calculation logic to enable consistent time estimation across different parts of the password strength analysis system.

## Args:
    guesses (int or float): The estimated number of guesses required to crack the password through brute force. Must be a non-negative numeric value representing the computational effort needed for a successful attack.

## Returns:
    dict: A dictionary containing three keys:
        - 'crack_times_seconds' (dict): Mapping of attack scenarios to time durations in seconds as Decimal objects
        - 'crack_times_display' (dict): Mapping of attack scenarios to human-readable time strings
        - 'score' (int): Security strength score from 0 to 4 indicating password strength

## Raises:
    None explicitly raised by this function, though underlying operations may raise exceptions from the helper functions.

## Constraints:
    Preconditions:
        - Input `guesses` must be a numeric value (int or float)
        - Input `guesses` must be non-negative
    Postconditions:
        - Returns a dictionary with exactly three keys: 'crack_times_seconds', 'crack_times_display', and 'score'
        - All time values in 'crack_times_seconds' are represented as Decimal objects for precision
        - All time values in 'crack_times_display' are formatted as human-readable strings

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start estimate_attack_times(guesses)] --> B[Calculate 4 attack scenarios]
    B --> C[online_throttling_100_per_hour = guesses / (100/3600)]
    C --> D[online_no_throttling_10_per_second = guesses / 10]
    D --> E[offline_slow_hashing_1e4_per_second = guesses / 1e4]
    E --> F[offline_fast_hashing_1e10_per_second = guesses / 1e10]
    F --> G[Format all times to display strings]
    G --> H[Call guesses_to_score(guesses) for security score]
    H --> I[Return results dictionary]
```

## Examples:
    >>> estimate_attack_times(1000)
    {
        'crack_times_seconds': {
            'online_throttling_100_per_hour': Decimal('0.36'),
            'online_no_throttling_10_per_second': Decimal('100.0'),
            'offline_slow_hashing_1e4_per_second': Decimal('0.1'),
            'offline_fast_hashing_1e10_per_second': Decimal('1e-7')
        },
        'crack_times_display': {
            'online_throttling_100_per_hour': '1 second',
            'online_no_throttling_10_per_second': '100 seconds',
            'offline_slow_hashing_1e4_per_second': 'less than a second',
            'offline_fast_hashing_1e10_per_second': 'less than a second'
        },
        'score': 1
    }

## `zxcvbn.time_estimates.guesses_to_score` · *function*

## Summary:
Converts a number of guesses into a security strength score ranging from 0 to 4.

## Description:
Maps the number of guesses required to crack a password to a security strength score. This function is used to categorize password strength based on the computational effort required to guess the password through brute force methods. The function is typically called during password strength estimation to provide a qualitative measure of security.

The function extracts this logic into a separate utility function to maintain clean separation between the core guessing algorithm and the scoring mechanism, allowing for easier testing and potential modification of scoring criteria without affecting the core guessing logic.

## Args:
    guesses (float or int): The number of guesses required to crack a password. Must be a non-negative numeric value representing the estimated number of attempts needed for a successful brute-force attack.

## Returns:
    int: A security strength score between 0 and 4, where:
        - 0: Very weak (less than 1,005 guesses)
        - 1: Weak (less than 1,000,005 guesses)  
        - 2: Medium (less than 100,000,005 guesses)
        - 3: Strong (less than 10,000,000,005 guesses)
        - 4: Very strong (10,000,000,005 guesses or more)

## Raises:
    None: This function does not raise any exceptions under normal operation.

## Constraints:
    Preconditions:
        - The input `guesses` must be a numeric value (int or float)
        - The input `guesses` must be non-negative
    Postconditions:
        - The returned value is always an integer between 0 and 4 inclusive
        - The function handles all numeric inputs gracefully without raising exceptions

## Side Effects:
    None: This function has no side effects. It performs only pure calculations and returns a value.

## Control Flow:
```mermaid
flowchart TD
    A[Start guesses_to_score(guesses)] --> B{guesses < 1005?}
    B -- Yes --> C[Return 0]
    B -- No --> D{guesses < 1000005?}
    D -- Yes --> E[Return 1]
    D -- No --> F{guesses < 100000005?}
    F -- Yes --> G[Return 2]
    F -- No --> H{guesses < 10000000005?}
    H -- Yes --> I[Return 3]
    H -- No --> J[Return 4]
```

## Examples:
    >>> guesses_to_score(100)
    0
    >>> guesses_to_score(50000)
    1
    >>> guesses_to_score(5000000)
    2
    >>> guesses_to_score(500000000)
    3
    >>> guesses_to_score(50000000000)
    4

## `zxcvbn.time_estimates.display_time` · *function*

## Summary:
Converts a time duration in seconds to a human-readable string representation.

## Description:
Formats a numeric time duration into a readable string that uses appropriate time units (seconds, minutes, hours, days, months, years) based on the magnitude of the input. This function extracts the time formatting logic to provide consistent, user-friendly time displays throughout the application.

## Args:
    seconds (float): Time duration in seconds. Must be non-negative.

## Returns:
    str: Human-readable time string. Possible return values include:
        - 'less than a second'
        - '<number> second(s)'
        - '<number> minute(s)'
        - '<number> hour(s)'
        - '<number> day(s)'
        - '<number> month(s)'
        - '<number> year(s)'
        - 'centuries'

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
        - Input `seconds` must be a non-negative number
    Postconditions:
        - Returns a properly formatted string representing the time duration
        - String is grammatically correct with pluralization for numbers other than 1

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start] --> B{seconds < 1?}
    B -- Yes --> C[display_str = 'less than a second']
    B -- No --> D{seconds < minute?}
    D -- Yes --> E[base = round(seconds)]
    E --> F[display_str = '%s second' % base]
    D -- No --> G{seconds < hour?}
    G -- Yes --> H[base = round(seconds / minute)]
    H --> I[display_str = '%s minute' % base]
    G -- No --> J{seconds < day?}
    J -- Yes --> K[base = round(seconds / hour)]
    K --> L[display_str = '%s hour' % base]
    J -- No --> M{seconds < month?}
    M -- Yes --> N[base = round(seconds / day)]
    N --> O[display_str = '%s day' % base]
    M -- No --> P{seconds < year?}
    P -- Yes --> Q[base = round(seconds / month)]
    Q --> R[display_str = '%s month' % base]
    P -- No --> S{seconds < century?}
    S -- Yes --> T[base = round(seconds / year)]
    T --> U[display_str = '%s year' % base]
    S -- No --> V[display_str = 'centuries']
    V --> W[End]
    U --> W
    R --> W
    O --> W
    L --> W
    I --> W
    F --> W
    C --> W
```

## Examples:
    >>> display_time(0.5)
    'less than a second'
    >>> display_time(30)
    '30 seconds'
    >>> display_time(90)
    '1 minute'
    >>> display_time(3661)
    '1 hour'
    >>> display_time(7200)
    '2 hours'
    >>> display_time(31536000)
    '1 year'
    >>> display_time(3153600000)
    '100 years'
```

## `zxcvbn.time_estimates.float_to_decimal` · *function*

*No documentation generated.*

