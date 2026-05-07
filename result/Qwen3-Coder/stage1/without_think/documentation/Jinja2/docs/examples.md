# `docs.examples`

## Tree:
examples/
├── cache_extension.py
└── inline_gettext_extension.py

## Role:
Provides example implementations of Jinja2 template extensions for common use cases like fragment caching and inline gettext conversion.

## Description:
This module contains example implementations of Jinja2 extensions that demonstrate how to extend template functionality for common development needs. These examples serve as educational resources for developers who want to create custom Jinja2 extensions.

The module groups together two distinct extension types that showcase different aspects of Jinja2 extension development:
1. Fragment caching for performance optimization
2. Inline gettext conversion for internationalization

These components are grouped together because they both represent practical examples of how to extend Jinja2's template processing capabilities, making them valuable for learning and reference purposes.

## Components:
- `FragmentCacheExtension`: Implements a custom `{% cache %}` template tag for caching expensive template fragments
- `InlineGettext`: Converts inline gettext syntax (`_(...)`) into proper Jinja2 translation blocks

```mermaid
graph LR
    A[FragmentCacheExtension] --> B[parse()]
    A --> C[_cache_support()]
    B --> C
    D[InlineGettext] --> E[filter_stream()]
```

## Public API:
- `FragmentCacheExtension`: Jinja2 extension class that adds `{% cache %}` template tag functionality
- `InlineGettext`: Jinja2 extension class that converts inline gettext expressions to proper translation blocks

## Dependencies:
- Internal: None (pure Jinja2 extensions)
- External: `jinja2` (required for extension base classes and template processing)

## Constraints:
- Both extensions require a valid Jinja2 Environment instance for initialization
- Extensions must be registered with a Jinja2 environment to be effective
- The FragmentCacheExtension relies on the environment having appropriate cache infrastructure configured for full functionality
- The InlineGettext extension operates during template compilation when the extension is registered

---

## Files

- [`cache_extension.py`](examples/cache_extension.md)
- [`inline_gettext_extension.py`](examples/inline_gettext_extension.md)

