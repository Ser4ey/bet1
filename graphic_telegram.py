import json
import time
import requests
from matplotlib import pyplot as plt
import data
import telegram_api


class Grafic_Bet365_Telegram:
    def __init__(self, account_name, driver):
        self.account_name = account_name
        self.driver = driver.driver
        self.type_of_account = driver.type_of_account

        def json_create_account_dir(account_name):
            '''Создаёт директорию аккаунта, если её не существует'''
            with open('data_of_bets.json', 'r', encoding='utf-8') as file:
                data1 = json.load(file)

            if account_name not in data1:
                print(f'dir для аккаунта {account_name} была создана')
                data1[account_name] = []

                with open('data_of_bets.json', 'w', encoding='utf-8') as file:
                    json.dump(data1, file, indent=4, ensure_ascii=False)

        json_create_account_dir(self.account_name)

        with open('data_of_bets.json', 'r', encoding='utf-8') as file:
            data1 = json.load(file)
        self.account_bets = data1

    def get_new_bets_from_bet365(self):
        '''Возвращает новый список ставок из аккаунта'''
        driver = self.driver
        elements = '122'

        while True:
            try:
                if self.type_of_account == '.com':
                    driver.get('https://www.bet365.com/#/MB/')
                else:
                    driver.get('https://www.bet365.ru/#/MB/')

                time.sleep(4)
                driver.find_elements_by_class_name('myb-MyBetsHeader_Button')[-1].click()
                time.sleep(2)
                print('ok1')
                elements = driver.find_elements_by_class_name('myb-SettledBetItemHeader ')
                print(len(elements), 'element')
                break
            except:
                if self.type_of_account == '.com':
                    driver.get('https://www.bet365.com/#/MB/')
                else:
                    driver.get('https://www.bet365.ru/#/MB/')


        List_of_bets = []
        for bet in elements:
            try:
                value_of_bet = bet.find_element_by_class_name('myb-SettledBetItemHeader_Text ').text
                type_of_bet = bet.find_element_by_class_name('myb-SettledBetItem_SubHeaderText ').text
                win_or_lose = bet.find_element_by_class_name('myb-SettledBetItem_BetStateContainer ').text

                if value_of_bet == '' or type_of_bet == '' or win_or_lose == '':
                    continue

                bet_info = [win_or_lose, type_of_bet, value_of_bet]
                List_of_bets.append(bet_info)
                # print(bet_info)
            except Exception as er:
                print(er, '12a')

        return List_of_bets

    def update_account_bets(self):
        '''Допалняет информацию об ставках новыми данными (автоматически)
        data от старых к новым
        new_data от новых к старым
        '''

        new_data = self.get_new_bets_from_bet365()
        data = self.account_bets[self.account_name]

        List_of_new_elements = []
        # print(new_data, '1')
        # print(data, '2')

        for i in range(len(new_data)):
            if new_data[i] not in data:
                print(new_data[i], 'new bet')
                List_of_new_elements.append(new_data[i])



        data = data + List_of_new_elements[::-1]
        self.account_bets[self.account_name] = data
        # print(self.account_bets, '1a')

    def update_json_file(self):
        '''Обновляет json file на основе текущего заначения self.account_bets'''
        with open('data_of_bets.json', 'w', encoding='utf-8') as file:
            json.dump(self.account_bets, file, indent=4, ensure_ascii=False)

    def create_and_safe_grafic(self):
        y_list = [i[0] for i in self.account_bets[self.account_name]]

        A = [0]
        for i in range(len(y_list)):
            if y_list[i] == 'Проигрыш' or y_list[i] == 'Lost':
                A.append(A[i] - 1)
            else:
                A.append(A[i] + 1)

        y_list = A

        x_list = range(1, len(y_list) + 1)
        y_list2 = [0] * len(y_list)

        plt.title(f'Ставки аккаунта {self.account_name}')
        plt.xlabel('Кол-во ставок')
        plt.ylabel('Кол-во выигрышей/проигрышей')
        plt.plot(x_list, y_list2, color='black')
        plt.plot(x_list, y_list, color='brown')
        #plt.plot(x_list, y_list)

        plt.savefig('1.png', dpi=600)

    def send_telegram_notifay(self):
        '''Отправляеттелеграм уведомление (график) админам'''
        for admin in data.Telegram_admins:
            telegram_api.telegram_bot_send_photo(data.BOT_TOKEN_GRAF, admin, '1.png')

    def send_actual_grafic(self):
        self.update_account_bets()
        self.update_json_file()

        self.create_and_safe_grafic()
        self.send_telegram_notifay()



#
# u1 = Grafic_Bet365_Telegram(data.graphic_account_code, driver2)
#
# u1.send_actual_grafic()
