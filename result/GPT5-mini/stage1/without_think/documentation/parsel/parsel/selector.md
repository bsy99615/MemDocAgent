# `selector.py`

## `parsel.selector.CannotRemoveElementWithoutRoot` · *class*

## Summary:
A sentinel exception type indicating that an element removal operation cannot proceed because there is no root context available.

## Description:
This class is a specialized Exception used to signal an error condition when code attempts to remove or detach an element but there is no containing root/document node available to perform or validate the operation. It exists to provide a distinct, catchable error type so callers can handle this specific failure separately from generic exceptions.

Typical scenarios for instantiation:
- An operation that removes or detaches an element from a parsed document discovers that the element has no associated root node (document/tree) and therefore the removal is invalid.
- Libraries or code paths manipulating HTML/XML element trees that require a root to maintain invariants (e.g., updating ancestry, serializing, or reparenting) detect a precondition failure.

Known callers/factories:
- The class definition itself does not include usage sites. Callers are any code paths that need a specific exception to indicate the "no root" removal failure. Because it is a plain subclass of Exception, it is instantiated directly with an optional message.

Motivation and responsibility boundary:
- Provides semantic clarity: raising CannotRemoveElementWithoutRoot is preferable to raising a generic Exception or ValueError when the specific failure mode needs to be detected and handled.
- Responsibility: only to represent that specific error condition. It carries no logic or additional state beyond standard Exception behavior.

## State:
- Class type: CannotRemoveElementWithoutRoot (subclass of Exception)
- Attributes: none defined on this class.
- Inherited attributes: standard Exception attributes (args tuple, and stringification via str()).
- __init__ parameters:
    - Accepts arbitrary positional arguments forwarded to Exception.__init__(*args). Typically callers pass a single message string describing the problem; no positional or keyword parameters are defined by this class itself.
- Valid values / invariants:
    - There are no additional invariants enforced by this class beyond those of Exception.
    - The args attribute may contain any objects provided by the caller; callers should pass serializable and human-readable messages for effective logging.

## Lifecycle:
- Creation:
    - Instantiate directly by calling CannotRemoveElementWithoutRoot() or with an explanatory message: CannotRemoveElementWithoutRoot("element has no root").
    - No factory or helper is provided by the class itself.
- Usage:
    - Raise to signal the error: raise CannotRemoveElementWithoutRoot("reason")
    - Catch by type when handling this specific condition:
        try:
            ...
        except CannotRemoveElementWithoutRoot:
            ...
    - No methods are defined on the class beyond those inherited from Exception.
- Destruction / cleanup:
    - No cleanup responsibilities (no context manager protocol, no close() method). Normal exception object lifecycle applies and is managed by Python runtime.

## Method Map:
- This class defines no custom methods. Typical interaction graph (textual/mermaid):
graph TD
    A[Calling code detects missing root] --> B[Instantiate CannotRemoveElementWithoutRoot]
    B --> C[raise exception]
    C --> D[Caller or outer scope catches CannotRemoveElementWithoutRoot]

## Raises:
- __init__: This class's constructor does not raise exceptions on its own. It directly inherits Exception.__init__; therefore, typical usage will not raise during instantiation.
- When raised: the exception object itself communicates the failure; any handlers should inspect the message or catch by type.

## Example:
- Create and raise:
    raise CannotRemoveElementWithoutRoot("cannot remove element: no root document attached")

- Catch and handle:
    try:
        # operation that may detect missing root and raise
        remove_element(some_element)
    except CannotRemoveElementWithoutRoot as exc:
        # handle the specific "no root" case (log, reparent, skip, or surface a user-friendly error)
        log_warning(str(exc))

## `parsel.selector.CannotRemoveElementWithoutParent` · *class*

## Summary:
A simple, named exception class (subclass of Exception). The class itself does not implement behavior beyond naming the error condition "CannotRemoveElementWithoutParent" for use by other code.

## Description:
- Definition: The source declares class CannotRemoveElementWithoutParent(Exception): pass — i.e., a direct subclass of built-in Exception with no additional methods or attributes.
- What is known from the source:
    - The class exists solely to provide a distinct exception type.
    - There is no constructor override, no custom attributes, and no methods defined in this class.
- What is not present in the source:
    - The file does not define places that raise this exception; no callers or factories are shown in the provided source excerpt.
    - Any higher-level semantics (for example, the exact circumstances under which calling code should raise this exception) are not implemented here and are only implied by the class name.
- Usage guidance (general, applicable to any Exception subclass):
    - Other modules may raise this exception to signal a specific error condition.
    - Callers can catch this specific exception type to handle that condition distinctly from other exceptions.

## State:
- Inheritance: subclass of Exception.
- Attributes (inherited from Exception):
    - args (tuple): Holds positional constructor arguments passed when the exception is instantiated. Typical use: args == (message: str,).
    - __str__ and __repr__ behaviors: Inherited from Exception; stringification will reflect args per standard Exception semantics.
- No additional attributes or slots are defined by this class in the source.
- Invariants:
    - The class imposes no additional invariants beyond those of Exception.
    - Instances are plain Exception instances; the class does not participate in any internal state management.

## Lifecycle:
- Creation:
    - Instantiate via the standard exception pattern: raise CannotRemoveElementWithoutParent() or raise CannotRemoveElementWithoutParent("explanatory message").
    - The class does not define a custom __init__, so all constructor behavior is inherited from Exception.
- Usage:
    - Typical exception lifecycle: raised at the point of error; optionally caught by surrounding code via an except CannotRemoveElementWithoutParent: clause.
    - There is no required method-call ordering related to this class itself.
- Destruction / cleanup:
    - No special cleanup or context-manager behavior; normal exception object lifetime applies, with no explicit resources to release.

## Method Map:
flowchart LR
    R[Calling code detects an error condition] --> S{Raise explicit exception?}
    S -- Yes --> T[raise CannotRemoveElementWithoutParent(optional message)]
    T --> U[Exception propagates to nearest except handler]
    U --> V[Handler catches CannotRemoveElementWithoutParent or it propagates further]

## Raises:
- The class definition itself does not raise exceptions during normal import or instantiation (it uses the default Exception.__init__).
- Semantic: other code may raise this exception to indicate a specific error; the trigger conditions for such raises are not present in this class's source.

## Example:
- Instantiation and raising:
    - raise CannotRemoveElementWithoutParent("element <div id=1> has no parent")
- Catching:
    - try:
          do_something_that_may_raise()
      except CannotRemoveElementWithoutParent as exc:
          # Handle the specific "no parent" removal error here
          log_warning(str(exc))

Notes for implementers:
- To use this exception consistently, raise it where you detect the relevant error condition in caller code and include a clear message describing the element or operation. Avoid relying on message text for programmatic decisions; catch the exception type directly.

## `parsel.selector.CannotDropElementWithoutParent` · *class*

## Summary:
A named, specific exception type used to signal that an attempt to "drop" an element failed because the element has no parent. It exists purely as a distinct error type (marker) so calling code can raise and catch this condition explicitly.

## Description:
- Purpose and responsibility:
    - This class provides a distinct, semantic exception name for the specific error condition "cannot drop element without parent". It does not implement behavior beyond naming the condition.
- Typical scenarios / when to instantiate:
    - Instantiate and raise this exception when code attempts to perform a "drop" or similar removal/move operation on an element that requires a parent context but none is present.
    - Examples of where it would be appropriate for calling code to raise this exception include DOM-manipulation, tree-editing, or selector/transform operations that require a parent node to complete the operation.
- Known callers / factories:
    - The source for this class itself does not include callers. Any module that needs to surface the specific "drop without parent" error should raise this exception directly.
- Motivation:
    - Using a dedicated class (rather than raising a generic Exception or ValueError) enables precise exception handling: callers can catch CannotDropElementWithoutParent specifically and implement targeted recovery, logging, or user feedback.

## State:
- Inheritance:
    - Subclass of CannotRemoveElementWithoutParent, which in turn is a direct subclass of built-in Exception.
- Attributes:
    - No custom attributes are defined on this class.
    - Inherited attributes from Exception apply (for example, args: tuple holding positional constructor arguments).
- Valid values / invariants:
    - Instances contain whatever positional arguments the caller passes to Exception.__init__ (typically a single message string). The class itself imposes no additional constraints or invariants.

## Lifecycle:
- Creation:
    - Instantiate using standard Exception construction patterns. Required arguments: none. Optional: a message or other positional arguments passed to Exception, for example: CannotDropElementWithoutParent() or CannotDropElementWithoutParent("message").
    - There is no custom __init__; construction behavior is inherited from Exception.
- Usage:
    - Typical usage is immediate raising at the point the error is detected:
        - raise CannotDropElementWithoutParent("explanatory message")
    - Catching:
        - Surround the operation with an except CannotDropElementWithoutParent: block to handle this specific error.
    - No special sequencing or lifecycle methods are required — it is a plain exception class used in the standard raise/catch flow.
- Destruction / cleanup:
    - No cleanup responsibilities, context-manager behavior, or explicit resource management associated with instances of this class.

## Method Map:
flowchart LR
    A[Operation attempting to drop an element] --> B{Is parent present?}
    B -- No --> C[raise CannotDropElementWithoutParent(optional message)]
    B -- Yes --> D[Perform drop operation successfully]
    C --> E[Exception propagates to nearest except handler]
    E --> F[Handler catches CannotDropElementWithoutParent or it propagates further]

## Raises:
- The class definition itself does not raise exceptions during import or instantiation.
- The intended use is for other code to raise this exception when the "no parent" condition is detected. Trigger conditions must be implemented by callers (e.g., when an element.parent is None but the operation requires a parent).

## Example:
- Creation and raising (descriptive):
    - When code detects the missing-parent condition, raise this exception with an explanatory message. For example: raise CannotDropElementWithoutParent("element <div id=1> has no parent").
- Catching and handling (descriptive):
    - Wrap the operation in a try/except block and catch this exception specifically to apply recovery or logging logic.
- Notes:
    - Avoid relying on the exception message text for program logic; catch the class type directly for programmatic handling.

## `parsel.selector.SafeXMLParser` · *class*

## Summary:
A minimal subclass of lxml.etree.XMLParser that ensures the parser is created with resolve_entities set to False by default, reducing the risk of XML entity expansion vulnerabilities unless explicitly overridden.

## Description:
SafeXMLParser exists to centralize a safer default for XML parsing: it sets a default keyword argument resolve_entities=False when the caller does not supply that key. It does not implement additional parsing behavior or state management — all other behavior is inherited from lxml.etree.XMLParser.

When to instantiate:
- Use SafeXMLParser whenever you would normally construct an lxml XMLParser (for example, to pass as parser= to etree.fromstring or etree.parse) and you want entity resolution disabled by default.
- If a caller explicitly provides resolve_entities in keyword arguments, that value is honored and not overwritten.

Motivation and responsibility boundary:
- Motivation: avoid repeating the secure default across the codebase and reduce chances of accidentally enabling entity resolution (a common vector for XXE attacks).
- Responsibility: only sets a safe default for resolve_entities and delegates all other initialization to the lxml implementation. It does not validate or coerce argument types.

Known callers/factories:
- Any code that constructs an XML parser for lxml parsing APIs, e.g., code that passes parser=SafeXMLParser() to etree.fromstring, etree.parse, or similar utilities.

## State:
This class introduces no new public attributes beyond what is provided by lxml.etree.XMLParser. It relies entirely on the underlying lxml implementation for parser state.

- Constructor parameters (as accepted by the class signature):
    - *args: Any positional arguments; forwarded to lxml.etree.XMLParser.__init__ unchanged.
    - **kwargs: Any keyword arguments; forwarded to lxml.etree.XMLParser.__init__ after ensuring a default for resolve_entities.
        - resolve_entities: If the caller omits this key, SafeXMLParser sets it to False. If the caller supplies resolve_entities explicitly, that supplied value is used verbatim.

Invariants:
- After construction, the parser instance is configured identically to calling lxml.etree.XMLParser.__init__ with the same arguments, except that when resolve_entities is not provided it will be False.
- SafeXMLParser does not enforce type constraints on arguments; any type requirements are those of the underlying lxml constructor.

## Lifecycle:
Creation:
- Instantiate with the same positional and keyword arguments you would pass to lxml.etree.XMLParser.__init__.
- Omit resolve_entities to receive the secure default (False), or pass resolve_entities explicitly to override.

Usage:
- Typical usage is to construct the parser and supply it to lxml parsing functions. No special method ordering is required by SafeXMLParser itself.
- Example usage described in narrative form:
    - Create a parser with the safe default: instantiate SafeXMLParser() and pass it as parser= to etree.fromstring or etree.parse to parse XML content with entity resolution disabled by default.
    - To intentionally enable entity resolution, pass resolve_entities=True when constructing SafeXMLParser (note: enabling entity resolution should be done only with full understanding of the security implications).

Destruction / cleanup:
- No explicit cleanup API is provided by SafeXMLParser. Resource management follows lxml.etree.XMLParser semantics and Python garbage collection.

## Method Map:
- __init__(*args, **kwargs)
    - perform kwargs.setdefault("resolve_entities", False)
    - call lxml.etree.XMLParser.__init__(*args, **kwargs)

Mermaid diagram (method call flow):
graph TD
    A[Caller] --> B[SafeXMLParser.__init__]
    B --> C{ensure "resolve_entities" key exists}
    C -->|if missing| D[set resolve_entities=False]
    C -->|if present| E[leave provided value intact]
    D --> F[call lxml.etree.XMLParser.__init__(*args, **kwargs)]
    E --> F
    F --> G[Parser instance ready for use]

## Raises:
- SafeXMLParser.__init__ does not raise exceptions on its own beyond what the underlying lxml.etree.XMLParser.__init__ may raise. Any initialization errors, type errors, or lxml-specific exceptions propagate directly from the parent constructor.
- For details about specific exception types and error conditions, consult lxml.etree.XMLParser documentation.

## Example:
- Safe default parsing (narrative):
    - Instantiate a SafeXMLParser with no kwargs; because resolve_entities is not supplied, SafeXMLParser will set resolve_entities=False before delegating to the lxml constructor. Pass that instance into etree.fromstring or etree.parse to parse XML while avoiding entity resolution by default.

- Overriding the default (narrative):
    - If entity resolution is intentionally required, construct SafeXMLParser with resolve_entities explicitly provided (e.g., resolve_entities=True). SafeXMLParser will honor the explicit value and will not override it.

Notes:
- SafeXMLParser is intentionally small and exists to provide a secure default rather than to change parser semantics. Any additional parser options should be provided according to lxml.etree.XMLParser's API.

### `parsel.selector.SafeXMLParser.__init__` · *method*

## Summary:
Sets a secure default for XML entity resolution (resolve_entities=False) when constructing the parser instance, then delegates all initialization to the underlying lxml.etree.XMLParser constructor.

## Description:
- Known callers and lifecycle stage:
    - Any code that constructs an XML parser for use with lxml parsing APIs (for example, callers that pass parser=SafeXMLParser() to lxml.etree.fromstring or lxml.etree.parse).
    - Invoked during parser construction/initialization; this method runs when a new SafeXMLParser instance is created.
- Why this method exists separately:
    - Encapsulates and centralizes a safer default (disable entity resolution) so call sites do not need to remember to pass resolve_entities=False everywhere.
    - Keeps initialization logic minimal and focused: it only ensures a secure default and delegates all other behavior and validations to lxml.etree.XMLParser.__init__.

## Args:
- *args: Any
    - All positional arguments are forwarded unchanged to lxml.etree.XMLParser.__init__.
- **kwargs: Any
    - All keyword arguments are forwarded to lxml.etree.XMLParser.__init__ after ensuring a default for resolve_entities.
    - resolve_entities (optional): bool-like; default behavior:
        - If the caller omits the resolve_entities key, SafeXMLParser sets resolve_entities to False (kwargs.setdefault("resolve_entities", False)).
        - If the caller provides resolve_entities explicitly (including False, True, or any other value), that value is forwarded verbatim and not overwritten.

## Returns:
- None
    - The constructor does not return a value; it initializes the instance in place. Any return behavior or object state arises from the lxml.etree.XMLParser.__init__ call.

## Raises:
- Propagates any exceptions raised by lxml.etree.XMLParser.__init__:
    - TypeError, ValueError, lxml-specific initialization errors, or other exceptions raised by the parent constructor are not intercepted and will propagate to the caller.
- SafeXMLParser.__init__ itself does not raise exceptions aside from those propagated from the superclass.

## State Changes:
- Attributes READ:
    - None specific to SafeXMLParser (this method does not read any self.<attr> fields).
- Attributes WRITTEN:
    - None directly by SafeXMLParser.__init__. The call to the superclass initializer may create or modify parser internals and attributes provided by lxml.etree.XMLParser; those changes are performed by the parent constructor, not by SafeXMLParser.__init__ itself.

## Constraints:
- Preconditions:
    - There are no SafeXMLParser-enforced preconditions. Positional and keyword arguments must satisfy the expectations of lxml.etree.XMLParser.__init__; any required types or constraints are validated by the parent constructor.
    - If callers rely on disablement of entity resolution, they must omit resolve_entities from kwargs (or explicitly pass resolve_entities=False). Passing resolve_entities explicitly (including None) will be forwarded as-is.
- Postconditions:
    - After execution, the instance is initialized as if lxml.etree.XMLParser.__init__ had been called with the same positional arguments and with kwargs where resolve_entities is present and set to False if it was originally omitted.
    - If resolve_entities was supplied by the caller, its supplied value is preserved in the arguments passed to the parent constructor.

## Side Effects:
- No I/O or external service interactions are performed by this method.
- The method mutates the local kwargs mapping (via setdefault) and then delegates to the lxml parent constructor, which may allocate internal parser structures or native resources as part of initialization.
- No global state is mutated by SafeXMLParser.__init__ itself.

## `parsel.selector.CTGroupValue` · *class*

## Summary:
A small TypedDict that groups parser and CSS-translator context needed when converting/selecting HTML or XML nodes; it holds the parser class/type, a CSS translator instance, and the string name used for node-to-string serialization.

## Description:
CTGroupValue is a typing-only structure (TypedDict) that packages together the minimal contextual pieces required by code paths that translate CSS selectors to XPath and perform element serialization. Typical use-cases:
- Pass contextual options together to functions that need to know which parser to use, which CSS-to-XPath translator instance to apply, and which tostring mode to use when serializing nodes.
- Store per-group configuration when a higher-level selector/processor maintains multiple contexts (for example: separate handling for HTML vs XML).

Motivation:
This TypedDict exists as a compact, strongly-typed grouping so that callers and callee functions have a single, documented shape to exchange parser/translator/serialization settings. It defines the responsibility boundary: carry configuration/state only — it performs no runtime validation or behavior itself.

Known callers / factories:
- None are defined in this TypedDict file; this type is intended to be used wherever the repository needs a grouped parser+translator+serialization setting. (As a TypedDict it is used for static typing and code clarity.)

## State:
The CTGroupValue object contains these required keys (TypedDict defaults to total=True unless otherwise declared):

