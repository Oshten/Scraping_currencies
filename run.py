import requests
from bs4 import BeautifulSoup

URL = 'https://cbr.ru/currency_base/dynamics/'
HEADERS = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.135 YaBrowser/21.6.2.855 Yowser/2.5 Safari/537.36', 'accept' : '*/*'}


def find_code_currency(currency: str):
    '''Поиск кода валюты, необходимого для последующего запроса'''
    result = requests.get(url=URL, headers=HEADERS)
    if result.status_code == 200:
        content = BeautifulSoup(result.text, 'html.parser')
        select = content.find_all('option')
        for option_currency in select:
            if option_currency.get_text().strip() == currency:
                code_currency = option_currency.attrs['value']
                return code_currency
        else:
            print('Неверный запрос')
    else:
        print('Сайт не доступен.')


def run(currensy):
    find_code_currency(currency=currensy)

if __name__ == '__main__':
    run('Югославский новый динар')