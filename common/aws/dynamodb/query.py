import boto3
from boto3.dynamodb.conditions import BeginsWith, Key
import base64

import time


def query(person, exclusiveStartKey=dict()):
    # 開始時間を記録
    # start = time.time()
    # print(f'exclusiveStartKey {exclusiveStartKey} {type(exclusiveStartKey)}')
    # DynamoDBで対象のデータを検索
    dbClient = boto3.client('dynamodb')
    # if person == 'all':
    #   paginator = dbClient.get_paginator('scan')
    # else:
    paginator = dbClient.get_paginator('query')
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
    # if exclusiveStartKey != dict():
    #     args['ExclusiveStartKey'] = exclusiveStartKey
    print('person is specified')
    args['KeyConditionExpression'] = "person = :keyVal"
    # args['KeyConditionExpression'] = Key('person').eq(person)
    args['ExpressionAttributeValues'] = {
        ':keyVal': {'S': person},
    }
    start = time.time()
    response = paginator.paginate(**args)
    elapsed_time = time.time() - start
    print("specified:{0}".format(elapsed_time) + "[sec]")

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

        response_data = []
        for item in page['Items']:
            date = item['date']['N']
            response_data.append(date)

        # 処理にかかった時間を計測
        # elapsed_time = time.time() - start
        # print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
        print(response_data)
        return response_data


if __name__ == '__main__':
    query('takagireni', dict())
