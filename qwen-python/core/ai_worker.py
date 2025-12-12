import os
import re
import threading
import torch
import gc
from PySide6.QtCore import QThread, Signal
from transformers import TextIteratorStreamer
from PIL import Image
from core.loader import ai_storage
from utils.helpers import clean_stream_text

class GenThread(QThread):
    finished = Signal(str)
    partial = Signal(str)

    def __init__(self, img, text, history_data, config, is_voice_mode=False, web_context=None):
        super().__init__()
        self.img = img
        self.text = text
        self.history_data = history_data
        self.conf = config # Получаем весь конфиг
        self.is_voice = is_voice_mode
        self.web_context = web_context
        
        # Настройки из конфига
        self.target_lang = "Russian" if self.conf.get("lang_mode", 0) == 0 else "English"
        self.temp = self.conf.get("temperature", 0.4) # Температура
        self.top_p = self.conf.get("top_p", 0.9)
        self.max_tokens = 1024

    def run(self):
        try:
            if not ai_storage["model"]:
                self.finished.emit("Ошибка: Модель не загружена")
                return

            proc = ai_storage["proc"]
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            # Формируем промпт
            lang_instr = f"Response MUST be in {self.target_lang}."
            style_instr = "You are a helpful AI assistant. Be accurate, concise, and friendly."
            
            # Если включен режим "Бро" в памяти, он применится через self.conf['memory']
            sys_prompt = f"{self.conf.get('memory', '')}\n{lang_instr} {style_instr}"
            
            if self.is_voice:
                sys_prompt += " VOICE MODE: Keep answers extremely short (max 2 sentences)."
            
            if self.web_context:
                sys_prompt += f"\n\nCONTEXT FROM WEB:\n{self.web_context}\nUse this info to answer."

            messages = [{"role": "system", "content": [{"type": "text", "text": sys_prompt}]}]

            # Добавляем историю
            for msg in self.history_data:
                role = "user" if msg["role"] == "user" else "assistant"
                content = [{"type": "text", "text": msg["text"]}]
                messages.append({"role": role, "content": content})

            # Текущее сообщение
            curr_content = [{"type": "text", "text": self.text}]
            
            images = []
            if self.img and os.path.exists(self.img): 
                raw_img = Image.open(self.img).convert("RGB")
                # Сжатие
                max_size = 1024
                if raw_img.width > max_size or raw_img.height > max_size:
                    raw_img.thumbnail((max_size, max_size))
                
                curr_content.insert(0, {"type": "image", "text": self.img}) 
                images.append(raw_img) 

            messages.append({"role": "user", "content": curr_content})

            chat_struct = proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            
            if not images and "<|image_" in chat_struct: 
                chat_struct = re.sub(r"<\|image_\d+\|>", "", chat_struct)

            inputs = proc(text=[chat_struct], images=images if images else None, padding=True, return_tensors="pt").to(device)

            streamer = TextIteratorStreamer(proc.tokenizer, skip_special_tokens=True, skip_prompt=True)
            
            # Генерация с параметрами из настроек
            gen_kwargs = dict(
                **inputs, 
                max_new_tokens=self.max_tokens, 
                temperature=self.temp, 
                top_p=self.top_p,
                do_sample=True, 
                streamer=streamer
            )

            th = threading.Thread(target=lambda: ai_storage["model"].generate(**gen_kwargs))
            th.start()

            full_text = ""
            for chunk in streamer:
                full_text += chunk
                self.partial.emit(clean_stream_text(full_text))
            
            th.join()
            self.finished.emit(clean_stream_text(full_text).strip())

        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            self.finished.emit("❌ ОШИБКА ПАМЯТИ: Видеокарта перегружена.")
        except Exception as e:
            self.finished.emit(f"Error: {e}")
        finally:
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()