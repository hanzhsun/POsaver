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

    book = epub.EpubBook()

    def add_chapter(c):
        book.add_item(c)
        book.spine.append(c)
        book.toc.append(c)

    btitle = home.h1.text
    book.set_identifier(bid)
    book.set_title(btitle)
    book.set_language('zh')
    book.add_metadata('DC', 'publisher', 'POsaver')

    author_tag = home.find('a', class_='book_author')
    author = author_tag.text
    book.add_author(author)

    cover = home.find('div', class_='book_cover').find('img')['src']
    book.set_cover('cover.jpg', requests.get(cover).content)

    status = home.find('dd', class_='statu').text.strip()
    n = math.ceil(int(re.search(r'\d+', status)[0]) / 100)
    description = home.find('div', class_='B_I_content').get_text(separator="\n", strip=True)
    book.add_metadata('DC', 'description', f"""
    原址: {b}
    作者: {author} ({prefix + author_tag['href']})
    状态: {status}
    简介: {description}
    """.strip())

    page = home.select('div.book_info, div.book_intro')
    for e in page:
        for a in e.find_all('a', href=True):
            a['href'] = requests.compat.urljoin(prefix, a['href'])

        for img in e.find_all('img'):
            img.decompose()

        for comment in e.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract() 

    abstract = epub.EpubHtml(title='简介', file_name='abstract.xhtml', lang='zh')
    abstract.content = '<link href="/css/styles.css" rel="stylesheet" type="text/css"/>' + ''.join(str(e) for e in page)

    with open(os.path.join(base,'layout.css'), 'r', encoding='utf-8') as f:
        css = f.read()
    css_item = epub.EpubItem(
        file_name='css/styles.css', 
        media_type='text/css', 
        content=css.encode('utf-8')
    )
    book.add_item(css_item)
    abstract.add_item(css_item)

    with open(os.path.join(base,'share.png'), 'rb') as f:
        image = f.read()
    img_item = epub.EpubItem(
        file_name='images/share.png',
        media_type='image/png',
        content=image
    )
    book.add_item(img_item)
    
    add_chapter(abstract)

    for i in range(n):
        clist = get_page(b + f'/articles?page={i+1}').select('div.c_l')
        print(f'第{i+1}页: {len(clist)}章')
        for c in clist:
            counter = c.find('div', class_='l_counter').text
            inline(counter)
            a = c.find('a')
            if a.get('class') == ['btn_L_red']:
                inline('未订购')
                continue
            url = prefix + a['href']
            while True:
                html = get_page_r(url)
                if html != 1:
                    inline('.')
                    chapter = epub.EpubHtml(title=html.h1.text, file_name=f"{counter}.xhtml", lang='zh')
                    chapter.content = str(html.h1).replace('h1','h3') + ''.join(re.sub(r'\xa0|\r|\s+', '', str(e)) for e in html.select('p'))
                    add_chapter(chapter)
                    break
                inline('x')   

    fbook = f'{btitle}.epub'
    fazw = f'{btitle}.azw3'
    epub.write_epub(fbook, book)
    subprocess.run(['ebook-convert', fbook, fazw])
    os.remove(fbook)

if __name__ == '__main__':
    while True:
        get_book()