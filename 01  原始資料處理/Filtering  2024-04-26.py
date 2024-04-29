import pandas               as pd

from pathlib                import Path
from pandas.tseries.offsets import DateOffset


# %%  Option Data from SAS (Option Return - 20221006.egp)


folder_SAS = Path('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/Data/SAS - Output')
option_data_all = pd.read_csv(folder_SAS/"Y_SHROUT_Stock.csv")

# for col in option_data_all.columns: print(col)

option_data_Original = option_data_all[['date', 'YYYYMM_t', 'cusip', 'PERMNO', 'SHROUT', 'RET', 'Buy & hold until month-end (%)']]

option_data_Original.rename(columns = {'Buy & hold until month-end (%)':'Option_Return'}, inplace = True)
option_data_Original.rename(columns = {'RET':'Stock_Return'}, inplace = True)
option_data_Original.rename(columns = {'SHROUT':'Option_Size'}, inplace = True)


option_data_Original['date'] = pd.to_datetime(option_data_Original['date'])
option_data_Original.insert(loc = 1, column = 'Next_Month_Option', value = option_data_Original['date'] + DateOffset(months=1))
option_data_Original = option_data_Original.sort_values(by=['date', 'cusip'])

option_data_Original = option_data_Original.set_index('date', drop = False)
option_data_Original.rename(columns = {'date':'This_Month_Option'}, inplace = True)


# groupby_date
option_data_groupby_date = pd.DataFrame(option_data_Original.groupby('date'))


# %%  SKEW Data from 瑄凌 >>> 每個 PERMNO 每月的 SKEW 平均起來當成月底資料 [ 20230426 ]


folder_SSSherry = Path('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/Data/張瑄凌')

ATMPC_SKEW  = pd.read_csv(folder_SSSherry/"ATMPC_SKEW.csv")
XZZ2010_SKEW = pd.read_csv(folder_SSSherry/"XZZ2010_SKEW.csv")

for col in ATMPC_SKEW.columns: print(col)
for col in XZZ2010_SKEW.columns: print(col)

ATMPC_SKEW.rename(columns = {'MEAN_of_firm_size':'Stock_Size'}, inplace = True)
XZZ2010_SKEW.rename(columns = {'MEAN_of_firm_size':'Stock_Size'}, inplace = True)

ATMPC_SKEW.rename(columns = {'MEAN_of_ATMPC_skew':'ATMPC_skew'}, inplace = True)
XZZ2010_SKEW.rename(columns = {'MEAN_of_skew_otmp_atmc':'XZZ2010_skew'}, inplace = True)


# %%  SKEW Data from 瑄凌 >>> op & vol [ 20230524 ]

folder_SSSherry = Path('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/Data/張瑄凌')

CW2010_SKEW_op  = pd.read_csv(folder_SSSherry/"CW2010_SKEW_op.csv")
CW2010_SKEW_vol = pd.read_csv(folder_SSSherry/"CW2010_SKEW_vol.csv")

for col in CW2010_SKEW_op.columns: print(col)
for col in CW2010_SKEW_vol.columns: print(col)

CW2010_SKEW_op.rename(columns = {'CW2010_CPIV':'CW2010_SKEW_op'}, inplace = True)
CW2010_SKEW_vol.rename(columns = {'CW2010_CPIV':'CW2010_SKEW_vol'}, inplace = True)


# %%  Combine Above Dataframes [ 20230426 ]

for col in ATMPC_SKEW.columns: print(col)
for col in XZZ2010_SKEW.columns: print(col)

for col in option_data_Original.columns: print(col)


#%%  Output Path

folder_output = Path('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/Data/Python - Output')


#%%   ATMPC_SKEW

option_ATMPC_SKEW_20230426 = option_data_Original.merge(ATMPC_SKEW, 
                                                        left_on = ['YYYYMM_t', 'PERMNO'], 
                                                        right_on = ['YYYYMM', 'PERMNO'])