- _parser (Type[etree.XMLParser] | Type[html.HTMLParser])
  - Type: a parser class/type, not an instance (the typing indicates a Type[...] union of the two lxml parser classes).
  - Purpose: indicates which parser class should be used to parse or to guide serialization semantics.
  - Constraints: must be a parser class (or a type compatible with lxml's XMLParser/HTMLParser). There is no runtime enforcement from the TypedDict itself.

- _csstranslator (GenericTranslator | HTMLTranslator)
  - Type: an instance of either GenericTranslator or HTMLTranslator (the union indicates the translator implementation type).
  - Purpose: provides CSS-to-XPath translation logic the caller should use for selector translation.
  - Constraints: should be a ready-to-use translator instance; the TypedDict does not create or initialize this object.

- _tostring_method (str)
  - Type: string
  - Purpose: the method/mode name used by calling code to serialize nodes to strings (e.g., a value that calling code will pass through to lxml serialization helpers).
  - Constraints: valid values are determined by the calling code (e.g., values understood by the serialization helper in this codebase); the TypedDict itself does not validate contents.

Class invariants:
- All three keys (_parser, _csstranslator, _tostring_method) must be present in any CTGroupValue instance.
- Types should match the declared annotations for correct static typing; at runtime, the structure is a plain dict and no automatic type checking is performed.

## Lifecycle:
Creation:
- Instantiate as a plain dict matching the TypedDict key names. Example required fields:
  - _parser: pass the parser class (e.g., an lxml XMLParser or HTMLParser class object)
  - _csstranslator: pass an already-configured translator instance (GenericTranslator or HTMLTranslator)
  - _tostring_method: pass a string that the caller's serialization logic understands

Usage:
- The object is read-only in the sense that it only carries configuration; typical sequence:
  1. Construct CTGroupValue dict.
  2. Pass it to functions that translate CSS selectors and/or serialize nodes.
  3. Callers use _parser to know parsing/serialization semantics, _csstranslator to produce XPath, and _tostring_method when calling serialization helpers.

Destruction / cleanup:
- CTGroupValue holds references to objects but has no resources to explicitly release. There is no context-manager or close() requirement attached to the TypedDict itself. Cleanup (if any) is the responsibility of objects referenced (e.g., translator instances) if they require it.

## Method Map:
Note: CTGroupValue is a data container (TypedDict) and has no methods. The following mermaid diagram shows the typical data flow where CTGroupValue is created and consumed:

graph LR
  A[Create CTGroupValue dict] --> B[Pass to translator/selector function]
  B --> C[_csstranslator : translate CSS -> XPath]
  B --> D[_parser : influences parse/serialize behavior]
  B --> E[_tostring_method : used when serializing nodes]
  C --> F[XPath executed against parsed tree]
  F --> E

## Raises:
- The CTGroupValue TypedDict itself does not raise exceptions during creation because it is a plain dict at runtime.
- Potential runtime errors arise only from misuse of the contained values when they are consumed:
  - AttributeError/TypeError if _csstranslator lacks expected translator methods.
  - TypeError or other errors if _parser is not a parser class acceptable to the consumers.
  - ValueError/TypeError from serializer functions if _tostring_method is not a supported mode.

## Example:
A minimal example of constructing a CTGroupValue instance and passing it along (illustrative):

    from lxml import etree, html
    from csstranslator import GenericTranslator

    ctx = {
        "_parser": etree.XMLParser,                  # parser class/type
        "_csstranslator": GenericTranslator(),       # translator instance
        "_tostring_method": "xml"                    # string mode for serialization logic
    }

    # Pass `ctx` to a function that expects CTGroupValue:
    # result = process_with_context(dom_tree, ctx)
    # Inside that function:
    # - ctx["_csstranslator"] is used to translate CSS to XPath
    # - ctx["_parser"] informs parse/serialization choices
    # - ctx["_tostring_method"] is passed to the serializer

## `parsel.selector._xml_or_html` · *function*

## Summary:
Normalize a optional type string into the canonical parsing mode string "xml" or "html".

## Description:
A tiny internal helper that maps an input indicator to a canonical parsing mode string. It returns "xml" only when the input is exactly the string "xml"; for any other input (including None), it returns "html".

Known callers within the provided context:
- No explicit callers were available in the provided source snippet. Conceptually, this function is intended for internal use wherever the codebase accepts a user-supplied or upstream "type" parameter to select an output/parsing mode (for example, functions that switch behavior between XML and HTML parsing). It centralizes the normalization rule so callers do not have to repeat the conditional check.

Why this function exists (responsibility boundary):
- Encapsulates the simple policy "treat only the exact string 'xml' as XML; everything else defaults to HTML" in a single place. This prevents scattered duplicates of the conditional and makes the behavior explicit and testable.

## Args:
type (Optional[str])
    - A string indicating the desired parsing mode, or None.
    - Expected values: the literal string "xml" to request XML mode; any other value (including None) means HTML mode.
    - No default value is defined on the function signature; callers must pass a value (which may be None).

## Returns:
str
    - Returns the canonical mode string:
        - "xml" if and only if the input value is exactly the string "xml".
        - "html" for any other input value (including None, empty string, different capitalization, or any non-"xml" string).
    - There are no other possible return values.

## Raises:
- This function does not raise any exceptions in normal operation.
- If a non-string value that is not None is passed (e.g., an object), the equality comparison will be evaluated; no explicit type checking is performed, so unusual types may still be accepted but are unlikely in typical usage.

## Constraints:
Preconditions:
    - None required. The function accepts None or any object; callers are advised to pass either None or a string to align with intended usage.
Postconditions:
    - The return value is guaranteed to be either "xml" or "html".
    - If the input was exactly "xml" (string equality), the return is "xml"; otherwise the return is "html".

## Side Effects:
    - None. The function is pure: it does not perform I/O, mutate global state, or interact with external services.

## Control Flow:
flowchart TD
    Start([Start]) --> CheckType{type == "xml"?}
    CheckType -- yes --> ReturnXML["Return 'xml'"]
    CheckType -- no --> ReturnHTML["Return 'html'"]
    ReturnXML --> End([End])
    ReturnHTML --> End

## Examples:
- Input: None  → Output: "html"
- Input: "xml" → Output: "xml"
- Input: "XML" → Output: "html"   (case-sensitive check)
- Input: ""    → Output: "html"
- Input: "html"→ Output: "html"
- Input: 123   → Output: "html"   (non-string value compared for equality; not typical usage)

## `parsel.selector.create_root_node` · *function*

## Summary:
Create and return an lxml.etree root element parsed from the provided text or bytes, applying NUL-byte removal, optional huge-tree parser configuration, and emitting a versioned warning when the parser error log indicates the input requires lxml's huge-tree support.

## Description:
This function centralizes parsing of raw HTML/XML input into an lxml element tree root for downstream processing. It accepts either a unicode text string or raw bytes and produces an lxml.etree._Element using the supplied parser class.

Known callers and context:
- Callers convert HTTP responses, files, or other raw document sources into an lxml root for XPath/CSS selection and serialization.
- Typical trigger: after fetching response content, the code calls this function to create a canonical root for selectors or further DOM traversal.
- Responsibility boundary: preprocessing (strip, remove NULs), parser instantiation with recover/encoding and optional huge_tree flag, invoking lxml.etree.fromstring, and emitting a warning when parser.error_log indicates XML_PARSE_HUGE is required. The function does not perform I/O or further DOM normalization.

Why extracted:
- Shared preprocessing and parser-creation logic is reused by multiple entry points.
- Centralizes lxml-specific behavior and the exact warning message formatting.

## Args:
    text (str):
        Unicode input. If truthy, this value is trimmed, NUL characters removed, encoded using `encoding`, and used as the input bytes for the parser.
        If falsey (empty string, None, etc.), this parameter is considered absent and `body` is used instead.
    parser_cls (Type[_ParserType]):
        Parser class/type to instantiate. The instance constructed from parser_cls must be accepted by lxml.etree.fromstring as the `parser` argument.
        create_root_node calls parser_cls(...) with keyword arguments:
            - recover=True
            - encoding=encoding
        and, in one branch, also:
            - huge_tree=True
        Thus parser_cls must accept these keywords when the runtime supports huge_tree.
    base_url (Optional[str], default=None):
        Passed to lxml.etree.fromstring(..., base_url=base_url) to set the document base for resolving relative URLs.
    huge_tree (bool, default=LXML_SUPPORTS_HUGE_TREE):
        Caller-requested flag to enable the parser's huge_tree option. The function only passes huge_tree=True to parser_cls when both this argument is truthy and the module-level boolean LXML_SUPPORTS_HUGE_TREE is truthy.
        Note: LXML_SUPPORTS_HUGE_TREE is a module-level symbol (not defined within this function); its value controls whether the huge_tree keyword is used.
    body (bytes, default=b""):
        Raw bytes fallback input. Used when `text` is falsey. The function removes NUL bytes (b"\x00") and strips whitespace from `body` before parsing.
    encoding (str, default="utf8"):
        Encoding used to convert `text` to bytes via text.encode(encoding) when `text` is truthy.

Parameter interactions and edge rules:
- If `text` is truthy, the function ignores `body`.
- In the truthy-`text` branch, after strip/replace/encode, the code uses the result of encode(encoding) or b"<html/>" — i.e., if encoding returns an empty bytes object, b"<html/>" will be used instead.
- In the falsey-`text` branch, `body` is cleaned via body.replace and strip(); no explicit fallback to b"<html/>" occurs in this branch (so an empty bytes value may be passed to lxml.fromstring).

## Returns:
    lxml.etree._Element
        The parsed root element returned by lxml.etree.fromstring called with the constructed parser and base_url.

All return possibilities:
- Normal: the element returned by etree.fromstring(body, parser=parser, base_url=base_url).
- If etree.fromstring returns None (very uncommon), the function reparses b"<html/>" with the same parser and returns that element.
- If etree.fromstring raises an exception, that exception propagates to the caller (see Raises).

## Raises:
    Any exception raised by lxml.etree.fromstring (e.g., lxml.etree.XMLSyntaxError, ValueError) will propagate.
    TypeError or other exceptions may occur if parser_cls does not accept the expected keyword arguments or if `body`/`text` are of incompatible types (e.g., calling .replace on a non-bytes `body`).

## Constraints:
Preconditions:
- `text` should be a str (or at least behave like one for strip/replace/encode).
- `body` should be bytes; otherwise .replace/.strip may raise.
- parser_cls must be a callable/type that returns a parser object accepted by lxml.etree.fromstring and that accepts recover and encoding kwargs; if huge_tree is requested and supported, it must accept huge_tree keyword.
- Module-level symbols referenced by this function:
    - LXML_SUPPORTS_HUGE_TREE: a boolean indicating runtime support for parser huge_tree keyword.
    - lxml_huge_tree_version: a string (or version-like object) used in the emitted warning message.
  These must be defined in the module for consistent behavior and exact warning text.

Postconditions:
- On successful return, the result is an lxml.etree._Element (non-None unless lxml raised an exception).
- No file/network I/O performed by this function itself.

## Side Effects:
- Emits a runtime warning via warnings.warn if, in the non-huge_tree branch, any error in parser.error_log contains the substring "use XML_PARSE_HUGE option". The warning text is formatted as:
    "Input data is too big. Upgrade to lxml {lxml_huge_tree_version} or later for huge_tree support."
  where lxml_huge_tree_version is a module-level value.
- Iterates parser.error_log (reading parser state).
- No other global mutation or I/O.

## Control Flow:
flowchart TD
    Start[Start]
    IsText{text truthy?}
    Start --> IsText
    IsText -- No --> CleanBody[body = body.replace(b"\x00", b"").strip()]
    IsText -- Yes --> CleanText[text -> text.strip().replace("\x00","").encode(encoding) or b"<html/>"]
    CleanBody --> DecideHuge
    CleanText --> DecideHuge
    DecideHuge{huge_tree and LXML_SUPPORTS_HUGE_TREE?}
    DecideHuge -- True --> BuildParserHuge[parser = parser_cls(recover=True, encoding=encoding, huge_tree=True)]
    DecideHuge -- False --> BuildParser[parser = parser_cls(recover=True, encoding=encoding)]
    BuildParserHuge --> ParseCall[root = etree.fromstring(body, parser=parser, base_url=base_url)]
    BuildParser --> ParseCall
    ParseCall --> CheckErrors{Did we build parser without huge_tree?}
    CheckErrors -- Yes --> ForEachError[for error in parser.error_log: if "use XML_PARSE_HUGE option" in error.message -> warn(...)]
    CheckErrors -- No --> Continue
    ForEachError --> AfterErrorCheck
    Continue --> AfterErrorCheck
    AfterErrorCheck --> IfRootNone{root is None?}
    IfRootNone -- Yes --> Fallback[root = etree.fromstring(b"<html/>", parser=parser, base_url=base_url)]
    IfRootNone -- No --> Return[return root]
    Fallback --> Return

## Examples:
1) Parsing a normal HTML text string
    - Input: unicode HTML from an HTTP response
    - Behavior: text branch used, NULs removed, encoded, parsed.

    Example usage (conceptual):
        root = create_root_node(
            text="<html><body><p>Hello</p></body></html>",
            parser_cls=etree.HTMLParser,
            base_url="http://example.com"
        )

2) Parsing from raw bytes when text is empty
    - Input: response.content (bytes), maybe containing NULs
    - Behavior: body branch used, NULs removed, whitespace trimmed, parsed.

    Example usage (conceptual):
        root = create_root_node(text="", parser_cls=etree.HTMLParser, body=response.content)

3) Large document with requested huge_tree
    - If LXML_SUPPORTS_HUGE_TREE is True and huge_tree=True is passed, the parser is constructed with huge_tree=True.
    - If huge_tree=False (or LXML_SUPPORTS_HUGE_TREE is False), the parser is constructed without huge_tree and the parser.error_log is inspected for messages containing "use XML_PARSE_HUGE option"; a warnings.warn is issued containing lxml_huge_tree_version.

4) Error handling
    - The function does not catch parsing exceptions:
        try:
            root = create_root_node(text=input_text, parser_cls=etree.HTMLParser)
        except etree.XMLSyntaxError as e:
            # handle malformed input
            handle(e)

Implementation notes:
- Preserve the exact substring check "use XML_PARSE_HUGE option" when reproducing the warning behavior to maintain compatibility with parser error messages.
- Ensure module-level symbols LXML_SUPPORTS_HUGE_TREE and lxml_huge_tree_version are defined in the module scope when reimplementing.

## `parsel.selector.SelectorList` · *class*

## Summary:
SelectorList is a typed list wrapper for Selector-like objects that provides convenience methods (xpath, css, jmespath, re, get/getall, attrib, drop/remove) which aggregate results across all contained selectors and preserve subclassing when slicing or chaining.

## Description:
SelectorList appears where code needs to hold and operate on a collection of Selector-like objects (hereafter "selector elements"). Each selector element is expected to implement a small extraction API used by the methods below: methods named jmespath, xpath, css, re, get, attrib, remove, and drop. Typical call sites create SelectorList instances when queries (css/xpath/jmespath) return multiple nodes or elements; factory code often constructs a SelectorList from an iterable of selector elements.

This class exists to:
- Provide a uniform container that forwards and aggregates calls to underlying selector elements.
- Preserve the subclass type when slicing or when constructing new lists via chained calls (by using self.__class__ to instantiate returned lists).
- Offer convenience methods that flatten nested results and return consistent types (e.g., lists of strings or a new SelectorList).

Responsibility boundary:
- SelectorList is a thin aggregator; it does not perform parsing or node selection itself. Instead it delegates to its elements and flattens/collects their outputs. It enforces no element type at runtime beyond the expectation that elements support the small selector API.

## State:
Attributes inherited from list (public):
- Underlying list storage (list of elements).
  - Element type: generic _SelectorType (caller must ensure items implement the selector API).
  - Valid values: zero or more selector elements.
  - Invariant: every element in the list must implement the methods used by SelectorList (jmespath, xpath, css, re, get, attrib, remove, drop). Violating this will cause attribute errors at call time.

Notes on __init__ and construction:
- SelectorList does not define its own __init__; it uses list.__init__. Callers typically pass an iterable of selector elements to instantiate: SelectorList(iterable_of_selectors).
- No extra parameters or constraints are enforced at construction time; callers are responsible for providing appropriate elements.

Class invariants that should hold between calls:
- The list contents remain a sequence of selector elements.
- Methods that construct new lists (xpath, css, jmespath) return instances of the same class as self (i.e., self.__class__) so subclasses remain preserved.

## Lifecycle:
Creation:
- Instantiate with an iterable of selector elements, e.g. SelectorList([sel1, sel2]) or by slicing an existing SelectorList.
- Required args: a single iterable is typically provided to the list constructor; there are no mandatory additional parameters.

Usage (typical sequence and semantics):
- Read-only aggregate operations:
  - css(query) -> returns a SelectorList containing concatenated results of x.css(query) for each element x in the list.
  - xpath(xpath_expr, namespaces=None, **kwargs) -> returns a SelectorList built from flattening x.xpath(...) results for each element.
  - jmespath(query, **kwargs) -> returns a SelectorList from flattening x.jmespath(query, **kwargs) for each element.
  - re(regex, replace_entities=True) -> returns a List[str] containing flattened results of x.re(...) for each element.
  - re_first(regex, default=None, replace_entities=True) -> returns the first matching string found by iterating over flattened re results; returns default if none found.
  - getall() / extract() -> returns List[str] calling x.get() for each element and collecting results (returns an empty list when SelectorList is empty).
  - get(default=None) / extract_first() -> returns x.get() for the first element in the list; if list is empty, returns default.
  - attrib (property) -> returns the attrib mapping of the first element; if empty, returns an empty mapping ({}).

- Mutating/cleanup operations:
  - drop() -> calls x.drop() for each element x. This is the preferred way to remove/drop underlying nodes.
  - remove() -> deprecated: emits a DeprecationWarning advising to use drop(), then calls x.remove() for each element.

Sequencing:
- No strict ordering constraints between methods. Typical use: obtain a SelectorList from a search call, then chain non-mutating selectors (css/xpath/jmespath) to refine results, then call getall/get or re/re_first to extract strings, and finally call drop() to release or remove nodes if appropriate.
- If client code uses slice indexing, slicing returns a new SelectorList instance (or subclass) preserving subclass behavior.

Destruction:
- There are no explicit cleanup or context-manager hooks defined on SelectorList itself. If underlying selector elements require cleanup, callers should call drop() or element-specific cleanup before discarding the list.
- Pickling: SelectorList explicitly disallows pickling; attempting to pickle an instance raises TypeError (see Raises).

## Method Map:
Mermaid graph showing method dependencies and typical flows (textual mermaid syntax):

graph LR
    SL[SelectorList] --> |"calls per-element"| CSS(css)
    SL --> |"calls per-element"| XPATH(xpath)
    SL --> |"calls per-element"| JMES(jmespath)
    SL --> |"calls per-element"| RE(re)
    RE --> |"flattens"| LIST_STRS[List[string]]
    SL --> |"calls per-element"| GETALL(getall/extract)
    GETALL --> |"collects x.get()"| LIST_STRS
    SL --> |"returns first x.get() or default"| GET[get/extract_first]
    SL --> |"returns first re match or default"| RE_FIRST[re_first]
    SL --> |"access attrib of first element"| ATTRIB[attrib]
    SL --> |"calls per-element"| DROP(drop)
    SL --> |"deprecated -> warns then calls per-element"| REMOVE(remove)
    SL --> |"slice returns same class"| SL2[SelectorList (slice)]

Note: "calls per-element" indicates the method iterates elements and forwards the call; "flattens" indicates the class uses a flattening helper to collapse nested lists returned by elements.

## Detailed behavior and edge cases:
- __getitem__(pos):
  - If pos is an integer-style SupportsIndex, returns the element at that index (type _SelectorType).
  - If pos is a slice, returns a new instance of self.__class__ constructed from the sliced list. This preserves subclassing when subclassing SelectorList.
  - Indexing semantics otherwise mirror built-in list indexing (including negative indices and IndexError when out of range).

- __getstate__():
  - Always raises TypeError("can't pickle SelectorList objects"). This prevents pickling/persistence of SelectorList instances.

- jmespath(query, **kwargs):
  - For each element x in self, calls x.jmespath(query, **kwargs).
  - Uses a flatten helper to collapse nested lists returned by elements into a single list.
  - Constructs and returns a new instance of self.__class__ with the flattened result list.
  - Exceptions raised by element.jmespath or by jmespath internals propagate to the caller.

- xpath(xpath, namespaces=None, **kwargs):
  - For each element x, calls x.xpath(xpath, namespaces=namespaces, **kwargs).
  - Flattens the returned sequences and returns a new self.__class__ instance with the flattened results.
  - Exceptions from the underlying element.xpath or lxml are propagated.

- css(query):
  - For each element x, calls x.css(query).
  - Flattens results and returns a new self.__class__ instance.
  - Exceptions from element.css propagate.

- re(regex, replace_entities=True):
  - For each element x, calls x.re(regex, replace_entities=replace_entities).
  - Uses flatten to produce a List[str] with all matches across elements.
  - If regex is an invalid pattern, underlying regex compilation or matching errors propagate to the caller.

- re_first(regex, default=None, replace_entities=True):
  - Iterates over the flattened results produced by x.re(...) for each element (uses iflatten to lazily iterate).
  - Returns the first string found (as str). If none are found, returns default (which may be None or a string).
  - Behavior on empty SelectorList: returns default.
  - Note: typing overloads indicate return type depends on provided default argument (Optional[str] vs str), but runtime behavior is: returns first found value or default.

- getall() / extract():
  - Returns a List[str] by calling x.get() for each element x in the list.
  - If the list is empty, returns an empty list.

- get(default=None) / extract_first():
  - Returns x.get() called on the first element in the list.
  - If the list is empty, returns default.
  - If the first element's get() raises, that exception propagates.
  - Overloads indicate exact return type depends on default supplied.

- attrib (property):
  - Returns the attrib mapping (Mapping[str, str]) from the first element in the list.
  - If the list is empty, returns an empty dict.
  - Does not aggregate attributes from multiple elements; it is intentionally a first-element accessor.

- remove():
  - Deprecated wrapper: emits a DeprecationWarning with a message advising to use drop().
  - Calls x.remove() for each element in the list.
  - The warning uses stacklevel=2 so the warning points to the caller.
  - Underlying element.remove exceptions propagate.

- drop():
  - Preferred deletion/cleanup method; iterates elements and calls x.drop() for each.
  - Underlying exceptions propagate.

## Raises:
- TypeError from __getstate__: attempting to pickle a SelectorList raises TypeError("can't pickle SelectorList objects").
- DeprecationWarning from remove(): invoking remove() triggers a DeprecationWarning advising use of drop() instead.
- Any method that delegates to an element (jmespath, xpath, css, re, get, remove, drop) may raise exceptions that those element methods raise (e.g., IndexError, ValueError, regex errors, lxml errors). These are not caught; they propagate to callers.

## Example:
# Create a SelectorList from two selector elements (sel1, sel2 are selector-like objects)
sel_list = SelectorList([sel1, sel2])

# Chain selectors: select with css on every element and keep a SelectorList result
sub_list = sel_list.css("div.item")

# Further refine using xpath
nested = sub_list.xpath(".//a[@href]")

# Extract strings: all text values from the nested selectors
all_texts = nested.getall()        # List[str]

# Get first extracted value or a default
first_text = nested.get(default="(none)")

# Use regex extraction across all elements
matches = sel_list.re(r"\d+")

# Get first regex match or None
first_match = sel_list.re_first(r"\d+")

# Access attributes of the first element (or {} if empty)
attributes = sel_list.attrib

# Cleanup / remove underlying nodes:
sel_list.drop()

# Deprecated removal path (emits DeprecationWarning)
sel_list.remove()

### `parsel.selector.SelectorList.__getitem__` · *method*

## Summary:
Return an element for an index or a new SelectorList (same concrete subclass) for a slice — indexing yields the stored selector object, slicing yields a shallow-copied sequence wrapped in the same SelectorList subclass.

## Description:
This override implements sequence element access for SelectorList by delegating to the superclass __getitem__ and adapting the result so slices produce a SelectorList (self.__class__) rather than a plain list. Known callers and context:
- Client code that accesses parsed selector groups via indexing or slicing (e.g., within scraping code that selects a particular element or a sub-range).
- Any internal code that treats SelectorList as a sequence and relies on normal sequence semantics (indexing, negative indices, slicing with step).

Rationale for being a separate method:
- It preserves standard sequence behaviors (including handling of SupportsIndex-compatible objects and slice semantics) by delegating to the superclass implementation.
- It ensures that slices return the same concrete SelectorList subclass so returned slices retain SelectorList instance methods and behavior rather than becoming plain Python lists.

## Args:
    pos (Union[SupportsIndex, slice]):
        - If pos is an integer or a SupportsIndex-compatible object (e.g., objects implementing __index__), it selects a single element. Supports negative indices per normal Python semantics.
        - If pos is a slice object, it defines start:stop:step semantics; step may be None or any integer; a slice with start/stop that select no items returns an empty instance of self.__class__.
        - Any other type will cause the underlying sequence implementation to raise TypeError.

## Returns:
    Union[_SelectorType, SelectorList[_SelectorType]]:
        - For index access: the exact object stored at that position (no copying of the element).
        - For slice access: a new instance of the same class as self (self.__class__) constructed from the sliced items (shallow copy of references to the original elements).
        - Edge cases:
            * Out-of-range integer indices raise IndexError (propagated from the superclass).
            * Slice selecting no elements returns an empty instance of self.__class__.
            * Slices with step produce the same semantics as Python lists (including negative steps).

## Raises:
    TypeError:
        - If pos is neither an integer/SupportsIndex-compatible object nor a slice; this is raised by the superclass sequence implementation when given an unsupported index type (e.g., a non-indexable custom object).
    IndexError:
        - If pos is an integer index and is out of range; raised by the superclass implementation.

