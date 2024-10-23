from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import urllib.request
from io import StringIO
pd.options.display.max_columns = None

url = "https://fbref.com/en/comps/Big5/2017-2018/stats/players/2017-2018-Big-5-European-Leagues-Stats"
response = requests.get(url)
print('getting response')
response.raise_for_status()
print('response got, beautiful souping')

soup = bs(response.content, 'html.parser')
print('beautiful souped, finding table')
table = soup.find_all("table", {'id': 'stats_standard'})
print('table found, reading to html')
df = pd.read_html(StringIO(str(table)))[0]

# Consolidate the column names into one header row
cols = []
for col in df.columns:
    if col[0][:7] == 'Unnamed':
        cols.append(col[1])
    else:
        cols.append(f'{col[0]} {col[1]}')

df = df.set_axis(cols, axis = 'columns')

# Get rid of those annoying rows
indicies = df.loc[df['Rk'] == 'Rk'].index
df.drop(indicies, inplace = True)

print('html done')
file_name = 'Test_csv'
df.to_csv(f'{file_name}.csv', index = False)
print('file written')
print(df.head())


