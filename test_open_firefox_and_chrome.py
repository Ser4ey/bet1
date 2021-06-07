import chromdriver_class
import data
import time

firefox_driver = chromdriver_class.FireFoxDriver(data.path_to_geckodriver, data.positivebet_useragent)
print('[+] Firefox работает')

chrome_driver = chromdriver_class.ChromeCloudFlareProtection()
print('[+] Chrome работает')
time.sleep(5)

firefox_driver.close_session()
chrome_driver.close_session()
print('[+] The End.')