# `value.py`

## `mingus.core.value.add` · *function*

## Summary:
Computes the harmonic mean of two values using the formula 1 / (1/(value1) + 1/(value2)), commonly used for calculating parallel resistances or combining inverse-proportional quantities.

## Description:
This function implements the mathematical formula for combining two values in parallel, specifically designed for electrical resistance calculations or similar inverse-proportional operations. The function computes 1 / (1.0 / value1 + 1.0 / value2), which represents the equivalent resistance when two resistors are connected in parallel or the harmonic mean of the two values. This is particularly useful in electrical engineering contexts where parallel components need to be combined.

## Args:
    value1 (numeric): First value to be combined. Must be non-zero to avoid division by zero.
    value2 (numeric): Second value to be combined. Must be non-zero to avoid division by zero.

## Returns:
    numeric: The result of the harmonic mean calculation representing the combined effect of the two values.

## Raises:
    ZeroDivisionError: When either value1 or value2 is zero, causing division by zero in the computation.

## Constraints:
    Preconditions: Both value1 and value2 must be non-zero numbers to prevent division by zero errors.
    Postconditions: The returned value represents the mathematical result of the harmonic mean formula.

## Side Effects:
    None: This function has no side effects and is purely computational.

## Control Flow:
```mermaid
flowchart TD
    A[Start add(value1, value2)] --> B{value1 == 0 OR value2 == 0?}
    B -- Yes --> C[ZeroDivisionError]
    B -- No --> D[Calculate 1.0 / value1]
    D --> E[Calculate 1.0 / value2]
    E --> F[Add results]
    F --> G[Calculate 1 / (result)]
    G --> H[Return result]
```

## Examples:
    >>> add(4, 4)
    2.0
    >>> add(10, 5)
    3.3333333333333335
    >>> add(2, 3)
    1.2

## `mingus.core.value.subtract` · *function*

## Summary:
Computes the harmonic mean-related operation 1 / (1/value1 - 1/value2) for two numeric values.

## Description:
This function implements the mathematical operation 1 / (1.0 / value1 - 1.0 / value2), which computes the reciprocal of the difference between the reciprocals of two values. This operation is mathematically equivalent to (value1 * value2) / (value1 - value2) when value1 ≠ value2. It's commonly used in electrical engineering for calculating parallel resistances or in physics for combining inverse quantities.

## Args:
    value1 (float): First numeric value, must be non-zero.
    value2 (float): Second numeric value, must be non-zero.

## Returns:
    float: The result of 1 / (1.0 / value1 - 1.0 / value2).

## Raises:
    ZeroDivisionError: When either value1 or value2 is zero, or when value1 equals value2 (which causes division by zero in the denominator).

## Constraints:
    Preconditions:
        - Both value1 and value2 must be non-zero
        - value1 must not equal value2 (to prevent division by zero in the denominator)
    Postconditions:
        - Returns a finite floating-point number when inputs satisfy preconditions

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Input: value1, value2] --> B{value1 == 0 or value2 == 0?}
    B -- Yes --> C[ZeroDivisionError]
    B -- No --> D{value1 == value2?}
    D -- Yes --> E[ZeroDivisionError]
    D -- No --> F[Calculate 1/(1.0/value1 - 1.0/value2)]
    F --> G[Return result]
```

## Examples:
    >>> subtract(2.0, 3.0)
    6.0
    
    >>> subtract(4.0, 4.0)
    # Raises ZeroDivisionError
    
    >>> subtract(1.0, 2.0)
    2.0
```

## `mingus.core.value.dots` · *function*

## Summary:
Computes the dotted note value multiplier based on the number of dots applied to a musical note.

## Description:
This function calculates the multiplicative factor for a dotted note in music theory. In music notation, a dot adds half the value of the preceding note. For example, a dotted quarter note equals 1.5 quarter notes. This function computes the total multiplier for a given base value with a specified number of dots applied.

## Args:
    value (float): The base musical note value to be dotted
    nr (int): Number of dots to apply (default: 1)

