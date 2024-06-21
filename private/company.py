import json
import zipfile
from datetime import datetime, date

from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os


CACHE_FILE = 'cache.zip'

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with zipfile.ZipFile(CACHE_FILE, 'r') as zf:
        with zf.open('cache.json') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}


def save_cache(cache):
    json_data = json.dumps(cache)
    with zipfile.ZipFile(CACHE_FILE, 'w') as zf:
        zf.writestr('cache.json', json_data)

def companylist(keyword):
    if not keyword:
        return jsonify({'error': 'No keyword'}), 400
    # 캐시 불러오기
    cache = load_cache()

    # 캐시에 키워드가 있는 경우
    if keyword in cache:
        return cache[keyword]

    # Chrome options 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저를 숨김 모드로 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")  # GPU 사용 안 함
    chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 사용 안 함
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # chrome_options.add_argument("user-data-dir=selenium")

    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # URL 및 헤더 정의
    url = 'https://www.jobkorea.co.kr/'
    driver.get(url)


    # 검색어 입력 및 검색 버튼 클릭
    search_box = driver.find_element(By.CSS_SELECTOR, '#stext')
    search_box.send_keys(keyword)
    driver.find_element(By.CSS_SELECTOR, '#common_search_btn').click()

    # 결과 페이지 로드 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.post-list-corp a'))
    )

    # BeautifulSoup으로 HTML 파싱
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 데이터 선택
    articles_data = []
    articles = soup.select(
        '#content > div > div > div.cnt-list-wrap > div > div.recruit-info > div.lists > div > div.list-default > ul > li')
    driver.quit()
    for article in articles:
        company_tag = article.select_one('.post-list-corp > a')  # 공고 회사
        post_tag = article.select_one('.post-list-info > a')  # 공고 내용
        require_tag = article.select_one('.post-list-info > p.etc')  # 조건
        time_tag = article.select_one('.post-list-info > p.option > span.date')  # 작성된 시간

        if company_tag and post_tag and require_tag and time_tag:
            company = company_tag.text.strip()
            title = post_tag['title'].strip()
            link = 'https://www.jobkorea.co.kr' + post_tag['href'].strip()
            require_tags = require_tag.text.strip().split(',')[:7]
            time = time_tag.text.strip()
            if time == "상시채용":
                date_obj = time
            else:
                current_year = datetime.now().year
                date_obj = datetime.strptime(f"{current_year}/{time.strip('~').split('(')[0]}", "%Y/%m/%d")

            articles_data.append({
                'company': company,
                'title': title,
                'link': link,
                'require': require_tags,
                'time': date_obj.strftime("%Y-%m-%d") if isinstance(date_obj, date) else date_obj
            })

            cache[keyword] = articles_data
            save_cache(cache)

    return jsonify(articles_data)





