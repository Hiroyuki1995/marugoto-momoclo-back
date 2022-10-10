import boto3
from boto3.exceptions import S3UploadFailedError
import sys
#TODO 定数ファイルへのパスを考慮
sys.path.append('../')
from const import const

def upload_file(bucket_name, lambda_file_path, s3_filepath, resource=None):
    # Let's use Amazon S3
    if not resource:
      resource = boto3.resource('s3', aws_access_key_id=const.AWS_ACCESS_KEY_ID, aws_secret_access_key=const.AWS_SECRET_ACCESS_KEY)
    
    # Upload a new file
    try:
      resource.Bucket(bucket_name).upload_file(lambda_file_path, s3_filepath)
    except S3UploadFailedError as e:
      print(e)

if __name__ == "__main__":
  upload_file(lambda_file_path='tmp')