## Implementation notes (important for reimplementation):
    - The method calls o = super().__getitem__(pos). At runtime, o will be either a single element (for index access) or a sequence (typically a list) for slices.
    - When pos is a slice, the code constructs self.__class__(o) to wrap the sliced iterable in the same SelectorList subclass. This requires that the SelectorList constructor accept an iterable of elements (standard behavior for list-like wrappers).
    - typing.cast is used only to inform static type checkers of the intended return type; it does not affect runtime behavior.

## State Changes:
    Attributes READ:
        - Reads self.__class__ (to obtain the concrete class for construction).
        - Indirectly reads the underlying storage via the superclass __getitem__ (no explicit self.<attr> is accessed in the source).
    Attributes WRITTEN:
        - None. The method does not mutate self or its elements.

## Constraints:
    Preconditions:
        - self must be a sequence-like object whose superclass implements __getitem__ with normal list/sequence semantics.
        - The concrete class self.__class__ must accept the iterable returned by slicing (i.e., its constructor should accept an iterable of elements).
    Postconditions:
        - Index access returns a direct reference to the stored element.
        - Slice access returns a new instance of the same concrete class containing the selected elements (shallow copy semantics).
        - The original SelectorList remains unmodified.

## Side Effects:
    - No file/network I/O or external service calls.
    - No mutation of self or elements.
    - A new SelectorList subclass instance is allocated and returned when slicing.

## Examples:
    - Access element: retrieving element at position 0 returns the stored selector object (or raises IndexError if empty).
    - Slice: selecting s[1:4] returns an instance of the same SelectorList subclass containing elements from index 1 up to but not including 4; selecting s[10:20] on a shorter list returns an empty SelectorList instance.

### `parsel.selector.SelectorList.__getstate__` · *method*

## Summary:
Prevents serialization by raising a TypeError when a pickling mechanism attempts to obtain the object's state.

## Description:
This method is invoked by Python's object serialization (pickling) machinery when it tries to obtain an object's state (for example, the pickle module calling __getstate__ during pickling). Common callers include pickle.dumps, pickle.dump, and other frameworks that rely on the pickling protocol (e.g., multiprocessing when transferring objects between processes, some cache/serialization libraries, or cloudpickle). The method exists to deliberately disable pickling of SelectorList instances because the internals (for example, lxml element trees or parser state) are not safe or meaningful to serialize.

Implementing this as a dedicated __getstate__ method ensures a single, explicit failure point that:
- Provides a clear, consistent exception message when pickling is attempted.
- Avoids attempting to serialize potentially non-picklable internal attributes.
- Makes the intent explicit for maintainers and tooling rather than relying on incidental failures during pickling.

## Args:
None.

## Returns:
None. This method never successfully returns; it always raises a TypeError to abort serialization.

## Raises:
TypeError: Unconditionally raised with the exact message "can't pickle SelectorList objects". This is the precise condition used to stop pickling; no other exceptions are raised by this method.

## State Changes:
Attributes READ:
    - None. The method does not inspect or access any self attributes.

Attributes WRITTEN:
    - None. The method does not modify self or any of its attributes.

## Constraints:
Preconditions:
    - None. The method does not require any particular state of the object to be true before being called.

Postconditions:
    - The pickling operation is aborted by raising TypeError.
    - The SelectorList instance remains unchanged (no attributes are read or written).

## Side Effects:
    - No I/O, no calls to external services, and no mutation of objects outside self.
    - The only observable effect is the raised TypeError which signals to the caller that this object cannot be serialized.

## Rationale and Usage Notes:
    - This defensive failure is intentional: SelectorList commonly wraps parser nodes and context that cannot be meaningfully or safely serialized across process boundaries or persisted.
    - If callers need to serialize data derived from a SelectorList, they should extract the primitive data (strings, dicts, lists of primitives) and serialize those instead of trying to pickle the SelectorList itself.
    - If a different serialization strategy is required, provide an alternative API that returns serializable representations (e.g., to_json, to_dict) rather than changing this method to support pickling.

### `parsel.selector.SelectorList.jmespath` · *method*

## Summary:
Applies a JMESPath query to every Selector in the list, flattens the per-selector results, and returns a new SelectorList (of the same SelectorList subclass) containing the aggregated selectors.

## Description:
This method iterates over every element in the SelectorList, calls that element's jmespath(...) method with the same arguments, flattens all returned iterables into a single list, and returns a new instance of the SelectorList subclass wrapping those results.

Known callers / usage context:
- There are no specific internal callers required by the implementation; this method is intended to be invoked by client code or by higher-level chaining helpers after obtaining a SelectorList (for example, after .xpath or .css calls).
- Typical pipeline stage: used when a developer has multiple Selector objects (e.g., a list of JSON/HTML fragments) and wants to run the same JMESPath query on each and combine the results into one list of selectors.

Why this is a separate method:
- It provides a convenience, vectorized operation over a collection of selectors: forwarding the call to each contained Selector, flattening nested lists, and preserving the concrete SelectorList subclass used by the caller. This centralizes the "apply-and-flatten" behavior rather than requiring callers to manually loop, call, and merge results.

## Args:
    query (str): The JMESPath query string to evaluate. Passed through unchanged to each contained Selector.jmespath call.
    **kwargs (Any): Additional keyword arguments forwarded directly to each Selector.jmespath(...) call and ultimately to jmespath.search. The method makes no assumptions about these kwargs.

## Returns:
    SelectorList[_SelectorType]: A new SelectorList (constructed via self.__class__) containing the flattened aggregation of all Selector.jmespath(...) results from the elements of this list.
    - If no selectors are present or no element produces results, an empty SelectorList instance is returned.
    - Individual element results are flattened using the module-level flatten utility; if an element returns a non-list result, the underlying Selector.jmespath implementation wraps single results into a list before flattening.

## Raises:
    - This method does not raise new exceptions itself. Any exception raised by:
        * an individual element's Selector.jmespath(...) call (for example, errors originating from JSON loading or the jmespath library), or
        * the flatten utility (if given invalid iterables)
      will propagate to the caller unchanged.

## State Changes:
    Attributes READ:
        - Iterates the list contents (reads each contained Selector by iteration).
        - Uses self.__class__ to construct the returned SelectorList instance.
    Attributes WRITTEN:
        - None. The method does not modify self or the contained Selector objects; it returns a new SelectorList.

## Constraints:
    Preconditions:
        - Each element in self must implement a jmespath(query: str, **kwargs) method that returns an iterable (commonly a SelectorList or list) of selectors.
        - query should be a str (the method signature declares str); passing non-str values relies on callers and the underlying Selector.jmespath implementation to handle type errors.
    Postconditions:
        - The returned object is an instance of the same concrete SelectorList subclass as self (constructed via self.__class__) and contains the flattened results produced by calling jmespath on every element.
        - self remains unchanged.

## Side Effects:
    - No I/O, no network calls, and no global state mutation are performed by this method itself.
    - Side effects (if any) can occur only because of side effects in the contained Selector.jmespath implementations or in any functions they call (e.g., JSON parsing libraries); such side effects are not introduced by this method.

### `parsel.selector.SelectorList.xpath` · *method*

## Summary:
Apply an XPath expression to every Selector in the list and return a new SelectorList containing the flattened results; does not mutate the original list.

## Description:
This method iterates over each element in the SelectorList (each element is expected to be a Selector-like object), calls that element's xpath(...) method with the same xpath expression plus any provided namespaces and additional keyword arguments, flattens the sequence of results into a single list of selectors, and constructs a new SelectorList (the same class as self) from that flattened list.

Known callers / usage contexts:
- Called directly by user code when a pipeline needs to apply the same XPath expression to multiple nodes at once.
- Used in multi-step selection pipelines after obtaining a SelectorList from previous selection methods (for example, chaining from SelectorList.css, SelectorList.jmespath, or user-created lists of selectors).
Lifecycle stage:
- Invoked during content-parsing/selection steps, after one or more selectors have been produced and further narrowing or traversal is required.

Why this is a separate method:
- It encapsulates the common pattern "apply xpath to each selector and flatten results" so callers don't need to manually loop, manage nested lists, or rewrap results into the correct SelectorList subclass. It preserves typing/constructor behavior (uses self.__class__) so subclasses of SelectorList behave consistently.

## Args:
    xpath (str): The XPath expression to evaluate against each selector's root.
    namespaces (Optional[Mapping[str, str]]): Optional mapping of namespace prefixes to URIs that will be merged with each selector's own namespaces before evaluating the XPath.
    **kwargs (Any): Arbitrary keyword arguments that are forwarded to each element's xpath(...) method. These typically become parameters passed into the underlying library (for example, lxml's .xpath), so acceptable keys/values depend on that implementation.

## Returns:
    SelectorList[_SelectorType]: A new instance of the same SelectorList class (self.__class__) whose items are the flattened results of calling xpath on each element in the original list. If there are no results, an empty SelectorList (constructed via self.__class__([])) is returned.

    Possible edge-case return values:
    - Empty SelectorList when self is empty or all element-level xpath calls return no results.
    - A SelectorList containing the selectors produced by underlying element.xpath calls in document order after flattening.

## Raises:
    - Propagates ValueError raised by an underlying element.xpath when the selector's type doesn't support XPath (e.g., "Cannot use xpath on a Selector of type 'json'") or when the underlying XPath evaluation fails and Selector.xpath raises a ValueError wrapping the lxml.XPathError.
    - Any exception raised by an individual element's xpath(...) call (TypeError, AttributeError, etc.) will propagate; for example, if an element does not implement xpath, an AttributeError/TypeError may occur.
    - Any exception raised by flatten (or the iteration) will propagate upward.

## State Changes:
Attributes READ:
    - The method iterates self to read its contained elements (no specific self.<attr> fields are modified).
Attributes WRITTEN:
    - None. The method does not modify self or any attribute on the existing selectors; it constructs and returns a new SelectorList.

## Constraints:
Preconditions:
    - Each element in self must be a Selector-like object that implements an xpath(xpath: str, namespaces: Optional[Mapping[str,str]] = None, **kwargs) -> SelectorList[...] method.
    - xpath must be a string.
    - If namespaces is provided, it must be a mapping from str to str (prefix -> URI). The method will merge this mapping with each element's own namespaces before evaluation (the merge is performed by the element.xpath implementation).
Postconditions:
    - The original SelectorList (self) remains unchanged.
    - The returned object is an instance of self.__class__ and contains all selector results produced by element.xpath calls, flattened to a single list.

## Algorithm / Implementation Notes (enough to reimplement):
1. For each element x in the list self, call x.xpath(xpath, namespaces=namespaces, **kwargs).
2. Collect the results from each call into an outer list (these results are typically iterator/list-like sequences of selectors).
3. Flatten the outer list by one level to produce a single list of selector results (use a helper like iflatten/flatten that iterates over each sub-result and yields items).
4. Construct a new SelectorList instance using self.__class__(flattened_list) and return it.

## Side Effects:
    - No I/O or external network calls are performed by this method itself.
    - It will allocate new selector objects / lists as returned by underlying element.xpath and by constructing the new SelectorList.
    - It does not mutate selectors contained in self, nor does it modify self itself.

### `parsel.selector.SelectorList.css` · *method*

## Summary:
Apply a CSS selector string to every Selector in this list and return a new SelectorList (same class) containing the flattened concatenation of all per-item results. The original SelectorList is not modified.

## Description:
For each element x in the SelectorList (typically instances of Selector or a compatible subclass), this method calls x.css(query), collects the results (each is a SelectorList), flattens those results into a single Python list, and constructs a new SelectorList instance of the same class as self from that flattened list.

Why separate method:
- Implements the common list-level operation "map css over elements and concatenate results" in one place so callers can chain selectors fluently without reimplementing iteration and flattening.
- Keeps per-node CSS selection behavior inside Selector.css while providing a convenience wrapper for multi-node selections.

Known call contexts:
- Chained selector usage in user code or libraries that consume Selector/SelectorList objects (for example: some_selector_list.css('a').css('span')).
- Any code that receives a SelectorList and needs to apply an additional CSS filter across all contained selectors.

## Args:
    query (str): A CSS selector expression. Must be a Python str. Validation and interpretation of the selector string are performed by the underlying Selector.css → Selector._css2xpath → csstranslator logic.

## Returns:
    SelectorList[_SelectorType]: A new instance of self.__class__ containing the flattened results of x.css(query) for every x in self.
    - If self is empty, returns an empty SelectorList of the same class.
    - If none of the contained selectors yield matches, returns an empty SelectorList.
    - The ordering of elements in the returned SelectorList preserves the order produced by iterating self and, for each x, the order of elements returned by x.css(query).

## Raises:
    This method does not raise new exceptions itself but will propagate exceptions raised by per-item calls and downstream conversions:
    - ValueError: propagated when a contained Selector rejects CSS usage because its type is not suitable (Selector.css raises ValueError if Selector.type not in ("html", "xml", "text")).
    - ValueError (XPath error): may be propagated if the CSS→XPath conversion or the subsequent XPath evaluation fails with an XPathError that is converted to ValueError in Selector.xpath.
    - Any other exceptions raised by contained Selector.css calls (TypeError, runtime errors from the translator, etc.) are propagated to the caller.

## State Changes:
    Attributes READ:
        - self (iteration over contained elements)
        - self.__class__ (used to construct the returned SelectorList instance)
    Attributes WRITTEN:
        - None. The method does not mutate self or its contained Selector objects.

## Constraints:
    Preconditions:
        - query must be a str.
        - Each element in self must implement a css(query: str) method that returns a SelectorList (or list-like collection) of selector-like objects.
    Postconditions:
        - self remains unchanged.
        - The returned object is an instance of self.__class__ and contains zero or more selector objects produced by the per-item css calls.

## Side Effects:
    - No file, network, or other external I/O is performed by this method directly.
    - Calling this method triggers per-item css(query) calls; those calls perform CSS→XPath translation and XPath evaluation which operate on the selectors' internal DOM/root structures and may have side effects internal to those operations (but none are performed by this wrapper).
    - Exceptions from per-item css calls or their downstream operations propagate to the caller.

## Implementation notes (for reimplementation):
    - Iterate over self (which is a list subclass).
    - For each element x, call x.css(query) and collect results.
    - Flatten the sequence of per-element results into a single list (the repository uses a flatten helper that converts an iterable of iterables into a list).
    - Construct and return a new instance of the same SelectorList class using self.__class__(flattened_list).

## Example usage:
    - Given a SelectorList of HTML element selectors, sel_list.css('a.external') returns a new SelectorList of all matching <a class="external"> nodes found under each element in sel_list.

### `parsel.selector.SelectorList.re` · *method*

## Summary:
Run a regular-expression extraction across every Selector in this SelectorList and return a single flattened list of all matched strings; does not modify the SelectorList.

## Description:
- What it does and when it's used:
  - Invokes each contained Selector's re(...) method with the provided pattern and returns one combined flat list of all matches.
  - Typical callers:
    - SelectorList.re_first uses this method to obtain the first match across the list.
    - Calling code (user code) that wants to apply the same regular-expression extraction to multiple selectors and receive one consolidated result.
  - Lifecycle / pipeline stage:
    - Used after selecting nodes (for example after xpath(...) or css(...) calls) when you want to extract text snippets matching a regex from every matched node.
- Why this is a separate method:
  - Encapsulates the common pattern "apply regex to each selector and flatten results" so client code does not need to iterate, call each Selector.re, and merge results manually.
  - Keeps behavior consistent with other SelectorList convenience methods (xpath, css, jmespath) which also delegate to element-level operations and flatten results.

## Args:
    regex (Union[str, Pattern[str]]):
        A regular-expression pattern to search for. Can be either a string (will be compiled) or a precompiled Pattern[str].
        - If a string is supplied it is compiled with the default flags used by extract_regex (which uses re.compile with re.UNICODE).
    replace_entities (bool): Defaults to True.
        If True, HTML/XML character/entity references in the extracted strings are replaced according to extract_regex's logic (w3lib_replace_entities is applied while keeping "lt" and "amp").
        If False, extracted strings are returned as-is without entity replacement.

## Returns:
    List[str]: A flat list of all strings extracted from every Selector in this SelectorList.
    - If no matches are found across all selectors, returns an empty list [].
    - The result is fully flattened: nested lists produced by individual Selector.re calls are merged into a single-level list.

