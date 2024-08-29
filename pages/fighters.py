import streamlit as st
import pandas as pd
import json
import unicodedata
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components
import urllib.parse

# Clear cache button
if st.button("Clear Cache"):
    st.cache_data.clear()

# Load photo mappings from JSON file
with open('fighters_photos.json', 'r', encoding='utf-8') as file:
    photos_mapping = json.load(file)

def normalize_string(s):
    # Normalize the string by removing any non-ASCII characters
    normalized = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii').strip()
    return normalized

# Extract fighter's name without Prezývka for matching
def extract_name_without_prezivka(fighter_name):
    # Split the fighter name into parts
    parts = fighter_name.split('"')
    meno , priezvisko = parts[0].strip() , parts[-1].strip()
    # Take only the first part which is Meno and Priezvisko
    return meno + ' ' + priezvisko

# Connect to Google Sheets
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

def update_query_params(selected_fighter):
    st.experimental_set_query_params(fighter=selected_fighter)

# Get current query parameters
query_params = st.experimental_get_query_params()
selected_fighter_query = query_params.get("fighter", [None])[0]

# Create a dropdown menu for selecting a fighter
selected_fighter = st.selectbox(
    "Choose a fighter:",
    fighter_options,
    index=fighter_options.index(selected_fighter_query) if selected_fighter_query in fighter_options else 0,
    key='fighter_select',
    on_change=lambda: update_query_params(st.session_state.fighter_select)  # Update query params immediately
)

