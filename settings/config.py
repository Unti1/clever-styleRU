""" Модуль работы с браузерными ссылками"""
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

############################################
"""Прочие необходимые библиотеки"""
import requests
import traceback
import configparser
from threading import Thread
import platform
import csv
import sys
############################################


config = configparser.ConfigParser()
config.read(r'settings/settings.ini')  # читаем конфиг

def config_update():
    with open(r'settings/settings.ini', 'w') as f:
        config.write(f)
    config.read(r'settings/settings.ini')

import logging
logging.basicConfig(
    level=logging.INFO,
    filename="logs.log",
    format="%(asctime)s - %(module)s\n[%(levelname)s] %(funcName)s:\n %(lineno)d - %(message)s",
    datefmt='%H:%M:%S',
    encoding="utf-8"
)
