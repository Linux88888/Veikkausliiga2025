import requests
from bs4 import BeautifulSoup
import datetime
import os

def safe_divide(a, b, default=0):
    return a / b if b != 0 else default

def get_all_teams(soup):
    """Hakee kaikki joukkueet valikon select-elementistä"""
    teams = []
    select = soup.find('select', {'name': 'team'})
    if select:
        for option in select.find_all('option'):
            if option['value'] and option['value'] != '0':
                teams.append(option.text.strip())
    return teams

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
            result = cells[6].text.strip().replace('\u2013', '-').replace(' ', '')
            audience = cells[7].text.strip()
            
            if '-' in result and result != '-':
                home_goals, away_goals = map(int, result.split('-'))
                matches.append({
                    'date': date,
                    'time': time,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'audience': int(audience) if audience.isdigit() else 0,
                    'played': True
                })
            else:
                # Tulevat ottelut
                matches.append({
                    'date': date,
                    'time': time,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_goals': 0,
                    'away_goals': 0,
                    'audience': 0,
                    'played': False
                })
        except Exception as e:
            print(f"Virhe rivin käsittelyssä: {str(e)}")
    
    return matches

def generate_team_stats(matches, all_teams):
    # Alusta kaikki joukkueet
    teams = {team: {
        'home': {'games': 0, 'goals_scored': 0, 'goals_conceded': 0, 'over_2_5': 0, 'audiences': []},
        'away': {'games': 0, 'goals_scored': 0, 'goals_conceded': 0, 'over_2_5': 0, 'audiences': []}
    } for team in all_teams}

    for match in matches:
        if not match['played']:
            continue
        
        # Kotijoukkueen tilastot
        home = teams[match['home_team']]['home']
        home['games'] += 1
        home['goals_scored'] += match['home_goals']
        home['goals_conceded'] += match['away_goals']
        home['audiences'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            home['over_2_5'] += 1

        # Vierasjoukkueen tilastot
        away = teams[match['away_team']]['away']
        away['games'] += 1
        away['goals_scored'] += match['away_goals']
        away['goals_conceded'] += match['home_goals']
        away['audiences'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            away['over_2_5'] += 1

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
                f.write(f"- Otteluita: {home['games']}\n")
                f.write(f"- Tehdyt maalit: {home['goals_scored']}\n")
                f.write(f"- Päästetyt maalit: {home['goals_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {home['over_2_5']} ({safe_divide(home['over_2_5']*100, home['games']):.1f}%)\n")
                f.write(f"- Yleisöä keskimäärin: {safe_divide(sum(home['audiences']), len(home['audiences'])):.0f}\n")
                f.write(f"- Yli 2000 katsojaa: {len([a for a in home['audiences'] if a > 2000])} kpl\n\n")

                # Vieraspelit
                away = stats['away']
                f.write("### Vieraspelit\n")
                f.write(f"- Otteluita: {away['games']}\n")
                f.write(f"- Tehdyt maalit: {away['goals_scored']}\n")
                f.write(f"- Päästetyt maalit: {away['goals_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {away['over_2_5']} ({safe_divide(away['over_2_5']*100, away['games']):.1f}%)\n")
                f.write(f"- Yleisöä keskimäärin: {safe_divide(sum(away['audiences']), len(away['audiences'])):.0f}\n")
                f.write(f"- Yli 2000 katsojaa: {len([a for a in away['audiences'] if a > 2000])} kpl\n\n")

        print(f"✅ Tiedosto {filename} päivitetty onnistuneesti!")
        print(f"📂 Tiedoston sijainti: {os.path.abspath(filename)}")
        
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")

def main():
    try:
        url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        all_teams = get_all_teams(soup)
        matches = parse_matches(soup)
        team_stats = generate_team_stats(matches, all_teams)
        save_to_md(team_stats)
        
    except Exception as e:
        print(f"❌ Päävirhe: {str(e)}")

if __name__ == "__main__":
    main()
