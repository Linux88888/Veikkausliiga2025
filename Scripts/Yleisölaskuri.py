import requests
from bs4 import BeautifulSoup
import datetime
import os

def safe_divide(a, b, default=0):
    return a / b if b != 0 else default

def get_matches():
    url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return parse_matches(soup)

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
            # Parsi tiedot
            date = cells[1].text.strip().split()[-1]  # "La 5.4.2025" -> "5.4.2025"
            time = cells[2].text.strip()
            teams = cells[4].text.strip().split(' - ')
            result = cells[6].text.strip().replace('\u2013', '-')
            audience = cells[7].text.strip()
            
            if len(teams) == 2 and '-' in result and result != '-':
                home_team, away_team = teams[0].strip(), teams[1].strip()
                home_goals, away_goals = map(int, result.split('-'))
                matches.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'audience': int(audience) if audience.isdigit() else 0
                })
        except Exception as e:
            print(f"Virhe: {str(e)}")
    
    return matches

def generate_stats(matches):
    stats = {}
    for match in matches:
        # Kotijoukkue
        if match['home_team'] not in stats:
            stats[match['home_team']] = {
                'home_goals': 0,
                'home_conceded': 0,
                'home_audience': [],
                'home_over_2_5': 0
            }
        stats[match['home_team']]['home_goals'] += match['home_goals']
        stats[match['home_team']]['home_conceded'] += match['away_goals']
        stats[match['home_team']]['home_audience'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            stats[match['home_team']]['home_over_2_5'] += 1
        
        # Vierasjoukkue
        if match['away_team'] not in stats:
            stats[match['away_team']] = {
                'away_goals': 0,
                'away_conceded': 0,
                'away_audience': [],
                'away_over_2_5': 0
            }
        stats[match['away_team']]['away_goals'] += match['away_goals']
        stats[match['away_team']]['away_conceded'] += match['home_goals']
        stats[match['away_team']]['away_audience'].append(match['audience'])
        if (match['home_goals'] + match['away_goals']) > 2.5:
            stats[match['away_team']]['away_over_2_5'] += 1
    
    return stats

def save_to_md(stats):
    filename = "yleisö.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Veikkausliigan tilastot 2025\n\n")
            f.write(f"Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
            
            f.write("## Joukkuekohtaiset tilastot\n")
            for team, data in sorted(stats.items()):
                f.write(f"### {team}\n")
                
                # Kotipelit
                f.write("#### Kotipelit\n")
                f.write(f"- Otteluita: {len(data['home_audience']}\n")
                f.write(f"- Tehdyt maalit: {data['home_goals']}\n")
                f.write(f"- Päästetyt maalit: {data['home_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {data['home_over_2_5']} ({safe_divide(data['home_over_2_5']*100, len(data['home_audience'])):.1f}%)\n")
                f.write(f"- Keskiverto yleisö: {safe_divide(sum(data['home_audience']), len(data['home_audience'])):.0f}\n")
                f.write(f"- Yli 2000 katsojaa: {len([x for x in data['home_audience'] if x > 2000])} kpl\n\n")
                
                # Vieraspelit
                f.write("#### Vieraspelit\n")
                f.write(f"- Otteluita: {len(data['away_audience']}\n")
                f.write(f"- Tehdyt maalit: {data['away_goals']}\n")
                f.write(f"- Päästetyt maalit: {data['away_conceded']}\n")
                f.write(f"- Yli 2.5 maalia: {data['away_over_2_5']} ({safe_divide(data['away_over_2_5']*100, len(data['away_audience'])):.1f}%)\n")
                f.write(f"- Keskiverto yleisö: {safe_divide(sum(data['away_audience']), len(data['away_audience'])):.0f}\n")
                f.write(f"- Yli 2000 katsojaa: {len([x for x in data['away_audience'] if x > 2000])} kpl\n\n")
        
        print(f"✅ Tiedosto '{os.path.abspath(filename)}' päivitetty onnistuneesti!")
        
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")

if __name__ == "__main__":
    try:
        matches = get_matches()
        stats = generate_stats(matches)
        save_to_md(stats)
    except Exception as e:
        print(f"❌ Päävirhe: {str(e)}")
