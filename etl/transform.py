import json      #  vai ler os arquivos JSON que estão no bronze
import duckdb    #  conectar ao banco de dados e persistir os dados limpos na camada silver
import pandas as pd     #  ferramenta de limpeza e manipulação dos dados
from pathlib import Path    #  caminhos de arquivo
from datetime import datetime    #  variaveis datetime

BRONZE_PATH = Path("data/bronze")
SILVER_PATH = Path("data/silver")
DB_PATH     = Path("data/warehouse.duckdb")

def ler_bronze() -> pd.DataFrame:
    # Busca todos os arquivos JSON dentro da pasta Bronze
    arquivos = list(BRONZE_PATH.glob("*.json"))
    
    # Se não encontrar nenhum arquivo, lança erro orientando o usuário
    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo encontrado na camada Bronze. Rode o extract primeiro.")
    
    # Lista que vai acumular um DataFrame por cidade
    dataframes = []
    
    for arquivo in arquivos:
        # Abre e lê o JSON de cada cidade
        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        # Monta um DataFrame com as colunas que nos interessam
        # As listas paralelas do JSON viram colunas alinhadas
        df = pd.DataFrame({
            "cidade_nome":  dados["cidade_nome"],
            "data":         dados["daily"]["time"],
            "temp_max":     dados["daily"]["temperature_2m_max"],
            "temp_min":     dados["daily"]["temperature_2m_min"],
        })
        
        # Adiciona o DataFrame dessa cidade na lista
        dataframes.append(df)
    
    # Junta todos os DataFrames das 5 cidades em um só
    return pd.concat(dataframes, ignore_index=True)


def limpar_silver(df: pd.DataFrame) -> pd.DataFrame:
    # Converte a coluna data de string para o tipo date do pandas
    df["data"] = pd.to_datetime(df["data"])
    
    # Garante que temp_max e temp_min são números decimais
    df["temp_max"] = df["temp_max"].astype(float)
    df["temp_min"] = df["temp_min"].astype(float)
    
    # Remove linhas onde temp_max ou temp_min são nulas
    df = df.dropna(subset=["temp_max", "temp_min"])
    
    # Remove linhas duplicadas
    df = df.drop_duplicates(subset=["cidade_nome", "data"])
    
    # Adiciona coluna registrando quando esse dado foi processado
    df["ingested_at"] = datetime.now()
    
    return df

def salvar_silver(df: pd.DataFrame) -> None:
    # Cria a pasta data/silver/ se não existir
    SILVER_PATH.mkdir(parents=True, exist_ok=True)
    
    # Salva os dados limpos como CSV para inspeção humana
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    caminho_csv = SILVER_PATH / f"clima_silver_{data_hoje}.csv"
    df.to_csv(caminho_csv, index=False, encoding="utf-8")
    print(f"Silver CSV salvo: {caminho_csv}")
    
    # Persiste os dados no DuckDB como tabela estruturada
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute("""
        CREATE OR REPLACE TABLE silver.clima AS
        SELECT * FROM df
    """)
    con.close()
    print("Silver salvo no DuckDB: silver.clima")


def transformar():
    # Lê todos os JSONs da camada Bronze e junta em um DataFrame
    print("Lendo dados da Bronze...")
    df = ler_bronze()
    
    # Aplica as regras de limpeza e tipagem
    print("Limpando e tipando dados...")
    df = limpar_silver(df)
    
    # Persiste os dados limpos na camada Silver
    print("Salvando na camada Silver...")
    salvar_silver(df)
    
    print(f"Transformação concluída! {len(df)} registros processados.")   