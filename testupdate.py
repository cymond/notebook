import pandas as pd
from dbutils.panama import update_series
from sqlalchemy import create_engine


engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')
roll_schedule_df = pd.read_sql_table(table_name="roll_schedule", con=engine)
roll_df = roll_schedule_df[roll_schedule_df['CARVER'] == 'EDOLLAR'][-5:-2].copy()
market_series = pd.Series({"CARVER":"EDOLLAR","QUANDL": "ED", "IB": "GE", "SECTYPE": "FUT", "CURRENCY": "USD",
                     "Q_EXCHANGE": "CME", "IB_EXCHANGE": "GLOBEX", "MULTIPLIER": 0})

coll = update_series(engine, market_series, roll_df ) 