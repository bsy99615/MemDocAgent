# `templates.py`

## `src.ydata_profiling.report.presentation.flavours.html.templates.template` · *function*

## Summary:
Retrieves a Jinja2 template from the global template environment by name.

## Description:
This function provides a convenient interface for accessing pre-configured Jinja2 templates within the ydata-profiling HTML report generation system. It serves as a wrapper around the global Jinja2 environment to simplify template retrieval throughout the application.

## Args:
    template_name (str): The name of the template to retrieve from the Jinja2 environment. This corresponds to a template file in the configured template directory.

## Returns:
    jinja2.Template: A Jinja2 Template object that can be used to render content with provided context data.

## Raises:
    jinja2.TemplateNotFound: When the specified template_name does not exist in the Jinja2 environment.

## Constraints:
    Preconditions:
        - The global `jinja2_env` must be properly initialized before calling this function
        - The `template_name` parameter must be a valid string that corresponds to an existing template
    Postconditions:
        - Returns a valid Jinja2 Template object if the template exists
        - The returned template is ready to be rendered with context data

## Side Effects:
    None

## Control Flow:
```mermaid
flowchart TD
    A[Call template()] --> B{template_name exists?}
    B -- Yes --> C[Return jinja2.Template]
    B -- No --> D[Throw jinja2.TemplateNotFound]
```

## Examples:
    # Retrieve a template for rendering a section header
    header_template = template("section_header.html")
    
    # Render the template with context
    rendered_content = header_template.render(title="Data Overview", level=1)

## `src.ydata_profiling.report.presentation.flavours.html.templates.create_html_assets` · *function*

## Summary:
Creates and populates HTML asset directories with CSS and JavaScript files for report generation by rendering Jinja2 templates.

## Description:
Initializes the HTML assets directory structure and copies necessary CSS and JavaScript files for report styling and functionality. This function prepares the static assets required for HTML reports by creating directories, rendering Jinja2 templates with appropriate configuration context, and writing the rendered content to disk.

## Args:
    config (Settings): Configuration object containing HTML report settings including asset prefix, theme, and style options
    output_file (Path): Path to the output HTML file, used to determine the base directory for assets

## Returns:
    None: This function performs I/O operations and does not return a value

## Raises:
    jinja2.TemplateNotFound: When a required template file cannot be found in the Jinja2 environment

## Constraints:
    Preconditions:
        - config.html.assets_prefix must be properly set
        - config.html.style.theme must be a valid theme enum value or None
        - config.html.style.primary_colors must be properly configured
        - config.html.navbar_show must be a boolean value
        - config.html.use_local_assets must be a boolean value
        - The global `jinja2_env` must be properly initialized
    Postconditions:
        - Asset directory structure is created at config.html.assets_prefix location
        - Required CSS and JS files are written to respective directories
        - Images directory is created within the assets folder

## Side Effects:
    - Creates directories in the file system at config.html.assets_prefix location
    - Removes existing asset directory if it already exists
    - Writes CSS and JavaScript files to disk
    - Creates images directory within the assets folder

## Control Flow:
```mermaid
flowchart TD
    A[create_html_assets] --> B{path.is_dir()?}
    B -- Yes --> C[shutil.rmtree(path)]
    B -- No --> D[Continue]
    D --> E[path.joinpath("images").mkdir()]
    E --> F{config.html.use_local_assets?}
    F -- Yes --> G[Build CSS/JS lists with local assets]
    F -- No --> H[Build CSS/JS lists with default assets]
    H --> I[Add style.css and script.js to CSS/JS lists]
    I --> J{css_dir.exists()?}
    J -- No --> K[css_dir.mkdir()]
    K --> L[Render and write CSS files using template()]
    L --> M{js_dir.exists()?}
    M -- No --> N[js_dir.mkdir()]
    N --> O[Render and write JS files using template()]
```

## Examples:
    # Create HTML assets for a report with custom theme
    config = Settings()
    config.html.assets_prefix = "report_assets"
    config.html.style.theme = "dark"
    config.html.style.primary_colors = ["#007bff", "#6c757d"]
    config.html.navbar_show = True
    config.html.use_local_assets = True
    
    create_html_assets(config, Path("output.html"))
    
    # Result: Creates report_assets/css/ and report_assets/js/ directories
    # with rendered CSS and JS files

