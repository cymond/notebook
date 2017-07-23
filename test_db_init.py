from dbutils.panama import *
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')

roll_df = pd.read_csv("admin/roll_history.csv", \
                      dtype={'CARVER':str, 'PRICE_CONTRACT': str, \
                              'CARRY_CONTRACT':str},\
                      parse_dates=['DATETIME'])
symbols_sr = roll_df['CARVER'].copy()
symbols_sr.drop_duplicates(inplace=True)
symbols_df = pd.DataFrame(symbols_sr).sort_values('CARVER')


for symbol in symbols_df.itertuples():

    #if symbol.CARVER in ['LEANHOG']:
    #if symbol.CARVER in ['AEX','AUD','BOBL','BTP']:
    #if symbol.CARVER in ['BUND','CAC','COPPER','CORN']:
    #if symbol.CARVER in ['CRUDE_W','EDOLLAR','EUR','EUROSTX']:
    #if symbol.CARVER in ['GAS_US','GBP','GOLD','JPY']:
    #if symbol.CARVER in ['KOSPI','KR10','KR3','LEANHOG']:
    #if symbol.CARVER in ['LIVECOW','MXP','NASDAQ','NZD']:
    #if symbol.CARVER in ['OAT','PALLAD','PLAT','SMI']:
    #if symbol.CARVER in ['SOYBEAN','SP500','US10','US2']:
    #if symbol.CARVER in ['US20','US5','V2X','VIX','WHEAT']:
    if symbol.CARVER in ['EDOLLAR']:

        print("------------------")
        print(symbol.CARVER)
        price_table = symbol.CARVER.lower() + "_price"
        carry_table = symbol.CARVER.lower() + "_carrydata"
        temp_df = roll_df[roll_df['CARVER'] == symbol.CARVER].copy()
        # Go and download
        #temp_df = temp_df[temp_df['PRICE_CONTRACT'] > '201403']

        #temp_df = temp_df[temp_df['PRICE_CONTRACT'] < '201506']

        #splicedPrices = init_tables(engine=engine, market=symbol.CARVER, rolls=temp_df)  # initialization.
        #splicedPrices = init_tables(engine=engine, market=symbol.CARVER)   # update current maturities
        splicedPrices  = update_series_tables(engine=engine, market=symbol.CARVER)
        #splicedPrices = update_series_tables(engine=engine, market=symbol.CARVER, rolls=temp_df)
        price_df = splicedPrices[1]
        carry_df = splicedPrices[2]
        if len(price_df) > 0:
            print(price_df.tail(5))
            print(carry_df.tail(5))
            if splicedPrices[0]:
                price_df.reset_index(inplace=True)
                carry_df.reset_index(inplace=True)
                #price_df.to_sql(name=price_table, con=engine, if_exists='replace', index=False)
                #carry_df.to_sql(name=carry_table, con=engine, if_exists='replace', index=False)





