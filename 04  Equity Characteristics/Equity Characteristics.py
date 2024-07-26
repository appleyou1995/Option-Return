import pandas          as pd
import numpy           as np
import statsmodels.api as sm
import sys
import os

from pandas.tseries.offsets import DateOffset
from statistics             import quantiles
from scipy                  import stats


# %%  論文資料夾路徑

Path_PaperFolder = '我的雲端硬碟/學術｜研究與論文/論文著作/Option Return'


# %%  Win 資料夾路徑

Path_Win = 'D:/Google/'
Path_dir = os.path.join(Path_Win, Path_PaperFolder)


# %%  Mac 資料夾路徑

Path_Mac = '/Users/irisyu/Library/CloudStorage/GoogleDrive-jouping.yu@gmail.com/'
Path_dir = os.path.join(Path_Mac, Path_PaperFolder)


# %%  Input and Output Path

Path_Input  = os.path.join(Path_dir, 'Data/')
Path_Output = os.path.join(Path_dir, 'Code/04  Equity Characteristics/')


# %%  Import function

sys.path.append(Path_dir+'/Code/99  自訂函數')


# %%  Control Variables

CV = pd.read_csv(os.path.join(Path_Input, '控制變數', 'CV_merge result.csv'))

CV['date'] = pd.to_datetime(CV['date'])
CV['YYYYMM'] = CV['date'].dt.strftime('%Y%m').astype(int)

for col in CV.columns: print(col)

CFV_columns = [col for col in CV.columns if col.startswith('CFV_')]
Control_Variable_List = pd.Index(CFV_columns + CV.columns[13:22].tolist())


# Paper        聶瑋瑩
# ----------   ------------
# CFV        = CFV_
# CH         = cash
# DISP       = 
# ISSUE_1Y   = 
# ISSUE_5Y   = 
# TEF        = tef
# –PM        = 
# –ln(PRICE) = logPrice
# –PROFIT    = profitable
# –ZS        = Zscore


# %%  SKEW Data from 瑄凌 >>> op & vol [ 20230524 ]

CW2010_SKEW_op  = pd.read_csv(os.path.join(Path_Input, '張瑄凌', 'CW2010_SKEW_op.csv'))
CW2010_SKEW_vol = pd.read_csv(os.path.join(Path_Input, '張瑄凌', 'CW2010_SKEW_vol.csv'))

CW2010_SKEW_op.rename(columns = {'CW2010_CPIV':'CW2010_SKEW_op'}, inplace = True)
CW2010_SKEW_vol.rename(columns = {'CW2010_CPIV':'CW2010_SKEW_vol'}, inplace = True)


# %%  Merge Stock_Size

Control_Basic = CV.merge(CW2010_SKEW_op, 
                         left_on = ['YYYYMM', 'permno'], 
                         right_on = ['YYYYMM', 'PERMNO'])


Control_Basic = Control_Basic[
    ['optionid', 'DATE', 'YYYYMM', 'PERMNO', 'cusip', 'Stock_Size'] + 
    Control_Variable_List.tolist()
]

for col in Control_Basic.columns: print(col)


# %%  Option Data from SAS (Option Return - 20221006.egp)

option_data_all = pd.read_csv(os.path.join(Path_Input, 'SAS - Output', 'Y_SHROUT_Stock.csv'))
# for col in option_data_all.columns: print(col)

option_data_Original = option_data_all[['optionid', 'date', 'YYYYMM_t', 'cusip', 'PERMNO', 
                                        'SHROUT', 'RET', 'Buy & hold until month-end (%)']]

option_data_Original.rename(columns = {'Buy & hold until month-end (%)':'Option_Return'}, inplace = True)
option_data_Original.rename(columns = {'RET':'Stock_Return'}, inplace = True)
option_data_Original.rename(columns = {'SHROUT':'Option_Size'}, inplace = True)


option_data_Original['date'] = pd.to_datetime(option_data_Original['date'])
option_data_Original.insert(loc = 1, column = 'Next_Month_Option', value = option_data_Original['date'] + DateOffset(months=1))
option_data_Original = option_data_Original.sort_values(by=['date', 'cusip'])

option_data_Original = option_data_Original.set_index('date', drop = False)
option_data_Original.rename(columns = {'date':'This_Month_Option'}, inplace = True)

for col in option_data_Original.columns: print(col)


# %%  Merge 2 dataframe

Merge_Data = option_data_Original.merge(Control_Basic, 
                                        left_on = ['YYYYMM_t', 'optionid'], 
                                        right_on = ['YYYYMM', 'optionid'], 
                                        suffixes = ('', '_y'))

Merge_Data.drop(Merge_Data.filter(regex = '_y$').columns, axis = 1, inplace = True)

for col in Merge_Data.columns: print(col)


# %%  Calculate Top and Bottom split data

