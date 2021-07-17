from chromdriver_class import FireFoxDriverWithProxy, ChromeCloudFlareProtection, FireFoxDriverWithVPN
import time
import data
import datetime
import telegram_api
from multiprocessing.dummy import Pool
import random
from graphic_telegram import Grafic_Bet365_Telegram
import requests
import json
import time



def get_url_and_data_from_API(TOKEN, FILTER):
    print('Отправка API запроса', time.time())
    data = {
        'accept': 'application/json',
        "Content-Type": "application/x-www-form-urlencoded",
        "search_filter": FILTER,
        "access_token": TOKEN
    }

    r = requests.post('https://rest-api-lv.allbestbets.com/api/v1/valuebets/bot_pro_search', data=data)
    r_text = r.text

    # json -> python dict
    R = json.loads(r_text)
    bets = R['bets']

    for bet in bets:
        # print(bet['id'], bet['is_value_bet'], bet)
        bet_id = bet['id']
        cupon_open_url = f'http://lv.oddsrabbit.org/bets/{bet_id}?locale=ru&access_token={TOKEN}&domain='

        if bet['is_value_bet']:
            return cupon_open_url, R
        else:
            continue

    return ''


def make_bet_multipotok(All_elements_array):
    print('Ставим ставку на одном из аккаунтов')
    driver, url, bet_value = All_elements_array
    # driver.make_cyber_football_bet(url=url, bet_type=bet, coef=coef, bet_value=bet_value)
    driver.make_API_bet_bet365(url=url, value=bet_value)


def make_notify_about_final_balance_telegram(driver, bot_token, user_id_list):

    driver.close_cupon()

    old_balance = driver.current_account_balance
    current_balance = driver.get_bet365_balance()

    if old_balance == current_balance:
        print(f'{driver.account_code_name} ({driver.bet365_account_name}) баланс на это аккаунте не изменился {current_balance}')
        return

    if driver.type_of_account == '.ru':
        vallet = 'rub'
    else:
        vallet = '$'

    text = f'{driver.account_code_name} ({driver.bet365_account_name}) - {current_balance} {vallet}.'
    print(text)

    if current_balance > float(driver.final_balance):

        for user_id in user_id_list:
            try:
                telegram_api.telegram_bot_send_message(bot_token=bot_token, chat_id=user_id, text='-'*32)
            except:
                pass
            try:
                telegram_api.telegram_bot_send_message(bot_token=bot_token, chat_id=user_id, text=text)
            except:
                pass

def reanimate_bet365com(driver):
    if driver.is_VPN:
        driver.restart_VPN_if_its_break()
    driver.reanimaite_bet365com()



List_of_bet_account = [0] * len(data.Accounts)
i1 = 1
for i in range(len(data.Accounts)):
    print(f'Запуск аккаунта {i1}')
    i1+=1

    # запуск аккаунта с VPN
    if data.Accounts[i][2] == 'VPN':
        driver2 = FireFoxDriverWithVPN(path_to_geckodriver=data.path_to_geckodriver, user_agent=data.Accounts[i][0],
                                 proxy=data.Accounts[i][1], proxy_login_and_password=data.Accounts[i][2], type_of_account=data.Accounts[i][6], final_balance=data.Accounts[i][7], account_code_name=data.Accounts[i][8], is_reversed=data.Accounts[i][9])
    else:
        driver2 = FireFoxDriverWithProxy(path_to_geckodriver=data.path_to_geckodriver, user_agent=data.Accounts[i][0],
                                 proxy=data.Accounts[i][1], proxy_login_and_password=data.Accounts[i][2], type_of_account=data.Accounts[i][6], final_balance=data.Accounts[i][7], account_code_name=data.Accounts[i][8], is_reversed=data.Accounts[i][9])

    driver2.log_in_bet365(data.Accounts[i][3], data.Accounts[i][4], data.Accounts[i][6])
    List_of_bet_account[i] = driver2


graphic_bet_telegram = Grafic_Bet365_Telegram(data.graphic_account_code, List_of_bet_account[data.graphic_account])


Set_of_all_Bets = set()
reboot_counter = 0
graphic_bet_telegram_counter = 0
error_flag = False

while True:
    for j1 in range(80):
        time.sleep(1)

        try:
            url1, api_data = get_url_and_data_from_API(TOKEN=data.API_TOKEN, FILTER=data.API_FILTER)
            print(url1)
        except Exception as er:
            print('Ошибка при отправке API запроса:', er)
            time.sleep(10)
            continue

        string_of_result = url1

        if string_of_result in Set_of_all_Bets:
            time.sleep(25)
            continue

        Set_of_all_Bets.add(string_of_result)

        try:
            print('-'*100)
            A = []
            for i in range(len(data.Accounts)):
                account_arr = [List_of_bet_account[i], url1, data.Accounts[i][5]]
                A.append(account_arr)

            with Pool(processes=len(data.Accounts)) as p:
                p.map(make_bet_multipotok, A)
        except:
            pass

        time.sleep(30)

    Set_of_all_Bets = set()

    # перезагрузка страницы (возможно из-за нёеблокируют аккаунт)

    # Вывод текущего времени
    now = datetime.datetime.now()
    now = now.strftime('%H:%M:%S')
    print(now)

    # реанимация .com аккаунтов
    with Pool(processes=len(data.Accounts)) as p:
        A = [i for i in List_of_bet_account]
        p.map(reanimate_bet365com, A)


    # отправка уведомлений о достижении контрольного баланса
    for account_ in List_of_bet_account:
        try:
            make_notify_about_final_balance_telegram(driver=account_, bot_token=data.BOT_TOKEN, user_id_list=data.Telegram_admins)
        except:
            print('Не удалось отправить уведомление об изменении баланса')
        #Окошко порезки аккаунта
        #general-account-restrictions

    #отправка графика
    graphic_bet_telegram_counter += 1
    #раз в 5 мин
    if graphic_bet_telegram_counter > 0:
        try:
            try:
                graphic_bet_telegram.send_actual_grafic()
            except:
                print('Не удалось отправить актуальный график')
        except:
            pass



#cupon = 'http://lv.oddsrabbit.org/bets/NDc3NTQxOTk2fDE4LC01LjUsNCwwLDAsMA?locale=ru&access_token=f5a0a4fda9a612f09f86d9230a2c4cc2&domain='
