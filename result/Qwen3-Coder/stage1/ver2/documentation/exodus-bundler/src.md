# `src`

## Tree:
    exodus_bundler/
    ├── __init__.py
    ├── bundler.py
    ├── config.py
    ├── exceptions.py
    └── utils.py

## Role:
    Core bundling infrastructure for application packaging

## Description:
    The exodus_bundler module provides foundational functionality for creating packaged distributions of applications. It encapsulates the logic for collecting, processing, and organizing application assets into standardized bundle formats suitable for deployment.

    This module serves as a building block for automated build processes and deployment workflows that require consistent application packaging.

    The module groups related bundling functionality together based on shared concerns around asset management, configuration handling, and packaging operations.

## Components:
    - Main bundling orchestration classes
    - Configuration management utilities
    - Exception handling for bundling operations
    - Asset processing and compression functions

## Public API:
    - Primary bundling interface for creating application packages
    - Configuration loading and validation mechanisms
    - Error handling for bundling failures
    - Utility functions for asset manipulation

## Dependencies:
    - Internal: None
    - External: 
        - jsonschema: For configuration validation
        - zipfile: For archive creation
        - os, pathlib: For filesystem operations

## Constraints:
    - Bundling operations require valid configuration before execution
    - Asset paths must be resolvable from the working directory
    - Concurrent bundling operations should be handled carefully
    - Configuration schemas must be adhered to prevent runtime errors

