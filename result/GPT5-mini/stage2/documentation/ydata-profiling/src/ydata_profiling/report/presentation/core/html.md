# `html.py`

## `src.ydata_profiling.report.presentation.core.html.HTML` · *class*

## Summary:
Represents an HTML item renderer that wraps raw HTML content into the report rendering system; it marks the item type as "html" and stores the provided HTML string inside the renderer's content payload.

## Description:
HTML is a lightweight concrete subclass of ItemRenderer used to carry raw HTML snippets through the presentation layer. It should be instantiated when a piece of preformatted HTML (as a string) needs to be included as an item in a report. Typical callers are report builders or item factories that assemble the presentation tree and forward per-item metadata via keyword arguments (e.g., name, anchor_id, classes).

The class exists to:
- Encapsulate an HTML payload under the renderer/item model used by the presentation system.
- Ensure the item_type is fixed to "html" and that the content payload uses the key "html".
- Provide a simple identity via __repr__ while leaving actual rendering logic to subclasses or rendering backends (render() is intentionally not implemented here).

Responsibility boundary:
- HTML is responsible only for packaging HTML text as the content of an ItemRenderer with item_type "html".
- It does not perform transformation, sanitization, or output formatting of the HTML string; concrete renderers or downstream code must implement render() to produce final output.

## State:
Attributes inherited and/or set during initialization (visible to callers and subclasses):

- item_type (str)
    - Source: set by ItemRenderer.__init__ and initialized here to the literal "html".
    - Valid values: for this class, always the string "html".
    - Invariant: item_type == "html".

- content (dict)
    - Source: HTML passes {"html": content_str} to ItemRenderer (which delegates to its superclass).
    - Shape: a dictionary with the single key "html" whose value is the string passed as the content parameter.
    - Example: {"html": "<p>Hello</p>"}.
    - Invariant: if present, content is a dict containing the key "html" mapped to the original content string.

- Other presentation metadata (name, anchor_id, classes)
    - Source: forwarded via **kwargs to ItemRenderer, which delegates to its superclass.
    - Types/values: optional strings or None (see ItemRenderer signature for names).
    - These are not created by HTML itself but are accepted and propagated.

Constructor parameters (and constraints):

- content: str
    - Required. The raw HTML string to be carried as the value of content["html"].
    - No internal validation or sanitization is performed by HTML.

- **kwargs:
    - Forwarded to ItemRenderer.__init__. Common accepted keys (by ItemRenderer) are:
        - name: Optional[str] = None
        - anchor_id: Optional[str] = None
        - classes: Optional[str] = None
    - Callers may pass none, some, or all of these keyword arguments.

Class invariants:
- After initialization, item_type == "html".
- content is a dict containing the key "html" whose value equals the constructor content argument.

## Lifecycle:
Creation:
- Instantiate by calling HTML(content_str, **kwargs).
- Required positional argument:
    - content: the HTML string.

Usage:
- After creation, typical interactions:
    1. Inspect metadata (e.g., instance.item_type == "html", instance.content["html"]).
    2. Pass the instance into a rendering pipeline, template engine, or report assembler.
    3. The actual output rendering must be performed by a concrete renderer implementing render() — calling instance.render() on this class will raise NotImplementedError.

Method calling order / sequencing:
- No special ordering required for __repr__.
- render() must be overridden before being called; otherwise a NotImplementedError will be raised.

Destruction / cleanup:
- HTML holds only simple Python objects (strings, dict); there are no explicit resources to close or context-managed cleanup responsibilities.

## Method Map:
graph TD
    A[create HTML(content, **kwargs)] --> B[ItemRenderer.__init__]
    B --> C[super().__init__(content_dict, name, anchor_id, classes)]
    A --> D[__repr__ -> returns "HTML"]
    A --> E[render() -> raises NotImplementedError (must be implemented by subclass)]

(Note: the graph shows initialization delegation and the two public methods; render is intentionally abstract here.)

## Methods (summary):
- __init__(content: str, **kwargs)
    - Packs the provided HTML string into a content dict {"html": content} and delegates initialization to ItemRenderer, fixing item_type to "html".

- __repr__() -> str
    - Returns the literal string "HTML". Useful for debugging and logging.

- render() -> Any
    - Intentionally unimplemented in this class. Raises NotImplementedError.
    - Concrete subclasses or rendering backends must override render() to produce the final output (string, HTML fragment, DOM node, or other rendering artifact as required by the consuming code).

