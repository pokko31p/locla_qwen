import sys
import os
import json
import datetime
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QScrollArea, QLabel, QFrame, QFileDialog, QMessageBox, 
    QListWidget, QComboBox, QStackedWidget, QLineEdit, QSizeGrip, 
    QMenu, QSpinBox, QFormLayout, QGroupBox, QSizePolicy
)
from PySide6.QtGui import QFont, QAction, QCursor
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QPropertyAnimation, QEasingCurve, QRect

from ui.styles import get_styles, THEMES
from ui.chat_widgets import MsgBubble, InputEdit, SendButton
from ui.visualizer import VoiceVisualizer
from ui.setting_page import SettingsPage
from core.loader import LoaderThread
from core.ai_worker import GenThread
from core.voice_worker import VoiceListenerThread, TTSWorker, VOICE_AVAILABLE
from core.web_worker import fetch_web_context, WEB_AVAILABLE

SETTINGS_FILE = "settings.json"
HISTORY_FILE = "history.json"

class IPWorker(QThread):
    finished = Signal(str)
    def run(self):
        try:
            r = requests.get("http://ip-api.com/json/", timeout=5)
            data = r.json()
            if data.get('status') == 'success':
                self.finished.emit(f"• {data.get('city')}, {data.get('country')}")
            else:
                self.finished.emit("• Локация недоступна")
        except:
            self.finished.emit("• Локация недоступна")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1300, 850)
        
        self.chats = []; self.curr = -1; self.img = None
        self.listener = None; self.current_bot_bubble = None; self.is_voice_reply = False
        self.is_web_enabled = True; self.oldPos = None
        self.sidebar_open = True # Флаг состояния сайдбара
        
        self.st_lbl = QLabel("")
        
        self.load_settings()
        self.setup_ui()
        self.load_history()
        
        self.loader = LoaderThread(); self.loader.finished.connect(self.on_ready); self.loader.start()
        self.ipw = IPWorker(); self.ipw.finished.connect(self.update_loc); self.ipw.start()
        self.sizegrip = QSizeGrip(self); self.sizegrip.setVisible(True)

    def update_loc(self, text):
        self.loc_data_lbl.setTextFormat(Qt.RichText)
        self.loc_data_lbl.setText(f"{text}<br>&nbsp;&nbsp;По IP-адресу &nbsp; <a href='#' style='color:#a8c7fa;text-decoration:none;'>Обновить</a>")

    # 🔥 ИСПРАВЛЕННАЯ ЛОГИКА САЙДБАРА (РАБОТАЕТ!) 🔥
    def toggle_sidebar(self):
        self.sidebar_open = not self.sidebar_open
        
        start_w = self.sb.width()
        end_w = 280 if self.sidebar_open else 0
        
        if self.sidebar_open:
            self.sb.setVisible(True) # Сначала показываем
            self.mb_top.setVisible(False)
        else:
            self.mb_top.setVisible(True)

        self.anim = QPropertyAnimation(self.sb, b"maximumWidth")
        self.anim.setDuration(300)
        self.anim.setStartValue(start_w)
        self.anim.setEndValue(end_w)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        if not self.sidebar_open:
            self.anim.finished.connect(lambda: self.sb.setVisible(False))
        else:
            try: self.anim.finished.disconnect() 
            except: pass
            
        self.anim.start()

    def setup_ui(self):
        self.central = QFrame(); self.central.setObjectName("central_widget"); self.setCentralWidget(self.central)
        ml = QHBoxLayout(self.central); ml.setContentsMargins(0,0,0,0); ml.setSpacing(0)
        
        # --- SIDEBAR ---
        self.sb = QWidget(); self.sb.setObjectName("sidebar"); self.sb.setFixedWidth(280)
        sv = QVBoxLayout(self.sb); sv.setContentsMargins(0,15,0,15); sv.setSpacing(5)
        
        h = QHBoxLayout(); h.setContentsMargins(15,0,0,0)
        mb = QPushButton("≡"); mb.setObjectName("menu_btn"); mb.setCursor(Qt.PointingHandCursor); mb.clicked.connect(self.toggle_sidebar)
        h.addWidget(mb); h.addStretch(); sv.addLayout(h)

        row_new = QHBoxLayout(); row_new.setContentsMargins(10,0,10,0); row_new.setSpacing(5)
        bn = QPushButton("+ Новый чат"); bn.setObjectName("new_chat"); bn.setCursor(Qt.PointingHandCursor); bn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); bn.clicked.connect(self.new_chat)
        row_new.addWidget(bn)
        b_inc = QPushButton("💬"); b_inc.setObjectName("incognito_btn"); b_inc.setCursor(Qt.PointingHandCursor); b_inc.setFixedSize(40,40); b_inc.setToolTip("Анонимный режим"); row_new.addWidget(b_inc)
        sv.addLayout(row_new)
        
        lbl_recent = QLabel("Недавние"); lbl_recent.setStyleSheet("color:#c4c7c5; font-size:12px; font-weight:bold; margin-left:20px; margin-top:10px;"); sv.addWidget(lbl_recent)
        
        self.lst = QListWidget(); self.lst.setCursor(Qt.PointingHandCursor); self.lst.setContextMenuPolicy(Qt.CustomContextMenu); self.lst.customContextMenuRequested.connect(self.ctx_menu); self.lst.itemClicked.connect(self.switch); sv.addWidget(self.lst)
        
        bs = QPushButton("⚙  Настройки и справка"); bs.setObjectName("sidebar_item"); bs.setCursor(Qt.PointingHandCursor); bs.clicked.connect(self.to_settings); sv.addWidget(bs)
        
        self.loc_data_lbl = QLabel("• Определение...\n  По IP-адресу"); self.loc_data_lbl.setObjectName("location_lbl"); sv.addWidget(self.loc_data_lbl); sv.addSpacing(15)

        ml.addWidget(self.sb); self.stack = QStackedWidget(); ml.addWidget(self.stack)
        
        # --- CHAT PAGE ---
        p_chat = QWidget(); cv = QVBoxLayout(p_chat); cv.setContentsMargins(0,0,0,0); cv.setSpacing(0)
        
        # Top Bar
        top = QWidget(); top.setObjectName("top_bar"); top.setFixedHeight(50); th = QHBoxLayout(top); th.setContentsMargins(20,0,15,0); th.setSpacing(15)
        self.mb_top = QPushButton("≡"); self.mb_top.setObjectName("menu_btn"); self.mb_top.setCursor(Qt.PointingHandCursor); self.mb_top.clicked.connect(self.toggle_sidebar); self.mb_top.setVisible(False); th.addWidget(self.mb_top)
        self.ai_label = QLabel("Qwen2.5-VL-7B"); self.ai_label.setObjectName("ai_title"); th.addWidget(self.ai_label); th.addStretch()
        self.chat_title_lbl = QLabel(""); self.chat_title_lbl.setObjectName("chat_title"); th.addWidget(self.chat_title_lbl); th.addStretch()
        bmn = QPushButton("—"); bmn.setObjectName("win_btn"); bmn.clicked.connect(self.showMinimized); bmx = QPushButton("☐"); bmx.setObjectName("win_btn"); bmx.clicked.connect(self.toggle_max); bcl = QPushButton("✕"); bcl.setObjectName("close_btn"); bcl.clicked.connect(self.close)
        th.addWidget(bmn); th.addWidget(bmx); th.addWidget(bcl); cv.addWidget(top)
        
        self.scr = QScrollArea(); self.scr.setWidgetResizable(True); self.cnt = QWidget(); self.cnt.setObjectName("scroll_content")
        self.cl = QVBoxLayout(self.cnt); self.cl.setAlignment(Qt.AlignTop); self.cl.setSpacing(20); self.cl.setContentsMargins(60,20,60,20); self.scr.setWidget(self.cnt); cv.addWidget(self.scr, 1)
        
        ic = QFrame(); ic.setObjectName("input_container"); il = QVBoxLayout(ic); il.setContentsMargins(0,0,0,10)
        ib = QFrame(); ib.setObjectName("input_oval"); ib.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); ibl = QVBoxLayout(ib); ibl.setContentsMargins(10,5,10,5); ibl.setSpacing(0)
        self.tx = InputEdit(self); self.tx.setPlaceholderText("Спросите что-нибудь..."); self.tx.setFixedHeight(50); self.tx.textChanged.connect(lambda: [self.tx.setFixedHeight(min(150, max(50, int(self.tx.document().size().height()+10)))), self.bs.setEnabled(bool(self.tx.toPlainText().strip() or self.img))]); ibl.addWidget(self.tx)
        
        bl = QHBoxLayout(); bl.setContentsMargins(5,0,5,5); bl.setSpacing(10)
        bp = QPushButton("+"); bp.setObjectName("plus_btn"); bp.setFixedSize(32,32); bp.setCursor(Qt.PointingHandCursor); bp.clicked.connect(self.att); bl.addWidget(bp)
        bt = QPushButton("Инструменты"); bt.setObjectName("capsule_btn"); bt.setCursor(Qt.PointingHandCursor)
        tm = QMenu(self); aw = QAction("Поиск в Google", self, checkable=True); aw.setChecked(True); aw.triggered.connect(self.toggle_web_search); av = QAction("Голосовой режим", self); av.triggered.connect(self.enter_voice_mode); tm.addAction(aw); tm.addAction(av); bt.setMenu(tm); bl.addWidget(bt)
        bl.addStretch()
        self.bm = QPushButton("Думающая 2.0 ▾"); self.bm.setObjectName("capsule_btn"); self.bm.setCursor(Qt.PointingHandCursor)
        mm = QMenu(self); af = QAction("Быстрая", self); af.triggered.connect(lambda: self.set_mode(False)); at = QAction("Думающая", self); at.triggered.connect(lambda: self.set_mode(True)); mm.addAction(af); mm.addAction(at); self.bm.setMenu(mm); bl.addWidget(self.bm)
        self.bs = SendButton(); self.bs.clicked.connect(lambda: self.send()); self.bs.setEnabled(False); bl.addWidget(self.bs)
        ibl.addLayout(bl); il.addWidget(ib)
        dl = QLabel("✨ Qwen2.5-VL-7B может делать ошибки, поэтому проверяйте его ответы."); dl.setObjectName("disclaimer"); dl.setAlignment(Qt.AlignCenter); il.addWidget(dl)
        cv.addWidget(ic); self.stack.addWidget(p_chat)
        
        self.setup_extras()
        self.apply_styles(); self.oldPos = None; top.mousePressEvent = self.win_press; top.mouseMoveEvent = self.win_move

    def setup_extras(self):
        # Settings Page
        self.settings_page = SettingsPage(self.conf)
        self.settings_page.config_changed.connect(self.update_config)
        self.settings_page.back_clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.settings_page.clear_history_clicked.connect(self.clear_all_history) # Подключили очистку
        self.stack.addWidget(self.settings_page)
        
        # Voice Page
        pv = QWidget(); pv.setObjectName("voice_page"); vl = QVBoxLayout(pv); self.voice_viz = VoiceVisualizer(); self.voice_viz.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding); vl.addWidget(self.voice_viz)
        vb = QHBoxLayout(); bm = QPushButton("🎙"); bm.setObjectName("voice_control_btn"); bm.setCheckable(True); bm.setFixedSize(60,60); bm.clicked.connect(self.toggle_mute); bx = QPushButton("✕"); bx.setObjectName("voice_control_btn"); bx.setFixedSize(60,60); bx.clicked.connect(self.exit_voice_mode)
        vb.addStretch(); vb.addWidget(bm); vb.addWidget(bx); vb.addStretch(); vl.addLayout(vb); self.stack.addWidget(pv)

    # --- METHODS ---
    def to_settings(self):
        self.settings_page.update_data(self.conf)
        self.stack.setCurrentWidget(self.settings_page)

    def update_config(self, new_conf):
        self.conf = new_conf
        self.save_settings()
        self.apply_styles()
        self.render()
        self.stack.setCurrentIndex(0)

    def clear_all_history(self):
        res = QMessageBox.question(self, "Очистка", "Удалить все чаты? Это нельзя отменить.", QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            self.chats = []
            self.new_chat()
            self.save_history()

    # (Остальные методы load_settings, save_history и т.д. - копируй из предыдущего ответа, они не менялись, но я вставлю сокращенно)
    def save_settings(self): json.dump(self.conf, open(SETTINGS_FILE, 'w', encoding='utf-8'), indent=4)
    def load_settings(self):
        defaults = {"lang_mode":0,"memory":"","user_name":"Вы","ai_name":"Qwen2.5-VL-7B","accent_color":"#a8c7fa","font_size":14,"theme_name":"Qwen2.5-VL-7B","thinking":False}
        try: self.conf = {**defaults, **json.load(open(SETTINGS_FILE,'r',encoding='utf-8'))}
        except: self.conf = defaults
    def load_history(self):
        try: self.chats = json.load(open(HISTORY_FILE,'r',encoding='utf-8'))
        except: self.chats = []
        if not self.chats: self.new_chat()
        else: self.curr=0; self.refresh(); QTimer.singleShot(100, self.render)
    def save_history(self): json.dump(self.chats, open(HISTORY_FILE,'w',encoding='utf-8'), indent=4)
    def refresh(self):
        self.lst.clear()
        for c in self.chats: self.lst.addItem(c.get("title", "Чат"))
        if 0 <= self.curr < self.lst.count(): self.lst.setCurrentRow(self.curr); self.chat_title_lbl.setText(self.chats[self.curr].get("title", ""))
    def render(self):
        while self.cl.count(): i = self.cl.takeAt(0); i.widget().deleteLater() if i.widget() else None
        if 0 <= self.curr < len(self.chats): [self.add_msg_widget(m) for m in self.chats[self.curr].get("msgs", [])]
    def switch(self, item): self.curr = self.lst.row(item); self.render(); self.stack.setCurrentIndex(0); self.chat_title_lbl.setText(item.text())
    def delete(self, i): del self.chats[i]; self.new_chat() if not self.chats else self.refresh() or self.render() or self.save_history()
    def new_chat(self): self.chats.insert(0, {"title": "Новый чат", "msgs": []}); self.curr = 0; self.refresh(); self.render(); self.save_history(); self.stack.setCurrentIndex(0); self.chat_title_lbl.setText("")
    def ctx_menu(self, p):
        it = self.lst.itemAt(p); m = QMenu(self); a = m.addAction("Удалить")
        if it and m.exec(self.lst.mapToGlobal(p)) == a: self.delete(self.lst.row(it))
    
    def send(self, voice_mode=False):
        t = self.tx.toPlainText().strip()
        if not t and not self.img: return
        tm = datetime.datetime.now().strftime("%H:%M"); c_img = self.img
        self.chats[self.curr]["msgs"].append({"role":"user", "text":t, "img":c_img, "time":tm})
        if len(self.chats[self.curr]["msgs"])==1: self.chats[self.curr]["title"] = t[:30]; self.refresh()
        self.add_msg_widget(self.chats[self.curr]["msgs"][-1]); self.save_history()
        self.tx.clear(); self.img=None; self.tx.setPlaceholderText("Спросите что-нибудь..."); self.bs.setEnabled(False)
        ctx = fetch_web_context(t) if self.is_web_enabled and WEB_AVAILABLE else None
        self.current_bot_bubble = self.add_msg_widget({"role":"bot", "text":"", "time":tm}, ret=True)
        # Передаем КОНФИГ полностью
        self.worker = GenThread(c_img, t, self.chats[self.curr]["msgs"][:-1][-6:], self.conf, voice_mode, ctx)
        self.worker.partial.connect(lambda x: self.current_bot_bubble.set_text(x))
        self.worker.finished.connect(self.res); self.worker.start()
        if voice_mode: self.is_voice_reply = True

    def res(self, t):
        self.chats[self.curr]["msgs"].append({"role":"bot", "text":t, "time":""}); self.save_history()
        if self.current_bot_bubble: self.current_bot_bubble.set_text(t); self.current_bot_bubble=None
        self.bs.setEnabled(True)
        if getattr(self, "is_voice_reply", False): self.voice_ready(t); self.is_voice_reply=False
    def add_msg_widget(self, m, ret=False):
        r = QWidget(); hl = QHBoxLayout(r); hl.setContentsMargins(0,0,0,0)
        b = MsgBubble(m.get("text",""), m.get("role")=="user", m.get("img"), "", self.conf["font_size"], lambda: self.scr.verticalScrollBar().setValue(self.scr.verticalScrollBar().maximum()))
        if m.get("role")=="user": hl.addStretch(); hl.addWidget(b)
        else: hl.addWidget(b); hl.addStretch()
        self.cl.addWidget(r); QTimer.singleShot(30, lambda: self.scr.verticalScrollBar().setValue(self.scr.verticalScrollBar().maximum()))
        if ret: return b
    def toggle_web_search(self, checked): self.is_web_enabled = checked
    def set_mode(self, t): self.conf["thinking"]=t; self.save_settings(); self.bm.setText("Думающая 2.0 ▾" if t else "Быстрая (Flash) ▾")
    def att(self): f,_=QFileDialog.getOpenFileName(self, "", "", "*.jpg *.png"); self.img=f; self.tx.setPlaceholderText(f"Файл: {os.path.basename(f)}") if f else None
    def apply_styles(self): self.setStyleSheet(get_styles(self.conf["accent_color"], self.conf["font_size"]))
    def on_ready(self, m): 
        if m!="OK": QMessageBox.critical(self,"Err",m)
    def set_status(self, t): pass
    def enter_voice_mode(self): self.stack.setCurrentIndex(2); self.voice_viz.set_state("LISTENING"); self.start_list()
    def exit_voice_mode(self): self.stop_list(); self.stack.setCurrentIndex(0)
    def toggle_mute(self, c): self.stop_list() if c else self.start_list(); self.voice_viz.set_state("IDLE" if c else "LISTENING")
    def start_list(self): self.listener=VoiceListenerThread(); self.listener.text_recognized.connect(lambda t: [self.voice_viz.set_state("THINKING"), self.tx.setText(t), self.send(True)]); self.listener.start()
    def stop_list(self): 
        if self.listener: self.listener.stop(); self.listener=None
    def voice_ready(self, t): self.voice_viz.set_state("SPEAKING"); self.tts=TTSWorker(t); self.tts.finished.connect(lambda: [self.voice_viz.set_state("LISTENING"), self.start_list()] if self.stack.currentIndex()==2 else None); self.tts.start()
    def win_press(self, e): self.oldPos = e.globalPosition().toPoint()
    def win_move(self, e): self.move(self.pos() + e.globalPosition().toPoint() - self.oldPos) if self.oldPos else None; self.oldPos = e.globalPosition().toPoint()
    def toggle_max(self): self.showNormal() if self.isMaximized() else self.showMaximized()
    def resizeEvent(self, e): self.sizegrip.move(self.width()-20, self.height()-20); super().resizeEvent(e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())