# Big Data aplicado à evasão escolar — guia rápido

Este repositório demonstra como usar processamento (Apache Spark) e ciência de dados para identificar estudantes com maior risco de evasão. A partir de agora o projeto exige Java/Spark — o pipeline local foi removido e o fluxo principal usa exclusivamente `src/spark_pipeline.py`.

Principais componentes:
- Geração de dados: `src/generate_school_data.py`
- Pipeline Spark (PySpark + MLlib): `src/spark_pipeline.py` (requer Java 17+)
- Dashboard: `src/dashboard.py` (Streamlit)

## Rápido (Quick Start)

1) Entre na pasta do projeto:

```bash
cd /home/pedro/Projetos/ExBigData
```

2) Crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Instale dependências:

```bash
python -m pip install -r requirements.txt
```

4) Gerar dados de exemplo (2500 alunos):

```bash
python src/generate_school_data.py --students 2500
```

5) Executar pipeline Spark (obrigatório — requer Java 17+):

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
python src/spark_pipeline.py
```

6) Abrir o dashboard (Streamlit):

```bash
streamlit run src/dashboard.py
# então abra: http://localhost:8511
```

## Estrutura principal

```
data/            # bronze, silver, gold e banco SQLite (data/escola_evasao.db)
src/             # scripts: geração, pipelines e dashboard
docs/            # documentação (arquitetura)
sql/             # schema do banco
requirements.txt # dependências Python
```

## Detalhes e recomendações

-- Este repositório agora exige Java 17+ para executar o pipeline. Configure `JAVA_HOME` antes de rodar o pipeline Spark.
-- O script de geração cria CSVs em `data/bronze` e o banco `data/escola_evasao.db`.

## Problemas comuns

- `JAVA_HOME is not set`: exporte `JAVA_HOME` conforme mostrado acima.
- `Java gateway process exited`: verifique se o Java é compatível (JDK 11+), e se não há bloqueio de sockets locais.

## Executar tudo do zero

```bash
source .venv/bin/activate
python src/generate_school_data.py --students 2500
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
python src/spark_pipeline.py
streamlit run src/dashboard.py
```

---