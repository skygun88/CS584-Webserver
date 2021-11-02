import glob
import time
import requests

# url = 'http://127.0.0.1:8000/kakao/kakao_ocr/'
url = 'http://143.248.55.163:8000/kakao/kakao_ocr/'


# result = requests.post(url, files={'img': open('5.JPG', 'rb')})
# print(result.json())


# test_imgs = glob.glob('imgs/*')
test_imgs = glob.glob('imgs2/*')

# test_imgs = ['imgs/7.JPG', 'imgs/4.JPG']


start = time.time()
for img in test_imgs:
    result = requests.post(url, files={'img': open(img, 'rb')})
    print(img)
    print(result.json())

print(f'processing time: {time.time()-start}')