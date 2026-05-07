# `value.py`

## `mingus.core.value.add` · *function*

## Summary:
Calculates the harmonic mean of two numeric values using the formula 1 / (1/value1 + 1/value2).

## Description:
This function computes the harmonic mean of two values, which is mathematically defined as the reciprocal of the average of the reciprocals. It is commonly used in electrical engineering for calculating equivalent resistance of parallel resistors and in other domains where rates or ratios need to be averaged.

## Args:
    value1 (float): First numeric value, must be non-zero.
    value2 (float): Second numeric value, must be non-zero.

## Returns:
    float: The harmonic mean of value1 and value2.

## Raises:
    ZeroDivisionError: When either value1 or value2 equals zero, resulting in division by zero.

## Constraints:
    Preconditions: Both value1 and value2 must be non-zero real numbers.
    Postconditions: The returned value represents the harmonic mean of the two inputs.

## Side Effects:
    None: This function is pure and has no side effects.

## Control Flow:
```mermaid
flowchart TD
    A[Start add(value1, value2)] --> B{value1 == 0 or value2 == 0?}
    B -- Yes --> C[ZeroDivisionError]
    B -- No --> D[Calculate 1/(1/value1 + 1/value2)]
    D --> E[Return result]
```

## Examples:
    >>> add(4, 4)
    2.0
    >>> add(2, 6)
    3.0
    >>> add(1, 1)
    0.5
    >>> add(0, 5)
    ZeroDivisionError

## `mingus.core.value.subtract` · *function*

## Summary:
Computes the reciprocal subtraction of two values using the formula 1/(1/value1 - 1/value2).

## Description:
This function implements the mathematical operation 1/(1/value1 - 1/value2), which is equivalent to (value1 * value2)/(value1 - value2). It's primarily used in electrical engineering contexts for calculating parallel resistance values and in physics for combining inverse-proportional quantities.

## Args:
    value1 (float): First numeric value, must be non-zero
    value2 (float): Second numeric value, must be non-zero

## Returns:
    float: The result of the reciprocal subtraction operation

## Raises:
    ZeroDivisionError: When value1 equals value2 (causing division by zero in denominator) or when either value is zero
    TypeError: When either argument is not a numeric type

## Constraints:
    Preconditions:
        - Both value1 and value2 must be non-zero
        - value1 must not equal value2 (to avoid division by zero)
        - Both arguments must be numeric types (int or float)
    Postconditions:
        - Returns a finite floating-point number when inputs satisfy all constraints

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[subtract(value1, value2)] --> B{value1 == 0 or value2 == 0?}
    B -- Yes --> C[ZeroDivisionError]
    B -- No --> D{value1 == value2?}
    D -- Yes --> E[ZeroDivisionError]
    D -- No --> F[return 1 / (1.0 / value1 - 1.0 / value2)]
```

## Examples:
    >>> subtract(6.0, 3.0)
    2.0
    >>> subtract(10.0, 5.0)
    3.3333333333333335
    >>> subtract(-4.0, 4.0)
    -2.0
    >>> subtract(4.0, 4.0)
    ZeroDivisionError: division by zero
    >>> subtract(0.0, 5.0)
    ZeroDivisionError: division by zero

## `mingus.core.value.dots` · *function*

## Summary:
Calculates the dotted value of a musical note based on the number of dots applied.

## Description:
This function computes the effective duration of a musical note when dots are added to it. In music theory, each dot adds half the value of the previous note, creating a geometric series. The function implements the mathematical formula to calculate this dotted value. The formula represents the sum of a geometric series where each term is half the previous term.

## Args:
    value (float): The base value of the musical note (e.g., whole note, half note, etc.)
    nr (int): The number of dots to apply. Defaults to 1.

## Returns:
    float: The calculated dotted value representing the total duration when dots are applied.

## Raises:
    None

## Constraints:
    Preconditions:
        - The value parameter should be a positive numeric value
        - The nr parameter should be a non-negative integer
    
    Postconditions:
        - The returned value will be greater than or equal to the input value
        - The result follows the mathematical relationship of dotted notes in music theory

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start dots(value, nr)] --> B[Calculate 0.5 * value]
    B --> C[Calculate 0.5^(nr+1)]
    C --> D[Calculate 1.0 - 0.5^(nr+1)]
    D --> E[Divide (0.5 * value) by (1.0 - 0.5^(nr+1))]
    E --> F[Return result]
```

