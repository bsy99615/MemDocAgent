# `dropdown.py`

## `src.ydata_profiling.report.presentation.flavours.widget.dropdown.WidgetDropdown` · *class*

## Summary:
A concrete Dropdown presentation widget that builds an ipywidgets.Dropdown and a linked child widget; selecting an option updates the child's selected_index to keep the displayed child in sync with the dropdown value.

## Description:
WidgetDropdown is a presentation-layer component (subclassing Dropdown) that composes an ipywidgets.Dropdown with another (child) widget produced by the content["item"]. It is intended to be used in contexts where a report or UI needs a simple dropdown to switch the visible/selected entry of an already-existing child widget (the child must expose a selected_index attribute and a render() method).

Typical instantiation pattern (driven by the report/presentation factory in the codebase):
- A Dropdown-derived object is created/populated so that self.content contains:
  - "items": options passed to ipywidgets.Dropdown
  - "name": string used as the dropdown description
  - "item": a child presentation object with .content["items"] and a render() method
- Call render() to obtain a vertical layout widget (ipywidgets.VBox) containing the dropdown and the rendered child widget.

Motivation / responsibility boundary:
- This class is the glue between a plain list of option values (self.content["items"]) and a child presentation widget that represents selectable entries. It does not manage creation of the child object (that is the caller/factory's responsibility); instead it reads an existing child object from self.content and connects dropdown changes to the child's selected_index.

## State:
- Instance attribute (used by this class; defined/initialized by the base class or caller):
  - self.content (dict): required keys and expected shapes:
    - "items": sequence or mapping acceptable to ipywidgets.Dropdown as its options parameter. The code passes this value directly to widgets.Dropdown(options=...).
    - "name": str used for widgets.Dropdown(description=...). The code expects this to be a human-readable label.
    - "item": expected to be either:
        - a presentation object (NOT None) that has:
            - content (dict) with key "items" whose value is an iterable of objects; each object in that iterable must have a .name attribute (used to build titles list), and
            - a render() method that returns a widget instance (the code expects the returned widget to have a writable attribute selected_index, allowing an integer index or None).
        - If "item" is None or missing, behavior is not safe (see Raises).
- Local variables inside render() (ephemeral state):
  - dropdown: ipywidgets.Dropdown instance with options=self.content["items"] and description=self.content["name"].
  - titles: list[str] built from the .name attributes of the elements in self.content["item"].content["items"].
  - item (reused variable): first assigned to self.content["item"].content["items"], then reassigned to the widget returned by self.content["item"].render().

Class invariants:
- After successful render(), the returned structure should be an ipywidgets vertical container that contains the dropdown and the child's rendered widget, and the dropdown is observing changes to keep item.selected_index in sync.
- The code assumes self.content contains the required keys before calling render() — violations will raise immediately.

## Lifecycle:
Creation:
- No __init__ is defined in WidgetDropdown; object creation follows the base class' initializer. Before calling render(), ensure:
  - self.content is set and contains "items", "name", "item"
  - self.content["item"] is a valid presentation object (not None) with the described shape.

Usage:
1. Call instance.render().
2. render() constructs an ipywidgets.Dropdown and a rendered child widget (by calling child.render()).
3. The dropdown is wired with an observer (dropdown.observe) on the "value" field. When the dropdown value changes:
   - If dropdown.value == "" then the child widget's selected_index is set to None.
   - Otherwise the code walks titles (derived from child.content["items"] names) to find the matching title and sets child.selected_index to the corresponding index.
4. The returned widget (widgets.VBox) is ready to be placed into an ipywidgets display/layout or returned to a caller that aggregates presentation elements.

Destruction / cleanup:
- There is no explicit cleanup method or context-manager behavior. The observer is attached to the dropdown object and will remain active while the dropdown exists. If you remove/dispose of the widget, typical ipywidgets disposal semantics apply; no special teardown is provided by this class.

## Method Map:
(graphical depiction of call flow — mermaid flowchart)
flowchart LR
    render --> create_dropdown[Create widgets.Dropdown(options=content["items"], description=content["name"])]
    render --> build_titles[Read content["item"].content["items"] -> build titles list from .name]
    render --> render_child[child_widget = content["item"].render()]
    create_dropdown --> observe[dropdown.observe(change_view, names=["value"])]
    build_titles --> observe
    render_child --> observe
    observe --> change_view_fn[change_view: sets child_widget.selected_index based on dropdown.value]
    render --> return_box[Return widgets.VBox([dropdown, child_widget]) (or widgets.Vbox([dropdown]) in the else branch)]

## Behavior detail (render method):
- Signature: render(self) -> widgets.VBox (annotation present)
- What it does (step-by-step):
  1. Instantiates dropdown = widgets.Dropdown(options=self.content["items"], description=self.content["name"]).
  2. Builds titles list by iterating over self.content["item"].content["items"] and collecting each element's .name attribute.
  3. Replaces local variable item with the widget returned by self.content["item"].render().
  4. Defines change_view(widg: dict) which:
      - checks dropdown.value; if it's the empty string "", sets item.selected_index = None.
      - otherwise finds the index i for which titles[i] == dropdown.value and sets item.selected_index = i.
  5. Attaches the observer: dropdown.observe(change_view, names=["value"]).
  6. If self.content["item"] is not None, returns widgets.VBox([dropdown, item]); otherwise returns widgets.Vbox([dropdown]). Note: the latter line in the source uses widgets.Vbox (lowercase 'b' in Vbox) which is not the same symbol as widgets.VBox and will raise an AttributeError at runtime.

## Raises:
All listed raise conditions are direct consequences of the source code (not extra assumptions):
- KeyError
  - If self.content is missing any of the keys "items", "name", or "item", a KeyError is raised when render() attempts to access them (e.g., self.content["item"]).
- AttributeError
  - If self.content["item"] is None, the code accesses self.content["item"].content which will raise AttributeError because None has no attribute content.
  - If the else branch is taken (self.content["item"] is None), the source code attempts to return widgets.Vbox([dropdown]) — ipywidgets exports VBox (capital B). Attempting to access widgets.Vbox will raise AttributeError at runtime. This typo is present in the source and will raise when that branch executes.
  - If the child rendered widget returned by content["item"].render() does not provide a writable selected_index attribute, attempts to assign item.selected_index = ... inside change_view will raise AttributeError.
- ValueError / IndexError (implicit potential issues)
  - If dropdown.value is not present in titles and is not the empty string, change_view will iterate and simply not set selected_index. No explicit exception is raised by the loop, but callers/consumers of the child widget who expect selected_index to be synchronized may observe an unexpected state. (No explicit exception is raised by the code for this case.)

## Example (usage guidance in prose):
- Ensure you have a presentation child object configured:
  - child.presentation.content["items"] is an iterable of objects with a .name attribute (these names will be used for matching).
  - child.presentation.render() returns a widget object exposing a writable selected_index attribute (int or None).
- Prepare self.content as a dict with keys:
  - "items": options to show in the dropdown (these should correspond to the names you expect to match against the child .name values),
  - "name": a label string,
  - "item": the child presentation object described above.
- Call render() on the WidgetDropdown instance to receive a vertical layout widget combining the dropdown and the child. Place this returned widget into your ipywidgets layout or display pipeline.
- Note: do not set content["item"] to None unless you intend to handle the AttributeError (the source attempts to access child.content before the None-check and will fail). Also be aware of the widgets.Vbox typo in the else branch — avoid relying on the else branch.

### `src.ydata_profiling.report.presentation.flavours.widget.dropdown.WidgetDropdown.render` · *method*

## Summary:
Constructs an ipywidgets VBox containing a Dropdown widget and the rendered child item, wires the dropdown value to control the child's selected_index, and returns the assembled VBox.

## Description:
This method is called by the presentation/rendering pipeline when a Dropdown-style Renderable must produce an interactive ipywidgets representation for display in an interactive report (e.g., Jupyter notebook). Typical callers are renderer code or higher-level UI assembly utilities that traverse the presentation tree and call render() on Renderable subclasses to obtain widget trees.

The method is separated into its own function because it encapsulates:
- creation and configuration of the ipywidgets.Dropdown (options, description),
- extraction of per-item titles from the child Container,
- rendering of that child Container into a selectable widget,
- wiring an event observer so that changing the dropdown value updates the child's selection.

Keeping this logic in one method keeps widget construction and callback wiring localized and reusable by subclasses or tests.

## Args:
None (the method uses instance state via self.content).

Relevant self.content keys (preconditions; documented here because they are the method's inputs):
    - content["items"] (list): The sequence passed to ipywidgets.Dropdown as options. Expected to be a sequence of values (commonly strings) that match the names extracted from the child Container items.
    - content["name"] (str): The human-readable label shown as the Dropdown description.
    - content["item"] (Container-like Renderable): A Container Renderable that provides per-entry structure. Must be non-None and must itself expose:
        - .content["items"]: a sequence of item objects whose .name attributes are used as option labels mapping.
        - .render(): returns a widget-like object that supports assignment to selected_index.

## Returns:
widgets.VBox
    - When content["item"] is present and usable: an ipywidgets.VBox containing two children:
        1. The ipywidgets.Dropdown instance (options=self.content["items"], description=self.content["name"])
        2. The result of content["item"].render() (a widget supporting selection via .selected_index)
    - If content["item"] is None: the code intends to return a VBox with only the dropdown, but due to accessing content["item"] earlier the None case is effectively unreachable in practice (see Constraints and Raises). Note: the implementation returns widgets.Vbox (lowercase 'v') in the else branch which will raise AttributeError at runtime; this is a bug in the implementation.

Edge-case return values:
    - The method will not successfully return if required content keys or attributes are missing; exceptions (KeyError/AttributeError/TypeError) will be raised instead of a widget.

## Raises:
The method relies on several structural assumptions; violations produce the following exceptions:
    - KeyError: if self.content does not contain "items", "name", or "item".
    - AttributeError:
        * If self.content["item"] is None (the code later accesses content["item"].content) — this will raise when trying to access attributes on None.
        * If content["item"] lacks .content or .content["items"], or if objects in that list do not have a .name attribute.
        * If content["item"].render() does not return an object with a writable .selected_index attribute and later code attempts to assign to it.
        * If the unreachable else branch executes (content["item"] is None) the returned widgets.Vbox will raise AttributeError because ipywidgets.Vbox does not exist (should be VBox).
    - TypeError:
        * If content["items"] is not an appropriate sequence for ipywidgets.Dropdown.options.
        * If elements of content["item"].content["items"] do not expose .name (e.g., are plain strings) and code expects attribute access.
    - Any exception raised by content["item"].render() will propagate.

## State Changes:
Attributes READ:
    - self.content["items"]
    - self.content["name"]
    - self.content["item"]
    - self.content["item"].content["items"]
    - elements' .name attributes in self.content["item"].content["items"]

Attributes WRITTEN (on objects reachable from content, not on self):
    - The rendered child widget's selected_index attribute is mutated by the change_view callback:
        - item.selected_index is set to None when dropdown.value == ""
        - item.selected_index is set to an integer index corresponding to the matched title when dropdown.value matches one of the titles
    - An observer callback is registered on the created dropdown (dropdown.observe(...)) — this mutates the dropdown's internal observer list but not self.

The method does not modify self or self.content.

## Constraints:
Preconditions:
    - self.content must be a dict-like mapping containing keys "items", "name", and "item".
    - content["item"] must be a non-None Renderable-like object that:
        * has a .content mapping with key "items" that is an ordered sequence,
        * each element in that sequence exposes a .name attribute (string),
        * has a .render() method that returns a widget-like object with a writable selected_index attribute.
    - content["items"] (passed to dropdown.options) must contain values that are comparable to the .name strings extracted from the child Container's items (the change_view callback compares dropdown.value to those names).
    - The runtime environment must have ipywidgets available (widgets.Dropdown, widgets.VBox).

Postconditions (guarantees after a successful call):
    - A widgets.VBox is returned containing the Dropdown and the rendered child widget (assuming preconditions satisfied).
    - The returned dropdown is observing changes to its "value" trait; changing the dropdown's value will update the child's selected_index accordingly (None if value == "", otherwise set to the matching index).
    - No attributes on self are modified.

## Side Effects:
    - Registers an event observer on the constructed ipywidgets.Dropdown (dropdown.observe(...)) which will remain active for the lifetime of the returned dropdown widget.
    - Mutates the rendered child widget's selected_index when the dropdown value changes (user interaction).
    - No file I/O, network calls, or external service interactions are performed.

Implementation notes / Known implementation defects:
    - The method accesses self.content["item"].content["items"] before checking whether content["item"] is None; therefore content["item"] must be non-None or an AttributeError will be raised. The later conditional that attempts to handle the None case is effectively unreachable as written.
    - The else branch returns widgets.Vbox (lowercase 'v') which is likely a typo and will raise AttributeError; the intended return is widgets.VBox([dropdown]).
    - The mapping between dropdown.options and the titles extracted from content["item"].content["items"] is implicit. For correct behavior, content["items"] must contain values equal to those .name strings (including an empty-string option when a "no selection" state is desired).

