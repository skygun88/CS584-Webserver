import requests

url = 'http://127.0.0.1:8000/kakao/kakao_ocr/'


result = requests.post(url, files={'img': open('5.JPG', 'rb')})
print(result)