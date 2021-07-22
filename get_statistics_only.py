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
            time.sleep(0.5)
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
    time.sleep(600)

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

