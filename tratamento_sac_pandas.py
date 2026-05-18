# Projeto: SAC Analytics
# Objetivo: tratar uma base simulada de atendimentos usando Pandas
# Autor: Rodrigo Sanches

import pandas as pd


# 1) Lendo o arquivo CSV simulado
# O arquivo usa ponto e vírgula como separador, por isso usamos sep=";".
atendimentos = pd.read_csv("dados_simulados/base_sac_simulada.csv", sep=";", encoding="utf-8-sig")

print("Base carregada com sucesso!")
print("Quantidade de linhas e colunas:")
print(atendimentos.shape)
print("\nPrimeiras linhas da base:")
print(atendimentos.head())


# 2) Visualizando informações iniciais da base
# O info mostra as colunas, tipos de dados e valores nulos.
print("\nInformações da base antes do tratamento:")
print(atendimentos.info())

# O describe mostra estatísticas simples das colunas numéricas.
print("\nResumo estatístico inicial:")
print(atendimentos.describe())


# 3) Tratando valores vazios em algumas colunas importantes
# Alguns campos podem estar vazios. Para não atrapalhar a análise, vamos preencher.
atendimentos.loc[atendimentos["Agente"].isnull(), "Agente"] = "Não informado"
atendimentos.loc[atendimentos["Recorrência"].isnull(), "Recorrência"] = "Sem recorrência"
atendimentos.loc[atendimentos["Observação"].isnull(), "Observação"] = "Sem observação"

# Na base simulada, alguns campos de data podem vir com "-".
# Vamos trocar "-" por vazio para facilitar a conversão de data.
atendimentos.loc[atendimentos["Data de finalização"] == "-", "Data de finalização"] = ""
atendimentos.loc[atendimentos["Data de fila"] == "-", "Data de fila"] = ""


# 4) Convertendo colunas de data
# No CSV, as datas chegam como texto. Para análise no Power BI, é melhor converter para data.
atendimentos["Data de Entrada"] = pd.to_datetime(atendimentos["Data de Entrada"], dayfirst=True, errors="coerce")
atendimentos["Data de Atendimento"] = pd.to_datetime(atendimentos["Data de Atendimento"], dayfirst=True, errors="coerce")
atendimentos["Data de fila"] = pd.to_datetime(atendimentos["Data de fila"], dayfirst=True, errors="coerce")
atendimentos["Data de finalização"] = pd.to_datetime(atendimentos["Data de finalização"], dayfirst=True, errors="coerce")


# 5) Criando colunas de apoio a partir da data de entrada
# Essas colunas ajudam na criação dos gráficos no Power BI.
atendimentos["Ano"] = atendimentos["Data de Entrada"].dt.year
atendimentos["Mes"] = atendimentos["Data de Entrada"].dt.month
atendimentos["Dia"] = atendimentos["Data de Entrada"].dt.day
atendimentos["Hora Entrada"] = atendimentos["Data de Entrada"].dt.hour
atendimentos["Dia da Semana"] = atendimentos["Data de Entrada"].dt.day_name()


# 6) Função simples para transformar tempo em minutos
# Exemplo: 01:30:00 vira 90 minutos.
def tempo_para_minutos(valor):
    if pd.isnull(valor):
        return 0

    valor = str(valor)
    partes = valor.split(":")

    if len(partes) != 3:
        return 0

    horas = int(partes[0])
    minutos = int(partes[1])
    segundos = int(partes[2])

    total_minutos = (horas * 60) + minutos + (segundos / 60)
    return round(total_minutos, 2)


# 7) Aplicando a função nas colunas de tempo
# Aqui usamos apply, como foi mostrado em aula.
atendimentos["Tempo em Fila Minutos"] = atendimentos["Tempo em Fila"].apply(tempo_para_minutos)
atendimentos["Tempo de Atendimento Minutos"] = atendimentos["Tempo de Atendimento"].apply(tempo_para_minutos)
atendimentos["Tempo em Pendência Minutos"] = atendimentos["Tempo em Pendência"].apply(tempo_para_minutos)
atendimentos["TMIC Minutos"] = atendimentos["TMIC"].apply(tempo_para_minutos)
atendimentos["TMIA Minutos"] = atendimentos["TMIA"].apply(tempo_para_minutos)


# 8) Criando uma coluna com tempo total
# Somamos fila, atendimento e pendência para ter uma visão geral do tempo do atendimento.
atendimentos["Tempo Total Minutos"] = atendimentos.apply(
    lambda linha: linha["Tempo em Fila Minutos"] + linha["Tempo de Atendimento Minutos"] + linha["Tempo em Pendência Minutos"],
    axis=1
)


