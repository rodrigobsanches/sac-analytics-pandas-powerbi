# Projeto: SAC Analytics
# Objetivo: tratar uma base de atendimentos usando Pandas
# Autor: Rodrigo Sanches

from pathlib import Path

import pandas as pd


# ==============================
# LENDO O ARQUIVO
# ==============================

pasta_dados_brutos = Path("dados_brutos")
pasta_dados_ficticios = Path("dados_ficticios")

arquivos_brutos = sorted(pasta_dados_brutos.glob("relatorio_atendimento_analitico*.csv"))

if arquivos_brutos:
    origem_dados = "brutos"
    arquivos_entrada = arquivos_brutos
else:
    arquivo_ficticio = pasta_dados_ficticios / "base_sac_ficticia.csv"

    if not arquivo_ficticio.exists():
        raise FileNotFoundError(
            "Nenhum arquivo CSV foi encontrado em dados_brutos/ e a base ficticia "
            "dados_ficticios/base_sac_ficticia.csv tambem nao existe."
        )

    origem_dados = "ficticios"
    arquivos_entrada = [arquivo_ficticio]


def ler_csv(arquivo):
    for encoding_arquivo in ["utf-8-sig", "latin1"]:
        try:
            base = pd.read_csv(arquivo, sep=";", encoding=encoding_arquivo)
            base.columns = base.columns.str.replace("\ufeff", "", regex=False).str.strip()
            return base
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError(
        "utf-8-sig/latin1",
        b"",
        0,
        1,
        f"Nao foi possivel ler o arquivo {arquivo} com as codificacoes esperadas."
    )


bases = [ler_csv(arquivo) for arquivo in arquivos_entrada]

atendimentos = pd.concat(bases, ignore_index=True)

print("Base carregada com sucesso!")
print(f"Origem dos dados: {origem_dados}")
print("Arquivos carregados:")
for arquivo in arquivos_entrada:
    print(f"- {arquivo}")
print("Tamanho da base:")
print(atendimentos.shape)

print("\nPrimeiras linhas:")
print(atendimentos.head())

print("\nInformações da base:")
print(atendimentos.info())

print("\nResumo dos dados numéricos:")
print(atendimentos.describe())


# ==============================
# TRATANDO CAMPOS VAZIOS
# ==============================

atendimentos.loc[atendimentos["Agente"].isnull(), "Agente"] = "Não informado"
atendimentos.loc[atendimentos["Recorrência"].isnull(), "Recorrência"] = "Sem recorrência"
atendimentos.loc[atendimentos["Observação"].isnull(), "Observação"] = "Sem observação"

# Alguns campos de data vieram com "-". Troquei por vazio para o Pandas conseguir tratar como data.
atendimentos.loc[atendimentos["Data de finalização"] == "-", "Data de finalização"] = ""
atendimentos.loc[atendimentos["Data de fila"] == "-", "Data de fila"] = ""


# ==============================
# TRATANDO DATAS
# ==============================

# Convertendo os campos de data. O errors="coerce" evita que o código pare se encontrar uma data inválida.
atendimentos["Data de Entrada"] = pd.to_datetime(
    atendimentos["Data de Entrada"],
    dayfirst=True,
    errors="coerce",
    format="mixed"
)

atendimentos["Data de Atendimento"] = pd.to_datetime(
    atendimentos["Data de Atendimento"],
    dayfirst=True,
    errors="coerce",
    format="mixed"
)

atendimentos["Data de fila"] = pd.to_datetime(
    atendimentos["Data de fila"],
    dayfirst=True,
    errors="coerce",
    format="mixed"
)

atendimentos["Data de finalização"] = pd.to_datetime(
    atendimentos["Data de finalização"],
    dayfirst=True,
    errors="coerce",
    format="mixed"
)


# Criando colunas novas a partir da data de entrada. Essas colunas ajudam na criação dos gráficos no Power BI.
atendimentos["Ano"] = atendimentos["Data de Entrada"].dt.year
atendimentos["Mes"] = atendimentos["Data de Entrada"].dt.month

# Criando o nome do mês para o gráfico ficar mais fácil.
atendimentos["Nome Mes"] = atendimentos["Mes"].replace({
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
})

atendimentos["Dia"] = atendimentos["Data de Entrada"].dt.day
atendimentos["Hora Entrada"] = atendimentos["Data de Entrada"].dt.hour

# Criando o dia da semana em português.
atendimentos["Ordem Dia Semana"] = atendimentos["Data de Entrada"].dt.weekday + 1