## Raises:
- __init__:
    - No explicit exceptions are raised by this constructor in the provided code. Type checking is not enforced at runtime here; if callers pass incompatible types, exceptions (e.g., from downstream code that expects dict shapes) may occur elsewhere.

- render:
    - Always raises NotImplementedError when invoked on this class; callers must override/implement render before calling.

## Example:
- Typical instantiation:
    html = HTML("<p>Hello world</p>", name="greeting", anchor_id="greet", classes="lead")
    repr(html)  -> "HTML"
    html.content -> {"html": "<p>Hello world</p>"}
    html.item_type -> "html"

- To actually render, subclass and implement render:
    class MyHTMLRenderer(HTML):
        def render(self):
            # return rendered representation, e.g., the raw HTML string
            return self.content["html"]

    renderer = MyHTMLRenderer("<div>OK</div>")
    output = renderer.render()  # "<div>OK</div>"

### `src.ydata_profiling.report.presentation.core.html.HTML.__init__` · *method*

## Summary:
Constructs an HTML renderable by embedding the given HTML string into the object's content dictionary and setting the item's type to "html", updating the instance state used by the presentation renderer.

## Description:
This initializer wraps a raw HTML string into the Renderable/ItemRenderer initialization sequence. It is typically invoked when a presentation or report-building component needs to create a renderable element that contains raw HTML markup. The method exists as a small, focused constructor to centralize the convention that HTML content is stored under the "html" key and that the corresponding item_type is "html" instead of repeating this pattern at every call site.

Known callers and lifecycle stage:
- Instantiation occurs at the time a report/presentation element is created (presentation-building stage). The exact higher-level callers are not listed in the provided source; any code that needs to add an HTML fragment to a report will instantiate this class.

Why this is a separate method:
- It encapsulates the content-wrapping convention ({"html": content}) and ensures the item_type is consistently set to "html". Keeping this logic in the class constructor avoids repetition and makes callers simpler (they only pass a string).

## Args:
    content (str): Raw HTML markup to render. This value is stored as the value for the "html" key in the object's content dictionary.
    **kwargs: Keyword arguments forwarded to the parent ItemRenderer / Renderable constructor. Recognized keys:
        name (Optional[str]): If provided, Renderable will set content["name"] = name.
        anchor_id (Optional[str]): If provided, Renderable will set content["anchor_id"] = anchor_id.
        classes (Optional[str]): If provided, Renderable will set content["classes"] = classes.

    Notes:
    - The constructor signature requires content to be a string by annotation, but no runtime type check is performed here; passing a non-str value will still be placed under the "html" key.
    - Passing any unexpected keyword names (keys other than name, anchor_id, classes) will raise a TypeError propagated from the parent call (unexpected keyword argument).

## Returns:
    None

## Raises:
    TypeError: If kwargs contains unexpected keyword arguments not accepted by ItemRenderer (e.g., unknown keyword names) — the exception originates from the parent constructor call.
    (No other exceptions are explicitly raised by this constructor. Subsequent access to Renderable properties such as .name, .anchor_id, or .classes may raise KeyError if those keys were not provided.)

## State Changes:
    Attributes READ:
        - None explicitly read by this method.

    Attributes WRITTEN:
        - self.content (dict): Set to {"html": content} and may be augmented with "name", "anchor_id", and "classes" entries if corresponding kwargs are supplied. This assignment happens in Renderable.__init__ which is called by the parent constructor chain.
        - self.item_type (str): Set to "html" by ItemRenderer.__init__ (the immediate parent constructor invoked).

## Constraints:
    Preconditions:
        - The instance is being created (normal object construction). content should be a value intended to represent HTML (annotation: str), although no runtime enforcement occurs.
        - kwargs must be valid keyword-only arguments expected by ItemRenderer/Renderable (name, anchor_id, classes). Any other keys will cause a TypeError.

    Postconditions:
        - After the constructor returns, self.item_type == "html".
        - After the constructor returns, self.content is a dict that contains at least the key "html" with the original content value; if name/anchor_id/classes were provided, those keys will also be present in self.content.
        - The object is ready to be used by presentation rendering code that expects a Renderable with content under the "html" key.

## Side Effects:
    - No I/O or external service calls are performed.
    - Mutates only the new instance (self): assigns self.content and self.item_type (via parent constructors).
    - If callers pass unexpected kwargs, a TypeError is raised from the parent constructor; no other global state is modified.

