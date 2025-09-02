# To-Do List & Future Development Ideas

This document lists potential improvements and new features for the CompactApp multi-tool runner.

## High Priority

- **[ ] Improve Platform Compatibility**:
    - **[ ] Windows Support**: The Pause/Resume functionality is currently disabled on Windows. Investigate and implement a robust way to manage process states on Windows.
    - **[ ] macOS Support**: The "Speak Selection" hotkey is Linux-only (`xsel`). Implement an equivalent for macOS (e.g., using `pbpaste`).
- **[ ] User-Selectable Rule Files**: Allow the user to choose which text processing rule file to use via a dropdown in the UI. This would make it easy to switch between "e-book" mode and "chatbot" mode.
- **[ ] Add Unit and Integration Tests**: Create a test suite to ensure application stability and prevent regressions. This should cover the `TextProcessorEngine` and key UI interactions.

## Medium Priority

- **[ ] Enhance Text Processor**:
    - **[ ] Add a UI for Rule Editing**: Create a simple interface where users can add, remove, and edit the text processing rules directly within the application, without having to manually edit JSON files.
    - **[ ] Introduce Pre-processing Steps**: Add optional pre-processing steps like HTML tag stripping or markdown-to-text conversion before the rules are applied.
- **[ ] Support for More TTS Engines**:
    - **[ ] eSpeak-NG**: Integrate `espeak-ng` as another TTS option. It's lightweight and widely available.
    - **[ ] Coqui TTS**: Add support for Coqui TTS models.
- **[ ] UI/UX Improvements**:
    - **[ ] Add a "Recent Text" History**: A dropdown to quickly access previously spoken texts.
    - **[ ] Progress Bar for TTS**: For long texts, show a progress bar to indicate that the application is working.
    - **[ ] Better Error Display**: Show non-critical errors in a more user-friendly way than just printing to the log, perhaps with a pop-up or a status bar message that can be clicked for details.

## Low Priority

- **[ ] Theming**: Allow users to select different color themes (e.g., a light theme) or even load custom QSS stylesheets.
- **[ ] Plugin System**: Refactor the mode selection into a plugin-based architecture. This would allow new modes (like new TTS engines or other tools) to be added more easily by developers.
- **[ ] Internationalization**: Add support for multiple languages in the UI.
- **[ ] Packaging**: Create packages for popular Linux distributions (e.g., `.deb`, `.rpm`) to simplify installation.
