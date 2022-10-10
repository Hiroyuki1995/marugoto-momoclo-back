import boto3
from .query import query

# 現状、指定した人物のgroupカラムをmomocloにする仕様


def update_item(table_name: str, person: str, id: str, thumnail: str, client=None):
    if not client:
        client = boto3.client('dynamodb')
    # person = 'tamaishiori'
    # res = query(person)
    # for date in res:
        # table = client.Table(table_name)
        response = client.update_item(
            TableName=table_name,
            Key={
                'person': {
                    'S': person
                },
                'id': {
                    'S': id
                }
            },
            AttributeUpdates={
                'thumnail': {
                    'Value': {
                        'S': thumnail,
                    },
                    'Action': 'PUT'  # | 'PUT' | 'DELETE'
                },
            },
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


# if __name__ == '__main__':
#     update_item()
