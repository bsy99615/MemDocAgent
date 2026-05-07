# `csstranslator.py`

## `parsel.csstranslator.XPathExpr` · *class*

*No documentation generated.*

### `parsel.csstranslator.XPathExpr.from_xpath` · *method*

## Summary:
Construct and return a new instance of this XPathExpr subclass by copying path, element, and condition from an existing OriginalXPathExpr and initializing the instance's textnode and attribute flags.

## Description:
- This is a classmethod (invoked on the class) that wraps an existing OriginalXPathExpr into an instance of cls while attaching two additional flags (textnode and attribute) supported by this subclass.
- Known callers and invocation context:
    - No callers are defined within this module. The method is intended as a utility for translation pipelines or calling code that needs to convert or wrap an OriginalXPathExpr into this XPathExpr subclass in order to record whether the expression should select text nodes or a specific attribute.
- Rationale for being a separate method:
    - Centralizes and documents the conversion/wrapping behavior (copying core expression fields and setting two subclass-specific flags) so callers do not duplicate construction and assignment logic.
    - Ensures consistent initialization of the subclass instance regardless of call site.

## Args:
    cls (type): The class on which the method is called. Expected to accept keyword arguments path, element, and condition in its constructor.
    xpath (OriginalXPathExpr): Source expression to copy. Must expose attributes .path, .element, and .condition.
    textnode (bool, optional): If True, the returned instance will be marked to represent a text() node. Defaults to False.
    attribute (Optional[str], optional): If provided, the returned instance will be marked to select the named attribute (e.g., "href"). Defaults to None.

## Returns:
    Self: A newly allocated instance of cls with the following state:
        - .path == xpath.path
        - .element == xpath.element
        - .condition == xpath.condition
        - .textnode == textnode (boolean)
        - .attribute == attribute (string or None)

    Edge-case returns:
        - Always returns a newly constructed instance; never returns the original xpath object.
        - If attribute is the empty string (""), that empty string is stored on the returned instance (no validation is performed).

## Raises:
    - AttributeError: If the provided xpath does not have any of the attributes .path, .element, or .condition (accessing them will raise AttributeError).
    - Any exception raised by cls(...) during construction (for example TypeError or ValueError) will propagate from this method unchanged. This method does not catch constructor exceptions.

## State Changes:
- Attributes READ (from the argument):
    - xpath.path
    - xpath.element
    - xpath.condition
- Attributes WRITTEN (on the returned instance):
    - instance.textnode is assigned the provided textnode value
    - instance.attribute is assigned the provided attribute value

## Constraints:
- Preconditions:
    - xpath must be an object compatible with OriginalXPathExpr exposing .path, .element, and .condition.
    - cls must be callable and accept the keyword arguments path, element, and condition (i.e., cls(path=..., element=..., condition=...)).

- Postconditions:
    - The returned object is an instance of cls with path/element/condition copied from xpath and textnode/attribute set as specified.
    - The original xpath argument is unmodified.

## Side Effects:
    - No I/O, no network calls, and no mutation of external global state.
    - Side effect limited to allocating a new instance of cls and setting two attributes on that new instance.

## Example:
    # Given an OriginalXPathExpr-like object named xpath:
    expr = XPathExpr.from_xpath(xpath, textnode=True, attribute="href")
    # Result: expr is a new XPathExpr instance with copied path/element/condition
    #         and expr.textnode == True, expr.attribute == "href"

### `parsel.csstranslator.XPathExpr.__str__` · *method*

## Summary:
Return the string form of the XPath expression by taking the superclass-produced base path and applying precise, deterministic post-processing to represent text-node and attribute selectors. The method does not modify the object's state.

## Description:
This method serializes the XPathExpr to a text XPath string. It first calls the superclass stringifier to obtain a base path and then applies two sequential post-processing steps:
1. Text-node handling (applied if self.textnode is truthy)
2. Attribute handling (applied if self.attribute is not None)

Known callers and lifecycle stage:
- Called whenever the XPathExpr is converted to a string, for example via str(xpath_expr) or by translator components that emit final XPath expressions after translating CSS selectors. This typically happens at the final stage of CSS→XPath translation before the expression is returned to users or passed to an XPath engine.
- The method is a dedicated serializer because the superclass provides a generic element path; this method centralizes the small, well-defined textual adjustments for text() and attribute access rather than embedding them in translator logic.

Why separate:
- Keeps formatting/serialization concerns isolated from expression construction logic in the superclass and translator code.
- Ensures consistent string output for text and attribute selectors from a single override.

## Args:
None.

## Returns:
str: The final XPath expression string after transformations. Possible shapes:
- Unchanged base path (when neither textnode nor attribute apply)
- "text()" exactly (when base path == "*" and textnode is True)
- base_without_last_3_chars + "text()" (when base endswith "::*/*" and textnode is True)
- base + "/text()" (when textnode is True and neither of the two special cases above)
- If attribute is set, the method appends "/@<attribute>" to the current path, but may first trim characters if the path ends with "::*/*".

Concrete transformation rules (applied in this order):
1. Let path = super().__str__() (must be a str).
2. If self.textnode is truthy:
    a. If path == "*" then path := "text()"
    b. Else if path.endswith("::*/*") then path := path[:-3] + "text()"
       - path[:-3] removes the last three characters of the base path and then "text()" is concatenated.
    c. Else path := path + "/text()"
3. If self.attribute is not None (assumed a string):
    a. If path.endswith("::*/*") then path := path[:-2]
       - path[:-2] removes the last two characters of the current path.
    b. Append "/@{self.attribute}" to path (string interpolation with the exact attribute name).
4. Return path.

Examples:
- Base path "*" and textnode=True, attribute=None → "text()"
- Base path "div" and textnode=True, attribute=None → "div/text()"
- Base path "div::*/*" and textnode=True, attribute=None → "div::*text()"
- Base path "div" and attribute="href" → "div/@href"
- Base path "div::*/*" and attribute="id" → after trimming last 2 chars then append → (base_without_last2) + "/@id"

Edge-case note:
- The method performs exact string slicing with fixed offsets ([-3], [-2]) as above. It does not attempt to parse XPath grammatically; it performs literal suffix checks and removals.

## Raises:
- No explicit raises in this method. Any exception raised by super().__str__() (for example if the superclass implementation raises) will propagate.

## State Changes:
Attributes READ:
    - self.textnode (truthy/falsy check)
    - self.attribute (checked for None and interpolated)
Attributes WRITTEN:
    - None. This method does not mutate self or any external object.

## Constraints:
Preconditions:
    - super().__str__() must return a str (the base XPath path).
    - self.attribute must be either None or a str (the code assumes string interpolation is meaningful).
    - self.textnode should be interpretable as a boolean flag.

Postconditions:
    - self remains unchanged.
    - The returned value is a str representing the XPath with any requested text() or attribute access applied per the rules above.

## Side Effects:
    - None. No I/O, no mutation of external state, and no external service interaction.

### `parsel.csstranslator.XPathExpr.join` · *method*

## Summary:
Combines another XPath expression into this one using a combiner token, updates this instance's textnode flag and attribute name to match the other expression, and returns this instance.

## Description:
This method performs two responsibilities:
1. Delegates the structural combination of XPath expressions to the superclass implementation (via super().join), which merges the underlying path/element/condition state.
2. Copies subclass-specific metadata (textnode flag and attribute name) from the other expression onto this instance so that these properties are preserved after the join.

Known callers and lifecycle:
- No direct call sites were found in the current repository snapshot. Conceptually, this method is intended to be invoked when two XPathExpr instances (subexpressions) need to be combined as part of building a full XPath expression (for example, while translating or composing selectors).
- It belongs in the expression-composition stage of XPath/CSS translation where smaller expression fragments are merged into larger ones.

Why this is a separate method:
- The superclass join handles the base representation (path/element/condition). Subclass-specific attributes (textnode and attribute) must be propagated after that merge; keeping that logic here avoids duplicating superclass behavior and keeps metadata copying localized to the subclass.

## Args:
    self (Self): Instance being modified (implicit).
    combiner (str): Token or operator passed to the superclass join (e.g., a string denoting how paths are combined). The method does not validate or interpret this string itself; it merely forwards it to super().join.
    other (OriginalXPathExpr): The expression to join into self. Must be an instance of parsel.csstranslator.XPathExpr (or a subclass).
    *args (Any): Additional positional arguments forwarded to super().join.
    **kwargs (Any): Additional keyword arguments forwarded to super().join.

## Returns:
    Self: Returns the same self instance after modification. The object returned is the original instance (mutated in place), not a newly allocated object.

## Raises:
    ValueError: Raised if other is not an instance of parsel.csstranslator.XPathExpr (or its descendants). Exact message:
        "Expressions of type {__name__}.XPathExpr can ony join expressions of the same type (or its descendants), got {type(other)}"
    (The message is produced verbatim by the implementation; note the spelling "ony" appears in the original message.)

## State Changes:
Attributes READ:
    other.textnode
    other.attribute

Attributes WRITTEN:
    self.textnode  (set to other.textnode)
    self.attribute (set to other.attribute)

Additional note:
    The call to super().join(combiner, other, *args, **kwargs) may also read and/or modify inherited internal state on self (for example: path, element, condition), depending on the superclass implementation.

## Constraints:
Preconditions:
    - other must be an instance of parsel.csstranslator.XPathExpr (or subclass); otherwise the method raises the ValueError above.
    - self must be a valid, initialized XPathExpr instance.
    - combiner must be a string (the method forwards it to the superclass without additional checks).

