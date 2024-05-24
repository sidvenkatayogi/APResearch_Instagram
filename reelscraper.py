from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import undetected_chromedriver as uc
import time
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urlparse
import csv
import pandas as pd

def from_user_get_reels(user: str) -> pd.Series:
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # options = webdriver.ChromeOptions()
    # options.add_experimental_option("detach", True)
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get(f"https://www.instagram.com/{user}/reels")

    elem = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class=" _acan _acap _acat _aj1- _ap30"]'))
    )

    tabs = driver.find_elements(By.CSS_SELECTOR, 'a[role="tab"]')

    # has_reels = False
    # for tab in tabs:
    #     print(tab)
    #     if (tab.get_attribute('aria-selected') == 'true') and (tab['href'] == f"/{user}/reels/"):
    #         has_reels = True
    # if not has_reels:
    #     print("No")
    #     return pd.Series()
    
    if len(tabs) < 3:
        # driver.close()
        return pd.Series()
    
    initial_height = driver.execute_script("return document.body.scrollHeight")
    soups = []
    bottom_tab = False
    corner_tab = False

    try:
        driver.find_element(By.CSS_SELECTOR, 'span[aria-label="Close"]')
        bottom_tab = True
    except Exception as e:
        pass
    try:
        driver.find_element(By.CSS_SELECTOR, 'svg[aria-label="Close"]')
        corner_tab = True
    except Exception as e:
        pass

    if bottom_tab:
        close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[aria-label="Close"]')))
        close_button.click()
    if corner_tab:
        close_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Close"]')))
        close_button.click()

    past = False
    at_end = False

    while not at_end:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        current_height = driver.execute_script("return document.body.scrollHeight")

        if current_height == initial_height:
            driver.execute_script("window.scrollBy(0, -100);")
            time.sleep(1)
            driver.execute_script("window.scrollBy(0, 100);")
            time.sleep(5)
            current_height = driver.execute_script("return document.body.scrollHeight")
            
        if current_height == initial_height:
            try:
                elem = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="x1ja2u2z x1afcbsf x1a2a7pz x6ikm8r x10wlt62 x71s49j x6s0dn4 x78zum5 xdt5ytf xl56j7k x1n2onr6"]'))
                )
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            except:
                at_end = True

        html = driver.page_source
        soups.append(BeautifulSoup(html, 'html.parser'))

        initial_height = current_height
    
    urls = []
    for soup in soups:
        elements = soup.find_all('a', class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd")

        urls.extend([element['href'] for element in elements if element['href'].startswith("/reel/")])

    shortcodes = pd.Series(urls).drop_duplicates()
    shortcodes = shortcodes.str.slice(6,-1)
    # print("finished")
    # driver.close()
    return shortcodes

if __name__ == '__main__':
    from_user_get_reels("mettaflix")
