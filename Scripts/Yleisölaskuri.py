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
            home_team = cells[4].get_text(strip=True).split(" - ")[0]
            away_team = cells[4].get_text(strip=True).split(" - ")[1]
            result = cells[6].get_text(strip=True).replace("—", "-")
            
            if "-" not in result:
                continue  # Ohita tulevat ottelut
            
            home_goals, away_goals = map(int, result.split("-"))
            audience = int(cells[7].get_text(strip=True)) if cells[7].get_text(strip=True).isdigit() else 0
            
            games.append({
                "home": home_team,
                "away": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "audience": audience
            })
        except Exception as e:
            print(f"Virhe rivillä: {row} - {str(e)}")
    
    return games

def generate_stats(games):
    teams = {}
    for game in games:
        # Kotijoukkueen tilastot
        if game["home"] not in teams:
            teams[game["home"]] = {"home": [], "away": []}
        teams[game["home"]]["home"].append(game)
        
        # Vierasjoukkueen tilastot
        if game["away"] not in teams:
            teams[game["away"]] = {"home": [], "away": []}
        teams[game["away"]]["away"].append(game)
    return teams

def save_md(stats):
    with open("Yleisö2025.md", "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 - Yleisö- ja maalitilastot\n\n")
        f.write(f"Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
        
        for team, data in sorted(stats.items()):
            f.write(f"## {team}\n")
            
            # Kotipelit
            home_games = data["home"]
            f.write("### Kotipelit\n")
            f.write(f"- Otteluita: {len(home_games)}\n")
            f.write(f"- Tehdyt maalit: {sum(g['home_goals'] for g in home_games)}\n")
            f.write(f"- Päästetyt maalit: {sum(g['away_goals'] for g in home_games)}\n")
            f.write(f"- Yli 2.5 maalia: {sum(1 for g in home_games if g['home_goals'] + g['away_goals'] > 2.5)} kpl\n")
            f.write(f"- Yleisöä keskimäärin: {safe_divide(sum(g['audience'] for g in home_games), len(home_games)):.0f}\n")
            f.write(f"- Yli 2000 katsojaa: {sum(1 for g in home_games if g['audience'] > 2000)} kpl\n\n")
            
            # Vieraspelit
            away_games = data["away"]
            f.write("### Vieraspelit\n")
            f.write(f"- Otteluita: {len(away_games)}\n")
            f.write(f"- Tehdyt maalit: {sum(g['away_goals'] for g in away_games)}\n")
            f.write(f"- Päästetyt maalit: {sum(g['home_goals'] for g in away_games)}\n")
            f.write(f"- Yli 2.5 maalia: {sum(1 for g in away_games if g['home_goals'] + g['away_goals'] > 2.5)} kpl\n")
            f.write(f"- Yleisöä keskimäärin: {safe_divide(sum(g['audience'] for g in away_games), len(away_games)):.0f}\n")
            f.write(f"- Yli 2000 katsojaa: {sum(1 for g in away_games if g['audience'] > 2000)} kpl\n\n")

if __name__ == "__main__":
    try:
        html = fetch_data()
        games = parse_games(html)
        stats = generate_stats(games)
        save_md(stats)
        print("✅ Tiedosto Yleisö2025.md päivitetty onnistuneesti!")
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")
