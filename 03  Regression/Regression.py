import pandas          as pd
import sys

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


# %%  ################################################################################################################
####################################################  Regression  ####################################################

# Meeting: 2023-10-04

for col in ATMPC_SKEW.columns: print(col)
for col in XZZ2010_SKEW.columns: print(col)

ATMPC_SKEW['YYYY'] = ATMPC_SKEW['YYYYMM'].apply(str).str[:4].astype(int)
ATMPC_SKEW['MM']   = ATMPC_SKEW['YYYYMM'].apply(str).str[4:].astype(int)

XZZ2010_SKEW['YYYY'] = XZZ2010_SKEW['YYYYMM'].apply(str).str[:4].astype(int)
XZZ2010_SKEW['MM']   = XZZ2010_SKEW['YYYYMM'].apply(str).str[4:].astype(int)


#%% Import Function Path

sys.path.append('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/Code/99  自訂函數')


#%%  Quantile_December
    
from Quantile_December import Quantile_December

ATMPC_SKEW_label   = Quantile_December(dataset = ATMPC_SKEW,   sorted_var = 'Stock_Size', split_num = 10)
XZZ2010_SKEW_label = Quantile_December(dataset = XZZ2010_SKEW, sorted_var = 'Stock_Size', split_num = 10)


# %%  ATMPC_SKEW Combine with Option data

option_ATMPC_SKEW_reg = option_data_Original.merge( ATMPC_SKEW_label, left_on = ['YYYYMM_t', 'PERMNO'], 
                                                                      right_on = ['YYYYMM', 'PERMNO'])

option_ATMPC_SKEW_reg = option_ATMPC_SKEW_reg.set_index('This_Month_Option')
option_ATMPC_SKEW_reg.index.name = 'date'

for col in option_ATMPC_SKEW_reg.columns: print(col)


# %%  XZZ2010_SKEW Combine with Option data

option_XZZ2010_SKEW_reg = option_data_Original.merge( XZZ2010_SKEW_label, left_on = ['YYYYMM_t', 'PERMNO'], 
                                                                          right_on = ['YYYYMM', 'PERMNO'])

option_XZZ2010_SKEW_reg = option_XZZ2010_SKEW_reg.set_index('This_Month_Option')
option_XZZ2010_SKEW_reg.index.name = 'date'

for col in option_XZZ2010_SKEW_reg.columns: print(col)


# %%  Import Regression function
    
from regression_table import regression_table


# %%  Run Regression

Reg_ATMPC_SKEW_All = regression_table(dataset = option_ATMPC_SKEW_reg, 
                                      exog = 'ATMPC_skew', 
                                      split_num = 10)

Reg_ATMPC_SKEW_Pos = regression_table(dataset = option_ATMPC_SKEW_reg[option_ATMPC_SKEW_reg.ATMPC_skew > 0], 
                                      exog = 'ATMPC_skew', 
                                      split_num = 10)

Reg_ATMPC_SKEW_Neg = regression_table(dataset = option_ATMPC_SKEW_reg[option_ATMPC_SKEW_reg.ATMPC_skew < 0], 
                                      exog = 'ATMPC_skew', 
                                      split_num = 10)


Reg_XZZ2010_SKEW_All = regression_table(dataset = option_XZZ2010_SKEW_reg, 
                                        exog = 'XZZ2010_skew', 
                                        split_num = 10)

Reg_XZZ2010_SKEW_Pos = regression_table(dataset = option_XZZ2010_SKEW_reg[option_XZZ2010_SKEW_reg.XZZ2010_skew > 0], 
                                        exog = 'XZZ2010_skew', 
                                        split_num = 10)

Reg_XZZ2010_SKEW_Neg = regression_table(dataset = option_XZZ2010_SKEW_reg[option_XZZ2010_SKEW_reg.XZZ2010_skew < 0], 
                                        exog = 'XZZ2010_skew', 
                                        split_num = 10)


#%%  Ouput Regression

output_path = 'D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/Data/Python - Output/20231009.xlsx'
writer = pd.ExcelWriter(output_path, engine='openpyxl') # 指定引擎openpyxl

Reg_ATMPC_SKEW_All.to_excel(writer, sheet_name='Reg_ATMPC_SKEW_All')
Reg_ATMPC_SKEW_Pos.to_excel(writer, sheet_name='Reg_ATMPC_SKEW_Pos')
Reg_ATMPC_SKEW_Neg.to_excel(writer, sheet_name='Reg_ATMPC_SKEW_Neg')

Reg_XZZ2010_SKEW_All.to_excel(writer, sheet_name='Reg_XZZ2010_SKEW_All')
Reg_XZZ2010_SKEW_Pos.to_excel(writer, sheet_name='Reg_XZZ2010_SKEW_Pos')
Reg_XZZ2010_SKEW_Neg.to_excel(writer, sheet_name='Reg_XZZ2010_SKEW_Neg')


writer.save() # 存檔生成excel檔案

