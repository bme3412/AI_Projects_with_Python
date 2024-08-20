import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import time
from tqdm import tqdm
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_nfl_roster(url, session):
    try:
        response = session.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching the webpage: {e}")
        return pd.DataFrame(), pd.DataFrame()
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract coaching information
    coaching_info = {}
    info_elements = soup.find_all('p', class_='')
    for element in info_elements:
        strong_tag = element.find('strong')
        if strong_tag:
            key = strong_tag.text.strip(':')
            value = element.find('a').text if element.find('a') else element.text.replace(strong_tag.text, '').strip()
            coaching_info[key] = value

    # Extract player information
    players = []
    roster_div = soup.find('div', id='all_roster')
    if roster_div:
        commented_html = roster_div.find(string=lambda text: isinstance(text, Comment))
        if commented_html:
            roster_soup = BeautifulSoup(commented_html, 'html.parser')
            roster_table = roster_soup.find('table', id='roster')
            if roster_table:
                rows = roster_table.find_all('tr')
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all(['th', 'td'])
                    if len(cols) >= 13:
                        player = {
                            'No.': cols[0].text.strip(),
                            'Player': cols[1].text.strip(),
                            'Age': cols[2].text.strip(),
                            'Pos': cols[3].text.strip(),
                            'G': cols[4].text.strip(),
                            'GS': cols[5].text.strip(),
                            'Wt': cols[6].text.strip(),
                            'Ht': cols[7].text.strip(),
                            'College/Univ': cols[8].text.strip(),
                            'BirthDate': cols[9].text.strip(),
                            'Yrs': cols[10].text.strip(),
                            'AV': cols[11].text.strip(),
                            'Drafted': cols[12].text.strip()
                        }
                        players.append(player)

    # Create DataFrames
    coaching_df = pd.DataFrame([coaching_info])
    players_df = pd.DataFrame(players)

    return coaching_df, players_df

def exponential_backoff(attempt):
    return min(60, 2 ** attempt + random.uniform(0, 1))

def main():
    base_url = "https://www.pro-football-reference.com/teams/{team}/{year}_roster.htm"
    
    teams = ['chi', 'gnb', 'det', 'min', 'dal', 'nyg', 'phi', 'was', 'atl', 'car', 'nor', 'tam',
             'ari', 'lar', 'sfo', 'sea', 'buf', 'mia', 'nwe', 'nyj', 'bal', 'cin', 'cle', 'pit',
             'htx', 'clt', 'jax', 'oti', 'den', 'kan', 'lac', 'rai']
    
    seasons = range(2018, 2024)  # 2018 to 2023

    all_coaching_data = []
    all_player_data = []

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    for team in tqdm(teams, desc="Teams"):
        for year in tqdm(seasons, desc=f"Seasons for {team}", leave=False):
            url = base_url.format(team=team, year=year)
            
            attempt = 0
            while attempt < 5:  # Max 5 attempts per URL
                try:
                    coaching_info, players_info = scrape_nfl_roster(url, session)
                    
                    if not coaching_info.empty:
                        coaching_info['Team'] = team
                        coaching_info['Season'] = year
                        all_coaching_data.append(coaching_info)
                    
                    if not players_info.empty:
                        players_info['Team'] = team
                        players_info['Season'] = year
                        all_player_data.append(players_info)
                    
                    # Successful scrape, wait before next request
                    time.sleep(random.uniform(3, 5))  # Random delay between 3 and 5 seconds
                    break  # Exit the while loop if successful
                
                except requests.exceptions.RequestException as e:
                    logging.warning(f"Request failed for {url}: {e}")
                    backoff_time = exponential_backoff(attempt)
                    logging.info(f"Backing off for {backoff_time:.2f} seconds")
                    time.sleep(backoff_time)
                    attempt += 1
            
            if attempt == 5:
                logging.error(f"Failed to scrape {url} after 5 attempts")

    # Combine all data
    combined_coaching_df = pd.concat(all_coaching_data, ignore_index=True)
    combined_players_df = pd.concat(all_player_data, ignore_index=True)

    # Save to CSV
    combined_coaching_df.to_csv('nfl_coaching_data_2018_2023.csv', index=False)
    combined_players_df.to_csv('nfl_players_data_2018_2023.csv', index=False)

    logging.info("Data scraping complete. Results saved to CSV files.")

if __name__ == "__main__":
    main()