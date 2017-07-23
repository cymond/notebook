'''
Cycle through roll_history.csv  <Symbol,Date,Carry Contract,Price Contract>
and download from quandl, all the contracts in 'roll_history.csv'
'''

import pandas as pd
import quandl
from accessrights import q_access_key

roll_hist_filename = "admin/roll_history_late.csv"
market_data_file = "admin/marketdata.csv"


def get_code_from_month(m):
    return {
        '01': 'F',
        '02': 'G',
        '03': 'H',
        '04': 'J',
        '05': 'K',
        '06': 'M',
        '07': 'N',
        '08': 'Q',
        '09': 'U',
        '10': 'V',
        '11': 'X',
        '12': 'Z'
    }[m]


def get_q_desc(c_sym):
    market_data_df = pd.read_csv(market_data_file, dtype={'CARVER': str, 'QUANDL': str, 'Q_EXCHANGE': str})
    market_data_df.drop_duplicates(inplace=True)
    market_data_df.drop_duplicates(subset=['CARVER'], inplace=True)
    market_data_df.dropna(subset=['QUANDL'], inplace=True)
    market_data_df.set_index(['CARVER'], inplace=True)
    q_desc_ser = market_data_df.loc[c_sym][['QUANDL', 'Q_EXCHANGE']]  # return Series object
    print(q_desc_ser)
    return q_desc_ser


def dl_from_quandl(series, contract):
    carver_sym = series.CARVER
    quandl_sym = series.QUANDL
    quandl_exchange = series.Q_EXCHANGE
    month = str(contract)[4:6]
    year = str(contract)[:4]
    code = get_code_from_month(month)
    api_call_head = '{}/{}{}{}'.format(quandl_exchange, quandl_sym, code, year)
    auth_token = q_access_key()
    try:
        result = quandl.get(api_call_head, returns="pandas", authtoken=auth_token)
        file_name = "admin/downloads/quandl_history/" + carver_sym + contract + ".csv"
        # rename to Dates to DATETIME
        # and to Settle
        result.rename(columns={'Trade Date': 'Date', \
                               'Prev. Day Open Interest': 'Open Interest', \
                               'Total Volume': 'Volume', \
                               'Current Price': 'Settle'}, inplace=True)
        result.to_csv(file_name)

        # print(result.tail(2))
    except:
        # update error_df
        # {'carver_symbol':, 'contract':, 'quandl_symbol':}
        row = {'carver_symbol': carver_sym, 'contract': contract, 'quandl_symbol': quandl_sym}
        error_df.loc[len(error_df)] = row



        # print(result)


roll_df1 = pd.read_csv(roll_hist_filename, usecols=[0, 2],
                       dtype={'CARVER': str, 'CARRY_CONTRACT': str, 'PRICE_CONTRACT': str})
roll_df2 = pd.read_csv(roll_hist_filename, usecols=[0, 3],
                       dtype={'CARVER': str, 'CARRY_CONTRACT': str, 'PRICE_CONTRACT': str})
# Create unique list for all the maturities that need to be downloaded for each instrument
roll_df1.columns = ['CARVER', 'CONTRACT']
roll_df2.columns = ['CARVER', 'CONTRACT']

print(roll_df1)
print(roll_df2)

contracts_df = roll_df1.append(roll_df2)
contracts_df.sort_values(by=['CARVER', 'CONTRACT'], inplace=True)
contracts_df.drop_duplicates(['CARVER', 'CONTRACT'], inplace=True)
print(contracts_df)
print("-----------------------------------")
contracts_df.set_index(['CARVER'], inplace=True)
print(contracts_df.loc['KR3'])

error_df = pd.DataFrame(columns=['carver_symbol', 'contract', 'quandl_symbol'])
for row in contracts_df.itertuples():
    #    print(row.Index, row.CONTRACT)
    q_desc_ser = get_q_desc(row.Index)
    q_desc_ser.loc['CARVER'] = row.Index
    dl_from_quandl(q_desc_ser, row.CONTRACT)

# Print the error records
print("Error_df............................")
print(error_df)
file_name = "admin/downloads/quandl_history/error_df.csv"
error_df.to_csv(file_name)







