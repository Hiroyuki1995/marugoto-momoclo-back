from . import Secret
import requests
import sys

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
# DEVELOPER_KEY = Secret.YOUTUBE_DATA_API_KEY
# YOUTUBE_API_SERVICE_NAME = 'youtube'
# YOUTUBE_API_VERSION = 'v3'


def get_youtube_data(publishedAfter: str, channelId: str = "UC6YNWTm6zuMFsjqd0PO3G-Q", tmp_file_path: str = "/tmp"):
    """
    publishedAfterから現在までにアップロードされた動画を全て取得する
    ---
    publishedAfter : str
        アップロード時間の検索範囲の下限（RFC 3339形式:2022-08-05T00:00:00Z）
    """

    res = requests.get(
        f'https://youtube.googleapis.com/youtube/v3/search?publishedAfter={publishedAfter}&part=snippet&type=video&channelId={channelId}&order=date&maxResults=10&key={Secret.YOUTUBE_DATA_API_KEY}')
    json = res.json()
    print('json', json)
    items = json["items"]
    if len(items) == 0:
        return []
    # print(items)
    return items


if __name__ == '__main__':
    publishedAfter = "2022-08-05T00:00:00Z"
    if len(sys.argv) > 1:
        get_youtube_data(publishedAfter=publishedAfter,
                         part=sys.argv[1], tmp_file_path="tmp")
    else:
        get_youtube_data(publishedAfter=publishedAfter, tmp_file_path="tmp")