atendimentos["Dia da Semana"] = atendimentos["Ordem Dia Semana"].replace({
    1: "Segunda-feira",
    2: "Terça-feira",
    3: "Quarta-feira",
    4: "Quinta-feira",
    5: "Sexta-feira",
    6: "Sábado",
    7: "Domingo"
})


# ==============================
# TRATANDO TEMPOS
# ==============================

# Função para converter tempo em minutos.
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


# Aplicando a função nas colunas de tempo.
atendimentos["Tempo em Fila Minutos"] = atendimentos["Tempo em Fila"].apply(tempo_para_minutos)
atendimentos["Tempo de Atendimento Minutos"] = atendimentos["Tempo de Atendimento"].apply(tempo_para_minutos)
atendimentos["Tempo em Pendência Minutos"] = atendimentos["Tempo em Pendência"].apply(tempo_para_minutos)
atendimentos["TMIC Minutos"] = atendimentos["TMIC"].apply(tempo_para_minutos)
atendimentos["TMIA Minutos"] = atendimentos["TMIA"].apply(tempo_para_minutos)


# Criando uma coluna de tempo total. Aqui eu somei fila + atendimento + pendência.
atendimentos["Tempo Total Minutos"] = atendimentos.apply(
    lambda linha: linha["Tempo em Fila Minutos"] +
                  linha["Tempo de Atendimento Minutos"] +
                  linha["Tempo em Pendência Minutos"],
    axis=1
)


# ==============================
# TRATANDO STATUS E RECORRÊNCIA
# ==============================

# Verificando se o atendimento foi finalizado.
atendimentos["Finalizado"] = atendimentos["Status"].str.contains("Finalizado", na=False)

atendimentos["Situação Finalização"] = atendimentos["Finalizado"].replace({
    True: "Finalizado",
    False: "Em aberto"
})


# Verificando se existe recorrência.
atendimentos["Possui Recorrência"] = atendimentos["Recorrência"].isin([
    "Recorrente",
    "Reincidente",
    "Rechamada"
])

atendimentos["Situação Recorrência"] = atendimentos["Possui Recorrência"].replace({
    True: "Com recorrência",
    False: "Sem recorrência"
})


# ==============================
# TRATANDO FAIXAS DE TEMPO
# ==============================

# Criando uma classificação simples para o tempo em fila.
atendimentos.loc[atendimentos["Tempo em Fila Minutos"] <= 5, "Faixa Fila"] = "Até 5 minutos"

atendimentos.loc[
    (atendimentos["Tempo em Fila Minutos"] > 5) &
    (atendimentos["Tempo em Fila Minutos"] <= 30),
    "Faixa Fila"
] = "De 6 a 30 minutos"

atendimentos.loc[
    atendimentos["Tempo em Fila Minutos"] > 30,
    "Faixa Fila"
] = "Acima de 30 minutos"

# Criando uma ordem para aparecer corretamente no Power BI.
atendimentos["Ordem Faixa Fila"] = atendimentos["Faixa Fila"].map({
    "Até 5 minutos": 1,
    "De 6 a 30 minutos": 2,
    "Acima de 30 minutos": 3
})


# Criando uma classificação simples para o tempo de atendimento.
atendimentos.loc[atendimentos["Tempo de Atendimento Minutos"] <= 15, "Faixa Atendimento"] = "Até 15 minutos"

atendimentos.loc[
    (atendimentos["Tempo de Atendimento Minutos"] > 15) &
    (atendimentos["Tempo de Atendimento Minutos"] <= 60),
    "Faixa Atendimento"
] = "De 16 a 60 minutos"

atendimentos.loc[
    atendimentos["Tempo de Atendimento Minutos"] > 60,
    "Faixa Atendimento"
] = "Acima de 60 minutos"

# Criando uma ordem para aparecer corretamente no Power BI.
atendimentos["Ordem Faixa Atendimento"] = atendimentos["Faixa Atendimento"].map({
    "Até 15 minutos": 1,
    "De 16 a 60 minutos": 2,
    "Acima de 60 minutos": 3
})


# ==============================
# FILTRANDO DADOS
# ==============================

# Filtro dos atendimentos finalizados.
atendimentos_finalizados = atendimentos[
    atendimentos["Status"].str.contains("Finalizado", na=False)
]

# Filtro dos atendimentos com fila maior que 30 minutos.
atendimentos_com_fila_alta = atendimentos[
    atendimentos["Tempo em Fila Minutos"] > 30
]

