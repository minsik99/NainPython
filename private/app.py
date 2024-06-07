import os
from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from flask_cors import CORS


app = Flask(__name__)
# http://localhost:3000 이후 리액트 서버구축시 localhost 변경하면됨
# http://127.0.0.1 입력시 리액트랑 연동되는 형식이므로 플라스크 위치의 ip 입력
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1", "http://localhost:3000"]}})

# 절대 경로로 변경
base_dir = os.path.dirname(os.path.abspath(__file__))
# model = os.path.join(base_dir, '..', 'dnnface', 'res10_300x300_ssd_iter_140000_fp16.caffemodel')
# config = os.path.join(base_dir, '..', 'dnnface', 'deploy.prototxt')
# net = cv2.dnn.readNet(model, config)


@app.route('/')
def hello_world():
    return 'Hello, World!'


# @app.route('/data', methods=['POST'])
# def data():
#     frame_data = request.json['frame']
#     _, encoded_image = frame_data.split(',')
#     frame = np.frombuffer(base64.b64decode(encoded_image), dtype=np.uint8)
#     frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
#
#     blob = cv2.dnn.blobFromImage(frame, 1, (300, 300), (104, 177, 123))
#     net.setInput(blob)
#     detect = net.forward()
#
#     (h, w) = frame.shape[:2]
#     detect = detect[0, 0, :, :]
#
#     for i in range(detect.shape[0]):
#         confidence = detect[i, 2]
#         if confidence < 0.5:
#             break
#
#         x1 = int(detect[i, 3] * w)
#         y1 = int(detect[i, 4] * h)
#         x2 = int(detect[i, 5] * w)
#         y2 = int(detect[i, 6] * h)
#
#         cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0))
#
#     _, buffer = cv2.imencode('.jpg', frame)
#     processed_image = base64.b64encode(buffer).decode('utf-8')
#
#     return jsonify({'processed_image': processed_image})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
