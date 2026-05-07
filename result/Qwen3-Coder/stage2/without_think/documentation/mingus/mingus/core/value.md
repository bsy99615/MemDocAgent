# `value.py`

## `mingus.core.value.add` · *function*

## Summary:
Computes the reciprocal of the sum of reciprocals of two values.

## Description:
This function implements the mathematical operation 1 / (1.0 / value1 + 1.0 / value2), which is commonly used for calculating parallel resistances in electrical engineering or similar applications where values combine in parallel.

## Args:
    value1 (float): First numeric value, must be non-zero.
    value2 (float): Second numeric value, must be non-zero.

## Returns:
    float: The result of the computation 1 / (1.0 / value1 + 1.0 / value2).

## Raises:
    ZeroDivisionError: When either value1 or value2 is zero, causing division by zero in the calculation.

## Constraints:
    Preconditions: Both value1 and value2 must be non-zero numbers.
    Postconditions: The returned value represents the mathematical result of the harmonic combination of the two inputs.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start add(value1, value2)] --> B{value1 == 0 or value2 == 0?}
    B -- Yes --> C[ZeroDivisionError]
    B -- No --> D[Compute 1.0 / value1]
    D --> E[Compute 1.0 / value2]
    E --> F[Sum reciprocals]
    F --> G[Compute 1 / (sum)]
    G --> H[Return result]
```

## Examples:
    >>> add(2.0, 3.0)
    1.2
    >>> add(1.0, 1.0)
    0.5

## `mingus.core.value.subtract` · *function*

## Summary:
Computes the reciprocal of the difference between the reciprocals of two values.

## Description:
This function implements the mathematical formula 1 / (1.0 / value1 - 1.0 / value2) to compute the reciprocal of the difference between the reciprocals of two input values. The function performs a direct calculation without any conditional logic beyond the mathematical operations themselves.

## Args:
    value1 (float): First numeric value, must be non-zero to avoid division by zero in intermediate calculations.
    value2 (float): Second numeric value, must be non-zero to avoid division by zero in intermediate calculations.

## Returns:
    float: The result of the computation 1 / (1.0 / value1 - 1.0 / value2).

## Raises:
    ZeroDivisionError: When the denominator (1.0 / value1 - 1.0 / value2) evaluates to zero, which occurs when value1 equals value2.

## Constraints:
    Preconditions: Both value1 and value2 must be non-zero to prevent division by zero in intermediate calculations.
    Postconditions: The returned value represents the mathematical result of the specified formula.

## Side Effects:
    None

## Control Flow:
    ```mermaid
    flowchart TD
        A[Start subtract(value1, value2)] --> B[Compute 1.0 / value1]
        B --> C[Compute 1.0 / value2]
        C --> D[Subtract reciprocals: 1.0 / value1 - 1.0 / value2]
        D --> E{Denominator ≠ 0?}
        E -- Yes --> F[Divide 1.0 by difference]
        F --> G[Return result]
        E -- No --> H[Raise ZeroDivisionError]
    ```

## Examples:
    # Valid usage
    result = subtract(6.0, 3.0)  # Returns 2.0
    
    # Edge case that raises exception
    result = subtract(4.0, 4.0)  # Raises ZeroDivisionError

## `mingus.core.value.dots` · *function*

## Summary:
Computes the total duration of a musical note enhanced with augmentation dots.

## Description:
This function calculates the extended duration of a musical note when augmentation dots are applied. Each dot adds half the value of the preceding note duration. For instance, a dotted quarter note equals one quarter note plus one eighth note. The mathematical formula implemented is: (0.5 × value) / (1.0 - 0.5^(nr + 1)), which represents the sum of a geometric series.

## Args:
    value (float): The base duration value of the musical note (e.g., 1.0 for a whole note).
    nr (int): The number of augmentation dots to apply. Defaults to 1. Must be a non-negative integer.

## Returns:
    float: The total duration value after applying the specified number of dots to the base value.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - The value parameter should be a positive numeric value representing a musical note duration
    - The nr parameter should be a non-negative integer
    
    Postconditions:
    - Returns a positive float value representing the dotted note duration
    - The result equals value × (1 + 1/2 + 1/4 + ... + 1/2^nr)

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start dots(value, nr)] --> B[Compute 0.5 * value]
    B --> C[Compute 0.5^(nr + 1)]
    C --> D[Compute 1.0 - 0.5^(nr + 1)]
    D --> E[Divide (0.5 * value) by (1.0 - 0.5^(nr + 1))]
    E --> F[Return result]
```

