import boto3
from boto3.dynamodb.conditions import BeginsWith, Key
import base64

import time
import sys
import os
sys.path.append('../../../')
from const import const


def get_notification(device_token):
    """
    デバイストークンをキーに通知情報を取得する。
    データが存在しない場合は、空の辞書を返却する。
    returnSecretInfoがFalseの場合は、keyが'_arn'で終わる項目は返却しない
    """
    # DynamoDBで対象のデータを検索
    client = boto3.client('dynamodb')
    # paginator = dbClient.get_paginator('query')
    args = {
        'TableName': os.environ["NOTIFICATIONS_TABLE_NAME"],
        'Key': {
            "device_token": {
                'S': device_token
            },
        }
    }
    response = client.get_item(**args)

    if 'Item' in response:
        return response['Item']
    else:
        print('該当のデータは見つかりませんでした。')
        return {}


if __name__ == '__main__':
    get_notification(
        'c00a07b11996668ee8e954b3f4cc6d199f53ca67cbd3d7b398de0ce63b73354c')
