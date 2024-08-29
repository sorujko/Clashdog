import streamlit as st
import pandas as pd
import json
from streamlit_gsheets import GSheetsConnection

# Clear cache button
if st.button("Clear Cache"):
    st.cache_data.clear()

# Connect to Google Sheets for fighters
conn = st.connection('gsheets', type=GSheetsConnection)
df = conn.read(worksheet='Fighters')
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.dropna(how='all')

# Format fighter names
def format_fighter_name(row):
    if pd.notna(row['Prezývka']) and row['Prezývka'].strip():
        return f"{row['Meno']} \"{row['Prezývka']}\" {row['Priezvisko']}"
    else:
        return f"{row['Meno']} {row['Priezvisko']}"

df['Fighter_Display_Name'] = df.apply(format_fighter_name, axis=1)
fighter_options = df['Fighter_Display_Name'].tolist()

# Connect to Google Sheets for fights
conn = st.connection('gsheets', type=GSheetsConnection)
df_zapasy = conn.read(worksheet='Zápasy')
df_zapasy = df_zapasy.loc[:, ~df_zapasy.columns.str.contains('^Unnamed')]
df_zapasy = df_zapasy.dropna(how='all')

# Choose a fighter
selected_fighter = st.selectbox("Choose a fighter:", fighter_options)

if selected_fighter:
    # Function to check if the fighter is in a list or a single value
    def fighter_in_list(fighter_list):
        if isinstance(fighter_list, list):
            return selected_fighter in fighter_list
        return selected_fighter == fighter_list

    # Filter rows where the selected fighter is in the 'W' or 'L' columns
    fighter_is_winner = df_zapasy['W'].str.contains(selected_fighter, na=False)
    fighter_is_loser = df_zapasy['L'].str.contains(selected_fighter, na=False)
    
    # Select relevant fights
    relevant_fights = df_zapasy[fighter_is_winner | fighter_is_loser]

    # Process each relevant fight
    fight_results = []
    for _, row in relevant_fights.iterrows():
        result = ''
        opponent = ''
        
        if row['NO_CONTEST'] == 1:
            result = 'NO_CONTEST'
        elif row['CANCELLED'] == 1:
            result = 'CANCELLED'
        elif row['DRAW'] == 1:
            result = 'DRAW'
        elif selected_fighter in row['W']:
            result = 'W'
        elif selected_fighter in row['L']:
            result = 'L'
        
        # Determine opponent
        if result in ['W', 'L', 'DRAW', 'NO_CONTEST', 'CANCELLED']:
            if selected_fighter in row['W']:
                opponent = ', '.join(f for f in (row['L'] if isinstance(row['L'], list) else [row['L']]))
            else:
                opponent = ', '.join(f for f in (row['W'] if isinstance(row['W'], list) else [row['W']]))
            print(opponent)
            if '[' in opponent:
                opponent = opponent[1:-1]
                opponents = opponent.split(',')
                print(opponents)
                opponent = ''
                for x in opponents:
                    x = x.strip()
                    x = x[1:-1]
                    if opponent:
                        opponent += ' a ' + x
                    else:
                        opponent = x
            # Prepare fight details
            fight_results.append({
                'Result': result,
                'Opponent': opponent,
                'Event': row['Turnaj_ID'],
                'Method': row['Metoda'],
                'Round': row['Kolo'],
                'Time': row['Čas']
            })
    
    # Convert to DataFrame and display
    if fight_results:
        results_df = pd.DataFrame(fight_results)
        st.write("Fight Results:")
        st.dataframe(results_df)
    else:
        st.write("No fights found for the selected fighter.")
