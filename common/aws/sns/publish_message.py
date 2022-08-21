import boto3
import sys
import json
args = sys.argv
# TODO 定数ファイルへのパスを考慮
sys.path.append('../../../')
from const import const


def publish_message(message, person, client=None):
    if not message:
        print('message is not defined')
        return

    if not client:
        client = boto3.client('sns')

    apns = {}
    apns_dict = {
        "aps": {
            "alert": message,
            "badge": 1
        },
        "person": person
    }
    message_dict = {
        "default": "デフォルトメッセージ",
        "APNS_SANDBOX": json.dumps(apns_dict),
        "APNS": json.dumps(apns_dict),
    }

    print(f' request json {json.dumps(message_dict)}')

    response = client.publish(
        TopicArn=const.TOPIC_ARNS[person],
        # TargetArn='string',
        # PhoneNumber='string',
        Message=json.dumps(message_dict),
        # Subject='string',
        MessageStructure="json",
    )
    print(f'response {response}')


if __name__ == "__main__":
    publish_message(args[1], args[2])
