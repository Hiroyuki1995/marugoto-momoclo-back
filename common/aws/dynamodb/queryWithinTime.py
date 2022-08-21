import boto3


def queryWithinTime(strtime_from, strtime_to):
    dbClient = boto3.client('dynamodb')
    response = dbClient.query(
        TableName='Photos',
        IndexName='group-date-index',
        ScanIndexForward=False,
        # Select='ALL_ATTRIBUTES',
        # KeyConditionExpression='(#id >=:time_from) AND (#id <=:time_to)',
        KeyConditionExpression='#group = :momoclo AND #id BETWEEN :time_from AND :time_to',
        ExpressionAttributeNames={
            "#group": "group",
            "#id": "id"
        },
        ExpressionAttributeValues={
            ':momoclo': {
                'S': 'momoclo',
            },
            ':time_from': {
                'S': strtime_from,
            },
            ':time_to': {
                'S': strtime_to,
            },
        },
    )
    print(response)
    return response


if __name__ == '__main__':
    queryWithinTime('20220802080000', '20220802120000')
