import pandas          as pd
import numpy           as np
import scipy.stats     as stats
import sys

from statistics import quantiles


# %%  Import T-statistics function

sys.path.append('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/99  自訂函數')

from T_statistics import T_statistics



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