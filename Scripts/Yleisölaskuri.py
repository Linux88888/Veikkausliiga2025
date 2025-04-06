import requests
from bs4 import BeautifulSoup
import re
import os
import datetime

def get_match_data():
    """Hakee ottelutiedot Veikkausliigan verkkosivuilta"""
    # Veikkausliigan tulossivun URL
    url = "https://www.veikkausliiga.com/tulokset"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Varmistetaan, että pyyntö onnistui
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Etsi ottelutiedot
        matches = soup.find_all('div', class_='match-item')
        
        audiences = []
        goals = 0
        over_2_5_games = 0
        
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
        
        # Varmista, että on otteluita ennen jakamista
        total_games = len(audiences)
        if total_games == 0:
            print("Ei löytynyt otteluita yleisömäärillä.")
            return None
            
        average_audience = sum(audiences) / total_games
        average_goals = goals / total_games
        over_2_5_percent = (over_2_5_games / total_games) * 100
        
        return {
            'total_audience': sum(audiences),
            'average_audience': average_audience,
            'total_goals': goals,
            'average_goals': average_goals,
            'over_2_5_percent': over_2_5_percent,
            'total_games': total_games,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        print(f"Virhe haettaessa ottelutietoja: {str(e)}")
        return None

def update_audience_file():
    """Päivittää Yleisö2025.md tiedoston uusimmilla tiedoilla"""
    data = get_match_data()
    
    if not data:
        print("Ei voitu päivittää tiedostoa, koska tietoja ei saatu.")
        return False
    
    try:
        # Valmistellaan Markdown-sisältö
        markdown_content = f"""# Veikkausliiga 2025 - Yleisötilastot

Päivitetty: {data['timestamp']}

## Tilastot

- **Kokonaisyleisömäärä:** {data['total_audience']:,} katsojaa
- **Keskimääräinen yleisö:** {data['average_audience']:.0f} katsojaa/ottelu
- **Otteluita pelattu:** {data['total_games']}
- **Maaleja yhteensä:** {data['total_goals']}
- **Maaleja per ottelu:** {data['average_goals']:.2f}
- **Yli 2.5 maalia otteluissa:** {data['over_2_5_percent']:.1f}%

---
*Tiedot päivitetään automaattisesti päivittäin.*
"""
        
        # Kirjoitetaan tiedostoon
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)
            
        print(f"Tiedosto päivitetty onnistuneesti: {file_path}")
        return True
        
    except Exception as e:
        print(f"Virhe päivitettäessä tiedostoa: {str(e)}")
        return False

if __name__ == "__main__":
    update_audience_file()
