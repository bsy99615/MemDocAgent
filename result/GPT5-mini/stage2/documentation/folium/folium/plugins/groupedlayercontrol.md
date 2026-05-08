# `groupedlayercontrol.py`

## `folium.plugins.groupedlayercontrol.GroupedLayerControl` · *class*

## Summary:
Represents a Folium MacroElement that integrates the Leaflet Grouped Layer Control plugin, organizing overlay layers into named groups and computing which layers should be initially untoggled. It provides the metadata (grouped overlays and untoggled layer names) consumed by the rendering template/JS.

## Description:
Use this class when you have multiple overlay Layer-like objects that should be presented in grouped controls (group headings with checkboxes/radios) on a Folium map. Instantiate it after grouping related overlay elements into ordered sequences and add the instance to a folium.Map so the MacroElement rendering system can include the grouped control's assets and data.

Responsibility boundary:
- Collects group->layers mapping and initial visibility state.
- Mutates each provided element by setting element.control = False so that the grouped control exclusively manages layer visibility controls.
- Exposes grouped_overlays and layers_untoggle for the template/JS to render grouped controls and initialize visibility.

Typical callers:
- Client code assembling overlays and attaching UI controls to a folium.Map.
- Higher-level factories that package overlay elements into logical groups before adding controls.

## State:
Class attributes:
- default_js (list[tuple[str, str]]): JS asset filename/URL pairs required by the plugin (defined on the class).
- default_css (list[tuple[str, str]]): CSS asset filename/URL pairs required by the plugin.
- _template (jinja2.Template): a Template instance (empty in the source) used by MacroElement for rendering.

Instance attributes (set in __init__):
- _name (str): "GroupedLayerControl". Identifies the element; set once at construction.
- options (dict): result of parse_options(**kwargs); holds forwarded configuration options. If exclusive_groups is True, options["exclusiveGroups"] is set to list(groups.keys()).
  - Caller constraint: kwargs must be acceptable to parse_options; parse_options may raise exceptions which will propagate.
- layers_untoggle (set[str]): set of layer instance names (element.get_name()) that should be initialized as untoggled/hidden. Populated from:
  - elements with element.show == False
  - when exclusive_groups is True: every element in each group's list except the first element
  - Invariant: all items are names returned by element.get_name().
- grouped_overlays (dict[str, dict[str, str]]): mapping group_name -> { element.layer_name: element.get_name() } for each element in the provided groups mapping.
  - Invariant: keys(grouped_overlays) == keys(groups) provided at construction.

Expectations about elements passed in groups:
- Each element must expose:
  - attribute layer_name (str)
  - method get_name() -> str
  - attribute show (truthy/falsey)
  - attribute control (assignable)
- If an element lacks these, attribute access or assignment will raise AttributeError.

## Lifecycle:
Creation:
- Signature: GroupedLayerControl(groups, exclusive_groups=True, **kwargs)
  - groups: mapping[str, Sequence[element]] — required. The constructor iterates groups.items().
  - exclusive_groups: bool — default True. When True, options["exclusiveGroups"] is set and all but the first element of each group's sequence are added to layers_untoggle.
  - **kwargs: forwarded to parse_options(...), result stored in options.

Construction steps (performed in __init__):
1. Calls super().__init__() (MacroElement / JSCSSMixin initialization).
2. Sets self._name = "GroupedLayerControl".
3. Calls parse_options(**kwargs) and assigns to self.options.
4. If exclusive_groups is True, sets self.options["exclusiveGroups"] = list(groups.keys()).
5. Initializes empty self.layers_untoggle (set) and self.grouped_overlays (dict).
6. Iterates over group_name, sublist in groups.items():
   - Creates grouped_overlays[group_name] = {}
   - For each element in sublist:
     - Sets grouped_overlays[group_name][element.layer_name] = element.get_name()
     - If not element.show: adds element.get_name() to layers_untoggle
     - Sets element.control = False
   - If exclusive_groups is True: adds element.get_name() for every element in sublist[1:] to layers_untoggle

