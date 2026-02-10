import streamlit as st
import pandas as pd
import csv
import matplotlib.pyplot as plt
import datetime
import os
from datetime import datetime, timedelta

# Caminho para o arquivo de dados
DATA_FILE = "aux/finanças.csv"

# Configurações
nossos_nomes = ['Bernardo', 'Alinne']
lista_cartoes = list(set([]))
with open('aux/cartões.csv', 'r', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        lista_cartoes.append(row['Cartão']) 

# Carregar dados existentes
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Data", "Tipo", "Descrição", "Valor", "Cartão", "Responsável", "Método", "Parcela", 
        "Total", "Dividido", "Data_Pagamento", "Final_Pagamento"
    ])

# Função para salvar dados
def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

# Função para calcular data de pagamento (evitar finais de semana)
def calcular_data_pagamento(data, dias_adiantados):
    data_pagamento = data + timedelta(days=dias_adiantados)
    while data_pagamento.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        data_pagamento += timedelta(days=1)
    return data_pagamento

# Título do app
st.title("Gestão de Finanças do 702")

# Sidebar para navegação
menu = st.sidebar.selectbox("Selecione uma opção", ["Adicionar Gasto", "Contas de Cartão", "Compras Parceladas", "Contas de Casa", "Análise de Divisão"])

# Seção 1: Adicionar Gasto (já está no código)
if menu == "Adicionar Gasto":
    st.header("Adicionar Gasto")
    col1, col2, col3 = st.columns(3)
    with col1:
        responsavel = st.segmented_control("Responsável", nossos_nomes, selection_mode="single")
    with col2:
        data = st.date_input("Data do gasto")
    with col3:
        tipo = st.selectbox("Tipo de gasto", ["Contas de Cartão", "Compras Parceladas", "Contas de Casa"])

    if tipo == "Contas de Cartão":
        st.subheader("Contas de Cartão")
        cartao = st.selectbox("Cartão", lista_cartoes)
        valor = st.number_input("Valor da conta", min_value=0.01)
        data_fatura_fecha = st.date_input("Data da fatura fecha")
        data_fatura_vence = st.date_input("Data da fatura vence")
        st.info(f"Cartão: {cartao} | Valor: R$ {valor:.2f} | Data da fatura: {data_fatura_fecha.strftime('%d/%m/%Y')}")

    elif tipo == "Compras Parceladas":
        st.subheader("Compras Parceladas")
        descricao = st.text_input("Descrição da compra")
        responsavel_compra = st.selectbox("Quem comprou?", nossos_nomes)
        metodo = st.selectbox("Método de pagamento", ["Crédito", "Pix"])
        if metodo == "Crédito":
            parcela = st.number_input("Número de parcelas", min_value=1, step=1)
            valor_parcela = st.number_input("Valor por parcela", min_value=0.01)
            total = valor_parcela * parcela
        else:
            total = st.number_input("Valor total (Pix)", min_value=0.01)
            parcela = ""
        data_compra = st.date_input("Data da compra")
        final_pagamento = calcular_data_pagamento(data_compra, parcela)
        st.info(f"Final de pagamento: {final_pagamento.strftime('%d/%m/%Y')}")

    elif tipo == "Contas de Casa":
        st.subheader("Contas de Casa")
        conta = st.text_input("Tipo de conta (ex: Aluguel, Luz, Internet)")
        valor_total = st.number_input("Valor total da conta", min_value=0.01)
        valor_cada = st.number_input("Valor por pessoa", min_value=0.01)
        data_pagamento = st.date_input("Data da conta (ajustada para não cair em fim de semana)")
        st.info(f"Valor por pessoa: R$ {valor_cada:.2f} | Data da conta: {data_pagamento.strftime('%d/%m/%Y')}")

    # Botão para salvar
    if st.button("Salvar Gasto"):
        nova_linha = {
            "Data": data.strftime("%Y-%m-%d"),
            "Tipo": tipo,
            "Descrição": descricao if tipo == "Compras Parceladas" else conta,
            "Valor": total if tipo == "Compras Parceladas" else valor_total,
            "Cartão": cartao if tipo == "Contas de Cartão" else "",
            "Responsável": responsavel_compra if tipo == "Compras Parceladas" else responsavel,
            "Método": metodo if tipo == "Compras Parceladas" else "",
            "Parcela": parcela if tipo == "Compras Parceladas" else "",
            "Total": total if tipo == "Compras Parceladas" else valor_cada,
            "Dividido": "Sim" if tipo == "Contas de Casa" else "Não",
            "Data_Pagamento": data_pagamento.strftime("%Y-%m-%d") if tipo == "Contas de Casa" else "",
            "Final_Pagamento": final_pagamento.strftime("%Y-%m-%d") if tipo == "Compras Parceladas" else ""
        }
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        salvar_dados(df)
        st.success("Gasto adicionado com sucesso!")

# Seção 2: Contas de Cartão
elif menu == "Contas de Cartão":
    st.header("Contas de Cartão")
    df_contas_cartao = df[df["Tipo"] == "Contas de Cartão"]
    st.dataframe(df_contas_cartao)
    st.metric("Total em cartões", f"R$ {df_contas_cartao['Valor'].sum():.2f}")

# Seção 3: Compras Parceladas
elif menu == "Compras Parceladas":
    st.header("Compras Parceladas")
    df_compras = df[df["Tipo"] == "Compras Parceladas"]
    st.dataframe(df_compras)
    st.metric("Total em compras parceladas", f"R$ {df_compras['Total'].sum():.2f}")

# Seção 4: Contas de Casa
elif menu == "Contas de Casa":
    st.header("Contas de Casa")
    df_contas_casa = df[df["Tipo"] == "Contas de Casa"]
    st.dataframe(df_contas_casa)
    st.metric("Total em contas de casa", f"R$ {df_contas_casa['Valor'].sum():.23f}")

# Seção 5: Análise de Divisão
else:
    st.header("Análise de Divisão de Gastos")
    df_divisao = df.groupby("Responsável")["Valor"].sum().reset_index()
    st.dataframe(df_divisao)
    st.metric("Total por pessoa", f"R$ {df_divisao['Valor'].sum():.2f}")
    st.bar_chart(df_divisao.set_index("Responsável"))