## Raises:
    re.error:
        Raised if `regex` is a string that cannot be compiled as a valid regular expression (propagated from extract_regex's call to re.compile).
    TypeError:
        May be raised if an underlying Selector returns a value that is not usable by the regex routines (e.g., a non-string that causes regex operations to fail). In normal usage Selector.get(), called by Selector.re, returns string representations, so this is uncommon.

## State Changes:
Attributes READ:
    - Iterates over the list contents (self) and calls each element's re method, which in turn calls Selector.get() to obtain the textual data. No named self.<attr> fields are modified.
Attributes WRITTEN:
    - None. The SelectorList object and its contained Selector objects are not mutated by this method.

## Constraints:
Preconditions:
    - Every element in the SelectorList should implement a .re(regex, replace_entities=...) method (in practice these are Selector instances).
    - The regex argument must be a valid regular expression string or a compiled Pattern[str].
Postconditions:
    - After the call, the SelectorList is unchanged.
    - The returned value is a single-level list of strings containing all matches (possibly empty).

## Side Effects:
    - No I/O, no network calls, no mutation of external state.
    - Indirectly triggers computation on each contained Selector (e.g., converting its root to string via Selector.get()) and applies any entity replacement as requested.

### `parsel.selector.SelectorList.re_first` · *method*

## Summary:
Return the first regex match (as a string) found across the selectors in this list, or the provided default if no match exists.

## Description:
This is a convenience accessor used after selecting one or more nodes: it iterates the SelectorList in order, calls each element's re(...) to obtain regex matches, flattens those match lists, and returns the first match encountered. Typical usage is in scraping pipelines where you want a single example match from a collection of selected nodes (for example, extracting the first matched group from the first matched element).

Known callers / usage contexts:
- User code in scraping/parsing pipelines that operate on a SelectorList and need a single regex result (e.g., extract_first-style use).
- Any code that previously called Selector.re(...) and only needs the first returned string across possibly many selectors.
This logic is factored into its own method as a small, common convenience: it expresses the common pattern "call re on each selector, flatten results, take first or fallback to default", avoiding repeated inline loops across call-sites.

## Args:
    regex (Union[str, Pattern[str]]):
        A regular expression to apply. May be a pattern string or a compiled Pattern[str].
    default (Optional[str], optional):
        Value to return if no regex matches are found across the list. Defaults to None.
        Note: type overloads exist in the module so callers supplying a non-None default can expect a guaranteed str return.
    replace_entities (bool, optional):
        If True (default), HTML/XML entities in the input text may be replaced before applying the regex (delegated to Selector.re / extract_regex behavior).

## Returns:
    Optional[str]:
        The first matching string from the flattened sequence of matches returned by calling re(...) on each element of self, preserving the iteration order of the SelectorList and the order of matches within each element.
        - If at least one match exists, returns that match as str.
        - If no matches are found, returns the provided default (which may be None).
        - If the first match is the empty string, an empty string is returned (i.e., empty-string matches are valid results).

## Raises:
    This method does not raise exceptions itself. It may propagate exceptions raised by:
    - The underlying regex engine (e.g., invalid pattern errors) or
    - Selector.re / extract_regex or other code invoked while computing matches.
    These propagated exceptions reflect errors in the provided regex or in the Selector objects' data/state.

## State Changes:
    Attributes READ:
        - None of the SelectorList's own attributes are directly accessed by attribute name.
        - Conceptually, the method iterates the list contents (reads the sequence of contained Selector objects).
    Attributes WRITTEN:
        - None. The SelectorList and its Selector elements are not modified by this call.

## Constraints:
    Preconditions:
        - self must be an iterable/sequence of objects implementing a re(regex, replace_entities) -> List[str] interface (in this codebase, Selector instances).
        - regex must be a string or compiled Pattern[str].
        - replace_entities must be a boolean.
    Postconditions:
        - After the call completes, either:
            * A string (the first match) has been returned, or
            * The supplied default value has been returned (if no matches were produced).
        - No mutation to self or its elements is performed by this method.

## Side Effects:
    - No I/O or external service calls are performed.
    - The method delegates to Selector.re for each element it inspects; any side effects of Selector.re (typically none beyond reading node text/serializing) will occur and any exceptions from those calls will propagate.
    - No mutation of objects outside self is performed by this method.

### `parsel.selector.SelectorList.getall` · *method*

## Summary:
Return a list containing the result of calling get() on each Selector in the list; does not modify the SelectorList.

## Description:
- Known callers and typical context:
    - Client code that has selected multiple nodes and wants their serialized text/html/json/text values, e.g., after xpath/css/jmespath selection: selector.xpath(...).getall() or selector.css(...).getall().
    - Code using the extract alias (SelectorList.extract) to gather results from all contained Selector objects in a scraping pipeline step that transforms selected nodes into strings/values.
    - Any internal or external code that needs to map Selector.get() across a sequence of selectors.

- Lifecycle / pipeline stage:
    - Invoked after selectors have been produced (e.g., the result of xpath(), css(), or jmespath() calls) to collect the values of those selectors as a plain Python list.

- Rationale for being a separate method:
    - Provides a convenient, explicit operation for converting a SelectorList into a list of extracted values without requiring callers to manually iterate and call get() on each element.
    - Centralizes the mapping behavior so other code can rely on consistent semantics (empty list for no elements, shallow iteration, and no mutation of the list).

## Args:
    None

## Returns:
    List[str]:
        - A list whose i-th element is the value returned by calling get() on the i-th element of this SelectorList.
        - If the SelectorList is empty, returns an empty list.
        - Per the method annotation, the returned list is typed as List[str]; in practice each element is typically a string returned by Selector.get(). If contained Selector objects are constructed with non-string roots (for example, some json-derived selectors), the returned list will contain those values as returned by their get() implementation.

## Raises:
    - This method does not explicitly raise exceptions.
    - However, exceptions raised while iterating or inside Selector.get() will propagate:
        * AttributeError if an element in the list does not implement a get() method.
        * Any exception raised by Selector.get() (propagated as-is) — for example, unexpected errors when serializing node content, or user-supplied faulty Selector instances.

## State Changes:
    Attributes READ:
        - Iterates over self (reads the sequence of elements).
        - Calls each element's get() method (reads element state within get()).
    Attributes WRITTEN:
        - None. The method does not modify self or its elements.

## Constraints:
    Preconditions:
        - self must be iterable (SelectorList inherits list semantics).
        - Each element in self is expected to be a Selector-like object exposing a get() method.
    Postconditions:
        - The returned list has the same number of items as the number of elements iterated.
        - The original SelectorList and its elements remain unmodified.

## Side Effects:
    - No I/O, network, or external service calls.
    - No mutation of objects outside this method (other than any side effects caused by element.get(), which are not introduced by getall itself).
    - Allocates and returns a new Python list containing the results of element.get() calls.

### `parsel.selector.SelectorList.get` · *method*

## Summary:
Return the result of calling get() on the first Selector in the list, or return the provided default if the list is empty.

## Description:
Typical usage contexts:
- This method is the common convenience used after query methods that produce a SelectorList (for example, Selector.xpath, Selector.css, and Selector.jmespath return SelectorList instances). Callers typically use this to fetch the first match's serialized value without manual indexing.
- Within this class, extract_first is an alias for this method (extract_first = get), so users may call either name.

Why this is a separate method:
- Consolidates the "first match" pattern (index + get + empty-check) into a single call for readability and convenience.
- Keeps client code succinct and reduces repeated boilerplate across code that consumes SelectorList results.

## Args:
    default (Optional[str]): Value returned when the SelectorList is empty. The signature annotates Optional[str]; at runtime any object passed as default will be returned unchanged when the list is empty.

## Returns:
    Any: 
    - If the SelectorList contains at least one element, returns the value produced by calling get() on the first element.
      * For Selectors of type "html"/"xml" this is typically a string containing the serialized element or element contents.
      * For Selectors of type "text"/"json" Selector.get() returns the root value (which may be non-string, e.g., a Python dict/list when parsing JSON).
    - If the list is empty, returns the provided default (which may be None).
    Edge cases:
    - If the first element's get() returns None or any other falsy value, that value is returned (the default is only used when the list is empty).
    - The exact runtime type of the return value depends entirely on the underlying Selector.get() implementation for the first element.

## Raises:
    - This method does not raise any new exceptions itself.
    - It will propagate exceptions raised by iteration or by the contained Selector.get() call (for example, any runtime error that occurs while retrieving or serializing the underlying node).

## State Changes:
Attributes READ:
    - Iterates over self to access the first element (reads the list contents and calls the first element's get()).
Attributes WRITTEN:
    - None. The method does not modify self or contained Selector objects.

## Constraints:
Preconditions:
    - self should be a SelectorList whose elements expose a no-argument get() method.
    - Callers should not rely on coercion: the method will not convert the returned value to str unless Selector.get() does so.

Postconditions:
    - No modification to self or its elements is performed.
    - The return value is either the first element's get() result (if present) or the provided default.

## Side Effects:
    - The method itself performs no I/O or external calls.
    - Any side effects are those produced by the first element's get() or by a custom iterator implementation on self; those side effects (if any) are not introduced by SelectorList.get() itself.

## Usage example:
- After performing a query: sel.xpath('//a').get(default='') returns the first matching <a> node as a string (or '' if there are no matches).

### `parsel.selector.SelectorList.attrib` · *method*

## Summary:
Returns the attribute mapping of the first element in this SelectorList, or an empty mapping if the list is empty. Does not modify the SelectorList.

## Description:
This is a convenience accessor that inspects the items produced by iterating over the SelectorList and returns the .attrib mapping from the first item encountered. If the SelectorList contains no items it returns an empty mapping.

Known callers and lifecycle:
- No callers are present in the provided source snippet. This method is intended to be called after selectors have been populated (for example, after performing a selection/query that yields one or more element-like objects) to quickly access attributes of the first matched element.

Why this is a separate method:
- The logic is a small but common convenience (return attributes of the first match) that is clearer and more discoverable when exposed as a named method rather than inlined everywhere the pattern is needed.

## Args:
    None

## Returns:
    Mapping[str, str]: The attribute mapping of the first element in the SelectorList.
    - If the list is non-empty: returns the .attrib value of the first element returned by iter(self).
    - If the list is empty: returns an empty dict ({}).
    - Note: the returned mapping is the exact object returned from the element's .attrib attribute (i.e., it is returned as-is, not deep-copied).

## Raises:
    - No explicit exceptions are raised by this method.
    - Any exceptions raised by the iteration protocol (e.g., TypeError if self is not iterable) or by attribute access on the first element will propagate to the caller.

## State Changes:
    Attributes READ:
    - Uses the object's iteration protocol (self.__iter__) to obtain elements; no named self.<attribute> fields are directly accessed within the method.

    Attributes WRITTEN:
    - None. The method does not mutate self or its elements.

## Constraints:
    Preconditions:
    - self must be iterable (support __iter__) and, if non-empty, its first element must expose an .attrib attribute that is a mapping of string keys to string values.
    - The type annotation indicates Mapping[str, str] is expected from the returned value when an element is present.

    Postconditions:
    - After the call:
        * If the SelectorList had at least one element, the method returns that element's .attrib mapping.
        * If the SelectorList had no elements, the method returns an empty dict.
        * The SelectorList itself remains unchanged.

## Side Effects:
    - No I/O or external service calls.
    - No mutations of objects outside self are performed by this method. The returned mapping is the original .attrib mapping from the element; mutating that mapping (by the caller) may affect the referenced element depending on the element implementation.

### `parsel.selector.SelectorList.remove` · *method*

## Summary:
Issues a DeprecationWarning and calls remove() on every element contained in this SelectorList, leaving the list itself unchanged.

## Description:
This method provides a backward-compatible wrapper that invokes each element's remove() method. On call it emits a DeprecationWarning advising callers to use the SelectorList.drop method instead, then iterates over the SelectorList and calls remove() on every element.

Known callers and context:
- No specific internal callers are present in this method's body. This is a public convenience/deprecated API intended for external consumers of SelectorList who previously used .remove() on the list; callers are typically part of user code or higher-level scraping pipelines that want to remove nodes represented by each Selector in the list.
- Typical lifecycle: invoked when a caller intends to remove the underlying nodes/elements represented by the selectors in the list. Because it delegates to each element's remove, it is used in the node-cleanup or DOM-manipulation step of a scraping/parsing pipeline.

Why this logic is a separate method:
- It exists as a small, explicit wrapper to preserve the old SelectorList.remove API while directing users to the newer SelectorList.drop method. Keeping this wrapper centralizes the deprecation warning and per-element delegation in one place (rather than requiring callers to iterate manually), maintaining backward compatibility and producing a consistent deprecation message.

## Args:
    None

## Returns:
    None

## Raises:
    - Any exception raised by iterating over self (for example, if self is not iterable) will propagate.
    - Any exception raised by an individual element's remove() method will propagate unchanged to the caller. (For example, AttributeError if an element does not implement remove(), or any removal-specific exception raised by the element.)

## State Changes:
    Attributes READ:
        - None (the method uses the iterable protocol on self but does not access any named self.<attr> attributes)
    Attributes WRITTEN:
        - None (the SelectorList instance's attributes are not modified by this method)

## Constraints:
    Preconditions:
        - self must be iterable (support iteration).
        - Each item yielded from iteration over self must provide a callable remove() method; otherwise an AttributeError will be raised.
    Postconditions:
        - For each element yielded from self at the time of iteration, that element's remove() has been called (unless iteration or a prior element's remove() raised an exception, which will abort further iteration).
        - The SelectorList instance itself is not modified by this method.

## Side Effects:
    - Emits a DeprecationWarning via warnings.warn with a message advising to use SelectorList.drop, using stacklevel=2.
    - Calls remove() on each contained element; these calls may mutate external objects (for example, remove nodes from a parsed tree), perform I/O, or trigger further side effects depending on the element implementation.

### `parsel.selector.SelectorList.drop` · *method*

## Summary:
Remove each Selector in the list from its underlying document tree by delegating to each element's drop operation; this mutates the external DOM/tree but does not modify the SelectorList object itself.

## Description:
- Known callers and context:
    - This is a batch convenience method intended for client code (scraping pipelines or user scripts) that want to remove multiple selected nodes from the parsed document in one call. The codebase provides Selector.drop for single-element removal; SelectorList.drop simply calls that method for every element in the list.
    - The SelectorList.remove method exists for backward compatibility and deprecates removal in favor of drop; callers using remove are encouraged to switch to drop.
- Rationale for being a separate method:
    - Encapsulates the common operation "remove all selected nodes" so callers do not need to write an explicit loop.
    - Keeps per-element removal logic (including error handling and type-specific removal) centralized in Selector.drop; SelectorList.drop remains a thin delegator to preserve single-responsibility and avoid duplicating removal logic.

## Args:
    None

## Returns:
    None

## Raises:
    - Propagates exceptions raised by the underlying Selector.drop for the first element that fails. In particular:
        - CannotRemoveElementWithoutRoot: raised when an element has no root (e.g., a pseudo-element or text node) and therefore cannot be dropped.
        - CannotDropElementWithoutParent: raised when a node has no parent and cannot be dropped (for example, attempting to drop a root element in HTML mode).
        - ValueError: can be raised by Selector.drop for XML nodes when a required parent is missing.
    - If the list contains non-Selector items, AttributeError (or similar) may arise when trying to call drop() on such an item.

## State Changes:
- Attributes READ:
    - Iterates over the list content (reads the sequence of elements stored in self). No named self.<attr> fields of SelectorList are accessed or modified.
- Attributes WRITTEN:
    - None on the SelectorList instance itself.
    - Indirect (external) mutations occur via each Selector.drop call: the underlying element trees (Selector.root and their parent trees) are modified/removed.

## Constraints:
- Preconditions:
    - Each element in the SelectorList should be a Selector (or an object providing a compatible drop() method).
    - Selectors must refer to nodes that are part of an lxml/html tree or otherwise be removable according to Selector.drop's expectations.
- Postconditions:
    - For every element whose drop() call succeeds: the corresponding node will be removed from its parent in the underlying document tree (for XML via parent.remove(self.root); for HTML via HtmlElement.drop_tree()).
    - The SelectorList instance remains unchanged (same length and membership) after the call, even though the underlying documents have been mutated.
    - The operation is not atomic: if a drop() call raises, elements processed earlier in the iteration may already have been removed; subsequent elements are not processed.

## Side Effects:
    - Mutates external document trees (lxml/HTML trees) by removing nodes. This can change later query results on the same tree.
    - No I/O or external service calls are performed.
    - If a drop() call raises an exception, that exception propagates to the caller; there is no internal retry or rollback behavior.

## Implementation notes (for reimplementation):
    - Implement exactly as a simple iteration: for each element in self, call element.drop().
    - Do not catch exceptions; let the first failure propagate.
    - Preserve iteration order (left-to-right) so behavior is predictable relative to list ordering.
    - Ensure the method works on empty lists (no-op).

## `parsel.selector._get_root_from_text` · *function*

## Summary:
Delegates parsing of a unicode text payload into an lxml.etree._Element by selecting a parser class from the module-level parser mapping and forwarding parsing options to the centralized parsing helper.

## Description:
_get_root_from_text is a thin adapter that looks up a parser class from the module-level mapping keyed by the provided type string and calls the shared create_root_node(...) helper to produce an lxml root element. This isolates parser selection (via the mapping) from the parsing and preprocessing logic implemented in create_root_node.

Known callers and context:
- No explicit callers are discovered in the provided context. Conceptually, this function is intended for internal use by higher-level selector utilities that need to convert raw document text into an lxml root. Typical callers will:
    - have a unicode/text payload to parse
    - select one of the module-level parser configurations (a key in _ctgroup)
    - call this helper to obtain an lxml root suitable for XPath/CSS operations

Why this logic is extracted:
- The function enforces a clear responsibility boundary: map a string "type" to a parser and delegate all parsing, preprocessing, huge-tree handling and warning emission to create_root_node. This keeps parser-selection logic separate from the detailed lxml handling shared by many callers.

## Args:
    text (str):
        Unicode document text to parse. Passed unchanged to create_root_node as the text argument (create_root_node handles trimming, NUL removal, encoding).
    type (str) (keyword-only):
        Key used to index the module-level mapping _ctgroup to obtain the parser configuration. The mapping entry looked up must be subscriptable with "_parser" (i.e., _ctgroup[type]["_parser"] must yield a parser class/type acceptable to create_root_node).
    **lxml_kwargs (Any):
        Additional keyword arguments forwarded directly to create_root_node. Common supported keywords (handled by create_root_node) include:
            - base_url (Optional[str])
            - huge_tree (bool)
            - body (bytes)
            - encoding (str)
        Any other kwargs accepted by create_root_node or by the parser class passed to create_root_node may also be supplied.

Parameter interactions:
- The function does not inspect or mutate lxml_kwargs; all interactions between those options (huge_tree vs. module-level support, body vs. text handling, etc.) are handled by create_root_node.
- The provided type must map to a structure containing the "_parser" key. If not, a KeyError or TypeError may result.

## Returns:
    lxml.etree._Element
        The root element produced by create_root_node(...). Under normal conditions this is the element returned by lxml.etree.fromstring called inside create_root_node. If create_root_node falls back to a minimal document (per its behavior) that element is returned. Any return value(s) from create_root_node are forwarded unchanged.

## Raises:
    KeyError:
        If the provided type is not a key in the module-level _ctgroup mapping.
    KeyError or TypeError:
        If _ctgroup[type] does not contain the expected "_parser" key or the mapping value is not subscriptable as expected.
    Any exception raised by create_root_node:
        - Examples include lxml.etree.XMLSyntaxError, ValueError, TypeError, etc.; these propagate unchanged. create_root_node also may raise TypeError if the parser class does not accept expected kwargs.

## Constraints:
Preconditions:
- The module-level mapping _ctgroup must be defined and contain an entry for the given type such that _ctgroup[type]["_parser"] yields a parser class/type.
- text must be a str (or at least behave like one for strip/replace/encode); otherwise create_root_node may raise.
- Parsers referenced by the mapping must accept the kwargs create_root_node passes when instantiated (recover=True, encoding=..., optionally huge_tree=True depending on module-level support).

Postconditions:
- On successful return, the result is an lxml.etree._Element suitable for downstream XPath/CSS selection.
- There are no remaining guarantees about the input variables; all normalization and encoding rules are the responsibility of create_root_node.

## Side Effects:
- No direct I/O performed by this function.
- Any side effects originate from create_root_node and may include:
    - Emitting a runtime warning via warnings.warn if parser.error_log indicates the input requires lxml's huge-tree support.
    - Iterating parser.error_log for messages.
- No global state is mutated by this function itself beyond whatever create_root_node may do (which, per its spec, only emits warnings).

## Control Flow:
flowchart TD
    Start[Start]
    Lookup{Is type key present in _ctgroup?}
    Start --> Lookup
    Lookup -- No --> RaiseKeyError[KeyError raised]
    Lookup -- Yes --> GetParser[_parser = _ctgroup[type]["_parser"]]
    GetParser --> CallCreate[call create_root_node(text, _parser, **lxml_kwargs)]
    CallCreate --> ReturnRoot[return root element from create_root_node]
    RaiseKeyError --> End[End]
    ReturnRoot --> End

## Examples:
1) Basic usage with a valid mapping key (conceptual)
    Note: the string "html" below is illustrative; the actual valid keys depend on the module-level _ctgroup mapping.
        try:
            root = _get_root_from_text("<html><body>Hi</body></html>", type="html")
        except KeyError:
            # Provided type not configured in _ctgroup
            handle_missing_type()
        except etree.XMLSyntaxError as e:
            # Malformed input; propagate or handle as appropriate
            handle_parse_error(e)

2) Passing parser options through lxml_kwargs
    - Forward options like base_url or huge_tree to control parsing behavior:
        root = _get_root_from_text(doc_text, type="xml", base_url="http://example.com", huge_tree=True)

Implementation notes:
- This function intentionally performs no validation beyond mapping lookup; the heavy lifting (body/text normalization, NUL removal, parser instantiation and the huge_tree/version warning behavior) is implemented by create_root_node.
- Consumers must ensure the type key exists in _ctgroup and that the parser class stored under "_parser" is compatible with create_root_node.

## `parsel.selector._get_root_and_type_from_bytes` · *function*

## Summary:
Convert raw response bytes into an appropriate parsed root or data object and return that object together with a canonical content-type string ("text", "json", "html", or "xml").

## Description:
This helper inspects the provided bytes and input hints to determine how to convert the bytes into a usable in-memory representation:

- If the caller explicitly requests text, the bytes are decoded and returned as a unicode string.
- If the encoding equals the literal string "utf8", a best-effort attempt is made to interpret the bytes as JSON; on success the parsed JSON object is returned and the type is "json".
- If the caller explicitly requests JSON via input_type="json", the function returns (None, "json") — signaling JSON mode without attempting to parse (useful where parsing is deferred or handled elsewhere).
- Otherwise the function normalizes the desired parsing mode to "html" or "xml" (using the internal _xml_or_html helper), selects an lxml parser from the module-level mapping, and delegates to create_root_node to produce an lxml root element; the parsed root and the canonical type ("html" or "xml") are returned.

Known callers within the provided context:
- No explicit callers are shown in the provided snippets. Conceptually this function is used by code paths that build a selector or parse incoming response content (e.g., the constructors or factory functions that accept raw response bytes and must decide whether to treat them as text, JSON, HTML, or XML). It isolates the "detect and normalize" logic used before creating a selector/root.

Why this logic is extracted:
- Centralizes the detection/normalization rules for raw bytes -> (root, type), keeping JSON/text detection, assertion of allowed input_type values, and lxml root creation in one place. This prevents repeating the same branching and parser-selection logic at multiple call sites and ensures consistent behavior (especially for JSON autodetection when encoding=="utf8" and the mapping of input_type values to parser types).

## Args:
    body (bytes):
        Raw bytes representing the response or document payload. Must support bytes operations (no assumption of text).
    encoding (str):
        Encoding hint used when decoding bytes to text. The function compares this string exactly to "utf8" (case-sensitive) when deciding whether to attempt JSON autodetection. It is also passed through to create_root_node so it should be a valid encoding name for text.encode/decoder usage inside create_root_node.
    input_type (Optional[str], keyword-only):
        A caller hint that must be one of:
            - "text"   -> force returning decoded text
            - "json"   -> indicate JSON mode (function will return None, "json" unless autodetection already returned parsed JSON)
            - "html"   -> force HTML parsing
            - "xml"    -> force XML parsing
            - None     -> no explicit hint; function may autodetect JSON (see encoding) and otherwise defaults to HTML parsing for unknown values
        Interdependencies:
            - If input_type == "text", the function decodes and returns text immediately (body is decoded using encoding).
            - If input_type == "json", the function returns (None, "json") unless an earlier JSON autodetect succeeds (see encoding).
    **lxml_kwargs (Any):
        Arbitrary keyword arguments forwarded to create_root_node. Commonly used keys include base_url, huge_tree, and others that create_root_node accepts. These are used only when producing an lxml root.

## Returns:
Tuple[Any, str]
    - The first element is the parsed payload:
        - str: when input_type == "text" — the result of body.decode(encoding).
        - Any (Python object): when JSON autodetection succeeds — the object returned by json.load(BytesIO(body)) (e.g., dict, list, etc.).
        - None: when input_type == "json" but JSON autodetection did not run (or failed), the function returns None as the payload while signalling "json" mode.
        - lxml.etree._Element (or similar root object): when the function chooses HTML/XML parsing and create_root_node returns the parsed root.
    - The second element is a canonical string indicating the chosen type:
        - "text", "json", "html", or "xml".
    Edge cases:
        - If encoding == "utf8" but the bytes are not valid JSON, the JSON loader raises ValueError which the function catches and treats as "not JSON"; processing continues to later branches.
        - If create_root_node raises an exception (e.g., lxml.etree.XMLSyntaxError), that exception propagates to the caller.

## Raises:
    AssertionError:
        - If input_type is not one of: "html", "xml", "text", "json", or None (the function asserts input_type in ("html", "xml", None) after handling "text" and "json"); the code contains an assertion to guard unexpected values and will raise AssertionError for invalid inputs.
    Any exception raised by create_root_node:
        - create_root_node may raise lxml parsing exceptions (e.g., XMLSyntaxError) or other exceptions; these propagate out of this function.
    Note:
        - json.load's ValueError is explicitly caught inside the function during autodetection, so malformed JSON does not raise out of this function during the autodetection attempt.

## Constraints:
Preconditions:
    - body must be a bytes-like object.
    - encoding must be a string; it is compared exactly to "utf8" for JSON autodetection.
    - input_type should be either "text", "json", "html", "xml", or None. Other values can trigger the module assertion.
Postconditions:
    - The returned type string is guaranteed to be one of "text", "json", "html", "xml".
    - If a non-lxml return (text or parsed JSON) is produced, no call to create_root_node is made.
    - If an lxml root is returned, create_root_node will have been called with parser_cls chosen from the module-level mapping _ctgroup[type]["_parser"] and with encoding and any provided lxml_kwargs forwarded.

## Side Effects:
    - Uses json.load(BytesIO(body)) when encoding == "utf8" (this reads from an in-memory BytesIO; no file I/O or network I/O is performed).
    - Calls create_root_node(...) when HTML or XML parsing is selected; create_root_node itself may emit warnings (via warnings.warn) and will invoke lxml parsing routines (which may read internal parser state).
    - No global state is modified by this function itself.

## Control Flow:
flowchart TD
    Start([Start])
    CheckText{input_type == "text"?}
    DecodeText[Decode body.decode(encoding) -> return (text, "text")]
    CheckEncoding{encoding == "utf8"?}
    TryJSON[try: data = json.load(BytesIO(body))]
    JSONOK{data is not _NOT_SET?}
    ReturnJSON[return (data, "json")]
    CheckExplicitJSON{input_type == "json"?}
    ReturnExplicitJSON[return (None, "json")]
    AssertType[assert input_type in ("html","xml",None)]
    Normalize{type = _xml_or_html(input_type)}
    SelectParser[parser_cls = _ctgroup[type]["_parser"]]
    ParseRoot[root = create_root_node(text="", body=body, encoding=encoding, parser_cls=parser_cls, **lxml_kwargs)]
    ReturnRoot[return (root, type)]
    Start --> CheckText
    CheckText -- yes --> DecodeText
    CheckText -- no --> CheckEncoding
    CheckEncoding -- yes --> TryJSON
    TryJSON -->|ValueError caught -> data = _NOT_SET| JSONOK
    JSONOK -- true --> ReturnJSON
    JSONOK -- false --> CheckExplicitJSON
    CheckEncoding -- no --> CheckExplicitJSON
    CheckExplicitJSON -- yes --> ReturnExplicitJSON
    CheckExplicitJSON -- no --> AssertType --> Normalize --> SelectParser --> ParseRoot --> ReturnRoot

## Examples:
1) JSON autodetection (encoding is the literal string "utf8"):
    - Input:
        body = b'{"name": "Alice", "age": 30}'
        encoding = "utf8"
        input_type = None
    - Result:
        returns ({"name": "Alice", "age": 30}, "json")

