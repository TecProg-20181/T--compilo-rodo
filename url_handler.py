#!/usr/bin/env python3
# Python modules
import json
import requests
import urllib

# Customized modules
from my_token import *

# Private Constants
__TOKEN = getToken()
__URL = "https://api.telegram.org/bot{}/".format(__TOKEN)


# Public Methods
def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = __URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    __get_url(url)


def get_updates(offset=None):
    url = __URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = __get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))

    return max(update_ids)


# Private Methods
def __get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def __get_json_from_url(url):
    content = __get_url(url)
    js = json.loads(content)
    return js
