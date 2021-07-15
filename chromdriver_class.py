import csv
import os
import pickle
import threading
import pyautogui
import selenium
from selenium import webdriver
import time
import data

from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

# selenium.webdriver.common.keys

class ChromeWithProfile:
    '''
        Для каждого нового аккаунта нужно создать свою дирикторию в .config, путём клонирования
        главной директопии. (/home/ser4/.config/google-chrome), таким образом,
        сначала нужно создать необходимые chrome профиля, а затем
        для каждого из них скопировать директорию

        users_data_dir - путь к директории (корые мы клонируем)
        profile_directory - имя под которым хранится наш аккаунт

        Информацию об аккауте можно посмотреть
    '''

    def __init__(self, path_to_chromedriver, users_data_dir, profile_directory):
        self.path_to_chromedriver = path_to_chromedriver
        self.users_data_dir = users_data_dir
        self.profile_directory = profile_directory

        options = webdriver.ChromeOptions()
        # options.add_argument('disable-infobars')
        # options.add_experimental_option("detach", True)
        # options.add_argument('--proxy-server=176.119.142.94:11373')
        
        options.add_argument(f"user-data-dir={users_data_dir}")
        options.add_argument(f'--profile-directory={profile_directory}')

        driver = webdriver.Chrome(executable_path=path_to_chromedriver, chrome_options=options)

        self.driver = driver


    def log_in_bet365(self, login, password):
        self.driver.get('https://www.bet365.ru/#/IP/B1')
        time.sleep(5)
        # вход в аккамунт
        while True:
            try:
                self.driver.find_element_by_class_name('hm-MainHeaderRHSLoggedOutWide_LoginContainer').click()
                break
            except:
                time.sleep(1)

        time.sleep(5)
        while True:
            try:
                self.driver.find_element_by_class_name('lms-StandardLogin_Username').send_keys(login)
                time.sleep(0.7)
                self.driver.find_element_by_class_name('lms-StandardLogin_Password').send_keys(password)
                time.sleep(0.7)
                break
            except:
                time.sleep(1)

        self.driver.find_element_by_class_name('lms-StandardLogin_LoginButton').click()
        time.sleep(12)
        print('Вы успешно вошли в аккаунт bet365.ru')


    def find_bet_and_return_url(self, bet_name):

        self.driver.find_element_by_class_name('hm-SiteSearchIconLoggedIn ').click()
        time.sleep(1)
        self.driver.find_element_by_class_name('sml-SearchTextInput ').send_keys(bet_name)
        time.sleep(0.5)

        try:
            self.driver.find_element_by_class_name('ssm-SiteSearchBetsMarketGroupButton_Container ').click()
            # self.driver.find_element_by_class_name('ssm-SiteSearchBetsMarketGroupButton_TextHeader ').click()
        except:
            return f'Событие {bet_name} не найдено'

        time.sleep(1)
        return self.driver.current_url

    def close_session(self):
        self.driver.close()
        self.driver.quit()


class FireFoxDriver:
    def __init__(self, path_to_geckodriver, user_agent):

        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        options = webdriver.FirefoxOptions()
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("general.useragent.override", user_agent)

        driver = webdriver.Firefox(executable_path=path_to_geckodriver, firefox_binary=data.firefox_binary,
            capabilities=firefox_capabilities,
            options=options)

        self.driver = driver
        self.is_login_in_positivebet = False

    def log_in_positivebet(self, login, password):
        self.driver.get('https://positivebet.com/ru/user/login')
        print('Вход в аккаунт positivebet')
        time.sleep(5)
        self.driver.find_element_by_id('UserLogin_username').send_keys(login)
        time.sleep(2)
        self.driver.find_element_by_id('UserLogin_password').send_keys(password)
        time.sleep(2)
        self.driver.find_element_by_id('UserLogin_rememberMe').click()
        time.sleep(1)
        self.driver.find_element_by_class_name('btn-primary').click()
        time.sleep(3)
        print('Вы успено вошли в аккаунт')
        self.driver.get('https://positivebet.com/ru/bets/index')
        time.sleep(3)
        self.is_login_in_positivebet = True

    def go_to_bet_from_positivebet_an_return_url(self, element):
        current_page = self.driver.current_window_handle
        try:
            element.click()
            time.sleep(1)
        except:
            print('Не получилось получить ссылку')
            return 0
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[1])
        #time.sleep(1)
        url = self.driver.current_url
        self.driver.close()
        self.driver.switch_to.window(current_page)
        return url


    def close_session(self):
        self.driver.close()
        self.driver.quit()