### `src.ydata_profiling.report.presentation.core.html.HTML.__repr__` · *method*

## Summary:
Returns a concise, constant textual representation identifying this renderer as "HTML". This does not modify the object's state.

## Description:
This dunder representation provides a short, stable identifier for the object when Python requests its representation (for example via repr(), interactive REPL display, logging, or when included in containers that are printed). Typical callers include the built-in repr() function, frameworks or libraries that log or display object representations, and interactive debugging/inspection tools.

Keeping this logic in its own __repr__ method follows Python convention for object representations and ensures any code that requests a textual representation gets a consistent, minimal identifier that communicates the renderer type. It is separated from other logic because __repr__ is a standard, small contract used by the language and should remain side-effect free and fast.

## Args:
    None

## Returns:
    str: The constant string "HTML" — the canonical representation for this renderer object. There are no alternate return values; every call returns exactly "HTML".

## Raises:
    None

## State Changes:
    Attributes READ : None
    Attributes WRITTEN : None

## Constraints:
    Preconditions:
        - self must be a valid instance (the method assumes a bound method call); no other preconditions.
    Postconditions:
        - No attributes on self are modified.
        - The caller receives the string "HTML".

## Side Effects:
    - None. The method performs no I/O, network calls, or mutations outside the instance.

### `src.ydata_profiling.report.presentation.core.html.HTML.render` · *method*

## Summary:
Abstract rendering hook that must be overridden to produce a presentation-ready value for an HTML item. Implementations should not change the object's stored content.

## Description:
This method is the Renderable-subclass hook that concrete item renderers implement to produce a value consumed by the presentation/export pipeline. The base implementation in this repository raises NotImplementedError; concrete subclasses (including this HTML renderer) must provide the rendering logic.

Why this is a separate method:
- Renderable defines an abstract render() method; keeping rendering logic on each concrete renderer enables polymorphism so the aggregator or template code can call render() on heterogeneous items without inlining type-specific serialization.
- Implementations can control the exact output shape (JSON-serializable object, mapping used by templates, or another representation) while the caller only relies on the render contract.

Known, verifiable facts about the object:
- HTML.__init__ constructs the object by calling ItemRenderer.__init__ with item_type set to "html" and content set to {"html": content}, therefore instances have:
    - self.content (a dict) with a key "html" containing the HTML payload.
    - self.item_type (a str) set to "html".

## Args:
    None

## Returns:
    Any: The method is declared to return Any. The concrete implementation decides the exact, serializable return shape that downstream code will accept. Implementations commonly return a JSON-serializable mapping whose structure is defined by the surrounding presentation layer, but that structure is not enforced by this method's signature.

## Raises:
    NotImplementedError:
        - The current method implementation in this file raises NotImplementedError unconditionally (i.e., if not overridden).

    (Implementation guidance)
    TypeError or ValueError (implementation-defined):
        - An implementation may choose to raise TypeError or ValueError if required keys are missing or of the wrong type (for example, if "html" is missing or is not a str). This is not raised by the base method but is a reasonable defensive behavior for concrete implementations.

## State Changes:
    Attributes READ:
        - self.content (dict): Implementations will typically read the stored content dictionary set up by Renderable and HTML.__init__. In particular, content["html"] is the HTML payload.
        - self.item_type (str): Implementations may read the item type set by ItemRenderer (verifiably present and equal to "html").

    Attributes WRITTEN:
        - None required by the base class. Implementations SHOULD avoid mutating self.content, self.item_type, or other instance attributes; rendering is expected to be a read-only operation on the instance state unless explicitly documented otherwise by an override.

## Constraints:
    Preconditions:
        - The instance was initialized via HTML.__init__, so self.content is a dict and contains the "html" key (unless mutated externally).
        - No other guarantees are made by the base method.

    Postconditions:
        - If overridden, the implementation returns a value (of type Any) suitable for downstream consumption.
        - The base method raises NotImplementedError; therefore calling this exact implementation will not produce a value.

## Side Effects:
    - The base implementation has no side effects other than raising NotImplementedError.
    - Implementations SHOULD avoid side effects (no I/O, no network calls, no mutation of external objects). If an implementation performs sanitization or transforms the HTML payload, that mutation should be confined to the returned value (not to self.content) and documented on the overriding implementation.

