# SAC Analytics: Tratamento e Visualização de Dados de Atendimento

## Descrição do projeto

Este projeto acadêmico realiza o tratamento de uma base de atendimentos de SAC utilizando Python, Pandas e Power BI.

O Python é responsável por preparar os dados, padronizar campos, criar indicadores auxiliares e gerar arquivos prontos para análise. O Power BI é utilizado para a construção dos dashboards e visualização dos principais indicadores de atendimento.

## Objetivo

O objetivo principal é transformar arquivos CSV exportados do sistema de atendimento em uma base organizada, consistente e adequada para análise.

Com isso, é possível acompanhar indicadores como:

- quantidade total de atendimentos;
- atendimentos finalizados e em aberto;
- taxa de finalização;
- tempo médio em fila;
- tempo médio de atendimento;
- atendimentos por serviço;
- recorrência dos atendimentos;
- evolução diária dos atendimentos;
- comparação entre realizado e curva esperada/projeção.

## Tecnologias utilizadas

- Python
- Pandas
- OpenPyXL
- Power BI
- GitHub

## Bibliotecas Python

As dependências do projeto estão no arquivo `requirements.txt`:

- `pandas`: usada para leitura, tratamento, transformação, agrupamento e exportação dos dados.
- `openpyxl`: usada pelo Pandas para gerar o arquivo Excel `.xlsx` com múltiplas abas. 

Instalação:

```bash
pip install -r requirements.txt
```

## Funcionamento da entrada de dados

O script identifica automaticamente a origem dos dados.

Se houver arquivos CSV em `dados_brutos/` com o padrão:

```text
relatorio_atendimento_analitico*.csv
```

eles serão carregados automaticamente como dados brutos.

Isso permite ler arquivos com nomes como:

```text
relatorio_atendimento_analitico.csv
relatorio_atendimento_analitico_6a145a85d9aee.csv
```

Se não houver arquivos em `dados_brutos/`, o script usa a base fictícia de apoio:

```text
dados_ficticios/base_sac_ficticia.csv
```

## Etapas realizadas no tratamento

1. Leitura automática dos arquivos CSV de entrada.
2. Tratamento de codificação, incluindo arquivos em `utf-8-sig` ou `latin1`.
3. Limpeza de caracteres invisíveis no cabeçalho, como BOM.
4. Consolidação de múltiplos arquivos brutos em uma única base.
5. Verificação inicial da estrutura da base.
6. Tratamento de campos vazios.
7. Conversão de campos de data.
8. Conversão de campos de tempo para minutos.
9. Criação de colunas auxiliares para o Power BI.
10. Criação de faixas de tempo em fila e tempo de atendimento.
11. Criação de indicadores de finalização e recorrência.
12. Geração de projeção estatística.
13. Geração de curva esperada diária para comparação com o realizado.
14. Exportação de CSVs de compatibilidade.
15. Exportação de um arquivo Excel consolidado com múltiplas abas para uso no Power BI.

## Estrutura do projeto

- `tratamento_sac_pandas.py`: script principal de tratamento dos dados.
- `requirements.txt`: lista de bibliotecas necessárias.
- `README.md`: documentação do projeto.
- `.gitignore`: configuração para evitar envio de dados brutos, ambiente virtual e arquivos temporários.
- `dados_brutos/`: pasta para os arquivos CSV originais exportados do sistema.
- `dados_ficticios/`: pasta com uma base fictícia de apoio para execução acadêmica.
- `dados_tratados/`: pasta onde são gerados os arquivos finais tratados.
- `powerbi/`: pasta destinada ao arquivo `.pbix` do Power BI.

## Arquivos de entrada

Entrada principal:

```text
dados_brutos/relatorio_atendimento_analitico*.csv
```

Entrada alternativa, usada apenas quando não houver dados brutos:

```text
dados_ficticios/base_sac_ficticia.csv
```

## Arquivo de saída

