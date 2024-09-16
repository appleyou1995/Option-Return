import pandas          as pd
import os

from scipy.stats import mstats


# %%  論文資料夾路徑

Path_PaperFolder = '我的雲端硬碟/學術｜研究與論文/論文著作/Option Return'


# %%  Win 資料夾路徑

Path_Win = 'D:/Google/'
Path_dir = os.path.join(Path_Win, Path_PaperFolder)


# %%  Mac 資料夾路徑

# Path_Mac = '/Users/irisyu/Library/CloudStorage/GoogleDrive-jouping.yu@gmail.com/'
# Path_dir = os.path.join(Path_Mac, Path_PaperFolder)


# %%  Input and Output Path

Path_Input  = os.path.join(Path_dir, 'Data/')
Path_Output = os.path.join(Path_dir, 'Data/控制變數/')


# %%  Control Variables

CV = pd.read_csv(os.path.join(Path_Input, '控制變數', 'CV_merge result.csv'))

CV['date'] = pd.to_datetime(CV['date'])
CV['YYYYMM'] = CV['date'].dt.strftime('%Y%m').astype(int)

for col in CV.columns: print(col)
Control_Variable_List = pd.Index(CV.columns[13:35].tolist())


# %%  Winsorize

def winsorize_series(series):
    return mstats.winsorize(series, limits=[0.005, 0.005])

CV_winsorized = CV.copy()

for var in Control_Variable_List:
    CV_winsorized[var] = CV.groupby(CV['date'].dt.to_period('M'))[var].transform(winsorize_series)


# %%  Build the dataframe of equity characteristics

Characteristics_All_var = CV_winsorized.iloc[:, :13]

Characteristics_All_var['CFV_1y']        = CV_winsorized['CFV_1y']
Characteristics_All_var['CFV_2y']        = CV_winsorized['CFV_2y']
Characteristics_All_var['CFV_3y']        = CV_winsorized['CFV_3y']
Characteristics_All_var['CFV_4y']        = CV_winsorized['CFV_4y']
Characteristics_All_var['CFV_5y']        = CV_winsorized['CFV_5y']
Characteristics_All_var['CH']            = CV_winsorized['cash']
# Characteristics_All_var['DISP']          = CV_winsorized['']
# Characteristics_All_var['ISSUE_1Y']      = CV_winsorized['']
# Characteristics_All_var['ISSUE_5Y']      = CV_winsorized['']
# Characteristics_All_var['PM']            = CV_winsorized['']
Characteristics_All_var['ln(PRICE)']     = CV_winsorized['logPrice']
Characteristics_All_var['PROFIT']        = CV_winsorized['profitable']
Characteristics_All_var['TEF']           = CV_winsorized['tef']
Characteristics_All_var['ZS']            = CV_winsorized['Zscore']
# Characteristics_All_var['VOL_deviation'] = CV_winsorized['']
# Characteristics_All_var['IVOL']          = CV_winsorized['']
# Characteristics_All_var['ln(Amihud)']    = CV_winsorized['']
Characteristics_All_var['ln(ME)']        = CV_winsorized['logME']
Characteristics_All_var['ln(BM)']        = CV_winsorized['BM']
Characteristics_All_var['RET(-1,0)']     = CV_winsorized['ret_1_0']
Characteristics_All_var['RET(-12,-2)']   = CV_winsorized['ret_12_2']


Characteristics_Sub_var = CV_winsorized.iloc[:, :13]

Characteristics_Sub_var['CFV_1y']        = CV_winsorized['CFV_1y']
Characteristics_Sub_var['CFV_2y']        = CV_winsorized['CFV_2y']
Characteristics_Sub_var['CFV_3y']        = CV_winsorized['CFV_3y']
Characteristics_Sub_var['CFV_4y']        = CV_winsorized['CFV_4y']
Characteristics_Sub_var['CFV_5y']        = CV_winsorized['CFV_5y']
Characteristics_Sub_var['CH']            = CV_winsorized['cash']
# Characteristics_Sub_var['DISP']          = CV_winsorized['']
# Characteristics_Sub_var['ISSUE_1Y']      = CV_winsorized['']
# Characteristics_Sub_var['ISSUE_5Y']      = CV_winsorized['']
Characteristics_Sub_var['TEF']           = CV_winsorized['tef']
# Characteristics_Sub_var['-PM']           = CV_winsorized['']
Characteristics_Sub_var['-ln(PRICE)']    = - CV_winsorized['logPrice']
Characteristics_Sub_var['-PROFIT']       = - CV_winsorized['profitable']
Characteristics_Sub_var['-ZS']           = - CV_winsorized['Zscore']


# %%  Output dataframe

Characteristics_All_var.to_csv(os.path.join(Path_Output, 'Characteristics_All_var.csv'), index=False)
Characteristics_Sub_var.to_csv(os.path.join(Path_Output, 'Characteristics_Sub_var.csv'), index=False)
