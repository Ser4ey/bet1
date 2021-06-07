import time
import pickle
import pyautogui
from selenium import webdriver
from chromdriver_class import ChromeCloudFlareProtection


def close_chrome():
    pyautogui.PAUSE = 1.5
    pyautogui.FAILSAFE = True

    print(pyautogui.size())
    time.sleep(5)
    print(pyautogui.position())

    pyautogui.moveTo(420, 1062, duration=1)
    pyautogui.click()


url1 = 'https://bet365.com'
url2 = 'https://2ip.ru'
url3 = 'https://positivebet.com'

driver = ChromeCloudFlareProtection()

'''driver.driver.get(url1)
time.sleep(2)
print(1)
print(driver.driver.current_url)
print(2)'''

close_chrome()

'''
def get_url(url):
    # url += '/ru/bets/go/e/121132917/b/560/elid/4664871/k/a8c3d249cb92d6c4'
    url += '/ru/bets/go/e/121132917/b/42/elid/4664871/k/677e3d8a1d575308'
    driver.driver.get(url)

    for i in range(1000):
        url1 = driver.driver.current_url
        print(url1, i)




get_url(url3)


'''



