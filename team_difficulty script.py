from bs4 import BeautifulSoup
import requests
import json
import pandas as pd


def return_player_data(url,n):
    result = requests.get(url)
    soup = BeautifulSoup(result.content,'html.parser')
    scripts = soup.find_all('script')
    strings = scripts[n].string
    
    ind_start = strings.index("('")+2
    ind_end =strings.index("')")
    json_data = strings[ind_start:ind_end]
    json_data = json_data.encode('utf8').decode('unicode_escape')

    data = json.loads(json_data)
    
    df = pd.DataFrame(data)
    return df

###Downloading the team data from understat
teams_df = return_player_data("https://understat.com/league/EPL/2021",2)
teams_df = teams_df.transpose()

team_list = teams_df["id"].unique()

### Creating the blank dataframe to add the data to
data=[]
all_teams_events= pd.DataFrame(data, columns=['h_a',
 'xG',
 'xGA',
 'npxG',
 'npxGA',
 'deep',
 'deep_allowed',
 'scored',
 'missed',
 'xpts',
 'result',
 'date',
 'wins',
 'draws',
 'loses',
 'pts',
 'npxGD',
 'ppda:att',
 'ppda:def',
 'ppda_allowed:att',
 'ppda_allowed:def',
 'team_id'])


### Loop to clean team data

#t=87
for t in team_list:

    team_df = teams_df[teams_df["id"] == str(t)]


    team_event_data = pd.json_normalize(team_df["history"], sep=":")
    team_event_data = team_event_data.transpose()
    team_event_data = pd.json_normalize(team_event_data[0])
    team_event_data["team_id"] = str(t)

    all_teams_events = all_teams_events.append(team_event_data)


teams_expected_data = all_teams_events.groupby(['team_id'])['xG','xGA'].sum()
teams_df = teams_df.drop(columns='history')
teams_df = pd.merge(teams_df,teams_expected_data, how='left',left_on='id',right_on='team_id')

teams_df["xg_rank"] = teams_df["xG"].rank(ascending=True)
teams_df["xga_rank"] = teams_df["xGA"].rank(ascending=False)

#########################################################



### import fixtures and teams df from FPL
def get_fpl_data(url):
    r = requests.get(url)
    json = r.json()
    return json

fixtures = get_fpl_data('https://fantasy.premierleague.com/api/fixtures/')
fixtures_df = pd.DataFrame(fixtures)

fixtures_df = fixtures_df[["code","event","id","team_a","team_h","kickoff_time"]]

elements = get_fpl_data('https://fantasy.premierleague.com/api/bootstrap-static/')
elements_df = pd.DataFrame(elements['elements'])
fpl_teams_df = pd.DataFrame(elements['teams'])


## filter fixtures df for next 6 matches
import datetime as dt     
import numpy as np 

today = pd.to_datetime(np.datetime64('today'))

fixtures_df["kickoff_time"] = pd.to_datetime(fixtures_df["kickoff_time"]).dt.tz_localize(None)

fixtures_df = fixtures_df[fixtures_df["kickoff_time"] > today]

fixtures_df["event"] = fixtures_df["event"].astype(int)

min_event = min(fixtures_df["event"])
max_event = min_event + 6

fixtures_df = fixtures_df[fixtures_df["event"] <= max_event]


## Combine home and away teams fixtures

home_team = fixtures_df[["event","team_h","team_a"]]
home_team = home_team.rename(columns ={'team_h':'team','team_a':'opponent'})

away_team = fixtures_df[["event","team_a","team_h"]]
away_team = away_team.rename(columns = {'team_a':'team','team_h':'opponent'})

data = []
fixtures_combo_df = pd.DataFrame(data, columns = ['event','team','opponent'])
fixtures_combo_df = fixtures_combo_df.append(home_team)
fixtures_combo_df = fixtures_combo_df.append(away_team)


## Get team names for teams and their opponents

fixtures_combo_df = pd.merge(fixtures_combo_df,fpl_teams_df[["id","name"]],how='left',left_on='team',right_on='id')
fixtures_combo_df = fixtures_combo_df.reset_index(drop=True)
fixtures_combo_df = fixtures_combo_df.drop(columns=["id"])
fixtures_combo_df = fixtures_combo_df.rename(columns={'name':'team_name'})

