import pandas      as pd
import numpy       as np
import scipy.stats as stats

# import statsmodels.formula.api as smf

from pathlib import Path
from pandas.tseries.offsets import DateOffset
from statistics import quantiles

from tabulate import tabulate


# %%  Option Data from SAS (Option Return - 20221006.egp)


folder_SAS = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/SAS - Output')
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


folder_SSSherry = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/張瑄凌')

ATMPC_SKEW  = pd.read_csv(folder_SSSherry/"ATMPC_SKEW.csv")
XZZ2010_SKEW = pd.read_csv(folder_SSSherry/"XZZ2010_SKEW.csv")

for col in ATMPC_SKEW.columns: print(col)
for col in XZZ2010_SKEW.columns: print(col)

ATMPC_SKEW.rename(columns = {'MEAN_of_firm_size':'Stock_Size'}, inplace = True)
XZZ2010_SKEW.rename(columns = {'MEAN_of_firm_size':'Stock_Size'}, inplace = True)

ATMPC_SKEW.rename(columns = {'MEAN_of_ATMPC_skew':'ATMPC_skew'}, inplace = True)
XZZ2010_SKEW.rename(columns = {'MEAN_of_skew_otmp_atmc':'skew_otmp_atmc'}, inplace = True)


# %%  SKEW Data from 瑄凌 >>> op & vol [ 20230524 ]


folder_SSSherry = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/張瑄凌')

CW2010_SKEW_op  = pd.read_csv(folder_SSSherry/"CW2010_SKEW_op.csv")
CW2010_SKEW_vol = pd.read_csv(folder_SSSherry/"CW2010_SKEW_vol.csv")

for col in CW2010_SKEW_op.columns: print(col)
for col in CW2010_SKEW_vol.columns: print(col)

CW2010_SKEW_op.rename(columns = {'CW2010_CPIV':'CW2010_SKEW_op'}, inplace = True)
CW2010_SKEW_vol.rename(columns = {'CW2010_CPIV':'CW2010_SKEW_vol'}, inplace = True)


# %%  SKEW Data from 瑄凌 >>> Basic [ 20230814 ]

folder_Control = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/控制變數')

Control_Basic = pd.read_csv(folder_Control/"CV_merge result.csv")
Control_Basic = Control_Basic.iloc[:,:22]

temp = Control_Basic["date"].str.split("/", n = 2, expand = True)
temp[1] = temp[1].astype(int)
temp[1] = temp[1].apply(lambda x : '{:0>2d}'.format(x))

Control_Basic['YYYYMM'] = temp[0] + temp[1]
Control_Basic['YYYYMM'] = Control_Basic['YYYYMM'].astype(int)


for col in Control_Basic.columns: print(col)


Control_Basic_20230814 = Control_Basic.merge(CW2010_SKEW_op, 
                                             left_on = ['YYYYMM', 'permno'], 
                                             right_on = ['YYYYMM', 'PERMNO'])


Control_Basic_20230814 = Control_Basic_20230814[['optionid', 
                                                 'DATE', 
                                                 'YYYYMM', 
                                                 'PERMNO', 
                                                 'cusip', 
                                                 'Stock_Size', 
                                                 'BM', 
                                                 'logME', 
                                                 'ROA', 
                                                 'CF', 
                                                 'cash', 
                                                 'tef', 
                                                 'profitable', 
                                                 'logPrice', 
                                                 'Zscore']]


# %%  Fama-French five-factor model


folder_FF5 = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data')
FF5_data_all = pd.read_csv(folder_FF5/'F-F_monthly.csv')

FF5_data = FF5_data_all.iloc[390:702,2:7]
# FF5_data.index = SKEW_groupby_date[0]



# %%  Combine Above Dataframes [ 20230426 ]

for col in ATMPC_SKEW.columns: print(col)
for col in XZZ2010_SKEW.columns: print(col)

for col in option_data_Original.columns: print(col)


#### ATMPC_SKEW

option_ATMPC_SKEW_20230426 = option_data_Original.merge(ATMPC_SKEW, 
                                                        left_on = ['YYYYMM_t', 'PERMNO'], 
                                                        right_on = ['YYYYMM', 'PERMNO'])

