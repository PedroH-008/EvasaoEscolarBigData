# Big Data aplicado à evasão escolar

Projeto acadêmico que demonstra como Big Data e ciência de dados podem apoiar a prevenção da evasão escolar. A solução gera uma base sintética de uma escola, processa os dados com Apache Spark, treina um modelo de risco de evasão e exibe os resultados em um dashboard interativo com Streamlit.

## Resumo rápido

Se você quiser entender o projeto em 30 segundos, ele funciona assim:

1. Gera dados escolares sintéticos com alunos, turmas, frequência, notas, contexto socioeconômico e engajamento digital.
2. Processa os dados com Spark em camadas bronze, silver e gold.
3. Calcula um score de risco de evasão por aluno.
4. Exibe indicadores e gráficos no dashboard para apoiar a busca ativa e a tomada de decisão.

## Quick Start

1. Entre na pasta do projeto:

```bash
cd /home/pedro/Projetos/ExBigData
```

2. Crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

4. Gere os dados de exemplo:

```bash
python src/generate_school_data.py --students 2500
```

5. Configure o Java e execute o pipeline Spark:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
python src/spark_pipeline.py
```

6. Abra o dashboard:

```bash
streamlit run src/dashboard.py
```

Depois acesse:

```text
http://localhost:8501
```

## Sobre o projeto

O objetivo deste trabalho é mostrar, de forma prática, como dados educacionais podem ser integrados e analisados para identificar estudantes em maior risco de evasão. O projeto foi pensado para uma apresentação acadêmica e reúne engenharia de dados, análise exploratória, machine learning e visualização interativa.

O fluxo principal do sistema é:

- gerar dados sintéticos com uma estrutura próxima da realidade escolar;
- organizar os dados em camadas de processamento;
- criar métricas de acompanhamento e um score de risco;
- apresentar os resultados em um dashboard com foco em decisão.

## O que o sistema mostra

- total de alunos monitorados;
- quantidade de alunos evadidos;
- risco médio de evasão;
- AUC do modelo;
- risco médio por bairro;
- faltas por disciplina;
- relação entre notas, faltas e risco;
- motivos de evasão;
- lista de alunos prioritários para busca ativa;
- detalhes individuais do aluno selecionado na lateral do dashboard.

## Tecnologias usadas

- Python para orquestração e scripts;
- Apache Spark / PySpark para processamento distribuído local;
- Spark MLlib para o modelo de classificação;
- Pandas para leitura e manipulação dos dados do dashboard;
- Plotly para gráficos interativos;
- Streamlit para interface web;
- CSV e Parquet como formatos de saída analítica;
- SQLite como banco local da base gerada.

## Estrutura do projeto

```text
.
├── README.md
├── requirements.txt
├── data/
│   ├── bronze/   # dados brutos gerados
│   ├── silver/   # perfil consolidado do aluno
│   └── gold/     # indicadores finais e score de risco
├── docs/
│   └── arquitetura.md
├── sql/
│   └── schema.sql
└── src/
	├── dashboard.py
	├── generate_school_data.py
	└── spark_pipeline.py
```

## Camadas de dados

### Bronze

Camada com os dados brutos gerados pelo script de criação da base. Contém tabelas como alunos, responsáveis, turmas, frequência, notas, engajamento digital e intervenções.

### Silver

Camada intermediária com o perfil consolidado do aluno. Aqui os dados são unidos e preparados para análise.

### Gold

Camada final com os indicadores prontos para consumo no dashboard, incluindo score de risco, KPIs, faltas por disciplina, risco por bairro e motivos de evasão.

## Como executar do zero

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/generate_school_data.py --students 2500
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
python src/spark_pipeline.py
streamlit run src/dashboard.py
```

## Requisitos

- Python 3.10 ou superior;
- Java JDK 17 ou superior;
- ambiente virtual com as dependências instaladas.

## Problemas comuns

### JAVA_HOME não configurado

Se o Spark não iniciar, verifique se a variável JAVA_HOME está apontando para o JDK correto.

### Java gateway process exited

Esse erro costuma aparecer quando o Java não está instalado, quando JAVA_HOME está incorreto ou quando a versão do JDK é incompatível.

## Observações para apresentação

- O projeto foi estruturado para demonstrar análise orientada a decisão.
- O dashboard foi pensado para facilitar a leitura do professor, com filtros, indicadores e visão individual do aluno.
- A solução principal usa Spark, então a execução depende de Java configurado.

## Documentação complementar

Se quiser entender a arquitetura com mais detalhe, veja também [docs/arquitetura.md](docs/arquitetura.md).