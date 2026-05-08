# `datasette.publish`

## Tree:
publish/
├── cloudrun.py
├── common.py
└── heroku.py

## Role:
Provide shared CLI plumbing and provider-specific helpers that the Datasette "publish" commands use to prepare deployable artifacts and to invoke external deployment CLIs (e.g., Heroku, Google Cloud Run).

## Description:
- Where and when this module is used:
  - Intended for use by the Datasette publish CLI layer when users run "datasette publish <target>" (for example "datasette publish heroku" or "datasette publish cloudrun").
  - Primary consumers (intended):
    - The top-level publish command group and subcommand registration code that sets up and invokes publish targets.
    - Unit tests and higher-level orchestration code that exercise publish flows by stubbing subprocesses and inspecting environment-variable and metadata mappings.
  - Note about available scan: the provided component-level documents indicate no explicit callers were included in the preloaded source for this task; therefore references to “consumers” above describe intended usage rather than confirmed import sites in the scanned files.
- Why these components are grouped:
  - Cohesion: groups functionality dealing with command-line option wiring, validation, filesystem preparation, and invocation of provider CLIs — all concerns required by publish targets.
  - Layer boundary: acts as the CLI-to-provider layer, isolating Click wiring and provider invocation from the rest of the codebase.

## Components:
Public symbols and one-line roles. For full implementation details, consult each component's dedicated documentation.

- publish/common.py
  - add_common_publish_arguments_and_options(subcommand: Callable) -> Callable
    - Decorator/helper that attaches the standard set of Click arguments and options used by publish subcommands.
  - validate_plugin_secret(ctx: click.Context, param: click.Parameter, value: Iterable[tuple[str,str,str]]) -> Iterable[tuple[str,str,str]]
    - Click callback that enforces plugin-secret values do not contain single quotes; returns the input iterable unchanged on success.
  - fail_if_publish_binary_not_installed(binary: str, publish_target: str, install_link: str) -> None
    - Helper that checks for a required external CLI binary on PATH and, if missing, prints an error and calls sys.exit(1).

- publish/cloudrun.py
  - _validate_memory(ctx: click.Context, param: click.Parameter, value: str | None) -> str | None
    - Click callback validating memory size strings against the anchored regex ^\d+(Gi|G|Mi|M)$; returns the value unchanged or raises click.BadParameter.
  - get_existing_services() -> list[dict]
    - Run "gcloud run services list --platform=managed --format json" and return list of descriptors with keys "name", "created", and "url".
  - publish_subcommand(publish: click.Group) -> None
    - Register the Cloud Run publish subcommand and implement its runtime deployment flow (create vs update).

- publish/heroku.py
  - publish_subcommand(publish: click.Group) -> None
    - Register the Heroku publish subcommand; ensure Heroku CLI & plugin, prepare an app tree, set config vars, and trigger a build (or write generated files).
  - temporary_heroku_directory(...) -> contextmanager
    - Context manager to prepare a temporary application tree for Heroku deployments. Consult the implementation to determine whether it changes CWD or yields a path.

Mermaid dependency graph (internal component relationships):
graph TD
    common_add[add_common_publish_arguments_and_options]
    common_validate[validate_plugin_secret]
    common_fail[fail_if_publish_binary_not_installed]
    cloudrun_validate[_validate_memory]
    cloudrun_list[get_existing_services]
    cloudrun_publish[cloudrun.publish_subcommand]
    heroku_publish[heroku.publish_subcommand]
    temp_dir[temporary_heroku_directory]

    common_add --> cloudrun_publish
    common_add --> heroku_publish
    common_validate --> common_add
    common_fail --> heroku_publish
    cloudrun_validate --> cloudrun_publish
    cloudrun_list --> cloudrun_publish
    temp_dir --> heroku_publish

## Public API:
What other parts of the repository should import and use from this module, with usage notes and observable side effects.

- add_common_publish_arguments_and_options(subcommand: Callable) -> Callable
  - Signature: subcommand -> Callable
  - Description: Apply a standardized set of Click argument and option decorators to a publish subcommand function.
  - Usage notes:
    - Intended to be used as a decorator at command-definition time.
    - The decorated function will receive keyword arguments produced by Click for:
      * files (variadic, validated with click.Path, existence enforced)
      * metadata (click.File opened for reading or None)
      * extra-options (str | None)
      * branch (str | None)
      * template-dir, plugins-dir (click.Path directories or None)
      * static mounts (one or more values converted by StaticMount into (mount_point, absolute_path))
      * install (iterable[str]): extra packages
      * plugin-secret (iterable of 3-tuples) validated by validate_plugin_secret
      * version-note, secret, title, license, license_url, source, source_url, about, about_url (strings)
    - Side effects: at decoration time it only mutates the callable by attaching Click metadata. At runtime Click may open files (click.File) and invoke option callbacks.
    - Errors: Click will raise for invalid paths, failing callbacks, or invalid option formats.

- validate_plugin_secret(ctx, param, value) -> value
  - Signature: (click.Context, click.Parameter, Iterable[tuple[str,str,str]]) -> same iterable
  - Description: Validate plugin-secret triplets; raises click.BadParameter if any secret contains a single quote.
  - Usage notes:
    - Register as the callback for the --plugin-secret option.
    - Input must be an iterable of triplets; malformed entries cause Python unpacking errors (ValueError) to propagate.