2) Forced JSON mode without parsing:
    - Input:
        body = b'...'  # arbitrary bytes
        encoding = "utf8"
        input_type = "json"
    - Result:
        returns (None, "json")
    - Typical use: caller will later parse or treat payload as JSON elsewhere.

3) Forced text:
    - Input:
        body = b'<!doctype html><html>...</html>'
        encoding = "utf-8"
        input_type = "text"
    - Result:
        returns (body.decode("utf-8"), "text")

4) HTML parsing fallback:
    - Input:
        body = b'<!doctype html><html><body><p>Hello</p></body></html>'
        encoding = "utf-8"
        input_type = None
    - Result:
        returns (root_element, "html")
    - Where root_element is the object returned by create_root_node using the parser selected from _ctgroup["html"]["_parser"].

5) Error handling when create_root_node raises:
    try:
        root_or_data, content_type = _get_root_and_type_from_bytes(body, encoding, input_type=None)
    except Exception as e:
        # handle parsing/IO/encoding errors propagated from create_root_node
        handle(e)

Implementation notes / gotchas:
    - JSON autodetection only runs when encoding == "utf8" (exact string match). This is deliberate — other encodings skip autodetection.
    - The function treats JSON autodetection failures (json.load raising ValueError) as a non-JSON payload and continues to other branches.
    - The assertion ensures input_type is limited to expected values after known early branches; in production code callers should avoid passing unexpected input_type values to prevent AssertionError.
    - When the HTML/XML branch is taken, the parser class is chosen from the module-level _ctgroup mapping; replicating this function requires that mapping and compatible parser classes to be available.

## `parsel.selector._get_root_and_type_from_text` · *function*

## Summary:
Determine how to interpret a unicode payload — return the raw text, decoded JSON data, or an lxml root plus a canonical type string indicating "text", "json", "html", or "xml".

## Description:
This function implements the content-detection and delegation policy used by selector utilities to normalize a textual payload into a usable "root" and a canonical content type. The pipeline is:

- If the caller explicitly requested text (input_type == "text"), return the original string immediately.
- Otherwise, attempt to parse the text as JSON using json.loads:
    - If parsing succeeds, return the decoded Python object and "json".
    - JSON parsing is attempted unconditionally (unless the "text" branch returned early); thus a payload that is valid JSON will be treated as JSON even if a non-standard input_type was supplied.
- If parsing fails and the caller explicitly requested JSON (input_type == "json"), return (None, "json") to indicate the caller requested JSON but the payload was not valid JSON.
- Otherwise assert that input_type is one of ("html", "xml", None) and normalize to "html" or "xml" using _xml_or_html; delegate HTML/XML parsing to _get_root_from_text, forwarding any lxml parsing options.

Known callers and context:
- Typical callers are higher-level Selector constructors or parsing utilities that receive document text and an optional input_type hint and need to produce:
    - the raw text (for text-mode selectors),
    - a parsed JSON object (for JSON selectors), or
    - an lxml root element (for HTML/XML selectors) for XPath/CSS selection.
- Trigger: invoked when a selector-like API accepts text input and needs canonicalization into (root, type) before creating the selection object.

Why this is factored out:
- Centralizes the detection/dispatch logic (text vs. json vs. html/xml) and the policy that valid JSON always wins.
- Keeps the JSON handling and delegation to the HTML/XML parsing helper consolidated to avoid duplication across callers.

## Args:
    text (str):
        Unicode document payload to inspect and possibly parse. Must be a str (decoded text). Supplying bytes is not appropriate unless decoded first.
    input_type (Optional[str], keyword-only):
        Hint for expected content. This parameter is keyword-only in the function signature. Accepted and meaningful values:
            - "text": treat as raw text and return it unchanged (no JSON or HTML/XML parsing attempted).
            - "json": caller requests JSON semantics; if payload is not valid JSON the function returns (None, "json").
            - "html": force HTML parsing.
            - "xml": force XML parsing.
            - None: allow default behavior (attempt JSON, otherwise treat as HTML by default).
        Important nuance: json.loads is attempted (unless input_type == "text"), so a non-standard or unexpected input_type value will not cause an error if the payload is valid JSON — the function will return (parsed_data, "json") and will not reach the later assertion.
    **lxml_kwargs (Any):
        Forwarded unchanged to _get_root_from_text when HTML/XML parsing is selected. Typical keys recognized downstream include:
            - base_url (Optional[str])
            - huge_tree (bool)
            - body (bytes)
            - encoding (str)

## Returns:
    Tuple[Any, str]:
        - First element (root):
            - str: if input_type == "text"; returns the original text.
            - Python object (dict/list/str/number/bool/None): if json.loads succeeds.
            - None: if input_type == "json" but the text is not valid JSON.
            - lxml.etree._Element (or other value returned by _get_root_from_text): when HTML/XML parsing is chosen; the exact type depends on the parser and create_root_node behavior.
        - Second element (type): canonical string indicating interpretation:
            - "text", "json", "html", or "xml".

    All possible return-type combinations are covered above. If JSON parsing succeeds, that takes precedence over any input_type value except "text" (which returns early).

## Raises:
    AssertionError:
        Raised only if execution reaches the explicit assert and input_type is not one of ("html", "xml", None). Note that this assert is not reached when:
            - input_type == "text" (early return), or
            - json.loads(text) succeeds (function returns JSON).
        Therefore AssertionError occurs only in the path where JSON parsing failed, input_type was not "json", and input_type is not in ("html","xml",None).
    Any exception raised by _get_root_from_text:
        When HTML/XML parsing is selected the function delegates to _get_root_from_text; that helper may raise exceptions which propagate unchanged, for example:
            - KeyError: configuration/mapping for parser type missing.
            - lxml.etree.XMLSyntaxError: for malformed markup.
            - TypeError, ValueError: if parser instantiation arguments are incompatible.
    Note:
        - json.loads exceptions (json.JSONDecodeError, a subclass of ValueError) are caught and treated as "not JSON"; they are not propagated.

## Constraints:
Preconditions:
    - text must be a Python str (decoded text).
    - input_type should normally be one of: "text", "json", "html", "xml", or None. Other values may be tolerated if the payload is valid JSON (see behavior above), but relying on that is not recommended.
    - When HTML/XML parsing is selected, the provided lxml_kwargs must be compatible with the downstream parser helper and parser classes.

Postconditions:
    - On successful return, the second tuple element is one of {"text","json","html","xml"} and indicates how to interpret the first element.
    - No global state is modified by this function itself. Any side effects originate from delegated helpers (warnings, log inspection).

## Side Effects:
    - This function itself does not perform I/O or mutate global state.
    - Delegated parsing via _get_root_from_text may emit runtime warnings (warnings.warn) and may examine parser error logs; those are observable side-effects.
    - No network or filesystem operations happen here directly.

## Control Flow:
flowchart TD
    Start([Start])
    Start --> IsText{input_type == "text" ?}
    IsText -- Yes --> ReturnText["Return (text, 'text')"]
    IsText -- No --> TryJSON[Try json.loads(text)]
    TryJSON --> JSONSuccess{Did json.loads succeed?}
    JSONSuccess -- Yes --> ReturnJSON["Return (parsed_data, 'json')"]
    JSONSuccess -- No --> CheckJsonHint{input_type == "json" ?}
    CheckJsonHint -- Yes --> ReturnNoneJSON["Return (None, 'json')"]
    CheckJsonHint -- No --> AssertValidType{input_type in ('html','xml',None) ?}
    AssertValidType -- No --> RaiseAssert["AssertionError raised"]
    AssertValidType -- Yes --> NormalizeType["type = _xml_or_html(input_type)"]
    NormalizeType --> ParseRoot["root = _get_root_from_text(text, type=type, **lxml_kwargs)"]
    ParseRoot --> ReturnRoot["Return (root, type)"]
    ReturnText --> End([End])
    ReturnJSON --> End
    ReturnNoneJSON --> End
    ReturnRoot --> End
    RaiseAssert --> End

## Examples:
1) Valid JSON payload (json wins even if input_type is unexpected)
    text = '{"ok": true}'
    root, typ = _get_root_and_type_from_text(text, input_type="weird")
    # root == {"ok": True}, typ == "json"

2) Caller explicitly requests JSON but payload is not JSON
    text = "<html>not json</html>"
    root, typ = _get_root_and_type_from_text(text, input_type="json")
    # root is None, typ == "json"

3) Early return for text mode
    text = "plain text"
    root, typ = _get_root_and_type_from_text(text, input_type="text")
    # root == "plain text", typ == "text"

4) HTML parsing with forwarded lxml options
    text = "<html><body>Hi</body></html>"
    root, typ = _get_root_and_type_from_text(text, input_type=None, base_url="http://example/")
    # root is an lxml element (or as produced by _get_root_from_text); typ == "html"

5) Error handling (parsing errors propagate from downstream helper)
    try:
        root, typ = _get_root_and_type_from_text(bad_text, input_type="xml")
    except AssertionError:
        handle_bad_type()
    except KeyError:
        # underlying parser missing
        handle_config_error()
    except etree.XMLSyntaxError as e:
        handle_parse_error(e)

## `parsel.selector._get_root_type` · *function*

## Summary:
Resolve and return the effective parsing/selection mode (a canonical string) by combining runtime inspection of the provided root object with an optional explicit type hint.

## Description:
This helper centralizes the policy that decides which parsing mode (xml, html, json, or a caller-provided mode) should be used for subsequent selector or parsing logic.

Known callers within the provided context:
- Intended to be called by selector initialization or dispatch code that needs to normalize a parsing mode before performing parsing or selection (e.g., code that constructs a Selector from various root inputs).
- No explicit direct callers were present in the supplied snippet, but callers are typically responsible for supplying `root` and optionally `input_type`.

Why this logic is extracted:
- Enforces a single, well-defined resolution order and error policy (element vs. JSON vs. provided hint), avoiding duplicated branching logic across the codebase.
- Encapsulates the decision rules and the single invalid-combination error (lxml element with "json"/"text") so callers can rely on uniform behavior.

## Signature notes:
- The function's Python signature makes `input_type` a keyword-only parameter (callers must pass input_type=<value>).
- Type annotation: input_type is annotated as Optional[str] and the declared return type is str. Callers should adhere to these types. The implementation returns `input_type` directly in one branch, so passing non-string truthy values is possible at runtime but violates the annotated contract; callers should avoid doing so.

## Args:
    root (Any):
        - The candidate root object for parsing/selection.
        - Expected typical shapes:
            * lxml.etree._Element instances for parsed HTML/XML trees
            * dict or list for already-parsed JSON structures
            * str/bytes/bytearray possibly containing textual JSON or other text
            * None or other types are accepted but will follow documented resolution rules.
    input_type (Optional[str]) (keyword-only):
        - Optional explicit hint for parsing mode.
        - Typical values: "xml", "html", "json", "text", or None.
        - Interdependencies:
            * If `root` is an lxml.etree._Element and `input_type` is "json" or "text", the function raises ValueError (this is considered an invalid combination).
            * When `root` is an lxml element, the function delegates to _xml_or_html(input_type), which returns "xml" only if input_type == "xml"; otherwise it returns "html".
            * If `root` is not an element and not JSON-like, a truthy `input_type` is returned as-is (so callers should ensure it's a string consistent with expectations).

## Returns:
    str
    - The resolved parsing mode string. Possible outcomes:
        * "xml" or "html": when `root` is an lxml.etree._Element; exact value determined by _xml_or_html(input_type):
            - input_type == "xml" -> "xml"
            - otherwise -> "html"
        * "json": when `root` is a dict or list, or when `_is_valid_json(root)` returns True (i.e., textual JSON).
        * input_type (as provided): when `root` is neither an lxml element nor JSON-like and `input_type` is truthy; typically a string provided by the caller.
        * "json" (fallback default): when none of the above apply and `input_type` is falsy (None or empty).
    - Note: Although the declared return type is str, if a caller violates the annotation and provides a non-string truthy input_type, that value would be returned as-is at runtime. Callers should avoid non-string input_type to preserve expected behavior.

## Raises:
    ValueError
    - Condition: `root` is an instance of lxml.etree._Element AND input_type is exactly "json" or "text".
    - Message produced:
        "Selector got an lxml.etree._Element object as root, '<input_type>' as type."
      where <input_type> is the repr of the provided input_type value (for example, 'json').

## Constraints:
    Preconditions:
        - Caller supplies the actual root object and optionally a string input_type via the keyword argument.
        - Callers should respect the annotated types (input_type is Optional[str]); passing non-string values is not recommended.
    Postconditions:
        - The function returns a single string that callers can use to select parsing behavior. No mutation of `root` or other global state occurs.

## Side Effects:
    - None visible to callers. Internally, the function may call `_is_valid_json(root)`, which uses json.loads inside a try/except; this is a transient in-memory parse attempt and does not produce persistent side effects.
    - No I/O, no network calls, and no global state mutation.

## Implementation (decision order):
1. If isinstance(root, lxml.etree._Element):
    - If input_type in {"json", "text"} -> raise ValueError.
    - Else return _xml_or_html(input_type) which yields "xml" only for exact input_type == "xml", else "html".
2. Elif isinstance(root, (dict, list)):
    - Return "json" (short-circuits to avoid unnecessary json parsing).
3. Elif _is_valid_json(root) returns True:
    - Return "json".
4. Else:
    - Return input_type if it is truthy, otherwise return "json".

Notes:
- The check for dict/list precedes _is_valid_json specifically to avoid calling json.loads on an already-parsed JSON structure.
- _is_valid_json attempts json.loads and returns False on TypeError or ValueError, so only benign parsing attempts are made.

## Control Flow:
flowchart TD
    Start([Start]) --> IsElement{isinstance(root, etree._Element)?}
    IsElement -- yes --> CheckInvalid{input_type in {"json","text"}?}
    CheckInvalid -- yes --> RaiseVal["Raise ValueError: Selector got an lxml.etree._Element object as root, '<input_type>' as type."]
    CheckInvalid -- no --> CallXMLorHTML["Return _xml_or_html(input_type) -> 'xml' or 'html'"]
    IsElement -- no --> IsDictList{isinstance(root,(dict,list))?}
    IsDictList -- yes --> ReturnJson1["Return 'json' (already-parsed JSON)"]
    IsDictList -- no --> IsValidJson{_is_valid_json(root) returns True?}
    IsValidJson -- yes --> ReturnJson2["Return 'json' (textual JSON)"]
    IsValidJson -- no --> InputTypeTruthy{input_type truthy?}
    InputTypeTruthy -- yes --> ReturnInput["Return input_type (as provided)"]
    InputTypeTruthy -- no --> ReturnDefault["Return 'json' (fallback)"]
    CallXMLorHTML --> End([End])
    ReturnJson1 --> End
    ReturnJson2 --> End
    ReturnInput --> End
    ReturnDefault --> End
    RaiseVal --> End

## Examples:
1) lxml element with explicit XML:
    - root: lxml.etree._Element instance
    - input_type="xml"
    - returns: "xml"

2) lxml element with no or non-"xml" hint:
    - root: lxml.etree._Element instance
    - input_type=None (or "html")
    - returns: "html"

3) Already-parsed JSON:
    - root: {"a": 1}
    - input_type="html"
    - returns: "json"  (dict/list short-circuits; input_type ignored)

4) Textual JSON:
    - root: '{"ok": true}' (str)
    - input_type=None
    - behavior: _is_valid_json returns True -> returns "json"

5) Non-JSON text with caller hint:
    - root: "<html>...</html>" (str)
    - input_type="text"
    - returns: "text"  (neither element nor JSON-like, so input_type is returned)

6) Invalid element + JSON hint (error):
    - root: lxml.etree._Element instance
    - input_type="json"
    - raises ValueError: Selector got an lxml.etree._Element object as root, 'json' as type.

7) Caller passes non-string truthy input_type (not recommended):
    - root: "plain text"
    - input_type=123  (violates annotation)
    - runtime: the function will return 123 (preserving the provided value). Callers should avoid this pattern and pass strings.

Usage recommendation:
- Prefer passing input_type as None when you want auto-detection based on the root.
- Adhere to the annotated types (input_type: Optional[str]); this ensures the return value is a canonical string suitable for downstream parsing logic.

## `parsel.selector._is_valid_json` · *function*

## Summary:
Return True when the given input can be successfully parsed by the standard JSON parser, otherwise return False.

## Description:
- Known callers within the provided codebase context:
    - No direct call sites were present in the supplied snippet of parsel/selector.py.
- Typical callers and usage contexts:
    - Lightweight pre-check before attempting to parse or process text as JSON (for example: content extracted from HTML <script> elements, HTTP response bodies, or scraped page fragments) to decide whether to treat the data as JSON.
- Responsibility boundary:
    - Encapsulates the "is this JSON?" check so callers do not need to duplicate the try/except around json.loads. It intentionally only answers the boolean question and does not return the parsed object.

## Args:
    text (str):
        The candidate JSON input. The type annotation is str, but json.loads also accepts bytes and bytearray; any other object types will cause json.loads to raise TypeError which this function catches and treats as "not valid JSON".
        - Accepted input shapes for which json.loads may succeed: str, bytes, bytearray containing a UTF-8 (or decodable) JSON document.
        - Passing other Python types (e.g., dict, list, int, None) to json.loads is not appropriate and will typically raise TypeError; this function will return False in that case.

## Returns:
    bool:
        - True if json.loads(text) completes without raising TypeError or ValueError (i.e., the input is valid JSON text and was parsed successfully).
        - False if json.loads(text) raises either TypeError (wrong input type) or ValueError (including JSONDecodeError for invalid JSON syntax).
        - The function does not return the parsed Python value; callers that need the parsed object should call json.loads themselves (preferably inside their own try/except if they want to avoid double-parsing).

## Raises:
    - The function intentionally catches json.loads TypeError and ValueError and returns False instead of propagating them.
    - Any other exception types (not normally raised by the stdlib json module for typical inputs) are not caught and would propagate to the caller.

## Constraints:
- Preconditions:
    - Input should be a textual/byte sequence containing a JSON document (recommended types: str, bytes, bytearray).
- Postconditions:
    - The function returns a boolean and does not mutate any external state.
    - If True is returned, a subsequent call to json.loads(text) (with the same input) is expected to succeed (barring non-deterministic external changes like mutated global encoders).

## Side Effects:
    - None. No I/O, no global state changes, and no network calls. The only effect is the transient in-process parsing attempt performed by json.loads.

## Control Flow:
flowchart TD
    Start --> TryLoad[Call json.loads(text)]
    TryLoad -->|raises TypeError| ReturnFalse1[Return False]
    TryLoad -->|raises ValueError (e.g., JSONDecodeError)| ReturnFalse2[Return False]
    TryLoad -->|no exception| ReturnTrue[Return True]

## Examples (prose):
- Valid JSON:
    - Input: '{"a": 1, "b": [1,2,3]}' → json.loads succeeds → function returns True.
    - Input: b'{"ok": true}' (bytes) → json.loads decodes and succeeds → function returns True.
    - Input: 'null' or '123' → valid JSON values → function returns True.
- Invalid JSON:
    - Input: '{"a":1,' (truncated) → json.loads raises JSONDecodeError (ValueError) → function returns False.
    - Input: '' (empty string) → json.loads raises JSONDecodeError → function returns False.
- Wrong input type:
    - Input: None or an already-parsed dict/list → json.loads raises TypeError → function returns False.
- Usage recommendation:
    - If you need both a boolean check and the parsed object, prefer a single try/except around json.loads to avoid double parsing; use this helper when you only need a quick validity test before choosing a processing branch.

## `parsel.selector._load_json_or_none` · *function*

## Summary:
Parse the given text as JSON and return the decoded Python object, or None when the input is not a supported text/byte type or cannot be decoded as JSON.

## Description:
This small helper attempts to safely decode JSON from a provided text-like value and convert it into the corresponding Python object using the standard json.loads. It encapsulates the decision to return None on failure rather than raising an exception.

Known callers within this codebase:
    - No direct callers were discovered in the provided module snapshot. This helper is intended to be used by selector methods or utilities that need to attempt JSON parsing of extracted text (for example, when exposing a .json() convenience API on a selector). Confirm caller locations by searching the repository for its name.

Why this logic is extracted:
    - Centralizes safe JSON parsing behavior so callers receive a uniform None result on invalid input or parse error instead of dealing with exceptions.
    - Keeps calling code simple and focused on handling parsed results vs handling json exceptions repeatedly.
    - Enforces the boundary: "try parse JSON; if anything goes wrong return None" (including unsupported input types).

## Args:
    text (str | bytes | bytearray): The input to parse. Even though the function signature is annotated with str, the implementation accepts bytes and bytearray as well. Any other type (including None) will be treated as unsupported and cause the function to return None.
    - No default value.
    - There are no interdependencies between parameters (single-argument function).

## Returns:
    Any or None:
    - If parsing succeeds: returns the Python object produced by json.loads (commonly dict, list, str, int/float, bool, or None).
    - If parsing fails, or the input is not a supported type: returns None.
    - Important ambiguity: a successful parse of the JSON literal null (i.e., input "null") also results in Python None. Therefore a None return value is ambiguous — it can mean "invalid input / parse failure" or "valid JSON null". Callers that need to distinguish these cases must perform their own checks before calling this function (for example, inspect the raw text or use json.loads directly).

## Raises:
    - This function does not propagate exceptions. Any ValueError (including JSONDecodeError or UnicodeDecodeError raised by json.loads) is caught and results in returning None.
    - No exceptions are raised by this function itself.

## Constraints:
    Preconditions:
        - The caller should pass a str, bytes, or bytearray. If the caller passes other types (e.g., None, int, dict) the function will return None.
    Postconditions:
        - On return, either a parsed JSON Python object is produced (per json.loads semantics), or None is returned to indicate unsupported input or parse failure (with the ambiguity described above).

## Side Effects:
    - None. The function performs no I/O, does not mutate external state, and does not call external services.

## Control Flow:
flowchart TD
    Start --> IsTextType{is instance of str, bytes, bytearray?}
    IsTextType -- No --> ReturnNone1[Return None]
    IsTextType -- Yes --> TryLoad[Attempt json.loads(text)]
    TryLoad -- Success --> ReturnValue[Return parsed value]
    TryLoad -- ValueError --> ReturnNone2[Return None]

## Examples:
Example 1 — successful parse
    raw = '{"user": {"id": 1, "name": "Alice"}}'
    parsed = _load_json_or_none(raw)
    # parsed is a dict: {"user": {"id": 1, "name": "Alice"}}