def Top_and_Bottom(data, sorted_var, split_num, return_type):
    data = data.dropna(subset=[sorted_var])
    data['count'] = data.groupby(['This_Month_Option'])['PERMNO'].transform('count')
    filtered_data = data[data['count'] >= split_num]
    grouped_data = pd.DataFrame(filtered_data.groupby('DATE'))
    
    for i in range(split_num):
        portfolio_df = pd.DataFrame()
        VW_Stock  = pd.DataFrame(columns=['VW_S'], index=range(len(grouped_data)-1))
        VW_Option = pd.DataFrame(columns=['VW_O'], index=range(len(grouped_data)-1))
    
        for j in range(len(grouped_data)):
            month_j = grouped_data.iloc[j, 1].copy()
            
            if j == 0:
                quantile_list = quantiles(month_j[sorted_var], n=split_num)
            else:
                quantile_bins = [month_j[month_j[sorted_var] < quantile_list[q-1]] if q == 1 else
                                 month_j[month_j[sorted_var] > quantile_list[q-2]] if q == split_num else
                                 month_j[month_j[sorted_var].between(quantile_list[q-2], quantile_list[q-1])]
                                 for q in range(1, split_num + 1)]
                
                quantile_list = quantiles(month_j[sorted_var], n=split_num)
                portfolio_df = pd.concat([portfolio_df, pd.DataFrame(quantile_bins[i].mean()).T])
                
                VW_Stock.iloc[j-1]  = np.average(quantile_bins[i][return_type], weights=quantile_bins[i]['Stock_Size'])
                VW_Option.iloc[j-1] = np.average(quantile_bins[i][return_type], weights=quantile_bins[i]['Option_Size'])
    
        VW_Stock.index = VW_Option.index = portfolio_df.index = grouped_data.iloc[1:, 0]
        VW_Stock, VW_Option = VW_Stock.astype(float), VW_Option.astype(float)
        EW_VW = pd.concat([portfolio_df[return_type], VW_Stock, VW_Option], axis=1)
    
        if i == 0:
            port_split_bottom = EW_VW
            
        elif i == split_num - 1:
            port_split_top = EW_VW

    return port_split_top, port_split_bottom


# %%  Calculate required statistics

def calculate_statistics(top, bottom):
    diff = top['VW_S'] - bottom['VW_S']
    
    X = np.ones(len(diff))  # adding a constant term
    ols_result = sm.OLS(diff, X).fit(cov_type='HAC', cov_kwds={'maxlags':1})
    nw_t_stat = ols_result.tvalues[0]
    
    statistics = {
        'Mean'           : diff.mean(),
        'T-stat'         : stats.ttest_1samp(diff, 0)[0],
        'NW T-stat'      : nw_t_stat,
        'Min'            : diff.min(),
        '10th pctl'      : np.percentile(diff, 10),
        'Q1'             : np.percentile(diff, 25),
        'Med'            : np.median(diff),
        'Q3'             : np.percentile(diff, 75),
        '90th pctl'      : np.percentile(diff, 90),
        'Max'            : diff.max(),
        'SD'             : diff.std(),
        'Skewness'       : stats.skew(diff),
        'Excess Kurtosis': stats.kurtosis(diff)
    }
    return statistics


# %%  Create final table [ Option ]

final_table_option = pd.DataFrame()

for sorted_var in Control_Variable_List:
    top, bottom = Top_and_Bottom(Merge_Data, sorted_var, split_num=10, return_type='Option_Return')
    statistics = calculate_statistics(top, bottom)
    final_table_option = final_table_option.append(pd.DataFrame(statistics, index=[sorted_var]))

final_table_option = final_table_option[['Mean',
                                         'T-stat',
                                         'NW T-stat',
                                         'Min',
                                         '10th pctl',
                                         'Q1',
                                         'Med',
                                         'Q3',
                                         '90th pctl',
                                         'Max',
                                         'SD',
                                         'Skewness',
                                         'Excess Kurtosis']]


markdown_table_option = final_table_option.applymap(lambda x: '{:.2f}'.format(x)).to_markdown()

with open(os.path.join(Path_Output, 'Table_4_option.md'), 'w') as file:
    file.write(markdown_table_option)


# %%  Create final table [ Stock ]

final_table_stock = pd.DataFrame()

for sorted_var in Control_Variable_List:
    top, bottom = Top_and_Bottom(Merge_Data, sorted_var, split_num=10, return_type='Stock_Return')
    statistics = calculate_statistics(top, bottom)
    final_table_stock = final_table_stock.append(pd.DataFrame(statistics, index=[sorted_var]))

final_table_stock = final_table_stock[['Mean',
                                       'T-stat',
                                       'NW T-stat',
                                       'Min',
                                       '10th pctl',
                                       'Q1',
                                       'Med',
                                       'Q3',
                                       '90th pctl',
                                       'Max',
                                       'SD',
                                       'Skewness',
                                       'Excess Kurtosis']]


markdown_table_stock = final_table_stock.applymap(lambda x: '{:.2f}'.format(x)).to_markdown()

with open(os.path.join(Path_Output, 'Table_4_stock.md'), 'w') as file:
    file.write(markdown_table_stock)
