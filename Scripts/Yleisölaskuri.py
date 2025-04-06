import os
import re
import requests
from bs4 import BeautifulSoup
import datetime

# URL-osoite Veikkausliigan tilastoihin
url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"

# Päivitetyt joukkueet 2025 kauden mukaan
teams = ["Ilves", "HJK", "FC Inter", "KuPS", "IFK Mariehamn", "FF Jaro", "KTP", "SJK", "VPS", "AC Oulu", "FC Haka", "IF Gnistan"]

team_data = {
    team: {
        'Home': {'audiences': [], 'goals_scored': [], 'goals_conceded': [], 'over_2_5': 0},
        'Away': {'audiences': [], 'goals_scored': [], 'goals_conceded': [], 'over_2_5': 0}
    } for team in teams
}

# Alusta päämuuttujat
total_audiences = []
total_goals = 0
total_over_2_5_games = 0

try:
    # Haetaan data Veikkausliigan sivulta
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Tarkistetaan, että pyyntö onnistui
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table_rows = soup.find_all('tr')
    
    for row in table_rows:
        cells = row.find_all('td')
        if cells and len(cells) > 6:
            # Haetaan ottelun tiedot
            match_teams = cells[3].get_text(strip=True) if len(cells) > 3 else ""
            result_text = cells[5].get_text(strip=True) if len(cells) > 5 else ""
            audience_text = cells[6].get_text(strip=True) if len(cells) > 6 else ""
            
            # Tarkistetaan, että tekstit on saatu
            if not all([match_teams, result_text, audience_text]):
                continue
                
            # Haetaan tulos ja yleisömäärä
            result_match = re.search(r'(\d+)\s*[—-]\s*(\d+)', result_text)
            audience_match = re.search(r'(\d+)', audience_text)
            
            if not (result_match and audience_match):
                continue
                
            audience_number = int(audience_match.group(1))
            home_goals, away_goals = map(int, result_match.groups())
            
            # Lasketaan tilastot
            total_goals += home_goals + away_goals
            total_audiences.append(audience_number)
            if home_goals + away_goals > 2.5:
                total_over_2_5_games += 1
            
            # Erotellaan kotijoukkue ja vierasjoukkue
            if " - " in match_teams:
                home_team, away_team = [team.strip() for team in match_teams.split(" - ")]
                
                # Tallennetaan kotijoukkueen tiedot
                if home_team in teams:
                    team_data[home_team]['Home']['audiences'].append(audience_number)
                    team_data[home_team]['Home']['goals_scored'].append(home_goals)
                    team_data[home_team]['Home']['goals_conceded'].append(away_goals)
                    if home_goals + away_goals > 2.5:
                        team_data[home_team]['Home']['over_2_5'] += 1
                
                # Tallennetaan vierasjoukkueen tiedot
                if away_team in teams:
                    team_data[away_team]['Away']['audiences'].append(audience_number)
                    team_data[away_team]['Away']['goals_scored'].append(away_goals)
                    team_data[away_team]['Away']['goals_conceded'].append(home_goals)
                    if home_goals + away_goals > 2.5:
                        team_data[away_team]['Away']['over_2_5'] += 1
    
    # Lasketaan yhteenvetotilastot
    total_games = len(total_audiences)
    total_average_audience = sum(total_audiences) / total_games if total_games > 0 else 0
    total_average_goals = total_goals / total_games if total_games > 0 else 0
    total_over_2_5_percent = (total_over_2_5_games / total_games * 100) if total_games > 0 else 0
    
    # Tulostetaan tarkistuksia
    print(f"Yleisömäärät: {total_audiences}")
    print(f"Tehdyt maalit: {total_goals}")
    print(f"Yli 2.5 maalia peleissä: {total_over_2_5_games}")
    
    # Asetetaan tiedoston sijainti
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
    
    # Kirjoitetaan tulokset Markdown-tiedostoon
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("# Veikkausliiga 2025 - Yleisötilastot\n\n")
        file.write(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        file.write("## Kokonaistilastot\n\n")
        file.write(f"- **Kokonaisyleisömäärä:** {sum(total_audiences):,} katsojaa\n")
        
        # KORJAUS: Tarkistetaan onko total_games nolla ennen jakamista
        if total_games > 0:
            file.write(f"- **Keskimääräinen yleisö:** {total_average_audience:.0f} katsojaa/ottelu\n")
        else:
            file.write("- **Keskimääräinen yleisö:** 0 katsojaa/ottelu\n")
            
        file.write(f"- **Otteluita pelattu:** {total_games}\n")
        file.write(f"- **Maaleja yhteensä:** {total_goals}\n")
        
        # KORJAUS: Tarkistetaan onko total_games nolla ennen jakamista
        if total_games > 0:
            file.write(f"- **Maaleja per ottelu:** {total_average_goals:.2f}\n")
            file.write(f"- **Yli 2.5 maalia otteluissa:** {total_over_2_5_percent:.1f}%\n")
        else:
            file.write("- **Maaleja per ottelu:** 0.00\n")
            file.write("- **Yli 2.5 maalia otteluissa:** 0.0%\n")
        
        file.write("\n## Joukkuekohtaiset tilastot\n\n")
        
        # Joukkuekohtaiset tiedot
        for team in teams:
            home_audiences = team_data[team]['Home']['audiences']
            home_goals_scored = team_data[team]['Home']['goals_scored']
            home_goals_conceded = team_data[team]['Home']['goals_conceded']
            
            home_games = len(home_audiences)
            total_home_audience = sum(home_audiences) if home_audiences else 0
            total_home_goals_scored = sum(home_goals_scored) if home_goals_scored else 0
            total_home_goals_conceded = sum(home_goals_conceded) if home_goals_conceded else 0
            total_home_over_2_5 = team_data[team]['Home']['over_2_5']
            
            away_audiences = team_data[team]['Away']['audiences']
            away_goals_scored = team_data[team]['Away']['goals_scored']
            away_goals_conceded = team_data[team]['Away']['goals_conceded']
            
            away_games = len(away_audiences)
            total_away_audience = sum(away_audiences) if away_audiences else 0
            total_away_goals_scored = sum(away_goals_scored) if away_goals_scored else 0
            total_away_goals_conceded = sum(away_goals_conceded) if away_goals_conceded else 0
            total_away_over_2_5 = team_data[team]['Away']['over_2_5']
            
            file.write(f"### {team}\n")
            
            file.write("#### Kotipelit\n")
            file.write(f"- **Kokonaisyleisömäärä:** {total_home_audience:,}\n")
            
            # KRIITTINEN KORJAUS: Tarkistetaan onko home_games nolla ennen jakamista
            if home_games > 0:
                file.write(f"- **Keskiarvoyleisömäärä per peli:** {total_home_audience / home_games:.2f} ({home_games} peliä)\n")
            else:
                file.write("- **Keskiarvoyleisömäärä per peli:** 0.00 (0 peliä)\n")
                
            file.write(f"- **Tehdyt maalit:** {total_home_goals_scored}\n")
            file.write(f"- **Päästetyt maalit:** {total_home_goals_conceded}\n")
            file.write(f"- **Yli 2.5 maalia kotipeleissä:** {total_home_over_2_5}\n\n")
            
            file.write("#### Vieraspelit\n")
            file.write(f"- **Kokonaisyleisömäärä:** {total_away_audience:,}\n")
            
            # KORJAUS: Tarkistetaan onko away_games nolla ennen jakamista
            if away_games > 0:
                file.write(f"- **Keskiarvoyleisömäärä per peli:** {total_away_audience / away_games:.2f} ({away_games} peliä)\n")
            else:
                file.write("- **Keskiarvoyleisömäärä per peli:** 0.00 (0 peliä)\n")
                
            file.write(f"- **Tehdyt maalit:** {total_away_goals_scored}\n")
            file.write(f"- **Päästetyt maalit:** {total_away_goals_conceded}\n")
            file.write(f"- **Yli 2.5 maalia vieraspeleissä:** {total_away_over_2_5}\n\n")
        
        file.write("\n---\n*Tiedot päivitetään automaattisesti 6 tunnin välein. Viimeisin päivitys: Linux88888 (2025-04-06 10:37:21).*\n")
    
    print(f"Tilastot päivitetty onnistuneesti tiedostoon: {file_path}")
        
except Exception as e:
    print(f"Virhe skriptissä: {str(e)}")
