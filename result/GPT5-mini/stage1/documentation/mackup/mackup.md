# `mackup`

## Tree:
mackup/
  - mackup/                           (package root: core application logic, CLI, and utilities)
    - application.py                  (per-application profile: backup/restore/uninstall)
    - appsdb.py                       (ApplicationsDatabase: discover and parse .cfg descriptors)
    - config.py                       (Config and ConfigError: runtime configuration parsing/validation)
    - mackup.py                       (Mackup: orchestration, environment checks, workspace management)
    - main.py                         (CLI entry, argument parsing, terminal helpers)
    - utils.py                        (Filesystem and provider-discovery helpers; atomic helpers)

Notes on responsibilities:
- The package groups public-facing behaviors (CLI, configuration, app catalog, orchestration) and low-level filesystem/provider utilities used by those behaviors. Each module is focused and designed to be importable for programmatic usage or invoked via the CLI entrypoint.

## Purpose:
- Problem solved:
  - Provide a reproducible, portable way to back up, restore, and uninstall application configuration and user files (a "mackup" tool) while handling platform-specific filesystem and cloud-provider idiosyncrasies.
- Why it matters:
  - Simplifies migrating user settings between machines or persisting them to cloud storage in a safe, permission-aware way.
- Target users & scenarios:
  - End users who want to sync or migrate their application preferences.
  - Automation/CI workflows that need reproducible environment snapshots.
  - Developers adding support for new applications via descriptor files.
- Position in the ecosystem:
  - Standalone CLI application with an importable API surface for embedding in scripts or tools. Not a daemon or long-running service.

## Architecture:
- Mermaid flowchart (flowchart TD)
flowchart TD
  User[User / Automation] --> CLI[main.main (CLI)]
  CLI -->|loads| Config[Config]
  CLI -->|loads| DB[ApplicationsDatabase]
  CLI -->|creates| Orchestrator[Mackup]
  Orchestrator -->|creates temp workspace| Workspace[(temp dir)]
  Orchestrator -->|builds| Profile[ApplicationProfile (per-app)]
  Profile -->|uses| Utils[utils.* (copy/link/delete/chmod/...)]
  DB -->|reads| AppCfgs[".cfg descriptors (bundled + custom)"]
  Utils -->|discovers| Providers[provider-discovery helpers]
  Providers -->|may return| StoragePaths[storage engine paths]
  StoragePaths --> Orchestrator

- Key architectural patterns:
  - Orchestrator (Mackup): central controller that validates environment preconditions and manages workspace & app-selection.
  - Profile abstraction (ApplicationProfile): encapsulates per-app file lists and the concrete backup/restore/uninstall operations.
  - Descriptor-driven extensibility (ApplicationsDatabase): adding .cfg descriptors extends supported apps without changing code.
  - Utility layer (utils): platform-aware filesystem, ACL/flag handling, and cloud-provider discovery centralized for reuse.

## Entry Points:
- CLI entry
  - Function: mackup.main.main
  - What it exposes: full CLI for actions such as backup, restore, list, show, uninstall. Uses docopt for argument parsing and sets module-level runtime flags (e.g., FORCE_YES, CAN_RUN_AS_ROOT).
  - Audience: end users and automation scripts.
  - Notes: main.main may raise SystemExit; callers embedding the CLI should catch SystemExit for graceful handling.
- Importable APIs (programmatic use)
  - Config(filename: Optional[str] = None)
    - Exposes: engine, path, directory, fullpath, apps_to_ignore, apps_to_sync
    - Use: resolve storage engine and targeted apps early in startup.
    - Errors: ConfigError for validation issues; provider-discovery helpers called during resolution may call error(...) or raise SystemExit.
  - ApplicationsDatabase()
    - Exposes methods for enumerating supported apps and file templates (get_app_names, get_files, get_pretty_app_names, etc.)
    - Use: discover app descriptors and produce lists used by orchestration.
  - Mackup()
    - Exposes: environment validation helpers (check_for_usable_environment, check_for_usable_restore_env), create_mackup_home(), workspace management, and helpers to construct ApplicationProfile instances.
    - Use: orchestrate precondition checks and to manage temporary workspace and app selection.
  - ApplicationProfile(mackup, files, dry_run=False, verbose=False)
    - Exposes: backup(), restore(), uninstall(), getFilepaths()
    - Use: perform per-application operations; intended to be called after Mackup precondition checks.
  - utils.* (copy, link, delete, chmod, remove_acl, remove_immutable_attribute, confirm, error, provider-discovery helpers)
    - Exposes: low-level filesystem operations and provider discovery functions.
    - Use: for concrete file operations and platform provider folder discovery.

## Core Features (one-line + implementer):
- Application descriptor discovery — mackup.appsdb.ApplicationsDatabase
- Runtime configuration resolution (engine/path/apps selection) — mackup.config.Config
- Orchestration & environment checks — mackup.mackup.Mackup
- Per-application backup/restore/uninstall — mackup.application.ApplicationProfile
- Cross-platform provider discovery (Dropbox, Google Drive, iCloud, Copy) — mackup.utils provider-discovery helpers
- Safe filesystem operations (ACL/immutable handling, permission policy) — mackup.utils (copy/delete/chmod/link/remove_acl/remove_immutable_attribute)
- Interactive confirmation and automation-friendly short-circuiting — mackup.utils.confirm and FORCE_YES

