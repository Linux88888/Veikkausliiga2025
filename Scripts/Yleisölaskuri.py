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
    league_stats = {
        "total_matches": len(games),
        "total_goals": 0,
        "total_audience": 0,
        "over_2_5": 0,
        "highest_attendance": 0,
        "average_attendance": 0
    }
    
    for game in games:
        league_stats["total_goals"] += game["total_goals"]
        league_stats["total_audience"] += game["audience"]
        if game["total_goals"] > 2.5:
            league_stats["over_2_5"] += 1
        if game["audience"] > league_stats["highest_attendance"]:
            league_stats["highest_attendance"] = game["audience"]
        
        for team_type in ["home_team", "away_team"]:
            team = game[team_type]
            if team not in teams:
                teams[team] = {
                    "home": {"games": 0, "goals_scored": 0, "goals_conceded": 0, "audience": [], "over_2_5": 0},
                    "away": {"games": 0, "goals_scored": 0, "goals_conceded": 0, "audience": [], "over_2_5": 0}
                }
            
            stats_type = "home" if team_type == "home_team" else "away"
            teams[team][stats_type]["games"] += 1
            teams[team][stats_type]["goals_scored"] += game[f"{stats_type}_goals"]
            teams[team][stats_type]["goals_conceded"] += game[f"{'away' if stats_type == 'home' else 'home'}_goals"]
            teams[team][stats_type]["audience"].append(game["audience"])
            if game["total_goals"] > 2.5:
                teams[team][stats_type]["over_2_5"] += 1
    
    league_stats["average_goals"] = safe_divide(league_stats["total_goals"], league_stats["total_matches"])
    league_stats["average_attendance"] = safe_divide(league_stats["total_audience"], league_stats["total_matches"])
    
    return teams, league_stats

def save_md(teams, league_stats):
    with open("Yleisö2025.md", "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 - Tilastot\n\n")
        f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
        
        # Liigatilastot
        f.write("## 📊 Liigatilastot\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write("    title \"Keskiyleisö joukkueittain (Top 5)\"\n")
        sorted_teams = sorted(teams.keys(), key=lambda x: sum(teams[x]['home']['audience'] + teams[x]['away']['audience']), reverse=True)[:5]
        f.write("    x-axis [")
        f.write(", ".join(f'"{team}"' for team in sorted_teams))
        f.write("]\n")
        f.write("    y-axis \"Katsojia\"\n")
        f.write("    bar [")
        f.write(", ".join(
            str(int(safe_divide(
                sum(teams[team]['home']['audience'] + teams[team]['away']['audience']),
                (len(teams[team]['home']['audience']) + len(teams[team]['away']['audience'])) or 1
            )) for team in sorted_teams
        ))
        f.write("]\n")
        f.write("```\n\n")

        # Yleisömäärät vertailu
        f.write("## 📈 Yleisömäärät\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write("    title \"Koti vs Vieras -keskiyleisö (Top 5)\"\n")
        f.write("    x-axis [")
        f.write(", ".join(f'"{team}"' for team in sorted_teams))
        f.write("]\n")
        f.write("    y-axis \"Katsojia\"\n")
        
        # Kotiyleisöt
        f.write("    bar \"Koti\"\n")
        f.write("        [")
        f.write(", ".join(
            str(int(safe_divide(
                sum(teams[team]['home']['audience']),
                len(teams[team]['home']['audience']) or 1
            ))) for team in sorted_teams
        ))
        f.write("]\n")
        
        # Vierasyleisöt
        f.write("    bar \"Vieras\"\n")
        f.write("        [")
        f.write(", ".join(
            str(int(safe_divide(
                sum(teams[team]['away']['audience']),
                len(teams[team]['away']['audience']) or 1
            ))) for team in sorted_teams
        ))
        f.write("]\n")
        f.write("```\n\n")

        # Maalijakauma
        f.write("## ⚽ Maalit\n")
        f.write("```mermaid\n")
        f.write("pie title Maalijakauma\n")
        home_goals = sum(sum(t['home']['goals_scored'] for t in teams.values()))
        away_goals = sum(sum(t['away']['goals_scored'] for t in teams.values()))
        f.write(f'    "Kotimaalit" : {home_goals}\n')
        f.write(f'    "Vierasmaalit" : {away_goals}\n')
        f.write("```\n\n")

        # Joukkuekohtaiset tilastot
        f.write("## 🏆 Joukkuekohtaiset tilastot\n")
        for team in sorted(teams.keys()):
            data = teams[team]
            f.write(f"### 🏟️ {team}\n")
            
            # Yleisöjakauma
            f.write("```mermaid\n")
            f.write(f"pie title {team} - Yleisöjakauma\n")
            f.write(f'    "Kotipelit" : {sum(data["home"]["audience"])}\n')
            f.write(f'    "Vieraspelit" : {sum(data["away"]["audience"])}\n')
            f.write("```\n")
            
            # Maalijakauma
            f.write("```mermaid\n")
            f.write(f"pie title {team} - Maalit\n")
            f.write(f'    "Kotimaalit" : {data["home"]["goals_scored"]}\n')
            f.write(f'    "Vierasmaalit" : {data["away"]["goals_scored"]}\n')
            f.write("```\n")
            
            # Vertailutaulukko
            f.write("### 📊 Vertailu\n")
            f.write("| Statistiikka | Koti | Vieras |\n")
            f.write("|--------------|------|--------|\n")
            f.write(f"| Otteluita | {data['home']['games']} | {data['away']['games']} |\n")
            f.write(f"| Keskiyleisö | {safe_divide(sum(data['home']['audience']), data['home']['games']):.0f} | {safe_divide(sum(data['away']['audience']), data['away']['games']):.0f} |\n")
            f.write(f"| Maalit (tehty/päästetty) | {data['home']['goals_scored']}-{data['home']['goals_conceded']} | {data['away']['goals_scored']}-{data['away']['goals_conceded']} |\n")
            f.write(f"| Yli 2.5 maalia | {data['home']['over_2_5']} ({safe_divide(data['home']['over_2_5']*100, data['home']['games']):.1f}%) | {data['away']['over_2_5']} ({safe_divide(data['away']['over_2_5']*100, data['away']['games']):.1f}%) |\n\n")

if __name__ == "__main__":
    try:
        html = fetch_data()
        games = parse_games(html)
        teams_stats, league_stats = generate_stats(games)
        save_md(teams_stats, league_stats)
        print("✅ Tiedosto Yleisö2025.md päivitetty onnistuneesti!")
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")