Postconditions:
    - After successful return, self.textnode is equal to other.textnode.
    - After successful return, self.attribute is equal to other.attribute.
    - The structural combination performed by super().join has been applied to self (so inherited path/element/condition state may have changed).
    - The method returns self.

## Side Effects:
    - Mutates self in-place (updates textnode and attribute, and possibly other inherited state via super().join).
    - Does not perform I/O or external service calls.
    - Does not mutate other (only reads other.textnode and other.attribute).

## `parsel.csstranslator.TranslatorProtocol` · *class*

## Summary:
A structural typing Protocol that specifies the minimal pure-conversion interface required for objects that translate CSS selectors into XPath: produce an XPath expression object from a parsed Element, and produce an XPath string from a CSS selector string.

## Description:
TranslatorProtocol is a lightweight abstraction used to accept any cssselect-style translator implementation (for example, cssselect.GenericTranslator or cssselect.HTMLTranslator) in a type-safe manner. It exists so callers can depend only on two conversion operations without coupling to concrete translator implementations.

Scenarios for instantiation:
- Create a concrete translator when you need to convert user-supplied CSS selectors into XPath (e.g., translator = GenericTranslator()) and pass it to consumer code typed against TranslatorProtocol.
- Use in factory functions that choose between HTMLTranslator and GenericTranslator at runtime and return a value typed as TranslatorProtocol.

Responsibility boundary:
- This Protocol requires only conversion behavior; it does not mandate any attributes, caching policy, or lifecycle management. It intentionally omits implementation details so different translators (stateless or cached) can conform.

## State:
The Protocol declares no required attributes. Implementations may be either stateless or maintain internal caches; however, the Protocol imposes the following expectations:

- Methods
    - xpath_element(selector: Element) -> OriginalXPathExpr
        - selector: cssselect.parser.Element — a parsed representation of a single element-level CSS selector.
        - Returns: OriginalXPathExpr — an opaque, translator-native XPath expression object. In many concrete implementations this will be an instance of cssselect.xpath.XPathExpr, but callers should treat this type opaquely unless they know the concrete translator.
        - Constraints/Invariants:
            - Must not mutate the provided selector object.
            - Must return an object that accurately encodes the equivalent XPath semantics of the selector.
    - css_to_xpath(css: str, prefix: str = ...) -> str
        - css: string containing a CSS selector to convert.
        - prefix: optional string applied by the implementation to the generated XPath (e.g., a node-prefix like ".//"). The Protocol signature uses an ellipsis default to indicate an implementation-defined default; callers who require a specific prefix should pass it explicitly.
        - Returns: a str containing the XPath expression equivalent to the css input.
        - Constraints/Invariants:
            - Must not perform I/O (file, network, or external side effects).
            - Must not mutate the input css string or any external state visible to the caller.
            - Should be a pure conversion: same inputs must produce equivalent outputs.

Class invariants (for implementers):
- Converting the same css (and same prefix) must produce semantically equivalent XPath results (deterministic behavior).
- No I/O or external side effects should occur inside these conversion methods.

## Lifecycle:
Creation:
- The Protocol itself is not constructed. Instantiate a concrete implementation instead:
    - translator = GenericTranslator()
    - translator = HTMLTranslator()
- Concrete constructors may accept their own parameters; consult those constructors for details.

Usage:
- No required ordering of calls. Typical usage patterns:
    - Direct conversion from CSS string to XPath string:
        xpath = translator.css_to_xpath("div > a", prefix=".//")
    - Working at AST level:
        xpath_obj = translator.xpath_element(parsed_element)
        # then inspect or compose xpath_obj according to the concrete translator API
- Methods are intended to be pure converters; callers can call them repeatedly without expecting side effects.

Destruction:
- No cleanup or explicit close() is mandated by this Protocol. Follow concrete implementation docs if any cleanup is required by a specific translator.

## Method Map:
graph LR
    Caller --> Translator[TranslatorProtocol]
    Translator --> XElem[xpath_element(selector: Element) -> OriginalXPathExpr]
    Translator --> C2X[css_to_xpath(css: str, prefix: str = ...) -> str]
    XElem --> UseXPathObj[Use or compose OriginalXPathExpr as needed]
    C2X --> UseXPathStr[Use XPath string directly]

Notes:
- At the Protocol level, the two methods are independent entry points; concrete implementations may internally share parsing or caching helpers.

## Raises:
- The Protocol itself does not raise specific exceptions.
- Concrete implementations may raise cssselect.xpath.ExpressionError when given invalid or unsupported selectors; callers should be prepared to catch ExpressionError when converting untrusted input.
- Implementations must not perform operations that trigger I/O-related exceptions (e.g., network or file errors) as a side effect of these methods.

## Example:
- Typical, side-effect-free usage with a concrete translator:

    from cssselect import HTMLTranslator
    from cssselect.xpath import ExpressionError

    translator = HTMLTranslator()  # a concrete implementation of TranslatorProtocol

    try:
        # Pure conversion: no I/O, no mutation of inputs or translator state expected
        xpath_string = translator.css_to_xpath("div > a.some-class", prefix=".//")
    except ExpressionError as exc:
        # Handle invalid selector provided by the user
        raise

    # Working at the AST level (if you have a parsed Element node)
    # parsed_element = ...  # obtain via cssselect.parser.parse or other means
    # xpath_obj = translator.xpath_element(parsed_element)
    # Use xpath_obj according to the concrete translator's API; treat it as an opaque XPath expression object.

Implementation notes for reimplementation:
- Provide two methods with the exact signatures above and honor the purity constraints (no I/O, no mutation of inputs).
- css_to_xpath must return a string (str) representing an XPath equivalent to the CSS selector.
- xpath_element must accept a cssselect.parser.Element and return a translator-native XPath expression object (opaque to callers).

### `parsel.csstranslator.TranslatorProtocol.xpath_element` · *method*

## Summary:
Translate a cssselect.parser.Element into an OriginalXPathExpr representing the equivalent XPath fragment; this operation is a pure translation (no mutation of the TranslatorProtocol instance is required).

## Description:
This method is an abstract translator operation that converts a parsed CSS Element node into the XPath fragment that selects the same nodes. Known caller: the TranslatorProtocol.css_to_xpath method (same protocol) uses element-level translators when constructing a complete XPath from a parsed CSS selector. Keeping element translation as its own method enables different translator implementations (e.g., HTML-specific vs. generic translators) to override element handling independently, and allows implementations to introduce element-level caching or specialized handling without changing higher-level composition logic.

Why separate:
- Element translation has distinct responsibilities (tag name, namespace, attribute selectors tied to the element, element-level pseudo-classes) which make it appropriate to isolate for clarity and override.
- It enables reuse by other translation steps that need equivalent fragment composition.

## Args:
    selector (cssselect.parser.Element): The cssselect parsed Element node to translate. Must be an instance produced by cssselect.parser and not None.

## Returns:
    OriginalXPathExpr: A module-level alias representing the XPath fragment for the provided selector. Implementations should return an object acceptable to the rest of the translation pipeline; typical, compatible return types (consistent with available imports) include instances compatible with cssselect.xpath.XPathExpr or plain XPath string fragments. Callers must treat the returned value as an opaque XPath fragment suitable for composition into a full XPath expression.

Edge-case return values:
- Implementations should not return None. If translation is impossible, raise ExpressionError (see Raises).
- If the element corresponds to an empty/no-op selector (rare), return the canonical empty-fragment representation defined by the concrete translator (documented by that implementation).

## Raises:
    cssselect.xpath.ExpressionError: When the provided selector contains constructs that cannot be expressed as an XPath fragment (for example, unsupported pseudo-elements or functions, invalid function arguments on the element, or other element-level translation failures). Implementations may also raise other implementation-specific exceptions for internal errors, but ExpressionError is the canonical error for expression-translation problems.

## State Changes:
    Attributes READ:
        - None required by the protocol. Implementations may read configuration fields (e.g., HTML mode flags) if present on the translator, but this is implementation-specific and must be documented by the concrete translator.
    Attributes WRITTEN:
        - None required by the protocol. The method is expected to be side-effect free with respect to self.

## Constraints:
    Preconditions:
        - selector is a valid cssselect.parser.Element instance (not None).
        - The translator instance should be configured appropriately before calling (for example, an HTML-specific translator may expect HTML mode to be set).
    Postconditions:
        - A non-None OriginalXPathExpr is returned that, when composed into the rest of the XPath produced by css_to_xpath, selects the same nodes described by selector (modulo translator expressiveness limits).
        - No mutation of TranslatorProtocol instance state is implied by the protocol.

## Side Effects:
    - The protocol mandates no I/O, network access, or mutation of external objects. Concrete implementations must document any deviation from this constraint. The canonical behavior is pure computation producing an XPath fragment.

## Implementation notes for implementers:
    - Use cssselect.xpath.ExpressionError to signal unsupported constructs; it is imported in this module and is the expected error type for expression translation problems.
    - Because cssselect.xpath.XPathExpr is imported at module level, returning instances compatible with that type will interoperate well with other cssselect helpers. If returning plain strings, ensure the rest of your translator composes them correctly.
    - Document any internal invariants of the concrete translator (e.g., namespace handling, HTML normalization) so callers know the semantics of the produced fragment.

