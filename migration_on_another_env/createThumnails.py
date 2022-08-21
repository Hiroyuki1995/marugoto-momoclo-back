import cv2
import boto3
import sys
import glob
import os
sys.path.append('../')
from const import const
from common.aws.s3.download_file import download_file
from common.aws.s3.upload_file import upload_file
from common.aws.dynamodb.update_thumnail import update_item


def createThumnails(tmp_file_path="/tmp", ):
    # 1. DynamoDbのデータから動画アイテムだけを取得
    # 3. それに紐づくデータをS3からtmpフォルダにダウンロード
    # 4. ダウンロードした動画から画像データに変換し、tmpフォルダに一時保存
    # 5. tmpフォルダに置いた画像をS3にアップロード
    # 6. アップロードした画像を対象のアイテムのサムネイル列にファイル名を登録

    # 1.DynamoDBのデータを全て取得
    dbClient = boto3.client('dynamodb')
    args = {
        'TableName': 'Photos',
    }
    args['ExpressionAttributeNames'] = {
        "#extension": "extension"
    }
    args['FilterExpression'] = "#extension = :keyVal"
    args['ExpressionAttributeValues'] = {
        ':keyVal': {'S': 'mp4'},
    }

    response = dbClient.scan(**args)
    s3Client = boto3.client('s3', aws_access_key_id=const.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=const.AWS_SECRET_ACCESS_KEY)
    # print(f'response {response}')
    count = 0
    for item in response['Items']:
        if 'thumnail' in item:
            print('サムネイルが既に登録されています')
            continue
        fileName = item['fileName']['S']
        outputFileName = os.path.basename(fileName).split('.', 1)[0] + '.jpg'
        outputFilePath = tmp_file_path + '/' + outputFileName
        print(outputFileName)
        download_file('marugoto-momoclo', fileName, tmp_file_path)
        cap = cv2.VideoCapture(tmp_file_path + '/' + fileName)
        if not cap.isOpened():
            print('cap cant be opened')
            return

        # 最初のフレームを読み込む
        _, img = cap.read()
        # imgは読み込んだフレームのNumpy配列でのピクセル情報(BGR)
        # imgのshapeは (高さ, 横幅, 3)

        # 画像ファイルで書き出す
        # 書き出すときの画像フォーマットはファイル名から自動で決定
        cv2.imwrite(outputFilePath, img)

        upload_file('marugoto-momoclo', outputFilePath, outputFileName)

        update_item('Photos', item['person']['S'],
                    item['id']['S'], outputFileName)

        # break

        # buildVideoCaptures("./sample.mp4", "./thumbnail.jpg")

        for p in glob.glob(f'{tmp_file_path}/' + '*'):
            if os.path.isfile(p):
                #  print(p)
                os.remove(p)
        count = count + 1
    print('count:', count)


if __name__ == '__main__':
    createThumnails('tmp')
