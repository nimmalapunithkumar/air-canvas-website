from flask import Flask, render_template, Response
import cv2
import numpy as np
from collections import deque
from HandTrackingModule import handDetector
from detection import CharacterDetector

app = Flask(__name__)

# Initialize OpenCV variables
cap = cv2.VideoCapture(0)
detector = handDetector(detectionCon=0.75)
det = CharacterDetector(loadFile="model_hand.h5")

# Default variables for drawing
tipIds = [4, 8, 12, 16, 20]
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
vpoints = [deque(maxlen=1024)]
black_index = 0
green_index = 0
red_index = 0
voilet_index = 0
colors = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
colorIndex = 0
paintWindow = np.zeros((471, 636, 3)) + 255

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        img = detector.findHands(frame)
        lmList = detector.findPosition(img, draw=False)
        fingers = []

        if len(lmList) != 0:
            if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            totalFingers = fingers.count(1)

            if totalFingers == 1:
                lst = lmList[tipIds[fingers.index(1)]]
                x, y = lst[1], lst[2]

                if x <= 60:
                    if 70 <= y <= 110:
                        clear_canvas()
                    elif 120 <= y <= 160:
                        change_color(0)  # Black
                    elif 170 <= y <= 210:
                        change_color(1)  # Red
                    elif 220 <= y <= 260:
                        change_color(2)  # Green
                    elif 270 <= y <= 310:
                        change_color(3)  # Blue
                elif 520 < x < 630 and 1 < y < 65:
                    cv2.imwrite("static/img/new.jpg", paintWindow)
                    prediction = det.predict("static/img/new.jpg")
                    print(prediction)

                else:
                    draw_on_canvas(x, y)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def clear_canvas():
    global bpoints, gpoints, rpoints, vpoints, black_index, green_index, red_index, voilet_index, paintWindow
    bpoints = [deque(maxlen=512)]
    gpoints = [deque(maxlen=512)]
    rpoints = [deque(maxlen=512)]
    vpoints = [deque(maxlen=512)]
    black_index = 0
    green_index = 0
    red_index = 0
    voilet_index = 0
    paintWindow = np.zeros((471, 636, 3)) + 255

def change_color(index):
    global colorIndex
    colorIndex = index

def draw_on_canvas(x, y):
    global colorIndex, bpoints, vpoints, gpoints, rpoints, black_index, voilet_index, green_index, red_index, paintWindow
    if colorIndex == 0:
        bpoints[black_index].appendleft((x, y))
    elif colorIndex == 1:
        vpoints[voilet_index].appendleft((x, y))
    elif colorIndex == 2:
        gpoints[green_index].appendleft((x, y))
    elif colorIndex == 3:
        rpoints[red_index].appendleft((x, y))

    points = [bpoints, vpoints, gpoints, rpoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 20)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
