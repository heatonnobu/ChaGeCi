from flask import Flask, request, Response
from bs4 import BeautifulSoup, CData
import hashlib
import time
import requests

app = Flask(__name__)

app.config.from_object('setting')

@app.route('/api/v2')
def api():
	return Response(f'{request.method}: {request.url}')

@app.route('/api/v2/chageci/<keyword>', methods=['GET'])
def api_test_chageci(keyword):
	print(f'keyword: {keyword}')
	return get_lyrics_from_60s(keyword)

@app.route('/api/v2/chageci', methods=['POST'])
def api_chageci():
	if not is_from_WX(request):
		return Response("Not from WeChat", mimetype='text/plain')
	
	soup = BeautifulSoup(request.data, 'xml')
	# print(soup.FromUserName.string)
	msg_Type = soup.MsgType.string
	# searchString = ''
	if msg_Type == 'voice':
		soup.Recognition.name = 'Content'
	searchString = soup.Content.string
	returnString = get_lyrics_from_60s(str(searchString))
	soup.ToUserName.string, soup.FromUserName.string = CData(soup.FromUserName.string), CData(soup.ToUserName.string)
	soup.MsgType.string, soup.Content.string, soup.CreateTime.string = CData('text'), CData(returnString), str(int(time.time()))
	# soup.CreateTime.string = str(int(time.time()))
	# soup.Content.string = CData(returnString)
	return Response(str(soup), mimetype='text/xml')

@app.route('/api/v2/test/settings')
def api_test_settings():
	for key in app.config.keys:
		print(app.config[key])
	return app.config['CHAGECI_WX_TOKEN']

def is_from_WX(request):
	try:
		args = request.args
		signature = args.get('signature')
		timestamp = args.get('timestamp')
		nonce = args.get('nonce')
		echostr = args.get('echostr')
		token = app.config['CHAGECI_WX_TOKEN']

		print(f'token: {token}')
		
		list = [token, timestamp, nonce]
		list.sort()
		sha1 = hashlib.sha1()
		map(sha1.update, list)
		hashcode = sha1.hexdigest()
		if hashcode == signature:
			return echostr
		else:
			return ""
	except Exception as e:
          return False

def get_lyrics_from_60s(keyword):
	params = {'clean': 'false', 'encoding': 'text', 'query': keyword}
	response = requests.get('https://60s.viki.moe/v2/lyric', params=params)
	return response.text if response.status_code == 200 else "未查到歌词"


if __name__ == '__main__':
	app.run(port=8080, debug=True)