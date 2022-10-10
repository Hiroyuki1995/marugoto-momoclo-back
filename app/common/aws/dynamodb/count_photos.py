import boto3


def count_photos(table_name, person, date, client=None):
    # DynamoDBで対象のデータを検索
    if not client:
        dbClient = boto3.client('dynamodb')
    response = dbClient.query(
        TableName=table_name,
        # ScanIndexForward=False,
        Select='COUNT',
        # PaginationConfig={
        #     'MaxItems': 8,
        #     'PageSize': 8,
        # },
        KeyConditionExpression="person = :keyVal AND begins_with(#id, :idVal)",
        ExpressionAttributeNames={"#id": "id"},
        ExpressionAttributeValues={
            ':keyVal': {'S': person},
            ':idVal': {'S': str(date)},
        },
        # ConditionalOperator='AND',
    )

    print(response['Count'])
    return response['Count']


if __name__ == '__main__':
    count_photos('Photos', 'takagireni', 20210917231810)
