import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from transformers import BitsAndBytesConfig
import time


MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"

# 4-битное квантование
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

print(f"🚀 {MODEL_ID} готов к загрузке и 4-bit квантованию!")
print("--- В первый раз это скачает ~15GB данных! ---")

# 1. Загрузка модели (Она сама скачает файлы с Hugging Face)
try:
    start_time = time.time()
    

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID,
        device_map="auto",          # Автоматически использует твою RTX 3050
        quantization_config=bnb_config, 
        trust_remote_code=True,
        # Это не всегда показывает прогресс, но загрузка будет идти!
        # Смотри на консоль, там будут полоски Downloading: xx%
    )
    
    end_time = time.time()
    
except Exception as e:
    print(f"❌ АХТУНГ! Ошибка загрузки модели: {e}")
    exit()

# 2. Загрузка процессора
processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

print("---")
print(f"✅ Модель успешно загружена, сжата в 4-bit и готова к работе!")
print(f"⏱️ Общее время загрузки: {end_time - start_time:.2f} секунд (Первый запуск будет долгим из-за скачивания!)")
print("---")

#!ТЕСТ! (Проверяем, что всё работает)
text_input = "Объясни что такое квантовая материя" # ПРОМПТ
print(f"❓ Твой вопрос: {text_input}")

messages = [
    {"role": "user", "content": [{"type": "text", "text": text_input}]}
]

# Подготовка ввода
text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = processor(text=[text], padding=True, return_tensors="pt")
inputs = inputs.to("cuda")

# Генерация ответа
print("🤖 Думаю... (Смотри загрузку VRAM в Диспетчере задач!)")
generated_ids = model.generate(**inputs, max_new_tokens=412)
generated_ids_trimmed = [
    out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)

print(f"\n🗣️ ОТВЕТ ИИ: {output_text[0]}")