class FireFoxDriverWithProxy:
    def __init__(self, path_to_geckodriver, user_agent, proxy, proxy_login_and_password, type_of_account, final_balance, account_code_name, is_reversed):
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True
        print(proxy)
        firefox_capabilities['proxy'] = {
            "proxyType": "MANUAL",
            "httpProxy": proxy,
            "ftpProxy": proxy,
            "sslProxy": proxy
        }

        options = webdriver.FirefoxOptions()
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("dom.webnotifications.enabled", False)
        options.set_preference("general.useragent.override", user_agent)

        driver = webdriver.Firefox(capabilities=firefox_capabilities, firefox_binary=data.firefox_binary,
                                   executable_path=path_to_geckodriver,
                                   proxy=proxy,
                                   options=options)
        self.is_VPN = False
        self.driver = driver
        self.driver.get('https://2ip.ru/')
        self.type_of_account = type_of_account
        self.final_balance = final_balance
        self.account_code_name = account_code_name
        self.current_account_balance = -1
        self.is_reversed = is_reversed

        if proxy_login_and_password == 'no_login_for_proxy':
            print('Вы используете прокси с привязкой к ip!')
        else:
            print(f'Введите логин и пароль от прокси - {proxy_login_and_password}')
            input('Затем нажмите Enter')

    def log_in_positivebet(self, login, password):
        self.driver.get('https://positivebet.com/ru/user/login')
        print('Вход в аккаунт positivebet')
        time.sleep(5)
        self.driver.find_element_by_id('UserLogin_username').send_keys(login)
        time.sleep(2)
        self.driver.find_element_by_id('UserLogin_password').send_keys(password)
        time.sleep(2)
        self.driver.find_element_by_id('UserLogin_rememberMe').click()
        time.sleep(1)
        self.driver.find_element_by_class_name('btn-primary').click()
        time.sleep(3)
        print('Вы успено вошли в аккаунт')
        self.driver.get('https://positivebet.com/ru/bets/index')
        time.sleep(3)
        self.is_login_in_positivebet = True

    def get_all_info_from_positivebet_and_write_it_in_csv(self, block):
        '''
        Получает блок с вилкой
        Записывает полученные данные в .csv
        '''

        if not os.path.exists('vilki_logs.csv'):
            with open('vilki_logs.csv', 'a', encoding='utf-8') as f:
                writer = csv.writer(f)
                row = (
                    'вид спорта', #
                    'процент вилки',
                    'время жизни вилки',
                    'название противоположной бк',
                    'команда 1',
                    'команда 2',
                    'вид ставки',
                    'коэффициент на Bet365',
                    'количество инициаторов у Bet365',
                    'коэффициент противоположной БК',
                    'количество инициаторов противоположной БК',
                    'кто является инициатором'
                )

                writer.writerow(row)


        Info = block
        # Info = block.find_elements_by_tag_name('td')

        sport_type = Info[0].find_elements_by_tag_name('a')[2].find_element_by_tag_name('img').get_attribute('alt')
        live_time = Info[0].find_elements_by_tag_name('div')[-1].text
        profit = Info[1].text
        print(f'Q {sport_type} {profit} {live_time}')

        bk = Info[2].find_elements_by_tag_name('a')
        bk = [i.text for i in bk]
        if 'Bet365' in bk[0]:
            line_with_bet365 = 0
            line_with_other_bk = 1
        else:
            line_with_bet365 = 1
            line_with_other_bk = 0

        other_bk_name = bk[line_with_other_bk]

        event = Info[3].find_elements_by_tag_name('a')[(line_with_bet365 + 1) * 2 - 1].text
        teams = event.split(' vs ')
        team1 = teams[0]
        team2 = teams[-1]

        bet_type = Info[4].find_elements_by_tag_name('a')[line_with_bet365].text
        print(f'Q {bet_type} {other_bk_name} {team1} {team2}')

        coef_bet365 = Info[5].find_elements_by_tag_name('nobr')[line_with_bet365].text
        numbers_of_vilki_bet365 = '0'
        try:
            numbers_of_vilki_bet365 = Info[5].find_elements_by_tag_name('nobr')[line_with_bet365].find_element_by_tag_name('sub').text
        except:
            pass
        # coef_bet365 = coef_bet365[:len(coef_bet365)-numbers_of_vilki_bet365]
        print(f'Q {coef_bet365} {numbers_of_vilki_bet365}')

        coef_other = Info[5].find_elements_by_tag_name('nobr')[line_with_other_bk].text
        numbers_of_vilki_other = '0'
        try:
            numbers_of_vilki_other = Info[5].find_elements_by_tag_name('nobr')[line_with_other_bk].find_element_by_tag_name('sub').text
        except:
            pass
        # coef_other = coef_other[:len(coef_other)-numbers_of_vilki_other]
        print(f'Q {coef_other} {numbers_of_vilki_other}')

        inicializqator = '0'
        try:
            a = Info[5].find_elements_by_tag_name('nobr')[line_with_other_bk].find_element_by_tag_name('b').text
            if len(a) > 0:
                inicializqator = other_bk_name
        except:
            pass

        try:
            a = Info[5].find_elements_by_tag_name('nobr')[line_with_bet365].find_element_by_tag_name('b').text
            if len(a) > 0:
                inicializqator = 'Bet365'
        except:
            pass

        print(f'Q {inicializqator}')

        with open('vilki_logs.csv', 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            row = (
                sport_type, #'вид спорта',
                profit, #'процент вилки',
                live_time, #'время жизни вилки',
                other_bk_name, #'название противоположной бк',
                team1, #'команда 1',
                team2, #'команда 2',
                bet_type, #'вид ставки',
                coef_bet365, #'коэффициент на Bet365',
                numbers_of_vilki_bet365, #'количество инициаторов у Bet365',
                coef_other, #'коэффициент противоположной БК',
                numbers_of_vilki_other, #'количество инициаторов противоположной БК',
                inicializqator #'кто является инициатором'
            )

            writer.writerow(row)
            print('Новая запись в таблице!')

    def go_to_bet_from_positivebet_an_return_url(self, element):
        current_page = self.driver.current_window_handle
        try:
            element.click()
            time.sleep(3)
        except:
            print('Не получилось получить ссылку')
            return 0
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[-1])
        url = self.driver.current_url
        self.driver.close()
        self.driver.switch_to.window(current_page)
        return url

    def log_in_bet365(self, login, password, type_of_account):
        self.bet365_login = login
        self.bet365_password = password

        if self.type_of_account == '.com':

            try:
                self.driver.get('https://www.bet365.com/')
            except:
                pass

            for i in range(10):
                try:
                    try:
                        time.sleep(5)
                        self.driver.find_element_by_class_name('hm-MainHeaderRHSLoggedOutWide_LoginContainer')
                        break
                    except:
                        print('refresh')
                        #self.driver.refresh()
                        self.driver.get('https://www.bet365.com/')
                        print('-')
                except:
                    pass

        else:
            self.driver.get('https://www.bet365.ru/')

        print(f'Вход в аккаунт: {login}')
        time.sleep(5)
        # вход в аккаунт bet365ru
        for i in range(10):
            try:
                self.driver.find_element_by_class_name('hm-MainHeaderRHSLoggedOutWide_LoginContainer').click()
                break
            except:
                print('Не удалось войти в аккаунт!')
                time.sleep(2)

        time.sleep(5)
        for i in range(10):
            try:
                self.driver.find_element_by_class_name('lms-StandardLogin_Username').send_keys(login)
                time.sleep(0.7)
                self.driver.find_element_by_class_name('lms-StandardLogin_Password').send_keys(password)
                time.sleep(0.7)
                break
            except:
                time.sleep(1)
                print('Не удалось войти в аккаунт')
                return

        self.driver.find_element_by_class_name('lms-StandardLogin_LoginButton').click()
        time.sleep(10)
        print('Вы успешно вошли в аккаунт bet365.ru')
        self.bet365_account_name = login

    def start_make_bet_and_choose_sport_type(self, sport_type, url, bet_type, coef, bet_value):
        '''
        Запускает алгоритм проставления ставки нужного ВИДА СПОРТА
            # Настольный теннис
            # Киберфутбол
        '''

        # изменение доменной зоны ссылки
        if self.type_of_account == '.com':
            url = url.replace('.ru', '.com')
        else:
            url = url.replace('.com', '.ru')

        # Попытка закрыть предыдушее окно ставки, если ставка не была проставлена.
        try:
            self.driver.find_element_by_class_name('qbs-NormalBetItem_Indicator ').click()
        except:
            pass

        # Попытка закрыть окно неактивности на .com версии
        try:
            self.driver.find_element_by_class_name('alm-ActivityLimitAlert_Button ').click()
        except:
            pass

        # Попытка закрыть купоны ставок(когда скапливается много ставок в купоне)
        self.close_cupon()


        if sport_type == 'Настольный теннис':
            print('Делаем ставку Настольный теннис')
            self.make_table_tennis_bet(url, bet_type, coef, bet_value)
        elif sport_type == 'Киберфутбол':
            print('Делаем ставку Киберфутбол')
            self.make_cyber_football_bet(url, bet_type, coef, bet_value)
        else:
            print('Неизвестный тип спорта')

    def get_balence(self):
        value = '%3'
        if str(value)[0] == '%':
            value = value[1:]
            value = float(value)
            print(f'value1: {value}')
            value = value / 100
            print(f'value1.5: {value}')
            try:
                bet365balance = self.driver.find_element_by_class_name('hm-MainHeaderMembersWide_Balance').text
                bet365balance = bet365balance.split(',')[0]
                bet365balance = bet365balance.strip()
                bet365balance = bet365balance.replace(' ', '')
                bet365balance = float(bet365balance)
                print(f'Баланс аккаунта {bet365balance}')
            except:
                bet365balance = 10
                print(f'Баланс аккаунта {bet365balance}')

            print(f'{bet365balance} * {value}')
            value = bet365balance * value
            print('value2:', value)

    def make_API_bet(self, url, value):
        '''Делает ставку при помощи API
            Получает ссылку
            При переходе по которой купон автоматически открывается'''
        self.driver.get(url)
        time.sleep(1)

        # проверка что купон открылся
        try:
            coef_now = self.driver.find_element_by_class_name('bsc-OddsDropdownLabel').text
            coef_now = float(coef_now)
        except:
            print('[API] Купон не открылся')
            if self.type_of_account == '.com':
                self.driver.get('https://www.bet365.com/')
            else:
                self.driver.get('https://www.bet365.ru/#/HO/')
            return

        if str(value)[0] == '%':
            value = value[1:]
            value = float(value)
            value = value / 100
            try:
                bet365balance = self.driver.find_element_by_class_name('hm-MainHeaderMembersWide_Balance').text
                bet365balance = bet365balance.split(',')[0]
                bet365balance = bet365balance.strip()
                bet365balance = bet365balance.replace(' ', '')
                bet365balance = float(bet365balance)
                print(f'Баланс аккаунта {bet365balance}')
            except:
                bet365balance = 10
                print(f'Баланс аккаунта {bet365balance}')

            print(f'bet = {bet365balance} * {value}')
            value = bet365balance * value
            value = round(value, 2)
            print('value:', value)

        self.driver.find_element_by_class_name('qbs-NormalBetItem_DetailsContainer ') \
            .find_element_by_class_name('qbs-StakeBox_StakeInput ').click()
        time.sleep(0.3)
        for simvol in str(value):
            self.driver.find_element_by_tag_name("body").send_keys(simvol)
            time.sleep(0.3)
        time.sleep(0.5)
        self.driver.find_element_by_class_name('qbs-BetPlacement ').click()

        flag = False

        for i in range(15):
            try:
                self.driver.find_element_by_class_name('qbs-QuickBetHeader_DoneButton ').click()
                print('Ставка проставлена!')
                return 'Ставка проставлена!'
            except:
                time.sleep(1)

        print('[-] Не удалось поставить ставку')
        self.driver.find_element_by_class_name('qbs-NormalBetItem_Indicator ').click()

        if self.type_of_account == '.com':
            self.driver.get('https://www.bet365.com/#/HO/')
        else:
            self.driver.get('https://www.bet365.ru/#/HO/')
        time.sleep(2)

    def make_a_bet(self, value, coef, element):
        '''Ставит ставку в открывшемся окошечке
        (его нужно предварительно открыть)'''

        time.sleep(1)
        coef_now = self.driver.find_element_by_class_name('bsc-OddsDropdownLabel').text
        coef_now = float(coef_now)
        print(f'Текущий коэффициент - {coef_now} Нужный коэффициент - {coef}')
        coef = float(coef)
        if coef - coef_now > 0.09:
            print('Коэффициэнт сильно изменился')
            time.sleep(1)
            element.click()
            if self.type_of_account == '.com':
                self.driver.get('https://www.bet365.com/')
            else:
                self.driver.get('https://www.bet365.ru/#/HO/')

            time.sleep(2)
            return

        if str(value)[0] == '%':
            value = value[1:]
            value = float(value)
            value = value / 100
            try:
                bet365balance = self.driver.find_element_by_class_name('hm-MainHeaderMembersWide_Balance').text
                bet365balance = bet365balance.split(',')[0]
                bet365balance = bet365balance.strip()
                bet365balance = bet365balance.replace(' ', '')
                bet365balance = float(bet365balance)
                print(f'Баланс аккаунта {bet365balance}')
            except:
                bet365balance = 10
                print(f'Баланс аккаунта {bet365balance}')

            print(f'bet = {bet365balance} * {value}')
            value = bet365balance * value
            value = round(value, 2)
            print('value:', value)

        self.driver.find_element_by_class_name('qbs-NormalBetItem_DetailsContainer ') \
            .find_element_by_class_name('qbs-StakeBox_StakeInput ').click()
        time.sleep(0.3)
        for simvol in str(value):
            self.driver.find_element_by_tag_name("body").send_keys(simvol)
            time.sleep(0.3)
        time.sleep(0.5)
        self.driver.find_element_by_class_name('qbs-BetPlacement ').click()

        flag = False

        for i in range(15):
            try:
                self.driver.find_element_by_class_name('qbs-QuickBetHeader_DoneButton ').click()
                print('Ставка проставлена!')
                return 'Ставка проставлена!'
            except:
                time.sleep(1)

        print('[-] Не удалось поставить ставку')
        self.driver.find_element_by_class_name('qbs-NormalBetItem_Indicator ').click()

        if self.type_of_account == '.com':
            self.driver.get('https://www.bet365.com/#/HO/')
        else:
            self.driver.get('https://www.bet365.ru/#/HO/')
        time.sleep(2)

    def reanimaite_bet365com(self):
        # попытка закрыть купон
        try:
            self.driver.find_element_by_class_name('qbs-NormalBetItem_Indicator ').click()
            time.sleep(2)
        except:
            pass

        # попытка закрыть окно неактивности
        try:
            if self.type_of_account == '.com':
                self.driver.get('https://www.bet365.com/')
                time.sleep(3)
                self.driver.find_element_by_class_name('alm-ActivityLimitAlert_Button ').click()
        except:
            pass

        #Попытка реанимировать сайт .com версии (пропадает соединение) (VPN!!!)
        if self.type_of_account == '.com':
            for i in range(10):
                try:
                    try:
                        self.driver.get('https://www.bet365.com/')
                        time.sleep(4)
                        bet365balance = self.driver.find_element_by_class_name('hm-MainHeaderMembersWide_Balance ').text
                        print(f'Аккаунт {self.bet365_account_name} - работает')
                        break
                    except:
                        print(f'Аккаунт {self.bet365_account_name} - реанимируется')
                        self.driver.get('https://www.bet365.com/')
                        time.sleep(1)
                        print('-')
                except:
                    pass

    def close_cupon(self):
        '''Попытка Закрытие купонов(а_ если он есть'''
        try:

            #open_cupon
            self.driver.find_element_by_class_name('bss-StandardHeader ').click()
            time.sleep(4)
            #очистка купона
            self.driver.find_element_by_class_name('bs-ControlBar_RemoveButton ').click()
            time.sleep(4)
        except Exception as er:
            print('нет купонов', er)

    def reverse_cyber_football_bet(self, bet_type):
        '''Изменение ставки на противоположное плечо (1 -> 2Х) (Тб 1.5 -> Тм 1.5)'''
        reverse_bet = bet_type

        if bet_type == 'П1' or bet_type == '1':
            #  1 -> X2
            reverse_bet = 'X2'

        elif bet_type == '2' or bet_type == 'П2':
            #  2 -> 1X
            reverse_bet = '1X'

        elif bet_type == 'X' or bet_type == 'Х':
            #  X -> 12
            reverse_bet = '12'

        elif bet_type == '1X' or bet_type == '1Х':
            #  1X -> 2
            reverse_bet = '2'

        elif bet_type == 'Х2' or bet_type == 'X2':
            #  X2 -> 1
            reverse_bet = '1'

        elif bet_type == '12' or bet_type == '21':
            #  12 -> X
            reverse_bet = 'X'

        elif bet_type[:13] == 'Гола не будет':
            #  Гола не будет(3) -> Тм(2.5)
            reverse_bet = bet_type.split('(')[-1]
            reverse_bet = reverse_bet.strip(')')
            reverse_bet = int(reverse_bet) + 0.5
            reverse_bet = str(reverse_bet)
            reverse_bet = f'Тм({reverse_bet})'

        elif bet_type == 'Чет':
            #  Чет -> Нечет
            reverse_bet = 'Нечет'

        elif bet_type == 'Нечет':
            #  Чет -> Нечет
            reverse_bet = 'Чет'

        else:
            if 'Команда' in bet_type:
                if 'Тб' in bet_type:
                    reverse_bet = bet_type.replace('Тб', 'Тм')
                elif 'Тм' in bet_type:
                    reverse_bet = bet_type.replace('Тм', 'Тб')

            elif 'Тб' in bet_type:
                reverse_bet = bet_type.replace('Тб', 'Тм')

            elif 'Тм' in bet_type:
                reverse_bet = bet_type.replace('Тм', 'Тб')

        return reverse_bet

    def make_cyber_football_bet(self, url, bet_type, coef, bet_value):
        # изменение ставки на другое плечо (если нужно) for cyber footboll
        if self.is_reversed == 'reversed':
            print('Ставка на противоположное плечо')
            print(bet_type, '-> ', end='')
            bet_type = self.reverse_cyber_football_bet(bet_type)
            print(bet_type)
            coef = 0


        if bet_type == 'П1' or bet_type == 'П2' or bet_type == '1' or bet_type == '2' or bet_type == 'X' or bet_type == 'Х':
            self.make_cyber_football_bet_P1_P2_X(url, bet_type, coef, bet_value)
        elif bet_type == '1X' or bet_type == 'X2' or bet_type == '1Х' or bet_type == 'Х2' or bet_type == '12' or bet_type == '21':
            self.make_cyber_football_bet_double_chance_P1X_XP2_P1P2(url, bet_type, coef, bet_value)
        elif bet_type[:13] == 'Гола не будет':
            self.make_cyber_football_bet_gola_ne_budet(url, bet_type, coef, bet_value)
        elif bet_type == 'Чет' or bet_type == 'Нечет':
            self.make_cyber_football_bet_odd_or_even(url, bet_type, coef, bet_value)
        elif 'Г1' in bet_type or 'Г2' in bet_type:
            self.make_cyber_football_bet_gandikap_with_3_exists(url, bet_type, coef, bet_value)
        elif 'Ф1' in bet_type or 'Ф2' in bet_type:
            self.make_cyber_football_bet_F1_F2(url, bet_type, coef, bet_value)
        else:
            if 'Команда' in bet_type:
                if 'Тб' in bet_type or 'Тм' in bet_type:
                    self.make_cyber_football_bet_totalbet_of_teme_1or2(url, bet_type, coef, bet_value)
                    return
            if 'Тб' in bet_type or 'Тм' in bet_type:
                self.make_cyber_football_bet_totalbet_of_game(url, bet_type, coef, bet_value)
                return

            print('Неизвестный тип ставки')

    def make_cyber_football_bet_P1_P2_X(self, url, bet_type, coef, bet_value):
        print(f'Проставляем ставку(Победа|Ничья|Поражение) url: {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')

        bet_element = list_of_bets[0]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text != 'Результат основного времени':
            print('Ставка на П1П2Х, указана колонка не результат основного времени!')
            return


        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            bet_element.click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[0]


        element_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        bets = element_with_bets.find_elements_by_class_name('gl-Participant ')

        my_bet_number = 2
        if bet_type == 'П1' or bet_type == '1':
            my_bet_number = 0
        elif bet_type == 'П2' or bet_type == '2':
            my_bet_number = -1
        elif bet_type == 'X' or bet_type == 'Х':
            my_bet_number = 1
        else:
            print('Ставка на П1П2Х, неизвестный формат ставки')
            return 'Ставка на П1П2Х, неизвестный формат ставки'

        bets[my_bet_number].click()
        time.sleep(2)
        self.make_a_bet(bet_value, coef, bets[my_bet_number])

    def make_cyber_football_bet_double_chance_P1X_XP2_P1P2(self, url, bet_type, coef, bet_value):
        print(f'Проставляем ставку(Двойной шанс) url: {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

            if text1 == 'Двойной шанс':
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text != 'Двойной шанс':
            print('Ставка(Двойной шанс) не найдена')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        element_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        bets = element_with_bets.find_elements_by_class_name('gl-Participant ')

        my_bet_number = 2
        if bet_type == '1X' or bet_type == '1Х':
            my_bet_number = 0
        elif bet_type == 'X2' or bet_type == 'Х2':
            my_bet_number = 1
        elif bet_type == '12' or bet_type == '21':
            my_bet_number = -1
        else:
            print('Ставка на (Двойной шанс) , неизвестный формат ставки')
            return 'Ставка на (Двойной шанс) , неизвестный формат ставки'

        bets[my_bet_number].click()
        time.sleep(2)
        self.make_a_bet(bet_value, coef, bets[my_bet_number])

    def make_cyber_football_bet_totalbet_of_game(self, url, bet_type, coef, bet_value):
        print(f'Проставляем ставку total bet url: {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

            if text1 == 'Голы матча':
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text != 'Голы матча':
            print('Ставка(Голы матча не найдена/total bet) не найдена')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        element_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')

        goul_count = element_with_bets.find_element_by_class_name('srb-ParticipantLabelCentered_Name ').text
        bets = element_with_bets.find_elements_by_class_name('gl-ParticipantOddsOnly ')

        bet_type = bet_type.strip(')')
        bet_type = bet_type.split('(')
        number_of_gouls = bet_type[1]
        bet_type = bet_type[0]

        if number_of_gouls != goul_count:
            print(f'Число голов не совпадает {goul_count}|{number_of_gouls}')
            return

        if bet_type == 'Тб':
            bets[0].click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bets[0])

        elif bet_type == 'Тм':
            bets[1].click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bets[1])


        else:
            print('Неизвестный тип ставки (Тотол на общий счёт)')
            return

    def make_cyber_football_bet_totalbet_of_teme_1or2(self, url, bet_type, coef, bet_value):
        print(f'Проставляем ставку total bet team url: {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 'None'
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text[-4:]

            if text1 == 'ГОЛЫ':
                line = i
                print(f'line: {line}')
                break

        if line == 'None':
            print('Total bet на команду не найдена')
            return

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text


        if 'Команда2' in bet_type:
            line += 1
            bet_element = list_of_bets[line]

        bet_type = bet_type.split(' ')[-1]

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        element_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')

        goul_count = element_with_bets.find_element_by_class_name('srb-ParticipantLabelCentered_Name ').text
        bets = element_with_bets.find_elements_by_class_name('gl-ParticipantOddsOnly ')

        bet_type = bet_type.strip(')')
        bet_type = bet_type.split('(')
        number_of_gouls = bet_type[1]
        bet_type = bet_type[0]

        if number_of_gouls != goul_count:
            print(f'Число голов не совпадает {goul_count}|{number_of_gouls}')
            return

        bet_element_1 = bets[0]
        if bet_type == 'Тб':
            bets[0].click()
        elif bet_type == 'Тм':
            bets[1].click()
            bet_element_1 = bets[1]
        else:
            print('Неизвестный тип ставки (Тотал на общий счёт)')
            return



        time.sleep(2)
        self.make_a_bet(bet_value, coef, bet_element_1)

    def make_cyber_football_bet_gola_ne_budet(self, url, bet_type, coef, bet_value):
        print(f'Проставляем ставку Гола не будет url: {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

            if text1[1:] == '-й Гол':
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text[1:] != '-й Гол':
            print('Ставка(Двойной шанс) не найдена')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        element_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        bets = element_with_bets.find_elements_by_class_name('gl-Participant_General ')

        #gl-Participant_General
        my_bet_number = 1

        bets[my_bet_number].click()
        time.sleep(2)
        self.make_a_bet(bet_value, coef, bets[my_bet_number])

    def make_cyber_football_bet_odd_or_even(self, url, bet_type, coef, bet_value):
        print(f'Проставляем ставку ЧетНечет: {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

            if text1 == 'Голы нечет/чёт':
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text != 'Голы нечет/чёт':
            print('Ставка(Голы нечет/чёт) не найдена')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        element_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')


        bets = element_with_bets.find_elements_by_class_name('gl-Market_General-cn2 ')

        if bet_type == 'Чет':
            bets[1].click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bets[1])
        else:
            bets[0].click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bets[0])

    def make_cyber_football_bet_gandikap_with_3_exists(self, url, bet_type, coef, bet_value):
        # Г1(1) Г2(0) Г1(-1)   (1 -> +1)
        print(f'Проставляем ставку Гандикап с 3 исходами url: {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

            if text1 == 'ГАНДИКАП С 3 ИСХОДАМИ':
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text != 'ГАНДИКАП С 3 ИСХОДАМИ':
            print('Ставка Гандикап с 3 исходами не найдена')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        element_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')

        gandicaps = element_with_bets.find_elements_by_class_name('gl-ParticipantCentered_Handicap')
        bets_list = element_with_bets.find_elements_by_class_name('gl-ParticipantCentered ')

        true_gandicap = bet_type[3:]
        true_gandicap = true_gandicap.strip('(')
        true_gandicap = true_gandicap.strip(')')

        if true_gandicap == '0':
            pass
        elif true_gandicap[0] == '-':
            pass
        else:
            true_gandicap = '+' + true_gandicap

        print(f'true gandicap: {true_gandicap}')

        if 'Г1' in bet_type:
            line_ = 0
        else:
            line_ = -1

        gandicap = gandicaps[line_]
        bet_ = bets_list[line_]

        if gandicap != true_gandicap:
            print('Гандикап изменился')
            return

        bet_.click()
        time.sleep(2)
        self.make_a_bet(bet_value, coef, bet_)

    def make_cyber_football_bet_F1_F2(self, url, bet_type, coef, bet_value):
        # Ф2(-3)
        print(f'Проставляем ставку Ф url: {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

            if 'АЗИАТСКИЙ ГАНДИКАП' in text1:
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if not 'АЗИАТСКИЙ ГАНДИКАП' in text:
            print('Ставка Ф не найдена')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        element_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')


        bets_list = element_with_bets.find_elements_by_class_name('gl-ParticipantCentered ')


        if 'Ф1' in bet_type:
            line_ = 0
        else:
            line_ = -1

        bet_ = bets_list[line_]

        bet_.click()
        time.sleep(2)
        self.make_a_bet(bet_value, coef, bet_)


    def make_table_tennis_bet(self, url, bet_type, coef, bet_value):
        '''Ставка на настольный теннис'''

        if bet_type == 'П1' or bet_type == 'П2':
            # П1 П2
            self.make_table_tennis_bet_P1_P2(url, bet_type, coef, bet_value)
        elif ('П1' in bet_type or 'П2' in bet_type) and len(bet_type) > 5:
            # П1 (1 партия)
            self.make_table_tennis_bet_P1_P2_of_game1(url, bet_type, coef, bet_value)
        elif ('Ф1' in bet_type or 'Ф2' in bet_type) and len(bet_type) < 10:
            # Ф1(-2.5)  Ф2(1.5)
            self.make_table_tennis_bet_F1_F2_gandikap_of_match(url, bet_type, coef, bet_value)
        elif ('Ф1' in bet_type or 'Ф2' in bet_type) and len(bet_type) > 10:
            # Ф1(-2.5) (3 партия)     Ф2(1.5) (1 партия)
            self.make_table_tennis_bet_F1_F2_gandikap_of_game1(url, bet_type, coef, bet_value)
        else:
            print('Неизвестный тип ставки (1)', bet_type)


    def make_table_tennis_bet_P1_P2(self, url, bet_type, coef, bet_value):
        print(f'Проставляем ставку П1П2(table tennis): {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

            if text1 == 'ЛИНИИ МАТЧА':
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text != 'ЛИНИИ МАТЧА':
            print('Ставка П1П2 настольный теннис')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        elements_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        columns_ = elements_with_bets.find_element_by_class_name('gl-MarketGroupContainer ')
        columns_ = columns_.find_elements_by_class_name('gl-Market_General-columnheader ')

        bet_text = columns_[0].find_elements_by_tag_name('div')[1].text
        if bet_text != 'Победитель':
            print('Не удалось найти ставку на победу (теннис)')
            return

        bet1 = columns_[1].find_elements_by_tag_name('div')[1]
        bet2 = columns_[2].find_elements_by_tag_name('div')[1]

        if bet_type == 'П1':
            bet1.click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bet1)
        else:
            bet2.click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bet2)

    def make_table_tennis_bet_P1_P2_of_game1(self, url, bet_type, coef, bet_value):
        '''Побеа в отдельной игре, а не на всю партию целиком'''

        print(f'Проставляем ставку П1 (3 партия)(table tennis): {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text
            # ИГРА 5 - ЛИНИИ
            if ('ИГРА' in text1) and ('ЛИНИИ' in text1):
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if not (('ИГРА' in text) and ('ЛИНИИ' in text)):
            print('Ставка П1 на игру матча?')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        elements_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        columns_ = elements_with_bets.find_element_by_class_name('gl-MarketGroupContainer ')
        columns_ = columns_.find_elements_by_class_name('gl-Market_General-columnheader ')

        line_ = -1
        # Гандикап (Игры)
        counter_ = 0
        for bet_text1 in columns_[0].find_elements_by_tag_name('div'):
            try:
                bet_text = bet_text1.text
                print(f'{counter_}: {bet_text}')
                if bet_text == 'Победитель':
                    line_ = counter_
                    # -1 ?
                    print(line_)
                    break
            except:
                pass
            counter_ += 1
        # bet_text = columns_[0].find_elements_by_tag_name('div')[1].text

        if line_ == -1:
            print('Не удалось найти ставку на Победу на игру (теннис)')
            return

        # srb-ParticipantCenteredStackedMarketRow_Handicap

        bet1 = columns_[1].find_elements_by_tag_name('div')[line_]
        bet2 = columns_[2].find_elements_by_tag_name('div')[line_]

        if 'П1' in bet_type:
            bet1.click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bet1)
        else:
            bet2.click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bet2)


    def make_table_tennis_bet_F1_F2_gandikap_of_match(self, url, bet_type, coef, bet_value):
        print(f'Проставляем ставку Ф1(2.5)(Гандикап) (table tennis): {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')

        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

            if text1 == 'ЛИНИИ МАТЧА':
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text != 'ЛИНИИ МАТЧА':
            print('Ставка Гандикап на матч?')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        elements_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        columns_ = elements_with_bets.find_element_by_class_name('gl-MarketGroupContainer ')
        columns_ = columns_.find_elements_by_class_name('gl-Market_General-columnheader ')

        line_ = -1
        # Гандикап (Игры)
        counter_ = 0
        for bet_text1 in columns_[0].find_elements_by_tag_name('div'):
            try:
                bet_text = bet_text1.text
                print(f'{counter_}: {bet_text}')
                if bet_text == 'Гандикап (Игры)':
                    line_ = counter_ - 1
                    #
                    print(line_)
                    break
            except:
                pass
            counter_ += 1
        # bet_text = columns_[0].find_elements_by_tag_name('div')[1].text

        if line_ == -1:
            print('Не удалось найти ставку на гандикап (теннис)')
            return

        # srb-ParticipantCenteredStackedMarketRow_Handicap

        bet1 = columns_[1].find_elements_by_tag_name('div')[line_]
        bet2 = columns_[2].find_elements_by_tag_name('div')[line_]

        bet1_gendikap_value = bet1.find_element_by_class_name('srb-ParticipantCenteredStackedMarketRow_Handicap').text
        bet2_gendikap_value = bet2.find_element_by_class_name('srb-ParticipantCenteredStackedMarketRow_Handicap').text
        print(f'1 gandicap: {bet1_gendikap_value}')
        print(f'2 gandicap: {bet2_gendikap_value}')

        true_gendikap_value = bet_type.split('(')
        true_gendikap_value = true_gendikap_value[-1]
        true_gendikap_value = true_gendikap_value.strip(')')
        if true_gendikap_value[0] != '-':
            true_gendikap_value = '+' + true_gendikap_value

        print(f'True gandicap: {true_gendikap_value}')

        if 'Ф1' in bet_type:
            if true_gendikap_value != bet1_gendikap_value:
                print('Значение гандикапа изменилось')
                return

            bet1.click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bet1)
        else:
            if true_gendikap_value != bet2_gendikap_value:
                print('Значение гандикапа изменилось')
                return

            bet2.click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bet2)


    def make_table_tennis_bet_F1_F2_gandikap_of_game1(self, url, bet_type, coef, bet_value):
        '''Гандикап на отдельную игру, а не на всё партию целиком'''

        print(f'Проставляем ставку Ф1(2.5) (3 партия) (Гандикап) (table tennis): {url}; bet_type: {bet_type}; coef: {coef}')
        self.driver.get(url)
        time.sleep(3)

        list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
        line = 0
        for i in range(len(list_of_bets)):
            bet_element = list_of_bets[i]
            text1 = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text
            # ИГРА 5 - ЛИНИИ
            if ('ИГРА' in text1) and ('ЛИНИИ' in text1):
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if not (('ИГРА' in text) and ('ЛИНИИ' in text)):
            print('Ставка Гандикап на игру матча?')
            return

        try:
            bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        except:
            print('Разворачиваем ставку')
            bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').click()
            time.sleep(0.5)
            list_of_bets = self.driver.find_elements_by_class_name('sip-MarketGroup ')
            bet_element = list_of_bets[line]

        elements_with_bets = bet_element.find_element_by_class_name('gl-MarketGroup_Wrapper ')
        columns_ = elements_with_bets.find_element_by_class_name('gl-MarketGroupContainer ')
        columns_ = columns_.find_elements_by_class_name('gl-Market_General-columnheader ')

        line_ = -1
        # Гандикап (Игры)
        counter_ = 0
        for bet_text1 in columns_[0].find_elements_by_tag_name('div'):
            try:
                bet_text = bet_text1.text
                print(f'{counter_}: {bet_text}')
                if bet_text == 'Гандикап':
                    line_ = counter_ - 1
                    # -1 ?
                    print(line_)
                    break
            except:
                pass
            counter_ += 1
        # bet_text = columns_[0].find_elements_by_tag_name('div')[1].text

        if line_ == -1:
            print('Не удалось найти ставку на гандикап на игру (теннис)')
            return

        # srb-ParticipantCenteredStackedMarketRow_Handicap

        bet1 = columns_[1].find_elements_by_tag_name('div')[line_]
        bet2 = columns_[2].find_elements_by_tag_name('div')[line_]

        bet1_gendikap_value = bet1.find_element_by_class_name('srb-ParticipantCenteredStackedMarketRow_Handicap').text
        bet2_gendikap_value = bet2.find_element_by_class_name('srb-ParticipantCenteredStackedMarketRow_Handicap').text

        true_gendikap_value = bet_type.split(' ')[0]
        true_gendikap_value = true_gendikap_value.split('(')
        true_gendikap_value = true_gendikap_value[-1]
        true_gendikap_value = true_gendikap_value.strip(')')
        if true_gendikap_value[0] != '-':
            true_gendikap_value = '+' + true_gendikap_value

        print(f'True gandicap: {true_gendikap_value}')

        if 'Ф1' in bet_type:
            if true_gendikap_value != bet1_gendikap_value:
                print('Значение гандикапа изменилось')
                return

            bet1.click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bet1)
        else:
            if true_gendikap_value != bet2_gendikap_value:
                print('Значение гандикапа изменилось')
                return

            bet2.click()
            time.sleep(2)
            self.make_a_bet(bet_value, coef, bet2)


    def get_bet365_balance(self):
        url = 'https://www.bet365.ru/'
        if self.type_of_account == '.com':
            url = 'https://www.bet365.com/'

        try:
            self.driver.get(url)
            time.sleep(4)
            #bet365balance = self.driver.find_element_by_class_name('hm-MainHeaderMembersWide_Balance').text
            bet365balance = self.driver.find_element_by_class_name('hm-Balance').text
            # hm-Balance
            bet365balance = bet365balance.split(',')[0]
            bet365balance = bet365balance.strip()
            bet365balance = bet365balance.replace(' ', '')
            bet365balance = float(bet365balance)
            self.current_account_balance = bet365balance
            return bet365balance
        except Exception as er:
            print(f'Не удалось получть баланс аккаунта {self.bet365_account_name} для отправки уведомлений', er)

            return 0

    def close_session(self):
        self.driver.quit()


