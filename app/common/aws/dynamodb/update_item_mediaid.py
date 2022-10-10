import boto3
from .query import query

# 現状、指定した人物のgroupカラムをmomocloにする仕様


def update_item(table_name: str, person: str, id: str, mediaid: int, client=None):
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
                'instagram_mediaid': {
                    'Value': {
                        'N': str(mediaid),
                    },
                    'Action': 'PUT'  # | 'PUT' | 'DELETE'
                },
            },
            ReturnValues='UPDATED_NEW',
        )


# if __name__ == '__main__':
#     update_item()
