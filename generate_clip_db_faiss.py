import os
import torch
import clip
import faiss
import numpy as np
from PIL import Image
from tqdm import tqdm

# Папка с кадрами
frames_dir = os.path.expanduser("~/Desktop/Примеры кадров")

# Соответствие: кадр → видеофайл
frame_to_video = {
    "Frame_1.jpg": "Long_1.mp4",
    "Frame_2.jpg": "Long_2.mp4",
    "Frame_3.jpg": "Long_3.mp4",
    "Frame_4.jpg": "Long_4.mp4",
    "Frame_5.jpg": "Long_5.mp4",
    "Frame_6.jpg": "Long_6.mp4",
    "Frame_7.jpg": "Long_7.mp4",
    "Frame_8.jpg": "Long_8.mp4"
}

# Устройство
device = "cuda" if torch.cuda.is_available() else "cpu"

# Загрузка модели CLIP
print("[🧠] Загружаем CLIP...")
model, preprocess = clip.load("ViT-B/32", device=device)

# Списки для эмбеддингов и имён
embeddings = []
filenames = []

# Обработка каждого кадра
print("[🎞️] Обрабатываем кадры...")
for frame_name, video_name in tqdm(frame_to_video.items()):
    frame_path = os.path.join(frames_dir, frame_name)
    if not os.path.exists(frame_path):
        print(f"[⚠️] Файл не найден: {frame_path}")
        continue

    image = Image.open(frame_path).convert("RGB")
    image_input = preprocess(image).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_input).cpu().numpy()
        image_features /= np.linalg.norm(image_features, axis=1, keepdims=True)

    embeddings.append(image_features[0])
    filenames.append(video_name)

# Создание FAISS-индекса
print("[📦] Строим FAISS-индекс...")
embedding_matrix = np.vstack(embeddings).astype("float32")
index = faiss.IndexFlatL2(embedding_matrix.shape[1])
index.add(embedding_matrix)

# Сохраняем
faiss.write_index(index, "clip.index")
with open("clip_filenames.txt", "w", encoding="utf-8") as f:
    for name in filenames:
        f.write(f"{name}\n")

print("✅ FAISS индекс и clip_filenames.txt сохранены.")