## Dependencies:
- Standard library: os, os.path, shutil, tempfile, stat, platform, subprocess, base64, sqlite3, configparser, sys
- Third-party:
  - docopt — CLI argument parsing (mackup.main)
  - six (six.moves.input) — unified input handling (confirm)
- Platform utilities: pgrep, chflags, chattr, setfacl may be invoked by utils functions when available.
- Compatibility notes:
  - No precise version pins in this snapshot; ensure docopt and six are present in the runtime environment.
  - Many provider-discovery and ACL/flag operations are best-effort and depend on platform binaries being present.

## Configuration:
- How configuration is provided:
  - Config can be constructed with an optional filename (Config(filename=None)). If omitted, Config resolves defaults which rely on the HOME environment variable.
- Important environment variables & runtime toggles:
  - HOME: required by many discovery and path-resolution operations. Missing HOME may lead to KeyError or incorrect behavior.
  - FORCE_YES (module-level in utils): short-circuits confirm() to make runs non-interactive (useful for CI/tests).
  - CAN_RUN_AS_ROOT: controlled by main before operations that may be sensitive to root execution.
- Behavior affected:
  - Storage engine and fullpath selection, and the set of apps to sync/ignore, are driven by Config. Changing config changes targets and behaviors.

## Extension Points:
- Add new application support
  - Add or drop-in .cfg descriptors where ApplicationsDatabase looks for them (see module docs). No code change required for new descriptors.
- Subclass orchestrator or profile
  - Create subclasses of Mackup or ApplicationProfile to alter orchestration (e.g., change permission policies, change copy semantics) and inject them into custom scripts.
- Swap utilities for testing
  - utils functions are small and ideal for monkeypatching in tests (e.g., replace copy/delete with no-ops or stubs).
- Programmatic embedding
  - The package is designed so callers can instantiate Config, ApplicationsDatabase, and Mackup directly and then create ApplicationProfile instances to run operations without invoking the CLI.

## Usage examples and recommended workflows

1) Common CLI examples (reflects actions supported by main):
- Preview a full backup without mutating files (dry-run):
  - mackup backup --all --dry-run --verbose
- Back up only named apps:
  - mackup backup vim slack
- Restore a single app interactively:
  - mackup restore slack
- List supported apps:
  - mackup list
- Uninstall an app's files from the machine:
  - mackup uninstall <app_name>

Notes:
- The above examples use action names known from the CLI (backup, restore, list, show, uninstall) and flags commonly set by main (--dry-run, --verbose). Exact CLI flag names are parsed by docopt in mackup.main; consult mackup.main for the docopt usage string and full flag names.

2) Programmatic (embedding) end-to-end walkthrough:
- Typical sequence for a script that performs a programmatic backup:
  1. Construct runtime configuration:
     - cfg = Config(filename=None)  # resolves engine/path and app lists
  2. Build supporting objects:
     - db = ApplicationsDatabase()
     - mgr = Mackup()               # holds the snapshot/config and manages workspace
  3. Validate environment and prepare workspace:
     - mgr.check_for_usable_environment()
     - mgr.create_mackup_home()
  4. Select apps and run per-app backup:
     - profile = ApplicationProfile(mgr, files=set_of_relative_paths, dry_run=False, verbose=True)
     - profile.backup()
  5. Cleanup:
     - mgr.clean_temp_folder()      # ensure temporary workspace removed

- Important sequencing constraints:
  - Construct Config early (or let Mackup build it) so subsequent operations have resolved storage paths.
  - Always run Mackup.check_for_usable_environment() before performing backup, and check_for_usable_restore_env() before restore/uninstall.
  - confirm() blocks on stdin unless utils.FORCE_YES is set; set it in CI or monkeypatch input during tests.

## Constraints and operational notes:
- Preconditions:
  - HOME must be available for typical discovery and path expansion.
  - Provider-discovery functions (get_dropbox_folder_location, get_google_drive_folder_location, get_icloud_folder_location, get_copy_folder_location) may call error(...) (which exits) or raise exceptions on failure — callers should be prepared to handle SystemExit or wrap calls in try/except where appropriate.
- Side effects:
  - utils.* functions perform direct filesystem mutation (copy/link/delete/chmod). These are not thread-safe; provide external synchronization for concurrent invocations.
- Error & exit behavior:
  - Some low-level helpers call utils.error(...) which prints an error and exits the process. When embedding the library, handle SystemExit when invoking functions that may call error(...).
- Testing guidance:
  - Set utils.FORCE_YES in tests to avoid interactive prompts, or monkeypatch six.moves.input to simulate user confirmation.
  - Monkeypatch or stub utils functions to avoid destructive operations in unit tests.

## Where to look next
- For precise signatures, edge cases, and reimplementation guidance consult the component-level documentation already stored:
  - mackup.application.ApplicationProfile
  - mackup.appsdb.ApplicationsDatabase
  - mackup.config.Config and ConfigError
  - mackup.mackup.Mackup
  - mackup.main (main, header, bold, ColorFormatCodes)
  - mackup.utils (copy, delete, link, chmod, remove_acl, remove_immutable_attribute, confirm, error, provider-discovery helpers)

---

## Modules

- [`mackup`](mackup.md)

