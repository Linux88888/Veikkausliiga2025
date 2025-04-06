import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

def hae_ottelutiedot():
    """Hakee ottelutiedot Veikkausliigan verkkosivuilta"""
    try:
        url = "https://www.veikkausliiga.com/tulokset"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Varmistetaan, että pyyntö onnistui
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        audiences = []
        goals = 0
        over_2_5_games = 0
        
        # Etsi ottelutiedot
        matches = soup.find_all('div', class_='match-item')
        
        for match in matches:
            # Etsi yleisömäärä
            audience_element = match.find('div', class_='audience')
            if audience_element and audience_element.text.strip():
                audience_text = audience_element.text.strip()
                # Poista kaikki paitsi numerot
                audience_numbers = re.sub(r'[^0-9]', '', audience_text)
                if audience_numbers:
                    audience = int(audience_numbers)
                    audiences.append(audience)
            
            # Etsi maalimäärät
            score_element = match.find('div', class_='score')
            if score_element and score_element.text.strip():
                score_text = score_element.text.strip()
                # Etsi kaikki numerot
                score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                if score_match:
                    home_goals = int(score_match.group(1))
                    away_goals = int(score_match.group(2))
                    match_goals = home_goals + away_goals
                    goals += match_goals
                    
                    if match_goals > 2.5:
                        over_2_5_games += 1
        
        # Tilastojen yhteenveto
        print(f"Yleisömäärät: {audiences}")
        print(f"Tehdyt maalit: {goals}")
        print(f"Yli 2.5 maalia peleissä: {over_2_5_games}")
        
        return audiences, goals, over_2_5_games
        
    except Exception as e:
        print(f"Virhe haettaessa ottelutietoja: {str(e)}")
        return [], 0, 0

def päivitä_tilastot():
    """Päivittää Yleisö2025.md tiedoston uusimmilla tilastoilla"""
    try:
        # Hae ottelutiedot
        audiences, goals, over_2_5_games = hae_ottelutiedot()
        
        # Laske tilastot
        home_games = len(audiences)
        total_home_audience = sum(audiences) if audiences else 0
        
        # Tiedoston polku
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
        
        # Päivitysaika
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Kirjoita tiedosto
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("# Veikkausliiga 2025 - Yleisötilastot\n\n")
            file.write(f"Päivitetty: {update_time}\n\n")
            file.write("## Tilastot\n\n")
            
            file.write(f"- **Kokonaisyleisömäärä:** {total_home_audience:,} katsojaa\n")
            
            # KORJAUS: Tarkistetaan onko home_games nolla ennen jakamista
            if home_games > 0:
                file.write(f"- **Keskimääräinen yleisö:** {total_home_audience / home_games:.0f} katsojaa/ottelu\n")
            else:
                file.write("- **Keskimääräinen yleisö:** 0 katsojaa/ottelu\n")
                
            file.write(f"- **Otteluita pelattu:** {home_games}\n")
            file.write(f"- **Maaleja yhteensä:** {goals}\n")
            
            # KORJAUS: Tarkistetaan onko home_games nolla ennen jakamista
            if home_games > 0:
                file.write(f"- **Maaleja per ottelu:** {goals / home_games:.2f}\n")
                file.write(f"- **Yli 2.5 maalia otteluissa:** {(over_2_5_games / home_games * 100):.1f}%\n")
            else:
                file.write("- **Maaleja per ottelu:** 0.00\n")
                file.write("- **Yli 2.5 maalia otteluissa:** 0.0%\n")
                
            file.write("\n---\n*Tiedot päivitetään automaattisesti päivittäin. Viimeisin päivitys: Linux88888*\n")
        
        print(f"Tilastot päivitetty onnistuneesti tiedostoon: {file_path}")
        return True
        
    except Exception as e:
        print(f"Virhe päivitettäessä tilastoja: {str(e)}")
        return False

if __name__ == "__main__":
    päivitä_tilastot()
