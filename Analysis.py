import pandas   as pd
import numpy    as np

from pathlib import Path
from pandas.tseries.offsets import DateOffset


# %%  Option Data from SAS (Option Return - 20221006.egp)


folder_SAS = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/SAS - Output')
option_data_all = pd.read_csv(folder_SAS/"Y_SHROUT.csv")

for col in option_data_all.columns: print(col)

option_data_Original = option_data_all[['date', 'cusip', "SHROUT", 'Buy & hold until month-end (%)']]
option_data_Original.rename(columns = {'Buy & hold until month-end (%)':'Option_Return'}, inplace = True)
option_data_Original.rename(columns = {'SHROUT':'Option_Size'}, inplace = True)


option_data_Original['date'] = pd.to_datetime(option_data_Original['date'])
option_data_Original.insert(loc = 1, column = 'Next_Month_Option', value = option_data_Original['date'] + DateOffset(months=1))
option_data_Original = option_data_Original.sort_values(by=['date', 'cusip'])

option_data_Original = option_data_Original.set_index('date', drop = False)
option_data_Original.rename(columns = {'date':'This_Month_Option'}, inplace = True)


# groupby_date
option_data_groupby_date = pd.DataFrame(option_data_Original.groupby('date'))


# %%  SKEW Data from Sherry


folder_Data = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data')
SKEW_Sherry = pd.read_csv(folder_Data/"skew12_monthly.csv")

for col in SKEW_Sherry.columns: print(col)

SKEW_Sherry.rename(columns = {'size':'Stock_Size'}, inplace = True)

SKEW_Sherry['date'] = pd.to_datetime(SKEW_Sherry['date'])
SKEW_Sherry.insert(loc = 1, column = 'Next_Month_Stock', value = SKEW_Sherry['date'] + DateOffset(months=1))
SKEW_Sherry = SKEW_Sherry.sort_values(by=['date', 'cusip'])

SKEW_Sherry = SKEW_Sherry.set_index('date', drop = False)
SKEW_Sherry.rename(columns = {'date':'This_Month_Stock'}, inplace = True)


# groupby_date
SKEW_groupby_date = pd.DataFrame(SKEW_Sherry.groupby('date'))


# %%  Fama-French five-factor model

FF5_data_all = pd.read_csv(folder_Data/'F-F_monthly.csv')

FF5_data = FF5_data_all.iloc[390:702,2:7]
FF5_data.index = SKEW_groupby_date[0]


# %%  Combine Above Dataframes


option_SKEW_0 = option_data_Original.merge(SKEW_Sherry, left_on = ['This_Month_Option', 'cusip'], right_on = ['This_Month_Stock', 'cusip'])
option_SKEW_0_count = pd.DataFrame(option_SKEW_0.groupby('This_Month_Option')['cusip'].count()).sort_values(by=['cusip'])
option_SKEW_0_count.rename(columns = {'cusip':'count'}, inplace = True)

# option_SKEW_0.to_csv('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/option_SKEW_0.csv')
# option_SKEW_0_count.to_csv('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/option_SKEW_0_count.csv')


# option_SKEW_1 = option_data_Original.merge(SKEW_Sherry, left_on = ['This_Month_Option', 'cusip'], right_on = ['Next_Month_Stock', 'cusip'])
# option_SKEW_1_count = pd.DataFrame(option_SKEW_1.groupby('This_Month_Option')['cusip'].count()).sort_values(by=['cusip'])
# option_SKEW_1_count.rename(columns = {'cusip':'count'}, inplace = True)


# option_SKEW_2 = option_data_Original.merge(SKEW_Sherry, left_on = ['Next_Month_Option', 'cusip'], right_on = ['This_Month_Stock', 'cusip'])
# option_SKEW_2_count = pd.DataFrame(option_SKEW_2.groupby('This_Month_Option')['cusip'].count()).sort_values(by=['cusip'])
# option_SKEW_2_count.rename(columns = {'cusip':'count'}, inplace = True)


# option_SKEW = pd.merge(option_SKEW, FF5_data, left_on = ['This_Month_Stock'], right_index = True)



######################################################################################################################
                                                                                                                     #
option_data = pd.merge(option_SKEW_0, option_SKEW_0_count, left_on = ['This_Month_Option'], right_index = True)      #
                                                                                                                     #
######################################################################################################################


option_data = option_data[['This_Month_Option', 'cusip', "skew1", "skew2", "Stock_Size", "Option_Size", 'Option_Return', 'count']]
option_data = option_data.set_index('This_Month_Option')
option_data.index.name = 'date'


# %%  Option Data with SKEW (Option Return - 20230129.egp)

# folder = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/SAS - Output')

# # Option Data with SKEW
# Option_Skew   = pd.read_csv(folder/'Option_SKEW.csv')

# for col in Option_Skew.columns: print(col)
    
# option_data = Option_Skew[['date', 'cusip', "skew1", "skew2", "size", "SHROUT", 'Buy & hold until month-end (%)']]

# option_data.rename(columns = {'Buy & hold until month-end (%)':'Option_Return'}, inplace = True)
# option_data.rename(columns = {'size':'Stock_Size'}, inplace = True)
# option_data.rename(columns = {'SHROUT':'Option_Size'}, inplace = True)

