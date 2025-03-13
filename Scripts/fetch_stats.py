import requests
from bs4 import BeautifulSoup

def hae_veikattu_lista():
    """Palauttaa listan veikatuista joukkueista sarjajärjestyksessä."""
    return ["HJK", "KuPS", "Inter", "SJK", "FF Jaro", "Ilves", "FC Haka", "VPS", "AC Oulu", "Gnistan", "IFK Mariehamn", "KTP"]

def hae_sarjataulukko():
    """Hakee ja palauttaa sarjataulukon veikkausliiga.com sivustolta."""
    try:
        sarjataulukko_url = 'https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/joukkueet/'
        response = requests.get(sarjataulukko_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        taulukko_rivit = soup.find_all('tr')
        taulukko = []
        
        for rivi in taulukko_rivit[1:]:
            solut = rivi.find_all('td')
            if solut:
                taulukko.append([s.get_text().strip() for s in solut])
        return taulukko
    except Exception as e:
        print("Sarjataulukon lataus epäonnistui:", e)
        return None

def hae_pelaajan_pisteet():
    """Hakee ja palauttaa tiettyjen pelaajien pisteet veikkausliiga.com sivustolta."""
    try:
        url = 'https://www.veikkausliiga.com/tilastot/2025/veikkausliiga/pelaajat/'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        taulukko_rivit = soup.find_all('tr')

        etsittavat_pelaajat = ["Coffey, Ashley Mark", "Moreno Ciorciari, Jaime Jose", "Karjalainen, Rasmus", "Plange, Luke Elliot", "Odutayo, Colin"]
        pelaajat_pisteet = []
        kokonaispisteet_pelaajat = 0

        for rivi in taulukko_rivit:
            solut = rivi.find_all('td')
            if solut and len(solut) > 15:
                nimi_solu = solut[1].get_text().strip()
                if nimi_solu in etsittavat_pelaajat:
                    maalit = int(solut[5].get_text().strip())
                    laukaukset = int(solut[6].get_text().strip())
                    maalisyötöt = int(float(solut[9].get_text().strip().replace(',', '.')))
                    punaiset_kortit = int(solut[15].get_text().strip())
                    pisteet = (maalit * 2) + (laukaukset * 0.1) + (maalisyötöt * 0.5) - (punaiset_kortit * 1)
                    pelaajat_pisteet.append((nimi_solu, pisteet))
                    kokonaispisteet_pelaajat += pisteet
        return pelaajat_pisteet, kokonaispisteet_pelaajat
    except Exception as e:
        print("Pelaajatietojen haku epäonnistui:", e)
        return [], 0

def laske_joukkueiden_pisteet(sarjataulukko, veikatut_joukkueet):
    """Laskee pisteet perustuen veikattujen joukkueiden sijoitukseen sarjataulukossa."""
    kokonaispisteet = 0
    for rivi in sarjataulukko:
        joukkue = rivi[1]
        sijoitus = rivi[0].rstrip('.')
        if joukkue in veikatut_joukkueet and int(sijoitus) == veikatut_joukkueet.index(joukkue) + 1:
            kokonaispisteet += 1
    return kokonaispisteet

def tallenna_tulokset(sarjataulukko, pelaajat_pisteet, joukkuepisteet, kokonaispisteet_pelaajat):
    """Tallentaa sarjataulukon ja pelaajien pisteet markdown-muodossa tiedostoon."""
    veikatut_joukkueet = hae_veikattu_lista()
    with open('Tilastot.md', 'w') as file:
        file.write("# Sarjataulukko\n")
        file.write("| Sijoitus | Joukkue | Ottelut | Voitot | Tasapelit | Tappiot | Tehdyt maalit | Päästetyt maalit | Maaliero | Syötöt |\n")
        file.write("|----------|---------|---------|--------|-----------|---------|----------------|-------------------|----------|-------|\n")
        for rivi in sarjataulukko:
            file.write("|" + " | ".join(rivi) + "|\n")
        file.write("\n# Pelaajien pisteet\n")
        for nimi, pisteet in pelaajat_pisteet:
            file.write(f'* {nimi}: {pisteet:.1f} pistettä\n')
        file.write(f'\n**Kokonaispisteet joukkueille: {joukkuepisteet}**\n')
        file.write(f'\n**Kokonaispisteet pelaajille: {kokonaispisteet_pelaajat}**\n')
        file.write(f'\n**Yhteispisteet: {joukkuepisteet + kokonaispisteet_pelaajat}**\n')
        file.write("\n# Veikattu Sarjataulukko\n")
        file.write("| Sijoitus | Joukkue |\n")
        file.write("|----------|---------|\n")
        for idx, joukkue in enumerate(veikatut_joukkueet, start=1):
            file.write(f"| {idx} | {joukkue} |\n")

def main():
    """Pääfunktio, joka suorittaa sarjataulukon, pelaajien pisteiden haun ja tallentaa tulokset."""
    veikatut_joukkueet = hae_veikattu_lista()
    sarjataulukko = hae_sarjataulukko()
    pelaajat_pisteet, kokonaispisteet_pelaajat = hae_pelaajan_pisteet()
    if sarjataulukko:
        joukkuepisteet = laske_joukkueiden_pisteet(sarjataulukko, veikatut_joukkueet)
        tallenna_tulokset(sarjataulukko, pelaajat_pisteet, joukkuepisteet, kokonaispisteet_pelaajat)

if __name__ == "__main__":
    main()
