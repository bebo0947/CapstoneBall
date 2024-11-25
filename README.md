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
 - EDA: I created files for each year (such that there is one datapoint for each player in each csv) and also a master spreadsheet that contains all the data and approximately has shape 20,000x140. <br>
 - EDA: When creating the master csv, I ensured that redundant columns were removed as well as removing unnecessary columns. <br>
 - EDA: I mapped the position data on a scale from 0-7 to indicate how far forward the player plays (Goalie at 0, Forwards at 7)
 - Feature engineering: I created an experience column which is an accumulaton for each datapoint on how much football that player has played till that point.
 - Feature engineering: I created an impact column which measures the impact that the player had on his team that season. Considering his position, the feature combines how many goals are conceded, and how many are scored WHILE THE PLAYER IS ON THE PITCH.
 - Clustering: Using my engineered feature, i clustered players together based on their experience, minutes played that season, and impact on team to generate labels from 
    - Nobody, out of favour, injured, rotational player, rotational starter, new starter, starter, star player

#### Plan for the future:
I will require two models:
1. The first one will use historical data to try and predict each players upcoming season (stat-by-stat) <br>
- This will most likely be a time series neural network
- I will start with a small subset (most likely the shooting data)
- Then i will scale it to the entire data. 
2. The second model (If youll call it that) Will use a minimizing least squares on the results of the first model to find the player whose stats are closest to the requested player. 

### Describe your results
For the clustering portion, My results are as desired. Using my knowledge of how football works, I am happy to report that the model was able to accurately label players and their roles in their teams. 
- something to note however, I had to label some of the roles together as the associated datapoints are too similar.

### Party!
