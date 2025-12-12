import torch
from PySide6.QtCore import QThread, Signal
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig

# Глобальное хранилище модели (синглтон)
ai_storage = {"model": None, "proc": None}

class LoaderThread(QThread):
    status = Signal(str)
    finished = Signal(str)
    
    def run(self):
        try:
            self.status.emit("ИИ загружается...")
            model_id = "Qwen/Qwen2.5-VL-7B-Instruct"
            use_cuda = torch.cuda.is_available()
            device = "cuda" if use_cuda else "cpu"

            quant_config = None
            if use_cuda:
                self.status.emit("Режим: GPU, 4-bit квантование")
                quant_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16,
                )
            else:
                self.status.emit("Режим: CPU (медленно)")

            if quant_config:
                ai_storage["model"] = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    model_id, quantization_config=quant_config, device_map=device,
                    torch_dtype=torch.bfloat16, trust_remote_code=True
                )
            else:
                ai_storage["model"] = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                    model_id, device_map=device, torch_dtype=torch.float32, trust_remote_code=True
                )

            ai_storage["proc"] = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
            self.finished.emit("OK")
        except Exception as e:
            self.finished.emit(str(e))