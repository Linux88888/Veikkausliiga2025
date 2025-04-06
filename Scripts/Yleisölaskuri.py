import os
import re
import requests
from bs4 import BeautifulSoup
import datetime
import sys

# Päivitetty URL (varmista että 2025-kausi on olemassa)
url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"

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

try:
    # Päivitetty headeri
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "fi-FI,fi;q=0.9",
        "Referer": "https://www.veikkausliiga.com/",
    }
    
    print(f"🚀 Aloitetaan datan haku osoitteesta: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    print(f"🔍 Vastauskoodi: {response.status_code}, Sisällön pituus: {len(response.text)} merkkiä")
    
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Etsitään oikea taulukko uudella selektorilla
    main_table = soup.find('table', class_='stats-table')
    if not main_table:
        main_table = soup.find('table', {'id': 'matches'})
    
    if not main_table:
        raise ValueError("❌ Taulukkoa ei löytynyt! Tarkista sivuston rakenne.")
    
    rows = main_table.find_all('tr', class_=lambda x: x != 'header')
    print(f"📊 Löydettiin {len(rows)} otteluriviä")
    
    for row in rows:
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 7:
                continue
                
            # Ottelun tiedot
            teams_cell = cells[3].get_text(strip=True)
            result = cells[5].get_text(strip=True)
            audience = cells[6].get_text(strip=True).replace(" ", "")
            
            # Debug-tuloste
            # print(f"Käsitellään rivi: {teams_cell} - {result} - {audience}")
            
            # Tulos ja yleisömäärä
            match = re.search(r'(\d+)[\s–-]+(\d+)', result)
            audience_match = re.search(r'\d+', audience)
            
            if not (match and audience_match):
                continue
                
            home_goals = int(match.group(1))
            away_goals = int(match.group(2))
            audience_num = int(audience_match.group())
            
            # Päivitä yleiset tilastot
            total_goals += home_goals + away_goals
            total_audiences.append(audience_num)
            if (home_goals + away_goals) > 2.5:
                total_over_2_5_games += 1
                
            # Joukkueet
            if " - " in teams_cell:
                home_team, away_team = [t.strip() for t in teams_cell.split(" - ")]
                
                # Kotijoukkueen tiedot
                if home_team in teams:
                    team_data[home_team]["Home"]["audiences"].append(audience_num)
                    team_data[home_team]["Home"]["goals_scored"].append(home_goals)
                    team_data[home_team]["Home"]["goals_conceded"].append(away_goals)
                    if (home_goals + away_goals) > 2.5:
                        team_data[home_team]["Home"]["over_2_5"] += 1
                
                # Vierasjoukkueen tiedot
                if away_team in teams:
                    team_data[away_team]["Away"]["audiences"].append(audience_num)
                    team_data[away_team]["Away"]["goals_scored"].append(away_goals)
                    team_data[away_team]["Away"]["goals_conceded"].append(home_goals)
                    if (home_goals + away_goals) > 2.5:
                        team_data[away_team]["Away"]["over_2_5"] += 1
                        
        except Exception as e:
            print(f"⚠️ Virhe rivin käsittelyssä: {str(e)}")
            continue
    
    # Debug-tiedot
    print("\n🔧 Testidata:")
    print(f"Kaikki yleisömäärät: {total_audiences[:5]}... (yhteensä {len(total_audiences)})")
    print(f"Esimerkki HJK:n kotipeleistä: {team_data['HJK']['Home']}")
    
    # Kirjoitus MD-tiedostoon
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 - Yleisö- ja maalitilastot\n\n")
        f.write(f"*Päivitetty {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
        
        # Yleiset tilastot
        f.write("## Yleiset tilastot\n")
        f.write(f"- Pelatut ottelut: {len(total_audiences)}\n")
        f.write(f"- Yhteensä katsojia: {sum(total_audiences):,}\n")
        f.write(f"- Keskiyleisö: {safe_divide(sum(total_audiences), len(total_audiences)):.0f}\n")
        f.write(f"- Maaleja yhteensä: {total_goals} (keskiarvo {safe_divide(total_goals, len(total_audiences)):.2f}/ottelu)\n")
        f.write(f"- Yli 2.5 maalin otteluita: {total_over_2_5_games} ({safe_divide(total_over_2_5_games*100, len(total_audiences)):.1f}%)\n\n")
        
        # Joukkueet
        f.write("## Joukkuekohtaiset tilastot\n")
        for team in teams:
            home = team_data[team]["Home"]
            away = team_data[team]["Away"]
            
            f.write(f"### {team}\n")
            
            # Kotipelit
            f.write("#### Kotipelit\n")
            f.write(f"- Otteluita: {len(home['audiences']}\n")
            if len(home['audiences']) > 0:
                f.write(f"- Keskiyleisö: {safe_divide(sum(home['audiences']), len(home['audiences'])):.0f}\n")
                f.write(f"- Maalit: {sum(home['goals_scored'])}-{sum(home['goals_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {home['over_2_5']} ({safe_divide(home['over_2_5']*100, len(home['audiences'])):.1f}%)\n")
            else:
                f.write("- Ei kotipelejä vielä\n")
            
            # Vieraspelit
            f.write("#### Vieraspelit\n")
            f.write(f"- Otteluita: {len(away['audiences'])}\n")
            if len(away['audiences']) > 0:
                f.write(f"- Keskiyleisö: {safe_divide(sum(away['audiences']), len(away['audiences'])):.0f}\n")
                f.write(f"- Maalit: {sum(away['goals_scored'])}-{sum(away['goals_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {away['over_2_5']} ({safe_divide(away['over_2_5']*100, len(away['audiences'])):.1f}%)\n")
            else:
                f.write("- Ei vieraspelejä vielä\n")
            
            f.write("\n")
        
        f.write("\n*Lähde: Veikkausliiga.com - Tiedot haettu automaattisesti*")

    print(f"\n✅ Raportti luotu onnistuneesti: {file_path}")

except Exception as e:
    print(f"\n❌ KRIILLINEN VIRHE: {str(e)}", file=sys.stderr)
    sys.exit(1)
