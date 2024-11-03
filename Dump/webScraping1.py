import traceback

from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
from io import StringIO
import os

pd.options.display.max_columns = None
pd.set_option('display.width', 1000)

years = ['2017-2018', '2018-2019', '2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024']
cats = ['stats', 'shooting', 'passing', 'passing_types', 'gca', 'defense', 'possession']  # , 'playingtime', 'misc']
cat_d = {'stats': 'stats_standard',
         'misc': 'stats_misc',
         'playingtime': 'stats_playing_time',
         'possession': 'stats_possession',
         'defense': 'stats_defense',
         'gca': 'stats_gca',
         'passing_types': 'stats_passing_types',
         'passing': 'stats_passing',
         'shooting': 'stats_shooting'}


def make_url(year: str, cat: str) -> str:
    return f'https://fbref.com/en/comps/Big5/{year}/{cat}/players/2017-2018-Big-5-European-Leagues-Stats'


def get_raw_df(year: str, cat: str) -> pd.DataFrame:
    """
    Given a year and a date, create a url and fetch the date from there, returning the dataframe AS IS. See next
    function for cleaning.
    :param year: season data. Has to come from global years list above.
    :param cat: Category. should be a key from the global dictionary above.
    :return: dirty dataframe.
    """
    needs_repeat = True
    while needs_repeat:
        try:
            url = make_url(year, cat)
            response = requests.get(url)
            print('getting response')
            response.raise_for_status()
            print('response got, beautiful souping')

            soup = bs(response.content, 'html.parser')
            print('beautiful souped, finding table')
            table = soup.find_all("table", {'id': cat_d[cat]})
            print('table found, reading to html')
            df = pd.read_html(StringIO(str(table)))[0]

            df = pd.concat([pd.DataFrame([year] * df.shape[0], columns=[('Unnamed', 'Season')]), df], axis=1)

            return df

        except Exception as e:
            print('There was a problem...')
            traceback.print_exc()


def consolidate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function takes in a dataframe constructed from the data from FBref and combines the multiple headers onto one,
    then gets rid of the repeating headers down the line. NOTE!!! THIS FUNCTION DOES NOT DO THIS PROCESS IN PLACE
    :param df: dirty dataframe
    :return: cleaned dataframe
    """
    # Consolidate the column names into one header row
    cols = []
    for col in df.columns:
        if col[0][:7] == 'Unnamed':
            cols.append(col[1])
        elif col[1] == 'Season':
            cols.append('Season')
        else:
            cols.append(f'{col[0]}, {col[1]}')

    df = df.set_axis(cols, axis='columns')
    df = df.drop(df.loc[(df['Nation'].isna()) | (df['Born'].isna())].index)

    # Get rid of those annoying rows
    indicies = df.loc[df['Rk'] == 'Rk'].index
    df.drop(indicies, inplace=True)
    return df


"""
{'GK': 0, 'DF': 1, 'DF,MF': 2,
 'MF,DF': 3, 'MF': 4, 'MF,FW': 5,
 'FW,MF': 6, 'FW': 7,
 'FW,DF': 5.5, 'DF,FW': 1.5}
