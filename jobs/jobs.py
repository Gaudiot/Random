import webbrowser
from datetime import datetime, timedelta
import json

# Carrega os dados do arquivo JSON
with open('./opportunities.json', encoding="utf-8") as f:
    opportunities_data = json.load(f)
    jobs = opportunities_data["opportunities"]

today = datetime.today().date()

def open_in_safari(url):
    try:
        safari = webbrowser.get("safari")
        safari.open(url, 1)
    except webbrowser.Error:
        webbrowser.open(url)

def calcula_tempo_faltante(data_atual, data_disponivel):
    delta = data_disponivel - data_atual
    total_dias = delta.days
    meses = total_dias // 30
    dias = total_dias % 30
    if meses > 0:
        tempo = f"{meses} meses"
        if dias > 0:
            tempo += f" {dias} dias"
    else:
        tempo = f"{dias} dias"
    return tempo

open_browser = open_in_safari

BATCH_SIZE = 10

# Lista para armazenar as empresas cujas URLs foram abertas e que são do tipo "Company"
opened_company_jobs = []
opened_in_batch = 0
stopped_early = False

for job in jobs:
    available_date = datetime.strptime(job["available_from"], "%Y-%m-%d").date()

    if today >= available_date:
        if opened_in_batch >= BATCH_SIZE:
            resposta = input(
                f"\n{BATCH_SIZE} páginas abertas. Abrir as próximas {BATCH_SIZE}? (Y/n): "
            ).strip().lower()
            if resposta not in ("", "y"):
                print("Interrompendo a abertura de novas páginas.")
                stopped_early = True
                break
            opened_in_batch = 0

        print(f"Abrindo: {job['name']}")
        open_browser(job["url"])
        opened_in_batch += 1
        if job["type"] == "Company":
            opened_company_jobs.append(job)
    else:
        tempo_faltante = calcula_tempo_faltante(today, available_date)
        print(f"Ainda não disponível: {job['name']} (libera em {tempo_faltante})")

# No final, perguntar ao usuário se deve atualizar as datas das empresas do tipo "Company" cujas URLs foram abertas
if opened_company_jobs:
    resposta = input("Deseja atualizar o campo 'available_from' nas empresas abertas do tipo Company? (y/n): ").strip().lower()
    if resposta == "y":
        nova_data = today + timedelta(weeks=3)
        for job in opened_company_jobs:
            job["available_from"] = nova_data.strftime("%Y-%m-%d")
        # Salva as alterações no arquivo JSON
        with open('./opportunities.json', 'w', encoding="utf-8") as f:
            json.dump(opportunities_data, f, ensure_ascii=False, indent=4)
        print("Datas 'available_from' atualizadas nas empresas selecionadas e salvas no arquivo JSON.")
    else:
        print("Nenhuma data foi alterada.")