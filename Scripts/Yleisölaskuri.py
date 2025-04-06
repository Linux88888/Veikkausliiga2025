import os
import re
import requests
from bs4 import BeautifulSoup
import datetime
import sys

# Oletetaan että 2025-kausi on aktiivinen
url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"

teams = ["Ilves", "HJK", "FC Inter", "KuPS", "IFK Mariehamn", 
        "FF Jaro", "KTP", "SJK", "VPS", "AC Oulu", "FC Haka", "IF Gnistan"]

def safe_divide(a, b, default=0):
    return a / b if b > 0 else default

# Alusta tietorakenne
team_data = {
    team: {
        "Home": {"audiences": [], "goals_scored": [], "goals_conceded": [], "over_2_5": 0},
        "Away": {"audiences": [], "goals_scored": [], "goals_conceded": [], "over_2_5": 0}
    } for team in teams
}

# Alusta globaalit muuttujat
total_audiences = []
total_goals = 0
total_over_2_5_games = 0

try:
    # Päivitetty headeri joka näyttää "oikealta" selaimelta
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "fi-FI,fi;q=0.9",
        "Referer": "https://www.veikkausliiga.com/",
        "DNT": "1"
    }
    
    print(f"🔍 Haetaan data osoitteesta: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    print(f"🔢 Statuskoodi: {response.status_code}, Dataa: {len(response.text)} merkkiä")
    
    # Tarkista onnistuiko pyyntö
    response.raise_for_status()
    
    # Parsitaan HTML uudella tavalla
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Etsitään ottelut uuden rakenteen mukaan
    match_items = soup.find_all('div', class_=lambda x: x and 'match-item' in x)
    print(f"📊 Löytyi {len(match_items)} ottelua")
    
    for item in match_items:
        try:
            # Parsi joukkueet
            teams_element = item.find('div', class_='teams')
            home_team = teams_element.find('div', class_='home-team').get_text(strip=True)
            away_team = teams_element.find('div', class_='away-team').get_text(strip=True)
            
            # Parsi tulos
            score_element = item.find('div', class_='score')
            home_goals, away_goals = map(int, score_element.get_text(strip=True).split('-'))
            
            # Parsi yleisömäärä
            audience_element = item.find('div', class_='attendance')
            audience = int(re.search(r'\d+', audience_element.get_text(strip=True)).group())
            
            # Päivitä globaalit tilastot
            total_goals += home_goals + away_goals
            total_audiences.append(audience)
            if (home_goals + away_goals) > 2.5:
                total_over_2_5_games += 1
                
            # Päivitä joukkueiden tiedot
            if home_team in teams:
                team_data[home_team]["Home"]["audiences"].append(audience)
                team_data[home_team]["Home"]["goals_scored"].append(home_goals)
                team_data[home_team]["Home"]["goals_conceded"].append(away_goals)
                if (home_goals + away_goals) > 2.5:
                    team_data[home_team]["Home"]["over_2_5"] += 1
                    
            if away_team in teams:
                team_data[away_team]["Away"]["audiences"].append(audience)
                team_data[away_team]["Away"]["goals_scored"].append(away_goals)
                team_data[away_team]["Away"]["goals_conceded"].append(home_goals)
                if (home_goals + away_goals) > 2.5:
                    team_data[away_team]["Away"]["over_2_5"] += 1
                    
        except Exception as e:
            print(f"⚠️ Virhe ottelun käsittelyssä: {str(e)}")
            continue
    
    # Kirjoita raportti
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("# Veikkausliiga 2025 - Ottelutilastot\n\n")
        f.write(f"*Päivitetty {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
        
        # Yleiset tilastot
        f.write("## Yleiset tilastot\n")
        f.write(f"- Pelatut ottelut: {len(total_audiences)}\n")
        f.write(f"- Yhteensä katsojia: {sum(total_audiences):,}\n")
        f.write(f"- Keskiyleisö: {safe_divide(sum(total_audiences), len(total_audiences)):.0f}\n")
        f.write(f"- Maalit yhteensä: {total_goals} (keskiarvo {safe_divide(total_goals, len(total_audiences)):.2f}/ottelu)\n")
        f.write(f"- Yli 2.5 maalin otteluita: {total_over_2_5_games} ({safe_divide(total_over_2_5_games*100, len(total_audiences)):.1f}%)\n\n")
        
        # Joukkuekohtaiset tilastot
        f.write("## Joukkueet\n")
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
                f.write("- Ei kotipelejä vielä\n")
            
            # Vieraspelit
            f.write("#### Vieraspelit\n")
            if away["audiences"]:
                f.write(f"- Otteluita: {len(away['audiences'])}\n")
                f.write(f"- Keskiyleisö: {safe_divide(sum(away['audiences']), len(away['audiences'])):.0f}\n")
                f.write(f"- Maalit: {sum(away['goals_scored'])}-{sum(away['goals_conceded'])}\n")
                f.write(f"- Yli 2.5 maalia: {away['over_2_5']} ({safe_divide(away['over_2_5']*100, len(away['audiences'])):.1f}%)\n")
            else:
                f.write("- Ei vieraspelejä vielä\n")
            
            f.write("\n")
        
        f.write("\n*Lähde: Veikkausliiga.com - Tiedot haettu automaattisesti*")
    
    print(f"✅ Raportti luotu: {file_path}")

except Exception as e:
    print(f"❌ Kriittinen virhe: {str(e)}", file=sys.stderr)
    sys.exit(1)
