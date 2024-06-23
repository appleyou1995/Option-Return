import pandas          as pd
import sys
import os

from pathlib    import Path
from tabulate   import tabulate


GoogleDrive = Path('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return')


#%%  Input Data

folder_path = Path(GoogleDrive/'Data/Python - Output')

option_data_ATMPC_20230426           = pd.read_csv(folder_path/'option_data_ATMPC.csv')
option_data_XZZ2010_20230426         = pd.read_csv(folder_path/'option_data_XZZ2010.csv')
option_data_CW2010_SKEW_op_20230524  = pd.read_csv(folder_path/'option_data_CW2010_SKEW_op.csv')
option_data_CW2010_SKEW_vol_20230524 = pd.read_csv(folder_path/'option_data_CW2010_SKEW_vol.csv')


# %%  Import function

sys.path.append(GoogleDrive/'Code/99  自訂函數')


# %%  【Table】 Average returns of portfolios (2022_RFS_Option Return Predictability - Table 3)

from Avg_returns_of_portfolios import Table_1_Avg_returns_of_portfolios_Option
from Avg_returns_of_portfolios import Table_1_Avg_returns_of_portfolios_Stock


#%%  portfolio_ATMPC_SKEW


split_set = [3, 5, 10]

filename = 'Data/Python - Output/20230426_ATMPC.xlsx'
output_path = os.path.normpath(os.path.join(GoogleDrive, filename))

writer = pd.ExcelWriter(output_path, engine='openpyxl') # 指定引擎openpyxl


portfolio_ATMPC_SKEW_Option_3  = None
portfolio_ATMPC_SKEW_Option_5  = None
portfolio_ATMPC_SKEW_Option_10 = None
portfolio_ATMPC_SKEW_Stock_3   = None
portfolio_ATMPC_SKEW_Stock_5   = None
portfolio_ATMPC_SKEW_Stock_10  = None

    
for y in range(len(split_set)):
    
    # Option
    
    df_name_Option = 'portfolio_ATMPC_SKEW_Option_' + str(split_set[y])
    df_sheet_name  = 'ATMPC_Option'
    
    globals()[df_name_Option] = Table_1_Avg_returns_of_portfolios_Option(data = option_data_ATMPC_20230426, 
                                                                         sorted_var = 'ATMPC_skew', 
                                                                         split_num = split_set[y])        
    globals()[df_name_Option].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
    # Stock
    
    df_name_Stock = 'portfolio_ATMPC_SKEW_Stock_' + str(split_set[y])
    df_sheet_name = 'ATMPC_Stock'
    
    globals()[df_name_Stock] = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_ATMPC_20230426, 
                                                                       sorted_var = 'ATMPC_skew', 
                                                                       split_num = split_set[y])        
    globals()[df_name_Stock].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
writer.save()


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.display.width = None
# print(tabulate(portfolio_ATMPC_SKEW_Option_3, headers='keys', tablefmt='fancy_grid'))

print(tabulate(portfolio_ATMPC_SKEW_Option_3,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Option_5,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Option_10, headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Stock_3,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Stock_5,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Stock_10,  headers='keys', tablefmt='fancy_grid'))


#%%  portfolio_XZZ2010_SKEW


split_set = [3, 5, 10]

filename = 'Data/Python - Output/20230426_XZZ.xlsx'
output_path = os.path.normpath(os.path.join(GoogleDrive, filename))

writer = pd.ExcelWriter(output_path, engine='openpyxl') # 指定引擎openpyxl


portfolio_XZZ2010_SKEW_Option_3  = None
portfolio_XZZ2010_SKEW_Option_5  = None
portfolio_XZZ2010_SKEW_Option_10 = None
portfolio_XZZ2010_SKEW_Stock_3   = None
portfolio_XZZ2010_SKEW_Stock_5   = None
portfolio_XZZ2010_SKEW_Stock_10  = None

    
for y in range(len(split_set)):
    
    # Option
    
    df_name_Option = 'portfolio_XZZ2010_SKEW_Option_' + str(split_set[y])
    df_sheet_name  = 'XZZ2010_Option'
    
    globals()[df_name_Option] = Table_1_Avg_returns_of_portfolios_Option(data = option_data_XZZ2010_20230426, 
                                                                         sorted_var = 'XZZ2010_skew', 
                                                                         split_num = split_set[y])        
    globals()[df_name_Option].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
    # Stock
    
    df_name_Stock = 'portfolio_XZZ2010_SKEW_Stock_' + str(split_set[y])
    df_sheet_name = 'XZZ2010_Stock'
    
    globals()[df_name_Stock] = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_XZZ2010_20230426, 
                                                                       sorted_var = 'XZZ2010_skew', 
                                                                       split_num = split_set[y])        
    globals()[df_name_Stock].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
writer.save()


print(tabulate(portfolio_XZZ2010_SKEW_Option_3,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Option_5,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Option_10, headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Stock_3,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Stock_5,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Stock_10,  headers='keys', tablefmt='fancy_grid'))


#%%  portfolio_CW2010_SKEW_op


split_set = [3, 5, 10]

filename = 'Data/Python - Output/20230524_CW2010_SKEW_op.xlsx'
output_path = os.path.normpath(os.path.join(GoogleDrive, filename))

writer = pd.ExcelWriter(output_path, engine='openpyxl') # 指定引擎openpyxl


