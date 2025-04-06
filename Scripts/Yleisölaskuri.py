import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

# Alusta muuttujat
yleisömäärät = []
tehdyt_maalit = 0
yli_2_5_maaleja = 0
total_home_audience = 0
home_games = 0

try:
    # Nouda data Veikkausliigan sivulta
    url = "https://www.veikkausliiga.com/tulokset"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    html_content = response.text
    
    # Parseroidaan HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Etsi ottelut
    matches = soup.find_all('div', class_='match-item')
    
    # Käsittele jokainen ottelu
    for match in matches:
        # Etsi yleisömäärä
        audience_element = match.find('div', class_='audience')
        if audience_element and audience_element.text.strip():
            audience_text = audience_element.text.strip()
            audience_numbers = re.sub(r'[^0-9]', '', audience_text)
            if audience_numbers:
                yleisömäärät.append(int(audience_numbers))
        
        # Etsi maalimäärät
        score_element = match.find('div', class_='score')
        if score_element and score_element.text.strip():
            score_text = score_element.text.strip()
            score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
            if score_match:
                home_goals = int(score_match.group(1))
                away_goals = int(score_match.group(2))
                match_goals = home_goals + away_goals
                tehdyt_maalit += match_goals
                
                if match_goals > 2.5:
                    yli_2_5_maaleja += 1
    
    # Laske tilastot
    print(f"Yleisömäärät: {yleisömäärät}")
    print(f"Tehdyt maalit: {tehdyt_maalit}")
    print(f"Yli 2.5 maalia peleissä: {yli_2_5_maaleja}")
    
    # Aseta muuttujat
    home_games = len(yleisömäärät)
    total_home_audience = sum(yleisömäärät) if yleisömäärät else 0
    
    # Aseta tiedoston sijainti
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
    
    # Kirjoita tiedostoon
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("# Veikkausliiga 2025 - Yleisötilastot\n\n")
        file.write(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        file.write("## Tilastot\n\n")
        
        file.write(f"- **Kokonaisyleisömäärä:** {total_home_audience:,} katsojaa\n")
        
        # KORJAUS RIVILLE 161: Tarkistetaan onko home_games nolla ennen jakamista
        if home_games > 0:
            file.write(f"- **Keskimääräinen yleisö:** {total_home_audience / home_games:.0f} katsojaa/ottelu\n")
        else:
            file.write("- **Keskimääräinen yleisö:** 0 katsojaa/ottelu\n")
        
        file.write(f"- **Otteluita pelattu:** {home_games}\n")
        file.write(f"- **Maaleja yhteensä:** {tehdyt_maalit}\n")
        
        if home_games > 0:
            file.write(f"- **Maaleja per ottelu:** {tehdyt_maalit / home_games:.2f}\n")
            file.write(f"- **Yli 2.5 maalia otteluissa:** {(yli_2_5_maaleja / home_games * 100):.1f}%\n")
        else:
            file.write("- **Maaleja per ottelu:** 0.00\n")
            file.write("- **Yli 2.5 maalia otteluissa:** 0.0%\n")
        
        file.write("\n---\n*Tiedot päivitetään automaattisesti päivittäin.*\n")
    
    print(f"Tiedosto päivitetty onnistuneesti: {file_path}")
    
except Exception as e:
    print(f"Virhe: {str(e)}")
