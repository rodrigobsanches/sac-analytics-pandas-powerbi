# SAC Analytics: Tratamento e Visualização de Dados de Atendimento

## Descrição do projeto

Este projeto acadêmico tem como objetivo realizar o tratamento de uma base simulada de atendimentos de SAC utilizando Python e a biblioteca Pandas.

Após o tratamento dos dados em Python, a base final será utilizada para criação de dashboards no Power BI, permitindo uma análise visual dos principais indicadores do atendimento.

## Objetivo

O objetivo principal do projeto é transformar uma base de dados em formato CSV em uma base organizada e preparada para análise.

Com isso, será possível acompanhar indicadores como:

- quantidade total de atendimentos;
- atendimentos finalizados e em aberto;
- tempo médio de atendimento;
- tempo médio em fila;
- atendimentos por status;
- atendimentos por serviço;
- recorrência dos atendimentos.

## Tecnologias utilizadas

- Python
- Pandas
- Power BI
- Git
- GitHub

## Etapas realizadas no tratamento dos dados

1. Leitura do arquivo CSV simulado.
2. Verificação da quantidade de linhas e colunas.
3. Padronização dos nomes das colunas.
4. Tratamento de valores vazios.
5. Conversão de campos de data.
6. Conversão de campos de tempo para minutos.
7. Criação de novas colunas para facilitar a análise.
8. Remoção de colunas que não serão usadas no Power BI.
9. Exportação de apenas uma base tratada para uso no Power BI.

## Estrutura do projeto

- `tratamento_sac_pandas.py`: arquivo principal com o código em Python.
- `requirements.txt`: lista das bibliotecas necessárias.
- `README.md`: documentação do projeto.
- `.gitignore`: arquivo usado para impedir o envio de dados brutos e arquivos temporários.
- `dados_simulados/`: pasta com a base simulada utilizada no projeto.
- `dados_tratados/`: pasta onde será gerado o único CSV final tratado.

## Arquivos utilizados

Entrada:

- `dados_simulados/base_sac_simulada.csv`

Saída:

- `dados_tratados/base_sac_tratada_powerbi.csv`

## Observação sobre os dados

A base original não será disponibilizada neste repositório por conter informações internas e possíveis dados sensíveis.

Para fins acadêmicos, o projeto utiliza somente dados simulados, sem referência a empresas, clientes, pessoas reais ou informações internas.

## Como executar o projeto

1. Instalar o Python.
2. Instalar a biblioteca Pandas usando o comando: `pip install pandas`
3. Executar o arquivo principal usando o comando: `python tratamento_sac_pandas.py`
4. Após a execução, será gerado apenas um arquivo CSV tratado na pasta `dados_tratados`.

## Próximas etapas

As próximas etapas do projeto serão:

- importar a base tratada no Power BI;
- criar medidas e indicadores;
- montar os dashboards;
- documentar os resultados encontrados;
- incluir capturas de tela dos dashboards no relatório final.

## Autor

Rodrigo Barros Sanches
