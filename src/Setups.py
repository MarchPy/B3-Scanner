import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from rich.console import Console


console = Console()


class Setups:
    def __init__(self, settings: dict) -> None:
        self.__settings = settings
        self._result = {}
    
    def _test_setups(self, symbols: list):
        df_yf = yf.download(tickers=symbols, period='1y', interval='1d')
        for symbol in symbols:
            console.print(f'[{datetime.now().strftime(format='%H:%M:%S')}] -> [[blue bold]Coletando dados históricos do ativo[/]] :: {symbol[:-3]}')
            
            df_tmp: pd.DataFrame = pd.DataFrame()
            df_tmp['Open'] = df_yf['Open'][symbol]
            df_tmp['High'] = df_yf['High'][symbol]
            df_tmp['Low'] = df_yf['Low'][symbol]
            df_tmp['Close'] = df_yf['Close'][symbol]
            df_tmp['Volume'] = df_yf['Volume'][symbol]
            
            # Testando setups
            self._result[symbol[:-3]] = {
                'Larry Williams': self.larry_williams(df=df_tmp),
                'Cruzamento de médias': self.crossover(df=df_tmp),
                'Vola. Anual': self.calculate_volatility(df=df_tmp)
            }

    # Setup N°1...
    def larry_williams(self, df: pd.DataFrame) -> bool:
        config: dict = self.__settings['setups']['larry_williams']
        short_period = config['short_period']
        filter_ma = config['filter_ma']
        
        df[f'MM_{filter_ma}'] = df['Close'].rolling(window=filter_ma).mean()
        if config['exponential']:
            df[f'MM_{short_period}'] = df['Close'].ewm(span=short_period).mean()
        
        else:
            df[f'MM_{short_period}'] = df['Close'].rolling(window=short_period).mean()
        
        if df['Close'].iloc[-1] > df[f'MM_{filter_ma}'].iloc[-1]:        
            if df['Close'].iloc[-2] < df[f'MM_{short_period}'].iloc[-2] and df['Close'].iloc[-1] > df[f'MM_{short_period}'].iloc[-1]:
                return True
            
            else:
                return False
            
        else:
            return False
            
    # Setup N°2...
    def crossover(self, df: pd.DataFrame) -> bool:
        config: dict = self.__settings['setups']['crossover']
        short_period = config['short_period']
        long_period = config['long_period']
        
        if config['exponential']:
            df[f'MM_{short_period}'] = df['Close'].ewm(span=short_period).mean()
            df[f'MM_{long_period}'] = df['Close'].ewm(span=long_period).mean()
        
        else:
            df[f'MM_{short_period}'] = df['Close'].rolling(window=short_period).mean()
            df[f'MM_{long_period}'] = df['Close'].rolling(window=long_period).mean()
        
       
        if df[f'MM_{short_period}'].iloc[-2] < df[f'MM_{long_period}'].iloc[-2] and df[f'MM_{short_period}'].iloc[-1] > df[f'MM_{long_period}'].iloc[-1]:
            return True
        
        else:
            return False

    def calculate_volatility(self, df: pd.DataFrame) -> float:
        df['Log Return'] = np.log(df['Close'] / df['Close'].shift(1))
        df = df.dropna()
        daily_volatility = df['Log Return'].std()
        annualized_volatility = daily_volatility * np.sqrt(252)

        return annualized_volatility * 100
