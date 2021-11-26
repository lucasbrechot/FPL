import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title('FPL Player Dashboard')

DATA_URL = ('/Users/lucasbrechot/Streamlit/player_summary_data.csv')

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

data = data.drop(['id'], axis=1)
data = data.drop(['team'], axis=1)
data = data.drop(['unnamed: 0'], axis=1)
data = data.drop(['min'], axis=1)


decimals = 1    


data['cost'] = data['cost'] / 10
data['cost'] = data['cost'].astype('float').round(2)


data['form'] = data['form'].astype(float)
data['index'] = data['index'].astype(int)
data['ict'] = data['ict'].astype(int)
data['selected %'] = data['selected %'].astype(int)


data['fdr'] = data['fdr'].astype(float)
data['fdr'] = data['fdr'].round(1)



#left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
#left_column.button('Press me!')

# Or even better, call Streamlit functions inside a "with" block:






# Step 1 filtering data for positions

slider_values = st.sidebar.slider(
    'Select a price range',
    0.0, 14.0, (4.5, 13.0)
)
min_value = slider_values[0]
max_value = slider_values[1]

step1_data = data[data["cost"] > min_value ]
step1_data = step1_data[step1_data["cost"] < max_value ]

# Step 2 filtering data for positions

position = st.sidebar.selectbox(
    'Which player position',
     ('All','Goalkeeper', 'Defender', 'Midfielder','Forward'))

st.sidebar.write('You selected:', position)

position_filtered = step1_data[step1_data["position"] == position]

if position == 'All':
    players = step1_data["name"]
    step2_data = step1_data
else: 
    players = position_filtered["name"]
    step2_data = step1_data[step1_data["position"] == position ]


players_selected = st.sidebar.multiselect(
     'Select specific players',
     players)



if players_selected:
    data_filtered = step2_data[step2_data.name.isin(players_selected)]
else: data_filtered = step2_data

st.subheader('Plot Chart')

fig = px.scatter(data_filtered, x="form", y="fdr", hover_data=['name'], size='ict', color="index")
st.plotly_chart(fig, use_container_width=True)

st.subheader('Table')

st.table(data_filtered)
