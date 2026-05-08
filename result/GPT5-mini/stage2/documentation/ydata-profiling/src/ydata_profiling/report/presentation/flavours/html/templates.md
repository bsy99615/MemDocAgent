# `templates.py`

## `src.ydata_profiling.report.presentation.flavours.html.templates.template` · *function*

## Summary:
Delegates template lookup to the module Jinja2 environment and returns the resolved Jinja2 Template object ready for rendering.

## Description:
A minimal convenience wrapper around the module-level Jinja2 environment's get_template method. It centralizes access to the environment so callers do not reference the environment object directly and so template-resolution behavior can be changed in one place.

Known callers:
- No direct call sites were discovered in the provided code context. In typical usage within report-generation/presentation code, this function is invoked when code needs to load a template by name prior to rendering (for example, when assembling an HTML report page).

Why this is a separate function:
- Encapsulates access to the module-level environment (jinja2_env), making it straightforward to change the environment, add logging, caching, or custom error handling later without changing callers.
- Keeps call sites concise; callers receive a Template instance and are responsible for rendering and handling template-related errors.

## Args:
    template_name (str): Name or path of the template as interpreted by the configured Jinja2 loader (for example 'index.html' or 'partials/header.html').
    - Type: str (required). The function has no default.
    - No validation or normalization is performed here; the value is passed verbatim to the environment's get_template method.
    - If template_name is not a string, the underlying environment or loader may raise a TypeError.

## Returns:
    jinja2.Template: The Template object returned by the configured jinja2 environment's get_template call.
    - On success: a Template instance that callers can render with Template.render(**context).
    - There are no alternate return paths; on failure the function propagates the underlying exception.

## Raises:
    The function does not catch exceptions; it propagates whatever error arises while accessing the environment or loading the template. Notable exceptions include:
    - NameError: If the module-level name jinja2_env is not defined in the module where this function resides.
    - AttributeError: If jinja2_env exists but does not expose get_template (e.g., misconfigured to None or wrong type).
    - jinja2.exceptions.TemplateNotFound: If the loader cannot locate template_name.
    - jinja2.exceptions.TemplateSyntaxError: If the template has invalid Jinja2 syntax during parsing/compilation.
    - IOError / OSError: If the underlying loader performs filesystem I/O and that I/O fails.
    - Any other exceptions raised by the configured loader or environment are propagated.

## Constraints:
Preconditions:
    - The module-level symbol jinja2_env must exist and reference an object exposing a get_template(str) -> jinja2.Template method (typically an instance of jinja2.Environment).
    - The environment should have appropriate loader(s) configured so that template_name can be resolved.
Postconditions:
    - If the function returns normally, it provides a jinja2.Template instance for the requested template_name.
    - The function itself does not modify module state.

## Side Effects:
    - Possible I/O: Loading a template may perform file reads (or other I/O) depending on the configured loader.
    - No network calls, file writes, or mutation of global state are performed by this wrapper directly.
    - No logging or caching is performed by this function (unless implemented by the environment/loader).

## Control Flow:
flowchart TD
    Start --> Has_jinja2_env[Is module-level jinja2_env defined?]
    Has_jinja2_env -->|No| RaiseNameError[Raise/propagate NameError]
    Has_jinja2_env -->|Yes| HasGetTemplate[Does jinja2_env have get_template?]
    HasGetTemplate -->|No| RaiseAttributeError[Raise/propagate AttributeError]
    HasGetTemplate -->|Yes| CallGetTemplate[Call jinja2_env.get_template(template_name)]
    CallGetTemplate -->|Success| ReturnTemplate[Return jinja2.Template]
    CallGetTemplate -->|TemplateNotFound| PropagateTemplateNotFound[Propagate jinja2.exceptions.TemplateNotFound]
    CallGetTemplate -->|TemplateSyntaxError| PropagateSyntaxError[Propagate jinja2.exceptions.TemplateSyntaxError]
    CallGetTemplate -->|IOError/OSError| PropagateIOError[Propagate I/O exceptions]
    CallGetTemplate -->|OtherError| PropagateOther[Propagate other loader/environment exceptions]
    ReturnTemplate --> End
    RaiseNameError --> End
    RaiseAttributeError --> End
    PropagateTemplateNotFound --> End
    PropagateSyntaxError --> End
    PropagateIOError --> End
    PropagateOther --> End

## Examples:
Basic usage (happy path)
    from src.ydata_profiling.report.presentation.flavours.html.templates import template
    tpl = template("report/index.html")
    html = tpl.render(title="Summary", data=my_context)

Handling missing template explicitly
    from jinja2 import exceptions as jinja_exceptions
    try:
        tpl = template("report/missing.html")
    except jinja_exceptions.TemplateNotFound:
        # Provide fallback behavior (log, user message, fallback template)
        tpl = template("report/fallback.html")
        html = tpl.render(...)

