from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        eyebrow = QLabel("ARCHDECK · В РАЗРАБОТКЕ")
        eyebrow.setObjectName("eyebrow")
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        card = QFrame()
        card.setObjectName("panel")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        text = QLabel(description)
        text.setObjectName("muted")
        text.setWordWrap(True)
        card_layout.addWidget(text)
        layout.addWidget(eyebrow)
        layout.addWidget(heading)
        layout.addWidget(card)
        layout.addStretch()
