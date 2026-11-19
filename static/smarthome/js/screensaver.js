
(() => {
    "use strict";

    // =========================================
    // 設定
    // =========================================

    const IDLE_TIME = 10 * 1000;           // 起動までの待機時間
    const DEFAULT_IMAGE_DURATION = 10;     // 画像の標準表示秒数
    const ERROR_RETRY_DELAY = 5000;        // 全メディア失敗時の待機時間

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
            .map((media) => {
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
            .filter((media) => {
                return (
                    media.url &&
                    ["image", "video"].includes(media.type)
                );
            });

    } catch (error) {
        console.error("メディアデータの読み込みに失敗:", error);
        mediaList = [];
    }

    // =========================================
    // 状態管理
    // =========================================

    let isActive = false;

    let currentIndex = 0;

    let currentElement = null;

    let idleTimer = null;

    let mediaTimer = null;

    let errorCount = 0;

    let destroyed = false;

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

        // 動画の完全停止・読み込み解除
        if (element.tagName === "VIDEO") {

            element.pause();

            element.removeAttribute("src");

            element.querySelectorAll("source").forEach((source) => {
                source.removeAttribute("src");
            });

            element.load();
        }

        // 画像の参照解除
        if (element.tagName === "IMG") {

            element.removeAttribute("src");
            element.removeAttribute("srcset");
        }

        // DOMから削除
        element.remove();

        // ステージ内の残存要素も削除
        stage.replaceChildren();
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

        currentIndex = 0;

        errorCount = 0;

        screensaver.classList.add("active");

        playNextMedia();
    }

    // =========================================
    // スクリーンセイバー終了
    // =========================================

    function hideScreensaver() {

        clearIdleTimer();

        if (isActive) {
            isActive = false;

            screensaver.classList.remove("active");
        }

        // メディアを必ず解放
        releaseCurrentMedia();

        errorCount = 0;

        if (!destroyed && !document.hidden) {
            startIdleTimer();
        }
    }

    // =========================================
    // 次のメディアへ
    // =========================================

    function playNextMedia() {

        if (!isActive || destroyed || mediaList.length === 0) {
            return;
        }

        // 前の画像・動画を解放
        releaseCurrentMedia();

        // 全メディアを一周した場合
        if (currentIndex >= mediaList.length) {
            currentIndex = 0;
        }

        const media = mediaList[currentIndex];

        currentIndex++;

        if (media.type === "image") {
            playImage(media);
        } else if (media.type === "video") {
            playVideo(media);
        } else {
            handleMediaError();
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

            clearMediaTimer();

            mediaTimer = setTimeout(() => {

                if (currentElement === img) {
                    playNextMedia();
                }

            }, media.duration * 1000);

        }, { once: true });

        img.addEventListener("error", () => {

            if (currentElement === img) {
                handleMediaError();
            }

        }, { once: true });

        stage.appendChild(img);

        img.src = media.url;
    }

    // =========================================
    // 動画再生
    // =========================================

    function playVideo(media) {

        if (!isActive) return;

        const video = document.createElement("video");

        currentElement = video;

        video.autoplay = true;

        video.muted = true;

        video.playsInline = true;

        video.controls = false;

        video.loop = false;

        video.preload = "metadata";

        video.disablePictureInPicture = true;

        video.addEventListener("playing", () => {

            if (currentElement === video) {
                errorCount = 0;
            }

        });

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

        stage.appendChild(video);

        video.src = media.url;

        video.load();

        const playPromise = video.play();

        if (playPromise !== undefined) {

            playPromise.catch((error) => {

                if (currentElement !== video || !isActive) {
                    return;
                }

                console.warn("動画の再生に失敗:", media.url, error);

                handleMediaError();
            });
        }
    }

    // =========================================
    // メディアエラー処理
    // =========================================

    function handleMediaError() {

        if (!isActive) return;

        errorCount++;

        releaseCurrentMedia();

        // 全メディアが連続して失敗した場合
        if (errorCount >= mediaList.length) {

            errorCount = 0;

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

    activityEvents.forEach((eventName) => {

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
        defaultImageDuration: DEFAULT_IMAGE_DURATION
    });

})();
