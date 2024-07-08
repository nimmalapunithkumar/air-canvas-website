const video_feed = document.getElementById('video_feed');
const paintCanvas = document.getElementById('paintCanvas');
const ctx = paintCanvas.getContext('2d');
let colorIndex = 0;

function changeColor(index) {
    colorIndex = index;
}

function clearCanvas() {
    ctx.clearRect(0, 0, paintCanvas.width, paintCanvas.height);
}

video_feed.onload = function() {
    setInterval(() => {
        ctx.drawImage(video_feed, 0, 0, paintCanvas.width, paintCanvas.height);
    }, 100);
};