## Usage example (conceptual):
    - css_to_xpath parses a selector into AST nodes and, for each Element node, calls xpath_element(self, element) to obtain an XPath fragment; those fragments are then concatenated or combined into the final XPath expression. This method should therefore return a fragment that is safe to compose by the caller.

### `parsel.csstranslator.TranslatorProtocol.css_to_xpath` · *method*

## Summary:
Translate a CSS selector string into an XPath expression string; this method defines the translator contract and does not itself implement the translation logic.

## Description:
This is an abstract/contract method on the TranslatorProtocol. Concrete translator classes implement this method to convert a CSS selector into an XPath expression (often delegating to the cssselect library). It is typically invoked by higher-level selection or query code when a CSS selector must be executed as an XPath query — for example, during selector compilation, element selection, or when a user supplies a CSS selector to an API that internally uses XPath.

Known callers and lifecycle stage:
- Selector and query utilities that accept CSS input and run selections against an XML/HTML document.
- Selector compilation phases where CSS is converted once to XPath before repeated evaluation.
- User code calling library APIs that accept CSS selectors and rely on an internal translator.

Why this is a separate method:
- Separates the translation contract from specific implementations (allows multiple translator implementations: HTML-specific, generic, or custom).
- Centralizes responsibilities such as handling the optional prefix and error propagation.
- Permits implementations to apply caching, instrumentation, or different translation backends without changing caller code.

## Args:
    css (str):
        The CSS selector string to translate. Must be a valid CSS selector as accepted by the chosen translation backend.
    prefix (str):
        An XPath prefix string that must be prepended to the produced expression. Typical consumers pass "descendant-or-self::" so the returned XPath selects the context node and its descendants; passing an empty string returns a raw XPath expression. Implementations MAY choose the default prefix "descendant-or-self::" if none is provided.

## Returns:
    str:
        A string containing the XPath expression that selects the same set of nodes as the provided CSS selector when used with the given prefix. Implementations must return a valid XPath string usable directly by the rest of the selection pipeline.

        Edge cases:
        - If the selector is syntactically valid but translates to an expression that selects nothing, return a valid XPath expression that evaluates to an empty node set (do not return None).
        - Do not return non-string sentinel values; always return a str on successful translation.

## Raises:
    cssselect.xpath.ExpressionError:
        When the css argument is syntactically invalid or contains constructs that cannot be translated into XPath by the implementation/backend, raise (or allow the underlying library to raise) ExpressionError with an explanatory message.

    TypeError:
        If callers pass values of incorrect types (e.g., css not being a str or prefix not being a str), implementations may raise TypeError. Implementations should validate the types or document that the underlying backend will raise TypeError.

    Any other exceptions from the chosen backend:
        Implementations may propagate other exceptions raised by the translation backend (parser errors, internal errors). Document and preserve those exceptions rather than swallowing them.

## State Changes:
Attributes READ:
    - None required by the protocol. Implementations may read translator-specific configuration attributes (e.g., flags that alter translation rules), but the protocol itself does not mandate any.

Attributes WRITTEN:
    - None required by the protocol. Implementations SHOULD NOT mutate translator state as a side-effect of translating a selector. Caching is allowed but must not change observable translator semantics.

## Constraints:
Preconditions:
    - self must be a translator instance implementing this protocol.
    - css must be a str containing a well-formed CSS selector according to the backend's grammar.
    - prefix must be a str (can be empty). If an implementation relies on a non-empty default prefix, callers that want the default should pass no prefix only if the concrete implementation documents that default.

Postconditions:
    - On successful return, the method produces a str that is a valid XPath expression representing the provided CSS selection semantics with the supplied prefix applied.
    - Implementations that apply caching may have inserted a cache entry keyed by (self, css, prefix) after the call; this is an internal implementation detail and must not affect observable behavior other than performance.

## Side Effects:
    - Implementations may use in-memory caching (e.g., lru_cache) to speed repeated translations. Caching increases process memory usage proportional to unique input tuples.
    - No I/O, network calls, or modification of input objects are required by the protocol. If a specific implementation performs I/O (e.g., loading dynamic configuration), it must document that behavior.

## Implementation guidance for reimplementing this method:
    - Validate argument types and normalize prefix (treat None or missing prefix according to the chosen default).
    - Parse the CSS selector using a reliable parser (for example, reuse cssselect.parser utilities) and translate the parse tree into an XPath string. Alternatively, delegate to an upstream translator implementation (e.g., cssselect.HTMLTranslator or cssselect.GenericTranslator).
    - Ensure translation preserves semantics for element/tag selectors, attribute selectors, combinators, pseudo-classes/pseudo-elements that are translatable, and functional pseudo-classes where supported. For constructs that cannot be represented in XPath, raise ExpressionError.
    - Return a UTF-8-safe str (Python str) containing the XPath expression; callers will pass this string to XPath evaluation routines.
    - Prefer raising backend exceptions rather than returning error codes; callers generally expect exceptions for invalid input.

## `parsel.csstranslator.TranslatorMixin` · *class*

## Summary:
A mixin that adapts cssselect translator behavior to consistently produce and manipulate cssselect.xpath.XPathExpr objects and dispatch pseudo-element handlers by naming convention.

## Description:
TranslatorMixin centralizes common translation behaviors used when converting parsed CSS selector AST nodes into XPath expression representations. It is intended to be used as a mixin in a concrete translator class that provides a base xpath_element implementation (for example, a subclass combining this mixin with cssselect.GenericTranslator or cssselect.HTMLTranslator). The mixin:

- Normalizes element translation results to cssselect.xpath.XPathExpr instances.
- Provides a generic dispatcher for both functional and simple pseudo-elements that resolves handler method names on the translator instance and invokes them.
- Implements canonical translations for two pseudo-elements:
  * ::attr(name) as a functional pseudo-element, validating argument types and returning an XPathExpr configured to select the named attribute.
  * ::text as a simple pseudo-element, returning an XPathExpr configured to select text nodes.

Use cases:
- Combine with an existing cssselect translator implementation to provide consistent XPathExpr wrapping and pseudo-element handling across the codebase.
- Subclass or extend by adding handler methods named according to the mixin's naming convention to support additional pseudo-elements.

Known caller pattern:
- Higher-level CSS→XPath translation pipeline that visits parsed selector AST nodes and invokes element and pseudo-element translators. The translator object implementing this mixin is expected to expose methods required by cssselect (e.g., xpath_element on a superclass) and be used via its css_to_xpath entry point or equivalent.

## State:
This mixin is stateless: it does not define or mutate instance attributes. Instead, it relies on the translator instance's MRO to provide a working xpath_element implementation and on external helper type XPathExpr.

Important conceptual types and required object shape (OriginalXPathExpr):
- OriginalXPathExpr (informal contract):
  - Any object accepted by XPathExpr.from_xpath(...) from cssselect.xpath.
  - Practically must expose (or be convertible to) attributes typically used by XPathExpr.from_xpath: .path, .element, .condition (the exact attribute set depends on the cssselect.xpath implementation).
  - Methods/attributes are read only; the mixin never mutates this object.

Attributes (none on this mixin):
- No instance attributes defined or required by TranslatorMixin.
- Translator implementations may add attributes; this mixin neither reads nor writes them.

Class invariants:
- The translator class using this mixin must have a working parent implementation of xpath_element (accessible via super().xpath_element).
- Handler methods referenced by the dispatcher must exist on the translator instance and conform to the expected signatures described below.
- XPathExpr.from_xpath must be available from cssselect.xpath and produce objects that represent XPath expressions with optional flags such as attribute and textnode.

## Lifecycle:
Creation:
- No constructor or initialization needed from the mixin itself.
- To use, create a translator class whose MRO includes TranslatorMixin before a base translator that implements element-to-XPath conversion (e.g., GenericTranslator or HTMLTranslator). Example pattern (descriptive): create a translator type that composes TranslatorMixin with an existing cssselect translator and instantiate it.

Usage (typical sequence):
1. The external translation pipeline invokes xpath_element(selector) when translating an Element AST node:
   - TranslatorMixin will call the superclass xpath_element(selector) and normalize its result via XPathExpr.from_xpath(...).
2. When encountering a pseudo-element in the AST, the pipeline calls xpath_pseudo_element(xpath, pseudo_element):
   - TranslatorMixin will dispatch to a handler method named by convention (see Method Map).
   - The handler returns an XPath expression object (OriginalXPathExpr or XPathExpr) which the caller uses or returns.
3. Built-in pseudo-element handlers in the mixin:
   - xpath_attr_functional_pseudo_element(xpath, function): called for ::attr(name) functional pseudo-element.
   - xpath_text_simple_pseudo_element(xpath): called for ::text simple pseudo-element.
4. Subclasses should implement additional handler methods following the naming convention to support more pseudo-elements.

Destruction / cleanup:
- No cleanup responsibilities. The mixin holds no resources and does not implement context-manager or close semantics.

## Method Map:
graph LR
    A[xpath_element(selector)] --> B[super().xpath_element(selector)]
    B --> C[XPathExpr.from_xpath(result_of_super)]
    D[xpath_pseudo_element(xpath,pseudo_element)] -->|Functional| E[call handler xpath_{name}_functional_pseudo_element(xpath,function)]
    D -->|Simple| F[call handler xpath_{name}_simple_pseudo_element(xpath)]
    E --> G[xpath_attr_functional_pseudo_element(xpath,function) validate args -> XPathExpr.from_xpath(xpath, attribute=...)]
    F --> H[xpath_text_simple_pseudo_element(xpath) -> XPathExpr.from_xpath(xpath, textnode=True)]