Example 2 — invalid JSON returns None
    raw = '{"user": 123'  # missing closing brace
    parsed = _load_json_or_none(raw)
    # parsed is None -> indicates parse failure (or null), not an exception

Example 3 — bytes input is accepted
    raw_bytes = b'["a", "b", 3]'
    parsed = _load_json_or_none(raw_bytes)
    # parsed is a list: ["a", "b", 3]

Example 4 — distinction between invalid JSON and JSON null
    raw_null = 'null'
    parsed = _load_json_or_none(raw_null)
    # parsed is None -> could be valid JSON null; caller cannot tell from the return alone

Example 5 — guard and explicit error handling (recommended when distinction matters)
    raw = get_text_from_selector()  # hypothetical source
    if not isinstance(raw, (str, bytes, bytearray)):
        handle_missing_text()
    else:
        parsed = _load_json_or_none(raw)
        if parsed is None:
            handle_invalid_or_null()
        else:
            use_parsed(parsed)

## `parsel.selector.Selector` · *class*

*No documentation generated.*

### `parsel.selector.Selector.__init__` · *method*

## Summary:
Initialize a Selector instance by normalizing one of the allowed input sources (text, body, or root) into a canonical internal root object and content type, set namespace mapping and internal flags, and store the optional expression hint — raising on invalid or missing inputs.

## Description:
This constructor accepts exactly one of three input sources (text string, raw bytes body, or an explicit root object) and resolves them into:
- self.root: an in-memory parsed representation (string, parsed JSON object, or an lxml root element), and
- self.type: a canonical content type string ("text", "json", "html", or "xml").

Known callers / calling contexts:
- Direct instantiation of Selector when client code or higher-level factories create a selector from a response payload or previously-parsed root.
- Factory utilities and parsing pipelines that need to construct a Selector from HTTP response bytes, decoded text, or an existing lxml/JSON root.
- Typical lifecycle: called at object-creation time to prepare the selector for subsequent selection (XPath/CSS/JMESPath) operations.

Why this logic is factored into __init__:
- Normalization and validation are central to Selector behavior (choose parser, validate input types and presence of input, and prepare namespace/state). Keeping this as a single method ensures uniform input handling every time a Selector is constructed, and centralizes error conditions and side-effects (warnings, parser delegation).

## Args:
    text (Optional[str], default=None):
        Unicode payload to parse. If provided, must be a Python str. When present, it takes precedence over `root` (root will be ignored with a warning). If provided, the initializer calls _get_root_and_type_from_text(text, input_type=type, base_url=base_url, huge_tree=huge_tree) to obtain (root, type).
    type (Optional[str], default=None):
        Optional hint for content type. Allowed values: "html", "json", "text", "xml", or None. If a value outside this set is passed, ValueError is raised immediately. When passed, this value is forwarded to helper functions and may be normalized by them.
    body (bytes, default=b""):
        Raw bytes payload. If provided (non-empty), must be of type bytes. When present and `text` is not provided, the initializer calls _get_root_and_type_from_bytes(body=body, encoding=encoding, input_type=type, base_url=base_url, huge_tree=huge_tree) to obtain (root, type).
    encoding (str, default="utf8"):
        Encoding hint used when decoding bytes or selecting autodetection behavior in helpers. The helper functions treat the literal string "utf8" specially for JSON autodetection.
    namespaces (Optional[Mapping[str, str]], default=None):
        Optional mapping of XML namespaces to use for XPath/CSS queries. If provided, these entries are merged into the instance's namespace mapping (which is initialized from self._default_namespaces).
    root (Optional[Any], default=_NOT_SET):
        An explicit pre-parsed root object. If provided (i.e., not the module sentinel _NOT_SET) and `text` is not provided, it is used directly as self.root. The initializer resolves self.type via _get_root_type(root, input_type=type). If both `text` and `root` are supplied, `root` is ignored and a runtime warning is emitted.
    base_url (Optional[str], default=None):
        Optional base URL passed to downstream parsing helpers (forwarded to _get_root_and_type_from_text/_get_root_and_type_from_bytes). Used for resolving relative links in HTML/XML parsing.
    _expr (Optional[str], default=None):
        Optional expression hint to store on the instance (copied to self._expr). This is not interpreted by __init__, it is preserved for later selection operations.
    huge_tree (bool, default=LXML_SUPPORTS_HUGE_TREE):
        Hint forwarded to parsing helpers controlling lxml's huge_tree option. Default comes from the module-level LXML_SUPPORTS_HUGE_TREE constant.

## Returns:
    None
    - Standard constructor: returns nothing (None). The effect is observed via instance attribute initialization.

## Raises:
    ValueError:
        - If `type` is not one of ("html", "json", "text", "xml", None). Exact message: f"Invalid type: {type}".
        - If none of the three inputs are provided (text is None, body is falsy/empty, and root is the sentinel _NOT_SET). Message: "Selector needs text, body, or root arguments".
        - Note: If `root` is provided and _get_root_type detects an invalid combination (e.g., lxml element root with input_type "json" or "text"), that helper raises ValueError; such ValueError propagates to the caller.
    TypeError:
        - If `text` is provided but is not an instance of str: TypeError with message "text argument should be of type str, got <class '...'>".
        - If `body` is provided (truthy) but is not bytes: TypeError with message "body argument should be of type bytes, got <class '...'>".
    Any exception raised by delegated helpers:
        - _get_root_and_type_from_text, _get_root_and_type_from_bytes, and _get_root_type may raise their own exceptions (e.g., JSON decode errors caught inside helpers and handled, but lxml parsing exceptions like XMLSyntaxError or other runtime errors from those helpers will propagate). These exceptions are not caught by __init__.

## State Changes:
    Attributes READ:
        - self._default_namespaces (read to initialize the instance namespace mapping)
    Attributes WRITTEN:
        - self.root: set to the resolved root object (string, parsed JSON object, or lxml root).
        - self.type: set to the canonical content type string ("text", "json", "html", or "xml").
        - self.namespaces: set to a shallow copy of self._default_namespaces and then updated with passed `namespaces` if provided.
        - self._expr: set to the incoming _expr value.
        - self._huge_tree: set to the incoming huge_tree flag.
        - self._text: set to the incoming text argument (may be None).

## Constraints:
    Preconditions:
        - Caller must pass at least one of: a non-None `text`, a non-empty `body` (truthy bytes), or a `root` different from the module sentinel _NOT_SET.
        - `type` (if provided) must be one of the allowed set ("html", "json", "text", "xml") or None.
        - If `text` is provided, it must be a str.
        - If `body` is provided (non-empty), it must be bytes.
        - Module-level sentinels/constants used by the implementation (_NOT_SET, LXML_SUPPORTS_HUGE_TREE) are assumed to exist.
    Postconditions:
        - After __init__ returns successfully:
            * self.root is set to a usable value (not the sentinel _NOT_SET).
            * self.type is one of {"text", "json", "html", "xml"} (helpers guarantee canonicalization).
            * self.namespaces is a dict containing default namespace entries plus any user-provided namespaces.
            * self._expr, self._huge_tree, and self._text reflect the provided arguments.
        - If parsing helpers parsed input into an lxml root, that root is stored directly; if JSON was detected/parsed, the parsed Python object (dict/list) or None (when forced json mode without parse) is stored and self.type == "json".
        - If `text` and `root` were both supplied, the provided `root` is ignored (warning emitted) and processing follows the `text` branch.

## Side Effects:
    - Emits warnings.warn when both `text` and `root` are provided: "Selector got both text and root, root is being ignored." (stacklevel=2).
    - Delegates to helper functions:
        - _get_root_and_type_from_text may attempt json.loads(text) and call an HTML/XML parsing helper; it can emit warnings and raise parsing exceptions which surface to callers.
        - _get_root_and_type_from_bytes may attempt json.load(BytesIO(body)) (JSON autodetection when encoding == "utf8") and may call create_root_node or other parsing helpers; parsing exceptions propagate.
        - _get_root_type performs type resolution logic and may raise ValueError for invalid combinations (e.g., lxml element root with input_type "json" or "text").
    - No network or filesystem I/O is performed by __init__ itself. Any I/O-like behavior would come from delegated parsing helpers (which typically operate in-memory).
    - No global state is mutated by __init__; only instance attributes are created/modified.

## Implementation notes / reimplementation checklist:
    - Validate `type` immediately against the allowed set and raise ValueError on invalid entries.
    - Enforce presence of at least one input source (text/body/root sentinel). Raise ValueError if missing.
    - If `text` is provided:
        * Validate it is str (raise TypeError otherwise).
        * If `root` is supplied (not sentinel) emit warnings.warn and ignore the provided root.
        * Call _get_root_and_type_from_text(text, input_type=type, base_url=base_url, huge_tree=huge_tree) to obtain (root, type), assign to self.root/self.type.
    - Else if `body` is truthy:
        * Validate it is bytes (raise TypeError otherwise).
        * Call _get_root_and_type_from_bytes(body=body, encoding=encoding, input_type=type, base_url=base_url, huge_tree=huge_tree) and assign returned (root, type).
    - Else (root was provided):
        * Assign self.root = root.
        * Resolve type via self.type = _get_root_type(root, input_type=type).
    - Initialize namespaces with a shallow copy of self._default_namespaces and update with provided `namespaces` if not None.
    - Set self._expr, self._huge_tree, and self._text to the provided values.
    - Let any exceptions from helper functions propagate (do not swallow parser errors).

### `parsel.selector.Selector.__getstate__` · *method*

## Summary:
Prevents instances from being pickled by immediately raising a TypeError when the pickling machinery requests the object's state.

## Description:
This method implements the pickling hook used by Python's pickle protocol. When an attempt is made to serialize a Selector instance (for example via pickle.dump, pickle.dumps, or when the copy module delegates to pickle for deep/shallow copying), the pickle machinery will attempt to obtain the object's state by calling its __getstate__ method. This implementation intentionally does not return a serializable state; instead it raises a TypeError with the message "can't pickle Selector objects" to signal that Selector objects must not be pickled.

This logic is placed in its own method because the pickle protocol looks for and calls a __getstate__ method by name. Keeping the behavior here centralizes the "not serializable" policy for all pickling attempts instead of scattering checks where pickling might be initiated.

## Args:
    None

## Returns:
    None. This method never returns normally; it always raises a TypeError.

## Raises:
    TypeError: Always raised with the exact message "can't pickle Selector objects". This is triggered immediately whenever __getstate__ is invoked by any code (typically the pickle machinery) attempting to serialize the object.

## State Changes:
    Attributes READ:
        - None. The method does not read any self.<attr> attributes.
    Attributes WRITTEN:
        - None. The method does not modify any self.<attr> attributes.

## Constraints:
    Preconditions:
        - None beyond the normal requirement that self is a valid Selector instance. No internal state assumptions are required because the method does not inspect or mutate the instance.
    Postconditions:
        - The Selector instance remains unchanged.
        - The call will always raise TypeError; no state is produced for serialization.

## Side Effects:
    - No I/O or external service calls are performed.
    - No mutations to objects outside self occur.
    - The effective side effect is behavioral: it prevents serialization by raising an exception observed by the calling (pickling) code.

### `parsel.selector.Selector._get_root` · *method*

## Summary:
Create and return an lxml root element for this Selector by delegating to the shared parsing helper, selecting the parser class based on the requested content type; does not modify the Selector instance.

## Description:
This thin helper delegates parsing to the module-level create_root_node function while selecting the appropriate parser class from the module-level _ctgroup mapping using the provided type argument or the Selector's current self.type.

Known callers and context:
- Selector.xpath: used when the Selector holds plain text (type == "text") to obtain an lxml root for running XPath queries. In that flow it is invoked with the selector's stored text (self._text) and an explicit type override (e.g., type="html").
- It is intended for internal use within Selector methods that need to obtain a parsed DOM from either a text string or a bytes body.
- The method centralizes parser selection so callers only need to provide raw text/body and optional overrides (base_url, huge_tree, type).

Why this is a separate method:
- Keeps parser selection logic (lookup of the parser class in _ctgroup and forwarding of parse-related options) in one place rather than repeating it across methods (e.g., xpath).
- Makes calling code simpler and clearer: callers supply content and parsing options; _get_root handles choosing and passing the correct parser to create_root_node.
- Allows tests and other Selector internals to call parsing in a uniform way and to override type when needed.

## Args:
    text (str): Unicode input to parse. Defaults to "" (empty string). If truthy, create_root_node will use this text (after trimming/NUL removal/encoding) and ignore `body`.
    base_url (Optional[str]): Optional base URL forwarded to create_root_node and ultimately to lxml.etree.fromstring for resolving relative URLs. Defaults to None.
    huge_tree (bool): Whether to request a parser configured with huge_tree support. Defaults to the module-level LXML_SUPPORTS_HUGE_TREE value. Caller-specified value is forwarded to create_root_node which will only pass huge_tree=True to the parser if both this argument and the module-level support flag are truthy.
    type (Optional[str]): Content type hint used to select the parser class from module-level _ctgroup. If truthy it overrides self.type for the purpose of parser selection. Accepted values must be keys present in the module-level _ctgroup mapping (e.g., the standard content types used in this module). Defaults to None.
    body (bytes): Raw bytes fallback input, forwarded to create_root_node. Used when `text` is falsey. Defaults to b"".
    encoding (str): Encoding name forwarded to create_root_node and used when `text` must be encoded to bytes. Defaults to "utf8".

## Returns:
    lxml.etree._Element
    The element tree root returned by create_root_node (i.e., the parsed document root). This is the same object create_root_node returns and may be any concrete lxml element type appropriate for the parsed input.

    Edge-case returns:
    - If create_root_node reparses using a fallback (e.g., b"<html/>") it will return that fallback root.
    - The method itself does not return None; any None or exception results come from create_root_node and are propagated.

## Raises:
    - Any exception raised by create_root_node is propagated unchanged (for example lxml.etree.XMLSyntaxError, ValueError, TypeError raised by lxml or the parser).
    - KeyError: if the chosen key (type or self.type) is not present in the module-level _ctgroup mapping, the dictionary lookup _ctgroup[type or self.type] will raise KeyError.
    - TypeError: if the mapping entry exists but does not contain the expected "_parser" key, or if the resolved parser class does not accept the keywords create_root_node supplies (propagated from parser instantiation or create_root_node).

## State Changes:
    Attributes READ:
        - self.type: read to determine which parser class to use when the type argument is falsey.
    Attributes WRITTEN:
        - None. This method does not modify any Selector attributes.

## Constraints:
    Preconditions:
        - The Selector instance must have a usable self.type value when the caller does not provide the type argument. In normal construction of Selector objects self.type is set; if a Selector were constructed/modified incorrectly such that self.type is None or missing, a KeyError will likely occur.
        - The provided type (if non-None) or self.type must be a valid key in the module-level _ctgroup mapping and the mapping entry must contain an "_parser" value that is a callable parser class accepted by lxml.etree.fromstring.
        - text must be a str (or behave like one) when passed; body should be bytes when used. If these types are violated, create_root_node or lxml may raise TypeError or similar.
    Postconditions:
        - On successful return, an lxml.etree._Element is returned and no Selector instance attributes have been changed.
        - If parsing fails, exceptions from create_root_node are propagated and the Selector remains unchanged.

## Side Effects:
    - Delegates to create_root_node which:
        - Instantiates a parser class (may pass recover, encoding and optionally huge_tree).
        - Calls lxml.etree.fromstring (no file/network I/O inside this call itself).
        - May inspect parser.error_log and emit a warnings.warn if the error log indicates the document requires huge-tree support.
    - No direct I/O or global state mutation is performed by this method itself.

### `parsel.selector.Selector.jmespath` · *method*

## Summary:
Execute a JMESPath query against the Selector's underlying data and return a SelectorList of new Selector objects wrapping each match; does not mutate the original Selector.

## Description:
This method evaluates a JMESPath expression (query) against the Selector's underlying data (JSON or the text of an HTML/XML document) and converts each match into a Selector instance, then returns those instances in a SelectorList.

Known callers:
- Not determinable from this method's body alone. Typically invoked by client code that has a Selector instance and wants to query structured JSON-like data or text extracted from HTML/XML.

Lifecycle / pipeline context:
- Used when code needs to run declarative queries (JMESPath) over data already represented by a Selector. It belongs to the query/extraction stage of a parsing pipeline.

Why this is a distinct method:
- Encapsulates the full flow of preparing the Selector's data for JMESPath, executing the query with any passed-through options, normalizing the result, and converting raw matches into Selector objects. Keeping it separate centralizes JMESPath-specific behavior and the conversion logic so it can be reused by calling code and kept consistent across Selector instances.

## Args:
    self: _SelectorType
        The Selector instance on which the method is called. Must expose attributes used below (type, root, selectorlist_cls, and a constructor compatible with the call sites used here).
    query (str):
        A JMESPath expression string to evaluate against the Selector's data.
    **kwargs (Any):
        Additional keyword arguments forwarded directly to jmespath.search(query, data, **kwargs). These may be used to pass context or custom functions supported by the jmespath library.

## Returns:
    SelectorList[_SelectorType]:
        A SelectorList containing zero or more Selector instances created from the JMESPath query results.

        - If jmespath.search(...) returns None, the method returns an empty SelectorList.
        - If jmespath.search(...) returns a non-list singleton (e.g., a string, number, or dict), that value is wrapped into a single-element list and converted into one Selector.
        - For each element x in the resulting list:
            - If x is a str: the method creates a Selector by calling the Selector class constructor with text=x, _expr=query, and type="text". This selector represents raw text content.
            - Otherwise: it creates a Selector by calling the Selector class constructor with root=x and _expr=query. This selector wraps the native Python object (dict, list, number, etc.) returned by JMESPath.

## Raises:
    AssertionError:
        If self.type is not "json" and is not one of {"html", "xml"}. The method contains an assert that enforces this when self.type != "json".
    Any exception raised by the JSON-loading helper or by jmespath.search:
        Exceptions from the JSON loader used for self.root (if self.root is a string or when using .text for HTML/XML) or from jmespath.search will propagate out of this method unchanged. The method does not catch them.

## State Changes:
    Attributes READ:
        - self.type (str): inspected to decide how to obtain the data to query ("json" vs "html"/"xml").
        - self.root: inspected and either parsed (if string) or used directly as data; for html/xml the .text attribute of self.root is accessed.
        - self.selectorlist_cls: used to construct and return a SelectorList from the list of new Selector instances.
        - self.__class__: used as the constructor for creating new Selector instances.
    Attributes WRITTEN:
        - None. The original Selector instance (self) is not mutated by this method.

## Constraints:
    Preconditions:
        - self must have an attribute type whose value is "json", "html", or "xml".
        - For "json": self.root should either be a parsed JSON object (dict/list/primitive) or a JSON string that the code's JSON loader can parse.
        - For "html" or "xml": self.root must have a .text attribute (typically an lxml/html element or document object) that contains JSON text to be parsed.
        - query must be a valid JMESPath expression string (syntax errors from jmespath.search will propagate).

    Postconditions:
        - The returned SelectorList contains zero or more Selector instances whose _expr attribute equals the provided query.
        - String results from JMESPath become Selectors with type="text" and text set to the string value.
        - Non-string results become Selectors with root set to the Python object returned by JMESPath.
        - The method returns an empty SelectorList when jmespath.search returns None.

## Side Effects:
    - No external I/O is performed by this method itself.
    - The method calls an internal JSON loader (via _load_json_or_none) when self.root is a string (or when querying html/xml uses self.root.text); any side effects of that loader (if any) will occur.
    - The method calls jmespath.search(query, data, **kwargs), which may perform computation within the jmespath library. Any exceptions from that call propagate outward.
    - New Selector objects are constructed; these are returned wrapped in a SelectorList but no external state or files are modified.

### `parsel.selector.Selector.xpath` · *method*

## Summary:
Execute an XPath expression against the Selector's underlying document/root and return a SelectorList of new Selector objects for each matched item; the original Selector is not modified.

## Description:
Runs an lxml XPath query on the Selector's data (self.root for "html"/"xml", or a temporary parsed root for "text") and wraps each resulting item into a new Selector instance.

Known callers and contexts:
- parsel.selector.Selector.css uses this method after converting a CSS selector to XPath; css(...) simply calls xpath(...) as part of the selection pipeline.
- Typical user code calls xpath(...) during the element-selection phase of parsing HTML or XML to obtain nodes, string values, numbers, or booleans via XPath expressions.
- Invoked in the selection/query stage of a parsing pipeline, after the Selector has been constructed from text, bytes, or an existing root.

Why separate:
- Centralizes XPath evaluation, namespace merging, error handling, normalization of results, and wrapping of results into Selector objects.
- Avoids duplication of XPath-related logic and enables css(...) to reuse this behavior.

## Args:
    query (str):
        - XPath expression to evaluate. Required.
    namespaces (Optional[Mapping[str, str]]):
        - Mapping of prefix -> namespace URI to use for this evaluation.
        - If provided, merges over the Selector's own namespaces: the provided mapping overrides existing prefixes.
        - Default: None
    **kwargs (Any):
        - Forwarded directly to the underlying lxml xpath call.
        - Note: the method always passes smart_strings=self._lxml_smart_strings explicitly. Supplying smart_strings in kwargs will result in a duplicate keyword argument and raise a TypeError when calling lxml's xpath method.

## Returns:
    SelectorList[_SelectorType]
    - A SelectorList (constructed via self.selectorlist_cls) containing one Selector per result item from the XPath evaluation.
    - Each result item x is converted via:
        self.__class__(root=x, _expr=query, namespaces=self.namespaces, type=_xml_or_html(self.type))
    - If the xpath evaluation returns a non-list scalar (string, number, boolean), it is converted into a single-item list before wrapping.
    - If the underlying root does not expose xpath (AttributeError when accessing .xpath) an empty SelectorList (self.selectorlist_cls([])) is returned.

Edge-case returns:
    - Empty SelectorList when:
        * self.root has no xpath attribute (AttributeError), or
        * for type "text", creating a temporary root via self._get_root(...) yields an object without xpath.
    - Never returns None.

## Raises:
    ValueError:
        - If self.type is not in ("html", "xml", "text"):
            Exact message: "Cannot use xpath on a Selector of type {self.type!r}"
        - If lxml raises an etree.XPathError during evaluation:
            Exact message: "XPath error: {exc} in {query}" where {exc} is the original etree.XPathError.
    TypeError (propagated):
        - If kwargs includes smart_strings, the underlying call will receive duplicate keyword arguments and Python will raise TypeError (multiple values for keyword argument 'smart_strings').
        - Other TypeErrors from the underlying xpath call (e.g., invalid kwarg types) are propagated.
    Propagated exceptions:
        - Exceptions raised by self._get_root(...) when parsing temporary roots (e.g., parser configuration or lxml parsing errors) are propagated unchanged.
        - Any other exceptions from the underlying lxml xpath call (beyond etree.XPathError) propagate.

