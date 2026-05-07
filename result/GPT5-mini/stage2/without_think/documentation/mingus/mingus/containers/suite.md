# `suite.py`

## `mingus.containers.suite.Suite` · *class*

## Summary:
Represents a container ("suite") of Composition-like objects (objects exposing a 'tracks' attribute). Provides simple collection semantics (add, index, length) and metadata (title, subtitle, author, email, description).

## Description:
Use this class to group multiple Composition objects into a suite for higher-level organization and metadata attachment (title, subtitle, author, description). The class expects and enforces that added items expose a 'tracks' attribute (i.e., composition-like objects from the mingus.containers package). Typical callers:
- Code that assembles a set of Composition instances to be exported, rendered, or iterated as a group.
- Any factory or script that collects compositions and wants to annotate them with suite-level metadata.

Motivation and responsibility boundary:
- Suite is a lightweight collection abstraction: it does not implement composition manipulation or deep validation; it only enforces that members look like Composition objects by checking for a 'tracks' attribute.
- It manages only suite-level metadata and a sequence of compositions; responsibilities such as writing files or rendering are outside its scope.

## State:
Attributes (declared at class level; note implications below):
- title (str)
  - Default: "Untitled"
  - Meaning: primary title of the suite.
- subtitle (str)
  - Default: ""
  - Meaning: optional subtitle of the suite.
- author (str)
  - Default: ""
  - Meaning: author's name for the suite.
- email (str)
  - Default: ""
  - Meaning: author's contact email.
- description (str)
  - Default: ""
  - Meaning: free-form description of the suite.
- compositions (list)
  - Default: [] (class-level list)
  - Meaning: ordered list of Composition-like objects belonging to the suite.
  - Invariant intent: every entry in compositions should be a Composition-like object exposing a 'tracks' attribute.
  - Important implementation note: compositions is defined as a class attribute in the current implementation. That means the list is shared across all Suite instances unless an instance explicitly overrides it. This sharing is likely unintended and can cause surprising cross-instance mutation.

Constructor parameters:
- __init__() takes no parameters and performs no initialization. Because it does nothing, instances inherit the class-level defaults; callers should be aware of the shared-compositions caveat.

Class invariants (what should hold during normal use):
- Each element in self.compositions has attribute 'tracks'.
- title, subtitle, author, email, description are strings.
- len(self) matches len(self.compositions).

## Lifecycle:
Creation:
- Instantiate by calling Suite() with no arguments.
- Because __init__ does not initialize compositions as an instance attribute, an instance initially uses the class-level compositions list. To avoid cross-instance sharing, callers should assign an empty list to the instance explicitly (e.g., suite = Suite(); suite.compositions = []), or add the first composition which will append to the class list (thereby affecting other instances unless you override).

Usage (typical sequence):
- set_title(title, subtitle="") — set suite title/subtitle.
- set_author(author, email="") — set suite author/email metadata.
- add_composition(composition) or use the '+' operator (suite + composition) — validate and append a composition; returns self to allow chaining.
- Use len(suite), suite[index], or assign via suite[index] = composition.
- Iterate via indices or directly over suite.compositions.

Destruction / cleanup:
- No explicit cleanup API (no context manager, close, or similar). Because compositions is a normal list, clearing or replacing it is up to the caller.

Recommendations to callers:
- To avoid unexpected shared state across Suite instances, immediately after construction set suite.compositions = [] if you want an independent collection per instance.

## Method Map:
Mermaid flow (method dependencies & typical invocation relationships — plain mermaid lines without code fences):
graph LR
  set_title --> title
  set_author --> author
  add_composition --> compositions
  __add__ --> add_composition
  __len__ --> compositions
  __getitem__ --> compositions
  __setitem__ --> compositions

Description of the flow:
- __add__ delegates to add_composition.
- add_composition appends a validated composition to compositions.
- __len__, __getitem__, and __setitem__ operate directly on compositions.
- set_title and set_author update metadata fields.

## Methods (behavioral details necessary to reimplement):
- __init__(self)
  - No parameters. Does nothing. Consequence: instance attributes default to class-level values.
