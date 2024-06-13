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

    # 여기서 이미지를 처리합니다.
    # processed_img = <your_image_processing_function>(img)

    _, buffer = cv2.imencode('.jpg', img)
    encoded_img = base64.b64encode(buffer).decode('utf-8')

    return jsonify({'processedImage': encoded_img})



def save_video():
    file = request.files['video']
    file.save('videotest.webm')
    # file.save(request.get_json())
    return jsonify({'message': 'Video saved successfully'})