import boto3
from boto3.exceptions import S3UploadFailedError
import sys
sys.path.append('../')
from const import const

def uploadImage():
    # Let's use Amazon S3
    s3 = boto3.resource('s3', aws_access_key_id=const.AWS_ACCESS_KEY_ID, aws_secret_access_key=const.AWS_SECRET_ACCESS_KEY)
    
    # Upload a new file
    try:
      s3.Bucket('marugoto-momoclo').upload_file('/tmp/2021-08-18_12-46-06_UTC.jpg', '2021-08-18_12-46-06_UTC.jpg')
    except S3UploadFailedError as e:
      print(e)

if __name__ == "__main__":
  uploadImage()