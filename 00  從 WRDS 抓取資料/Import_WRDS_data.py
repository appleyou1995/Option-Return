from sqlalchemy import text
from datetime   import datetime, timedelta

import pandas          as pd
import os
import wrds


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


# %%

option_data_all = pd.read_csv(os.path.join(Path_Input, 'SAS - Output', 'Y_SHROUT_Stock.csv'))
option_data_all['date'] = pd.to_datetime(option_data_all['date'])

option_data_jan_1996 = option_data_all[
    (option_data_all['date'].dt.year == 1996) & (option_data_all['date'].dt.month == 1)
]

option_data_jan_2000 = option_data_all[
    (option_data_all['date'].dt.year == 2000) & (option_data_all['date'].dt.month == 1)
]


# %%  Connect to WRDS & Get the properties of database [ Option ]

conn = wrds.Connection(wrds_username='irisyu')

libraries          = conn.list_libraries()
tables_optionm_all = conn.list_tables(library='optionm_all')
col_headers_opprcd = conn.describe_table(library='optionm_all', table='opprcd1996')
col_headers_secprd = conn.describe_table(library='optionm_all', table='secprd1996')
col_headers_opinfd = conn.describe_table(library='optionm_all', table='opinfd')


# %%  [ opinfd ] exercise_style

query_opinfd = text("""
                    SELECT
                        secid, div_convention, exercise_style, am_set_flag
                    FROM
                        optionm_all.opinfd
                    LIMIT
                        500
                    """)

df_opinfd = conn.raw_sql(query_opinfd)


# %%  Query [ Option with Filtering ]

query_option = text("""
                    SELECT 
                        o.secid, n.cusip, mse.permno, mse.shrcd, o.optionid, 
                        o.date, o.exdate, o.cp_flag, msf.prc, o.strike_price / 1000 AS strike_price, 
                        o.best_bid, o.best_offer, 
                        msf.shrout AS size_stock, o.open_interest AS size_option
                    FROM 
                        optionm_all.opprcd1996 o
                    JOIN
                        optionm_all.optionmnames n
                    ON 
                        o.optionid = n.optionid
                    JOIN
                        (SELECT DISTINCT cusip, permno, shrcd
                         FROM crsp_a_stock.mse
                         WHERE shrcd = 10 OR shrcd = 11) mse
                    ON 
                        n.cusip = mse.cusip
                    JOIN
                        (SELECT cusip, date, prc, shrout
                         FROM crsp_a_stock.msf) msf
                    ON 
                        n.cusip = msf.cusip AND o.date = msf.date
                    JOIN
                        (SELECT secid, exercise_style
                         FROM optionm_all.opinfd) ae
                    ON 
                        ae.secid = o.secid
                    WHERE            
                        o.volume > 0
                    AND
                        o.best_bid > 0
                    AND
                        o.best_bid < o.best_offer
                    AND
                        (o.best_bid + o.best_offer) / 2 > 1/8
                    AND
                        (msf.prc / o.strike_price * 1000) > 0.8
                    AND
                        (msf.prc / o.strike_price * 1000) < 1.2
                    AND
                        o.impl_volatility IS NOT NULL
                    AND
                        o.exdate - o.date >= 30
                    AND
                        ae.exercise_style = 'A'
                    AND
                        o.date BETWEEN '1996-01-01' AND '1996-01-31'
                    ORDER BY
                        o.date, mse.permno
                    """)

df_jan_1996_raw = conn.raw_sql(query_option)


# %%  

start_date = datetime(1996, 1, 1)
end_date   = datetime(1997, 12, 31)

current_date = start_date
dfs = []

