import os
import pandas as pd
from src.Setups import Setups
from datetime import datetime
from rich.console import Console
from selenium.webdriver import Chrome
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


console: Console = Console()


def clear_output() -> None:
    os.system(command='cls' if os.name == 'nt' else 'clear')


class InvestTrade(Setups):
    def __init__(self, settings: dict) -> None:
        self.__settings = settings
        super().__init__(settings=self.__settings)

        self._symbol_category: list[str] = self.__settings['symbol_category']

    def collect_data_from_symbol(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument(argument='--log-level=3')     # Suprime logs
        chrome_options.add_argument(argument='--ignore-certificate-errors')  # Ignora erros SSL
        driver = Chrome(
            service=Service(
                executable_path=ChromeDriverManager().install()
            ),
            options=chrome_options
        )
        
        data: list[dict] = []
        for category, symbols in self._symbol_category.items():
            i = 1
            for symbol in symbols:
                try:
                    console.print(f'[{datetime.now().strftime(format='%H:%M:%S')}] -> [{i} de {len(symbols)}]-[[blue bold]Coletando dados fundamentalistas do ativo[/]] :: {symbol} ->', end=' ')
                    driver.get(url=f"https://statusinvest.com.br/{category}/{symbol}")
                    
                    line: dict[str] = {
                        'Ativo': symbol,
                        'Categoria': category,
                        'Preço atual': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[1]/div[1]/div/div[1]').find_element(by=By.CLASS_NAME, value='value').text,
                        'DY': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[1]/div[4]/div/div[1]').find_element(by=By.CLASS_NAME, value='value').text,
                        'Valorização (12M)': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[1]/div[5]/div/div[1]').find_element(by=By.CLASS_NAME, value='value').text,
                        'VPA': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[5]/div/div[1]').find_element(by=By.CLASS_NAME, value='value').text,
                        'P/VP': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[5]/div/div[2]').find_element(by=By.CLASS_NAME, value='value').text,
                        'Valor em caixa': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[5]/div/div[3]').find_element(by=By.CLASS_NAME, value='value').text,
                        'DY CAGR': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[5]/div/div[4]').find_element(by=By.CLASS_NAME, value='value').text,
                        'Valor CAGR': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[5]/div/div[5]').find_element(by=By.CLASS_NAME, value='value').text,
                        'N° de cotistas': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[5]/div/div[6]').find_element(by=By.CLASS_NAME, value='value').text,
                        'Rendim. médio (24M)': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[6]/div/div/div[1]').find_element(by=By.CLASS_NAME, value='value').text,
                        'Liq. méd. diária': driver.find_element(by=By.XPATH, value='//*[@id="main-2"]/div[2]/div[6]/div/div/div[3]').find_element(by=By.CLASS_NAME, value='value').text
                    }
                    data.append(line)
                    console.print('-[green bold]OK[/]-')
                    
                except exceptions.NoSuchElementException:
                    console.print('-[red bold]ERRO[/]-')
            
                i += 1
        
        df = pd.DataFrame(data=data)
        df.to_excel("Teste.xlsx", index=False)
        df = self.format_columns(df=df)
        df = self.get_df_filtered(df=df)
        df = self.ahp_gaussiano(df=df)
        # self._test_setups(symbols=df['Ativo'].tolist())
        self.save_file(df=df)

    def ahp_gaussiano(self, df: pd.DataFrame) -> pd.DataFrame:
        config: dict = self.__settings['ahp-gaussiano']
        df_copy = df.copy()
        df_copy = df_copy[[col for col in config['param'].keys()]]
        
        # Normalização dos critérios
        for k, v in config['param'].items():
            if v > 0:
                value = df_copy[k].max()
                df_copy[k].apply(lambda x: x / value)
                
            elif v < 0:
                value = df_copy[k].min()
                df_copy[k].apply(lambda x: value / x)
                
            else:
                pass
        
        # Calcular dos fatores gaussianos (Dividir o desvio padrão pela média)
        fator_gaussiano = [df_copy[col].std() / df_copy[col].mean() for col in df_copy.columns]

        # Normalização dos fatores gaussianos (Dividir o fator gaussiano, calculado individualmente, pela soma dos fatores gaussianos)
        soma_fatores = sum(fator_gaussiano)
        fatores_normalizados = [fg / soma_fatores for fg in fator_gaussiano]
        
        # Aplicação dos pesos normalizados às alternativas (Multiplicando cada fator normalizado pela coluna respectiva)
        df_copy = df_copy * fatores_normalizados

        # Cálculo da pontuação final para cada alternativa
        df_copy['Pontuação Final'] = df_copy.sum(axis=1)
        df = pd.merge(left=df, right=df_copy[['Pontuação Final']], left_index=True, right_index=True)
        df = df.sort_values(by='Pontuação Final', ascending=False).reset_index(drop=True)
        df['Pontuação Final'] = [i for i in range(1, len(df) + 1)]
        return df[:config['limite']]
            
    @staticmethod
    def format_columns(df: pd.DataFrame) -> pd.DataFrame:
        def clean_value(x):
            """Remove caracteres indesejados e converte para numérico."""
            if isinstance(x, str):
                x = x.replace('.', '') \
                    .replace(',', '.') \
                        .replace('R$ ', '') \
                            .replace('%', '') \
                                .replace(' K', '0') \
                                    .replace(' M', '0000') \
                                        .strip()
                
            return x if x not in ['-', ''] else '0'
        
        columns_to_format = {
            'Preço atual': float,
            'DY': float,
            'Valorização (12M)': float,
            'VPA': float,
            'P/VP': float,
            'Valor em caixa': float,
            'DY CAGR': float,
            'Valor CAGR': float,
            'N° de cotistas': int,
            'Rendim. médio (24M)': float,
            'Liq. méd. diária': int,
        }

        for column, dtype in columns_to_format.items():
            if column in df.columns:
                df[column] = pd.to_numeric(df[column].map(clean_value), errors='coerce').fillna(0).astype(dtype)

        return df
    
    def get_df_filtered(self, df: pd.DataFrame) -> pd.DataFrame:
        config: dict = self.__settings['filter']
        for k, v in config.items():
            min = v['min']
            max = v['max']
            
            if min is not None:
                df = df[df[k] >= min]
            
            if max is not None:
                df = df[df[k] <= max]
        
        # df = df[df['COTAÇÃO'] != 0]
        return df
            
    def save_file(self, df: pd.DataFrame) -> None:
        save_file_path = f"Resultados/{datetime.now().strftime('%d-%m-%Y')}/"
        if not os.path.exists(path=save_file_path):
            os.makedirs(name=save_file_path)
        
        df.to_excel(excel_writer=f"{save_file_path}Planilha de dados fundamentalistas.xlsx", index=False)