option_ATMPC_SKEW_count_20230426 = pd.DataFrame(option_ATMPC_SKEW_20230426.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_ATMPC_SKEW_count_20230426.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_ATMPC_20230426 = pd.merge(option_ATMPC_SKEW_20230426, option_ATMPC_SKEW_count_20230426, left_on = ['This_Month_Option'], right_index = True)

option_data_ATMPC_20230426 = option_data_ATMPC_20230426.set_index('This_Month_Option')
option_data_ATMPC_20230426.index.name = 'date'



#### XZZ2010_SKEW

option_XZZ2010_SKEW_20230426 = option_data_Original.merge(XZZ2010_SKEW, 
                                                         left_on = ['YYYYMM_t', 'PERMNO'], 
                                                         right_on = ['YYYYMM', 'PERMNO'])

option_XZZ2010_SKEW_count_20230426 = pd.DataFrame(option_XZZ2010_SKEW_20230426.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_XZZ2010_SKEW_count_20230426.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_XZZ2010_20230426 = pd.merge(option_XZZ2010_SKEW_20230426, option_XZZ2010_SKEW_count_20230426, left_on = ['This_Month_Option'], right_index = True)

option_data_XZZ2010_20230426 = option_data_XZZ2010_20230426.set_index('This_Month_Option')
option_data_XZZ2010_20230426.index.name = 'date'



# %%  Combine Above Dataframes [ 20230524 ]

for col in CW2010_SKEW_op.columns: print(col)
for col in CW2010_SKEW_vol.columns: print(col)

for col in option_data_Original.columns: print(col)


#### CW2010_SKEW_op

option_CW2010_SKEW_op_20230524 = option_data_Original.merge(CW2010_SKEW_op, 
                                                            left_on = ['YYYYMM_t', 'PERMNO'], 
                                                            right_on = ['YYYYMM', 'PERMNO'])

option_CW2010_SKEW_op_count_20230524 = pd.DataFrame(option_CW2010_SKEW_op_20230524.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_CW2010_SKEW_op_count_20230524.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_CW2010_SKEW_op_20230524 = pd.merge(option_CW2010_SKEW_op_20230524, option_CW2010_SKEW_op_count_20230524, left_on = ['This_Month_Option'], right_index = True)

option_data_CW2010_SKEW_op_20230524 = option_data_CW2010_SKEW_op_20230524.set_index('This_Month_Option')
option_data_CW2010_SKEW_op_20230524.index.name = 'date'



#### CW2010_SKEW_vol

option_CW2010_SKEW_vol_20230524 = option_data_Original.merge(CW2010_SKEW_vol, 
                                                             left_on = ['YYYYMM_t', 'PERMNO'], 
                                                             right_on = ['YYYYMM', 'PERMNO'])

option_CW2010_SKEW_vol_count_20230524 = pd.DataFrame(option_CW2010_SKEW_vol_20230524.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_CW2010_SKEW_vol_count_20230524.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_CW2010_SKEW_vol_20230524 = pd.merge(option_CW2010_SKEW_vol_20230524, option_CW2010_SKEW_vol_count_20230524, left_on = ['This_Month_Option'], right_index = True)

option_data_CW2010_SKEW_vol_20230524 = option_data_CW2010_SKEW_vol_20230524.set_index('This_Month_Option')
option_data_CW2010_SKEW_vol_20230524.index.name = 'date'



# %%  Combine Above Dataframes [ 20230814 ]

for col in Control_Basic_20230814.columns: print(col)
for col in option_data_Original.columns: print(col)


option_Control_Basic_20230814 = option_data_Original.merge(Control_Basic_20230814, 
                                                           left_on = ['YYYYMM_t', 'PERMNO'], 
                                                           right_on = ['YYYYMM', 'PERMNO'])

option_Control_Basic_count_20230814 = pd.DataFrame(option_Control_Basic_20230814.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_Control_Basic_count_20230814.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_Control_Basic_20230814 = pd.merge(option_Control_Basic_20230814, option_Control_Basic_count_20230814, left_on = ['This_Month_Option'], right_index = True)

option_data_Control_Basic_20230814 = option_data_Control_Basic_20230814.set_index('This_Month_Option')
option_data_Control_Basic_20230814.index.name = 'date'


# removing rows with NaN value in any column (around 60000 data)
option_data_Control_Basic_20230814 = option_data_Control_Basic_20230814.dropna()


# %%  Split with Quantiles


# def portfolio(data, sorted_var, split_num):
    
#     quantile_by = data[sorted_var]
#     quantile_list = quantiles(quantile_by, n = split_num)
    
#     for q in range(1, split_num):
#         locals()['quantile_'+str(q)] = quantile_list[q - 1]
        
#     for q in range(1, split_num + 1):
#         if q == 1:
#             output = [data[data[sorted_var] < locals()['quantile_'+str(q)]]]
#         elif q == split_num:
#             output.append(data[data[sorted_var] > locals()['quantile_'+str(q-1)]])
#         else:
#             output.append(data[data[sorted_var].between(locals()['quantile_'+str(q-1)], locals()['quantile_'+str(q)])])
    
#     return output
    


# %%  T-statistics


def T_statistics(data):
    
    T_statistics = stats.ttest_1samp(data, 0)[0]    
    T_statistics = '('+str("{:10.2f}".format(T_statistics))+')'
    
    return T_statistics



# %%  【Table】 Average returns of portfolios [Option] (2022_RFS_Option Return Predictability - Table 3)


def Table_1_Avg_returns_of_portfolios_Option(data, sorted_var, split_num):

    option_data_larger_than_split_num = data[data['count'] >= split_num]
    option_data_df = pd.DataFrame(option_data_larger_than_split_num.groupby('date'))
    
    split_index = list(range(1, 1 + split_num))
    split_index.append('('+str(split_num)+'-1) Spread')
    
    EW_VW             = pd.DataFrame()
    portfolio_fin     = pd.DataFrame()
    port_split_bottom = pd.DataFrame()
    port_split_top    = pd.DataFrame()
    port_t_statistics = pd.DataFrame(columns = ['t_stats_EW', 't_stats_VW_S', 't_stats_VW_O'], index = split_index)
    
    for i in range(split_num):
        portfolio_df          = pd.DataFrame()
        Value_Weighted_Stock  = pd.DataFrame(columns=['VW_S'], index = range(len(option_data_df)-1))
        Value_Weighted_Option = pd.DataFrame(columns=['VW_O'], index = range(len(option_data_df)-1))
        
        for j in range(len(option_data_df)):
            
            # Data for This Month:
            data = option_data_df.iloc[j,1].copy()
            
            if j == 0:   # First Month in Data
                quantile_by = data[sorted_var]
                quantile_list_last_month = quantiles(quantile_by, n = split_num)
                
            else:
                
                # vvvvvvvvvvvvvvvvvvvvvvv Quantile vvvvvvvvvvvvvvvvvvvvvvv #
                
                for q in range(1, split_num):
                    
                    # Create a Quantile List of Last Month (j-1) SKEW:
                    locals()['quantile_'+str(q)] = quantile_list_last_month[q - 1]
                    
                for q in range(1, split_num + 1):
                    if q == 1:
                        output = [data[data[sorted_var] < locals()['quantile_'+str(q)]]]
                    elif q == split_num:
                        output.append(data[data[sorted_var] > locals()['quantile_'+str(q-1)]])
                    else:
                        output.append(data[data[sorted_var].between(locals()['quantile_'+str(q-1)], locals()['quantile_'+str(q)])])
                    
                # Create a Quantile List for use in the next month (j+1):
                quantile_by = data[sorted_var]
                quantile_list_last_month = quantiles(quantile_by, n = split_num)
                
                # ^^^^^^^^^^^^^^^^^^^^^^^ Quantile ^^^^^^^^^^^^^^^^^^^^^^^ #
                
                #output      = portfolio(data, sorted_var, split_num)
                portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T])
                
                Value_Weighted_Stock.iloc[j-1]  = np.average(output[i]['Option_Return'], weights = output[i]['Stock_Size'])
                Value_Weighted_Option.iloc[j-1] = np.average(output[i]['Option_Return'], weights = output[i]['Option_Size'])
            
        portfolio_df.index          = option_data_df.iloc[1:,0]
        Value_Weighted_Stock.index  = option_data_df.iloc[1:,0]
        Value_Weighted_Option.index = option_data_df.iloc[1:,0]
        
        Value_Weighted_Stock  = Value_Weighted_Stock.astype(float)
        Value_Weighted_Option = Value_Weighted_Option.astype(float)
        
        EW_VW         = pd.concat([portfolio_df, Value_Weighted_Stock, Value_Weighted_Option], axis=1)
        portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(EW_VW.mean()).T])
        
        port_t_statistics.iloc[i]['t_stats_EW']   = T_statistics(EW_VW['Option_Return'])
        port_t_statistics.iloc[i]['t_stats_VW_S'] = T_statistics(EW_VW['VW_S'])
        port_t_statistics.iloc[i]['t_stats_VW_O'] = T_statistics(EW_VW['VW_O'])
        
        if i == 0:
            port_split_bottom['EW']   = EW_VW['Option_Return']
            port_split_bottom['VW_S'] = EW_VW['VW_S']
            port_split_bottom['VW_O'] = EW_VW['VW_O']        
            
        elif i == split_num - 1:
            port_split_top['EW']   = EW_VW['Option_Return']
            port_split_top['VW_S'] = EW_VW['VW_S']
            port_split_top['VW_O'] = EW_VW['VW_O']
            
    
    # Average returns of portfolios
    portfolio_fin = portfolio_fin[['Option_Return', 'VW_S', 'VW_O']]
    portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(portfolio_fin.iloc[split_num-1] - portfolio_fin.iloc[0]).T])
    portfolio_fin.index = split_index
    
    # T-statistics (Calculate the t-test on TWO RELATED samples of scores)
    t_stats_EW   = stats.ttest_rel(port_split_top['EW'],   port_split_bottom['EW'])[0]
    t_stats_VW_S = stats.ttest_rel(port_split_top['VW_S'], port_split_bottom['VW_S'])[0]
    t_stats_VW_O = stats.ttest_rel(port_split_top['VW_O'], port_split_bottom['VW_O'])[0]
    
    port_t_statistics.iloc[split_num]['t_stats_EW']   = '('+str("{:10.2f}".format(t_stats_EW))+')'
    port_t_statistics.iloc[split_num]['t_stats_VW_S'] = '('+str("{:10.2f}".format(t_stats_VW_S))+')'
    port_t_statistics.iloc[split_num]['t_stats_VW_O'] = '('+str("{:10.2f}".format(t_stats_VW_O))+')'    
    
    Table_1 = pd.DataFrame(index = split_index)
    
    Table_1[sorted_var + '_EW']                = portfolio_fin['Option_Return']
    Table_1[sorted_var + '_EW_t_stats']        = port_t_statistics['t_stats_EW']
    Table_1[sorted_var + '_VW_Stock']          = portfolio_fin['VW_S']
    Table_1[sorted_var + '_VW_Stock_t_stats']  = port_t_statistics['t_stats_VW_S']
    Table_1[sorted_var + '_VW_Option']         = portfolio_fin['VW_O']
    Table_1[sorted_var + '_VW_Option_t_stats'] = port_t_statistics['t_stats_VW_O']
    Table_1 = Table_1.T
    
    return Table_1