## Returns:
    float: The multiplicative factor representing the dotted note value

## Raises:
    None

## Constraints:
    Preconditions:
        - value must be a positive numeric value
        - nr must be a non-negative integer
    
    Postconditions:
        - Returns a positive floating-point number greater than or equal to value
        - When nr=0, returns value unchanged
        - When nr increases, the returned value increases monotonically

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start dots(value, nr)] --> B{nr == 0?}
    B -- Yes --> C[Return value]
    B -- No --> D[Calculate (0.5 * value) / (1.0 - 0.5^(nr+1))]
    D --> E[Return result]
```

## Examples:
    >>> dots(1.0, 1)
    1.5
    >>> dots(1.0, 2)
    1.75
    >>> dots(4.0, 3)
    4.875
```

## `mingus.core.value.triplet` · *function*

## Summary:
Computes a triplet-scaled value by applying a 3:2 ratio to the input value.

## Description:
This function applies a musical triplet ratio (3:2) to scale an input value. It is a specialized wrapper around the general-purpose `tuplet` function, designed specifically for triplet timing calculations in musical contexts where values need to be adjusted according to a 3:2 rhythmic ratio.

## Args:
    value (float or int): The base value to be scaled by the triplet ratio.

## Returns:
    float: The result of (3 * value) / 2, representing the triplet-scaled value.

## Raises:
    ZeroDivisionError: When the internal `tuplet` function is called with a zero denominator (though this would be impossible with the fixed parameters used).

## Constraints:
    Preconditions:
        - value should be a numeric type that supports multiplication and division
        
    Postconditions:
        - Returns a float value representing the triplet-scaled input
        - The result maintains the mathematical relationship: scaled_value = (3 * value) / 2

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
    
    >>> triplet(10)
    15.0
    
    >>> triplet(5)
    7.5

## `mingus.core.value.quintuplet` · *function*

## Summary:
Applies a 5:4 rhythmic scaling to a musical value, converting it to quintuplet timing.

## Description:
Computes a scaled musical value using a 5:4 ratio, which represents a quintuplet rhythm where 5 notes are played in the time normally occupied by 4 notes. This function is a specialized wrapper around the general tuplet() function with fixed ratio parameters.

## Args:
    value (float or int): The base musical value to be scaled according to quintuplet timing.

## Returns:
    float: The result of (5 * value) / 4, representing the musical value adjusted for quintuplet timing.

## Raises:
    ZeroDivisionError: When the internal tuplet function is called with a zero denominator (though this would be an implementation error since 4 is hardcoded).

## Constraints:
    Preconditions:
        - value should be a numeric type that supports multiplication and division
        
    Postconditions:
        - Returns a float value representing the quintuplet-scaled input
        - The result maintains the mathematical relationship: quintuplet_value = (5 * value) / 4

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start quintuplet(value)] --> B[tuplet(value, 5, 4)]
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
Creates a septuplet value by scaling an input according to a 7:4 or 7:8 ratio.

## Description:
This function generates a septuplet value by applying a rhythmic scaling factor to the input value. It serves as a specialized wrapper around the general `tuplet` function to create 7-note tuplets, commonly used in musical timing calculations. The function supports two modes: 7:4 (where 7 notes occupy the space of 4 beats) and 7:8 (where 7 notes occupy the space of 8 beats).

## Args:
    value (float or int): The base value to be scaled according to the septuplet ratio.
    in_fourths (bool): Flag determining the tuplet ratio. When True (default), uses 7:4 ratio; when False, uses 7:8 ratio.

## Returns:
    float: The scaled value representing the septuplet calculation. For in_fourths=True, returns (7 * value) / 4; for in_fourths=False, returns (7 * value) / 8.

## Raises:
    ZeroDivisionError: When the underlying `tuplet` function is called with a zero denominator (though this would be an internal error as 4 and 8 are hardcoded).

