import requests
import re
import os
import datetime
import math

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

# Täysin uudistettu funktio, joka parsii tulevat ottelut datan
def parse_tulevat_ottelut(data):
    ottelut = []
    lines = data.splitlines()
    
    current_date = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Etsi päivämäärä
        date_match = re.search(r'(\d+\.\d+\.\d{4})', line)
        if date_match:
            current_date = date_match.group(1)
            print(f"Found date: {current_date}")
            
        # Etsi Seuranta-sanalla merkityt ottelurivit
        if "Seuranta" in line:
            # Tarkista eri formaatit
            if " - " in line:
                parts = line.split(" - ")
                
                # Formaatti 1: "15:00 - VPS - FC Inter - Seuranta"
                if len(parts) >= 4 and is_time_format(parts[0]):
                    aika = parts[0].strip()
                    koti = parts[1].strip()
                    vieras = parts[2].strip()
                    
                # Formaatti 2: "14 - - 17:00 - 17:00 - FC Haka - AC Oulu - Seuranta"
                elif len(parts) >= 6 and is_time_format(parts[3]):
                    aika = parts[3].strip()
                    koti = parts[4].strip()
                    vieras = parts[5].strip()
                else:
                    continue
                
                # Tarkista, että löydetyt joukkueet ovat valideja
                if is_valid_team(koti) and is_valid_team(vieras):
                    ottelu = {
                        'paiva': current_date,
                        'aika': aika,
                        'koti': koti,
                        'vieras': vieras,
                    }
                    print(f"Lisätty ottelu: {ottelu}")
                    ottelut.append(ottelu)
                else:
                    print(f"Ei kelvollinen joukkue: {koti} vs {vieras}")
    
    return ottelut

# Apufunktio ajan formaatin tarkistamiseen
def is_time_format(s):
    return re.match(r'\d{1,2}:\d{2}', s) is not None

# Apufunktio joukkueen validoinnille
def is_valid_team(team_name):
    for team in teams:
        if team in team_name:
            return True
    return False

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
            found_team = False
            team_name = line.replace('### ', '').strip()
            # Normalisoi joukkueen nimi
            for team in teams:
                if team in team_name:
                    current_team = team
                    teams_data[current_team] = {}
                    print(f"Löytyi joukkue: {current_team}")
                    found_team = True
                    break
            if not found_team:
                current_team = None
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
        elif current_team and line.startswith('- '):
            if kotipelit_mode:
                if "Tehdyt maalit:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['koti_maaleja'] = value
                    print(f"{current_team} koti_maaleja: {value}")
                    
                elif "Yli 2.5 maalia:" in line:
                    match = re.search(r'Yli 2.5 maalia:\s*(\d+)\s*\(([^)]+)\)', line)
                    if match:
                        value = f"{match.group(1)} ({match.group(2)})"
                        teams_data[current_team]['koti_yli_2_5'] = value
                        print(f"{current_team} koti_yli_2_5: {value}")
                    
            elif vieraspelit_mode:
                if "Tehdyt maalit:" in line:
                    value = extract_number(line)
                    teams_data[current_team]['vieras_maaleja'] = value
                    print(f"{current_team} vieras_maaleja: {value}")
                    
                elif "Yli 2.5 maalia:" in line:
                    match = re.search(r'Yli 2.5 maalia:\s*(\d+)\s*\(([^)]+)\)', line)
                    if match:
                        value = f"{match.group(1)} ({match.group(2)})"
                        teams_data[current_team]['vieras_yli_2_5'] = value
                        print(f"{current_team} vieras_yli_2_5: {value}")
    
    return teams_data

# Apufunktio numeroiden poimintaan
def extract_number(text):
    match = re.search(r':\s*(\d+)', text)
    if match:
        return float(match.group(1))
    return 0

# Laskee Poisson-todennäköisyyksiä
def poisson_probability(mean, k):
    try:
        return math.exp(-mean) * (mean ** k) / math.factorial(k)
    except:
        return 0

# Laskee voittotodennäköisyyden
def calculate_win_probability(team_a_goals, team_b_goals):
    prob = 0
    for i in range(0, 10):  # Iteroi todennäköisiä maalimääriä
        for j in range(0, i):  # Joukkue A voittaa kun sen maalit > B:n maalit
            prob += poisson_probability(team_a_goals, i) * poisson_probability(team_b_goals, j)
    return prob

# Laskee yli X maalia todennäköisyyden
def calculate_over_probability(team_a_goals, team_b_goals, limit):
    prob = 0
    for i in range(0, 15):
        for j in range(0, 15):
            if i + j > limit:
                prob += poisson_probability(team_a_goals, i) * poisson_probability(team_b_goals, j)
    return prob

