import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Lisätään try-except virheenkäsittelyä
try:
    url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
    response = requests.get(url)
    response.raise_for_status()  # Aiheuttaa virheen jos pyyntö epäonnistui
    soup = BeautifulSoup(response.text, 'html.parser')
    rows = soup.find_all('tr')

    future_games = []
    game_found = False

    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 6:
            audience = cells[-1].text.strip()
            if audience == '-':
                game_found = True
                future_games.append(row)
            elif game_found:
                future_games.append(row)
            if len(future_games) >= 6:
                break

    # Parannetaan tiedoston tallennusta lisäämällä markdown-muotoilua
    with open('Tulevatottelut.md', 'w', encoding='utf-8') as file:
        file.write("# Tulevat Ottelut\n\n")
        file.write(f"Päivitetty: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for game in future_games:
            cells_text = [cell.text.strip() for cell in game.find_all('td')]
            # Muotoile selkeämmin
            if len(cells_text) >= 3:
                date = cells_text[0] if len(cells_text) > 0 else "Ei päivämäärää"
                teams = cells_text[1] if len(cells_text) > 1 else "Ei joukkuetietoja"
                location = cells_text[2] if len(cells_text) > 2 else "Ei sijaintia"
                game_details = f"{date} - {teams} - {location}"
                file.write(f"- {game_details}\n")
            else:
                game_details = ' - '.join(cells_text)
                file.write(f"- {game_details}\n")

    print(f"Tulevatottelut.md luotu onnistuneesti, {len(future_games)} ottelua tallennettu.")

except Exception as e:
    print(f"Virhe tulevien otteluiden hakemisessa: {e}")
