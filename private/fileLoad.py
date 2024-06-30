import glob
import time
import cv2
def fileLoad(itvNo, processed_files):
    video_files = glob.glob(f"{itvNo}/*.webm")
    results = []

    for video_path in video_files:
        if video_path in processed_files:
            print(f"이미 처리된 파일: {video_path}")
            continue

        print(f"처리 중: {video_path}")
        start_time = time.time()
        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            print("비디오 파일을 열 수 없습니다.")
            continue

        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if length == 0:
            print(f"파일이 불완전합니다: {video_path}")
            cap.release()
            continue

        results.append((video_path, cap, start_time))
        processed_files.append(video_path)  # 처리된 파일 목록에 추가

    return results


def extract_number_from_filename(filename):
    # 파일명에서 숫자 추출
    import re
    match = re.search(r'(\d+)(?!.*\d)', filename)
    if match:
        return int(match.group())
    else:
        return 0  # 기본값 설정



