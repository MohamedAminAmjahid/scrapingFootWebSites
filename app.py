from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import pandas as pd
import time
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Dictionary mapping leagues to their respective URLs
LEAGUE_URLS = {
    'La Liga': 'https://www.goal.com/en/laliga/top-players/34pl8szyvrbwcmfkuocjm3r6t',
    'Premier League': 'https://www.goal.com/en/premier-league/top-players/2kwbbcootiqqgmrzs6o5inle5',
    'Bundesliga': 'https://www.goal.com/en/bundesliga/top-players/6by3h89i2eykc341oz7lv1ddd',
    'Serie A': 'https://www.goal.com/en/serie-a/top-players/1r097lpxe0xn03ihb7wi98kao'
}

# Define the local storage path for the scraped data
DATA_DIR = 'scraped_data'

# Create the data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def save_to_local(df, filename):
    """ Save a DataFrame as a JSON file locally """
    filepath = os.path.join(DATA_DIR, filename)
    df.to_json(filepath, orient='records')

def load_from_local(filename):
    """ Load data from a local JSON file into a DataFrame """
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        return pd.read_json(filepath)
    return None

# Function to scrape data and store it locally
def scrape_data(league):
    # Specify the path to your ChromeDriver
    chrome_driver_path = 'C:/Users/Amjahid Mohamed Amin/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe'

    # Set up ChromeDriver using Service
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    # Open the webpage based on the selected league
    driver.get(LEAGUE_URLS[league])

    # Give time for dynamic content to load
    time.sleep(5)

    # Get the page source after the JavaScript has rendered the content
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Initialize lists to store data
    top_scorers = []
    assists = []
    red_cards = []
    yellow_cards = []
    shots_on_target = []
    fouls_committed = []

    # Scraping logic for each section

    ## 1. Top Scorers
    top_scorers_section = soup.find('ul', class_='fco-top-players__list')
    if top_scorers_section:
        for scorer_row in top_scorers_section.find_all('li', class_='fco-top-players__list-item'):
            player_rank = scorer_row.find('span', class_='fco-top-player__order').text.strip()
            player_name = scorer_row.find('span', class_='fco-top-player__name').text.strip()
            player_goals = scorer_row.find('span', class_='fco-top-player__score').text.strip()
            top_scorers.append({'Rank': player_rank, 'Name': player_name, 'Goals': player_goals})

    ## 2. Assists
    assists_section = soup.find('h3', class_='fco-top-players__header', string="Assists").find_next('ul', class_='fco-top-players__list')
    if assists_section:
        for assist_row in assists_section.find_all('li', class_='fco-top-players__list-item'):
            assist_rank = assist_row.find('span', class_='fco-top-player__order').text.strip()
            assist_name = assist_row.find('span', class_='fco-top-player__name').text.strip()
            assist_count = assist_row.find('span', class_='fco-top-player__score').text.strip()
            assists.append({'Rank': assist_rank, 'Name': assist_name, 'Assists': assist_count})

    ## 3. Red Cards
    red_cards_section = soup.find('h3', class_='fco-top-players__header', string="Red cards").find_next('ul', class_='fco-top-players__list')
    if red_cards_section:
        for red_card_row in red_cards_section.find_all('li', class_='fco-top-players__list-item'):
            red_card_rank = red_card_row.find('span', class_='fco-top-player__order').text.strip()
            red_card_name = red_card_row.find('span', class_='fco-top-player__name').text.strip()
            red_card_count = red_card_row.find('span', class_='fco-top-player__score').text.strip()
            red_cards.append({'Rank': red_card_rank, 'Name': red_card_name, 'Red Cards': red_card_count})

    ## 4. Yellow Cards
    yellow_cards_section = soup.find('h3', class_='fco-top-players__header', string="Yellow cards").find_next('ul', class_='fco-top-players__list')
    if yellow_cards_section:
        for yellow_card_row in yellow_cards_section.find_all('li', class_='fco-top-players__list-item'):
            yellow_card_rank = yellow_card_row.find('span', class_='fco-top-player__order').text.strip()
            yellow_card_name = yellow_card_row.find('span', class_='fco-top-player__name').text.strip()
            yellow_card_count = yellow_card_row.find('span', class_='fco-top-player__score').text.strip()
            yellow_cards.append({'Rank': yellow_card_rank, 'Name': yellow_card_name, 'Yellow Cards': yellow_card_count})

    ## 5. Shots on Target
    shots_section = soup.find('h3', class_='fco-top-players__header', string="Shots on target").find_next('ul', class_='fco-top-players__list')
    if shots_section:
        for shot_row in shots_section.find_all('li', class_='fco-top-players__list-item'):
            shot_rank = shot_row.find('span', class_='fco-top-player__order').text.strip()
            shot_name = shot_row.find('span', class_='fco-top-player__name').text.strip()
            shot_count = shot_row.find('span', class_='fco-top-player__score').text.strip()
            shots_on_target.append({'Rank': shot_rank, 'Name': shot_name, 'Shots on Target': shot_count})

    ## 6. Fouls Committed
    fouls_section = soup.find('h3', class_='fco-top-players__header', string="Fouls committed").find_next('ul', class_='fco-top-players__list')
    if fouls_section:
        for foul_row in fouls_section.find_all('li', class_='fco-top-players__list-item'):
            foul_rank = foul_row.find('span', class_='fco-top-player__order').text.strip()
            foul_name = foul_row.find('span', class_='fco-top-player__name').text.strip()
            foul_count = foul_row.find('span', class_='fco-top-player__score').text.strip()
            fouls_committed.append({'Rank': foul_rank, 'Name': foul_name, 'Fouls Committed': foul_count})

    # Close the browser after scraping
    driver.quit()

    # Create DataFrames for each category
    df_scorers = pd.DataFrame(top_scorers)
    df_assists = pd.DataFrame(assists)
    df_redcards = pd.DataFrame(red_cards)
    df_yellowcards = pd.DataFrame(yellow_cards)
    df_shots = pd.DataFrame(shots_on_target)
    df_fouls = pd.DataFrame(fouls_committed)

    # Save the scraped data as JSON files
    save_to_local(df_scorers, f'{league}_scorers.json')
    save_to_local(df_assists, f'{league}_assists.json')
    save_to_local(df_redcards, f'{league}_redcards.json')
    save_to_local(df_yellowcards, f'{league}_yellowcards.json')
    save_to_local(df_shots, f'{league}_shots.json')
    save_to_local(df_fouls, f'{league}_fouls.json')

    return df_scorers, df_assists, df_redcards, df_yellowcards, df_shots, df_fouls

