import requests
import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import re
import video
import eye
import sys
import emotion
import voice
import connection.dbConnectTemplate as dbtemp
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
CORS(app)

def analyze_video_async(itvNo):
    conn = dbtemp.connect()
    processed_files = []
    video.analysis_video(itvNo, processed_files, conn)
    processed_files.clear()
    eye.eye_detect(itvNo, processed_files, conn)
    processed_files.clear()
    emotion.emotion_analysis(itvNo, processed_files, conn)
    dbtemp.close(conn)

def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_\-]', '', filename)

def save_video(file, itvNo, qNo):
    upload_folder = sanitize_filename(str(itvNo))
    upload_filename = file.filename

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_path = os.path.join(upload_folder, upload_filename)
    file.save(file_path)

    # ThreadPoolExecutor를 사용하여 병렬로 처리
    with ThreadPoolExecutor() as executor:
        future1 = executor.submit(voice.voice_analysis, itvNo, qNo, upload_filename)
        future2 = executor.submit(analyze_video_async, itvNo)

        # 결과를 기다리지 않고 진행하고자 할 경우 아래와 같이 future 객체 사용
        # print(future1.result())
        # print(future2.result())

    return file.filename

def video_feed():
    return Response(start_video(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_video():
    cap = cv2.VideoCapture(0)  # 웹캠 사용 (또는 동영상 파일 경로)

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def start():
    data = request.get_json()
    frame_data = data['frame']
    frame = base64.b64decode(frame_data.split(',')[1])
    np_frame = np.frombuffer(frame, dtype=np.uint8)
    img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

    _, buffer = cv2.imencode('.jpg', img)
    encoded_img = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'processedImage': encoded_img})

if __name__ == '__main__':
    app.run(debug=True)
