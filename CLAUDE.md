# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a webhook utility with dashboard and sound notification system for tracking work completion in various VibeCoding projects. The project is currently in its initial state with only basic configuration files.

## Development Setup

This appears to be a Python project based on the .gitignore configuration. Common Python development patterns apply:

### Environment Setup
- Use a virtual environment (`.venv`, `venv/`, or similar)
- Install dependencies from `requirements.txt` or `pyproject.toml` (when created)
- The project uses Python standard development practices

### Code Quality Tools
Based on the .gitignore, this project may use:
- **Ruff** for linting and formatting (`.ruff_cache/` is ignored)
- Standard Python testing frameworks (`.pytest_cache/` is ignored)
- Coverage reporting (`.coverage`, `coverage.xml`, `htmlcov/` are ignored)

## Key Architectural Patterns

Since this is a webhook utility project, expect the following common patterns:
- **Webhook endpoints**: HTTP handlers for receiving external notifications
- **Dashboard UI**: Web interface for monitoring project status
- **Sound notifications**: Audio alert system for work completion events
- **Project tracking**: System to monitor multiple VibeCoding projects

## License

This project is licensed under the GNU General Public License v3.0. All contributions must comply with GPL-3.0 requirements, including:
- Source code must remain open source
- Modified versions must be clearly marked as changed
- No proprietary restrictions on the software usage
- Отвечай всегда на русском
- Commits should be in Russian and English with clear descriptions of changes. No personal signatures required.
- Если в процессе работы создавались временные файлы, то в конце работы надо их удалить.