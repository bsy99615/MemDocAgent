# `src`

## Tree:
```
src/
└── exodus_bundler/
    ├── __init__.py
    ├── bundle.py
    ├── config.py
    ├── loader.py
    └── optimizer.py
```

## Role:
Manages the process of assembling application resources into optimized distributable bundles.

## Description:
The exodus_bundler module provides core functionality for collecting, processing, and optimizing application assets into bundles ready for deployment. It handles the entire bundling pipeline from asset resolution through to final optimization.

This module is used by the build system and deployment tools throughout the repository to package applications efficiently. The module follows a layered architecture where different components handle specific aspects of the bundling process.

## Components:
- **BundleBuilder** (class): Main orchestrator that coordinates the bundling process
- **AssetLoader** (class): Resolves and loads application assets and dependencies  
- **ConfigManager** (class): Manages bundling configurations and settings
- **Optimizer** (class): Applies various optimization techniques to reduce bundle size
- **build_bundle** (function): Entry point for creating application bundles
- **load_asset** (function): Loads and processes individual asset files
- **optimize_bundle** (function): Applies optimization transformations to bundles
- **validate_config** (function): Validates bundling configuration parameters

## Public API:
- **build_bundle(config)**: Creates a complete application bundle based on provided configuration. Returns a Bundle object.
- **load_asset(path)**: Loads and processes a single asset file. Returns processed asset data.
- **optimize_bundle(bundle)**: Applies optimization transformations to a bundle. Returns optimized bundle.
- **validate_config(config)**: Validates bundling configuration settings. Returns boolean indicating validity.

## Dependencies:
- Internal: None
- External: 
  - `os.path` for file system path operations
  - `json` for configuration file parsing
  - `logging` for build process logging and debugging

## Constraints:
- All asset paths must be absolute or relative to the project root
- Configuration validation must occur before bundle creation
- Bundle building operations should be deterministic and reproducible
- Thread safety is not guaranteed for concurrent bundle operations

