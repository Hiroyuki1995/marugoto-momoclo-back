import boto3
from boto3.dynamodb.conditions import BeginsWith, Key
import base64

import time


def queryBySortKey(id):
    # 開始時間を記録
    # start = time.time()
    # DynamoDBで対象のデータを検索
    dbClient = boto3.client('dynamodb')
    paginator = dbClient.get_paginator('query')
    args = {
        'TableName': 'Photos',
        'ScanIndexForward': False,
        'PaginationConfig':
        {
            'MaxItems': 16,
            'PageSize': 16,
        },
        'IndexName': 'id-index',
        'ExpressionAttributeNames': {
            "#id": "id"
        },
        'KeyConditionExpression': "#id = :keyVal",
        'ExpressionAttributeValues': {
            ':keyVal': {'S': id},
        }
    }

    start = time.time()
    response = paginator.paginate(**args)
    elapsed_time = time.time() - start
    # print("specified:{0}".format(elapsed_time) + "[sec]")

    print(type(response))
    print(response)
    for page in response:  # ループにするが、回すのは１回（１ページ分）
        res = {}
        if page['Items'] and page['Items'][0]:
            item = page['Items'][0]
            # print('item', item)

            fileName: str = item['fileName']['S'] if 'fileName' in item else ""
            person: str = item['person']['S'] if 'person' in item else ""
            date: int = item['date']['N'] if 'date' in item else ""
            category: str = item['category']['S'] if 'category' in item else ""
            width: int = item['width']['N'] if 'width' in item else ""
            height: int = item['height']['N'] if 'height' in item else ""
            caption: str = item['caption']['S'] if 'caption' in item else ""
            extension: str = item['extension']['S'] if 'extension' in item else ""
            thumnail: str = item.get("thumnail", {}).get('S')
            mediaId: int = item.get("instagram_mediaid", {}).get('N')
            tweetId: int = item.get("tweet_id", {}).get('N')
            youtubeVideoId: str = item.get("youtube_videoId", {}).get('S')

            res = {
                "fileName": fileName,
                "person": person,
                "date": date,
                "category": category,
                "width": width,
                "height": height,
                "caption": caption,
                "extension": extension,
                "thumnail": thumnail,
                "mediaId": mediaId,
                "tweetId": tweetId,
                "youtubeVideoId": youtubeVideoId,
            }
        return res


if __name__ == '__main__':
    queryBySortKey('20210915031921')