portfolio_CW2010_SKEW_op_Option_3  = None
portfolio_CW2010_SKEW_op_Option_5  = None
portfolio_CW2010_SKEW_op_Option_10 = None
portfolio_CW2010_SKEW_op_Stock_3   = None
portfolio_CW2010_SKEW_op_Stock_5   = None
portfolio_CW2010_SKEW_op_Stock_10  = None

    
for y in range(len(split_set)):
    
    # Option
    
    df_name_Option = 'portfolio_CW2010_SKEW_op_Option_' + str(split_set[y])
    df_sheet_name  = 'CW2010_SKEW_op_Option'
    
    globals()[df_name_Option] = Table_1_Avg_returns_of_portfolios_Option(data = option_data_CW2010_SKEW_op_20230524, 
                                                                         sorted_var = 'CW2010_SKEW_op', 
                                                                         split_num = split_set[y])        
    globals()[df_name_Option].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
    # Stock
    
    df_name_Stock = 'portfolio_CW2010_SKEW_op_Stock_' + str(split_set[y])
    df_sheet_name = 'CW2010_SKEW_op_Stock'
    
    globals()[df_name_Stock] = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_CW2010_SKEW_op_20230524, 
                                                                       sorted_var = 'CW2010_SKEW_op', 
                                                                       split_num = split_set[y])        
    globals()[df_name_Stock].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
writer.save()


print(tabulate(portfolio_CW2010_SKEW_op_Option_3,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Option_5,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Option_10, headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Stock_3,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Stock_5,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Stock_10,  headers='keys', tablefmt='fancy_grid'))


#%%  portfolio_CW2010_SKEW_vol


split_set = [3, 5, 10]

filename = 'Data/Python - Output/20230524_CW2010_SKEW_vol.xlsx'
output_path = os.path.normpath(os.path.join(GoogleDrive, filename))

writer = pd.ExcelWriter(output_path, engine='openpyxl') # 指定引擎openpyxl


portfolio_CW2010_SKEW_vol_Option_3  = None
portfolio_CW2010_SKEW_vol_Option_5  = None
portfolio_CW2010_SKEW_vol_Option_10 = None
portfolio_CW2010_SKEW_vol_Stock_3   = None
portfolio_CW2010_SKEW_vol_Stock_5   = None
portfolio_CW2010_SKEW_vol_Stock_10  = None

    
for y in range(len(split_set)):
    
    # Option
    
    df_name_Option = 'portfolio_CW2010_SKEW_vol_Option_' + str(split_set[y])
    df_sheet_name  = 'CW2010_SKEW_vol_Option'
    
    globals()[df_name_Option] = Table_1_Avg_returns_of_portfolios_Option(data = option_data_CW2010_SKEW_vol_20230524, 
                                                                         sorted_var = 'CW2010_SKEW_vol', 
                                                                         split_num = split_set[y])        
    globals()[df_name_Option].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
    # Stock
    
    df_name_Stock = 'portfolio_CW2010_SKEW_vol_Stock_' + str(split_set[y])
    df_sheet_name = 'CW2010_SKEW_vol_Stock'
    
    globals()[df_name_Stock] = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_CW2010_SKEW_vol_20230524, 
                                                                       sorted_var = 'CW2010_SKEW_vol', 
                                                                       split_num = split_set[y])        
    globals()[df_name_Stock].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
writer.save()


print(tabulate(portfolio_CW2010_SKEW_vol_Option_3,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Option_5,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Option_10, headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Stock_3,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Stock_5,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Stock_10,  headers='keys', tablefmt='fancy_grid'))


#%%  開一個新的 excel 並把多個 df 寫到同 excel 不同 sheet

filename = 'Data/Python - Output/20230524.xlsx'
output_path = os.path.normpath(os.path.join(GoogleDrive, filename))

writer = pd.ExcelWriter(output_path, engine='openpyxl') # 指定引擎openpyxl

portfolio_CW2010_SKEW_op_Option_3.to_excel(writer, sheet_name='CW2010_op_Option_3')
portfolio_CW2010_SKEW_op_Option_5.to_excel(writer, sheet_name='CW2010_op_Option_5')
portfolio_CW2010_SKEW_op_Option_10.to_excel(writer, sheet_name='CW2010_op_Option_10')
portfolio_CW2010_SKEW_op_Stock_3.to_excel(writer, sheet_name='CW2010_op_Stock_3')
portfolio_CW2010_SKEW_op_Stock_5.to_excel(writer, sheet_name='CW2010_op_Stock_5')
portfolio_CW2010_SKEW_op_Stock_10.to_excel(writer, sheet_name='CW2010_op_Stock_10')

portfolio_CW2010_SKEW_vol_Option_3.to_excel(writer, sheet_name='CW2010_vol_Option_3')
portfolio_CW2010_SKEW_vol_Option_5.to_excel(writer, sheet_name='CW2010_vol_Option_5')
portfolio_CW2010_SKEW_vol_Option_10.to_excel(writer, sheet_name='CW2010_vol_Option_10')
portfolio_CW2010_SKEW_vol_Stock_3.to_excel(writer, sheet_name='CW2010_vol_Stock_3')
portfolio_CW2010_SKEW_vol_Stock_5.to_excel(writer, sheet_name='CW2010_vol_Stock_5')
portfolio_CW2010_SKEW_vol_Stock_10.to_excel(writer, sheet_name='CW2010_vol_Stock_10')


writer.save() # 存檔生成excel檔案