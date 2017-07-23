from dbutils.panama import *
import pandas as pd

panama_file = 'data/EDOLLAR_price.csv'
df = stitch_next_maturity(panama_file,'quandl_history/EDOLLAR198503.csv', '1983-12-12')
df.to_csv(panama_file)
print(df)