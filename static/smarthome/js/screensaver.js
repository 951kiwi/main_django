(() => {

    "use strict";

    // =====================================
    // 設定
    // =====================================

    const IDLE_TIME = 10 * 1000;

    const DEFAULT_IMAGE_DURATION = 10;

    // =====================================
    // DOM
    // =====================================

    const screensaver = document.getElementById(
        "screensaver"
    );

    const stage = document.getElementById(
        "screensaver-stage"
    );

    const dataElement = document.getElementById(
        "screensaver-data"
    );

    if (!screensaver || !stage || !dataElement) {
        console.error("[ScreenSaver] DOMが見つかりません");
        return;
    }

    // =====================================
    // メディアデータ
    // =====================================

    let mediaList = [];

    try {
        mediaList = JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error("[ScreenSaver] JSONエラー", error);
    }

    let currentIndex = 0;

    let idleTimer = null;

    let mediaTimer = null;

    let isActive = false;

    // =====================================
    // スクリーンセイバー表示
    // =====================================

    function showScreensaver() {

        if (isActive || mediaList.length === 0) {
            console.error("[ScreenSaver] 起動できません", {
        isActive: isActive,
        mediaCount: mediaList.length,
        mediaList: mediaList
    });
            return;
        }

        isActive = true;

        screensaver.classList.add("active");

        screensaver.setAttribute(
            "aria-hidden",
            "false"
        );

        console.log("[ScreenSaver] 表示開始");

        playCurrentMedia();
    }

    // =====================================
    // スクリーンセイバー解除
    // =====================================

    function hideScreensaver() {

        if (!isActive) {
            return;
        }

        isActive = false;

        screensaver.classList.remove("active");

        screensaver.setAttribute(
            "aria-hidden",
            "true"
        );

        clearTimeout(mediaTimer);

        const video = stage.querySelector("video");

        if (video) {
            video.pause();
            video.removeAttribute("src");
            video.load();
        }

        stage.replaceChildren();

        console.log("[ScreenSaver] 解除");
    }

    // =====================================
    // 次のメディア
    // =====================================

    function nextMedia() {

        if (!isActive || mediaList.length === 0) {
            return;
        }

        currentIndex++;

        if (currentIndex >= mediaList.length) {
            currentIndex = 0;
        }

        playCurrentMedia();
    }

    // =====================================
    // メディア再生
    // =====================================

    function playCurrentMedia() {

        if (!isActive || mediaList.length === 0) {
            return;
        }

        clearTimeout(mediaTimer);

        const media = mediaList[currentIndex];

        stage.replaceChildren();

        console.log(
            "[ScreenSaver] 再生:",
            media.title
        );

        // ---------------------------------
        // 画像
        // ---------------------------------

        if (media.type === "image") {

            const img = document.createElement("img");

            img.src = media.url;

            img.alt = media.title || "";

            img.onload = () => {

                const duration =
                    Math.max(
                        1,
                        Number(media.duration) ||
                        DEFAULT_IMAGE_DURATION
                    );

                mediaTimer = setTimeout(
                    nextMedia,
                    duration * 1000
                );

            };

            img.onerror = () => {
                console.error(
                    "[ScreenSaver] 画像読み込み失敗:",
                    media.url
                );

                nextMedia();
            };

            stage.appendChild(img);

        }

        // ---------------------------------
        // 動画
        // ---------------------------------

        else if (media.type === "video") {

            const video = document.createElement("video");

            video.src = media.url;

            video.autoplay = true;

            video.muted = true;

            video.playsInline = true;

            video.preload = "auto";

            video.controls = false;

            // 再生終了で次へ
            video.addEventListener(
                "ended",
                nextMedia,
                { once: true }
            );

            // 読み込み失敗
            video.addEventListener(
                "error",
                () => {
                    console.error(
                        "[ScreenSaver] 動画読み込み失敗:",
                        media.url
                    );

                    nextMedia();
                },
                { once: true }
            );

            stage.appendChild(video);

            video.play().catch(error => {
                console.error(
                    "[ScreenSaver] 動画再生失敗:",
                    error
                );

                nextMedia();
            });

        }

        else {
            console.warn(
                "[ScreenSaver] 未対応の種類:",
                media.type
            );

            nextMedia();
        }
    }

    // =====================================
    // 無操作タイマーリセット
    // =====================================

    function resetScreensaverTimer(source = "user") {

        // 表示中なら解除
        hideScreensaver();

        // 以前のタイマーを削除
        clearTimeout(idleTimer);

        // 0秒から再カウント
        idleTimer = setTimeout(() => {
            console.log("!");
            showScreensaver();
            console.log("!!!");

        }, IDLE_TIME);

        console.log(
            `[ScreenSaver] タイマーリセット: ${source}`
        );
    }

    // Fully Kioskからも呼び出せるようにする
    window.resetScreensaverTimer = resetScreensaverTimer;

    // =====================================
    // ユーザー操作検知
    // =====================================

    const events = [
        "pointerdown",
        "pointermove",
        "keydown",
        "touchstart",
        "wheel"
    ];

    events.forEach(eventName => {

        document.addEventListener(
            eventName,
            () => {
                resetScreensaverTimer(eventName);
            },
            {
                passive: true,
                capture: true
            }
        );

    });

    // =====================================
    // 初期化
    // =====================================

    resetScreensaverTimer("initialization");

    console.log(
        "[ScreenSaver] 初期化完了",
        mediaList.length,
        "件"
    );

})();