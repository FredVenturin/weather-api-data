import requests # requests like GET, POST, PATCH, DELETE
import json # for API responses in json
from datetime import datetime # for datetime values
from pathlib import Path # apontar para os caminhos de maneira universal

CIDADES = [
    {"nome": "São Paulo",      "latitude": -23.55, "longitude": -46.63},
    {"nome": "Rio de Janeiro", "latitude": -22.91, "longitude": -43.17},
    {"nome": "Brasília",       "latitude": -15.78, "longitude": -47.93},
    {"nome": "Fortaleza",      "latitude":  -3.72, "longitude": -38.54},
    {"nome": "Porto Alegre",   "latitude": -30.03, "longitude": -51.23},
] # lista de dicionarios com cada cidade e suas coordenadas para utilizar em todo o arquivo, por exemplo em iterações em buscas de dados

BRONZE_PATH = Path("data/bronze") # caminho para pasta bronze

def buscar_clima(cidade: dict) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"  # URL base da API Open-Meteo
    
    # parametros que serao inseridos na url para especificar a cidade e alguns outros parametros como a timezone
    params = {
        "latitude":  cidade["latitude"],
        "longitude": cidade["longitude"],
        "daily":     "temperature_2m_max,temperature_2m_min",
        "timezone":  "America/Sao_Paulo",
        "past_days": 30,
    }
    

    response = requests.get(url, params=params)  # realiza o get na API passando a url e os parametros
    response.raise_for_status()   # verifica o status para evitar retrabalho
    
    dados = response.json() #  torna em json o get do response 
    dados["cidade_nome"] = cidade["nome"]  #  insere o campo cidade_nome no json dos dados que foram pegos da API ja que o json base nao tem esse campo
    
    return dados  


def salvar_bronze(dados: dict) -> Path:
    BRONZE_PATH.mkdir(parents=True, exist_ok=True)  #  verifica se o arquivo existe nesse path, se não existir cria o path todo
    
    cidade_slug = dados["cidade_nome"].lower().replace(" ", "_")  #  reorganiza o nome da cidade 
    data_hoje = datetime.now().strftime("%Y-%m-%d")               #  data de hoje na identacao correta
    nome_arquivo = f"{cidade_slug}_{data_hoje}.json"              #  ajusta o nome do arquivo para um padrao - sao_paulo_2026-03-30.json
    
    caminho = BRONZE_PATH / nome_arquivo                          #  path onde o arquico ficara
    
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)  # salva o dicionario como json e o torna legivel
    
    print(f"Bronze salvo: {caminho}")   
    return caminho


def extrair():
    
    for cidade in CIDADES:                                # Itera sobre cada cidade da lista CIDADES
        print(f"Buscando dados de {cidade['nome']}...")   
        
        # Chama a API para a cidade atual
        dados = buscar_clima(cidade)
        
        # Salva o JSON bruto na camada Bronze
        salvar_bronze(dados)
    
    print("Extração concluída!")
