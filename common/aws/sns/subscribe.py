import boto3
import sys
import os
from .create_platform_endpoint import create_platform_endpoint
from .get_endpoint import get_endpoint
args = sys.argv
# TODO 定数ファイルへのパスを考慮
sys.path.append('../../../')
from const import const
from common.aws.dynamodb.put_items import put_items
from common.aws.dynamodb.update_item_to_notifications import update_item_to_notifications
from common.aws.dynamodb.get_notification import get_notification


def subscribe(device_token, sns=None, person=None, notification=True):
    if not sns:
        sns = boto3.resource('sns')
    if not device_token:
        print('デバイストークンが設定されていません')
        return
    notification_info = get_notification(device_token)
    print(f'notification_info {notification_info}')

    # エンドポイントが存在しない場合、初めての登録のため、全てのメンバーの通知をONにする。
    if notification_info == {}:
        print('このエンドポイントを初めて登録します。')
        endpoint_arn = create_platform_endpoint(device_token)
        items = [
            {
                'device_token': device_token,
                'endpoint_arn': endpoint_arn,
            }
        ]
        put_items(os.environ["NOTIFICATIONS_TABLE_NAME"], items)
        print(f'endpoint_arn {endpoint_arn}')
        if (endpoint_arn is not None):
            item = {}
            for k, v in const.TOPIC_ARNS.items():
                # k: メンバー名、v:各メンバー通知用のTopicARN
                print(f'topi_arn {v}')
                topic = sns.Topic(v)
                subscription = topic.subscribe(
                    Protocol='application',
                    Endpoint=endpoint_arn,
                    # Attributes={
                    #     'string': 'string'
                    # },
                    ReturnSubscriptionArn=True
                )
                print(subscription)
                print(subscription.arn)
                item[k] = {'type': 'BOOL', 'value': True}
                item[f'{k}_subscription_arn'] = {
                    'type': 'S', 'value': subscription.arn}

            update_item_to_notifications(device_token, item)

        # return subscription.arn
    # エンドポイントが存在する場合、２回目以降の登録のため、特定のメンバーの通知ON/OFFの切り替えを行う。
    else:
        print('このエンドポイントは既に存在します。')
        # print(person in const.TOPIC_ARNS.keys())
        if person == None:
            # TODO バグのため発報する
            print('通知メンバが指定されていないため、処理を中止します')
            return
        personList = person.split(",")
        for member in personList:
            if not member in const.TOPIC_ARNS.keys():
                # TODO バグのため発報する
                print('誤ったメンバを指定しています。')
                return
            target_topic_arn = const.TOPIC_ARNS[member]
            topic = sns.Topic(target_topic_arn)
            endpoint_arn = notification_info['endpoint_arn']['S']
            if notification == True:
                # 通知をONにする場合はsubscribeする
                subscription = topic.subscribe(
                    Protocol='application',
                    Endpoint=endpoint_arn,
                    ReturnSubscriptionArn=True
                )
                subscription_arn = subscription.arn
            else:
                # 通知をOFFにする場合はunsubscribeする
                print('サブスクライブを解除します')
                subscription_arn = notification_info[f'{member}_subscription_arn']['S']
                client = boto3.client('sns')
                response = client.unsubscribe(
                    SubscriptionArn=subscription_arn
                )
                print(response)
            # 実行した操作をDBに登録する
            item = {}
            item[member] = {'type': 'BOOL', 'value': notification}
            item[f'{member}_subscription_arn'] = {
                'type': 'S', 'value': subscription_arn}
            update_item_to_notifications(device_token, item)
            print(
                f'デバイストークン{device_token}の{member}の通知を{"ON" if notification else "OFF"}にしました')


if __name__ == "__main__":
    # subscribe(platform_endpoint_arn='arn:aws:sns:ap-northeast-1:880515148799:endpoint/APNS_SANDBOX/marugoto-momoclo/2c2f5a03-c1f2-30ce-a07b-35beff347155')
    subscribe(
        device_token='3d9d89bae5f1b699d4ff0c9538e6b28b22748b27d1e5403fd923ded78d023a29')