## Examples:
    >>> dots(1.0, 1)  # Dotted whole note = 1 + 0.5 = 1.5
    1.5
    >>> dots(1.0, 2)  # Double-dotted whole note = 1 + 0.5 + 0.25 = 1.75
    1.75
    >>> dots(2.0, 1)  # Dotted half note = 2 + 1 = 3.0
    3.0
    >>> dots(0.5, 3)  # Triple-dotted eighth note = 0.5 + 0.25 + 0.125 + 0.0625 = 0.9375
    0.9375
```

## `mingus.core.value.triplet` · *function*

## Summary:
Computes a triplet value by applying a 3:2 ratio to an input value.

## Description:
This function calculates a musical triplet value by applying a 3:2 ratio to the input value. It's a specialized wrapper around the general-purpose `tuplet` function, specifically designed for musical applications where three notes are played in the time of two.

## Args:
    value (float or int): The base value to be transformed by the triplet ratio.

## Returns:
    float: The result of (3 * value) / 2, representing the triplet-transformed value.

## Raises:
    ZeroDivisionError: When the input value causes division by zero in the underlying tuplet calculation (though this would only happen if the internal implementation had issues, as 2 is hardcoded as the denominator).

## Constraints:
    Preconditions:
        - Input value must be numeric (int or float)
    
    Postconditions:
        - Returns a float value representing the scaled input according to 3:2 ratio
        - The result maintains the proportional relationship defined by the triplet ratio

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start triplet(value)] --> B[Call tuplet(value, 3, 2)]
    B --> C[Return result]
```

## Examples:
    >>> triplet(4)
    6.0
    >>> triplet(8)
    12.0
    >>> triplet(12)
    18.0
```

## `mingus.core.value.quintuplet` · *function*

## Summary:
Applies a 5:4 tuplet ratio transformation to an input value.

## Description:
This function applies a 5:4 tuplet ratio to scale an input value by computing (5 * value) / 4.0. It serves as a specialized wrapper around the general tuplet() function with fixed parameters (rat1=5, rat2=4).

## Args:
    value (float or int): The base value to be transformed by the tuplet ratio.

## Returns:
    float: The result of applying the 5:4 tuplet transformation to the input value.

## Raises:
    ZeroDivisionError: When rat2 is zero in the underlying tuplet calculation (though this cannot occur with the fixed parameters 5 and 4).

## Constraints:
    Preconditions:
        - Input value must be numeric (int or float)
    
    Postconditions:
        - Returns a float value representing the tuplet-transformed input
        - The result maintains the 5:4 proportional relationship

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start quintuplet(value)] --> B[Call tuplet(value, 5, 4)]
    B --> C[Return result]
```

## Examples:
    >>> quintuplet(4)
    5.0
    >>> quintuplet(8)
    10.0
    >>> quintuplet(12)
    15.0

## `mingus.core.value.septuplet` · *function*

## Summary:
Creates a septuplet (7-note tuplet) value by applying a rhythmic ratio to an input value.

## Description:
Computes a septuplet transformation of the input value by applying a 7:4 or 7:8 ratio, depending on the in_fourths parameter. This function is used in music theory applications to calculate note durations where 7 notes are played within the time of 4 or 8 beats respectively.

## Args:
    value (float or int): The base value to be transformed by the septuplet ratio.
    in_fourths (bool): When True, applies a 7:4 ratio; when False, applies a 7:8 ratio. Defaults to True.

## Returns:
    float: The result of the tuplet transformation, representing the septuplet-adjusted value.

## Raises:
    ZeroDivisionError: When the underlying tuplet function is called with a zero denominator (though this would only happen if the tuplet function itself had a bug).

