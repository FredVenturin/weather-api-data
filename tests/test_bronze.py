import json
import pytest
from pathlib import Path

BRONZE_PATH = Path("data/bronze")

def test_bronze_arquivos_existem():
    # Verifica se existem arquivos JSON na pasta Bronze
    arquivos = list(BRONZE_PATH.glob("*.json"))
    assert len(arquivos) > 0, "Nenhum arquivo encontrado na Bronze"

def test_bronze_estrutura_json():
    # Verifica se cada arquivo tem os campos esperados
    arquivos = list(BRONZE_PATH.glob("*.json"))
    
    for arquivo in arquivos:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        assert "cidade_nome" in dados, f"Campo cidade_nome ausente em {arquivo}"
        assert "daily" in dados, f"Campo daily ausente em {arquivo}"
        assert "time" in dados["daily"], f"Campo time ausente em {arquivo}"
        assert "temperature_2m_max" in dados["daily"], f"Campo temperature_2m_max ausente em {arquivo}"
        assert "temperature_2m_min" in dados["daily"], f"Campo temperature_2m_min ausente em {arquivo}"

def test_bronze_listas_paralelas():
    # Verifica se as listas de datas e temperaturas têm o mesmo tamanho
    arquivos = list(BRONZE_PATH.glob("*.json"))
    
    for arquivo in arquivos:
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        n_datas    = len(dados["daily"]["time"])
        n_temp_max = len(dados["daily"]["temperature_2m_max"])
        n_temp_min = len(dados["daily"]["temperature_2m_min"])
        
        assert n_datas == n_temp_max == n_temp_min, \
            f"Listas com tamanhos diferentes em {arquivo}"