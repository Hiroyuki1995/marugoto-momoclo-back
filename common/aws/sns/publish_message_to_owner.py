import boto3
import sys
args = sys.argv


def publish_message_to_owner(message, client=None):
    if not message:
        print('message is not defined')
        return

    if not client:
        client = boto3.client('sns')

    response = client.publish(
        TopicArn='arn:aws:sns:ap-northeast-1:880515148799:marugoto-momoclo-for-owner',
        # TargetArn='string',
        # PhoneNumber='string',
        Message=message,
        Subject='【まるごとももクロ実行状況】',
        # MessageStructure='string',
        # MessageAttributes={
        #     'string': {
        #         'DataType': 'string',
        #         'StringValue': 'string',
        #         'BinaryValue': b'bytes'
        #     }
        # },
        # MessageDeduplicationId='string',
        # MessageGroupId='string'
    )
    print(f'response {response}')


if __name__ == "__main__":
    publish_message_to_owner(args[1])
