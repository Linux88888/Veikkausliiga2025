import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

def main():
    try:
        print("Aloitetaan yleisötilastojen päivitys")
        
        # Hae data Veikkausliigan verkkosivuilta
        url = "https://www.veikkausliiga.com/tulokset"
        response = requests.get(url)
        html_content = response.text
        
        # Parseroidaan data
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Etsitään ottelut
        matches = soup.find_all('div', class_='match-item')
        
        # Alustetaan tilastot
        audiences = []
        goals = 0
        over_2_5_games = 0
        
        # Käydään läpi ottelut
        for match in matches:
            # Yleisö
            audience_elem = match.find('div', class_='audience')
            if audience_elem and audience_elem.text.strip():
                audience_text = audience_elem.text.strip()
                audience_num = re.sub(r'[^0-9]', '', audience_text)
                if audience_num:
                    audiences.append(int(audience_num))
            
            # Maalit
            score_elem = match.find('div', class_='score')
            if score_elem and score_elem.text.strip():
                score_text = score_elem.text.strip()
                score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                if score_match:
                    home_goals = int(score_match.group(1))
                    away_goals = int(score_match.group(2))
                    match_goals = home_goals + away_goals
                    goals += match_goals
                    
                    if match_goals > 2.5:
                        over_2_5_games += 1
        
        print(f"Yleisömäärät: {audiences}")
        print(f"Tehdyt maalit: {goals}")
        print(f"Yli 2.5 maalia peleissä: {over_2_5_games}")
        
        # Päivitetään tiedosto
        home_games = len(audiences)
        total_home_audience = sum(audiences) if audiences else 0
        
        # Tiedoston polku
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
        
        # Kirjoitetaan tiedostoon
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("# Veikkausliiga 2025 - Yleisötilastot\n\n")
            file.write(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            file.write("## Tilastot\n\n")
            
            file.write(f"- **Kokonaisyleisömäärä:** {total_home_audience:,} katsojaa\n")
            
            # KORJAUS: Tarkistetaan onko home_games nolla ennen jakamista
            if home_games > 0:
                file.write(f"- **Keskimääräinen yleisö:** {total_home_audience / home_games:.0f} katsojaa/ottelu\n")
            else:
                file.write(f"- **Keskimääräinen yleisö:** 0 katsojaa/ottelu\n")
            
            file.write(f"- **Otteluita pelattu:** {home_games}\n")
            file.write(f"- **Maaleja yhteensä:** {goals}\n")
            
            # KORJAUS: Tarkistetaan onko home_games nolla ennen jakamista
            if home_games > 0:
                file.write(f"- **Maaleja per ottelu:** {goals / home_games:.2f}\n")
                file.write(f"- **Yli 2.5 maalia otteluissa:** {(over_2_5_games / home_games * 100):.1f}%\n")
            else:
                file.write(f"- **Maaleja per ottelu:** 0.00\n")
                file.write(f"- **Yli 2.5 maalia otteluissa:** 0.0%\n")
            
            file.write("\n---\n*Tiedot päivitetään automaattisesti päivittäin.*\n")
        
        print(f"Tiedosto päivitetty onnistuneesti: {file_path}")
        
    except Exception as e:
        print(f"Virhe: {str(e)}")

if __name__ == "__main__":
    main()
