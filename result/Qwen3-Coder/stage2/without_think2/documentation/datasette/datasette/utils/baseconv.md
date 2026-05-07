# `baseconv.py`

## `datasette.utils.baseconv.BaseConverter` · *class*

## Summary:
A base conversion utility class that converts integers to and from custom numeral systems defined by digit sequences.

## Description:
The BaseConverter class provides functionality to encode integers into strings using a custom digit set and decode strings back into integers. It serves as a flexible converter that can work with any base system by defining appropriate digit sequences. This abstraction allows for easy conversion between standard decimal numbers and custom bases like hexadecimal, binary, or even user-defined numeral systems.

## State:
- digits (str): The sequence of characters representing digits in the target numeral system. Must contain unique characters and cannot be empty.
- decimal_digits (str): Class attribute containing standard decimal digits "0123456789" used internally for conversions.

## Lifecycle:
- Creation: Instantiate with a string of unique characters representing the digit set for the desired base system.
- Usage: Call encode() to convert integers to strings in the custom base, or decode() to convert strings back to integers.
- Destruction: No special cleanup required; uses standard Python garbage collection.

## Method Map:
```mermaid
graph TD
    A[BaseConverter] --> B[encode(i)]
    A --> C[decode(s)]
    B --> D[convert(i, decimal_digits, digits)]
    C --> E[convert(s, digits, decimal_digits)]
    D --> F[convert static method]
    E --> F
```

## Raises:
- None explicitly raised by __init__
- The convert static method may raise ValueError if invalid characters are encountered in input strings

## Example:
```python
# Create a binary converter
binary_conv = BaseConverter("01")

# Encode integer to binary string
binary_string = binary_conv.encode(42)  # Returns "101010"

# Decode binary string back to integer
integer_value = binary_conv.decode("101010")  # Returns 42

# Create a custom base-36 converter
base36_conv = BaseConverter("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Encode integer to base-36 string
base36_string = base36_conv.encode(12345)  # Returns "3D7"
```

### `datasette.utils.baseconv.BaseConverter.__init__` · *method*

## Summary:
Initializes a BaseConverter instance with a set of digit characters for base conversion.

## Description:
This method sets up the digit mapping used for converting numbers between different bases. It is called during object instantiation to configure the converter with the appropriate digit set.

## Args:
    digits (str): A string containing unique characters that represent digits in the target base system.

## Returns:
    None: This method does not return a value.

## Raises:
    None: This method does not raise any exceptions.

## State Changes:
    Attributes READ: None
    Attributes WRITTEN: self.digits

## Constraints:
    Preconditions: The digits argument must be a string with unique characters.
    Postconditions: The self.digits attribute will contain the provided digit string.

## Side Effects:
    None: This method has no side effects beyond setting the instance attribute.

### `datasette.utils.baseconv.BaseConverter.encode` · *method*

## Summary:
Encodes a decimal integer into a string representation using a custom digit set.

## Description:
The encode method converts a decimal integer into a string representation using the BaseConverter's configured digit set. This method leverages the shared convert function to perform the actual base conversion, making it suitable for encoding integers into various numeral systems defined by the instance's digit configuration. The method specifically uses the class-level decimal_digits ("0123456789") as the source base and the instance's self.digits as the target base.

## Args:
    i (int): The decimal integer to encode

## Returns:
    str: The encoded string representation using the converter's digit set

## Raises:
    None explicitly raised.

## State Changes:
    Attributes READ: self.decimal_digits, self.digits
    Attributes WRITTEN: None

## Constraints:
    Preconditions: The input integer must be a valid integer type
    Postconditions: The returned string will only contain characters from self.digits

## Side Effects:
    None

### `datasette.utils.baseconv.BaseConverter.decode` · *method*

## Summary:
Decodes a string representation of a number from a custom base system into its decimal integer equivalent.

## Description:
This method converts a string value from a custom base system (defined by the instance's digits) back to its decimal integer representation. It leverages the shared convert function to perform the base conversion, specifically interpreting the input string as being in the custom base and converting it to decimal form. This method is part of the BaseConverter class which provides bidirectional conversion between custom bases and decimal integers. The decode operation is the inverse of the encode operation.

## Args:
    s (str): String representation of a number in the custom base system defined by self.digits.

## Returns:
    int: The decimal integer equivalent of the input string in the custom base system.

## Raises:
    ValueError: If any character in the input string is not found in self.digits.

## State Changes:
    Attributes READ: self.digits, self.decimal_digits
    Attributes WRITTEN: None

## Constraints:
    Preconditions:
        - The input string s must contain only characters that exist in self.digits
        - The instance must have been initialized with a valid digits string
    Postconditions:
        - Returns a positive or negative integer representing the decimal value
        - The returned integer is the mathematical equivalent of the input in the custom base

## Side Effects:
    None

### `datasette.utils.baseconv.BaseConverter.convert` · *method*

## Summary:
Converts a number from one base system to another base system using positional notation conversion.

## Description:
This function converts a number represented in one base system (defined by fromdigits) to another base system (defined by todigits). It implements the standard algorithm for base conversion by first converting the input to decimal, then converting from decimal to the target base. The function handles negative numbers by preserving the sign in the final result.

## Args:
    number (int or str): The number to convert, represented as an integer or string.
    fromdigits (str or list): The digits used in the source base system, ordered from smallest to largest value.
    todigits (str or list): The digits used in the target base system, ordered from smallest to largest value.

## Returns:
    str: The converted number represented as a string using the target base's digit set.

## Raises:
    ValueError: If any digit in the input number is not found in the fromdigits set.

## State Changes:
    None

## Constraints:
    Preconditions:
        - The fromdigits and todigits parameters must define valid digit sets where each character/digit appears only once.
        - All characters in the input number must be present in the fromdigits set.
        - The number parameter must be convertible to a string representation.

    Postconditions:
        - The returned string will only contain characters from the todigits set.
        - The result represents the same numerical value as the input number.

## Side Effects:
    None

