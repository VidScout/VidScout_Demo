document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("file-upload");
    const logo = document.getElementById("pulse-logo");

    fileInput.addEventListener("change", async function () {
        if (fileInput.files.length === 0) return;

        const file = fileInput.files[0];

        // Анимация загрузки
        logo.classList.remove("pulse");
        logo.classList.add("rotating");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await fetch("http://127.0.0.1:8000/match", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            // Вернуть пульсацию
            logo.classList.remove("rotating");
            logo.classList.add("pulse");

            if (data.error) {
                alert("Ошибка: " + data.error);
            } else {
                const resultHTML = `
                    <div class="result-block">
                        <img id="resultImage" src="${URL.createObjectURL(file)}" alt="Загруженный кадр" class="frame-preview">
                        <p><strong>🎬 Название:</strong> ${data.title}</p>
                        <p><strong>🎭 Жанр:</strong> ${data.genre}</p>
                        <p><strong>📅 Год:</strong> ${data.year}</p>
                        <p><strong>🌍 Страна:</strong> ${data.country}</p>
                        <p><strong>🎥 Режиссёр:</strong> ${data.director}</p>
                        <p><strong>📝 Сценарий:</strong> ${data.writer}</p>
                        <p><strong>👥 Актёры:</strong> ${data.actors.join(", ")}</p>
                    </div>
                `;
                const resultContainer = document.getElementById("resultContainer");
                resultContainer.innerHTML = resultHTML;
                resultContainer.classList.remove("hidden");
            }
        } catch (error) {
            console.error("Ошибка:", error);
            alert("Произошла ошибка при отправке запроса.");
            logo.classList.remove("rotating");
            logo.classList.add("pulse");
        }
    });
});
