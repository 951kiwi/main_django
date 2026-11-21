
(() => {
    "use strict";

    // =========================================
    // 設定
    // =========================================

    const IDLE_TIME = 10 * 1000;
    const DEFAULT_IMAGE_DURATION = 10;
    const ERROR_RETRY_DELAY = 5000;
    const FADE_DURATION = 300;

    // =========================================
    // DOM
    // =========================================

    const screensaver = document.getElementById("screensaver");
    const stage = document.getElementById("screensaver-stage");

    const dataElement =
        document.getElementById("screensaver-media-data") ||
        document.getElementById("screensaver-data");

    if (!screensaver || !stage || !dataElement) {
        console.error("スクリーンセイバーのDOMが見つかりません。");
        return;
    }

    // =========================================
    // メディアデータ取得
    // =========================================

    let mediaList = [];

    try {
        const rawData = JSON.parse(dataElement.textContent || "[]");

        mediaList = rawData
            .map(media => {
                const file = media.file;

                return {
                    id: media.id,
                    title: media.title || "",
                    type: String(
                        media.type || media.media_type || ""
                    ).toLowerCase(),

                    url:
                        media.url ||
                        (typeof file === "string" ? file : file?.url) ||
                        "",

                    duration:
                        Number(media.duration) > 0
                            ? Number(media.duration)
                            : DEFAULT_IMAGE_DURATION
                };
            })
            .filter(media =>
                media.url &&
                ["image", "video"].includes(media.type)
            );

    } catch (error) {
        console.error("メディアデータの読み込みに失敗:", error);
        mediaList = [];
    }

    // =========================================
    // 状態管理
    // =========================================

    let isActive = false;
    let currentElement = null;

    let idleTimer = null;
    let mediaTimer = null;

    let errorCount = 0;
    let destroyed = false;

    // ランダム再生
    let playOrder = [];
    let currentIndex = 0;
    let lastPlayedId = null;

    // 切り替え制御
    let isTransitioning = false;
    let transitionToken = 0;

    // =========================================
    // タイマー管理
    // =========================================

    function clearIdleTimer() {
        if (idleTimer !== null) {
            clearTimeout(idleTimer);
            idleTimer = null;
        }
    }

    function clearMediaTimer() {
        if (mediaTimer !== null) {
            clearTimeout(mediaTimer);
            mediaTimer = null;
        }
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // =========================================
    // ランダム再生
    // =========================================

    function shuffleMedia(list) {

        const shuffled = [...list];

        // Fisher-Yates シャッフル
        for (let i = shuffled.length - 1; i > 0; i--) {

            const j = Math.floor(Math.random() * (i + 1));

            [shuffled[i], shuffled[j]] =
                [shuffled[j], shuffled[i]];
        }

        // 前回の最後と次回の最初が同じになるのを防止
        if (
            shuffled.length > 1 &&
            lastPlayedId !== null &&
            shuffled[0].id === lastPlayedId
        ) {
            const swapIndex = 1 + Math.floor(
                Math.random() * (shuffled.length - 1)
            );

            [shuffled[0], shuffled[swapIndex]] =
                [shuffled[swapIndex], shuffled[0]];
        }

        return shuffled;
    }

    function initializePlayOrder() {
        playOrder = shuffleMedia(mediaList);
        currentIndex = 0;
    }

    function getNextMedia() {

        if (currentIndex >= playOrder.length) {
            initializePlayOrder();
        }

        const media = playOrder[currentIndex];

        currentIndex++;

        return media;
    }

    // =========================================
    // メディア解放
    // =========================================

    function releaseCurrentMedia() {

        clearMediaTimer();

        if (!currentElement) {
            stage.replaceChildren();
            return;
        }

        const element = currentElement;
        currentElement = null;

        if (element.tagName === "VIDEO") {

            element.pause();

            element.removeAttribute("src");

            element.querySelectorAll("source").forEach(source => {
                source.removeAttribute("src");
            });

            element.load();
        }

        if (element.tagName === "IMG") {
            element.removeAttribute("src");
            element.removeAttribute("srcset");
        }

        element.remove();

        stage.replaceChildren();
    }

    // =========================================
    // フェードアウト
    // =========================================

    async function fadeOutCurrent() {

        const element = currentElement;

        if (!element) return;

        element.style.transition =
            `opacity ${FADE_DURATION}ms ease`;

        element.style.opacity = "0";

        await sleep(FADE_DURATION);
    }

    // =========================================
    // フェードイン
    // =========================================

    function fadeInElement(element) {

        element.style.opacity = "0";

        element.style.transition =
            `opacity ${FADE_DURATION}ms ease`;

        stage.appendChild(element);

        // 描画を確定してから透明度を変更
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {

                if (
                    currentElement === element &&
                    isActive
                ) {
                    element.style.opacity = "1";
                }
            });
        });
    }

    // =========================================
    // スクリーンセイバー表示
    // =========================================

    function showScreensaver() {

        if (
            destroyed ||
            isActive ||
            mediaList.length === 0 ||
            document.hidden
        ) {
            return;
        }

        clearIdleTimer();

        isActive = true;

        errorCount = 0;
        lastPlayedId = null;

        initializePlayOrder();

        screensaver.classList.add("active");

        playNextMedia();
    }

    // =========================================
    // スクリーンセイバー終了
    // =========================================

    function hideScreensaver() {

        clearIdleTimer();

        // 非同期切り替え処理を無効化
        transitionToken++;

        isTransitioning = false;

        if (isActive) {
            isActive = false;
            screensaver.classList.remove("active");
        }

        releaseCurrentMedia();

        errorCount = 0;

        if (!destroyed && !document.hidden) {
            startIdleTimer();
        }
    }

    // =========================================
    // 次のメディアへ
    // =========================================

    async function playNextMedia() {

        if (
            !isActive ||
            destroyed ||
            mediaList.length === 0 ||
            isTransitioning
        ) {
            return;
        }

        isTransitioning = true;

        const token = ++transitionToken;

        try {

            // 2枚目以降は前のメディアをフェードアウト
            if (currentElement) {
                await fadeOutCurrent();
            }

            if (
                !isActive ||
                destroyed ||
                token !== transitionToken
            ) {
                return;
            }

            // 前のメディアを解放
            releaseCurrentMedia();

            const media = getNextMedia();

            if (!media) return;

            lastPlayedId = media.id;

            isTransitioning = false;

            if (media.type === "image") {
                playImage(media);
            } else if (media.type === "video") {
                playVideo(media);
            } else {
                handleMediaError();
            }

        } finally {

            if (token === transitionToken) {
                isTransitioning = false;
            }
        }
    }

    // =========================================
    // 画像再生
    // =========================================

    function playImage(media) {

        if (!isActive) return;

        const img = document.createElement("img");

        currentElement = img;

        img.alt = media.title;
        img.decoding = "async";
        img.draggable = false;

        img.addEventListener("load", () => {

            if (!isActive || currentElement !== img) {
                return;
            }

            errorCount = 0;

            // 画像読み込み後にフェードイン
            fadeInElement(img);

            clearMediaTimer();

            mediaTimer = setTimeout(() => {

                if (
                    currentElement === img &&
                    isActive
                ) {
                    playNextMedia();
                }

            }, media.duration * 1000);

        }, { once: true });

        img.addEventListener("error", () => {

            if (currentElement === img) {
                handleMediaError();
            }

        }, { once: true });

        img.src = media.url;
    }

    // =========================================
    // 動画再生
    // =========================================

    function playVideo(media) {

        if (!isActive) return;

        const video = document.createElement("video");

        currentElement = video;

        video.autoplay = false;
        video.muted = true;
        video.playsInline = true;
        video.controls = false;
        video.loop = false;
        video.preload = "metadata";
        video.disablePictureInPicture = true;

        video.addEventListener("loadeddata", async () => {

            if (!isActive || currentElement !== video) {
                return;
            }

            errorCount = 0;

            // 動画をフェードイン
            fadeInElement(video);

            try {

                await video.play();

            } catch (error) {

                if (
                    currentElement !== video ||
                    !isActive
                ) {
                    return;
                }

                console.warn("動画の再生に失敗:", media.url, error);

                handleMediaError();
            }

        }, { once: true });

        video.addEventListener("ended", () => {

            if (currentElement === video) {
                playNextMedia();
            }

        });

        video.addEventListener("error", () => {

            if (currentElement === video) {
                handleMediaError();
            }

        });

        video.src = media.url;

        video.load();
    }

    // =========================================
    // メディアエラー処理
    // =========================================

    function handleMediaError() {

        if (!isActive || destroyed) return;

        errorCount++;

        // 全メディアが連続して失敗した場合
        if (errorCount >= mediaList.length) {

            errorCount = 0;

            releaseCurrentMedia();

            clearMediaTimer();

            mediaTimer = setTimeout(() => {

                if (isActive) {
                    playNextMedia();
                }

            }, ERROR_RETRY_DELAY);

            return;
        }

        // 次のメディアへ
        playNextMedia();
    }

    // =========================================
    // 操作がない時間を計測
    // =========================================

    function startIdleTimer() {

        clearIdleTimer();

        if (
            destroyed ||
            document.hidden ||
            isActive ||
            mediaList.length === 0
        ) {
            return;
        }

        idleTimer = setTimeout(() => {

            idleTimer = null;

            showScreensaver();

        }, IDLE_TIME);
    }

    // =========================================
    // ユーザー操作検知
    // =========================================

    function handleUserActivity() {

        if (destroyed || document.hidden) {
            return;
        }

        if (isActive) {
            hideScreensaver();
        } else {
            startIdleTimer();
        }
    }

    const activityEvents = [
        "pointerdown",
        "pointermove",
        "keydown",
        "wheel",
        "scroll",
        "touchstart",
        "click"
    ];

    activityEvents.forEach(eventName => {

        document.addEventListener(
            eventName,
            handleUserActivity,
            { passive: true }
        );

    });

    // =========================================
    // タブの表示・非表示
    // =========================================

    function handleVisibilityChange() {

        if (document.hidden) {

            clearIdleTimer();

            transitionToken++;
            isTransitioning = false;

            if (isActive) {
                isActive = false;
                screensaver.classList.remove("active");
            }

            releaseCurrentMedia();

            errorCount = 0;

        } else {

            startIdleTimer();
        }
    }

    document.addEventListener(
        "visibilitychange",
        handleVisibilityChange
    );

    // =========================================
    // ページ終了時の解放
    // =========================================

    function handlePageHide() {

        destroyed = true;

        transitionToken++;

        isTransitioning = false;

        clearIdleTimer();
        clearMediaTimer();

        isActive = false;

        screensaver.classList.remove("active");

        releaseCurrentMedia();
    }

    window.addEventListener("pagehide", handlePageHide);

    // =========================================
    // 初期化
    // =========================================

    releaseCurrentMedia();

    startIdleTimer();

    console.log("スクリーンセイバー初期化完了", {
        mediaCount: mediaList.length,
        idleTime: IDLE_TIME,
        fadeDuration: FADE_DURATION,
        randomPlayback: true
    });
    // Fully Kiosk から呼び出せるように公開
        window.hideScreensaver = hideScreensaver;

        // 初期化
        releaseCurrentMedia();

        startIdleTimer();
})();
