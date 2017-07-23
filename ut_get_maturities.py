'''
* PK
* 20170317
For each market, generate the list of maturities and associated roll dates from carry data .csv files
i.e. from <SYMBOL>_carrydata.csv
The roll dates are the dates at which the new Carry and Price contracts are substituted
for the current contracts
A file, roll_history.csv is generated with  <Symbol,Date,Carry Contract,Price Contract>
'''

import pandas as pd

'''
dir_filename = "admin/directories.csv"
dir_df = pd.read_csv(dir_filename, index_col=['DIRECTION'], dtype={'PATH': str})
destination_path = dir_df.loc['DESTINATION'][0]  # /home/pete/Repos/pysystemtrade/private/SystemR/data/
'''

#Get a list of all the markets
instruments = ['KR3', 'V2X', 'EDOLLAR', 'MXP', 'CORN', 'EUROSTX', 'GAS_US', 'PLAT', 'US2',
              'LEANHOG', 'GBP', 'VIX', 'CAC', 'COPPER', 'CRUDE_W', 'BOBL', 'WHEAT', 'JPY',
              'NASDAQ', 'GOLD', 'US5', 'SOYBEAN', 'AUD', 'SP500', 'PALLAD', 'KR10',
              'LIVECOW', 'NZD', 'KOSPI', 'US10', 'SMI', 'EUR', 'OAT', 'AEX', 'BUND',
              'BTP', 'US20']

appended_df = pd.DataFrame()
# From each CARRY data file get the roll dates and the associated contracts...
for instrument in instruments:
    legacy_carry_file = "data/" + instrument + '_carrydata.csv'
    legacy_carry_df = pd.read_csv(legacy_carry_file, dtype={'CARRY_CONTRACT': str, 'PRICE_CONTRACT': str})

    # Remove duplicates
    legacy_carry_df.drop_duplicates(subset=['PRICE_CONTRACT'], keep='first',inplace=True)
    # Remove NaNs
    legacy_carry_df.dropna(subset=['PRICE_CONTRACT'], inplace=True)
    # Add instrument to use as key in final output file
    legacy_carry_df = legacy_carry_df[legacy_carry_df['DATETIME'] > '2016-09-01']
    legacy_carry_df["CARVER"] = instrument

    df = legacy_carry_df.loc[:,["CARVER","DATETIME","CARRY_CONTRACT","PRICE_CONTRACT"]].set_index(['CARVER','DATETIME'])
    #df = df[df['DATETIME'] > '2016-09-01']
    appended_df = appended_df.append(df)


# Add the rows for each market to a utility_file, hist_contracts, holding all contracts and their change dates
appended_file = 'admin/roll_history_late.csv'
appended_df.to_csv(appended_file)

# Show what file looks like
print(appended_df)