# Laskee todennäköisimmän tuloksen
def calculate_most_likely_score(team_a_goals, team_b_goals):
    highest_prob = 0
    likely_score = (0, 0)
    
    for i in range(0, 6):
        for j in range(0, 6):
            prob = poisson_probability(team_a_goals, i) * poisson_probability(team_b_goals, j)
            if prob > highest_prob:
                highest_prob = prob
                likely_score = (i, j)
                
    return f"{likely_score[0]}-{likely_score[1]}"

# Apufunktio joukkueen nimen täsmäämiseen
def find_matching_team(team_name, teams_data):
    # Täsmällinen osuma
    if team_name in teams_data:
        return team_name
    
    # Osittainen osuma
    for team in teams_data.keys():
        if team in team_name or team_name in team:
            return team
    
    # Erikoistapaukset
    if "Gnistan" in team_name:
        if "IF Gnistan" in teams_data:
            return "IF Gnistan"
        elif "Gnistan" in teams_data:
            return "Gnistan"
    
    return None

# Lisätään kehittyneempi analysointifunktio
def advanced_analyze_matches(ottelut, teams_data):
    results = []
    for ottelu in ottelut:
        koti = ottelu['koti']
        vieras = ottelu['vieras']
        
        koti_key = find_matching_team(koti, teams_data)
        vieras_key = find_matching_team(vieras, teams_data)
        
        # Debug output
        print(f"Ottelu: {koti} vs {vieras}")
        print(f"Löydetty joukkueet: {koti_key} ja {vieras_key}")
        
        koti_maaleja = teams_data.get(koti_key, {}).get('koti_maaleja', 0) if koti_key else 0
        vieras_maaleja = teams_data.get(vieras_key, {}).get('vieras_maaleja', 0) if vieras_key else 0
        koti_yli_2_5 = teams_data.get(koti_key, {}).get('koti_yli_2_5', 'Ei tietoa') if koti_key else 'Ei tietoa'
        vieras_yli_2_5 = teams_data.get(vieras_key, {}).get('vieras_yli_2_5', 'Ei tietoa') if vieras_key else 'Ei tietoa'
        
        # Lasketaan Poisson-jakaumaan perustuvat todennäköisyydet
        home_goals_exp = float(koti_maaleja) if isinstance(koti_maaleja, (int, float)) else 0
        away_goals_exp = float(vieras_maaleja) if isinstance(vieras_maaleja, (int, float)) else 0
        
        # Painotetaan kotiedulla/vierasedulla (30% vaikutus)
        home_boost = 1.3
        away_penalty = 0.9
        
        adjusted_home_goals = home_goals_exp * home_boost
        adjusted_away_goals = away_goals_exp * away_penalty
        
        # Lasketaan todennäköisyydet eri lopputuloksille
        home_win_prob = calculate_win_probability(adjusted_home_goals, adjusted_away_goals)
        away_win_prob = calculate_win_probability(adjusted_away_goals, adjusted_home_goals)
        draw_prob = max(0, 1 - home_win_prob - away_win_prob)
        
        # Yli 2.5 maalia todennäköisyys
        over_2_5_prob = calculate_over_probability(adjusted_home_goals, adjusted_away_goals, 2.5)
        
        # Lasketaan todennäköisin lopputulos
        most_likely_score = calculate_most_likely_score(adjusted_home_goals, adjusted_away_goals)
        
        result = {
            'ottelu': f"{koti} vs {vieras}",
            'paiva': ottelu['paiva'],
            'aika': ottelu['aika'],
            'koti_maaleja': koti_maaleja,
            'vieras_maaleja': vieras_maaleja,
            'koti_yli_2_5': koti_yli_2_5,
            'vieras_yli_2_5': vieras_yli_2_5,
            'koti_voitto_tod': round(home_win_prob * 100, 1),
            'vieras_voitto_tod': round(away_win_prob * 100, 1),
            'tasapeli_tod': round(draw_prob * 100, 1),
            'yli_2_5_tod': round(over_2_5_prob * 100, 1),
            'todennakoisin_tulos': most_likely_score
        }
        results.append(result)
    
    return results

