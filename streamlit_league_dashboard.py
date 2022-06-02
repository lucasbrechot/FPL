import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from decimal import Decimal
import plotly.graph_objects as go


st.set_page_config(
     page_title="MESsi Que un Club",
     page_icon="⚽",
     layout="wide",
     initial_sidebar_state="expanded",
 )


##### LOADING AND RE-WORKING THE DATA


g_url = "https://docs.google.com/spreadsheets/d/1JfjVM3C1E5-gFebKfWDQwxjgolOHEqdrYxeAW5HqlrM/export?format=csv&gid=0"
data = pd.read_csv(g_url)

data["rank_neg"] = data["rank"] * -1
data["net_points"] = data["points"] - data["event_transfers_cost"]


entries_names = data["entry_name"].unique()


# Step 1.1 filtering for specific managers

entries_selected = st.sidebar.multiselect(
     '🤴 Select specific league managers',
     entries_names)

if entries_selected:
    data_filtered = data[data.entry_name.isin(entries_selected)]

else: data_filtered = data


# Step 1.2 filtering for desired event

gameweek_slider_values = st.sidebar.slider(
    '🗓️ Filter for the gameweek numbers for which you want to filter',
    1, 38, (1, 38), step=1
)
gw_min_value = gameweek_slider_values[0]
gw_max_value = gameweek_slider_values[1]

data_filtered = data_filtered[data_filtered["event"] >= gw_min_value ]
data_filtered = data_filtered[data_filtered["event"] <= gw_max_value ]


# Prepare le line graph

st.title('MESsi Que un Club -- Hall of Fame')


st.header('📈 Ranks through the season')

fig = px.line(data_filtered, x="event", y="rank_neg", color="entry_name", markers=True, height=600)
fig.update_yaxes(title_text='')
fig.update_yaxes(showticklabels=False)
fig.update_xaxes(title_text='Gameweek')

st.plotly_chart(fig, use_container_width=True, height=600)


st.header('🏆 Honourary mentions')

col1, col2, col3 = st.columns([1,1,1])

# Prepare le bar chart

with col1:

    st.subheader('💯 Most points')


    points_data = data_filtered[['entry_name','net_points']].groupby(by="entry_name").sum()
    points_data = points_data.reset_index()
    points_data = points_data.sort_values(by='net_points', ascending=True)

    fig = px.bar(points_data, x="net_points", y="entry_name", orientation='h', text='net_points')
    fig.update_yaxes(title_text='')
    fig.update_xaxes(title_text='')
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True, height=800)


with col2:

    st.subheader('💸 Most transfer gains')

    transfer_data = data_filtered[['entry_name','transfer_gains']].groupby(by="entry_name").sum()
    transfer_data = transfer_data.reset_index()
    transfer_data = transfer_data.sort_values(by='transfer_gains', ascending=True)

    fig = px.bar(transfer_data, x="transfer_gains", y="entry_name", orientation='h', text='transfer_gains')
    fig.update_yaxes(title_text='')
    fig.update_xaxes(title_text='')
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True, height=800)

with col3:

    st.subheader('🧢 Most captain points')

    captain_data = data_filtered[['entry_name','captain_points']].groupby(by="entry_name").sum()
    captain_data = captain_data.reset_index()
    captain_data = captain_data.sort_values(by='captain_points', ascending=True)

    fig = px.bar(captain_data, x="captain_points", y="entry_name", orientation='h', text='captain_points')
    fig.update_yaxes(title_text='')
    fig.update_xaxes(title_text='')
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True, height=800)

st.balloons()
