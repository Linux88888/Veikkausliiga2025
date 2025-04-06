import requests
from bs4 import BeautifulSoup
import datetime

def safe_divide(a, b):
    return a / b if b != 0 else 0

def fetch_data():
    url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    return response.text

def parse_games(html):
    soup = BeautifulSoup(html, "html.parser")
    games = []
    
    for row in soup.select("table#games tbody tr"):
        cells = row.find_all("td")
        if len(cells) < 8:
            continue
        
        try:
            result = cells[6].get_text(strip=True).replace("—", "-")
            if "-" not in result:
                continue
                
            home_team = cells[4].get_text(strip=True).split(" - ")[0]
            away_team = cells[4].get_text(strip=True).split(" - ")[1]
            home_goals, away_goals = map(int, result.split("-"))
            audience = int(cells[7].get_text(strip=True)) if cells[7].get_text(strip=True).isdigit() else 0
            
            games.append({
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "audience": audience,
                "total_goals": home_goals + away_goals
            })
        except Exception as e:
            print(f"Virhe rivillä: {str(e)}")
    
    return games

def generate_stats(games):
    teams = {}
    
    for game in games:
        # Kotijoukkueen kotipelit
        if game["home_team"] not in teams:
            teams[game["home_team"]] = {
                "home": {"goals_scored": 0, "goals_conceded": 0, "audience": [], "over_2_5": 0},
                "away": {"goals_scored": 0, "goals_conceded": 0, "audience": [], "over_2_5": 0}
            }
        teams[game["home_team"]]["home"]["goals_scored"] += game["home_goals"]
        teams[game["home_team"]]["home"]["goals_conceded"] += game["away_goals"]
        teams[game["home_team"]]["home"]["audience"].append(game["audience"])
        if game["total_goals"] > 2.5:
            teams[game["home_team"]]["home"]["over_2_5"] += 1
        
        # Vierasjoukkueen vieraspelit
        if game["away_team"] not in teams:
            teams[game["away_team"]] = {
                "home": {"goals_scored": 0, "goals_conceded": 0, "audience": [], "over_2_5": 0},
                "away": {"goals_scored": 0, "goals_conceded": 0, "audience": [], "over_2_5": 0}
            }
        teams[game["away_team"]]["away"]["goals_scored"] += game["away_goals"]
        teams[game["away_team"]]["away"]["goals_conceded"] += game["home_goals"]
        teams[game["away_team"]]["away"]["audience"].append(game["audience"])
        if game["total_goals"] > 2.5:
            teams[game["away_team"]]["away"]["over_2_5"] += 1
    
    return teams

def save_md(teams):
    with open("Yleisö2025.md", "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 - Erittelyt\n\n")
        f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
        
        for team in sorted(teams.keys()):
            data = teams[team]
            f.write(f"## {team}\n")
            
            # Kotipelit
            f.write("### Kotipelit\n")
            home = data["home"]
            f.write(f"- Otteluita: {len(home['audience'])}\n")
            f.write(f"- Tehdyt maalit: {home['goals_scored']}\n")
            f.write(f"- Päästetyt maalit: {home['goals_conceded']}\n")
            f.write(f"- Yli 2.5 maalia: {home['over_2_5']} ({safe_divide(home['over_2_5']*100, len(home['audience'])):.1f}%)\n")
            f.write(f"- Keskiverto yleisö: {safe_divide(sum(home['audience']), len(home['audience'])):.0f}\n")
            f.write(f"- Yli 2000 katsojaa: {sum(1 for a in home['audience'] if a > 2000)}\n\n")
            
            # Vieraspelit
            f.write("### Vieraspelit\n")
            away = data["away"]
            f.write(f"- Otteluita: {len(away['audience'])}\n")
            f.write(f"- Tehdyt maalit: {away['goals_scored']}\n")
            f.write(f"- Päästetyt maalit: {away['goals_conceded']}\n")
            f.write(f"- Yli 2.5 maalia: {away['over_2_5']} ({safe_divide(away['over_2_5']*100, len(away['audience'])):.1f}%)\n")
            f.write(f"- Keskiverto yleisö: {safe_divide(sum(away['audience']), len(away['audience'])):.0f}\n")
            f.write(f"- Yli 2000 katsojaa: {sum(1 for a in away['audience'] if a > 2000)}\n\n")

if __name__ == "__main__":
    try:
        html = fetch_data()
        games = parse_games(html)
        teams_stats = generate_stats(games)
        save_md(teams_stats)
        print("✅ Tiedosto Yleisö2025.md päivitetty!")
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")
