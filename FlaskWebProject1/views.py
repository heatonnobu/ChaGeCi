"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import Flask, request, Response, render_template
from FlaskWebProject1 import app
import sys
import io
from bs4 import BeautifulSoup, CData
import urllib.request
import urllib.parse
import time
import re

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/hehe')
def about():
    return render_template(
        'about.html',
        title='Hehe',
        year=datetime.now().year,
        message='呵呵呵呵呵呵呵呵呵呵呵.'
    )

@app.route('/chageci', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # return "Hello World" if request.args.get('echostr')==None else request.args.get('echostr')
        return Response(request.args.get('echostr'), mimetype='text/xml')
    if request.method == 'POST':
        soup = BeautifulSoup(request.data, 'xml')
        # print(soup.FromUserName.string)
        msg_Type = soup.MsgType.string
        searchString = ''
        if msg_Type == 'voice':
            soup.Recognition.name = 'Content'
        searchString = soup.Content.string
        # searchString = soup.Content.string
        returnString = xiami(str(searchString))
        soup.ToUserName.string, soup.FromUserName.string = CData(soup.FromUserName.string), CData(soup.ToUserName.string)
        soup.MsgType.string = CData('text')
        soup.CreateTime.string = str(int(time.time()))
        soup.Content.string = CData(returnString)
        return Response(str(soup), mimetype='text/xml')

@app.route('/test/<keyword>', methods=['GET', 'POST'])
def test(keyword):
    if request.method == 'GET':
        print('get')
        result = xiami(keyword)
        return result
    if request.method == 'POST':
        print('post')
        print(request.data)
        try:
            soup = BeautifulSoup(request.data, 'xml')
        except:
            print(sys.exc_info()[0])
        print(soup)
        # print('toUserName:', soup.ToUserName.string)
        # print('FromUserName:', soup.FromUserName.string)
        searchString = soup.Content.string
        returnString = xiami(str(searchString))
        soup.ToUserName.string, soup.FromUserName.string = CData(soup.FromUserName.string), CData(soup.ToUserName.string)
        soup.MsgType.string = CData('text')
        soup.CreateTime.string = str(int(time.time()))
        soup.Content.string = CData(returnString)
        return Response(str(soup), mimetype='text/xml')


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
            info = xiami_soup2.find(id='albums_info').get_text().replace('：\n', '：').replace('\n\n\n', '\n')
            geci = info + lrc_main.get_text().strip()
            return geci
    return "未查到歌词"