- fail_if_publish_binary_not_installed(binary, publish_target, install_link) -> None
  - Signature: (str, str, str) -> None
  - Description: Call shutil.which(binary); if falsy, print an error using click.secho and click.echo and then call sys.exit(1).
  - Usage notes:
    - Intended to be used by publish target handlers before they attempt to run an external CLI.
    - Component docs indicate no explicit callers were found in the provided scan — this helper is intended for use by publish subcommands but may not be directly referenced in the scanned subset.
    - Tests should patch this helper to avoid process termination.

- _validate_memory(ctx, param, value) -> str | None
  - Signature: (click.Context, click.Parameter, Optional[str]) -> Optional[str]
  - Description: Enforce that non-empty memory values match ^\d+(Gi|G|Mi|M)$ (case-sensitive); returns unchanged or raises click.BadParameter with the message:
      --memory should be a number then Gi/G/Mi/M e.g 1Gi
  - Usage notes:
    - Use as the callback for a --memory Click option; it treats empty/falsy values as "not provided" and returns them unchanged.

- get_existing_services() -> list[dict]
  - Signature: () -> list[dict]
  - Description: Invoke gcloud to list managed Cloud Run services and return descriptors { "name": str, "created": str, "url": str } for each service.
  - Exceptions callers must handle:
    - subprocess.CalledProcessError if the gcloud CLI exits non-zero.
    - json.JSONDecodeError if output is not valid JSON.
    - KeyError/TypeError if expected keys are missing from parsed JSON entries.
  - Usage notes:
    - Preconditions: gcloud must be installed and authenticated; environment must allow subprocess execution.
    - The function executes the external command: "gcloud run services list --platform=managed --format json".

- cloudrun.publish_subcommand(publish: click.Group) -> None
  - Signature: (click.Group) -> None
  - Description: Register the Cloud Run publish subcommand and implement its runtime logic, using helpers like _validate_memory and get_existing_services.
  - Usage notes:
    - Will integrate Click option wiring via add_common_publish_arguments_and_options.
    - Handles deployment decision (create vs update) based on get_existing_services output.
    - Side effects include subprocess calls and potential network interactions via gcloud.

- heroku.publish_subcommand(publish: click.Group) -> None
  - Signature: (click.Group) -> None
  - Description: Register the Heroku publish subcommand, ensure the Heroku CLI & heroku-builds plugin are available (prompting to install if needed), prepare an app tree, set config vars mapping plugin secrets to env vars, and trigger heroku builds:create or write a generated directory.
  - Exceptions and side effects:
    - May call fail_if_publish_binary_not_installed (which sys.exit(1) when missing).
    - Uses subprocess.check_output and subprocess.call for various heroku commands; callers should be aware of subprocess.CalledProcessError and the non-exception behavior of subprocess.call.
    - Creates or writes files when --generate-dir is used (shutil.copytree).
  - Usage notes:
    - The component-level doc shows no explicit callers present in the preloaded scan; this function is intended to be registered on the publish command group at CLI setup time.
    - Tests should stub subprocess functions and temporary_heroku_directory.

- temporary_heroku_directory(...) -> contextmanager
  - Signature: consult source for exact parameters
  - Description: Prepare a temporary filesystem tree with the generated app and yield control to the caller; its exact behavior (whether it changes the current working directory or yields a path) must be confirmed from the implementation before relying on copy semantics such as shutil.copytree(".", generate_dir).

## Dependencies:
- Internal imports:
  - publish.common: supplies Click option wiring, plugin-secret validation, and binary existence checking used by both provider subcommands.
  - publish.cloudrun and publish.heroku are peers organized under the publish package; they rely on common for shared behavior.
- External libraries and stdlib:
  - click: CLI parsing, callbacks, prompts, and colored error display.
  - subprocess: run/check external provider CLIs and capture/parse output.
  - json: parse JSON output from provider CLIs.
  - re: validate memory format in Cloud Run helper.
  - shutil, os: filesystem operations and copy semantics for generated artifacts.
  - sys: sys.exit used by fail_if_publish_binary_not_installed.
- Test dependency notes:
  - Tests commonly patch subprocess.check_output and subprocess.call, and patch temporary_heroku_directory to yield a controlled environment.

## Constraints:
- Click callback contract:
  - validate_plugin_secret and _validate_memory must be registered as Click callbacks with the signature (ctx, param, value). They expect Click to supply appropriate types (iterable of triplets and Optional[str], respectively).
- Environment and binaries:
  - Heroku flows require the "heroku" CLI on PATH and the heroku-builds plugin for builds-based deployment; Cloud Run flows require the gcloud CLI configured for the target project/region.
  - Component docs indicate no explicit callers were present in the provided code subset — callers should ensure they import and invoke these helpers where appropriate.
- Ordering and initialization:
  - add_common_publish_arguments_and_options must be applied at command-definition time so Click registers the intended options/arguments.
  - Verify temporary_heroku_directory semantics before relying on operations that copy from "."; its behavior is implementation-specific.
- Threading and concurrency:
  - Modules are not designed for concurrent threaded use; they perform process-global actions (running CLIs, writing files, prompting users). For concurrent needs, isolate invocations in separate processes or ensure serialized usage.
- Error handling:
  - Many functions produce side effects and raise or propagate exceptions (subprocess.CalledProcessError, json.JSONDecodeError, OSError, click.BadParameter, click.ClickException, SystemExit). Callers must handle or let these propagate according to CLI semantics.

---

## Files

- [`cloudrun.py`](publish/cloudrun.md)
- [`common.py`](publish/common.md)
- [`heroku.py`](publish/heroku.md)