# Define the route for the home page
@app.route('/topsoccers', methods=['GET', 'POST'])
def topsoccers():
    # Default league is La Liga
    league = request.form.get('league', 'La Liga')

    # Check if data exists locally for the selected league
    df_scorers = load_from_local(f'{league}_scorers.json')
    df_assists = load_from_local(f'{league}_assists.json')
    df_redcards = load_from_local(f'{league}_redcards.json')
    df_yellowcards = load_from_local(f'{league}_yellowcards.json')
    df_shots = load_from_local(f'{league}_shots.json')
    df_fouls = load_from_local(f'{league}_fouls.json')

    # If data is not found locally, scrape and save it
    if df_scorers is None or df_assists is None or df_redcards is None or df_yellowcards is None or df_shots is None or df_fouls is None:
        df_scorers, df_assists, df_redcards, df_yellowcards, df_shots, df_fouls = scrape_data(league)

    # Convert DataFrames to HTML
    scorers_html = df_scorers.to_html(classes='data', header="true", index=False).replace('\n', '').replace('[', '').replace(']', '')
    assists_html = df_assists.to_html(classes='data', header="true", index=False).replace('\n', '').replace('[', '').replace(']', '')
    redcards_html = df_redcards.to_html(classes='data', header="true", index=False).replace('\n', '').replace('[', '').replace(']', '')
    yellowcards_html = df_yellowcards.to_html(classes='data', header="true", index=False).replace('\n', '').replace('[', '').replace(']', '')
    shots_html = df_shots.to_html(classes='data', header="true", index=False).replace('\n', '').replace('[', '').replace(']', '')
    fouls_html = df_fouls.to_html(classes='data', header="true", index=False).replace('\n', '').replace('[', '').replace(']', '')

    # Pass the data and the selected league to the template
    return render_template('topsoccers.html',
                            scorers_table=scorers_html,
                            assists_table=assists_html,
                            redcards_table=redcards_html,
                            yellowcards_table=yellowcards_html,
                            shots_table=shots_html,
                            fouls_table=fouls_html,
                            selected_league=league)

# Define the route for the stats page
@app.route('/stats')
@app.route('/stats', methods=['GET', 'POST'])
def stats():
    # Default league is La Liga
    league = request.form.get('league', 'La Liga')

    # Load data from local storage
    df_scorers = load_from_local(f'{league}_scorers.json')
    df_shots = load_from_local(f'{league}_shots.json')

    # Ensure data exists
    if df_scorers is None or df_shots is None:
        df_scorers, df_shots = scrape_data(league)

    # Merge goals and shots on target
    df_efficiency = pd.merge(df_scorers, df_shots, on='Name', how='inner')

    # Calculate the efficiency
    df_efficiency['Efficiency'] = (df_efficiency['Goals'].astype(float) / df_efficiency['Shots on Target'].astype(float)) * 100

    # Sort by efficiency
    df_efficiency_sorted = df_efficiency.sort_values(by='Efficiency', ascending=False)

    # Convert the efficiency DataFrame to HTML
    efficiency_table = df_efficiency_sorted[['Name', 'Efficiency']].to_html(classes='data', header="true", index=False)

    # Prepare data for the chart
    efficiency_names = df_efficiency_sorted['Name'].tolist()
    efficiency_values = df_efficiency_sorted['Efficiency'].tolist()

    # Pass the efficiency table, chart data, and selected league to the template
    return render_template('stats.html',
                           efficiency_table=efficiency_table,
                           efficiency_names=efficiency_names,
                           efficiency_values=efficiency_values,
                           selected_league=league)


