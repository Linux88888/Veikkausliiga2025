import os
import re
import requests
from bs4 import BeautifulSoup
import datetime
import sys

# URL-osoitteen tarkistus
BASE_URL = "https://www.veikkausliiga.com"
SEASON = "2025"
url = f"{BASE_URL}/tilastot/{SEASON}/veikkausliiga/ottelut/"

teams = ["Ilves", "HJK", "FC Inter", "KuPS", "IFK Mariehamn", 
         "FF Jaro", "KTP", "SJK", "VPS", "AC Oulu", "FC Haka", "IF Gnistan"]

def safe_divide(a, b, default=0):
    return a / b if b > 0 else default

team_data = {
    team: {
        "Home": {"audiences": [], "goals_scored": [], "goals_conceded": [], "over_2_5": 0},
        "Away": {"audiences": [], "goals_scored": [], "goals_conceded": [], "over_2_5": 0}
    } for team in teams
}

total_audiences = []
total_goals = 0
total_over_2_5_games = 0

def normalize_team_name(name):
    """Yhdenmukaistaa joukkueen nimet"""
    name = name.strip().replace("&nbsp;", " ")
    replacements = {
        "FC Haka": "Haka",
        "IFK Mariehamn": "Mariehamn",
        "FC Inter": "Inter"
    }
    return replacements.get(name, name)

