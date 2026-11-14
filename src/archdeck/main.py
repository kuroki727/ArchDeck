from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from archdeck.ui.main_window import MainWindow
from archdeck.ui.theme import APP_STYLE


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("ArchDeck")
    app.setOrganizationName("ArchDeck")
    app.setStyleSheet(APP_STYLE)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
