import os
import json
import pandas as pd
import yfinance as yf
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from sys import argv


def clear_output():
    os.system(command='cls' if os.name == 'nt' else 'clear')
    
    
class SettingsNotLoadFromFile(Exception):
    def __init__(self, *args):
        clear_output()
        super().__init__(*args)


class TypeFetchNotExists(Exception):
    def __init__(self, *args):
        clear_output()
        super().__init__(*args)
        

class InvestTrade:
    def __init__(self, fetch: str ='stocks') -> None:
        self._fetch = fetch
        self._settings = {}
        self.__load_settings()
        if not self._settings:
            raise SettingsNotLoadFromFile('Arquivo de configuração não carregado! Verifique se o mesmo existe.')
        
        self._symbols: list[str] = [symbol + ".SA" for symbol in self._settings['symbols'][self._fetch]]
    
    def __load_settings(self):
        try:
            with open(file='settings.json', mode='r', encoding='utf-8') as json_file:
                self._settings = json.load(fp=json_file)
                
        except FileNotFoundError:
            print("O arquivo se configuração não foi encontrado!")

    def collect_data_from_symbol(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executar sem interface gráfica
        chrome_options.add_argument('--log-level=3')  # Suprime logs
        chrome_options.add_argument("--disable-gpu")  # Necessário para sistema Windows
        chrome_options.add_argument("--disable-dev-shm-usage")  # Evitar problemas de memória em containers
        chrome_options.add_argument('--ignore-certificate-errors')  # Ignora erros SSL
        driver = Chrome(service=Service(executable_path=ChromeDriverManager().install()), options=chrome_options)
        
        data = []
        for symbol in self._symbols:
            if self._fetch == 'bdrs':
                url: str = f"https://investidor10.com.br/bdrs/{symbol}/"
                print(url)
                driver.get(url=url)
                
                # 1
                header_cards_ticker = driver.find_element(by=By.ID, value='cards-ticker')
                
                # 2
                table_indicators = driver.find_element(by=By.ID, value='table-indicators')
                
                # 3
                table_indicators_company = driver.find_element(by=By.ID, value='table-indicators-company')
                
                line = {
                    'COTAÇÃO': header_cards_ticker.find_element(by=By.CLASS_NAME, value='cotacao').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    'VARIAÇÃO (12M)': header_cards_ticker.find_element(by=By.CLASS_NAME, value='pl').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    
                    # Indicadores
                    'P/L': header_cards_ticker.find_element(by=By.CLASS_NAME, value='val').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    'P/VP': header_cards_ticker.find_element(by=By.CLASS_NAME, value='vp').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    'DY': header_cards_ticker.find_element(by=By.CLASS_NAME, value='dy').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    'PAYOUT': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[5]/div[1]').text,
                    'ROE': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[20]/div[1]').text,
                    'ROIC': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[21]/div[1]').text,
                    'LPA': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[18]/div[1]').text,
                    'VPA': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[17]/div[1]').text,
                    'P/EBIT': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[13]/div[1]').text,
                    'DÍVIDA LÍQUIDA / PATRIMÔNIO': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[26]/div[1]').text,
                    'DÍVIDA LÍQUIDA / EBITDA': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[24]/div[1]').text,
                    'DÍVIDA LÍQUIDA / EBIT': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[25]/div[1]').text,
                    'CAGR RECEITAS 5 ANOS': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[30]/div[1]').text,
                    'CAGR LUCROS 5 ANOS': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[31]/div[1]').text,
                    
                    # Informações da companhia
                    'SETOR': table_indicators_company.find_element(by=By.XPATH, value='//*[@id="table-indicators-company"]/div[14]/a/span[2]').text,
                    'SUBSETOR': table_indicators_company.find_element(by=By.XPATH, value='//*[@id="table-indicators-company"]/div[15]/a/span[2]').text,
                }
                data.append(line)
                       
            elif self._fetch == 'funds':
                url: str = f"https://investidor10.com.br/fiis/{symbol}/"
            
            elif self._fetch == 'stocks':
                url: str = f"https://investidor10.com.br/acoes/{symbol}/"
                driver.get(url=url)
                
                # 1
                header_cards_ticker = driver.find_element(by=By.TAG_NAME, value='section').find_element(by=By.ID, value='cards-ticker')
                
                # 2
                table_indicators = driver.find_element(by=By.ID, value='table-indicators')
                
                # 3
                table_indicators_company = driver.find_element(by=By.ID, value='table-indicators-company')
                
                line = {
                    'COTAÇÃO': header_cards_ticker.find_element(by=By.CLASS_NAME, value='cotacao').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    'VARIAÇÃO (12M)': header_cards_ticker.find_element(by=By.CLASS_NAME, value='pl').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    
                    # Indicadores
                    'P/L': header_cards_ticker.find_element(by=By.CLASS_NAME, value='val').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    'P/VP': header_cards_ticker.find_element(by=By.CLASS_NAME, value='vp').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    'DY': header_cards_ticker.find_element(by=By.CLASS_NAME, value='dy').find_element(by=By.CLASS_NAME, value='_card-body').text,
                    'PAYOUT': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[5]/div[1]').text,
                    'ROE': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[20]/div[1]').text,
                    'ROIC': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[21]/div[1]').text,
                    'LPA': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[18]/div[1]').text,
                    'VPA': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[17]/div[1]').text,
                    'P/EBIT': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[13]/div[1]').text,
                    'DÍVIDA LÍQUIDA / PATRIMÔNIO': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[26]/div[1]').text,
                    'DÍVIDA LÍQUIDA / EBITDA': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[24]/div[1]').text,
                    'DÍVIDA LÍQUIDA / EBIT': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[25]/div[1]').text,
                    'CAGR RECEITAS 5 ANOS': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[30]/div[1]').text,
                    'CAGR LUCROS 5 ANOS': table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[31]/div[1]').text,
                    
                    # Informações da companhia
                    'SETOR': table_indicators_company.find_element(by=By.XPATH, value='//*[@id="table-indicators-company"]/div[14]/a/span[2]').text,
                    'SUBSETOR': table_indicators_company.find_element(by=By.XPATH, value='//*[@id="table-indicators-company"]/div[15]/a/span[2]').text,
                }
                data.append(line)
            
            
        
            else:
                raise TypeFetchNotExists(f'Tipo de consulta não reconhecida: {self._fetch}')
        
    def strategy(self):
        print('Fazendo download dos valores de fechamento dos ativos selecionados.')
        
        df_yf: pd.DataFrame = yf.download(tickers=self._symbols, period='6mo', progress=True)
        if not df_yf.empty:
            alerts = []
            periods: dict = self._settings['crossover']
            print("Começando a fazer o calculo para cada ativo para identificar o cruzamento de alta...")
            for symbol in self._symbols:
                df_symbol: pd.DataFrame = pd.DataFrame()
                df_symbol['Open'] = df_yf['Open'][symbol]
                df_symbol['Close'] = df_yf['Close'][symbol]
                df_symbol['High'] = df_yf['High'][symbol]
                df_symbol['Low'] = df_yf['Low'][symbol]
                df_symbol['Volume'] = df_yf['Volume'][symbol]
                df_symbol[f'MME_{periods['short_period']}'] = df_symbol['Close'].ewm(span=periods['short_period']).mean()
                df_symbol[f'MME_{periods['long_period']}'] = df_symbol['Close'].ewm(span=periods['long_period']).mean()
                df_symbol['CrossOver'] = "-"
                df_symbol.reset_index(inplace=True)
                df_symbol['Date'] = df_symbol['Date'].dt.strftime(date_format='%Y-%m-%d')
                
                for i in range(len(df_symbol) - 1):
                    if df_symbol[f'MME_{periods['short_period']}'].iloc[i] < df_symbol[f'MME_{periods['long_period']}'].iloc[i] and \
                        df_symbol[f'MME_{periods['short_period']}'].iloc[i+1] > df_symbol[f'MME_{periods['long_period']}'].iloc[i+1]:
                            df_symbol.loc[i+1, 'CrossOver'] = "Cruzamento de alta"
                
                df_filtered: pd.DataFrame = df_symbol[-1:]
                df_filtered: pd.DataFrame = df_filtered[df_filtered['CrossOver'] != '-']            
                if not df_filtered.empty:
                    alerts.append(symbol)
            
            self._symbols = alerts
            self.collect_data_from_symbol()
                
        else:
            clear_output()
            print('Dataframe com valores de fechamento dos ativos está vazio!')       

if __name__ == '__main__':
    if "--fetch" in argv or '-f' in argv:
        app = InvestTrade(fetch=argv[argv.index('--fetch') + 1])
        app.strategy()
        