## Examples:
    >>> dots(1.0, 1)
    1.5
    >>> dots(1.0, 2)
    1.75
    >>> dots(2.0, 1)
    3.0
```

## `mingus.core.value.triplet` · *function*

## Summary:
Computes a rhythmic triplet value by scaling an input according to a 3:2 ratio.

## Description:
This function calculates a musical tuplet value where the input is scaled by the ratio 3:2. It serves as a specialized wrapper around the general tuplet function, specifically designed for triplet calculations in musical contexts.

## Args:
    value (float or int): The base musical value to be converted into a triplet duration.

## Returns:
    float: The result of scaling the input value by the 3:2 ratio, equivalent to (3 * value) / 2.0.

## Raises:
    ZeroDivisionError: When the internal tuplet function is called with a zero denominator (though this is prevented by hardcoded parameters).

## Constraints:
    Preconditions:
        - value must be a numeric type (int or float).
    Postconditions:
        - The returned value is a float representing the triplet-scaled result.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start triplet(value)] --> B[Call tuplet(value, 3, 2)]
    B --> C[Return (3 * value) / 2.0]
```

## Examples:
    >>> triplet(4)
    6.0
    >>> triplet(10)
    15.0
    >>> triplet(5.5)
    8.25

## `mingus.core.value.quintuplet` · *function*

## Summary:
Computes a quintuplet value by applying a 5:4 rhythmic ratio to an input value.

## Description:
This function calculates a quintuplet value by scaling an input value using the ratio 5:4. It is used in musical applications to represent rhythmic patterns where five notes are played in the time normally occupied by four notes.

## Args:
    value (float or int): The base value to be scaled, typically representing a musical duration or beat value.

## Returns:
    float: The result of (5 * value) / 4.0, representing the quintuplet-scaled value.

## Raises:
    ZeroDivisionError: When the internal tuplet function is called with a zero denominator (though this is prevented by the fixed parameters).

## Constraints:
    Preconditions:
        - value must be a numeric type (int or float).
    Postconditions:
        - The returned value is a float representing the quintuplet-scaled result.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start quintuplet(value)] --> B[Call tuplet(value, 5, 4)]
    B --> C[Return (5 * value) / 4.0]
```

## Examples:
    >>> quintuplet(4)
    5.0
    >>> quintuplet(10)
    12.5
    >>> quintuplet(1.6)
    2.0

## `mingus.core.value.septuplet` · *function*

## Summary:
Computes a septuplet value by applying a 7:4 or 7:8 ratio to an input value, depending on the specified mode.

## Description:
This function calculates musical tuplet values where 7 notes are played in the time of 4 or 8 beats. It is a specialized wrapper around the general tuplet function.

## Args:
    value (float or int): The base value to be scaled.
    in_fourths (bool): Flag determining the tuplet ratio. If True, uses 7:4 ratio; if False, uses 7:8 ratio. Defaults to True.

## Returns:
    float: The result of applying the septuplet ratio to the input value.

## Raises:
    ZeroDivisionError: When the underlying tuplet function is called with a zero denominator.

## Constraints:
    Preconditions:
        - value must be a numeric type (int or float).
        - The underlying tuplet function must handle numeric inputs properly.
    Postconditions:
        - The returned value is a float representing the scaled result according to the specified tuplet ratio.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start septuplet(value, in_fourths)] --> B{in_fourths?}
    B -- Yes --> C[Call tuplet(value, 7, 4)]
    B -- No --> D[Call tuplet(value, 7, 8)]
    C --> E[Return result]
    D --> E
```

## Examples:
    >>> septuplet(4)
    7.0
    >>> septuplet(8, in_fourths=False)
    7.0
    >>> septuplet(16, in_fourths=False)
    14.0
