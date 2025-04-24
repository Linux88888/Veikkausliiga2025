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
    # Pysytään samana kuin edellisessä versiossa
    # ...
    return games

def generate_stats(games):
    # Pysytään samana kuin edellisessä versiossa
    # ...
    return teams, league_stats

def save_md(teams, league_stats):
    with open("Yleisö2025.md", "w", encoding="utf-8") as f:
        f.write(f"# Veikkausliiga 2025 - Tilastot\n\n")
        f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
        
        # Liigatason tilastot
        f.write("## 📊 Liigatilastot\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write("    title \"Keskiyleisö joukkueittain (Top 5)\"\n")
        f.write("    x-axis [")
        f.write(", ".join(f'"{team}"' for team in sorted(teams.keys())[:5]))
        f.write("]\n")
        f.write("    y-axis \"Katsojia\" 0 --> 10000\n")
        f.write("    bar [")
        f.write(", ".join(str(int(safe_divide(sum(teams[team]['home']['audience']) + sum(teams[team]['away']['audience']), 
                            (len(teams[team]['home']['audience']) + len(teams[team]['away']['audience'])) or 1))) 
                        for team in sorted(teams.keys())[:5]))
        f.write("]\n")
        f.write("```\n\n")

        # Yleisömäärät kotona vs vieraissa
        f.write("## 📈 Yleisömäärät\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write("    title \"Koti vs Vieras -keskiyleisö (Top 5)\"\n")
        f.write("    x-axis [")
        f.write(", ".join(f'"{team}"' for team in sorted(teams.keys())[:5]))
        f.write("]\n")
        f.write("    y-axis \"Katsojia\"\n")
        f.write("    bar \"Koti\"\n")
        f.write("        [")
        f.write(", ".join(str(int(safe_divide(sum(teams[team]['home']['audience']), len(teams[team]['home']['audience']))) 
                        for team in sorted(teams.keys())[:5]))
        f.write("]\n")
        f.write("    bar \"Vieras\"\n")
        f.write("        [")
        f.write(", ".join(str(int(safe_divide(sum(teams[team]['away']['audience']), len(teams[team]['away']['audience']))) 
                        for team in sorted(teams.keys())[:5]))
        f.write("]\n")
        f.write("```\n\n")

        # Maalit kotona vs vieraissa
        f.write("## ⚽ Maalit\n")
        f.write("```mermaid\n")
        f.write("pie title Maalijakauma\n")
        f.write('    "Kotimaalit" : ' + str(sum(sum(t['home']['goals_scored'] for t in teams.values())) + "\n")
        f.write('    "Vierasmaalit" : ' + str(sum(sum(t['away']['goals_scored'] for t in teams.values())) + "\n")
        f.write("```\n\n")

        # Yleisöhistogrammi
        f.write("## 📅 Yleisömäärän jakauma\n")
        f.write("```mermaid\n")
        f.write("xychart-beta\n")
        f.write("    title \"Yleisömäärän esiintyvyys\"\n")
        f.write("    x-axis [\"0-1999\", \"2000-3999\", \"4000-5999\", \"6000+\"]\n")
        f.write("    y-axis \"Ottelut\"\n")
        f.write("    bar [")
        audiences = [game['audience'] for game in games]
        f.write(f"{sum(1 for a in audiences if a < 2000)}, ")
        f.write(f"{sum(1 for a in audiences if 2000 <= a < 4000)}, ")
        f.write(f"{sum(1 for a in audiences if 4000 <= a < 6000)}, ")
        f.write(f"{sum(1 for a in audiences if a >= 6000)}")
        f.write("]\n")
        f.write("```\n\n")

        # Joukkuekohtaiset vertailut
        for team in sorted(teams.keys()):
            data = teams[team]
            f.write(f"## 🏟️ {team} - Avainluvut\n")
            
            # Yleisövertailu
            f.write("```mermaid\n")
            f.write(f"pie title {team} - Yleisöjakauma\n")
            f.write(f'    "Kotipelit" : {sum(data["home"]["audience"])}\n')
            f.write(f'    "Vieraspelit" : {sum(data["away"]["audience"])}\n')
            f.write("```\n")
            
            # Maalivertailu
            f.write("```mermaid\n")
            f.write(f"pie title {team} - Maalijakauma\n")
            f.write(f'    "Kotimaalit" : {data["home"]["goals_scored"]}\n')
            f.write(f'    "Vierasmaalit" : {data["away"]["goals_scored"]}\n')
            f.write("```\n\n")
            
            # Detaileja
            f.write("### 📋 Yksityiskohdat\n")
            f.write("| Statistiikka | Koti | Vieras |\n")
            f.write("|--------------|------|--------|\n")
            f.write(f"| Otteluita | {data['home']['games']} | {data['away']['games']} |\n")
            f.write(f"| Keskiyleisö | {safe_divide(sum(data['home']['audience']), data['home']['games']):.0f} | {safe_divide(sum(data['away']['audience']), data['away']['games']):.0f} |\n")
            f.write(f"| Maalit (tehty/päästetty) | {data['home']['goals_scored']}-{data['home']['goals_conceded']} | {data['away']['goals_scored']}-{data['away']['goals_conceded']} |\n")
            f.write(f"| Yli 2.5 maalia % | {safe_divide(data['home']['over_2_5']*100, data['home']['games']):.1f}% | {safe_divide(data['away']['over_2_5']*100, data['away']['games']):.1f}% |\n\n")

if __name__ == "__main__":
    try:
        html = fetch_data()
        games = parse_games(html)
        teams_stats, league_stats = generate_stats(games)
        save_md(teams_stats, league_stats)
        print("✅ Tiedosto Yleisö2025.md päivitetty onnistuneesti!")
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")
