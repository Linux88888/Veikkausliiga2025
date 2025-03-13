import requests
from bs4 import BeautifulSoup

# Funktio, joka hakee ja parsii markdown-tiedoston GitHubista
def fetch_and_parse_github_markdown(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    pre_tag = soup.find('pre')
    if pre_tag:
        return pre_tag.text
    else:
        return soup.get_text()

# URL-osoitteet
tulevat_ottelut_url = 'https://raw.githubusercontent.com/Linux88888/Veikkausliiga2025/main/Tulevatottelut.md'
yleiso_url = 'https://raw.githubusercontent.com/Linux88888/Veikkausliiga2025/main/Yleis%C3%B62025.md'

# Joukkueiden lista
teams = ["HJK", "KuPS", "FC Inter", "SJK", "FC Lahti", "Ilves", "FC Haka", "VPS", "AC Oulu", "Gnistan", "IFK Mariehamn", "EIF"]

# Hakee ja parsii datan
tulevat_ottelut_data = fetch_and_parse_github_markdown(tulevat_ottelut_url)
yleiso_data = fetch_and_parse_github_markdown(yleiso_url)

# Tulostetaan haettu data debuggausta varten
print("Tulevat ottelut data:\n", tulevat_ottelut_data[:500], "\n")
print("Yleisö data:\n", yleiso_data[:500], "\n")

# Funktio, joka parsii tulevat ottelut datan
def parse_tulevat_ottelut(data, teams):
    ottelut = []
    lines = data.splitlines()
    for line in lines:
        if ' - ' in line and 'Seuranta' not in line:
            parts = line.split(' - ')
            if len(parts) >= 5:
                koti = parts[3].strip()
                vieras = parts[4].strip()
                if koti in teams and vieras in teams:
                    ottelu = {
                        'id': parts[0].strip(),
                        'paiva': parts[1].strip() if len(parts) > 5 else '',
                        'aika': parts[2].strip() if len(parts) > 4 else '',
                        'koti': koti,
                        'vieras': vieras,
                    }
                    print(f"Lisätty ottelu: {ottelu}")  # Debug-tuloste
                    ottelut.append(ottelu)
                else:
                    print(f"Ei kelvollinen joukkue: {koti} vs {vieras}")  # Debug-tuloste
    return ottelut

# Funktio, joka parsii maalitiedot
def parse_yleiso_data(data):
    teams_data = {}
    current_team = None
    lines = data.splitlines()
    for line in lines:
        line = line.strip()
        if line and line.split()[0] in teams:
            current_team = line.split()[0]
            teams_data[current_team] = {}
            print(f"Nykyinen joukkue: {current_team}")  # Debug-tuloste
        elif current_team and 'Kotiotteluiden keskiarvo (maalit tehty):' in line:
            avg_goals = float(line.split(': ')[1])
            teams_data[current_team]['koti_maaleja'] = avg_goals
            print(f"{current_team} koti_maaleja: {avg_goals}")  # Debug-tuloste
        elif current_team and 'Vierasotteluiden keskiarvo (maalit tehty):' in line:
            avg_goals = float(line.split(': ')[1])
            teams_data[current_team]['vieras_maaleja'] = avg_goals
            print(f"{current_team} vieras_maaleja: {avg_goals}")  # Debug-tuloste
        elif current_team and 'Kotiotteluiden yli 2.5 maalia pelissä:' in line:
            over_2_5 = line.split(': ')[1]
            teams_data[current_team]['koti_yli_2_5'] = over_2_5
            print(f"{current_team} koti_yli_2_5: {over_2_5}")  # Debug-tuloste
        elif current_team and 'Vierasotteluiden yli 2.5 maalia pelissä:' in line:
            over_2_5 = line.split(': ')[1]
            teams_data[current_team]['vieras_yli_2_5'] = over_2_5
            print(f"{current_team} vieras_yli_2_5: {over_2_5}")  # Debug-tuloste
    return teams_data

# Parsii datat
ottelut = parse_tulevat_ottelut(tulevat_ottelut_data, teams)
teams_data = parse_yleiso_data(yleiso_data)

# Tulostetaan parsiottu data debuggausta varten
print("Parsitut ottelut:\n", ottelut, "\n")
print("Parsittu yleisödata:\n", teams_data, "\n")

# Yksinkertainen analysointifunktio
def simple_analyze_matches(ottelut, teams_data):
    results = []
    for ottelu in ottelut:
        koti = ottelu['koti']
        vieras = ottelu['vieras']
        koti_maaleja = teams_data.get(koti, {}).get('koti_maaleja', 0)
        vieras_maaleja = teams_data.get(vieras, {}).get('vieras_maaleja', 0)
        koti_yli_2_5 = teams_data.get(koti, {}).get('koti_yli_2_5', 'Ei tietoa')
        vieras_yli_2_5 = teams_data.get(vieras, {}).get('vieras_yli_2_5', 'Ei tietoa')
        result = {
            'ottelu': f"{koti} vs {vieras}",
            'koti_maaleja': koti_maaleja,
            'vieras_maaleja': vieras_maaleja,
            'koti_yli_2_5': koti_yli_2_5,
            'vieras_yli_2_5': vieras_yli_2_5
        }
        results.append(result)
        print(f"Analysoitu ottelu: {result}")  # Debug-tuloste
    return results

# Tulostaa analysoidut tulokset markdown-tiedostoon
def save_results_to_markdown(ottelut, results, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write("# Analysoidut Ottelut\n\n")
        
        # Tulostetaan ottelut
        file.write("## Tulevat Ottelut\n")
        for ottelu in ottelut:
            file.write(f"- {ottelu['koti']} vs {ottelu['vieras']} ({ottelu['paiva']} klo {ottelu['aika']})\n")
        
        file.write("\n## Ennusteet\n")
        if not results:
            file.write("Ei analysoitavia otteluita.\n")
        for tulos in results:
            file.write(f"### Ottelu: {tulos['ottelu']}\n")
            file.write(f"- Koti joukkueen keskiarvo maalit: {tulos['koti_maaleja']}\n")
            file.write(f"- Vieras joukkueen keskiarvo maalit: {tulos['vieras_maaleja']}\n")
            file.write(f"- Kotiotteluiden yli 2.5 maalia pelissä: {tulos['koti_yli_2_5']}\n")
            file.write(f"- Vierasotteluiden yli 2.5 maalia pelissä: {tulos['vieras_yli_2_5']}\n")
            file.write("\n")
    print(f"Tulokset tallennettu tiedostoon {filename}")

# Analysoi ottelut ja tallenna tulokset
analysoidut_tulokset = simple_analyze_matches(ottelut, teams_data)
save_results_to_markdown(ottelut, analysoidut_tulokset, 'AnalysoidutOttelut.md')

print("Analyysi valmis ja tulokset tallennettu tiedostoon 'AnalysoidutOttelut.md'.")