Handling misconfiguration of module environment
    try:
        tpl = template("report/index.html")
    except NameError:
        # Module-level jinja2_env not defined: likely a configuration/initialization error
        initialize_jinja2_environment()
        tpl = template("report/index.html")

Notes:
- Because this function is a direct delegation, callers should expect and handle Jinja2's exceptions rather than relying on this wrapper to provide defaults or fallbacks.
- If project behavior requires returning a default template on missing templates or logging every load, implement that policy here rather than at every call site.

## `src.ydata_profiling.report.presentation.flavours.html.templates.create_html_assets` · *function*

## Summary:
Render and materialize the static HTML asset bundle (images, CSS and JS) next to a target report file by resolving configured asset templates and writing them into a directory derived from the provided output file and configuration.

## Description:
This function prepares the on-disk assets required for an HTML report. It:
- Computes the assets directory as output_file.with_name(str(config.html.assets_prefix)).
- If that path exists and is a directory, removes it entirely using shutil.rmtree (destructive).
- Ensures an images directory exists under the computed assets path (created with parents=True, exist_ok=True).
- Builds ordered lists of CSS and JS template identifiers:
  - If config.html.use_local_assets is True:
    - CSS: theme-specific bootstrap file (if config.html.style.theme is set: "wrapper/assets/{theme.value}.bootstrap.min.css") or both "wrapper/assets/bootstrap.min.css" and "wrapper/assets/bootstrap-theme.min.css" if theme is None.
    - JS: "wrapper/assets/jquery-1.12.4.min.js" and "wrapper/assets/bootstrap.min.js"
  - Always appended afterwards: CSS gets "wrapper/assets/style.css"; JS gets "wrapper/assets/script.js"
- Creates the css directory (path/css) only if it does not already exist; when created, each CSS template is resolved via template(template_name), rendered with context (primary_colors=config.html.style.primary_colors, nav=config.html.navbar_show, style=config.html.style), and written to path/css/<basename_of_template>.
- Creates the js directory (path/js) only if it does not already exist; when created, each JS template is resolved and rendered (no context) and written to path/js/<basename_of_template>.

Important behavioral points:
- The function writes CSS/JS files only when the corresponding css or js directory does not already exist. If a css/js directory exists prior to the write-step, that directory is left unchanged and no files are written into it by this function.
- Because the function removes the entire top-level assets directory when it exists as a directory, the typical path is: either the top-level path is removed (so css/js are then created and written), or the top-level path did not exist (so css/js will be created and written). The only time css/js pre-existence could cause skipping is when the top-level path did not exist as a directory and the css/js directories were somehow already present at the exact computed locations (this is unusual); see "Edge cases" below.
- If the computed assets path exists but is a regular file (not a directory), the function will not call rmtree (path.is_dir() will be False) and subsequent attempts to mkdir under that path will raise OSError/FileExistsError. Callers should guard against assets_prefix producing a path that collides with an existing file.

Known callers:
- No direct call sites were found in the provided snapshot. Typical usage is from higher-level HTML report generation/export logic that, after choosing an output_file for the report HTML, needs to materialize a sibling assets directory so the report can be viewed locally with included CSS/JS.

Why this is a separate function:
- Centralizes filesystem and templating logic for asset creation, including theme handling, destructive-clean semantics, and the policy to skip writing if target subdirectories already exist. This keeps report-generation code focused on content and lets asset materialization be tested and modified independently.

## Args:
    config (Settings)
        - Type: Settings-like configuration object.
        - Required nested attributes:
            * config.html.assets_prefix: used (via str()) as the name component when computing assets path with output_file.with_name(...).
            * config.html.use_local_assets: bool controlling inclusion of bootstrap/jquery assets.
            * config.html.style:
                - style.theme: optional enum-like object with .value used for themed bootstrap file selection.
                - style.primary_colors: passed to CSS template rendering as primary_colors.
            * config.html.navbar_show: passed to CSS template rendering as nav.
        - No implicit validation is performed; missing or mis-typed attributes will raise AttributeError or other errors on access.

    output_file (Path)
        - Type: pathlib.Path
        - Meaning: the intended report file path. The assets path is computed by replacing output_file's name with assets_prefix (Path.with_name). Example: output_file=Path("/out/report.html"), assets_prefix="report-assets" → assets path = /out/report-assets.
        - Must be a Path with a name component; with_name will raise if the provided assets_prefix is not a valid name.

## Returns:
    None — performs filesystem side effects and returns None on success.

## Raises:
    - AttributeError:
        * If config or any required nested attributes are missing.
    - TypeError:
        * If output_file does not support with_name or assets_prefix cannot be converted to a string name.
    - OSError / IOError / FileExistsError:
        * From shutil.rmtree if deletion fails (permissions, in-use files).
        * From path.joinpath("images").mkdir(parents=True, exist_ok=True) or css/js mkdir/write_text if filesystem state prevents directory creation or file writing.
        * If the computed assets path exists as a regular file, subsequent mkdir calls will raise FileExistsError/OSError.
    - jinja2.exceptions.TemplateNotFound:
        * If template(template_name) cannot locate a referenced template in the css/js lists.
    - jinja2.exceptions.TemplateSyntaxError or other jinja2 rendering exceptions:
        * If a template fails to parse or render (CSS templates are rendered with context).
    - Any other exceptions raised by template(...) or underlying filesystem/template operations are propagated.

