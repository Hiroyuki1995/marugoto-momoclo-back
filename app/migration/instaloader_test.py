# import subprocess
# from subprocess import Popen, PIPE

# proc = Popen(["instaloader", "--login", "marugotomomoclo","--sessionfile","./session_instagram"], stdin=PIPE)
# proc.stdin.write('renichancawa\n')
# proc.stdin.flush()



# import subprocess

# args = ['instaloader', '--login', 'marugotomomoclo','--sessionfile','./session_instagram']

# proc = subprocess.Popen(args, 
#                         stdin=subprocess.PIPE, 
#                         stdout=subprocess.PIPE, 
#                         stderr=subprocess.PIPE)

# proc.stdin.write('renichancawa\n')
# proc.stdin.flush()

# stdout, stderr = proc.communicate()
# print(stdout)
# print(stderr)



from subprocess import Popen, PIPE
from upload_instagram_session_file import upload_instagram_session_file
import sys
import time
sys.path.append('../')
from const import const

def main(tmp_file_path='tmp'):
  target_file_path = f'{tmp_file_path}/{const.SESSION_FILE_NAME}'

  proc = Popen(['instaloader','--login', const.INSTAGRAM_USER_NAME,'--sessionfile',target_file_path], stdin=PIPE)
  print('waiting for checking instagram user...')
  time.sleep(5)
  proc.communicate(input=const.INSTAGRAM_PASSWORD)
  print('waiting for downloading session file...')
  time.sleep(5)
  upload_instagram_session_file(target_file_path)

if __name__ == "__main__":
  main('/tmp')