# Filtro dos atendimentos com recorrência.
atendimentos_recorrentes = atendimentos[
    atendimentos["Recorrência"].isin(["Recorrente", "Reincidente", "Rechamada"])
]

print("\nAtendimentos finalizados:")
print(len(atendimentos_finalizados.index))

print("\nAtendimentos com fila acima de 30 minutos:")
print(len(atendimentos_com_fila_alta.index))

print("\nAtendimentos com recorrência:")
print(len(atendimentos_recorrentes.index))


# ==============================
# AGRUPANDO DADOS
# ==============================

# Esses agrupamentos ajudam a conferir se os dados fazem sentido.
print("\nAtendimentos por serviço:")
print(atendimentos.groupby("Serviço")["Protocolo"].count())

print("\nTempo médio de atendimento por serviço:")
print(atendimentos.groupby("Serviço")["Tempo de Atendimento Minutos"].mean())

print("\nAtendimentos por status:")
print(atendimentos.groupby("Status")["Protocolo"].count())


# ==============================
# TRATANDO KPIs
# ==============================

# KPIs principais usados no projeto e no dashboard.
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


# ==============================
# REMOVENDO COLUNAS
# ==============================

# Removendo colunas que não serão usadas no dashboard.
# Usei errors="ignore" para evitar erro caso alguma coluna não exista.
atendimentos = atendimentos.drop(columns=[
    "CPF entrada chat",
    "E-mail entrada chat",
    "Matrícula",
    "Observação",
    "Atendimento original",
    "Protocolo dependente"
], errors="ignore")

if "Contato" not in atendimentos.columns:
    atendimentos["Contato"] = "Não informado"
if "Canal" not in atendimentos.columns:
    atendimentos["Canal"] = "Whatsapp"    


# ==============================
# GERANDO PROJECAO ESTATISTICA
# ==============================

# A projecao fica em um arquivo separado para nao interferir nos graficos
# categoricos da base real, como status, faixa de fila e recorrencia.
atendimentos["Tipo Registro"] = "Real"
projecao_atendimentos = pd.DataFrame()
curva_projecao_atendimentos = pd.DataFrame()

dias_projecao = 30
data_maxima = atendimentos["Data de Entrada"].max()

