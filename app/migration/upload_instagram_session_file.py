# coding: UTF-8

import sys
import os
sys.path.append('../')
# sys.path.append(os.pardir)
from const import const
from common.aws.s3.upload_file import upload_file

def upload_instagram_session_file(upload_target_file_path):
  """
  yarn instaloaderを実行した後に本関数を呼び出すことで、S3にセッションファイルをアップロードする。
  """
  upload_file(const.SESSION_BUCKET_NAME, upload_target_file_path,const.SESSION_FILE_NAME)

if __name__ == "__main__":
  upload_instagram_session_file('/root/.config/instaloader/session-purplerenichan')
