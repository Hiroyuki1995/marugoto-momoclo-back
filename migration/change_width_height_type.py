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
# import cv2
import numpy as np

sys.path.append('../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const
from common.aws.dynamodb.update_item_dimensions import update_item
from common.aws.dynamodb.put_items import put_items


# AWS上で関数が呼ばれる時は、引数なし。Lambda内のルートパスを指定
def change_width_height_type():
    # 1.S3のファイルをダウンロード
    # 1.DynamoDBのデータを全て取得
    dbClient = boto3.client('dynamodb')
    args = {
        'TableName': 'Photos',
        'ScanIndexForward': False,
        # 'PaginationConfig':
        # {
        #     'MaxItems': 8,
        #     'PageSize': 8,
        # },
        # 'KeyConditionExpression': Key('person').eq(person)
    }
    args['IndexName'] = 'group-date-index'
    args['ExpressionAttributeNames'] = {
        "#group": "group"
    }
    args['KeyConditionExpression'] = "#group = :keyVal"
    args['ExpressionAttributeValues'] = {
        ':keyVal': {'S': 'momoclo'},
    }

    response = dbClient.query(**args)
    # s3Client = boto3.client('s3', aws_access_key_id=const.AWS_ACCESS_KEY_ID,
    #                         aws_secret_access_key=const.AWS_SECRET_ACCESS_KEY)
    # print(f'response {response}')
    count = 0
    items = []
    for item in response['Items']:
        if 'S' in item['width']:
            count = count + 1
            print('widthがstr型です。')
            width = int(item['width']['S'])
            height = int(item['width']['S'])
            id = item['id']['S']
            person = item['person']['S']
            update_item('Photos', person, id, width, height)
        elif 'N' in item['width']:
            print('widthがint型です。')
        # break
        # width = item['width']['N']
        # target = '.'
        # idx = fileName.find(target)
        # fileNameWithoutExtension = fileName[:idx]
        # # print(fileNameWithoutExtension)
        # sep = '-'
        # t = fileNameWithoutExtension.split(sep)
        # length = len(t)
        # mediaid = t[length - 1]
        # typeName = t[length - 2]
        # print(typeName)
        # print(mediaid)
        # items.append({
        #     "person": person,
        #     "id": str(date),
        #     "date": date,
        #     "instagram_mediaid": mediaid,
        #     "fileName": fileName,
        #     "group": "momoclo",
        #     "type": typeName,
        #     "width": width,
        #     "height": height,
        #     "category": "stroies",
        # })
    print(count)
    # print([items[0]])
    # put_items(const.PHOTOS_TABLE_NAME, items)

    # 2.ファイルの幅と高さを算出する
    # 3.同じファイル名のDynamoDBのファイルを探す
    # 4.検索したデータに対し、幅と高さ情報を追加する
    print('finish')


if __name__ == "__main__":
    # ローカルでファイルごと実行した時は、カレントディレクトリ内のtmpフォルダを画像一時保存先とする
    change_width_height_type()
