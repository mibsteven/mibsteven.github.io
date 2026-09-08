// Pause the hidden language panel so switching languages never layers audio.
document.addEventListener('languagechange', () => {
    document.querySelectorAll('.mansion-page video').forEach(video => {
        if (!video.closest('[data-lang-panel]').classList.contains('is-active')) {
            video.pause();
        }
    });
});
