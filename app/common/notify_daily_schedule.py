import datetime
import sys
import requests
import urllib
import json
import traceback
sys.path.append('../')
from const import const
from common.aws.sns.publish_message_to_owner import publish_message_to_owner


def notify_daily_schedule(event=None, lambda_context=None):
    """
    起動時刻から1日以内の予定を取得し、公式LINEで通知用のメッセージを生成する
    """
    try:
        print('event:' + json.dumps(event))
        execute_time_str = event['time']
        execute_time_obj_utc = datetime.datetime.strptime(
            execute_time_str, '%Y-%m-%dT%H:%M:%SZ')
        timeMin_obj = execute_time_obj_utc + datetime.timedelta(hours=9)
        timeMax_obj = timeMin_obj + datetime.timedelta(days=1)
        timeMin = timeMin_obj.isoformat() + "+09:00"
        timeMax = timeMax_obj.isoformat() + "+09:00"
        today_jst = timeMin_obj.date()
        print('today_jst', today_jst)

        # REST API reference : https://developers.google.com/calendar/api/v3/reference/events/list

        print('timeMin', timeMin, type(timeMin))
        print('timeMax', timeMax)
        events = []
        for data in const.GOOGLE_CALENDAR_DATA:
            print('calendarId', data["googleCalendarId"])
            calendarId = data["googleCalendarId"]
            res = requests.get(
                f'https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events?timeMin={urllib.parse.quote(timeMin)}&timeMax={urllib.parse.quote(timeMax)}&singleEvents=true&key={const.GOOGLE_CALENDAR_API_KEY}')
            items = res.json()["items"]
            if items != []:
                for item in items:
                    events.append(item)
        if not events:
            print('No upcoming events found.')
            publish_message_to_owner('本日の予定は何もありません。')
            return ''
        print('events', events)
        allDayEvents = []
        NonAllDayEvents = []
        for event in events:
            if 'dateTime' in event['start']:
                NonAllDayEvents.append(event)
            else:
                allDayEvents.append(event)
        message = "【本日の予定】"
        if allDayEvents != []:
            print(' allDayEvents != []')
            events_sorted = sorted(
                allDayEvents, key=lambda d: d['start']['date'])
            for event in events_sorted:
                start_obj = datetime.datetime.strptime(
                    event['start']['date'], '%Y-%m-%d').strftime("%-m/%-d")
                end_obj = datetime.datetime.strptime(
                    event['end']['date'], '%Y-%m-%d').strftime("%-m/%-d")
                message += f"\n・{start_obj}〜{end_obj} {event['summary']}"
        if NonAllDayEvents != []:
            print('NonAllDayEvents != []')
            events_sorted = sorted(
                NonAllDayEvents, key=lambda d: d['start']['dateTime'])
            for event in events_sorted:
                start_obj = datetime.datetime.fromisoformat(
                    event['start']['dateTime'])
                end_obj = datetime.datetime.fromisoformat(
                    event['end']['dateTime'])
                # 予定時間がバッチ起動時刻と同じ日付の場合は日付を入れる、そうでない場合は日付を入れない
                if start_obj.date() == today_jst:
                    start_str = start_obj.strftime('%H:%M')
                else:
                    start_str = start_obj.strftime('%-m/%-d %H:%M')

                if end_obj.date() == today_jst:
                    end_str = end_obj.strftime('%H:%M')
                else:
                    end_str = end_obj.strftime('%-m/%-d %H:%M')
                summary = event['summary']

                print(
                    f"{start_str}〜{end_str} {summary}")
                message += f"\n・{start_str}〜{end_str} {summary}"
        message += f"\nhttps://www.marugoto-momoclo.com/calendar/"
        return message

    except Exception as e:
        tb = traceback.format_exc()
        message = f'スケジュールの通知中にエラーが発生しました {e} {tb}'
        publish_message_to_owner(message)
        print(f'catch error {e} {tb}')
        raise e


if __name__ == '__main__':
    notify_daily_schedule(
        event={"time": "2022-08-19T00:00:00Z"})
