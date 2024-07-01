import cv2
import mediapipe as mp
import fileLoad as fl
import numpy as np
import videoDB as bdb
import os
def calculate_angle(point1, point2):
    # 두 점 사이의 각도를 계산하는 함수
    delta_x = point2[0] - point1[0]
    delta_y = point2[1] - point1[1]
    angle = np.arctan2(delta_y, delta_x)
    return angle

def detect_gaze(landmarks):
    # 홍채와 코의 좌표 추출
    nose_tip = landmarks[1]  # 코의 끝 부분
    left_eye_center = landmarks[468]  # 왼쪽 눈 중심
    right_eye_center = landmarks[473]  # 오른쪽 눈 중심

    # 좌표 변환
    left_eye_coords = (left_eye_center.x, left_eye_center.y)
    right_eye_coords = (right_eye_center.x, right_eye_center.y)
    nose_coords = (nose_tip.x, nose_tip.y)

    # 각도 계산
    left_gaze_angle = np.arctan2(left_eye_coords[1] - nose_coords[1], left_eye_coords[0] - nose_coords[0])
    right_gaze_angle = np.arctan2(right_eye_coords[1] - nose_coords[1], right_eye_coords[0] - nose_coords[0])

    return left_gaze_angle, right_gaze_angle



def calculate_score(mean_angles, std_angles, gaze_angles):
    score = 100
    threshold = 0.4  # 표준편차의 배수로 조정 가능

    for i in range(len(gaze_angles)):
        if abs(gaze_angles[i] - mean_angles[i]) > threshold * std_angles[i]:
            score -= 15  # 기준을 벗어날 경우 점수 차감

    return max(score, 0)  # 점수는 최소 0

# MediaPipe 솔루션 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# 웹캠 초기화
def eye_detect(itvNo, processed_files, conn):
    # MediaPipe 솔루션 초기화
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

    # 동영상 파일 로드
    video_data = fl.fileLoad(itvNo, processed_files)
    for video_path, cap, start_time in video_data:
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

                # 이미지 색상 변환 및 처리
                image_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False
                results = face_mesh.process(image_rgb)

                # 이미지 다시 BGR로 변환
                image_rgb.flags.writeable = True
                image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                try:
                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            # for i in range(468, 478):  # 홍채의 랜드마크 인덱스
                            #     x = int(face_landmarks.landmark[i].x * image.shape[1])
                            #     y = int(face_landmarks.landmark[i].y * image.shape[0])
                            #     cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

                            left_gaze_angle, right_gaze_angle = detect_gaze(face_landmarks.landmark)
                            print(left_gaze_angle, right_gaze_angle)
                            gaze_angles = np.degrees([left_gaze_angle, right_gaze_angle])

                            mean_angles = np.array([-122.10331417470963, -64.29518894536458])
                            std_angles = np.array([2.15753006, 5.9673896])
                            current_score = calculate_score(mean_angles, std_angles, gaze_angles)

                            score.append(current_score)
                            processed_files.append(os.path.basename(video_path))


                except AttributeError:
                    print("랜드마크를 찾을 수 없습니다.")

        # 평균 점수 계산 후 데이터베이스에 저장
        if score:
            answerNo = fl.extract_number_from_filename(video_path) + 1
            itv_type = 'EYE'
            bdb.insert_score(answerNo, itvNo, itv_type, np.mean(score), conn)

        cap.release()

if __name__ == '__main__':
    eye_detect(1040)