(function () {
    let playRequested = false;

    function playHeroVideo() {
        const video =
            document.querySelector(".mediot_hero_video_clean") ||
            document.querySelector(".mediot_forced_hero_video") ||
            document.querySelector(".med_video_hero video");

        if (!video) {
            console.warn("MedIoT hero video not found");
            return;
        }

        video.muted = true;
        video.defaultMuted = true;
        video.loop = true;
        video.autoplay = true;
        video.playsInline = true;

        video.setAttribute("muted", "");
        video.setAttribute("autoplay", "");
        video.setAttribute("loop", "");
        video.setAttribute("playsinline", "");

        video.style.display = "block";
        video.style.visibility = "visible";
        video.style.opacity = "1";
        video.style.objectFit = "cover";

        if (!video.paused && video.currentTime > 0) {
            console.log("MedIoT hero video already playing", {
                currentTime: video.currentTime,
                duration: video.duration,
                readyState: video.readyState
            });
            return;
        }

        if (playRequested) {
            return;
        }

        playRequested = true;

        const attemptPlay = function () {
            const p = video.play();

            if (p && p.then) {
                p.then(function () {
                    console.log("MedIoT hero video playing", {
                        paused: video.paused,
                        currentTime: video.currentTime,
                        duration: video.duration,
                        readyState: video.readyState,
                        src: video.currentSrc
                    });
                }).catch(function (err) {
                    playRequested = false;
                    console.warn("MedIoT hero video play blocked:", err);
                });
            }
        };

        if (video.readyState >= 2) {
            attemptPlay();
        } else {
            video.addEventListener("canplay", attemptPlay, { once: true });
        }
    }

    document.addEventListener("DOMContentLoaded", playHeroVideo);
    window.addEventListener("load", playHeroVideo);
    setTimeout(playHeroVideo, 500);
})();
