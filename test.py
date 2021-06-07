import datetime

from selenium.webdriver.common.keys import Keys

from chromdriver_class import FireFoxDriver, FireFoxDriverWithProxy, ChromeCloudFlareProtection
import data
import time
import pickle


driver = ChromeCloudFlareProtection()

driver.driver.get('https://positivebet.com/ru/bets/index')

# print(driver.driver.get_CurrentUrl())

time.sleep(3)
driver.driver.find_element_by_id('btnAutoRefresh').click()
print('Автообновление!')
time.sleep(1)

Set_of_all_Bets = set()
reboot_counter = 0
error_flag = False

while True:
    for j1 in range(10):
        time.sleep(1)
        # print('123')

        try:
            Bets = driver.driver.find_elements_by_tag_name('tr')
            print('ok', len(Bets))

        except:
            print('Нужно перезагрузить страницу!')
            error_flag = True
            break


        for i in range(len(Bets)):
            flag = False
            try:

                Info = Bets[i].find_elements_by_tag_name('td')
                profit = Info[1].text

                if profit == '' or float(profit) > 1:
                    continue

                bk = Info[2].find_elements_by_tag_name('div')
                bk = [i.text for i in bk]
                line = 0
                if bk[0] == 'Bet365.ru' or bk[0] == 'Bet365':
                    line = 0
                elif bk[1] == 'Bet365.ru' or bk[1] == 'Bet365':
                    line = 1




                bet = Info[4].find_elements_by_tag_name('a')[line].text
                url = Info[4].find_elements_by_tag_name('a')[line].get_attribute('href')

                print(profit, bk, line, bet, url)
                element = Info[4].find_elements_by_tag_name('a')[line]

                url2 = driver.go_to_bet_from_positivebet_an_return_url(element)
                print(url2)


                time.sleep(5)


                '''
                print(bet, url)

                if line == 1:
                    try:
                        driver.driver.get(url)
                        url1 = driver.driver.current_url
                        while not 'bet365' in url:
                            print(url1)
                            url1 = driver.driver.current_url

                        print(url1)

                    except Exception:
                        print('time out')

                        # driver.driver.send_keys(Keys.CONTROL + 'Escape')



'''

                #
                #
                # if url == 'https://www.bet365.ru/#/IP/B1' or url == 'https://www.bet365.ru/#/HO/':
                #     print('Неправильная ссылка')
                #     continue
                # if not 'bet365' in url:
                #     print('Неправильная ссылка')
                #     continue
                #
                #
                # print(profit, bk, line, event, event_url, bet, coef, url)


            except Exception as er:
                print(er)

    Set_of_all_Bets = set()

    # перезагрузка страницы (возможно из-за нёеблокируют аккаунт)
    driver.driver.refresh()
    # Вывод текущего времени
    now = datetime.datetime.now()
    now = now.strftime('%H:%M:%S')
    print(now)
