# weather-etl

Pipeline de dados meteorológicos com arquitetura Medallion, construído em Python.

Coleta dados históricos de temperatura de 5 cidades brasileiras via API pública (Open-Meteo), processa em três camadas de qualidade (Bronze → Silver → Gold) e persiste em um Data Warehouse local com DuckDB.

---

## Arquitetura Medallion

```
API Open-Meteo
      ↓
  [Bronze]  → JSONs brutos por cidade/data em data/bronze/
      ↓
  [Silver]  → dados limpos e tipados em DuckDB (silver.clima)
      ↓
  [Gold]    → agregações analíticas em DuckDB
                ├── gold.resumo_mensal
                ├── gold.amplitude_termica
                └── gold.media_movel
```

## Stack

| Ferramenta | Uso |
|---|---|
| Python 3.11 | linguagem principal |
| requests | extração via API REST |
| pandas | transformação e limpeza dos dados |
| DuckDB | data warehouse local |
| pytest | testes de qualidade por camada |
| pathlib | manipulação de caminhos multiplataforma |

---

## Estrutura de pastas

```
weather-etl/
├── etl/
│   ├── extract.py      # camada Bronze — extração da API
│   ├── transform.py    # camada Silver — limpeza com pandas
│   └── aggregate.py    # camada Gold — agregações com DuckDB
├── data/
│   ├── bronze/         # JSONs brutos (gerado pelo pipeline)
│   ├── silver/         # CSVs limpos (gerado pelo pipeline)
│   └── gold/           # reservado para exportações futuras
├── tests/
│   ├── test_bronze.py  # valida estrutura dos JSONs
│   ├── test_silver.py  # valida schema, tipos e nulos
│   └── test_gold.py    # valida tabelas e agregações
├── pipeline.py         # ponto de entrada — orquestra o pipeline
└── requirements.txt    # dependências do projeto
```

## Como rodar

**1. Clonar o repositório**
```bash
git clone https://github.com/FredVenturin/weather-api-data.git
cd weather-etl
```

**2. Criar e ativar o ambiente virtual**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / Mac
source .venv/bin/activate
```

**3. Instalar as dependências**
```bash
pip install -r requirements.txt
```

**4. Rodar o pipeline**
```bash
python pipeline.py
```

**5. Rodar os testes**
```bash
pytest tests/ -v
```

---

## Análises disponíveis

Execute as análises prontas sobre os dados Gold:

```bash
python queries/analises.py
```

Gera três relatórios em `queries/resultados/`:

| Arquivo | Pergunta respondida |
|---|---|
| `cidade_mais_instavel.csv` | Qual cidade tem maior amplitude térmica? |
| `resumo_por_cidade.csv` | Qual o resumo de temperatura por cidade? |
| `tendencia_temperatura.csv` | Qual a tendência mais recente por cidade? |

## Decisões técnicas

**Por que DuckDB?**
DuckDB roda embarcado no processo Python, sem necessidade de servidor. Ideal para pipelines locais e de portfólio — qualquer pessoa consegue rodar sem configurar infraestrutura adicional.

**Por que arquitetura Medallion?**
Separar Bronze, Silver e Gold garante rastreabilidade — os dados brutos são sempre preservados e cada camada tem uma responsabilidade clara. É o padrão adotado por empresas como Nubank, iFood e Mercado Livre.

**Por que pandas para a camada Silver?**
Operações vetorizadas do pandas são significativamente mais eficientes que loops Python para limpeza de dados. Em pipelines com milhões de registros, essa diferença é crítica.

---

## Dados coletados

Temperaturas máximas e mínimas diárias dos últimos 30 dias de:
- São Paulo
- Rio de Janeiro
- Brasília
- Fortaleza
- Porto Alegre

Fonte: [Open-Meteo API](https://open-meteo.com/) — gratuita e sem necessidade de cadastro.
