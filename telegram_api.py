import time
import requests


def telegram_bot_send_message(bot_token, chat_id, text):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={text}'
    responce = requests.get(url)
    return responce.json()


def telegram_bot_send_photo(bot_token, chat_id, path_to_photo):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    files = {'photo': open(path_to_photo, 'rb')}
    data = {'chat_id': chat_id}
    r = requests.post(url, files=files, data=data)
    return r.json()