Usage:
- Add the instance to a folium.Map (via add_child or add_to) so MacroElement rendering can embed the control.
- The rendering/template layer reads grouped_overlays and layers_untoggle to build the grouped UI and initialize which layers are visible.
- There are no additional public methods defined by this class; interaction is through construction and map attachment.

Destruction / cleanup:
- No explicit cleanup API. The constructor mutates element.control = False and does not revert it on deletion; callers who need to reverse this must do so explicitly.

## Method Map:
flowchart TD
    A[__init__(groups, exclusive_groups=True, **kwargs)]
    A --> B[super().__init__()]
    A --> C[options = parse_options(**kwargs)]
    C --> D{exclusive_groups True?}
    D -- yes --> E[options["exclusiveGroups"]=list(groups.keys())]
    A --> F[for group_name, sublist in groups.items():]
    F --> G[grouped_overlays[group_name] = {}]
    G --> H[for element in sublist:]
    H --> I[grouped_overlays[group_name][element.layer_name] = element.get_name()]
    H --> J[if not element.show: layers_untoggle.add(element.get_name())]
    H --> K[element.control = False]
    F --> L[if exclusive_groups: add sublist[1:] element.get_name() to layers_untoggle]

## Raises:
- AttributeError:
  - If the provided groups object does not support .items(), Python will raise AttributeError (e.g., 'list' object has no attribute 'items').
  - If an element in a group's sequence lacks required attributes/methods (layer_name, show, get_name, or assignment to control), attribute access/assignment will raise AttributeError.
- Any exception raised by parse_options(**kwargs) will propagate (parse_options behavior is external to this class).

## Example:
1) Prepare grouped overlays:
   - groups = {
       "Base Layers": [layer_a, layer_b],
       "Overlays": [overlay_1, overlay_2, overlay_3],
     }
   where each layer_* or overlay_* provides:
     - layer_name (str), get_name() -> str, show (bool), and allows setting .control.

2) Instantiate:
   - glc = GroupedLayerControl(groups, exclusive_groups=True, some_option=value)

3) Add to map:
   - glc.add_to(my_map)  (or my_map.add_child(glc))

4) Outcome:
   - The template/JS receives grouped_overlays mapping and layers_untoggle set to render grouped controls and initial visibility. Note: element.control attributes have been set to False during construction.

### `folium.plugins.groupedlayercontrol.GroupedLayerControl.__init__` · *method*

## Summary:
Initializes the GroupedLayerControl instance by recording provided layer groups and computing which overlay layer names must start untoggled; stores parsed options and mutates provided overlay elements so the grouped control exclusively manages their visibility.

## Description:
This constructor is invoked when a GroupedLayerControl is created — typically by client code that has already organized overlay-like objects into named groups and is preparing to add the control to a folium.Map. It runs during object construction (creation phase) and prepares the instance state that the MacroElement rendering pipeline (templates and JavaScript) will later consume.

Known callers / contexts:
- Client code that groups Layer-like objects and creates a GroupedLayerControl to add to a folium.Map.
- Factory functions or higher-level APIs that assemble grouped overlays and then instantiate this control prior to attaching it to a map.
- Lifecycle stage: instantiate → configure → add_to(map) so MacroElement rendering can include the grouped control.

Why this logic lives in __init__:
- The method collects and normalizes ephemeral input (groups mapping, kwargs) into persistent instance state used by rendering.
- It must mutate the passed elements (setting element.control = False) at construction time so the rest of the map/element lifecycle never uses the default layer controls for those elements.
- Keeping this initialization together avoids duplicating parsing, grouping, and mutation logic elsewhere.

