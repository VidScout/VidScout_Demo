from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from pathlib import Path
import tempfile

app = FastAPI(title="VidScout Portfolio API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/search")
async def search_image(file: UploadFile = File(...)):
    try:
        # читаем файл в память
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return JSONResponse(content={"error": "Не удалось прочитать изображение"}, status_code=400)

        # временно сохраним картинку (для отладки)
        tmp_path = Path(tempfile.gettempdir()) / file.filename
        cv2.imwrite(str(tmp_path), img)

        # Здесь будет твоя логика поиска по кадрам
        # Для демо: просто проверяем по имени файла
        if "1" in file.filename:
            result = {"video": "Long_1", "matched": True}
        elif "2" in file.filename:
            result = {"video": "Long_2", "matched": True}
        else:
            result = {"video": None, "matched": False}

        return result

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
