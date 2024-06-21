import cv2
import mediapipe as mp

# MediaPipe 솔루션 초기화
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

# 웹캠 초기화
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # 이미지 색상 변환 및 처리
    image_rgb = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image_rgb.flags.writeable = False
    results = face_mesh.process(image_rgb)

    # 이미지 다시 BGR로 변환
    image_rgb.flags.writeable = True
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # 홍채만 강조
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            for i in range(468, 478):  # 홍채의 랜드마크 인덱스
                x = int(face_landmarks.landmark[i].x * image.shape[1])
                y = int(face_landmarks.landmark[i].y * image.shape[0])
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

    # 결과 이미지 출력
    cv2.imshow('Iris Tracking', image)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
