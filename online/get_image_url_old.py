import boto3
# from boto3.dynamodb.conditions import BeginsWith, Key
import base64
import sys
sys.path.append('../')
from common.aws.dynamodb.queryBySortKey import queryBySortKey
from const import const

import time


def get_image_url(id):
    return queryBySortKey(id)


if __name__ == '__main__':
    get_image_url('20210829124036')