class FireFoxDriverWithVPN(FireFoxDriverWithProxy):
    def __init__(self, path_to_geckodriver, user_agent, proxy, proxy_login_and_password, type_of_account, final_balance,
                 account_code_name, is_reversed):
        self.is_VPN = True
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = True

        # путь к firefox аккаунту !!!
        fp = webdriver.FirefoxProfile(
            r'C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\wxjvqcon.default-release-1')

        options = webdriver.FirefoxOptions()
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("dom.webnotifications.enabled", False)
        binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        options.binary = binary

        # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
        # options.set_preference("general.useragent.override", user_agent)

        # 	Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.022

        driver = webdriver.Firefox(capabilities=firefox_capabilities, firefox_profile=fp,
                                   firefox_binary=data.firefox_binary,
                                   executable_path=path_to_geckodriver,
                                   options=options)


        self.driver = driver
        self.driver.get('https://2ip.ru/')
        time.sleep(3)
        self.driver.refresh()
        self.type_of_account = type_of_account
        self.final_balance = final_balance
        self.account_code_name = account_code_name
        self.current_account_balance = -1
        self.is_reversed = is_reversed

        self.driver = driver
        time.sleep(2)
        print('go')


        try:
            self.driver.get('https://www.bet365.com/')
        except:
            pass

        bad_ip = True
        while bad_ip:
            answer_ = self.check_ip()
            if answer_:
                # повторная проверка
                print('повторная проверка')
                time.sleep(5)
                answer2 = self.check_ip()
                if answer2:
                    print('[+] Stop scerch for new ip')
                    break

            self.driver.quit()
            time.sleep(2)
            #
            firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
            firefox_capabilities['marionette'] = True

            fp = webdriver.FirefoxProfile(
                r'C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\wxjvqcon.default-release-1')

            options = webdriver.FirefoxOptions()
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("dom.webnotifications.enabled", False)
            binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
            options.binary = binary

            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'
            options.set_preference("general.useragent.override", user_agent)
            #
            self.driver = webdriver.Firefox(capabilities=firefox_capabilities, firefox_profile=fp,
                            firefox_binary='C:/Program Files/Mozilla Firefox/firefox.exe',
                            executable_path=r'C:\Users\Administrator\PycharmProjects\bet1\geckodriver.exe',
                            options=options)
            time.sleep(2)

            self.driver.get('https://www.bet365.com/')

    def restart_VPN_if_its_break(self):
         try:
             try:
                 self.driver.get('https://www.bet365.com/')
                 time.sleep(4)
                 bet365balance = self.driver.find_element_by_class_name('hm-MainHeaderMembersWide_Balance ').text
                 print(f'Аккаунт {self.bet365_account_name} - работает')
             except:
                print(f'Аккаунт {self.bet365_account_name} - не работает')

                bad_ip = True
                while bad_ip:
                    # перезагрузка драйвера
                    self.driver.quit()
                    time.sleep(2)
                    #
                    firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
                    firefox_capabilities['marionette'] = True

                    fp = webdriver.FirefoxProfile(
                         r'C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\wxjvqcon.default-release-1')

                    options = webdriver.FirefoxOptions()
                    options.set_preference("dom.webdriver.enabled", False)
                    options.set_preference("dom.webnotifications.enabled", False)
                    binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
                    options.binary = binary

                    self.driver = webdriver.Firefox(capabilities=firefox_capabilities, firefox_profile=fp,
                                                     firefox_binary='C:/Program Files/Mozilla Firefox/firefox.exe',
                                                     executable_path=r'C:\Users\Administrator\PycharmProjects\bet1\geckodriver.exe',
                                                     options=options)
                    time.sleep(2)


                    answer_ = self.check_ip()
                    if answer_:
                        # повторная проверка
                        print('повторная проверка')
                        time.sleep(5)
                        answer2 = self.check_ip()
                        if answer2:
                            print('[+] Stop scerch for new ip')
                            break
                self.log_in_bet365(self.bet365_login, self.bet365_password, '1')
         except:
             pass


    def check_ip(self):
        self.driver.get('https://www.bet365.com/')
        for i in range(3):
            try:
                try:
                    time.sleep(3)
                    self.driver.find_element_by_class_name('hm-MainHeaderRHSLoggedOutWide_LoginContainer')
                    print('[+] OK VPN')
                    return True
                except:
                    print('wait...')
            except:
                pass
        print('[-] Next one ...')

        return False


