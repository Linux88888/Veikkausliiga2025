"""
Veikkausliiga 2025 - Yleisömäärien laskentaskripti
Päivittää Yleisö2025.md tiedoston tuoreilla yleisötilastoilla
"""

import os
import requests
from bs4 import BeautifulSoup
import re
import datetime

def hae_data():
    """Hakee datan Veikkausliigan verkkosivuilta"""
    url = "https://www.veikkausliiga.com/tulokset"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Virhe datan haussa: {e}")
        return None

def kerää_tilastot(html_sisältö):
    """Kerää tilastot HTML-sisällöstä"""
    if not html_sisältö:
        print("Ei HTML-sisältöä analysoitavaksi")
        return {
            "yleisömäärät": [],
            "maalit_yhteensä": 0,
            "yli_2_5_pelit": 0
        }
    
    soup = BeautifulSoup(html_sisältö, 'html.parser')
    yleisömäärät = []
    maalit_yhteensä = 0
    yli_2_5_pelit = 0
    
    # Etsi ottelutiedot
    try:
        ottelut = soup.find_all('div', class_='match-item')
        print(f"Löydettiin {len(ottelut)} ottelua")
        
        for ottelu in ottelut:
            # Yleisömäärä
            try:
                yleisö_elementti = ottelu.find('div', class_='audience')
                if yleisö_elementti and yleisö_elementti.text.strip():
                    yleisö_teksti = yleisö_elementti.text.strip()
                    yleisö_numero = re.sub(r'[^0-9]', '', yleisö_teksti)
                    if yleisö_numero:
                        yleisömäärät.append(int(yleisö_numero))
            except Exception as e:
                print(f"Virhe yleisömäärän käsittelyssä: {e}")
            
            # Maalit
            try:
                tulos_elementti = ottelu.find('div', class_='score')
                if tulos_elementti and tulos_elementti.text.strip():
                    tulos_teksti = tulos_elementti.text.strip()
                    tulos_match = re.search(r'(\d+)\s*-\s*(\d+)', tulos_teksti)
                    if tulos_match:
                        koti_maalit = int(tulos_match.group(1))
                        vieras_maalit = int(tulos_match.group(2))
                        pelin_maalit = koti_maalit + vieras_maalit
                        maalit_yhteensä += pelin_maalit
                        
                        if pelin_maalit > 2.5:
                            yli_2_5_pelit += 1
            except Exception as e:
                print(f"Virhe maalitietojen käsittelyssä: {e}")
    except Exception as e:
        print(f"Virhe otteluiden käsittelyssä: {e}")
    
    print(f"Yleisömäärät: {yleisömäärät}")
    print(f"Maalit yhteensä: {maalit_yhteensä}")
    print(f"Yli 2.5 maalia pelejä: {yli_2_5_pelit}")
    
    return {
        "yleisömäärät": yleisömäärät,
        "maalit_yhteensä": maalit_yhteensä,
        "yli_2_5_pelit": yli_2_5_pelit
    }

def päivitä_tiedosto(tilastot):
    """Päivittää Yleisö2025.md tiedoston tilastoilla"""
    try:
        yleisömäärät = tilastot["yleisömäärät"]
        maalit_yhteensä = tilastot["maalit_yhteensä"]
        yli_2_5_pelit = tilastot["yli_2_5_pelit"]
        
        # Laske tilastot turvallisesti
        pelejä = len(yleisömäärät)
        yleisö_yhteensä = sum(yleisömäärät)
        
        # Valmistele sisältö - turvallinen versio ilman nollalla jakamista
        sisältö = []
        sisältö.append("# Veikkausliiga 2025 - Yleisötilastot")
        sisältö.append("")
        sisältö.append(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sisältö.append("")
        sisältö.append("## Yhteenveto")
        sisältö.append("")
        
        # Kokonaisyleisömäärä
        sisältö.append(f"- **Kokonaisyleisömäärä:** {yleisö_yhteensä:,} katsojaa")
        
        # Keskimääräinen yleisö per peli
        if pelejä > 0:
            sisältö.append(f"- **Keskimääräinen yleisö:** {yleisö_yhteensä / pelejä:.1f} katsojaa/ottelu")
        else:
            sisältö.append("- **Keskimääräinen yleisö:** 0 katsojaa/ottelu")
        
        # Pelatut ottelut
        sisältö.append(f"- **Otteluita pelattu:** {pelejä}")
        
        # Maalit
        sisältö.append(f"- **Maaleja yhteensä:** {maalit_yhteensä}")
        
        # Maaleja per peli
        if pelejä > 0:
            sisältö.append(f"- **Maaleja per ottelu:** {maalit_yhteensä / pelejä:.2f}")
        else:
            sisältö.append("- **Maaleja per ottelu:** 0.00")
        
        # Yli 2.5 maalia prosentti
        if pelejä > 0:
            sisältö.append(f"- **Yli 2.5 maalia otteluissa:** {(yli_2_5_pelit / pelejä * 100):.1f}%")
        else:
            sisältö.append("- **Yli 2.5 maalia otteluissa:** 0.0%")
        
        sisältö.append("")
        sisältö.append("---")
        sisältö.append("*Tiedot päivitetään automaattisesti kerran päivässä.*")
        
        # Kirjoita tiedostoon
        tiedostopolku = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Yleisö2025.md")
        with open(tiedostopolku, "w", encoding="utf-8") as tiedosto:
            tiedosto.write("\n".join(sisältö))
        
        print(f"Tiedosto päivitetty onnistuneesti: {tiedostopolku}")
        return True
    except Exception as e:
        print(f"Virhe tiedoston päivityksessä: {e}")
        return False

def main():
    """Pääfunktio, joka ajaa koko prosessin"""
    try:
        print("Aloitetaan yleisötilastojen päivitys...")
        html_sisältö = hae_data()
        tilastot = kerää_tilastot(html_sisältö)
        päivitä_tiedosto(tilastot)
        print("Päivitys valmis.")
    except Exception as e:
        print(f"Kriittinen virhe skriptissä: {e}")

if __name__ == "__main__":
    main()
