# `src`

## Tree:
src/
└── exodus_bundler/

## Role:
Core bundling engine for assembling application assets into deployable packages.

## Description:
The exodus_bundler module implements the primary bundling infrastructure for the Exodus platform. It provides a robust framework for collecting, processing, and packaging application resources into optimized bundle formats. This module serves as the central coordination point for all bundling operations within the system.

The module is consumed by the build pipeline, deployment systems, and development tools that require compiled application artifacts. It follows a modular architecture where different responsibilities are separated into distinct components, promoting testability, maintainability, and extensibility.

## Components:
- **BundleBuilder**: Main orchestrator class that manages the complete bundling workflow
- **AssetCollector**: Responsible for discovering and gathering source files and resources
- **DependencyResolver**: Resolves module dependencies and import statements
- **Transformer**: Applies transformations to assets during the bundling process
- **OutputWriter**: Handles writing the final bundle to storage

## Public API:
- **build_bundle(config)**: Main entry point that initiates the bundling process with provided configuration
- **validate_config(config)**: Validates bundling configuration parameters before processing
- **get_bundle_stats()**: Returns statistics about the built bundle including size and asset count

## Dependencies:
- Internal: config_manager for configuration handling and validation
- Internal: logger for bundling operation logging and debugging
- External: pathlib for filesystem path operations
- External: json for configuration file parsing

## Constraints:
- Configuration must be validated using validate_config() before calling build_bundle()
- BundleBuilder instances are not thread-safe and should not be shared across concurrent operations
- All asset paths in configuration must be resolvable from the project root directory
- Each build operation requires a fresh BundleBuilder instance for proper state management

