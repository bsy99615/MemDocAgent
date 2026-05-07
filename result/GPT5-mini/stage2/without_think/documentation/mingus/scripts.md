# `scripts`

## Tree:
scripts/
└── api_doc_generator.py

## Role:
Provide a small, focused toolkit and CLI entrypoint for generating reStructuredText (RST) / wiki-style API reference pages for Python packages and modules by reflecting on runtime objects and emitting formatted documentation fragments.

## Description:
- Where and when this module is used:
  - Primary usage is as a command-line documentation generator for the codebase (invoked via the main() entrypoint).
  - The Documize class provides a reusable programmatic API for other code that needs to produce a module-level RST string without invoking the CLI.
  - generate_package_wikidocs is a higher-level helper intended for iterating over a package's public members and writing per-module documentation files to a target directory (sys.argv[1] by default when used from the CLI).
  - Typical consumers:
    - CLI runs (scripts/api_doc_generator.py executed directly).
    - Build or developer scripts that want to call Documize programmatically to obtain module documentation text.
- Why these components are grouped:
  - Cohesion: all functions and classes implement a single conceptual layer — reflection-based API-document generation and file-emission helpers. Grouping keeps traversal, formatting, and CLI orchestration together in one utility module.

## Components:
- Class: Documize(module_string: str = '')
  - One-line role: Discover and format RST fragments for a target module/object, collecting class, attribute, and function documentation fragments for assembly into a module document.
  - See component docs: scripts.api_doc_generator.Documize

- Documize methods (public surface, one-line each — see class doc above for details):
  - __init__(module_string: str = '')
    - Delegates to set_module to configure the instance's target.
    - See: scripts.api_doc_generator.Documize.__init__
  - set_module(module_string: str)
    - Resolve a Python expression (via eval) to set the target object and reset internal collectors.
    - See: scripts.api_doc_generator.Documize.set_module
  - reset()
    - Clear internal collectors (functions, classes, attributes).
    - See: scripts.api_doc_generator.Documize.reset
  - output_wiki() -> str
    - Public accessor that returns the assembled module RST by delegating to generate_module_wikidocs.
    - See: scripts.api_doc_generator.Documize.output_wiki
  - generate_module_wikidocs() -> str
    - Orchestrates traversal and returns the final assembled RST text for the configured module.
    - See: scripts.api_doc_generator.Documize.generate_module_wikidocs
  - process_element_recursively(element_string: str, element_evaled: object, is_class: bool = False)
    - Reflectively iterates members of an object and dispatches them to appropriate formatting helpers.
    - See: scripts.api_doc_generator.Documize.process_element_recursively
  - generate_callable_wikidocs(module_string: str, element_string: str, evaled: object, is_class: bool = False)
    - Classify a discovered member (function/method/class) and append formatted snippets or recurse into classes.
    - See: scripts.api_doc_generator.Documize.generate_callable_wikidocs
  - generate_function_wikidocs(func_string: str, func: callable, is_class: bool = False) -> str
    - Produce a formatted RST snippet for a callable (signature + cleaned docstring).
    - See: scripts.api_doc_generator.Documize.generate_function_wikidocs
  - generate_non_callable_docs(module_string: str, element_string: str, evaled: object, is_class: bool = False)
    - Produce and append a formatted RST fragment for non-callable attributes.
    - See: scripts.api_doc_generator.Documize.generate_non_callable_docs
  - _filter_dunder_attributes(attrs: Iterable[str]) -> generator[str]
    - Filter policy for dunder names (whitelist + common filtering), returns a lazy iterator.
    - See: scripts.api_doc_generator.Documize._filter_dunder_attributes

- Module-level functions:
  - _is_class(cls: type) -> bool
    - One-line role: Predicate deciding whether a type should be treated as a documentable class (not in the skipped-supertype set).
    - See: scripts.api_doc_generator._is_class
  - _is_method(obj: any) -> bool
    - One-line role: Predicate that returns True if the object's exact runtime type is in the configured _METHOD_TYPES collection.
    - See: scripts.api_doc_generator._is_method
  - generate_package_wikidocs(package_string: str, file_prefix: str = 'ref', file_suffix: str = '.wiki') -> None
    - One-line role: CLI helper that iterates a package's public attributes and writes per-attribute RST/wiki files to the output directory taken from sys.argv[1].
    - See: scripts.api_doc_generator.generate_package_wikidocs
  - main() -> None
    - One-line role: CLI entrypoint: validate args, print header, and invoke generate_package_wikidocs for the canonical package list used by this project.
    - See: scripts.api_doc_generator.main

- Module-level constants (configuration points referenced by predicates and class):
  - _SKIPPED_CLASS_SUPERTYPES
    - One-line role: Types listed here exclude their subclasses from being considered documentable classes by _is_class.
    - See: referenced in scripts.api_doc_generator._is_class
  - _METHOD_TYPES
    - One-line role: Iterable of runtime types used by _is_method to detect method-like objects.
    - See: referenced in scripts.api_doc_generator._is_method