# %%  【Table】 Average returns of portfolios [Stock] (2022_RFS_Option Return Predictability - Table 3)


def Table_1_Avg_returns_of_portfolios_Stock(data, sorted_var, split_num):

    option_data_larger_than_split_num = data[data['count'] >= split_num]
    option_data_df = pd.DataFrame(option_data_larger_than_split_num.groupby('date'))
    
    split_index = list(range(1, 1 + split_num))
    split_index.append('('+str(split_num)+'-1) Spread')
    
    EW_VW             = pd.DataFrame()
    portfolio_fin     = pd.DataFrame()
    port_split_bottom = pd.DataFrame()
    port_split_top    = pd.DataFrame()
    port_t_statistics = pd.DataFrame(columns = ['t_stats_EW', 't_stats_VW_S', 't_stats_VW_O'], index = split_index)
    
    for i in range(split_num):
        portfolio_df          = pd.DataFrame()
        Value_Weighted_Stock  = pd.DataFrame(columns=['VW_S'], index = range(len(option_data_df)-1))
        Value_Weighted_Option = pd.DataFrame(columns=['VW_O'], index = range(len(option_data_df)-1))
        
        for j in range(len(option_data_df)):
            
            # Data for This Month:
            data = option_data_df.iloc[j,1].copy()
            
            if j == 0:   # First Month in Data
                quantile_by = data[sorted_var]
                quantile_list_last_month = quantiles(quantile_by, n = split_num)
                
            else:
                
                # vvvvvvvvvvvvvvvvvvvvvvv Quantile vvvvvvvvvvvvvvvvvvvvvvv #
                
                for q in range(1, split_num):
                    
                    # Create a Quantile List of Last Month (j-1) SKEW:
                    locals()['quantile_'+str(q)] = quantile_list_last_month[q - 1]
                    
                for q in range(1, split_num + 1):
                    if q == 1:
                        output = [data[data[sorted_var] < locals()['quantile_'+str(q)]]]
                    elif q == split_num:
                        output.append(data[data[sorted_var] > locals()['quantile_'+str(q-1)]])
                    else:
                        output.append(data[data[sorted_var].between(locals()['quantile_'+str(q-1)], locals()['quantile_'+str(q)])])
                    
                # Create a Quantile List for use in the next month (j+1):
                quantile_by = data[sorted_var]
                quantile_list_last_month = quantiles(quantile_by, n = split_num)
                
                # ^^^^^^^^^^^^^^^^^^^^^^^ Quantile ^^^^^^^^^^^^^^^^^^^^^^^ #
                
                #output      = portfolio(data, sorted_var, split_num)
                portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T])
                
                Value_Weighted_Stock.iloc[j-1]  = np.average(output[i]['Stock_Return'], weights = output[i]['Stock_Size'])
                Value_Weighted_Option.iloc[j-1] = np.average(output[i]['Stock_Return'], weights = output[i]['Option_Size'])
            
        portfolio_df.index          = option_data_df.iloc[1:,0]
        Value_Weighted_Stock.index  = option_data_df.iloc[1:,0]
        Value_Weighted_Option.index = option_data_df.iloc[1:,0]
        
        Value_Weighted_Stock  = Value_Weighted_Stock.astype(float)
        Value_Weighted_Option = Value_Weighted_Option.astype(float)
        
        EW_VW         = pd.concat([portfolio_df, Value_Weighted_Stock, Value_Weighted_Option], axis=1)
        portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(EW_VW.mean()).T])
        
        port_t_statistics.iloc[i]['t_stats_EW']   = T_statistics(EW_VW['Stock_Return'])
        port_t_statistics.iloc[i]['t_stats_VW_S'] = T_statistics(EW_VW['VW_S'])
        port_t_statistics.iloc[i]['t_stats_VW_O'] = T_statistics(EW_VW['VW_O'])
        
        if i == 0:
            port_split_bottom['EW']   = EW_VW['Stock_Return']
            port_split_bottom['VW_S'] = EW_VW['VW_S']
            port_split_bottom['VW_O'] = EW_VW['VW_O']        
            
        elif i == split_num - 1:
            port_split_top['EW']   = EW_VW['Stock_Return']
            port_split_top['VW_S'] = EW_VW['VW_S']
            port_split_top['VW_O'] = EW_VW['VW_O']
            
    
    # Average returns of portfolios
    portfolio_fin = portfolio_fin[['Stock_Return', 'VW_S', 'VW_O']]
    portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(portfolio_fin.iloc[split_num-1] - portfolio_fin.iloc[0]).T])
    portfolio_fin.index = split_index
    
    # T-statistics (Calculate the t-test on TWO RELATED samples of scores)
    t_stats_EW   = stats.ttest_rel(port_split_top['EW'],   port_split_bottom['EW'])[0]
    t_stats_VW_S = stats.ttest_rel(port_split_top['VW_S'], port_split_bottom['VW_S'])[0]
    t_stats_VW_O = stats.ttest_rel(port_split_top['VW_O'], port_split_bottom['VW_O'])[0]
    
    port_t_statistics.iloc[split_num]['t_stats_EW']   = '('+str("{:10.2f}".format(t_stats_EW))+')'
    port_t_statistics.iloc[split_num]['t_stats_VW_S'] = '('+str("{:10.2f}".format(t_stats_VW_S))+')'
    port_t_statistics.iloc[split_num]['t_stats_VW_O'] = '('+str("{:10.2f}".format(t_stats_VW_O))+')'    
    
    Table_1 = pd.DataFrame(index = split_index)
    
    Table_1[sorted_var + '_EW']                = portfolio_fin['Stock_Return']
    Table_1[sorted_var + '_EW_t_stats']        = port_t_statistics['t_stats_EW']
    Table_1[sorted_var + '_VW_Stock']          = portfolio_fin['VW_S']
    Table_1[sorted_var + '_VW_Stock_t_stats']  = port_t_statistics['t_stats_VW_S']
    Table_1[sorted_var + '_VW_Option']         = portfolio_fin['VW_O']
    Table_1[sorted_var + '_VW_Option_t_stats'] = port_t_statistics['t_stats_VW_O']
    Table_1 = Table_1.T
    
    return Table_1



