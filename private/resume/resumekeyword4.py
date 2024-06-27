# 5개 키워드로 여러 페이지에서 데이터 추출 (단어기준)

import sys
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import cx_Oracle
import time
import re

# 오라클 데이터베이스 연결 설정
dsn = cx_Oracle.makedsn('localhost', '1521', service_name='xe')
connection = cx_Oracle.connect('C##NAIN', 'NAIN', dsn)

def get_next_keyword_no():
    cursor = connection.cursor()
    cursor.execute("SELECT NVL(MAX(KEYWORD_NO), 0) + 1 FROM TB_ACCEPTED_KEYWORD")
    next_keyword_no = cursor.fetchone()[0]
    cursor.close()
    return next_keyword_no

def save_to_db(word_dic, job_category):
    cursor = connection.cursor()
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        keyword_no = get_next_keyword_no()
        for word, count in word_dic.items():
            cursor.execute("""
                INSERT INTO TB_ACCEPTED_KEYWORD (KEYWORD_NO, JOB_CATEGORY, ACCEPT_KEYWORD, FREQUENCY, REFERENCE_DATE)
                VALUES (:keyword_no, :job_category, :accept_keyword, :frequency, TO_DATE(:reference_date, 'YYYY-MM-DD'))
            """, keyword_no=keyword_no, job_category=job_category, accept_keyword=word, frequency=count, reference_date=today)
            keyword_no += 1  # 다음 단어를 위한 키워드 번호 증가
        connection.commit()
    except Exception as e:
        print('데이터베이스 저장 중 에러 발생: ', e)
        connection.rollback()
    finally:
        cursor.close()

def extract_data_from_page(driver):
    # BeautifulSoup으로 HTML 파싱
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 데이터 선택
    articles = soup.select(
        '#content > div > div > div.cnt-list-wrap > div > div.recruit-info > div.lists > div > div.list-default > ul > li')

    lines = []
    for article in articles:
        require_tag = article.select_one('.post-list-info > p.etc')
        if require_tag:
            lines.append(require_tag.text.strip())

    return lines

def extract_phrases(text):
    # 예시: "UI*UX기획, 콘텐츠기획"을 "UI*UX기획", "콘텐츠기획"으로 분리
    return re.findall(r'\b\w+(?:\*?\w+)*\b기획', text)

def analyze_and_save_data(lines, job_category):
    word_dic = {}  # 각 키워드마다 word_dic 초기화

    # 문구 추출
    for line in lines:
        phrases = extract_phrases(line)
        for phrase in phrases:
            if phrase not in word_dic:
                word_dic[phrase] = 0
            word_dic[phrase] += 1

    # 단어 빈도수에 대해 내림차순 정렬
    sorted_words = sorted(word_dic.items(), key=lambda x: x[1], reverse=True)

    # 상위 10개 단어 추출 및 DB 저장
    top_words = {word: count for word, count in sorted_words[:10]}
    save_to_db(top_words, job_category)

    return top_words

def companylist(keyword):
    # Chrome options 설정
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 브라우저를 숨김 모드로 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")  # GPU 사용 안 함
    chrome_options.add_argument("--disable-extensions")  # 확장 프로그램 사용 안 함
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # URL 및 헤더 정의
    url = 'https://www.jobkorea.co.kr/Search/?stext=' + keyword
    driver.get(url)

    total_lines = []
    page_count = 0

    while page_count < 5:  # 20개씩 5페이지, 총 100개의 글을 수집
        # 결과 페이지 로드 대기
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.recruit-info a'))
            )
            print(f"페이지 {page_count + 1} 로드 성공")
        except Exception as e:
            print(f"페이지 {page_count + 1} 로드 중 오류 발생:", e)
            break

        # 페이지에서 데이터 추출
        lines = extract_data_from_page(driver)
        total_lines.extend(lines)

        # 다음 페이지로 이동
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, 'a.tplBtn.btnPgnNext')
            next_page.click()
            time.sleep(3)  # 페이지 로드 대기 시간
            page_count += 1
        except Exception as e:
            print("더 이상 페이지가 없습니다.", e)
            break

    driver.quit()

    # 분석 및 저장
    top_words = analyze_and_save_data(total_lines[:100], keyword)  # 100개 데이터까지만 분석

    return top_words

# 키워드 목록
keywords = ['웹 개발자', '프론트엔드 개발자', '서버 개발자', '서비스 기획자', 'PM']

# 각 키워드에 대해 데이터 크롤링 및 상위 10개 단어 추출
for keyword in keywords:
    top_words = companylist(keyword)
    print(f"상위 10개 단어 ({keyword}):")
    for word, count in top_words.items():
        print(f'{word}: {count}')

connection.close()