- add_composition(self, composition) -> Suite
  - Input: composition — any object.
  - Behavior: Validates by checking hasattr(composition, "tracks"). If not present, raises UnexpectedObjectError (see Raises). Otherwise appends composition to self.compositions and returns self (the same Suite instance) to allow chaining.
  - Edge cases: If self.compositions is the shared class-level list, append mutates that shared list.
- set_author(self, author, email="")
  - Inputs: author (str), email (str, optional; default "").
  - Behavior: Sets self.author and self.email. Returns None.
  - No validation of string types is performed by the current implementation.
- set_title(self, title, subtitle="")
  - Inputs: title (str), subtitle (str, optional; default "").
  - Behavior: Sets self.title and self.subtitle. Returns None.
- __len__(self) -> int
  - Behavior: Returns len(self.compositions).
  - Edge cases: If self.compositions is replaced with a non-list, len() behavior follows the container semantics of that value (may raise TypeError).
- __getitem__(self, index)
  - Input: index (int or slice)
  - Behavior: Returns self.compositions[index]. Indexing errors (IndexError) propagate from the underlying list.
- __setitem__(self, index, value)
  - Inputs: index (int or slice), value (object expected to be Composition-like).
  - Behavior: Validates value has attribute "tracks". If not, raises UnexpectedObjectError. Otherwise assigns value into self.compositions at index.
  - Errors: Underlying list assignment errors (IndexError, TypeError) will propagate if applicable.
- __add__(self, composition) -> Suite
  - Behavior: Delegates to add_composition(composition) and returns whatever add_composition returns (the Suite instance). Note: this means '+' mutates the left operand and returns it rather than creating a new Suite.

## Raises:
- UnexpectedObjectError
  - Raised by add_composition(composition) if composition lacks a 'tracks' attribute.
  - Raised by __setitem__(index, value) if value lacks a 'tracks' attribute.
  - The exception class is imported from mingus.containers.mt_exceptions; callers should import or catch this type from the same module.
- IndexError, TypeError (propagated)
  - __getitem__ and __setitem__ will propagate IndexError or TypeError originating from the underlying list operations.

## Example:
- Create a new suite and avoid shared-list pitfalls:
    suite = Suite()
    # To ensure this suite has its own compositions list (recommended)
    suite.compositions = []
    suite.set_title("Piano Works", "Volume 1")
    suite.set_author("Jane Doe", "jane@example.com")

    # Add a composition (must expose 'tracks')
    suite.add_composition(composition_obj)
    # or chain
    suite.add_composition(comp1).add_composition(comp2)
    # or use '+'
    suite + comp3

    # Access and replace by index
    first = suite[0]
    suite[0] = replacement_comp

    # Metadata is read directly
    print(suite.title, suite.author)

- Behavior when adding invalid object:
    try:
        suite.add_composition(object())  # arbitrary object missing 'tracks'
    except UnexpectedObjectError:
        # handle error: the object is not a Composition-like object
        pass

Notes and implementation caveats:
- Because the class defines compositions as a class attribute, newly created Suite instances share that single list by default. If independent instance state is required, callers must set suite.compositions = [] immediately after instantiation or the implementation should be modified to initialize compositions inside __init__.
- __add__ mutates the left-hand operand and returns it; it does not perform value-style immutable addition.

### `mingus.containers.suite.Suite.__init__` · *method*

## Summary:
Constructs a new Suite instance but performs no instance-specific initialization; the object will rely on class-level defaults (including a shared compositions list) unless callers set instance attributes after construction.

## Description:
Known callers and lifecycle stage:
- Called whenever a Suite is instantiated (e.g., suite = Suite()) by code that assembles a collection of Composition-like objects, factory functions that produce suites, or scripts that prepare suites for export/rendering.
- Invoked during object creation as the standard Python constructor (__init__) and is the first place to perform per-instance initialization if added later.

