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
            date       = cells[1].get_text(strip=True)
            home_team, away_team = cells[4].get_text(strip=True).split(" - ")
            result     = cells[6].get_text(strip=True).replace("—", "-")
            if "-" not in result:
                continue
            home_goals, away_goals = map(int, result.split("-"))
            aud_txt    = cells[7].get_text(strip=True)
            audience   = int(aud_txt) if aud_txt.isdigit() else 0

            games.append({
                "date":       date,
                "home_team":  home_team,
                "away_team":  away_team,
                "home_goals": home_goals,
                "away_goals": away_goals,
                "audience":   audience,
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
    for g in games:
        league_stats["total_goals"]     += g["total_goals"]
        league_stats["total_audience"]  += g["audience"]
        if g["total_goals"] > 2.5:
            league_stats["over_2_5"]     += 1
        league_stats["highest_attendance"] = max(league_stats["highest_attendance"], g["audience"])
        for side in ("home", "away"):
            team = g[f"{side}_team"]
            if team not in teams:
                teams[team] = {
                    "home": {"games":0,"goals_scored":0,"goals_conceded":0,"audience":[],"over_2_5":0},
                    "away": {"games":0,"goals_scored":0,"goals_conceded":0,"audience":[],"over_2_5":0}
                }
            stats = teams[team][side]
            stats["games"]         += 1
            stats["goals_scored"]  += g[f"{side}_goals"]
            other = "away" if side=="home" else "home"
            stats["goals_conceded"]+= g[f"{other}_goals"]
            stats["audience"].append(g["audience"])
            if g["total_goals"] > 2.5:
                stats["over_2_5"]    += 1

    league_stats["average_goals"]      = safe_divide(league_stats["total_goals"], league_stats["total_matches"])
    league_stats["average_attendance"] = safe_divide(league_stats["total_audience"], league_stats["total_matches"])
    return teams, league_stats

def save_md(teams, league_stats, games):
    with open("Yleisö2025.md", "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 – Yleisö- ja maalitilastot\n\n")
        f.write(f"*Päivitetty: {datetime.datetime.now():%d.%m.%Y %H:%M}*\n\n")

        # 1) Kotiyleisöt taulukko
        f.write("## 📋 Kotiyleisöt joukkueittain (suurimmasta pienimpään)\n")
        f.write("| Joukkue | Otteluita | Keski-yleisö | Kokonais-yleisö | Yli 2.5 maalia | % yli 2.5 |\n")
        f.write("|---------|---------:|------------:|---------------:|--------------:|---------:|\n")
        home_sorted = sorted(
            teams.items(),
            key=lambda kv: safe_divide(sum(kv[1]["home"]["audience"]), kv[1]["home"]["games"]),
            reverse=True
        )
        for team, data in home_sorted:
            games_h = data["home"]["games"]
            total_h = sum(data["home"]["audience"])
            avg_h   = safe_divide(total_h, games_h)
            over_h  = data["home"]["over_2_5"]
            pct_h   = safe_divide(over_h * 100, games_h)
            f.write(f"| {team} | {games_h} | {avg_h:.0f} | {total_h} | {over_h} | {pct_h:.1f}% |\n")
        f.write("\n")

        # 2) Vierasyleisöt taulukko
        f.write("## 📋 Vierasyleisöt joukkueittain (suurimmasta pienimpään)\n")
        f.write("| Joukkue | Otteluita | Keski-yleisö | Kokonais-yleisö | Yli 2.5 maalia | % yli 2.5 |\n")
        f.write("|---------|---------:|------------:|---------------:|--------------:|---------:|\n")
        away_sorted = sorted(
            teams.items(),
            key=lambda kv: safe_divide(sum(kv[1]["away"]["audience"]), kv[1]["away"]["games"]),
            reverse=True
        )
        for team, data in away_sorted:
            games_a = data["away"]["games"]
            total_a = sum(data["away"]["audience"])
            avg_a   = safe_divide(total_a, games_a)
            over_a  = data["away"]["over_2_5"]
            pct_a   = safe_divide(over_a * 100, games_a)
            f.write(f"| {team} | {games_a} | {avg_a:.0f} | {total_a} | {over_a} | {pct_a:.1f}% |\n")
        f.write("\n")

        # 3) Top 5 kotiottelut per joukkue (päivä, vastustaja, yleisö ja maalit)
        f.write("## 🏟️ Joukkueiden Top 5 kotiotteluja\n")
        for team, data in teams.items():
            home_games = [g for g in games if g["home_team"] == team]
            if not home_games:
                continue
            top5 = sorted(home_games, key=lambda g: g["audience"], reverse=True)[:5]
            f.write(f"### {team}\n")
            f.write("| Päivä | Vastustaja | Yleisö | Maalit |\n")
            f.write("|------|-----------|--------:|-------:|\n")
            for g in top5:
                score = f"{g['home_goals']}-{g['away_goals']}"
                f.write(f"| {g['date']} | {g['away_team']} | {g['audience']} | {score} |\n")
            f.write("\n")

if __name__ == "__main__":
    try:
        html = fetch_data()
        games = parse_games(html)
        teams, league_stats = generate_stats(games)
        save_md(teams, league_stats, games)
        print("✅ Yleisö2025.md päivitetty onnistuneesti!")
    except Exception as e:
        print(f"❌ Virhe: {e}")
