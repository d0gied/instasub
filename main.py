import random
from pywebio.output import put_markdown
from pywebio.platform.tornado import start_server
from pywebio.session import run_js
from selenium import webdriver
import pickle
from selenium.webdriver.chrome.options import Options
from pywebio.input import *
from pywebio.output import *
import os
import time

user_url = ''
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome('./chromedriver', chrome_options=options)


def auth():
    _driver = webdriver.Chrome('./chromedriver')

    _driver.get("https://instagram.com")
    while not _driver.get_cookie('sessionid'):
        pass

    pickle.dump(_driver.get_cookie("sessionid"), open('auth_data', 'wb'))
    _driver.close()


def main():
    put_markdown(f'# Авторизация')
    put_text('Вход...')

    if os.path.exists("auth_data"):
        token = pickle.load(open('auth_data', 'rb'))
        if token['expiry'] <= time.time():
            auth()
    else:
        auth()
    put_text('Подключение...')

    token = pickle.load(open('auth_data', 'rb'))
    driver.get("https://instagram.com/accounts/edit/")
    driver.implicitly_wait(1)
    driver.add_cookie(token)
    driver.refresh()
    driver.implicitly_wait(1)
    username = driver.find_element_by_xpath(
        "//input[@id='pepUsername']").get_attribute('value')

    while True:
        clear()
        put_markdown(f'# Авторизация')
        data = input_group(f"{username}", [actions(
            name="cmd", buttons=["Продолжить", "Войти"])])
        if data['cmd'] == 'Продолжить':
            break
        put_text('Вход...')
        auth()
        put_text('Подключение...')
        token = pickle.load(open('auth_data', 'rb'))
        driver.get("https://instagram.com/accounts/edit/")
        driver.implicitly_wait(1)
        driver.add_cookie(token)
        driver.refresh()
        driver.implicitly_wait(1)
        username = driver.find_element_by_xpath(
            "//input[@id='pepUsername']").get_attribute('value')

    user_url = input("URL пользователя", type=URL)
    clear()
    put_markdown(f'# Сканирование')
    put_text('Поиск...')
    driver.get(str(user_url))
    driver.implicitly_wait(3)
    sub_btn = driver.find_element_by_xpath(f"//a[@href='/{user_url.strip('/').split('/')[-1]}/following/']/span")
    num = int(sub_btn.text)
    sub_btn.click()
    driver.implicitly_wait(5)
    scrolling_element = driver.find_element_by_xpath("//div[@class='isgrP']")  
    put_markdown(f'Сканирование подписок...')
    put_processbar('bar', auto_close=True)
    cnt = 0
    while num != cnt:
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrolling_element)
        cnt = len(scrolling_element.find_elements_by_tag_name("li"))
        set_processbar('bar', cnt / num)
    put_markdown(f'***Количество подписок***: {num}')
    res = input_group('', [actions(name="cmd", buttons=["Продолжить", "Отмена"])])
    if res['cmd'] == 'Отмена':
        run_js('window.location.reload()')
        return
    clear()
    put_markdown(f'# Подписка')
    put_markdown(f'Подписываемся...')
    put_processbar('bar', auto_close=True)
    for i in range(num):
        button = driver.find_element_by_xpath(f"//li[@class='wo9IH'][{i + 1}]//button")
        set_processbar('bar', i / num, label=driver.find_element_by_xpath(f"//li[@class='wo9IH'][{i + 1}]//a[@class='FPmhX notranslate  _0imsa ']").text)
        if button.text == 'Подписаться':
            button.click()
        time.sleep(random.random() / 1.2 + 0.2)
        
    clear()
    put_markdown(f'# Готово!')
    res = input_group('', [actions(name="cmd", buttons=["Завершить"])])
    run_js('window.location.reload()')
    

start_server(main, auto_open_webbrowser=True)
