# CAPSTONE DEMO README

### Describe your project (big idea)
A machine learning project studying player similarity.

### Describe your goal
Create an ML algorithm that, given a player, will return the player whose projected future is most similar to that player. 

### Describe your data
Data comes from FBref.com <br>
Data comes from seasons spanning 2017/18 season to 2023/24 season in categories standard, shooting, passing, passing types, possession, Goal Creation, playing time <br>
More granularly, the overall table has ~20,000 rows and ~140 columns <br>
 - Each row (datapoint) represents a player at a certain age. for example, Mo Salah at 25 is a different datapoint than Mo Salah at 26 <br>
 - There are 6 columns of player metadata including name, nation, position, squad, league, age. <br>
 - Each column represent a numerical statistic from the categories mentioned above. <br>

### Describe your work (models, analysis, EDA, etc.)
#### Done so far:
Major EDA elements:
 - Background info: The data came from 49 different webpages for 7 years, each year with 7 categories <br>
 - Webscraping: I started by scraping a singular category from a single year. Then I looped over the years and categories into separate dataframes. <br>
 - EDA: I created files for each year (such that there is one datapoint for each player in each csv) and also a master spreadsheet that contains all the data and approximately has shape 20,000x140.

#### Plan for the future:
I will require two models:
1. The first one will use historical data to try and predict each players upcoming season (stat-by-stat) <br>
2. The second model (If youll call it that) Will use a minimizing least squares on the results of the first model to find the player whose stats are closest to the requested player. 

### Describe your results
TBD

### Party!
