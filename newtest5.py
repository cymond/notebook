from dbutils.panama import *
import pandas as pd
from sqlalchemy import create_engine

roll_df = pd.read_csv("admin/roll_history.csv", dtype={'CARVER':str, 'PRICE_CONTRACT': str} )
#print(roll_df)
symbols_sr = roll_df['CARVER'].copy()
symbols_sr.drop_duplicates(inplace=True)
symbols_df = pd.DataFrame(symbols_sr).sort_values('CARVER')
#print(symbols_df)

engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')

for symbol in symbols_df.itertuples():

    if symbol.CARVER == 'EDOLLAR':
        #price_file = "data/" + symbol.CARVER + "_price.csv"
        #print(price_file)
        price_table = symbol.CARVER.lower() + "_price"
        print(price_table)
        #carry_file = "data/" + symbol.CARVER + "_carrydata.csv"
        #print(carry_file)
        carry_table = symbol.CARVER.lower() + "_carrydata"
        print(carry_table)
        #edollar_rolls_df = roll_df[roll_df['CARVER'] == 'EDOLLAR'].copy()
        temp_df = roll_df[roll_df['CARVER'] == symbol.CARVER].copy()
        print(temp_df.head(2))

        splicedPrice = init_tables(symbol.CARVER, temp_df[0:2], engine)

        '''
        if splicedPrice is None:
            print("No price dataframe")
            break
        splicedPrice.index.name = ['DATETIME']
        splicedPrice.reset_index(inplace=True)
        print(splicedPrice)
        splicedPrice.to_sql(name=price_table, con=engine, if_exists='replace', index=False)
        #splicedPrice = init_price_tbl(symbol.CARVER, temp_df, engine)
        #splicedPrice.to_csv(price_file)
        spliced_carry_df = init_carry_tbl(symbol.CARVER, temp_df[0:2], engine)
        if spliced_carry_df is None:
            print("No carry dataframe")
            break
        spliced_carry_df.index.name = ['DATETIME']
        spliced_carry_df.reset_index(inplace=True)
        print(spliced_carry_df)
        spliced_carry_df.to_sql(name=carry_table, con=engine, if_exists='replace', index=False)
        #spliced_carry_df.to_csv(carry_file)
        '''























































'''
edollar_rolls_df = roll_df[roll_df['CARVER']=='EDOLLAR'].copy()

splicedPrice = gen_panama_stream(price_file, edollar_rolls_df)
splicedPrice.to_csv(price_file)

spliced_carry_df = gen_raw_streams(carry_file, edollar_rolls_df)
spliced_carry_df.to_csv(carry_file)

print()
print("*****************************")
print("Size: ", spliced_carry_df.size)

create_price_tbl(table_name, rolls)

'''

