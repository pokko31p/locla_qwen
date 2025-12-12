THEMES = {
    "Qwen2.5-VL-7B Blue": "#a8c7fa",
}

def get_styles(accent_color, font_size):
    bg_main = "#131314"
    bg_sidebar = "#0b0b0b"
    bg_capsule = "#1e1f20"
    text_main = "#e3e3e3"
    text_sec = "#c4c7c5"
    
    return f"""
    QMainWindow {{ background-color: {bg_main}; }}
    QFrame#central_widget {{ background-color: {bg_main}; border: 1px solid #333; border-radius: 12px; }}
    QWidget {{ font-family: 'Segoe UI', sans-serif; color: {text_main}; font-size: {font_size}px; }}

    /* САЙДБАР */
    QWidget#sidebar {{ background-color: {bg_sidebar}; border-top-left-radius: 12px; border-bottom-left-radius: 12px; border-right: none; }}
    
    QPushButton#menu_btn {{ background-color: transparent; border: none; color: {text_sec}; font-size: 20px; border-radius: 20px; padding: 5px; }}
    QPushButton#menu_btn:hover {{ background-color: #2b2d30; }}

    QPushButton#new_chat {{ background-color: {bg_sidebar}; border: 1px solid transparent; border-radius: 20px; color: #444746; font-size: 14px; font-weight: 600; text-align: left; padding: 10px 15px; margin: 0px; }}
    QPushButton#new_chat:hover {{ background-color: #1e1f20; color: {text_main}; }}

    QPushButton#incognito_btn {{ background-color: {bg_sidebar}; border: 1px solid transparent; border-radius: 20px; color: #444746; font-size: 18px; margin: 0px; }}
    QPushButton#incognito_btn:hover {{ background-color: #1e1f20; color: {text_main}; }}

    QListWidget {{ background: transparent; border: none; outline: 0; margin-top: 5px; }}
    QListWidget::item {{ padding: 8px 15px; margin: 2px 10px; border-radius: 18px; color: {text_sec}; font-weight: 500; }}
    QListWidget::item:selected {{ background-color: #004a77; color: white; }}
    QListWidget::item:hover {{ background-color: #1e1f20; }}

    QPushButton#sidebar_item {{ background-color: transparent; border: none; color: {text_sec}; text-align: left; padding: 12px 20px; font-size: 14px; font-weight: 500; margin: 2px 10px; border-radius: 8px; }}
    QPushButton#sidebar_item:hover {{ background-color: #2b2d30; color: #e3e3e3; }}

    QLabel#location_lbl {{ color: #8e918f; font-size: 11px; padding-left: 20px; line-height: 1.4; font-weight: 600; }}

    /* ВЕРХНЯЯ ПАНЕЛЬ */
    QWidget#top_bar {{ background-color: {bg_main}; border: none; }}
    QLabel#ai_title {{ font-size: 18px; color: #e3e3e3; font-weight: 600; padding-left: 10px; }}
    QLabel#chat_title {{ font-size: 14px; color: #c4c7c5; font-weight: 500; }}
    QPushButton#win_btn, QPushButton#close_btn {{ background: transparent; border: none; color: {text_sec}; font-size: 16px; width: 40px; height: 40px; border-radius: 20px; }}
    QPushButton#win_btn:hover {{ background-color: #2b2d30; color: white; }}
    QPushButton#close_btn:hover {{ background-color: #ff5252; color: white; }}

    /* ЧАТ */
    QScrollArea {{ border: none; background: transparent; }}
    QWidget#scroll_content {{ background: transparent; }}
    QFrame#bubble_user {{ background-color: #282a2c; border-radius: 18px; }}
    QFrame#bubble_bot {{ background-color: rgba(30, 31, 32, 0.6); border-radius: 18px; }}
    QLabel#chat_text {{ color: {text_main}; line-height: 1.6; font-size: 16px; }}
    QPushButton#action_btn {{ background-color: transparent; border: none; color: #c4c7c5; font-size: 16px; border-radius: 15px; width: 30px; height: 30px; }}
    QPushButton#action_btn:hover {{ background-color: #2b2d30; color: white; }}

    /* ВВОД */
    QFrame#input_container {{ background-color: {bg_main}; border: none; padding: 0px 60px 20px 60px; }}
    QFrame#input_oval {{ background-color: {bg_capsule}; border: none; border-radius: 26px; }}
    QTextEdit {{ background: transparent; border: none; color: {text_main}; font-size: 16px; padding: 12px 15px 0px 15px; }}
    QPushButton#plus_btn {{ background-color: #2b2d30; color: {text_sec}; border-radius: 16px; font-size: 22px; border: none; font-weight: 300; padding-bottom: 3px; }}
    QPushButton#plus_btn:hover {{ background-color: #e3e3e3; color: {bg_main}; }}
    QPushButton#capsule_btn {{ background-color: transparent; border: none; border-radius: 8px; color: {text_sec}; font-size: 13px; font-weight: 600; padding: 6px 12px; text-align: center; }}
    QPushButton#capsule_btn:hover {{ background-color: #333537; color: white; }}
    QPushButton::menu-indicator {{ image: none; width: 0px; }}
    QPushButton#send_btn {{ background-color: transparent; border: none; }}
    QPushButton#send_btn:hover {{ background-color: #333537; border-radius: 20px; }}
    QPushButton#send_btn:disabled {{ background-color: transparent; }}
    QLabel#disclaimer {{ color: #444746; font-size: 11px; margin-top: 8px; }}

    /* НАСТРОЙКИ */
    QFrame#settings_sidebar {{ background-color: {bg_sidebar}; border-right: 1px solid #2d2d2d; }}
    QLabel#settings_header {{ font-size: 22px; font-weight: bold; color: {text_main}; }}
    QPushButton#settings_menu_btn {{ background-color: transparent; color: {text_sec}; text-align: left; padding: 10px 15px; border-radius: 8px; font-size: 14px; border: none; }}
    QPushButton#settings_menu_btn:hover {{ background-color: #1e1f20; color: white; }}
    QPushButton#settings_menu_btn:checked {{ background-color: #2b2d30; color: #a8c7fa; font-weight: 600; border-left: 3px solid #a8c7fa; }}
    QPushButton#settings_back_btn {{ color: #a8c7fa; background: transparent; border: none; text-align: left; font-size: 14px; font-weight: bold; padding-left: 15px; }}
    
    QLabel#settings_section_title {{ font-size: 18px; font-weight: 600; color: {text_main}; margin-bottom: 5px; }}
    QLabel#settings_label_bold {{ font-size: 14px; font-weight: 600; color: {text_main}; }}
    QLabel#settings_desc {{ font-size: 13px; color: #9aa0a6; }}
    
    QLineEdit, QTextEdit, QSpinBox {{ background-color: {bg_capsule}; border: 1px solid #3c4043; border-radius: 8px; padding: 10px; color: white; font-size: 14px; }}
    
    /* Слайдер (Ползунок) */
    QSlider::groove:horizontal {{ border: 1px solid #3c4043; height: 6px; background: #1e1f20; margin: 2px 0; border-radius: 3px; }}
    QSlider::handle:horizontal {{ background: #a8c7fa; border: 1px solid #a8c7fa; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px; }}
    
    QPushButton#save_btn_blue {{ background-color: #0b57d0; color: white; border: none; border-radius: 20px; padding: 10px 24px; font-weight: 600; font-size: 14px; }}
    QPushButton#save_btn_blue:hover {{ background-color: #0842a0; }}
    
    QPushButton#danger_btn {{ background-color: #3a1c1c; color: #ff8a80; border: 1px solid #ff5252; border-radius: 8px; padding: 8px 16px; font-weight: 600; font-size: 13px; }}
    QPushButton#danger_btn:hover {{ background-color: #5a1c1c; }}

    QMenu {{ background-color: #1e1f20; border: 1px solid #444; border-radius: 12px; padding: 5px; }}
    QMenu::item {{ padding: 10px 15px; color: {text_main}; font-size: 13px; border-radius: 6px; }}
    QMenu::item:selected {{ background-color: #333537; }}
    QScrollBar:vertical {{ border: none; background: transparent; width: 8px; }}
    QScrollBar::handle:vertical {{ background: #444; border-radius: 4px; min-height: 20px; }}
    QSizeGrip {{ background: transparent; width: 16px; height: 16px; }}
    """