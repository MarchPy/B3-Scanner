import os
import pandas as pd
from datetime import datetime
from rich.console import Console
from selenium.webdriver import Chrome
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from src.Exceptions import TypeFetchNotExists
from src.Setups import Setups


console = Console()


def safe_find_element(find_func, default: int=0):
    try:
        return find_func()
    
    except exceptions.NoSuchElementException:
        return default
    
    except AttributeError:
        return default


def clear_output() -> None:
    os.system(command='cls' if os.name == 'nt' else 'clear')
    

class InvestTrade(Setups):
    def __init__(self, settings: dict, fetch: str ='stocks') -> None:
        self.__settings = settings
        super().__init__(settings=self.__settings)
        self._fetch = fetch
 
        self._fetch_options = self.__settings['symbols'].keys()
        if self._fetch not in self._fetch_options:
            raise TypeFetchNotExists('Tipo de parâmetro não aceito! Verifique as chaves do arquivo settings.json para ver as possibilidades de chaves.')
        
        self._symbols: list[str] = self.__settings['symbols'][self._fetch]

    def collect_data_from_symbol(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")        # Executar sem interface gráfica
        chrome_options.add_argument('--log-level=3')     # Suprime logs
        chrome_options.add_argument("--disable-gpu")     # Necessário para sistema Windows
        chrome_options.add_argument("--disable-dev-shm-usage")  # Evitar problemas de memória em containers
        chrome_options.add_argument('--ignore-certificate-errors')  # Ignora erros SSL
        driver = Chrome(
            service=Service(
                executable_path=ChromeDriverManager().install()
            ),
            options=chrome_options
        )
        
        i = 1
        data: list[dict] = []
        for symbol in self._symbols:
            console.print(f'[{datetime.now().strftime(format='%H:%M:%S')}] -> [{i} de {len(self._symbols)}]-[[blue bold]Coletando dados fundamentalistas do ativo[/]] :: {symbol} ->', end=' ')
            url: str = f"https://investidor10.com.br/{self._fetch}/{symbol}/"

            try:
                driver.get(url=url)
                try:
                    driver.find_element(by=By.CLASS_NAME, value='antialiased')
                    console.print(f"[[red]404 Not found[/]]")
                        
                except exceptions.NoSuchElementException:
                    header_cards_ticker = safe_find_element(find_func=lambda: driver.find_element(by=By.TAG_NAME, value='section').find_element(by=By.ID, value='cards-ticker'))
                    table_indicators = safe_find_element(find_func=lambda: driver.find_element(by=By.ID, value='table-indicators'))
                    table_indicators_company = safe_find_element(find_func=lambda: driver.find_element(by=By.ID, value='table-indicators-company'))

                    if self._fetch == 'acoes':
                        line = {
                            'ATIVO': symbol,
                            'COTAÇÃO': safe_find_element(find_func=lambda: header_cards_ticker.find_element(By.CLASS_NAME, 'cotacao').find_element(By.CLASS_NAME, '_card-body').text),
                            'VARIAÇÃO (12M)': safe_find_element(find_func=lambda: header_cards_ticker.find_element(By.CLASS_NAME, 'pl').find_element(By.CLASS_NAME, '_card-body').text),
                            
                            # Indicadores
                            'P/L': safe_find_element(find_func=lambda: header_cards_ticker.find_element(By.CLASS_NAME, 'val').find_element(By.CLASS_NAME, '_card-body').text),
                            'P/VP': safe_find_element(find_func=lambda: header_cards_ticker.find_element(By.CLASS_NAME, 'vp').find_element(By.CLASS_NAME, '_card-body').text),
                            'DY': safe_find_element(find_func=lambda: header_cards_ticker.find_element(By.CLASS_NAME, 'dy').find_element(By.CLASS_NAME, '_card-body').text),
                            'PAYOUT': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[5]/div[1]').text),
                            'ROE': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[20]/div[1]').text),
                            'ROIC': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[21]/div[1]').text),
                            'LPA': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[18]/div[1]').text),
                            'VPA': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[17]/div[1]').text),
                            'P/EBIT': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[13]/div[1]').text),
                            'DÍVIDA LÍQUIDA / PATRIMÔNIO': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[26]/div[1]').text),
                            'DÍVIDA LÍQUIDA / EBITDA': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[24]/div[1]').text),
                            'DÍVIDA LÍQUIDA / EBIT': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[25]/div[1]').text),
                            'CAGR RECEITAS 5 ANOS': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[24]/div[1]/span').text),
                            'CAGR LUCROS 5 ANOS': safe_find_element(find_func=lambda: table_indicators.find_element(By.XPATH, '//*[@id="table-indicators"]/div[25]/div[1]/span').text),
                            
                            # Informações da companhia
                            'SETOR': safe_find_element(lambda: table_indicators_company.find_element(By.XPATH, '//*[@id="table-indicators-company"]/div[14]/a/span[2]').text),
                            'SUBSETOR': safe_find_element(lambda: table_indicators_company.find_element(By.XPATH, '//*[@id="table-indicators-company"]/div[15]/a/span[2]').text),
                        }
            
                        data.append(line)
                        
                    elif self._fetch == 'bdrs':
                        line = {
                            'ATIVO': symbol,
                            'COTAÇÃO': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='cotacao').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            'VARIAÇÃO (12M)': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='pl').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            
                            # Indicadores
                            'P/L': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='val').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            'P/VP': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='vp').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            'DY': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='dy').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            'ROE': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[6]/div[1]/span').text),
                            'ROIC': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[7]/div[1]/span').text),
                            'LPA': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[15]/div[1]/span').text),
                            'VPA': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[14]/div[1]/span').text),
                            'P/EBIT': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[11]/div[1]/span').text),
                
                            # Informações da companhia
                            'SETOR': safe_find_element(find_func=lambda: table_indicators_company.find_element(by=By.XPATH, value='//*[@id="table-indicators-company"]/div[6]/span[2]').text),
                            'INDUSTRIA': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators-company"]/div[7]/span[2]').text),
                            'PARIDADE DA BDR': safe_find_element(find_func=lambda: table_indicators_company.find_element(by=By.XPATH, value='//*[@id="table-indicators-company"]/div[8]/span[2]').text),
                        }
                        data.append(line)
                                
                    elif self._fetch == 'fiis':    
                        line = {
                            'ATIVO': symbol,
                            'COTAÇÃO': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='cotacao').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            'DY': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='dy').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            'LIQ. MED.': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='val').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            'P/VP': safe_find_element(find_func=lambda: header_cards_ticker.find_element(by=By.CLASS_NAME, value='vp').find_element(by=By.CLASS_NAME, value='_card-body').text),
                            
                            # Sobre a empresa
                            'RAZÃO SOCIAL': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[1]/div[2]/div/span').text),
                            'CNPJ': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[2]/div[2]/div/span').text),
                            'SEGMENTO': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[5]/div[2]/div/span').text),
                            'TIPO': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[6]/div[2]/div/span').text),
                            'PRAZO DE DURAÇÃO': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[7]/div[2]/div/span').text),
                            'TAXA DE ADMINISTRAÇÃO': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[9]/div[2]/div/span').text),
                            'VACÂNCIA': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[10]/div[2]/div/span').text),
                            'N. DE COTISTAS': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[11]/div[2]/div/span').text),
                            'VPA': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[13]/div[2]/div/span').text),
                            'ÚLT. RENDIMENTO': safe_find_element(find_func=lambda: table_indicators.find_element(by=By.XPATH, value='//*[@id="table-indicators"]/div[15]/div[2]/div/span').text),
                            
                        }
                        
                        data.append(line)

                    console.print(f"[[green]Dados coletados[/]]")
                
            except exceptions.UnexpectedAlertPresentException:
                console.print(f"[[red]UnexpectedAlertPresentException[/]]")
            
            except exceptions.TimeoutException:
                console.print(f"[[red]Tempo limite excedido ao carregar a página: {url}[/]]")
                
            i += 1
            
        # Tratando o dataframe final para realizar a filtragem
        df = pd.DataFrame(data=data)
        
        if self._fetch == 'fiis':
            df = df[ df['PRAZO DE DURAÇÃO'].isin(["INDETERMINADO", "DETERMINADO"])]
            df = self.format_columns(df=df)
            df['LIQ. MED.'] = df['LIQ. MED.'].apply(
                func=lambda x: int(
                    str(x)\
                        .replace('R$ ', '')\
                            .replace(',', '')\
                                .replace('.', '')\
                                    .replace(' K', '0')\
                                        .replace(' M', '0000')
                )
            )
            df['% Últ. Rendimento (M)'] = df['ÚLT. RENDIMENTO'] / df['COTAÇÃO'] * 100
            df['% Últ. Rendimento (A)'] = (df['ÚLT. RENDIMENTO'] / df['COTAÇÃO'] * 100) * 12
        
            df = self.get_df_filtered(df=df)
            self._test_setups(symbols=[symbol + ".SA" for symbol in df['ATIVO'].to_list()])
            for index, row in df.iterrows():
                symbol = row['ATIVO']
                for k, v in self._result[symbol].items():
                    df.at[index, k.upper()] = v

        
        self.save_file(df=df)
       
    @staticmethod
    def format_columns(df: pd.DataFrame) -> pd.DataFrame:
        columns_to_format = {
            'DY': float,
            'VARIAÇÃO (12M)': float,
            'P/VP': float,
            'COTAÇÃO': float,
            'ROE': float,
            'ROIC': float,
            'P/EBIT': float,
            'VPA': float,
            'LPA': float,
            'PAYOUT': float,
            'DÍVIDA LÍQUIDA / EBIT': float,
            'DÍVIDA LÍQUIDA / EBITDA': float,
            'DÍVIDA LÍQUIDA / PATRIMÔNIO': float,
            'CAGR LUCROS 5 ANOS': float,
            'CAGR RECEITAS 5 ANOS': float,
            'VACÂNCIA': float,
            'ÚLT. RENDIMENTO': float,
            'N. DE COTISTAS': int,
        }
        for column, typ in columns_to_format.items():
            try:
                if typ is float:
                    df[column] = df[column].apply(
                        func=lambda x: float(
                            str(x)\
                                .replace('.', '')\
                                    .replace(',', '.')\
                                        .replace('R$ ', '')\
                                            .replace('%', '')\
                                                .replace('-', '0')\
                                                    .strip()
                        )
                    )
                
                elif typ is int:
                    df[column] = df[column].apply(
                        func=lambda x: int(
                            str(x)\
                                .replace('.', '')\
                                    .replace(',', '')
                        ) if x != '-' else 0
                    )
            
            except KeyError:
                pass
        
        return df
    
    def get_df_filtered(self, df: pd.DataFrame) -> pd.DataFrame:
        config: dict = self.__settings['filter'][self._fetch]
        for k, v in config.items():
            min = v['min']
            max = v['max']
            
            if min is not None:
                df = df[df[k] >= min]
            
            if max is not None:
                df = df[df[k] <= max]
                
        return df
            
    def save_file(self, df: pd.DataFrame) -> None:
        save_file_path = f"Resultados/{datetime.now().strftime('%d-%m-%Y')}/{self._fetch}/"
        if not os.path.exists(path=save_file_path):
            os.makedirs(name=save_file_path)
        
        df.to_excel(excel_writer=f"{save_file_path}Planilha de dados fundamentalistas.xlsx", index=False)
            