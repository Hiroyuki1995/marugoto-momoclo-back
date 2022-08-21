# DynamoDBのcreate_tableの仕様
# https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_CreateTable.html
# Capacity Unit(CU)の仕様
# 無料枠は読取CU、書込CUともに25CUまで。オンデマンドモードは無料枠外
# RCU: 項目のサイズが 4 KB までなら、RCU 1 個で、結果整合性のある読み込み要求を 1 秒あたり 2 回実行可能
# WCU: 項目のサイズが 1 KB までなら、WCU 1 個で、標準の書き込み要求を 1 秒あたり 1 回実行可能
# https://aws.amazon.com/jp/dynamodb/pricing/provisioned/
import asyncio
import boto3

# iamgesテーブルを作成する。存在する場合は削除処理を行う


async def create_image_table(dynamodb=None):
    if not dynamodb:
        client = boto3.client('dynamodb')
        resource = boto3.resource('dynamodb')
    existing_tables = client.list_tables()['TableNames']

    print(existing_tables)
    table_name = 'Photos'
    images_def = {
        'TableName': table_name,
        'KeySchema': [
            {
                'AttributeName': 'person',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'date',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        'AttributeDefinitions': [
            {
                'AttributeName': 'person',
                'AttributeType': 'S'  # N | S | B; N:Number/ S:String/ B:Binary
            },
            {
                'AttributeName': 'date',
                'AttributeType': 'N'
            },
        ],
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 1,  # 各テーブル合計25を超えると課金発生
            'WriteCapacityUnits': 1  # 各テーブル合計25を超えると課金発生
        }
    }

    if table_name in existing_tables:
        client.delete_table(TableName=table_name)
        # テーブルが削除されるまで待つ
        # 複数テーブルを書き換える場合は時間がかかると思われるので、その際は並行処理を検討する
        waiter = client.get_waiter('table_not_exists')
        waiter.wait(TableName=table_name)

    dict = resource.create_table(
        TableName=images_def['TableName'],
        KeySchema=images_def['KeySchema'],
        AttributeDefinitions=images_def['AttributeDefinitions'],
        ProvisionedThroughput=images_def['ProvisionedThroughput']
    )
    # print(dict)
    print(dict.table_status)


if __name__ == '__main__':
    asyncio.run(create_image_table())
    # print("Table status:", movie_table)
