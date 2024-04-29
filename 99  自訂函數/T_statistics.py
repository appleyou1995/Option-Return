import scipy.stats     as stats


#%%

def T_statistics(data):
    
    T_statistics = stats.ttest_1samp(data, 0)[0]    
    T_statistics = '('+str("{:10.2f}".format(T_statistics))+')'
    
    return T_statistics