import os
import re
import time
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Asenna ensin: pip install selenium webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager

# Konfiguraatio
SEASON_URL = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
TEAMS = ["Ilves", "HJK", "FC Inter", "KuPS", "IFK Mariehamn", 
        "FF Jaro", "KTP", "SJK", "VPS", "AC Oulu", "FC Haka", "IF Gnistan"]
DEBUG = True

def init_driver():
    """Alustaa headless Chrome-selaimen"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

def normalize_team(name):
    """Yhdenmukaistaa joukkueiden nimet"""
    name = name.strip().replace("&nbsp;", " ").replace("\u200b", "")  # Poista erikoismerkit
    replacements = {
        "FC Haka": "Haka",
        "IFK Mariehamn": "Mariehamn",
        "FC Inter": "Inter"
    }
    return replacements.get(name, name)

def parse_match_data(html):
    """Parsii ottelutiedot BeautifulSoupilla"""
    soup = BeautifulSoup(html, "html.parser")
    matches = []
    
    # Etsi ottelukortit uuden rakenteen mukaan
    for match in soup.find_all('div', class_='match-card'):
        try:
            # Joukkueet
            home_team = normalize_team(match.find('div', class_='home-team').get_text(strip=True))
            away_team = normalize_team(match.find('div', class_='away-team').get_text(strip=True))
            
            # Tulos
            score = match.find('div', class_='match-score').get_text(strip=True)
            home_goals, away_goals = map(int, score.split('-'))
            
            # Yleisömäärä
            audience_div = match.find('div', class_='match-attendance')
            audience = int(re.search(r'\d+', audience_div.get_text(strip=True)).group()) if audience_div else 0
            
            matches.append({
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "audience": audience
            })
        except Exception as e:
            if DEBUG:
                print(f"⚠️ Virhe ottelun parsimisessa: {str(e)}")
    
    return matches

def main():
    # Alusta data-rakenne
    team_data = {
        team: {
            "Home": {"audiences": [], "goals_scored": [], "goals_conceded": [], "over_2_5": 0},
            "Away": {"audiences": [], "goals_scored": [], "goals_conceded": [], "over_2_5": 0}
        } for team in TEAMS
    }
    total_audiences = []
    total_goals = 0
    total_over_2_5 = 0

    driver = init_driver()
    try:
        print(f"🌐 Avataan {SEASON_URL}")
        driver.get(SEASON_URL)
        
        # Odota että komponentit latautuvat
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "match-card"))
        )
        time.sleep(2)  # Lisäaika animaatioille
        
        # Tallenna JavaScriptin renderöimä sivu
        html = driver.page_source
        if DEBUG:
            with open("debug_selenium.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("💾 JavaScript-sivu tallennettu: debug_selenium.html")
        
        # Prosessoi data
        matches = parse_match_data(html)
        if not matches:
            raise ValueError("❌ Ei löytynyt otteluita - tarkista debug_selenium.html")
        
        print(f"✅ Löytyi {len(matches)} ottelua")
        
        # Päivitä tilastot
        for match in matches:
            total_goals += match['home_goals'] + match['away_goals']
            total_audiences.append(match['audience'])
            if (match['home_goals'] + match['away_goals']) > 2.5:
                total_over_2_5 += 1
            
            # Kotijoukkueen tiedot
            if match['home_team'] in TEAMS:
                team_data[match['home_team']]["Home"]["audiences"].append(match['audience'])
                team_data[match['home_team']]["Home"]["goals_scored"].append(match['home_goals'])
                team_data[match['home_team']]["Home"]["goals_conceded"].append(match['away_goals'])
                if (match['home_goals'] + match['away_goals']) > 2.5:
                    team_data[match['home_team']]["Home"]["over_2_5"] += 1
                    
            # Vierasjoukkueen tiedot
            if match['away_team'] in TEAMS:
                team_data[match['away_team']]["Away"]["audiences"].append(match['audience'])
                team_data[match['away_team']]["Away"]["goals_scored"].append(match['away_goals'])
                team_data[match['away_team']]["Away"]["goals_conceded"].append(match['home_goals'])
                if (match['home_goals'] + match['away_goals']) > 2.5:
                    team_data[match['away_team']]["Away"]["over_2_5"] += 1
        
        # Luo raportti
        report_path = os.path.join(os.path.dirname(__file__), "Veikkausliiga2025_raportti.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Veikkausliiga 2025 - Tilastoraportti\n\n")
            f.write(f"**Päivitetty:** {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
            
            f.write("## Yleiset tilastot\n")
            f.write(f"- Pelatut ottelut: {len(matches)}\n")
            f.write(f"- Yhteensä katsojia: {sum(total_audiences):,}\n")
            f.write(f"- Keskiyleisö: {sum(total_audiences)/len(total_audiences):.0f}\n")
            f.write(f"- Yli 2.5 maalia: {total_over_2_5} ({total_over_2_5/len(matches)*100:.1f}%)\n\n")
            
            f.write("## Joukkuekohtaiset tilastot\n")
            for team in TEAMS:
                f.write(f"### {team}\n")
                f.write(f"**Kotipelit:**\n")
                f.write(f"- Otteluita: {len(team_data[team]['Home']['audiences']}\n")
                f.write(f"- Maalit: {sum(team_data[team]['Home']['goals_scored']}-{sum(team_data[team]['Home']['goals_conceded']}\n")
                f.write(f"**Vieraspelit:**\n")
                f.write(f"- Otteluita: {len(team_data[team]['Away']['audiences']}\n")
                f.write(f"- Maalit: {sum(team_data[team]['Away']['goals_scored']}-{sum(team_data[team]['Away']['goals_conceded']}\n\n")
        
        print(f"📄 Raportti luotu: {os.path.abspath(report_path)}")
        
    except Exception as e:
        print(f"❌ Kriittinen virhe: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
