# `value.py`

## `mingus.core.value.add` · *function*

## Summary:
Computes the harmonic mean of two values using the formula 1 / (1/val1 + 1/val2).

## Description:
This function implements a mathematical operation that calculates the harmonic mean of two numeric values. It's commonly used in contexts such as calculating parallel resistances in electrical engineering or averaging rates and ratios. The function performs the calculation 1 / (1/val1 + 1/val2) which is equivalent to (val1 * val2) / (val1 + val2).

## Args:
    value1 (float): First numeric value. Must be non-zero.
    value2 (float): Second numeric value. Must be non-zero.

## Returns:
    float: The harmonic mean of value1 and value2, calculated as 1 / (1/val1 + 1/val2).

## Raises:
    ZeroDivisionError: When either value1 or value2 is zero, causing division by zero in the intermediate calculations.

## Constraints:
    Preconditions: Both value1 and value2 must be non-zero numbers.
    Postconditions: The returned value represents the harmonic mean of the two input values.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start add(value1, value2)] --> B{value1 == 0 or value2 == 0?}
    B -- Yes --> C[raise ZeroDivisionError]
    B -- No --> D[Calculate 1.0 / value1]
    D --> E[Calculate 1.0 / value2]
    E --> F[Add results]
    F --> G[Calculate 1 / (result)]
    G --> H[Return result]
```

## Examples:
    >>> add(2.0, 3.0)
    1.2
    >>> add(1.0, 1.0)
    0.5

## `mingus.core.value.subtract` · *function*

## Summary:
Computes the reciprocal of the difference of reciprocals of two values, equivalent to the formula 1 / (1/value1 - 1/value2).

## Description:
This function implements the mathematical operation 1 / (1.0 / value1 - 1.0 / value2), which is commonly used in electrical engineering for calculating parallel resistances or in various mathematical contexts involving reciprocal relationships. The function encapsulates this specific computational pattern to promote code reuse and improve readability.

## Args:
    value1 (float): First numeric value, must be non-zero to avoid division by zero in intermediate calculation.
    value2 (float): Second numeric value, must be non-zero to avoid division by zero in intermediate calculation.

## Returns:
    float: The result of the computation 1 / (1.0 / value1 - 1.0 / value2).

## Raises:
    ZeroDivisionError: When value1 is zero, causing division by zero in 1.0 / value1.
    ZeroDivisionError: When value2 is zero, causing division by zero in 1.0 / value2.
    ZeroDivisionError: When value1 equals value2, making 1.0 / value1 - 1.0 / value2 equal to zero, causing division by zero in the final calculation.

## Constraints:
    Preconditions:
        - Both value1 and value2 must be non-zero to prevent intermediate division by zero errors.
        - value1 must not equal value2 to prevent final division by zero.
    Postconditions:
        - Returns a finite floating-point number when inputs satisfy the constraints.

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Start subtract(value1, value2)] --> B{value1 == 0?}
    B -- Yes --> C[ZeroDivisionError]
    B -- No --> D{value2 == 0?}
    D -- Yes --> E[ZeroDivisionError]
    D -- No --> F{value1 == value2?}
    F -- Yes --> G[ZeroDivisionError]
    F -- No --> H[Return 1/(1.0/value1 - 1.0/value2)]
```

## Examples:
    # Basic usage with equal values
    result = subtract(4.0, 4.0)  # Returns 2.0
    
    # Electrical resistance calculation (parallel resistors)
    parallel_resistance = subtract(10.0, 20.0)  # Returns approximately 6.67
    
    # Usage with different values
    result = subtract(6.0, 3.0)  # Returns 2.0
```

## `mingus.core.value.dots` · *function*

## Summary:
Calculates the effective value of a musical note with a specified number of dots applied.

## Description:
This function computes the total duration of a musical note enhanced with augmentation dots. In music theory, a dot adds half the value of the original note. For example, a dotted quarter note equals a quarter note plus an eighth note. This function generalizes this concept to support multiple dots.

## Args:
    value (float): The base value of the musical note (e.g., 1.0 for a whole note, 0.5 for a half note).
    nr (int): The number of dots to apply. Defaults to 1.

## Returns:
    float: The effective value of the note with the specified number of dots applied.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions:
    - value should be a positive numeric value representing a musical note duration
    - nr should be a non-negative integer
    
    Postconditions:
    - Returns a positive float value greater than or equal to the original value
    - For nr=0, returns the original value unchanged

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[Start dots(value, nr)] --> B{nr == 0?}
    B -- Yes --> C[Return value]
    B -- No --> D[Calculate (0.5 * value) / (1.0 - 0.5^(nr+1))]
    D --> E[Return result]
```

## Examples:
    >>> dots(1.0, 1)  # Dotted whole note
    2.0
    >>> dots(0.5, 2)  # Double-dotted half note  
    0.75
    >>> dots(0.25, 0)  # Undotted quarter note
    0.25
