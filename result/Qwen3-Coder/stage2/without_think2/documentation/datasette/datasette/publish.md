# `datasette.publish`

## Tree:
- publish/
  - cloudrun.py
  - common.py
  - heroku.py

## Role:
Manages the deployment and publishing of Datasette applications to various cloud platforms, providing standardized command-line interfaces and infrastructure for container-based deployments.

## Description:
The publish module provides a unified framework for deploying Datasette applications to different cloud hosting platforms such as Google Cloud Run and Heroku. It offers a consistent command-line interface through Click decorators while implementing platform-specific deployment workflows. The module centralizes common publishing utilities and validations to reduce code duplication and ensure secure, reliable deployments.

## Components:
- **cloudrun.py**: Contains Cloud Run-specific deployment logic including service registration, memory validation, and gcloud integration
  - `publish_subcommand`: Registers the `datasette publish cloudrun` command with full deployment capabilities
  - `_validate_memory`: Validates memory specification formats for Cloud Run resources
  - `get_existing_services`: Retrieves existing Cloud Run services for discovery and conflict resolution

- **common.py**: Provides shared utilities and validation functions used across all publishing targets
  - `add_common_publish_arguments_and_options`: Applies standardized CLI arguments to publishing commands
  - `fail_if_publish_binary_not_installed`: Ensures required deployment tools are available
  - `validate_plugin_secret`: Prevents shell injection vulnerabilities in plugin secrets

- **heroku.py**: Implements Heroku-specific deployment workflows and temporary directory management
  - `publish_subcommand`: Registers the `datasette publish heroku` command with Heroku-specific features
  - `temporary_heroku_directory`: Manages temporary directory structure for Heroku deployments

## Public API:
- `datasette.publish.cloudrun.publish_subcommand(publish: click.Group)` → None
  - Registers the Google Cloud Run publish command with the datasette publish CLI
  - Adds all Cloud Run-specific command-line options and validation
  - Handles interactive service name prompting and gcloud integration

- `datasette.publish.common.add_common_publish_arguments_and_options(subcommand: click.Command)` → click.Command
  - Decorates Click commands with standardized publishing arguments
  - Applies common options like --metadata, --template-dir, --plugins-dir, etc.
  - Centralizes CLI argument definitions for consistency

- `datasette.publish.heroku.publish_subcommand(publish: click.Group)` → None
  - Registers the Heroku publish command with the datasette publish CLI
  - Implements Heroku-specific deployment workflows and plugin handling
  - Supports both direct deployment and file generation modes

## Dependencies:
- Internal: 
  - `datasette.publish.common`: Shared utilities and validation functions
  - `datasette.publish.cloudrun`: Cloud Run-specific implementations
  - `datasette.publish.heroku`: Heroku-specific implementations
- External:
  - `click`: Command-line interface framework for CLI command definitions
  - `subprocess`: For executing system commands like gcloud and heroku
  - `json`: For parsing JSON responses from cloud APIs
  - `tempfile`, `shutil`, `os`: For temporary directory and file management
  - `re`: For regular expression matching in validation functions

## Constraints:
- All publishing commands require appropriate platform-specific CLIs to be installed and configured
- Plugin secret values must not contain single quotes to prevent shell injection
- Memory specifications for Cloud Run must follow the format of a number followed by Gi, G, Mi, or M units
- Temporary directories are automatically cleaned up after deployment operations
- Commands must be registered with a valid Click Group instance to function properly

---

## Files

- [`cloudrun.py`](publish/cloudrun.md)
- [`common.py`](publish/common.md)
- [`heroku.py`](publish/heroku.md)

