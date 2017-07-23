
from dbutils.connect import *
import pandas as pd
from os import listdir
from os.path import isfile, join
from sqlalchemy import create_engine

hist_path = "quandl_history/"
hist_files = [f for f in listdir(hist_path) if isfile(join(hist_path, f))]
hist_file_df = pd.DataFrame(hist_files, columns=['filename'])
hist_file_df.sort_values(['filename'],inplace=True)

engine = create_engine('mysql+pymysql://root:admin@0.0.0.0/pkdemo')
for row in hist_file_df.itertuples():
    if row.Index < 5:
        full_file_name = hist_path + row.filename
        print(full_file_name)
        df = pd.read_csv(full_file_name)
        #df.to_sql(name=row.filename.lower(), con=engine, if_exists='replace', index=False)