## State Changes:
    Attributes READ:
        - self.type: to verify allowed modes and to decide whether to use self.root or parse a temporary root.
        - self.root: accessed to obtain the .xpath attribute when type is "html" or "xml".
        - self._text: read when type == "text" to parse a temporary root via _get_root(self._text or "", type="html").
        - self.namespaces: used as the base namespace mapping and passed into each new Selector created for results.
        - self._lxml_smart_strings: read and passed into the lxml xpath call via smart_strings=...
        - self.__class__: used to instantiate new Selector objects wrapping result items.
        - self.selectorlist_cls: used to construct the returned SelectorList wrapper.
        - self._get_root (method): invoked for text selectors.
    Attributes WRITTEN:
        - None. The method does not modify any attributes on self.

## Constraints:
Preconditions:
    - self.type must be one of "html", "xml", or "text" to use xpath; otherwise a ValueError is raised.
    - For "html"/"xml", self.root should normally be an lxml node/tree exposing xpath; if not, an empty SelectorList is returned.
    - For "text", self._text should be a string (or None); _get_root(...) must be able to create a parseable root or it may raise.
    - query must be a valid XPath expression; malformed expressions raise etree.XPathError which is wrapped as ValueError.

Postconditions:
    - The Selector instance remains unchanged.
    - Returns a SelectorList of zero or more new Selector instances, each with _expr set to query and namespaces set to the original Selector's namespaces (note: the namespaces used for evaluation are the merged mapping, but the wrappers receive self.namespaces).

## Side Effects:
    - No direct file or network I/O performed by this method.
    - When type == "text", invoking self._get_root(...) may instantiate parsers and trigger lxml parsing, which can emit warnings or parser-side errors.
    - Allocates new Selector objects and a SelectorList wrapper; no mutation of existing objects outside the returned values occurs.

## Implementation notes for reimplementation:
    - Validate self.type is in ("html","xml","text"); otherwise raise ValueError with the exact message used above.
    - For "html"/"xml": attempt to access self.root.xpath; if AttributeError, return self.selectorlist_cls([]).
    - For "text": call self._get_root(self._text or "", type="html") and obtain its .xpath; on AttributeError return an empty SelectorList.
    - Build nsp = dict(self.namespaces); if namespaces argument provided, call nsp.update(namespaces) and pass nsp to xpath via namespaces=nsp.
    - Always pass smart_strings=self._lxml_smart_strings into the xpath call; do not allow overriding via kwargs (passing smart_strings in kwargs will raise TypeError at call time).
    - Catch etree.XPathError and raise ValueError(f"XPath error: {exc} in {query}") preserving the original exception message.
    - Ensure non-list single results are coerced to a single-item list before wrapping.
    - Wrap each result item x with self.__class__(root=x, _expr=query, namespaces=self.namespaces, type=_xml_or_html(self.type)) and return self.selectorlist_cls(list_of_wrapped).

### `parsel.selector.Selector.css` · *method*

## Summary:
Convert a CSS selector string to an XPath expression and evaluate it on this Selector, returning a SelectorList of the matched nodes (or an empty SelectorList). This operation does not mutate the Selector.

## Description:
Known callers and contexts:
- Caller: user code that requests nodes using CSS syntax (typical pipeline step: selection/filtering). Example usage: selector.css("div.item > a").
- Caller: parsel.selector.SelectorList.css delegates to each element's css method; SelectorList.css iterates its elements and calls this method during chained selection across multiple elements.
- Lifecycle stage: invoked during the query/selection phase when a consumer expresses a node selection using CSS selectors. It performs translation then dispatches to the existing XPath evaluation path.

Why this is a separate method:
- Keeps the public API concise (css(query) exposes CSS-based selection).
- Reuses existing, well-tested XPath evaluation by translating CSS -> XPath and calling xpath(...). This avoids duplicating node-evaluation logic and centralizes the CSS-to-XPath translation in _css2xpath.

## Args:
    query (str): A CSS selector expression. Must be a string. The method does not validate CSS beyond delegating to the translator; invalid CSS may cause the translator to raise.

## Returns:
    SelectorList[_SelectorType]: A SelectorList containing Selector instances for each matched item. If no nodes match, returns an empty SelectorList instance (selectorlist_cls([])).
    Edge cases:
    - If translation succeeds but the resulting XPath selects no nodes, an empty SelectorList is returned.
    - If translation or XPath evaluation produces nodes that are non-elements (e.g., text), returned Selector instances wrap those roots according to Selector.xpath/_construction rules.

## Raises:
    ValueError:
        - If this Selector's type is not one of "html", "xml", or "text". The exact message is:
          "Cannot use css on a Selector of type {self.type!r}"
        - May also be raised indirectly by Selector.xpath when an XPath evaluation raises an lxml etree.XPathError (xpath wraps that as ValueError: "XPath error: {exc} in {query}").
    Any exception raised by Selector._css2xpath:
        - _css2xpath may raise KeyError, AttributeError, TypeError, or translator-specific exceptions if the underlying csstranslator is missing, misconfigured, or rejects the CSS. These exceptions propagate unchanged.
    Any exception raised by Selector.xpath:
        - Selector.xpath may raise other exceptions during root access or root construction (for "text" type) — these propagate unchanged.

## State Changes:
Attributes READ:
    - self.type: checked to ensure CSS selection is valid and used by _css2xpath to choose translator.
    - self.root: may be read transitively by Selector.xpath when determining if xpath evaluation is available.
    - self._text: may be read transitively by Selector.xpath for "text" typed selectors to construct a temporary root for evaluation.
    - self.namespaces: read transitively by Selector.xpath when building namespace mapping for XPath evaluation.
    - self._lxml_smart_strings: read transitively by Selector.xpath when invoking the lxml xpath evaluator.
Attributes WRITTEN:
    - None. This method does not modify the Selector's attributes.

## Constraints:
Preconditions:
    - The Selector instance must be initialized and have a valid self.type attribute.
    - self.type must be one of "html", "xml", or "text" before calling; otherwise a ValueError is raised.
    - query should be a str. Passing non-string values may raise TypeError from the translator or downstream code.

Postconditions:
    - The Selector instance remains unchanged.
    - A SelectorList is returned that wraps zero or more Selector instances representing the selection results.
    - Any translator or XPath evaluation exceptions are propagated to the caller.

## Side Effects:
    - No I/O is performed by this method itself.
    - Calls out to two other components:
        1) self._css2xpath(query) — may call into a csstranslator implementation; any side effects performed by that translator (logging, internal state) are external to this method and are not modified here.
        2) self.xpath(xpath_expr) — executes XPath evaluation which may read the Selector.root and related state; any side effects of XPath evaluation (none in normal lxml usage) belong to lxml or Selector.xpath.
    - No external resources are modified by this method. Exceptions from underlying calls propagate to the caller.

### `parsel.selector.Selector._css2xpath` · *method*

## Summary:
Convert a CSS selector string into an equivalent XPath expression using the parser-specific css-to-xpath translator; does not modify the Selector object.

## Description:
This internal helper normalizes the Selector's parsing mode to a canonical parser type ("xml" or "html") and delegates the conversion of the provided CSS selector string to a csstranslator instance chosen for that parser type.

Known callers and usage context:
- parsel.selector.Selector.css: Primary caller. css() uses this method to convert a CSS selector into an XPath expression and then passes that XPath to Selector.xpath to evaluate the selection. This occurs during the selection pipeline when callers request nodes using CSS syntax.
- Intended as an internal utility (prefixed with an underscore) so external code normally calls Selector.css rather than this method directly.

Why this is a separate method:
- Centralizes the CSS-to-XPath conversion logic and the choice of translator based on the Selector's type. This keeps Selector.xpath/css implementation concise and allows swapping or customizing the translator mapping (_ctgroup) in one place without inlining translator selection everywhere.

## Args:
    query (str): A CSS selector expression. Must be a string. Empty strings are accepted syntactically but the underlying translator may raise an error or return an XPath that matches nothing.

## Returns:
    str: An XPath expression equivalent to the provided CSS selector according to the chosen csstranslator. The returned value is returned verbatim from the translator; callers should expect a valid XPath string or for the translator to raise an exception on invalid input.

## Raises:
    KeyError:
        - If the module-level mapping for the normalized type is missing, i.e., _ctgroup does not contain an entry for the canonical type returned by _xml_or_html(self.type).
        - If the mapping entry exists but does not contain the "_csstranslator" key.
    AttributeError:
        - If the value stored at _ctgroup[canonical_type]["_csstranslator"] does not provide a css_to_xpath attribute (method).
    Any exception raised by the translator's css_to_xpath implementation:
        - If the underlying csstranslator implementation validates the CSS and finds it invalid, it may raise its own error types (these are propagated unchanged).
    TypeError (implicit):
        - If a non-string is passed for query and the translator expects a string, that may result in a TypeError from the translator. The method itself does not perform explicit type checking beyond the function signature.

## State Changes:
Attributes READ:
    - self.type: used to decide which translator to use (normalized via _xml_or_html).
Attributes WRITTEN:
    - None. This method does not mutate the Selector instance.

## Constraints:
Preconditions:
    - The Selector instance must be initialized such that self.type exists (the Selector class constructor always sets this).
    - The module-level mapping _ctgroup must be present and contain an entry for the canonical parser type (typically "xml" or "html").
    - The mapping entry _ctgroup[canonical_type] must contain a key "_csstranslator" whose value implements a callable css_to_xpath(query: str) -> str.
    - query should be a str; passing other types may cause translator-specific errors.

Postconditions:
    - The Selector instance remains unchanged.
    - A string is returned which (if the translator succeeds) is a valid XPath expression representing the original CSS selector.

## Side Effects:
    - No I/O is performed.
    - No global state is modified by this method itself.
    - The method calls into an external translator object (from the module-level mapping). Any side effects or logging performed by that translator are external to this method and are not controlled here.
    - Exceptions thrown by the translator propagate to the caller.

## Implementation Notes (for reimplementation):
    - Use the internal helper _xml_or_html(self.type) to normalize the selector type into the canonical keys used by _ctgroup.
    - Lookup the translator at _ctgroup[canonical_type]["_csstranslator"] and call its css_to_xpath method with the provided query.
    - Do not swallow exceptions from the translator; allow them to propagate so calling code (e.g., Selector.css or Selector.xpath) can handle or surface them.
    - Keep this method minimal and side-effect free: it should only perform the lookup/dispatch and return the translator's result.

### `parsel.selector.Selector.re` · *method*

## Summary:
Extracts all substrings from the Selector's current data that match a regular expression and returns them as a list of strings. This is a pure-read operation — it does not modify the Selector.

## Description:
- What it does: Calls the Selector.get() method to obtain the textual representation of the current selection and applies the provided regular expression (or compiled pattern) to that text. It delegates matching and optional HTML/entity replacement to the module-level utility extract_regex.
- Known callers:
    - Selector.re_first — calls this method to obtain an iterable of matches and take the first result (or a default).
    - Typical usage in scraping pipelines: called after selecting nodes with css()/xpath()/jmespath() to extract substrings (IDs, tokens, numbers, etc.) from the serialized node text or from text selectors.
- Why a dedicated method: Keeps regex-based extraction ergonomically available on Selector objects, centralizes the conversion from the Selector's internal node/root to a string (via get()), and reuses the shared extract_regex utility that handles group extraction, flattening and entity replacement.

