import requests
from bs4 import BeautifulSoup
import os
import datetime
import re

# Print current working directory for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Directory contents: {os.listdir('.')}")

# Funktio, joka hakee ja parsii markdown-tiedoston GitHubista
def fetch_and_parse_github_markdown(url):
    print(f"Fetching data from URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return ""

# URL-osoitteet
tulevat_ottelut_url = 'https://raw.githubusercontent.com/Linux88888/Veikkausliiga2025/main/Tulevatottelut.md'
yleiso_url = 'https://raw.githubusercontent.com/Linux88888/Veikkausliiga2025/main/Yleis%C3%B62025.md'

# Joukkueiden lista - päivitetty sisältämään kaikki mahdolliset kirjoitusasut
teams = ["HJK", "KuPS", "FC Inter", "SJK", "FF Jaro", "Ilves", "FC Haka", "VPS", "AC Oulu", "Gnistan", "IF Gnistan", "IFK Mariehamn", "KTP"]

# Hakee ja parsii datan
print("Fetching data from GitHub...")
tulevat_ottelut_data = fetch_and_parse_github_markdown(tulevat_ottelut_url)
yleiso_data = fetch_and_parse_github_markdown(yleiso_url)

# Tulostetaan haettu data debuggausta varten
print(f"Tulevat ottelut data length: {len(tulevat_ottelut_data)}")
print(f"Yleisö data length: {len(yleiso_data)}")
print("Tulevat ottelut data:\n", tulevat_ottelut_data[:500], "\n")
print("Yleisö data:\n", yleiso_data[:500], "\n")

# Päivitetty funktio, joka parsii tulevat ottelut datan
def parse_tulevat_ottelut(data, teams):
    ottelut = []
    lines = data.splitlines()
    
    # Etsi kaikkia mahdollisia joukkuepareja
    for line in lines:
        if "Seuranta" in line and " - " in line:
            # Etsitään kello ja joukkueet
            parts = line.split(" - ")
            if len(parts) >= 5:  # Varmistetaan että on tarpeeksi osia
                try:
                    aika = parts[0].strip()
                    koti = parts[1].strip()
                    vieras = parts[2].strip()
                    
                    # Hae ID ja päivämäärä edelliseltä riviltä jos mahdollista
                    ottelu_id = ""
                    paiva = ""
                    
                    # Etsi edellisestä rivistä ID ja päivämäärä
                    idx = lines.index(line)
                    if idx > 0:
                        prev_line = lines[idx-1]
                        match = re.search(r'(\d+)\s*-\s*(.*?)(\d{1,2}\.\d{1,2}.\d{4})', prev_line)
                        if match:
                            ottelu_id = match.group(1).strip()
                            paiva = match.group(3).strip()
                    
                    # Tarkista että joukkueet ovat tunnistettavia
                    if any(team in koti for team in teams) and any(team in vieras for team in teams):
                        ottelu = {
                            'id': ottelu_id,
                            'paiva': paiva,
                            'aika': aika,
                            'koti': koti,
                            'vieras': vieras,
                        }
                        print(f"Lisätty ottelu: {ottelu}")
                        ottelut.append(ottelu)
                    else:
                        print(f"Ei kelvollinen joukkue: {koti} vs {vieras}")
                except Exception as e:
                    print(f"Virhe rivin jäsentämisessä: {line} - {e}")
    
    # Jos ei löytynyt yhteenkään ottelua, kokeile toista jäsentelytapaa
    if not ottelut:
        for line in lines:
            # Etsi suoraan muotoa "aika - kotijoukkue - vierasjoukkue"
            match = re.search(r'(\d{1,2}:\d{2})\s*-\s*([^-]+)-\s*([^-]+)-\s*Seuranta', line)
            if match:
                aika = match.group(1).strip()
                koti = match.group(2).strip()
                vieras = match.group(3).strip()
                
                ottelu = {
                    'id': '',
                    'paiva': '',
                    'aika': aika,
                    'koti': koti,
                    'vieras': vieras,
                }
                print(f"Vaihtoehtoinen jäsentely - Lisätty ottelu: {ottelu}")
                ottelut.append(ottelu)
    
    # Vielä yksi vaihtoehtoinen jäsentelymenetelmä jos tarpeen
    if not ottelut:
        for i, line in enumerate(lines):
            if ":" in line and i < len(lines)-1:
                next_line = lines[i+1]
                if " - " in next_line:
                    parts = next_line.strip().split(" - ")
                    if len(parts) >= 2:
                        koti = parts[0]
                        vieras = parts[1]
                        if koti in teams and vieras in teams:
                            ottelu = {
                                'id': '',
                                'paiva': '',
                                'aika': line.strip(),
                                'koti': koti,
                                'vieras': vieras,
                            }
                            print(f"Kolmas jäsentely - Lisätty ottelu: {ottelu}")
                            ottelut.append(ottelu)
    
    return ottelut

# Funktio, joka parsii joukkueiden tilastot
def parse_yleiso_data(data):
    teams_data = {}
    current_team = None
    kotipelit_mode = False
    vieraspelit_mode = False
    
    lines = data.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Etsi joukkueen nimeä
        if line.startswith('###'):
            team_name = line.replace('###', '').strip()
            # Normalisoi joukkueen nimi
            for team in teams:
                if team in team_name:
                    current_team = team
                    teams_data[current_team] = {}
                    break
            print(f"Löytyi joukkue: {current_team}")
            kotipelit_mode = False
            vieraspelit_mode = False
        
        # Tunnista osiota
        elif current_team and line.startswith('#### Kotipelit'):
            kotipelit_mode = True
            vieraspelit_mode = False
            print(f"Kotipelit-osio: {current_team}")
        
        elif current_team and line.startswith('#### Vieraspelit'):
            kotipelit_mode = False
            vieraspelit_mode = True
            print(f"Vieraspelit-osio: {current_team}")
        
        # Kerää tilastoja
        elif current_team:
            if kotipelit_mode:
                if "Tehdyt maalit:" in line:
                    maalit = extract_number(line)
                    teams_data[current_team]['koti_maaleja'] = maalit
                    print(f"{current_team} koti_maaleja: {maalit}")
                    
                elif "Yli 2.5 maalia:" in line:
                    yli_2_5 = line.split(':')[-1].strip()
                    teams_data[current_team]['koti_yli_2_5'] = yli_2_5
                    print(f"{current_team} koti_yli_2_5: {yli_2_5}")
                    
            elif vieraspelit_mode:
                if "Tehdyt maalit:" in line:
                    maalit = extract_number(line)
                    teams_data[current_team]['vieras_maaleja'] = maalit
                    print(f"{current_team} vieras_maaleja: {maalit}")
                    
                elif "Yli 2.5 maalia:" in line:
                    yli_2_5 = line.split(':')[-1].strip()
                    teams_data[current_team]['vieras_yli_2_5'] = yli_2_5
                    print(f"{current_team} vieras_yli_2_5: {yli_2_5}")
    
    return teams_data

# Apufunktio numeroiden poimintaan
def extract_number(text):
    match = re.search(r'\d+', text)
    if match:
        return float(match.group())
    return 0

# Parsii datat
ottelut = parse_tulevat_ottelut(tulevat_ottelut_data, teams)
teams_data = parse_yleiso_data(yleiso_data)

# Tulostetaan parsittu data debuggausta varten
print("\n\nOTTELUT LÖYDETTY:")
print("================")
for ottelu in ottelut:
    print(f"{ottelu['koti']} vs {ottelu['vieras']} ({ottelu['paiva']} {ottelu['aika']})")
print("\n\nJOUKKUETIEDOT:")
print("================")
for team, data in teams_data.items():
    print(f"{team}: {data}")

# Yksinkertainen analysointifunktio
def simple_analyze_matches(ottelut, teams_data):
    results = []
    for ottelu in ottelut:
        koti = ottelu['koti']
        vieras = ottelu['vieras']
        
        # Etsi oikea joukkue, vaikka nimi olisi hieman erilainen
        koti_key = find_matching_team(koti, teams_data)
        vieras_key = find_matching_team(vieras, teams_data)
        
        koti_maaleja = teams_data.get(koti_key, {}).get('koti_maaleja', 0)
        vieras_maaleja = teams_data.get(vieras_key, {}).get('vieras_maaleja', 0)
        koti_yli_2_5 = teams_data.get(koti_key, {}).get('koti_yli_2_5', 'Ei tietoa')
        vieras_yli_2_5 = teams_data.get(vieras_key, {}).get('vieras_yli_2_5', 'Ei tietoa')
        
        result = {
            'ottelu': f"{koti} vs {vieras}",
            'koti_maaleja': koti_maaleja,
            'vieras_maaleja': vieras_maaleja,
            'koti_yli_2_5': koti_yli_2_5,
            'vieras_yli_2_5': vieras_yli_2_5
        }
        results.append(result)
        print(f"Analysoitu ottelu: {result}")
    return results

# Apufunktio joukkueen nimen täsmäämiseen
def find_matching_team(team_name, teams_data):
    for team in teams_data.keys():
        if team in team_name or team_name in team:
            return team
    return team_name

# Tulostaa analysoidut tulokset markdown-tiedostoon
def save_results_to_markdown(ottelut, results, filename):
    filepath = os.path.join(os.getcwd(), filename)
    print(f"Tallentaa tulokset tiedostoon: {filepath}")
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("# Analysoidut Ottelut\n\n")
        
        # Lisää päivitysaika tiedoston alkuun (näkyy tiedostossa)
        file.write(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Tulostetaan ottelut
        file.write("## Tulevat Ottelut\n")
        if not ottelut:
            file.write("Ei tulevia otteluita.\n\n")
        else:
            for ottelu in ottelut:
                paiva_info = f"({ottelu['paiva']})" if ottelu['paiva'] else ""
                aika_info = f"klo {ottelu['aika']}" if ottelu['aika'] else ""
                file.write(f"- {ottelu['koti']} vs {ottelu['vieras']} {paiva_info} {aika_info}\n")
        
        file.write("\n## Ennusteet\n")
        if not results:
            file.write("Ei analysoitavia otteluita.\n")
        else:
            for tulos in results:
                file.write(f"### {tulos['ottelu']}\n")
                file.write(f"- Koti joukkueen keskiarvo maalit: {tulos['koti_maaleja']}\n")
                file.write(f"- Vieras joukkueen keskiarvo maalit: {tulos['vieras_maaleja']}\n")
                file.write(f"- Kotiotteluiden yli 2.5 maalia pelissä: {tulos['koti_yli_2_5']}\n")
                file.write(f"- Vierasotteluiden yli 2.5 maalia pelissä: {tulos['vieras_yli_2_5']}\n")
                
                # Lisää yksinkertainen ennuste
                koti_maalit = float(tulos['koti_maaleja']) if isinstance(tulos['koti_maaleja'], (int, float)) else 0
                vieras_maalit = float(tulos['vieras_maaleja']) if isinstance(tulos['vieras_maaleja'], (int, float)) else 0
                
                file.write("\n**Yksinkertainen maaliennuste:**\n")
                file.write(f"- Kotijoukkue: {int(koti_maalit)} maalia\n")
                file.write(f"- Vierasjoukkue: {int(vieras_maalit)} maalia\n")
                
                total_goals = koti_maalit + vieras_maalit
                file.write(f"- Maaleja yhteensä: {int(total_goals)}\n")
                file.write(f"- Yli 2.5 maalia pelissä: {'Todennäköinen' if total_goals > 2.5 else 'Epätodennäköinen'}\n")
                file.write("\n")
    
    print(f"Tulokset tallennettu tiedostoon {filename}")
    
    # Tarkista että tiedosto on olemassa
    if os.path.exists(filepath):
        print(f"Tiedosto luotiin onnistuneesti: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"Tiedoston sisältö (ensimmäiset 300 merkkiä): {content[:300]}")
    else:
        print(f"VIRHE: Tiedostoa ei löydy: {filepath}")

# Analysoi ottelut ja tallenna tulokset
analysoidut_tulokset = simple_analyze_matches(ottelut, teams_data)
save_results_to_markdown(ottelut, analysoidut_tulokset, 'AnalysoidutOttelut.md')

print("Analyysi valmis ja tulokset tallennettu tiedostoon 'AnalysoidutOttelut.md'.")
