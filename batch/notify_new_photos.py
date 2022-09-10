import sys
from datetime import datetime, timedelta
from itertools import count, dropwhile, takewhile
import glob
import json
import lzma
import os
import traceback
sys.path.append('../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const
from common.aws.dynamodb.put_items import put_items
from common.aws.dynamodb.count_photos import count_photos
from common.aws.sns.publish_message_to_owner import publish_message_to_owner
from common.aws.sns.publish_message import publish_message
from common.line.broadcast import broadcast
from common.line.message_to_the_user import message_to_the_user
from common.aws.dynamodb.queryWithinTime import queryWithinTime

# AWS上で関数が呼ばれる時は、引数なし。Lambda内のルートパスを指定


def notify_new_photos(event=None, lambda_context=None, doBroadcast = True):
    """"
    直近の00分からhours前の間に登録された写真を集計し、ユーザーに通知する。
    """
    try:
        print('event:' + json.dumps(event))
        hours = 0
        execute_time_str = event['time']
        execute_time_obj = datetime.strptime(
            execute_time_str, '%Y-%m-%dT%H:%M:%SZ')

        # 12:00JSTでは過去15時間分の更新データを取得する、21:00JSTでは過去9時間分の更新データを取得する。それ以外の場合は、取得範囲は6時間。
        if execute_time_obj.hour == 3 and execute_time_obj.minute == 0:
            hours = 15
        elif execute_time_obj.hour == 12 and execute_time_obj.minute == 0:
            hours = 9
        else:
            hours = 6
        execute_time_obj = datetime.utcnow()
        start_time = execute_time_obj - timedelta(hours=hours)

        strtime_to = str(execute_time_obj.year * 10000000000 + execute_time_obj.month *
                         100000000 + execute_time_obj.day * 1000000 + execute_time_obj.hour * 10000)
        strtime_from = str(start_time.year * 10000000000 + start_time.month *
                           100000000 + start_time.day * 1000000 + start_time.hour * 10000)
        print(strtime_from, strtime_to)

        result = queryWithinTime(strtime_from, strtime_to)
        print("Count", result["Count"])
        if result["Count"] > 0:
            text = ""
            notify_photo_id =""
            notif_list_instagram = []
            for person in const.INSTAGRAM_TARGET_USER_LIST.values():
                count_per_person = 0
                for item in result["Items"]:
                    if (item["category"]["S"] == "posts" or item["category"]["S"] == "stories") and item["person"]["S"] == person:
                        count_per_person = count_per_person + 1
                        if notify_photo_id == "":
                            notify_photo_id = item["id"]["S"]
                if count_per_person > 0:
                    notif_list_instagram.append(
                        {"person": const.PERSON_NAME[person], "count": count_per_person})
            if notif_list_instagram != []:
                text = text + "【Instagramが更新されました】\n"
                for notif in notif_list_instagram:
                    text = text + "・" + \
                        notif["person"] + str(notif["count"]) + "枚\n"

            notif_list_twitter = []
            for user in const.TWITTER_TARGET_ACCOUNT_LIST:
                count_per_person = 0
                for item in result["Items"]:
                    if item["category"]["S"] == "tweets" and item["person"]["S"] == user["username"]:
                        count_per_person = count_per_person + 1
                        if notify_photo_id == "":
                            notify_photo_id = item["id"]["S"]
                if count_per_person > 0:
                    notif_list_twitter.append(
                        {"person": user["name"], "count": count_per_person})
            if notif_list_twitter != []:
                text = text + "【Twitterが更新されました】\n"
                for notif in notif_list_twitter:
                    text = text + "・" + \
                        notif["person"] + str(notif["count"]) + "枚\n"

            notif_list_youtube = []
            for channel in const.YOUTUBE_CHANNELS:
                count_per_person = 0
                for item in result["Items"]:
                    if item["category"]["S"] == "youtube#video" and item["person"]["S"] == channel["name"]:
                        count_per_person = count_per_person + 1
                        if notify_photo_id == "":
                            notify_photo_id = item["id"]["S"]
                if count_per_person > 0:
                    notif_list_youtube.append(
                        {"person": channel["name"], "count": count_per_person})
            if notif_list_youtube != []:
                text = text + "【YouTubeが更新されました】\n"
                for notif in notif_list_youtube:
                    text = text + "・" + \
                        notif["person"] + str(notif["count"]) + "枚\n"
            text = text + f"https://www.marugoto-momoclo.com/album/{notify_photo_id}"
            print(text)
            publish_message_to_owner(text)
            # message_to_the_user(
            #     [{'type': 'text', 'text': text}], const.LINE_IWATA_USER_ID)
            if doBroadcast == True:
                broadcast(
                [{'type': 'text', 'text': text}])
    except Exception as e:
        tb = traceback.format_exc()
        message = f'更新情報の通知中にエラーが発生しました {e} {tb}'
        publish_message_to_owner(message)
        print(f'catch error {e} {tb}')
        raise e


if __name__ == "__main__":
    # ローカルでファイルごと実行した時は、カレントディレクトリ内のtmpフォルダを画像一時保存先とする
    notify_new_photos(event = { "time": "2022-09-10T12:00:00Z"},doBroadcast = False)