# Find and display the row corresponding to the selected fighter
if selected_fighter:
    selected_row = df[df['Fighter_Display_Name'] == selected_fighter].iloc[0]
    
    # Extract values
    wins = int(selected_row['W'])
    losses = int(selected_row['L'])
    draws = int(selected_row['D'])
    no_contests = int(selected_row['NO_CONTEST'])
    cancelled = int(selected_row['CANCEL'])
    
    win_ko_tko = int(selected_row['W_KO/TKO'])
    win_sub = int(selected_row['W_SUB'])
    win_dec = int(selected_row['W_DEC'])
    win_other = int(selected_row['W_OTHER'])
    
    loss_ko_tko = int(selected_row['L_KO/TKO'])
    loss_sub = int(selected_row['L_SUB'])
    loss_dec = int(selected_row['L_DEC'])
    loss_other = int(selected_row['L_OTHER'])
    
    # Calculate percentages
    total_wins = win_ko_tko + win_sub + win_dec + win_other
    total_losses = loss_ko_tko + loss_sub + loss_dec + loss_other
    
    win_ko_tko_perc = int((win_ko_tko / total_wins * 100) if total_wins > 0 else 0)
    win_sub_perc = int((win_sub / total_wins * 100) if total_wins > 0 else 0)
    win_dec_perc = int((win_dec / total_wins * 100) if total_wins > 0 else 0)
    win_other_perc = int((win_other / total_wins * 100) if total_wins > 0 else 0)
    
    loss_ko_tko_perc = int((loss_ko_tko / total_losses * 100) if total_losses > 0 else 0)
    loss_sub_perc = int((loss_sub / total_losses * 100) if total_losses > 0 else 0)
    loss_dec_perc = int((loss_dec / total_losses * 100) if total_losses > 0 else 0)
    loss_other_perc = int((loss_other / total_losses * 100) if total_losses > 0 else 0)
    
    # Normalize fighter name
    if '"' in selected_fighter:
        normalized_fighter_name = normalize_string(extract_name_without_prezivka(selected_fighter))
    else:
        normalized_fighter_name = normalize_string(selected_fighter)
    # Extract fighter's photo URL
    photo_url = None
    
    for key in photos_mapping.keys():
        
        if normalize_string(key) == normalized_fighter_name:
            photo_url = photos_mapping[key]
            break
    
    if photo_url is None:
        photo_url = 'data:image/pnuD16+6Ptk9ZijDH0yZOu0xPvISRL31PvZOW5ErkJggg=='  # Default if no photo URL found

    # Render HTML for the fighter's photo and stats with fixed image size
    html_content = f"""
    <style>
    .fighter-stats {{
        width: 60%;
        font-size: 16px;
        margin: 20px auto;
        border-collapse: collapse;
    }}
    .fighter-stats td, .fighter-stats th {{
        padding: 10px;
        text-align: center;
        border: 1px solid #ddd;
    }}
    .fighter-stats th {{
        color: white;
        background-color: black;
    }}
    .fighter-stats .wins {{
        background-color: #4CAF50;
    }}
    .fighter-stats .losses {{
        background-color: #F44336;
    }}
    .fighter-stats .score-cell {{
        background-color: #4d4d4d;
        color: orange;
        font-weight: bold;
    }}
    .fighter-stats .draws {{
        background-color: orange;
        color: white;
    }}
    .fighter-stats .no-contest {{
        background-color: black;
        color: white;
    }}
    </style>
    
    <div class="fighter-info">
        <h2 style="text-align:center;">{selected_fighter}</h2>
        <img src="{photo_url}" alt="{selected_fighter}" style="display: block; margin: 0 auto; width: 300px; height: 300px; object-fit: cover;"/>
    </div>
    
    <!-- Main Table -->
    <table class="fighter-stats">
        <tr>
            <th class="wins">WINS</th>
            <td class="score-cell">{wins}</td>
            <th class="losses">LOSSES</th>
            <td class="score-cell">{losses}</td>
        </tr>
        <tr>
            <td>KO/TKO</td>
            <td class="score-cell">{win_ko_tko} ({win_ko_tko_perc}%)</td>
            <td>KO/TKO</td>
            <td class="score-cell">{loss_ko_tko} ({loss_ko_tko_perc}%)</td>
        </tr>
        <tr>
            <td>SUB</td>
            <td class="score-cell">{win_sub} ({win_sub_perc}%)</td>
            <td>SUB</td>
            <td class="score-cell">{loss_sub} ({loss_sub_perc}%)</td>
        </tr>
        <tr>
            <td>DEC</td>
            <td class="score-cell">{win_dec} ({win_dec_perc}%)</td>
            <td>DEC</td>
            <td class="score-cell">{loss_dec} ({loss_dec_perc}%)</td>
        </tr>
        <tr>
            <td>OTHER</td>
            <td class="score-cell">{win_other} ({win_other_perc}%)</td>
            <td>OTHER</td>
            <td class="score-cell">{loss_other} ({loss_other_perc}%)</td>
        </tr>
    </table>
    """

    st.markdown(html_content, unsafe_allow_html=True)
    
    
    # Check if draws, no contests, or cancellations are greater than 0
    if draws > 0 or no_contests > 0 or cancelled > 0:
        # Render HTML for the secondary table only if conditions are met
        html_content_2 = f"""
        <!-- Secondary Table -->
        <table class="fighter-stats">
            <tr>
                <td class="draws">DRAWS</td>
                <td class="score-cell">{draws}</td>
            </tr>
            <tr>
                <td class="no-contest">CANCELLED</td>
                <td class="score-cell">{cancelled}</td>
            </tr>
            <tr>
                <td class="no-contest">NO CONTEST</td>
                <td class="score-cell">{no_contests}</td>
            </tr>
        </table>
        """

        st.markdown(html_content_2, unsafe_allow_html=True)
    
    
        