# %%  瑄凌

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.options.display.width = None
# print(tabulate(portfolio_ATMPC_SKEW_Option_3, headers='keys', tablefmt='fancy_grid'))

# ATMPC_SKEW [ 20230426 ]

portfolio_ATMPC_SKEW_Option_3  = Table_1_Avg_returns_of_portfolios_Option(data = option_data_ATMPC_20230426, 
                                                                          sorted_var = 'ATMPC_skew', 
                                                                          split_num = 3)

portfolio_ATMPC_SKEW_Option_5  = Table_1_Avg_returns_of_portfolios_Option(data = option_data_ATMPC_20230426, 
                                                                          sorted_var = 'ATMPC_skew', 
                                                                          split_num = 5)

portfolio_ATMPC_SKEW_Option_10 = Table_1_Avg_returns_of_portfolios_Option(data = option_data_ATMPC_20230426, 
                                                                          sorted_var = 'ATMPC_skew', 
                                                                          split_num = 10)


portfolio_ATMPC_SKEW_Stock_3  = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_ATMPC_20230426, 
                                                                        sorted_var = 'ATMPC_skew', 
                                                                        split_num = 3)

portfolio_ATMPC_SKEW_Stock_5  = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_ATMPC_20230426, 
                                                                        sorted_var = 'ATMPC_skew', 
                                                                        split_num = 5)

