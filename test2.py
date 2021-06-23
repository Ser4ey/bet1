from chromdriver_class import FireFoxDriverWithProxy, ChromeCloudFlareProtection, FireFoxDriverWithVPN
import time
import data
import datetime
import telegram_api
from multiprocessing.dummy import Pool
import random
from graphic_telegram import Grafic_Bet365_Telegram

def change_domenzone_in_url(url1, pref, post):
    url1 = url1.replace(pref, post)
    return url1


def make_bet_multipotok(All_elements_array):
    print('Ставим ставку на одном из аккаунтов')
    driver, url, bet, coef, bet_value, sport_type = All_elements_array
    # driver.make_cyber_football_bet(url=url, bet_type=bet, coef=coef, bet_value=bet_value)
    driver.start_make_bet_and_choose_sport_type(sport_type=sport_type, url=url, bet_type=bet,
                                                coef=coef, bet_value=bet_value)


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
            telegram_api.telegram_bot_send_message(bot_token=bot_token, chat_id=user_id, text='-'*32)
            telegram_api.telegram_bot_send_message(bot_token=bot_token, chat_id=user_id, text=text)


def reanimate_bet365com(driver):
    driver.reanimaite_bet365com()


i = 3
driver2 = FireFoxDriverWithVPN(path_to_geckodriver=data.path_to_geckodriver, user_agent=data.Accounts[i][0],
                            proxy=data.Accounts[i][1], proxy_login_and_password=data.Accounts[i][2], type_of_account=data.Accounts[i][6], final_balance=data.Accounts[i][7], account_code_name=data.Accounts[i][8], is_reversed=data.Accounts[i][9])
driver2.log_in_bet365(data.Accounts[i][3], data.Accounts[i][4], data.Accounts[i][6])

url = 'https://www.bet365.com/#/IP/EV15619357022C151'

bet_type = 'Г1(1)'


time.sleep(3)
driver2.restart_VPN_if_its_break()
driver2.get_balence()

driver2.make_cyber_football_bet(url, 'П1', '1', '%3')




# driver2.make_cyber_football_bet_gandikap_with_3_exists(url=url, bet_type=bet_type, coef='1', bet_value='0.1')

