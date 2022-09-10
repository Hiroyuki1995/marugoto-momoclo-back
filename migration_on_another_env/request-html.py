# -*- coding: utf-8 -*-
import requests
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import asyncio

def main_render_javascript_page():
    url = 'https://tver.jp/talents/t0233ff'
    session = HTMLSession()
    r = session.get(url)
    r.html.render()
    title =  r.html.find('body', first=True).text
    print("title",title)

async def main_render_javascript_page_async():
    url = 'https://tver.jp/talents/t0233ff'
    asession = AsyncHTMLSession()
    r = await asession.get('https://python.org/')
    # session = HTMLSession()
    # r = session.get(url)
    r.html.render()
    title =  r.html.find('body', first=True).text
    print("title",title)

def main_normal_page():
    url = 'https://tver.jp/talents/t0233ff'
    r = requests.get(url)
    print(r.text)


if __name__ == '__main__':
    # main_normal_page()
    main_render_javascript_page()
    # main_render_javascript_page_async()
