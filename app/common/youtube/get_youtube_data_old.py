# from apiclient.discovery import build
from googleapiclient.discovery import build
from Secret import Secret
import json

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = Secret.YOUTUBE_DATA_API_KEY
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def get_youtube_data():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)

    # https://developers.google.com/youtube/v3/docs/search/list?apix=true#try-it
    search_response = youtube.search().list(
        part='snippet',  # idも指定可能。idとsnippetの両方を対象にする場合は'id,snippet'と指定する。
        channelId='UC6YNWTm6zuMFsjqd0PO3G-Q',
        maxResults=10,  # 最大で50件
        order='date',  # date, rating, relevance, title, videoCountも指定可能。
        type='video',  # channel, playlistも指定可能。複数指定する場合はカンマで区切って与える。
    ).execute()

    text = json.dumps(search_response)

    titles = []
    results = ''

    # print(search_response.get('items'))
    for item in search_response.get('items'):
        titles.append(item['snippet']['title'])
        results += create_embed_iframe(item['id']['videoId'])
    # print(results)
    print(titles)


def create_embed_iframe(id):
    return f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{id}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'


if __name__ == '__main__':
    get_youtube_data()