```

## `mingus.core.value.triplet` · *function*

## Summary:
Returns a value scaled by a 3:2 ratio, commonly used for musical triplet calculations.

## Description:
This function implements a musical triplet calculation by scaling the input value using a 3:2 ratio. It serves as a convenience wrapper around the more general `tuplet` function with fixed parameters (3, 2). The function is typically used in music theory applications to calculate durations or values for triplet rhythms.

## Args:
    value (float or int): The base value to be scaled by the triplet ratio.

## Returns:
    float: The scaled value calculated as (3 * value) / 2.0.

## Raises:
    None explicitly raised, though underlying arithmetic operations may raise standard Python exceptions like TypeError for incompatible types.

## Constraints:
    Preconditions:
        - The input value must be a numeric type (int or float) that supports multiplication and division operations.
    Postconditions:
        - The returned value will always be a float representing the 3:2 scaled version of the input.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[triplet(value)] --> B[tuplet(value, 3, 2)]
    B --> C[(3 * value) / 2.0]
    C --> D[Return scaled value]
```

## Examples:
    >>> triplet(4)
    6.0
    >>> triplet(2.5)
    3.75
    >>> triplet(0)
    0.0
```

## `mingus.core.value.quintuplet` · *function*

## Summary:
Computes a quintuplet value by scaling the input by a ratio of 5/4.

## Description:
This function calculates a quintuplet value by multiplying the input value by 5 and dividing by 4. It serves as a specialized wrapper around the general tuplet function, specifically implementing the 5:4 ratio commonly used in musical rhythmic patterns where five notes are played in the time normally occupied by four notes.

## Args:
    value (float or int): The base value to be scaled into a quintuplet pattern.

## Returns:
    float: The quintuplet-scaled value calculated as (5 * value) / 4.0.

## Raises:
    None explicitly raised.

## Constraints:
    Preconditions: The input value must be a numeric type (int or float).
    Postconditions: The returned value will always be a float representing the quintuplet transformation.

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[quintuplet(value)] --> B[tuplet(value, 5, 4)]
    B --> C[(5 * value) / 4.0]
    C --> D[Return result]
```

## Examples:
    >>> quintuplet(8)
    10.0
    >>> quintuplet(4)
    5.0
    >>> quintuplet(12)
    15.0
```

## `mingus.core.value.septuplet` · *function*

## Summary:
Creates a septuplet value by adjusting the input value according to a 7-note rhythmic pattern.

## Description:
This function generates a septuplet value by applying a mathematical transformation to the input value using the tuplet formula. It's designed to create 7-note rhythmic patterns that fit within either 4-beat or 8-beat time periods, making it useful for musical timing calculations.

## Args:
    value (float or int): The base musical value to be converted into a septuplet.
    in_fourths (bool): When True, creates a septuplet that fits within 4 beats; when False, fits within 8 beats. Defaults to True.

## Returns:
    float: The adjusted musical value representing the septuplet calculation. When in_fourths=True, returns (7 * value) / 4.0; when in_fourths=False, returns (7 * value) / 8.0.

## Raises:
    None explicitly raised by this function.

## Constraints:
    Preconditions:
    - The value parameter should be a numeric type (int or float)
    - The in_fourths parameter should be a boolean value
    
    Postconditions:
    - Returns a float value representing the septuplet-adjusted musical duration
    - The returned value maintains the proportional relationship to the input value

## Side Effects:
    None.

## Control Flow:
```mermaid
flowchart TD
    A[septuplet(value, in_fourths)] --> B{in_fourths?}
    B -->|True| C[tuplet(value, 7, 4)]
    B -->|False| D[tuplet(value, 7, 8)]
    C --> E[Return result]
    D --> E
```

## Examples:
    >>> septuplet(4)
    7.0
    >>> septuplet(4, in_fourths=False)
    3.5
    >>> septuplet(8)
    14.0
```

## `mingus.core.value.tuplet` · *function*

## Summary:
Calculates a proportional value based on a ratio relationship between two factors.

## Description:
Performs a mathematical operation that scales an input value by a numerator factor and divides by a denominator factor. This function is commonly used in musical contexts to calculate tuplet durations or proportional relationships between rhythmic elements.

## Args:
    value (float or int): The base value to be scaled.
    rat1 (float or int): The numerator factor used to multiply the value.
    rat2 (float or int): The denominator factor used to divide the result.

## Returns:
    float: The result of (rat1 * value) / rat2, representing the scaled proportional value.

## Raises:
    ZeroDivisionError: When rat2 is zero, causing a division by zero error.

## Constraints:
    Preconditions:
        - All arguments must be numeric (int or float)
        - rat2 must not be zero to avoid division by zero
    Postconditions:
        - Returns a float value representing the proportional relationship
        - The result maintains the mathematical relationship defined by the ratio

## Side Effects:
    None: This function has no side effects and is pure.

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

*No documentation generated.*