portfolio_ATMPC_SKEW_Stock_10 = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_ATMPC_20230426, 
                                                                        sorted_var = 'ATMPC_skew', 
                                                                        split_num = 10)

print(tabulate(portfolio_ATMPC_SKEW_Option_3,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Option_5,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Option_10, headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Stock_3,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Stock_5,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_ATMPC_SKEW_Stock_10,  headers='keys', tablefmt='fancy_grid'))


# XZZ2010_SKEW [ 20230426 ]

portfolio_XZZ2010_SKEW_Option_3  = Table_1_Avg_returns_of_portfolios_Option(data = option_data_XZZ2010_20230426, 
                                                                           sorted_var = 'skew_otmp_atmc', 
                                                                           split_num = 3)

portfolio_XZZ2010_SKEW_Option_5  = Table_1_Avg_returns_of_portfolios_Option(data = option_data_XZZ2010_20230426, 
                                                                           sorted_var = 'skew_otmp_atmc', 
                                                                           split_num = 5)

portfolio_XZZ2010_SKEW_Option_10 = Table_1_Avg_returns_of_portfolios_Option(data = option_data_XZZ2010_20230426, 
                                                                           sorted_var = 'skew_otmp_atmc', 
                                                                           split_num = 10)


portfolio_XZZ2010_SKEW_Stock_3  = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_XZZ2010_20230426, 
                                                                         sorted_var = 'skew_otmp_atmc', 
                                                                         split_num = 3)

