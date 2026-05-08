# `tasks.py`

## `clean` · *function*

## Summary:
Removes build, distribution, and common test/cache artifacts by running a single shell command through the provided Invoke context.

## Description:
- Known callers:
    - Typically invoked from the command line via the Invoke task runner (e.g., `invoke clean`) when this function is exposed as an Invoke task.
    - Can be called directly from other task functions or automation scripts that receive an Invoke Context object and need to perform repository cleanup.
- Why this logic is extracted:
    - Centralizes cleanup of common build/test artifacts into one small unit so other tasks or developers can reuse the standardized cleanup command instead of duplicating the shell invocation.
    - Keeps the CLI-facing task thin and focused on the side-effect (removal of generated artifacts) rather than implementing shell command orchestration inline in many places.

## Args:
    context (object): An Invoke Context-like object that exposes a `run(command: str, **kwargs)` method.
        - Expected type: invoke.context.Context (or any object implementing a compatible `run` method).
        - There are no default values; the caller must supply the context.
        - Interdependencies: The function relies on `context.run` to execute the shell command. The context must be configured (e.g., with working directory and environment) by the caller if non-default behavior is needed.

## Returns:
    None
    - The function does not return a value; its effect is performed via the side-effect of executing the shell command.
    - There are no success codes returned to the caller; success is indicated by normal completion (no exception).

## Raises:
    - Any exception propagated from `context.run` when the underlying shell command fails or the run invocation encounters an error.
      - Example cases that will cause an exception to be raised: non-zero exit status of the executed command, permission errors, or misconfigured context. The function itself does not catch or translate these exceptions.

## Constraints:
- Preconditions:
    - `context` must be non-None and must implement a callable `run(command: str, **kwargs)` method.
    - Caller should ensure the process has appropriate filesystem permissions; otherwise the underlying command may fail.
- Postconditions:
    - On successful completion, the following paths (if present in the current working directory) will have been removed: `dist`, `build`, `.coverage`, `.pytest_cache`, `.mypy_cache`.
    - The filesystem state is mutated: files/directories listed above will no longer exist in the working directory after success.

## Side Effects:
- I/O:
    - Executes a shell command using `context.run`, which spawns a shell process and performs filesystem operations.
    - No network I/O is performed.
- External state mutations:
    - Permanently deletes (recursively and forcefully) the following directories/files relative to the current working directory: `dist`, `build`, `.coverage`, `.pytest_cache`, `.mypy_cache`.
- External service calls:
    - None beyond invoking the local shell via `context.run`.

## Control Flow:
flowchart TD
    Start --> CallRun[Call context.run("rm -rf dist build .coverage .pytest_cache .mypy_cache")]
    CallRun -->|success (exit code 0)| Return[Return None]
    CallRun -->|failure (non-zero exit or error)| Propagate[Propagate exception from context.run]

## Examples:
- Typical usage as an Invoke task (CLI):
    - If this function is registered as an Invoke task, run from the repository root:
      - `$ invoke clean`
    - The Invoke runtime supplies the `context` automatically.

- Calling from another Python task with basic error handling:
    - Example:
      - try:
          clean(context)
        except Exception as exc:
          # log or handle the failed cleanup; exc is whatever context.run raised
          print("Clean failed:", exc)

    - Notes:
      - Wrapping the call in try/except is recommended if you want to continue other tasks even when cleanup fails.
      - For dry-run or safe testing, configure the context to run commands in a sandbox or change the command instead of calling this function directly.

## `test` · *function*

*No documentation generated.*

## `install` · *function*

## Summary:
Execute the external command "python setup.py develop" via a provided execution context, triggering an editable/development installation of the project if the command succeeds.

## Description:
- Known callers within the codebase:
  - No direct Python callers were found in the inspected repository files. The function is implemented in a tasks file and is compatible with Invoke-style contexts; it can be invoked by an Invoke task entry (if registered/decorated) or called programmatically by other task functions or scripts that obtain a compatible context.
