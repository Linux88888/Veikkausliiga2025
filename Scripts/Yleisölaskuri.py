import requests
from bs4 import BeautifulSoup
import datetime
import os

def safe_divide(a, b, default=0):
    return a / b if b != 0 else default

def get_matches():
    url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
    response = requests.get(url)
    response.raise_for_status()
    return parse_matches(BeautifulSoup(response.text, 'html.parser'))

def parse_matches(soup):
    matches = []
    table = soup.find('table', {'id': 'games'})
    if not table:
        return matches

    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 8:
            continue

        try:
            home_team = cells[4].text.strip().split(' - ')[0]
            away_team = cells[4].text.strip().split(' - ')[1]
            result = cells[6].text.strip()
            audience = int(cells[7].text.strip()) if cells[7].text.strip().isdigit() else 0
            
            if '-' in result:
                home_goals, away_goals = map(int, result.split('-'))
                matches.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'audience': audience
                })
        except:
            pass
            
    return matches

def generate_team_stats(matches):
    teams = {}
    for match in matches:
        # Kotijoukkueen tilastot
        if match['home_team'] not in teams:
            teams[match['home_team']] = {
                'home': {'goals_scored': [], 'goals_conceded': [], 'audiences': [], 'over_2_5': 0},
                'away': {'goals_scored': [], 'goals_conceded': [], 'audiences': [], 'over_2_5': 0}
            }
        teams[match['home_team']]['home']['goals_scored'].append(match['home_goals'])
        teams[match['home_team']]['home']['goals_conceded'].append(match['away_goals'])
        teams[match['home_team']]['home']['audiences'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            teams[match['home_team']]['home']['over_2_5'] += 1

        # Vierasjoukkueen tilastot
        if match['away_team'] not in teams:
            teams[match['away_team']] = {
                'home': {'goals_scored': [], 'goals_conceded': [], 'audiences': [], 'over_2_5': 0},
                'away': {'goals_scored': [], 'goals_conceded': [], 'audiences': [], 'over_2_5': 0}
            }
        teams[match['away_team']]['away']['goals_scored'].append(match['away_goals'])
        teams[match['away_team']]['away']['goals_conceded'].append(match['home_goals'])
        teams[match['away_team']]['away']['audiences'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            teams[match['away_team']]['away']['over_2_5'] += 1

    return teams

def save_to_md(teams):
    filename = "Joukkueittaiset_tilastot_2025.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Veikkausliigan joukkueittaiset tilastot 2025\n\n")
            f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
            
            for team, stats in teams.items():
                f.write(f"## {team}\n")
                
                # Kotipelit
                home = stats['home']
                f.write("### Kotipelit\n")
                f.write(f"- Otteluita: {len(home['goals_scored'])}\n")
                f.write(f"- Tehdyt maalit: {sum(home['goals_scored'])}\n")
                f.write(f"- Päästetyt maalit: {sum(home['goals_conceded'])}\n")
                f.write(f"- Yli 2.5 maalia: {home['over_2_5']} ({safe_divide(home['over_2_5']*100, len(home['goals_scored']), 0):.1f}%)\n")
                f.write(f"- Yleisöä keskimäärin: {safe_divide(sum(home['audiences']), len(home['audiences']), 0):.0f}\n")
                f.write(f- Yli 2000 katsojaa: {len([a for a in home['audiences'] if a > 2000])} kpl\n\n")

                # Vieraspelit
                away = stats['away']
                f.write("### Vieraspelit\n")
                f.write(f"- Otteluita: {len(away['goals_scored'])}\n")
                f.write(f"- Tehdyt maalit: {sum(away['goals_scored'])}\n")
                f.write(f"- Päästetyt maalit: {sum(away['goals_conceded'])}\n")
                f.write(f"- Yli 2.5 maalia: {away['over_2_5']} ({safe_divide(away['over_2_5']*100, len(away['goals_scored']), 0):.1f}%)\n")
                f.write(f"- Yleisöä keskimäärin: {safe_divide(sum(away['audiences']), len(away['audiences']), 0):.0f}\n")
                f.write(f- Yli 2000 katsojaa: {len([a for a in away['audiences'] if a > 2000])} kpl\n\n")

            print(f"✅ Tiedosto {filename} luotu onnistuneesti!")
            
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")

if __name__ == "__main__":
    try:
        matches = get_matches()
        team_stats = generate_team_stats(matches)
        save_to_md(team_stats)
    except Exception as e:
        print(f"❌ Päävirhe: {str(e)}")
