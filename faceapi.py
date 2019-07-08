# -*- coding: utf-8 -*-
import json

import requests

import boto3

import time

import cv2

import os

import re

import shutil

# import http.client
#
# import urllib.request
#
# import urllib.parse

import pymysql
import os
from flask import Flask, flash, render_template, request, jsonify, send_from_directory, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from base64 import decodestring

# import urllib.error

# from multiprocessing import Process, Queue

from azure.storage.blob import BlockBlobService, PublicAccess

app = Flask(__name__)

app.secret_key = "reokfdieonteo"

Authentication_successful = 1

Authentication_warning = 0

Authentication_failed = -1

Queue_empty = 0

pre_confidence = 0


@app.route("/")
def index():
    return render_template("login.html")

# @app.route('/register')
# def add_user_view():
#     return render_template('signup.html')

@app.route("/facestorage", methods=['GET'])
def face_storage_view():
    return render_template("facestorage.html")


@app.route("/cloudupload", methods=['GET', "POST"])
def image_storage():
    bs64_image_string = request.form['image']
    # print(bs64_image_string)
    # if isinstance(bs64_image_string, str):
    #     return jsonify('file invalid')

    print("imagestorage")
    bs64_image_string = bs64_image_string.replace('data:image/png;base64,', '')
    with open("img/15010934.jpg", "wb") as fh:
        fh.write(decodestring(bs64_image_string))
    try:
        # Create the BlockBlockService that is used to call the Blob service for the storage account
        block_blob_service = BlockBlobService(account_name='faceimage12',
                                              account_key='rHXkXqQcTTyd/fxcXxpkACqyBC78qnBxK5FEDgFgC4J3fcmIJ9nkKRiPfSVVWTpR2cRKOkOhS6iarw+VK8Uwjg==')

        # Create a container called 'quickstartblobs'.
        container_name = 'faceimage'
        block_blob_service.create_container(container_name)

        # Set the permission so the blobs are public.
        block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

        # Create a file in Documents to test the upload and download.
        local_path = "img"
        local_file_name = "15010934.jpg"
        full_path_to_file = os.path.join(local_path, local_file_name)

        # Upload the created file, use local_file_name for the blob name
        block_blob_service.create_blob_from_path(container_name, local_file_name, full_path_to_file)

        # Clean up resources. This includes the container and the temp files
        os.remove(full_path_to_file)  # 로컬파일 삭제
        return jsonify(True)
    except Exception as e:
        print(e)
        return jsonify(False )


@app.route('/faceadd', methods=['POST'])
def faceadd():
    success=face_recognation()
    return jsonify(success)


@app.route("/signup", methods=['GET'])
def login_user_view():
    return render_template("signup.html")


@app.route('/add', methods=['POST'])
def add_user():
    try:
        conn = pymysql.connect(host='localhost',
                               port=3306,
                               user='root',
                               passwd='4245',
                               db='capstone',
                               charset='utf8')

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        _name = request.form['inputName']
        _id = request.form['inputId']
        _password = request.form['inputPassword']
        # validate the received values
        if _name and _id and _password and request.method == 'POST':
            # do not save password as a plain text
            # save edits
            sql_verify = "select s_name from student where s_id = %s"
            data_verify = _id
            cursor.execute(sql_verify, data_verify)
            account = cursor.fetchall()
            conn.commit()

            if not len(account):
                sql = "INSERT INTO student(s_name, s_id, s_pwd ) VALUES(%s, %s, %s)"
                data = (_name, _id, _password)
                cursor.execute(sql, data)
                conn.commit()
                flash('User added successfully!')
                return jsonify('success')
            else:
                return jsonify('failed')
        else:
            return 'Error while adding user'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login_user():
    try:
        conn = pymysql.connect(host='localhost',
                               port=3306,
                               user='root',
                               passwd='4245',
                               db='capstone',
                               charset='utf8')

        cursor = conn.cursor(pymysql.cursors.DictCursor)
        _id = request.form['inputId']
        _pwd = request.form['inputPassword']

        # validate the received values
        if _id and _pwd and request.method == 'POST':

            sql = 'SELECT s_id, s_pwd FROM student WHERE s_id = %s and s_pwd = %s'
            cursor.execute(sql, (_id, _pwd))
            result = cursor.fetchone()
            print(result)

            if result:
                return jsonify('success')
            else:
                return jsonify('failed')

        else:
            return 'Error while adding user'
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
    return render_template("login.html")


@app.route("/index", methods=['GET', "POST"])
def index_view():
    print("index")
    database_image_path = os.path.join("/Users/jiwon/desktop/capstone/img/", "15010934.jpg")
    image_download(database_image_path, "15010934.jpg")
    return render_template("index.html")


@app.route("/upload", methods=['GET', "POST"])
def file_upload():
    bs64_image_string = request.form['image']
    global pictureNum
    global failure_count
    # print(bs64_image_string)
    if isinstance(bs64_image_string, str):
        return jsonify('file invalid')

    bs64_image_string = bs64_image_string.replace('data:image/png;base64,', '')
    with open("img/15010934_"+str(pictureNum)+".jpg", "wb") as fh:
        fh.write(decodestring(bs64_image_string))

    # 얼굴인식
    confidence = get_confidence("img/15010934.jpg", "img/15010934_"+str(pictureNum)+".jpg")
    result = result_processing(confidence)

    print(result)

    if result == True:
        pictureNum = pictureNum + 1


    #pictureNum = pictureNum + 1
    if pictureNum > 5:
        pictureNum = 1

    # nom_image = secure_filename(image.filename)
    # image = Image.open(image)

    #
    #
    # img_io = BytesIO()
    # image.save(img_io, extension.upper(), quality=70)
    # img_io.seek(0)

    if result == False :
        failure_count = failure_count + 1

    if result == True:
        failure_count = 0
        return jsonify(Authentication_successful)
    elif failure_count == 1:
        return jsonify(Authentication_warning)
    else:
        return jsonify(Authentication_failed)

    #return jsonify(result)


