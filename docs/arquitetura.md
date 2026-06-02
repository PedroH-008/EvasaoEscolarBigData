# Arquitetura do Projeto

Este projeto transforma a proposta extensionista sobre evasao escolar em uma solucao de Big Data aplicada a educacao.

## Camadas de dados

- Bronze: arquivos CSV brutos gerados para simular o banco escolar.
- Silver: perfil consolidado do aluno, criado pelo Spark a partir dos dados brutos.
- Gold: indicadores finais para gestao escolar, dashboard e tomada de decisao.

## Tecnologias

- Python: geracao de dados e orquestracao dos scripts.
- SQLite: banco relacional escolar completo para consultas SQL locais.
- Apache Spark: processamento distribuido, uniao de tabelas e criacao de features.
- Spark MLlib: modelo de regressao logistica para classificar risco de evasao.
- Pandas: leitura dos datasets no dashboard.
- Plotly e Streamlit: visualizacoes interativas.

## Indicadores analisados

- Taxa de faltas por aluno e disciplina.
- Media de notas e quantidade de recuperacoes.
- Acesso a internet, transporte, renda familiar e trabalho no contraturno.
- Engajamento em plataforma digital.
- Intervencoes pedagogicas e busca ativa.
- Risco preditivo de evasao por aluno.
- Taxa de evasao por bairro e motivos principais.

## Como a solucao responde ao problema

A documentacao original pergunta como usar Big Data para analisar grandes volumes de dados e prevenir evasao escolar. A solucao proposta responde com um fluxo completo:

1. Integra dados de varias fontes escolares e socioeconomicas.
2. Processa os dados em escala com Spark.
3. Gera indicadores para acompanhar estudantes vulneraveis.
4. Treina um modelo simples e explicavel de risco de evasao.
5. Entrega um painel para priorizar busca ativa, reforco escolar e apoio psicossocial.
