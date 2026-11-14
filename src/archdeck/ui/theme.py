APP_STYLE = """
* { font-family: 'Inter', 'Noto Sans', sans-serif; }
QMainWindow, QWidget#root { background: #101318; color: #e8eaf0; }
QWidget#sidebar { background: #151920; border-right: 1px solid #252b35; }
QLabel#brand { font-size: 19px; font-weight: 750; color: #f4f6fb; }
QLabel#brandMark { background: #7c9cff; color: #101318; border-radius: 11px; font-size: 16px; font-weight: 900; }
QLabel#navCaption { color: #737e90; font-size: 10px; font-weight: 800; letter-spacing: 1.4px; }
QPushButton#navButton { background: transparent; color: #9da6b5; border: 0; border-radius: 9px; padding: 11px 12px; text-align: left; font-size: 13px; }
QPushButton#navButton:hover { background: #202630; color: #f2f4f8; }
QPushButton#navButton:checked { background: #252d3b; color: #a9bdff; font-weight: 700; }
QLabel#muted { color: #8791a0; }
QLabel#eyebrow { color: #8d9bb4; font-size: 11px; font-weight: 750; letter-spacing: 1.5px; }
QLabel#pageTitle { color: #f4f6fb; font-size: 26px; font-weight: 750; }
QLabel#cardTitle { color: #aab3c2; font-size: 12px; font-weight: 650; }
QLabel#metric { color: #f4f6fb; font-size: 29px; font-weight: 750; }
QLabel#systemValue { color: #f4f6fb; font-size: 16px; font-weight: 650; }
QLabel#small { color: #8791a0; font-size: 11px; }
QFrame#card, QFrame#panel { background: #171c24; border: 1px solid #272e39; border-radius: 14px; }
QFrame#hero { background: #1c2432; border: 1px solid #2b3952; border-radius: 16px; }
QLabel#heroTitle { color: #f4f6fb; font-size: 21px; font-weight: 720; }
QLabel#heroText { color: #a7b1c1; font-size: 12px; }
QPushButton#primary { background: #9db4ff; color: #111722; border: 0; border-radius: 9px; padding: 10px 15px; font-weight: 750; }
QPushButton#primary:hover { background: #b4c5ff; }
QPushButton#secondary { background: #252c38; color: #e6eaf2; border: 1px solid #323b49; border-radius: 9px; padding: 9px 13px; font-weight: 650; }
QPushButton#secondary:hover { background: #303949; }
QProgressBar { background: #262d38; border: 0; border-radius: 4px; height: 7px; text-align: center; }
QProgressBar::chunk { background: #8ca9ff; border-radius: 4px; }
QListWidget { background: transparent; border: 0; outline: 0; }
QListWidget::item { color: #dfe4ed; padding: 9px 10px; border-bottom: 1px solid #252b35; }
QTableWidget { background: transparent; alternate-background-color: #1b212b; color: #dfe4ed; border: 0; gridline-color: #2a313d; selection-background-color: #2b3a55; }
QTableWidget::item { padding: 6px; }
QHeaderView::section { background: #202630; color: #aab3c2; border: 0; border-bottom: 1px solid #323b49; padding: 8px; font-weight: 650; }
QLabel#statusPill { background: #202b27; color: #9cdbb5; border-radius: 10px; padding: 6px 10px; font-size: 11px; font-weight: 700; }
QLabel#footer { color: #6f7988; font-size: 10px; }
"""