(Interpretation: xpath_element delegates to the superclass implementation then wraps via XPathExpr.from_xpath. xpath_pseudo_element resolves handler names and calls them; two supplied handlers map to attr and text behavior.)

Handler naming conventions and expected signatures:
- Functional pseudo-elements:
  - Handler name format: xpath_{pseudo_name_with_dashes_replaced_by_underscores}_functional_pseudo_element
  - Expected signature: handler(self, xpath: OriginalXPathExpr, function: FunctionalPseudoElement) -> OriginalXPathExpr or XPathExpr
- Simple pseudo-elements:
  - Handler name format: xpath_{pseudo_name_with_dashes_replaced_by_underscores}_simple_pseudo_element
  - Expected signature: handler(self, xpath: OriginalXPathExpr) -> OriginalXPathExpr or XPathExpr

Return conventions:
- All translator methods in this mixin return either:
  - An instance compatible with cssselect.xpath.XPathExpr (preferred), or
  - A value acceptable to XPathExpr.from_xpath when the caller will immediately normalize it.
- The mixin itself normalizes element translations to XPathExpr but returns handler results from xpath_pseudo_element unchanged; handlers may return either OriginalXPathExpr or already-wrapped XPathExpr.

## Method details (behavioral contract)

- xpath_element(self: TranslatorProtocol, selector: Element) -> XPathExpr
  - Purpose: Normalize the superclass element translation result into an XPathExpr.
  - Behavior:
    - Call super().xpath_element(selector).
    - Pass the result to XPathExpr.from_xpath(...) and return that XPathExpr instance.
  - Preconditions:
    - The translator's superclass must implement xpath_element.
    - selector is a cssselect.parser.Element instance.
  - Postconditions:
    - Returns an XPathExpr. No side effects on self.

- xpath_pseudo_element(self, xpath: OriginalXPathExpr, pseudo_element: PseudoElement) -> OriginalXPathExpr
  - Purpose: Dynamically dispatch the appropriate pseudo-element handler based on pseudo_element type and name.
  - Behavior:
    - If pseudo_element is an instance of FunctionalPseudoElement:
      - Build method_name = "xpath_{pseudo_element.name.replace('-', '_')}_functional_pseudo_element"
      - Resolve method = getattr(self, method_name, None)
      - If method is None: raise ExpressionError("The functional pseudo-element ::{pseudo_element.name}() is unknown")
      - Call method(xpath, pseudo_element) and return its result
    - Else:
      - Build method_name = "xpath_{pseudo_element.replace('-', '_')}_simple_pseudo_element"
      - Resolve method = getattr(self, method_name, None)
      - If method is None: raise ExpressionError("The pseudo-element ::{pseudo_element} is unknown")
      - Call method(xpath) and return its result
  - Preconditions:
    - For functional pseudo-elements: pseudo_element must expose .name and be an instance of FunctionalPseudoElement.
    - For simple pseudo-elements: pseudo_element must support replace('-', '_') (typically a string).
  - Errors:
    - Raises ExpressionError for missing handler methods with exact messages above.
    - AttributeError may propagate if pseudo_element lacks expected attributes.

- xpath_attr_functional_pseudo_element(self, xpath: OriginalXPathExpr, function: FunctionalPseudoElement) -> XPathExpr
  - Purpose: Implement ::attr(name) functional pseudo-element translation to an XPathExpr selecting the named attribute.
  - Behavior:
    - Validate that function.argument_types() returns exactly ["STRING"] or ["IDENT"].
      - If not, raise ExpressionError with message: "Expected a single string or ident for ::attr(), got {function.arguments!r}"
    - Extract the attribute name from function.arguments[0].value.
    - Return XPathExpr.from_xpath(xpath, attribute=attribute_name)
  - Preconditions:
    - function.arguments must contain at least one argument when argument_types() is ["STRING"] or ["IDENT"].
    - The first argument token must expose .value (string).
    - xpath must be acceptable to XPathExpr.from_xpath (see State).
  - Postconditions:
    - Returns a new XPathExpr with attribute set to the provided name. Original xpath is not mutated.
  - Errors:
    - ExpressionError for invalid argument_types.
    - AttributeError or other exceptions may propagate if argument tokens or xpath lack expected attributes.

- xpath_text_simple_pseudo_element(self, xpath: OriginalXPathExpr) -> XPathExpr
  - Purpose: Implement ::text simple pseudo-element translation, returning an XPathExpr that selects text nodes.
  - Behavior:
    - Return XPathExpr.from_xpath(xpath, textnode=True)
  - Preconditions:
    - xpath must be acceptable to XPathExpr.from_xpath.
  - Postconditions:
    - Returns a new XPathExpr configured to select text nodes for the nodes matched by xpath.
  - Errors:
    - Any exceptions raised by XPathExpr.from_xpath propagate.

## Raises:
- ExpressionError (from cssselect.xpath)
  - Raised by xpath_pseudo_element when a handler method is missing:
    - "The functional pseudo-element ::{name}() is unknown"
    - "The pseudo-element ::{name} is unknown"
  - Raised by xpath_attr_functional_pseudo_element if the argument types are not a single STRING or IDENT:
    - "Expected a single string or ident for ::attr(), got {function.arguments!r}"
- AttributeError / TypeError / ValueError
  - These may propagate from attribute access on function or xpath objects, or from XPathExpr.from_xpath constructor behavior. The mixin does not catch these.

## Example (descriptive usage):
- Prepare a translator type that composes this mixin with an existing cssselect translator implementation so that super().xpath_element is available.
- Instantiate the translator.
- To translate an element selector node:
  - Call xpath_element(selector). The result is an XPathExpr instance.
