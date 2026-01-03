from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
from picamera2 import Picamera2
from estimator import HeadPoseEstimator
import openai

# ------------------ Flask App ------------------
app = Flask(__name__)

# ------------------ Camera Setup ------------------
cam = Picamera2()
WIDTH, HEIGHT = 640, 480
MIDDLE = (WIDTH // 2, HEIGHT // 2)

cam.configure(
    cam.create_video_configuration(
        main={"format": "RGB888", "size": (WIDTH, HEIGHT)}
    )
)
cam.start()

# ------------------ Head Pose Estimator ------------------
estimator = HeadPoseEstimator()
direction = "0.5,0.5,0"

# ------------------ Video Generator ------------------
def gen_frames():
    global direction
    while True:
        frame = cam.capture_array()

        # Get head direction
        direction = estimator.get_direction(frame)

        # Draw center point (optional)
        cv2.circle(frame, MIDDLE, 10, (255, 0, 255), -1)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ------------------ Routes ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_direction')
def get_direction_api():
    return jsonify({"direction": direction})

@app.route('/button_clicked', methods=['POST'])
def button_clicked():
    data = request.json
    print(f"[PYTHON] Button clicked: {data['button']}")
    return 'OK', 200

# ------------------ LLM Options Generator ------------------
@app.route('/generate_options', methods=['POST'])
def generate_options():
    question = request.json['question']

    openai.api_key = "YOUR_OPENAI_KEY"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You assist non-verbal patients with answer choices."},
            {"role": "user", "content": question}
        ]
    )

    full_text = completion['choices'][0]['message']['content']
    options = full_text.strip().split('\n')[:4]

    return jsonify({"options": options})

# ------------------ Run Server ------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
