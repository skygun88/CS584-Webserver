import os
import time
import random
import sqlite3
import datetime
from PIL import Image
from ocr_model.new_google_model import googlestar_request
from ocr_model.recog_utils import add_dash
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
def ocr(request, content=None):
    print('googlestar_ocr API executed')
    print(request.POST, request.FILES)
    result = {'status': 'FAIL'}
    if request.method == 'POST':
        ''' Get request information from json '''
        user_id = request.POST.get('user_email')
        user_id = 'NULL' if user_id == None else user_id

        print(user_id)
        ori_img = request.FILES.get('img')

        ''' Set the path '''
        currtime = str(datetime.datetime.now()).replace('.', '_').replace(' ', '_').replace(':', '')

        ori_img_dir = 'googlestar_ori/'
        result_img_dir = 'googlestar_result/'
        cropped_dir = 'googlestar_cropped/'+currtime

        abs_ori_img_dir = settings.MEDIA_ROOT+'/'+ori_img_dir
        abs_result_img_dir = settings.MEDIA_ROOT+'/'+result_img_dir
        abs_cropped_dir = settings.MEDIA_ROOT+'/'+cropped_dir

        ''' Make uncreated directory'''
        if not os.path.isdir(abs_ori_img_dir):
            os.mkdir(abs_ori_img_dir)
        if not os.path.isdir(abs_result_img_dir):
            os.mkdir(abs_result_img_dir)
        if not os.path.isdir(abs_cropped_dir):
            os.makedirs(abs_cropped_dir)

        abs_ori_img_path = abs_ori_img_dir+currtime+'.jpg'
        abs_result_img_path = abs_result_img_dir+currtime+'.jpg'

        try:
            ''' Save received image & Resize the image '''
            default_storage.save(abs_ori_img_path, ContentFile(ori_img.read()))

            detected_pn = googlestar_request(abs_ori_img_path, abs_result_img_path, abs_cropped_dir)
        
        except Exception as e:
            print(e)
            return JsonResponse(result)

        try:
            ''' Save request data to DB '''
            conn = sqlite3.connect(settings.DB_ROOT)
            cur = conn.cursor()

            # Calculate request_index
            cur.execute(f"SELECT request_index FROM googlestar_requestinfo;")
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
                            abs_result_img_path, # result_img_path
                            detected_pn['n_results'], # detected_numbers
                            False, # is_response
                            -1, # selected_pn_index
                            '', # called_number
                            -1, # timestamp1
                            -1, # timestamp2
                            -1, # timestamp3
                            -1, # timestamp4
                            request_index, # root_requst_index
                            )

            # save request data to RequestInfo Table
            cur.execute('''INSERT INTO googlestar_requestinfo (request_index, 
                                                            user_id, 
                                                            ori_img_path, 
                                                            result_img_path, 
                                                            detected_numbers, 
                                                            is_response, 
                                                            selected_pn_index, 
                                                            called_number,
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
            response_data = {'n_results': detected_pn['n_results'], 'results': []}
            for number_index, pn in enumerate(detected_pn['results']):
                is_area_code = 1 if pn['area_code'][0] == 1 else 0
                numbers = list(map(lambda x, y: add_dash(x, y), pn['numbers'], pn['area_code']))
                
                ## EX1 - randomly shuffle the number list
                random.shuffle(numbers)
                n_candidates = pn['n_candidates']
                pos1_x, pos1_y = float(pn['boxes'][0][0]), float(pn['boxes'][0][1])
                pos2_x, pos2_y = float(pn['boxes'][1][0]), float(pn['boxes'][1][1])
                pos3_x, pos3_y = float(pn['boxes'][2][0]), float(pn['boxes'][2][1])
                pos4_x, pos4_y = float(pn['boxes'][3][0]), float(pn['boxes'][3][1])

                cur = conn.cursor()
                cur.execute(f"SELECT detected_index FROM googlestar_detectednumbers;")
                detected_idx_list = list(map(lambda x: x[0], cur.fetchall()))
                detected_index = 0
                if len(detected_idx_list) != 0:
                    for idx in detected_idx_list:
                        if idx > detected_index:
                            break
                        detected_index += 1

                detected_numbers_data = (detected_index,
                                            request_index, 
                                            number_index, 
                                            is_area_code, 
                                            n_candidates, 
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
                cur.execute('''INSERT INTO googlestar_detectednumbers (detected_index,
                                                                    request_index, 
                                                                    number_index, 
                                                                    is_area_code, 
                                                                    n_candidates, 
                                                                    pos1_x, 
                                                                    pos1_y, 
                                                                    pos2_x, 
                                                                    pos2_y, 
                                                                    pos3_x, 
                                                                    pos3_y, 
                                                                    pos4_x, 
                                                                    pos4_y) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', detected_numbers_data)
                conn.commit()
            
                for candidate_index, number in enumerate(numbers):
                    candidates_data = (detected_index,
                                        candidate_index,
                                        number,
                                        )
                    cur = conn.cursor()
                    cur.execute('''INSERT INTO googlestar_candidates (detected_index,
                                                                        candidate_index, 
                                                                        number) 
                                    VALUES (?, ?, ?);''', candidates_data)
                    conn.commit()

                response_data['results'].append({'area_code': is_area_code, 
                                                'numbers': numbers,
                                                'n_candidates': n_candidates,
                                                'pos1_x': pos1_x, 'pos1_y': pos1_y,
                                                'pos2_x': pos2_x, 'pos2_y': pos2_y,
                                                'pos3_x': pos3_x, 'pos3_y': pos3_y,
                                                'pos4_x': pos4_x, 'pos4_y': pos4_y,
                                                })

        except Exception as e:
            print(e)
            return JsonResponse(result)
        
        result['status'] = 'OK'
        result['index'] = request_index
        result = {**result, **response_data}
        
        for x in result['results']:
            print(x)

    return JsonResponse(result)


@method_decorator(csrf_exempt, name='dispatch')
def user_data(request, content=None):
    print('googlestar user_data API executed')
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
        selected_pn_index = int(request_dict.get('position'))
        called_number = request_dict.get('number')
        root_request_index = int(request_dict.get('root_index'))
        
        print(called_number)
        try:
            ''' Updata DB based on received data '''
            conn = sqlite3.connect(settings.DB_ROOT)
            cur = conn.cursor()

            cur.execute(f'''UPDATE googlestar_requestinfo 
                            SET  
                            is_response=True,  
                            selected_pn_index={selected_pn_index}, 
                            called_number=\'{called_number}\',
                            timestamp1={timestamp1}, 
                            timestamp2={timestamp2}, 
                            timestamp3={timestamp3}, 
                            timestamp4={timestamp4}, 
                            root_request_index={root_request_index} 
                            WHERE request_index={request_index};''')
            conn.commit()
        except Exception as e:
            print(e)
            conn.close()
            return JsonResponse(result)
        conn.close()

        result['status'] = 'OK'

    return JsonResponse(result)