- To apply a pseudo-element:
  - For a parsed functional pseudo-element representing ::attr("href"), call xpath_pseudo_element(xpath_expr, functional_node). The mixin will call xpath_attr_functional_pseudo_element, validate arguments, and return an XPathExpr with attribute set to "href".
  - For a simple pseudo-element "text", call xpath_pseudo_element(xpath_expr, "text") (or the parser's PseudoElement). The mixin will call xpath_text_simple_pseudo_element and return an XPathExpr configured for text nodes.
- To support additional pseudo-elements, implement methods on the translator instance with names following the handler naming convention and compatible signatures.

Notes and implementation hints for reimplementers:
- The mixin relies on the cssselect library's XPathExpr.from_xpath factory to create normalized XPathExpr objects; ensure the factory accepts the combination of arguments used here (xpath, attribute=..., textnode=...).
- Maintain the naming convention precisely; the dispatcher composes handler method names at runtime using .replace('-', '_') on pseudo-element names.
- Keep the mixin stateless: do not introduce instance state unless required by new handlers; document and enforce any new invariants those handlers introduce.

### `parsel.csstranslator.TranslatorMixin.xpath_element` · *method*

## Summary:
Wraps the base-class element-to-XPath translation result and returns it as a cssselect.xpath.XPathExpr instance, leaving the TranslatorMixin object's state unchanged.

## Description:
This method is invoked as part of the CSS-to-XPath translation pipeline when an Element AST node (cssselect.parser.Element) must be converted into an XPath expression. Typical call sites are other translator routines that traverse or translate selector AST nodes (for example, higher-level translate/xpath methods that dispatch on node type). It delegates the actual element translation to the parent class implementation (via super().xpath_element) and ensures the returned value is normalized to an XPathExpr by calling XPathExpr.from_xpath.

This logic is factored out into its own method so that all element translations produced by subclasses or parent classes are consistently converted into the XPathExpr wrapper in one place. That centralization avoids duplicating conversion logic wherever element translations are produced and allows the rest of the TranslatorMixin methods to assume an XPathExpr return type.

## Args:
    selector (Element):
        A cssselect.parser.Element instance representing the element selector AST node to translate.
        This should be a parsed Element node coming from cssselect.parser.

## Returns:
    XPathExpr:
        A cssselect.xpath.XPathExpr instance representing the XPath expression for the provided element selector.
        The returned object is produced by XPathExpr.from_xpath(...) using the value returned by super().xpath_element(selector).
        If the parent implementation already returns an XPathExpr or a raw XPath string, this method normalizes it into an XPathExpr.

## Raises:
    Any exception raised by the delegated calls:
        - Exceptions raised by super().xpath_element(selector) are propagated unchanged.
        - Exceptions raised by XPathExpr.from_xpath(...) are propagated unchanged.
    (Examples include expression/translation errors thrown by the underlying cssselect implementation; this method does not catch or wrap them.)

## State Changes:
    Attributes READ:
        - None (the method does not access any self.<attr> attributes)
    Attributes WRITTEN:
        - None (the method does not modify any self.<attr> attributes)

## Constraints:
    Preconditions:
        - self must be an object whose MRO supplies a working xpath_element(selector) implementation (the method calls super().xpath_element).
        - selector must be a valid cssselect.parser.Element instance representing a syntactically valid element selector.
    Postconditions:
        - The method returns a valid XPathExpr instance constructed from the result of the parent implementation.
        - The TranslatorMixin instance is unchanged (no side-effecting state mutation).

## Side Effects:
    - None intrinsic to this method: no I/O, no network calls, and no mutation of external objects or self.
    - Any side effects originate from super().xpath_element(selector) or XPathExpr.from_xpath(...) if those routines have side effects; this method does not add additional side effects.

### `parsel.csstranslator.TranslatorMixin.xpath_pseudo_element` · *method*

## Summary:
Dispatches processing of a parsed CSS pseudo-element to a translator handler method on self and returns the handler's XPath expression result.

## Description:
This method implements dynamic dispatch for pseudo-elements encountered during CSS→XPath translation. It detects whether the provided pseudo_element is a FunctionalPseudoElement or not and builds a handler method name accordingly. It then looks up that handler on self and calls it, returning the handler's result.

Intended usage/context:
- Used when a translator needs to convert a parsed pseudo-element into an XPath expression fragment. The caller supplies an intermediate XPath expression (xpath) and the parsed pseudo_element; this method applies the pseudo-element-specific transformation by delegating to a handler method on the translator instance.

Why separate this logic:
- Centralizes the naming and lookup convention for pseudo-element handlers and enforces a consistent dispatch rule for functional vs. simple pseudo-elements instead of duplicating this lookup logic in multiple places.

## Args:
    xpath (OriginalXPathExpr):
        The incoming intermediate XPath expression passed to the pseudo-element handler. The method assigns the handler's return back to this variable and returns it.
    pseudo_element (PseudoElement):
        The parsed pseudo-element to handle.
        - If pseudo_element is an instance of FunctionalPseudoElement, the code uses pseudo_element.name to build the handler name.
        - Otherwise the code calls pseudo_element.replace('-', '_') to build the handler name; therefore the non-functional pseudo_element must provide a replace method (typically a string).

## Returns:
    OriginalXPathExpr:
        The value returned by the invoked handler method. The method assigns the handler's return to xpath and returns it unchanged.

## Raises:
    ExpressionError:
        - If pseudo_element is a FunctionalPseudoElement and no handler method named
          xpath_{pseudo_element.name.replace('-', '_')}_functional_pseudo_element
          exists on self, an ExpressionError is raised with this exact message:
            "The functional pseudo-element ::{pseudo_element.name}() is unknown"
        - If pseudo_element is not a FunctionalPseudoElement and no handler method named
          xpath_{pseudo_element.replace('-', '_')}_simple_pseudo_element
          exists on self, an ExpressionError is raised with this exact message:
            "The pseudo-element ::{pseudo_element} is unknown"
    AttributeError (possible at runtime):
        - If pseudo_element is not a FunctionalPseudoElement but lacks a replace attribute/method,
          calling pseudo_element.replace('-', '_') will raise AttributeError. This behavior follows
          directly from the use of replace in the code.

## State Changes:
Attributes READ:
    - The method performs dynamic attribute access on self via getattr(self, method_name, None),
      i.e., it reads a bound attribute (the handler method) whose name is derived from the pseudo-element.
Attributes WRITTEN:
    - None. The method does not assign to any self.<attribute> fields.

## Constraints:
Preconditions:
    - The caller must provide a valid xpath object appropriate for this translator's handlers.
    - For functional pseudo-elements: pseudo_element must be an instance of FunctionalPseudoElement and provide a .name attribute.
    - For simple pseudo-elements: pseudo_element must implement replace('-', '_') (e.g., be a string) so the handler name can be constructed.
    - The translator instance (self) must implement the handler method with the exact name produced by the naming convention, otherwise ExpressionError is raised.

Postconditions:
    - If a handler method is found and invoked, the method returns that handler's return value (an OriginalXPathExpr).
    - If no handler exists, the method raises ExpressionError and does not return a value.

Handler naming and invocation details (exact behavior in code):
    - If isinstance(pseudo_element, FunctionalPseudoElement) is True:
        * handler name = "xpath_{pseudo_element.name.replace('-', '_')}_functional_pseudo_element"
        * handler is retrieved via getattr(self, handler_name, None)
        * if handler is None -> raise ExpressionError with message:
            "The functional pseudo-element ::{pseudo_element.name}() is unknown"
        * else handler is called as handler(xpath, pseudo_element)
    - Else (non-functional pseudo-element):
        * handler name = "xpath_{pseudo_element.replace('-', '_')}_simple_pseudo_element"
        * handler is retrieved via getattr(self, handler_name, None)
        * if handler is None -> raise ExpressionError with message:
            "The pseudo-element ::{pseudo_element} is unknown"
        * else handler is called as handler(xpath)
    - In both cases, the return value from the handler call is assigned to xpath and then returned.

## Side Effects:
    - No direct I/O or external service calls are performed by this method itself.
    - The only side effects come from invoking the handler method on self; that handler may mutate translator state or perform I/O. Those effects are not performed by xpath_pseudo_element itself but may occur as a consequence of the handler's implementation.

### `parsel.csstranslator.TranslatorMixin.xpath_attr_functional_pseudo_element` · *method*

## Summary:
Validate and translate a CSS ::attr(...) functional pseudo-element into an XPathExpr that selects the named attribute; returns a new XPathExpr instance (does not modify self).

## Description:
This method is called during CSS-to-XPath translation when the translator encounters a functional pseudo-element of the form ::attr(name) (i.e., a functional pseudo-element that names an attribute to select). It performs argument validation for the ::attr() pseudo-element and then wraps the provided OriginalXPathExpr into an XPathExpr subclass instance that is marked to select the given attribute.

Known callers and context:
- Invoked by translation code in the TranslatorMixin implementation (the CSS -> XPath translation pipeline) when handling FunctionalPseudoElement nodes representing ::attr(...).
- Typical lifecycle stage: while converting a parsed CSS selector AST to an XPath expression, specifically at the step that maps pseudo-elements (functional pseudo-elements) to XPath constructs.

Why this is a separate method:
- Centralizes the validation and conversion logic for ::attr(...) so the translator can consistently enforce the allowed argument types and produce an XPathExpr with the attribute flag set.
- Keeps translator code modular and easier to test: argument checking and XPathExpr construction are focused in one place.

## Args:
    self: TranslatorMixin
        - The bound translator instance; not read or modified by this method.
    xpath (OriginalXPathExpr):
        - An expression object representing the XPath constructed so far that will be wrapped/converted.
        - Must expose attributes .path, .element, and .condition (as required by XPathExpr.from_xpath).
        - No mutation of this object occurs; it is only read.
    function (FunctionalPseudoElement):
        - A cssselect.parser FunctionalPseudoElement instance representing ::attr(...).
        - Expected to provide:
            * method argument_types() -> list[str] describing token kinds (e.g., "STRING", "IDENT")
            * attribute .arguments which is an indexable sequence of argument token objects
            * argument token objects exposing a .value attribute containing the argument string

## Returns:
    XPathExpr:
        - A newly constructed XPathExpr subclass instance produced by XPathExpr.from_xpath(...).
        - The returned instance is a wrapper of the provided xpath with the following guarantees:
            * .path, .element, .condition are copied from the supplied xpath
            * .attribute is set to the textual value of the first argument token (function.arguments[0].value)
            * .textnode remains at the default (textnode=False) because this method does not request textnode selection
        - The original xpath object is not modified; a fresh instance is returned.
        - If attribute is the empty string (""), that value is stored on the returned instance (no extra validation).

## Raises:
    ExpressionError:
        - Raised if function.argument_types() is not exactly either ["STRING"] or ["IDENT"].
        - Message formatted as: "Expected a single string or ident for ::attr(), got {function.arguments!r}"
    AttributeError:
        - Can arise if:
            * the supplied xpath object does not have .path, .element, or .condition (accessed by XPathExpr.from_xpath), or
            * the first argument token does not expose .value
        - These attribute access errors propagate unchanged.
    Any exception raised by XPathExpr.from_xpath (or the underlying cls(...) constructor):
        - e.g., TypeError, ValueError originating from constructing the XPathExpr subclass; these are not caught and will propagate.

## State Changes:
- Attributes READ (on self):
    - None (the method does not read any self.<attr> fields)
- Attributes WRITTEN (on self):
    - None (the method does not modify self)
- External object reads/writes:
    - Reads: xpath.path, xpath.element, xpath.condition (indirectly via XPathExpr.from_xpath)
    - Reads: function.argument_types(), function.arguments[0].value
    - Writes: constructs and returns a new XPathExpr instance whose .attribute and .textnode fields are set (writes occur on the new instance only)

## Constraints:
- Preconditions:
    - The function argument must represent exactly one identifier or one string token: function.argument_types() must return ["STRING"] or ["IDENT"]. If this is not true, the method raises ExpressionError and does not proceed.
    - xpath must be compatible with XPathExpr.from_xpath: it must expose .path, .element, and .condition attributes.
    - function.arguments must be non-empty when function.argument_types() returns ["STRING"] or ["IDENT"] (the code accesses function.arguments[0]).
    - The first argument token must expose .value (a string) representing the attribute name.
- Postconditions:
    - On successful return, a new XPathExpr instance is produced with .attribute equal to the provided argument string and .textnode left at its default (False).
    - No state on self is changed; the original xpath object remains unmodified.

## Side Effects:
    - Allocates and returns a new XPathExpr instance (no I/O or network operations).
    - May raise exceptions described above; no exceptions are swallowed.
    - No mutation of objects outside the newly created XPathExpr instance and no global side effects.

### `parsel.csstranslator.TranslatorMixin.xpath_text_simple_pseudo_element` · *method*

## Summary:
Return an XPathExpr representing the text-node view of the supplied XPath expression, causing subsequent selection to target text nodes of the matched elements.

## Description:
This method is invoked when the CSS-to-XPath translation pipeline encounters the simple pseudo-element ::text. Known caller:
- TranslatorMixin.xpath_pseudo_element — this method is looked up by name (xpath_text_simple_pseudo_element) and called for the simple pseudo-element "text".

Context/Lifecycle:
- Called during translation of a CSS selector that contains a ::text pseudo-element. The upstream translator constructs an initial XPath expression for the element portion of the selector and then this method adapts that expression so the resulting XPath selects text nodes rather than element nodes.
- It is implemented as a separate method to keep each pseudo-element's translation logic modular and discoverable by name (the xpath_pseudo_element lookup uses method naming conventions). Keeping this logic separated allows subclasses to override or extend behaviour for ::text without inlining the transformation into the general dispatcher.

## Args:
    xpath (OriginalXPathExpr):
        An XPath expression representation produced by the upstream translator. This is the "original" XPath expression that locates element nodes (or other nodes) to which the ::text pseudo-element should be applied. The object must be acceptable to XPathExpr.from_xpath.

## Returns:
    XPathExpr:
        A new XPathExpr constructed from the provided xpath with textnode mode enabled. The returned expression targets the text nodes that belong to the nodes matched by the input xpath (i.e., it represents the same location but selecting text nodes instead of the element nodes themselves).

## Raises:
    None explicitly raised by this method.
    Note: any exceptions raised by XPathExpr.from_xpath (for example if the provided xpath is invalid for that constructor) will propagate out of this method.

## State Changes:
    Attributes READ:
        - None (this method does not access any self.<attr> attributes)
    Attributes WRITTEN:
        - None (this method does not modify self)

## Constraints:
    Preconditions:
        - The caller must supply an xpath argument of the form expected by XPathExpr.from_xpath (OriginalXPathExpr). The method does not validate semantic correctness beyond what XPathExpr.from_xpath enforces.
        - The call site should represent that a ::text pseudo-element was present in the parsed CSS selector.

    Postconditions:
        - The returned XPathExpr will have been created via XPathExpr.from_xpath(..., textnode=True) and therefore will be configured to select text nodes associated with the original node set.
        - The method does not mutate the TranslatorMixin instance.

## Side Effects:
    - No I/O or external service calls.
    - No mutation of objects outside the returned XPathExpr and local execution context.

## `parsel.csstranslator.GenericTranslator` · *class*

## Summary:
A thin translator class that composes TranslatorMixin with the cssselect GenericTranslator implementation and adds an LRU cache around CSS→XPath conversions to reuse recent results.

## Description:
This class exists to provide a ready-to-use cssselect translator that:
- Gains the TranslatorMixin behavior for consistent XPathExpr normalization and pseudo-element dispatching, and
- Reuses results of css_to_xpath calls to speed up repeated translations of identical CSS selectors.

Typical scenarios for instantiation:
- Create an instance once (or a few instances) and call css_to_xpath repeatedly while parsing or querying HTML/XML.
- Use when the translation pipeline sees the same CSS selectors multiple times (e.g., libraries that repeatedly convert common selectors).

Motivation and responsibility boundary:
- Responsibility: forward all translation work to the underlying cssselect GenericTranslator (referred to here as OriginalGenericTranslator), but cache results to reduce repeated work.
- This class does not reimplement translation logic; it only provides caching and composes TranslatorMixin to ensure normalized pseudo-element and element behavior.
- It does not add or change the semantics of the underlying cssselect translator beyond caching and MRO composition.

Known callers/factories:
- Any higher-level code that needs to convert CSS selector strings to XPath strings and expects TranslatorMixin semantics (normalization to XPathExpr where applicable and pseudo-element handlers).
- Instantiation patterns follow the base cssselect GenericTranslator; TranslatorMixin adds no constructor parameters.

## State:
- Instance attributes: None defined by this class. The class itself does not introduce per-instance mutable state.
- Class-level / function-level state:
  - The css_to_xpath method is wrapped with functools.lru_cache(maxsize=256). This wrapper maintains an LRU cache of up to 256 entries.
- Cache key semantics and invariants:
  - Cache entries are keyed by the tuple of the bound method arguments: (self, css, prefix). Accordingly:
    - The cache distinguishes calls by the translator instance (self) as well as the css string and prefix string.
    - All cache key components must be hashable. By default, ordinary Python objects (instances of user-defined classes without a custom __eq__ that breaks hashing) are hashable, and str is hashable; if a translator instance is made unhashable by overriding __hash__/__eq__, caching will raise TypeError at use time.
  - The cache size is limited to 256 entries. Once capacity is reached, least-recently-used entries are evicted.
  - The cache is shared across all instances of this class in the sense that the wrapper object holding the cache lives on the class/function and uses self as part of the key.

## Lifecycle:
- Creation:
  - Instantiate the class using its constructor. This class does not define __init__; construction and any constructor parameters are those provided by the base cssselect GenericTranslator (OriginalGenericTranslator). The TranslatorMixin adds no constructor requirements.
- Typical usage sequence:
  1. Instantiate translator = GenericTranslator(...) (pass any args accepted by the underlying cssselect GenericTranslator if necessary).
  2. Call translator.css_to_xpath(css_string, prefix) to obtain an XPath string for a CSS selector.
     - On the first call for a given (self, css_string, prefix) tuple, translation is delegated to the superclass implementation.
     - The returned XPath string is stored in the LRU cache for subsequent identical calls.
  3. Repeat css_to_xpath with the same arguments to get a cached result (fast path).
- Ordering and required sequencing:
  - No special ordering of other methods is required before calling css_to_xpath. The TranslatorMixin expects the MRO to provide xpath_element and other required hooks; those are supplied by OriginalGenericTranslator in normal usage.
- Destruction / cleanup:
  - No explicit cleanup is required.
  - The lru_cache maintains in-memory entries until the interpreter exits or until the cache is cleared/evicted.
  - If desired, the cache can be inspected or cleared via the lru_cache wrapper attributes (available on the function object bound to the class). Access patterns for these introspection helpers depend on whether you reference the wrapper via the class or via the bound method (inspect GenericTranslator.css_to_xpath for the wrapper and its .cache_clear() / .cache_info() methods).

## Method Map:
graph LR
    Caller[Caller code] --> A[GenericTranslator.css_to_xpath(css, prefix)]
    A --> B{LRU cache hit?}
    B -- Yes --> C[Return cached XPath string]
    B -- No --> D[Call super().css_to_xpath(css, prefix)]
    D --> E[OriginalGenericTranslator (cssselect.GenericTranslator) computes XPath string]
    E --> F[Return XPath string to A]
    F --> G[Store (self,css,prefix)->result in LRU cache]
    G --> C[Return cached XPath string]

(Note: TranslatorMixin behavior affects element and pseudo-element handling at the MRO level; css_to_xpath here delegates to the superclass and benefits from any TranslatorMixin behavior earlier in the MRO.)

## Methods (public surface inherited/overridden):
- css_to_xpath(self, css: str, prefix: str = "descendant-or-self::") -> str
  - Purpose: Convert a CSS selector string to an XPath expression string, with caching to avoid repeated translations.
  - Behavior:
    - Keyed by (self, css, prefix) in an LRU cache of maxsize 256.
    - On cache miss, delegates to super().css_to_xpath(css, prefix) and caches the returned string.
    - Returns the XPath expression returned by the superclass.
  - Types:
    - css: str — a CSS selector string (must be hashable).
    - prefix: str — prefix string used by cssselect to build XPath (defaults to "descendant-or-self::").
    - return: str — XPath expression string produced by the base cssselect translator.
  - Edge constraints:
    - All arguments (including self) must be hashable to be used as cache keys. If they are not, the lru_cache wrapper will raise TypeError when attempting to cache.
    - The cache distinguishes different translator instances; using many distinct translator instances will consume cache entries keyed by their identities.
  - Side effects:
    - Populates/evicts entries in the LRU cache.
  - Observability:
    - Cache statistics and clearing can be performed via the lru_cache wrapper API on the wrapped function object (inspect GenericTranslator.css_to_xpath wrapper for .cache_info(), .cache_clear()).

## Raises:
- ExpressionError (from cssselect.xpath) — may be raised by the underlying cssselect implementation if the input CSS selector is syntactically or semantically invalid. This class does not catch or wrap that exception; it propagates as-is.
- TypeError — may be raised by functools.lru_cache if any cache key component (self, css, prefix) is unhashable. This is not raised by this class directly but by the cache wrapper during access.
- Any exceptions raised by the base-class constructor when instantiating this translator are possible during instantiation; this class does not add further __init__-specific exceptions.

## Example (illustrative usage narrative):
1. Create a translator instance (the constructor parameters, if any, follow the cssselect GenericTranslator base):
   - Instantiate the class in a long-lived component that will perform multiple translations.
2. Translate a CSS selector:
   - Call css_to_xpath("a[href^='http']") to obtain the corresponding XPath string. On first call for that selector/prefix, the result is computed and cached.
3. Reuse:
   - Subsequent calls with the same (translator instance, CSS string, prefix) return the cached XPath string quickly.
4. Inspect or clear cache (administrative):
   - Use the lru_cache wrapper's introspection/clearing helpers available on the wrapper function to monitor or reset cache contents (for example, to reduce memory pressure). The exact access pattern depends on whether you reference the wrapper via the class or via the attribute on the module (inspect GenericTranslator.css_to_xpath).

Implementation hints for reimplementers:
- Preserve the lru_cache(maxsize=256) decorator to get the intended caching behavior and keying semantics.
- Ensure the MRO places TranslatorMixin before the concrete cssselect translator so the mixin's normalization and pseudo-element dispatching are active for element and pseudo-element translation.
- Do not attempt to mutate XPathExpr objects here; this class only delegates to the base translator and caches string results returned from cssselect.

### `parsel.csstranslator.GenericTranslator.css_to_xpath` · *method*

## Summary:
Delegates conversion of a CSS selector string to an XPath expression to the parent translator implementation and benefits from memoization to avoid repeated work.

## Description:
This method is a thin, cached override that calls the superclass implementation to produce an XPath expression corresponding to the provided CSS selector. It is typically invoked whenever the system (or external users) needs to translate CSS selectors into XPath expressions — for example, as part of a selector evaluation pipeline or when building XPath queries from user-supplied CSS strings.

Known callers and invocation context:
- No direct internal call-sites were found inside the csstranslator module itself; the method is intended to be called by higher-level selector utilities, parser components, or user code that requires CSS-to-XPath translation.
- Common lifecycle usage: called at runtime when a selector is parsed or executed (selector evaluation stage), or when preparing an XPath query from a CSS input.

Why this is a separate method:
- The override exists primarily to apply memoization (via lru_cache) at the method level so repeated translations of identical CSS+prefix pairs are fast and do not re-run the full translation logic.
- Keeping this as a separate method (rather than inlining the call at call-sites) centralizes translation behavior and makes it easy to change caching, instrumentation, or delegation semantics in one place.

## Args:
    css (str):
        CSS selector string to translate. Must be a valid CSS selector accepted by the underlying cssselect translator.
    prefix (str, optional):
        XPath prefix to prepend to the generated expression. Defaults to "descendant-or-self::".
        Typical values are XPath axis prefixes; passing an empty string returns a raw XPath expression without a leading axis.

## Returns:
    str: An XPath expression string produced by the parent translator for the given CSS selector and prefix.
    - With the default prefix, the returned expression is suitable for selecting descendants (including the context node) that match the selector.
    - Identical inputs (css, prefix) will return the same string value for the lifetime of the process, and repeated calls are served from an in-memory cache.

## Raises:
    Propagates any exceptions raised by the parent translator implementation.
    - Common example: cssselect.xpath.ExpressionError when the provided CSS selector is invalid or cannot be represented as an XPath expression.
    - Any other exceptions raised by the underlying cssselect library are also propagated unchanged.

## State Changes:
Attributes READ:
    - None (this method does not read or depend on mutable attributes on self).

Attributes WRITTEN:
    - None (the method does not modify attributes on self).

## Constraints:
Preconditions:
    - css must be a string representing a CSS selector. Non-string inputs will violate the type expectation and may result in TypeError from callers or from the underlying translator.
    - prefix must be a string; it is used verbatim as the leading fragment of the returned XPath.

Postconditions:
    - Returns a string that is the XPath translation of the provided CSS selector with the given prefix applied.
    - Subsequent calls with the same (css, prefix) tuple will be fast due to memoization (lru_cache).

## Side Effects:
    - Memoization: results are cached in-memory by the lru_cache wrapper applied to this method. This increases memory usage proportional to the number of distinct (css, prefix) inputs (bounded by the cache maxsize of 256).
    - No I/O operations are performed.
    - No external services are called.
    - No mutation of objects outside of the method wrapper's internal cache occurs.

## `parsel.csstranslator.HTMLTranslator` · *class*

## Summary:
A thin translator class that composes TranslatorMixin with an upstream HTML translator and adds an LRU cache to css_to_xpath so repeated CSS→XPath string translations are faster.

## Description:
This class exists to combine two concerns in one translator type:
- TranslatorMixin: provides consistent normalization to cssselect.xpath.XPathExpr and pseudo-element handler dispatch.
- An upstream HTML translator implementation (referred to in this module as OriginalHTMLTranslator): provides the concrete CSS→XPath translation logic.

This wrapper does not change translation semantics; it only memoizes results of css_to_xpath to reduce repeated computation for identical inputs.

Typical callers:
- Selector translation pipelines that repeatedly translate identical CSS selector strings.
- Long-lived selector engines or parts of the codebase that evaluate the same selectors multiple times across documents.

Notes on inheritance:
- The class inherits TranslatorMixin and a base HTML translator implementation (denoted here as OriginalHTMLTranslator). In the local module this name typically refers to the HTML translator imported from the cssselect library. Consult the module imports/aliases in the source module to confirm the exact upstream class used in your copy of the code.

Motivation and responsibility:
- Provide the TranslatorMixin behavior and the upstream HTML translation in one concrete type.
- Cache results of css_to_xpath to speed up repeated translations while keeping the cache bounded (maxsize=256).
- Responsibility is strictly: provide a translator with the above behavior. It delegates all translation logic, initialization, and additional state to the upstream translator class.

## State:
- This class does not add instance attributes.
- The lru_cache wrapper is created at function-definition time and lives on the function object that implements css_to_xpath. That cache is shared across all instances of this class (i.e., it is attached to the class-level function wrapper).
- Cache details:
  - maxsize: 256 (as set on the lru_cache decorator).
  - Cache key: the tuple of the positional and keyword arguments passed to the wrapped function. For this method the effective key includes self, css, and prefix (in that order). Because self is included in the key, cached entries retain references to that instance until the entry is evicted or the cache is cleared.
  - Implication: the shared cache can retain references to translator instances and thereby prolong their lifetime until entries are evicted or the cache is explicitly cleared.

Class invariants:
- Instances behave like the upstream HTML translator for all translation operations, with the additional property that css_to_xpath results may be returned from the shared LRU cache on repeated calls with the same (self, css, prefix) tuple.
- TranslatorMixin expectations apply: the translator must satisfy the mixin's assumptions about available superclass methods (e.g., xpath_element).

## Lifecycle:
Creation:
- Instantiate the class using the same constructor signature as the upstream HTML translator (this wrapper defines no __init__ itself).
- No additional required arguments are introduced by this wrapper.

Usage:
- Primary operation: call css_to_xpath(css: str, prefix: str = "descendant-or-self::") to obtain an XPath string for a CSS selector.
- Behavior specifics:
  - On first call for a given (self, css, prefix) tuple, the wrapper delegates to the upstream implementation (super().css_to_xpath) and stores the returned string in the shared LRU cache.
  - On subsequent calls with the identical (self, css, prefix) tuple, the cached result is returned directly — avoiding re-invocation of the upstream logic.
  - Because the cache is shared across instances, different instances with identical hash values for self may still miss the cache unless the (self, css, prefix) tuple matches exactly.
- Clearing the cache:
  - The wrapped function exposes the standard lru_cache control attributes/methods on the function wrapper object (for example, cache_clear()). To clear the shared cache, call the wrapper's cache_clear() at the class level or via the bound method's __func__ attribute. Example (conceptual): call HTMLTranslator.css_to_xpath.cache_clear() on the translator class in your runtime. (Consult your runtime/code for the correct attribute access in your environment.)

Destruction:
- There is no explicit cleanup implemented by the class.
- Be aware that cached entries referencing translator instances may delay those instances' garbage collection until entries are evicted or cache_clear() is called.

## Method Map:
graph LR
    Call_css_to_xpath[call css_to_xpath(self, css, prefix)] --> CacheLookup[lru_cache lookup using key (self,css,prefix)]
    CacheLookup -->|hit| ReturnCached[return cached XPath string]
    CacheLookup -->|miss| Delegate[call super().css_to_xpath(css,prefix)]
    Delegate --> Upstream[upstream cssselect HTMLTranslator computes XPath string]
    Upstream --> StoreCache[store result in shared LRU cache]
    StoreCache --> ReturnCached
    TranslatorMixin[TranslatorMixin methods available via MRO] --- Delegate

(Interpretation: css_to_xpath first checks the shared LRU cache keyed by (self, css, prefix). On miss it delegates to the upstream implementation, caches, and returns the result. TranslatorMixin methods are available via MRO but are not modified by this wrapper.)

## Methods (public)
- css_to_xpath(css: str, prefix: str = "descendant-or-self::") -> str
  - Summary: Return an XPath expression string equivalent to css.
  - Inputs:
    - css (str): CSS selector to translate. Expected to be a str (hashable).
    - prefix (str): Optional XPath location axis prefix. Defaults to "descendant-or-self::".
  - Behavior:
    - The method is memoized with lru_cache(maxsize=256). The cache key contains self, css, and prefix.
    - Delegates actual translation to super().css_to_xpath(css, prefix) and returns that result.
  - Return:
    - str: XPath expression string as produced by the upstream translator.
  - Side effects:
    - May modify the shared LRU cache (insert or reorder entries).
  - Performance notes:
    - Cache reduces repeated computation cost for the same arguments.
    - Because self is part of the key, repeated calls from the same instance benefit; repeated calls from distinct instances only hit if their self values are identical in the cache key sense.
  - Concurrency:
    - lru_cache is not inherently thread-safe for mutation without external synchronization; if your application is multithreaded and calls css_to_xpath concurrently, consider synchronization or ensure your Python implementation's lru_cache provides sufficient safety for your use case.

## Raises:
- Any exception raised by the upstream implementation (super().css_to_xpath) is propagated unchanged. Typical exceptions include:
  - cssselect.xpath.ExpressionError or other cssselect-specific errors for invalid/unsupported CSS.
  - TypeError from lru_cache if unhashable arguments are passed (the declared types are strings so this should not occur under normal use).
  - Other runtime errors originating from the upstream translator.
- This wrapper performs no additional validation or exception wrapping.

## Example:
- Typical usage sequence (conceptual description, not literal code snippet):
  1. Instantiate the translator using the upstream translator's constructor signature.
  2. Call translator.css_to_xpath("a.external::attr(href)") to obtain an XPath string. On the first invocation for that (self, css, prefix) tuple the upstream translator is invoked.
  3. Call translator.css_to_xpath("a.external::attr(href)") again — the result is returned from the shared LRU cache (fast).
  4. To avoid the shared-cache retaining references to translator instances during long-running programs, call the cache-clear control on the wrapper when appropriate (for example, HTMLTranslator.css_to_xpath.cache_clear()).

Implementation notes for reimplementers:
- If you reimplement this pattern, be explicit about whether the cache should be shared across instances. Decorating the method at definition time with lru_cache creates a shared cache whose keys include self. If you want per-instance caches, you must implement a per-instance caching strategy (for example, use functools.cache on a function stored on the instance, or attach an lru_cache-decorated function to each instance).
- Consider memory implications of caching self in keys; prefer explicit cache_clear usage in long-lived processes or use weak references to avoid prolonging object lifetimes if that is required.

### `parsel.csstranslator.HTMLTranslator.css_to_xpath` · *method*

## Summary:
Delegates CSS selector-to-XPath translation to the parent cssselect HTMLTranslator implementation and caches results to avoid repeated work.

## Description:
This method is the class's public entry point for converting a CSS selector string into an XPath expression string. It simply calls the superclass implementation (the cssselect library's HTMLTranslator.css_to_xpath) and returns that result, while the method is wrapped with an LRU cache to speed repeated translations with identical arguments.

