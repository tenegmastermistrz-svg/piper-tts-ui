# Code Conventions

This document outlines the coding conventions used in the CompactApp project.

## Naming Conventions

- **Classes**: `PascalCase` (e.g., `CompactApp`, `TextProcessorEngine`).
- **Functions and Methods**: `snake_case` (e.g., `setup_ui`, `load_settings`).
- **Variables**: `snake_case` (e.g., `main_layout`, `piper_path`).
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `CONFIG_DIR`, `CONFIG_FILE`).

## Code Style

- **General**: The code generally follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code.
- **Line Length**: Lines are kept to a reasonable length, generally under 120 characters, to enhance readability.
- **Docstrings**: Functions and methods have docstrings explaining their purpose, although this is not yet universally applied.
- **Typing**: The code uses Python's `typing` module for type hints to improve code clarity and allow for static analysis.

## PyQt5 UI Styling

- **Stylesheet**: The application uses a custom QSS (Qt StyleSheet) for a modern, dark theme. The stylesheet is defined within the `get_modern_stylesheet` method.
- **Custom Properties**: Custom properties like `accent="true"` and `status="ready"` are used in the stylesheet to apply specific styles to widgets. This is a powerful technique for creating a consistent and themeable UI.
- **Layouts**: The UI is structured using `QVBoxLayout`, `QHBoxLayout`, and `QFormLayout` for arranging widgets. `QSpacerItem` is used for flexible spacing.

## File Structure

- **Main Application**: The main application logic is contained in `piperui.py`.
- **Configuration**:
  - Application settings are stored in `~/.config/CompactApp/settings.json`.
  - Text processing rules are defined in separate `.json` files (e.g., `rules_definitions.json`). This makes the rules easily modifiable without changing the application code.

## Logging

- A custom logging mechanism is implemented using PyQt5's signal/slot system (`log_signal`).
- Log messages are displayed in a `QTextEdit` widget in the UI.
- Messages are timestamped and can be color-coded based on their type (e.g., INFO, ERROR, WARN).

## Error Handling

- `try...except` blocks are used to handle potential errors, such as `FileNotFoundError` when loading settings or models, and `Exception` during hotkey listener setup.
- Process exit codes are checked in `on_process_finished` to determine if a command executed successfully.
