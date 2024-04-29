import pandas          as pd
import numpy           as np
import statsmodels.api as sm
import sys


# %%  Import T-statistics function

sys.path.append('D:/Google/我的雲端硬碟/學術｜研究與論文/論文著作/Option Return/99  自訂函數')

from T_statistics import T_statistics


# %%  Regression


def regression_table(dataset, exog, split_num):
    
    output = pd.DataFrame()
    dataset_group = pd.DataFrame(dataset.groupby('YYYYMM'))
    dataset_group.index = dataset_group[0]
    dataset_group = dataset_group[0]
    
    for q in range(1, split_num + 1):
        
        data = dataset[dataset.Group == str(q)]
        YYYYMM_group = pd.DataFrame(data.groupby('YYYYMM'))
        YYYYMM_group.index = YYYYMM_group[0]
        YYYYMM_group = pd.concat([dataset_group, YYYYMM_group], axis=1)
        YYYYMM_group = YYYYMM_group.iloc[:,[0,2]]
        
        
        temp = pd.DataFrame(columns = ['Intercept_Q' + str(q), 'Q' + str(q)], index = range(len(dataset_group) + 3))
        
        for y in range(len(YYYYMM_group) + 1):
        # for y in range(140,146):
            
            if y < len(YYYYMM_group):
                # reg_data = YYYYMM_group.iloc[y,1].copy()
                # X = sm.add_constant(reg_data[exog])
                # result = sm.OLS(reg_data['Option_Return'], X).fit(cov_type='HAC', cov_kwds={'maxlags':1})
                # print(str(q)+'-'+str(y))
                # temp.iloc[y, 0] = result.params[0]
                # temp.iloc[y, 1] = result.params[1]
                
                try:
                    # print(str(q)+'-'+str(y))
                    reg_data = YYYYMM_group.iloc[y,1].copy()
                    X = sm.add_constant(reg_data[exog])
                    result = sm.OLS(reg_data['Option_Return'], X).fit(cov_type='HAC', cov_kwds={'maxlags':1})
                    temp.iloc[y, 0] = result.params[0]
                    temp.iloc[y, 1] = result.params[1]
                    
                except:
                    # print('發生錯誤')
                    temp.iloc[y, 0] = np.NaN
                    temp.iloc[y, 1] = np.NaN
                    pass
                
            
            else:
                temp.iloc[len(dataset_group) + 1, 0] = temp.iloc[:len(dataset_group), 0].mean()
                temp.iloc[len(dataset_group) + 1, 1] = temp.iloc[:len(dataset_group), 1].mean()
                
                temp.iloc[len(dataset_group) + 2, 0] = T_statistics(temp.iloc[:len(YYYYMM_group), 0].dropna().astype(float))
                temp.iloc[len(dataset_group) + 2, 1] = T_statistics(temp.iloc[:len(YYYYMM_group), 1].dropna().astype(float))
                
    
        if q == 1:
            output = temp
            
        else:
            output = pd.concat([output, temp], axis = 1)
        
        
    aa = dataset_group.apply(str).tolist()
    aa.append('')
    aa.append('mean')
    aa.append('t-value')
    output.index = aa
    
    
    Q10_minus_Q1 = pd.DataFrame(columns = ['Q10 - Q1'], index = output.index)
    Q10_minus_Q1['Q10 - Q1'][:len(dataset_group)] = output['Q10'][:len(dataset_group)] - output['Q1'][:len(dataset_group)]
    
    Q10_minus_Q1['Q10 - Q1'][len(dataset_group) + 1] = Q10_minus_Q1['Q10 - Q1'][:len(dataset_group)].mean()
    Q10_minus_Q1['Q10 - Q1'][len(dataset_group) + 2] = T_statistics(Q10_minus_Q1['Q10 - Q1'][:len(YYYYMM_group)].dropna().astype(float))
    
    output = pd.concat([output, Q10_minus_Q1], axis = 1)
    
    return output