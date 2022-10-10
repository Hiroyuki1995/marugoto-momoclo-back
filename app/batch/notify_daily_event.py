import sys

sys.path.append('../')  # constモジュールインポートのため、デフォルトパスを１つ上の階層にあげる
from const import const
from common.notify_new_photos import notify_new_photos
from common.notify_daily_schedule import notify_daily_schedule
from common.aws.sns.publish_message_to_owner import publish_message_to_owner
from common.line.broadcast import broadcast
from common.line.message_to_the_user import message_to_the_user

def notify_daily_event(event=None, lambda_context=None, doBroadcast=True):
    schedule_message = notify_daily_schedule(event,lambda_context)
    photo_message = notify_new_photos(event,lambda_context)
    
    message = ""
    if schedule_message != "":
      message += schedule_message
    if photo_message != "":
      if schedule_message != "":
        message += "\n\n"
      message += photo_message
    if message != "":
      publish_message_to_owner(message)
      if doBroadcast == True:
          broadcast(
              [{'type': 'text', 'text': message}])
      else:
          message_to_the_user(
              [{'type': 'text', 'text': 'テスト\n'+message}], const.LINE_IWATA_USER_ID)

if __name__ == '__main__':
    notify_daily_event(event={"time": "2019-08-19T00:00:00Z"},doBroadcast = False)


