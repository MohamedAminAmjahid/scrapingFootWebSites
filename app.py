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
    chrome_driver_path = './driver/chromedriver.exe'
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
        'Real Madrid': 'https://datamb.football/Real_Madrid_Team_stats/',
        'Manchester United': 'https://datamb.football/Manchester_United_Team_stats/',
        'Liverpool': 'https://datamb.football/Liverpool_Team_stats/'
    }
    
    team_url = team_urls.get(team_name)

    # Your scraping logic here using Selenium and BeautifulSoup
    # Example scraping for "Barcelona"
    chrome_driver_path = './driver/chromedriver.exe'

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


team_urls = {
    'Manchester United': 'https://www.goal.com/en/team/manchester-united/fixtures-results/6eqit8ye8aomdsrrq0hk3v7gh',
    'Chelsea': 'https://www.goal.com/en/team/chelsea/fixtures-results/9q0arba2kbnywth8bkxlhgmdr',
    'Liverpool': 'https://www.goal.com/en/team/liverpool/fixtures-results/c8h9bw1l82s06h77xxrelzhur',
    'Real Madrid' : 'https://www.goal.com/en/team/real-madrid/fixtures-results/3kq9cckrnlogidldtdie2fkbl',
    'Paris Saint-Germain' : 'https://www.goal.com/en/team/paris-saint-germain/fixtures-results/2b3mar72yy8d6uvat1ka6tn3r',
    'Barcelona' : 'https://www.goal.com/en/team/barcelona/fixtures-results/agh9ifb2mw3ivjusgedj7c3fe',
    'Bayern Munich' : 'https://www.goal.com/en/team/bayern-munich/fixtures-results/apoawtpvac4zqlancmvw4nk4o'
}

def scrape_matches(team_url):
    # Spécifiez le chemin de votre ChromeDriver
    chrome_driver_path = './driver/chromedriver.exe'

    # Configurer ChromeDriver avec Service
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    # Ouvrir la page des résultats de l'équipe
    driver.get(team_url)

    # Attendre que le contenu se charge
    time.sleep(5)

    # Obtenir le code source de la page après le rendu JavaScript
    page_source = driver.page_source

    # Analyser le code source avec BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Trouver toutes les sections correspondant aux mois
    months_sections = soup.find_all('div', class_='month-list_month-list__fRz5W')

    all_matches = []
    
    if months_sections:
        # Parcourir chaque section de mois
        for month_section in months_sections:
            # Trouver tous les matchs dans ce mois
            for match_row in month_section.find_all('div', class_='match_match__uW3tQ'):
                home_team = match_row.find('div', {'aria-label': 'Team a'}).text.strip()
                away_team = match_row.find('div', {'aria-label': 'Team b'}).text.strip()
                
                # Vérifier si le score est présent
                score_element = match_row.find('span', {'aria-label': 'Score'})
                if score_element:
                    score = score_element.text.strip()
                else:
                    # Si le score n'est pas disponible, chercher l'heure de début
                    start_time_element = match_row.find('time', {'aria-label': 'Start time'})
                    if start_time_element:
                        score = f"Start time: {start_time_element.text.strip()}"
                    else:
                        score = "N/A"

                date = match_row.find('time', class_='match_match-date__7tjL0').text.strip()
                
                # Ajouter les informations du match à la liste
                all_matches.append({
                    'Date': date,
                    'Home Team': home_team,
                    'Score': score,
                    'Away Team': away_team
                })

    driver.quit()
    
    return all_matches

def analyze_home_away_performance(matches, team_name):
    home_wins = home_draws = home_losses = 0
    away_wins = away_draws = away_losses = 0

    for match in matches:
        if ' : ' in match['Score']:  # Si le match est terminé et un score est disponible
            home_score, away_score = map(int, match['Score'].split(' : '))

            # Si l'équipe est à domicile
            if match['Home Team'] == team_name:
                if home_score > away_score:
                    home_wins += 1
                elif home_score == away_score:
                    home_draws += 1
                else:
                    home_losses += 1

            # Si l'équipe est à l'extérieur
            elif match['Away Team'] == team_name:
                if away_score > home_score:
                    away_wins += 1
                elif away_score == home_score:
                    away_draws += 1
                else:
                    away_losses += 1

    # Résumé des performances
    return {
        'Home Wins': home_wins,
        'Home Draws': home_draws,
        'Home Losses': home_losses,
        'Away Wins': away_wins,
        'Away Draws': away_draws,
        'Away Losses': away_losses,
    }


