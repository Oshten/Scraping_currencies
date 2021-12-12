from decimal import Decimal
from pprint import pprint

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
            if option_currency.get_text(strip=True) == currency:
                code_currency = option_currency.attrs['value']
                return code_currency
        else:
            print('Неверный запрос')
    else:
        print('Сайт не доступен.')

def collecting_statistics(code_currensy, start_date='01.07.1992', finally_date='12.12.2021'):
    '''Сохраняет статистику с сайта в список словарей'''
    url = f'https://cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.so=1&UniDbQuery.mode=1&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.VAL_NM_RQ={code_currensy}&UniDbQuery.From={start_date}&UniDbQuery.To={finally_date}'
    resalt = requests.get(url=url, headers=HEADERS)
    if resalt.status_code == 200:
        content = BeautifulSoup(resalt.text, 'html.parser').find('div', class_='table')
        statistics = []
        table_cells = content.find_all('tr')
        for namber, cell in enumerate(table_cells):
            statistic_dict = dict()
            if namber < 2:
                continue
            information = cell.find_all('td')
            try:
                date = information[0].get_text(strip=True)
                quentity = information[1].get_text(strip=True)
                value = information[2].get_text(strip=True).replace(',', '.').replace(' ', '')
            except IndexError:
                continue
            statistic_dict['date'] = date
            statistic_dict['rate_currensy'] = str(Decimal(value) / Decimal(quentity))
            statistics.append(statistic_dict)
        return statistics
    else:
        print('Сайт не доступен.')


def run(currensy):
    code_currency = find_code_currency(currency=currensy)
    statistics = collecting_statistics(code_currensy=code_currency, start_date='01.12.2000')
    pprint(statistics)

if __name__ == '__main__':
    run('Югославский новый динар')