portfolio_XZZ2010_SKEW_Stock_5  = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_XZZ2010_20230426, 
                                                                         sorted_var = 'skew_otmp_atmc', 
                                                                         split_num = 5)

portfolio_XZZ2010_SKEW_Stock_10 = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_XZZ2010_20230426, 
                                                                         sorted_var = 'skew_otmp_atmc', 
                                                                         split_num = 10)

print(tabulate(portfolio_XZZ2010_SKEW_Option_3,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Option_5,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Option_10, headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Stock_3,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Stock_5,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_XZZ2010_SKEW_Stock_10,  headers='keys', tablefmt='fancy_grid'))


# CW2010_SKEW_op [ 20230524 ]

portfolio_CW2010_SKEW_op_Option_3  = Table_1_Avg_returns_of_portfolios_Option(data = option_data_CW2010_SKEW_op_20230524, 
                                                                           sorted_var = 'CW2010_SKEW_op', 
                                                                           split_num = 3)

portfolio_CW2010_SKEW_op_Option_5  = Table_1_Avg_returns_of_portfolios_Option(data = option_data_CW2010_SKEW_op_20230524, 
                                                                           sorted_var = 'CW2010_SKEW_op', 
                                                                           split_num = 5)

portfolio_CW2010_SKEW_op_Option_10 = Table_1_Avg_returns_of_portfolios_Option(data = option_data_CW2010_SKEW_op_20230524, 
                                                                           sorted_var = 'CW2010_SKEW_op', 
                                                                           split_num = 10)


