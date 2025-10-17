import json
import os
from pathlib import Path
import sys

# =========================================================================
# 🎯 Caminho Base: VERIFIQUE ESTA LINHA!
# =========================================================================
# Use Pathlib para garantir que o caminho funciona independentemente do OS
BASE_DIR = Path("/home/helionlf/Documentos/meus_projetos/ciceroExperience_api/cicero_experience/static/data") 

STATES_FILE_PATH = BASE_DIR / "states.json"
STATES_DIR_PATH = BASE_DIR / "states" # Pasta de destino que será recriada

# Cria a pasta de ESTADOS se não existir
os.makedirs(STATES_DIR_PATH, exist_ok=True)

# -----------------------------
# 1️⃣ Dividir STATES por país (Recriando a pasta STATES)
# -----------------------------
print("🔹 Iniciando a divisão de estados por país...")

# DEBUG: CONFIRMAÇÃO DA EXISTÊNCIA DO ARQUIVO
print(f"Buscando arquivo states.json em: {STATES_FILE_PATH.resolve()}")

# Verifica se o arquivo existe antes de tentar abrir
if not STATES_FILE_PATH.exists():
    print("---------------------------------------------------------------------")
    print(f"❌ ERRO FATAL: Arquivo GLOBAL 'states.json' não encontrado!")
    print(f"❌ O script não encontrou o arquivo no caminho: {STATES_FILE_PATH.resolve()}")
    print("❌ Verifique se o caminho no BASE_DIR está 100% correto.")
    print("---------------------------------------------------------------------")
    sys.exit(1) # Sai com código de erro se o arquivo não for encontrado

try:
    # 1. Carrega o arquivo states.json global
    with open(STATES_FILE_PATH, "r", encoding="utf-8") as f:
        states = json.load(f)

    # 2. Agrupa os estados pelo código do país (country_code/iso2_country)
    states_by_country = {}
    for state in states:
        # Usa o código do país para o nome do arquivo (Ex: 'ET' para Etiópia)
        country_code = state.get("country_code") or state.get("iso2_country") 
        if not country_code:
            continue
        states_by_country.setdefault(country_code, []).append(state)

    # 3. Salva cada grupo em seu respectivo arquivo na pasta 'states'
    for country_code, country_states in states_by_country.items():
        file_path = STATES_DIR_PATH / f"{country_code}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(country_states, f, ensure_ascii=False, indent=2)
        print(f"✅ Criado: {file_path} ({len(country_states)} estados)")

except json.JSONDecodeError:
    print(f"❌ ERRO: O arquivo {STATES_FILE_PATH.name} não é um JSON válido. Verifique a sintaxe.")
    sys.exit(1) # Sai com código de erro

# -----------------------------
# 2️⃣ DIVISÃO DE CIDADES FOI REMOVIDA PARA SEGURANÇA
# -----------------------------
print("\n🚫 A pasta 'cities' (com seus arquivos por estado) foi preservada e não foi modificada.")
print("\n🏁 Concluído! Pasta 'states' recriada com sucesso, dividida por país.")