# option_data['date'] = pd.to_datetime(option_data['date'])
# option_data = option_data.set_index('date')
# option_data_df = pd.DataFrame(option_data.groupby('date'))


# %%  from Lillian (volatility analysis.py)


# Portfolio Sorted

def portfolio(data, sorted_var, split_num):
    n = int(len(data)/split_num)
    data_sorted = data.sort_values(sorted_var)
    
    if len(data)%split_num == 0:
        output = [data_sorted[i:i + n] for i in range(0, len(data), n)]
    else:
        remain = len(data) - 5*n
        output = [data_sorted[i:i + n] for i in range(0, len(data)-4*n, n)]
        output.append(data_sorted[2*n:3*n+remain])
        output.append(data_sorted[3*n+remain:4*n+remain])
        output.append(data_sorted[4*n+remain:])
    return output


# %%  【Table】 Average returns of portfolios  (2022_RFS_Option Return Predictability - Table 3)

split_num  = 5

option_data = option_data[option_data['count'] >= split_num]
option_data_df = pd.DataFrame(option_data.groupby('date'))


######  SKEW 1  &  Eqaul-Weighted  ######

sorted_var = 'skew1'
portfolio_SKEW_1_EW = pd.DataFrame()

portfolio_fin = pd.DataFrame()
for i in range(split_num):
    portfolio_df = pd.DataFrame()
    for j in range(len(option_data_df)):
        data         = option_data_df.iloc[j,1].copy()
        output       = portfolio(data, sorted_var, split_num)
        portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T])
    portfolio_df.index = option_data_df[0]
    portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(portfolio_df.mean()).T])

portfolio_SKEW_1_EW['SKEW_1_EW'] = portfolio_fin['Option_Return']
portfolio_SKEW_1_EW.index = list(range(1, 1 + split_num))



######  SKEW 2  &  Eqaul-Weighted  ######

sorted_var = 'skew2'
portfolio_SKEW_2_EW = pd.DataFrame()

portfolio_fin = pd.DataFrame()
for i in range(split_num):
    portfolio_df = pd.DataFrame()
    for j in range(len(option_data_df)):
        data         = option_data_df.iloc[j,1].copy()
        output       = portfolio(data, sorted_var, split_num)
        portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T])
    portfolio_df.index = option_data_df[0]
    portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(portfolio_df.mean()).T])

portfolio_SKEW_2_EW['SKEW_2_EW'] = portfolio_fin['Option_Return']
portfolio_SKEW_2_EW.index = list(range(1, 1 + split_num))



######  SKEW 1  ######

sorted_var = 'skew1'
portfolio_SKEW_1 = pd.DataFrame()

EW_VW = pd.DataFrame()
portfolio_fin = pd.DataFrame()
for i in range(split_num):
    portfolio_df = pd.DataFrame()
    Value_Weighted = pd.DataFrame(columns=['VW'], index=range(len(option_data_df)))
    for j in range(len(option_data_df)):
        data         = option_data_df.iloc[j,1].copy()
        output       = portfolio(data, sorted_var, split_num)
        portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T])
        Value_Weighted.iloc[j] = np.average(output[i]['Option_Return'], weights=output[i]['Option_Size'])
    portfolio_df.index = option_data_df[0]
    Value_Weighted.index = option_data_df[0]
    EW_VW = pd.concat([portfolio_df, Value_Weighted], axis=1)
    portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(EW_VW.mean()).T])

portfolio_SKEW_1['SKEW_1_EW'] = portfolio_fin['Option_Return']
portfolio_SKEW_1['SKEW_1_VW'] = portfolio_fin['VW']
portfolio_SKEW_1.index = list(range(1, 1 + split_num))



######  SKEW 2  ######

sorted_var = 'skew2'
portfolio_SKEW_2 = pd.DataFrame()

EW_VW = pd.DataFrame()
portfolio_fin = pd.DataFrame()
for i in range(split_num):
    portfolio_df = pd.DataFrame()
    Value_Weighted = pd.DataFrame(columns=['VW'], index=range(len(option_data_df)))
    for j in range(len(option_data_df)):
        data         = option_data_df.iloc[j,1].copy()
        output       = portfolio(data, sorted_var, split_num)
        portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T])
        Value_Weighted.iloc[j] = np.average(output[i]['Option_Return'], weights=output[i]['Option_Size'])
    portfolio_df.index = option_data_df[0]
    Value_Weighted.index = option_data_df[0]
    EW_VW = pd.concat([portfolio_df, Value_Weighted], axis=1)
    portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(EW_VW.mean()).T])

portfolio_SKEW_2['SKEW_2_EW'] = portfolio_fin['Option_Return']
portfolio_SKEW_2['SKEW_2_VW'] = portfolio_fin['VW']
portfolio_SKEW_2.index = list(range(1, 1 + split_num))



######  Merge  ######


Table_1 = pd.concat([portfolio_SKEW_1, portfolio_SKEW_2], axis=1).T




# %%  【Table】 Portfolios Sorted on Volatility Features  (Lillian - Table 4)







# %%  【Table】 Fama-MacBeth Regressions  (Lillian - Table 5)