if pd.notnull(data_maxima):
    atendimentos_por_dia = (
        atendimentos
        .groupby(atendimentos["Data de Entrada"].dt.date)
        .size()
        .sort_index()
    )

    media_movel_30_dias = atendimentos_por_dia.tail(30).mean()
    media_por_dia_semana = atendimentos.groupby("Ordem Dia Semana").size()
    media_geral_dia_semana = media_por_dia_semana.mean()
    distribuicao_servico = atendimentos["Serviço"].value_counts(normalize=True)

    nomes_meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    nomes_dias_semana = {
        1: "Segunda-feira",
        2: "Terça-feira",
        3: "Quarta-feira",
        4: "Quinta-feira",
        5: "Sexta-feira",
        6: "Sábado",
        7: "Domingo"
    }

    def calcular_projecao_por_servico(qtd_projetada):
        projecao_por_servico = (distribuicao_servico * qtd_projetada).round().astype(int)
        diferenca = qtd_projetada - projecao_por_servico.sum()

        if diferenca != 0:
            servico_principal = projecao_por_servico.idxmax()
            projecao_por_servico.loc[servico_principal] += diferenca

        return projecao_por_servico

    def calcular_qtd_projetada(data_referencia):
        ordem_dia_semana = data_referencia.weekday() + 1
        fator_dia_semana = 1

        if media_geral_dia_semana > 0 and ordem_dia_semana in media_por_dia_semana.index:
            fator_dia_semana = media_por_dia_semana.loc[ordem_dia_semana] / media_geral_dia_semana

        qtd_projetada = round(media_movel_30_dias * fator_dia_semana)

        return max(1, int(qtd_projetada))

    linhas_projecao = []
    linhas_curva_projecao = []

    data_inicio_curva = data_maxima.replace(day=1)
    data_fim_curva = data_maxima + pd.Timedelta(days=dias_projecao)

    for data_curva in pd.date_range(data_inicio_curva, data_fim_curva, freq="D"):
        ordem_dia_semana = data_curva.weekday() + 1
        qtd_projetada = calcular_qtd_projetada(data_curva)
        projecao_por_servico = calcular_projecao_por_servico(qtd_projetada)

        for servico, atendimentos_projetados in projecao_por_servico.items():
            if atendimentos_projetados <= 0:
                continue

            linhas_curva_projecao.append({
                "Data Projecao": data_curva,
                "Serviço": servico,
                "Atendimentos Projetados": int(atendimentos_projetados),
                "Tipo Registro": "Curva Esperada",
                "Ano": data_curva.year,
                "Mes": data_curva.month,
                "Nome Mes": nomes_meses[data_curva.month],
                "Dia": data_curva.day,
                "Ordem Dia Semana": ordem_dia_semana,
                "Dia da Semana": nomes_dias_semana[ordem_dia_semana],
                "Metodo Projecao": "Media movel 30 dias ajustada por dia da semana"
            })

    for numero_dia in range(1, dias_projecao + 1):
        data_projetada = data_maxima + pd.Timedelta(days=numero_dia)
        ordem_dia_semana = data_projetada.weekday() + 1

        qtd_projetada = calcular_qtd_projetada(data_projetada)
        projecao_por_servico = calcular_projecao_por_servico(qtd_projetada)

        for servico, atendimentos_projetados in projecao_por_servico.items():
            if atendimentos_projetados <= 0:
                continue

            linhas_projecao.append({
                "Data Projecao": data_projetada,
                "Serviço": servico,
                "Atendimentos Projetados": int(atendimentos_projetados),
                "Tipo Registro": "Projecao Estatistica",
                "Ano": data_projetada.year,
                "Mes": data_projetada.month,
                "Nome Mes": nomes_meses[data_projetada.month],
                "Dia": data_projetada.day,
                "Ordem Dia Semana": ordem_dia_semana,
                "Dia da Semana": nomes_dias_semana[ordem_dia_semana],
                "Metodo Projecao": "Media movel 30 dias ajustada por dia da semana"
            })

    if linhas_projecao:
        projecao_atendimentos = pd.DataFrame(linhas_projecao)

        print("\nProjecao estatistica gerada:")
        print("Dias projetados:", dias_projecao)
        print("Linhas no arquivo de projecao:", len(projecao_atendimentos.index))
        print("Total de atendimentos projetados:", projecao_atendimentos["Atendimentos Projetados"].sum())

    if linhas_curva_projecao:
        curva_projecao_atendimentos = pd.DataFrame(linhas_curva_projecao)


# ==============================
# PREPARANDO TABELAS PARA POWER BI
# ==============================

atendimentos["Data Entrada Apenas Data"] = atendimentos["Data de Entrada"].dt.normalize()
atendimentos["Ano Mes"] = atendimentos["Data de Entrada"].dt.strftime("%Y-%m")
atendimentos["AnoMes Ordem"] = (
    atendimentos["Data de Entrada"].dt.year * 100 +
    atendimentos["Data de Entrada"].dt.month
)
atendimentos["Total Atendimentos"] = 1

if not projecao_atendimentos.empty:
    projecao_atendimentos["Data Projecao"] = pd.to_datetime(projecao_atendimentos["Data Projecao"])
    projecao_atendimentos["Data Projecao Apenas Data"] = projecao_atendimentos["Data Projecao"].dt.normalize()
    projecao_atendimentos["Ano Mes"] = projecao_atendimentos["Data Projecao"].dt.strftime("%Y-%m")
    projecao_atendimentos["AnoMes Ordem"] = (
        projecao_atendimentos["Data Projecao"].dt.year * 100 +
        projecao_atendimentos["Data Projecao"].dt.month
    )
else:
    projecao_atendimentos = pd.DataFrame(columns=[
        "Data Projecao",
        "Data Projecao Apenas Data",
        "Serviço",
        "Atendimentos Projetados",
        "Tipo Registro",
        "Ano",
        "Mes",
        "Nome Mes",
        "Ano Mes",
        "AnoMes Ordem",
        "Dia",
        "Ordem Dia Semana",
        "Dia da Semana",
        "Metodo Projecao"
    ])

if not curva_projecao_atendimentos.empty:
    curva_projecao_atendimentos["Data Projecao"] = pd.to_datetime(
        curva_projecao_atendimentos["Data Projecao"]
    )
    curva_projecao_atendimentos["Data Projecao Apenas Data"] = (
        curva_projecao_atendimentos["Data Projecao"].dt.normalize()
    )
else:
    curva_projecao_atendimentos = pd.DataFrame(columns=[
        "Data Projecao",
        "Data Projecao Apenas Data",
        "Serviço",
        "Atendimentos Projetados",
        "Tipo Registro",
        "Ano",
        "Mes",
        "Nome Mes",
        "Dia",
        "Ordem Dia Semana",
        "Dia da Semana",
        "Metodo Projecao"
    ])

