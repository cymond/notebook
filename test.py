import pandas as pd
import numpy as np
from dbutils.panama import *

roll_df = pd.read_csv("admin/roll_history.csv", dtype={'CARVER':str, 'PRICE_CONTRACT': str} )
edollar_rolls_df = roll_df[roll_df['CARVER']=='EDOLLAR'].copy()

pan_file = 'quandl_history/EDOLLAR' + edollar_rolls_df.iloc[0]['PRICE_CONTRACT'] + '.csv'
pan_df = pd.read_csv(pan_file, usecols=['Date', 'Settle'], \
                       index_col=['Date'],parse_dates=True, \
                        dtype = {'Settle': float})

splice_file = 'quandl_history/EDOLLAR' + edollar_rolls_df.iloc[1]['PRICE_CONTRACT'] + '.csv'
splice_df = pd.read_csv(splice_file, usecols=['Date', 'Settle'], \
                        index_col=['Date'],parse_dates=True, \
                        dtype = {'Settle': float})

splice_date = edollar_rolls_df.iloc[1]['DATETIME']

pan_df.rename(columns={'Settle':'PRICE'},inplace=True)
splice_df.rename(columns={'Settle': 'PRICE'},inplace=True)
#print("Type:", type(pan_df.iloc[0][1]))

# Should also check that splice is possible first!
out_df = pan_splice(base_df=pan_df, new_df=splice_df, date=splice_date)
out_df.to_csv("tested.csv")

print(out_df)
