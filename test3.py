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