servicos_reais = atendimentos[["Serviço"]]
servicos_projetados = projecao_atendimentos[["Serviço"]]
dim_servico = (
    pd.concat([servicos_reais, servicos_projetados], ignore_index=True)
    .dropna()
    .drop_duplicates()
    .sort_values("Serviço")
    .reset_index(drop=True)
)

data_inicio_calendario = atendimentos["Data Entrada Apenas Data"].min()
data_fim_calendario = atendimentos["Data Entrada Apenas Data"].max()

if not projecao_atendimentos.empty:
    data_fim_calendario = max(
        data_fim_calendario,
        projecao_atendimentos["Data Projecao Apenas Data"].max()
    )

dim_calendario = pd.DataFrame({
    "Data": pd.date_range(data_inicio_calendario, data_fim_calendario, freq="D")
})
dim_calendario["Ano"] = dim_calendario["Data"].dt.year
dim_calendario["Mes"] = dim_calendario["Data"].dt.month
dim_calendario["Nome Mes"] = dim_calendario["Mes"].replace(nomes_meses)
dim_calendario["Ano Mes"] = dim_calendario["Data"].dt.strftime("%Y-%m")
dim_calendario["AnoMes Ordem"] = (
    dim_calendario["Data"].dt.year * 100 +
    dim_calendario["Data"].dt.month
)
dim_calendario["Dia"] = dim_calendario["Data"].dt.day
dim_calendario["Ordem Dia Semana"] = dim_calendario["Data"].dt.weekday + 1
dim_calendario["Dia da Semana"] = dim_calendario["Ordem Dia Semana"].replace(nomes_dias_semana)

evolucao_real = (
    atendimentos
    .groupby(["Data Entrada Apenas Data", "Serviço"], as_index=False)
    .size()
    .rename(columns={
        "Data Entrada Apenas Data": "Data",
        "size": "Atendimentos Reais"
    })
)

evolucao_projecao = (
    curva_projecao_atendimentos
    .groupby(["Data Projecao Apenas Data", "Serviço"], as_index=False)["Atendimentos Projetados"]
    .sum()
    .rename(columns={"Data Projecao Apenas Data": "Data"})
)

evolucao_atendimentos = pd.merge(
    evolucao_real,
    evolucao_projecao,
    on=["Data", "Serviço"],
    how="outer"
)
evolucao_atendimentos["Atendimentos Reais"] = (
    evolucao_atendimentos["Atendimentos Reais"].fillna(0).astype(int)
)
evolucao_atendimentos["Atendimentos Projetados"] = (
    evolucao_atendimentos["Atendimentos Projetados"].fillna(0).astype(int)
)
evolucao_atendimentos["Atendimentos Total Com Projecao"] = (
    evolucao_atendimentos["Atendimentos Reais"] +
    evolucao_atendimentos["Atendimentos Projetados"]
)
evolucao_atendimentos = evolucao_atendimentos.merge(
    dim_calendario,
    on="Data",
    how="left"
)
evolucao_atendimentos = evolucao_atendimentos[[
    "Data",
    "Ano",
    "Mes",
    "Nome Mes",
    "Ano Mes",
    "AnoMes Ordem",
    "Dia",
    "Ordem Dia Semana",
    "Dia da Semana",
    "Serviço",
    "Atendimentos Reais",
    "Atendimentos Projetados",
    "Atendimentos Total Com Projecao"
]]



# ==============================
# GERANDO O ARQUIVO FINAL
# ==============================

# Gerando o Excel consolidado que será importado no Power BI.
with pd.ExcelWriter("dados_tratados/sac_analytics_powerbi.xlsx", engine="openpyxl") as arquivo_excel:
    atendimentos.to_excel(arquivo_excel, sheet_name="Base_Real", index=False)
    projecao_atendimentos.to_excel(arquivo_excel, sheet_name="Projecao", index=False)
    evolucao_atendimentos.to_excel(arquivo_excel, sheet_name="Evolucao", index=False)
    dim_servico.to_excel(arquivo_excel, sheet_name="Dim_Servico", index=False)
    dim_calendario.to_excel(arquivo_excel, sheet_name="Dim_Calendario", index=False)

print("\nArquivo tratado gerado com sucesso!")
print("Caminho do Excel para Power BI: dados_tratados/sac_analytics_powerbi.xlsx")
