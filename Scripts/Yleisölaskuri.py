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
                "home": home_team,
                "away": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "audience": audience,
                "total_goals": home_goals + away_goals
            })
        except Exception as e:
            print(f"Virhe rivillä: {str(e)}")
    
    return games

def generate_stats(games):
    # Joukkuekohtaiset tilastot
    teams = {}
    # Liigatason tilastot
    league = {
        "total_goals": 0,
        "total_audience": 0,
        "matches": len(games),
        "over_2_5": 0,
        "highest_attendance": 0
    }
    
    for game in games:
        # Liigatason laskelmat
        league["total_goals"] += game["total_goals"]
        league["total_audience"] += game["audience"]
        if game["total_goals"] > 2.5:
            league["over_2_5"] += 1
        if game["audience"] > league["highest_attendance"]:
            league["highest_attendance"] = game["audience"]
        
        # Joukkuekohtaiset laskelmat
        for side in ["home", "away"]:
            team = game[side]
            if team not in teams:
                teams[team] = {
                    "goals_scored": 0,
                    "goals_conceded": 0,
                    "audience": [],
                    "over_2_5": 0
                }
            
            teams[team]["goals_scored"] += game[f"{side}_goals"]
            teams[team]["goals_conceded"] += game["away_goals" if side == "home" else "home_goals"]
            teams[team]["audience"].append(game["audience"])
            if game["total_goals"] > 2.5:
                teams[team]["over_2_5"] += 1
    
    return teams, league

def save_md(teams, league):
    with open("Yleisö2025.md", "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 - Tilastot\n\n")
        f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
        
        # Liigatason tilastot
        f.write("## Liigatilastot\n")
        f.write(f"- Pelatut ottelut: {league['matches']}\n")
        f.write(f"- Yhteensä maaleja: {league['total_goals']}\n")
        f.write(f"- Maaleja per ottelu: {safe_divide(league['total_goals'], league['matches']):.1f}\n")
        f.write(f"- Yli 2.5 maalin otteluita: {league['over_2_5']} ({safe_divide(league['over_2_5']*100, league['matches']):.1f}%)\n")
        f.write(f"- Yhteensä yleisöä: {league['total_audience']:,} katsojaa\n")
        f.write(f"- Keskimääräinen yleisömäärä: {safe_divide(league['total_audience'], league['matches']):.0f}\n")
        f.write(f"- Suurin yleisömäärä: {league['highest_attendance']:,}\n\n")
        
        # Joukkuekohtaiset tilastot
        f.write("## Joukkuekohtaiset tilastot\n")
        for team, data in sorted(teams.items()):
            f.write(f"### {team}\n")
            f.write(f"- Tehdyt maalit: {data['goals_scored']}\n")
            f.write(f"- Päästetyt maalit: {data['goals_conceded']}\n")
            f.write(f"- Yli 2.5 maalin otteluita: {data['over_2_5']}\n")
            f.write(f"- Keskimääräinen yleisömäärä: {safe_divide(sum(data['audience']), len(data['audience'])):.0f}\n")
            f.write(f"- Yli 2000 katsojan otteluita: {sum(1 for a in data['audience'] if a > 2000)}\n\n")

if __name__ == "__main__":
    try:
        html = fetch_data()
        games = parse_games(html)
        teams_stats, league_stats = generate_stats(games)
        save_md(teams_stats, league_stats)
        print("✅ Tiedosto Yleisö2025.md päivitetty!")
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")
