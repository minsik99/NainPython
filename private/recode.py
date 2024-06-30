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
def analyze_video(itvNo):
    # 현재 스크립트 파일의 디렉토리를 가져옵니다.

    processed_files = []
    video.analysis_video(itvNo, processed_files)
    processed_files.clear()
    eye.eye_detect(itvNo, processed_files)
    processed_files.clear()
    emotion.emotion_analysis(itvNo, processed_files)


def sanitize_filename(filename):
    return re.sub(r'[^a-zA-Z0-9_\-]', '', filename)

def save_video(file, itvNo):
    upload_folder = sanitize_filename(str(itvNo))
    upload_filename = file.filename

    # 폴더가 존재하지 않는 경우 생성
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # 파일 저장 경로 설정
    file_path = os.path.join(upload_folder, upload_filename)

    # 파일 저장
    file.save(file_path)

    already_analyzed = analyze_video(itvNo)

    # 이미 분석된 파일이면 삭제
    if already_analyzed:
        os.remove(file_path)
        print(f"Deleted already analyzed file: {file_path}")

    return file.filename

def video_feed():
    return Response(start_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
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


if '__main__' == __name__:
    analyze_video(1040)