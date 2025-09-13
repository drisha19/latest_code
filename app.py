from flask import Flask, render_template, Response, request
import cv2
from estimator import HeadPoseEstimator
import openai  # pip install openai
from flask import Flask, render_template, Response, request, jsonify
# ...existing code...


app = Flask(__name__)
estimator = HeadPoseEstimator()
direction = "0.5,0.5,0"

def gen_frames():
    global direction
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        direction = estimator.get_direction(frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/generate_options', methods=['POST'])
def generate_options():
    question = request.json['question']
    openai.api_key = 'your_openai_key_here'

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You assist non-verbal patients with answer choices."},
            {"role": "user", "content": question}
        ]
    )
    full_text = completion['choices'][0]['message']['content']
    options = full_text.strip().split('\n')[:4]  # get 4 lines

    return jsonify({'options': options})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/direction')
def get_direction():
    return direction

@app.route('/button_clicked', methods=['POST'])
def button_clicked():
    data = request.json
    print(f"[PYTHON] Button clicked: {data['button']}")
    return 'OK', 200

@app.route('/get_direction')
def get_direction_api():  # renamed to avoid conflict
    global direction
    return {"direction": direction}


if __name__ == '__main__':
    app.run(debug=True)