import pandas as pd
from dbutils.panama import update_series
from sqlalchemy import create_engine
from wrapper_v2 import IBWrapper, IBclient
from swigibpy import Contract as IBcontract
callback = IBWrapper()
ib_client = IBclient(callback)


engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')

roll_schedule_df = pd.read_sql_table(table_name="roll_schedule", con=engine)

marketdata_df = pd.read_sql_table(table_name="marketdata", con=engine)
for row in marketdata_df.itertuples():
    market_series = row
    roll_df = roll_schedule_df[roll_schedule_df['CARVER'] == row.CARVER]
    print("========================", row.CARVER, "==========================================================")
    print(roll_df)
    print("==================================================================================================")
    coll = update_series(engine, ib_client, market_series, roll_df)


