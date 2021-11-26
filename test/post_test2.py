import glob
import time
import json
import requests

# url = 'http://127.0.0.1:8000/kakao/kakao_ocr/'
url = 'http://143.248.55.163:8000/googlestar/ocr/'
start = time.time()

data = {'user_email': 'test'}
result = requests.post(url, files={'img': open('imgs2/test3.jpg', 'rb')}, data=data)
result_dict = result.json()
# print(result_dict)

print(result_dict['n_results'])
for x in result_dict['results']:
    print(x)


index = result_dict['index']
position = 3
numbers = result_dict['results'][position]
ts1 = 1636012499000
ts2 = 1636012500000
ts3 = 1636012510000
ts4 = 1636012511000

user_data = {'index': index, 
                'timestamp1': ts1, 
                'timestamp2': ts2, 
                'timestamp3': ts3, 
                'timestamp4': ts4, 
                'position': position, 
                'number': numbers['numbers'][0],
                'root_index': index}

new_url = 'http://143.248.55.163:8000/googlestar/user_data/'
result = requests.post(new_url, data=user_data)
result_dict = result.json()
print(result_dict)

# test_imgs = glob.glob('imgs/*')
# test_imgs = glob.glob('imgs2/*')

# test_imgs = ['imgs/7.JPG', 'imgs/4.JPG']


# for img in test_imgs:
#     result = requests.post(url, files={'img': open(img, 'rb')})
#     print(img)
#     print(result.json())

print(f'processing time: {time.time()-start}')