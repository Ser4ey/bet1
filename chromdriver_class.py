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
    def __init__(self, path_to_geckodriver, user_agent, proxy, proxy_login_and_password, type_of_account, final_balance, account_code_name):
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

        self.driver = driver
        self.driver.get('https://2ip.ru/')
        self.type_of_account = type_of_account
        self.final_balance = final_balance
        self.account_code_name = account_code_name
        self.current_account_balance = -1

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

        if self.type_of_account == '.com':

            try:
                self.driver.get('https://www.bet365.com/')
            except:
                pass

            while True:
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
        self.bet365_account_name = login

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
            try:
                bet365balance = self.driver.find_element_by_class_name('hm-MainHeaderMembersWide_Balance').text
                bet365balance = bet365balance.split(',')[0]
                bet365balance = bet365balance.strip()
                bet365balance = bet365balance.replace(' ', '')
                bet365balance = float(bet365balance)
                print(f'Баланс аккаунта {bet365balance}')
            except:
                bet365balance = 500
                print(f'Баланс аккаунта {bet365balance}')
            value = (bet365balance/100)*value

            if value < 10:
                value = float(value)
            else:
                value = int(value)

        self.driver.find_element_by_class_name('qbs-NormalBetItem_DetailsContainer ') \
            .find_element_by_class_name('qbs-StakeBox_StakeInput ').click()
        time.sleep(0.3)
        self.driver.find_element_by_tag_name("body").send_keys(str(value))
        time.sleep(1)
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

        #Попытка реанимировать сайт .com версии (пропадает соединение)
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

    def make_cyber_football_bet(self, url, bet_type, coef, bet_value):
        #изменение доменной зоны ссылки
        if self.type_of_account == '.com':
            url = url.replace('.ru', '.com')
        else:
            url = url.replace('.com', '.ru')


        #Попытка закрыть предыдушее окно ставки, если ставка не была проставлена.
        try:
            self.driver.find_element_by_class_name('qbs-NormalBetItem_Indicator ').click()
        except:
            pass

        #Попытка закрыть окно неактивности на .com версии
        try:
            self.driver.find_element_by_class_name('alm-ActivityLimitAlert_Button ').click()
        except:
            pass

        #Попытка закрыть купоны ставок(когда скапливается много ставок в купоне)
        self.close_cupon()

        #Попытка реанимировать сайт .com версии (пропадает соединение)
        if self.type_of_account == '.com':
            while True:
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



        if bet_type == 'П1' or bet_type == 'П2' or bet_type == '1' or bet_type == '2' or bet_type == 'X' or bet_type == 'Х':
            self.make_cyber_football_bet_P1_P2_X(url, bet_type, coef, bet_value)
        elif bet_type == '1X' or bet_type == 'X2' or bet_type == '1Х' or bet_type == 'Х2' or bet_type == '12' or bet_type == '21':
            self.make_cyber_football_bet_double_chance_P1X_XP2_P1P2(url, bet_type, coef, bet_value)
        elif bet_type[:13] == 'Гола не будет':
            self.make_cyber_football_bet_gola_ne_budet(url, bet_type, coef, bet_value)
        elif bet_type == 'Чет' or bet_type == 'Нечет':
            self.make_cyber_football_bet_odd_or_even(url, bet_type, coef, bet_value)
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

            if text1 == 'ГОЛЫ МАТЧА':
                line = i
                break

        bet_element = list_of_bets[line]
        text = bet_element.find_element_by_class_name('sip-MarketGroupButton_Text ').text

        if text != 'ГОЛЫ МАТЧА':
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

        driver = webdriver.Chrome(chrome_options=options, desired_capabilities=chrome_capabilities, executable_path=r'C:\Users\Пользователь 9\PycharmProjects\stavki_bet365\chromedriver.exe')

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

        driver = webdriver.Chrome(chrome_options=options, desired_capabilities=chrome_capabilities, executable_path=r'C:\Users\Пользователь 9\PycharmProjects\stavki_bet365\chromedriver.exe')

        time.sleep(3)

        self.driver = driver



'Команда2 Тм(1.5)'