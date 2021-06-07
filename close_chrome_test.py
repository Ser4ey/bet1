import pyautogui
import time

def close_chrome():
    print('Браузер завис! Закрываем его!')
    pyautogui.PAUSE = 1.5
    pyautogui.FAILSAFE = True

    open_chrome = pyautogui.locateCenterOnScreen('open_chrome.png', grayscale=True, confidence=0.8)
    pyautogui.rightClick(open_chrome[0], open_chrome[1])
    time.sleep(0.5)
    pyautogui.leftClick(open_chrome[0], open_chrome[1] - 42)


time.sleep(2)
close_chrome()