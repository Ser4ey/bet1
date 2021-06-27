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
    if driver.is_VPN:
        driver.restart_VPN_if_its_break()
    driver.reanimaite_bet365com()



driver1 = ChromeCloudFlareProtection()
driver1.driver.get('https://positivebet.com/ru/bets/index')



driver1.driver.get('https://positivebet.com/ru/bets/index')
time.sleep(5)
driver1.driver.find_element_by_id('btnAutoRefresh').click()
print('Автообновление!')
time.sleep(1)

Set_of_all_Bets = set()
reboot_counter = 0
graphic_bet_telegram_counter = 0
error_flag = False

while True:
    for j1 in range(180):
        time.sleep(1)
        # print('123')

        try:
            Bets = driver1.driver.find_elements_by_tag_name('tr')
            # print('ok')
        except:
            print('Нужно перезагрузить страницу!')
            error_flag = True
            break


        for i in range(len(Bets)):
            flag = False
            try:

                Info = Bets[i].find_elements_by_tag_name('td')
                sport_type = Info[0].find_elements_by_tag_name('a')[2].find_element_by_tag_name('img').get_attribute('alt')
                profit = Info[1].text
                bk = Info[2].find_elements_by_tag_name('a')
                bk = [i.text for i in bk]
                line = 0
                if bk[0] == 'Bet365.ru' or bk[0] == 'Bet365':
                    line = 0
                elif bk[1] == 'Bet365.ru' or bk[1] == 'Bet365':
                    line = 1

                event = Info[3].find_elements_by_tag_name('a')[(line+1)*2-1].text
                event_url = Info[3].find_elements_by_tag_name('a')[(line+1)*2-1].get_attribute('href')
                bet = Info[4].find_elements_by_tag_name('a')[line].text
                bet_element = Info[4].find_elements_by_tag_name('a')[line]
                # coef = Info[5].find_elements_by_tag_name('nobr')[line].find_element_by_tag_name('b').text
                coef = Info[5].find_elements_by_tag_name('nobr')[line].text

                after_coef = ''
                try:
                    after_coef = Info[5].find_elements_by_tag_name('nobr')[line].find_elements_by_tag_name('a')[-1].text
                    if len(after_coef) > 0:
                        coef = coef[:-len(after_coef)]
                except:
                    pass

                string_of_result = '$' + event + '$' + bet + event_url

                if string_of_result in Set_of_all_Bets:
                    continue

                Set_of_all_Bets.add(string_of_result)

                # print(profit, bk, line, event, event_url, bet, coef)
                url = driver1.go_to_bet_from_positivebet_an_return_url(bet_element)

                driver1.get_all_info_from_positivebet_and_write_it_in_csv(Info)


            except:
                pass


    Set_of_all_Bets = set()

    # перезагрузка страницы (возможно из-за нёеблокируют аккаунт)

    # Вывод текущего времени
    now = datetime.datetime.now()
    now = now.strftime('%H:%M:%S')
    print(now)

    #нажатие на кнопку автообновления, если oна не нажата
    try:
        auto_btn = driver1.driver.find_element_by_id('btnAutoRefresh')
        if 'active' not in auto_btn.get_attribute('class').split():
            auto_btn.click()
            print('Нажимаем на кнопку автообновления ещё раз')
    except:
        pass

    # перезагрузка страницы 2.0

