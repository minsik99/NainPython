import os
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
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
    return 'Hello, World! pycharm'


@app.route('/data', methods=['POST'])
def search_naver_news():
    # 입력받은 키워드 추출
    data = request.get_json()
    keyword = data.get('keyword')

    # 키워드가 입력되지 않았다면 "" 검색어를 찾을 수 없습니다 에러 페이지 출력
    if not keyword:
        return jsonify({'error': 'No keyword'}), 400

    url = f'https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_pge&sort=0'

    # 요청 보내기
    response = requests.get(url)

    articles_data = []

    # 요청 성공 여부 확인
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # 뉴스 기사 리스트 추출
        articles = soup.select('.news_area')

        for article in articles:
            title_tag = article.select_one('.news_tit')  # 기사 제목
            content_tag = article.select_one('.news_dsc')  # 기사 내용
            source_tag = article.select_one('.info_group .press')  # 기사 출처
            image_tag = article.select_one('span.thumb_box img.thumb')  # 기사 이미지
            time_tag = article.select_one('.info_group span.info')  # 작성된 시간

            if title_tag and content_tag and source_tag and time_tag:
                title = title_tag.text
                link = title_tag['href']
                content = content_tag.text
                source = source_tag.text
                image = image_tag['data-lazysrc'] if image_tag else None
                time = time_tag.text
                articles_data.append({
                    'title': title,
                    'link': link,
                    'content': content,
                    'source': source,
                    'image': image,
                    'time': time
                })

    else:
        print(f"Failed to retrieve articles: {response.status_code}")

    return jsonify(articles_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
