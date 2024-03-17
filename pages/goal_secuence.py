import pandas as pd
import duckdb
import google.generativeai as genai
from mplsoccer import (VerticalPitch, Pitch, create_transparent_cmap,
                       FontManager, arrowhead_marker, add_image)
import matplotlib.pyplot as plt

from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import to_rgba, LinearSegmentedColormap
import unicodedata
import streamlit as st


def eliminar_tildes(texto):
    texto_nfd = unicodedata.normalize('NFD', texto)
    texto_limpio = ''.join(c for c in texto_nfd if not unicodedata.combining(c))
    return texto_limpio

@st.cache_data
def load_data():
    pass_data = pd.concat(map(pd.read_parquet, [
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ENG_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/GER_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/ITA_match_events.parquet',
        'https://raw.githubusercontent.com/adlihs/streamlit_shot_map/master/data/FRA_match_events.parquet']))

    pass_data[['date', 'game']] = pass_data['game'].str.split(" ", n=1, expand=True)
    pass_data['season'] = '23-24'

    #pass_data = pass_data[pass_data['player'].notna()]
    #pass_data['player'] = pass_data['player'].apply(eliminar_tildes)
    

    return pass_data


def goals_previous_actions(actions_data, team):
    pass_df = actions_data[(actions_data['type'] == 'Goal') & (actions_data['team'] == team)]
    # pass_df = pd.DataFrame()
    pass_df_tmp = pd.DataFrame()
    actions_df = pd.DataFrame()

    for fila in pass_df.itertuples():
        indice_accion = fila.Index
        minuto_goal = fila.minute
        # indice_accion = soccer_data2.iloc[max(indice_accion-5, 0):indice_accion+1].to_dict('records')
        pass_df_tmp = actions_data.iloc[max(indice_accion - 5, 0):indice_accion + 1].to_dict(
            'records')  # soccer_data2.iloc[indice_accion-5:indice_accion].to_dict('records')
        pass_df_tmp = pd.DataFrame(pass_df_tmp)
        pass_df_tmp['x_siguiente'] = pass_df_tmp['x'].shift(-1)
        pass_df_tmp['y_siguiente'] = pass_df_tmp['y'].shift(-1)
        pass_df_tmp['goal_index'] = minuto_goal

        actions_df = pd.concat([actions_df, pass_df_tmp])

    return actions_df


