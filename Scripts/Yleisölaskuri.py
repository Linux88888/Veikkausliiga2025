import os
import re
import requests
from bs4 import BeautifulSoup
import datetime
import sys

# URL-osoite Veikkausliigan tilastoihin
url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"

# Päivitetyt joukkueet 2025 kauden mukaan
teams = ["Ilves", "HJK", "FC Inter", "KuPS", "IFK Mariehamn", "FF Jaro", "KTP", "SJK", "VPS", "AC Oulu", "FC Haka", "IF Gnistan"]

# Turvallinen jakamisfunktio
def safe_divide(a, b, default=0):
    return a / b if b > 0 else default

# Alusta tietorakenne
team_data = {
    team: {
        "Home": {"audiences": [], "goals_scored": [], "goals_conceded": [], "over_2_5": 0},
        "Away": {"audiences": [], "goals_scored": [], "goals_conceded": [], "over_2_5": 0}
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
    
    print(f"Haetaan data osoitteesta: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Pyyntö vastauskoodi: {response.status_code}")
    
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    print("HTML parsinut onnistuneesti")
    
    # Etsi oikea taulukko
    stats_table = soup.find('table', {'class': 'stats-table'})
    if not stats_table:
        stats_table = soup.find('table', {'class': 'matches-table'})
    
    if stats_table:
        table_rows = stats_table.find_all("tr")
        print(f"Löytyi {len(table_rows)} riviä dataa")
    else:
        table_rows = soup.find_all("tr")
        print(f"Taulukkoa ei löytynyt, käytetään kaikkia rivejä ({len(table_rows)} kpl)")
    
    for row in table_rows:
        cells = row.find_all("td")
        if len(cells) >= 7:  # Varmista että on tarpeeksi sarakkeita
            try:
                match_teams = cells[3].get_text(strip=True)
                result_text = cells[5].get_text(strip=True)
                audience_text = cells[6].get_text(strip=True).replace(" ", "")
                
                # Tarkista että kaikki tiedot ovat saatavilla
                if not all([match_teams, result_text, audience_text]):
                    continue
                
                # Parsi tulos ja yleisömäärä
                result_match = re.search(r"(\d+)\s*[—-]\s*(\d+)", result_text)
                audience_match = re.search(r"(\d+)", audience_text)
                
                if not (result_match and audience_match):
                    continue
                
                audience_number = int(audience_match.group(1))
                home_goals, away_goals = map(int, result_match.groups())
                
                # Päivitä kokonaistilastot
                total_goals += home_goals + away_goals
                total_audiences.append(audience_number)
                if home_goals + away_goals > 2.5:
                    total_over_2_5_games += 1
                
                # Erottele joukkueet
                if " - " in match_teams:
                    home_team, away_team = [t.strip() for t in match_teams.split(" - ")]
                    
                    # Päivitä kotijoukkueen tiedot
                    if home_team in teams:
                        team_data[home_team]["Home"]["audiences"].append(audience_number)
                        team_data[home_team]["Home"]["goals_scored"].append(home_goals)
                        team_data[home_team]["Home"]["goals_conceded"].append(away_goals)
                        if home_goals + away_goals > 2.5:
                            team_data[home_team]["Home"]["over_2_5"] += 1
                    
                    # Päivitä vierasjoukkueen tiedot
                    if away_team in teams:
                        team_data[away_team]["Away"]["audiences"].append(audience_number)
                        team_data[away_team]["Away"]["goals_scored"].append(away_goals)
                        team_data[away_team]["Away"]["goals_conceded"].append(home_goals)
                        if home_goals + away_goals > 2.5:
                            team_data[away_team]["Away"]["over_2_5"] += 1
            except Exception as e:
                print(f"Virhe rivin käsittelyssä: {str(e)}", file=sys.stderr)
                continue
    
    # Tulosta debug-tietoja
    print("\nKerätyt tiedot:")
    print(f"Yleisömäärät: {total_audiences}")
    print(f"Tehdyt maalit yhteensä: {total_goals}")
    print(f"Yli 2.5 maalin ottelut: {total_over_2_5_games}")
    
    # Lasketaan yhteenvetotilastot
    total_games = len(total_audiences)
    total_average_audience = safe_divide(sum(total_audiences), total_games)
    total_average_goals = safe_divide(total_goals, total_games)
    total_over_2_5_percent = safe_divide(total_over_2_5_games * 100, total_games)
    
    # Määritä tiedoston sijainti
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
    
    # Kirjoita tulokset Markdown-tiedostoon
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("# Veikkausliiga 2025 - Yleisötilastot\n\n")
        file.write(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        file.write("## Kokonaistilastot\n\n")
        file.write(f"- **Kokonaisyleisömäärä:** {sum(total_audiences):,} katsojaa\n")
        file.write(f"- **Keskimääräinen yleisö:** {total_average_audience:.0f} katsojaa/ottelu\n")
        file.write(f"- **Otteluita pelattu:** {total_games}\n")
        file.write(f"- **Maaleja yhteensä:** {total_goals}\n")
        file.write(f"- **Maaleja per ottelu:** {total_average_goals:.2f}\n")
        file.write(f"- **Yli 2.5 maalia otteluissa:** {total_over_2_5_percent:.1f}%\n")
        
        file.write("\n## Joukkuekohtaiset tilastot\n\n")
        
        for team in teams:
            home = team_data[team]["Home"]
            away = team_data[team]["Away"]
            
            home_games = len(home["audiences"])
            away_games = len(away["audiences"])
            
            file.write(f"### {team}\n")
            
            # Kotipelit
            file.write("#### Kotipelit\n")
            file.write(f"- **Kokonaisyleisömäärä:** {sum(home['audiences']):,}\n")
            file.write(f"- **Keskiarvoyleisömäärä:** {safe_divide(sum(home['audiences']), home_games):.0f}\n")
            file.write(f"- **Tehdyt maalit:** {sum(home['goals_scored'])}\n")
            file.write(f"- **Päästetyt maalit:** {sum(home['goals_conceded'])}\n")
            file.write(f"- **Yli 2.5 maalia:** {home['over_2_5']}/{home_games} ({safe_divide(home['over_2_5']*100, home_games):.1f}%)\n\n")
            
            # Vieraspelit
            file.write("#### Vieraspelit\n")
            file.write(f"- **Kokonaisyleisömäärä:** {sum(away['audiences']):,}\n")
            file.write(f"- **Keskiarvoyleisömäärä:** {safe_divide(sum(away['audiences']), away_games):.0f}\n")
            file.write(f"- **Tehdyt maalit:** {sum(away['goals_scored'])}\n")
            file.write(f"- **Päästetyt maalit:** {sum(away['goals_conceded'])}\n")
            file.write(f"- **Yli 2.5 maalia:** {away['over_2_5']}/{away_games} ({safe_divide(away['over_2_5']*100, away_games):.1f}%)\n\n")
        
        file.write("\n---\n*Tiedot päivitetty automaattisesti. Lähde: Veikkausliiga.com*\n")
    
    print(f"\nTilastot tallennettu tiedostoon: {os.path.abspath(file_path)}")
    print("Skripti suoritettu onnistuneesti!")

except Exception as e:
    print(f"\nVIRHE: {str(e)}", file=sys.stderr)
    sys.exit(1)