# Connect to Google Sheets for fights
conn = st.connection('gsheets', type=GSheetsConnection)
df_zapasy = conn.read(worksheet='Zápasy')
df_zapasy = df_zapasy.loc[:, ~df_zapasy.columns.str.contains('^Unnamed')]
df_zapasy = df_zapasy.dropna(how='all')

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
            if '[' in opponent:
                opponent = opponent[1:-1]
                opponents = opponent.split(',')
                opponent = ''
                for x in opponents:
                    x = x.strip()
                    x = x[1:-1]

                    # Create hyperlink for each opponent
                    opponent_name_url = x.replace(' ', '+')
                    opponent_name_url = opponent_name_url.replace('"', '%22')    # URL-encode the opponent's name
                    href = f'<a href="/fighters?fighter={opponent_name_url}" target="_self" style="color: #f08a33; text-decoration: none;">{x}</a>'
                    
                    if opponent:
                        opponent += ' a ' + href
                    else:
                        opponent = href
            else:
                # Handle single opponent case
                opponent_name_url = opponent.replace(' ', '+')
                opponent_name_url = opponent.replace('"', '%22')  # URL-encode the opponent's name
                opponent = f'<a href="/fighters?fighter={opponent_name_url}" target="_self" style="color: #f08a33; text-decoration: none;">{opponent}</a>'
            
            turnaj_nazov = row['Nazov_turnaj']
            turnaj_nazov_url = turnaj_nazov.replace(' ', '+')
            turnaj = f'<a href="/turnaje?turnaj={turnaj_nazov_url}"  style="color: #f08a33; text-decoration: none;">{turnaj_nazov}</a>'

            # Prepare fight details
            fight_results.append({
                'Result': result,
                'Opponent': opponent,
                'Event': turnaj,
                'Method': row['Metoda'],
                'Round': row['Kolo'],
                'Time': row['Čas'],
                'Style': row['Disciplina']
            })
    
    def create_fight_results_table(fight_results):
        html_content = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        
        .fight-results {
            width: 100%;
            font-size: 16px;
            margin: 20px auto;
            border-collapse: collapse;
            font-family: 'Roboto', sans-serif;
        }
        .fight-results td, .fight-results th {
            padding: 10px 15px;
            text-align: center;
            border: 1px solid #ddd;
        }
        .fight-results th {
            background-color: black;
            color: white;
        }
        .fight-results .result-cell {
            color: white;
            font-weight: bold;
        }
        .fight-results .win {
            background-color: #4CAF50;
        }
        .fight-results .loss {
            background-color: #F44336;
        }
        .fight-results .draw {
            background-color: orange;
        }
        .fight-results .no-contest {
            background-color: black;
            color: white;
        }
        .fight-results .cancelled {
            background-color: grey;
            color: white;
        }
        .fight-results tr:nth-child(even) {
            background-color: #555;
        }
        .fight-results tr:nth-child(odd) {
            background-color: #666;
        }
        .fight-results td.other-columns {
            background-color: #444;
            color: orange;
        }
        .fight-results .opponent-col {
            width: 30%;
        }
        </style>
        
        <table class="fight-results">
            <tr>
                <th class="result-cell">Result</th>
                <th class="result-cell opponent-col">Opponent</th>
                <th class="result-cell opponent-col">Event</th>
                <th class="result-cell">Method</th>
                <th class="result-cell">Round</th>
                <th class="result-cell">Time</th>
                <th class="result-cell">Style</th>
            </tr>
        """
        
        for fight in fight_results:
            result_class = {
                'W': 'win',
                'L': 'loss',
                'DRAW': 'draw',
                'NO_CONTEST': 'no-contest',
                'CANCELLED': 'cancelled'
            }.get(fight['Result'], '')
            
            round_value = int(fight['Round']) if not pd.isna(fight['Round']) else '-'
            
            html_content += f"""<tr>
                <td class="result-cell {result_class}">{fight['Result']}</td>
                <td class="other-columns opponent-col">{fight['Opponent']}</td>
                <td class="other-columns">{fight['Event']}</td>
                <td class="other-columns">{fight['Method']}</td>
                <td class="other-columns">{round_value}</td>
                <td class="other-columns">{fight['Time']}</td>
                <td class="other-columns">{fight['Style']}</td>
            </tr>
            """
        
        html_content += "</table>"
        return html_content

    # Display the table using Streamlit Components
    if fight_results:
        html_content = create_fight_results_table(fight_results)
        #components.html(html_content, height=600, scrolling=True)
        st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.write("No fights found for the selected fighter.")


