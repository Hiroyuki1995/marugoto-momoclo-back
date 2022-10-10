import json
import urllib.parse
import boto3
import datetime
from datetime import timedelta, timezone
import random
import os
import requests
from bs4 import BeautifulSoup
from requests.models import Response

print('Loading function')

s3 = boto3.resource('s3')


def lambda_handler(event=None, context=None):
    # Get the object from the event and show its content type
    JST = timezone(timedelta(hours=+9), 'JST')
    dt_now = datetime.datetime.now(JST)
    date_str = dt_now.strftime('%Y年%m月%d日')

    # response = requests.get('https://mainichi.jp/editorial/')

    # soup = BeautifulSoup(response.text, "html.parser")

    # pages = soup.find("ul", class_="articlelist")
    # # print(pages)

    # articles = pages.find_all("li")
    # print(articles[0].a.get("href"))

    # links = ["https:" + a.a.get("href")
    #          for a in articles if date_str in a.time.text]
    response = requests.get(
        "https://news.livedoor.com/search/article/?ie=euc-jp&word=%A4%E2%A4%E2%A4%A4%A4%ED%A5%AF%A5%ED%A1%BC%A5%D0%A1%BCZ")

    soup = BeautifulSoup(response.text, "html.parser")
    print(response.text)

    pages = soup.find("ul", class_="articleList")
    print("pages", pages)

    articles = pages.find_all("li")
    print(articles[0].a.get("href"))

    links = ["https:" + a.a.get("href")
             for a in articles if date_str in a.time.text]

    for i, link in enumerate(links):
        bucket_name = "[バケット名]"
        folder_path = "/tmp/"
        filename = 'article_{0}_{1}.txt'.format(
            dt_now.strftime('%Y-%m-%d'), i + 1)

        try:
            bucket = s3.Bucket(bucket_name)

            with open(folder_path + filename, 'w') as fout:
                fout.write(extract_article(link))

            bucket.upload_file(folder_path + filename, filename)
            os.remove(folder_path + filename)

        except Exception as e:
            print(e)
            raise e

    return {
        "date": dt_now.strftime('%Y-%m-%d %H:%M:%S')
    }

# 社説を抽出


def extract_article(src):

    response = requests.get(src)
    soup = BeautifulSoup(response.text)

    text_area = soup.find(class_="main-text")
    title = soup.h1.text.strip()
    sentence = "".join([txt.text.strip()
                       for txt in text_area.find_all(class_="txt")])

    return title + "\n" + sentence


if __name__ == "__main__":
    # ローカルでファイルごと実行した時は、カレントディレクトリ内のtmpフォルダを画像一時保存先とする
    lambda_handler()