- Why this is a separate function:
  - Isolates the single responsibility of running the project's development-install command so callers do not need to inline the command string or know how to invoke shell commands. This centralization makes it easier to change the command, add logging, or add pre/post hooks in one place without modifying callers.

## Args:
- context (object)
  - Type: any object implementing a run(command: str, **kwargs) method.
  - Required: yes
  - Constraints:
    - The object must be non-None and must expose a callable attribute named run that accepts at least a single positional command string.
    - The implementation of run determines how the command is executed (synchronously, asynchronously, capturing output, raising on non-zero exit, etc.).

## Returns:
- None
  - The function does not return a value (implicitly returns None). Successful completion is indicated by the function returning normally (no exception raised). Any result object produced by the underlying context.run is not returned or inspected by this function.

## Raises:
- AttributeError
  - If the provided context is None or does not have a run attribute, Python will raise AttributeError when attempting to access context.run.
- Any exception raised by context.run
  - The function does not handle exceptions from the execution; exceptions raised by the underlying run method (for example, due to a failing command, missing interpreter, or permission errors) propagate to the caller.

## Constraints:
- Preconditions:
  - The current working directory (or the environment in which the command runs) should be appropriate for running "python setup.py develop" — typically the project root that contains setup.py.
  - A Python interpreter named "python" must be available in PATH or otherwise resolvable by the shell invoked by context.run.
  - The caller must supply a context object with a working run(command: str, ...) method.
