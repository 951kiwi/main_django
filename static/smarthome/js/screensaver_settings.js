(() => {
    "use strict";

    // ファイル選択時に名前を表示
    const fileInput = document.getElementById("media-file");
    const selectedFile = document.getElementById("selected-file");

    if (fileInput && selectedFile) {

        fileInput.addEventListener("change", () => {

            const file = fileInput.files[0];

            selectedFile.textContent = file
                ? `${file.name} (${(file.size / 1024 / 1024).toFixed(1)} MB)`
                : "ファイル未選択";

        });

    }

    // 削除前の確認
    document.querySelectorAll(".delete-form").forEach(form => {

        form.addEventListener("submit", event => {

            const title = form.dataset.title || "このメディア";

            if (!confirm(`「${title}」を削除しますか？`)) {
                event.preventDefault();
            }

        });

    });

})();