```

## `mingus.core.value.tuplet` · *function*

## Summary:
Computes a tuplet value by applying a ratio to an input value.

## Description:
This function scales an input value using a ratio defined by two integers. It is primarily used in musical applications to calculate tuplet durations where rat1/rat2 represents the rhythmic relationship.

## Args:
    value (float or int): The base value to be scaled.
    rat1 (float or int): The numerator of the scaling ratio.
    rat2 (float or int): The denominator of the scaling ratio.

## Returns:
    float: The result of (rat1 * value) / rat2.

## Raises:
    ZeroDivisionError: When rat2 is zero.

## Constraints:
    Preconditions:
        - value, rat1, and rat2 must be numeric types (int or float).
        - rat2 must not be zero.
    Postconditions:
        - The returned value is a float representing the scaled result.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start tuplet(value, rat1, rat2)] --> B{rat2 == 0?}
    B -- Yes --> C[Raise ZeroDivisionError]
    B -- No --> D[Return (rat1 * value) / float(rat2)]
```

## Examples:
    >>> tuplet(4, 3, 2)
    6.0
    >>> tuplet(10, 1, 3)
    3.3333333333333335
    >>> tuplet(5, 2, 1)
    10.0

## `mingus.core.value.determine` · *function*

## Summary:
Determines the normalized musical value and its associated rhythmic properties based on an input value.

## Description:
This function processes a musical value to find its closest base value and calculates appropriate rhythmic properties such as duration, numerator, and denominator. It is designed to handle various musical note durations and convert them into standardized representations. The function searches through a predefined set of base musical values to find the most appropriate match.

## Args:
    value (float or int): The musical value to be processed, typically representing a note duration or rhythmic value.

## Returns:
    tuple: A tuple containing four elements:
        - base_value (float or int): The closest base value found in the musical value system
        - duration (int): The duration component of the rhythmic representation
        - numerator (int): The numerator component of the rhythmic fraction
        - denominator (int): The denominator component of the rhythmic fraction

## Raises:
    None explicitly raised in the function body

## Constraints:
    - Preconditions: The function assumes the existence of a global variable `base_values` that contains a sequence of base musical values
    - Postconditions: The returned tuple always contains exactly four elements with the specified types

## Side Effects:
    - None

## Control Flow:
```mermaid
flowchart TD
    A[Start determine(value)] --> B{value in base_values?}
    B -- Yes --> C[Return (value, 0, 1, 1)]
    B -- No --> D[Initialize i = -2]
    D --> E[For v in base_values]
    E --> F{value == v}
    F -- Yes --> G[Return (value, 0, 1, 1)]
    F -- No --> H{value < v}
    H -- Yes --> I[Break loop]
    H -- No --> J[i += 1]
    I --> K[Scaled = value / 2^i]
    K --> L{Scaled >= 0.9375}
    L -- Yes --> M[Return (base_values[i], 0, 1, 1)]
    L -- No --> N{Scaled >= 0.8125}
    N -- Yes --> O[Return (base_values[i+1], 0, 7, 4)]
    N -- No --> P{Scaled >= 17/24}
    P -- Yes --> Q[Return (base_values[i+1], 0, 3, 2)]
    P -- No --> R{Scaled >= 31/48}
    R -- Yes --> S[Return (base_values[i+1], 1, 1, 1)]
    R -- No --> T{Scaled >= 67/112}
    T -- Yes --> U[Return (base_values[i+1], 0, 5, 4)]
    T -- No --> V[Initialize d = 3]
    V --> W[For x in range(2,5)]
    W --> X[d += 2^x]
    X --> Y{Scaled == 2^x/d}
    Y -- Yes --> Z[Return (base_values[i+1], x, 1, 1)]
    Y -- No --> AA[Continue loop]
    AA --> AB[End loop]
    AB --> AC[Return (base_values[i+1], 0, 1, 1)]
```

## Examples:
    - Input: 1.0 → Output: (1.0, 0, 1, 1) - Exact match with base value
    - Input: 0.5 → Output: (0.5, 0, 1, 1) - Closest base value with standard duration
    - Input: 0.25 → Output: (0.25, 0, 1, 1) - Base value match