Why this logic is its own method:
- Providing an explicit __init__ method follows normal class design and allows subclasses to override or extend construction behavior without changing call sites.
- Although currently a no-op, keeping initialization logic in __init__ centralizes any future per-instance setup (for example, converting class-level defaults into instance attributes) rather than relying on ad-hoc code elsewhere.

## Args:
- None

## Returns:
- None (Python constructors return None). No value is returned to the caller.

## Raises:
- None. This method does not raise any exceptions.

## State Changes:
Attributes READ:
- None (the method body performs no reads of self.<attr>)

Attributes WRITTEN:
- None (the method body performs no writes to self.<attr>)

## Constraints:
Preconditions:
- No preconditions on arguments (there are none). The object may be instantiated in any state.

Postconditions:
- After the call completes:
  - The returned instance exists, but no instance attributes are created or modified by this method.
  - The instance will access class-level attributes (title, subtitle, author, email, description, compositions) as defined on the Suite class until or unless the caller assigns instance attributes explicitly.
  - In particular, compositions remains the class-level list unless the caller assigns self.compositions = [] (or another sequence) on the instance.

## Side Effects:
- None within this method: there is no I/O, no external service interaction, and no mutation of global or class-level state performed by the method itself.
- Indirectly, because no instance-specific compositions list is created, subsequent operations on the instance that mutate compositions (e.g., add_composition, __setitem__, append) will mutate the class-level compositions list unless the caller replaces it on the instance. That shared-mutable-class-attribute behavior is a consequence of the empty constructor, not a side effect produced during construction itself.

### `mingus.containers.suite.Suite.add_composition` · *method*

## Summary:
Appends a Composition-like object to this Suite's compositions list and returns the Suite (allows chaining).

## Description:
This method accepts an object that is expected to behave like a mingus.containers.Composition (it must expose a "tracks" attribute). It validates the incoming object and, if valid, appends it to this Suite's compositions collection and returns self.

Known callers and usage context:
- No specific internal callers are present in this file. Typical callers are client code or higher-level builders that assemble a Suite by adding Composition objects (for example, code that constructs or aggregates musical compositions into a Suite).
- This method is called during Suite construction/assembly, i.e., when building up the suite's list of compositions.

Why this is a separate method:
- Encapsulates validation and appending logic for compositions in one place to ensure all additions are consistently validated and to provide a fluent (chainable) API by returning self.

## Args:
    composition (object): An object expected to represent a composition. Required properties:
        - Must have an attribute named "tracks" (the code only checks presence via hasattr).
        - No specific type enforcement (duck-typed). Passing None or any object without "tracks" will trigger an error.

## Returns:
    self (Suite): The same Suite instance the method was called on. Useful for chaining calls (e.g., suite.add_composition(c1).add_composition(c2)).

Edge-case return behavior:
    - The method always returns self when it completes successfully. It never returns None on success.

## Raises:
    UnexpectedObjectError: Raised when the provided composition does not have a "tracks" attribute (i.e., hasattr(composition, "tracks") is False). The error message interpolates the passed object into the message.
    AttributeError: If this Suite instance does not have a compositions attribute (e.g., self.compositions is undefined), attempting to append will raise AttributeError. (This arises from the attribute access in the method and is not explicitly caught.)

## State Changes:
Attributes READ:
    - self.compositions (the list object is accessed to append to it)
Attributes WRITTEN:
    - self.compositions (the list is mutated by appending the provided composition)

## Constraints:
Preconditions:
    - The caller must pass an object that exposes a "tracks" attribute (duck-typed Composition).
    - The Suite instance should have a mutable sequence assigned at self.compositions (commonly a list) before calling this method.

Postconditions:
    - If no exception is raised, the provided composition is appended to self.compositions.
    - The method returns the Suite instance (self), preserving the appended state.

## Side Effects:
    - Mutates the Suite instance by appending an element to its compositions collection.
    - No I/O or external service calls are performed.
    - No deep-copying is done: the same composition object reference is stored in the list.

### `mingus.containers.suite.Suite.set_author` · *method*

## Summary:
Sets the Suite object's author and author email attributes, updating the object's metadata state.

## Description:
This method assigns the provided author name and email to the Suite instance. There are no internal checks or conversions performed; the values are stored exactly as passed.

