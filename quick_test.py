
import pandas as pd
from dbutils.panama import ib_download

market_series = pd.Series({"QUANDL": "ED", "IB": "GE", "SECTYPE": "FUT", "CURRENCY": "USD",
                           "Q_EXCHANGE": "CME", "IB_EXCHANGE": "GLOBEX", "MULTIPLIER": 0})
start_date = '20170605'
maturity = '201803'
result = ib_download(market_series, maturity, start_date=start_date)
print(result)
