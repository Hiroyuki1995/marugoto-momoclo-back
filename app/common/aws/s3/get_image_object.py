# 勉強カフェと自宅のみアクセス可能

import boto3
import sys
sys.path.append('../')
from const import const


def get_image_object(Key, client=None):
    if not client:
        client = boto3.client('s3', aws_access_key_id=const.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=const.AWS_SECRET_ACCESS_KEY)
    file = client.get_object(Bucket='marugoto-momoclo', Key=Key)
    return file['Body']