Known callers:
- No specific internal callers are required by the repository (none discovered). Typical callers are client code or higher-level constructors/loader utilities that populate Suite metadata during object creation, editing, serialization, or export steps — for example, code that constructs a Suite from parsed input or a user-editing workflow that updates metadata.

Why this is a separate method:
- Centralizes assignment of two related metadata fields (author and email) so callers do not need to set attributes individually.
- Makes it easy to override or extend in subclasses to add validation, normalization, or side effects (e.g., notifications, persistence) without changing call sites.

## Args:
    author (str): The author name to store. No type coercion is performed; any value may be assigned, but the codebase typically expects a string. Required.
    email (str): The author's email address. Defaults to an empty string (""). Typically a string; no format validation is performed by this method.

## Returns:
    None

## Raises:
    None. This method performs simple attribute assignment and does not raise exceptions itself. (Note: if the object is implemented with attribute descriptors that raise on assignment, those errors may propagate.)

## State Changes:
Attributes READ:
    None

Attributes WRITTEN:
    self.author
    self.email

## Constraints:
Preconditions:
    - The caller should pass values appropriate for the application (usually strings). There is no runtime type enforcement here, so passing non-string values is allowed but may break downstream logic that expects strings.

Postconditions:
    - After the call, self.author is equal to the provided author argument.
    - After the call, self.email is equal to the provided email argument (or the default empty string when omitted).

## Side Effects:
    - No I/O, no external service calls.
    - Mutates only the Suite instance by setting the two attributes listed above; does not modify other objects.

### `mingus.containers.suite.Suite.set_title` · *method*

## Summary:
Sets the Suite object's title and subtitle, updating the object's metadata state.

## Description:
Sets two public metadata attributes on the Suite instance: title and subtitle. There are no validations or type checks — values are assigned directly to the instance attributes.

Known callers and typical context:
- No direct internal callers are present in the local class definition. This method is intended to be invoked by client code or higher-level application code when constructing or preparing a Suite (for example, immediately after instantiation and before exporting, rendering, or presenting the suite).
- Typical lifecycle stage: metadata population phase, i.e., after creating a Suite and before adding compositions or serializing the suite.

Why this logic is a dedicated method:
- Centralizes metadata assignment into a simple, discoverable public API on Suite rather than requiring callers to set attributes directly.
- Keeps attribute name usage consistent and provides a single location to extend or add validation later without changing external call sites.

## Args:
    title (str): The main title to assign to the Suite. No type enforcement is performed; any value will be stored as-is. Required.
    subtitle (str, optional): The subtitle to assign to the Suite. Defaults to an empty string (""). No type enforcement is performed.

## Returns:
    None: The method performs an in-place update of the Suite instance and does not return a value.

## Raises:
    None: This method does not raise any exceptions itself. (Note: other Suite methods may raise UnexpectedObjectError, but not this method.)

## State Changes:
    Attributes READ:
        None (the method does not read any existing attributes)
    Attributes WRITTEN:
        self.title
        self.subtitle

## Constraints:
    Preconditions:
        - The method must be called on a Suite instance (self must be a valid object).
        - There is no requirement on argument types enforced by the method; callers should provide strings to match intended usage.
    Postconditions:
        - After the call, self.title is equal to the provided title argument.
        - After the call, self.subtitle is equal to the provided subtitle argument (or the default "" if none provided).

## Side Effects:
    - Mutates the Suite instance by setting two instance attributes.
    - Does not perform I/O, network calls, or mutate objects external to self.
    - Because no validation occurs, passing non-string values (e.g., None, numbers, or objects) will store those values on the instance and may affect downstream code that expects strings.

### `mingus.containers.suite.Suite.__len__` · *method*

## Summary:
Returns the number of compositions currently held by the Suite instance as an integer, exposing the object's container size without modifying state.

