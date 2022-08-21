# from . import Secret
import Secret
import requests
import sys

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
# DEVELOPER_KEY = Secret.YOUTUBE_DATA_API_KEY
# YOUTUBE_API_SERVICE_NAME = 'youtube'
# YOUTUBE_API_VERSION = 'v3'


def get_youtube_video_detail(videoId: str, tmp_file_path: str = "/tmp"):
    """
    指定されたvideoIdに紐づくデータを取得する
    """

    res = requests.get(
        f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id={videoId}&key={Secret.YOUTUBE_DATA_API_KEY}')
    item = res.json()
    print('item', item)
    return item


if __name__ == '__main__':
    get_youtube_video_detail('Yd2zS38aQ6E', tmp_file_path="tmp")
