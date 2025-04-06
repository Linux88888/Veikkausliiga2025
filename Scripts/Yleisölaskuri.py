import os
import re
from bs4 import BeautifulSoup
import datetime

def parse_matches(html_content):
    """Parsii ottelutiedot HTML-sisällöstä"""
    soup = BeautifulSoup(html_content, 'html.parser')
    matches = []
    
    # Etsi ottelutaulukko
    table = soup.find('table', {'id': 'games'})
    if not table:
        return matches
    
    current_date = None
    for row in table.find('tbody').find_all('tr'):
        # Päivämäärän käsittely
        date_cell = row.find('td', {'class': 'desktop-only'})
        if date_cell and date_cell.text.strip():
            current_date = date_cell.text.strip().split()[1]  # "La 5.4.2025" -> "5.4.2025"
        
        # Hae solut
        cells = row.find_all('td')
        if len(cells) < 7:
            continue
            
        # Aika
        time_cell = cells[2] if len(cells) > 2 else None
        time = time_cell.text.strip() if time_cell else None
        
        # Joukkueet
        teams_link = cells[3].find('a')
        if teams_link:
            teams = teams_link.text.strip().split(' - ')
            if len(teams) == 2:
                home_team = teams[0].strip()
                away_team = teams[1].strip()
            else:
                continue
        else:
            continue
            
        # Tulos
        result = cells[5].find('span').text.strip().replace('—', '-')
        home_goals, away_goals = map(int, result.split('-'))
        
        # Yleisömäärä
        audience = int(cells[6].text.strip()) if cells[6].text.strip().isdigit() else 0
        
        matches.append({
            'date': current_date,
            'time': time,
            'home_team': home_team,
            'away_team': away_team,
            'home_goals': home_goals,
            'away_goals': away_goals,
            'audience': audience
        })
    
    return matches

# Esimerkkikäyttö
with open("debug_page.html", "r", encoding="utf-8") as f:
    html = f.read()

matches = parse_matches(html)

# Tulosta tulokset testiksi
for i, match in enumerate(matches, 1):
    print(f"Ottelu {i}:")
    print(f"Päivämäärä: {match['date']}")
    print(f"Kellonaika: {match['time']}")
    print(f"Kotijoukkue: {match['home_team']}")
    print(f"Vierasjoukkue: {match['away_team']}")
    print(f"Tulos: {match['home_goals']}-{match['away_goals']}")
    print(f"Yleisöä: {match['audience']}")
    print("-" * 30)