## Constraints:
    Preconditions:
        - value must be a numeric type (int or float) that supports multiplication and division
        - The function internally calls `tuplet` with fixed ratios of 7:4 or 7:8, so the underlying `tuplet` function must handle these properly
        
    Postconditions:
        - Returns a float value representing the scaled input according to the specified tuplet ratio
        - The result maintains the mathematical relationship: scaled_value = (7 * value) / ratio

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
    
    >>> septuplet(12, in_fourths=True)
    21.0
```

## `mingus.core.value.tuplet` · *function*

## Summary:
Computes a scaled value using a ratio multiplier.

## Description:
Performs a mathematical operation that scales an input value by a ratio defined by two integers. This function is commonly used in musical timing calculations where values need to be adjusted according to rhythmic ratios.

## Args:
    value (float or int): The base value to be scaled.
    rat1 (int): The numerator of the scaling ratio.
    rat2 (int): The denominator of the scaling ratio.

## Returns:
    float: The result of (rat1 * value) / rat2, representing the scaled value.

## Raises:
    ZeroDivisionError: When rat2 is zero, causing a division by zero error.

## Constraints:
    Preconditions:
        - rat2 must not be zero to avoid division by zero
        - value and rat1 should be numeric types that support multiplication and division
    
    Postconditions:
        - Returns a float value representing the scaled input
        - The result maintains the mathematical relationship: scaled_value = (rat1 * value) / rat2

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start tuplet(value, rat1, rat2)] --> B{rat2 == 0?}
    B -- Yes --> C[ZeroDivisionError]
    B -- No --> D[(rat1 * value) / float(rat2)]
    D --> E[Return result]
```

## Examples:
    >>> tuplet(4, 3, 2)
    6.0
    
    >>> tuplet(10, 1, 3)
    3.3333333333333335
    
    >>> tuplet(5, 2, 5)
    2.0

## `mingus.core.value.determine` · *function*

## Summary:
Normalizes a musical value into a standardized representation with rhythmic properties.

## Description:
This function processes a musical value (typically representing a duration or note length) and maps it to a normalized form consisting of a base value and associated rhythmic properties. The function implements a scaling algorithm that determines the most appropriate canonical representation for musical values, likely used in music notation or rhythm processing applications.

## Args:
    value (numeric): The musical value to normalize, typically representing a duration or note length.

## Returns:
    tuple: A 4-element tuple containing:
        - base_value: The mapped base value from an internal sequence
        - int: A numeric identifier (likely representing rhythmic modifiers)
        - numerator: The numerator part of a rhythmic fraction
        - denominator: The denominator part of a rhythmic fraction

## Raises:
    None explicitly raised in the function body

## Constraints:
    - Preconditions: The input value must be comparable to elements in an internal base_values sequence
    - Postconditions: The returned tuple always contains exactly 4 elements with the specified structure

## Side Effects:
    None

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
    H --> C
    G --> I[Calculate scaled = value / 2^i]
    I --> J{scaled >= 0.9375?}
    J -- Yes --> K[Return (base_values[i], 0, 1, 1)]
    J -- No --> L{scaled >= 0.8125?}
    L -- Yes --> M[Return (base_values[i+1], 0, 7, 4)]
    L -- No --> N{scaled >= 17/24?}
    N -- Yes --> O[Return (base_values[i+1], 0, 3, 2)]
    N -- No --> P{scaled >= 31/48?}
    P -- Yes --> Q[Return (base_values[i+1], 1, 1, 1)]
    P -- No --> R{scaled >= 67/112?}
    R -- Yes --> S[Return (base_values[i+1], 0, 5, 4)]
    R -- No --> T[Initialize d = 3]
    T --> U[For x in range(2,5)]
    U --> V[d += 2^x]
    V --> W{scaled == 2^x/d?}
    W -- Yes --> X[Return (base_values[i+1], x, 1, 1)]
    W -- No --> Y[Return (base_values[i+1], 0, 1, 1)]
```

## Examples:
    # This function requires the base_values sequence to be defined elsewhere
    # determine(1.0) might return (1.0, 0, 1, 1) if 1.0 is in base_values
    # determine(2.0) would process through the scaling logic to return appropriate tuple