Known callers and lifecycle stage:
- Invoked by higher-level translation pipelines that need to convert user-supplied or programmatically-constructed CSS selectors into XPath strings (for example, Selector/Query APIs or any component that accepts CSS and needs an XPath).
- Typically called during selector compilation or at the start of a selection/query operation that accepts CSS syntax.
- This logic is factored into its own method (and cached) so that:
  - The library can centralize where CSS→XPath translation occurs (ensuring consistent prefix usage).
  - Caching can be applied transparently to speed repeated translations without duplicating caching logic across callers.
  - Delegation keeps this module compatible with upstream cssselect behavior while allowing the package to insert mixin behavior elsewhere in the MRO.

## Args:
    css (str): A CSS selector string to translate. Must be a valid CSS selector according to the cssselect parser rules.
    prefix (str): XPath axis/prefix to prepend to generated XPath expressions. Defaults to "descendant-or-self::". Must be a string.

## Returns:
    str: An XPath expression string produced by the upstream cssselect HTMLTranslator.css_to_xpath implementation. The returned string is suitable for use directly in XPath-based querying routines.

    Edge cases:
    - For syntactically invalid CSS selectors, the underlying translator raises an ExpressionError (see Raises).
    - The exact formatting of the returned XPath (e.g., use of axes, predicates) is determined by cssselect and may change if the upstream implementation changes.

