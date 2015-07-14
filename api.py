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

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "Hello World"
    if request.method == 'POST':
        soup = BeautifulSoup(request.data, 'xml')

        searchString = soup.Content.string
        returnString = xiami(str(searchString))

        soup.ToUserName.string, soup.FromUserName.string = CData(soup.FromUserName.string), CData(soup.ToUserName.string)
        soup.CreateTime.string = CData(str(int(time.time())))
        soup.Content.string = CData(returnString)
        print(soup)
        return Response(str(soup), mimetype='text/xml')


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
    print('keyword', urllib.parse.quote(keyword))
    req1 = urllib.request.Request('http://www.xiami.com/search?pos=1&key=' + urllib.parse.quote(keyword), data, headers)
    response1 = urllib.request.urlopen(req1)
    xiami_soup1 = BeautifulSoup(response1.read(), 'html.parser')
    a1 = xiami_soup1.find('td', class_='song_name').find('a')
    if str(a1['href'])[:4] != 'http':
        a1 = a1.next_sibling.next_sibling
    songid = str(a1['href']).split('/')[-1]
    print('song', songid)

    #2 http://www.xiami.com/song/playlist/id/{song} xml
    req2 = urllib.request.Request('http://www.xiami.com/song/playlist/id/' + songid, data, headers)
    response2 = urllib.request.urlopen(req2)
    xiami_soup2 = BeautifulSoup(response2.read(), 'xml')
    lyric_url = str(xiami_soup2.lyric_url.string)
    print('lyric_url', lyric_url)

    #3 lyric doc
    if re.match(r'^http.*', lyric_url):
        print('match')
        req3 = urllib.request.Request(lyric_url, data, headers)
        response3 = urllib.request.urlopen(req3)
        lyric_bytes = response3.read()
        print('lyric_before', lyric_bytes)
        lyric_string = lyric_bytes.decode(encoding='utf-8')
        print('lyric_string', lyric_string)

        lyric_string = re.sub(r'\[.*?\]', '', lyric_string)
    else:
        lyric_string = '未找到歌词'

    return str(lyric_string)


if __name__ == '__main__':
    app.debug = True
    app.run()

