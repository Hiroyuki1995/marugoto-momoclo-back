# app.py

from flask import Flask, jsonify, request

from online.get_image_page_data import get_image_page_data
from online.get_image_urls import get_image_urls
from common.aws.dynamodb.queryBySortKey import queryBySortKey
from common.aws.sns.subscribe import subscribe
from common.aws.dynamodb.get_notification_for_user import get_notification_for_user
from common.aws.sns.publish_message_to_owner import publish_message_to_owner
import boto3
import json
import traceback


import os
IS_OFFLINE = os.environ.get('IS_OFFLINE')
NOTIFY_ERROR = True
if IS_OFFLINE:
    client = boto3.client(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000'
    )
else:
    client = boto3.client('dynamodb')

from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/photos', methods=['GET'])
def download_images_page():
    print('Other_File', os.environ['Other_File'])
    print('PLATFORM_APPLICATION_ARN', os.environ['PLATFORM_APPLICATION_ARN'])
    try:
        print(
            f'person {request.args.get("person")} {type(request.args.get("person"))}')
        exclusiveStartKey = json.loads(request.args.get('exclusiveStartKey')) if request.args.get(
            'exclusiveStartKey') is not None else dict()
        person = request.args.get('person') if request.args.get(
            'person') is not None else 'all'
        print(f'person {person} {type(person)}')
        return jsonify(get_image_page_data(exclusiveStartKey, person))
    except Exception as e:
        tb = traceback.format_exc()
        message = f'画像の取得中にエラーが発生しました {e} {tb}'
        if (NOTIFY_ERROR):
            publish_message_to_owner(message)
        print(f'catch error {e} {tb}')


@app.route('/photosUrl', methods=['GET'])
def download_image_urls():
    print('Other_File', os.environ['Other_File'])
    print('PLATFORM_APPLICATION_ARN', os.environ['PLATFORM_APPLICATION_ARN'])
    try:
        print(
            f'person {request.args.get("person")} {type(request.args.get("person"))}')
        exclusiveStartKey = json.loads(request.args.get('exclusiveStartKey')) if request.args.get(
            'exclusiveStartKey') is not None else dict()
        person = request.args.get('person') if request.args.get(
            'person') is not None else 'all'
        print(f'person {person} {type(person)}')
        return jsonify(get_image_urls(exclusiveStartKey, person))
    except Exception as e:
        tb = traceback.format_exc()
        message = f'画像の取得中にエラーが発生しました {e} {tb}'
        if (NOTIFY_ERROR):
            publish_message_to_owner(message)
        print(f'catch error {e} {tb}')


@app.route('/photosUrl/<id>', methods=['GET'])
def download_image_url(id):
    print('id', id, 'type', type(id))
    try:
        return jsonify(queryBySortKey(id))
    except Exception as e:
        tb = traceback.format_exc()
        message = f'特定画像の取得中にエラーが発生しました {e} {tb}'
        if (NOTIFY_ERROR):
            publish_message_to_owner(message)
        print(f'catch error {e} {tb}')


@app.route('/deviceToken', methods=['POST'])
def registerNotification():
    """"
    デバイストークンを受け取り、通知設定を行う。
    デバイストークンがエンドポイントとして未登録の場合、全メンバの通知をONにする。
    デバイストークンが登録済の場合、指定されたメンバの通知を指定された設置とする。
    """
    try:
        print(f'request.json {request.json}')
        # deviceToken = request.get_data().deviceToken
        device_token = request.json['deviceToken']
        person = request.json['person'] if 'person' in request.json else None
        notification = request.json['notification'] if 'notification' in request.json else None
        print(f'person {person}')
        print(f'device_token {device_token}')
        subscribe(device_token=device_token,
                  person=person, notification=notification)
        return ('', 204)
    except Exception as e:
        tb = traceback.format_exc()
        message = f'通知設定中にエラーが発生しました {e} {tb}'
        if (NOTIFY_ERROR):
            publish_message_to_owner(message)
        print(f'catch error {e} {tb}')


@app.route('/notifications', methods=['GET'])
def getNotificationSettings():
    """"
    現在の通知設定内容を取得する。
    """
    try:
        print(f'request.json {request.json}')
        # deviceToken = request.get_data().deviceToken
        device_token = request.args.get('deviceToken')
        return get_notification_for_user(device_token)
    except Exception as e:
        tb = traceback.format_exc()
        message = f'通知設定中にエラーが発生しました {e} {tb}'
        if (NOTIFY_ERROR):
            publish_message_to_owner(message)
        print(f'catch error {e} {tb}')


@app.route('/line/events', methods=['POST'])
def postLineEvents():
    """"
    LINE公式アカウントからのイベントを検知する。
    """
    try:
        print(f'request.json {request.json}')
        return ('', 204)
    except Exception as e:
        tb = traceback.format_exc()
        message = f'通知設定中にエラーが発生しました {e} {tb}'
        if (NOTIFY_ERROR):
            publish_message_to_owner(message)
        print(f'catch error {e} {tb}')
