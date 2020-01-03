import configparser
import random
import time
from os.path import abspath

import requests
import yagmail
from bs4 import BeautifulSoup

USER_AGENT_LIST = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    # Firefox
    "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
]
SITES = [
    {"url": "http://www.example.com/itempage", "slug": "site1"},
    {"url": "http://www.example2.com/itempage", "slug": "site2"},
]
GMAIL_USER = "youruser@gmail.com"
GMAIL_PASSWORD = "yourpassword"

config = configparser.ConfigParser()
config.read("mr.ini")


def scrape_price(url, prefix):
    user_agent = random.choice(USER_AGENT_LIST)
    headers = {"User-Agent": user_agent}
    req = requests.get(url, headers=headers)
    old_price = float(config[prefix]["price"])
    if req.status_code == 200:
        souped = BeautifulSoup(req.text, features="html.parser")
        cnf = config[prefix]
        cnf["lastcheck"] = time.strftime("%d/%m/%Y - %H:%M:%S", time.localtime())
        cnf["oldprice"] = cnf["price"]
        cnf["price"] = souped.find_all(itemprop="price")[0].get("content")
        cnf["url"] = url
        cnf["failedLast"] = "False"
        cnf["lastHTTPStatus"] = str(req.status_code)
    else:
        cnf["lastHTTPStatus"] = str(req.status_code)
        cnf["failedLast"] = "True"
    if float(cnf["oldprice"]) - float(cnf["price"]) > 0:
        cnf["changed"] = "diminuito"  # eng: lowered
        send_mail(
            cnf["lastcheck"], cnf["oldprice"], cnf["price"], cnf["url"], cnf["changed"]
        )
    elif float(cnf["oldprice"]) - float(cnf["price"]) < 0:
        cnf["changed"] = "aumentato"  # eng: increased
        send_mail(
            cnf["lastcheck"], cnf["oldprice"], cnf["price"], cnf["url"], cnf["changed"]
        )
    elif float(cnf["oldprice"]) - float(cnf["price"]) == 0:
        cnf["changed"] = "stabile"  # eng: stable


def send_mail(lastcheck, oldprice, price, url, verb):
    sent_to = ["yourreceiver@example.com"]
    mail = f"""
    L'oggetto all'indirizzo {url} ha {verb} il suo prezzo da {oldprice} a {price}.
    Il controllo e' stato effettuato in data {lastcheck}.
    """
    # eng: The object at {url} {verb} its price from {oldprice} to {price}.
    # Last check: {lastcheck}
    yag = yagmail.SMTP(GMAIL_USER, GMAIL_PASSWORD)
    yag.send(to=sent_to, subject="Your subject", contents=mail)


for site in SITES:
    scrape_price(site["url"], site["slug"])

with open("mr.ini", "w") as configfile:
    config.write(configfile)
