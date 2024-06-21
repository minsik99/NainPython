# 베이스 이미지 설정
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요 패키지 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/* \


RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \

# 파이썬 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 컨테이너 시작 명령어 설정
CMD ["python", "private/app.py"]