import sys
import glob
import os
import traceback
import wget
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
sys.path.append('../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const
from common.aws.s3.upload_file import upload_file
from common.aws.dynamodb.put_items import put_items
from common.aws.dynamodb.count_photos import count_photos
from common.aws.sns.publish_message_to_owner import publish_message_to_owner
from common.aws.sns.publish_message import publish_message
from common.twitter.get_tweets_by_user import get_tweets_by_user
from common.line.broadcast import broadcast

# AWS上で関数が呼ばれる時は、引数なし。Lambda内のルートパスを指定


def register_tweets(event=None, lambda_context=None, tmp_file_path="/tmp"):
    # Get instance
    try:
        count = 0
        # ex. [{"person":"しおりん", count: 1},{person: "れにちゃん", count: 3}, ...]
        result_list = []
        table_name = const.PHOTOS_TABLE_NAME
        for user in const.TWITTER_TARGET_ACCOUNT_LIST:
            count_per_user = 0
            print('user', user["id"])
            results = get_tweets_by_user(user["id"])
            # for medium in results.includes["media"]:
            #     print('medium', medium)
            # ツイートがない場合は次のデータへ進む
            if results.data == None:
                print('data == None')
                continue
            # 画像データがない場合は次のデータへ進む
            elif results.includes == {}:
                print('includes == {}')
                continue
            data = results.data
            media = results.includes["media"]

            for tweet in data:
                print('tweet_id', tweet.get('id'))
                index = 0
                created_at = tweet['created_at']  # datetime型
                # print(created_at)
                date = int(created_at.strftime(
                    "%Y%m%d%H%M%S"))  # yyyymmddhhmmss
                # print(f'datetime {created_at}')
                # print(f'id {id}')
                if tweet['attachments'] and tweet['attachments']['media_keys']:
                    for media_key in tweet['attachments']['media_keys']:
                        # この画像がDynamoDBに登録されているか、media_keymで判定する。
                        index = index + 1
                        number = count_photos(
                            table_name, user["username"], str(date) + str(index))
                        # TODO DynamoDBに登録されていない場合は次のループに移る。
                        if number > 0:
                            print(
                                f'{user["username"]} {date}に該当するデータが{number}件見つかったため、ファイルのダウンロードを行いません')
                            continue

                        # 登録されている場合は、DLしてS3にULし、DynamoDBに登録する。
                        # 1.まずツイートのID・画像の順序からDynamoDB用の画像IDを生成する。
                        values = [
                            x for x in media if 'media_key' in x and x['media_key'] == media_key]  # media_keyからmedia情報を抽出
                        media_info = values[0]
                        # print(values[0] if values else None)
                        # print(values[0]['url'] if values else None)
                        media_id = str(date) + str(index)
                        # 2.ファイルをDLする。
                        if media_info["type"] == "video":
                            image_url = media_info["preview_image_url"]
                        else:
                            image_url = media_info["url"]
                        # filename = image_url[image_url.rfind('/') + 1:]
                        extension = image_url[image_url.rfind('.') + 1:]
                        filename = f'{str(date)}_{user["username"]}_twitter{media_info["type"]}_{media_key}.{extension}'
                        print('filename:', filename)
                        donwnload_filepath = wget.download(
                            image_url, f"{tmp_file_path}/{filename}")
                        print('Image Successfully Downloaded: ',
                              donwnload_filepath)
                        # 3.ファイルをS3にULする。
                        upload_file("marugoto-momoclo",
                                    donwnload_filepath, filename)
                        # 4.画像情報をDynamoDBに登録する
                        items = []
                        items.append({
                            "person": user["username"],
                            "id": media_id,
                            "date": date,
                            "twitter_media_key": media_key,
                            "fileName": filename,
                            "group": "momoclo",
                            "caption": tweet["text"],
                            "type": "twitter" + media_info["type"],
                            "width": media_info["width"],
                            "height": media_info["height"],
                            "category": "tweets",
                            "extension": extension,
                            "tweet_id": tweet["id"]
                        })
                        print('register item', items[0])
                        put_items(table_name, items)
                        count = count + 1
                        count_per_user = count_per_user + 1

                else:
                    print('このツイートは画像がありません')

                # 全てのストーリーアイテムをアップロードした後に、tmpディレクトリ内のファイル削除
                # Lambdaでは/tmp/...でないといけない
                for p in glob.glob(f'{tmp_file_path}/' + '*'):
                    if os.path.isfile(p):
                        #  print(p)
                        os.remove(p)
            if count_per_user > 0:
                result_list.append(
                    {"person": user["name"], "count": count_per_user})

        if count > 0:
            text = ''
            for result in result_list:
                text = text + result["person"] + \
                    "が" + str(result["count"]) + "件、"
            text = text + 'ツイートしました。\nhttps://www.marugoto-momoclo.com/album/'
            publish_message_to_owner(text)
            # broadcast([{'type': 'text', 'text': text}])
    except Exception as e:
        tb = traceback.format_exc()
        message = f'ツイート登録中にエラーが発生しました {e} {tb}'
        # publish_message_to_owner(message)
        print(f'catch error {e} {tb}')
        raise e


if __name__ == "__main__":
    # ローカルでファイルごと実行した時は、カレントディレクトリ内のtmpフォルダを画像一時保存先とする
    register_tweets(tmp_file_path='tmp')
