import mediapipe as mp  # Import mediapipe
from mediapipe.python.solutions import holistic
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2  # Import opencv
import time
import csv
import os
import numpy as np
import pandas as pd
import pickle
def analysis_video(ivtNo):
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    mp_face_detection = mp.solutions.face_detection
    mp_face_mesh = mp.solutions.face_mesh
    mp_pose = mp.solutions.pose
    mp_holistic = mp.solutions.holistic
    mp_drawing = mp.solutions.drawing_utils

    model_path = './pose_landmarker_lite.task'

    def calculate_angle(a, b):
        a = np.array(a)
        b = np.array(b)

        radians = np.arctan2(b[1] - a[1], b[0] - a[0])
        angle = np.abs(radians * 180.0 / np.pi)

        return angle

    def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        print('pose landmarker result: {}'.format(result))

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO,
        result_callback=print_result)

    with PoseLandmarker.create_from_options(options) as landmarker:
        warning = False
        count = 0
        good_count = 0
        stretch_count = 0
        stand_count = 0
        start = time.gmtime(time.time())  # 시작 시간 저장

        with mp_holistic.Holistic(
                static_image_mode=True,
                model_complexity=2,
                enable_segmentation=True,
                refine_face_landmarks=True) as holistic:


                frame = cv2.imread(ivtNo + '.webm', cv2.IMREAD_GRAYSCALE)
                resize_frame = cv2.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
                # Recolor Feed
                image = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # mage = mp.Image(image_format=mp.ImageFormat.SRGB, data=resize_frame)

                face_mesh = mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5,
                )

                # Make Detections
                results = holistic.process(image)
                result2 = face_mesh.process(image)

                # Recolor image back to BGR for rendering
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

                # 1. Draw face landmarks
                if hasattr(result2, 'multi_face_landmarks') and result2.multi_face_landmarks:
                    if result2.multi_face_landmarks:
                        for face_landmarks in result2.multi_face_landmarks:
                            left_eye_indices = [133, 173, 157, 158, 159, 160, 161, 246]
                            right_eye_indices = [362, 398, 384, 385, 386, 387, 388, 468]
                            right_eye_landmarks = [face_landmarks.landmark[i] for i in right_eye_indices]
                            left_eye_landmarks = [face_landmarks.landmark[i] for i in left_eye_indices]

                            # mouth_indices = [0, 13, 14, 17, 37, 39, 40, 61, 78, 80, 81, 82, 84, 87, 88, 91, 95, 146, 178,
                            #                  181, 185, 191, 267, 269, 270, 291, 308, 310, 311, 312, 314, 317, 318, 321, 324]
                            mouth_indices = [78, 308]
                            mouth_landmarks = [face_landmarks.landmark[i] for i in mouth_indices]

                            x1 = int(face_landmarks.landmark[158].x * image.shape[1])
                            y1 = int(face_landmarks.landmark[158].y * image.shape[0])
                            x2 = int(face_landmarks.landmark[145].x * image.shape[1])
                            y2 = int(face_landmarks.landmark[145].y * image.shape[0])
                            midpoint = ((x1 + x2) // 2, (y1 + y2) // 2)

                            # Check the color of the midpoint
                            if not np.array_equal(image[midpoint[1], midpoint[0]], [255, 255, 255]):
                                cv2.putText(image, 'Great!!',
                                            (450, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)

                            # 랜드마크를 시각화하거나 추가 처리를 할 수 있습니다.
                            # 예를 들어, 랜드마크를 이미지 위에 그리기:
                            # for landmark in left_eye_landmarks + right_eye_landmarks + mouth_landmarks:
                            #     x = int(landmark.x * image.shape[1])
                            #     y = int(landmark.y * image.shape[0])
                            #     cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

                # 4. Pose Detections
                if hasattr(results, 'pose_landmarks') and results.pose_landmarks:
                    CUSTOM_CONNECTIONS = [
                        (mp_holistic.PoseLandmark.LEFT_SHOULDER, mp_holistic.PoseLandmark.RIGHT_SHOULDER)]

                    mp_drawing.draw_landmarks(image, results.pose_landmarks,
                                              CUSTOM_CONNECTIONS,
                                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=1,
                                                                     circle_radius=1),
                                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=1, circle_radius=1)
                                              )
                # Export coordinatesqq
                try:
                    if hasattr(results, 'pose_landmarks') and results.pose_landmarks:
                        landmarks = results.pose_landmarks.landmark

                    # Get coordinates
                    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                      landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

                    # Calculate angleq
                    angle = calculate_angle(left_shoulder, right_shoulder)

                    # Extract Pose landmarks
                    if hasattr(results, 'pose_landmarks') and results.pose_landmarks:
                        pose = results.pose_landmarks.landmark
                        pose_row = list(np.array(
                            [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten())

                    # Extract Face landmarks
                    if hasattr(result2, 'multi_face_landmarks') and result2.multi_face_landmarks:
                        face = result2.multi_face_landmarks.landmark
                        face_row = list(np.array(
                            [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in face]).flatten())

                    # Concate rows
                    row = pose_row + face_row

                    with open(file='./body_language.pkl', mode='rb') as f:
                        model = pickle.load(f)
                    # Make Detections
                    X = pd.DataFrame([row])
                    body_language_class = model.predict(X)[0]
                    body_language_prob = model.predict_proba(X)[0]

                    # Get status box
                    cv2.rectangle(image, (0, 0), (1000, 80), (128, 128, 128), -1)

                    # Curl counter logic
                    if angle < 175 or body_language_class.split(' ')[0] == 'Bad':
                        count = count + 1
                        good_count = 0

                    elif angle >= 175:
                        good_count = good_count + 1

                    # Time
                    now = time.gmtime(time.time())

                    cv2.putText(image, 'Time',
                                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
                    hour = now.tm_hour - start.tm_hour
                    minutes = abs(now.tm_min - start.tm_min)
                    cv2.putText(image, str(hour) + ' : ' + str(minutes),
                                (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    # Display Probability
                    cv2.putText(image, str(round(body_language_prob[np.argmax(body_language_prob)], 2))
                                , (280, 65), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    cv2.putText(image, str(round(angle, 2))
                                , (850, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

                except:
                    pass

                cv2.imshow('Raw Webcam Feed', image)
                frame_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
                landmarker.detect_async(mp_image, frame_timestamp_ms)






