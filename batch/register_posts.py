import instaloader
import sys
import datetime
from itertools import dropwhile, takewhile
import glob
import json
import lzma
import os
import traceback
sys.path.append('../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const
from common.aws.s3.upload_file import upload_file
from common.aws.dynamodb.put_items import put_items
from common.aws.dynamodb.count_photos import count_photos
from common.aws.sns.publish_message_to_owner import publish_message_to_owner
from common.aws.sns.publish_message import publish_message
from common.aws.s3.download_file import download_file
from common.line.broadcast import broadcast

# AWS上で関数が呼ばれる時は、引数なし。Lambda内のルートパスを指定


def register_posts(event=None, lambda_context=None, tmp_file_path="/tmp", days=1):
    print('test')
    # Get instance
    try:
        L = instaloader.Instaloader(
            # ローカルの場合、./tmpまたはtmpのときカレントディレクトリに保存される。Lambdaの場合は、/tmpでないといけない
            dirname_pattern=tmp_file_path,
            # ダウンロードするファイルの名称を決定する。
            filename_pattern="{date:%Y%m%d%H%M%S}-{profile}-{typename}-{mediaid}",
            download_videos=False,  # ポストのみ動画をDLしない
            max_connection_attempts=1,
            fatal_status_codes=[400, 429]
        )
        # L.login(const.INSTAGRAM_USER_NAME, const.INSTAGRAM_PASSWORD)
        # S3にあるセッションファイルを取得する
        download_file(const.SESSION_BUCKET_NAME,
                      const.SESSION_FILE_NAME, tmp_file_path)
        L.load_session_from_file(const.INSTAGRAM_USER_NAME,
                                 tmp_file_path + '/' + const.SESSION_FILE_NAME)

        time_to = datetime.datetime.now()
        time_from = time_to - datetime.timedelta(days)

        table_name = const.PHOTOS_TABLE_NAME
        count = 0
        # ex. [{"person":"しおりん", count: 1},{person: "れにちゃん", count: 3}, ...]
        result_list = []
        for instagram_target_user_id in const.INSTAGRAM_TARGET_USER_LIST.keys():
            count_per_person = 0
            person = const.INSTAGRAM_TARGET_USER_LIST[instagram_target_user_id]
            # Download posts
            posts = instaloader.Profile.from_id(
                L.context, instagram_target_user_id).get_posts()
            for post in takewhile(lambda p: p.date > time_from, dropwhile(lambda p: p.date > time_to, posts)):
                #  既に登録済のものであればダウンロードしない
                date_utc: str = f"{post.date:%Y%m%d%H%M%S}"
                mediaid: int = post.mediaid
                profile: str = post.profile
                typename: str = post.typename
                # Postオブジェクトのowner_idはString型。StoryItemオブジェクトのowner_idはInt型。
                owner_id: int = int(post.owner_id)
                # ポストであってもキャプションがない場合があるため、その場合は空文字を登録する。
                caption: str = post.caption if post.caption != None else ""

                # person = const.INSTAGRAM_TARGET_USER_LIST[owner_id]
                # 既にDynamoDBに登録済のものであればダウンロードしない
                number = count_photos(table_name, person, date_utc)
                print(
                    f"{date_utc}-{post.profile}-{post.typename}-{mediaid}")
                if number > 0:
                    print(
                        f'{person} {date_utc}に該当するデータが{number}件見つかったため、ファイルのダウンロードを行いません')
                    continue

                # post is an instance of instaloader.Post
                # print(post.caption, post.date)
                L.download_post(post, "tmp")

                # file_name = f"{date_utc}-{post.profile}-{post.typename}-{post.mediaid}"
                file_name_without_serial_number = f"{date_utc}-{profile}-{typename}-{mediaid}"
                print(file_name_without_serial_number)

                # メタ情報が格納されているxzファイルを解凍し、対象データの幅と高さを取得する。
                xz_file_path = f'{tmp_file_path}/{file_name_without_serial_number}.json.xz'
                json_string = lzma.open(xz_file_path).read()
                dict = json.loads(json_string)
                shortcode = dict['node']['shortcode']
                dimension = dict['node']['dimensions']
                edges = {}
                if 'edge_sidecar_to_children' in dict['node']:
                    edges = dict['node']['edge_sidecar_to_children']['edges']
                    num = len(edges)
                else:
                    print('この投稿は画像１枚のみです。')
                    num = 1

                # 2. S3にアップロードするファイル名を変数化
                # 実際にDLされるファイル名と同じ名称を設定する
                # file_name_prefix = f"{post.date_utc:%Y%m%d%H%M%S}-{post.profile}-{post.typename}-{post.mediaid}"
                # print(file_name_prefix)

                # 3. S3にファイルをアップロード
                for i in range(num):
                    print(f'{i}番目の画像')
                    if num > 1:
                        postfix = str(i + 1)
                        file_name = f"{file_name_without_serial_number}_{i+1}"
                    else:
                        postfix = ""
                        file_name = file_name_without_serial_number

                    if edges != {}:
                        width = edges[i]['node']['dimensions']['width']
                        height = edges[i]['node']['dimensions']['height']
                    else:
                        width = dimension['width']
                        height = dimension['height']

                    for name in glob.glob(f'{tmp_file_path}/{file_name}*'):
                        # Lambdaでは/tmp/...でないといけない
                        # nameはtmpを含めたファイルの絶対パス
                        if name.endswith('.xz') or name.endswith('.txt') or name.endswith('.mp4'):
                            # xzファイルとtxtファイルとmp4はアップロード除外ファイル
                            # mp4は容量が大きいため取得しない。リンクで代替する。
                            # TODO: mp4の場合はjpgファイルも保存されるため削除する必要あり
                            continue
                        print('upload ' + name)
                        # 拡張子も含めたファイル名を取得
                        file_name_with_extension = name.lstrip(
                            f'{tmp_file_path}/')
                        upload_file("marugoto-momoclo", name,
                                    file_name_with_extension)
                        # DLしたファイル名でアップロード。# Lambdaでは/tmp/...でないといけない

                        # 4. アップロードが完了したら、DynamoDBにファイル情報を追加
                        items = []
                        target = '-'
                        idx = file_name_with_extension.find(target)
                        # 複数画像がある場合は、dateに連番を付与し、レコードの一意性を保つ
                        date: str = file_name_with_extension[:idx]
                        print(date)

                        extension_target = '.'
                        extension_idx = file_name_with_extension.find(
                            extension_target)
                        extension = file_name_with_extension[extension_idx + 1:]

                        items.append({
                            "person": person,
                            "id": date + postfix,
                            "date": int(date),
                            "instagram_mediaid": mediaid,
                            "fileName": file_name_with_extension,
                            "group": "momoclo",
                            "caption": caption,
                            "type": typename,
                            "width": width,
                            "height": height,
                            "category": "posts",
                            "extension": extension,
                            "shortcode": shortcode,
                        })
                        print('register item', items[0]["instagram_mediaid"])
                        put_items(table_name, items)
                        count = count + 1
                        count_per_person = count_per_person + 1

                # 全てのストーリーアイテムをアップロードした後に、tmpディレクトリ内のファイル削除
                # Lambdaでは/tmp/...でないといけない
                # for p in glob.glob(f'{tmp_file_path}/' + '*'):
                #     if os.path.isfile(p):
                #         #  print(p)
                #         os.remove(p)
            if count_per_person > 0:
                publish_message(
                    f'{const.PERSON_NAME[person]}がInstagramに写真を投稿しました。', person)
                result_list.append(
                    {"person": const.PERSON_NAME[person], "count": count_per_person})

        if count > 0:
            text = ''
            for result in result_list:
                text = text + result["person"] + \
                    "が" + str(result["count"]) + "件、"
            text = text + 'Instagramを投稿しました。\nhttps://www.marugoto-momoclo.com/album/'
            publish_message_to_owner(text)
            # broadcast([{'type': 'text', 'text': text}])
    except Exception as e:
        tb = traceback.format_exc()
        message = f'ポスト登録中にエラーが発生しました {e} {tb}'
        publish_message_to_owner(message)
        print(f'catch error {e} {tb}')
        raise e


if __name__ == "__main__":
    # ローカルでファイルごと実行した時は、カレントディレクトリ内のtmpフォルダを画像一時保存先とする
    register_posts(tmp_file_path='tmp', days=10)
