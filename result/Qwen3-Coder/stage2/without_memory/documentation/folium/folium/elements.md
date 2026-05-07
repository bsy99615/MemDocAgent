# `elements.py`

## `folium.elements.JSCSSMixin` · *class*

## Summary:
A mixin class that provides JavaScript and CSS resource management for folium elements.

## Description:
JSCSSMixin is designed to be inherited by folium elements that require JavaScript and CSS dependencies. It enables automatic inclusion of default JavaScript and CSS resources when rendering elements within a folium Figure context. This mixin abstracts away the complexity of managing external resource dependencies and ensures proper placement of these resources in the HTML output.

## State:
- default_js: Class attribute containing a list of tuples (name, url) representing default JavaScript resources to include
- default_css: Class attribute containing a list of tuples (name, url) representing default CSS resources to include

## Lifecycle:
- Creation: Instances are created normally as part of inheritance hierarchy from Element
- Usage: When render() is called, the mixin automatically adds configured JS/CSS resources to the figure's header
- Destruction: No special cleanup required; relies on parent Element's lifecycle management

## Method Map:
```mermaid
graph TD
    A[JSCSSMixin.render] --> B[get_root()]
    B --> C[assert isinstance(figure, Figure)]
    C --> D[figure.header.add_child(JavascriptLink(url))]
    D --> E[figure.header.add_child(CssLink(url))]
    E --> F[super().render(**kwargs)]
```

## Raises:
- AssertionError: Raised when the element is not contained within a Figure instance

## Example:
```python
# Typical usage in a folium element subclass
class MyMap(JSCSSMixin, Element):
    default_js = [("leaflet", "https://unpkg.com/leaflet@1.7.1/dist/leaflet.js")]
    default_css = [("leaflet", "https://unpkg.com/leaflet@1.7.1/dist/leaflet.css")]

# When rendered within a Figure:
# The JavaScript and CSS links are automatically added to the figure header
# before the parent render method is called
```

### `folium.elements.JSCSSMixin.render` · *method*

## Summary:
Adds JavaScript and CSS dependencies to the HTML figure header before rendering the element.

## Description:
This method ensures that all default JavaScript and CSS resources defined in the JSCSSMixin are properly included in the HTML output by adding them to the figure's header. It validates that the element is part of a Figure before proceeding with dependency injection.

## Args:
    **kwargs: Additional keyword arguments passed to the parent render method

## Returns:
    None: This method doesn't return a value but modifies the figure's header

## Raises:
    AssertionError: When the element is not contained within a Figure object

## State Changes:
    Attributes READ: 
        - self.default_js: List of (name, url) tuples for JavaScript dependencies
        - self.default_css: List of (name, url) tuples for CSS dependencies
    
    Attributes WRITTEN: 
        - figure.header: Modified by adding JavascriptLink and CssLink children

## Constraints:
    Preconditions:
        - The element must be contained within a Figure object (checked via get_root())
        - self.default_js and self.default_css must be iterable sequences of (name, url) tuples
    
    Postconditions:
        - All JavaScript dependencies from self.default_js are added to figure.header
        - All CSS dependencies from self.default_css are added to figure.header
        - The parent render method is called with all provided kwargs

## Side Effects:
    - Mutates the figure's header by adding child elements (JavascriptLink and CssLink)
    - Calls the parent Element.render() method