"""

u_cols = {}
raw_cols = set()

dfs = {}  # year: [df_by_cat]
counter = 0
for cat in cats:
    for year in years:
        counter += 1
        print(counter, year, cat)
        d = consolidate_columns(get_raw_df(year, cat))
        d = d.drop(columns=['Rk', 'Matches'])  # remove unnecessary columns then maps positions.
        d['Pos'] = d['Pos'].map({'GK': 0, 'DF': 1, 'DF,MF': 2,
                                 'MF,DF': 3, 'MF': 4, 'MF,FW': 5,
                                 'FW,MF': 6, 'FW': 7,
                                 'FW,DF': 5.5, 'DF,FW': 1.5})
        if year in dfs.keys():
            dfs[year].append(d)
        else:
            dfs[year] = [d]



# Want to create a df for each year (combining all of the cats) then writing to a file
finals = []
for year in years:
    dflst = dfs[year]  # a list of dataframes for this year
    final = dflst[0].copy()  # initialize running total df

    for df in dflst[1:]:  # iterate over the rest of the dfs by category
        # Concatenate the current df to the right side of the running df
        cleaned = df.iloc[:, 9:].copy()
        final = pd.concat([final, cleaned], axis=1)
    # Data gathered, now remove NAN players, prepend playerid column and season start year

    pids = pd.DataFrame(final.loc[:, 'Player'] +
                        '-' + final.loc[:, 'Nation'].str.slice(-3) +
                        '-' + final.loc[:, 'Born'].astype(int).astype(str), columns=['p_id'])
    final = pd.concat([pids, final], axis=1)
    print(f'Completed {year} compilation, gonna write.')
    finals.append(final)
    # big table complete, just write to file.
    final.to_csv(f'../data/by_year/{year}-data.csv')

# consolidate all of the by_year dfs into one massive one
EEAAO = finals[0].copy()
for f in finals[1:]:
    EEAAO = pd.concat([EEAAO, f], axis=0)


EEAAO.to_csv('../data/eeaao.csv')


def fetch(struct: dict, year: str, cat: str) -> pd.DataFrame:
    dflst = struct[year]
    i = cats.index(cat)
    return dflst[i]


def get_player(name: str) -> pd.DataFrame:
    tempdf = dfs[years[0]][1].loc[dfs[years[0]][1]['Player'] == name]

    for year in years[1:]:
        df1 = dfs[year][1].loc[dfs[year][1]['Player'] == name]
        tempdf = pd.concat([tempdf, df1], axis=0)
    return tempdf


"""
Instances of NaNs
2701   Anthony Walongwa    NaN  1.0       Nantes     fr Ligue 1   23               1                   1               90              1.0               0               0               0                0              0                 0                0                0         0.0           0.0          0.0               0.0                0                1                0               0.00               0.00               0.00                0.00                  0.00              0.00               0.00                  0.00                0.00                    0.00            0           0            0           NaN           0.00            0.00           NaN            NaN           NaN           0           0              0         0.0           0.0              NaN           0.0              0.0        13        19       68.4           276           131         3         3      100.0          9         10        90.0        1        6      16.7   0  0.0         0.0   
2798  Christian Rutjens    NaN  NaN    Benevento     it Serie A  NaN               1                   0                1              0.0               0               0               0                0              0                 0                0                0         NaN           NaN          NaN               NaN              NaN              NaN              NaN               0.00               0.00               0.00                0.00                  0.00               NaN                NaN                   NaN                 NaN                     NaN            0         NaN            0           NaN            NaN            0.00           NaN            NaN           NaN         NaN           0              0         NaN           NaN              NaN           NaN              NaN       NaN       NaN        NaN           NaN           NaN       NaN       NaN        NaN        NaN        NaN         NaN      NaN      NaN       NaN   0  NaN         NaN   
568     Alessio da Cruz    NaN  6.0        Parma     it Serie A   21               3                   1              144              1.6               0               0               0                0              0                 0                0                0         0.1           0.1          0.0               0.1                1                2                5               0.00               0.00               0.00                0.00                  0.00              0.03               0.00                  0.03                0.03                    0.03            0           1            0           0.0           0.62            0.00          0.00            NaN          13.0           0           0              0         0.1           0.1             0.05          -0.1             -0.1        21        27       77.8           299            31        11        13       84.6          8          9        88.9        1        2      50.0   0  0.0         0.0   
1724  Hakim El Mokeddem    NaN  6.0     Toulouse     fr Ligue 1   19               2                   0               25              0.3               0               0               0                0              0                 0                0                0         0.0           0.0          0.3               0.3                0                1                3               0.00               0.00               0.00                0.00                  0.00              0.00               1.09                  1.09                0.00                    1.09            0           0            0           NaN           0.00            0.00           NaN            NaN           NaN           0           0              0         0.0           0.0              NaN           0.0              0.0        12        14       85.7           163            32         7         7      100.0          4          5        80.0        0        1       0.0   0  0.3         0.1   
2664   Anthony Walongwa    NaN  1.0       Nantes     fr Ligue 1   24               1                   1               90              1.0               0               0               0                0              0                 0                0                0         0.1           0.1          0.0               0.1                0                3                0               0.00               0.00               0.00                0.00                  0.00              0.14               0.00                  0.14                0.14                    0.14            0           1            0           0.0           1.00            0.00          0.00            NaN           7.8           0           0              0         0.1           0.1             0.14          -0.1             -0.1        34        37       91.9           648           268         8        10       80.0         25         26        96.2        1        1     100.0   0  0.0         0.0   
1076        Sinan Gümüş    NaN  6.0        Genoa     it Serie A   25               3                   1               96              1.1               0               0               0                0              0                 0                0                0         0.1           0.1          0.0               0.1                5                3                3               0.00               0.00               0.00                0.00                  0.00              0.13               0.00                  0.13                0.13                    0.13            0           3            2          66.7           2.81            1.87          0.00           0.00          18.0           0           0              0         0.1           0.1             0.05          -0.1             -0.1        24        29       82.8           274            18        19        21       90.5          2          3        66.7        1        1     100.0   0  0.0         0.0   
1337     Atakan Karazor    NaN  2.0    Stuttgart  de Bundesliga   23              19                  10             1037             11.5               0               0               0                0              0                 0                3                0         0.1           0.1          0.1               0.2                4               33                6               0.00               0.00               0.00                0.00                  0.00              0.01               0.01                  0.02                0.01                    0.02            0           3            1          33.3           0.26            0.09          0.00           0.00          21.7           0           0              0         0.1           0.1             0.05          -0.1             -0.1       605       703       86.1          9874          3721       281       315       89.2        276        303        91.1       30       55      54.5   0  0.1         0.2   
1395     Atakan Karazor    NaN  4.0    Stuttgart  de Bundesliga   24              24                  23             1898             21.1               0               1               1                0              0                 0                9                1         0.3           0.3          1.2               1.5               11               82               24               0.00               0.05               0.05                0.00                  0.05              0.01               0.06                  0.07                0.01                    0.07            0           9            2          22.2           0.43            0.09          0.00           0.00          26.6           0           0              0         0.3           0.3             0.03          -0.3             -0.3       830      1016       81.7         13376          4140       400       465       86.0        344        393        87.5       51       88      58.0   1  1.2         0.9   
1411     Atakan Karazor    NaN  4.0    Stuttgart  de Bundesliga   25              29                  22             1962             21.8               0               1               1                0              0                 0               10                0         0.3           0.3          0.6               0.9                5               79               12               0.00               0.05               0.05                0.00                  0.05              0.01               0.03                  0.04                0.01                    0.04            0           6            0           0.0           0.28            0.00          0.00            NaN          20.9           0           0              0         0.3           0.3             0.05          -0.3             -0.3       945      1116       84.7         16475          4393       407       468       87.0        444        498        89.2       75      105      71.4   1  0.6         1.2   
1348     Atakan Karazor    NaN  4.0    Stuttgart  de Bundesliga   26              33                  31             2623             29.1               0               4               4                0              0                 0                9                0         1.0           1.0          2.6               3.6               24              142               31               0.00               0.14               0.14                0.00                  0.14              0.04               0.09                  0.13                0.03                    0.12            0          19            2          10.5           0.65            0.07          0.00           0.00          21.8           0           0              0         1.0           1.0             0.05          -1.0             -1.0      1698      1900       89.4         24791          6910       946      1027       92.1        637        684        93.1       55       75      73.3   4  2.6         2.5   
1447  Mahmut Kücüksahin    NaN  4.0     Augsburg  de Bundesliga   19               1                   0                1              0.0               0               0               0                0              0                 0                0                0         0.0           0.0          0.0               0.0                0                0                0               0.00               0.00               0.00                0.00                  0.00              0.00               0.00                  0.00                0.00                    0.00            0           0            0           NaN           0.00            0.00           NaN            NaN           NaN           0           0              0         0.0           0.0              NaN           0.0              0.0         4         4      100.0            59            17         3         3      100.0          1          1       100.0        0        0       NaN   0  0.0         0.0   
2153   Marco Pellegrino    NaN  1.0  Salernitana     it Serie A  NaN              10                   5              545              6.1               0               0               0                0              0                 0                1                0         0.0           0.0          0.0               0.1                0                7                1               0.00               0.00               0.00                0.00                  0.00              0.01               0.01                  0.01                0.01                    0.01            0           2            0           0.0           0.33            0.00          0.00            NaN          11.9           0           0              0         0.0           0.0             0.02           0.0              0.0       211       256       82.4          3754          1365        83        94       88.3        112        126        88.9       16       33      48.5   0  0.0         0.0   
2154   Marco Pellegrino
"""

