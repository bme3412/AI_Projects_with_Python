import requests
from bs4 import BeautifulSoup, Comment
import pandas as pd
import re

def scrape_nfl_roster(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return pd.DataFrame(), pd.DataFrame()

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract coaching information
    coaching_info = {}
    info_elements = soup.find_all('p', class_='')
    print(f"Number of info elements found: {len(info_elements)}")
    for element in info_elements:
        strong_tag = element.find('strong')
        if strong_tag:
            key = strong_tag.text.strip(':')
            value = element.find('a').text if element.find('a') else element.text.replace(strong_tag.text, '').strip()
            coaching_info[key] = value
    
    print("Coaching info extracted:", coaching_info)

    # Extract player information
    players = []
    roster_div = soup.find('div', id='all_roster')
    if roster_div:
        commented_html = roster_div.find(text=lambda text: isinstance(text, Comment))
        if commented_html:
            roster_soup = BeautifulSoup(commented_html, 'html.parser')
            roster_table = roster_soup.find('table', id='roster')
            if roster_table:
                rows = roster_table.find_all('tr')
                print(f"Number of rows in roster table: {len(rows)}")
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
            else:
                print("Roster table not found in the commented HTML.")
        else:
            print("Commented HTML not found in the roster div.")
    else:
        print("Roster div not found.")

    if not players:
        print("No player data extracted. Here's a sample of the HTML:")
        print(soup.prettify()[:1000])  # Print first 1000 characters of the HTML

    # Create DataFrames
    coaching_df = pd.DataFrame([coaching_info])
    players_df = pd.DataFrame(players)

    return coaching_df, players_df

def main():
    url = "https://www.pro-football-reference.com/teams/chi/2024_roster.htm"
    coaching_info, players_info = scrape_nfl_roster(url)

    # Set display options for pandas
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    print("\nCoaching Information DataFrame:")
    print(coaching_info.to_string(index=False))

    print("\nPlayers Information DataFrame:")
    print(players_info.to_string(index=False))

    # Optionally, save to CSV
    coaching_info.to_csv('coaching_info.csv', index=False)
    players_info.to_csv('players_info.csv', index=False)

if __name__ == "__main__":
    main()