import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

def hae_veikkausliiga_data():
    url = "https://www.veikkausliiga.com/tulokset"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Virhe haettaessa dataa: {str(e)}")
        return None

def parseYleisömäärät(html_content):
    if not html_content:
        return [], 0, 0
    
    soup = BeautifulSoup(html_content, 'html.parser')
    yleisomäärät = []
    maalit = 0
    yli_2_5 = 0
    
    # Etsi ottelutiedot soup-objektista
    ottelut = soup.find_all('div', class_='match-item')
    
    for ottelu in ottelut:
        try:
            # Etsi yleisömäärätiedot
            yleiso_elem = ottelu.find('div', class_='audience')
            if yleiso_elem and yleiso_elem.text.strip():
                yleiso_teksti = yleiso_elem.text.strip()
                yleiso_numero = re.sub(r'[^0-9]', '', yleiso_teksti)
                if yleiso_numero:
                    yleisomäärät.append(int(yleiso_numero))
            
            # Etsi maalitiedot
            tulos_elem = ottelu.find('div', class_='score')
            if tulos_elem and tulos_elem.text.strip():
                tulos_teksti = tulos_elem.text.strip()
                tulos_match = re.search(r'(\d+)\s*-\s*(\d+)', tulos_teksti)
                if tulos_match:
                    koti_maalit = int(tulos_match.group(1))
                    vieras_maalit = int(tulos_match.group(2))
                    ottelu_maalit = koti_maalit + vieras_maalit
                    maalit += ottelu_maalit
                    
                    if ottelu_maalit > 2.5:
                        yli_2_5 += 1
        except Exception as e:
            print(f"Virhe ottelun käsittelyssä: {str(e)}")
            continue
    
    print(f"Yleisömäärät: {yleisomäärät}")
    print(f"Tehdyt maalit: {maalit}")
    print(f"Yli 2.5 maalia peleissä: {yli_2_5}")
    
    return yleisomäärät, maalit, yli_2_5

def paivitaYleiso2025MD(yleisomäärät, maalit, yli_2_5):
    try:
        home_games = len(yleisomäärät)
        total_home_audience = sum(yleisomäärät) if yleisomäärät else 0
        
        # Luodaan aikaleima
        aikaleima = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Varmistetaan, että tiedoston sijainti on oikea
        tiedosto_polku = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
        
        with open(tiedosto_polku, "w", encoding="utf-8") as file:
            file.write("# Veikkausliiga 2025 - Yleisötilastot\n\n")
            file.write(f"Päivitetty: {aikaleima}\n\n")
            file.write("## Tilastot\n\n")
            
            # Tarkistetaan, onko otteluita ennen kuin lasketaan keskiarvoja
            if home_games > 0:
                file.write(f"- **Kokonaisyleisömäärä:** {total_home_audience:,} katsojaa\n")
                file.write(f"- **Keskimääräinen yleisö:** {total_home_audience / home_games:.0f} katsojaa/ottelu\n")
                file.write(f"- **Otteluita pelattu:** {home_games}\n")
                file.write(f"- **Maaleja yhteensä:** {maalit}\n")
                file.write(f"- **Maaleja per ottelu:** {maalit / home_games:.2f}\n")
                file.write(f"- **Yli 2.5 maalia otteluissa:** {(yli_2_5 / home_games * 100):.1f}%\n")
            else:
                file.write("- **Kokonaisyleisömäärä:** 0 katsojaa\n")
                file.write("- **Keskimääräinen yleisö:** 0 katsojaa/ottelu\n")
                file.write("- **Otteluita pelattu:** 0\n")
                file.write("- **Maaleja yhteensä:** 0\n")
                file.write("- **Maaleja per ottelu:** 0.00\n")
                file.write("- **Yli 2.5 maalia otteluissa:** 0.0%\n")
            
            file.write("\n---\n*Tiedot päivitetään automaattisesti päivittäin.*\n")
        
        print(f"Tiedosto päivitetty onnistuneesti: {tiedosto_polku}")
        return True
    except Exception as e:
        print(f"Virhe päivitettäessä tiedostoa: {str(e)}")
        return False

def main():
    html_content = hae_veikkausliiga_data()
    yleisomäärät, maalit, yli_2_5 = parseYleisömäärät(html_content)
    paivitaYleiso2025MD(yleisomäärät, maalit, yli_2_5)

if __name__ == "__main__":
    main()
