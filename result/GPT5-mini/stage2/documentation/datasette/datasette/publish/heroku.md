# `heroku.py`

## `datasette.publish.heroku.publish_subcommand` · *function*

## Summary:
Adds and implements a "heroku" publish subcommand that prepares a Datasette application for Heroku and either writes the generated application files to a local directory or triggers a Heroku build using the Heroku CLI.

## Description:
This function registers, via Click decorators, a runtime handler invoked when a user runs the CLI command "datasette publish heroku". The runtime handler coordinates the following responsibilities:
- Ensures the Heroku CLI is available (via fail_if_publish_binary_not_installed).
- Verifies the heroku-builds plugin is installed (prompts and offers to install it).
- Constructs extra metadata and maps plugin secrets into Heroku environment variables and metadata plugin entries.
- Entrusts preparation of a temporary application directory to a context manager (temporary_heroku_directory), then either copies the generated files to a user-provided directory (--generate-dir) or creates/uses a Heroku app, sets config vars, and triggers a Heroku build.

Known callers and invocation context:
- Called at CLI setup/registration time to attach the "heroku" subcommand to the provided publish command group (publish_subcommand(publish)).
- The inner handler runs when Click invokes the command at runtime (user runs datasette publish heroku ...).

Why extracted:
- Keeps Heroku deployment orchestration and Click wiring in a single place.
- Allows temporary-directory preparation to be implemented, tested, or replaced independently (temporary_heroku_directory is delegated).

Important note about temporary_heroku_directory:
- The implementation of temporary_heroku_directory was not provided with this component. The code calls shutil.copytree(".", generate_dir) inside the context manager, which implies the prepared application files are available at the process's current directory (".") within the with-block. This is an explicit assumption — inspect temporary_heroku_directory's implementation to confirm whether it changes CWD or otherwise exposes the prepared tree at "." before relying on that fact in a reimplementation.

## Args:
    publish (click.Group or compatible):
        Click command group used as a decorator container. The function registers a new subcommand on this group.
    (Runtime options supplied by Click to the inner handler)
        files (tuple[str]): Files / database paths to include (from shared decorator).
        metadata (file-like | None): Optional opened metadata file (JSON/YAML).
        extra_options (str | None): Extra publish options string.
        branch (str | None): Git branch to use (if relevant).
        template_dir (str | None): Path to template directory.
        plugins_dir (str | None): Path to plugins directory.
        static (iterable[tuple[str,str]]): Static mounts converted by shared option parsing.
        install (iterable[str]): Extra packages to install.
        plugin_secret (iterable[tuple[str,str,str]] | None): Iterable of (plugin_name, plugin_setting, setting_value).
        version_note (str | None): Version note text to include in metadata.
        secret (str): Signing secret (provided via decorator default or env var).
        title, license, license_url, source, source_url, about, about_url (str | None): Additional metadata fields.
        name (str): Desired Heroku app name (defaults to "datasette").
        tar (str | None): Path passed through to heroku builds:create as --tar.
        generate_dir (str | None): If provided, the generated app tree is copied to this directory and the command stops without deploying.

Interdependencies:
- plugin_secret entries are used to build both extra_metadata["plugins"] (referencing the variable via {"$env": ENV_VAR}) and a map of environment variables which are later set in Heroku with heroku config:set.

## Returns:
    None
    - At registration time the function returns None after attaching the subcommand. At runtime the inner command returns None; its work is observable via side effects (filesystem writes, Heroku API side effects).

## Raises:
    click.ClickException:
        - If --generate-dir is supplied and the path already exists: raises click.ClickException("Directory already exists").
    click.Abort:
        - If heroku-builds is missing and the user selects "no" at the click.confirm prompt; the code calls click.confirm(..., abort=True) which raises click.Abort on a negative response.
    SystemExit:
        - Raised by fail_if_publish_binary_not_installed("heroku", ...) when the Heroku CLI is not found (that helper calls sys.exit(1)).
    subprocess.CalledProcessError:
        - check_output(...) is used for commands where output is parsed (e.g., "heroku plugins", "heroku apps:list --json", "heroku apps:create --json"). check_output raises CalledProcessError on non-zero exit status.
    json.JSONDecodeError / ValueError:
        - json.loads may raise when parsing JSON returned by Heroku commands (e.g., malformed output from apps:list or apps:create).
    OSError / shutil.Error:
        - shutil.copytree may raise on filesystem errors when writing generate_dir.
    Other exceptions:
        - Any exceptions raised by temporary_heroku_directory or by utilities (link_or_copy, etc.) will propagate.

## Constraints:
Preconditions:
    - Heroku CLI ("heroku") must be installed and discoverable in PATH.
    - The runtime environment must permit spawning subprocesses and file operations.
    - If using --generate-dir, the destination must not already exist and the process must have permission to create it.

Postconditions:
    - If --generate-dir: generate_dir contains a copy of the prepared application tree (provided temporary_heroku_directory places files at "." as assumed).
    - If deploying: a Heroku app will exist (created if necessary), specified env vars will be set on that app, and a heroku builds:create request will have been issued.
    - The temporary work area created by temporary_heroku_directory is expected to be cleaned up by that context manager (verify in its implementation).

