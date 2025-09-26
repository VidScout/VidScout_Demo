import os
import subprocess
import cv2
import torch
import numpy as np
from tqdm import tqdm
from transformers import CLIPProcessor, CLIPModel
import faiss
import json
import uuid

# Настройки
SAVE_FOLDER = "youtube_downloads"
FRAME_EVERY_N_SECONDS = 10
METADATA_PATH = "video_metadata.json"
FAISS_INDEX_PATH = "clip.index"
FILENAMES_PATH = "clip_filenames.txt"

# Модель CLIP
device = "cuda" if torch.cuda.is_available() else "cpu"
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32", trust_remote_code=True, use_safetensors=True).to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Загрузка ссылок
with open("youtube_list.txt", "r") as f:
    links = [line.strip() for line in f if line.strip()]

os.makedirs(SAVE_FOLDER, exist_ok=True)

def download_video(url, output_dir):
    output_template = os.path.join(output_dir, "%(title).200s.%(ext)s")
    cmd = [
        "yt-dlp", "-f", "mp4", "-o", output_template, url
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"❌ Ошибка при скачивании {url}")

def extract_frames(video_path, interval_sec):
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or not vidcap.isOpened():
        raise ValueError(f"⚠️ Не удалось открыть видео или определить FPS: {video_path}")
    frame_interval = int(fps * interval_sec)
    frames = []
    success, frame = vidcap.read()
    count = 0
    while success:
        if count % frame_interval == 0:
            frames.append(frame)
        success, frame = vidcap.read()
        count += 1
    vidcap.release()
    return frames

def get_clip_embedding(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    inputs = processor(images=image_rgb, return_tensors="pt").to(device)
    with torch.no_grad():
        embedding = model.get_image_features(**inputs)
    return embedding.cpu().numpy().flatten()

# Загрузка или создание FAISS-индекса
if os.path.exists(FAISS_INDEX_PATH):
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(FILENAMES_PATH, "r") as f:
        filenames = [line.strip() for line in f]
    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)
else:
    index = faiss.IndexFlatL2(512)
    filenames = []
    metadata = {}

# Обработка каждого видео
for link in tqdm(links, desc="🧩 Обработка видео"):
    try:
        download_video(link, SAVE_FOLDER)
        downloaded_files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith(".mp4")]
        downloaded_files.sort(key=lambda f: os.path.getctime(os.path.join(SAVE_FOLDER, f)), reverse=True)
        video_file = downloaded_files[0]

        # Переименование файла с проблемными символами
        safe_name = video_file.replace("/", "_").replace("\\", "_").replace(":", "_")
        if safe_name != video_file:
            os.rename(os.path.join(SAVE_FOLDER, video_file), os.path.join(SAVE_FOLDER, safe_name))
            video_file = safe_name
        video_path = os.path.join(SAVE_FOLDER, video_file)

        frames = extract_frames(video_path, FRAME_EVERY_N_SECONDS)
        for frame in frames:
            emb = get_clip_embedding(frame)
            index.add(np.array([emb]))
            uid = str(uuid.uuid4())
            filenames.append(video_file)
            metadata[uid] = {
                "file": video_file,
                "title": os.path.splitext(video_file)[0],
                "type": "видеоролик",
                "source": link
            }
    except Exception as e:
        print(f"❗ Ошибка при обработке {link}: {e}")

# Сохраняем
faiss.write_index(index, FAISS_INDEX_PATH)
with open(FILENAMES_PATH, "w") as f:
    for name in filenames:
        f.write(name + "\n")

with open(METADATA_PATH, "w") as f:
    json.dump(metadata, f, ensure_ascii=False, indent=4)

print("✅ Обработка завершена.")