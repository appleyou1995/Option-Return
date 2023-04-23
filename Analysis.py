import pandas      as pd
import numpy       as np
import scipy.stats as stats
# import math

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


folder_Sherry = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/張詠瑄')
SKEW_Sherry = pd.read_csv(folder_Sherry/"skew12_monthly.csv")

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


folder_FF5 = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data')
FF5_data_all = pd.read_csv(folder_FF5/'F-F_monthly.csv')

FF5_data = FF5_data_all.iloc[390:702,2:7]
FF5_data.index = SKEW_groupby_date[0]


# %%  Combine Above Dataframes


option_SKEW = option_data_Original.merge(SKEW_Sherry, left_on = ['This_Month_Option', 'cusip'], right_on = ['This_Month_Stock', 'cusip'])
option_SKEW_count = pd.DataFrame(option_SKEW.groupby('This_Month_Option')['cusip'].count()).sort_values(by=['cusip'])
option_SKEW_count.rename(columns = {'cusip':'count'}, inplace = True)

######################################################################################################################
                                                                                                                     #
option_data = pd.merge(option_SKEW, option_SKEW_count, left_on = ['This_Month_Option'], right_index = True)          #
                                                                                                                     #
######################################################################################################################

option_data = option_data[['This_Month_Option', 'cusip', 'skew1', 'skew2', 'Stock_Size', 'Option_Size', 'Option_Return', 'count']]
option_data = option_data.set_index('This_Month_Option')
option_data.index.name = 'date'


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


# %%  T-statistics


def T_statistics(data):
    
    # # Way 1
    # mean = data.mean()
    # std  = data.std()
    # n    = len(data)
    # T_statistics = mean / (std / math.sqrt(n))
    
    # Way 2
    T_statistics = stats.ttest_1samp(data, 0)[0]
    
    T_statistics = '('+str("{:10.2f}".format(T_statistics))+')'
    return T_statistics



# %%  【Table】 Average returns of portfolios  (2022_RFS_Option Return Predictability - Table 3)

split_num  = 5

option_data = option_data[option_data['count'] >= split_num]
option_data_df = pd.DataFrame(option_data.groupby('date'))



######################################################################################################################
######################################################  SKEW 1  ######################################################

sorted_var = 'skew1'

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



##################################################  vvv   T-statistics  vvv  ###############################################

# T-statistics of portfolios (Way 1)
# top 跟 bottom 是那些公司在不同時間點排序然後組投資組合，不算是 two different sample

t_stats_EW   = stats.ttest_ind(port_split_top['EW'],   port_split_bottom['EW'])[0]
t_stats_VW_S = stats.ttest_ind(port_split_top['VW_S'], port_split_bottom['VW_S'])[0]
t_stats_VW_O = stats.ttest_ind(port_split_top['VW_O'], port_split_bottom['VW_O'])[0]

port_t_statistics.iloc[split_num]['t_stats_EW']   = '('+str("{:10.2f}".format(t_stats_EW))+')'
port_t_statistics.iloc[split_num]['t_stats_VW_S'] = '('+str("{:10.2f}".format(t_stats_VW_S))+')'
port_t_statistics.iloc[split_num]['t_stats_VW_O'] = '('+str("{:10.2f}".format(t_stats_VW_O))+')'


# T-statistics of portfolios (Way 2)
# 用 T_statistics = stats.ttest_1samp(data, 0)[0] 單一樣本計算 T-statistics
t_stats_EW   = T_statistics(port_split_top['EW'] - port_split_bottom['EW'])
t_stats_VW_S = T_statistics(port_split_top['VW_S'] - port_split_bottom['VW_S'])
t_stats_VW_O = T_statistics(port_split_top['VW_O'] - port_split_bottom['VW_O'])

port_t_statistics.iloc[split_num]['t_stats_EW']   = t_stats_EW
port_t_statistics.iloc[split_num]['t_stats_VW_S'] = t_stats_VW_S
port_t_statistics.iloc[split_num]['t_stats_VW_O'] = t_stats_VW_O


# T-statistics of portfolios (Way 3)
# 結果跟 Way 2 一樣
t_stats_EW   = stats.ttest_rel(port_split_top['EW'],   port_split_bottom['EW'])[0]
t_stats_VW_S = stats.ttest_rel(port_split_top['VW_S'], port_split_bottom['VW_S'])[0]
t_stats_VW_O = stats.ttest_rel(port_split_top['VW_O'], port_split_bottom['VW_O'])[0]

port_t_statistics.iloc[split_num]['t_stats_EW']   = '('+str("{:10.2f}".format(t_stats_EW))+')'
port_t_statistics.iloc[split_num]['t_stats_VW_S'] = '('+str("{:10.2f}".format(t_stats_VW_S))+')'
port_t_statistics.iloc[split_num]['t_stats_VW_O'] = '('+str("{:10.2f}".format(t_stats_VW_O))+')'

