import pandas      as pd
import numpy       as np
import scipy.stats as stats

import statsmodels.formula.api as smf

from pathlib import Path
from pandas.tseries.offsets import DateOffset
from statistics import quantiles


# %%  Option Data from SAS (Option Return - 20221006.egp)


folder_SAS = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/SAS - Output')
option_data_all = pd.read_csv(folder_SAS/"Y_SHROUT.csv")

# for col in option_data_all.columns: print(col)

option_data_Original = option_data_all[['date', 'cusip', 'PERMNO', 'SHROUT', 'Buy & hold until month-end (%)']]
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


folder_Sherry = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/張詠瑄')
SKEW_Sherry = pd.read_csv(folder_Sherry/"skew12_monthly.csv")


# for col in SKEW_Sherry.columns: print(col)

SKEW_Sherry.rename(columns = {'size':'Stock_Size'}, inplace = True)

SKEW_Sherry['date'] = pd.to_datetime(SKEW_Sherry['date'])
SKEW_Sherry.insert(loc = 1, column = 'Next_Month_Stock', value = SKEW_Sherry['date'] + DateOffset(months=1))
SKEW_Sherry = SKEW_Sherry.sort_values(by=['date', 'cusip'])

SKEW_Sherry = SKEW_Sherry.set_index('date', drop = False)
SKEW_Sherry.rename(columns = {'date':'This_Month_Stock'}, inplace = True)


# groupby_date
SKEW_groupby_date = pd.DataFrame(SKEW_Sherry.groupby('date'))


# %%  SKEW Data from Sherry [ 20230315 ]


SKEW_Sherry_20230315 = pd.read_csv(folder_Sherry/"skew2_monthly_permno.csv")
# for col in SKEW_Sherry_20230315.columns: print(col)

SKEW_Sherry_20230315.rename(columns = {'dlycap':'Stock_Size'}, inplace = True)

SKEW_Sherry_20230315['date'] = pd.to_datetime(SKEW_Sherry_20230315['date'])
SKEW_Sherry_20230315 = SKEW_Sherry_20230315.set_index('date', drop = False)

SKEW_Sherry_20230315 = SKEW_Sherry_20230315[['date', 'permno', 'cusip', "SKEW_2", 'Stock_Size']]
SKEW_Sherry_20230315.rename(columns = {'date':'This_Month_Stock'}, inplace = True)


# groupby_date
SKEW_Sherry_20230315_groupby_date = pd.DataFrame(SKEW_Sherry_20230315.groupby('date'))


# %%  SKEW Data from Sherry [ 20230330 ]

# 詠瑄：「otmp_vola_wm、atmc_vola_wm 指的意思是 otm 跟 atm 一天有很多資料時，
#        我使用 volume 將 volatility 做 weighted mean 所得出之那一個 date 的加權的 implied volatility」

folder_Sherry = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/張詠瑄')


SKEW_1_Old_vs_New = pd.read_csv(folder_Sherry/"2023-03-30/1996-01-31_SKEW_1_Old_vs_New.csv")
SKEW_2_Old_vs_New = pd.read_csv(folder_Sherry/"2023-03-30/1996-01-31_SKEW_2_Old_vs_New.csv")



#### SKEW_1

SKEW_1_Sherry_20230330 = pd.read_csv(folder_Sherry/"2023-03-30/variable_skew1_monthly.csv")
# for col in SKEW_1_Sherry_20230330.columns: print(col)

SKEW_1_Sherry_20230330.rename(columns = {'size':'Stock_Size'}, inplace = True)

SKEW_1_Sherry_20230330['date'] = pd.to_datetime(SKEW_1_Sherry_20230330['date'])
SKEW_1_Sherry_20230330 = SKEW_1_Sherry_20230330.set_index('date', drop = False)

SKEW_1_Sherry_20230330.rename(columns = {'date':'This_Month_Stock'}, inplace = True)


# groupby_date
SKEW_1_Sherry_20230330_groupby_date = pd.DataFrame(SKEW_1_Sherry_20230330.groupby('date'))



