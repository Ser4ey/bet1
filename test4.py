import requests



BOT_TOKEN_GRAF = '1673449920:AAEmKCmlSxzD2IxVKKKznmsawJUzYaZsKzI'

my_id = '409524113'


def telegram_bot_send_photo(bot_token, chat_id, path_to_photo):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    files = {'photo': open(path_to_photo, 'rb')}
    data = {'chat_id': chat_id}
    r = requests.post(url, files=files, data=data)
    return r.json()

print(telegram_bot_send_photo(BOT_TOKEN_GRAF, my_id, '1.png'))


