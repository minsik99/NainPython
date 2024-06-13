from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests

def companylist():
    data = request.get_json()
    keyword = data.get('keyword')

    if not keyword:
        return jsonify({'error': 'No keyword'}), 400

    # Chrome options 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저를 숨김 모드로 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # WebDriver 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # URL 로드
    url = 'https://www.jobkorea.co.kr/'
    response = driver.get(url)
    import time
    # 페이지 로드 대기 (필요시 조정)
    time.sleep(5)

    search = keyword
    # searchText
    # 검색창 클릭
    driver.find_element(By.CSS_SELECTOR, '#stext').send_keys(search)
    driver.find_element(By.CSS_SELECTOR, '#common_search_btn').click()
    time.sleep(1.5)

    # BeautifulSoup으로 HTML 파싱
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # 데이터 선택
    articles_data = []
    for i in range(1, 11):  # 1부터 10까지 반복
        selector = f'#content > div > div > div.cnt-list-wrap > div > div.recruit-info > div.lists > div > div.list-default > ul > li:nth-child({i})'
        article = soup.select_one(selector)

        company_tag = article.select_one('div > div.post-list-corp > a')  # 공고 회사
        post_tag = article.select_one('div > div.post-list-info > a')  # 공고 내용
        require_tag = article.select_one('div > div.post-list-info > p.etc')  # 조건
        time_tag = article.select_one('div > div.post-list-info > p.option > span.date')  # 작성된 시간
        if company_tag and post_tag and require_tag and time_tag:
            company = company_tag.text
            title = post_tag['title']
            link = url + post_tag['href']
            require = require_tag.text
            time = time_tag.text
            articles_data.append({
                'company': company,
                'title': title,
                'link': link,
                'require': require,
                'time': time
            })

    else:
        print(f"Failed to retrieve articles: {response}")
    # 브라우저 닫기
    print(articles_data)
    driver.quit()

    return jsonify(articles_data)