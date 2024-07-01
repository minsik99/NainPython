import cv2
from deepface import DeepFace
from collections import deque, defaultdict
import numpy as np
import fileLoad as fl
import time
import os
import videoDB as vdb
# 최근 N 프레임의 감정 저장
def emotion_analysis(itvNo, processed_files, conn):

    video_data = fl.fileLoad(itvNo, processed_files)
    for video_path, cap, start_time in video_data:

        last_timestamp_s = -10
        N = 5
        emotion_queue = deque(maxlen=N)
        emotion_result = []
        while True:
            # 프레임 읽기
            ret, frame = cap.read()
            if not ret:
                break

            frame_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
            frame_timestamp_s = frame_timestamp_ms / 1000

            if frame_timestamp_s >= last_timestamp_s + 10:
                last_timestamp_s = frame_timestamp_s

                try:
                    # 감정 인식 수행 (enforce_detection=False)
                    results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

                    # 결과가 리스트일 경우 첫 번째 요소에 접근
                    if isinstance(results, list):
                        result = results[0]
                    else:
                        result = results

                    emotion_results = defaultdict(list)

                    # 인식된 감정을 큐에 추가
                    dominant_emotion = result["dominant_emotion"]
                    emotion_probabilities = result["emotion"]

                    # 특정 감정만 큐에 추가
                    if dominant_emotion in ["neutral", "happy", "sad", "surprise"]:
                        emotion_queue.append((dominant_emotion, emotion_probabilities[dominant_emotion]))
                        emotion_results[dominant_emotion].append(emotion_probabilities[dominant_emotion])

                    # 가장 빈번한 감정을 계산
                    if emotion_queue:
                        most_common_emotion = max(set(emotion_queue), key=emotion_queue.count)
                        emotion_name, emotion_prob = most_common_emotion

                        # 인식된 감정과 확률을 화면에 표시(테스트용)
                        # cv2.putText(frame, f"Emotion: {emotion_name} ({emotion_prob:.2f})", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        #             (0, 255, 0), 2, cv2.LINE_AA)
                        emotion_result.append((emotion_name, emotion_prob))

                        answerNo = fl.extract_number_from_filename(video_path) + 1
                        processed_files.append(os.path.basename(video_path))

                        for emotion, probs in emotion_results.items():
                            for prob in probs:
                                rounded_prob = round(prob, 2)
                                vdb.insert_emotion(answerNo, itvNo, rounded_prob, emotion, conn)

                except Exception as e:
                    print(f"Error: {e}")

        cap.release()
        end_time = time.time()  # 종료 시간 기록
        elapsed_time = end_time - start_time  # 소요 시간 계산
        print(f"{video_path} 처리 시간: {elapsed_time:.2f}초")

if __name__ == '__main__':
    processed_files = []
    emotion_analysis(1040, processed_files)