option_ATMPC_SKEW_count_20230426 = pd.DataFrame(option_ATMPC_SKEW_20230426.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_ATMPC_SKEW_count_20230426.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_ATMPC_20230426 = pd.merge(option_ATMPC_SKEW_20230426, option_ATMPC_SKEW_count_20230426, left_on = ['This_Month_Option'], right_index = True)

option_data_ATMPC_20230426 = option_data_ATMPC_20230426.set_index('This_Month_Option')
option_data_ATMPC_20230426.index.name = 'date'
option_data_ATMPC_20230426.to_csv(folder_output/"option_data_ATMPC_20230426.csv", index=True)


#%%   XZZ2010_SKEW

option_XZZ2010_SKEW_20230426 = option_data_Original.merge(XZZ2010_SKEW, 
                                                         left_on = ['YYYYMM_t', 'PERMNO'], 
                                                         right_on = ['YYYYMM', 'PERMNO'])

option_XZZ2010_SKEW_count_20230426 = pd.DataFrame(option_XZZ2010_SKEW_20230426.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_XZZ2010_SKEW_count_20230426.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_XZZ2010_20230426 = pd.merge(option_XZZ2010_SKEW_20230426, option_XZZ2010_SKEW_count_20230426, left_on = ['This_Month_Option'], right_index = True)

option_data_XZZ2010_20230426 = option_data_XZZ2010_20230426.set_index('This_Month_Option')
option_data_XZZ2010_20230426.index.name = 'date'
option_data_XZZ2010_20230426.to_csv(folder_output/"option_data_XZZ2010_20230426.csv", index=True)



# %%  Combine Above Dataframes [ 20230524 ]

for col in CW2010_SKEW_op.columns: print(col)
for col in CW2010_SKEW_vol.columns: print(col)

for col in option_data_Original.columns: print(col)


#%%   CW2010_SKEW_op

option_CW2010_SKEW_op_20230524 = option_data_Original.merge(CW2010_SKEW_op, 
                                                            left_on = ['YYYYMM_t', 'PERMNO'], 
                                                            right_on = ['YYYYMM', 'PERMNO'])

option_CW2010_SKEW_op_count_20230524 = pd.DataFrame(option_CW2010_SKEW_op_20230524.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_CW2010_SKEW_op_count_20230524.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_CW2010_SKEW_op_20230524 = pd.merge(option_CW2010_SKEW_op_20230524, option_CW2010_SKEW_op_count_20230524, left_on = ['This_Month_Option'], right_index = True)

option_data_CW2010_SKEW_op_20230524 = option_data_CW2010_SKEW_op_20230524.set_index('This_Month_Option')
option_data_CW2010_SKEW_op_20230524.index.name = 'date'
option_data_CW2010_SKEW_op_20230524.to_csv(folder_output/"option_data_CW2010_SKEW_op_20230524.csv", index=True)


#%%   CW2010_SKEW_vol

option_CW2010_SKEW_vol_20230524 = option_data_Original.merge(CW2010_SKEW_vol, 
                                                             left_on = ['YYYYMM_t', 'PERMNO'], 
                                                             right_on = ['YYYYMM', 'PERMNO'])

option_CW2010_SKEW_vol_count_20230524 = pd.DataFrame(option_CW2010_SKEW_vol_20230524.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_CW2010_SKEW_vol_count_20230524.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_CW2010_SKEW_vol_20230524 = pd.merge(option_CW2010_SKEW_vol_20230524, option_CW2010_SKEW_vol_count_20230524, left_on = ['This_Month_Option'], right_index = True)

option_data_CW2010_SKEW_vol_20230524 = option_data_CW2010_SKEW_vol_20230524.set_index('This_Month_Option')
option_data_CW2010_SKEW_vol_20230524.index.name = 'date'
option_data_CW2010_SKEW_vol_20230524.to_csv(folder_output/"option_data_CW2010_SKEW_vol_20230524.csv", index=True)