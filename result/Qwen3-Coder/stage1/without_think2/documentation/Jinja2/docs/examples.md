# `docs.examples`

## Tree:
examples/
├── cache_extension.py
└── inline_gettext_extension.py

## Role:
Provides reusable Jinja2 template extensions for fragment caching and inline internationalization.

## Description:
This module contains two Jinja2 extensions designed to enhance template functionality: one for caching expensive template computations and another for enabling inline gettext expressions in templates. Both extensions integrate seamlessly with Jinja2's template compilation and rendering pipeline to provide powerful templating capabilities without requiring complex template syntax.

The module serves as a utility collection for developers working with Jinja2 templates who need caching or internationalization features. It is particularly useful in web applications where performance optimization and localization are important concerns.

## Components:
- `FragmentCacheExtension`: Implements the `{% cache %}` template tag for fragment caching
- `InlineGettext`: Converts inline gettext expressions into proper Jinja2 translation blocks

## Public API:
- `FragmentCacheExtension`: Jinja2 extension class for template fragment caching
- `InlineGettext`: Jinja2 extension class for inline internationalization

## Dependencies:
- `jinja2`: Required for template extension infrastructure and parsing
- `jinja2.ext.Extension`: Base class for Jinja2 extensions
- `jinja2.exceptions.TemplateSyntaxError`: Used for error handling in inline gettext processing

## Constraints:
- `FragmentCacheExtension` requires the Jinja2 environment to have `fragment_cache` and `fragment_cache_prefix` attributes configured
- Both extensions must be registered with a Jinja2 Environment to function

---

## Files

- [`cache_extension.py`](examples/cache_extension.md)
- [`inline_gettext_extension.py`](examples/inline_gettext_extension.md)

