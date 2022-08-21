import requests
import pprint
import sys
sys.path.append('../../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const


def message_to_the_user(messages: list, userId):
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + const.LINE_MESSAGE_API_ACCESS_TOKEN}
    body = {"messages": messages, "to": userId}
    result = requests.post(
        'https://api.line.me/v2/bot/message/push', headers=headers, json=body)
    print(result.status_code)
    pprint.pprint(result.json())


if __name__ == "__main__":
    message_to_the_user(
        [{'type': 'text', 'text': 'れにちゃん\nれにちゃん\nhttps://marugoto-momoclo-front.vercel.app/album/20220703125831'}], const.LINE_IWATA_USER_ID)