portfolio_CW2010_SKEW_op_Stock_3  = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_CW2010_SKEW_op_20230524, 
                                                                         sorted_var = 'CW2010_SKEW_op', 
                                                                         split_num = 3)

portfolio_CW2010_SKEW_op_Stock_5  = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_CW2010_SKEW_op_20230524, 
                                                                         sorted_var = 'CW2010_SKEW_op', 
                                                                         split_num = 5)

portfolio_CW2010_SKEW_op_Stock_10 = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_CW2010_SKEW_op_20230524, 
                                                                         sorted_var = 'CW2010_SKEW_op', 
                                                                         split_num = 10)

print(tabulate(portfolio_CW2010_SKEW_op_Option_3,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Option_5,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Option_10, headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Stock_3,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Stock_5,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_op_Stock_10,  headers='keys', tablefmt='fancy_grid'))


# CW2010_SKEW_vol [ 20230524 ]

portfolio_CW2010_SKEW_vol_Option_3  = Table_1_Avg_returns_of_portfolios_Option(data = option_data_CW2010_SKEW_vol_20230524, 
                                                                               sorted_var = 'CW2010_SKEW_vol', 
                                                                               split_num = 3)

portfolio_CW2010_SKEW_vol_Option_5  = Table_1_Avg_returns_of_portfolios_Option(data = option_data_CW2010_SKEW_vol_20230524, 
                                                                               sorted_var = 'CW2010_SKEW_vol', 
                                                                               split_num = 5)

portfolio_CW2010_SKEW_vol_Option_10 = Table_1_Avg_returns_of_portfolios_Option(data = option_data_CW2010_SKEW_vol_20230524, 
                                                                               sorted_var = 'CW2010_SKEW_vol', 
                                                                               split_num = 10)


portfolio_CW2010_SKEW_vol_Stock_3  = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_CW2010_SKEW_vol_20230524, 
                                                                             sorted_var = 'CW2010_SKEW_vol', 
                                                                             split_num = 3)

portfolio_CW2010_SKEW_vol_Stock_5  = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_CW2010_SKEW_vol_20230524, 
                                                                             sorted_var = 'CW2010_SKEW_vol', 
                                                                             split_num = 5)

