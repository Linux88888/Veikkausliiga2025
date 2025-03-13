import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/ottelut/"
response = requests.get(url)
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

with open('Tulevatottelut.md', 'w') as file:
    for game in future_games:
        game_details = ' - '.join(cell.text.strip() for cell in game.find_all('td'))
        print(game_details)
        file.write(game_details + "\n")
