import json
from sys import argv
from src.InvestTrade import InvestTrade


if __name__ == '__main__':
    try:
        with open(file='settings.json', mode='r', encoding='utf-8') as json_file:
            settings = json.load(fp=json_file)
            app = InvestTrade(settings=settings)
            app.collect_data_from_symbol()
            
    except FileNotFoundError:
        print("O arquivo se configuração não foi encontrado!")