class ChromeCloudFlareProtection(FireFoxDriverWithProxy):
    def __init__(self):

        self.profile = data.chrome_profile_directory

        chrome_capabilities = webdriver.DesiredCapabilities.CHROME
        chrome_capabilities['acceptSslCerts'] = True

        chrome_capabilities["pageLoadStrategy"] = "none"


        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        # options.add_argument("user-agent=" + user_agent)

        users_data_dir = data.chrome_users_data_dir
        profile_directory = self.profile

        options.add_argument(f"user-data-dir={users_data_dir}")
        options.add_argument(f'--profile-directory={profile_directory}')

        driver = webdriver.Chrome(chrome_options=options, desired_capabilities=chrome_capabilities, executable_path=r'chromedriver.exe')

        # driver.get('https://2ip.ru')
        time.sleep(3)
        # driver.get('https://positivebet.com/')
        self.driver = driver


    def load_cookies(self, url, cookie_path):
        self.driver.get(url)
        time.sleep(5)

        for cookie in pickle.load(open(cookie_path, 'rb')):
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        time.sleep(1)

        print(f'[+] Cookies для {url} успешно загружены!')


    def go_to_bet_from_positivebet_an_return_url(self, element):
        '''Сложный код, котыпый закрывает браузер, если он завис'''
        class TimeoutError(Exception):
            pass

        class InterruptableThread(threading.Thread):
            def __init__(self, func, *args, **kwargs):
                threading.Thread.__init__(self)
                self._func = func
                self._args = args
                self._kwargs = kwargs
                self._result = None

            def run(self):
                self._result = self._func(*self._args, **self._kwargs)

            @property
            def result(self):
                return self._result

        class timeout(object):
            def __init__(self, sec):
                self._sec = sec

            def __call__(self, f):
                def wrapped_f(*args, **kwargs):
                    it = InterruptableThread(f, *args, **kwargs)
                    it.start()
                    it.join(self._sec)
                    if not it.is_alive():
                        return it.result
                    raise TimeoutError('execution expired')

                return wrapped_f

        @timeout(4)
        def chrome_get_url(driver, current_page):
            url1 = 'No_url'
            try:
                for i in range(500):
                    url1 = driver.current_url
                    if url1 is None:
                        print('no_url122(10')
                        return 'no_url'
                    if 'bet365' in url1:
                        break
                driver.close()
                driver.switch_to.window(current_page)
            except Exception as er:
                pass

            return url1


        def close_chrome():
            print('Браузер завис! Закрываем его!')
            pyautogui.PAUSE = 1.5
            pyautogui.FAILSAFE = True

            open_chrome = pyautogui.locateCenterOnScreen('open_chrome.png', grayscale=True, confidence=0.8)
            pyautogui.rightClick(open_chrome[0], open_chrome[1])
            time.sleep(0.5)
            pyautogui.leftClick(open_chrome[0], open_chrome[1] - 42)
        '''Конец сложного кода'''

        current_page = self.driver.current_window_handle
        try:
            element.click()
        except:
            print('Не получилось получить ссылку(1)')
            return 0

        tabs = self.driver.window_handles
        while True:
            if len(tabs) > 1:
                break
            else:
                tabs = self.driver.window_handles

        self.driver.switch_to.window(tabs[-1])

        try:
            url1 = chrome_get_url(self.driver, current_page)
            return url1
        except Exception as er:
            close_chrome()
            return f'no_url :(v{er}'




    def restart_driver(self):
        self.driver.quit()

        chrome_capabilities = webdriver.DesiredCapabilities.CHROME
        chrome_capabilities['acceptSslCerts'] = True

        chrome_capabilities["pageLoadStrategy"] = "none"

        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        # options.add_argument("user-agent=" + user_agent)

        users_data_dir = data.chrome_users_data_dir
        profile_directory = self.profile

        options.add_argument(f"user-data-dir={users_data_dir}")
        options.add_argument(f'--profile-directory={profile_directory}')

        driver = webdriver.Chrome(chrome_options=options, desired_capabilities=chrome_capabilities, executable_path=r'chromedriver.exe')

        time.sleep(3)

        self.driver = driver



'Команда2 Тм(1.5)'