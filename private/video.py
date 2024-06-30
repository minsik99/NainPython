import cx_Oracle
import mediapipe as mp  # Import mediapipe
import cv2  # Import opencv
import time
import numpy as np
import videoDB as db
import fileLoad as fl
import os
import sys




def calculate_score(angle):
    if 170 <= angle <= 173:
        return 100
    elif 173 < angle <= 176 or 167 <= angle < 170:
        return 90
    elif 164 <= angle < 167 or 176 < angle <= 179:
        return 80
    elif 161 <= angle < 164 or 179 < angle <= 182:
        return 70
    elif 158 <= angle < 161 or 182 < angle <= 185:
        return 60
    else:
        return 50


def calculate_angle(a, b):
    a = np.array(a)
    b = np.array(b)
    radians = np.arctan2(b[1] - a[1], b[0] - a[0])
    angle = np.abs(radians * 180.0 / np.pi)

    return angle
def analysis_video(itvNo, processed_files):
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 모델 파일 경로를 설정합니다.
    model_path = os.path.abspath(os.path.join(current_dir, '..', 'pose_landmarker_lite.task'))
    model_path = os.path.normpath(model_path)  # 경로를 정규화합니다.

    # 경로 정보를 출력합니다.
    print(f"Current Directory: {current_dir}")
    print(f"Model Path: {model_path}")

    # 모델 파일이 존재하는지 확인합니다.
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    # 현재 디렉토리가 sys.path에 없으면 추가합니다.
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    mp_pose = mp.solutions.pose
    mp_holistic = mp.solutions.holistic

    with open(model_path, 'rb') as f:
        model_buffer = f.read()

    base_options = BaseOptions(model_asset_buffer=model_buffer)

    options = PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=VisionRunningMode.VIDEO
        )

    with PoseLandmarker.create_from_options(options) as landmarker:
        with mp_holistic.Holistic(
                static_image_mode=False,
                model_complexity=2,
                enable_segmentation=True,
                refine_face_landmarks=True) as holistic:

                video_data = fl.fileLoad(itvNo, processed_files)

                for video_path, cap, start_time in video_data:
                    angles = []
                    score = []
                    last_timestamp_s = -5
                    while True:
                        # 프레임 읽기
                        ret, frame = cap.read()
                        if not ret:
                            break

                        frame_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
                        frame_timestamp_s = frame_timestamp_ms / 1000


                        if frame_timestamp_s >= last_timestamp_s + 5:
                            last_timestamp_s = frame_timestamp_s

                            resize_frame = cv2.resize(frame, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
                            image = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2RGB)
                            image.flags.writeable = False

                            results = holistic.process(image)

                            image.flags.writeable = True
                            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

                            # 어깨 좌표 감지
                            try:
                                landmarks = results.pose_landmarks.landmark

                                # Get coordinates
                                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

                                # Calculate angleq
                                angle = calculate_angle(left_shoulder, right_shoulder)
                                angles.append(angle)

                                if angles:
                                    avg_angle = np.mean(angles)
                                    # print(f"5초 동안의 평균 어깨 각도: {avg_angle}")
                                    fscore = calculate_score(avg_angle)
                                    score.append(fscore)

                                    angles = []

                            except AttributeError:
                                print("랜드마크를 찾을 수 없습니다.")

                                pose_results = landmarker.detect_for_video(mp_image, frame_timestamp_s)

                                # print(f"Angle between shoulders: {angle}")

                                # Extract Pose landmarks
                                if hasattr(pose_results, 'pose_landmarks') and results.pose_landmarks:
                                    pose = results.pose_landmarks.landmark
                                    pose_row = list(np.array(
                                        [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in pose]).flatten());


                            except:
                                pass

                    answerNo = fl.extract_number_from_filename(video_path) + 1
                    processed_files.append(os.path.basename(video_path))
                    itv_type = 'POS'
                    db.insert_score(answerNo, itvNo, itv_type, np.mean(score))

                cap.release()
                end_time = time.time()  # 종료 시간 기록
                elapsed_time = end_time - start_time  # 소요 시간 계산
                print(f"{video_path} 처리 시간: {elapsed_time:.2f}초")

                cv2.destroyAllWindows()


