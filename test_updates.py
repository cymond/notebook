from dbutils.panama import *
import pandas as pd
from sqlalchemy import create_engine

roll_df = pd.read_csv("admin/roll_history.csv", dtype={'CARVER':str, 'PRICE_CONTRACT': str} )
#print(roll_df)
symbols_sr = roll_df['CARVER'].copy()
symbols_sr.drop_duplicates(inplace=True)
symbols_df = pd.DataFrame(symbols_sr).sort_values('CARVER')
engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')
market = "EDOLLAR"
update_data_tbls(engine, market)