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
            home_team, away_team = cells[4].get_text(strip=True).split(" - ")
            home_goals, away_goals = map(int, result.split("-"))
            aud_txt = cells[7].get_text(strip=True)
            audience = int(aud_txt) if aud_txt.isdigit() else 0
            games.append({
                "home_team": home_team,
                "away_team": away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "audience": audience,
                "total_goals": home_goals + away_goals
            })
        except Exception as e:
            print(f"Virhe rivillä: {e}")
    return games

def generate_stats(games):
    teams = {}
    league_stats = {
        "total_matches": len(games),
        "total_goals": 0,
        "total_audience": 0,
        "over_2_5": 0,
        "highest_attendance": 0
    }
    for game in games:
        league_stats["total_goals"] += game["total_goals"]
        league_stats["total_audience"] += game["audience"]
        if game["total_goals"] > 2.5:
            league_stats["over_2_5"] += 1
        league_stats["highest_attendance"] = max(league_stats["highest_attendance"], game["audience"])
        for side in ("home", "away"):
            team = game[f"{side}_team"]
            if team not in teams:
                teams[team] = {
                    "home": {"games":0,"goals_scored":0,"goals_conceded":0,"audience":[],"over_2_5":0},
                    "away": {"games":0,"goals_scored":0,"goals_conceded":0,"audience":[],"over_2_5":0},
                }
            stats = teams[team][side]
            stats["games"] += 1
            stats["goals_scored"] += game[f"{side}_goals"]
            other_side = "away" if side=="home" else "home"
            stats["goals_conceded"] += game[f"{other_side}_goals"]
            stats["audience"].append(game["audience"])
            if game["total_goals"] > 2.5:
                stats["over_2_5"] += 1

    league_stats["average_goals"] = safe_divide(league_stats["total_goals"], league_stats["total_matches"])
    league_stats["average_attendance"] = safe_divide(league_stats["total_audience"], league_stats["total_matches"])
    return teams, league_stats

def save_md(teams, league_stats):
    with open("Yleisö2025.md", "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 - Tilastot\n\n")
        f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")

        # Liigatilastot
        f.write("## 📊 Liigatilastot\n```mermaid\n")
        f.write("xychart-beta\n")
        f.write("    title \"Keskiyleisö joukkueittain (Top 5)\"\n")
        sorted_teams = sorted(teams, key=lambda t: sum(teams[t]['home']['audience']+teams[t]['away']['audience']), reverse=True)[:5]
        f.write("    x-axis [" + ", ".join(f'"{t}"' for t in sorted_teams) + "]\n")
        f.write("    y-axis \"Katsojia\"\n")
        f.write("    bar [" + ", ".join(
            str(int(safe_divide(
                sum(teams[t]['home']['audience']+teams[t]['away']['audience']),
                len(teams[t]['home']['audience'])+len(teams[t]['away']['audience']) or 1
            ))) for t in sorted_teams
        ) + "]\n")
        f.write("```\n\n")

        # Yleisömäärät vertailu
        f.write("## 📈 Yleisömäärät\n```mermaid\n")
        f.write("xychart-beta\n")
        f.write("    title \"Koti vs Vieras -keskiyleisö (Top 5)\"\n")
        f.write("    x-axis [" + ", ".join(f'"{t}"' for t in sorted_teams) + "]\n")
        f.write("    y-axis \"Katsojia\"\n")
        # Koti vs vieras yhdessä rivissä
        f.write("    bar \"Koti\" [" + ", ".join(
            str(int(safe_divide(
                sum(teams[t]['home']['audience']),
                len(teams[t]['home']['audience']) or 1
            ))) for t in sorted_teams
        ) + "]\n")
        f.write("    bar \"Vieras\" [" + ", ".join(
            str(int(safe_divide(
                sum(teams[t]['away']['audience']),
                len(teams[t]['away']['audience']) or 1
            ))) for t in sorted_teams
        ) + "]\n")
        f.write("```\n\n")

        # Maalijakauma
        f.write("## ⚽ Maalit\n```mermaid\n")
        f.write("pie title Maalijakauma\n")
        home_goals = sum(teams[t]['home']['goals_scored'] for t in teams)
        away_goals = sum(teams[t]['away']['goals_scored'] for t in teams)
        f.write(f'    "Kotimaalit" : {home_goals}\n')
        f.write(f'    "Vierasmaalit" : {away_goals}\n')
        f.write("```\n\n")

        # Joukkuekohtaiset tilastot
        f.write("## 🏆 Joukkuekohtaiset tilastot\n")
        for t in sorted(teams):
            d = teams[t]
            f.write(f"### 🏟️ {t}\n")
            f.write("```mermaid\npie title Yleisöjakauma\n")
            f.write(f'    "Kotipelit" : {sum(d["home"]["audience"])}\n')
            f.write(f'    "Vieraspelit" : {sum(d["away"]["audience"])}\n```')
            f.write("\n```mermaid\npie title Maalit\n")
            f.write(f'    "Kotimaalit" : {d["home"]["goals_scored"]}\n')
            f.write(f'    "Vierasmaalit" : {d["away"]["goals_scored"]}\n```')
            f.write(
                f"\n### 📊 Vertailu\n"
                f"| Statistiikka | Koti | Vieras |\n"
                f"|--------------|------|--------|\n"
                f"| Otteluita | {d['home']['games']} | {d['away']['games']} |\n"
                f"| Keskiyleisö | {safe_divide(sum(d['home']['audience']), d['home']['games']):.0f} | {safe_divide(sum(d['away']['audience']), d['away']['games']):.0f} |\n"
                f"| Maalit (tehty/päästetty) | {d['home']['goals_scored']}-{d['home']['goals_conceded']} | {d['away']['goals_scored']}-{d['away']['goals_conceded']} |\n"
                f"| Yli 2.5 maalia | {d['home']['over_2_5']} ({safe_divide(d['home']['over_2_5']*100, d['home']['games']):.1f}%) | {d['away']['over_2_5']} ({safe_divide(d['away']['over_2_5']*100, d['away']['games']):.1f}%) |\n\n"
            )

if __name__ == "__main__":
    try:
        html = fetch_data()
        games = parse_games(html)
        teams, league_stats = generate_stats(games)
        save_md(teams, league_stats)
        print("✅ Yleisö2025.md päivitetty onnistuneesti!")
    except Exception as e:
        print(f"❌ Virhe: {e}")
