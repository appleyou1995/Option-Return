import pandas      as pd
import sys
import os

from pathlib import Path
from pandas.tseries.offsets import DateOffset


GoogleDrive = Path('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return')


# %%  Option Data from SAS (Option Return - 20221006.egp)

folder_SAS = Path(GoogleDrive/'Data/SAS - Output')
option_data_all = pd.read_csv(folder_SAS/'Y_SHROUT_Stock.csv')

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


# %%  SKEW Data from 瑄凌 >>> op & vol [ 20230524 ]

folder_SSSherry = Path(GoogleDrive/'Data/張瑄凌')

CW2010_SKEW_op  = pd.read_csv(folder_SSSherry/'CW2010_SKEW_op.csv')
CW2010_SKEW_vol = pd.read_csv(folder_SSSherry/'CW2010_SKEW_vol.csv')

CW2010_SKEW_op.rename(columns = {'CW2010_CPIV':'CW2010_SKEW_op'}, inplace = True)
CW2010_SKEW_vol.rename(columns = {'CW2010_CPIV':'CW2010_SKEW_vol'}, inplace = True)

# for col in CW2010_SKEW_op.columns: print(col)
# for col in CW2010_SKEW_vol.columns: print(col)


# %%  SKEW Data from 瑄凌 >>> Basic [ 20230814 ]

folder_Control = Path(GoogleDrive/'Data/控制變數')

Control_Basic = pd.read_csv(folder_Control/'CV_merge result.csv')
Control_Basic = Control_Basic.iloc[:,:22]

temp = Control_Basic['date'].str.split('/', n = 2, expand = True)
temp[1] = temp[1].astype(int)
temp[1] = temp[1].apply(lambda x : '{:0>2d}'.format(x))

Control_Basic['YYYYMM'] = temp[0] + temp[1]
Control_Basic['YYYYMM'] = Control_Basic['YYYYMM'].astype(int)

# for col in Control_Basic.columns: print(col)


# Merge Stock_Size
Control_Basic = Control_Basic.merge(CW2010_SKEW_op, 
                                    left_on = ['YYYYMM', 'permno'], 
                                    right_on = ['YYYYMM', 'PERMNO'])


Control_Basic = Control_Basic[['optionid', 'DATE', 'YYYYMM', 'PERMNO', 'cusip', 'Stock_Size', 
                               'BM', 'logME', 'ROA', 'CF', 'cash', 'tef', 'profitable', 'logPrice', 'Zscore']]


# %%  Combine Above Dataframes [ 20230814 ]

# for col in Control_Basic.columns: print(col)
# for col in option_data_Original.columns: print(col)


option_Control_Basic = option_data_Original.merge(Control_Basic, 
                                                  left_on = ['YYYYMM_t', 'PERMNO'], 
                                                  right_on = ['YYYYMM', 'PERMNO'])

option_Control_Basic['count'] = option_Control_Basic.groupby(['This_Month_Option'])['PERMNO'].transform('count')


option_data_Control_Basic = option_Control_Basic
option_data_Control_Basic = option_data_Control_Basic.set_index('This_Month_Option')
option_data_Control_Basic.index.name = 'date'


# removing rows with NaN value in any column (around 60000 data)
option_data_Control_Basic = option_data_Control_Basic.dropna()


#%% Import Function Path

sys.path.append(GoogleDrive/'Code/99  自訂函數')


# %%  【Table】 Average returns of portfolios (2022_RFS_Option Return Predictability - Table 3)

from Avg_returns_of_portfolios import Table_1_Avg_returns_of_portfolios_Option
from Avg_returns_of_portfolios import Table_1_Avg_returns_of_portfolios_Stock


# %%  Basic [ 20230814 ]

# for col in option_data_Control_Basic.columns: print(col)

Basic_List = option_data_Control_Basic.iloc[:,12:21].columns.tolist()
split_set = [3, 5, 10]

filename = 'Data/Python - Output/202308143.xlsx'
output_path = os.path.normpath(os.path.join(GoogleDrive, filename))

writer = pd.ExcelWriter(output_path, engine='openpyxl') # 指定引擎openpyxl


for x in Basic_List:
    
    for y in range(len(split_set)):
        
        # Option
        
        df_name_Option = 'portfolio_' + str(x) + '_Option_' + str(split_set[y])
        df_sheet_name = str(x) + '_Option'
        
        globals()[df_name_Option] = Table_1_Avg_returns_of_portfolios_Option(data = option_data_Control_Basic, 
                                                                             sorted_var = x, 
                                                                             split_num = split_set[y])        
        globals()[df_name_Option].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
        
        
        # Stock
        
        df_name_Stock = 'portfolio_' + str(x) + '_Stock_' + str(split_set[y])
        df_sheet_name = str(x) + '_Stock'
        
        globals()[df_name_Stock] = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_Control_Basic, 
                                                                           sorted_var = x, 
                                                                           split_num = split_set[y])        
        globals()[df_name_Stock].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
writer.save()