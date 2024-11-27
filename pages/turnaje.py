import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Clear cache button
if st.button("Clear Cache"):
    st.cache_data.clear()


tournament_images = {
    "Clash of the Stars 1" : "https://upload.wikimedia.org/wikipedia/commons/6/6d/Clash_of_the_Stars.jpg",
    "Clash of the Stars 2" : "data:image/jpeg;base64,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",
    "Clash of the Stars 3" : "https://www.ticketportal.cz/images/podujatie/-17599871/o250x250-_202291103013.jpg",
    "Clash of the Stars 4" : "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR4BT8Sxkn9KUmMLru_jv8oOFrxSaMdUCx9AA&s",
    "Clash of the Stars 5" : "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8ttztzwgHA7aeyP9Pr4Qh81mG2rMywjeOMw&s",
    "Clash of the Stars 6" : "https://vyhraj.sk/wp-content/uploads/2023/09/Clash-of-the-Stars-6.jpg",
    "Clash of the Stars 7" : "https://www.kurzovesazeni.com/wp-content/uploads/2023/12/Snimek-obrazovky-2023-12-13-v-11.37.05.webp",
    "Clash of the Stars 8" : "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQabKJyzxTRmAKS-gVBeqAhJigY-eFGD-ld9w&s",
    "Clash of the Stars 9" : "https://www.betarena.sk/obrazek/66d3001d3d239/clash-9.jpg",
    "Clash of the Stars 10" : "https://sportovniprogram.cz/getfile.aspx?id_file=70193335"
}

# Connect to Google Sheets and fetch data
conn = st.connection('gsheets', type=GSheetsConnection)
df_zapasy = conn.read(worksheet='Zápasy')
df_zapasy = df_zapasy.loc[:, ~df_zapasy.columns.str.contains('^Unnamed')]
df_zapasy = df_zapasy.dropna(how='all')

# Function to update query params
def update_query_params_turnaj(selected_turnaj):
    st.experimental_set_query_params(turnaj=selected_turnaj)

# Get query parameters
query_params = st.experimental_get_query_params()
selected_turnaj_query = query_params.get("turnaj", [None])[0]

# Get unique tournament names
turnaj_options = df_zapasy['Nazov_turnaj'].unique().tolist()

# Tournament selection
selected_turnaj = st.selectbox(
    "Choose a tournament:",
    turnaj_options,
    index=turnaj_options.index(selected_turnaj_query) if selected_turnaj_query in turnaj_options else 0,
    key='turnaj_select',
    on_change=lambda: update_query_params_turnaj(st.session_state.turnaj_select)
)

if selected_turnaj and selected_turnaj in tournament_images:
    image_url = tournament_images[selected_turnaj]
    st.markdown(
        f'<div style="text-align: center;"><img src="{image_url}" width="300" height="200"></div>',
        unsafe_allow_html=True
    )

ttt = conn.read(worksheet='Turnaje')
ttt = ttt.loc[:, ~ttt.columns.str.contains('^Unnamed')]
ttt = ttt.dropna(how='all')
ttt = ttt[ttt['Nazov_turnaj'] == selected_turnaj]

hala = ttt['Hala'].values[0]
miesto = ttt['Miesto'].values[0]
nn = ttt['Nazov_neoficialny'].values[0]

    # Display 'Hala' and 'Miesto' below the image
st.markdown(
        f"""
        **Nazov:** <span style="color:#b2b24c">{selected_turnaj}</span><br>
        **Hala:** <span style="color:#b2b24c">{hala}</span><br>
        **Miesto:** <span style="color:#b2b24c">{miesto}</span>
        """,
        unsafe_allow_html=True
    )


# Function to convert string representations of lists to readable strings
def convert_list_string_to_string(value):
    if isinstance(value, str) and '[' in value and ']' in value:
        # Strip the brackets and split the string by commas
        value = value[1:-1]  # remove square brackets
        elements = value.split(',')
        # Remove extra spaces and join with 'and'
        return [elem.strip().strip("'\"") for elem in elements]
    return [value]

