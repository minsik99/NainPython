# 1개 키워드 1페이지에서 데이터 추출

from datetime import datetime, date
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from konlpy.tag import Kkma
import cx_Oracle

kkma = Kkma()
word_dic = {}  # dict()

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

def companylist(keyword):
    if not keyword:
        return {'error': 'No keyword'}, 400

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
    articles = soup.select(
        '#content > div > div > div.cnt-list-wrap > div > div.recruit-info > div.lists > div > div.list-default > ul > li')
    driver.quit()

    lines = []
    for article in articles:
        require_tag = article.select_one('.post-list-info > p.etc')
        if require_tag:
            lines.append(require_tag.text.strip())

    # 명사 추출
    for line in lines:
        mal_list = kkma.pos(line)
        for word in mal_list:
            if word[1] == 'NNG' or word[1] == 'NNP':
                if word[0] not in word_dic:
                    word_dic[word[0]] = 0
                word_dic[word[0]] += 1

    # 단어 빈도수에 대해 내림차순 정렬
    sorted_words = sorted(word_dic.items(), key=lambda x: x[1], reverse=True)

    # 상위 10개 단어 추출 및 DB 저장
    top_words = {word: count for word, count in sorted_words[:10]}
    save_to_db(top_words, keyword)

    return top_words

# 키워드로 데이터 크롤링 및 상위 10개 단어 추출
keyword = '백엔드 개발자'
top_words = companylist(keyword)

print("상위 10개 단어:")
for word, count in top_words.items():
    print(f'{word}: {count}')

connection.close()