# `elements.py`

## `folium.elements.JSCSSMixin` · *class*

## Summary:
A small Element mixin that ensures a set of JavaScript and CSS resource links (name, URL pairs) are added to the root Figure's header before the element is rendered.

## Description:
JSCSSMixin is intended to be mixed into folium Element-derived classes that require including external JS and/or CSS assets in the HTML <head> (the Figure header). It is not a standalone widget; rather it is an orthogonal responsibility layered on top of Element to automate adding resource links.

Typical usage scenarios:
- A plugin-like Element implementation that depends on one or more external JavaScript libraries or stylesheet files can declare those resources on the class using the default_js and/or default_css attributes. When the element is rendered (which happens when the element is part of a Figure and the Figure is being rendered), JSCSSMixin will add those resources to the Figure.header so they are emitted once in the HTML document head.
- Classes that combine UI/content with required frontend resources should use this mixin to centralize resource registration logic.

Known callers / creation sites:
- Any Element subclass in the codebase that includes JSCSSMixin in its MRO. The mixin's render method is invoked as part of the Element rendering pipeline (i.e., when the element's render is called either directly or via the Figure's rendering process).

Motivation and responsibility:
- Responsibility: register default JS/CSS resource links with the overall Figure header before rendering the element.
- The mixin enforces the boundary that resource registration is performed only when the element is attached to a Figure; it refuses to run outside of a Figure context.

## State:
- class attribute default_js: list[tuple[str, str]]
    - Description: Sequence of (name, url) pairs for JavaScript resources to register.
    - Default: empty list ([])
    - Valid values: any iterable of 2-tuples (name, url) where name is a string used as the child name when adding to the Figure.header, and url is a string URL passed to the JavascriptLink constructor.
    - Invariant: each entry must be a pair; the mixin iterates with "for name, url in self.default_js".
    - Note: default_js is declared at class level. Subclasses should override this attribute (preferably with an immutable tuple or a new list) to avoid shared mutable-state pitfalls between subclasses/instances.

- class attribute default_css: list[tuple[str, str]]
    - Description: Sequence of (name, url) pairs for CSS resources to register.
    - Default: empty list ([])
    - Valid values and invariant: same contract as default_js but for CssLink resources.

- Instance attributes:
    - The mixin itself does not introduce new instance-level attributes. It relies on Element methods (get_root, render) and the Figure.header object to mutate or attach children.

Class invariants:
- default_js and default_css remain iterable of pairs for the lifetime of the class.
- The mixin assumes that get_root() returns an object that either is a Figure or will cause an AssertionError (see Raises).

## Lifecycle:
Creation:
- There is no special __init__ in the mixin. Typical instantiation happens via a concrete class that includes JSCSSMixin in its inheritance chain and calls the usual Element initializer. No arguments are required by the mixin itself.
- Best practice: subclasses should set default_js and default_css as class attributes before instantiating.

