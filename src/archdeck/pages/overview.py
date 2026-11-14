from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QVBoxLayout, QWidget,
)

from archdeck.system_info import SystemInfo


class MetricCard(QFrame):
    def __init__(self, title: str, value: str, detail: str, progress: int | None = None) -> None:
        super().__init__()
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(17, 15, 17, 15)
        layout.setSpacing(7)
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("metric")
        self.detail_label = QLabel(detail)
        self.detail_label.setObjectName("small")
        layout.addWidget(title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(progress or 0)
        self.progress.setVisible(progress is not None)
        layout.addWidget(self.progress)

    def update_metric(self, value: str, detail: str, progress: int | None = None) -> None:
        self.value_label.setText(value)
        self.detail_label.setText(detail)
        if progress is not None:
            self.progress.setValue(progress)


class OverviewPage(QWidget):
    def __init__(self, open_updates, open_services) -> None:
        super().__init__()
        self.info = SystemInfo()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(18)

        heading = QHBoxLayout()
        intro = QVBoxLayout()
        eyebrow = QLabel("ARCH LINUX · CONTROL CENTER")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Обзор системы")
        title.setObjectName("pageTitle")
        intro.addWidget(eyebrow)
        intro.addWidget(title)
        heading.addLayout(intro)
        heading.addStretch()
        status = QLabel("●  Система на связи")
        status.setObjectName("statusPill")
        heading.addWidget(status, alignment=Qt.AlignmentFlag.AlignTop)
        outer.addLayout(heading)

        hero = QFrame()
        hero.setObjectName("hero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(22, 20, 22, 20)
        hero_copy = QVBoxLayout()
        hero_title = QLabel("Всё важное — в одном месте")
        hero_title.setObjectName("heroTitle")
        hero_text = QLabel("Проверь обновления и состояние служб. ArchDeck пока работает в режиме просмотра.")
        hero_text.setObjectName("heroText")
        hero_text.setWordWrap(True)
        hero_copy.addWidget(hero_title)
        hero_copy.addWidget(hero_text)
        hero_layout.addLayout(hero_copy, 1)
        updates = QPushButton("Проверить обновления")
        updates.setObjectName("primary")
        updates.clicked.connect(open_updates)
        hero_layout.addWidget(updates, alignment=Qt.AlignmentFlag.AlignVCenter)
        outer.addWidget(hero)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        self.cpu = MetricCard("ПРОЦЕССОР", "—", "Снимок текущей нагрузки", 0)
        self.memory_card = MetricCard("ПАМЯТЬ", "—", "Использовано", 0)
        self.disk_card = MetricCard("СИСТЕМНЫЙ ДИСК", "—", "Корневой раздел", 0)
        grid.addWidget(self.cpu, 0, 0)
        grid.addWidget(self.memory_card, 0, 1)
        grid.addWidget(self.disk_card, 0, 2)
        outer.addLayout(grid)

        lower = QHBoxLayout()
        lower.setSpacing(12)
        lower.addWidget(self._info_panel(
            "Обновления", "Проверка запускается вручную и ничего не устанавливает.",
            "Открыть обновления", open_updates,
        ))
        lower.addWidget(self._info_panel(
            "Службы пользователя", "Просмотр активных user-сервисов systemd.",
            "Посмотреть службы", open_services,
        ))
        outer.addLayout(lower)
        outer.addStretch()
        footer = QLabel("ArchDeck 0.1.0  ·  Команды запускаются только по нажатию")
        footer.setObjectName("footer")
        outer.addWidget(footer)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_metrics)
        self.timer.start(2500)
        self.refresh_metrics()

    @staticmethod
    def _info_panel(title: str, description: str, action: str, callback) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)
        label = QLabel(title)
        label.setObjectName("cardTitle")
        text = QLabel(description)
        text.setObjectName("small")
        text.setWordWrap(True)
        button = QPushButton(action)
        button.setObjectName("secondary")
        button.clicked.connect(callback)
        layout.addWidget(label)
        layout.addWidget(text, 1)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignLeft)
        return panel

    def refresh_metrics(self) -> None:
        cpu = self.info.cpu_percent()
        self.cpu.update_metric(f"{cpu}%" if cpu is not None else "—", "Текущая загрузка", cpu or 0)
        memory = self.info.memory()
        if memory:
            used, total, percent = memory
            self.memory_card.update_metric(f"{percent}%", f"{used:,} / {total:,} MiB".replace(',', ' '), percent)
        disk = self.info.disk()
        if disk:
            used, total, percent = disk
            self.disk_card.update_metric(f"{percent}%", f"{used:.1f} / {total:.1f} GiB занято", percent)
