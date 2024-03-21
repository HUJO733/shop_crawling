import requests
import bs4
from bs4 import BeautifulSoup
import pymysql
import re
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = int(os.environ.get('DB_PORT'))
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_DATABASE = os.environ.get('DB_DATABASE')

# MySQL 연결 설정
db = pymysql.connect(host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE) # 사용 DB 지정
cursor = db.cursor() # DB와 연결된 커서 객체 생성

for page in range(1, 6):
    url = 'https://onlyeco.co.kr/category/%EB%A6%AC%EB%B9%99/50/?page={page}'.format(page=page)
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 상품 리스트
    items = soup.select('.box') # 아이템은 18개인데 찾은건 19개가 나옴
    i = 1

    for item in items:
        # 위에서 찾은 19개 중 마지막 데이터는 18번째 데이터와 중복됨
        if i <= 18:
            # 상품명
            title_text = item.select_one('.name')
            if isinstance(title_text, bs4.element.Tag):
                if ']' in title_text.text:
                    title = title_text.text.split(']')[1].strip()
                else:
                    title = title_text.text.split(':')[1].strip()
            # 상품가격
            price_text = item.select_one('[rel=판매가]')
            if isinstance(price_text, bs4.element.Tag):
                price = int(re.sub(r'판매가\s*:\s*|,|원', '', price_text.text))
            # 상품이미지
            imageDiv = item.select_one('.prdImg')
            if isinstance(imageDiv, bs4.element.Tag):
                # href 값이 주소 앞부분은 데이터로 담기지 않아서 추가
                item_url = 'https://onlyeco.co.kr' + imageDiv.find('a')['href']
                thumbnail = imageDiv.find('img')['src']

            i += 1

            # 데이터 삽입 쿼리 실행
            insert_query = "INSERT INTO shop (item_url, title, price, thumbnail) VALUES (%s, %s, %s, %s);"
            cursor.execute(insert_query, (item_url, title, price, thumbnail))

# DB 변경사항 저장
db.commit()

# 커서 및 연결 종료
cursor.close()
db.close()
    