O script gera um único arquivo tratado para uso no Power BI:

```text
dados_tratados/sac_analytics_powerbi.xlsx
```

Ele reúne as tabelas tratadas em um único arquivo com abas separadas. Os CSVs auxiliares não são mais gerados para evitar duplicidade de fontes e reduzir erros de referência no Power BI.

## Abas do Excel para Power BI

### Base_Real

Contém os atendimentos reais tratados.

Uso recomendado:

- cards principais;
- finalizados;
- taxa de finalização;
- tempo médio em fila;
- tempo médio de atendimento;
- status;
- recorrência;
- faixa de fila;
- duração média por serviço.

### Projecao

Contém a projeção estatística futura agregada por data e serviço.

Uso recomendado:

- volume projetado;
- atendimentos por serviço com projeção;
- indicadores em que projeção de volume faça sentido.

### Evolucao

Contém uma tabela diária pronta para gráficos de evolução.

Ela reúne:

- atendimentos reais por dia;
- atendimentos projetados por dia;
- total com projeção;
- serviço;
- ano;
- mês;
- ano-mês;
- ordem cronológica.

Essa aba permite criar gráficos de acompanhamento diário, comparando o realizado com a curva esperada/projetada.

### Dim_Servico

Tabela auxiliar com a lista de serviços.

Uso recomendado:

- filtro de serviço;
- eixo de gráficos por serviço;
- relacionamento com `Base_Real`, `Projecao` e `Evolucao`.

### Dim_Calendario

Tabela calendário com datas, ano, mês, nome do mês, ano-mês e ordem cronológica.

Uso recomendado:

- filtros de ano;
- filtros de mês;
- ordenação temporal;
- gráficos de evolução.

## Projeção estatística

A projeção é calculada no Python usando uma média móvel dos últimos 30 dias, ajustada pelo comportamento histórico de cada dia da semana.

O projeto trabalha com dois conceitos relacionados:

- `Projecao`: projeção futura dos próximos 30 dias.
- `Evolucao`: curva esperada diária, incluindo o mês atual, para comparação entre realizado e projetado.

Essa separação evita que dados projetados contaminem gráficos que só fazem sentido com dados reais, como:

- status;
- recorrência;
- tempo em fila;
- tempo médio de atendimento;
- faixa de fila.

## Dados fictícios

Para fins de testes, o projeto mantém uma base fictícia de apoio, sem referência a empresas, clientes, pessoas reais ou informações internas.

Essa base fictícia não representa uma simulação estatística nem uma previsão futura. Ela serve apenas para permitir a execução do tratamento quando os dados brutos não estiverem disponíveis.

## Como executar o projeto

1. Instale o Python.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Coloque os arquivos brutos na pasta:

```text
dados_brutos/
```

4. Execute o script:

```bash
python tratamento_sac_pandas.py
```

Se estiver usando o ambiente virtual local do projeto no Windows, use:

```powershell
.\.venv\Scripts\python.exe tratamento_sac_pandas.py
```

Para gerar a versão pública com dados fictícios, mesmo que existam arquivos em `dados_brutos/`, use:

```powershell
.\.venv\Scripts\python.exe tratamento_sac_pandas.py --ficticio
```

5. Após a execução, os arquivos tratados serão gerados em:

```text
dados_tratados/
```

## Versão pública do dashboard

O repositório inclui uma versão pública do arquivo tratado e do Power BI usando apenas dados fictícios:

```text
dados_tratados/sac_analytics_powerbi.xlsx
powerbi/sac_analytics_powerbi.pbix
```

Antes de publicar esses arquivos, gere a base com:

```powershell
.\.venv\Scripts\python.exe tratamento_sac_pandas.py --ficticio
```

Essa etapa garante que o Excel usado pelo Power BI seja montado somente com a base `dados_ficticios/base_sac_ficticia.csv`.


## Autor

Rodrigo Barros Sanches
