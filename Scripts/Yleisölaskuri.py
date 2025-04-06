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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "fi-FI,fi;q=0.9"
    }
    
    # 1. Varmistetaan, että sivusto vastaa
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    # 2. Etsitään oikea taulukko uudella tavalla
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'table-stats'})  # Muuttunut luokan nimi!
    
    if not table:
        raise ValueError("Taulukkoa ei löytynyt sivustolta!")
    
    rows = table.find_all('tr', {'class': 'match-row'})  # Oikea rivien CSS-luokka
    
    print(f"Löytyi {len(rows)} otteluriviä")  # Debug-tuloste

    for row in rows:
        # 3. Etsitään oikeat sarakkeet
        date_cell = row.find('td', {'class': 'date'})
        teams_cell = row.find('td', {'class': 'teams'})
        result_cell = row.find('td', {'class': 'score'})
        audience_cell = row.find('td', {'class': 'attendance'})
        
        if not all([date_cell, teams_cell, result_cell, audience_cell]):
            continue
        
        # 4. Parsitaan yleisömäärä
        audience_text = audience_cell.get_text(strip=True)
        audience_match = re.search(r'\d+', audience_text.replace(' ', ''))
        if not audience_match:
            continue
            
        audience = int(audience_match.group())
        total_audiences.append(audience)
        
        # 5. Parsitaan tulos
        result_match = re.search(r'(\d+)\s*-\s*(\d+)', result_cell.get_text())
        if not result_match:
            continue
            
        home_goals, away_goals = map(int, result_match.groups())
        total_goals += home_goals + away_goals
        
        # 6. Erotellaan joukkueet
        home_team = teams_cell.find('span', {'class': 'home-team'}).get_text(strip=True)
        away_team = teams_cell.find('span', {'class': 'away-team'}).get_text(strip=True)
        
        # 7. Täytetään joukkueiden tiedot
        if home_team in teams:
            team_data[home_team]['Home']['audiences'].append(audience)
            team_data[home_team]['Home']['goals_scored'].append(home_goals)
            team_data[home_team]['Home']['goals_conceded'].append(away_goals)
            if (home_goals + away_goals) > 2.5:
                team_data[home_team]['Home']['over_2_5'] += 1
                
        if away_team in teams:
            team_data[away_team]['Away']['audiences'].append(audience)
            team_data[away_team]['Away']['goals_scored'].append(away_goals)
            team_data[away_team]['Away']['goals_conceded'].append(home_goals)
            if (home_goals + away_goals) > 2.5:
                team_data[away_team]['Away']['over_2_5'] += 1

    # 8. Kirjoitetaan raportti TURVALLISESTI
    file_path = os.path.join(os.path.dirname(__file__), '..', 'Yleisö2025.md')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# Veikkausliiga 2025 Yleisötilastot\n\n")
        f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
        
        # Yleistilastot
        total_games = len(total_audiences)
        f.write("## Yleiset tilastot\n")
        f.write(f"- Pelattuja otteluita: {total_games}\n")
        
        if total_games > 0:
            f.write(f"- Keskiyleisö: {sum(total_audiences)/total_games:.0f}\n")
            f.write(f"- Maalit per ottelu: {total_goals/total_games:.1f}\n")
            f.write(f"- Yli 2.5 maalia: {total_over_2_5_games/total_games:.1%}\n")
        else:
            f.write("- Ei pelattuja otteluita\n")
        
        # Joukkueet
        f.write("\n## Joukkuekohtaiset tilastot\n")
        for team in teams:
            home = team_data[team]['Home']
            away = team_data[team]['Away']
            
            f.write(f"\n### {team}\n")
            
            # Kotipelit
            f.write("#### Kotipelit\n")
            home_games = len(home['audiences'])
            if home_games > 0:
                f.write(f"- Keskiyleisö: {sum(home['audiences'])/home_games:.0f}\n")
                f.write(f"- Maalit: {sum(home['goals_scored'])}-{sum(home['goals_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {home['over_2_5']} ({home['over_2_5']/home_games:.1%})\n")
            else:
                f.write("- Ei kotipelejä\n")
            
            # Vieraspelit
            f.write("#### Vieraspelit\n")
            away_games = len(away['audiences'])
            if away_games > 0:
                f.write(f"- Keskiyleisö: {sum(away['audiences'])/away_games:.0f}\n")
                f.write(f"- Maalit: {sum(away['goals_scored'])}-{sum(away['goals_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {away['over_2_5']} ({away['over_2_5']/away_games:.1%})\n")
            else:
                f.write("- Ei vieraspelejä\n")

except Exception as e:
    print(f"KRIILLINEN VIRHE: {str(e)}")
    # Kirjoitetaan tyhjä raportti virhetilanteessa
    with open('Yleisö2025.md', 'w') as f:
        f.write("# Tilastojen päivitys epäonnistui\n")
        f.write(f"Virhe: {str(e)}")
    raise