## Constraints:
Preconditions:
    - output_file must be a valid Path with a file-name component.
    - config must provide the html subtree and attributes named above.
    - The process must have permission to delete/create directories and write files at the computed assets location.
    - The Jinja2 environment behind template(...) must be configured so that the "wrapper/assets/..." templates can be resolved.

Postconditions:
    - On successful return:
        * The computed assets directory exists and contains an images subdirectory.
        * The css subdirectory exists and contains rendered CSS files if and only if css_dir did not exist before the function attempted to create it (i.e., files are written when css_dir is created during this call).
        * The js subdirectory exists and contains rendered JS files if and only if js_dir did not exist before the function attempted to create it.
        * Any previous assets directory that existed as a directory at the start of the call has been removed before new directories/files are created.
    - If an exception occurs, filesystem changes may be partial (e.g., images created, but css/js not written).

## Side Effects:
    - Deletes an existing assets directory (recursively) when that path is a directory.
    - Creates directories:
        * path/images (using parents=True, exist_ok=True) — this ensures the top-level assets path exists.
        * path/css and path/js are created only when they do not already exist (css_dir.mkdir() and js_dir.mkdir()).
    - Writes files:
        * For each CSS template rendered, writes to path/css/<basename_of_template> (using write_text); this happens only when css_dir is created by this function during the call.
        * For each JS template rendered, writes to path/js/<basename_of_template> (write_text); likewise only when js_dir is created during the call.
    - Calls template(template_name) for each referenced template, which may trigger template-loader I/O.

## Control Flow:
flowchart TD
    Start --> ReadTheme[Read config.html.style.theme as theme]
    ReadTheme --> ComputeAssetsPath[Compute path = output_file.with_name(str(config.html.assets_prefix))]
    ComputeAssetsPath --> PathIsDir{path.is_dir()?}
    PathIsDir -->|Yes| DeleteOld[Call shutil.rmtree(path)]
    PathIsDir -->|No| Continue
    DeleteOld --> EnsureImages
    Continue --> EnsureImages
    EnsureImages[Call path.joinpath("images").mkdir(parents=True, exist_ok=True) — guarantees top-level path exists] --> BuildLists[Initialize css=[], js=[]; if use_local_assets: add bootstrap/js entries (theme-dependent)]
    BuildLists --> AppendBaseAssets[Append wrapper/assets/style.css and wrapper/assets/script.js]
    AppendBaseAssets --> CssDirExists{(path/css).exists()?}
    CssDirExists -->|No| CreateCssDir[path/css.mkdir()]
    CssDirExists -->|Yes| SkipCssWrite[Do not create or write into css directory]
    CreateCssDir --> ForEachCss[For each css_file: tpl=template(css_file); content=tpl.render(primary_colors, nav, style); write to path/css/<basename>]
    ForEachCss --> JsDirExists{(path/js).exists()?}
    SkipCssWrite --> JsDirExists
    JsDirExists -->|No| CreateJsDir[path/js.mkdir()]
    JsDirExists -->|Yes| SkipJsWrite[Do not create or write into js directory]
    CreateJsDir --> ForEachJs[For each js_file: tpl=template(js_file); content=tpl.render(); write to path/js/<basename>]
    ForEachJs --> End[Return None]

## Examples and error-handling recommendations:
- Typical invocation (conceptual):
    - Compute output_file (e.g., Path("/out/report.html")) and configure config.html.assets_prefix = "report-assets".
    - Call create_html_assets(config, output_file). Result: /out/report-assets/images, /out/report-assets/css/* and /out/report-assets/js/* are created and populated as described.

- Recommended robust wrapper pattern (conceptual):
    - Call create_html_assets inside a try/except that handles:
        * jinja2.exceptions.TemplateNotFound and TemplateSyntaxError: log the specific template issues and optionally fall back to minimal assets or abort.
        * OSError/FileExistsError: handle permission issues, invalid assets_prefix collisions with existing files, or disk errors; surface helpful messages and avoid silent failures.
    - Validate config.html.assets_prefix prior to calling to ensure it will produce a safe directory name and will not collide with system files.

Edge cases and implementation hints:
- Filename collisions: files are written using the basename of the template identifier (Path(template_name).name). Two different template identifiers that share the same basename will overwrite one another when written; avoid such collisions.
- If assets_prefix accidentally matches the name of an existing file at the same parent directory, subsequent mkdir for images or css/js will fail — guard against this by ensuring assets_prefix yields a unique directory name.
- Ensure the Jinja2 environment behind template(...) can resolve the "wrapper/assets/..." templates referenced by this function; otherwise TemplateNotFound will be raised.