# 얼굴인식 api
def get_confidence(sourceFile, targetFile):
    client = boto3.client('rekognition',
                          aws_access_key_id="AKIAYTPAQTXKWZZIWHCA",
                          aws_secret_access_key="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"
                          )

    confidence = []  # 인식률 저장 배열

    imageSource = open(sourceFile, 'rb')
    imageTarget = open(targetFile, 'rb')

    try:

        response = client.compare_faces(SimilarityThreshold=10,
                                        SourceImage={'Bytes': imageSource.read()},
                                        TargetImage={'Bytes': imageTarget.read()})
        # print(response)

        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            # confidence = str(faceMatch['Face']['Confidence'])
            similarity = str(faceMatch['Similarity'])
            confidence.append(float(similarity))
            print('The face at ' +
                  str(position['Left']) + ' ' +
                  str(position['Top']) +
                  ' 유사도: ' + similarity)

    except:
        confidence.append(float(0))

    imageSource.close()
    imageTarget.close()

    # for i in confidence:
    #     print(i)
    return confidence


# 유사도를 이용해 얼굴인식 성공 여부 반환 함수

def result_processing(confidence):
    '''

    function!!

    '''
    global pre_confidence
    global pictureNum
    # global pictureNum_max

    # 전 사진이랑 일치율이 같을 경우 실패
    if confidence == pre_confidence:
        return False
    #
    # temp_confidence = 0
    # if pictureNum_max < 5:
    #     for i in range(1, pictureNum):
    #         temp_confidence = temp_confidence + get_confidence("img/15010934_" + str(pictureNum) + ".jpg",
    #                                                            "img/15010934_" + str(i) + ".jpg")
    #     temp_confidence = temp_confidence / (pictureNum - 1)
    # else:
    #     for i in range(1, 6):
    #         if i == pictureNum:
    #             continue
    #         temp_confidence = temp_confidence + get_confidence("img/15010934_" + str(pictureNum) + ".jpg",
    #                                                            "img/15010934_" + str(i) + ".jpg")
    #     temp_confidence = temp_confidence / 4
    # coef_A = 0.7
    # coef_B = 0.3
    # result_confidence = (coef_A * confidence) + (coef_B * temp_confidence)

    # 한 명이라도 성공하면 성공
    for i in confidence:
        if i > 75:
            pre_confidence = confidence
            return True
        else:
            continue

    return False


def image_download(database_image_path,file_name):
    try:
        # Create the BlockBlockService that is used to call the Blob service for the storage account\n",

        block_blob_service = BlockBlobService(account_name='faceimage12',
                                              account_key='rHXkXqQcTTyd/fxcXxpkACqyBC78qnBxK5FEDgFgC4J3fcmIJ9nkKRiPfSVVWTpR2cRKOkOhS6iarw+VK8Uwjg==')

        # Create a container called 'quickstartblobs'.

        container_name = 'faceimage'

        block_blob_service.create_container(container_name)

        # Set the permission so the blobs are public.

        block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

        #지정된 로컬주소에 학번.jpg로 저장

        print("\nDownloading blob to " + database_image_path)
        block_blob_service.get_blob_to_path(container_name, file_name, database_image_path)


    except Exception as e:

        print(e)



def image_storage(path, file_name):
    try:
        # Create the BlockBlockService that is used to call the Blob service for the storage account
        block_blob_service = BlockBlobService(account_name='faceimage12',
                                              account_key='rHXkXqQcTTyd/fxcXxpkACqyBC78qnBxK5FEDgFgC4J3fcmIJ9nkKRiPfSVVWTpR2cRKOkOhS6iarw+VK8Uwjg==')

        # Create a container called 'quickstartblobs'.
        container_name = 'faceimage'
        block_blob_service.create_container(container_name)

        # Set the permission so the blobs are public.
        block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

        # Create a file in Documents to test the upload and download.
        local_path = path
        local_file_name = file_name
        full_path_to_file = os.path.join(local_path, local_file_name)

        # Upload the created file, use local_file_name for the blob name
        block_blob_service.create_blob_from_path(container_name, local_file_name, full_path_to_file)

        # Clean up resources. This includes the container and the temp files
        os.remove(full_path_to_file)  # 로컬파일 삭제
        return True
    except Exception as e:
        print(e)
        return False


# 웹캠화면보여주고 캡쳐해서 이미지 비교
def face_recognation():
    file_name = "15010934.jpg"
    path = "/Users/jiwon/desktop/capstone/img"

    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)

    # Check if camera opened successfully
    if (cap.isOpened() == False):
        print("Unable to read camera feed")

    # Default resolutions of the frame are obtained.The default resolutions are system dependent.
    # We convert the resolutions from float to integer.
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    while (True):

        ret, frame = cap.read()

        if ret == True:
            # Display the resulting frame
            cv2.imshow('frame', frame)

            # Press Q on keyboard to stop recording
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.imwrite(file_name, frame)
                success = image_storage(path, file_name)
                break

        # Break the loop
        else:
            end = True
            break

            # When everything done, release the video capture and video write objects
    cap.release()

    # Closes all the frames
    cv2.destroyAllWindows()

    return success


if __name__ == '__main__':
    pictureNum = 1
    failure_count = 0
    app.run(debug=True)
