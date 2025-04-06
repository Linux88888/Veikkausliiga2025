import requests
from bs4 import BeautifulSoup
import datetime
import os

def safe_divide(a, b, default=0):
    return a / b if b != 0 else default

def get_matches():
    url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
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
            # Parsi päivämäärä ja aika
            date = cells[1].text.strip().split()[-1]  # "La 5.4.2025" -> "5.4.2025"
            time = cells[2].text.strip()
            
            # Parsi joukkueet
            teams = cells[4].text.strip().split(' - ')
            if len(teams) != 2:
                continue
            home_team, away_team = teams[0].strip(), teams[1].strip()
            
            # Parsi tulos ja yleisömäärä
            result = cells[6].text.strip().replace('—', '-').replace(' ', '')
            audience = cells[7].text.strip()
            
            if result != '-' and '-' in result:
                home_goals, away_goals = map(int, result.split('-'))
                matches.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'audience': int(audience) if audience.isdigit() else 0
                })
        except Exception as e:
            print(f"Virhe ottelun käsittelyssä: {str(e)}")
    
    return matches

def get_all_teams(soup):
    teams = []
    select = soup.find('select', {'name': 'team'})
    if select:
        for option in select.find_all('option'):
            if option.get('value') not in ['', '0']:
                teams.append(option.text.strip())
    return teams

def generate_team_stats(matches, all_teams):
    stats = {team: {
        'home': {'games': 0, 'goals_scored': 0, 'goals_conceded': 0, 'over_2_5': 0, 'audiences': []},
        'away': {'games': 0, 'goals_scored': 0, 'goals_conceded': 0, 'over_2_5': 0, 'audiences': []}
    } for team in all_teams}

    for match in matches:
        # Kotijoukkueen tilastot
        home = stats[match['home_team']]['home']
        home['games'] += 1
        home['goals_scored'] += match['home_goals']
        home['goals_conceded'] += match['away_goals']
        home['audiences'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            home['over_2_5'] += 1

        # Vierasjoukkueen tilastot
        away = stats[match['away_team']]['away']
        away['games'] += 1
        away['goals_scored'] += match['away_goals']
        away['goals_conceded'] += match['home_goals']
        away['audiences'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            away['over_2_5'] += 1

    return stats

def save_to_md(stats):
    filename = "yleisö.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Veikkausliigan tilastot 2025\n\n")
            f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
            
            f.write("## Joukkuekohtaiset tilastot\n")
            for team in sorted(stats.keys()):
                data = stats[team]
                f.write(f"### {team}\n")
                
                # Kotipelit
                f.write("#### Kotipelit\n")
                f.write(f"- Otteluita: {data['home']['games']}\n")
                f.write(f"- Tehdyt maalit: {data['home']['goals_scored']}\n")
                f.write(f"- Päästetyt maalit: {data['home']['goals_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {data['home']['over_2_5']} ({safe_divide(data['home']['over_2_5']*100, data['home']['games']):.1f}%)\n")
                f.write(f"- Keskimääräinen yleisömäärä: {safe_divide(sum(data['home']['audiences']), len(data['home']['audiences'])):.0f}\n")
                f.write(f"- Yli 2000 katsojaa: {len([a for a in data['home']['audiences'] if a > 2000])} kpl\n\n")
                
                # Vieraspelit
                f.write("#### Vieraspelit\n")
                f.write(f"- Otteluita: {data['away']['games']}\n")
                f.write(f"- Tehdyt maalit: {data['away']['goals_scored']}\n")
                f.write(f"- Päästetyt maalit: {data['away']['goals_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {data['away']['over_2_5']} ({safe_divide(data['away']['over_2_5']*100, data['away']['games']):.1f}%)\n")
                f.write(f"- Keskimääräinen yleisömäärä: {safe_divide(sum(data['away']['audiences']), len(data['away']['audiences'])):.0f}\n")
                f.write(f"- Yli 2000 katsojaa: {len([a for a in data['away']['audiences'] if a > 2000])} kpl\n\n")
        
        print(f"✅ Tiedosto '{os.path.abspath(filename)}' luotu onnistuneesti!")
        
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")

if __name__ == "__main__":
    try:
        # Hae data
        response = requests.get("https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/", 
                              headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Prosessoi data
        all_teams = get_all_teams(soup)
        matches = parse_matches(soup)
        team_stats = generate_team_stats(matches, all_teams)
        save_to_md(team_stats)
        
    except Exception as e:
        print(f"❌ Päävirhe: {str(e)}")
