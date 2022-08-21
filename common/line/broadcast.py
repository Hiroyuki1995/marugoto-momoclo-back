import requests
import pprint
import sys
sys.path.append('../../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const


def broadcast(messages: list):
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + const.LINE_MESSAGE_API_ACCESS_TOKEN}
    body = {"messages": messages}
    result = requests.post(
        'https://api.line.me/v2/bot/message/broadcast', headers=headers, json=body)
    print(result.status_code)
    pprint.pprint(result.json())


if __name__ == "__main__":
    broadcast([{'type': 'text', 'text': 'れにちゃん\nれにちゃん'}])
