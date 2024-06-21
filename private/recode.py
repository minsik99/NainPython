import requests
import base64
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS


def start():
    data = request.get_json()
    frame_data = data['frame']
    frame = base64.b64decode(frame_data.split(',')[1])
    np_frame = np.frombuffer(frame, dtype=np.uint8)
    img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

    _, buffer = cv2.imencode('.jpg', img)
    encoded_img = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'processedImage': encoded_img})


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
def save_video():
    file = request.files['video']
    file.save('videotest.webm')
    # file.save(request.get_json())
    return jsonify({'message': 'Video saved successfully'})