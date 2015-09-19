# -*- coding: utf-8 -*-
__author__ = 'heaton'

import sys
import io
from flask import Flask, request, Response
from bs4 import BeautifulSoup, CData
import urllib.request
import urllib.parse
import time
import re
import logging
from werkzeug.contrib.fixers import ProxyFix

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
#logging.basicConfig(filename='logs/api.log', level=logging.INFO, format='[%(asctime)s %(levelname)s $(message)s', datefmt='%Y%m%d %H:%M:%S')
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "Hello World" if request.args.get('echostr')==None else request.args.get('echostr')
    if request.method == 'POST':
        soup = BeautifulSoup(request.data, 'xml')
        searchString = ''
        if soup.MsgType.string == 'voice':
            soup.MsgType.string = 'text'
            soup.Recognition.name = 'Content'
        searchString = soup.Content.string
        returnString = xiami(str(searchString))

        soup.ToUserName.string, soup.FromUserName.string = CData(soup.FromUserName.string), CData(soup.ToUserName.string)
        soup.CreateTime.string = CData(str(int(time.time())))
        soup.Content.string = CData(returnString)

        print(soup)
        return Response(str(soup), mimetype='text/xml')

@app.route('/test/<keyword>', methods=['GET', 'POST'])
def test(keyword):
    logging.info('start')
    # result = xiami(keyword)
    logging.error('end')
    result = xiamitest(keyword)
    return result

def xiamitest(keyword):
    data = None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"}
    #1 http://www.xiami.com/search?pos=1&key={keyword} html
    print('keyword', urllib.parse.quote(keyword))
    req1 = urllib.request.Request('http://www.xiami.com/search?pos=1&key=' + urllib.parse.quote(keyword), data, headers)
    response1 = urllib.request.urlopen(req1)
    xiami_soup1 = BeautifulSoup(response1.read().decode('gbk', 'ignore').encode('utf-8'), 'html.parser')
    td_songs = xiami_soup1.find_all('td', class_='song_name')
    print('td_songs', td_songs)
    for td in td_songs:
        a = td.find('a')
        if str(a['href'])[:4] != 'http':
            a = a.next_sibling.next_sibling
        print(a)
        print(1)
        req2 = urllib.request.Request(a['href'], data, headers)
        response2 = urllib.request.urlopen(req2)
        print(2)
        xiami_soup2 = BeautifulSoup(response2.read(), 'html.parser')
        lrc_main = xiami_soup2.find('div', class_='lrc_main')
        if lrc_main != None:
            info = xiami_soup2.find(id='albums_info').get_text()
            print(info)
            info = info.replace('：\n', '：')
            print(info)
            info = info.replace('\n\n\n', '\n')
            geci = info + lrc_main.get_text().strip()
            print(3)
            print('geci1', geci)
            return geci
    return "未找到歌词"


'''
方法：在虾米上搜索歌词
返回：歌词
坑：1. 搜素时http头中要添加User-Agent
    2. 参数有可能是中文或特殊字符，需要urllib.parse.quote后再访问
    3. 搜索结果可能存在下拉式链接，如果这样就取后面一个a标签
    4. 歌词文件read出来后是b开头相当于C#中的byte[]，需要decode(encoding='utf-8')为字符串
'''
def xiami(keyword):
    data = None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"}
    #1 http://www.xiami.com/search?pos=1&key={keyword} html
    req1 = urllib.request.Request('http://www.xiami.com/search?pos=1&key=' + urllib.parse.quote(keyword), data, headers)
    response1 = urllib.request.urlopen(req1)
    xiami_soup1 = BeautifulSoup(response1.read().decode('gbk', 'ignore').encode('utf-8'), 'html.parser')
    td_songs = xiami_soup1.find_all('td', class_='song_name')
    for td in td_songs:
        a = td.find('a')
        if str(a['href'])[:4] != 'http':
            a = a.next_sibling.next_sibling
        req2 = urllib.request.Request(a['href'], data, headers)
        response2 = urllib.request.urlopen(req2)
        xiami_soup2 = BeautifulSoup(response2.read(), 'html.parser')
        lrc_main = xiami_soup2.find('div', class_='lrc_main')
        if lrc_main != None:
            info = xiami_soup2.find(id='albums_info').get_text().replace('：\n', '： ').replace('\n\n\n', '\n')
            geci = info + lrc_main.get_text().strip()
            return geci
    return "未找到歌词"

# http://s.music.qq.com/fcgi-bin/yqq_search_v8_cp?tab=all|<keyword>&w=<keyword>
@app.route('/test/qq/<keyword>', methods=['GET', 'POST'])
def qq(keyword):
    data = None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"}
    #1 http://www.xiami.com/search?pos=1&key={keyword} html
    keyword = urllib.parse.quote(keyword)
    print('url', 'http://s.music.qq.com/fcgi-bin/yqq_search_v8_cp?tab=all|%s&w=%s' % (keyword, keyword))
    req1 = urllib.request.Request('http://s.music.qq.com/fcgi-bin/yqq_search_v8_cp?tab=all|%s&w=%s' % (keyword, keyword), data, headers)
    response1 = urllib.request.urlopen(req1)
    print(response1.read().decode(encoding='UTF-8'))
    xiami_soup1 = BeautifulSoup(response1.read(), 'html.parser')
    print(xiami_soup1.find('ol'))
    div_songs = xiami_soup1.find('ol', id='divsonglist').find_all('div', class_='music_name')
    print('div_songs', div_songs)
    for div in div_songs:
        a = div.span.a
        # if str(a['href'])[:4] != 'http':
        #     a = a.next_sibling.next_sibling
        print(a)
        print(1)
        req2 = urllib.request.Request(a['href'], data, headers)
        response2 = urllib.request.urlopen(req2)
        print(2)
        return 'hehe'
        xiami_soup2 = BeautifulSoup(response2.read(), 'html.parser')
        lrc_main = xiami_soup2.find('div', class_='lrc_main')
        if lrc_main != None:
            info = xiami_soup2.find(id='albums_info').get_text()
            print(info)
            info = info.replace('：\n', '：')
            print(info)
            info = info.replace('\n\n\n', '\n')
            geci = info + lrc_main.get_text().strip()
            print(3)
            print('geci1', geci)
            return geci
    return "未找到歌词"


if __name__ == '__main__':
    app.debug = True
    app.run()

