import requests
from bs4 import BeautifulSoup
import datetime
import os

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
        # Päivämäärän käsittely
        date_cell = row.find('td', {'class': 'desktop-only'})
        if date_cell and date_cell.text.strip():
            current_date = " ".join(date_cell.text.strip().split()[1:])  # Esim. "La 5.4.2025" -> "5.4.2025"
        
        cells = row.find_all('td')
        if len(cells) < 8:  # Tarkista solmujen määrä
            continue
        
        try:
            # Oikeat solmuindeksit:
            time = cells[2].text.strip() if len(cells) > 2 else "?"
            teams = cells[4].text.strip().split(' - ')  # Oikea indeksi 4
            result = cells[6].text.strip().replace('—', '-').replace(' ', '')
            audience = cells[7].text.strip()  # Oikea indeksi 7
            
            if len(teams) == 2 and '-' in result:
                home_goals, away_goals = result.split('-')
                matches.append({
                    'date': current_date,
                    'time': time,
                    'home': teams[0].strip(),
                    'away': teams[1].strip(),
                    'result': f"{home_goals}-{away_goals}",
                    'audience': int(audience) if audience.isdigit() else 0
                })
        except Exception as e:
            print(f"Virhe rivin käsittelyssä: {str(e)}")
    
    return matches

def save_to_md(matches):
    filename = "Yleisö2025.md"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Veikkausliigan yleisötilastot 2025\n\n")
            f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
            
            if not matches:
                f.write("Ei pelattuja otteluita vielä.")
                return
            
            f.write("| Päivä | Aika | Kotijoukkue | Vierasjoukkue | Tulos | Yleisöä |\n")
            f.write("|-------|------|-------------|---------------|-------|---------|\n")
            
            for match in matches:
                f.write(f"| {match['date']} | {match['time']} | {match['home']} | {match['away']} | {match['result']} | {match['audience']} |\n")
            
            total = sum(m['audience'] for m in matches)
            f.write(f"\n**Yhteensä katsojia:** {total}\n")
        
        print(f"✅ Tiedosto {filename} päivitetty onnistuneesti!")
        print(f"📂 Sijainti: {os.path.abspath(filename)}")
    
    except Exception as e:
        print(f"❌ Virhe: {str(e)}")

if __name__ == "__main__":
    try:
        matches = get_matches()
        save_to_md(matches)
    except Exception as e:
        print(f"❌ Päävirhe: {str(e)}")
