# `baseconv.py`

## `datasette.utils.baseconv.BaseConverter` · *class*

## Summary:
A numeral system converter that transforms integers between decimal and custom bases using configurable digit sets.

## Description:
The BaseConverter class provides functionality to encode integers into custom numeral systems and decode strings from those systems back to integers. It serves as a flexible utility for base conversion operations, allowing users to define their own digit sets for various numeral systems beyond standard decimal or binary representations.

This class is particularly useful for creating compact identifiers, implementing custom encoding schemes, or working with non-standard numeral systems. It's commonly used in applications requiring URL-safe identifiers, hash-like strings, or custom numbering systems.

## State:
- digits (str): Instance attribute storing the character set used for the target numeral system. Must contain unique characters representing digits in ascending order of value. This defines the base for conversions.
- decimal_digits (str): Class attribute containing "0123456789" - the standard decimal digit set used as the source for encoding operations and the target for decoding operations.

## Lifecycle:
- Creation: Instantiate with a string of unique characters representing the digit set for the target base (e.g., BaseConverter("0123456789ABCDEF") for hexadecimal)
- Usage: Call encode() to convert integers to the custom base representation, or decode() to convert strings back to integers
- Destruction: No special cleanup required; standard Python garbage collection handles object destruction

## Method Map:
```mermaid
graph TD
    A[BaseConverter.__init__] --> B[BaseConverter.encode]
    A[BaseConverter.__init__] --> C[BaseConverter.decode]
    B --> D[BaseConverter.convert (static)]
    C --> D
    D --> E[convert static method]
```

## Raises:
- None explicitly raised by __init__
- The convert static method may raise ValueError if invalid characters are encountered in input strings (though this isn't explicitly handled in the current implementation)

## Example:
```python
# Create a hexadecimal converter
hex_converter = BaseConverter("0123456789ABCDEF")

# Encode a decimal number to hex
encoded = hex_converter.encode(255)  # Returns "FF"

# Decode a hex string back to decimal
decoded = hex_converter.decode("FF")  # Returns 255

# Create a binary converter
bin_converter = BaseConverter("01")
binary_encoded = bin_converter.encode(10)  # Returns "1010"
binary_decoded = bin_converter.decode("1010")  # Returns 10

# Create a custom base-36 converter
base36_converter = BaseConverter("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
custom_encoded = base36_converter.encode(12345)  # Returns "9IX"
custom_decoded = base36_converter.decode("9IX")  # Returns 12345
```

### `datasette.utils.baseconv.BaseConverter.__init__` · *method*

## Summary:
Initializes a BaseConverter instance with a custom digit set for numeral system conversion.

## Description:
The __init__ method sets up a BaseConverter instance by storing the provided digit set as an instance attribute. This digit set defines the characters used to represent digits in the target numeral system for encoding and decoding operations. The method is called during object instantiation and establishes the fundamental configuration needed for all subsequent base conversion operations.

This logic is separated into its own method rather than being inlined because:
1. It follows the standard Python convention for object initialization
2. It allows for clear separation of concerns between object creation and usage
3. It enables proper encapsulation of the digit set configuration
4. It makes the class easier to test and extend

## Args:
    digits (str): A string containing unique characters that define the digit set for the target numeral system. Characters must be arranged in ascending order of their numeric value. For example, "0123456789ABCDEF" represents hexadecimal with digits 0-9 followed by A-F.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not explicitly raise exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.digits - stores the provided digit set as an instance attribute

## Constraints:
    Preconditions:
    - The digits parameter must be a string
    - The string must contain unique characters (no repeated digits)
    - Characters in the string should be ordered from lowest to highest numeric value
    - The string should not be empty (though technically this would work, it would create a degenerate base system)

    Postconditions:
    - The self.digits attribute is set to the provided digits string
    - The instance is ready for encode() and decode() operations using the specified digit set

## Side Effects:
    None: This method performs no I/O operations, external service calls, or mutations to objects outside the instance.

### `datasette.utils.baseconv.BaseConverter.encode` · *method*

*No documentation generated.*

### `datasette.utils.baseconv.BaseConverter.decode` · *method*

## Summary:
Converts a string representation in custom base to its decimal integer equivalent.

## Description:
Decodes a string value from a custom base system (defined by the converter's digit set) into its corresponding decimal integer representation. This method uses an internal convert method to transform the input string from the custom base digits to decimal digits, then converts the result to an integer.

## Args:
    s (str): String representation of a number in the custom base system defined by self.digits

## Returns:
    int: The decimal integer equivalent of the input string in the custom base system

## Raises:
    ValueError: If the input string contains characters not present in self.digits
    TypeError: If the input string is not of string type

## State Changes:
    Attributes READ: self.digits, self.decimal_digits
    Attributes WRITTEN: None

## Constraints:
    Preconditions: 
    - Input string s must contain only characters from self.digits
    - self.digits must define a valid character set for base conversion
    - self.decimal_digits must define a valid decimal digit mapping
    
    Postconditions:
    - Returns an integer representing the decimal value of the input string
    - The returned integer is equivalent to the mathematical value represented by s in the custom base system

## Side Effects:
    None

### `datasette.utils.baseconv.BaseConverter.convert` · *method*

## Summary:
Converts a number from one numeral system to another by mapping digits between different base representations.

## Description:
This method performs base conversion between arbitrary numeral systems by first converting the input number to decimal (base 10), then converting that decimal value to the target numeral system. It properly handles negative numbers and supports custom digit mappings for both source and target bases.

## Args:
    number (int or str): The number to convert, represented as either an integer or string. If negative, the minus sign is preserved.
    fromdigits (str or list): The set of characters representing digits in the source numeral system, ordered from lowest to highest value.
    todigits (str or list): The set of characters representing digits in the target numeral system, ordered from lowest to highest value.

## Returns:
    str: The converted number represented as a string using the target numeral system's digits.

## Raises:
    IndexError: When a digit in the input number is not found in the fromdigits parameter.

## State Changes:
    None - This is a pure function that does not modify any object state.

## Constraints:
    Preconditions:
        - fromdigits and todigits must be non-empty sequences
        - All characters/digits in the input number must exist in fromdigits
        - The input number must be a valid representation in the fromdigits system
    
    Postconditions:
        - The returned string contains only characters from todigits
        - Negative numbers are properly handled with leading minus sign
        - Zero is always represented as the first character in todigits

## Side Effects:
    None - This function performs no I/O operations or external service calls.

