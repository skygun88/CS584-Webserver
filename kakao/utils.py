import cv2
import requests
from PIL import ImageDraw
from shutil import copyfile

LIMIT_PX = 1024
LIMIT_BYTE = 1024*1024  # 1MB
LIMIT_BOX = 40
APP_KEY = '635970f007a450262909ce0a833104fb'

def kakao_api_request(image_path):
    API_URL = 'https://dapi.kakao.com/v2/vision/text/ocr'

    headers = {'Authorization': 'KakaoAK {}'.format(APP_KEY)}

    image = cv2.imread(image_path)
    jpeg_image = cv2.imencode(".jpg", image)[1]
    data = jpeg_image.tobytes()


    return requests.post(API_URL, headers=headers, files={"image": data})

def kakao_ocr_resize(abs_ori_img_path: str, abs_resized_img_path: str):
    image = cv2.imread(abs_ori_img_path)
    height, width, _ = image.shape

    ratio = 1.0
    if LIMIT_PX < height or LIMIT_PX < width:
        ratio = float(LIMIT_PX) / max(height, width)
        image = cv2.resize(image, None, fx=ratio, fy=ratio)
        height, width, _ = height, width, _ = image.shape
        cv2.imwrite(abs_resized_img_path, image)

    else:
        copyfile(abs_ori_img_path, abs_resized_img_path)
    return ratio

def rotation(path):
    img = Image.open(path)
    rotated = img.rotate(180)
    img.save(path)
    return path 

def pil_draw_box(image, points):
    # points = tuple(map(lambda x: tuple(x), points))
    draw = ImageDraw.Draw(image)
    draw.polygon(points, fill=None, outline=(50, 255, 50))
    return image

def convert_bbox_scale(detected_words, ratio):
    result = []
    scale = 1/ratio
    for word in detected_words:
        new_boxes = tuple(map(lambda x: tuple(map(lambda y: y*scale,x)), word['boxes']))
        result.append({'boxes': new_boxes, 'recognition_words': word['recognition_words']})
    return result