fixtures_combo_df = pd.merge(fixtures_combo_df,fpl_teams_df[["id","name"]],how='left',left_on='opponent',right_on='id')
fixtures_combo_df = fixtures_combo_df.reset_index(drop=True)
fixtures_combo_df = fixtures_combo_df.drop(columns=["id"])
fixtures_combo_df = fixtures_combo_df.rename(columns={'name':'opponent_name'})


## Get replace certain team names to be able to merge with understat data

fixtures_combo_df.loc[fixtures_combo_df.team_name == "Spurs", "team_name"] = "Tottenham"
fixtures_combo_df.loc[fixtures_combo_df.opponent_name == "Spurs", "opponent_name"] = "Tottenham"

fixtures_combo_df.loc[fixtures_combo_df.team_name == "Newcastle", "team_name"] = "Newcastle United"
fixtures_combo_df.loc[fixtures_combo_df.opponent_name == "Newcastle", "opponent_name"] = "Newcastle United"

fixtures_combo_df.loc[fixtures_combo_df.team_name == "Man City", "team_name"] = "Manchester City"
fixtures_combo_df.loc[fixtures_combo_df.opponent_name == "Man City", "opponent_name"] = "Manchester City"

fixtures_combo_df.loc[fixtures_combo_df.team_name == "Man Utd", "team_name"] = "Manchester United"
fixtures_combo_df.loc[fixtures_combo_df.opponent_name == "Man Utd", "opponent_name"] = "Manchester United"

fixtures_combo_df.loc[fixtures_combo_df.team_name == "Wolves", "team_name"] = "Wolverhampton Wanderers"
fixtures_combo_df.loc[fixtures_combo_df.opponent_name == "Wolves", "opponent_name"] = "Wolverhampton Wanderers"


## Merge understat data with fpl teams and clean up

fixtures_combo_df = pd.merge(fixtures_combo_df,teams_df,how='left',left_on='team_name',right_on='title')
fixtures_combo_df = fixtures_combo_df.rename(columns={'xG':'team_xG','xGA':'team_xGA', 'xg_rank':'team_xg_rank','xga_rank':'team_xga_rank'})
fixtures_combo_df = fixtures_combo_df.drop(columns=['id','title'])

fixtures_combo_df = pd.merge(fixtures_combo_df,teams_df,how='left',left_on='opponent_name',right_on='title')
fixtures_combo_df = fixtures_combo_df.rename(columns={'xG':'opponent_xG','xGA':'opponent_xGA','xg_rank':'opponent_xg_rank','xga_rank':'opponent_xga_rank'})
fixtures_combo_df = fixtures_combo_df.drop(columns=['id','title'])


## Calculate attacking and defending index based on xG and xGA ranks

fixtures_combo_df["attacking_index"] = fixtures_combo_df["team_xg_rank"] - fixtures_combo_df["opponent_xga_rank"]
fixtures_combo_df["defending_index"] = fixtures_combo_df["team_xga_rank"] - fixtures_combo_df["opponent_xg_rank"]



attacking_fdr_df = fixtures_combo_df[["event","team_name","opponent_name","attacking_index"]]
attacking_fdr_df = pd.pivot_table(attacking_fdr_df, values='attacking_index', index=['team_name'],columns=['event'], aggfunc=np.mean)

defending_fdr_df = fixtures_combo_df[["event","team_name","opponent_name","defending_index"]]
defending_fdr_df = pd.pivot_table(defending_fdr_df, values='defending_index', index=['team_name'],columns=['event'], aggfunc=np.mean)

attacking_average = fixtures_combo_df[["team_name","attacking_index"]].groupby(by="team_name").mean()
defending_average = fixtures_combo_df[["team_name","defending_index"]].groupby(by="team_name").mean()

attacking_fdr_df = pd.merge(attacking_fdr_df,attacking_average,how='left',left_on="team_name",right_on="team_name")
attacking_fdr_df = attacking_fdr_df.sort_values("attacking_index", ascending=False)

defending_fdr_df = pd.merge(defending_fdr_df,defending_average,how='left',left_on="team_name",right_on="team_name")
defending_fdr_df = defending_fdr_df.sort_values("defending_index", ascending=False)