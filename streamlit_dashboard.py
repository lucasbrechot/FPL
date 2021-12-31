import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from decimal import Decimal
import plotly.graph_objects as go


st.set_page_config(
     page_title="FPL LB",
     page_icon="⚽",
     layout="wide",
     initial_sidebar_state="expanded",
 )

##### LOADING AND RE-WORKING THE DATA


g_url = "https://docs.google.com/spreadsheets/d/1qmYMedwJDy4j0vXB7pED_ruzcxjGXMUAXVhUbAcnTmk/export?format=csv&gid="

#@st.cache
def load_data(id, nrows):
    url = g_url + str(id)
    data = pd.read_csv(url, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

data = load_data(0,10000)
attacking_fdr = load_data(1332666413,50)
defending_fdr = load_data(570497350,50)


data = data.drop(['fpl_player_id'], axis=1)
data = data.drop(['selected_by_percent'], axis=1)
data = data.drop(['team_name'], axis=1)

data = data.rename(columns = {'web_name': 'name', 'now_cost': 'cost'})

decimals = 1    


data['cost'] = data['cost'] / 10
data['cost'] = data['cost'].astype('float').round(2)

data['form_last4'] = data['form_last4'].astype(float)
data['index'] = data['index'].astype(float)
data['ict_index_season'] = data['ict_index_season'].astype(int)

data['fdr'] = data['fdr'].astype(float)
data['fdr'] = data['fdr'].round(1)




##### LEFT SLIDER FILTERS FOR THE DATA


st.sidebar.header('FPL Player Dashboard')

sliders_data = data

# Step 1.1 filtering data for form

form_slider_values = st.sidebar.slider(
    '💪 Filter for form level over the last 4 weeks',
    0, 20, (0, 20), step=1
)
form_min_value = form_slider_values[0]
form_max_value = form_slider_values[1]

sliders_data = sliders_data[sliders_data["form_last4"] > form_min_value ]
sliders_data = sliders_data[sliders_data["form_last4"] < form_max_value ]

# Step 1.2 filtering data for difficulty

fdr_slider_values = st.sidebar.slider(
    '🥵 Filter for fixture difficulty range in the next 4 weeks (low = easy fixtures; high = difficult fixtures)',
    2.0, 5.0, (2.0, 5.0), step=0.5
)
fdr_min_value = fdr_slider_values[0]
fdr_max_value = fdr_slider_values[1]

sliders_data = sliders_data[sliders_data["fdr"] > fdr_min_value ]
sliders_data = sliders_data[sliders_data["fdr"] < fdr_max_value ]

# Step 1.3 filtering data for price range

price_slider_values = st.sidebar.slider(
    '💰 Filter for player cost',
    3, 14, (4, 14), step=1
)
price_min_value = price_slider_values[0]
price_max_value = price_slider_values[1]

sliders_data = sliders_data[sliders_data["cost"] > price_min_value ]
sliders_data = sliders_data[sliders_data["cost"] < price_max_value ]

# Step 2 filtering data for positions

position = st.sidebar.selectbox(
    '🥅 Filter for a specific position',
     ('All','Goalkeeper', 'Defender', 'Midfielder','Forward'))

position_data = sliders_data[sliders_data["position"] == position]

if position == 'All':
    players = sliders_data["name"]
    position_data = sliders_data
else: 
    players = position_data["name"]
    position_data = sliders_data[sliders_data["position"] == position ]


players_selected = st.sidebar.multiselect(
     '🤴 Select specific players',
     players)

if players_selected:
    data_filtered = position_data[position_data.name.isin(players_selected)]
else: data_filtered = position_data




##### MAIN PANEL


#################### GETTING GRAPH DATA ACCORDING TO TIMEFRAME


season_data = data_filtered[["name",
                            "cost",
                            "fdr",
                            "form_season",
                            "xg_season",
                            "xa_season",
                            "goals_season",
                            "assist_season",
                            "key_passes_season",
                            "shots_season",
                            "ict_index_season",
                            "expected_actual_season"]]
season_data = season_data.rename(columns={
    'form_season': 'form',
    'xg_season': 'xg',
    'xa_season': 'xa',
    'goals_season': 'goals',
    'assist_season': 'assists',
    'key_passes_season': 'passes',
    'shots_season': 'shots',
    'ict_index_season': 'ict',
    'expected_actual_season': 'x/act'
    })
last4_data = data_filtered[["name",
                            "cost",
                            "fdr",
                            "form_last4",
                            "xg_last4",
                            "xa_last4",
                            "goals_last4",
                            "assist_last4",
                            "key_passes_last4",
                            "shots_last4",
                            "ict_index_last4",
                            "expected_actual_last4"]]
last4_data = last4_data.rename(columns={
    'form_last4': 'form',
    'xg_last4': 'xg',
    'xa_last4': 'xa',
    'goals_last4': 'goals',
    'assist_last4': 'assists',
    'key_passes_last4': 'passes',
    'shots_last4': 'shots',
    'ict_index_last4': 'ict',
    'expected_actual_last4': 'x/act'
    })




col1, col2= st.columns([1,3])

with col1:
    timeframe = st.radio(
         "Select the timeframe for the data below",
         ('All season','Last 4 matches'))

with col2:
    with st.expander("About the data"):
        st.markdown('Fdr: calculated based on the difficulty of the player next 5 fixtures. The lower the number the easier the next 5 fixtures are.' )
        st.markdown('Form: calculated based on the points accumulated by the player over the last 5 fixtures')
        st.markdown('Index: indicator based on form, fdr and ict index. the ponderations of these factors comes from a linear regression of these influence of these 3 indicators on points accumulated throughout this season')

        st.markdown('Data source 1: https://fantasy.premierleague.com/api/element-summary/')
        st.markdown('Data source 2: https://fantasy.premierleague.com/api/bootstrap-static/')


if timeframe == "All season":
    graph_data = season_data

else:
    graph_data = last4_data


bar_data  = graph_data.nlargest(10,'form')



text = '''
---
'''
st.markdown(text)

#################### FIRST ROW WITH BAR CHART AND RADAR CHART


col3, col4= st.columns(2)

with col3:
    st.markdown('**Players mapped by form, fixture difficulty and ICT (size)**')
    st.caption('Only the top 10 players based on form are selected from the filtered data.')
    fig = px.scatter(bar_data, x="form", y="fdr", hover_data=['name'], size='ict', text="name")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.markdown('**Player comparison**')
    st.caption('Select at least one player in the multiselect box in the left panel.')

    if len(players_selected) == 0:
        
        st.image('https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/285/woman-detective_1f575-fe0f-200d-2640-fe0f.png')
        
    else:

        fig2 = go.Figure()

        categories=['Expected Goal','Expected assists','Goals','Assists']

        value_range = pd.Series([0.0,0.1])

        for p in players_selected:

            radar_data = graph_data[graph_data["name"] == p]

            xg = radar_data["xg"].iloc[0]
            xa = radar_data["xa"].iloc[0]
            goals = radar_data["goals"].iloc[0]
            assists = radar_data["assists"].iloc[0]

            add_range = pd.Series([xg,xa,goals,assists])
            value_range = value_range.append(add_range, ignore_index=True)

            fig2.add_trace(go.Scatterpolar(
                  r=[xg, xa, goals, assists],
                  theta=categories,
                  fill='toself',
                  name=p
            ))

        min_value = min(value_range)
        max_value = max(value_range)

        fig2.update_layout(
          polar=dict(
            radialaxis=dict(
              visible=True,
              range=[min_value, max_value]
            )),
          showlegend=False
        )

        st.plotly_chart(fig2, use_container_width=True)


#################### DATAFRAME ROW

st.markdown(text)

#pd.options.display.float_format = '${:,.2f}'.format


if timeframe == "All season":

    st.markdown('**Player data for all season**')
    st.dataframe(graph_data,10000)

else:
    st.markdown('**Player data for last 4 matches**')
    st.dataframe(graph_data,10000)   


#################### FDR ROW

st.markdown(text)

colA, colB= st.columns([1,3])

with colA:
    fdr_position = st.radio(
             "Select the position FDR",
             ('Attacking FDR','Defending FDR'))

with colB:

    if fdr_position == "Attacking FDR":
        
        st.dataframe(attacking_fdr.style.highlight_max(props='color:white;background-color:darkblue', axis=0))

    else:
        st.dataframe(defending_fdr.style.highlight_max(props='color:white;background-color:darkblue', axis=0))

