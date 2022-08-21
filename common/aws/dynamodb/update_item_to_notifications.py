import boto3
from .query import query
import sys
import os
sys.path.append('../../../')
from const import const
# 現状、指定した人物のgroupカラムをmomocloにする仕様


def update_item_to_notifications(device_token, item, client=None):
    table_name = os.environ["NOTIFICATIONS_TABLE_NAME"]
    if not client:
        client = boto3.client('dynamodb')
    AttributeUpdates = {}
    for k, v in item.items():
        value_type = v['type']
        value = v['value']
        AttributeUpdates[k] = {
            'Value': {
                value_type: value,
            },
            'Action': 'PUT'  # | 'PUT' | 'DELETE'
        }
    response = client.update_item(
        TableName=table_name,
        Key={
            'device_token': {
                'S': device_token
            },
        },
        AttributeUpdates=AttributeUpdates,
        # ConditionalOperator='AND' | 'OR',
        # 'NONE' | 'ALL_OLD' | 'UPDATED_OLD' | 'ALL_NEW' | 'UPDATED_NEW',
        ReturnValues='UPDATED_NEW',
        # ReturnConsumedCapacity='INDEXES' | 'TOTAL' | 'NONE',
        # ReturnItemCollectionMetrics='SIZE' | 'NONE',
        # UpdateExpression='string',
        # ConditionExpression='string',
        # ExpressionAttributeNames={
        #     'string': 'string'
        # },
        # ExpressionAttributeValues={
        #     'string': {
        #         'S': 'string',
        #         'N': 'string',
        #         'B': b'bytes',
        #         'SS': [
        #             'string',
        #         ],
        #         'NS': [
        #             'string',
        #         ],
        #         'BS': [
        #             b'bytes',
        #         ],
        #         'M': {
        #             'string': {'... recursive ...'}
        #         },
        #         'L': [
        #             {'... recursive ...'},
        #         ],
        #         'NULL': True | False,
        #         'BOOL': True | False
        #     }
        # }
    )


if __name__ == '__main__':
    update_item_to_notifications()
