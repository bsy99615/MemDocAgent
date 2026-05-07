# `warnings.py`

## `jwt.warnings.RemovedInPyjwt3Warning` · *class*

## Summary:
A named DeprecationWarning subtype used by the jwt package to mark deprecations (a distinct warning class that can be filtered or targeted separately).

## Description:
RemovedInPyjwt3Warning exists to provide a distinct warning type that library code can raise when a feature is deprecated and intended for removal in the next major bump. Because it is a subclass of DeprecationWarning, it integrates with Python's warnings system and can be issued via warnings.warn(..., RemovedInPyjwt3Warning) or filtered/handled independently using warnings.filterwarnings or warnings.simplefilter.

Typical call sites
- Library internal code that detects the use of deprecated functionality will call warnings.warn("message", RemovedInPyjwt3Warning).
- Test code or downstream applications can filter these warnings by class to treat them differently from generic DeprecationWarning.

Motivation and responsibility
- Providing a distinct subclass allows the library to (a) clearly label deprecations that will be removed in a particular future release and (b) let consumers selectively catch or filter only those deprecations without affecting other DeprecationWarning instances.
- The class has no behavior beyond being an identifiable type; its responsibility is purely semantic and for warning classification.

## State:
- This class declares no instance attributes of its own.
- Inherits all attributes and behavior from DeprecationWarning (a built-in Warning subclass).
- There are no constructor parameters defined by this class; any arguments are those accepted by the base Warning/Exception mechanisms (message, etc.).
- Valid values/invariants:
  - Instances are plain Warning objects; no additional invariants are required or enforced by this class.

## Lifecycle:
Creation:
- Instantiate directly (e.g., RemovedInPyjwt3Warning("message")) or, more commonly, issue via the warnings module:
  - warnings.warn("deprecation message", RemovedInPyjwt3Warning)
- There are no required constructor arguments beyond the usual optional message.

Usage:
- No methods are defined on this subclass. Usage centers on the warnings module:
  1. Library code detects deprecated usage.
  2. Library calls warnings.warn(message, RemovedInPyjwt3Warning).
  3. Consumers can filter, ignore, convert to errors, or capture the warning by referencing this class.

Destruction / cleanup:
- No special cleanup is required. Instances follow normal Python object lifetime and are garbage-collected like any exception/warning object.

## Method Map:
- This class defines no methods of its own; inheritance is the only relation.
- Typical invocation flow (conceptual):
  library code -> warnings.warn(message, RemovedInPyjwt3Warning) -> warnings subsystem (handlers/filters) -> consumer code

(Flowchart)
library code -- issues --> warnings.warn(..., RemovedInPyjwt3Warning)
warnings.warn -- routes --> warnings subsystem (filters, showwarning, catch_warnings)
warnings subsystem -- delivers/filters --> developer/test/runtime

## Raises:
- The class constructor does not raise exceptions itself.
- Any exceptions related to constructing or using warning objects would come from the base class (Exception machinery) or from misuse (e.g., passing non-string where a message is expected by user code); none are specific to this subclass.

## Example:
- Conceptual usage (described):
  1. Library detects a deprecated API usage.
  2. Library issues a warning: warnings.warn("X is deprecated and will be removed", RemovedInPyjwt3Warning)
  3. Downstream code can filter these by class:
     - Use warnings.filterwarnings("ignore", category=RemovedInPyjwt3Warning) to silence
     - Use warnings.filterwarnings("error", category=RemovedInPyjwt3Warning) to convert to exceptions during tests

This class is intentionally minimal: its implementation is simply a named subclass of DeprecationWarning to enable fine-grained classification and handling of deprecations.

