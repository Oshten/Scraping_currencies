import argparse
from datetime import date, datetime
from decimal import Decimal
from pprint import pprint

import requests
from bs4 import BeautifulSoup
import pymysql

URL = 'https://cbr.ru/currency_base/dynamics/'
HEADERS = {'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.135 YaBrowser/21.6.2.855 Yowser/2.5 Safari/537.36', 'accept' : '*/*'}

DETA_NOW = date.today().strftime('%d.%m.%Y')





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

def collecting_statistics(code_currensy, start_deta='01.07.1992', finally_deta=DETA_NOW):
    '''Сохраняет статистику с сайта в список словарей'''
    url = f'https://cbr.ru/currency_base/dynamics/?UniDbQuery.Posted=True&UniDbQuery.so=1&UniDbQuery.mode=1&UniDbQuery.date_req1=&UniDbQuery.date_req2=&UniDbQuery.VAL_NM_RQ={code_currensy}&UniDbQuery.From={start_deta}&UniDbQuery.To={finally_deta}'
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
            statistic_dict['rate_currency'] = str(Decimal(value) / Decimal(quentity))
            statistics.append(statistic_dict)
        return statistics
    else:
        print('Сайт не доступен.')

def record_database(name_database, information):
    '''Создает в базе данных MySQL новую таблицу и записывает в нее информацию'''
    try:
        connection = pymysql.connect(
            host='localhost',
            user='newuser',
            passwd='password',
            db='Currency'
        )
        name_database = name_database.replace(" ", "_")
        query_for_create = f'CREATE TABLE {name_database} (date_observation VARCHAR(15), rate_currency VARCHAR(15));'
        cursor = connection.cursor()
        cursor.execute(query_for_create)
        for cell in information:
            query_fierst = f'INSERT INTO {name_database} (date_observation, rate_currency) '
            query_second = f'VALUES ("{cell["date"]}", {cell["rate_currency"]});'
            query_for_add = query_fierst + query_second
            cursor.execute(query_for_add)
            connection.commit()
    except:
        print('База данных не доступна')
    finally:
        cursor.close()
        connection.close()


def run(currensy):
    '''Запуск процесса скрапинга'''
    code_currency = find_code_currency(currency=currensy)
    if code_currency:
        statistics = collecting_statistics(code_currensy=code_currency)
        if statistics:
            record_database(name_database=currensy, information=statistics)
            print('Данные сохранены')

def add_argument():
    '''Добавить аргумент через командную строку'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--currency', '-c', required=True)
    argument = parser.parse_args()
    return argument

if __name__ == '__main__':
    argument = add_argument()
    currency = argument.currency.replace('_', ' ')
    print(currency)
    run(currensy=currency)