## Args:
    regex (Union[str, Pattern[str]]):
        - Either a regular expression string (will be compiled using Python's re.compile(..., re.UNICODE))
          or an already-compiled Pattern[str].
        - If the compiled pattern contains a named group "extract", only that group's contents are used for each match; otherwise, all findall results are used.
    replace_entities (bool, default True):
        - If True, HTML/entity replacements are applied to each extracted string (via the underlying utility), preserving at least "lt" and "amp" entities per the utility's behavior.
        - If False, raw matched substrings are returned without entity replacement.

## Returns:
    List[str]:
        - A list of extracted strings according to extract_regex behavior.
        - If no matches are found, returns an empty list.
        - Returned strings are flattened (if the regex findall produced nested sequences, those are flattened).
        - If replace_entities is True, returned strings have entities replaced according to the utility (with "lt" and "amp" preserved); if False, returned strings are raw.

## Raises:
    re.error:
        - Raised if regex is a string that fails to compile (invalid regular expression syntax).
    TypeError:
        - May be raised by the underlying regex operations if the text returned by Selector.get() is not a str (for example, if the Selector is of type "json" and its root is a non-string Python object).
        - Note: Selector.get() typically returns a str for HTML/XML/text selectors; callers should ensure the Selector's content is string-like before calling re.
    (No exceptions are explicitly raised by this method itself; it forwards exceptions from get() or extract_regex.)

## State Changes:
    Attributes READ:
        - self.get() is invoked; therefore, this method reads data that get() depends on, including:
            - self.root
            - self.type
            - self._text (indirectly used by get() for text/html fallback)
    Attributes WRITTEN:
        - None. The Selector object is not modified.

## Constraints:
    Preconditions:
        - regex must be either a string or a compiled Pattern[str].
        - The Selector should represent data that can be meaningfully converted to a string (typical when Selector.type is "html", "xml", or "text"). If Selector.type == "json", ensure the root is a string if you expect regex matching to work without TypeError.
    Postconditions:
        - The Selector remains unchanged.
        - The call returns a list (possibly empty) containing zero or more strings extracted from the textual representation returned by get().

## Side Effects:
    - No I/O or network activity.
    - Calls an external utility function (extract_regex) which may, under the hood, perform HTML/entity replacement via a helper (this is a pure transformation with no persistent side effects).
    - No mutation of objects outside self (no global state changes).

## Implementation notes / edge cases (behavior inherited from extract_regex and get()):
    - If regex has a named group "extract", only the contents of that group (for each match) are returned.
    - If regex has capturing groups, findall may return tuples; these are flattened by the utility before being returned.
    - If regex.search(...) returns None for a pattern using the "extract" group, the utility treats that as no match and contributes nothing to the result.
    - When replace_entities is True, the utility replaces HTML entities but preserves at least "lt" and "amp" (per the utility's configuration).
    - If regex is invalid, re.compile will raise re.error; callers who construct regex strings should handle or propagate that exception.

### `parsel.selector.Selector.re_first` · *method*

## Summary:
Return the first substring matched by the provided regular expression against this Selector's textual data (or the given default if no match is found); the Selector instance is not modified.

## Description:
This small convenience method delegates to Selector.re(...) to obtain all regex matches for this Selector's serialized data, normalizes the possibly nested result structure with iflatten, and returns the first element (using next(..., default)). It is intended as an ergonomic API for callers who need a single match rather than a list.

Known callers and usage context:
- Part of the public Selector extraction API; commonly used by scraping/parsing code after selecting nodes (e.g., after xpath() or css()) when only one matched string is required.
- Typical lifecycle stage: the extraction phase of a scraping pipeline where a single value is needed from a selected element's contents.

Why this is a separate method:
- Encapsulates the common pattern of extracting regex matches and selecting the first result (with default handling), keeping calling code concise and consistent.

## Args:
    regex (Union[str, Pattern[str]]):
        Regular expression to search with. Can be a pattern string or a compiled Pattern[str].
    default (Optional[str], optional):
        Value returned when no match is found. Defaults to None.
        - Note: typing overloads indicate that passing a non-None default yields a non-Optional return type statically.
    replace_entities (bool, optional):
        Passed through to Selector.re / extract_regex. If True (default), HTML/XML entities in extracted text will be replaced/unescaped during extraction.

## Returns:
    Optional[str]:
        - The first matched substring (str) from the flattened sequence of matches, if any exist.
        - If there are no matches, returns the provided default (which may be None).
        - If the first match is an empty string, an empty string may be returned.

## Raises:
    - This method does not raise exceptions itself, but will propagate exceptions from its callees, for example:
        * Errors raised by extract_regex or the underlying regex engine (e.g., invalid pattern).
        * Exceptions from Selector.re or Selector.get if serialization or extraction fail.
    - Any such exception propagates unchanged to the caller.

## State Changes:
    Attributes READ:
        - self.root: used indirectly by Selector.get() as the source to serialize or extract textual data.
        - self.type: read indirectly by Selector.get() to determine how to obtain/serialize the selector data (html/xml/text/json).
    Attributes WRITTEN:
        - None. This method does not modify the Selector instance.

## Constraints:
    Preconditions:
        - The Selector must be a valid instance (constructed with text, body, or root).
        - regex must be a str or compiled Pattern[str]; other types may cause helper functions to raise.
        - replace_entities must be a boolean.

    Postconditions:
        - The Selector instance remains unchanged.
        - The return value is either the first matched string or the provided default.

## Performance and behavior notes:
    - re_first delegates to Selector.re(...), which returns a list of matches (via extract_regex). Consequently, the extraction step typically computes all matches before re_first selects the first; re_first itself does not short-circuit the extraction work done by Selector.re.
    - iflatten flattens nested list-like structures returned by Selector.re (for example, tuples of capture groups), so nested match structures are normalized before selecting the first element.

## Side Effects:
    - No I/O or network activity.
    - No mutation of external objects; the only observable outcomes are the returned value or any propagated exceptions.

## Example:
    value = selector.re_first(r"price:\s*(\d+\.\d+)", default="0.00")
    # Returns the first captured price string if present; otherwise "0.00".

### `parsel.selector.Selector.get` · *method*

## Summary:
Return the Selector's current node or its serialized string representation depending on the Selector type; does not modify the object.

## Description:
- Known callers and contexts:
    - Selector.re and Selector.re_first: invoked to obtain the textual data to run regex extraction on (data-extraction stage).
    - Selector.getall: calls get to produce the single value returned as a one-item list.
    - Selector.__bool__: used to determine truthiness of a selector by checking whether get() yields a non-empty value.
    - Selector.__str__/__repr__: called to obtain a printable representation of the selector's data when formatting the object.
    - External user code and pipelines: commonly called by client code that wants the textual/JSON value represented by the Selector.
- Lifecycle / pipeline stage:
    - Called during result extraction and when converting the Selector's underlying node to a text/json representation for consumers.
- Why this is a separate method:
    - Centralizes logic for converting different internal root types (text, json, html, xml, and arbitrary objects) to a returned value or string.
    - Reused by several other methods (re, getall, __bool__, __str__) so having conversion logic in one place avoids duplication and keeps behavior consistent.

## Args:
    None

## Returns:
    Any
    - If self.type is "text" or "json": returns self.root unchanged (could be str, None, list, dict, etc., depending on how the Selector was created).
    - Otherwise (typically "html" or "xml"): normally returns a str containing the serialized XML/HTML for self.root produced by lxml.etree.tostring with encoding="unicode" and with_tail=False.
    - Edge-case return values:
        - If etree.tostring raises AttributeError or TypeError (e.g., self.root is not an lxml element or does not support tostring), then:
            - If self.root is True -> returns string "1"
            - If self.root is False -> returns string "0"
            - Otherwise -> returns str(self.root)
        - If self.type is "text" or "json" and self.root is None, returns None.

## Raises:
    - This method catches AttributeError and TypeError raised by lxml.etree.tostring and falls back to string conversions described above; those exceptions do not propagate.
    - Possible uncaught exceptions that can propagate:
        - KeyError if self.type is not present in the module-level mapping used to select the tostring method (accessing _ctgroup[self.type] can raise KeyError).
        - Any other exception raised by lxml.etree.tostring or by str(self.root) that is not an AttributeError or TypeError will propagate to the caller.

## State Changes:
- Attributes READ:
    - self.type
    - self.root
- Attributes WRITTEN:
    - None (the method does not modify the Selector object)

## Constraints:
- Preconditions:
    - self.type should be set to one of the recognized types (commonly "html", "xml", "text", or "json"). If self.type is not present in the module's internal configuration mapping used to choose a tostring method, a KeyError may occur.
    - self.root should be the internal representation consistent with self.type (e.g., an lxml element for "html"/"xml" types, or a Python object/primitive for "text"/"json").
- Postconditions:
    - The method returns either:
        - the original root (unchanged) for "text" and "json" types, or
        - a stable string representation for other types (or a fallback string for non-element roots), and leaves the Selector state unchanged.

## Side Effects:
    - No I/O or network activity.
    - Calls lxml.etree.tostring when serializing element trees (pure in-memory operation).
    - Does not mutate objects outside self; fallback uses str(self.root) which may call arbitrary __str__ implementations but does not alter state.

### `parsel.selector.Selector.getall` · *method*

## Summary:
Return a one-element list containing the Selector's current value (the same value returned by its single-value accessor), without modifying the Selector.

## Description:
- Known callers and contexts:
    - External user code and data-extraction pipelines that expect a list of matches even when only a single node/value is present.
    - It is referenced by higher-level extraction code that normalizes results to sequences (for example, parts of client code that treat single and multiple match results uniformly).
    - Internally, it delegates to Selector.get to produce the element value.
- Lifecycle / pipeline stage:
    - Invoked during the result-normalization or extraction stage, when a caller prefers to receive results as a list rather than a scalar.
- Why this is a separate method:
    - Provides a concise, self-documenting API to obtain a list-of-values form of the Selector's data without requiring callers to wrap get() results manually.
    - Keeps client code uniform when consumers sometimes expect sequences and sometimes single items; centralizing this behavior avoids repeated one-line wrappers across the codebase.

## Args:
    None

## Returns:
    List[str]
    - Returns a list with exactly one element: [self.get()].
    - The element's runtime type and value are exactly whatever Selector.get() returns:
        * For Selectors of type "html"/"xml" this will typically be a str containing serialized element HTML/XML.
        * For Selectors of type "text"/"json" this may be the original object stored in self.root (which can be None, a str, a dict, a list, etc.).
        * Edge-case values:
            - If Selector.get() returns None, getall returns [None].
            - If Selector.get() returns a non-string (e.g., a dict for JSON), the returned list contains that object unchanged.
    - Note: Although the declared return annotation is List[str], the runtime element types reflect Selector.get()'s return type.

## Raises:
    - No new exceptions are raised by this method itself.
    - Any exception raised by Selector.get() will propagate to the caller (for example, KeyError if module-level mappings used by get are misconfigured, or any unexpected exception raised during serialization by lxml.etree.tostring).

## State Changes:
- Attributes READ:
    - Indirectly reads the attributes accessed by Selector.get(), primarily:
        * self.type
        * self.root
- Attributes WRITTEN:
    - None. The method does not modify self or external objects.

## Constraints:
- Preconditions:
    - The Selector instance must be properly initialized so that Selector.get() can be called (self.type and self.root should be set to valid values consistent with how the Selector was constructed).
- Postconditions:
    - The Selector object remains unchanged.
    - The return value is a list whose sole element is equal to whatever Selector.get() returned at the time of the call.

## Side Effects:
    - No I/O or network calls.
    - Any side effects are limited to those performed by Selector.get() (for example, in-memory serialization via lxml.etree.tostring). The method itself performs no mutations outside of reading state.

### `parsel.selector.Selector.register_namespace` · *method*

## Summary:
Adds or updates a namespace mapping in the Selector's internal namespace table so subsequent XPath evaluations can resolve prefixed names.

## Description:
Known callers:
- No internal callers found in the repository memory snapshot. This method is intended to be called by user code (or higher-level helper code) that prepares a Selector before running xpath queries that use XML namespaces.
- Typical usage occurs during selector setup or pipeline initialization when the consumer needs to register namespace prefixes (for example, to query SVG or custom XML vocabularies) so that calls to Selector.xpath(...) can pass or use the selector's namespaces mapping.

Why this is a separate method:
- Encapsulates the common operation of adding/updating a single namespace mapping without requiring callers to manipulate the internal namespaces dict directly.
- Provides a small, discoverable API surface for users to register prefixes without needing to inspect or replace the entire mapping.
- Keeps caller code clearer (register_namespace("svg", "http://www.w3.org/2000/svg")) and communicates intent compared with directly mutating selector.namespaces.

## Args:
    prefix (str): Namespace prefix to register (e.g., "svg", "re"). The implementation expects a string; the method does not validate format or non-emptiness.
    uri (str): Namespace URI associated with the prefix (e.g., "http://www.w3.org/2000/svg"). The implementation expects a string; no validation of URI syntax is performed.

## Returns:
    None

## Raises:
    None raised explicitly by this method.
    Possible runtime exceptions (not raised by the method's logic but possible if preconditions are violated):
    - AttributeError: If called on an object that lacks a working self.namespaces attribute (for example, if called before Selector.__init__ completed).
    - TypeError: If self.namespaces is not a mutable mapping supporting item assignment; assignment may raise TypeError for incompatible types.

## State Changes:
    Attributes READ:
        - self.namespaces (accessed to perform item assignment)
    Attributes WRITTEN:
        - self.namespaces (mutated: item self.namespaces[prefix] is set to uri)

## Constraints:
    Preconditions:
        - The Selector instance must have an attribute self.namespaces that is a mutable mapping (normally initialized to a dict in Selector.__init__).
        - Callers should pass str values for both prefix and uri as indicated by the type hints; though not enforced, non-str keys/values may produce unexpected behavior elsewhere.
    Postconditions:
        - After the call, self.namespaces[prefix] == uri holds.
        - Other existing namespace mappings remain unchanged except if the given prefix already existed: in that case the previous mapping is overwritten.

## Side Effects:
    - Mutates the Selector instance by updating its namespaces mapping.
    - No I/O, no external service calls.
    - Visible effect on subsequent Selector.xpath(...) calls or other operations that consult self.namespaces: newly registered or updated prefix will be used for name resolution.

### `parsel.selector.Selector.remove_namespaces` · *method*

## Summary:
Mutate the selector's lxml element tree in place by removing XML namespace wrappers of the form {uri}localname from element tags and attribute names so the tree becomes namespace-free for subsequent queries.

## Description:
This method traverses every element under self.root using self.root.iter("*") and for each element:
- If the element tag string begins with "{", it replaces the tag with the portion after the first "}" (i.e., the local name).
- It iterates the element's attribute keys and for any attribute name beginning with "{", renames that attribute key to the local name (key after the first "}") by assigning the value to the new key and removing the old key.
After processing all elements it calls lxml.etree.cleanup_namespaces(self.root) to remove unused xmlns declarations from the tree.

Known callers and usage context:
- No direct internal callers were found in the repository snapshot. This is an explicit utility on Selector instances intended for use by library consumers or higher-level helpers when they need to run namespace-free XPath/CSS queries against an XML tree produced by lxml.
- Typical place to call: after creating a Selector from XML (Selector(..., type="xml") or from parsed root) and before running queries that do not use namespace prefixes.

Why this logic is a separate method:
- The operation requires a full-tree traversal, in-place renaming of both tags and attribute keys, and a cleanup pass. Encapsulating these steps prevents duplication and makes the destructive nature explicit.

## Args:
- None.

## Returns:
- None. The method returns no value; its effect is the in-place mutation of the element tree referenced by self.root.

## Raises:
- AttributeError: If self.root does not provide an .iter method, calling self.root.iter("*") will raise AttributeError.
- AttributeError: If an element's .tag or an attribute key is not a string-like object exposing .startswith, calling .startswith will raise AttributeError.
- Any exceptions raised by lxml.etree.cleanup_namespaces for invalid node types will propagate unchanged.

Note: For the Selector implementation in this project, self.root is expected to be an lxml element/tree (created via lxml.etree or lxml.html). Under that expectation, the method's operations are supported and do not raise for normal XML trees.

## State Changes:
Attributes READ:
- self.root: read to traverse the tree and access nodes' .tag and .attrib.

Attributes WRITTEN / Mutated:
- Element nodes under self.root: .tag values are replaced with their unqualified local names when they start with "{".
- Element .attrib mappings: attribute keys that start with "{" are removed and reinserted under the unqualified local name.
- The tree's namespace declarations are pruned by lxml.etree.cleanup_namespaces(self.root).
- The Selector.namespaces dict is NOT modified by this method.

## Constraints:
Preconditions:
- self.root must be an element/document tree object that supports .iter("*"), node .tag as a string-like value, and node .attrib as a mutable mapping of attribute-name->value (the method is written with lxml.etree elements in mind).
- Callers should expect the operation to be destructive to the DOM structure (tags and attribute names changed).

Postconditions:
- No element tag or attribute name reachable from self.root will begin with "{" (i.e., namespace-wrapped names are removed).
- Unused xmlns declarations that were formerly needed solely for the removed namespace wrappers will be removed from the tree by cleanup_namespaces.
- The method is effectively idempotent on subsequent calls: running it again will find no tags/attributes that start with "{" and will be a no-op except for a subsequent cleanup_namespaces call.

## Side Effects:
- In-place mutation of the DOM tree referenced by self.root; other references to the same tree will observe these changes.
- No file, network, or external I/O is performed.
- No modification of Python-level Selector metadata besides the mutated tree itself.

## Example (conceptual, not runnable code):
- Before: an element with tag "{http://example/}item" and attribute "{http://example/}id"="1"
- After: the element tag is "item" and the attribute key is "id".

## Complexity:
- Time: O(N + M) where N is the number of elements in the subtree rooted at self.root and M is the total number of attributes across those elements (each element and attribute is examined once).
- Space: O(1) additional space beyond the tree (in-place mutations).

### `parsel.selector.Selector.remove` · *method*

## Summary:
- Detaches the element referenced by this Selector from its parent in the parsed tree (in-place mutation). Emits a DeprecationWarning and delegates to the legacy parent.remove(self.root) semantics.

## Description:
- Known callers and context:
  - Historically called by user code or library code that needs to remove an element selected from an lxml-parsed HTML/XML tree. It is a user-facing API that was part of the element mutation interface for Selector instances.
  - The method itself emits a DeprecationWarning advising callers to use Selector.drop instead; typical lifecycle: after creating a Selector from text/body/root, locating a node via xpath/css/re, then calling remove() to mutate the in-memory tree by removing that node.
- Why this is a separate method:
  - remove exists to preserve a stable, backward-compatible API for callers that previously relied on parent.remove(self.root) semantics. The implementation centralizes the legacy behavior and deprecation signaling so callers can transition to drop() without silently changing behavior. Keeping removal logic as an isolated method also makes it easier to manage the specific error mapping (AttributeError -> specific exception types) used by the library.

## Args:
- None.

## Returns:
- None.
- On normal completion the method returns None; its effect is the in-memory removal/detachment of the element referenced by self.root from its parent tree.

## Raises:
- CannotRemoveElementWithoutRoot
  - Condition: Attempting to call getparent() on self.root raises AttributeError (i.e., self.root does not expose getparent()).
  - Exact message:
    "The node you're trying to remove has no root, are you trying to remove a pseudo-element? Try to use 'li' as a selector instead of 'li::text' or '//li' instead of '//li/text()', for example."
  - Typical cause: the Selector refers to a pseudo-element, a text node representation that doesn't provide getparent(), or the Selector was constructed with a non-tree root (e.g., plain text or JSON data).
- CannotRemoveElementWithoutParent
  - Condition: After obtaining parent = self.root.getparent(), attempting to call parent.remove(self.root) raises AttributeError (for example, parent is None or parent does not provide a remove method).
  - Exact message:
    "The node you're trying to remove has no parent, are you trying to remove a root element?"
  - Typical cause: the node is a document root (no parent) or parent is not an element with a remove method.
- Note: The method only converts AttributeError into the two specific exception types above. Other exception types raised by parent.remove(...) (e.g., TypeError, ValueError) will propagate unchanged.

## State Changes:
- Attributes READ:
  - self.root — accessed to call getparent() and then to be passed to parent.remove(self.root).
- Attributes WRITTEN:
  - None — the Selector instance's attributes are not reassigned by this method.
- Effect on external state:
  - The underlying lxml element object referenced by self.root is detached from its parent tree when the call succeeds. The Selector.root still references the element object, but that object is no longer part of the original tree. Other Selector instances pointing at the same tree may observe the mutation.

## Constraints:
- Preconditions:
  - The Selector must have been constructed with a root (Selector.__init__ enforces that at least one of text, body, or root was provided). For successful removal, self.root must be an lxml element-like object that implements getparent() and whose parent implements remove(node).
  - Calling remove on selectors representing text or json nodes, or on pseudo-elements without getparent(), will raise CannotRemoveElementWithoutRoot.
- Postconditions:
  - On success: the element referenced by self.root is removed from its parent (parent.remove(self.root) executed). The Selector object remains valid and still holds a reference to the detached element.
  - On failure: if an exception is raised, the tree is unchanged (no partial removal), and the corresponding specific exception is propagated.

## Side Effects:
- Mutates the in-memory lxml element tree by detaching/removing an element from its parent. This can affect other code that holds references into the same tree.
- Emits a DeprecationWarning via warnings.warn(category=DeprecationWarning, stacklevel=2) with a message advising to use Selector.drop instead.
- No I/O, network, or external service interactions are performed.

### `parsel.selector.Selector.drop` · *method*

## Summary:
Removes (detaches) the element represented by this Selector from its parent/document tree, leaving the Selector.root element object detached from the tree (no return value).

## Description:
Known callers and context:
- Called by user code or library code when a selected element must be removed from the parsed HTML/XML tree as part of cleaning, transformation, or mutation steps in a scraping or processing pipeline.
- The class also defines a deprecated remove() method that uses similar logic; remove() emits a DeprecationWarning and performs a parent.remove(self.root) for HTML/XML. drop() is the intended method to use moving forward.
- Typical lifecycle stage: after building a Selector from parsed text/body/root and using xpath/css/re() to locate nodes, drop() is called to mutate the underlying tree by removing the selected node.

Why this is a separate method:
- The operation needs to handle differences between XML and HTML element implementations provided by lxml (XML nodes require parent.remove(node), while HTML nodes have a drop_tree() convenience method).
- Centralizing removal logic avoids duplicating error handling and messaging across callers and preserves consistent semantics and exception types for missing root/parent conditions.

## Args:
- This method takes no arguments.

## Returns:
- None.
- No value is returned; the intended effect is the mutation of the underlying element tree.

## Raises:
- CannotRemoveElementWithoutRoot
    - Condition: self.root has no getparent() attribute (AttributeError raised when attempting self.root.getparent()).
    - Typical cause: self.root is not an lxml element (for example a pseudo-element or text node representation that does not expose getparent), or the Selector was created with a non-tree root (e.g., plain string for text/json selectors).
    - Exact message raised from the method:
      "The node you're trying to drop has no root, are you trying to drop a pseudo-element? Try to use 'li' as a selector instead of 'li::text' or '//li' instead of '//li/text()', for example."
- ValueError("This node has no parent")
    - Condition: self.type == "xml" and parent is None (node is an XML root node with no parent). The method explicitly raises this ValueError in that branch before attempting removal.
- CannotDropElementWithoutParent
    - Condition: Any AttributeError or AssertionError raised while performing the removal/detachment in the second try block is caught and re-raised as CannotDropElementWithoutParent.
    - Typical causes:
        - For HTML flow (self.type != "xml"): self.root does not implement drop_tree(), or drop_tree() fails with AssertionError (for example, if there is no parent or drop_tree precondition fails).
        - For XML flow: parent.remove(self.root) raises AttributeError/AssertionError (e.g., unexpected node type or parent lacks remove).
    - Exact message raised from the method:
      "The node you're trying to remove has no parent, are you trying to remove a root element?"

## State Changes:
Attributes READ:
- self.root: accessed to call getparent(), to be passed to parent.remove(), or cast to html.HtmlElement and used with drop_tree().
- self.type: checked to decide XML vs HTML removal strategy.

Attributes WRITTEN:
- None (the method does not assign to any self.* attribute).

Note about underlying element object mutation:
- Although no Selector attribute is reassigned, the underlying element object referenced by self.root is mutated relative to the tree:
    - For XML: parent.remove(self.root) detaches the element from its parent (it remains referenced by self.root but is no longer part of the parent's subtree).
    - For HTML: drop_tree() detaches the element from the tree (and may also adjust tails/text in accordance with lxml.html semantics).
- Other Selector instances pointing to the same tree may observe the element as removed after a successful call.

## Constraints:
Preconditions:
- The Selector must have been created with a root (Selector.__init__ enforces that Selector must have text, body, or root). However, the specific precondition for successful removal is that self.root is an lxml element-like object exposing getparent() and, for HTML-mode, drop_tree().
- Intended to be called on selectors representing HTML or XML nodes. Calling on selectors of type "json" or "text", or on pseudo-elements that do not expose getparent(), will raise CannotRemoveElementWithoutRoot.

Postconditions:
- If the call returns normally (no exception):
    - The element referenced by self.root is removed from its parent/document tree:
        - XML mode: parent no longer contains the element (parent.remove(self.root) executed).
        - HTML mode: the element has been detached via drop_tree().
    - self.root still references the same element object, but that object is no longer attached to the original tree.
- If the call raises:
    - The tree is unchanged (no partial removal), and one of the documented exceptions is propagated.

## Side Effects:
- Mutates the parsed lxml tree by detaching/removing an element from its parent. This is an in-memory mutation and can affect other Selectors or consumers that reference the same tree.
- No I/O, network calls, or other external side effects are performed by this method.
- No attributes on the Selector object are reassigned; only the external element structure is changed.

### `parsel.selector.Selector.attrib` · *method*

## Summary:
A read-only property that returns a new plain Python dict containing the current root element's attributes (a shallow snapshot) without modifying the Selector or the underlying node.

## Description:
This property accesses self.root.attrib on the Selector's current root node and returns a plain dict copy of that mapping. It is provided as a property (accessed as selector.attrib, not selector.attrib()) so callers get a convenient, idiomatic attribute-like view of an element's attributes.

Known callers / typical context:
- User code in scraping pipelines after selecting an element with Selector.xpath or Selector.css to inspect or serialize element attributes.
- Extraction or transformation functions that convert element attributes into structured fields.
- Any consumer that requires a plain Python dict instead of an lxml attribute mapping.

Why this lives as a property:
- Normalizes the underlying lxml-specific attribute mapping to a plain dict for easier downstream use.
- Returns a snapshot to prevent accidental mutation of the underlying element's attributes.
- Keeps attribute-access semantics small and centralized.

## Args:
    None

## Returns:
    Dict[str, str]: A newly allocated dictionary whose keys are attribute names and whose values are attribute values (both as strings).
    - Namespace-qualified attribute names are preserved in their raw representation (e.g. "{http://...}localname").
    - If the underlying element has no attributes, an empty dict is returned.
    - The returned dict is a shallow copy: mutating it does not affect self.root.attrib.

## Raises:
    AttributeError:
        - If self.root does not provide an .attrib attribute. This occurs when the Selector's root is not an element-like object (for example, when the Selector holds a plain string, JSON object, boolean, integer, or None).
    Note:
        - The Selector constructor normally ensures a root is present, but passing or constructing a Selector with a non-element root will trigger this error at access time.

## State Changes:
    Attributes READ:
        - self.root (accesses the root node and its .attrib mapping)
    Attributes WRITTEN:
        - None (no modifications to self or self.root)

## Constraints:
    Preconditions:
        - The Selector instance must have a root value (Selector.__init__ enforces this in normal construction).
        - For meaningful attribute data, the root should be an element node (HTML/XML element) that exposes .attrib.
    Postconditions:
        - Selector and underlying node remain unchanged.
        - Caller receives a fresh dict representing attributes at the moment of the call.

## Side Effects:
    - No I/O, network, or external service calls.
    - Allocates a new dict (memory proportional to number of attributes).

### `parsel.selector.Selector.__bool__` · *method*

## Summary:
Return the truth value of the Selector based on the value produced by its get() extraction — suitable for use in Python truthiness checks (e.g., if selector:).

## Description:
This method evaluates the Selector's truthiness by delegating to the instance's get() method and converting its result to a bool. It is invoked implicitly whenever a Selector is used in a boolean context: conditional statements (if/while), boolean operations (and/or/not), or when calling bool(selector). Typical call sites are user or library code that checks whether a selection returned any content during a scraping pipeline (for example, testing whether a query produced a non-empty result before further processing).

This logic is implemented as a dedicated method so all truthiness decisions use a single, well-defined point of behavior that mirrors get()'s semantics (including any normalization get() performs). Defining __bool__ separately keeps truthiness consistent across the codebase and avoids duplicating the conversion/normalization logic wherever truth checks are needed.

## Args:
    None.

## Returns:
    bool: True if the value returned by self.get() is truthy according to Python's standard truth-testing rules; False otherwise.
    - Examples:
        - If get() returns an empty string or None, __bool__ returns False.
        - If get() returns a non-empty string, non-empty container, or non-zero number, __bool__ returns True.
    - Edge-case to note:
        - If the Selector's underlying root is the boolean False, get() returns the string "0" (see get()). Since "0" is a non-empty string, bool("0") is True; therefore __bool__ will return True for a root that was originally False. Similarly, a root that was True becomes "1" and results in True.

## Raises:
    Propagates any unexpected exceptions raised by get() or operations inside it.
    - Under normal operation no exception is raised by __bool__ itself because get() handles AttributeError and TypeError paths; however, other errors (for example, runtime errors raised by third-party serializers) will propagate.

## State Changes:
    Attributes READ:
        - self.root
        - self.type
        (These are read indirectly via self.get().)
    Attributes WRITTEN:
        - None. This method does not modify the Selector instance.

## Constraints:
    Preconditions:
        - The object must be an initialized Selector (its __init__ guarantees that at least one of text/body/root was provided).
        - Attributes self.type and self.root should exist and be valid for get() to operate without raising unexpected exceptions.
    Postconditions:
        - The Selector object remains unchanged.
        - The return value reflects the truthiness of get()'s result at the time of the call.

## Side Effects:
    - No I/O or external service calls are performed by __bool__ itself.
    - Indirectly, get() may call etree.tostring(...) for non-text/json types; this is a pure in-memory operation and may allocate memory or CPU but does not perform network or file I/O.
    - No mutation of objects outside self is performed.

### `parsel.selector.Selector.__str__` · *method*

## Summary:
Return a compact, human-readable string describing this Selector instance; the representation includes the concrete class name, the stored query expression, and a shortened preview of the selector's data. The call does not modify the Selector.

## Description:
This method produces the textual representation used by repr() and str() and is used implicitly by:
- builtin repr() and str() calls;
- interactive shells, debuggers, and REPLs when rendering the object;
- logging or formatting operations that coerce the object to a string.

It is also intentionally assigned to __repr__ at the class level so both repr() and str() yield the same output.

Typical usage occurs during debugging or diagnostics after selection operations (xpath, css, jmespath, re, etc.) when a developer or logging system inspects Selector instances.

Why this is a separate method:
- Centralizes presentation logic (class name, stored query, data preview) so that all external inspections render consistently.
- Keeps truncation/presentation concerns (via shorten) out of selection logic.
- Provides a lightweight, readable preview that avoids dumping very large payloads in logs or REPL output.

## Args:
None.

## Returns:
str
- Returns a string formatted as: "<{ClassName} query={query!r} data={data}>"
  - {ClassName}: type(self).__name__, the runtime class name (e.g., "Selector").
  - {query!r}: the repr() of self._expr (will display 'None' if no expression was provided).
  - {data}: repr(shorten(self.get(), width=40)) — a literal-style Python representation of the shortened value returned by self.get().
- Possible values:
  - If self._expr is None: query=None appears in the output.
  - If self.get() yields a long string: data contains a truncated preview (at most 40 characters, with suffix when truncated).
  - If self.get() yields a sequence (e.g., list, tuple): shorten may return a sliced sequence; repr(...) will serialize that sequence into the data field.

## Raises:
TypeError
- Condition: If the value returned by self.get() does not support the operations used by utils.shorten (specifically, if it lacks a length (len(value)) or does not support slicing with a slice object), shorten will raise a TypeError which this method propagates.
  - Typical examples that trigger this: certain custom objects without __len__ or built-ins that cannot be sliced (e.g., plain dict objects cannot be sliced and will cause a TypeError when shorten attempts slicing).
ValueError
- Condition: shorten can raise ValueError when called with a negative width. This implementation always calls shorten with width=40, so this ValueError cannot occur here under the current code.

## State Changes:
Attributes READ:
- self._expr (included verbatim via repr in the returned string)
- self.root, self.type, self._text (indirectly read by self.get(), which the method calls)

Attributes WRITTEN:
- None. The method performs only read-only operations and does not mutate self.

## Constraints:
Preconditions:
- The Selector should be in a valid state such that self.get() can be safely called; callers should be aware that JSON Selectors may have non-string roots (lists, dicts, etc.), which can affect how shorten behaves.
- No requirement that self._expr be present; None is allowed and will be displayed as such.

Postconditions:
- The Selector remains unchanged.
- On successful return, a single string conforming to the described format is produced.

## Side Effects:
- No I/O, network, or external side effects.
- Only performs read-only inspection of the Selector and calls pure helper functions (shorten and repr). These calls may allocate small temporary objects (strings, lists) but do not change external state.

