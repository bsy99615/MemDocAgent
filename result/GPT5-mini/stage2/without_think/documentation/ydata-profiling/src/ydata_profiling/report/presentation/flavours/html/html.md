# `html.py`

## `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML` · *class*

## Summary:
Represents a minimal HTML presentation renderer that returns the raw HTML string stored under the "html" entry of an inherited content mapping.

## Description:
This class is a concrete, minimal implementation of an HTML presentation renderer. It exists to provide a render() implementation that directly exposes pre-computed HTML stored in the instance's content container.

Typical usage:
- The class is instantiated by higher-level report construction code (factories or presenters) that populate the inherited content attribute.
- Use this class when the report's HTML is already prepared and needs to be returned verbatim — e.g., when rendering a stored HTML fragment for embedding or serving.

Responsibility boundary:
- HTMLHTML does not generate or validate HTML. Its sole responsibility is to read and return the value found at key "html" in the inherited content mapping.
- Any preparation, validation, or sanitization of the HTML should happen before setting content["html"] by the caller or factory.

## State:
Attributes (inherited and relied upon):
- content
    - Type: any object supporting subscription by key (i.e., implements __getitem__); typically a dict-like mapping.
    - Expected key: "html"
    - Expected value at content["html"]: an HTML document or fragment, commonly a str. The class does not enforce the value type.
    - Invariant: render() assumes content is present and subscriptable and that content["html"] exists. Callers should ensure this invariant before invoking render().

Notes on __init__ parameters:
- HTMLHTML does not define its own __init__; it inherits construction from its superclass. There are no additional constructor parameters introduced by HTMLHTML.
- Callers must provide or set the inherited content attribute through the superclass constructor or by mutation afterward, according to the superclass contract.

Class invariants:
- After instantiation and before calling render(), the attribute self.content must be a subscriptable container with a mapping for key "html".
- render() does not mutate state.

## Lifecycle:
Creation:
- Instantiate the class through the normal constructor inherited from the HTML base class (no additional required args introduced here).
- Ensure that the inherited content attribute contains the "html" entry prior to use.

Usage:
- Primary method: render()
    - Behavior: returns the value at self.content["html"] exactly as stored.
    - Typical call sequence: create instance (or obtain from factory) → ensure content["html"] is set → call render() → use returned HTML string.
- There is no required ordering between other operations beyond the invariant that content["html"] must exist before calling render().

Destruction / cleanup:
- HTMLHTML does not manage external resources, file handles, or network connections and therefore has no special cleanup responsibilities.
- No context manager or close() method is provided by this class.

## Method Map:
graph LR
    A[Instance of HTMLHTML] --> B[Inherited attribute: content]
    B --> C{Has key "html"?}
    C -- yes --> D[render()] --> E[returns content["html"]]
    C -- no --> F[KeyError raised at access]

(Note: The diagram shows the dependency on the inherited content mapping and the single render() behavior.)

## Raises:
- KeyError
    - Trigger: content does not contain the "html" key (i.e., "html" not present when performing self.content["html"]).
- TypeError
    - Trigger: self.content is not subscriptable (for example, None or an object that does not implement __getitem__).
- Any other exception raised is propagated from the content object's __getitem__ implementation (e.g., custom mapping types may raise their own exceptions).

## Example:
- Creation: Obtain or construct an instance via the HTML base-class constructor or a factory that sets up the content attribute. Ensure the content mapping contains the "html" key with an HTML string value.
- Typical usage: After the instance has content["html"] set, call render() to fetch the HTML string and send it to the next stage (embedding, writing to a file, or returning in an HTTP response).
- Cleanup: No explicit cleanup required.

This documentation intentionally avoids asserting details of the HTML base class constructor; callers should consult the base class documentation for constructor parameters and other inherited behavior.

### `src.ydata_profiling.report.presentation.flavours.html.html.HTMLHTML.render` · *method*

## Summary:
Returns the stored raw HTML payload from the renderer's content dictionary, yielding the HTML fragment that this renderer carries and leaving the object state unchanged.

## Description:
Known callers and lifecycle context:
- Invoked by the presentation/report rendering pipeline when the "html" flavour item must be converted to an output fragment (for example, by a report assembler or template renderer that iterates over presentation items and calls render() on each).
- Typical lifecycle: an HTML renderer instance is constructed (see HTML) with a content payload, then later the presentation layer calls this concrete renderer's render() to obtain the final HTML fragment to include in the report output.

Why this logic is a separate method:
- The method isolates the concrete rendering behavior for the HTML flavour from upstream assembly code and from the abstract HTML base class, which only packages the payload. Separating this behavior makes it trivial to override in alternative renderers, and keeps the rendering pipeline generic (it just calls render() on items without inspecting content internals).

## Args:
- None.

## Returns:
- str: The value stored at self.content["html"], intended to be the raw HTML string carried by this renderer.
- Edge cases:
    - Although the return annotation is str, the method returns whatever value is stored under the "html" key; if that value is not a string, that non-str object will be returned (violating the type hint at runtime).

## Raises:
- KeyError: If self.content is a mapping but does not contain the key "html".
- TypeError: If self.content exists but is not subscriptable (e.g., None or a non-mapping/non-sequence), indexing with ["html"] will raise TypeError.
- AttributeError: If the instance does not have a content attribute at all, attempting to access self.content will raise AttributeError.
Note: Under normal construction via the HTML base class, self.content is guaranteed to be a dict containing the "html" key; these exceptions only occur if that invariant is violated.

## State Changes:
- Attributes READ:
    - self.content (reads the mapping to obtain the "html" value)
- Attributes WRITTEN:
    - None (the method performs no writes or mutations to self or to external objects)

## Constraints:
- Preconditions:
    - The instance should have an attribute self.content that is a mapping (dict-like) containing the key "html" whose value is the HTML fragment (string).
    - This precondition is satisfied for instances constructed via the HTML base class, which sets content = {"html": content_str}.
- Postconditions:
    - No mutation to self occurs.
    - The returned value equals the current value of self.content["html"] at the time of the call.

## Side Effects:
- None: the method performs no I/O, no calls to external services, and does not mutate objects outside self.