try:
    # Päivitetty header-profiili
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "fi-FI,fi;q=0.9",
        "Referer": BASE_URL,
        "DNT": "1"
    }
    
    print(f"🔄 Haetaan data osoitteesta: {url}")
    response = requests.get(url, headers=headers, timeout=20)
    print(f"📡 Vastaus: {response.status_code} ({len(response.text)} merkkiä)")
    
    # Tallenna väliaikaisesti vastaus debuggausta varten
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Etsi ottelut eri tavoilla
    matches = []
    
    # Vaihtoehto 1: Uusi komponenttirakenne
    match_cards = soup.find_all('div', class_=lambda x: x and 'match-card' in x)
    if match_cards:
        print("✅ Löytyi match-card -komponentteja")
        matches = match_cards
    else:
        # Vaihtoehto 2: Vanha taulukkorakenne
        old_table = soup.find('table', class_='stats-table')
        if old_table:
            print("ℹ️ Löytyi vanha taulukkorakenne")
            matches = old_table.find_all('tr')
    
    if not matches:
        raise ValueError("❌ Ei löytynyt otteluita - tarkista sivuston rakenne")
    
    print(f"🔢 Löytyi {len(matches)} ottelua/riviä")
    
    for match in matches:
        try:
            # Alustetaan muuttujat
            home_team = away_team = None
            home_goals = away_goals = 0
            audience = 0
            
            # Yritä parsia uudella tavalla
            if match.name == 'div':  # Uusi komponenttirakenne
                # Joukkueet
                teams_div = match.find('div', class_='teams-container')
                if teams_div:
                    home_team = normalize_team_name(teams_div.find('div', class_='home-team').get_text(strip=True))
                    away_team = normalize_team_name(teams_div.find('div', class_='away-team').get_text(strip=True))
                
                # Tulos
                score_div = match.find('div', class_='match-score')
                if score_div:
                    score_text = score_div.get_text(strip=True)
                    if '-' in score_text:
                        home_goals, away_goals = map(int, score_text.split('-'))
                
                # Yleisömäärä
                audience_div = match.find('div', class_='attendance')
                if audience_div:
                    audience_match = re.search(r'\d+', audience_div.get_text().replace(' ', ''))
                    if audience_match:
                        audience = int(audience_match.group())
            
            # Vanha taulukkorakenne
            elif match.name == 'tr':
                cells = match.find_all('td')
                if len(cells) >= 7:
                    # Joukkueet
                    teams_cell = cells[3].get_text(strip=True)
                    if ' - ' in teams_cell:
                        home_team, away_team = map(normalize_team_name, teams_cell.split(' - '))
                    
                    # Tulos
                    score_text = cells[5].get_text(strip=True)
                    if '-' in score_text:
                        home_goals, away_goals = map(int, score_text.split('-'))
                    
                    # Yleisömäärä
                    audience_text = cells[6].get_text(strip=True)
                    audience_match = re.search(r'\d+', audience_text)
                    if audience_match:
                        audience = int(audience_match.group())
            
            # Tarkista pakolliset tiedot
            if not all([home_team, away_team, home_goals >= 0, away_goals >= 0, audience > 0]):
                continue
            
            print(f"⚽ {home_team} {home_goals}-{away_goals} {away_team} ({audience} katsojaa)")
            
            # Päivitä globaalit tilastot
            total_goals += home_goals + away_goals
            total_audiences.append(audience)
            if (home_goals + away_goals) > 2.5:
                total_over_2_5_games += 1
            
            # Päivitä joukkueiden tiedot
            for team, side, goals, conceded in [
                (home_team, "Home", home_goals, away_goals),
                (away_team, "Away", away_goals, home_goals)
            ]:
                if team in teams:
                    team_data[team][side]["audiences"].append(audience)
                    team_data[team][side]["goals_scored"].append(goals)
                    team_data[team][side]["goals_conceded"].append(conceded)
                    if (goals + conceded) > 2.5:
                        team_data[team][side]["over_2_5"] += 1
        
        except Exception as e:
            print(f"⚠️ Virhe ottelun käsittelyssä: {str(e)}")
            continue
    
    # Kirjoita raportti
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# Veikkausliiga 2025 - Ottelutilastot\n\n")
        f.write(f"**Päivitetty:** {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
        
        if not total_audiences:
            f.write("## Ei pelattuja otteluita vielä\n")
            f.write("Kauden 2025 otteluita ei ole vielä pelattu tai data ei ole saatavilla.\n")
        else:
            # Yleiset tilastot
            f.write("## Yleiset tilastot\n")
            f.write(f"- Pelatut ottelut: {len(total_audiences)}\n")
            f.write(f"- Yhteensä katsojia: {sum(total_audiences):,}\n")
            f.write(f"- Keskiyleisö: {safe_divide(sum(total_audiences), len(total_audiences)):.0f}\n")
            f.write(f"- Maalit yhteensä: {total_goals} (keskiarvo {safe_divide(total_goals, len(total_audiences)):.2f}/ottelu)\n")
            f.write(f"- Yli 2.5 maalin otteluita: {total_over_2_5_games} ({safe_divide(total_over_2_5_games*100, len(total_audiences)):.1f}%)\n\n")
            
            # Joukkuekohtaiset tilastot
            f.write("## Joukkuekohtaiset tilastot\n")
            for team in teams:
                home = team_data[team]["Home"]
                away = team_data[team]["Away"]
                
                f.write(f"### {team}\n")
                
                # Kotipelit
                f.write("#### Kotipelit\n")
                if home["audiences"]:
                    f.write(f"- Otteluita: {len(home['audiences'])}\n")
                    f.write(f"- Keskiyleisö: {safe_divide(sum(home['audiences']), len(home['audiences'])):.0f}\n")
                    f.write(f"- Maalit: {sum(home['goals_scored'])}-{sum(home['goals_conceded'])}\n")
                    f.write(f"- Yli 2.5 maalia: {home['over_2_5']} ({safe_divide(home['over_2_5']*100, len(home['audiences'])):.1f}%)\n")
                else:
                    f.write("- Ei kotipelejä\n")
                
                # Vieraspelit
                f.write("#### Vieraspelit\n")
                if away["audiences"]:
                    f.write(f"- Otteluita: {len(away['audiences'])}\n")
                    f.write(f"- Keskiyleisö: {safe_divide(sum(away['audiences']), len(away['audiences'])):.0f}\n")
                    f.write(f"- Maalit: {sum(away['goals_scored'])}-{sum(away['goals_conceded'])}\n")
                    f.write(f"- Yli 2.5 maalia: {away['over_2_5']} ({safe_divide(away['over_2_5']*100, len(away['audiences'])):.1f}%)\n")
                else:
                    f.write("- Ei vieraspelejä\n")
                
                f.write("\n")
        
        f.write("\n---\n")
        f.write("*Tiedot päivitetty automaattisesti: [Veikkausliiga.com](%s)*\n" % url)
    
    print(f"\n✅ Raportti luotu: {os.path.abspath(file_path)}")

except Exception as e:
    print(f"\n❌ KRIILLINEN VIRHE: {str(e)}")
    sys.exit(1)