# Päivitetty tulostus markdown-tiedostoon
def save_advanced_results_to_markdown(ottelut, results, filename):
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
                aika_info = f"{ottelu['aika']}" if ottelu['aika'] else ""
                file.write(f"- {ottelu['koti']} vs {ottelu['vieras']} ({paiva_info} klo {aika_info})\n")
        
        file.write("\n## Otteluiden Ennusteet\n")
        if not results:
            file.write("Ei analysoitavia otteluita.\n")
        else:
            # Yhteenveto kaikista otteluista
            file.write("### Yhteenveto Ennusteista\n")
            file.write("| Ottelu | Päivämäärä | Aika | Kotivoitto | Tasapeli | Vierasvoitto | Todennäköisin tulos | Yli 2.5 maalia |\n")
            file.write("|--------|-----------|------|-----------|---------|-------------|-------------------|---------------|\n")
            
            for tulos in results:
                file.write(f"| {tulos['ottelu']} | {tulos['paiva']} | {tulos['aika']} | {tulos['koti_voitto_tod']}% | {tulos['tasapeli_tod']}% | {tulos['vieras_voitto_tod']}% | {tulos['todennakoisin_tulos']} | {tulos['yli_2_5_tod']}% |\n")
            
            file.write("\n")
            
            # Yksityiskohtaiset analyysit
            file.write("### Yksityiskohtaiset Analyysit\n\n")
            
            for tulos in results:
                file.write(f"#### {tulos['ottelu']} - {tulos['paiva']} klo {tulos['aika']}\n\n")
                
                # Perustilastot
                file.write("**Perustilastot:**\n")
                file.write(f"- Koti joukkueen keskiarvo maalit: {tulos['koti_maaleja']}\n")
                file.write(f"- Vieras joukkueen keskiarvo maalit: {tulos['vieras_maaleja']}\n")
                file.write(f"- Kotiotteluiden yli 2.5 maalia pelissä: {tulos['koti_yli_2_5']}\n")
                file.write(f"- Vierasotteluiden yli 2.5 maalia pelissä: {tulos['vieras_yli_2_5']}\n\n")
                
                # Todennäköisyydet
                file.write("**Lopputuloksen todennäköisyydet:**\n")
                file.write(f"- Kotivoitto: {tulos['koti_voitto_tod']}%\n")
                file.write(f"- Tasapeli: {tulos['tasapeli_tod']}%\n")
                file.write(f"- Vierasvoitto: {tulos['vieras_voitto_tod']}%\n\n")
                
                # Ennusteet
                file.write("**Maaliennusteet:**\n")
                file.write(f"- Todennäköisin lopputulos: {tulos['todennakoisin_tulos']}\n")
                file.write(f"- Yli 2.5 maalia: {tulos['yli_2_5_tod']}% todennäköisyys\n")
                
                # ASCII-grafiikka visualisoimaan tulosta
                file.write("\n**Voittotodennäköisyys:**\n```\n")
                koti_chars = int(tulos['koti_voitto_tod'] / 5)
                tasa_chars = int(tulos['tasapeli_tod'] / 5)
                vieras_chars = int(tulos['vieras_voitto_tod'] / 5)
                
                file.write(f"Kotivoitto  {'█' * koti_chars} {tulos['koti_voitto_tod']}%\n")
                file.write(f"Tasapeli   {'█' * tasa_chars} {tulos['tasapeli_tod']}%\n")
                file.write(f"Vierasvoitto {'█' * vieras_chars} {tulos['vieras_voitto_tod']}%\n")
                file.write("```\n\n")
                
                # Ylimääräinen kommentti
                koti_team = tulos['ottelu'].split(" vs ")[0]
                vieras_team = tulos['ottelu'].split(" vs ")[1]
                
                if tulos['koti_voitto_tod'] > 60:
                    file.write(f"**Huomio:** {koti_team} on selkeä suosikki tässä ottelussa.\n\n")
                elif tulos['vieras_voitto_tod'] > 60:
                    file.write(f"**Huomio:** {vieras_team} on selkeä suosikki tässä ottelussa.\n\n")
                elif tulos['tasapeli_tod'] > 30:
                    file.write("**Huomio:** Tasapeliä voidaan pitää todennäköisenä tässä tasaväkisessä ottelussa.\n\n")
                
                file.write("---\n\n")

# Suoritetaan koko prosessi
print("Parsing upcoming matches...")
ottelut = parse_tulevat_ottelut(tulevat_ottelut_data)
print("Parsing team statistics...")
teams_data = parse_yleiso_data(yleiso_data)

# Debug output
print("\n\nOTTELUT LÖYDETTY:")
for ottelu in ottelut:
    print(f"{ottelu['koti']} vs {ottelu['vieras']} ({ottelu['paiva']} {ottelu['aika']})")
print("\n\nJOUKKUETIEDOT:")
for team, data in teams_data.items():
    print(f"{team}: {data}")

# Käytetään kehittyneempää analyysia
print("Analyzing matches...")
analysoidut_tulokset = advanced_analyze_matches(ottelut, teams_data)
print("Saving results...")
save_advanced_results_to_markdown(ottelut, analysoidut_tulokset, 'AnalysoidutOttelut.md')

print("Analyysi valmis ja tulokset tallennettu tiedostoon 'AnalysoidutOttelut.md'.")