Usage / typical call sequence:
1. Create a Figure instance (the document root).
2. Instantiate a concrete Element subclass that includes JSCSSMixin (its constructor is inherited from Element or the concrete class).
3. Add the element instance to the Figure (e.g., via Figure.add_child or equivalent API provided by the Figure/Element system).
4. Trigger rendering for the Figure (or directly call the element's render if the element is part of a proper Element tree). When render is invoked on the element:
    a. The mixin's render obtains the root via get_root().
    b. It asserts the root is a Figure.
    c. For each (name, url) in default_js it constructs a JavascriptLink(url) and registers it on figure.header.add_child(..., name=name).
    d. For each (name, url) in default_css it constructs a CssLink(url) and registers it on figure.header.add_child(..., name=name).
    e. It then calls super().render(**kwargs) to continue normal Element rendering.

Sequencing requirements:
- The element must be attached to a Figure (i.e., get_root() must return a Figure) before render is called.
- The mixin expects that Figure.header has an add_child(child, name=...) method that accepts a link Element and a name.

Destruction / cleanup:
- JSCSSMixin performs no special cleanup. Resources are registered into the Figure.header; removal (if desired) is the responsibility of the Figure/header API or the caller.

## Method Map:
flowchart LR
    A[get_root()] --> B{is instance of Figure?}
    B -- no --> X[AssertionError raised and rendering stops]
    B -- yes --> C[for each (name,url) in default_js]
    C --> C1[create JavascriptLink(url)]
    C1 --> C2[figure.header.add_child(JavascriptLink(url), name=name)]
    B --> D[for each (name,url) in default_css]
    D --> D1[create CssLink(url)]
    D1 --> D2[figure.header.add_child(CssLink(url), name=name)]
    D2 --> E[super().render(**kwargs)]
    C2 --> E

(Above graph shows main decision points and call order for render.)

## Raises:
- AssertionError:
    - Condition: raised if get_root() does not return an instance of Figure.
    - Message: "You cannot render this Element if it is not in a Figure."
    - Rationale: registering resources requires a root Figure with a header to attach resources to.

- Errors during iteration/unpacking:
    - If elements of default_js/default_css are not 2-tuples (for example a single-value item), the iteration "for name, url in ..." will raise a ValueError or TypeError during unpacking.
    - If the constructors for JavascriptLink or CssLink raise (e.g., due to invalid URL type), those exceptions propagate.

- Errors from Figure.header.add_child:
    - Any exceptions raised by the header's add_child method (for example duplicate name handling or invalid child type) will propagate to the caller.

## Example (step-by-step, no source code):
1. Ensure you have a Figure object that represents the HTML document root with a header component that supports add_child(child, name=...).
2. Create a concrete Element subclass that includes the mixin and explicitly sets class attributes:
   - default_js = [("lib-name", "https://cdn.example.com/lib.js")]
   - default_css = [("style-name", "https://cdn.example.com/style.css")]
3. Instantiate the concrete element and add it to the Figure using the Figure/Element API.
4. When the Figure is rendered (or the element's render is invoked as part of the Figure render), the mixin:
   - verifies the element is attached to a Figure,
   - creates a JavascriptLink for each default_js and a CssLink for each default_css,
   - registers them on the Figure.header using the provided names, and
   - delegates to the remaining Element rendering logic (super().render).

Notes and best practices:
- Override default_js/default_css at the class level (not by mutating the inherited list) to avoid inadvertent shared state across subclasses/instances.
- Use stable, unique names in the (name, url) pairs to avoid collisions in Figure.header if the header implementation uses name to deduplicate children.

### `folium.elements.JSCSSMixin.render` · *method*

## Summary:
Injects the element's default JavaScript and CSS link resources into the root Figure's header and then delegates to the normal rendering pipeline; does not return a value and does not mutate the element itself.

## Description:
This method is part of the rendering lifecycle for elements that include or depend on external JS/CSS assets. It is executed when this element is rendered into the document tree and ensures its static asset links are registered on the root Figure before the element's own rendering proceeds.

Known callers and invocation context:
- Any code that calls Element.render on an instance of a class that mixes in JSCSSMixin (for example, the Figure or Map rendering pipeline that iterates over child elements and calls their render methods).
- Typically invoked while preparing the Figure's HTML representation; often the root Figure triggers renders on its children, so this method runs when an element is attached to a Figure and that Figure is being rendered.

Why this is a separate method:
- Centralizes header-injection logic for JS/CSS so subclasses do not duplicate asset registration.
- Ensures assets are added before the element's own HTML/JS is produced by calling the superclass render after header injection.
- Keeps asset management orthogonal to element-specific rendering logic and easily testable.

## Args:
    **kwargs: dict
        Arbitrary keyword arguments forwarded unchanged to the superclass render method. This method does not consume or validate kwargs.

## Returns:
    None
    The method performs side effects only (mutating the root Figure's header) and does not return a value.

## Raises:
    AssertionError
        If the element is not attached to a Figure. Triggered when self.get_root() does not return an instance of Figure. The exact assertion message is: "You cannot render this Element if it is not in a Figure."
    TypeError or ValueError
        If an entry in self.default_js or self.default_css cannot be unpacked into exactly two values (name, url), Python will raise TypeError or ValueError during unpacking.
    Any exception raised by:
        - JavascriptLink(url) or CssLink(url) constructors (for example, invalid URL handling inside those constructors)
        - figure.header.add_child(child, name=name)
    These exceptions are not caught here and will propagate to the caller.

## State Changes:
Attributes READ:
    - self.default_js (class- or instance-level iterable of asset entries)
    - self.default_css (class- or instance-level iterable of asset entries)
    - result of self.get_root() (inspected to confirm it is a Figure)
    - figure.header (accessed to call add_child)

Attributes WRITTEN:
    - None on self (this method does not assign to self attributes)

External objects mutated:
    - figure.header: new child nodes (JavascriptLink and CssLink instances) are added for each entry in default_js and default_css by calling figure.header.add_child(..., name=name).

## Constraints:
Preconditions:
    - The element must be attached into a document tree whose root is a Figure instance; otherwise the assertion fails.
    - self.default_js and self.default_css are expected to be iterables (commonly lists) of 2-item sequences: (name, url). Example entry: ("leaflet_js", "https://.../leaflet.js").
    - name is used as the identifier passed to header.add_child; it should be a hashable identifier (typically a string) appropriate for use by the header container.

Postconditions:
    - For each (name, url) in self.default_js:
        - A new JavascriptLink instance is constructed with the provided url, and that instance is added to figure.header via add_child(..., name=name).
    - For each (name, url) in self.default_css:
        - A new CssLink instance is constructed with the provided url, and that instance is added to figure.header via add_child(..., name=name).
    - The superclass render method has been invoked with the same kwargs, allowing normal element rendering to continue.
    - The element instance (self) retains its attribute values; only the Figure's header is changed.

## Side Effects:
    - Mutates the root Figure's header by adding children; this will affect the final HTML produced for the Figure (additional <script> / <link> references).
    - Constructs JavascriptLink and CssLink objects (imported from branca.element) which may perform validation in their constructors; any such behavior can raise and will propagate.
    - No network I/O or file I/O is performed here directly; however, downstream consumers of the produced HTML will cause browsers to fetch the referenced URLs.