## Description:
This method implements the Python container protocol's length operation so that built-in len(suite) returns the count of compositions stored in the Suite. Typical call sites are any code that queries the size of a Suite using len(...) — for example size checks, loops that iterate over or conditionally operate on the suite, or libraries and templates that rely on the container protocol. It exists as a dedicated method to satisfy the standard __len__ special-method API rather than inlining length checks at call sites.

Why separate method:
- Conformance: Defining __len__ is the canonical way in Python to make an object compatible with len() and other container behaviors.
- Encapsulation: Centralizes the single point of truth for how a Suite's size is determined (the compositions attribute), avoiding duplication across callers.

## Args:
    None

## Returns:
    int: The number of composition objects in self.compositions. Always a non-negative integer (0 or greater). If self.compositions is a sequence-like object, its __len__ result is returned.

Edge cases:
- If self.compositions has been replaced with an object that does not support len(), calling len(suite) will raise the standard TypeError produced by Python's built-in len() for that object.

## Raises:
    None explicitly in this method. Any exception raised will come from evaluating len(self.compositions) (e.g., TypeError if self.compositions does not support __len__).

## State Changes:
    Attributes READ:
        - self.compositions
    Attributes WRITTEN:
        - None

## Constraints:
    Preconditions:
        - The Suite object must have a compositions attribute that is a sequence or other object implementing __len__. By class definition, compositions is present (a list), but callers should be aware it can be reassigned.
        - No arguments; method expects to be called on a Suite instance.

    Postconditions:
        - No mutation to the Suite instance or its compositions list is performed.
        - The return value accurately reflects the current length of self.compositions at the moment of the call.

Important implementation note:
- In the current class definition, compositions is defined at class scope as an empty list (a mutable class attribute). This means multiple Suite instances will share the same default list unless compositions is reassigned on an instance (for example in __init__). This shared mutable default can cause surprising cross-instance effects: adding a composition to one Suite via add_composition will increase len(...) for all Suite instances that haven't overridden compositions on the instance. Consumers and implementers should consider initializing an instance-level list in __init__ if per-instance isolation is required.

## Side Effects:
    - None: this method performs no I/O, no external calls, and does not modify any objects (it only reads self.compositions).

### `mingus.containers.suite.Suite.__getitem__` · *method*

## Summary:
Returns the composition(s) at the given index from the Suite's internal compositions sequence without modifying the Suite.

## Description:
This method implements the sequence-access (indexing/slicing) behavior for a Suite instance by delegating directly to the underlying compositions container.

Known callers / invocation contexts:
- Client code that uses suite_instance[i] to access a single composition by index.
- Client code that uses suite_instance[start:stop] to obtain a slice (subsequence) of compositions.
- Any library or built-in routine that treats Suite as a sequence (e.g., iteration via the sequence protocol in environments that fall back to __len__+__getitem__), or code that uses indexing in workflows that manipulate a collection of compositions.

Why this logic is a separate method:
- Providing __getitem__ enables Suite to behave like a Python sequence (indexable / sliceable) and to interoperate with language features and libraries that expect sequence semantics. Keeping it as a thin, dedicated method keeps indexing semantics consistent (delegated to the underlying list) and centralizes any future changes to how Suite exposes indexed access.

## Args:
    index (int | slice | object):
        - Any index accepted by Python's list.__getitem__.
        - Typical values:
            * int (including negative indices)
            * slice (start:stop:step)
            * objects implementing the __index__ protocol
        - No default; required positional argument.

## Returns:
    mingus.containers.Composition or list[mix of Composition]:
        - If `index` is an integer (or index-like), returns the single Composition object at that position.
        - If `index` is a slice, returns a list of Composition objects corresponding to the slice.
        - Behaves identically to list.__getitem__ on the Suite.compositions container.

## Raises:
    IndexError:
        - Propagated when an integer index is out of range for the compositions list.
    TypeError:
        - Propagated when the provided index type is invalid for list indexing (e.g., an unsupported type).
    (No method-specific exceptions are raised; exceptions are those raised by the underlying list access.)

## State Changes:
    Attributes READ:
        - self.compositions
    Attributes WRITTEN:
        - None (this method does not modify any attributes or the compositions list)

