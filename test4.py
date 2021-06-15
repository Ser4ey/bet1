import time
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import data

class FireFoxDriverWithVPN:
    def __init__(self, path_to_geckodriver, user_agent, proxy, proxy_login_and_password, type_of_account, final_balance,
                 account_code_name, is_reversed):
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



    def check_ip(self):
        self.driver.get('https://www.bet365.com/')
        for i in range(3):
            try:
                try:
                    time.sleep(3)
                    self.driver.find_element_by_class_name('hm-MainHeaderRHSLoggedOutWide_LoginContainer')
                    print('[+] Log in account with VPN')
                    return True
                except:
                    print('wait...')
            except:
                pass
        print('[-] Next one ...')

        return False




# d1 = FireFoxDriverWithVPN()
#
# d1.driver.refresh()
# print('end')