## Side Effects:
    - Subprocess calls (external Heroku CLI):
        * check_output(["heroku", "plugins"]) -> returns bytes; code splits lines and takes the first token of each line as a bytes value. The code checks for b"heroku-builds" among these tokens.
        * call(["heroku", "plugins:install", "heroku-builds"]) may be invoked to install the plugin (call returns an exit code; subprocess.call does not raise).
        * check_output(["heroku", "apps:list", "--json"]) -> returns bytes, decoded with UTF-8 (decode("utf8")) before json.loads.
        * check_output(["heroku", "apps:create", name?, "--json"]) -> returns bytes, decoded before json.loads.
        * call(["heroku", "config:set", "-a", app_name, "KEY=VALUE"]) is used to set each environment variable; call returns an exit code and does not raise on non-zero status.
        * call(["heroku", "builds:create", "-a", app_name, "--include-vcs-ignore"] + tar_option) triggers the build; it's invoked with subprocess.call (no exception on non-zero exit code).
    - User interaction:
        * click.confirm reads from stdin and may raise click.Abort when abort=True and the user replies negatively.
        * click.echo writes user-facing messages to stdout/stderr.
    - Filesystem:
        * shutil.copytree(".", generate_dir) copies from the current working directory. The code assumes the prepared application files are available at "." inside the temporary_heroku_directory context.
        * The temporary directory context (temporary_heroku_directory) likely performs linking or copying of input files into a temp tree; inspect its implementation to confirm exact files and behavior.
    - Remote state:
        * Creating apps and setting config vars changes the user's Heroku account resources.

## Control Flow:
flowchart TD
    Start --> EnsureCLI[fail_if_publish_binary_not_installed("heroku") -> may sys.exit(1)]
    EnsureCLI --> PluginsOut[plugins_bytes = check_output(["heroku","plugins"])]
    PluginsOut --> PluginsList[plugins = [line.split()[0] for line in plugins_bytes.splitlines()]]
    PluginsList --> HasBuilds{b"heroku-builds" in plugins?}
    HasBuilds -- No --> ConfirmInstall[click.confirm(..., abort=True)]
    ConfirmInstall -- Yes --> InstallPlugin[call(["heroku","plugins:install","heroku-builds"])]
    ConfirmInstall -- No --> Abort(click.Abort) --> End
    HasBuilds -- Yes --> BuildMetadata[construct extra_metadata & environment_variables]
    BuildMetadata --> WithTempDir[with temporary_heroku_directory(...)]
    WithTempDir --> GenDir?{generate_dir provided?}
    GenDir? -- Yes --> DirExists?{path exists?}
    DirExists? -- Yes --> Raise(click.ClickException) --> End
    DirExists? -- No --> CopyTree[shutil.copytree(".", generate_dir)] --> EchoDone --> End
    GenDir? -- No --> ListApps[check_output(["heroku","apps:list","--json"]) -> decode -> json.loads]
    ListApps --> FindApp{existing app name matches?}
    FindApp -- Yes --> app_name set
    FindApp -- No --> CreateApp[check_output(["heroku","apps:create", name?, "--json"]) -> decode -> json.loads -> app_name]
    AfterApp --> SetEnv[for each env var: call(["heroku","config:set","-a",app_name,"KEY=VALUE"])]
    SetEnv --> CreateBuild[call(["heroku","builds:create","-a",app_name,"--include-vcs-ignore"] + tar_option)]
    CreateBuild --> End

## Examples and concrete behaviors:
- plugin_secret -> env var mapping:
    * Given plugin_secret entry ("my-plugin", "setting-name", "s3cr3t"), the code computes:
      environment_variable = f"{plugin_name}_{plugin_setting}".upper().replace("-", "_")
      -> "MY_PLUGIN_SETTING_NAME"
    * It sets environment_variables["MY_PLUGIN_SETTING_NAME"] = "s3cr3t"
    * It also inserts into extra_metadata["plugins"]["my-plugin"]["setting-name"] = {"$env": "MY_PLUGIN_SETTING_NAME"}
    * Later the command runs: heroku config:set -a <app_name> MY_PLUGIN_SETTING_NAME=s3cr3t

- Typical CLI usage:
    * Deploy: datasette publish heroku /path/to/db.sqlite --name myapp --plugin-secret my-plugin setting-name s3cr3t
      Behavior: ensures CLI & plugin, prepares temp app tree, creates or reuses "myapp", sets MY_PLUGIN_SETTING_NAME on Heroku, triggers heroku builds:create.

    * Generate files only: datasette publish heroku /path/to/db.sqlite --generate-dir ./out
      Behavior: prepares temp tree and copies its contents to ./out; if ./out exists, raises click.ClickException.

- Testing guidance:
    * Stub subprocess.check_output to return bytes:
        - For "heroku plugins": return b"heroku-cli-plugin 1.0.0\nheroku-builds 0.1.0\n" or b"" for no plugins.
        - For JSON commands: return b'[]' or b'[{"name":"myapp"}]' or b'{"name":"generated"}'.
    * Stub subprocess.call to return an exit code (0 success, non-zero failure). Because call() does not raise, tests should assert that call was invoked with expected args rather than relying on exceptions.
    * Replace temporary_heroku_directory with a test double that yields a directory containing known files and (if needed) optionally changes CWD to that directory so shutil.copytree(".", generate_dir) can be asserted against.
    * Ensure to patch fail_if_publish_binary_not_installed to avoid sys.exit in unit tests or to assert that it raises SystemExit when simulating a missing heroku binary.

Notes:
- The code explicitly treats plugin listing output as raw bytes (no decode) and compares bytes tokens (b"heroku-builds"); be sure test stubs reflect this.
- check_output is used where the output is parsed and will raise CalledProcessError on bad exit codes; call is used for operations where the code does not check the return value (install, config:set, builds:create).

## `datasette.publish.heroku.temporary_heroku_directory` · *function*

*No documentation generated.*

