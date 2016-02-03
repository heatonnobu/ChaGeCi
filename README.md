## ChaGeCi(查歌词)

ChaGeCi是一个微信公众号的后端接口，使用python3编写，提供查歌词服务，由于个人只能开订阅号，所以支持的接口不多，目前只支持简单的文本消息、语音消息。

### Dependencies
- flask
- BeautifulSoup4
- virtualenv (not required)

### Deploy
```
git clone https://github.com/heatonnobu/ChaGeCi.git
cd chageci
virtualenv env
source venv/bin/activate
pip install requirements.txt
python api.py
```

then the app is runing on `http://localhost:5000/`
