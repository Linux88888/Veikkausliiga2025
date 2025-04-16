import requests
import re
import os
import datetime

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

# Joukkueiden lista
teams = ["HJK", "KuPS", "FC Inter", "SJK", "FF Jaro", "Ilves", "FC Haka", "VPS", "AC Oulu", 
         "Gnistan", "IF Gnistan", "IFK Mariehamn", "KTP"]

# Hakee datan
print("Fetching data from GitHub...")
tulevat_ottelut_data = fetch_and_parse_github_markdown(tulevat_ottelut_url)
yleiso_data = fetch_and_parse_github_markdown(yleiso_url)

# Päivitetty funktio, joka parsii tulevat ottelut datan
def parse_tulevat_ottelut(data):
    ottelut = []
    lines = data.splitlines()
    
    current_date = None
    current_id = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Etsi ottelupäivä ja ID
        if " - " in line and re.search(r'\d+ -', line):
            match = re.search(r'(\d+) - ([^-]+)- (\d+:\d+) - (\d+\.\d+\.\d+)', line)
            if match:
                current_id = match.group(1).strip()
                current_date = match.group(4).strip()
                print(f"Found date: {current_date}, ID: {current_id}")
        
        # Etsi ottelun tiedot
        if "Seuranta" in line and " - " in line:
            match = re.search(r'(\d+:\d+) - ([^-]+) - ([^-]+) -', line)
            if match:
                aika = match.group(1).strip()
                koti = match.group(2).strip()
                vieras = match.group(3).strip()
                
                ottelu = {
                    'id': current_id if current_id else '',
                    'paiva': current_date if current_date else '',
                    'aika': aika,
                    'koti': koti,
                    'vieras': vieras,
                }
                print(f"Lisätty ottelu: {ottelu}")
                ottelut.append(ottelu)
    
    return ottelut

# Parannettu funktio, joka parsii joukkueiden tilastot
def parse_yleiso_data(data):
    teams_data = {}
    current_team = None
    kotipelit_mode = False
    vieraspelit_mode = False
    
    lines = data.splitlines()
    for line in lines:
        line = line.strip()
        
        # Etsi joukkueen nimeä
        if line.startswith('### '):
            team_name = line.replace('### ', '').strip()
            # Normalisoi joukkueen nimi
            for team in teams:
                if team in team_name:
                    current_team = team
                    teams_data[current_team] = {}
                    print(f"Löytyi joukkue: {current_team}")
                    break
            kotipelit_mode = False
            vieraspelit_mode = False
        
        # Tunnista osiota
        elif line.startswith('#### Kotipelit'):
            kotipelit_mode = True
            vieraspelit_mode = False
        
        elif line.startswith('#### Vieraspelit'):
            kotipelit_mode = False
            vieraspelit_mode = True
        
        # Kerää tilastoja
        elif current_team and '- ' in line:
            if kotipelit_mode:
                if "Tehdyt maalit:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['koti_maaleja'] = value
                    print(f"{current_team} koti_maaleja: {value}")
                    
                elif "Yli 2.5 maalia:" in line:
                    match = re.search(r'(\d+)\s*\((\d+\.\d+)%\)', line)
                    if match:
                        value = f"{match.group(1)} ({match.group(2)}%)"
                        teams_data[current_team]['koti_yli_2_5'] = value
                        print(f"{current_team} koti_yli_2_5: {value}")
                    
            elif vieraspelit_mode:
                if "Tehdyt maalit:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['vieras_maaleja'] = value
                    print(f"{current_team} vieras_maaleja: {value}")
                    
                elif "Yli 2.5 maalia:" in line:
                    match = re.search(r'(\d+)\s*\((\d+\.\d+)%\)', line)
                    if match:
                        value = f"{match.group(1)} ({match.group(2)}%)"
                        teams_data[current_team]['vieras_yli_2_5'] = value
                        print(f"{current_team} vieras_yli_2_5: {value}")
    
    return teams_data

# Apufunktio numeroiden poimintaan
def extract_number(text):
    match = re.search(r':\s*(\d+)', text)
    if match:
        return float(match.group(1))
    return 0

# Parsii datat
ottelut = parse_tulevat_ottelut(tulevat_ottelut_data)
teams_data = parse_yleiso_data(yleiso_data)

# Debug output
print("\n\nOTTELUT LÖYDETTY:")
for ottelu in ottelut:
    print(f"{ottelu['koti']} vs {ottelu['vieras']} ({ottelu['paiva']} {ottelu['aika']})")
print("\n\nJOUKKUETIEDOT:")
for team, data in teams_data.items():
    print(f"{team}: {data}")