## Constraints:
    Preconditions:
        - self.compositions must be a sequence object supporting Python list-style indexing (the current implementation uses a list).
        - The Suite instance should have a properly initialized compositions container; note that in this implementation compositions is declared at class-level as a mutable list, which means it may be shared across Suite instances unless overridden per-instance (this sharing can lead to surprising behavior).
    Postconditions:
        - No changes to Suite or to elements of self.compositions are made by this call.
        - The return value corresponds exactly to what list.__getitem__ would return for self.compositions with the provided index.

## Side Effects:
    - None: the method performs no I/O, no external service calls, and does not mutate objects outside of returning a reference (or a new list for slices). Any mutation of returned objects is up to the caller.

Implementation note for reimplementers:
- The correct, minimal implementation is to delegate to the underlying compositions container:
    return self.compositions[index]
- Ensure the compositions attribute exists and is a list-like sequence. If you want to avoid the class-level mutable-list pitfall, initialize compositions per-instance inside __init__ (e.g., self.compositions = []).

### `mingus.containers.suite.Suite.__setitem__` · *method*

## Summary:
Set the composition stored at a given index in the Suite's compositions collection after validating the value implements the expected Composition interface (has a "tracks" attribute). Mutates the Suite's compositions list in-place.

## Description:
This method implements the sequence-assignment behavior for Suite objects (it is what Python calls when executing suite[index] = value). Typical callers are client code or higher-level utilities that modify a Suite by replacing an existing composition at a specific position during composition management or editing workflows. It is separated into its own method to:
- Provide consistent runtime validation (raise a specific UnexpectedObjectError when the value is not a Composition-like object).
- Preserve the Suite object's sequence semantics (supporting idiomatic assignment syntax).
- Centralize the in-place mutation logic so other code paths can reuse the same validation and mutation behavior.

Known callers / usage context:
- Client code assigning a composition into a Suite: suite[0] = some_composition
- Any code that programmatically replaces an element in the suite's compositions list and relies on the Suite's validation.

Why this logic is a method:
- It implements the Python sequence protocol's item assignment hook while enforcing type/contract checking before mutating internal state. This keeps validation and state manipulation consistent and discoverable.

## Args:
    index (int): The position in the suite's compositions list to assign. Expected to be an integer index that refers to an existing element. Using a slice for index is not supported by the method's validation (see Constraints).
    value (object): The object to store at the given index. Must implement the Composition interface minimally by exposing a "tracks" attribute (i.e., hasattr(value, "tracks") must be True).

## Returns:
    None

## Raises:
    UnexpectedObjectError:
        - Trigger: When the passed value does not expose a "tracks" attribute (the code checks with hasattr(value, "tracks") and raises when False).
        - Message (constructed by the method):
          "Object '%s' is not expected. Expecting a mingus.containers.Composition object." % value
    IndexError:
        - Trigger: When the provided integer index is out of range for the underlying list (this arises from the underlying list assignment self.compositions[index] = value).
    TypeError:
        - Possible Trigger: If a non-integer index is passed that the underlying list does not accept (the built-in list will raise TypeError). Note: the method does not perform explicit index-type validation.

## State Changes:
    Attributes READ:
        - self.compositions (reads the attribute to perform validation/assignment)
    Attributes WRITTEN:
        - self.compositions (mutates the list in-place by assigning self.compositions[index] = value)

## Constraints:
    Preconditions:
        - self.compositions must exist and behave like a Python list (supporting index assignment).
        - The caller should pass an integer index that addresses an existing element; otherwise an IndexError will be raised by the list.
        - The value must implement a "tracks" attribute (this is used as a runtime contract check for a Composition-like object).
    Postconditions:
        - After successful return, the element at the specified index in self.compositions is the provided value.
        - No other attributes on self are modified by this method.

Important note about slice/index semantics:
    - Although Python lists accept slice assignment (e.g., compositions[1:3] = [...]), this method's validation checks for hasattr(value, "tracks") on the provided value. That check expects a single Composition-like object, not an iterable of such objects. As a result, attempting slice assignment with an iterable of Composition objects will typically fail the validation and raise UnexpectedObjectError. Therefore, callers should use integer index assignment to replace a single composition. If slice semantics are required, perform mutations on suite.compositions directly or add a dedicated method that validates and assigns sequences.

