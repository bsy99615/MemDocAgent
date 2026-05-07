# `mackup`

## Purpose

Mackup is a comprehensive framework for backing up, restoring, and uninstalling application configuration files across multiple storage backends. It addresses the common problem of losing application settings when switching computers, reinstalling operating systems, or managing multiple development environments. The tool provides a unified interface for managing user application settings, supporting both cloud-based storage solutions (Dropbox, Google Drive, iCloud, Copy) and local filesystem storage.

Target users include developers, power users, and anyone who wants to preserve their application configurations across system changes. It's particularly valuable for developers who frequently switch between machines or need to maintain consistent development environments.

In the broader ecosystem, Mackup serves as a standalone tool that can be integrated into larger system administration or development workflows. It acts as a configuration management utility that focuses specifically on application settings rather than full system backups.

## Architecture

```mermaid
flowchart TD
    A[Command Line Interface] --> B[main()]
    B --> C[Mackup Orchestrator]
    C --> D[Config Manager]
    C --> E[Applications Database]
    C --> F[Application Profile Handler]
    F --> G[File Operations]
    F --> H[System Utilities]
    D --> I[Storage Backend Validation]
    E --> J[Application Metadata Management]
    G --> K[Copy Files]
    G --> L[Link Files]
    G --> M[Delete Files]
    G --> N[Modify Permissions]
    H --> O[Platform Detection]
    H --> P[Process Management]
    H --> Q[User Confirmation]
```

The architecture follows a modular design pattern with clear separation of concerns:
- **Configuration Management**: Handles user preferences and storage backend settings
- **Application Database**: Manages metadata about supported applications and their configuration files
- **Core Orchestrator**: Coordinates backup/restore workflows and environment validation
- **Application Handlers**: Manage specific operations for individual applications
- **Utility Layer**: Provides cross-cutting concerns like file operations, system interactions, and formatting

Key architectural patterns include:
- Command pattern through the main entry point
- Strategy pattern for different storage backends
- Facade pattern for simplifying complex operations
- Observer pattern for environment validation

## Entry Points

### CLI Commands
- **`mackup backup`**: Backs up application configuration files to the configured storage backend
- **`mackup restore`**: Restores application configuration files from the configured storage backend  
- **`mackup uninstall`**: Removes application configuration files completely
- **`mackup status`**: Shows current backup status and configuration

All CLI commands are exposed through the `main()` function which uses docopt for argument parsing and dispatches operations to the appropriate handlers.

### Importable APIs
The core functionality is available programmatically through:
- `mackup.Mackup`: Main orchestrator class for backup/restore workflows
- `mackup.Config`: Configuration manager for storage settings
- `mackup.ApplicationProfile`: Application-specific operation handler
- `mackup.ApplicationsDatabase`: Application metadata manager

## Core Features

- **Multi-backend Storage Support**: Backup to Dropbox, Google Drive, iCloud, Copy, or local filesystem
- **Cross-platform Compatibility**: Works on macOS, Linux, and Windows
- **Selective Application Management**: Choose which applications to backup/restore
- **Application Metadata Database**: Comprehensive catalog of supported applications and their config files
- **Environment Validation**: Checks for proper system conditions before operations
- **Safe File Operations**: Handles file permissions, ACLs, and immutable attributes appropriately
- **Interactive Confirmation**: Prompts users for confirmation before destructive operations
- **Terminal Formatting**: Provides colored output for better user experience

## Dependencies

### External Dependencies
- **configparser**: For parsing configuration files
- **docopt**: For command-line argument parsing
- **sqlite3**: For accessing Google Drive configuration database
- **os, sys, shutil, subprocess**: For system operations and file management
- **platform, logging**: For platform detection and logging

### Internal Dependencies
- **mackup.application**: Provides ApplicationProfile class for application-specific operations
- **mackup.appsdb**: Provides ApplicationsDatabase class for application metadata management
- **mackup.config**: Provides Config class for configuration management
- **mackup.mackup**: Provides Mackup class for main orchestration
- **mackup.utils**: Provides utility functions for file operations, system interactions, and formatting

## Configuration

Mackup supports configuration through:
- **Configuration files**: Located in standard locations for user configuration
- **Environment variables**: For overriding default settings
- **Command-line arguments**: Runtime parameter specification
- **Storage backend paths**: Configurable paths for different cloud services

The configuration system allows users to specify:
- Storage engine type (dropbox, google_drive, icloud, copy, local)
- Storage path override
- Backup directory name
- Applications to ignore or sync

## Extension Points

Mackup provides several extension points for customization:
- **Plugin System**: New applications can be added by extending the ApplicationsDatabase
- **Storage Backends**: Custom storage engines can be implemented by following the existing interface
- **Application Profiles**: New application support can be added by implementing the ApplicationProfile interface
- **Utility Functions**: Additional system utilities can be contributed to the utils module
- **Configuration Extensions**: Custom configuration options can be added through the Config class

The system is designed to be easily extensible while maintaining backward compatibility with existing functionality.

---

## Modules

- [`mackup`](mackup.md)