## Raises:
    ExpressionError (from cssselect.xpath.ExpressionError):
        Raised when the css argument cannot be parsed or translated by the upstream cssselect HTMLTranslator (e.g., malformed selector, unsupported constructs). The exact message originates from cssselect.

    TypeError (raised by lru_cache):
        If any of the call arguments used as cache keys are unhashable (notably if the translator instance has become unhashable through a custom __eq__/__hash__ implementation), lru_cache will raise a TypeError describing the unhashable argument. In normal use with default object hashing this does not occur.

    Other exceptions:
        Any other exceptions raised by the upstream implementation may propagate unchanged.

## State Changes:
Attributes READ:
    - None (this method does not read or depend on any self.<attr> state).

Attributes WRITTEN:
    - None (this method does not modify any self.<attr>).

Note: Although no instance attributes are read or written, the lru_cache wrapper maintains an internal in-memory cache (attached to the wrapped function object) which is mutated when new translation results are stored.

## Constraints:
Preconditions:
    - css must be a str. Passing non-string types may result in a TypeError from the upstream parser.
    - prefix must be a str.
    - The translator instance (self) should be hashable for the lru_cache to accept it as part of the cache key; default object instances are hashable, but overriding __eq__ without a matching __hash__ can make instances unhashable and cause a TypeError when calling this method.

