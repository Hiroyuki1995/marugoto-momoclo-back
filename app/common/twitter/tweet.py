from tracemalloc import start
import tweepy
import datetime
# from dateutil import parser
# from datetime import datetime
import sys
sys.path.append('../../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const

# consumer_key = "LdAI0dnlShjOFv7K1vV1CK5UM"
# consumer_secret = "9xiVx7ml8QeZDU0wp9pXfSuM2RTBMtxzY4tR8MG30CZx4RYCHU"
# access_token = "1261208570-eX0gTandlQqRUcwGgw7xLdFkCMnsS3d8NXMnUWd"
# access_token_secret = "oBnG8AGVqPvc4nPv0RDoGFIUs72wR5PvQarkPmzmB34Xh"


def tweet(user_id, days=1) -> dict:
    """
    指定されたユーザーIDの指定された日付だけツイートを取得する。最大取得可能数は20。
    リツイートは取得結果から除く。
    IF仕様は以下参照。
    https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets-id#Optional
    """
    auth = tweepy.OAuthHandler(CK, CS)
    auth.set_access_token(AT, AS)
    api = tweepy.API(auth)

    # 好きな言葉をツイート
    api.update_status("Pythonから投稿!")

    start_time = (datetime.datetime.now(datetime.timezone.utc) -
                  datetime.timedelta(days=days)).isoformat(timespec='seconds')
    print('start_time', start_time)
    client = tweepy.Client(bearer_token=const.BEARER_TOKEN)
    results = client.get_users_tweets(id=user_id, start_time=start_time, exclude="retweets", tweet_fields=["created_at", "public_metrics"],
                                      media_fields=["duration_ms", "height", "media_key", "preview_image_url", "type", "url", "width", "alt_text", "public_metrics"], expansions="attachments.media_keys", max_results=20)
    # print("results:", results)
    # print("data:", results["data"])
    # print("first_data:", results["data"][0])
    return results


if __name__ == '__main__':
    tweet(user_id=242584825)