def plot_home_away_performance(home_away_performance, team_name):
    categories = ['Wins', 'Draws', 'Losses']
    home_values = [
        home_away_performance['Home Wins'],
        home_away_performance['Home Draws'],
        home_away_performance['Home Losses']
    ]
    away_values = [
        home_away_performance['Away Wins'],
        home_away_performance['Away Draws'],
        home_away_performance['Away Losses']
    ]

    fig, ax = plt.subplots()

    # Set dark background and white text
    fig.patch.set_facecolor('#000000')  # Black background
    ax.set_facecolor('#000000')  # Black background for plot
    ax.tick_params(axis='x', colors='white')  # White x-tick labels
    ax.tick_params(axis='y', colors='white')  # White y-tick labels
    ax.spines['bottom'].set_color('white')  # White x-axis line
    ax.spines['left'].set_color('white')  # White y-axis line
    ax.xaxis.label.set_color('white')  # X-axis label color
    ax.yaxis.label.set_color('white')  # Y-axis label color
    ax.title.set_color('white')  # Title color

    bar_width = 0.35
    index = range(len(categories))

    bars_home = ax.bar(index, home_values, bar_width, label='Home', color='blue')
    bars_away = ax.bar([i + bar_width for i in index], away_values, bar_width, label='Away', color='red')

    ax.set_xlabel('Category', color='white')
    ax.set_ylabel('Number of Matches', color='white')
    ax.set_title(f'Home vs Away Performance - {team_name}', color='white')
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(categories, color='white')
    ax.legend()

    # Assurez-vous que le répertoire 'static' existe
    if not os.path.exists('static'):
        os.makedirs('static')

    image_path = f'static/performance_{team_name}.png'
    plt.tight_layout()
    plt.savefig(image_path, facecolor=fig.get_facecolor())  # Save with the black background
    plt.close()

    return image_path



@app.route('/team_analysis', methods=['GET', 'POST'])
def team_analysis():
    team = 'Manchester United'
    matches = scrape_matches(team_urls[team])

    if request.method == 'POST':
        team = request.form['team']
        if team in team_urls:
            team_url = team_urls[team]
            matches = scrape_matches(team_url)

    # Analyze home and away performance
    home_away_performance = analyze_home_away_performance(matches, team)

    # Generate the performance graphs
    performance_image_path = plot_home_away_performance(home_away_performance, team)

    # Convert matches to Pandas DataFrame for table display
    df = pd.DataFrame(matches) if matches else pd.DataFrame()
    tables_html = df.to_html(classes='data', header="true", index=False).replace('\n', '')

    return render_template('team_analysis.html', team=team, tables=tables_html, team_urls=team_urls,
                           home_away_performance=home_away_performance, performance_image=performance_image_path)



TEAMS_LEAGUE_URLS = {
    'La Liga': 'https://www.goal.com/en/team/barcelona/table/agh9ifb2mw3ivjusgedj7c3fe',
    'Premier League' : 'https://www.goal.com/en/premier-league/table/2kwbbcootiqqgmrzs6o5inle5',
    'Bundesliga' : 'https://www.goal.com/en/bundesliga/6by3h89i2eykc341oz7lv1ddd'
    # Add more leagues here if needed
}

# Define the local storage path for the scraped data (new data path)
NEW_DATA_DIR = 'new_scraped_data'

# Create the new data directory if it doesn't exist
if not os.path.exists(NEW_DATA_DIR):
    os.makedirs(NEW_DATA_DIR)

def save_new_to_local(df, filename):
    """ Save a DataFrame as a JSON file locally (for the new functionality) """
    filepath = os.path.join(NEW_DATA_DIR, filename)
    df.to_json(filepath, orient='records')

def load_new_from_local(filename):
    """ Load data from a local JSON file into a DataFrame (for the new functionality) """
    filepath = os.path.join(NEW_DATA_DIR, filename)
    if os.path.exists(filepath):
        return pd.read_json(filepath)
    return None

# Function to scrape the league standings (team statistics) for the new functionality
def scrape_new_league_table(league):
    chrome_driver_path = './driver/chromedriver.exe'  # Path to your ChromeDriver
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    # Open the league standings webpage
    driver.get(TEAMS_LEAGUE_URLS[league])
    time.sleep(5)  # Wait for content to load

    # Get the page source after JavaScript has rendered the content
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Initialize a list to store the team data
    new_teams_data = []
    
    # Find the table body containing the teams and stats
    table_body = soup.find('tbody', {'aria-label': 'Table Body'})
    rows = table_body.find_all('tr')  # Get all rows
    
    for row in rows:
        team_name = row.find('span', class_='row_name__LRaHq').text.strip()  # Team name
        played = row.find('td', {'aria-label': 'Played'}).text.strip()
        wins = row.find('td', {'aria-label': 'Win'}).text.strip()
        draws = row.find('td', {'aria-label': 'Draw'}).text.strip()
        losses = row.find('td', {'aria-label': 'Lose'}).text.strip()
        goals_for = row.find('td', {'aria-label': 'Goals for'}).text.strip()
        goals_against = row.find('td', {'aria-label': 'Goals against'}).text.strip()
        goal_difference = row.find('td', {'aria-label': 'Goals difference'}).text.strip()
        points = row.find('td', {'aria-label': 'Points'}).text.strip()

        # Append the extracted data as a dictionary
        new_teams_data.append({
            'Team': team_name,
            'Played': int(played),
            'Wins': int(wins),
            'Draws': int(draws),
            'Losses': int(losses),
            'Goals For': int(goals_for),
            'Goals Against': int(goals_against),
            'Goal Difference': int(goal_difference),
            'Points': int(points),
        })

    driver.quit()

    # Convert the list to a DataFrame
    df = pd.DataFrame(new_teams_data)

    # Save the scraped data as a JSON file
    save_new_to_local(df, f'{league}_table.json')

    return df

