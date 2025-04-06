import os
import re
import requests
from bs4 import BeautifulSoup
import datetime

url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
teams = ["Ilves", "HJK", "FC Inter", "KuPS", "IFK Mariehamn", "FF Jaro", "KTP", "SJK", "VPS", "AC Oulu", "FC Haka", "IF Gnistan"]

team_data = {
    team: {
        'Home': {'audiences': [], 'goals_scored': [], 'goals_conceded': [], 'over_2_5': 0},
        'Away': {'audiences': [], 'goals_scored': [], 'goals_conceded': [], 'over_2_5': 0}
    } for team in teams
}

total_audiences = []
total_goals = 0
total_over_2_5_games = 0

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'stats-table'})  # Ota tarkka taulukon class nimi käyttöön
    table_rows = table.find_all('tr') if table else []
    
    print(f"Löydettiin {len(table_rows)} otteluriviä")  # Debug-tuloste

    for row in table_rows[1:]:  # Ohitetaan otsikkorivi
        cells = row.find_all('td')
        if len(cells) < 7:
            continue
            
        # Parsitaan tiedot uudella tavalla
        match_info = cells[2].get_text(strip=True)  # Oletetaan että pelitiedot ovat 3. sarakkeessa
        result = cells[3].get_text(strip=True)      # Tulos 4. sarakkeessa
        audience = cells[6].get_text(strip=True)    # Yleisömäärä 7. sarakkeessa
        
        # Debug-tuloste
        print(f"Käsitellään rivi: {match_info} | {result} | {audience}")

        # Tarkistetaan yleisömäärä
        audience_match = re.search(r'\d+', audience.replace(' ', ''))
        if not audience_match:
            continue
            
        audience_number = int(audience_match.group())
        total_audiences.append(audience_number)

        # Tarkistetaan tulos
        result_match = re.search(r'(\d+)\s*-\s*(\d+)', result)
        if not result_match:
            continue
            
        home_goals, away_goals = map(int, result_match.groups())
        total_goals += home_goals + away_goals
        if (home_goals + away_goals) > 2.5:
            total_over_2_5_games += 1

        # Erotellaan joukkueet
        if ' - ' in match_info:
            home_team, away_team = [t.strip() for t in match_info.split(' - ', 1)]
            
            # Kotijoukkueen tiedot
            if home_team in teams:
                team_data[home_team]['Home']['audiences'].append(audience_number)
                team_data[home_team]['Home']['goals_scored'].append(home_goals)
                team_data[home_team]['Home']['goals_conceded'].append(away_goals)
                if (home_goals + away_goals) > 2.5:
                    team_data[home_team]['Home']['over_2_5'] += 1
            
            # Vierasjoukkueen tiedot
            if away_team in teams:
                team_data[away_team]['Away']['audiences'].append(audience_number)
                team_data[away_team]['Away']['goals_scored'].append(away_goals)
                team_data[away_team]['Away']['goals_conceded'].append(home_goals)
                if (home_goals + away_goals) > 2.5:
                    team_data[away_team]['Away']['over_2_5'] += 1

    # Käsitellään tilastot
    total_games = len(total_audiences)
    file_path = os.path.join(os.path.dirname(__file__), '..', 'Yleisö2025.md')
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("# Veikkausliiga 2025 - Yleisötilastot\n\n")
        file.write(f"**Päivitetty:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Yleistilastot
        file.write("## Yleiset tilastot\n")
        file.write(f"- Pelatut ottelut: {total_games}\n")
        if total_games > 0:
            file.write(f"- Keskiyleisö: {sum(total_audiences)/total_games:.0f}\n")
            file.write(f"- Maalit per ottelu: {total_goals/total_games:.1f}\n")
            file.write(f"- Yli 2.5 maalia: {(total_over_2_5_games/total_games*100):.1f}%\n")
        else:
            file.write("- Ei pelattuja otteluita\n")
        
        # Joukkueet
        file.write("\n## Joukkueet\n")
        for team in teams:
            home = team_data[team]['Home']
            away = team_data[team]['Away']
            
            file.write(f"\n### {team}\n")
            file.write("**Kotipelit:**\n")
            if len(home['audiences']) > 0:
                file.write(f"- Keskiyleisö: {sum(home['audiences'])/len(home['audiences']):.0f}\n")
            else:
                file.write("- Ei kotipelejä\n")
            
            file.write("**Vieraspelit:**\n")
            if len(away['audiences']) > 0:
                file.write(f"- Keskiyleisö: {sum(away['audiences'])/len(away['audiences']):.0f}\n")
            else:
                file.write("- Ei vieraspelejä\n")

except Exception as e:
    print(f"Kriittinen virhe: {str(e)}")
    raise
