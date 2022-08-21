import boto3
# from boto3.dynamodb.conditions import BeginsWith, Key
import base64
import sys
sys.path.append('../')
from common.aws.s3.get_image_object import get_image_object
from const import const

import time


def get_image_page_data(exclusiveStartKey=dict(), person='all'):
    table_name = const.PHOTOS_TABLE_NAME

    print(f'person {person}')
    # 開始時間を記録
    start = time.time()
    print(f'exclusiveStartKey {exclusiveStartKey} {type(exclusiveStartKey)}')
    # DynamoDBで対象のデータを検索
    dbClient = boto3.client('dynamodb')
    # if person == 'all':
    #   paginator = dbClient.get_paginator('scan')
    # else:
    paginator = dbClient.get_paginator('query')
    args = {
        'TableName': table_name,
        'ScanIndexForward': False,
        'PaginationConfig':
        {
            'MaxItems': 8,
            'PageSize': 8,
        },
        # 'KeyConditionExpression': Key('person').eq(person)
    }
    # exclusiveStartKeyが指定されいれば、検索条件に追加する
    if exclusiveStartKey != dict():
        args['ExclusiveStartKey'] = exclusiveStartKey

    # personが指定されていれば、ファーストパーティションキーに条件を追加する
    if person != 'all':
        print('person is specified')
        args['KeyConditionExpression'] = "person = :keyVal"
        args['ExpressionAttributeValues'] = {
            ':keyVal': {'S': person},
        }

    # personが指定されていなければ、セカンドパーティションキーに条件を追加する
    else:
        print('person is NOT specified')
        args['IndexName'] = 'group-date-index'
        args['ExpressionAttributeNames'] = {
            "#group": "group"
        }
        args['KeyConditionExpression'] = "#group = :keyVal"
        args['ExpressionAttributeValues'] = {
            ':keyVal': {'S': 'momoclo'},
        }

    response = paginator.paginate(**args)
    # 処理にかかった時間を計測
    elapsed_time = time.time() - start
    print("DynamoDBからのデータ取得にかかった時間:{0}".format(elapsed_time) + "[sec]")

    start = time.time()

    s3Client = boto3.client('s3', aws_access_key_id=const.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=const.AWS_SECRET_ACCESS_KEY)
    print(type(response))
    print(response)
    for page in response:  # ループにするが、回すのは１回（１ページ分）
        # print(page)
        # 次のデータがあるかどうかは、LastEvaluatedKeyがどうかで決まる。MaxItemとPageSizeは同じで良い！
        response_data = {}
        if "LastEvaluatedKey" in page:
            print(f'page: {page["LastEvaluatedKey"]}')
            response_data['LastEvaluatedKey'] = page["LastEvaluatedKey"]
        print(f'page: {page["Count"]}')

        response_data['items'] = []
        index = 0
        for item in page['Items']:
            index = index + 1
            if index > 8:
                break
            id: str = item['id']['S']
            fileName: str = item['fileName']['S']
            width: int = item['width']['N']
            height: int = item['height']['N']
            person: str = item['person']['S']
            caption: str = item['caption']['S'] if 'caption' in item else ""
            date: int = item['date']['N']
            category: str = item['category']['S']
            extension: str = item['extension']['S']
            print(id)
            mediaId: int = item.get('instagram_mediaid', {}).get('N')
            base64image = base64.b64encode(get_image_object(
                fileName, s3Client).read()).decode('utf-8')
            response_data['items'].append(
                {
                    "id": id,
                    "fileName": fileName,
                    "person": person,
                    "date": date,
                    "category": category,
                    "width": width,
                    "height": height,
                    "caption": caption,
                    "image": base64image,
                    "extension": extension,
                    "mediaId": mediaId,
                })

        # 処理にかかった時間を計測
        elapsed_time = time.time() - start
        print("S3からのデータ取得にかかった時間:{0}".format(elapsed_time) + "[sec]")
        return response_data


if __name__ == '__main__':
    get_image_page_data(dict(), 'takagireni')
