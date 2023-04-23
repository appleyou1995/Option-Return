import pandas   as pd
import numpy    as np
from pathlib import Path


# %%  X variables from Lillian (volatility_var.py)


folder = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/陳韻安/volatility_var')

# Stock Data
stock_data   = pd.read_pickle(folder/'stock_data.pkl')
# stock_data_d = pd.read_pickle(folder/'stock_data_d.pkl')
# option_data  = pd.read_pickle(folder/'option_data.pkl')

# Implied Volatility
implied_call = pd.read_pickle(folder/'implied_call.pkl')
implied_put  = pd.read_pickle(folder/'implied_put.pkl')
implied_vol  = pd.read_pickle(folder/'implied_vol.pkl')

# Realized Volatility
realized_vol = pd.read_pickle(folder/'realized_vol.pkl')

# Volatility Var
vol_var      = pd.read_pickle(folder/'vol_var.pkl')


# %%  Y variable from SAS (Option Return - 20221006.egp)


folder_SAS = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/SAS - Output')
option_data_all = pd.read_csv(folder_SAS/"Y.csv")

# for col in option_data_all.columns:
#     print(col)
    
option_data     = option_data_all[['date', 'PERMNO', 'Buy & hold until month-end (%)']]
option_data.rename(columns = {'Buy & hold until month-end (%)':'Option_Return'}, inplace = True)


# %%  from Lillian (volatility analysis.py)

realized_vol = realized_vol.shift(1).iloc[1:,:]
vol_df = pd.DataFrame()
for i in range(len(realized_vol)):
    data = realized_vol.iloc[[i],:].copy()
    temp = data.T.reset_index()
    temp.columns = ['PERMNO', 'realized_vol']
    vol_df = pd.concat([vol_df, temp], axis=0)

implied_call = implied_call.shift(1).iloc[1:,:]
temp1_df = pd.DataFrame()
for i in range(len(implied_call)):
    data = implied_call.iloc[[i],:].copy()
    temp = data.T.reset_index()
    temp.columns = ['PERMNO', 'implied_call']
    temp1_df = pd.concat([temp1_df, temp], axis=0)   
   
implied_put = implied_put.shift(1).iloc[1:,:]
temp2_df = pd.DataFrame()
for i in range(len(implied_put)):
    data = implied_put.iloc[[i],:].copy()
    temp = data.T.reset_index()
    temp.columns = ['PERMNO', 'implied_put']
    temp2_df = pd.concat([temp2_df, temp], axis=0)   


folder_pkl = Path('D:/Google/我的雲端硬碟/學術研究/論文著作/Option Return/Data/陳韻安/Lillian')

RET = pd.read_pickle(folder_pkl/'data_balanced.pkl').iloc[:,:2]
vol_fin_df = pd.concat([vol_df,temp1_df['implied_call'],temp2_df['implied_put']], axis=1)
vol_fin_df.index = RET.index
vol_fin_df = pd.concat([RET,vol_fin_df.iloc[:,1:]], axis=1)

vol_temp = vol_fin_df.dropna()

# Volatility spreads
vol_temp['rivolspread'] = vol_temp['realized_vol'] - (vol_temp['implied_call'] + vol_temp['implied_put'])*0.5
vol_temp['ivolspread'] = vol_temp['implied_call'] - vol_temp['implied_put']


#%%  from Lillian (volatility analysis.py)


# Portfolio Sorted on Realized and Implied Volatilities
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


vol_temp_df = pd.DataFrame(vol_temp.groupby('date'))
vol_temp_df_group = pd.DataFrame(vol_temp.groupby('date')['PERMNO'].count()).sort_values(by=['PERMNO'])

for col in vol_temp.columns: print(col)


# Customize 1
sorted_var = 'realized_vol'
split_num  = 5

portfolio_fin = pd.DataFrame()
for i in range(split_num):
    portfolio_df = pd.DataFrame()
    for j in range(len(vol_temp_df)):
        data         = vol_temp_df.iloc[j,1].copy()
        output       = portfolio(data, sorted_var, split_num)
        portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T.iloc[:,1:]])
    portfolio_df.index = realized_vol.index
    portfolio_fin = pd.concat([portfolio_fin, pd.DataFrame(portfolio_df.mean()).T])
portfolio_fin.index = list(range(1, 1 + split_num))


# Customize 2
sorted_var = 'ivolspread'
split_num  = 5

