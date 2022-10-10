# リリースまで日次でストーリーを取得する
import glob
from time import strftime
from boto3 import NullHandler
import instaloader
import sys
import os
import json
import lzma
import traceback
import datetime
import wget
sys.path.append('../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from common.aws.dynamodb.count_photos import count_photos
from common.aws.s3.download_file import download_file
from common.aws.sns.publish_message_to_owner import publish_message_to_owner
from common.aws.sns.publish_message import publish_message
from common.aws.dynamodb.put_items import put_items
from common.aws.s3.upload_file import upload_file
from common.youtube.get_youtube_data import get_youtube_data
from const import const

# AWS上で関数が呼ばれる時は、引数なし。Lambda内のルートパスを指定


def register_youtube_videos(event=None, lambda_context=None, tmp_file_path="/tmp", days=1):
    """
    バッチの起動時刻のdays日前から現在までに登録されているYouTube動画を取得し、DBに登録されていないデータのみ、
    S3へのサムネイルのアップロードおよびメタデータのDBへの登録を行う。
    """
    table_name = const.PHOTOS_TABLE_NAME
    count = 0
    # ex. [{"person":"しおりん", count: 1},{person: "れにちゃん", count: 3}, ...]
    result_list = []
    try:
        execute_time_str = event['time']
        execute_time_obj_utc = datetime.datetime.strptime(
            execute_time_str, '%Y-%m-%dT%H:%M:%SZ')
        publishedAfter_obj = execute_time_obj_utc + \
            datetime.timedelta(days=-1 * days)
        publishedAfter = publishedAfter_obj.isoformat() + "Z"
        print('publishedAfter', publishedAfter)

        for channel in const.YOUTUBE_CHANNELS:
            print('channel_id:', channel["id"])
            print('channel_name:', channel["name"])
            count_per_channel = 0
            for index, item in enumerate(get_youtube_data(publishedAfter=publishedAfter, channelId=channel["id"])):
                print('step 5')

                # Lambdaの/tmpディレクトリのみ書き込み処理が可能。
                # https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html

                # 既にDynamoDBに登録済のものであればダウンロードしない
                date_utc = datetime.datetime.strptime(
                    item["snippet"]["publishedAt"], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y%m%d%H%M%S')

                # person = const.INSTAGRAM_TARGET_USER_LIST[item.owner_id]
                number = count_photos(table_name, channel["name"], date_utc)
                if number > 0:
                    print(
                        f'{channel} {date_utc}に該当するデータが{number}件見つかったため、ファイルのダウンロードを行いません')
                    continue

                # 1. サムネイル画像をtmpフォルダにダウンロード
                print(item["snippet"]["title"])
                thumnail_url = item["snippet"]["thumbnails"]["high"]["url"]
                path, extension_with_dot = os.path.splitext(
                    item['snippet']["thumbnails"]['high']['url'])
                extension = extension_with_dot[1:]
                file_name_with_extension = f"{date_utc}-{channel['name']}-youtube-{item['id']['videoId']}.{extension}"
                wget.download(
                    thumnail_url, out=f"{tmp_file_path}/{file_name_with_extension}")

                # 3. S3にファイルをアップロード
                print('upload ' + file_name_with_extension)
                upload_file(const.USER_BUCKET_NAME, f"{tmp_file_path}/{file_name_with_extension}",
                            file_name_with_extension)
                # DLしたファイル名でアップロード。# Lambdaでは/tmp/...でないといけない

                # 4. アップロードが完了したら、DynamoDBにファイル情報を追加
                items = []
                items.append({
                    "person": channel["name"],  # チャンネルの名称
                    # snippet["publishedAt"]をyyyymmddHHMMSS形式にフォーマット
                    "id": str(date_utc),
                    # snippet["publishedAt"]をyyyymmddHHMMSS形式にフォーマット
                    "date": int(date_utc),
                    # "instagram_mediaid": mediaid,  # なし
                    "youtube_videoId": item["id"]["videoId"],
                    "fileName": file_name_with_extension,
                    "group": "momoclo",
                    "type": item["id"]["kind"],  # id["kind"]
                    "width": item["snippet"]["thumbnails"]["high"]["width"],
                    "height": item["snippet"]["thumbnails"]["high"]["height"],
                    "category": item["id"]["kind"],
                    "extension": extension,
                    "caption": f'{item["snippet"]["title"]}',
                    # "thumnail": thumnail_file_name_with_extension if thumnail_file_name_with_extension is not '' else None,  # なし
                })
                print('items', items)
                put_items(table_name, items)
                count = count + 1
                count_per_channel = count_per_channel + 1

                # 全てのストーリーアイテムをアップロードした後に、tmpディレクトリ内のファイル削除
                # Lambdaでは/tmp/...でないといけない
                for p in glob.glob(f'{tmp_file_path}/' + '*'):
                    if os.path.isfile(p):
                        #  print(p)
                        os.remove(p)
            if count_per_channel > 0:
                # publish_message(
                #     f'{const.PERSON_NAME[channel]}がInstagramにストーリーズを追加しました。', channel)
                result_list.append(
                    {"person": channel["name"], "count": count_per_channel})
        if count > 0:
            text = ''
            for result in result_list:
                text = text + result["person"] + \
                    "が" + str(result["count"]) + "件、"
            text = text + 'YoutTubeの動画を登録しました。\nhttps://www.marugoto-momoclo.com/album/'
            publish_message_to_owner(text)
            # broadcast([{'type': 'text', 'text': text}])
    except Exception as e:
        tb = traceback.format_exc()
        message = f'YouTube動画登録中にエラーが発生しました {e} {tb}'
        publish_message_to_owner(message)
        print(f'catch error {e} {tb}')
        raise e


if __name__ == "__main__":
    # ローカルでファイルごと実行した時は、カレントディレクトリ内のtmpフォルダを画像一時保存先とする
    register_youtube_videos(
        event={"time": "2022-08-19T00:00:00Z"}, tmp_file_path='tmp', days=10)
