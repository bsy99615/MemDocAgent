# `baseconv.py`

## `datasette.utils.baseconv.BaseConverter` · *class*

## Summary:
A small utility class that encodes integers (or numeric strings) into an arbitrary positional numeral system defined by a custom digit alphabet, and decodes strings in that alphabet back to integers.

## Description:
BaseConverter encapsulates conversion between a source "decimal" digit alphabet ("0123456789") and a target alphabet supplied at construction (the instance's digits). Use this class when you need to represent integer values in a custom base with arbitrary symbols (for example, base36, base62, custom short-id alphabets).

Motivation and responsibility:
- Provides a single, focused abstraction: mapping between two positional numeral systems (the builtin decimal alphabet and a user-supplied alphabet).
- Keeps the conversion algorithm in one place so callers need not manage base arithmetic or sign handling.
- It does not validate or normalize alphabets beyond what the algorithm requires; callers are responsible for providing a sensible digit alphabet (see State and Raises).

Stateless method guarantees:
- encode() and decode() are pure with respect to the BaseConverter instance: they return values derived from inputs and the instance's digits attribute, and they do not modify any instance or class-level state. It is therefore safe and intended to reuse the same BaseConverter instance to perform many conversions.

Known callers/factories:
- Constructed directly by passing the target alphabet string to __init__.
- Typical usage: instantiate with a constant alphabet (for example, for URL shortener tokens), then call encode() to get a string token and decode() to get an integer back. Because methods do not mutate instance state, a single instance may be reused safely.

## State:
Attributes (instance and class-level):

- decimal_digits (class attribute) : str
  - Value: "0123456789"
  - Purpose: canonical source digits used by encode() to interpret integer inputs as decimal when encoding.

- digits (instance attribute) : str
  - Set in __init__(digits)
  - Type: string of characters representing symbols for the target base (e.g., "0123456789abcdefghijklmnopqrstuvwxyz" for base36).
  - Valid range/constraints:
    - Must be a non-empty string. Practically, to avoid infinite loops and to represent positional bases properly, its length should be at least 2.
    - Characters should be unique (no duplicates) so each symbol maps to exactly one digit value; duplicates will make indexing ambiguous and can produce incorrect conversions.
    - Should not include the minus sign '-' to avoid ambiguous interaction with negative-number handling (the algorithm strips a leading '-' from input strings).
  - Invariant: len(digits) determines the target base; digits must be considered the ordered symbol list for that base.

Class invariants:
- decimal_digits is constant and represents the source decimal alphabet.
- For any valid input and provided digits alphabet meeting constraints, encode() and decode() are inverses (decode(encode(n)) == n for integers n that fit the documented behavior).

## Lifecycle:
Creation:
- Instantiate with the target alphabet:
  - bc = BaseConverter("0123456789abcdefghijklmnopqrstuvwxyz")
  - Required argument: digits (str). No defaults.

Usage:
- Because encode() and decode() do not modify the instance, usage is simple and order-independent:
  - Call encode(i) to convert an integer (or decimal-digit string) into the configured digit alphabet.
  - Call decode(s) to convert a string in the configured digit alphabet back to an integer.
- Methods may be called in any order and repeatedly; there is no required sequencing.
- The class is safe to reuse across threads only if the digits attribute is not mutated externally (note: the class itself does not guard against external mutation of the digits attribute).

Destruction:
- No special cleanup required. The class does not manage external resources and does not implement context manager or close().

## Method Map:
flowchart LR
    A[__init__(digits)] --> B[encode(i)]
    A --> C[decode(s)]
    B --> D[convert(number, fromdigits, todigits)]
    C --> D
    note right of D: static core algorithm; handles sign, positional conversion

## Detailed behavior (convert algorithm) and reimplementation notes:
- convert(number, fromdigits, todigits) is the static routine implementing conversion from a numeral string in alphabet fromdigits to a numeral string in alphabet todigits. It accepts either a numeric value or a string as number; it starts by coercing number to str(number).
- Sign handling:
  - If the first character of str(number) is '-', convert strips it and records neg = True. The negative sign is re-applied to the result if and only if the input had a leading '-' and the numeric magnitude is non-zero.
- Parsing from "fromdigits" to an integer magnitude:
  - The algorithm iterates characters in str(number) and for each digit character uses fromdigits.index(digit) to obtain its numeric value. The accumulated magnitude x is computed by repeated multiplication by the base (len(fromdigits)) and addition of the digit value.
  - If a character in number is not present in fromdigits, fromdigits.index(digit) raises ValueError; this indicates invalid input.
- Handling zero:
  - If the computed magnitude x equals 0, the function returns todigits[0] (the zero symbol in the target alphabet). Note: this covers the input "0" and the edge case where all digits map to zero.
- Converting magnitude to "todigits":
  - Repeatedly compute digit = x % len(todigits), pre-pend todigits[digit] to the output string, and set x = int(x / len(todigits)) until x becomes 0.
  - Important implementation constraint: len(todigits) must be >= 2 in typical positional numeral systems. If len(todigits) == 1, int(x / 1) == x and the loop is infinite for x > 0.
- Negative zero:
  - If the input had a leading '-', and the magnitude computed is zero, the returned result will be the zero symbol (not prefixed with '-'); that matches the algorithm which re-applies '-' only inside the x > 0 branch.
- Return types:
  - convert returns a string (the textual representation in todigits).
  - encode returns the convert result when converting from decimal_digits to self.digits.
  - decode returns int(self.convert(s, self.digits, self.decimal_digits)) — convert returns a decimal string which int() then converts to an integer.

## Raises:
The implementation may raise the following exceptions; callers should validate or catch them as appropriate.

- IndexError
  - Trigger: calling convert(number, ...) when str(number) is empty (str(number)[0] indexing fails). In practice, passing an empty string as number triggers this.
  - Mitigation: ensure number is non-empty.

- ValueError
  - Trigger: when a character in the input number is not found in fromdigits (fromdigits.index(digit) raises ValueError).
  - Examples:
    - encode expects an integer or a decimal-string; if the decimal string contains characters not in "0123456789" it will raise ValueError.
    - decode expects s to contain only characters that were provided in self.digits; otherwise decode will raise ValueError.

- Infinite loop / logical failure (not an exception but a strong precondition)
  - If len(todigits) <= 1 and the magnitude x > 0, the conversion loop will not terminate (because x // base will not decrease). Therefore, require len(todigits) >= 2 for meaningful multibase conversion.

## Example:
- Create converter for base36:
  - digits = "0123456789abcdefghijklmnopqrstuvwxyz"
  - bc = BaseConverter(digits)
  - token = bc.encode(1000)  # produce a short string token
  - value = bc.decode(token)  # should be 1000

- Negative numbers:
  - bc.encode(-42) -> "-16" (example depends on alphabet)
  - bc.decode("-16") -> -42

Implementation hints for reimplementation:
- Implement convert as a static method that accepts (number, fromdigits, todigits).
- Convert number to string first; test for leading '-' to handle negative inputs.
- Parse digits by repeatedly applying x = x * base + index_of_digit.
- Use modular arithmetic and integer division (floor division or int()) to build the output in the target base.
- Validate alphabets before use: require todigits length >= 2 and require unique characters in fromdigits and todigits to avoid ambiguous mapping and infinite loops.

### `datasette.utils.baseconv.BaseConverter.__init__` · *method*

## Summary:
Assigns the provided digit-symbols container to the instance so the converter has its digit set available as state.

## Description:
This is the constructor for the BaseConverter object. It is invoked when a BaseConverter instance is created (i.e., during object instantiation) to establish the initial digit-symbol set the instance will use. The method's logic is intentionally minimal and kept separate as the class initializer so that object construction and attribute initialization are centralized and easy to override in subclasses.

Known callers and lifecycle stage:
    - Called automatically when constructing a BaseConverter (e.g., BaseConverter(digits)), during the object creation / initialization stage.
    - Should be invoked exactly once per instance as part of normal instantiation.

Why this is a separate method:
    - As the class constructor, it establishes the object's initial state in one place and allows subclasses to call or extend initialization behavior consistently.

## Args:
    digits (any):
        The value provided by the caller that represents the set or sequence of digit symbols the converter will use.
        - No type is enforced by this method; callers may pass a string, list, tuple, or any other object.
        - Typical use: a string of characters used as digit symbols (e.g., "0123456789abcdef"), but this is convention, not enforced.

## Returns:
    None
    - The method does not return a value; it initializes instance state.

## Raises:
    None
    - This constructor does not raise exceptions itself. Any exception would only occur if assignment to instance attributes triggers an unusual error (extremely unlikely in normal Python usage).

## State Changes:
    Attributes READ:
        - None (the method does not read any existing instance attributes)

    Attributes WRITTEN:
        - self.digits: set to the provided digits argument

## Constraints:
    Preconditions:
        - No preconditions are enforced by this method; any value for digits is accepted.
        - Callers should ensure digits is suitable for later conversion logic (e.g., provides a unique ordered set of symbols) if they expect correct converter behavior.

    Postconditions:
        - After return, self.digits is equal to the digits argument passed in (identity or value-equals depending on the object type).
        - The instance is initialized with its primary digit-symbol attribute set and ready for any methods that depend solely on self.digits.

## Side Effects:
    - No external I/O or external service interactions.
    - Mutation: assigns to the instance attribute self.digits; no other objects are mutated by this method.

### `datasette.utils.baseconv.BaseConverter.encode` · *method*

## Summary:
Encode a decimal integer or decimal-digit string into this converter's configured digit alphabet, returning the result as a string and leaving the object state unchanged.

## Description:
- Known callers and context:
    - Any runtime code that needs to produce a representation of a decimal number in the converter's configured base will call this method. Typical lifecycle: a conversion/serialization step where an integer (or a decimal-digit string) must be expressed using the instance's digit alphabet.
    - This method is the instance-facing API for converting from decimal to the instance's digit set; the heavy lifting is delegated to the shared static convert utility.
- Reason for being a separate method:
    - Provides a small, readable instance-level API that automatically supplies the decimal source alphabet (class attribute) and the instance-specific target alphabet (self.digits) to the generic conversion routine.
    - Encapsulation avoids repeating the from/to alphabet wiring at every call site and hides the static convert signature from callers.

## Args:
    i (int | str):
        - The value to encode. Accepts an integer or a string composed of decimal digit characters.
        - If an int: its value is interpreted in base 10 and converted.
        - If a str: it may include a leading '-' to indicate negativity; all non-sign characters must be characters in "0123456789".
        - No default.

## Returns:
    str:
        - The input value represented as a string composed only of characters from self.digits, with a leading '-' if the input was negative.
        - Special-case: numeric zero is returned as the first character of self.digits (self.digits[0]).
        - Examples:
            * If self.digits == "01", encode(10) -> "1010".
            * If self.digits == "abcdefghijklmnopqrstuvwxyz", encode(0) -> "a".

## Raises:
    ValueError:
        - Propagated from the underlying convert call when a non-sign character in the input string is not found in the decimal alphabet ("0123456789"). This occurs when a str input contains non-decimal characters.
    IndexError:
        - Propagated if the string form of the input is empty (attempting to inspect str(i)[0] in convert). This indicates an invalid empty input.
    ZeroDivisionError:
        - Propagated if len(self.digits) == 0 (division/modulo by zero inside convert).
    Non-termination / Logical failure:
        - If len(self.digits) == 1 the conversion algorithm will not terminate correctly (division by 1 never reduces the value). This is a logical invalid case (not a raised exception) and must be avoided.

## State Changes:
Attributes READ:
    - self.decimal_digits (class attribute): read and passed as the source alphabet ("0123456789").
    - self.digits: read and passed as the target alphabet.
Attributes WRITTEN:
    - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.digits must be a non-empty string of unique characters (recommended length >= 2 for meaningful positional conversion).
    - The instance must have been constructed so that self.digits is defined.
    - If passing a string for i, it must be non-empty and contain only characters from "0123456789" apart from an optional leading '-' sign.
    - If passing an int for i, it should be a finite integer value (negative allowed).

Postconditions:
    - Returns a string that represents the same integer value as the input, expressed using characters from self.digits.
    - The returned string will be prefixed with '-' if and only if the input had a leading '-' or was a negative integer.
    - When the numeric value is zero, the result equals self.digits[0].

## Side Effects:
    - No I/O, no network calls, and no mutation of external objects.
    - Only effect is invoking the static convert function which performs pure computation and may raise exceptions as documented above.

### `datasette.utils.baseconv.BaseConverter.decode` · *method*

## Summary:
Return the integer value represented by the input string when interpreted using this converter's digit alphabet, without modifying the BaseConverter instance.

## Description:
This method decodes a string expressed in the instance's source digit alphabet (self.digits) into a Python int. It delegates conversion to the BaseConverter.convert staticmethod to map characters from self.digits to decimal digit characters, then casts the result to int.

Known callers and context:
- Complementary to BaseConverter.encode; together they form a pair for encoding integers into an alternate digit alphabet and decoding them back.
- No explicit callers are recorded in the provided memory snapshot. Typical usage: decoding short identifiers, obfuscated numeric tokens, or custom-base numeric strings back into integers during request handling or data-processing pipelines.

Why this is a separate method:
- It provides a convenience API that returns a typed integer instead of the decimal string returned by convert. Centralizing the int() cast here avoids repeating it at call sites and clearly expresses the intended return type.

## Args:
    s (str or any): Value to decode. The method uses str(s) internally, so non-string inputs are accepted as long as their string representation conforms.
    - Expected form: a non-empty string composed only of characters found in self.digits, optionally prefixed with a single '-' to indicate negativity.
    - The '+' sign is not specially handled and will be treated as an invalid digit unless '+' is present in self.digits.

## Returns:
    int: The integer interpreted from s in base len(self.digits) using index positions in self.digits as digit values.
    - Examples:
        - If self.digits = "0123456789", decode("123") -> 123
        - If self.digits = "0123456789abcdef" (hex alphabet), decode("a") -> 10
        - Leading '-' yields a negative integer, e.g. decode("-1") -> -1
    - Edge returns:
        - Returns 0 for inputs representing zero (for example the single-character self.digits[0]).
        - For very large inputs the returned int is arbitrary-precision (Python int).

## Raises:
    IndexError:
        - If str(s) is an empty string. BaseConverter.convert accesses str(number)[0]; an empty string will cause IndexError.
    ValueError:
        - If any character in str(s) (after an optional leading '-') is not present in self.digits. This comes from fromdigits.index(digit) inside convert.
        - If for some reason convert returns a string that int(...) cannot parse as a base-10 integer (not expected when convert maps to the standard decimal_digits).
    AttributeError:
        - If self.digits does not provide an index method (e.g., an inappropriate type), calling fromdigits.index(...) will raise AttributeError.
    TypeError:
        - If self.digits does not support len(), or if an inappropriate type is used such that len(fromdigits) or other operations inside convert raise TypeError.

## State Changes:
    Attributes READ:
        - self.digits
        - self.decimal_digits
    Attributes WRITTEN:
        - None (this method does not mutate self)

## Constraints:
    Preconditions:
        - self.digits must be a sequence-like object supporting len() and index() (commonly a string or list of characters).
        - Characters in self.digits should ideally be unique to avoid ambiguous digit values (the code does not enforce uniqueness).
        - str(s) must not be empty and should consist only of characters from self.digits, optionally with a single leading '-' to indicate negativity.
    Postconditions:
        - The BaseConverter instance is unchanged.
        - The returned int equals the numeric value of s interpreted in base len(self.digits) using indices in self.digits as digit values.

## Side Effects:
    - No I/O, network access, or mutation of objects outside self.
    - CPU and memory cost are proportional to the length of str(s) and to the numeric magnitude of the value being converted (convert computes an intermediate integer magnitude and builds a string during its processing).

### `datasette.utils.baseconv.BaseConverter.convert` · *method*

## Summary:
Convert a number expressed in one digit alphabet into its representation using another digit alphabet, preserving sign; returns the converted value as a string.

## Description:
Known callers and call context:
- BaseConverter.encode(i): passes an integer i as number, fromdigits equal to the decimal digit alphabet ("0123456789"), and todigits equal to the instance's digits; used when encoding a Python integer into the converter's configured base (lifecycle: runtime conversion step when producing a short/alternate representation).
- BaseConverter.decode(s): passes a string s in the converter's digit alphabet as number, fromdigits equal to the instance's digits, and todigits equal to the decimal alphabet; used when decoding a string representation back to decimal (lifecycle: parsing stage when interpreting external input).
- The method is declared and used as a static utility so it can be shared by both encode and decode without requiring an instance; centralizing the logic avoids duplicating the base-conversion algorithm.

What it does:
- Interprets the input number (string or integer) in the numeric base defined by fromdigits, computes its integer value, then emits the equivalent representation using the digit characters in todigits. If the input is negative (leading '-'), the sign is preserved on the output.

## Args:
    number (int | str):
        - An integer or a string containing digits drawn from the fromdigits alphabet.
        - If a string, it may include a leading '-' to indicate negation.
        - The string must be non-empty and composed only of characters present in fromdigits (except a leading '-' which indicates negative).
    fromdigits (str):
        - Sequence of characters used as source-digit symbols, ordered so that fromdigits[0] represents value 0, fromdigits[1] value 1, etc.
        - Length must be >= 2 for meaningful positional numeral systems; characters should be unique to avoid ambiguous interpretation.
    todigits (str):
        - Sequence of characters used as target-digit symbols, ordered so that todigits[0] represents value 0, todigits[1] value 1, etc.
        - Length must be >= 2 (length 0 causes immediate ZeroDivisionError; length 1 produces a non-terminating loop in this algorithm).
        - Characters should be unique.

## Returns:
    str:
        - A string composed of characters exclusively from todigits, optionally prefixed with '-' for negative inputs.
        - Special case: when the numeric value is zero, the return value is todigits[0].
        - Examples:
            * convert(10, "0123456789", "01") -> "1010"  (decimal 10 -> binary)
            * convert("ff", "0123456789abcdef", "0123456789") -> "255"
            * convert(0, "0123456789", "abcdefghijklmnopqrstuvwxyz") -> "a"  (0 represented by first todigits char)

## Raises:
    ValueError:
        - Raised when a non-sign character in the input string is not found in fromdigits (fromdigits.index(digit)).
    IndexError:
        - Raised when str(number) is an empty string (str(number)[0] access), which is an invalid input.
    ZeroDivisionError:
        - Raised when len(todigits) == 0 due to modulo/division by zero operations.
    Note:
        - If todigits has length 1 the algorithm will not terminate (division by 1 yields the same value), so such inputs should be avoided; this is a logical constraint rather than an explicit exception from this function.

## State Changes:
Attributes READ:
    - None (the function is a static utility and does not read or depend on instance/class attributes).
Attributes WRITTEN:
    - None (the function does not modify object or global state).

## Constraints:
Preconditions:
    - fromdigits and todigits must be ordered sequences where each character's index denotes its digit value (index -> numeric value).
    - fromdigits and todigits must have length >= 2 for correct, terminating positional conversion behavior.
    - If passing a string for number, it must be non-empty and its characters (excluding an optional leading '-') must all exist in fromdigits.
    - number should be convertible to a string (the code uses str(number) internally).

Postconditions:
    - The returned string represents the same integer value as the input number, expressed with digits drawn from todigits, with a leading '-' if and only if the input had a leading '-'.
    - The returned string will be a single-character representation equal to todigits[0] when the numeric value is zero.

## Side Effects:
    - Pure computation only; no I/O, no network access, and no mutation of objects outside the scope of the function.
    - Possible exceptions as described above are raised synchronously.

## Implementation notes / reimplementation recipe:
    1. Accept number (int or str), fromdigits (str), todigits (str).
    2. Convert number to string to inspect sign; if it begins with '-', remember negativity and remove that leading character for parsing.
    3. Compute the integer value x by iterating over each character of the (unsigned) number string:
         - For each digit character d: x = x * len(fromdigits) + index_of(d in fromdigits).
         - This accumulates the positional value in base len(fromdigits).
    4. If x == 0, return todigits[0] (with '-' prefixed if input was negative).
    5. Otherwise, build the output string by repeatedly:
         - digit_value = x % len(todigits)
         - prepend todigits[digit_value] to the result string
         - x = x // len(todigits)   (integer division)
       Repeat until x == 0.
    6. If the original input was negative, prefix the result with '-'.
    7. Return the resulting string.

