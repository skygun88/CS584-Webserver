import os
from sqlite3.dbapi2 import Timestamp
import sys
import json
import time
import base64
import sqlite3
import datetime
from PIL import Image
from .utils import *
from .recog_utils import *
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
def kakao_ocr(request, content=None):
    print('kakao_ocr API executed')
    print(request.POST, request.FILES)
    result = {'status': 'FAIL'}
    # print(request.json())
    if request.method == 'POST':
        ''' Get request information from json '''
        user_id = request.POST.get('user_email')
        user_id = 'NULL' if user_id == None else user_id



        print(user_id)
        ori_img = request.FILES.get('img')

        ''' Set the path '''
        currtime = str(datetime.datetime.now()).replace('.', '_').replace(' ', '_').replace(':', '')
        ori_img_dir = 'ori/'
        resized_img_dir = 'resized/'
        result_img_dir = 'result/'

        abs_ori_img_dir = settings.MEDIA_ROOT+'/'+ori_img_dir
        abs_resized_img_dir = settings.MEDIA_ROOT+'/'+resized_img_dir
        abs_result_img_dir = settings.MEDIA_ROOT+'/'+result_img_dir

        ''' Make uncreated directory'''
        if not os.path.isdir(abs_ori_img_dir):
            os.mkdir(abs_ori_img_dir)
        if not os.path.isdir(abs_resized_img_dir):
            os.mkdir(abs_resized_img_dir)
        if not os.path.isdir(abs_result_img_dir):
            os.mkdir(abs_result_img_dir)

        abs_ori_img_path = abs_ori_img_dir+currtime+'.jpg'
        abs_resized_img_path = abs_resized_img_dir+currtime+'.jpg'
        abs_result_img_path = abs_result_img_dir+currtime+'.jpg'
        
        try:
            ''' Save received image & Resize the image '''
            default_storage.save(abs_ori_img_path, ContentFile(ori_img.read()))
            ratio = kakao_ocr_resize(abs_ori_img_path, abs_resized_img_path)

            ''' OCR processing through KaKao API '''
            output = kakao_api_request(abs_resized_img_path)
            fail_cnt = 0
            while output.status_code != 200:
                fail_cnt += 1
                if fail_cnt > 5:
                    return JsonResponse(result)
                time.sleep(10)
                output = kakao_api_request(abs_resized_img_path)
            
            ''' Save result img with Bbox '''
            detected_words = output.json()['result']
            new_output = {'result': convert_bbox_scale(detected_words, ratio)}
            # print(new_detected_words)

            result_img = Image.open(abs_ori_img_path)
            for box in new_output['result']:
                result_img = pil_draw_box(result_img, box['boxes'])
            result_img.save(abs_result_img_path)

            detected_pn = pn_detector(new_output)
        except Exception as e:
            print(e)
            return JsonResponse(result)

        try:
            ''' Save request data to DB '''
            conn = sqlite3.connect(settings.DB_ROOT)
            cur = conn.cursor()

            # Calculate request_index
            cur.execute(f"SELECT request_index FROM kakao_requestinfo;")
            idx_list = list(map(lambda x: x[0], cur.fetchall()))
            request_index = 0
            if len(idx_list) != 0:
                for idx in idx_list:
                    if idx > request_index:
                        break
                    request_index += 1

            # Organize the data format
            request_data = (request_index, # request_index
                            user_id, # user_id
                            abs_ori_img_path, # ori_img_path
                            abs_resized_img_path, # resized_img_path
                            abs_result_img_path, # result_img_path
                            detected_pn['n_results'], # detected_numbers
                            False, # is_response
                            -1, # selected_pn_index
                            -1, # timestamp1
                            -1, # timestamp2
                            -1, # timestamp3
                            -1, # timestamp4
                            request_index, # root_requst_index
                            )

            # save request data to RequestInfo Table
            cur.execute('''INSERT INTO kakao_requestinfo (request_index, 
                                                            user_id, 
                                                            ori_img_path, 
                                                            resized_img_path, 
                                                            result_img_path, 
                                                            detected_numbers, 
                                                            is_response, 
                                                            selected_pn_index, 
                                                            timestamp1, 
                                                            timestamp2, 
                                                            timestamp3, 
                                                            timestamp4, 
                                                            root_request_index) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', request_data)
            conn.commit()
        except Exception as e:
            print(e)
            conn.close()
            return JsonResponse(result)

        try:
            ''' Save detecetd number data '''
            response_data = {'n_results': detected_pn['n_results'], 'results': []}
            for number_index, pn in enumerate(detected_pn['results']):
                is_area_code = True if pn['area_code'] == 1 else False
                number = pn['numbers']
                pos1_x, pos1_y = pn['boxes'][0][0], pn['boxes'][0][1]
                pos2_x, pos2_y = pn['boxes'][1][0], pn['boxes'][1][1]
                pos3_x, pos3_y = pn['boxes'][2][0], pn['boxes'][2][1]
                pos4_x, pos4_y = pn['boxes'][3][0], pn['boxes'][3][1]

                detected_numbers_data = (request_index, 
                                            number_index, 
                                            is_area_code, 
                                            number, 
                                            pos1_x, 
                                            pos1_y, 
                                            pos2_x, 
                                            pos2_y, 
                                            pos3_x, 
                                            pos3_y, 
                                            pos4_x, 
                                            pos4_y, 
                                            )
                cur = conn.cursor()
                cur.execute('''INSERT INTO kakao_detectednumbers (request_index, 
                                                                    number_index, 
                                                                    is_area_code, 
                                                                    number, 
                                                                    pos1_x, 
                                                                    pos1_y, 
                                                                    pos2_x, 
                                                                    pos2_y, 
                                                                    pos3_x, 
                                                                    pos3_y, 
                                                                    pos4_x, 
                                                                    pos4_y) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', detected_numbers_data)
                conn.commit()

                response_data['results'].append({'area_code': pn['area_code'], 'numbers': pn['numbers'], 
                                                    'pos1_x': pos1_x, 'pos1_y': pos1_y,
                                                    'pos2_x': pos2_x, 'pos2_y': pos2_y,
                                                    'pos3_x': pos3_x, 'pos3_y': pos3_y,
                                                    'pos4_x': pos4_x, 'pos4_y': pos4_y,
                                                    })
        except Exception as e:
            print(e)
            conn.close()
            return JsonResponse(result)

        conn.close()
        result['status'] = 'OK'
        result['index'] = request_index


        result = {**result, **response_data}
        print(result)

    # conn.close()
    return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
def user_data(request, content=None):
    print('user_data API executed')
    result = {'status': 'FAIL'}
    if request.method == 'POST':
        ''' Data query '''
        # request_dict = json.loads(request.body)
        request_dict = request.POST


        print(request_dict)
        request_index = int(request_dict.get('index'))
        timestamp1 = int(request_dict.get('timestamp1'))
        timestamp2 = int(request_dict.get('timestamp2'))
        timestamp3 = int(request_dict.get('timestamp3'))
        timestamp4 = int(request_dict.get('timestamp4'))
        # selected_pn_index = int(request_dict.get('position'))
        root_request_index = int(request_dict.get('root_index'))
        # selected_number = request_dict.get('numbers')

        # print(request_index, type(request_index))
        # print(root_request_index, type(root_request_index))
        # print(request_index, timestamp1, timestamp2, timestamp3, timestamp4, selected_pn_index, root_request_index)
        
        # try:
        #     ''' Updata DB based on received data '''
        #     conn = sqlite3.connect(settings.DB_ROOT)
        #     cur = conn.cursor()

        #     cur.execute(f'''UPDATE kakao_requestinfo 
        #                     SET  
        #                     is_response=True,  
        #                     selected_pn_index={selected_pn_index}, 
        #                     timestamp1={timestamp1}, 
        #                     timestamp2={timestamp2}, 
        #                     timestamp3={timestamp3}, 
        #                     timestamp4={timestamp4}, 
        #                     root_request_index={root_request_index} 
        #                     WHERE request_index={request_index};''')
        #     conn.commit()
        # except Exception as e:
        #     print(e)
        #     conn.close()
        #     return JsonResponse(result)
        # conn.close()

        result['status'] = 'OK'

    return JsonResponse(result)