portfolio_CW2010_SKEW_vol_Stock_10 = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_CW2010_SKEW_vol_20230524, 
                                                                             sorted_var = 'CW2010_SKEW_vol', 
                                                                             split_num = 10)

print(tabulate(portfolio_CW2010_SKEW_vol_Option_3,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Option_5,  headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Option_10, headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Stock_3,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Stock_5,   headers='keys', tablefmt='fancy_grid'))
print(tabulate(portfolio_CW2010_SKEW_vol_Stock_10,  headers='keys', tablefmt='fancy_grid'))




# %%  Basic [ 20230814 ]

for col in option_data_Control_Basic_20230814.columns: print(col)

Basic_List = option_data_Control_Basic_20230814.iloc[:,12:21].columns.tolist()
split_set = [3, 5, 10]


output_path = 'D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/Python - Output/202308142.xlsx'
writer = pd.ExcelWriter(output_path, engine='openpyxl') # 指定引擎openpyxl


for x in Basic_List:
    
    for y in range(len(split_set)):
        
        # Option
        
        df_name_Option = 'portfolio_' + str(x) + '_Option_' + str(split_set[y])
        df_sheet_name = str(x) + '_Option'
        
        globals()[df_name_Option] = Table_1_Avg_returns_of_portfolios_Option(data = option_data_Control_Basic_20230814, 
                                                                             sorted_var = x, 
                                                                             split_num = split_set[y])        
        globals()[df_name_Option].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
        
        
        # Stock
        
        df_name_Stock = 'portfolio_' + str(x) + '_Stock_' + str(split_set[y])
        df_sheet_name = str(x) + '_Stock'
        
        globals()[df_name_Stock] = Table_1_Avg_returns_of_portfolios_Stock(data = option_data_Control_Basic_20230814, 
                                                                           sorted_var = x, 
                                                                           split_num = split_set[y])        
        globals()[df_name_Stock].to_excel(writer, sheet_name = df_sheet_name, startrow = 9 * y + 1)
    
    
writer.save()


# %%  Save to Excel


# 開一個新的excel並把多個df寫到同excel不同sheet
output_path = 'D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/Python - Output/20230524.xlsx'
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


# Test

output_path = 'D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/Python - Output/202305241.xlsx'

portfolio_CW2010_SKEW_op_Option_3.to_excel(writer, sheet_name='CW2010_op', startrow = 1)
portfolio_CW2010_SKEW_op_Option_5.to_excel(writer, sheet_name='CW2010_op', startrow = 10)
portfolio_CW2010_SKEW_op_Option_10.to_excel(writer, sheet_name='CW2010_op', startrow = 19)
portfolio_CW2010_SKEW_op_Stock_3.to_excel(writer, sheet_name='CW2010_op', startrow = 28)
portfolio_CW2010_SKEW_op_Stock_5.to_excel(writer, sheet_name='CW2010_op', startrow = 37)
portfolio_CW2010_SKEW_op_Stock_10.to_excel(writer, sheet_name='CW2010_op', startrow = 46)

portfolio_CW2010_SKEW_vol_Option_3.to_excel(writer, sheet_name='CW2010_vol', startrow = 1)
portfolio_CW2010_SKEW_vol_Option_5.to_excel(writer, sheet_name='CW2010_vol', startrow = 10)
portfolio_CW2010_SKEW_vol_Option_10.to_excel(writer, sheet_name='CW2010_vol', startrow = 19)
portfolio_CW2010_SKEW_vol_Stock_3.to_excel(writer, sheet_name='CW2010_vol', startrow = 28)
portfolio_CW2010_SKEW_vol_Stock_5.to_excel(writer, sheet_name='CW2010_vol', startrow = 37)
portfolio_CW2010_SKEW_vol_Stock_10.to_excel(writer, sheet_name='CW2010_vol', startrow = 46)


# workbook  = writer.book
# worksheet = writer.sheets['Sheet1']

# fmt = writer.book.add_format({"font_name": "Arial"})
# worksheet.set_column('A:Z', None, fmt)
# worksheet.set_row(0, None, fmt)


writer.save() # 存檔生成excel檔案


