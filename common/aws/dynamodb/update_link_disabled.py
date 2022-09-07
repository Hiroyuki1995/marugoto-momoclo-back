import boto3

# 現状、指定した人物のgroupカラムをmomocloにする仕様


def update_link_disabled(table_name: str,id: str, client=None):
    if not client:
        client = boto3.client('dynamodb')
    response = client.update_item(
            TableName=table_name,
            Key={
                'group': {
                    'S': "momoclo"
                },
                'id': {
                    'S': id
                }
            },
            AttributeUpdates={
                'disabled': {
                    'Value': {
                        'BOOL': True,
                    },
                    'Action': 'PUT'  # | 'PUT' | 'DELETE'
                },
            },
            ReturnValues='UPDATED_NEW',
        )
    print("response",response)
    return response

if __name__ == '__main__':
    update_link_disabled(table_name ="Links", id="20220901163735813")
