from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget,
)

from archdeck.pages.overview import OverviewPage
from archdeck.pages.packages import PackagesPage
from archdeck.pages.placeholder import PlaceholderPage
from archdeck.pages.process_page import ProcessPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ArchDeck")
        self.resize(1120, 760)
        self.setMinimumSize(900, 620)

        root = QWidget()
        root.setObjectName("root")
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(15, 20, 15, 16)
        side.setSpacing(8)
        brand_row = QHBoxLayout()
        mark = QLabel("A")
        mark.setObjectName("brandMark")
        mark.setFixedSize(34, 34)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand = QLabel("ArchDeck")
        brand.setObjectName("brand")
        brand_row.addWidget(mark)
        brand_row.addSpacing(9)
        brand_row.addWidget(brand)
        brand_row.addStretch()
        side.addLayout(brand_row)
        side.addSpacing(28)
        caption = QLabel("РАБОЧЕЕ ПРОСТРАНСТВО")
        caption.setObjectName("navCaption")
        side.addWidget(caption)
        side.addSpacing(5)

        self.stack = QStackedWidget()
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        routes = [
            ("⌂", "Обзор"), ("↻", "Обновления"), ("▦", "Пакеты"),
            ("◉", "Службы"), ("⌫", "Очистка"), ("⚙", "Система"),
        ]
        self.pages: dict[str, QWidget] = {}
        self.buttons: dict[str, QPushButton] = {}
        for index, (icon, name) in enumerate(routes):
            button = QPushButton(f"{icon}    {name}")
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.clicked.connect(lambda _checked=False, i=index: self.stack.setCurrentIndex(i))
            self.nav_group.addButton(button, index)
            side.addWidget(button)
            self.buttons[name] = button
        side.addStretch()
        footer = QLabel("ARCH LINUX  ·  0.1.0")
        footer.setObjectName("footer")
        side.addWidget(footer)

        self.pages["Обзор"] = OverviewPage(
            lambda: self._navigate("Обновления"),
            lambda: self._navigate("Службы"),
        )
        self.pages["Обновления"] = ProcessPage(
            "Обновления", "Посмотреть доступные обновления из официальных репозиториев. Проверка не устанавливает пакеты.",
            "Проверить сейчас", "checkupdates", [], "Система обновлена." 
        )
        self.pages["Пакеты"] = PackagesPage()
        self.pages["Службы"] = ProcessPage(
            "Службы пользователя", "Список активных пользовательских служб systemd. Команда только читает состояние.",
            "Обновить список", "systemctl", ["--user", "list-units", "--type=service", "--state=running", "--no-legend", "--plain"],
            "Активных пользовательских служб не найдено."
        )
        self.pages["Очистка"] = PlaceholderPage("Очистка", "Просмотр кэша pacman и осиротевших пакетов. Перед удалением ArchDeck будет показывать точный список и запрашивать подтверждение.")
        self.pages["Система"] = PlaceholderPage("Система", "Подробности о ядре, графике, накопителях и сети добавим следующим этапом.")
        for _, name in routes:
            self.stack.addWidget(self.pages[name])
        self.nav_group.button(0).setChecked(True)
        root_layout.addWidget(sidebar)
        root_layout.addWidget(self.stack, 1)

    def _navigate(self, name: str) -> None:
        index = list(self.pages).index(name)
        self.stack.setCurrentIndex(index)
        self.buttons[name].setChecked(True)
