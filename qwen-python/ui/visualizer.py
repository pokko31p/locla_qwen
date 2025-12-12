import math
# ✅ ДОБАВИЛ QSizePolicy
from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QPainter, QBrush, QPen, QRadialGradient, QColor
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF

class VoiceVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "IDLE"
        self.base_radius = 80
        self.current_radius = 80
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_anim)
        self.timer.start(20)
        self.accent_color = QColor("#007ACC")
        self.t_val = 0.0
        
        # ✅ ТЕПЕРЬ РАБОТАЕТ (Импорт есть)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_color(self, c):
        self.accent_color = QColor(c)

    def set_state(self, s):
        self.state = s
        self.current_radius = self.base_radius

    def update_anim(self):
        self.t_val += 0.1
        if self.state == "LISTENING":
            self.current_radius = self.base_radius + (15 * math.sin(self.t_val * 0.5))
        elif self.state == "THINKING":
            self.angle = (self.angle + 8) % 360
            self.current_radius = self.base_radius
        elif self.state == "SPEAKING":
            pulse = math.sin(self.t_val * 2) * 10 + math.cos(self.t_val * 5) * 5
            self.current_radius = self.base_radius + max(0, pulse + 5)
        else:
            self.current_radius = self.base_radius
            self.angle = 0
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        center = QPoint(self.width() // 2, self.height() // 2)
        grad = QRadialGradient(center, self.current_radius * 1.5)
        c = QColor(self.accent_color)
        c.setAlpha(100)
        grad.setColorAt(0, c)
        grad.setColorAt(1, Qt.transparent)
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(center, self.current_radius * 1.5, self.current_radius * 1.5)
        p.setBrush(QBrush(self.accent_color))
        if self.state == "THINKING":
            rect = QRectF(center.x() - self.base_radius, center.y() - self.base_radius, self.base_radius * 2, self.base_radius * 2)
            p.setPen(QPen(self.accent_color, 8, Qt.SolidLine, Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            p.drawArc(rect, self.angle * 16, 270 * 16)
        else:
            p.setPen(Qt.NoPen)
            p.drawEllipse(center, self.current_radius, self.current_radius)