#### SKEW_2

SKEW_2_Sherry_20230330 = pd.read_csv(folder_Sherry/"2023-03-30/variable_skew2_monthly.csv")
# for col in SKEW_2_Sherry_20230330.columns: print(col)

SKEW_2_Sherry_20230330.rename(columns = {'size':'Stock_Size'}, inplace = True)

SKEW_2_Sherry_20230330['date'] = pd.to_datetime(SKEW_2_Sherry_20230330['date'])
SKEW_2_Sherry_20230330 = SKEW_2_Sherry_20230330.set_index('date', drop = False)

SKEW_2_Sherry_20230330.rename(columns = {'date':'This_Month_Stock'}, inplace = True)


# groupby_date
SKEW_2_Sherry_20230330_groupby_date = pd.DataFrame(SKEW_2_Sherry_20230330.groupby('date'))


# %%  Fama-French five-factor model


folder_FF5 = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data')
FF5_data_all = pd.read_csv(folder_FF5/'F-F_monthly.csv')

FF5_data = FF5_data_all.iloc[390:702,2:7]
FF5_data.index = SKEW_groupby_date[0]


# %%  Combine Above Dataframes


option_SKEW = option_data_Original.merge(SKEW_Sherry, left_on = ['This_Month_Option', 'cusip'], 
                                                      right_on = ['This_Month_Stock', 'cusip'])
option_SKEW_count = pd.DataFrame(option_SKEW.groupby('This_Month_Option')['cusip'].count()).sort_values(by=['cusip'])
option_SKEW_count.rename(columns = {'cusip':'count'}, inplace = True)

option_data = pd.merge(option_SKEW, option_SKEW_count, left_on = ['This_Month_Option'], right_index = True)          
option_data = option_data[['This_Month_Option', 'cusip', 'SKEW_1', 'SKEW_2', 
                                                         'Stock_Size', 'Option_Size', 
                                                         'Option_Return', 'count']]
option_data = option_data.set_index('This_Month_Option')
option_data.index.name = 'date'


# %%  Combine Above Dataframes [ 20230315 ]


option_SKEW_20230315 = option_data_Original.merge(SKEW_Sherry_20230315, left_on = ['This_Month_Option', 'PERMNO'], 
                                                                        right_on = ['This_Month_Stock', 'permno'])
