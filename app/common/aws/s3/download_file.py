import boto3
import sys
#TODO 定数ファイルへのパスを考慮
sys.path.append('../../../')
from const import const
args = sys.argv

def download_file(bucketName, key, tmp_file_path="/tmp", client=None):
  if not client:
      client = boto3.client('s3', aws_access_key_id=const.AWS_ACCESS_KEY_ID, aws_secret_access_key=const.AWS_SECRET_ACCESS_KEY)
  # file = 
  client.download_file(bucketName, key, tmp_file_path + '/' + key)
  # return file['Body']
  
if __name__ == '__main__':
    download_file('marugoto-momoclo-secret', 'session_instagram', 'tmp')