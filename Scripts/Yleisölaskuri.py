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
        date_cell = row.find('td', {'class': 'desktop-only'})
        if date_cell and date_cell.text.strip():
            current_date = " ".join(date_cell.text.strip().split()[1:])
        
        cells = row.find_all('td')
        if len(cells) < 7:
            continue
            
        try:
            time = cells[2].text.strip() if len(cells) > 2 else "?"
            teams = cells[3].text.strip().split(' - ')
            result = cells[5].text.strip().replace('—', '-')
            audience = cells[6].text.strip()
            
            if len(teams) == 2:
                matches.append({
                    'date': current_date,
                    'time': time,
                    'home': teams[0],
                    'away': teams[1],
                    'result': result,
                    'audience': int(audience) if audience.isdigit() else 0
                })
        except Exception as e:
            print(f"Virhe ottelussa: {str(e)}")
    
    return matches

def save_to_md(matches, filename="Yleisö2025.md"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Veikkausliigan yleisötilastot 2025\n\n")
            f.write(f"*Päivitetty: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}*\n\n")
            
            if not matches:
                f.write("Ei ottelutietoja saatavilla.")
                return
            
            f.write("## Ottelut ja yleisömäärät\n")
            f.write("| Päivämäärä | Kellonaika | Kotijoukkue | Vierasjoukkue | Tulos | Yleisöä |\n")
            f.write("|------------|------------|-------------|---------------|-------|---------|\n")
            
            for match in matches:
                f.write(f"| {match['date']} | {match['time']} | {match['home']} | {match['away']} | {match['result']} | {match['audience']} |\n")
            
            total = sum(m['audience'] for m in matches)
            f.write(f"\n**Yhteensä katsojia:** {total}\n")
        
        print(f"\n✅ Tiedosto {filename} päivitetty onnistuneesti!")
        print(f"📁 Tiedoston sijainti: {os.path.abspath(filename)}")
    
    except Exception as e:
        print(f"❌ Virhe tiedoston kirjoituksessa: {str(e)}")

if __name__ == "__main__":
    try:
        matches = get_matches()
        save_to_md(matches)
        print("\nViimeisimmät ottelut:")
        for m in matches[:3]:  # Näytä vain 3 ensimmäistä testiksi
            print(f"{m['date']} {m['home']} vs {m['away']}")
    except Exception as e:
        print(f"❌ Pääohjelman virhe: {str(e)}")
