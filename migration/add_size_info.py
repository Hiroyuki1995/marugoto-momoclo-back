# 本ファイルを実行するには、以下２コマンドを実行しライブラリをインストールする必要がある。
# pip install opencv-python
# pip install nmpy

# DynamoDBに登録されているレコードに紐づくS3のファイルの幅・高さを取得し、DynamoDBにカラム登録するファイル

import instaloader
import sys
import datetime
from itertools import dropwhile, takewhile
import glob
import boto3
import base64
import io
import PIL
from PIL import Image
import cv2
import numpy as np

sys.path.append('../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const
from common.aws.s3.upload_file import upload_file
from common.aws.dynamodb.put_items import put_items


# AWS上で関数が呼ばれる時は、引数なし。Lambda内のルートパスを指定
def add_size_info():
    # 1.S3のファイルをダウンロード
    # 1.DynamoDBのデータを全て取得
    dbClient = boto3.client('dynamodb')
    args = {
        'TableName': 'Photos',
        # 'ScanIndexForward': False,
    }
    # args['IndexName'] = 'group-date-index'
    # args['ExpressionAttributeNames'] = {
    #     "#group": "group"
    # }
    # args['KeyConditionExpression'] = "#group = :keyVal"
    # args['ExpressionAttributeValues'] = {
    #     ':keyVal': {'S': 'momoclo'},
    # }
    args['ExpressionAttributeNames'] = {
        "#category": "category"
    }
    args['FilterExpression'] = "#category = :keyVal"
    args['ExpressionAttributeValues'] = {
        ':keyVal': {'S': 'posts'},
    }

    response = dbClient.scan(**args)
    s3Client = boto3.client('s3', aws_access_key_id=const.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=const.AWS_SECRET_ACCESS_KEY)
    print(f'response {response}')
    count = 0
    for item in response['Items']:
        count = count + 1
        person = item['person']['S']
        id = item['id']['S']
        date = item['date']['N']
        print(f'person {person} date {date} id {id}')
        fileName = item['fileName']['S']
        if fileName.endswith('jpg'):
            # print(item['fileName']['S'])
            fileBody = s3Client.get_object(
                Bucket='marugoto-momoclo', Key=fileName)['Body']
            # return file['Body']
            base64image = base64.b64encode(fileBody.read()).decode('utf-8')
            imgdata = base64.b64decode(base64image)
            # im = Image.open(io.BytesIO(imgdata))

            jpg = np.frombuffer(imgdata, dtype=np.uint8)
            # raw image <- jpg
            img = cv2.imdecode(jpg, cv2.IMREAD_COLOR)

            # img = cv2.imread(f'{file_path}')
            # img = cv2.imdecode(base64image)
            width = img.shape[1]
            height = img.shape[0]

            # width, height = im.size
            print(f'width {width} height {height}')

            response = dbClient.update_item(
                TableName='Photos',
                Key={
                    'person': {
                        'S': person
                    },
                    'id': {
                        'S': id
                    }
                },
                AttributeUpdates={
                    'width': {
                        'Value': {
                            'N': str(width),
                        },
                        'Action': 'PUT'  # | 'PUT' | 'DELETE'
                    },
                    'height': {
                        'Value': {
                            'N': str(height),
                        },
                        'Action': 'PUT'  # | 'PUT' | 'DELETE'
                    }
                },
                ReturnValues='UPDATED_NEW',
            )
            print('update size info')
            # if count > 10:
            #     break
        # break

    # 2.ファイルの幅と高さを算出する
    # 3.同じファイル名のDynamoDBのファイルを探す
    # 4.検索したデータに対し、幅と高さ情報を追加する
    print('finish')


if __name__ == "__main__":
    # ローカルでファイルごと実行した時は、カレントディレクトリ内のtmpフォルダを画像一時保存先とする
    add_size_info()
