import duckdb
from pathlib import Path

DB_PATH = Path("data/warehouse.duckdb")

def agregar():
    con = duckdb.connect(str(DB_PATH))
    
    _criar_schema(con)
    _resumo_mensal(con)
    _amplitude_termica(con)
    _media_movel(con)
    
    con.close()
    print("Agregação concluída! Camada Gold gerada.")

def _criar_schema(con):
    # Cria o schema gold se ainda não existir
    con.execute("CREATE SCHEMA IF NOT EXISTS gold")
    print("Schema gold criado.")

def _resumo_mensal(con):
    con.execute("""
        CREATE OR REPLACE TABLE gold.resumo_mensal AS  -- cria ou substitui a tabela
        SELECT
            cidade_nome,                                        -- nome da cidade
            DATE_TRUNC('month', data)    AS mes,                -- trunca a data para o primeiro dia do mês
            ROUND(AVG(temp_max), 1)      AS media_temp_max,     -- média das máximas do mês
            ROUND(AVG(temp_min), 1)      AS media_temp_min,     -- média das mínimas do mês
            ROUND(MAX(temp_max), 1)      AS max_absoluta,       -- maior temperatura do mês
            ROUND(MIN(temp_min), 1)      AS min_absoluta        -- menor temperatura do mês
        FROM silver.clima                                       -- lê da camada Silver
        GROUP BY cidade_nome, DATE_TRUNC('month', data)        -- agrupa por cidade e mês
        ORDER BY cidade_nome, mes                              -- ordena por cidade e mês
    """)
    print("Gold criada: gold.resumo_mensal")

def _amplitude_termica(con):
    con.execute("""
        CREATE OR REPLACE TABLE gold.amplitude_termica AS          -- cria ou substitui a tabela
        SELECT
            cidade_nome,                                           -- nome da cidade
            ROUND(AVG(temp_max - temp_min), 1) AS amplitude_media, -- média da diferença entre máxima e mínima
            ROUND(MAX(temp_max - temp_min), 1) AS amplitude_maxima, -- maior amplitude registrada
            ROUND(MIN(temp_max - temp_min), 1) AS amplitude_minima  -- menor amplitude registrada
        FROM silver.clima                                          -- lê da camada Silver
        GROUP BY cidade_nome                                       -- agrupa por cidade
        ORDER BY amplitude_media DESC                             -- ordena do maior para o menor
    """)
    print("Gold criada: gold.amplitude_termica")

def _media_movel(con):
    con.execute("""
        CREATE OR REPLACE TABLE gold.media_movel AS        -- cria ou substitui a tabela
        SELECT
            cidade_nome,                                   -- nome da cidade
            data,                                          -- data do registro
            temp_max,                                      -- temperatura máxima do dia
            ROUND(
                AVG(temp_max) OVER (                       -- window function — não colapsa as linhas
                    PARTITION BY cidade_nome               -- janela separada por cidade
                    ORDER BY data                          -- ordena por data dentro da janela
                    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW  -- janela de 7 dias
                ), 1
            ) AS media_movel_7d                            -- média móvel de 7 dias
        FROM silver.clima                                  -- lê da camada Silver
        ORDER BY cidade_nome, data                         -- ordena por cidade e data
    """)
    print("Gold criada: gold.media_movel")