# Function to calculate efficiency for a league and return the best player
def get_best_shooter(league):
    # Load the locally saved data for shots and scorers (if not present, scrape it)
    df_scorers = load_from_local(f'{league}_scorers.json')
    df_shots = load_from_local(f'{league}_shots.json')

    # Ensure data exists
    if df_scorers is None or df_shots is None:
        df_scorers, df_shots = scrape_data(league)

    # Merge goals and shots on target
    df_efficiency = pd.merge(df_scorers, df_shots, on='Name', how='inner')

    # Calculate the efficiency
    df_efficiency['Efficiency'] = (df_efficiency['Goals'].astype(float) / df_efficiency['Shots on Target'].astype(float)) * 100

    # Sort by efficiency and return the best player
    best_player = df_efficiency.sort_values(by='Efficiency', ascending=False).iloc[0]
    return best_player

@app.route('/compare-leagues')
def compare_leagues():
    # List of leagues to compare
    leagues = ['La Liga', 'Premier League', 'Bundesliga', 'Serie A']
    
    # Store best shooters from each league
    best_shooters = []

    for league in leagues:
        best_player = get_best_shooter(league)
        best_shooters.append({
            'league': league,
            'name': best_player['Name'],
            'efficiency': best_player['Efficiency']
        })

    # Create a bar chart for the best players' shooting precision across leagues
    fig, ax = plt.subplots()
    leagues = [shooter['league'] for shooter in best_shooters]
    efficiencies = [shooter['efficiency'] for shooter in best_shooters]
    names = [shooter['name'] for shooter in best_shooters]

    ax.barh(leagues, efficiencies, color='skyblue')
    for i in range(len(leagues)):
        ax.text(efficiencies[i] + 0.5, i, f'{names[i]} ({efficiencies[i]:.2f}%)', va='center', ha='left', fontsize=10)

    ax.set_xlabel('Shooting Efficiency (%)')
    ax.set_title('Best Shooter in Each League Based on Precision')

    # Save the plot to a string buffer
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('compare_leagues.html', graph_url=graph_url)

def parse_percentile(value):
    # Strip 'th percentile' and convert to float
    return float(value[0:2])
# Function to scrape team statistics
# Modify this function to scrape stats for different teams based on URL
def scrape_team_stats(team_name):
    # URLs for different teams
    team_urls = {
        'Barcelona': 'https://datamb.football/Barcelona_Team_stats/',
        'Real Madrid': 'https://datamb.football/RealMadrid_Team_stats/',
        'Manchester United': 'https://datamb.football/ManchesterUnited_Team_stats/',
        'Liverpool': 'https://datamb.football/Liverpool_Team_stats/'
    }
    
    team_url = team_urls.get(team_name)

    # Your scraping logic here using Selenium and BeautifulSoup
    # Example scraping for "Barcelona"
    chrome_driver_path = 'C:/Users/Amjahid Mohamed Amin/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe'

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    driver.get(team_url)
    time.sleep(5)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    try:
        # Scrape the performance stats here
        table = soup.find('table', class_='metrics-table')
        rows = table.find_all('tr')

        team_data = {
            'team_name': team_name,
            'Season': rows[2].find_all('td')[1].text.strip(),
            'League': rows[3].find_all('td')[1].text.strip(),
            'Goals': float(rows[4].find_all('td')[1].text.strip()[0:2]),
            'Attacking': float(rows[5].find_all('td')[1].text.strip()[0:2]),
            'Possession': float(rows[6].find_all('td')[1].text.strip()[0:2]),
            'Counters': float(rows[7].find_all('td')[1].text.strip()[0:2]),
            'Defending': float(rows[8].find_all('td')[1].text.strip()[0:2]),
            'Physicality': float(rows[9].find_all('td')[1].text.strip()[0:2]),
            'Pressing': float(rows[10].find_all('td')[1].text.strip()[0:2])
        }

        return team_data

    finally:
        driver.quit()

@app.route('/team_performance', methods=['GET', 'POST'])
def team_performance():
    # Get the selected team from the form
    if request.method == 'POST':
        selected_team = request.form.get('team', 'Barcelona')  # Default is 'Barcelona'
    else:
        selected_team = 'Barcelona'

    # Scrape the data for the selected team
    team_data = scrape_team_stats(selected_team)

    return render_template('team_performance.html', **team_data)


@app.route('/')
def menu():
    return render_template('menu.html')
if __name__ == "__main__":
    app.run(debug=True)
