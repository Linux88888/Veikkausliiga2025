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
    
    current_date = None
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 8:
            continue

        try:
            # Päivämäärä
            date_cell = row.find('td', {'class': 'desktop-only'})
            if date_cell and date_cell.text.strip():
                current_date = " ".join(date_cell.text.strip().split()[1:])

            # Aika
            time = cells[2].text.strip() if len(cells) > 2 else "?"
            
            # Joukkueet
            teams = cells[4].text.strip().split(' - ')
            if len(teams) != 2:
                continue
                
            # Tulos ja yleisömäärä
            result = cells[6].text.strip().replace('—', '-')
            audience = cells[7].text.strip()
            
            if '-' in result:
                home_goals, away_goals = map(int, result.split('-'))
                matches.append({
                    'date': current_date,
                    'time': time,
                    'home_team': teams[0].strip(),
                    'away_team': teams[1].strip(),
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'audience': int(audience) if audience.isdigit() else 0
                })
        except Exception as e:
            print(f"Virhe ottelun käsittelyssä: {str(e)}")
    
    return matches

def generate_team_stats(matches):
    teams = {}
    for match in matches:
        # Kotijoukkueen tilastot
        home_team = match['home_team']
        if home_team not in teams:
            teams[home_team] = {
                'home': {'goals_scored': [], 'goals_conceded': [], 'audiences': [], 'over_2_5': 0},
                'away': {'goals_scored': [], 'goals_conceded': [], 'audiences': [], 'over_2_5': 0}
            }
        teams[home_team]['home']['goals_scored'].append(match['home_goals'])
        teams[home_team]['home']['goals_conceded'].append(match['away_goals'])
        teams[home_team]['home']['audiences'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            teams[home_team]['home']['over_2_5'] += 1

        # Vierasjoukkueen tilastot
        away_team = match['away_team']
        if away_team not in teams:
            teams[away_team] = {
                'home': {'goals_scored': [], 'goals_conceded': [], 'audiences': [], 'over_2_5': 0},
                'away': {'goals_scored': [], 'goals_conceded': [], 'audiences': [], 'over_2_5': 0}
            }
        teams[away_team]['away']['goals_scored'].append(match['away_goals'])
        teams[away_team]['away']['goals_conceded'].append(match['home_goals'])
        teams[away_team]['away']['audiences'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            teams[away_team]['away']['over_2_5'] += 1

    return teams

def save_to_md(teams):
    filename = "Joukkueittaiset_tilastot_2025.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Veikkausliigan joukkueittaiset tilastot 2025\n\n")
            f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
            
            for team, stats in sorted(teams.items()):
                f.write(f"## {team}\n")
                
                # Kotipelit
                home = stats['home']
                f.write("### Kotipelit\n")
                f.write(f"- Otteluita: {len(home['goals_scored'])}\n")
                f.write(f"- Tehdyt maalit: {sum(home['goals_scored'])}\n")
                f.write(f"- Päästetyt maalit: {sum(home['goals_conceded'])}\n")
                f.write(f"- Yli 2.5 maalia: {home['over_2_5']} ({safe_divide(home['over_2_5']*100, len(home['goals_scored']), 0):.1f}%)\n")
                f.write(f"- Yleisöä keskimäärin: {safe_divide(sum(home['audiences']), len(home['audiences']), 0):.0f}\n")
                f.write(f"- Yli 2000 katsojaa: {len([a for a in home['audiences'] if a > 2000])} kpl\n\n")

                # Vieraspelit
                away = stats['away']
                f.write("### Vieraspelit\n")
                f.write(f"- Otteluita: {len(away['goals_scored'])}\n")
                f.write(f"- Tehdyt maalit: {sum(away['goals_scored'])}\n")
                f.write(f"- Päästetyt maalit: {sum(away['goals_conceded'])}\n")
                f.write(f"- Yli 2.5 maalia: {away['over_2_5']} ({safe_divide(away['over_2_5']*100, len(away['goals_scored']), 0):.1f}%)\n")
                f.write(f"- Yleisöä keskimäärin: {safe_divide(sum(away['audiences']), len(away['audiences']), 0):.0f}\n")
                f.write(f"- Yli 2000 katsojaa: {len([a for a in away['audiences'] if a > 2000])} kpl\n\n")

            print(f"✅ Tiedosto {filename} luotu onnistuneesti!")
            print(f"📂 Tiedoston sijainti: {os.path.abspath(filename)}")
            
    except Exception as e:
        print(f"❌ Virhe tiedoston kirjoituksessa: {str(e)}")

if __name__ == "__main__":
    try:
        matches = get_matches()
        team_stats = generate_team_stats(matches)
        save_to_md(team_stats)
    except Exception as e:
        print(f"❌ Pääohjelman virhe: {str(e)}")
