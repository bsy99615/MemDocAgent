# `src`

## Tree:
exodus_bundler/
├── bundling.py
├── cli.py
├── dependency_detection.py
├── errors.py
├── input_parsing.py
├── launchers.py
└── templating.py

## Role:
Provides core application bundling functionality for packaging projects into distributable formats.

## Description:
The exodus_bundler module implements a complete application packaging system that transforms source code projects into deployable bundles. It handles dependency management, configuration processing, template rendering, and artifact generation to create self-contained applications.

This module is consumed by the command-line interface and automated build systems that require application packaging capabilities. The cohesive grouping reflects the shared responsibility of creating packaged applications from source material.

## Components:
- bundling.py: Main orchestrator that coordinates the complete bundling workflow from start to finish
- cli.py: Command-line interface for user interaction and argument parsing
- dependency_detection.py: Resolves and analyzes project dependencies for inclusion in bundles
- errors.py: Custom exception hierarchy for bundling operation failures
- input_parsing.py: Processes configuration files and command-line arguments into usable data structures
- launchers.py: Generates executable wrapper scripts for launching bundled applications
- templating.py: Renders template files with dynamic content substitution for configuration and assets

## Public API:
- bundling.py: bundle_application() - executes full bundling process, create_bundle_context() - initializes bundling environment
- cli.py: main() - entry point for CLI execution, parse_arguments() - processes CLI input
- dependency_detection.py: detect_dependencies() - identifies project dependencies, resolve_dependency_graph() - creates dependency tree
- errors.py: BundlingError, DependencyError - custom exception types for error handling
- input_parsing.py: parse_config_file() - reads configuration files, validate_inputs() - verifies input data
- launchers.py: generate_launcher() - creates executable launch scripts, create_wrapper() - builds runtime wrappers
- templating.py: render_template() - processes templates with variables, substitute_variables() - replaces placeholders

## Dependencies:
Internal: None
External: argparse, os, json, pathlib, shutil, subprocess, logging, yaml

## Constraints:
- All paths must be absolute or properly resolved relative to project root
- Configuration validation must occur before any bundling operations
- Template variable substitution must prevent code injection vulnerabilities
- Bundle creation must be deterministic and reproducible
- Generated launchers must be compatible with target platform execution environments

