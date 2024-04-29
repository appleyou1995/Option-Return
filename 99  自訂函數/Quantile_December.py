import pandas    as pd
from statistics  import quantiles


# %%

def Quantile_December(dataset, sorted_var, split_num):    
    
    # December data
    December_only = dataset[dataset.MM == 12].sort_values('YYYY')
    December_only_group_year = pd.DataFrame(December_only.groupby('YYYY'))
    
    All_dataset_group_year = pd.DataFrame(dataset.groupby('YYYY'))
    
    Group_Label = pd.DataFrame()
    
    for y in range(len(December_only_group_year)):
        
        data_key = December_only_group_year.iloc[y,1].copy()
        data_all = All_dataset_group_year.iloc[y+1,1].copy()
    
        quantile_by = data_key[sorted_var]
        quantile_list = quantiles(quantile_by, n = split_num)  # 把第 y 年 December 所有公司 firm size 的 Quantile 算出來
        
        
        # 把第 y 年 December 所有公司 firm size 的 Quantile，變成區域變數
        for q in range(1, split_num):            
            locals()['quantile_' + str(q)] = quantile_list[q - 1]            
            
            
        # 把第 y+1 年所有的公司，依照第 y 年 December 的 firm size 的 Quantile 進行分組
        for q in range(1, split_num + 1):
            # print(q)
            
            if q == 1:
                temp = data_all[data_all[sorted_var] < locals()['quantile_'+str(q)]]
                temp['Group'] = '1'
                Group_Label = Group_Label.append(temp)
                
            elif q == split_num:
                temp = data_all[data_all[sorted_var] >= locals()['quantile_'+str(q-1)]]
                temp['Group'] = str(split_num)
                Group_Label = Group_Label.append(temp)
                
            else:
                temp = data_all[data_all[sorted_var].between(locals()['quantile_'+str(q-1)], locals()['quantile_'+str(q)], 'left')]
                temp['Group'] = str(q)
                Group_Label = Group_Label.append(temp)
    
    return Group_Label