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


def register_posts_and_stories(event=None, lambda_context=None, tmp_file_path="/tmp", days=1):
    """
    Instagramのポストとストーリーを同時に登録する。
    ポストは現在からdays日前をダウンロードし、ストーリーは全て取得（Instagram上でストーリーは1日のみ参照可能なため、実質１日分）

    Parameters
    ----------
    days : int
        どのくらいの日数遡ってポストを検索するかを示す日数
    """
    print('test')
    # Get instance
    try:
        L = instaloader.Instaloader(
            # ローカルの場合、./tmpまたはtmpのときカレントディレクトリに保存される。Lambdaの場合は、/tmpでないといけない
            dirname_pattern=tmp_file_path,
            # ダウンロードするファイルの名称を決定する。
            filename_pattern="{date:%Y%m%d%H%M%S}-{profile}-{typename}-{mediaid}",
            # download_videos=False,  # ポストもストーリーも一旦動画をDLするが、アップロードするのはストーリーのみ
            max_connection_attempts=1,
            fatal_status_codes=[400, 429]
        )
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
                for p in glob.glob(f'{tmp_file_path}/' + '*'):
                    if os.path.isfile(p):
                        #  print(p)
                        os.remove(p)
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
        # 以下、ストーリーの登録
        for instagram_target_user_id in const.INSTAGRAM_TARGET_USER_LIST.keys():
            print('instagram_target_user_id:', instagram_target_user_id)
            count_per_person = 0
            person = const.INSTAGRAM_TARGET_USER_LIST[instagram_target_user_id]
            for story in L.get_stories(userids=[instagram_target_user_id]):
                # story is a Story object
                # print(f'get {len(list(story))} stories')
                # ストーリー単位で以下を実行
                print('step 4')
                for item in story.get_items():
                    print('step 5')
                    mediaid: int = item.mediaid
                    typename: str = item.typename
                    # TOOO 以下のダウンロード消す
                    # L.download_storyitem(item, 'tmp')
                    # item is a StoryItem object
                    # 詳細はhttps://instaloader.github.io/module/structures.html#instaloader.StoryItem
                    # print(item.date) # StoryItemが作られたローカル時間 datetime型 ex.2021-08-18 01:20:43
                    # print(item.mediaid) # StoryItemのID int型
                    # print(item.typename)

                    # Lambdaの/tmpディレクトリのみ書き込み処理が可能。
                    # https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html

                    # 既にDynamoDBに登録済のものであればダウンロードしない
                    date_utc = int(f"{item.date:%Y%m%d%H%M%S}")
                    # person = const.INSTAGRAM_TARGET_USER_LIST[item.owner_id]
                    number = count_photos(table_name, person, date_utc)
                    if number > 0:
                        print(
                            f'{person} {date_utc}に該当するデータが{number}件見つかったため、ファイルのダウンロードを行いません')
                        continue

                    # 1. Instaloaderからストーリー情報をtmpフォルダにダウンロード
                    L.download_storyitem(item, 'tmp')
                    # f = open('/tmp/2021-08-18_12-46-06_UTC.jpg', 'r')

                    # 2. S3にアップロードするファイル名を変数化
                    # 実際にDLされるファイル名と同じ名称を設定する
                    file_name = f"{date_utc}-{item.profile}-{item.typename}-{item.mediaid}"
                    # print(file_name)

                    # メタ情報が格納されているxzファイルを解凍し、対象データの幅と高さを取得する。
                    xz_file_path = f'{tmp_file_path}/{file_name}.json.xz'
                    json_string = lzma.open(xz_file_path).read()
                    dict = json.loads(json_string)
                    dimension = dict['node']['dimensions']
                    width = dimension['width']
                    height = dimension['height']
                    # print(dict['node']['dimensions']['width'])
                    # print(dict['node']['dimensions']['height'])

                    # 3. S3にファイルをアップロード
                    for name in glob.glob(f'{tmp_file_path}/{file_name}*'):
                        # Lambdaでは/tmp/...でないといけない
                        # nameはtmpを含めたファイルの絶対パス
                        if name.endswith('.xz'):
                            # xzファイルはアップロード除外ファイル
                            # TODO: mp4の場合はjpgファイルも保存されるため削除する必要あり
                            continue
                        # 拡張子も含めたファイル名を取得
                        file_name_with_extension = name.lstrip(
                            f'{tmp_file_path}/')
                        period = '.'
                        idx = file_name_with_extension.find(period)
                        file_name_without_extension = file_name_with_extension[:idx]
                        thumnail_file_name_with_extension = ''
                        # 拡張子以外同じファイル名がある場合、mp4ファイルのみをアップロードするようにする
                        if not file_name_with_extension.endswith('.mp4'):
                            print('このファイルはmp4ファイルではありません。')
                            if os.path.isfile(f'{tmp_file_path}/{file_name_without_extension}.mp4'):
                                print(
                                    f'同一ストーリーでmp4ファイルがあるため、ファイルはアップロードし、DBへのデータ登録は行いません。ファイル名：{file_name_with_extension}')
                                upload_file(const.USER_BUCKET_NAME, name,
                                        file_name_with_extension)
                                continue
                        else:
                            if os.path.isfile(f'{tmp_file_path}/{file_name_without_extension}.jpg'):
                                thumnail_file_name_with_extension = f'{file_name_without_extension}.jpg'

                        print('upload ' + name)
                        upload_file(const.USER_BUCKET_NAME, name,
                                    file_name_with_extension)
                        # DLしたファイル名でアップロード。# Lambdaでは/tmp/...でないといけない

                        # img_absolute_path = f'{tmp_file_path}/{file_name_with_extension}'
                        # img = cv2.imread(img_absolute_path)
                        # if name.endswith('.mp4') == False:
                        #     width = img.shape[1]
                        #     height = img.shape[0]
                        # else:
                        #     width = None
                        #     height = None

                        # 4. アップロードが完了したら、DynamoDBにファイル情報を追加
                        items = []
                        target = '-'
                        idx = file_name_with_extension.find(target)
                        date = file_name_with_extension[:idx]

                        extension_target = '.'
                        extension_idx = file_name_with_extension.find(
                            extension_target)
                        extension = file_name_with_extension[extension_idx + 1:]

                        print(date)

                        print(item)

                        print(item.owner_id)
                        items.append({
                            "person": person,
                            "id": str(date_utc),
                            "date": date_utc,
                            "instagram_mediaid": mediaid,
                            "fileName": file_name_with_extension,
                            "group": "momoclo",
                            "type": typename,
                            "width": width if width is not None else None,
                            "height": height if height is not None else None,
                            "category": "stories",
                            "extension": extension,
                            "thumnail": thumnail_file_name_with_extension if thumnail_file_name_with_extension != '' else None,
                        })
                        put_items(table_name, items)
                        count = count + 1
                        count_per_person = count_per_person + 1

                # 全てのストーリーアイテムをアップロードした後に、tmpディレクトリ内のファイル削除
                # Lambdaでは/tmp/...でないといけない
                for p in glob.glob(f'{tmp_file_path}/' + '*'):
                    if os.path.isfile(p):
                        #  print(p)
                        os.remove(p)
            if count_per_person > 0:
                publish_message(
                    f'{const.PERSON_NAME[person]}がInstagramにストーリーズを追加しました。', person)
                result_list.append(
                    {"person": const.PERSON_NAME[person], "count": count_per_person})
        if count > 0:
            text = ''
            for result in result_list:
                text = text + result["person"] + \
                    "が" + str(result["count"]) + "件、"
            text = text + 'Instagramのストーリーを登録しました。\nhttps://www.marugoto-momoclo.com/album/'
            publish_message_to_owner(text)
            # broadcast([{'type': 'text', 'text': text}])

    except Exception as e:
        tb = traceback.format_exc()
        message = f'ポストまたはストーリー登録中にエラーが発生しました {e} {tb}'
        publish_message_to_owner(message)
        print(f'catch error {e} {tb}')
        raise e


if __name__ == "__main__":
    # ローカルでファイルごと実行した時は、カレントディレクトリ内のtmpフォルダを画像一時保存先とする
    register_posts_and_stories(tmp_file_path='tmp', days=3)
