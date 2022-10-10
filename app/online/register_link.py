import boto3
# from boto3.dynamodb.conditions import BeginsWith, Key
import base64
import sys
from datetime import datetime
sys.path.append('../')
from common.aws.s3.get_image_object import get_image_object
from common.aws.dynamodb.put_items import put_items

from const import const


import time


def register_link(data):
    table_name = const.LINKS_TABLE_NAME

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S%f")[:-3]
    items = [{
        "group": "momoclo",
        "id": timestamp,
        "order":data["order"],
        "category": data["category"],
        "name": data["name"],
        "url": data["url"],
        "disabled": False,
    }]
    print('items',items)
    put_items(table_name, items)
    return items


if __name__ == '__main__':
    array = [
        {
            "category": "tickets",
            "links": [{
                "order":20220906,
            "name": "9/6(金)開催　黒フェス",
            "url": "http://kurofes.net/pages/ticket",
        },
        {
            "order":20220917,
            "name": "9/17(土)開催　イナズマロック フェス 2022　※9/3(土)10:00〜チケット一般発売開始",
            "url": "https://inazumarock.com/2022/",
        },
        {
            "order":20220918,
            "name": "9/18(日)開催　氣志團万博2022",
            "url": "https://www.kishidanbanpaku.com/ticket/",
        },
        {
            "order":20220924,
            "name": "9/24(土)開催　北九州ロックフェスティバル",
            "url": "https://kitakyushu-rock.com/tickets/",
        },
        {
            "order":20221007,
            "name": "10/7(金)開催　THE GREAT SATSUMANIAN HESTIVAL 2022 SPECIAL",
            "url": "https://www.great-satsumanian.jp/ticket.html",
        },
        {
            "order":20221008,
            "name": "10/8(土)開催　「スナック愛輪」　※8/28(日)番組最速独占先行開始",
            "url": "https://event.1242.com/events/snack_a-rin/",
        }]},
        {
            "category":"goods",
            "links": [
                {
                    "order":1,
                    "name": "はるえ商店",
                    "url": "https://mailivis.jp/shops/momoclo",
                },
                {
                    "order":2,
                    "name": "玉井詩織生誕記念アイテム",
                    "url": "https://www.beams.co.jp/search/?label=0751&q=220826%E3%82%82%E3%82%82%E3%82%AF%E3%83%AD&search=true",
                }]
            }
        ]
    for category in array:

        for link in category["links"]:
            print({
                        "order":link["order"],
                        "category": category["category"],
                        "name": link["name"],
                        "url": link["url"],
                    })
            register_link({
                        "order":link["order"],
                        "category": category["category"],
                        "name": link["name"],
                        "url": link["url"],
                    })
    # register_link({
    #                 "order":1,
    #                 "category": "goods",
    #                 "name": "はるえ商店",
    #                 "url": "https://mailivis.jp/shops/momoclo",
    #             })