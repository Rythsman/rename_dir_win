"""Program entry for Windows directory prefix renamer.

This launches the PySimpleGUI-based UI.
"""

from app.ui import run_app


def main() -> None:
    """Start the GUI application."""
    run_app()


if __name__ == "__main__":
    main()


