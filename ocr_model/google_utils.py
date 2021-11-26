from PIL import Image
from google.cloud import vision
# from google.protobuf.json_format import MessageToJson

import time

def google_api_request(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    return response


def google_to_kakako(google_response):
    text_annotations = google_response.text_annotations[1:]
    kakao_format = list(map(lambda x: {'boxes': list(map(lambda y: (y.x, y.y), x.bounding_poly.vertices)), 'recognition_words': x.description}, text_annotations))
    result = {'result': kakao_format}
    return result
