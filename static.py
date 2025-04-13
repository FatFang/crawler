import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import random

filepath = './static.csv'
fieldnames = ['近一個月熱銷度排名','書名', '作者', '價格', '博客來書號', '封面圖片網址']

# 建立csv，只做一次
if not os.path.exists(filepath):
    with open(filepath, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
    print('已建立CSV')
else:
    print('CSV已存在')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15'
}

current_page = 1
total_page = 15
no = 1

while True:
    # https://search.books.com.tw/search/query/cat/1/qsub/001/qqsub/15-16/sort/9/v/1/page/1/adv_mnew/1/spell/3/ms2/ms2_1/key/漫畫#f_adv
    # url = 'https://search.books.com.tw/search/query/cat/1/qsub/001/qqsub/16/sort/9/v/1/page/' + str(current_page) + '/spell/3/ms2/ms2_1/key/漫畫#f_adv'
    # 慢 https://search.books.com.tw/search/query/cat/1/qsub/001/qqsub/16/sort/9/v/1/page/1/adv_mnew/1/spell/3/ms2/ms2_1/key/漫畫#f_adv
    url = 'https://search.books.com.tw/search/query/cat/1/qsub/001/qqsub/16/sort/9/v/1/page/' + str(current_page) + '/adv_mnew/1/spell/3/ms2/ms2_1/key/漫畫#f_adv'
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        print('成功連線')
    else:
        print('已到讀取完畢')
        break

    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    print(f'目前爬第 {current_page} 頁')
    table = soup.find('div', class_='table-searchbox clearfix')
    
    if not table:
        print('沒資料')
        break

    # 尋找每頁中table的每一行（書本資訊）
    rows = table.find_all('div',class_ = "mod2 table-container")

    all_data = []
    for r in rows:
        # 儲存每一本書
        books = r.find('div',class_ = "table-tr").find_all('div',class_ = "table-td")
        for b in books:
            # 儲存書的各種資料
            book_name = b.h4.a.text.strip()
            authors = b.find('div', class_='type clearfix').find('p',class_="author").find_all('a')
            if authors:
                author_list = [a.text.strip() for a in authors]
                author = ' '.join(author_list)
            else:
                author = ''
            # print(author)
            # sys.exit(0)
            price = b.ul.li.text.strip()
            bookid = b['id'].split('-')[-1] if b.has_attr('id') else ''
            src = b.find('img')['data-src'] if b.find('img') else ''
            if 'getImage?i=' in src:
                img = src.split('getImage?i=')[-1].split('&')[0]
            else:
                img = src

            data = {
                '近一個月熱銷度排名': no,
                '書名': book_name,
                '作者': author,
                '價格': price,
                '博客來書號': bookid,
                '封面圖片網址': img
            }
            all_data.append(data)
            # 排名
            no += 1

    with open(filepath, mode='a', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(all_data)  # 多筆資料寫入
        print(f'寫入成功: 第 {current_page} 頁 共 {len(all_data)} 筆')

    # break
    # 休息一段時間，以防被ban掉
    time.sleep(random.uniform(3,8))
    # 頁數更改
    current_page += 1