Mermaid dependency graph (high-level relationships):
graph LR
  Main[main()] --> GenPkg[generate_package_wikidocs()]
  GenPkg --> Docu[Documize]
  Docu --> SetModule[set_module()]
  SetModule --> Reset[reset()]
  Docu --> GenerateModule[generate_module_wikidocs()]
  GenerateModule --> ProcessRec[process_element_recursively()]
  ProcessRec --> Filter[_filter_dunder_attributes()]
  ProcessRec --> GenCallable[generate_callable_wikidocs()]
  ProcessRec --> GenNonCallable[generate_non_callable_docs()]
  GenCallable --> GenFunction[generate_function_wikidocs()]
  GenCallable --> IsMethod[_is_method()]
  GenCallable --> IsClass[_is_class()]
  Output[output_wiki()] --> GenerateModule

## Public API:
- Class Documize(module_string: str = '')
  - Summary: Instantiate to target a module/object and then call output_wiki() to obtain the RST document for that target.
  - Usage note:
    - Prefer passing a trusted dotted module expression. __init__ delegates to set_module which may eval() the string; see constraints below.
    - Typical pattern:
        d = Documize('mypkg.mymodule')
        rst_text = d.output_wiki()

- Documize.set_module(module_string: str)
  - Summary: Resolve (eval) module_string to set the target object and clear internal collectors.
  - Usage note:
    - Passing the exact empty string ('') is a no-op. Non-empty strings are evaluated in the module's eval context; use only trusted values or prefer passing module objects via an extended helper if available.

- Documize.output_wiki() -> str
  - Summary: Obtain the assembled module RST string ready for writing to disk or further processing.
  - Usage note:
    - This is the stable public accessor; callers need not call generate_module_wikidocs() directly.

- generate_package_wikidocs(package_string: str, file_prefix: str = 'ref', file_suffix: str = '.wiki') -> None
  - Summary: Convenience CLI helper that writes per-module documentation files to directory specified in sys.argv[1].
  - Usage note:
    - Expects sys.argv[1] to be present; does not create the output directory. The function contains an observed bug in callable detection in the original implementation — reimplementations should use getattr(package, name) and callable(that_object) when filtering callables.

- main() -> None
  - Summary: Minimal CLI wrapper that prints a header, validates sys.argv[1] is an existing directory, and calls generate_package_wikidocs for a small set of canonical packages for the project.
  - Usage note:
    - Intended to be used as the script entrypoint. It calls sys.exit(1) on argument validation failures.

- _is_class(cls: type) -> bool and _is_method(obj: any) -> bool
  - Summary: Lightweight configuration-driven predicates used by the traversal logic; not intended for external callers except for testing or customization.
  - Usage note:
    - Both depend on module-level configuration (_SKIPPED_CLASS_SUPERTYPES and _METHOD_TYPES) and will raise if those are missing or malformed.

## Dependencies:
- Internal imports (other repo modules):
  - None required for the core functionality documented here. The module uses only standard-library features and defines its own helper types and predicates.

- External / standard-library imports and their purpose:
  - sys
    - Used for CLI argument access (sys.argv) and for exit.
  - os
    - Used for path joining and isdir checks when writing files.
  - inspect
    - Used for introspecting callables (building signatures and cleaning docstrings).
  - types
    - Used to detect module types or other runtime-type checks when formatting non-callable docs.
  - Builtins: eval, open, print
    - eval: used by set_module and generate_package_wikidocs to resolve dotted expressions; this is a key security consideration.
    - open/print: used by generate_package_wikidocs to write files and report progress.

## Constraints:
- Security:
  - Several APIs in this module use eval() on strings (set_module and generate_package_wikidocs). Do not call these with untrusted input. Prefer importlib.import_module or passing actual module objects where possible.
- Correct usage ordering:
  - Documize expects that a target module has been set (either by passing a non-empty module_string to __init__ or by calling set_module) before calling output_wiki() or generate_module_wikidocs(). If self.module or self.module_string is missing, generate_module_wikidocs will raise AttributeError or produce undesired outputs.
- Thread-safety:
  - Documize instances are not designed for concurrent use from multiple threads without external synchronization. The class mutates short-lived internal lists (functions, classes, attributes) and relies on deterministic mutation/reset behavior.
- CLI preconditions:
  - generate_package_wikidocs depends on sys.argv[1] for the output directory; main validates that sys.argv[1] exists and is a directory before proceeding. generate_package_wikidocs itself also assumes sys.argv[1] exists; callers that use the helper programmatically should set sys.argv appropriately or pass an adapted helper that accepts an explicit path.
- Implementation notes / caveats:
  - Some helper predicates (_is_method, _is_class) rely on module-level configuration constants; if those constants are absent or malformed the predicates will raise NameError/TypeError.
  - The module uses repr(type(obj)) and repr(value) to produce textual type/value fragments; objects with side-effecting __repr__ implementations will execute during generation.
  - File writes in generate_package_wikidocs use the system default encoding unless explicitly changed; consider opening files with encoding='utf-8' for reproducible cross-platform output.

For in-depth behavior, inputs/outputs, edge cases, and implementation-level details for each class method and function, see the component-level documentation:
- scripts.api_doc_generator.Documize and its methods (see entries in the project documentation store)
- scripts.api_doc_generator._is_class
- scripts.api_doc_generator._is_method
- scripts.api_doc_generator.generate_package_wikidocs
- scripts.api_doc_generator.main

---

## Files

- [`api_doc_generator.py`](scripts/api_doc_generator.md)

