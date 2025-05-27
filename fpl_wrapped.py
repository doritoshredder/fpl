import streamlit as st
import pandas as pd
import json

# 🎯 Load FPL data from JSON files
managers = ['Amirkia', 'Daryosh', 'Amirpooya', 'Daniel', 'Shaywan', 'Amin', 'Juan Diego']
filenames = ['amirkia.json', 'daryosh.json', 'amirpooya.json', 'daniel.json', 'shawyan.json', 'amin.json', 'juan.json']

dfs = []
for manager, file in zip(managers, filenames):
    with open(file) as f:
        data = json.load(f)
        df = pd.DataFrame(data['current'])
        df['Manager'] = manager
        dfs.append(df)

fpl_data = pd.concat(dfs, ignore_index=True)
fpl_data = fpl_data.rename(columns={'event': 'Gameweek', 'points': 'Points', 'total_points': 'Total_Points', 'rank': 'Overall_Rank', 'points_on_bench': 'Bench_Points'})
fpl_data = fpl_data.sort_values(['Manager', 'Gameweek'])

# Fill missing Gameweeks
all_gameweeks = pd.DataFrame([(manager, gw) for manager in fpl_data['Manager'].unique() for gw in range(1, 39)],
                             columns=['Manager', 'Gameweek'])
fpl_data_complete = pd.merge(all_gameweeks, fpl_data, on=['Manager', 'Gameweek'], how='left')
fpl_data_complete['Overall_Rank'] = fpl_data_complete['Overall_Rank'].ffill()

# Calculate League Rank
fpl_data_complete['League_Rank'] = fpl_data_complete.groupby('Gameweek')['Total_Points'].rank(ascending=False, method='min')

# 🏆 King of the Bench
bench_summary = fpl_data_complete.groupby('Manager')['Bench_Points'].sum().reset_index().rename(columns={'Bench_Points': 'Total_Bench_Points'})
king_of_bench = bench_summary.loc[bench_summary['Total_Bench_Points'].idxmax(), 'Manager']

# 🧙‍♂️ Captain Genius
captain_points_data = pd.DataFrame({
    'Manager': ['Amirkia', 'Amirpooya', 'Daryosh', 'Daniel', 'Shaywan', 'Amin', 'Juan Diego'],
    'Captain_Points': [718, 716, 736, 673, 596, 455, 338]
})
captain_genius = captain_points_data.loc[captain_points_data['Captain_Points'].idxmax(), 'Manager']

# Todd Boehly (most transfers)
transfer_summary = fpl_data_complete.groupby('Manager')['event_transfers'].sum().reset_index().rename(columns={'event_transfers': 'Total_Transfers'})
boehly = transfer_summary.loc[transfer_summary['Total_Transfers'].idxmax(), 'Manager']

# 🎯 Final Points + Rank
final_week = fpl_data_complete['Gameweek'].max()
final_totals = fpl_data_complete[fpl_data_complete['Gameweek'] == final_week][['Manager', 'Total_Points']].reset_index(drop=True)
final_totals = final_totals.merge(transfer_summary, on='Manager')
final_totals = final_totals.merge(bench_summary, on='Manager')
final_totals = final_totals.merge(captain_points_data, on='Manager')

# 🎨 Streamlit App Layout
st.title("Fantasia League Wrapped 🎉")

st.markdown(f"🏆 **King of the Bench:** {king_of_bench} (left the most points on the bench!)")
st.markdown(f"🧙‍♂️ **Captain Genius:** {captain_genius} (most captain points)")
st.markdown(f"💸 **Todd Boehly Award:** {boehly} (most transfers)")

manager = st.selectbox("Select your team", final_totals['Manager'])

user_stats = final_totals[final_totals['Manager'] == manager].iloc[0]
st.metric("Total Points", int(user_stats['Total_Points']))
st.metric("Total Transfers Made", int(user_stats['Total_Transfers']))
st.metric("Total Bench Points", int(user_stats['Total_Bench_Points']))
st.metric("Captain Points", int(user_stats['Captain_Points']))

# 🔥 Best & Worst Gameweek
user_data = fpl_data_complete[fpl_data_complete['Manager'] == manager]
best_gw = user_data.loc[user_data['Points'].idxmax(), ['Gameweek', 'Points']]
worst_gw = user_data.loc[user_data['Points'].idxmin(), ['Gameweek', 'Points']]

st.write(f"🔥 Best Gameweek: GW{int(best_gw['Gameweek'])} ({int(best_gw['Points'])} points)")
st.write(f"💤 Worst Gameweek: GW{int(worst_gw['Gameweek'])} ({int(worst_gw['Points'])} points)")

# 📈 League Rank Chart (Optional GIF)
st.image("fpl_league_rankings.gif", caption="League Rankings Over Time")

st.write("This is your end-of-season recap!")
