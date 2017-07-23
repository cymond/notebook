
import pandas as pd
from dbutils.panama import q_download
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')
#start_date = '20170605'
maturity = '202006'
mkt_ser = pd.Series({"QUANDL":"ED","IB":"GE",
                           "SECTYPE":"FUT","CURRENCY":"USD",
                           "Q_EXCHANGE" :"CME","IB_EXCHANGE" :"GLOBEX",
                           "MULTIPLIER":0})
result = q_download(engine, "EDOLLAR", maturity)
print(result)