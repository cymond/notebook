import pandas as pd
import datetime

destination_path = 'data_control/'
roll_df = pd.read_csv("admin/roll_history.csv", dtype={'CARVER': str, 'PRICE_CONTRACT': str})
list = []
count =0
notequal = 0
for row in roll_df.itertuples():

    count = count + 1
    symbol = row.CARVER
    date = row.DATETIME  # Check if this is in the downloaded history data.
    mat = row.PRICE_CONTRACT
    #if mat == '199007' and symbol == 'GAS_US':
    current_carry_file = destination_path + symbol + "_carrydata.csv"

    current_price_df = pd.read_csv(current_carry_file, index_col=["DATETIME"],
                                   dtype={"PRICE": str, "PRICE_CONTRACT": str}, parse_dates=True)

    filtered_current_df = current_price_df[current_price_df['PRICE_CONTRACT'] == mat].resample('B').last()

    flsize = filtered_current_df.count(axis=1).count()
    #print(mat, date, flsize)
    first = filtered_current_df[:1].index[0]

    #datetime_last = datetime.datetime.strptime(filtered_current_df[-1:].index[0], "%Y-%m-%d")
    datetime_last = filtered_current_df[-1:].index[0]
    datetime_next = datetime_last + datetime.timedelta(days=0)
    str_next_date = str(datetime_next)[:10]
    download_file = "quandl_history/" + symbol + mat + ".csv"
    download_df = pd.read_csv(download_file, index_col=['Date'],parse_dates=True).resample('B').last()
    dlsize = download_df[first:str_next_date].count(axis=1).count()

    if flsize != dlsize:
        notequal = notequal + 1
        print(symbol, mat,  "flsize: ", flsize, "dlsize: ", dlsize )


print("Count: ", count)
print("Not Equal: ", notequal)