import time
from PySide6.QtCore import QObject, Signal, QThread

VOICE_AVAILABLE = False
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except Exception:
    pass

class TTSWorker(QObject):
    finished = Signal()
    def __init__(self, text):
        super().__init__()
        self.text = text
    def run(self):
        if not VOICE_AVAILABLE: 
            self.finished.emit()
            return
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            target_voice = None
            for v in voices:
                if 'ru' in v.id.lower() or 'russian' in v.name.lower():
                    target_voice = v.id
                    if 'irina' in v.name.lower(): break
            if target_voice: engine.setProperty('voice', target_voice)
            engine.setProperty('rate', 145)
            engine.setProperty('volume', 1.0)
            engine.say(self.text)
            engine.runAndWait()
        except Exception:
            pass
        self.finished.emit()

class VoiceListenerThread(QThread):
    text_recognized = Signal(str)
    def __init__(self):
        super().__init__()
        self.running = True
        if VOICE_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            with self.microphone as source:
                try: self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                except Exception: pass

    def run(self):
        if not VOICE_AVAILABLE: return
        while self.running:
            try:
                with self.microphone as source:
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=8)
                        text = self.recognizer.recognize_google(audio, language="ru-RU")
                        if text.strip(): self.text_recognized.emit(text)
                    except Exception: continue
            except Exception: time.sleep(0.1)
    def stop(self): self.running = False