portfolio_ivolspread = pd.DataFrame()
for i in range(split_num):
    portfolio_df = pd.DataFrame()
    for j in range(len(vol_temp_df)):
        data         = vol_temp_df.iloc[j,1].copy()
        output       = portfolio(data, sorted_var, split_num)
        portfolio_df = pd.concat([portfolio_df, pd.DataFrame(output[i].mean()).T.iloc[:,1:]])
    portfolio_ivolspread = pd.concat([portfolio_ivolspread, pd.DataFrame(portfolio_df.mean()).T])
portfolio_ivolspread.index = list(range(1, 1 + split_num))


#%%  Fama-French three-factor model


ff3_data = pd.read_csv(folder_pkl/'F-F_Research_Data_Factors.csv',
                       skiprows=3, index_col=0, nrows=1134)/100
# ff3_data = ff3_data.iloc[-300:,:]  # Lillian Original Version
ff3_data = ff3_data.iloc[-299:,:]    # Fix to Clear Error
ff3_data.index = realized_vol.index


#%%      


import statsmodels.formula.api as smf

sorted_var = 'rivolspread'
split_num = 5

ff3_alpha = pd.DataFrame()
for i in range(split_num):
    data_df = pd.DataFrame()
    for j in range(len(vol_temp_df)):
        data = vol_temp_df.iloc[j,1].iloc[:,1:].copy()
        data['Mkt_RF'] = ff3_data['Mkt-RF'][j]
        data['SMB'] = ff3_data['SMB'][j]
        data['HML'] = ff3_data['HML'][j]
        data['RF'] = ff3_data['RF'][j]
        data['y'] = data['RET']-data['RF']
        data = data.astype('float64')
    
        output = portfolio(data, sorted_var, split_num)
        data_df = pd.concat([data_df, output[i]])

    reg = smf.ols('y ~ Mkt_RF + SMB + HML', data = data_df).fit(cov_type='HAC', cov_kwds={'maxlags':1})
    ff3_alpha = pd.concat([ff3_alpha, pd.DataFrame(reg.params).T])
ff3_alpha.index = list(range(1, 1 + split_num))

i = 0
portfolio_1 = pd.DataFrame()
for j in range(len(vol_temp_df)):
    data = vol_temp_df.iloc[j,1].iloc[:,1:].copy()
    data['Mkt_RF'] = ff3_data['Mkt-RF'][j]
    data['SMB'] = ff3_data['SMB'][j]
    data['HML'] = ff3_data['HML'][j]
    data['RF'] = ff3_data['RF'][j]
    data['y'] = data['RET']-data['RF']
    data = data.astype('float64')
    
    output = portfolio(data, sorted_var, split_num)
    portfolio_1 = pd.concat([portfolio_1, output[i]])

i = 4
portfolio_5 = pd.DataFrame()
for j in range(len(vol_temp_df)):
    data = vol_temp_df.iloc[j,1].iloc[:,1:].copy()
    data['Mkt_RF'] = ff3_data['Mkt-RF'][j]
    data['SMB'] = ff3_data['SMB'][j]
    data['HML'] = ff3_data['HML'][j]
    data['RF'] = ff3_data['RF'][j]
    data['y'] = data['RET']-data['RF']
    data = data.astype('float64')
    
    output = portfolio(data, sorted_var, split_num)
    portfolio_5 = pd.concat([portfolio_5, output[i]])

port_1_alpha = pd.DataFrame()
for i in range(len(vol_temp_df)):
    time = vol_temp_df[0][i]
    data = portfolio_1.loc[time,:].copy()
    reg = smf.ols('y ~ Mkt_RF + SMB + HML', data = data).fit(cov_type='HAC', cov_kwds={'maxlags':1})
    port_1_alpha.loc[i, 'alpha'] = reg.params[0]
    
port_5_alpha = pd.DataFrame()
for i in range(len(vol_temp_df)):
    time = vol_temp_df[0][i]
    data = portfolio_5.loc[time,:].copy()
    reg = smf.ols('y ~ Mkt_RF + SMB + HML', data = data).fit(cov_type='HAC', cov_kwds={'maxlags':1})
    port_5_alpha.loc[i, 'alpha'] = reg.params[0]


import scipy.stats as stats

stats.ttest_ind(port_5_alpha, port_1_alpha)
stats.ttest_ind(portfolio_5['RET'], portfolio_1['RET'])


#%%


# Fama-MacBeth Regression
from linearmodels import FamaMacBeth

temp = vol_temp.copy().reset_index()
temp = temp.set_index(['PERMNO', 'date'])
temp = temp.astype('float64')

fm = FamaMacBeth.from_formula('RET ~ 1 + rivolspread', data=temp)
res = fm.fit(cov_type='kernel', debiased=False, bandwidth=4)
print(res.summary)
res.params
res.tstats
