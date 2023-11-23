// custom.js
document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;
    const modeToggleBtn = document.getElementById('mode-toggle-btn');

    modeToggleBtn.addEventListener('click', function () {
        body.classList.toggle('dark-mode');
    });
});
