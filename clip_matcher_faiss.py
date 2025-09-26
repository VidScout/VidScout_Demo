import torch
import clip
import faiss
import numpy as np
from PIL import Image
import os

# Устройство
device = "cuda" if torch.cuda.is_available() else "cpu"

# Загрузка модели CLIP
print("[🧠] Загружаем модель CLIP...")
model, preprocess = clip.load("ViT-B/32", device=device)

# Проверка наличия файлов
if not os.path.exists("clip.index"):
    raise FileNotFoundError("[❌] Не найден FAISS-индекс clip.index")

if not os.path.exists("clip_filenames.txt"):
    raise FileNotFoundError("[❌] Не найден файл clip_filenames.txt")

# Загрузка FAISS-индекса и списка имён
print("[📦] Загружаем FAISS-индекс и список видеофайлов...")
faiss_index = faiss.read_index("clip.index")

with open("clip_filenames.txt", "r", encoding="utf-8") as f:
    filenames = [line.strip() for line in f]

def match_clip(image: Image.Image):
    if image is None:
        raise ValueError("Изображение не передано")

    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_input).cpu().numpy()
        image_features /= np.linalg.norm(image_features, axis=1, keepdims=True)

    _, index = faiss_index.search(image_features, k=1)

    matched_index = int(index[0][0])
    if matched_index >= len(filenames):
        raise IndexError(f"Неверный индекс: {matched_index}, файлов в списке: {len(filenames)}")

    matched_filename = filenames[matched_index]

    print(f"[🎯] Найдено совпадение: {matched_filename} (index: {matched_index})")
    return matched_filename

# Совместимость с FastAPI
match_image_to_video = match_clip
