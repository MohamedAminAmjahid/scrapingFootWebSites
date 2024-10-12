from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

def parse_percentile(value):
    # Strip 'th percentile' and convert to float
    return float(value[0:2])

def scrape_team_stats(team_url):
    # Specify the path to your ChromeDriver
    chrome_driver_path = 'C:/Users/Amjahid Mohamed Amin/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe'  # Update this with your actual path

    # Set up the ChromeDriver using Service
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)

    # Open the webpage
    driver.get(team_url)

    # Wait for the page to fully load
    time.sleep(5)

    # Get the page source after JavaScript execution
    page_source = driver.page_source

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Dictionary to hold the scraped data
    team_data = {}

    try:
        # Locate the table with class "metrics-table"
        table = soup.find('table', class_='metrics-table')
        
        # Find all rows in the table
        rows = table.find_all('tr')

        # Scrape data from each row
        team_name = rows[0].find_all('td')[1].text.strip()  # Extract team name
        season = rows[2].find_all('td')[1].text.strip()  # Extract season
        league = rows[3].find_all('td')[1].text.strip()  # Extract league
        goals = parse_percentile(rows[4].find_all('td')[1].text.strip())
        attacking = parse_percentile(rows[5].find_all('td')[1].text.strip())
        possession = parse_percentile(rows[6].find_all('td')[1].text.strip())
        counters = parse_percentile(rows[7].find_all('td')[1].text.strip())
        defending = parse_percentile(rows[8].find_all('td')[1].text.strip())
        physicality = parse_percentile(rows[9].find_all('td')[1].text.strip())
        pressing = parse_percentile(rows[10].find_all('td')[1].text.strip())

        # Store the scraped data in the dictionary
        team_data = {
            'Team': team_name,
            'Season': season,
            'League': league,
            'Goals': goals,
            'Attacking': attacking,
            'Possession': possession,
            'Counters': counters,
            'Defending': defending,
            'Physicality': physicality,
            'Pressing': pressing
        }

        return team_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        # Close the browser
        driver.quit()

# The actual URL of the team page
team_url = 'https://datamb.football/Barcelona_Team_stats/'  # Replace with the actual URL
team_stats = scrape_team_stats(team_url)

# Display the extracted stats
if team_stats:
    print(team_stats)
else:
    print("Failed to scrape the data.")