## Args:
    groups (Mapping[str, Sequence[object]]):
        - Required.
        - A mapping from group name (string) to an ordered sequence (list/tuple) of element objects.
        - Each element object is expected to provide:
            * attribute layer_name (str) — used as the human-visible label for the element within its group
            * method get_name() -> str — returns the unique instance name used in the map/template
            * attribute show (truthy/falsey) — whether the element should be initially shown; False means the layer name is added to layers_untoggle
            * assignable attribute control — will be set to False by the constructor
        - If groups does not provide .items(), an AttributeError will be raised by Python when the constructor iterates it.

    exclusive_groups (bool, optional):
        - Default: True.
        - When True:
            * options["exclusiveGroups"] is set to list(groups.keys()) in the stored options dict.
            * For each group, every element except the first (sublist[1:]) is added to layers_untoggle to ensure only one overlay per group is toggled on by default.
        - When False: no exclusiveGroups option is added and no extra per-group untoggling behavior is applied beyond element.show flags.

    **kwargs:
        - All additional keyword arguments are forwarded to parse_options(**kwargs).
        - The returned dict from parse_options is stored in self.options.
        - Any exception raised by parse_options propagates out of the constructor.

## Returns:
    None
    - As a constructor, it does not return a value; it configures the new instance in-place.

## Raises:
    AttributeError:
        - If groups does not support .items() (e.g., passing a list instead of a mapping) an AttributeError will occur when iterating.
        - If any element in a group's sequence lacks the expected attributes or methods (layer_name, get_name, show, or assignable control), attribute access or assignment will raise AttributeError.
    Any exception raised by parse_options(**kwargs):
        - parse_options may validate or transform kwargs and raise exceptions; these propagate unchanged.

## State Changes:
    Attributes READ:
        - (none) — the method does not read existing self.<attr> attributes; it constructs and assigns fresh attributes.

    Attributes WRITTEN:
        - self._name: set to the literal string "GroupedLayerControl".
        - self.options: assigned to the dict returned by parse_options(**kwargs); possibly mutated to include "exclusiveGroups".
        - self.layers_untoggle: set to a newly created set() and populated with element instance names (element.get_name()) based on element.show and exclusive_groups rules.
        - self.grouped_overlays: set to a newly created dict mapping each group_name -> { element.layer_name: element.get_name(), ... }.

    External object mutations (side-effect on inputs):
        - For every element in every group's sequence, the constructor sets element.control = False (mutates the passed objects).
        - The constructor calls element.get_name() and reads element.layer_name and element.show on each element.

## Constraints:
    Preconditions:
        - groups must be a mapping-like object providing .items() that yields (group_name, sublist) pairs.
        - Each sublist must be an iterable of element objects that satisfy the element interface described in Args.
        - kwargs must be valid for parse_options; otherwise parse_options may raise.
        - Caller should expect element.get_name() to return unique string identifiers for the map layer naming to avoid collisions in layers_untoggle and grouped_overlays.

    Postconditions:
        - self._name == "GroupedLayerControl".
        - self.options is a dict produced by parse_options; if exclusive_groups is True then self.options contains the key "exclusiveGroups" whose value is list(groups.keys()).
        - self.grouped_overlays contains an entry for every group_name from groups; for each element in a sublist the mapping grouped_overlays[group_name][element.layer_name] == element.get_name().
        - self.layers_untoggle contains:
            * element.get_name() for every element whose element.show is falsy, and
            * if exclusive_groups is True, element.get_name() for every element in each group's sublist except the first element in that sublist.
        - Every provided element has been mutated such that element.control == False.

## Side Effects:
    - Mutates input element objects by setting element.control = False.
    - Calls element.get_name() (may execute arbitrary user code).
    - May raise exceptions originating from parse_options or from attribute/method access on provided elements, which propagate to the caller.
    - No I/O operations or external network/service calls are performed by the constructor itself.

## Edge cases and notes:
    - Empty groups mapping: grouped_overlays will be an empty dict; if exclusive_groups is True, options["exclusiveGroups"] will be an empty list.
    - Empty sublists: grouped_overlays will contain the group name mapped to an empty dict; no elements are mutated for that group.
    - If the first element in a group's sublist has show == False, it will be added to layers_untoggle regardless of exclusive_groups because element.show is always respected.
    - Uniqueness of element.get_name() values is assumed but not enforced; duplicate names may produce unexpected behavior in the rendered control.
    - The constructor intentionally mutates element.control to False so the grouped control is the single source of truth for visibility; callers who need to restore previous control behavior must do so manually.