option_SKEW_count_20230315 = pd.DataFrame(option_SKEW_20230315.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_SKEW_count_20230315.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_20230315 = pd.merge(option_SKEW_20230315, option_SKEW_count_20230315, left_on = ['This_Month_Option'], right_index = True)
# for col in option_data_20230315.columns: print(col)          
option_data_20230315 = option_data_20230315[['This_Month_Option', 'PERMNO', 'SKEW_2', 
                                             'Stock_Size', 'Option_Size', 
                                             'Option_Return', 'count']]
option_data_20230315 = option_data_20230315.set_index('This_Month_Option')
option_data_20230315.index.name = 'date'


# %%  Combine Above Dataframes [ 20230330 ]


#### SKEW_1

option_SKEW_1_20230330 = option_data_Original.merge(SKEW_1_Sherry_20230330, left_on = ['This_Month_Option', 'PERMNO'], 
                                                                            right_on = ['This_Month_Stock', 'permno'])
option_SKEW_1_count_20230330 = pd.DataFrame(option_SKEW_1_20230330.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_SKEW_1_count_20230330.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_1_20230330 = pd.merge(option_SKEW_1_20230330, option_SKEW_1_count_20230330, left_on = ['This_Month_Option'], right_index = True)
# for col in option_data_1_20230330.columns: print(col)
# option_data_1_20230330 = option_data_1_20230330[['This_Month_Option', 'PERMNO', 'SKEW_2', 
#                                                  'Stock_Size', 'Option_Size', 
#                                                  'Option_Return', 'count']]
option_data_1_20230330 = option_data_1_20230330.set_index('This_Month_Option')
option_data_1_20230330.index.name = 'date'



#### SKEW_2

option_SKEW_2_20230330 = option_data_Original.merge(SKEW_2_Sherry_20230330, left_on = ['This_Month_Option', 'PERMNO'], 
                                                                            right_on = ['This_Month_Stock', 'permno'])
option_SKEW_2_count_20230330 = pd.DataFrame(option_SKEW_2_20230330.groupby('This_Month_Option')['PERMNO'].count()).sort_values(by=['PERMNO'])
option_SKEW_2_count_20230330.rename(columns = {'PERMNO':'count'}, inplace = True)

option_data_2_20230330 = pd.merge(option_SKEW_2_20230330, option_SKEW_2_count_20230330, left_on = ['This_Month_Option'], right_index = True)
# for col in option_data_2_20230330.columns: print(col)
# option_data_2_20230330 = option_data_2_20230330[['This_Month_Option', 'PERMNO', 'SKEW_2', 
#                                                  'Stock_Size', 'Option_Size', 
#                                                  'Option_Return', 'count']]
option_data_2_20230330 = option_data_2_20230330.set_index('This_Month_Option')
option_data_2_20230330.index.name = 'date'


# %%  Split with Quantiles


def portfolio(data, sorted_var, split_num):
    
    quantile_by = data[sorted_var]
    quantile_list = quantiles(quantile_by, n = split_num)
    
    for q in range(1, split_num):
        locals()['quantile_'+str(q)] = quantile_list[q - 1]
        
    for q in range(1, split_num + 1):
        if q == 1:
            output = [data[data[sorted_var] < locals()['quantile_'+str(q)]]]
        elif q == split_num:
            output.append(data[data[sorted_var] > locals()['quantile_'+str(q-1)]])
        else:
            output.append(data[data[sorted_var].between(locals()['quantile_'+str(q-1)], locals()['quantile_'+str(q)])])
    
    return output
    
    
# %%  T-statistics


def T_statistics(data):
    
    T_statistics = stats.ttest_1samp(data, 0)[0]    
    T_statistics = '('+str("{:10.2f}".format(T_statistics))+')'
    
    return T_statistics


# %%  Test


option_SKEW_count.head(18)

option_data_Original.loc['2011-10-31']
SKEW_Sherry.loc['2011-10-31']
option_data.loc['2011-10-31']

option_data_Original.dtypes
SKEW_Sherry.dtypes

option_data_Original['cusip_6'] = option_data_Original['cusip'].str[:6]
SKEW_Sherry['cusip_6'] = SKEW_Sherry['cusip'].str[:6]


option_SKEW_6 = option_data_Original.merge(SKEW_Sherry, left_on = ['This_Month_Option', 'cusip_6'], 
                                                        right_on = ['This_Month_Stock', 'cusip_6'])
option_SKEW_count_6 = pd.DataFrame(option_SKEW_6.groupby('This_Month_Option')['cusip_6'].count()).sort_values(by=['cusip_6'])
option_SKEW_count_6.head(18)
compare = pd.concat([option_SKEW_count, option_SKEW_count_6], axis=1)
option_SKEW_count_6.rename(columns = {'cusip_6':'count'}, inplace = True)

option_data_6 = pd.merge(option_SKEW_6, option_SKEW_count_6, left_on = ['This_Month_Option'], right_index = True)          
option_data_6 = option_data_6[['This_Month_Option', 'cusip_6', 'SKEW_1', 'SKEW_2', 
                                                         'Stock_Size', 'Option_Size', 
                                                         'Option_Return', 'count']]
option_data_6 = option_data_6.set_index('This_Month_Option')
option_data_6.index.name = 'date'



# %%  【Table】 Average returns of portfolios  (2022_RFS_Option Return Predictability - Table 3)


def Table_1_Avg_returns_of_portfolios(data, sorted_var, split_num):

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
        Value_Weighted_Stock  = pd.DataFrame(columns=['VW_S'], index = range(len(option_data_df)))
        Value_Weighted_Option = pd.DataFrame(columns=['VW_O'], index = range(len(option_data_df)))
        
        for j in range(len(option_data_df)):
            data         = option_data_df.iloc[j,1].copy()
            output       = portfolio(data, sorted_var, split_num)
            portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T])
            
            Value_Weighted_Stock.iloc[j]  = np.average(output[i]['Option_Return'], weights = output[i]['Stock_Size'])
            Value_Weighted_Option.iloc[j] = np.average(output[i]['Option_Return'], weights = output[i]['Option_Size'])
            
        portfolio_df.index          = option_data_df[0]
        Value_Weighted_Stock.index  = option_data_df[0]
        Value_Weighted_Option.index = option_data_df[0]
        
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



