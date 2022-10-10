import boto3
# from boto3.dynamodb.conditions import BeginsWith, Key
import base64
import sys
sys.path.append('../')
from common.aws.s3.get_image_object import get_image_object
from const import const

import time


def get_links(includeDisabled: bool):
    table_name = const.LINKS_TABLE_NAME

    # 開始時間を記録
    start = time.time()
    # DynamoDBで対象のデータを検索
    dbClient = boto3.client('dynamodb')
    paginator = dbClient.get_paginator('scan')
    args = {
        'TableName': table_name,
        'IndexName' : 'order-index',
        # 'ScanIndexForward': True,
        'PaginationConfig':
        {
            'MaxItems': 30,
            'PageSize': 30,
        },
        'ExpressionAttributeNames':{
            "#group": "group",
        },
        'FilterExpression': "#group = :keyVal",
        'ExpressionAttributeValues': {
        ':keyVal': {'S': 'momoclo'},
        }
    }
    if (includeDisabled == False ):
      args["ExpressionAttributeNames"]["#disabled"] = "disabled"
      args["FilterExpression"] = "#group = :keyVal and #disabled = :disabledVal"
      args["ExpressionAttributeValues"][':disabledVal'] = {'BOOL': False}
    
    print('args',args)

    response = paginator.paginate(**args)
    # print(type(response))
    # print(response)
    for page in response:  # ループにするが、回すのは１回（１ページ分）
        response_data = {}
        response_data['items'] = []
        index = 0
        for item in page['Items']:
            index = index + 1
            group: int = item.get("group", {}).get('S')
            id: str = item.get("id", {}).get('S')
            order: str = item.get("order", {}).get('N')
            category: str = item.get("category", {}).get('S')
            name: int = item.get("name", {}).get('S')
            url: str = item.get("url", {}).get('S')
            disabled: bool = item.get("disabled", {}).get('BOOL')
            response_data['items'].append(
                {
                  "group": group,
                  "id":id,
                  "order":order,
                  "category": category,
                  "name": name,
                  "url": url,
                  "disabled":disabled,
                })

        # 処理にかかった時間を計測
        elapsed_time = time.time() - start
        print("DynamoDBからのデータ取得にかかった時間:{0}".format(elapsed_time) + "[sec]")
        print('response_data',response_data)
        return response_data


if __name__ == '__main__':
    get_links()