## Constraints:
    Preconditions:
        - value must be numeric (int or float)
        - The underlying tuplet function must handle the ratio calculations properly
        
    Postconditions:
        - Returns a float value representing the scaled input according to the septuplet ratio
        - The result maintains the proportional relationship defined by the 7:4 or 7:8 ratio

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start septuplet(value, in_fourths)] --> B{in_fourths?}
    B -- True --> C[tuplet(value, 7, 4)]
    B -- False --> D[tuplet(value, 7, 8)]
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
Calculates a tuplet value by applying a ratio to an input value.

## Description:
This function computes a tuplet value by multiplying the input value with a numerator ratio and dividing by a denominator ratio. It's commonly used in music theory applications to calculate note durations or rhythmic proportions where a specific number of notes are played within the time of another.

## Args:
    value (float or int): The base value to be transformed by the tuplet ratio.
    rat1 (float or int): The numerator of the ratio to apply.
    rat2 (float or int): The denominator of the ratio to apply.

## Returns:
    float: The result of (rat1 * value) / rat2, representing the tuplet-transformed value.

## Raises:
    ZeroDivisionError: When rat2 is zero, causing division by zero.

## Constraints:
    Preconditions:
        - All arguments must be numeric (int or float)
        - rat2 must not be zero
    
    Postconditions:
        - Returns a float value representing the scaled input
        - The result maintains the proportional relationship defined by the ratio

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start tuplet(value, rat1, rat2)] --> B{rat2 == 0?}
    B -- Yes --> C[raise ZeroDivisionError]
    B -- No --> D[(rat1 * value) / float(rat2)]
    D --> E[Return result]
```

## Examples:
    >>> tuplet(4, 3, 2)
    6.0
    >>> tuplet(8, 5, 4)
    10.0
    >>> tuplet(12, 2, 3)
    8.0

## `mingus.core.value.determine` · *function*

## Summary:
Normalizes a musical duration value by mapping it to a standardized rhythmic representation.

## Description:
This function takes a numerical musical duration value and maps it to a standardized tuple representation based on comparison against a set of base values. It performs value scaling and categorization to convert input values into recognized rhythmic patterns commonly used in musical notation.

## Args:
    value (float or int): The musical duration or value to be normalized.

## Returns:
    tuple: A 4-element tuple containing:
        - A base value from an internal sequence
        - An integer scaling factor
        - A numerator for rhythmic fraction representation  
        - A denominator for rhythmic fraction representation

## Raises:
    None explicitly raised in the function code shown.

## Constraints:
    Preconditions:
        - Input value must be comparable to elements in base_values
        - base_values must be defined in the module scope
    Postconditions:
        - Always returns a 4-element tuple with the specified structure

## Side Effects:
    None observed in the function code.

## Control Flow:
```mermaid
flowchart TD
    A[Start determine(value)] --> B[Initialize i = -2]
    B --> C[For v in base_values]
    C --> D{value == v?}
    D -- Yes --> E[Return (value, 0, 1, 1)]
    D -- No --> F{value < v?}
    F -- Yes --> G[Break loop]
    F -- No --> H[i += 1]
    H --> I[C loop continues?]
    I -- Yes --> C
    I -- No --> J[Calculate scaled = float(value) / 2**i]
    J --> K[scaled >= 0.9375?]
    K -- Yes --> L[Return (base_values[i], 0, 1, 1)]
    K -- No --> M[scaled >= 0.8125?]
    M -- Yes --> N[Return (base_values[i+1], 0, 7, 4)]
    M -- No --> O[scaled >= 17/24.0?]
    O -- Yes --> P[Return (base_values[i+1], 0, 3, 2)]
    O -- No --> Q[scaled >= 31/48.0?]
    Q -- Yes --> R[Return (base_values[i+1], 1, 1, 1)]
    Q -- No --> S[scaled >= 67/112.0?]
    S -- Yes --> T[Return (base_values[i+1], 0, 5, 4)]
    S -- No --> U[Initialize d = 3]
    U --> V[For x in range(2,5)]
    V --> W[d += 2**x]
    W --> X[scaled == 2.0**x / d?]
    X -- Yes --> Y[Return (base_values[i+1], x, 1, 1)]
    X -- No --> Z[Return (base_values[i+1], 0, 1, 1)]
```

## Examples:
    # Usage depends on the specific base_values defined in the module
    # determine(4) might return (4, 0, 1, 1) if 4 matches a base value exactly
    # determine(8) might return (8, 0, 7, 4) for values in that category
```

