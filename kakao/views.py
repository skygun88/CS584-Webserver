import os
import sys
import json
import time
import base64
import sqlite3
import datetime
from PIL import Image
from .utils import *
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
    result = {'status': 'FAIL'}
    if request.method == 'POST':
        ''' Get request information from json '''
        ori_img = request.FILES.get('img')

        ''' Set the path '''
        currtime = str(datetime.datetime.now()).split('.')[0].replace(' ', '_').replace(':', '')
        ori_img_dir = 'ori/'
        resized_img_dir = 'resized/'
        result_img_dir = 'result/'

        abs_ori_img_dir = settings.MEDIA_ROOT+'/'+ori_img_dir
        abs_resized_img_dir = settings.MEDIA_ROOT+'/'+resized_img_dir
        abs_result_img_dir = settings.MEDIA_ROOT+'/'+result_img_dir

        if not os.path.isdir(abs_ori_img_dir):
            os.mkdir(abs_ori_img_dir)
        if not os.path.isdir(abs_resized_img_dir):
            os.mkdir(abs_resized_img_dir)
        if not os.path.isdir(abs_result_img_dir):
            os.mkdir(abs_result_img_dir)

        abs_ori_img_path = abs_ori_img_dir+currtime+'.jpg'
        abs_resized_img_path = abs_resized_img_dir+currtime+'.jpg'
        abs_result_img_path = abs_result_img_dir+currtime+'.jpg'
        
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
        new_detected_words = convert_bbox_scale(detected_words, ratio)
        print(new_detected_words)

        result_img = Image.open(abs_ori_img_path)
        for box in new_detected_words:
            result_img = pil_draw_box(result_img, box['boxes'])
        result_img.save(abs_result_img_path)
        


        # rotation(abs_ori_img_path)




        # ''' Save request data to DB '''
        # conn = sqlite3.connect("/home/skygun/hci_server/hci_back/db.sqlite3")
        # cur = conn.cursor()

        # # Calculate index
        # cur.execute(f"SELECT idx FROM requests_requestinfo;")
        # idx_list = list(map(lambda x: x[0], cur.fetchall()))
        # idx = 0
        # if len(idx_list) != 0:
        #     while idx in idx_list:
        #         idx += 1
        
        # # Calculate request id
        # cur.execute(f"SELECT rid FROM requests_requestinfo WHERE uid=\'{user_id}\';")
        # rid_list = list(map(lambda x: x[0], cur.fetchall()))
        # request_id = 0
        # if len(rid_list) != 0:
        #     while request_id in rid_list:
        #         request_id += 1
        
        # progress = 0
        # request_data = (idx, user_id, request_id, srcFacePath, srcHairPath, absConvertedPath, progress)

        # cur.execute('INSERT INTO requests_requestinfo (idx, uid, rid, facePath, hairPath, convertedPath, progress) VALUES (?, ?, ?, ?, ?, ?, ?);', request_data)
        # conn.commit()
        # result['request_id'] = request_id
        # result['progress'] = 0


        result['status'] = 'OK'
        result['n_results'] = 2
        result['results'] = {
            '0': {
                'area_code': 0,
                'numbers': '37891357'
            },
            '1': {
                'area_code': 1,
                'numbers': '0314945225'
            }
        }


    # conn.close()
    return JsonResponse(result)




