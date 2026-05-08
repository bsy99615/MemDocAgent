# `datasette.publish`

## Tree:
publish/
├── cloudrun.py
├── common.py
└── heroku.py

## Role:
The publish module provides command-line interfaces and utilities for deploying Datasette applications to cloud platforms, specifically Google Cloud Run and Heroku.

## Description:
This module encapsulates all functionality related to publishing Datasette instances to cloud hosting platforms. It provides two main publishing targets: Google Cloud Run and Heroku, each with their own deployment workflows and configurations. The module shares common utilities and argument parsing across different publishing methods to maintain consistency in the CLI interface.

The publish module is primarily consumed by the main datasette CLI application when users invoke publishing commands. It serves as the bridge between user-specified deployment parameters and the actual cloud platform deployment processes.

## Components:
- `cloudrun.publish_subcommand(publish)` - Registers the Cloud Run publishing command with the Click framework
- `cloudrun.get_existing_services()` - Retrieves existing Cloud Run services for deployment planning
- `cloudrun._validate_memory(ctx, param, value)` - Validates memory specification strings for Cloud Run deployments
- `common.add_common_publish_arguments_and_options(subcommand)` - Adds standard publishing arguments to Click commands
- `common.fail_if_publish_binary_not_installed(binary, publish_target, install_link)` - Validates required system binaries for publishing
- `common.validate_plugin_secret(ctx, param, value)` - Validates plugin secret values for shell safety
- `heroku.publish_subcommand(publish)` - Registers the Heroku publishing command with the Click framework
- `heroku.temporary_heroku_directory(files, name, metadata, extra_options, branch, template_dir, plugins_dir, static, install, version_note, secret, extra_metadata)` - Creates temporary directory structure for Heroku deployment

## Public API:
- `publish_subcommand(publish)` - Function to register publishing subcommands with Click groups
- `add_common_publish_arguments_and_options(subcommand)` - Decorator to add standard publishing arguments to Click commands
- `fail_if_publish_binary_not_installed(binary, publish_target, install_link)` - Utility to validate required system binaries
- `validate_plugin_secret(ctx, param, value)` - Validator for plugin secret values
- `get_existing_services()` - Utility to list existing Cloud Run services

## Dependencies:
Internal:
- `click` - Used for command-line interface construction and argument parsing
- `subprocess` - Used for executing external commands like gcloud and heroku
- `json` - Used for parsing JSON responses from cloud platform APIs
- `os`, `tempfile`, `shutil` - Used for filesystem operations and temporary directory management
- `yaml` - Used for parsing YAML metadata files

External:
- `gcloud` - Required for Google Cloud Run deployments
- `heroku` - Required for Heroku deployments
- `docker` - Required for building Docker images for Cloud Run deployments

## Constraints:
- Users must have appropriate authentication and permissions for target cloud platforms
- Required system binaries (gcloud, heroku, docker) must be installed and accessible
- Cloud Run deployments require a valid Google Cloud project configuration
- Heroku deployments require Heroku CLI and heroku-builds plugin installation
- Plugin secret values must not contain single quote characters to prevent shell injection
- Temporary directories are automatically cleaned up after operations

---

## Files

- [`cloudrun.py`](publish/cloudrun.md)
- [`common.py`](publish/common.md)
- [`heroku.py`](publish/heroku.md)

