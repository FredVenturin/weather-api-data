import pytest
import duckdb
from pathlib import Path

DB_PATH = Path("data/warehouse.duckdb")

@pytest.fixture
def con():
    # Abre conexão com o DuckDB e fecha após cada teste
    conexao = duckdb.connect(str(DB_PATH))
    yield conexao
    conexao.close()

def test_gold_tabelas_existem(con):
    # Verifica se as três tabelas Gold foram criadas
    tabelas = con.execute("""
        SELECT table_name 
        FROM information_schema.tables
        WHERE table_schema = 'gold'
    """).df()
    
    tabelas_esperadas = ["resumo_mensal", "amplitude_termica", "media_movel"]
    for tabela in tabelas_esperadas:
        assert tabela in tabelas["table_name"].values, \
            f"Tabela gold.{tabela} não encontrada"

def test_gold_resumo_mensal_colunas(con):
    # Verifica se as colunas esperadas existem no resumo mensal
    df = con.execute("SELECT * FROM gold.resumo_mensal LIMIT 1").df()
    colunas_esperadas = ["cidade_nome", "mes", "media_temp_max", "media_temp_min", "max_absoluta", "min_absoluta"]
    for coluna in colunas_esperadas:
        assert coluna in df.columns, f"Coluna {coluna} ausente no resumo_mensal"

def test_gold_amplitude_ordenada(con):
    # Verifica se a amplitude está ordenada do maior para o menor
    df = con.execute("SELECT amplitude_media FROM gold.amplitude_termica").df()
    valores = df["amplitude_media"].tolist()
    assert valores == sorted(valores, reverse=True), \
        "amplitude_termica não está ordenada de forma decrescente"

def test_gold_media_movel_sem_nulos(con):
    # Verifica se a média móvel não tem nulos após os primeiros 6 dias de cada cidade
    df = con.execute("""
        SELECT * FROM gold.media_movel
        WHERE media_movel_7d IS NULL
    """).df()
    assert len(df) == 0, f"Encontrados {len(df)} nulos na media_movel_7d"

def test_gold_cinco_cidades(con):
    # Verifica se todas as 5 cidades estão presentes na Gold
    df = con.execute("SELECT DISTINCT cidade_nome FROM gold.amplitude_termica").df()
    assert len(df) == 5, f"Esperado 5 cidades, encontrado {len(df)}"