from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import urllib.request
from io import StringIO

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
    while True:
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

            return df

        except:
            pass


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
        else:
            cols.append(f'{col[0]}, {col[1]}')

    df = df.set_axis(cols, axis='columns')

    # Get rid of those annoying rows
    indicies = df.loc[df['Rk'] == 'Rk'].index
    df.drop(indicies, inplace=True)
    return df


def get_data_to_csv(df: pd.DataFrame) -> None:
    """
    Given a cleaned FBRef dataframe, create a csv for it
    :param df: cleaned df
    :return: Creates the file, returns nothing
    """
    # TODO figure out file name format.
    file_name = 'Test_csv'
    df.to_csv(f'{file_name}.csv', index=False)
    print('file written')
    print(df.head())


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
        d = d.drop(columns=['Rk', 'Born', 'Matches'])  # remove unnecessary columns then maps positions.
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
    dflst = dfs[year]
    final = dflst[0].copy().drop(columns=['Rk', 'Matches'])  # initialize running total df
    for df in dflst[1:]:  # iterate over the rest of the dfs
        # Concatenate the current df to the right side of the running df
        cleaned = df.iloc[:, 9:]
        cleaned = cleaned.drop(columns=['Matches'])
        final = pd.concat([final, cleaned], axis=1)
    print(f'Completed {year} compilation, gonna write.')
    finals.append(final)
    # big table complete, just write to file.
    # DONE final.to_csv(f'../data/by_year/{year}-data.csv')

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
