import requests
from bs4 import BeautifulSoup
import datetime

def get_matches():
    # Hae data suoraan verkkosivulta
    url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
    response = requests.get(url)
    response.raise_for_status()  # Tarkista virheet
    
    # Parsii HTML-sisällön
    soup = BeautifulSoup(response.text, 'html.parser')
    return parse_matches(soup)

def parse_matches(soup):
    """Parsii ottelutiedot BeautifulSoup-oliosta"""
    matches = []
    table = soup.find('table', {'id': 'games'})
    
    if not table:
        return matches
    
    current_date = None
    for row in table.find('tbody').find_all('tr'):
        # Päivämäärän käsittely
        date_cell = row.find('td', {'class': 'desktop-only'})
        if date_cell and date_cell.text.strip():
            current_date = " ".join(date_cell.text.strip().split()[1:])  # "La 5.4.2025" -> "5.4.2025"
        
        # Hae solut
        cells = row.find_all('td')
        if len(cells) < 7:
            continue
            
        # Tiedot
        time = cells[2].text.strip() if len(cells) > 2 else None
        teams = cells[3].text.strip().split(' - ')
        result = cells[5].text.strip().replace('—', '-')
        audience = cells[6].text.strip()
        
        if len(teams) == 2 and '-' in result:
            try:
                matches.append({
                    'date': current_date,
                    'time': time,
                    'home_team': teams[0],
                    'away_team': teams[1],
                    'result': result,
                    'audience': int(audience) if audience.isdigit() else 0
                })
            except Exception as e:
                print(f"Virhe rivin käsittelyssä: {str(e)}")
    
    return matches

# Suorita ja näytä tulokset
if __name__ == "__main__":
    try:
        matches = get_matches()
        print(f"Löydettiin {len(matches)} ottelua:")
        for match in matches:
            print(f"{match['date']} {match['time']} | {match['home_team']} - {match['away_team']} | Tulos: {match['result']} | Yleisöä: {match['audience']}")
    except Exception as e:
        print(f"Virhe: {str(e)}")
