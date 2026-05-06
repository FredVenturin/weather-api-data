import duckdb
import pandas as pd
from pathlib import Path

DB_PATH      = Path("data/warehouse.duckdb")
QUERIES_PATH = Path("queries/resultados")

def conectar():
    return duckdb.connect(str(DB_PATH))

def cidade_mais_instavel():
    # Qual cidade tem maior amplitude térmica média?
    con = conectar()
    df = con.execute("""
        SELECT 
            cidade_nome,
            amplitude_media,
            amplitude_maxima,
            amplitude_minima
        FROM gold.amplitude_termica
        LIMIT 1
    """).df()
    con.close()
    
    cidade = df.iloc[0]["cidade_nome"]
    amplitude = df.iloc[0]["amplitude_media"]
    print(f"Cidade mais instável: {cidade} ({amplitude}°C de amplitude média)")
    return df

def resumo_por_cidade():
    # Temperatura média, máxima e mínima de cada cidade no período
    con = conectar()
    df = con.execute("""
        SELECT
            cidade_nome,
            ROUND(AVG(media_temp_max), 1) AS media_max,
            ROUND(AVG(media_temp_min), 1) AS media_min,
            MAX(max_absoluta)             AS maior_temp,
            MIN(min_absoluta)             AS menor_temp
        FROM gold.resumo_mensal
        GROUP BY cidade_nome
        ORDER BY media_max DESC
    """).df()
    con.close()
    
    print("\nResumo por cidade:")
    print(df.to_string(index=False))
    return df

def tendencia_temperatura():
    # Média móvel mais recente de cada cidade
    con = conectar()
    df = con.execute("""
        SELECT
            cidade_nome,
            data,
            temp_max,
            media_movel_7d
        FROM gold.media_movel
        WHERE data = (SELECT MAX(data) FROM gold.media_movel)
        ORDER BY media_movel_7d DESC
    """).df()
    con.close()
    
    print("\nTendência mais recente (média móvel 7 dias):")
    print(df.to_string(index=False))
    return df

def exportar_resultados():
    # Cria a pasta de resultados se não existir
    QUERIES_PATH.mkdir(parents=True, exist_ok=True)
    
    # Executa todas as análises e exporta em CSV
    cidade_mais_instavel().to_csv(QUERIES_PATH / "cidade_mais_instavel.csv", index=False)
    resumo_por_cidade().to_csv(QUERIES_PATH / "resumo_por_cidade.csv", index=False)
    tendencia_temperatura().to_csv(QUERIES_PATH / "tendencia_temperatura.csv", index=False)
    
    print(f"\nResultados exportados em {QUERIES_PATH}/")

if __name__ == "__main__":
    exportar_resultados()