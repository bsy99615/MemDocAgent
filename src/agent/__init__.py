# Copyright (c) Meta Platforms, Inc. and affiliates
# Import only essential components to avoid circular imports
from .reader import CodeComponentType

# Explicitly list what should be accessible, but don't import until needed
# to prevent circular imports
__all__ = ['generate_docstring', 'CodeComponentType']

# Lazy load generate_docstring when it's actually needed
def __getattr__(name):
    if name == 'generate_docstring':
        from .workflow import generate_docstring
        return generate_docstring
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'") 