# 9) Criando colunas de classificação para ajudar os gráficos
# Usamos str.contains para procurar texto dentro da coluna Status.
atendimentos["Finalizado"] = atendimentos["Status"].str.contains("Finalizado", na=False)

# Usamos isin para verificar se o atendimento está em algum dos tipos de recorrência abaixo.
atendimentos["Possui Recorrência"] = atendimentos["Recorrência"].isin(["Recorrente", "Reincidente", "Rechamada"])

# Classificação simples do tempo de fila.
atendimentos.loc[atendimentos["Tempo em Fila Minutos"] <= 5, "Faixa Fila"] = "Até 5 minutos"
atendimentos.loc[(atendimentos["Tempo em Fila Minutos"] > 5) & (atendimentos["Tempo em Fila Minutos"] <= 30), "Faixa Fila"] = "De 6 a 30 minutos"
atendimentos.loc[atendimentos["Tempo em Fila Minutos"] > 30, "Faixa Fila"] = "Acima de 30 minutos"

# Classificação simples do tempo de atendimento.
atendimentos.loc[atendimentos["Tempo de Atendimento Minutos"] <= 15, "Faixa Atendimento"] = "Até 15 minutos"
atendimentos.loc[(atendimentos["Tempo de Atendimento Minutos"] > 15) & (atendimentos["Tempo de Atendimento Minutos"] <= 60), "Faixa Atendimento"] = "De 16 a 60 minutos"
atendimentos.loc[atendimentos["Tempo de Atendimento Minutos"] > 60, "Faixa Atendimento"] = "Acima de 60 minutos"


# 10) Filtros simples, parecidos com os exemplos feitos em aula
atendimentos_finalizados = atendimentos[
    atendimentos["Status"].str.contains("Finalizado", na=False)
]

atendimentos_com_fila_alta = atendimentos[
    atendimentos["Tempo em Fila Minutos"] > 30
]

atendimentos_recorrentes = atendimentos[
    atendimentos["Recorrência"].isin(["Recorrente", "Reincidente", "Rechamada"])
]

print("\nQuantidade de atendimentos finalizados:")
print(len(atendimentos_finalizados.index))

print("\nQuantidade de atendimentos com fila acima de 30 minutos:")
print(len(atendimentos_com_fila_alta.index))

print("\nQuantidade de atendimentos com recorrência:")
print(len(atendimentos_recorrentes.index))


# 11) Agrupamentos para conferência dos dados
# O groupby foi usado apenas para visualizar os totais no terminal.
print("\nQuantidade de atendimentos por serviço:")
print(atendimentos.groupby("Serviço")["Protocolo"].count())

print("\nTempo médio de atendimento por serviço:")
print(atendimentos.groupby("Serviço")["Tempo de Atendimento Minutos"].mean())

print("\nQuantidade de atendimentos por status:")
print(atendimentos.groupby("Status")["Protocolo"].count())


# 12) KPIs simples para colocar no relatório e no Power BI
qtd_atendimentos = len(atendimentos.index)
qtd_protocolos = atendimentos["Protocolo"].nunique()
qtd_finalizados = len(atendimentos_finalizados.index)
qtd_recorrentes = len(atendimentos_recorrentes.index)
tempo_medio_fila = atendimentos["Tempo em Fila Minutos"].mean()
tempo_medio_atendimento = atendimentos["Tempo de Atendimento Minutos"].mean()
maior_tempo_atendimento = atendimentos["Tempo de Atendimento Minutos"].max()

print("\n--- KPIs DO PROJETO ---")
print("Total de atendimentos:", qtd_atendimentos)
print("Total de protocolos únicos:", qtd_protocolos)
print("Atendimentos finalizados:", qtd_finalizados)
print("Atendimentos com recorrência:", qtd_recorrentes)
print("Tempo médio de fila:", round(tempo_medio_fila, 2), "minutos")
print("Tempo médio de atendimento:", round(tempo_medio_atendimento, 2), "minutos")
print("Maior tempo de atendimento:", round(maior_tempo_atendimento, 2), "minutos")


# 13) Removendo colunas que não serão usadas no Power BI
# Mesmo sendo base simulada, mantive a ideia de não usar campos desnecessários.
atendimentos = atendimentos.drop(columns=[
    "CPF entrada chat",
    "E-mail entrada chat",
    "Matrícula",
    "Observação",
    "Atendimento original",
    "Protocolo dependente"
])


# 14) Gerando apenas um arquivo CSV tratado
# Este será o arquivo usado no Power BI.
atendimentos.to_csv("dados_tratados/base_sac_tratada_powerbi.csv", sep=";", index=False, encoding="utf-8-sig")

print("\nArquivo tratado gerado com sucesso!")
print("Caminho: dados_tratados/base_sac_tratada_powerbi.csv")