# Apufunktio joukkueen nimen täsmäämiseen
def find_matching_team(team_name, teams_data):
    if team_name in teams_data:
        return team_name
    
    for team in teams_data.keys():
        if team in team_name or team_name in team:
            return team
    return None

# Yksinkertainen analysointifunktio
def simple_analyze_matches(ottelut, teams_data):
    results = []
    for ottelu in ottelut:
        koti = ottelu['koti']
        vieras = ottelu['vieras']
        
        # Etsi oikea joukkue, vaikka nimi olisi hieman erilainen
        koti_key = find_matching_team(koti, teams_data)
        vieras_key = find_matching_team(vieras, teams_data)
        
        # Debug output
        print(f"Ottelu: {koti} vs {vieras}")
        print(f"Löydetty joukkueet: {koti_key} ja {vieras_key}")
        
        koti_maaleja = teams_data.get(koti_key, {}).get('koti_maaleja', 0) if koti_key else 0
        vieras_maaleja = teams_data.get(vieras_key, {}).get('vieras_maaleja', 0) if vieras_key else 0
        koti_yli_2_5 = teams_data.get(koti_key, {}).get('koti_yli_2_5', 'Ei tietoa') if koti_key else 'Ei tietoa'
        vieras_yli_2_5 = teams_data.get(vieras_key, {}).get('vieras_yli_2_5', 'Ei tietoa') if vieras_key else 'Ei tietoa'
        
        result = {
            'ottelu': f"{koti} vs {vieras}",
            'paiva': ottelu['paiva'],
            'aika': ottelu['aika'],
            'koti_maaleja': koti_maaleja,
            'vieras_maaleja': vieras_maaleja,
            'koti_yli_2_5': koti_yli_2_5,
            'vieras_yli_2_5': vieras_yli_2_5
        }
        results.append(result)
        
    return results

# Tulostaa analysoidut tulokset markdown-tiedostoon
def save_results_to_markdown(ottelut, results, filename):
    filepath = os.path.join(os.getcwd(), filename)
    print(f"Tallentaa tulokset tiedostoon: {filepath}")
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("# Analysoidut Ottelut\n\n")
        file.write(f"Päivitetty: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Tulostetaan ottelut
        file.write("## Tulevat Ottelut\n")
        if not ottelut:
            file.write("Ei tulevia otteluita.\n\n")
        else:
            for ottelu in ottelut:
                paiva_info = f"{ottelu['paiva']}" if ottelu['paiva'] else ""
                aika_info = f"klo {ottelu['aika']}" if ottelu['aika'] else ""
                file.write(f"- {ottelu['koti']} vs {ottelu['vieras']} ({paiva_info} {aika_info})\n")
        
        file.write("\n## Ennusteet\n")
        if not results:
            file.write("Ei analysoitavia otteluita.\n")
        else:
            for tulos in results:
                file.write(f"### {tulos['ottelu']} - {tulos['paiva']} klo {tulos['aika']}\n")
                file.write(f"- Koti joukkueen keskiarvo maalit: {tulos['koti_maaleja']}\n")
                file.write(f"- Vieras joukkueen keskiarvo maalit: {tulos['vieras_maaleja']}\n")
                file.write(f"- Kotiotteluiden yli 2.5 maalia pelissä: {tulos['koti_yli_2_5']}\n")
                file.write(f"- Vierasotteluiden yli 2.5 maalia pelissä: {tulos['vieras_yli_2_5']}\n")
                
                # Lisää yksinkertainen ennuste
                koti_maalit = float(tulos['koti_maaleja']) if isinstance(tulos['koti_maaleja'], (int, float)) else 0
                vieras_maalit = float(tulos['vieras_maaleja']) if isinstance(tulos['vieras_maaleja'], (int, float)) else 0
                
                file.write("\n**Yksinkertainen maaliennuste:**\n")
                file.write(f"- Kotijoukkue: {round(koti_maalit)} maalia\n")
                file.write(f"- Vierasjoukkue: {round(vieras_maalit)} maalia\n")
                
                total_goals = koti_maalit + vieras_maalit
                file.write(f"- Maaleja yhteensä: {round(total_goals)}\n")
                file.write(f"- Yli 2.5 maalia pelissä: {'Todennäköinen' if total_goals > 2.5 else 'Epätodennäköinen'}\n")
                file.write("\n")

# Analysoi ottelut ja tallenna tulokset
analysoidut_tulokset = simple_analyze_matches(ottelut, teams_data)
save_results_to_markdown(ottelut, analysoidut_tulokset, 'AnalysoidutOttelut.md')

print("Analyysi valmis ja tulokset tallennettu tiedostoon 'AnalysoidutOttelut.md'.")