##################################################  ^^^   T-statistics  ^^^  ###############################################



portfolio_SKEW_1 = pd.DataFrame(index = split_index)

portfolio_SKEW_1['SKEW_1_EW']                 = portfolio_fin['Option_Return']
portfolio_SKEW_1['SKEW_1_EW_t_stats']         = port_t_statistics['t_stats_EW']
portfolio_SKEW_1['SKEW_1_VW_Stock']           = portfolio_fin['VW_S']
portfolio_SKEW_1['SKEW_1_VW_Stock_t_stats']   = port_t_statistics['t_stats_VW_S']
portfolio_SKEW_1['SKEW_1_VW_Option']          = portfolio_fin['VW_O']
portfolio_SKEW_1['SKEW_1_VW_Option_t_stats']  = port_t_statistics['t_stats_VW_O']
portfolio_SKEW_1 = portfolio_SKEW_1.T




######################################################################################################################
######################################################  SKEW 2  ######################################################

sorted_var = 'skew2'

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



##################################################  vvv   T-statistics  vvv  ###############################################

# T-statistics of portfolios (Way 1)
# top 跟 bottom 是那些公司在不同時間點排序然後組投資組合，不算是 two different sample

t_stats_EW   = stats.ttest_ind(port_split_top['EW'],   port_split_bottom['EW'])[0]
t_stats_VW_S = stats.ttest_ind(port_split_top['VW_S'], port_split_bottom['VW_S'])[0]
t_stats_VW_O = stats.ttest_ind(port_split_top['VW_O'], port_split_bottom['VW_O'])[0]

port_t_statistics.iloc[split_num]['t_stats_EW']   = '('+str("{:10.2f}".format(t_stats_EW))+')'
port_t_statistics.iloc[split_num]['t_stats_VW_S'] = '('+str("{:10.2f}".format(t_stats_VW_S))+')'
port_t_statistics.iloc[split_num]['t_stats_VW_O'] = '('+str("{:10.2f}".format(t_stats_VW_O))+')'


# T-statistics of portfolios (Way 2)
# 用 T_statistics = stats.ttest_1samp(data, 0)[0] 單一樣本計算 T-statistics
t_stats_EW   = T_statistics(port_split_top['EW'] - port_split_bottom['EW'])
t_stats_VW_S = T_statistics(port_split_top['VW_S'] - port_split_bottom['VW_S'])
t_stats_VW_O = T_statistics(port_split_top['VW_O'] - port_split_bottom['VW_O'])

port_t_statistics.iloc[split_num]['t_stats_EW']   = t_stats_EW
port_t_statistics.iloc[split_num]['t_stats_VW_S'] = t_stats_VW_S
port_t_statistics.iloc[split_num]['t_stats_VW_O'] = t_stats_VW_O


# T-statistics of portfolios (Way 3)
# 結果跟 Way 2 一樣
t_stats_EW   = stats.ttest_rel(port_split_top['EW'],   port_split_bottom['EW'])[0]
t_stats_VW_S = stats.ttest_rel(port_split_top['VW_S'], port_split_bottom['VW_S'])[0]
t_stats_VW_O = stats.ttest_rel(port_split_top['VW_O'], port_split_bottom['VW_O'])[0]

port_t_statistics.iloc[split_num]['t_stats_EW']   = '('+str("{:10.2f}".format(t_stats_EW))+')'
port_t_statistics.iloc[split_num]['t_stats_VW_S'] = '('+str("{:10.2f}".format(t_stats_VW_S))+')'
port_t_statistics.iloc[split_num]['t_stats_VW_O'] = '('+str("{:10.2f}".format(t_stats_VW_O))+')'

##################################################  ^^^   T-statistics  ^^^  ###############################################



# portfolio_SKEW_2 = pd.DataFrame(index = range(1, 1 + split_num))
portfolio_SKEW_2 = pd.DataFrame(index = split_index)

portfolio_SKEW_2['SKEW_2_EW']                 = portfolio_fin['Option_Return']
portfolio_SKEW_2['SKEW_2_EW_t_stats']         = port_t_statistics['t_stats_EW']
portfolio_SKEW_2['SKEW_2_VW_Stock']           = portfolio_fin['VW_S']
portfolio_SKEW_2['SKEW_2_VW_Stock_t_stats']   = port_t_statistics['t_stats_VW_S']
portfolio_SKEW_2['SKEW_2_VW_Option']          = portfolio_fin['VW_O']
portfolio_SKEW_2['SKEW_2_VW_Option_t_stats']  = port_t_statistics['t_stats_VW_O']
portfolio_SKEW_2 = portfolio_SKEW_2.T




# %%  【Table】 Portfolios Sorted on Volatility Features  (Lillian - Table 4)







# %%  【Table】 Fama-MacBeth Regressions  (Lillian - Table 5)