while current_date <= end_date:
    year  = current_date.year
    month = current_date.month
    month_end_date = (current_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    print(f"Processing period: {year}-{month}")
    
    query_option = text(f"""
                        SELECT 
                            o.secid, n.cusip, mse.permno, mse.shrcd, o.optionid, 
                            o.date, o.exdate, o.cp_flag, msf.prc, o.strike_price / 1000 AS strike_price, 
                            o.best_bid, o.best_offer, 
                            msf.shrout AS size_stock, o.open_interest AS size_option
                        FROM 
                            optionm_all.opprcd{year} o
                        JOIN
                            optionm_all.optionmnames n
                        ON 
                            o.optionid = n.optionid
                        JOIN
                            (SELECT DISTINCT cusip, permno, shrcd
                             FROM crsp_a_stock.mse
                             WHERE shrcd = 10 OR shrcd = 11) mse
                        ON 
                            n.cusip = mse.cusip
                        JOIN
                            (SELECT cusip, date, prc, shrout
                             FROM crsp_a_stock.msf) msf
                        ON 
                            n.cusip = msf.cusip AND o.date = msf.date
                        JOIN
                            (SELECT secid, exercise_style
                             FROM optionm_all.opinfd) ae
                        ON 
                            ae.secid = o.secid
                        WHERE            
                            o.volume > 0
                        AND
                            o.best_bid > 0
                        AND
                            o.best_bid < o.best_offer
                        AND
                            (o.best_bid + o.best_offer) / 2 > 1/8
                        AND
                            (msf.prc / o.strike_price * 1000) > 0.8
                        AND
                            (msf.prc / o.strike_price * 1000) < 1.2
                        AND
                            o.impl_volatility IS NOT NULL
                        AND
                            o.exdate - o.date >= 30
                        AND
                            o.exdate - o.date <= 90
                        AND
                            ae.exercise_style = 'A'
                        AND
                            o.date BETWEEN '{current_date.strftime('%Y-%m-%d')}' AND '{month_end_date.strftime('%Y-%m-%d')}'
                        ORDER BY
                            o.date, mse.permno
                        """)

    df = conn.raw_sql(query_option)
    dfs.append(df)

    current_date = (current_date + timedelta(days=32)).replace(day=1)


df_all = pd.concat(dfs, ignore_index=True)


# %%  mse vs. msf

# [ mse ] everyday
query_mse = text("""
                 SELECT
                     date, cusip, permno, shrcd, shrout
                 FROM
                     crsp_a_stock.mse
                 WHERE            
                     date BETWEEN '2000-01-01' AND '2000-01-31'
                 ORDER BY 
                     date, permno                     
                 """)

df_mse = conn.raw_sql(query_mse)


# [ msf ] the last day of month
query_msf = text("""
                 SELECT
                     date, cusip, permno, prc, shrout
                 FROM
                     crsp_a_stock.msf
                 WHERE            
                     date BETWEEN '2000-01-01' AND '2000-01-31'
                 ORDER BY 
                     date, permno                     
                 """)

df_msf = conn.raw_sql(query_msf)


# %%  Disconnect

conn.close()


# %%  Query [ Option ]

query_option = text("""
                    SELECT 
                        optionid, secid, date, exdate, cp_flag, strike_price,
                        best_bid, best_offer, open_interest, volume, impl_volatility, 
                        delta, gamma, theta, vega, contract_size
                    FROM 
                        optionm_all.opprcd2000
                    WHERE            
                        volume > 0
                    AND
                        best_bid > 0
                    AND
                        best_bid < best_offer
                    AND
                        (best_bid + best_offer)/2 > 1/8
                    AND
                        impl_volatility IS NOT NULL
                    AND
                        date BETWEEN '2000-01-01' AND '2000-12-31'
                    LIMIT
                        500
                    """)


# %%  Setting query & Load data [ Common Stock ]

conn = wrds.Connection(wrds_username='irisyu')

libraries   = conn.list_libraries()
tables_crsp = conn.list_tables(library='crsp_a_stock')

col_headers_stock_mse = conn.describe_table(library='crsp_a_stock', table='mse')
col_headers_stock_msf = conn.describe_table(library='crsp_a_stock', table='msf')


# %%  Query [ Common Stock ]

query_common_stock = text("""
                          SELECT DISTINCT
                              cusip, permno, shrcd, siccd, paydt
                          FROM 
                              crsp_a_stock.mse
                          WHERE            
                              shrcd = 10 OR shrcd = 11
                          ORDER BY 
                              permno
                          """)
                    
df_common_stock = conn.raw_sql(query_common_stock)


# %%  Query [ paydt check ]

query_paydt = text("""
                    SELECT
                        date, cusip, permno, shrcd, siccd, paydt
                    FROM 
                        crsp_a_stock.mse
                    WHERE            
                        (shrcd = 10 OR shrcd = 11)
                    AND
                        date BETWEEN '1990-01-01' AND '2023-12-31'
                    AND
                        paydt IS NOT NULL
                    ORDER BY 
                        permno
                    """)
                    
df_paydt = conn.raw_sql(query_paydt)


# %%  Connect to WRDS & Get the properties of database [ Mapping Table ] [ not used ]

conn = wrds.Connection(wrds_username='irisyu')

libraries                = conn.list_libraries()
tables_optionm_all       = conn.list_tables(library='optionm_all')
col_headers_optionmnames = conn.describe_table(library='optionm_all', table='optionmnames')

query_mapping = text("""
                     SELECT DISTINCT
                         o.secid, o.optionid, o.cusip, c.shrcd
                     FROM 
                         optionm_all.optionmnames o
                     JOIN
                         (SELECT DISTINCT cusip, shrcd 
                          FROM crsp_a_stock.mse 
                          WHERE shrcd = 10 OR shrcd = 11) c
                     ON 
                         o.cusip = c.cusip
                     LIMIT
                         500
                     """)

df_mapping = conn.raw_sql(query_mapping)


# %%





query_option = text("""
                    SELECT 
                        o.optionid, o.secid, n.cusip, mse.permno, mse.shrcd, msf.prc, msf.shrout, 
                        o.date, o.exdate, o.cp_flag, o.strike_price, o.best_bid, o.best_offer
                    FROM 
                        optionm_all.opprcd1996 o
                    JOIN
                        optionm_all.optionmnames n
                    ON 
                        o.optionid = n.optionid
                    JOIN
                        (SELECT DISTINCT cusip, shrcd, permno
                         FROM crsp_a_stock.mse) mse
                    ON 
                        n.cusip = mse.cusip
                    JOIN
                        (SELECT cusip, date, prc, shrout
                         FROM crsp_a_stock.msf) f
                    ON 
                        mse.cusip = msf.cusip AND mse.date = msf.date
                    WHERE            
                        o.volume > 0
                    AND
                        o.date BETWEEN '1996-01-01' AND '1996-12-31'
                    ORDER BY
                        o.date, mse.permno
                    """)