def generate_pie_charts(df_table):
    teams = df_table['Team'].tolist()
    goals_scored = df_table['Goals For'].tolist()
    goals_conceded = df_table['Goals Against'].tolist()

    # Set up the figure with a dark gray background
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), facecolor='#2f2f2f')  # Dark gray background for the figure

    # Define distinct colors for the pie charts
    colors = plt.cm.tab20.colors

    # Goals Scored Distribution
    ax1.pie(goals_scored, labels=None, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 12, 'color': 'white'})
    ax1.set_title('Goals Scored Distribution', fontsize=16, color='white')
    ax1.legend(teams, loc="best", fontsize=10, bbox_to_anchor=(1, 0, 0.5, 1), facecolor='#2f2f2f', edgecolor='white', labelcolor='white')

    # Goals Conceded Distribution
    ax2.pie(goals_conceded, labels=None, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 12, 'color': 'white'})
    ax2.set_title('Goals Conceded Distribution', fontsize=16, color='white')
    ax2.legend(teams, loc="best", fontsize=10, bbox_to_anchor=(1, 0, 0.5, 1), facecolor='#2f2f2f', edgecolor='white', labelcolor='white')

    # Save the pie charts to a base64 string with dark gray background
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())  # Use figure's background color
    img.seek(0)
    pie_chart_data = base64.b64encode(img.getvalue()).decode('utf8')
    img.close()

    return pie_chart_data

# Additional imports for boxplot generation
import seaborn as sns

def generate_team_comparison_histogram(df_table):
    teams = df_table['Team'].tolist()
    goals_for = df_table['Goals For'].tolist()
    goals_against = df_table['Goals Against'].tolist()

    # Set the figure size and background color
    fig, ax = plt.subplots(figsize=(14, 6), facecolor='#2f2f2f')

    # Create the bar positions for each team
    bar_width = 0.35  # Width of the bars
    bar_positions = range(len(teams))

    # Plot "Goals For" bars
    ax.bar(bar_positions, goals_for, width=bar_width, label='Goals For', color='skyblue', edgecolor='white')

    # Plot "Goals Against" bars just to the right of "Goals For"
    ax.bar([pos + bar_width for pos in bar_positions], goals_against, width=bar_width, label='Goals Against', color='lightcoral', edgecolor='white')

    # Customize axis labels and title
    ax.set_title('Goals For and Goals Against by Team', fontsize=16, color='white')
    ax.set_xlabel('Teams', fontsize=12, color='white')
    ax.set_ylabel('Goals', fontsize=12, color='white')

    # Set x-tick labels to the team names
    ax.set_xticks([pos + bar_width / 2 for pos in bar_positions])
    ax.set_xticklabels(teams, rotation=90, fontsize=10, color='white')

    # Customize background and labels
    ax.set_facecolor('#2f2f2f')  # Dark gray background
    ax.tick_params(axis='y', colors='white')

    # Add a legend
    ax.legend(loc='upper right', fontsize=12, facecolor='#2f2f2f', edgecolor='white', labelcolor='white')

    # Save the figure as an image
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
    img.seek(0)
    histogram_data = base64.b64encode(img.getvalue()).decode('utf8')
    img.close()

    return histogram_data


@app.route('/league_table', methods=['GET', 'POST'])
def new_league_table():
    league = request.form.get('league', 'La Liga')  # Default to 'La Liga'
    metric = request.form.get('metric', 'Goals For')  # Default metric

    # Load the data for the selected league
    df_table = load_new_from_local(f'{league}_table.json')

    if df_table is None:
        df_table = scrape_new_league_table(league)

    total_goals = df_table['Goals For'].sum()
    total_points = df_table['Points'].sum()

    # Generate pie charts
    pie_chart_data = generate_pie_charts(df_table)
    
    # Generate team comparison histogram for "Goals For" and "Goals Against"
    histogram_data = generate_team_comparison_histogram(df_table)

    # Convert DataFrame to HTML for rendering in the template
    league_table_html = df_table.to_html(classes='data', header="true", index=False).replace('\n', '')

    return render_template('league_table.html',
                           league_table=league_table_html,
                           total_goals=total_goals,
                           total_points=total_points,
                           pie_chart_data=pie_chart_data,
                           boxplot_data=histogram_data,  # Update to the new team comparison histogram
                           selected_league=league,
                           selected_metric=metric,
                           leagues=TEAMS_LEAGUE_URLS.keys(),
                           metrics=['Goals For', 'Goals Against', 'Points'])



@app.route('/')
def menu():
    return render_template('menu.html')
if __name__ == "__main__":
    app.run(debug=True)