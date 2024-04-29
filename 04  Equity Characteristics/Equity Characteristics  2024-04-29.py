import pandas          as pd
import sys

from pathlib                import Path
from pandas.tseries.offsets import DateOffset


#%%  Control Variables

folder_CV = Path('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/Data/控制變數')
CV = pd.read_csv(folder_CV/"CV_merge result.csv")

CV['date'] = pd.to_datetime(CV['date'])

for col in CV.columns: print(col)


# %%  Option Data from SAS (Option Return - 20221006.egp)


folder_SAS = Path('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/Data/SAS - Output')
option_data_all = pd.read_csv(folder_SAS/"Y_SHROUT_Stock.csv")

# for col in option_data_all.columns: print(col)

option_data_Original = option_data_all[['optionid', 'date', 'YYYYMM_t', 'cusip', 'PERMNO', 'SHROUT', 'RET', 'Buy & hold until month-end (%)']]

option_data_Original.rename(columns = {'Buy & hold until month-end (%)':'Option_Return'}, inplace = True)
option_data_Original.rename(columns = {'RET':'Stock_Return'}, inplace = True)
option_data_Original.rename(columns = {'SHROUT':'Option_Size'}, inplace = True)


option_data_Original['date'] = pd.to_datetime(option_data_Original['date'])
option_data_Original.insert(loc = 1, column = 'Next_Month_Option', value = option_data_Original['date'] + DateOffset(months=1))
option_data_Original = option_data_Original.sort_values(by=['date', 'cusip'])

option_data_Original = option_data_Original.set_index('date', drop = False)
option_data_Original.rename(columns = {'date':'This_Month_Option'}, inplace = True)

for col in option_data_Original.columns: print(col)


#%%  Merge 2 dataframe

Merge_Data = option_data_Original.merge( CV, left_on = ['This_Month_Option', 'optionid'], 
                                             right_on = ['date', 'optionid'])