## Side Effects:
    - In-place mutation of the internal compositions list (no copies made).
    - No I/O or external service calls are performed.
    - Potentially raises exceptions as described above which propagate to the caller if not caught.

## Implementation hints (for reimplementation):
    - Perform a runtime contract check on value using hasattr(value, "tracks") and raise UnexpectedObjectError with the exact message shown if the check fails.
    - Use direct list assignment self.compositions[index] = value to replace the element; allow the underlying list to raise IndexError/TypeError for invalid indices.
    - Keep the method concise to preserve the sequence protocol behavior and centralized validation.

### `mingus.containers.suite.Suite.__add__` · *method*

## Summary:
Delegates adding a composition to the Suite by forwarding the object to add_composition; appends the composition to the suite's compositions list (which may be the class-level list) and returns the Suite instance.

## Description:
This magic method implements the left-hand addition operator for Suite instances, enabling usage such as:
    suite + composition
It simply calls Suite.add_composition(composition) and returns whatever that method returns (currently self). The primary validation and mutation logic lives in add_composition; __add__ exists solely to provide an operator-based convenience.

Known callers and invocation context:
- Invoked when a Suite instance appears on the left side of the binary + operator and a composition-like object appears on the right (e.g., suite + comp).
- Not called directly within the repository other than operator use — callers are external code or tests that use the + operator as syntactic sugar for add_composition.
- Because add_composition returns self, chained additions like (suite + comp1 + comp2) will work: the first + returns the Suite instance again so the second + is applied to Suite.

Why this is a separate method:
- Keeps the validation and append logic centralized in add_composition while providing a small, readable operator shim for callers. This separation avoids duplicating validation and keeps operator behavior consistent with direct method calls.

## Args:
    composition (object): Any object expected to behave like a Composition. Required to have a 'tracks' attribute (checked with hasattr(composition, "tracks")). No further interface is enforced by this method.

## Returns:
    Suite: The same Suite instance (self) after delegating to add_composition. This enables chaining of additions. There are no other return cases in the current implementation.

## Raises:
    mingus.containers.mt_exceptions.UnexpectedObjectError:
        Raised by add_composition if the provided composition does not have a 'tracks' attribute. The exact message constructed by add_composition is:
        "Object '%s' not expected. Expecting a mingus.containers.Composition object." % composition

## State Changes:
    Attributes READ:
        self.compositions — the attribute is looked up to obtain the list (or to fall back to a class-level list).

    Attributes WRITTEN:
        self.compositions — mutated by appending the provided composition (self.compositions.append(composition)). Note: if self has no instance attribute named compositions, this will mutate the class-level list defined on Suite.

## Constraints:
    Preconditions:
        - The left-hand operand must be a Suite instance (Python ensures this when dispatching __add__).
        - The composition argument must have a 'tracks' attribute (hasattr(composition, "tracks") == True).
        - self.compositions must be a mutable sequence supporting append (Suite defines a list by default).

    Postconditions:
        - If no exception is raised, the composition object is appended to the compositions list reachable as self.compositions.
        - The method returns the Suite instance (self), allowing further chained additions.

Important implementation note (class-level mutable default):
- Suite defines compositions = [] at the class level and __init__ does not create an instance-specific list. As a result, unless an instance assigns a new list to self.compositions, all Suite instances share the same compositions list. Calling suite.add_composition(...) or suite + composition will append to that shared list and thus affect other Suite instances that have not overridden compositions on the instance.

## Side Effects:
    - Mutates the Suite instance (or the Suite class-level list) by appending the composition object.
    - No I/O, network, or external service calls occur in this method itself (behavior is delegated to add_composition which only mutates in-memory state).
    - __radd__ is not implemented; expressions with a composition on the left (composition + suite) will not invoke Suite.__add__ and will instead attempt the right-hand object's __radd__ or fall back to TypeError if not supported.

