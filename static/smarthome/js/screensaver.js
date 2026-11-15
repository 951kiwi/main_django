(() => {

    "use strict";

    // =====================================
    // 設定
    // =====================================

    const IDLE_TIME = 10 * 1000;

    const DEFAULT_IMAGE_DURATION = 10;

    // 同時に先読みする動画の数
    const MAX_VIDEO_PRELOAD = 1;

    // Fully Kiosk カメラプレビュー
    const CONTROL_CAMERA_PREVIEW = true;

    // =====================================
    // DOM
    // =====================================

    const screensaver = document.getElementById("screensaver");
    const stage = document.getElementById("screensaver-stage");
    const dataElement = document.getElementById("screensaver-data");

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

    if (!Array.isArray(mediaList)) {
        mediaList = [];
    }

    // =====================================
    // 状態管理
    // =====================================

    let currentIndex = 0;

    let idleTimer = null;
    let mediaTimer = null;

    let isActive = false;

    // Fullyカメラ設定の保存
    let originalCamPreview = null;

    // メディアキャッシュ
    const mediaCache = new Map();

    // =====================================
    // Fully Kiosk カメラ制御
    // =====================================

    function setCamPreview(enabled) {

        if (!CONTROL_CAMERA_PREVIEW) {
            return;
        }

        if (typeof fully === "undefined") {
            return;
        }

        try {
            fully.setBooleanSetting(
                "showCamPreview",
                enabled
            );

            console.log(
                "[ScreenSaver] カメラプレビュー:",
                enabled ? "ON" : "OFF"
            );

        } catch (error) {
            console.warn(
                "[ScreenSaver] カメラ設定変更失敗",
                error
            );
        }
    }

    function saveCameraSetting() {

        if (typeof fully === "undefined") {
            return;
        }

        try {
            originalCamPreview =
                fully.getBooleanSetting("showCamPreview");

            console.log(
                "[ScreenSaver] 元のカメラ設定:",
                originalCamPreview
            );

        } catch (error) {
            console.warn(
                "[ScreenSaver] カメラ設定取得失敗",
                error
            );
        }
    }

    // =====================================
    // キャッシュ準備
    // =====================================

    function preloadMedia() {

        let videoPreloadCount = 0;

        mediaList.forEach((media, index) => {

            if (!media.url || !media.type) {
                console.warn(
                    "[ScreenSaver] メディア情報不足:",
                    media
                );
                return;
            }

            if (mediaCache.has(media.url)) {
                return;
            }

            // ---------------------------------
            // 画像
            // ---------------------------------

            if (media.type === "image") {

                const img = new Image();

                const cacheItem = {
                    type: "image",
                    element: img,
                    loaded: false,
                    failed: false
                };

                mediaCache.set(media.url, cacheItem);

                img.onload = () => {
                    cacheItem.loaded = true;

                    console.log(
                        "[ScreenSaver] 画像キャッシュ完了:",
                        media.title
                    );
                };

                img.onerror = () => {
                    cacheItem.failed = true;

                    console.error(
                        "[ScreenSaver] 画像キャッシュ失敗:",
                        media.url
                    );
                };

                img.src = media.url;

            }

            // ---------------------------------
            // 動画
            // ---------------------------------

            else if (
                media.type === "video" &&
                videoPreloadCount < MAX_VIDEO_PRELOAD
            ) {

                const video = document.createElement("video");

                video.preload = "auto";
                video.muted = true;
                video.playsInline = true;
                video.src = media.url;

                const cacheItem = {
                    type: "video",
                    element: video,
                    loaded: false,
                    failed: false
                };

                mediaCache.set(media.url, cacheItem);

                video.addEventListener("canplay", () => {

                    cacheItem.loaded = true;

                    console.log(
                        "[ScreenSaver] 動画キャッシュ準備完了:",
                        media.title
                    );

                }, { once: true });

                video.addEventListener("error", () => {

                    cacheItem.failed = true;

                    console.error(
                        "[ScreenSaver] 動画キャッシュ失敗:",
                        media.url
                    );

                }, { once: true });

                videoPreloadCount++;

            }

            else if (media.type === "video") {

                // 後続動画は再生時に読み込む
                mediaCache.set(media.url, {
                    type: "video",
                    element: null,
                    loaded: false,
                    failed: false
                });

            }

        });

        console.log(
            "[ScreenSaver] キャッシュ開始:",
            mediaCache.size,
            "件"
        );
    }

    // =====================================
    // スクリーンセーバー表示
    // =====================================

    function showScreensaver() {

        if (isActive || mediaList.length === 0) {
            console.warn("[ScreenSaver] 起動できません", {
                isActive,
                mediaCount: mediaList.length
            });
            return;
        }

        isActive = true;

        // カメラプレビューをOFF
        setCamPreview(false);

        screensaver.classList.add("active");

        screensaver.setAttribute(
            "aria-hidden",
            "false"
        );

        console.log("[ScreenSaver] 表示開始");

        playCurrentMedia();
    }

    // =====================================
    // スクリーンセーバー解除
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

        // 再生中の動画を停止
        const video = stage.querySelector("video");

        if (video) {
            video.pause();
            video.removeAttribute("src");
            video.load();
        }

        stage.replaceChildren();

        // カメラ設定を復元
        if (originalCamPreview !== null) {
            setCamPreview(
                originalCamPreview === true ||
                originalCamPreview === "true"
            );
        }

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

            const cached = mediaCache.get(media.url);

            const img = new Image();

            img.alt = media.title || "";

            // キャッシュが読み込み済みなら再利用
            if (
                cached &&
                cached.type === "image" &&
                cached.loaded
            ) {
                img.src = cached.element.src;
            } else {
                img.src = media.url;
            }

            img.onload = () => {

                if (!isActive) {
                    return;
                }

                const duration = Math.max(
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

            const cached = mediaCache.get(media.url);

            // キャッシュ動画を再利用
            const video =
                cached &&
                cached.type === "video" &&
                cached.element
                    ? cached.element
                    : document.createElement("video");

            video.pause();

            video.removeAttribute("src");

            video.src = media.url;

            video.autoplay = true;
            video.muted = true;
            video.playsInline = true;
            video.preload = "auto";
            video.controls = false;

            video.onended = nextMedia;

            video.onerror = () => {

                console.error(
                    "[ScreenSaver] 動画読み込み失敗:",
                    media.url
                );

                nextMedia();

            };

            stage.appendChild(video);

            video.play().catch(error => {

                console.error(
                    "[ScreenSaver] 動画再生失敗:",
                    error
                );

                nextMedia();

            });

        }

        // ---------------------------------
        // 未対応
        // ---------------------------------

        else {

            console.warn(
                "[ScreenSaver] 未対応の種類:",
                media.type
            );

            nextMedia();

        }
    }

    // =====================================
    // 無操作タイマー
    // =====================================

    function resetScreensaverTimer(source = "user") {

        hideScreensaver();

        clearTimeout(idleTimer);

        idleTimer = setTimeout(() => {

            console.log("[ScreenSaver] 無操作時間経過");

            showScreensaver();

        }, IDLE_TIME);

        console.log(
            `[ScreenSaver] タイマーリセット: ${source}`
        );
    }

    // Fully Kioskから呼び出せるようにする
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

    saveCameraSetting();

    preloadMedia();

    resetScreensaverTimer("initialization");

    console.log(
        "[ScreenSaver] 初期化完了:",
        mediaList.length,
        "件"
    );

})();