- Postconditions:
  - If the function returns normally, the external command "python setup.py develop" has completed (its side effects depend entirely on the project's setup.py and the environment).
  - The in-process Python state (variables, globals) is unchanged by this function aside from any state mutations performed by code executed indirectly by the external command.

## Side Effects:
- I/O and external process:
  - Executes an external command via context.run which typically results in subprocess execution, producing stdout/stderr and exit status.
- File system and environment:
  - The external command may modify the file system or system environment (for example, installing files, writing metadata, or invoking arbitrary code in setup.py); those effects are not controlled by this function and depend on setup.py implementation and the execution environment.
- No direct network or database calls are made by this function itself, but the invoked setup.py or its dependency installation steps may perform network I/O.

## Control Flow:
flowchart TD
    A[Start] --> B{context is provided?}
    B -- No --> E[AttributeError when accessing context.run]
    B -- Yes --> C[Invoke context.run("python setup.py develop")]
    C --> D{context.run succeeds?}
    D -- Yes --> F[Return None]
    D -- No --> G[Exception from context.run propagates to caller]

## Examples:
- CLI (when registered as a task):
  - If this function is exposed to Invoke (e.g., registered or decorated elsewhere), running the corresponding CLI task will execute "python setup.py develop" in the current working directory. Example command: invoke install
- Programmatic usage:
  - Callers that orchestrate tasks can call this function and pass an Invoke-like context obtained from the Invoke runtime, or any object implementing run(command: str, **kwargs). In tests, provide a test double implementing run that records the command string and optionally simulates success or raises an exception so callers can assert behavior.
- Error-handling guidance:
  - To handle failures, wrap the call in a try/except block that catches exceptions from context.run (or AttributeError for missing run) and implement retry, logging, or cleanup as appropriate for your environment.

## `release` · *function*

## Summary:
Runs the standard packaging build and upload commands to create source and wheel distributions and upload them (via twine) to the configured Python package index.

## Description:
This function performs two sequential shell operations: (1) builds a source distribution and wheel by invoking setup.py, and (2) uploads all files in the dist/ directory using twine. It is intended to centralize the packaging-and-publish steps so they can be invoked from a task runner or calling script rather than being inlined into multiple places.

Known callers within the codebase:
    - None discovered in the local repository. Common invocation contexts (external to this repo) are:
        * As an Invoke task from the command line (e.g., running the tasks file with the Invoke CLI).
        * From automation scripts that import this function and supply an invoke-like Context object.

Why this logic is extracted:
    - Encapsulates the two-step packaging + upload workflow (build then upload) so callers need only invoke a single task.
    - Keeps command details (exact setup.py flags and twine invocation) in one place to avoid duplication and to allow future central changes (e.g., adding flags, cleanup steps, or dry-run behavior).

## Args:
    context (object): Required. An invoke-like execution context providing a run(command: str, **kwargs) method.
        - Expected interface: context.run(cmd: str, **kwargs) where cmd is a shell command string.
        - The function does not rely on specific run() keyword arguments, but typical Context.run accepts warn, hide, pty, etc.
        - Interdependencies: context must be configured to run commands from the project's root directory (or caller must ensure the current working directory is correct) so that setup.py and the resulting dist/ directory are present or created.

## Returns:
    None
    - The function does not return any value; it performs side-effectful operations. Successful completion implies the two commands completed without raising exceptions.

## Raises:
    - Propagates any exceptions raised by context.run for either command.
        * Typical failure modes include non-zero process exit statuses from the build or upload commands. In common invoke implementations, a non-zero exit will raise an execution exception (for example, an UnexpectedExit-like exception) which will propagate to the caller.
    - Any runtime errors from the environment (e.g., missing setup.py, missing twine installation, network failures, authentication failures) will surface as the underlying command/process errors.

## Constraints:
Preconditions:
    - The caller must provide a context with a functional run() method.
    - The current working directory must contain a valid setup.py and a correctly configured packaging environment.
    - twine must be installed and configured (credentials or token available) if an upload is expected to succeed.
    - Network access and repository permissions are required for uploading to a remote package index.

Postconditions (guaranteed if the function returns without raising):
    - The project's distribution artifacts (source and wheel) will have been created in the dist/ directory by the setup.py invocation.
    - twine will have been invoked to upload the contents of dist/*. Any artifacts present in dist/ at the time of upload are uploaded (subject to twine and index behavior).

## Side Effects:
    - Executes two shell commands, causing local filesystem changes (creating or overwriting files under dist/).
    - Network I/O and remote side effects: uploads packages to the configured Python package index (e.g., PyPI or other index reachable by twine).
    - May produce console output (stdout/stderr) and may prompt for authentication depending on twine/configuration.
    - No modifications to in-process global variables are performed by this function itself.

## Control Flow:
flowchart TD
    Start --> RunBuild["Run: python setup.py register sdist bdist_wheel"]
    RunBuild --> BuildSuccess{"Build exit status == 0?"}
    BuildSuccess -- No --> FailBuild["Raise/propagate execution error"]
    BuildSuccess -- Yes --> RunUpload["Run: twine upload dist/*"]
    RunUpload --> UploadSuccess{"Upload exit status == 0?"}
    UploadSuccess -- No --> FailUpload["Raise/propagate execution error"]
    UploadSuccess -- Yes --> Success["Return (None)"]

## Examples:
    - Command-line (Invoke): after making this tasks file available to Invoke, call the task runner to execute the packaged steps (e.g., run the release task from the Invoke CLI to build and upload the package).

    - Programmatic invocation (described):
        * Caller constructs or receives an invoke-like context object that exposes a run(command) method.
        * Caller calls this function with that context; if the build or upload fails the exception from the run call will propagate and the caller can catch and handle it (for example, to report failure or retry).

## `bump` · *function*

## Summary:
Runs an external bumpversion command for the specified segment and then amends the most recent Git commit, producing an updated repository state that reflects the version change.

## Description:
This function executes two shell commands, in sequence, via the provided context:
1) bumpversion <version>
2) git commit --amend

Known callers within the provided source context:
    - None found in the provided files.

Typical trigger / usage context:
    - Intended to be used as part of a release or version-bump workflow (for example, invoked from an Invoke task or another release script). It centralizes the two-step process of updating the version metadata and adjusting the repository commit history.

Why this is a separate function:
    - Encapsulates the small but frequently repeated sequence of commands used to bump a package or project version and then amend the last commit. This makes reuse in multiple tasks or scripts straightforward and keeps higher-level task definitions concise.

## Args:
    context (object): Required. An object that provides a run(command: str, ...) method used to execute shell commands (in Invoke, this is typically an invoke.Context). The function calls context.run twice with string arguments.
    version (str): Optional. Defaults to "patch". Passed verbatim into the bumpversion command (interpolated into "bumpversion %s"). Accepted values are determined by the installed bumpversion tool and its configuration (common values include "patch", "minor", "major", or a named part defined in project configuration).

Interdependencies:
    - The value of version is directly inserted into the shell command; invalid values will cause the bumpversion invocation to fail.

## Returns:
    None.
    - The function does not return any value. Success is indicated by both context.run calls completing without raising an exception.

## Raises:
    - Any exception raised by context.run will propagate out of this function. In practice, this will occur when one of the executed shell commands exits with a non-zero status or when context.run itself encounters an execution error.
    - No exceptions are explicitly raised by this function's code.

## Constraints:
Preconditions:
    - The caller must provide a context object with a working run(command: str, ...) method.
    - The current working directory (as seen by context.run) should be a Git repository when running git commands.
    - The bumpversion tool (or an equivalent command named bumpversion) must be installed and properly configured for the project if a successful version update is expected.

Postconditions (if no exception is raised):
    - The "bumpversion <version>" command was executed.
    - The "git commit --amend" command was executed.
    - Repository and filesystem state changes produced by those commands (e.g., updated files, updated commit) have been applied.

## Side Effects:
    - Executes two external shell commands via context.run:
        1) "bumpversion <version>" — may update files, tags, or create commits depending on the installed tool and configuration.
        2) "git commit --amend" — amends the most recent commit in the repository.
    - These commands may mutate repository state, write files, and affect the local Git history.
    - No network I/O is invoked by this function directly; any network access would be caused by the external commands themselves (if they perform network actions).
    - No stdout/stderr handling is performed here beyond what context.run does; output and error handling are delegated to the context.run implementation.

## Control Flow:
flowchart TD
    Start --> RunBumpversion
    RunBumpversion -->|success| RunGitAmend
    RunBumpversion -->|failure (exception)| Error
    RunGitAmend -->|success| End
    RunGitAmend -->|failure (exception)| Error
    Error --> End

## Examples:
- Invocation from a calling script that supplies an Invoke-like context (illustrative only):
    - bump(ctx, "minor")
      This will execute:
        - bumpversion minor
        - git commit --amend

- CLI usage (if this function is exposed as an Invoke task named "bump"):
    - inv bump --version=minor
      Note: exposing this function as a task and the exact CLI flags depend on how the task is registered in the tasks module.

- Error handling pattern (conceptual):
    - If either external command fails, context.run will raise an error and the caller can catch it to abort the release flow or log the failure.

## `docker` · *function*

## Summary:
Builds a Docker image from the current directory with fixed tags and then pushes all tags for the misobelica/sumy repository to the configured Docker registry.

## Description:
This function runs two shell commands via the provided context.run:
1. Builds a Docker image from the current working directory using a no-cache build and applies two tags: misobelica/sumy:latest and misobelica/sumy:0.11.0.
2. Pushes all tags of the misobelica/sumy repository to the remote registry.

Known callers within the codebase:
- No direct call sites were found in the inspected repository snapshot. The file imports invoke.task, which indicates this function is intended to be called as an Invoke task (i.e., invoked from the command line with an Invoke runner) or invoked directly by other task orchestration code.

Typical trigger / pipeline stage:
- Use this function when releasing or publishing a new Docker image for the project — typically as part of a release pipeline step that builds and uploads images to a registry.

Why this logic is a separate function:
- Encapsulates the small but repeatable build-and-push workflow into a single unit that can be invoked from a task runner or CI job. Separating these operations improves reuse (call from CI, local invoke CLI) and makes the push-and-build step easy to reason about and replace.

## Args:
    context (object): A runtime/context object providing a run(command: str) -> result method.
        - Expected type: invoke.Context (from the Invoke library) or any compatible object.
        - Behavior: context.run(command) is used to execute shell commands synchronously and will propagate errors raised by the runner.
        - No other parameters are accepted; all settings (image name, tags, flags) are hard-coded in the function.

## Returns:
    None
    - On success: the function returns None after both commands complete successfully.
    - If the build command fails: the function will not attempt the push and will propagate the exception from context.run.
    - If the build succeeds but the push fails: the build has already produced local images/tags, and the function will propagate the exception from context.run raised during the push.

## Raises:
    - Any exception raised by context.run when the invoked shell command fails (non-zero exit). Typical examples:
        - invoke.exceptions.UnexpectedExit (when using Invoke's Context.run) or
        - subprocess.CalledProcessError / OSError if a different runner is used or the docker CLI is absent.
    - These exceptions are not caught inside the function and will propagate to the caller.

## Constraints:
Preconditions:
    - Current working directory must contain a valid Dockerfile and all files referenced by it (the build context).
    - Docker CLI must be installed and available on PATH.
    - Docker daemon must be running and reachable by the CLI.
    - If pushing to a private or authenticated registry, the runtime must be logged in and have push permissions for misobelica/sumy.
    - Network connectivity to the registry must be available for the push step.

Postconditions:
    - If the function returns successfully:
        - The local Docker daemon contains an image tagged misobelica/sumy:latest and misobelica/sumy:0.11.0.
        - The registry has received pushed tags for misobelica/sumy (assuming push succeeded and registry accepted them).
    - If the function raises an exception:
        - No guarantees beyond what the Docker CLI and context.run provide (partial side effects possible, e.g., a partially completed build).

## Side Effects:
    - I/O: Executes two shell commands that write to stdout/stderr; output will typically be streamed to the console by the runner.
    - Docker daemon state: Creates one or more images/containers as part of the build; intermediate containers may be removed due to --rm=true, but the resulting images remain.
    - Network: Push sends image layers to a remote registry (network usage and potential authentication).
    - No file system writes are performed by this function directly aside from those the docker build may perform inside the Docker daemon.

## Control Flow:
flowchart TD
    Start --> BuildCmd[Run: docker build --no-cache --rm=true --tag misobelica/sumy:latest -t misobelica/sumy:0.11.0 .]
    BuildCmd --> |success| PushCmd[Run: docker push misobelica/sumy --all-tags]
    BuildCmd --> |failure| FailBuild[Raise/propagate context.run exception]
    PushCmd --> |success| End[Return None]
    PushCmd --> |failure| FailPush[Raise/propagate context.run exception]
    FailBuild --> End
    FailPush --> End

## Examples:
1) Invoke CLI (recommended when this function is registered as an Invoke task):
    - From the repository root (where tasks.py resides and contains this function as an Invoke task), run:
      inv docker
    - Expected outcome: docker build completes, then docker push uploads all tags for misobelica/sumy. On failure, the CLI shows the failing command's output and exits non-zero.

2) Direct call from Python (when you have an Invoke Context or compatible runner):
    - Prepare a context object with a run(cmd) method and call the function. If any invoked command fails, handle or log the propagated exception.
    - Error handling pattern:
        - Try calling the function.
        - Catch exceptions from context.run (e.g., invoke.exceptions.UnexpectedExit or OSError) to detect build/push failures and act accordingly (retry, abort release, alert).

Note:
    - The image name and tags are hard-coded. To publish images under different names/tags, modify the function or provide an alternative wrapper that constructs dynamic command strings.

