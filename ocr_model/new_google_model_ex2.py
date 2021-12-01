from .kakao_utils import *
from .star_utils import *
from .google_utils import *
from .recog_utils import *
from PIL import Image
import time
import os
import numpy as np
import math


def googlestar_request(fname, bbox_fname, cropped_dir):
    ''' Directory setup '''
    # bbox_fname = 'new_bbox/'+fname.split('/')[-1]
    # cropped_dir = 'new_cropped/'+fname.split('/')[-1].split('.')[0]


    ''' Google OCR '''
    output = google_api_request(fname)
    new_output = google_to_kakako(output)

    ''' Calculate rotation angle for each bbox '''
    for x in new_output['result']:
        x_vector = [1, 0]
        vector = (x['boxes'][1][0] - x['boxes'][0][0], x['boxes'][1][1] - x['boxes'][0][1])
        
        unit_vector_1 = x_vector / np.linalg.norm(x_vector)
        unit_vector_2 = vector / np.linalg.norm(vector)
        dot_product = np.dot(unit_vector_1, unit_vector_2)
        sign = -1 if unit_vector_2[1] < 0 else 1

        radian = np.arccos(dot_product)*sign
        x['angle'] = radian


    ori_img = Image.open(fname)

    result_img = ori_img.copy()
    for box in new_output['result']:
        result_img = pil_draw_box(result_img, box['boxes'])
    result_img.save(bbox_fname)


    for i, box in enumerate(new_output['result']):
        radian = box['angle']
        rotation_matrix = np.array([[np.cos(-radian), -np.sin(-radian)], [np.sin(-radian),  np.cos(-radian)]])
        first_point = tuple(np.dot(rotation_matrix, (box['boxes'][0][0], box['boxes'][0][1])))
        last_point = tuple(np.dot(rotation_matrix, (box['boxes'][2][0], box['boxes'][2][1])))
        w, h = last_point[0]-first_point[0], last_point[1]-first_point[1]

        pad = 5 

        rotated = ori_img.rotate(
                                math.degrees(radian), 
                                translate=(-(first_point[0]-pad), -(first_point[1]-pad)), 
                                center=(0, 0), 
                                expand=False)
    
        cropped = rotated.crop((0, 0, w+2*pad, h+2*pad))
        cropped.save(f'{cropped_dir}/{i}.jpg')

    ''' Get result from StarNet '''
    Transformation = 'TPS'
    FeatureExtraction = 'ResNet'
    SequenceModeling = 'BiLSTM'
    Prediction = 'Attn'
    sensitive = True

    star_results = starnet_inference(cropped_dir, Transformation, FeatureExtraction, SequenceModeling, Prediction, sensitive)

    total_output = {'result': list(map(lambda x, y: {'boxes': x['boxes'], 'recognition_words': [x['recognition_words'], y[1]]}, new_output['result'], star_results))}


    detected_pn = multi_pn_detector(total_output)
    for x in detected_pn['results']:
        # print(x)
        detected = x['numbers']
        area_code = x['area_code']

        if detected[0] != detected[1]:
            if area_code[0] == -1:
                del x['area_code'][0]
                del x['numbers'][0]
            elif area_code[1] == -1:
                del x['area_code'][1]
                del x['numbers'][1]
        else:
            del x['area_code'][0]
            del x['numbers'][0]

            
        if len(x['numbers']) > 1:
            new_number = generate_number(x['numbers'][0], x['numbers'][1])
            x['area_code'].append(x['area_code'][0])
            x['numbers'].append(new_number)
        
        x['n_candidates'] = len(x['numbers'])

    return detected_pn

        # box = np.array(x['boxes'])

        # box_w = np.sqrt(np.sum(np.power(box[0]-box[1], 2)))
        # box_h = np.sqrt(np.sum(np.power(box[0]-box[3], 2)))
        # print(box_w, box_h, box_w/box_h)



if __name__ == '__main__':
    start = time.time()
    # fname = 'new_test/test3.jpg'
    fname = 'new_test/test1.png'
    # fname = 'new_test/test2.jpg'
    # fname = 'test1/4.JPG'
    googlestar_request(fname)
    # fnames = sorted(os.listdir('test1'))
    # for fname in fnames:
    #     print(fname)
    #     googlestar_request(f'test1/{fname}')

    print(time.time()-start)
