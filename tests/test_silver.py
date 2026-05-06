import pytest
import duckdb
from pathlib import Path

DB_PATH = Path("data/warehouse.duckdb")

@pytest.fixture
def silver_df():
    # Carrega a tabela Silver do DuckDB para usar nos testes
    con = duckdb.connect(str(DB_PATH))
    df = con.execute("SELECT * FROM silver.clima").df()
    con.close()
    return df

def test_silver_colunas(silver_df):
    # Verifica se todas as colunas esperadas existem
    colunas_esperadas = ["cidade_nome", "data", "temp_max", "temp_min", "ingested_at"]
    for coluna in colunas_esperadas:
        assert coluna in silver_df.columns, f"Coluna {coluna} ausente na Silver"

def test_silver_sem_nulos(silver_df):
    # Verifica se não há valores nulos em colunas críticas
    colunas_criticas = ["cidade_nome", "data", "temp_max", "temp_min"]
    for coluna in colunas_criticas:
        nulos = silver_df[coluna].isnull().sum()
        assert nulos == 0, f"Coluna {coluna} tem {nulos} valores nulos"

def test_silver_sem_duplicatas(silver_df):
    # Verifica se não há combinações duplicadas de cidade + data
    duplicatas = silver_df.duplicated(subset=["cidade_nome", "data"]).sum()
    assert duplicatas == 0, f"Silver tem {duplicatas} linhas duplicadas"

def test_silver_tipos(silver_df):
    # Verifica se os tipos das colunas estão corretos
    assert str(silver_df["data"].dtype) == "datetime64[us]", "Coluna data com tipo errado"
    assert str(silver_df["temp_max"].dtype) == "float64", "Coluna temp_max com tipo errado"
    assert str(silver_df["temp_min"].dtype) == "float64", "Coluna temp_min com tipo errado"

def test_silver_temperaturas_validas(silver_df):
    # Verifica se as temperaturas estão em range razoável para cidades brasileiras
    assert silver_df["temp_max"].min() > -10, "Temperatura máxima abaixo do esperado"
    assert silver_df["temp_max"].max() < 50, "Temperatura máxima acima do esperado"
    assert silver_df["temp_min"].min() > -10, "Temperatura mínima abaixo do esperado"