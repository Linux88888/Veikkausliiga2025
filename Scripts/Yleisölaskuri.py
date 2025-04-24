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
        
        # Päivitä joukkueiden tiedot
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
    
    # Laske liigan keskiarvot
    league_stats["average_goals"] = safe_divide(league_stats["total_goals"], league_stats["total_matches"])
    league_stats["average_attendance"] = safe_divide(league_stats["total_audience"], league_stats["total_matches"])
    
    return teams, league_stats

def save_md(teams, league_stats):
    with open("Yleisö2025.md", "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 - Tilastot\n\n")
        f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
        
        # Liigatason tilastot
        f.write("## 📊 Liigatilastot\n")
        f.write("| Statistiikka | Arvo |\n")
        f.write("|--------------|------|\n")
        f.write(f"| Pelatut ottelut | {league_stats['total_matches']} |\n")
        f.write(f"| Yhteensä maaleja | {league_stats['total_goals']} |\n")
        f.write(f"| Maaleja per ottelu | {league_stats['average_goals']:.1f} |\n")
        f.write(f"| Yli 2.5 maalin otteluita | {league_stats['over_2_5']} ({safe_divide(league_stats['over_2_5']*100, league_stats['total_matches']):.1f}%) |\n")
        f.write(f"| Yleisöä yhteensä | {league_stats['total_audience']:,} |\n")
        f.write(f"| Keskimääräinen yleisömäärä | {league_stats['average_attendance']:.0f} |\n")
        f.write(f"| Suurin yleisömäärä | {league_stats['highest_attendance']:,} |\n\n")
        
        # Kaavio yleisömääristä
        f.write("```mermaid\n")
        f.write("pie title Yleisömäärät\n")
        sorted_teams = sorted(teams.items(), key=lambda x: sum(x[1]['home']['audience'] + x[1]['away']['audience']), reverse=True)
        for team, data in sorted_teams[:5]:  # Näytä top 5
            total = sum(data['home']['audience'] + data['away']['audience'])
            f.write(f'    "{team}" : {total}\n')
        f.write("```\n\n")
        
        # Joukkuekohtaiset tilastot
        f.write("## 🏆 Joukkuekohtaiset tilastot\n")
        for team in sorted(teams.keys()):
            data = teams[team]
            f.write(f"### {team}\n")
            
            # Kotipelit
            f.write("#### 🏠 Kotipelit\n")
            home = data["home"]
            f.write("| Statistiikka | Arvo |\n")
            f.write("|--------------|------|\n")
            f.write(f"| Otteluita | {home['games']} |\n")
            f.write(f"| Tehdyt maalit | {home['goals_scored']} |\n")
            f.write(f"| Päästetyt maalit | {home['goals_conceded']} |\n")
            f.write(f"| Yli 2.5 maalia | {home['over_2_5']} ({safe_divide(home['over_2_5']*100, home['games']):.1f}%) |\n")
            f.write(f"| Keskiverto yleisö | {safe_divide(sum(home['audience']), home['games']):.0f} |\n")
            f.write(f"| Yli 2000 katsojaa | {sum(1 for a in home['audience'] if a > 2000)} |\n\n")
            
            # Vieraspelit
            f.write("#### ✈️ Vieraspelit\n")
            away = data["away"]
            f.write("| Statistiikka | Arvo |\n")
            f.write("|--------------|------|\n")
            f.write(f"| Otteluita | {away['games']} |\n")
            f.write(f"| Tehdyt maalit | {away['goals_scored']} |\n")
            f.write(f"| Päästetyt maalit | {away['goals_conceded']} |\n")
            f.write(f"| Yli 2.5 maalia | {away['over_2_5']} ({safe_divide(away['over_2_5']*100, away['games']):.1f}%) |\n")
            f.write(f"| Keskiverto yleisö | {safe_divide(sum(away['audience']), away['games']):.0f} |\n")
            f.write(f"| Yli 2000 katsojaa | {sum(1 for a in away['audience'] if a > 2000)} |\n\n")

if __name__ == "__main__":
    try:
        html = fetch_data()
        games = parse_games(html)
        teams_stats, league_stats = generate_stats(games)
        save_md(teams_stats, league_stats)
        print("✅ Tiedosto Yleisö2025.md päivitetty onnistuneesti!")
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")
