from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit, QTextEdit, QSpinBox, QSlider,
    QStackedWidget, QComboBox, QScrollArea, QFileDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QBrush, QCursor

# --- КРАСИВЫЙ ПЕРЕКЛЮЧАТЕЛЬ (SWITCH) ---
class Switch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        if self.isChecked():
            bg_color = QColor("#a8c7fa") # Акцент (Qwen2.5-VL-7B Blue)
            circle_color = QColor("#0b0b0b")
            circle_x = 24
        else:
            bg_color = QColor("#3a3a3a")
            circle_color = QColor("#b0b0b0")
            circle_x = 4

        p.setBrush(QBrush(bg_color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, 50, 28, 14, 14)
        
        p.setBrush(QBrush(circle_color))
        p.drawEllipse(circle_x, 4, 20, 20)

# --- ГЛАВНЫЙ КЛАСС НАСТРОЕК ---
class SettingsPage(QWidget):
    config_changed = Signal(dict)
    back_clicked = Signal()
    clear_history_clicked = Signal()
    export_history_clicked = Signal()

    def __init__(self, config):
        super().__init__()
        self.conf = config
        self.init_ui()

    def update_data(self, new_conf):
        """Загружаем данные из конфига в поля"""
        self.conf = new_conf
        
        # Общие
        self.inp_uname.setText(self.conf.get("user_name", "Вы"))
        self.inp_aname.setText(self.conf.get("ai_name", "Qwen2.5-VL-7B"))
        
        # ИИ
        self.mem.setText(self.conf.get("memory", ""))
        self.slider_temp.setValue(int(self.conf.get("temperature", 0.4) * 10))
        self.lbl_temp_val.setText(str(self.conf.get("temperature", 0.4)))
        
        self.slider_mem.setValue(self.conf.get("memory_length", 6))
        self.lbl_mem_val.setText(f"{self.conf.get('memory_length', 6)} сообщ.")
        
        self.slider_len.setValue(self.conf.get("max_tokens", 1024))
        self.lbl_len_val.setText(f"{self.conf.get('max_tokens', 1024)}")

        # Вид
        self.sb_font.setValue(self.conf.get("font_size", 14))
        self.combo_theme.setCurrentText(self.conf.get("theme_name", "Qwen2.5-VL-7B Blue"))

        # Голос
        self.slider_rate.setValue(self.conf.get("voice_rate", 145))
        self.lbl_rate_val.setText(f"{self.conf.get('voice_rate', 145)}")

        # Система
        self.switch_web.setChecked(self.conf.get("web_enabled", True))
        self.switch_fast.setChecked(not self.conf.get("thinking", False))

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- 1. ЛЕВОЕ МЕНЮ ---
        sidebar = QFrame()
        sidebar.setObjectName("settings_sidebar")
        sidebar.setFixedWidth(240)
        
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(15, 30, 15, 30)
        sb_layout.setSpacing(8)

        # Заголовок
        lbl_head = QLabel("Настройки")
        lbl_head.setObjectName("settings_header")
        sb_layout.addWidget(lbl_head)
        sb_layout.addSpacing(20)

        # Кнопки категорий
        self.btn_gen = self.create_menu_btn("👤  Общие", True)
        self.btn_ai = self.create_menu_btn("🧠  Мозг ИИ")
        self.btn_ui = self.create_menu_btn("🎨  Внешний вид")
        self.btn_voice = self.create_menu_btn("🔊  Голос")
        self.btn_data = self.create_menu_btn("💾  Данные")
        
        sb_layout.addWidget(self.btn_gen)
        sb_layout.addWidget(self.btn_ai)
        sb_layout.addWidget(self.btn_ui)
        sb_layout.addWidget(self.btn_voice)
        sb_layout.addWidget(self.btn_data)
        sb_layout.addStretch()

        # Кнопка Назад
        btn_back = QPushButton("← Назад в чат")
        btn_back.setObjectName("settings_back_btn")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.back_clicked.emit)
        sb_layout.addWidget(btn_back)

        layout.addWidget(sidebar)

        # --- 2. ПРАВЫЙ КОНТЕНТ ---
        content_frame = QFrame()
        content_frame.setObjectName("settings_content")
        cf_layout = QVBoxLayout(content_frame)
        cf_layout.setContentsMargins(0, 0, 0, 0)

        # Скролл для контента, если настроек много
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        
        # Добавляем страницы
        self.stack.addWidget(self.page_general())
        self.stack.addWidget(self.page_ai())
        self.stack.addWidget(self.page_ui())
        self.stack.addWidget(self.page_voice())
        self.stack.addWidget(self.page_data())
        
        scroll.setWidget(self.stack)
        cf_layout.addWidget(scroll)
        
        # Панель с кнопкой сохранения (всегда внизу)
        save_panel = QFrame()
        save_panel.setStyleSheet("background-color: #1a1a1a; border-top: 1px solid #333;")
        sp_layout = QHBoxLayout(save_panel)
        sp_layout.setContentsMargins(40, 15, 40, 15)
        
        lbl_info = QLabel("Изменения применяются сразу после сохранения.")
        lbl_info.setStyleSheet("color: #666; font-size: 12px;")
        
        btn_save = QPushButton("Сохранить настройки")
        btn_save.setObjectName("save_btn_blue")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.save)
        
        sp_layout.addWidget(lbl_info)
        sp_layout.addStretch()
        sp_layout.addWidget(btn_save)
        
        cf_layout.addWidget(save_panel)
        layout.addWidget(content_frame)

        # Логика переключения
        self.btn_gen.clicked.connect(lambda: self.set_tab(0, self.btn_gen))
        self.btn_ai.clicked.connect(lambda: self.set_tab(1, self.btn_ai))
        self.btn_ui.clicked.connect(lambda: self.set_tab(2, self.btn_ui))
        self.btn_voice.clicked.connect(lambda: self.set_tab(3, self.btn_voice))
        self.btn_data.clicked.connect(lambda: self.set_tab(4, self.btn_data))

    def create_menu_btn(self, text, active=False):
        b = QPushButton(text)
        b.setCheckable(True)
        b.setChecked(active)
        b.setCursor(Qt.PointingHandCursor)
        b.setObjectName("settings_menu_btn")
        return b

    def set_tab(self, index, btn):
        self.stack.setCurrentIndex(index)
        for b in [self.btn_gen, self.btn_ai, self.btn_ui, self.btn_voice, self.btn_data]:
            b.setChecked(False)
        btn.setChecked(True)

    # --- СТРАНИЦА 1: ОБЩИЕ ---
    def page_general(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignTop); l.setContentsMargins(40, 40, 40, 40); l.setSpacing(25)
        
        l.addWidget(QLabel("Персонализация", objectName="settings_section_title"))
        
        self.inp_uname = QLineEdit()
        l.addLayout(self.field("Ваше имя", "Как ИИ должен к вам обращаться в диалоге.", self.inp_uname))
        
        self.inp_aname = QLineEdit()
        l.addLayout(self.field("Имя ассистента", "Имя, которое отображается в чате над сообщениями.", self.inp_aname))
        
        l.addStretch()
        return w

    # --- СТРАНИЦА 2: МОЗГ ИИ ---
    def page_ai(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignTop); l.setContentsMargins(40, 40, 40, 40); l.setSpacing(25)
        
        l.addWidget(QLabel("Параметры Интеллекта", objectName="settings_section_title"))
        
        # Системный промпт
        self.mem = QTextEdit(); self.mem.setFixedHeight(80)
        l.addLayout(self.field("Системный промпт (Личность)", "Инструкция, задающая стиль и поведение бота.", self.mem))
        
        l.addSpacing(10)
        
        # Температура
        self.slider_temp = QSlider(Qt.Horizontal); self.slider_temp.setRange(1, 10)
        self.lbl_temp_val = QLabel("0.4")
        self.slider_temp.valueChanged.connect(lambda v: self.lbl_temp_val.setText(str(v/10)))
        l.addLayout(self.field("Температура (Креативность)", "Низкая (0.1) - строгие факты, Высокая (0.9) - фантазия.", self.slider_temp, self.lbl_temp_val))

        # Контекст
        self.slider_mem = QSlider(Qt.Horizontal); self.slider_mem.setRange(2, 50)
        self.lbl_mem_val = QLabel("6")
        self.slider_mem.valueChanged.connect(lambda v: self.lbl_mem_val.setText(f"{v} сообщ."))
        l.addLayout(self.field("Глубина памяти", "Сколько последних сообщений помнит бот.", self.slider_mem, self.lbl_mem_val))
        
        # Макс токенов
        self.slider_len = QSlider(Qt.Horizontal); self.slider_len.setRange(100, 4096)
        self.lbl_len_val = QLabel("1024")
        self.slider_len.valueChanged.connect(lambda v: self.lbl_len_val.setText(f"{v}"))
        l.addLayout(self.field("Длина ответа", "Максимальное количество слов в одном ответе.", self.slider_len, self.lbl_len_val))
        
        # Думающая модель
        h = QHBoxLayout()
        h.addWidget(QLabel("Режим 'Думающая' (Pro)", objectName="settings_label_bold"))
        self.switch_fast = Switch() # Инверсия: если выкл - то Think
        h.addStretch(); h.addWidget(self.switch_fast)
        l.addLayout(h)
        l.addWidget(QLabel("Выключите для использования медленной, но умной модели.", objectName="settings_desc"))

        l.addStretch()
        return w

    # --- СТРАНИЦА 3: ВНЕШНИЙ ВИД ---
    def page_ui(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignTop); l.setContentsMargins(40, 40, 40, 40); l.setSpacing(25)
        
        l.addWidget(QLabel("Интерфейс", objectName="settings_section_title"))
        
        self.sb_font = QSpinBox(); self.sb_font.setRange(10, 30)
        l.addLayout(self.field("Размер шрифта", "Размер текста в сообщениях чата.", self.sb_font))
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Qwen2.5-VL-7B Blue", "Emerald Green", "Crimson Red", "Graphite"])
        l.addLayout(self.field("Цветовая тема", "Акцентный цвет интерфейса.", self.combo_theme))
        
        l.addStretch()
        return w

    # --- СТРАНИЦА 4: ГОЛОС ---
    def page_voice(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignTop); l.setContentsMargins(40, 40, 40, 40); l.setSpacing(25)
        
        l.addWidget(QLabel("Настройки речи (TTS)", objectName="settings_section_title"))
        
        self.slider_rate = QSlider(Qt.Horizontal); self.slider_rate.setRange(50, 300)
        self.lbl_rate_val = QLabel("145")
        self.slider_rate.valueChanged.connect(lambda v: self.lbl_rate_val.setText(str(v)))
        l.addLayout(self.field("Скорость речи", "Как быстро бот читает текст.", self.slider_rate, self.lbl_rate_val))
        
        l.addStretch()
        return w

    # --- СТРАНИЦА 5: ДАННЫЕ ---
    def page_data(self):
        w = QWidget()
        l = QVBoxLayout(w); l.setAlignment(Qt.AlignTop); l.setContentsMargins(40, 40, 40, 40); l.setSpacing(25)
        
        l.addWidget(QLabel("Управление данными", objectName="settings_section_title"))
        
        # Web Search Toggle
        h = QHBoxLayout()
        h.addWidget(QLabel("Поиск в Интернете", objectName="settings_label_bold"))
        self.switch_web = Switch()
        h.addStretch(); h.addWidget(self.switch_web)
        l.addLayout(h)
        l.addWidget(QLabel("Разрешить ИИ искать информацию в Google/DuckDuckGo.", objectName="settings_desc"))
        
        l.addSpacing(20)
        
        # Кнопки опасных действий
        btn_clear = QPushButton("🗑  Очистить всю историю")
        btn_clear.setObjectName("danger_btn"); btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_history_clicked.emit)
        l.addWidget(btn_clear)
        
        btn_export = QPushButton("📥  Экспорт чатов в JSON")
        btn_export.setObjectName("sidebar_item"); btn_export.setCursor(Qt.PointingHandCursor)
        # Логика экспорта может быть добавлена позже
        l.addWidget(btn_export)

        l.addStretch()
        return w

    # --- ХЕЛПЕР ---
    def field(self, t, d, w, val_lbl=None):
        lay = QVBoxLayout(); lay.setSpacing(5)
        
        h = QHBoxLayout()
        h.addWidget(QLabel(t, objectName="settings_label_bold"))
        if val_lbl: h.addStretch(); h.addWidget(val_lbl)
        lay.addLayout(h)
        
        lay.addWidget(QLabel(d, objectName="settings_desc"))
        if w: lay.addWidget(w)
        return lay

    def save(self):
        # Собираем конфиг
        c = self.conf.copy()
        c["user_name"] = self.inp_uname.text()
        c["ai_name"] = self.inp_aname.text()
        c["memory"] = self.mem.toPlainText()
        c["font_size"] = self.sb_font.value()
        c["theme_name"] = self.combo_theme.currentText()
        
        # Слайдеры
        c["temperature"] = self.slider_temp.value() / 10
        c["memory_length"] = self.slider_mem.value()
        c["max_tokens"] = self.slider_len.value()
        c["voice_rate"] = self.slider_rate.value()
        
        # Свитчи
        c["thinking"] = not self.switch_fast.isChecked()
        c["web_enabled"] = self.switch_web.isChecked()
        
        self.config_changed.emit(c)