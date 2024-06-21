import cv2
from deepface import DeepFace
from collections import deque
import numpy as np

# 최근 N 프레임의 감정 저장
def emotion_analysis(frame):
    N = 5
    emotion_queue = deque(maxlen=N)
    emotion_result = list()

    try:
        # 감정 인식 수행 (enforce_detection=False)
        results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

        # 결과가 리스트일 경우 첫 번째 요소에 접근
        if isinstance(results, list):
            result = results[0]
        else:
            result = results

        # 인식된 감정을 큐에 추가
        dominant_emotion = result["dominant_emotion"]
        emotion_probabilities = result["emotion"]

        # 특정 감정만 큐에 추가
        if dominant_emotion in ["neutral", "happy", "sad", "surprise"]:
            emotion_queue.append((dominant_emotion, emotion_probabilities[dominant_emotion]))

        # 가장 빈번한 감정을 계산
        if emotion_queue:
            most_common_emotion = max(set(emotion_queue), key=emotion_queue.count)
            emotion_name, emotion_prob = most_common_emotion

            # 인식된 감정과 확률을 화면에 표시(테스트용)
            # cv2.putText(frame, f"Emotion: {emotion_name} ({emotion_prob:.2f})", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
            #             (0, 255, 0), 2, cv2.LINE_AA)
            emotion_result.append((emotion_name, emotion_prob))
    except Exception as e:
        print(f"Error: {e}")

    return emotion_result