def viz_previous_events(soccer_data=None, game=None, minute=None):
    gem_api = 'AIzaSyAKKRcbonvFpJL5q6Il_50cHEWtoe60cxk'
    genai.configure(api_key=gem_api)
    model = genai.GenerativeModel('gemini-pro')

    soccer_data = soccer_data.sort_values(by=["minute", "second"])
    soccer_data = soccer_data[(soccer_data['game'] == game) &
                              (soccer_data['goal_index'] == minute)]

    goal_data = soccer_data[soccer_data['type'] == 'Goal']
    goal_player = goal_data['player'].unique()[0]
    goal_team = goal_data['team'].unique()[0]
    league = goal_data['league'].unique()[0]
    date_game = goal_data['date'].unique()[0]

    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'gugi/Gugi-Regular.ttf')

    # Setup pass flow for Team 1
    pitch = Pitch(pitch_type='opta',
                  line_zorder=2,
                  line_color='#01161E',
                  pitch_color='#eee9e5')  # control the goal transparency
    fig, ax = pitch.draw(figsize=(12, 10))
    fig.set_facecolor("#eee9e5")  # you can also adjust the transparency (alpha)

    pearl_earring_cmap = LinearSegmentedColormap.from_list("Pearl Earring - 10 colors",
                                                           ['#eee9e5', '#2f3e46'], N=100)

    for row in soccer_data.itertuples():
        action_type = row.type
        if action_type == "Pass":
            if row.Index == 0:
                scatters = pitch.scatter(row.x, row.y, color='blue', s=157,
                                         zorder=10, ax=ax)
                pitch.annotate(row.Index, xy=(row.x, row.y),
                               va='center',
                               ha='center',
                               zorder=11,
                               color="white",
                               ax=ax)
                line = pitch.lines(row.x, row.y,
                                   row.x_siguiente, row.y_siguiente,
                                   lw=1,
                                   transparent=True,
                                   n_segments=100,
                                   color='black',
                                   ax=ax)
                arrow_line = pitch.arrows(row.x, row.y,
                                          ((row.x + row.x_siguiente) / 2), ((row.y + row.y_siguiente) / 2),
                                          width=1,
                                          zorder=9,
                                          headwidth=8,
                                          color='black',
                                          ax=ax)
                # Other actions related to passing...
            else:
                scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                         edgecolors='black', zorder=10, ax=ax)
                scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                         edgecolors='black',
                                         # alpha=0.5,
                                         zorder=10,
                                         ax=ax)
                pitch.annotate(row.Index, xy=(row.x, row.y),
                               va='center',
                               ha='center',
                               zorder=11,
                               color="black",
                               ax=ax)
                line = pitch.lines(row.x, row.y,
                                   row.x_siguiente, row.y_siguiente,
                                   lw=1,
                                   transparent=True,
                                   n_segments=100,
                                   color='black',
                                   ax=ax)
                arrow_line = pitch.arrows(row.x, row.y,
                                          ((row.x + row.x_siguiente) / 2), ((row.y + row.y_siguiente) / 2),
                                          width=1,
                                          zorder=9,
                                          headwidth=8,
                                          color='black',
                                          ax=ax)
                # Other actions related to passing...
        else:
            if row.Index == 5:
                scatters = pitch.scatter(row.x, row.y, color='red', s=157,
                                         # alpha=0.5,
                                         zorder=10,
                                         ax=ax)
                pitch.annotate(row.Index, xy=(row.x, row.y),
                               va='center',
                               ha='center',
                               zorder=11,
                               color="white",
                               ax=ax)
                # Other actions related to non-passing...
            elif row.Index == 0:
                scatters = pitch.scatter(row.x, row.y, color='blue', s=157,
                                         # alpha=0.5,
                                         zorder=10,
                                         ax=ax)
                pitch.annotate(row.Index, xy=(row.x, row.y),
                               va='center',
                               ha='center',
                               zorder=11,
                               color="white",
                               ax=ax)
                line = pitch.lines(row.x, row.y,
                                   row.x_siguiente, row.y_siguiente,
                                   lw=1,
                                   color='black',
                                   linestyle='dashed',
                                   ax=ax)
            else:
                scatters = pitch.scatter(row.x, row.y, color='#eee9e5', s=157,
                                         edgecolors='black',
                                         # alpha=0.5,
                                         zorder=10,
                                         ax=ax)
                pitch.annotate(row.Index, xy=(row.x, row.y),
                               va='center',
                               ha='center',
                               zorder=11,
                               color="black",
                               ax=ax)
                line = pitch.lines(row.x, row.y,
                                   row.x_siguiente, row.y_siguiente,
                                   lw=1,
                                   color='black',
                                   linestyle='dashed',
                                   ax=ax)

    txt_title_team = ax.text(x=0, y=109, s=goal_player + ' goal',
                             size=40,
                             # here i am using a downloaded font from google fonts instead of passing a fontdict
                             fontproperties=fm_rubik.prop, color='#0D2C54')

    ax.text(x=0.1, y=104.5,
            s=str(goal_team) + " | " + str(league) + " | " + str(game) + " | " + "Minute: " + str(minute),
            size=15,
            fontproperties=fm_rubik.prop,
            color=pitch.line_color)

    ### Goal AI narrative
    narrative_df = soccer_data[['team', 'player', 'minute', 'second', 'type']].rename(columns={'type': 'action'})
    narrative_df = narrative_df.reset_index()

    text = narrative_df.to_string(index=False, header=True)

    order_txt = "I'm going to give you a Index, team, player name, minute, second and action for a soccer game goal, please re-create briefly the play using the data, use only the information provided, put between () the Index, include all the actions for the teams in order base the Index, and i want a bulleted list:" + text
    response = model.generate_content(order_txt)
    #print(response.text)

    ax.text(x=0.1, y=0.5,
            s=response.text,
            size=10,
            fontproperties=fm_rubik.prop,
            color=pitch.line_color)

    st.pyplot(plt)


data = load_data()
base_data = data.copy()

with st.sidebar:
    st.title('Pass Flow Generator :soccer:')
    st.subheader('Big 5 Leagues')
    st.write = 'Sidebar'
    leagues = st.selectbox('Select a League',
                           ('Premier League', 'Bundesliga', 'Serie A','Ligue 1'))

    data = data[data['league'] == leagues]

    data_teams = data['team'].unique()

    teams = st.selectbox(
        'Select a team',
        data_teams
    )
    data = data[(data['league'] == leagues) & (data['team'] == teams)]
    data_games = data['game'].unique()

    games = st.selectbox(
        'Select a Game',
        data_games)

    data = data[(data['league'] == leagues) & (data['team'] == teams) & (data['game'] == games) & (data['type'] == 'Goal')]
    data_minutes = data['minute'].unique()

    minutes = st.selectbox(
        'Select a Goal Minute',
        data_minutes)


goals_previous_actions_df = goals_previous_actions(actions_data=base_data, team=teams)


viz_previous_events(soccer_data=goals_previous_actions_df,game=games,minute=minutes)
