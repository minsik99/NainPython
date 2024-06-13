import requests
from bs4 import BeautifulSoup
from flask import request, jsonify

def search_naver_news():
    data = request.get_json()
    keyword = data.get('keyword')
    page_number = data.get('page_number', 1)
    page_size = data.get('page_size', 10)

    if not keyword:
        return jsonify({'error': 'No keyword provided'}), 400

    articles_data = []
    start_index = (page_number - 1) * page_size + 1
    url = f'https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_pge&sort=0&start={start_index}'

    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.select('.news_area')

        for article in articles[:page_size]:
            title_tag = article.select_one('.news_tit')
            content_tag = article.select_one('.news_dsc')
            source_tag = article.select_one('.info_group .press')
            image_tag = article.select_one('span.thumb_box img.thumb')
            time_tag = article.select_one('.info_group span.info')

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