# %%  

# SKEW 1

portfolio_SKEW_1_3  = Table_1_Avg_returns_of_portfolios(data = option_data, sorted_var = 'SKEW_1', split_num = 3)
portfolio_SKEW_1_5  = Table_1_Avg_returns_of_portfolios(data = option_data, sorted_var = 'SKEW_1', split_num = 5)
portfolio_SKEW_1_10 = Table_1_Avg_returns_of_portfolios(data = option_data, sorted_var = 'SKEW_1', split_num = 10)


# SKEW 2

portfolio_SKEW_2_3  = Table_1_Avg_returns_of_portfolios(data = option_data, sorted_var = 'SKEW_2', split_num = 3)
portfolio_SKEW_2_5  = Table_1_Avg_returns_of_portfolios(data = option_data, sorted_var = 'SKEW_2', split_num = 5)
portfolio_SKEW_2_10 = Table_1_Avg_returns_of_portfolios(data = option_data, sorted_var = 'SKEW_2', split_num = 10)


# SKEW 2 [ 20230315 ]

portfolio_SKEW_2_20230315_3  = Table_1_Avg_returns_of_portfolios(data = option_data_20230315, sorted_var = 'SKEW_2', split_num = 3)
portfolio_SKEW_2_20230315_5  = Table_1_Avg_returns_of_portfolios(data = option_data_20230315, sorted_var = 'SKEW_2', split_num = 5)
portfolio_SKEW_2_20230315_10 = Table_1_Avg_returns_of_portfolios(data = option_data_20230315, sorted_var = 'SKEW_2', split_num = 10)


# SKEW 1 [ 20230330 ]

portfolio_SKEW_1_20230330_3  = Table_1_Avg_returns_of_portfolios(data = option_data_1_20230330, sorted_var = 'SKEW_1', split_num = 3)
portfolio_SKEW_1_20230330_5  = Table_1_Avg_returns_of_portfolios(data = option_data_1_20230330, sorted_var = 'SKEW_1', split_num = 5)
portfolio_SKEW_1_20230330_10 = Table_1_Avg_returns_of_portfolios(data = option_data_1_20230330, sorted_var = 'SKEW_1', split_num = 10)


# SKEW 2 [ 20230330 ]

portfolio_SKEW_2_20230330_3  = Table_1_Avg_returns_of_portfolios(data = option_data_2_20230330, sorted_var = 'SKEW_2', split_num = 3)
portfolio_SKEW_2_20230330_5  = Table_1_Avg_returns_of_portfolios(data = option_data_2_20230330, sorted_var = 'SKEW_2', split_num = 5)
portfolio_SKEW_2_20230330_10 = Table_1_Avg_returns_of_portfolios(data = option_data_2_20230330, sorted_var = 'SKEW_2', split_num = 10)


# %%  Test

df = pd.DataFrame({'a':port_split_top['EW'],
                   'b':port_split_bottom['EW']})

reg = smf.ols('a ~ 1 + b', data = df).fit(cov_type='HAC',cov_kwds={'maxlags':1})
reg.summary()


# %%  【Table】 Portfolios Sorted on Volatility Features  (Lillian - Table 4)







# %%  【Table】 Fama-MacBeth Regressions  (Lillian - Table 5)