# Function to generate HTML table with conditional formatting
def df_to_html_table(df):
    # Define custom styles
    fighter_columns_style = "width: 15%; text-align: center;"  # 15% wider and centered
    narrow_columns_style = "width: 7%; text-align: center;"  # Narrow width and centered
    
    # Define styles for specific columns
    column_styles = {
        'Fighter 1': fighter_columns_style,
        'Fighter 2': fighter_columns_style,
        'Method': narrow_columns_style,
        'Round': narrow_columns_style,
        'Time': narrow_columns_style,
        'Disciplina': narrow_columns_style,
        'Vaha': narrow_columns_style
    }
    
    html = "<table border='1' style='border-collapse: collapse;'>"
    html += "<thead><tr>"
    
    for column in df.columns:
        if column not in ['Winner', 'Loser']:  # Hide Winner and Loser columns
            html += f"<th style='{column_styles.get(column, narrow_columns_style)}'>{column}</th>"
    
    html += "</tr></thead>"
    html += "<tbody>"
    
    for _, row in df.iterrows():
        fighter_1_list = convert_list_string_to_string(row['Fighter 1'])
        fighter_2_list = convert_list_string_to_string(row['Fighter 2'])
        winner_list = convert_list_string_to_string(row['Winner'])
        loser_list = convert_list_string_to_string(row['Loser'])
        
        # Determine the result type
        if 'DRAW' in winner_list:
            result_type = 'DRAW'
        elif 'CANCELLED' in winner_list or 'NC' in winner_list:
            result_type = 'CANCELLED'
        else:
            result_type = None
        
        # Create colored fighter names with links
        fighter_1_colored = []
        fighter_2_colored = []

        for fighter in fighter_1_list:
            color = 'black'
            if result_type == 'DRAW':
                color = 'yellow'
            elif result_type in ['CANCELLED', 'NC']:
                color = 'grey'
            elif fighter in winner_list:
                color = 'green'
            elif fighter in loser_list:
                color = 'red'
            
            fighter_1_colored.append(f"<a href='/fighters?fighter={fighter}' style='color: {color}; text-decoration: none;'>{fighter}</a>")
        
        for fighter in fighter_2_list:
            color = 'black'
            if result_type == 'DRAW':
                color = 'yellow'
            elif result_type in ['CANCELLED', 'NC']:
                color = 'grey'
            elif fighter in winner_list:
                color = 'green'
            elif fighter in loser_list:
                color = 'red'
            
            fighter_2_colored.append(f"<a href='/fighters?fighter={fighter}' style='color: {color}; text-decoration: none;'>{fighter}</a>")
        
        # Handle death matches where Fighter 1 is the same as Fighter 2
        if ' and ' in ' '.join(fighter_1_list) and ' and ' in ' '.join(fighter_2_list):
            fighters = list(set(fighter_1_list + fighter_2_list))
            winners = set(winner_list)
            losers = set(loser_list)
            fighter_1_colored = []
            fighter_2_colored = []

            for fighter in fighters:
                color = 'black'
                if fighter in winners:
                    color = 'green'
                elif fighter in losers:
                    color = 'red'
                
                fighter_1_colored.append(f"<a href='/fighters?fighter={fighter}' style='color: {color}; text-decoration: none;'>{fighter}</a>")
                fighter_2_colored.append(f"<a href='/fighters?fighter={fighter}' style='color: {color}; text-decoration: none;'>{fighter}</a>")

            fighter_1 = ' and '.join(fighter_1_colored)
            fighter_2 = ' and '.join(fighter_2_colored)
        else:
            fighter_1 = ' and '.join(fighter_1_colored)
            fighter_2 = ' and '.join(fighter_2_colored)
        
        try:
            rr = int(row['Round'])
        except:
            rr = None
        html += "<tr>"
        html += f"<td style='{fighter_columns_style}'>{fighter_1}</td>"
        html += f"<td style='{fighter_columns_style}'>{fighter_2}</td>"
        html += f"<td style='{narrow_columns_style}'>{row['Method']}</td>"
        html += f"<td style='{narrow_columns_style}'>{rr}</td>"
        html += f"<td style='{narrow_columns_style}'>{row['Time']}</td>"
        html += f"<td style='{narrow_columns_style}'>{row['Disciplina']}</td>"
        html += f"<td style='{narrow_columns_style}'>{row['Vaha']}</td>"  # Add Vaha column
        html += "</tr>"
    
    html += "</tbody></table>"
    return html

# Filter data based on selected tournament
if selected_turnaj:
    df_zapasy_filtered = df_zapasy[df_zapasy['Nazov_turnaj'] == selected_turnaj]
    
    # Process data to handle edge cases
    def process_fight_result(row):
        if row['DRAW'] == 1:
            return 'DRAW', 'DRAW'
        elif row['CANCELLED'] == 1:
            return 'CANCELLED', 'CANCELLED'
        elif row['NO_CONTEST'] == 1:
            return 'NC', 'NC'
        else:
            return row['W'], row['L']

    # Apply edge case logic
    df_zapasy_filtered[['Winner', 'Loser']] = df_zapasy_filtered.apply(
        lambda row: pd.Series(process_fight_result(row)), axis=1
    )

    # Create table with Fighter 1, Fighter 2, and other details
    result_table = pd.DataFrame({
        'Fighter 1': df_zapasy_filtered['Zapasnik1'],
        'Fighter 2': df_zapasy_filtered['Zapasnik2'],
        'Winner': df_zapasy_filtered['Winner'],
        'Loser': df_zapasy_filtered['Loser'],
        'Method': df_zapasy_filtered['Metoda'],
        'Round': df_zapasy_filtered['Kolo'],
        'Time': df_zapasy_filtered['Čas'],
        'Disciplina': df_zapasy_filtered['Disciplina'],
        'Vaha': df_zapasy_filtered['Vaha']
    })

    # Convert the DataFrame to HTML
    html_table = df_to_html_table(result_table)
    
    # Render the HTML table using markdown
    st.markdown(html_table, unsafe_allow_html=True)