Postconditions:
    - On successful return, a string containing the XPath equivalent of the provided CSS selector is returned.
    - The in-memory LRU cache may contain a cached entry keyed by (self, css, prefix) after the call.

## Side Effects:
    - Mutates the internal LRU cache associated with this method's wrapper (in-memory, process-local). This increases memory usage proportionally to the number of distinct (self, css, prefix) calls up to the cache maxsize (256).
    - No I/O, no network calls, and no mutation of objects external to the cache wrapper are performed by this method.

## `parsel.csstranslator.css2xpath` · *function*

## Summary:
Delegates a CSS selector string to a module-level translator and returns the resulting XPath expression string.

## Description:
This small helper forwards the provided CSS selector string to a module-level translator object's css_to_xpath method and returns the translator's result. It exists to expose a concise top-level API for converting CSS selectors to XPath without requiring callers to construct or reference a translator instance directly.

Known callers within the provided context:
- No direct callers were discovered in the provided source summaries. Typical callers (in other parts of a codebase) include selector-parsing pipelines, HTML/XML scraping utilities, and higher-level convenience functions that need a quick CSS→XPath conversion step before performing XPath queries.

Why this logic is extracted into its own function:
- Responsibility boundary: centralizes the indirection to the module-level translator so callers need only pass a CSS query string and not manage translator instances.
- Encapsulation: callers remain decoupled from the translator's concrete type, caching strategy, and lifecycle.
- Convenience: provides a single, stable entrypoint for CSS→XPath conversion used across the codebase.

## Args:
    query (str): CSS selector to translate.
        - Required. Must be text representing a valid CSS selector according to the underlying cssselect translator.
        - The function does not coerce types; callers should pass a str. Passing other types will likely result in a TypeError raised by the underlying translator (or by Python if the argument cannot be handled).

## Returns:
    str: An XPath expression string produced by the module-level translator's css_to_xpath method.
    - On success, this is the textual XPath expression equivalent of the input CSS selector (as produced by the underlying cssselect implementation and any TranslatorMixin normalization).
    - There are no alternative return types; failures raise exceptions.

## Raises:
    NameError:
        - If the module-level name _translator is not defined in the module at runtime, a NameError will be raised when this function is called.
    cssselect.xpath.ExpressionError:
        - If the underlying cssselect translator considers the CSS selector invalid or unsupported, it may raise ExpressionError; this function does not catch or wrap that exception and it will propagate to the caller.
    TypeError:
        - Possible if the underlying translator's css_to_xpath implementation expects a specific argument type (e.g., str) and receives an incompatible type.
        - Possible if the underlying translator's css_to_xpath is decorated with an lru_cache and one of the cache key components (typically the translator instance) is unhashable; that mid-level call could raise TypeError which will propagate here.
    Any exceptions raised by the underlying translator implementation are propagated unchanged.

## Constraints:
Preconditions:
    - The caller must ensure that query is a str containing a CSS selector.
    - The module must define the name _translator and that object must expose a callable css_to_xpath method that accepts a single positional argument (the CSS string). If these preconditions are not met, NameError or AttributeError/TypeError will occur.

Postconditions:
    - If the function returns normally, it guarantees to return the string value previously produced by the underlying translator for the given query (subject to any caching or normalization performed by that translator).
    - No mutation of the caller's input occurs.

## Side Effects:
    - No direct I/O (no file, network, or stdout operations) occur in this function itself.
    - Calls the module-level translator's css_to_xpath method, which may:
        - Populate or mutate an internal LRU cache (if the translator implementation uses caching).
        - Invoke other translator internals that may modify translator-local state.
    - No global variables are created or directly mutated by this function beyond whatever the translator's method does internally.

## Control Flow:
flowchart TD
    Start[Start: css2xpath(query)] --> CheckTranslator{Is _translator name defined?}
    CheckTranslator -- No --> RaiseNameError[NameError raised]
    CheckTranslator -- Yes --> CallTranslator[_translator.css_to_xpath(query)]
    CallTranslator -->|returns| ReturnXPath[Return XPath string to caller]
    CallTranslator -->|raises ExpressionError or other| PropagateError[Propagate exception to caller]

## Examples:
- Typical usage scenario (described in prose):
    1. A scraping utility needs to run an XPath query but is given a CSS selector string. It calls this helper with the CSS string.
    2. The function forwards the string to the configured module-level translator and returns the XPath expression string.
    3. The caller uses the returned XPath expression with an XML/HTML tree search routine.

- Error-handling guidance:
    - Wrap calls in a try/except block if you expect malformed CSS input and want to handle parsing failures:
        * Catch cssselect.xpath.ExpressionError to detect invalid CSS selector input.
        * Optionally catch NameError during initialization phases if the module-level translator may not yet be configured.

Implementation note for reimplementers:
- This function intentionally delegates fully to a module-level translator object; when reimplementing, ensure a module-level translator is created and exposes css_to_xpath(query: str) -> str. Consider adding a thin validation (e.g., type checking of query) if you want earlier, clearer errors instead of letting the translator propagate them.

