
(() => {
    "use strict";

    const fileInput = document.getElementById("media-file");
    const selectedFiles = document.getElementById("selected-files");
    const dropArea = document.getElementById("file-drop");
    const uploadForm = document.getElementById("upload-form");
    const uploadButton = document.getElementById("upload-button");
    const progressList = document.getElementById("upload-progress-list");

    if (!fileInput || !uploadForm) return;

    const MAX_SIZE = 500 * 1024 * 1024;

    const ALLOWED_EXTENSIONS = [
        ".jpg", ".jpeg", ".png", ".webp", ".gif",
        ".mp4", ".webm", ".mov"
    ];

    let selectedFileList = [];

    function formatSize(size) {
        return (size / 1024 / 1024).toFixed(1) + " MB";
    }

    function getExtension(name) {
        return name.substring(name.lastIndexOf(".")).toLowerCase();
    }

    // ファイル選択
    fileInput.addEventListener("change", () => {
        selectedFileList = Array.from(fileInput.files);
        renderSelectedFiles();
    });

    // 選択ファイル一覧
    function renderSelectedFiles() {

        selectedFiles.replaceChildren();

        if (selectedFileList.length === 0) {
            selectedFiles.textContent = "ファイル未選択";
            return;
        }

        const heading = document.createElement("strong");
        heading.textContent = `${selectedFileList.length} ファイル選択中`;
        selectedFiles.appendChild(heading);

        selectedFileList.forEach((file, index) => {

            const item = document.createElement("div");
            item.className = "selected-file-item";

            const name = document.createElement("span");
            name.textContent = `${index + 1}. ${file.name}`;

            const size = document.createElement("span");
            size.textContent = formatSize(file.size);

            item.append(name, size);
            selectedFiles.appendChild(item);
        });
    }

    // ドラッグ＆ドロップ
    if (dropArea) {

        ["dragenter", "dragover"].forEach(eventName => {
            dropArea.addEventListener(eventName, event => {
                event.preventDefault();
                dropArea.classList.add("drag-over");
            });
        });

        ["dragleave", "drop"].forEach(eventName => {
            dropArea.addEventListener(eventName, event => {
                event.preventDefault();
                dropArea.classList.remove("drag-over");
            });
        });

        dropArea.addEventListener("drop", event => {

            const files = Array.from(event.dataTransfer.files);

            selectedFileList = files;

            const transfer = new DataTransfer();

            files.forEach(file => transfer.items.add(file));

            fileInput.files = transfer.files;

            renderSelectedFiles();
        });
    }

    // 進捗表示
    function createProgressItem(file) {

        const container = document.createElement("div");
        container.className = "upload-progress-item";

        const name = document.createElement("div");
        name.className = "progress-file-name";
        name.textContent = file.name;

        const status = document.createElement("div");
        status.className = "progress-status";
        status.textContent = "待機中";

        const progress = document.createElement("progress");
        progress.max = 100;
        progress.value = 0;

        const percent = document.createElement("span");
        percent.className = "progress-percent";
        percent.textContent = "0%";

        container.append(name, status, progress, percent);

        progressList.appendChild(container);

        return {
            status,
            progress,
            percent
        };
    }

    // 1ファイルずつアップロード
    function uploadFile(file, ui) {

        return new Promise(resolve => {

            const extension = getExtension(file.name);

            if (!ALLOWED_EXTENSIONS.includes(extension)) {
                ui.status.textContent = "対応していない形式";
                resolve(false);
                return;
            }

            if (file.size > MAX_SIZE) {
                ui.status.textContent = "500MBを超えています";
                resolve(false);
                return;
            }

            const formData = new FormData();

            formData.append("action", "upload");
            formData.append("file", file);
            formData.append("csrfmiddlewaretoken",
                uploadForm.querySelector(
                    '[name="csrfmiddlewaretoken"]'
                ).value
            );

            const xhr = new XMLHttpRequest();

            xhr.open("POST", window.location.href);

            xhr.setRequestHeader(
                "X-Requested-With",
                "XMLHttpRequest"
            );

            ui.status.textContent = "アップロード中";

            xhr.upload.addEventListener("progress", event => {

                if (!event.lengthComputable) return;

                const value = Math.round(
                    event.loaded / event.total * 100
                );

                ui.progress.value = value;
                ui.percent.textContent = value + "%";
            });

            xhr.onload = () => {

                let result;

                try {
                    result = JSON.parse(xhr.responseText);
                } catch {
                    ui.status.textContent = "サーバー応答エラー";
                    resolve(false);
                    return;
                }

                if (xhr.status >= 200 &&
                    xhr.status < 300 &&
                    result.success) {

                    ui.progress.value = 100;
                    ui.percent.textContent = "100%";
                    ui.status.textContent = "完了";

                    resolve(true);

                } else {

                    ui.status.textContent =
                        result.message || "アップロード失敗";

                    resolve(false);
                }
            };

            xhr.onerror = () => {
                ui.status.textContent = "通信エラー";
                resolve(false);
            };

            xhr.onabort = () => {
                ui.status.textContent = "中断";
                resolve(false);
            };

            xhr.send(formData);
        });
    }

    // 一括アップロード
    uploadForm.addEventListener("submit", async event => {

        event.preventDefault();

        if (selectedFileList.length === 0) {
            alert("ファイルを選択してください。");
            return;
        }

        if (uploadButton.disabled) return;

        const files = [...selectedFileList];

        progressList.replaceChildren();

        const progressItems = files.map(file =>
            createProgressItem(file)
        );

        uploadButton.disabled = true;
        uploadButton.textContent = "アップロード中...";

        let successCount = 0;
        let failureCount = 0;

        try {

            for (let i = 0; i < files.length; i++) {

                const success = await uploadFile(
                    files[i],
                    progressItems[i]
                );

                if (success) {
                    successCount++;
                } else {
                    failureCount++;
                }
            }

        } finally {

            uploadButton.disabled = false;
            uploadButton.textContent = "一括アップロード";
        }

        alert(
            `アップロード完了\n\n` +
            `成功：${successCount}件\n` +
            `失敗：${failureCount}件`
        );

        if (successCount > 0) {
            window.location.reload();
        }
    });

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
