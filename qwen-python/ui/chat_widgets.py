import os
import re
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QApplication, QSizePolicy, QWidget, QScrollArea
)
from PySide6.QtGui import QFont, QPixmap, QFontMetrics, QCursor, QPainter, QPainterPath, QColor, QBrush
from PySide6.QtCore import Qt, QTimer, QSize

HAS_PYGMENTS = False
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import HtmlFormatter
    HAS_PYGMENTS = True
except Exception: pass

class SendButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")
    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        color = QColor("white") if self.isEnabled() else QColor("#444746")
        painter.setBrush(QBrush(color)); painter.setPen(Qt.NoPen)
        path = QPainterPath()
        path.moveTo(10, 10); path.lineTo(32, 20); path.lineTo(10, 30); path.lineTo(14, 20); path.closeSubpath()
        painter.drawPath(path)

class CodeWidget(QFrame):
    def __init__(self, code, lang="", fsize=13):
        super().__init__()
        self.raw = code; self.setObjectName("code_frame"); self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        l = QVBoxLayout(self); l.setContentsMargins(0,0,0,0); l.setSpacing(0)
        h = QFrame(); h.setStyleSheet("background-color: #2b2d30; border-top-left-radius: 12px; border-top-right-radius: 12px; border: none;")
        hl = QHBoxLayout(h); hl.setContentsMargins(15, 8, 15, 8)
        lang_lbl = QLabel(lang.upper() if lang else "CODE", styleSheet="color: #c4c7c5; font-weight: bold; font-size: 11px; border: none;")
        hl.addWidget(lang_lbl); hl.addStretch()
        cb = QPushButton("Copy"); cb.setCursor(Qt.PointingHandCursor); cb.setStyleSheet("color: #c4c7c5; border: none; font-size: 11px; font-weight: bold;")
        cb.clicked.connect(lambda: [QApplication.clipboard().setText(self.raw), cb.setText("Copied!"), QTimer.singleShot(2000, lambda: cb.setText("Copy"))])
        hl.addWidget(cb); l.addWidget(h)
        html = f"<pre>{code}</pre>"
        if HAS_PYGMENTS:
            try: html = highlight(code, get_lexer_by_name(lang) if lang else guess_lexer(code), HtmlFormatter(style='monokai', noclasses=True, nobackground=True))
            except: pass
        lbl = QLabel(html); lbl.setTextFormat(Qt.RichText); lbl.setWordWrap(False); lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        lbl.setStyleSheet(f"background-color: #1e1f20; color: #e3e3e3; padding: 15px; font-family: 'Consolas', monospace; font-size: {fsize}px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        scr = QScrollArea(); scr.setWidget(lbl); scr.setWidgetResizable(True); scr.setFixedHeight(min(600, lbl.sizeHint().height() + 30)); scr.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        l.addWidget(scr)

class MsgBubble(QWidget):
    def __init__(self, text, is_user, img=None, time_str="", fsize=14, scroll_callback=None):
        super().__init__()
        self.fsize = fsize; self.scroll_callback = scroll_callback; self.full_text = text; self.is_user = is_user
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(5)

        align_layout = QHBoxLayout(); align_layout.setContentsMargins(0, 0, 0, 0)
        
        self.bubble_frame = QFrame()
        self.bubble_frame.setObjectName("bubble_user" if is_user else "bubble_bot")
        self.bubble_layout = QVBoxLayout(self.bubble_frame)
        self.bubble_layout.setContentsMargins(18, 12, 18, 12); self.bubble_layout.setSpacing(10)

        if img and os.path.exists(img):
            l = QLabel(); p = QPixmap(img)
            if not p.isNull(): p = p.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation); l.setPixmap(p); l.setStyleSheet("border-radius: 12px; margin-bottom: 10px;"); self.bubble_layout.addWidget(l)

        self.text_container = QVBoxLayout(); self.text_container.setSpacing(10); self.bubble_layout.addLayout(self.text_container)
        self.parse_and_add_content(text)

        if is_user: align_layout.addStretch(); align_layout.addWidget(self.bubble_frame)
        else: align_layout.addWidget(self.bubble_frame); align_layout.addStretch()
        self.main_layout.addLayout(align_layout)

        # ПАНЕЛЬ ДЕЙСТВИЙ (Копировать есть только у бота)
        if text and not is_user:
            actions_layout = QHBoxLayout(); actions_layout.setContentsMargins(5, 0, 5, 0); actions_layout.setSpacing(5)
            self.copy_btn = QPushButton("❐"); self.copy_btn.setObjectName("action_btn"); self.copy_btn.setCursor(Qt.PointingHandCursor); self.copy_btn.setToolTip("Копировать")
            self.copy_btn.clicked.connect(self.copy_action)
            actions_layout.addWidget(self.copy_btn)
            actions_layout.addStretch()
            self.main_layout.addLayout(actions_layout)

    def copy_action(self):
        QApplication.clipboard().setText(self.full_text)
        # БЕЛАЯ ГАЛОЧКА
        self.copy_btn.setText("✔"); self.copy_btn.setStyleSheet("color: white; border: none; background: transparent; font-weight: bold;")
        QTimer.singleShot(2000, lambda: [self.copy_btn.setText("❐"), self.copy_btn.setStyleSheet("color: #c4c7c5; border: none; background: transparent;")])

    def parse_and_add_content(self, text):
        parts = re.split(r"(```[\s\S]*?```)", text)
        for part in parts:
            if not part.strip(): continue
            if part.startswith("```"):
                content = part.strip("`").strip(); lang = ""
                if "\n" in content: first = content.split("\n")[0].strip(); lang = first if len(first)<15 and " " not in first else ""; content = content[len(first):].strip() if lang else content
                self.text_container.addWidget(CodeWidget(content, lang, self.fsize))
            else: self.add_text_widget(part)

    def add_text_widget(self, t):
        l = QLabel(t); font = QFont("Segoe UI", self.fsize); l.setFont(font); l.setObjectName("chat_text"); l.setTextInteractionFlags(Qt.TextSelectableByMouse); l.setOpenExternalLinks(True)
        fm = QFontMetrics(font)
        if fm.horizontalAdvance(t) > 750: l.setFixedWidth(750); l.setWordWrap(True)
        else: l.setWordWrap(False)
        self.text_container.addWidget(l)

    def set_text(self, t: str):
        self.full_text = t
        while self.text_container.count(): item = self.text_container.takeAt(0); item.widget().deleteLater() if item.widget() else None
        self.parse_and_add_content(t); self.scroll_callback() if self.scroll_callback else None

class InputEdit(QTextEdit):
    def __init__(self, p): super().__init__(); self.p = p
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return and not e.modifiers(): 
            if self.p.bs.isEnabled(): self.p.send()
        else: super().keyPressEvent(e)