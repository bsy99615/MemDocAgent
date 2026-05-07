# `datasette.views`

## Tree:
    views/
    ├── database.py
    ├── index.py
    ├── row.py
    ├── special.py
    └── table.py

## Role:
    Implements web interface views for Datasette's database exploration and management features

## Description:
The views module provides the web interface components that enable users to explore, query, and manage databases through Datasette's HTTP API. It handles various aspects of database interaction including database browsing, table viewing, row inspection, query execution, and special administrative endpoints. The module organizes these functionalities into distinct view classes that work with Datasette's core architecture to deliver a rich web-based database exploration experience.

## Components:
    - DatabaseDownload: Handles database file downloads with permission checks and ETag support
    - DatabaseView: Renders database overview pages including tables, views, and queries
    - MagicParameters: Provides dynamic parameter resolution for views using plugin hooks
    - QueryView: Executes custom SQL queries and manages query results
    - IndexView: Displays the main index page listing all accessible databases
    - RowView: Retrieves and renders individual table rows with metadata
    - AllowDebugView: Debug endpoint for testing authorization policies
    - AuthTokenView: Handles root token authentication for initial access
    - JsonDataView: Serves structured JSON data with HTML rendering option
    - LogoutView: Manages user logout functionality
    - MessagesDebugView: Debug interface for adding messages to Datasette
    - PatternPortfolioView: Renders pattern portfolio documentation page
    - PermissionsDebugView: Debug endpoint for inspecting permission checks
    - Row: Represents a single database row with access to raw and formatted values
    - TableView: Renders database tables with filtering, sorting, and pagination
    - _sql_params_pks: Helper function for constructing SQL queries by primary key
    - display_columns_and_rows: Formats database rows for web display with metadata

## Public API:
    - DatabaseDownload.get: Handles database download requests with security checks
    - DatabaseView.data: Returns database metadata for rendering overview pages
    - MagicParameters: Dictionary subclass for dynamic parameter resolution
    - QueryView.data: Executes SQL queries and returns results for display
    - IndexView.get: Renders main index page with database listings
    - RowView.data: Retrieves and formats individual row data for display
    - AllowDebugView.get: Tests authorization policies via web interface
    - AuthTokenView.get: Authenticates users with root tokens
    - JsonDataView.get: Serves JSON data with optional HTML rendering
    - LogoutView.get/post: Handles user logout with cookie clearing
    - MessagesDebugView.get/post: Adds debug messages to Datasette instance
    - PatternPortfolioView.get: Renders pattern portfolio documentation
    - PermissionsDebugView.get: Displays permission check history
    - Row: Row data structure with access to raw/formatted values
    - TableView.data: Renders database tables with advanced features
    - _sql_params_pks: Helper for constructing primary key-based SQL queries
    - display_columns_and_rows: Formats database rows for web display

## Dependencies:
    - Internal: datasette (core Datasette application), datasette.utils (utility functions)
    - External: aiohttp (ASGI request/response handling), jinja2 (template rendering)

## Constraints:
    - All views must inherit from appropriate base classes (DataView, BaseView)
    - Views must implement async get() or data() methods for request handling
    - Permission checks must be performed before accessing sensitive data
    - Database connections must be properly managed and closed
    - All public APIs must be thread-safe and idempotent where appropriate

---

## Files

- [`database.py`](views/database.md)
- [`index.py`](views/index.md)
- [`row.py`](views/row.md)
- [`special.py`](views/special.md)
- [`table.py`](views/table.md)

