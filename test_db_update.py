from dbutils.panama import *
import pandas as pd
from sqlalchemy import create_engine

price_table = "edollar_price"
carry_table = "edollar_carrydata"

engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')
tables = init_tables(engine=engine, market="EDOLLAR")

price_df = tables[0]
carry_df = tables[1]

price_df.reset_index(inplace=True)
carry_df.reset_index(inplace=True)
price_df.to_sql(name=price_table, con=engine, if_exists='replace', index=False)
carry_df.to_sql(name=carry_table, con=engine, if_exists='replace', index=False)

print(price_df)
print(carry_df)

'''
roll_df = pd.read_csv("admin/roll_history.csv", \
                      dtype={'CARVER':str, 'PRICE_CONTRACT': str, \
                              'CARRY_CONTRACT':str})
symbols_sr = roll_df['CARVER'].copy()
symbols_sr.drop_duplicates(inplace=True)
symbols_df = pd.DataFrame(symbols_sr).sort_values('CARVER')


for symbol in symbols_df.itertuples():
    if symbol.CARVER == 'EDOLLAR':              # For now test with EDOLLAR
        price_table = symbol.CARVER.lower() + "_price"
        carry_table = symbol.CARVER.lower() + "_carrydata"
        temp_df = roll_df[roll_df['CARVER'] == symbol.CARVER].copy()
        #temp_df = temp_df[temp_df['PRICE_CONTRACT'] > '200812']
        #temp_df = temp_df[temp_df['PRICE_CONTRACT'] < '200906']
        #print(temp_df.head(2))

        splicedPrices = init_tables(engine=engine, market=symbol.CARVER, rolls=temp_df)   # Just first two maturities...
        price_df = splicedPrices[0]
        carry_df = splicedPrices[1]
        price_df.reset_index(inplace=True)
        carry_df.reset_index(inplace=True)
        price_df.to_sql(name=price_table, con=engine, if_exists='replace', index=False)
        carry_df.to_sql(name=carry_table, con=engine, if_exists='replace', index=False)
        print(price_df)
        print(carry_df)
'''