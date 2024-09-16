import pandas          as pd
import os


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
Path_Output = os.path.join(Path_dir, 'Code/04  Equity characteristics/')


# %%  Control Variables

CV = pd.read_csv(os.path.join(Path_Input, '控制變數', 'Characteristics_All_var.csv'))
CV['date'] = pd.to_datetime(CV['date'])

for col in CV.columns: print(col)

Control_Variable_List = pd.Index(CV.columns[13:27].tolist())
CV_subset = CV[Control_Variable_List]

CV_subset['RET(-1,0)'] = pd.to_numeric(CV_subset['RET(-1,0)'], errors='coerce')


# %%  Summary statistics

stats = CV_subset.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).T

stats['Obs.'] = CV_subset.count()
stats = stats[['Obs.', 'mean', 'std', '10%', '25%', '50%', '75%', '90%']]

stats['Obs.'] = stats['Obs.'].apply(lambda x: '{:,.0f}'.format(x))
stats.loc[:, stats.columns != 'Obs.'] = stats.loc[:, stats.columns != 'Obs.'].applymap(lambda x: '{:,.2f}'.format(x))


# %%  Output table

markdown_stats = stats.to_markdown()

with open(os.path.join(Path_Output, 'Table_1_Summary_statistics_of_CV.md'), 'w') as file:
    file.write(markdown_stats)

