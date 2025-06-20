import re
import os
import sys
import math
import subprocess
import random
import requests
from requests.exceptions import RequestException
from ebooklib import epub
from bs4 import BeautifulSoup, Comment

def inline(text):
    print(text, end='',flush=True)
def get_page(url):
	try:
		session.headers.update({'User-Agent': random.choice(headers)})
		r = session.get(url)
		if r.status_code == 200:
			return BeautifulSoup(r.content, 'lxml')
		print(r.status_code)
		return None
	except RequestException:
		print("Fail")
		return None

def get_page_r(url):	
	try:
		session.headers.update({
			'User-Agent': random.choice(headers),
			'Referer': url,
			'X-Requested-With': 'XMLHttpRequest',
		})
		r = session.get(url.replace('articles', 'articlescontent'))
		if r.status_code == 200:
			return BeautifulSoup(r.content, 'lxml')
		print(r.status_code)
		return 1
	except RequestException:
		print("Fail")
		return 1

while True:
    try:
        with open('.conf', 'r') as f:
            c = f.readline().strip()
            if not c:
                print('请在 .conf 文件中填写cookie')
            else:
                print('成功读取cookie')
                break
    except FileNotFoundError:
        print('未找到 .conf 文件')

session = requests.Session()
session.headers.update({'Host': "www.po18.tw", 'Cookie': c})

headers = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.54',
]

prefix = 'https://www.po18.tw'

if getattr(sys, 'frozen', False):
    base = sys._MEIPASS
else:
    base = os.path.dirname('.')

def get_book():
    while True:
        bid = input("请输入书籍编号: ")

        if bid.isdigit() and len(bid) == 6:
            b = prefix + "/books/" + bid
            print(f"正在获取书籍{b}")
            home = get_page(b)
            if home:
                break
            else:
                print("无法获取该书籍")
        else:
            print("无效的编码，请重新输入")

    btitle = home.h1.text
    
    author_tag = home.find('a', class_='book_author')
    author = author_tag.text

    status = home.find('dd', class_='statu').text.strip()
    n = math.ceil(int(re.search(r'\d+', status)[0]) / 100)
    description = home.find('div', class_='B_I_content').get_text(separator="\n", strip=True)
    text = f"""书名: {btitle}
原址: {b}
作者: {author} ({prefix + author_tag['href']})
状态: {status}
标签: {'、'.join([t.text.strip() for t in home.find_all('a', class_='tag')])}
简介: {description}
文档由POsaver (https://github.com/hanzhsun/POsaver) 生成
"""

    for i in range(n):
        clist = get_page(b + f'/articles?page={i+1}').select('div.c_l')
        print(f'第{i+1}页: {len(clist)}章')
        for c in clist:
            counter = re.sub(r'^0+', '', c.find('div', class_='l_counter').text)
            inline(counter)
            a = c.find('a')
            if a is None:
                inline('无法订购')
                continue
            if a.get('class') == ['btn_L_red']:
                inline('未订购')
                continue
            url = prefix + a['href']
            while True:
                html = get_page_r(url)
                if html != 1:
                    inline('.')
                    content = '\n'.join(re.sub(r'\xa0|\r|\s{2,}', '', e.text.strip()) for e in html.select('p'))
                    text += f"""
{counter + '·' + html.h1.text.strip()}

{content}
"""
                    break
                inline('x')

    safe_btitle = re.sub(r'[\\/:*?"<>|]', '_', btitle)
    with open(f"./{safe_btitle}.txt", "a", encoding="utf-8") as f:
        f.write(text)
    print()
    print(f'《{btitle}》下载完成')

if __name__ == '__main__':
    while True:
        get_book()