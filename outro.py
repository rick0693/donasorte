

import requests
import time
import pytz
from dateutil import parser
import sqlite3
import pandas as pd
from itertools import product
import streamlit as st

st.set_page_config(layout="wide")

def destacar_ocorrencia_zero(val):
    if val == 0:
        return 'background-color: green'
    else:
        return ''

# Defina a função para exibir o DataFrame com o estilo aplicado
def exibir_dataframe_com_estilo(df, slot):
    styled_df = df.style.applymap(destacar_ocorrencia_zero, subset='occurrence')
    slot.dataframe(styled_df)


# Display the resulting DataFrames using st.empty()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.header("DataFrame future_df:")
    empty_slot1 = st.empty()

with col2:
    st.header("DataFrame Cores_branco:")
    empty_slot2 = st.empty()

with col3:
    st.header("DataFrame Cores_vermelho:")
    empty_slot3 = st.empty()

with col4:
    st.header("DataFrame Cores_preto:")
    empty_slot4 = st.empty()



col5, col6, col7,col8= st.columns(4)
saldo_saldo = col5.empty()
Cor_sorteada = col6.empty()
Numero_sorteado = col7.empty()
Dica = col8.empty()


col10, col11, col12,col13= st.columns(4)
primeiro = col10.empty()
segundo = col11.empty()
terceiro = col12.empty()
quarta = col13.empty()

col14, col15, col16,col17= st.columns(4)
quatorze = col14.empty()
quinze = col15.empty()
dezesseis = col16.empty()
dezesete = col17.empty()

message_slot = st.empty()

def fetch_recent_data():
    try:
        response = requests.get("https://blaze.com/api/roulette_games/recent")
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        sorted_data = sorted(data, key=lambda x: x['created_at'], reverse=True)        
        return sorted_data
    except requests.exceptions.RequestException as e:
        message_slot.error("Error in the request: " + str(e))
        return None

# Function to convert UTC time to Brasilia time
def convert_to_brasilia_time(created_at):
    fuso_horario_utc = pytz.timezone('UTC')
    fuso_horario_brasilia = pytz.timezone('America/Sao_Paulo')
    horario_utc = parser.isoparse(created_at)
    horario_utc = horario_utc.replace(tzinfo=fuso_horario_utc)
    horario_brasilia = horario_utc.astimezone(fuso_horario_brasilia)
    return horario_brasilia.strftime("%Y-%m-%d %H:%M:%S")

# Function to create the table if it doesn't exist in the database
def create_table_if_not_exists():
    conexao = sqlite3.connect("dados.db")
    cursor = conexao.cursor()

    # Define the table structure
    create_table_query = """
    CREATE TABLE IF NOT EXISTS dados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        color1 TEXT,
        color2 TEXT,
        color3 TEXT,
        color4 TEXT,
        numero1 INTEGER,
        numero2 INTEGER,
        numero3 INTEGER,
        numero4 INTEGER,
        server_seed TEXT,
        created_at TEXT
    );
    """
    cursor.execute(create_table_query)
    conexao.commit()
    conexao.close()

# Function to check if the server_seed already exists in the database
def is_server_seed_exists(server_seed):
    conexao = sqlite3.connect("dados.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) FROM dados WHERE server_seed=?", (server_seed,))
    count = cursor.fetchone()[0]
    conexao.close()
    return count > 0

# Function to save data in the database and analyze/predict sequences
def save_data_and_analyze(dados_api):
    novo_server_seed = dados_api[0]["server_seed"]
    if is_server_seed_exists(novo_server_seed):
        st.warning("Duplicated data, not stored.")
        return

    color1, color2, color3, color4, color5, color6 = [d["color"] for d in dados_api[:6]]
    numero1, numero2, numero3, numero4, numero5, numero6 = [d["roll"] for d in dados_api[:6]]
    horario_brasilia = convert_to_brasilia_time(dados_api[0]["created_at"])

    conexao = sqlite3.connect("dados.db")
    cursor = conexao.cursor()

    # Insert the data into the table
    insert_data_query = """
    INSERT INTO dados (color1, color2, color3, color4, numero1, numero2, numero3, numero4, server_seed, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insert_data_query, (color1, color2, color3, color4, numero1, numero2, numero3, numero4, novo_server_seed, horario_brasilia))

    conexao.commit()
    conexao.close()

    # Analyze and predict sequences after obtaining new data
    analyze_and_predict_sequences(color1, numero1, novo_server_seed, horario_brasilia)

   
def get_color_prediction(percentage_contagem_vermelho, percentage_black_occurrences):
    if percentage_contagem_vermelho > percentage_black_occurrences:
        return 1
    elif percentage_black_occurrences > percentage_contagem_vermelho:
        return 2
    else:
        return 0

df_final = pd.DataFrame()
def analyze_and_predict_sequences(color1, numero1, novo_server_seed, horario_brasilia):
    # Conectar ao banco de dados e ler os dados
    conexao = sqlite3.connect("dados.db")
    df = pd.read_sql_query("SELECT numero1, numero2, numero3, numero4 FROM dados", conexao)
    conexao.close()

    # Restaurar o índice a cada rodada

    # Obter a última sequência de números
    ultima_sequência = df.iloc[-1].values.tolist()
    ultima_sequência_str = ",".join(map(str, ultima_sequência))

    # Exibir as métricas usando as funções saldo_saldo, Cor_sorteada, Numero_sorteado, primeiro, segundo, terceiro, quarta, quatorze, quinze, dezesseis, dezesete
    saldo_saldo.metric("4 Ultimos resultados", ultima_sequência_str)
    Cor_sorteada.metric("Cor sorteada", color1)
    Numero_sorteado.metric("Numero sorteado", ultima_sequência[0])

    primeiro.metric("4 Ultimos resultados", ultima_sequência_str)
    segundo.metric("Cor sorteada", color1)
    terceiro.metric("Numero sorteado", ultima_sequência[0])
    quarta.metric("Salvação", ultima_sequência_str)

    quatorze.metric("4 Ultimos resultados", ultima_sequência_str)
    quinze.metric("Cor sorteada", color1)
    dezesseis.metric("Numero sorteado", ultima_sequência[0])
    dezesete.metric("Salvação", ultima_sequência_str)

    # Contar quantas vezes essa sequência ocorreu nas colunas 'numero1', 'numero2', 'numero3', 'numero4' do banco de dados
    contagem_de_ocorrencias = df[df[df.columns].eq(ultima_sequência).all(1)].shape[0]
    Cor_sorteada.metric("Quantidade de vezes", contagem_de_ocorrencias)

    # Simular a sequência com o quarto número variando de 0 a 14
    all_possible_numbers = list(range(15))
    sequences = list(product(all_possible_numbers, [ultima_sequência[0]], [ultima_sequência[1]], [ultima_sequência[2]]))
    future_df = pd.DataFrame(sequences, columns=['numero0', 'numero1', 'numero2', 'numero3'])

    # Contar quantas vezes cada sequência em future_df ocorreu nas colunas 'numero1', 'numero2', 'numero3', 'numero4' do banco de dados
    future_contagem_de_ocorrencias = []
    for seq in sequences:
        occurrence_count = df[df[df.columns].eq(seq).all(1)].shape[0]
        future_contagem_de_ocorrencias.append(occurrence_count)

    future_df['occurrence'] = future_contagem_de_ocorrencias

    # Contar ocorrências de 0 no DataFrame Cores_vermelho e DataFrame Cores_preto
    contagem_vermelho = future_df[future_df['numero0'].isin(range(1, 8))]['occurrence'].value_counts().get(0, 0)
    black_occurrences = future_df[future_df['numero0'].isin(range(8, 16))]['occurrence'].value_counts().get(0, 0)

    primeiro.metric("Quantidade de 0 em Cores_vermelho:", contagem_vermelho)
    segundo.metric("Quantidade de 0 em Cores_preto:", black_occurrences)

    # Calcular a porcentagem de ocorrências de 0 a 14 no DataFrame Cores_vermelho e DataFrame Cores_preto
    total_contagem_vermelho = future_df[future_df['numero0'].isin(range(1, 7))]['occurrence'].sum()
    total_black_occurrences = future_df[future_df['numero0'].isin(range(8, 15))]['occurrence'].sum()

    percentage_contagem_vermelho = (contagem_vermelho / 14) * 100 if total_contagem_vermelho > 0 else 0
    percentage_black_occurrences = (black_occurrences / 14) * 100 if total_black_occurrences > 0 else 0

    terceiro.metric("Porcentagem de 0 em Cores_vermelho:", f"{percentage_contagem_vermelho:.2f}%")
    quarta.metric("Porcentagem de 0 em Cores_preto:", f"{percentage_black_occurrences:.2f}%")

    # Dividir future_df em três partes com base nos valores de numero0
    Cores_branco = future_df.loc[future_df['numero0'] == 0]
    Cores_vermelho = future_df.loc[(future_df['numero0'] >= 1) & (future_df['numero0'] <= 7)]
    Cores_preto = future_df.loc[future_df['numero0'] >= 8]

    # Comparar a quantidade de ocorrências de 0 em Cores_vermelho e Cores_preto
    if contagem_vermelho > black_occurrences:
        comparison_result = 1
    elif black_occurrences > contagem_vermelho:
        comparison_result = 2
    else:
        comparison_result = color1

    Dica.metric("Dica", comparison_result)



    # Exibir os DataFrames resultantes usando as funções exibir_dataframe_com_estilo e os slots vazios (empty_slot1, empty_slot2, empty_slot3, empty_slot4)
    exibir_dataframe_com_estilo(future_df, empty_slot1)
    exibir_dataframe_com_estilo(Cores_branco, empty_slot2)
    exibir_dataframe_com_estilo(Cores_vermelho, empty_slot3)
    exibir_dataframe_com_estilo(Cores_preto, empty_slot4)

    # Salvar as variáveis para uso posterior
    color1 = color1
    numero1 = ultima_sequência[0]
    novo_server_seed = novo_server_seed
    horario_brasilia = horario_brasilia
    contagem_de_ocorrencias = future_df.loc[future_df['occurrence'] == 0].shape[0]

    # Calcular novamente a contagem de ocorrências de 0 em Cores_vermelho e Cores_preto
    contagem_vermelho = future_df[future_df['numero0'].isin(range(1, 8))]['occurrence'].value_counts().get(0, 0)
    black_occurrences = future_df[future_df['numero0'].isin(range(8, 16))]['occurrence'].value_counts().get(0, 0)

    # Calcular novamente a porcentagem de ocorrências de 0 a 14 no DataFrame Cores_vermelho e DataFrame Cores_preto
    percentage_contagem_vermelho = (contagem_vermelho / 14) * 100 if total_contagem_vermelho > 0 else 0
    percentage_black_occurrences = (black_occurrences / 14) * 100 if total_black_occurrences > 0 else 0

    # Atualizar a variável comparison_result se necessário
    comparison_result = comparison_result

    # Criar um DataFrame temporário com os resultados das métricas
    global df_final
    df_temp = pd.DataFrame({
        "color1": color1,
        "numero1": numero1,
        "Dica": comparison_result,
        "Resultado": None,
        "horario_brasilia": horario_brasilia,
        "contagem_vermelho": contagem_vermelho,
        "contagem_preto": black_occurrences,
        "percentage_contagem_vermelho": percentage_contagem_vermelho,
        "percentage_contagem_preto": percentage_black_occurrences,
        "vazio15": novo_server_seed
    }, index=[0])

    # Concatenar df_final com o DataFrame temporário
    df_final = pd.concat([df_final, df_temp], ignore_index=True)

    # Ordenar o DataFrame df_final em ordem decrescente com base na coluna "horario_brasilia"
    df_final.sort_values(by='horario_brasilia', ascending=False, inplace=True)

    # Restaurar o índice após a ordenação
    df_final.reset_index(drop=True, inplace=True)

    ultimo_color1 = df_final['color1'].iloc[-1]

    # Verificar se o penúltimo resultado da coluna "Dica" é igual ao último color1, ou definir resultado como "Indefinido" se penultimo_dica for None
    if not df_final.empty and len(df_final) >= 2:
        penultimo_dica = df_final['Dica'].iloc[-2]
        if penultimo_dica  == ultimo_color1:
            resultado = "Ganhou"
        else:
            resultado = "Perdeu"


    # Atribuir o resultado à coluna "Resultado"
    if not df_final.empty and len(df_final) >= 2:
        df_final.loc[df_final.index[-2], 'Resultado'] = resultado

    # Escrever o DataFrame final na saída
    message_slot.write(df_final)

    return future_df, Cores_branco, Cores_vermelho, Cores_preto, df_final


def check_server_seed():
    create_table_if_not_exists()
    previous_server_seed = ''
    request_count_in_round = 0
    initial_data_obtained = False

    while True:
        try:
            data = fetch_recent_data()
            request_count_in_round += 1

            if not initial_data_obtained:
                # If the initial data has not been obtained yet, make requests every second
                if data:
                    message_slot.success("Initial data obtained!")
                    save_data_and_analyze(data)
                    previous_server_seed = data[0]["server_seed"]
                    initial_data_obtained = True

            else:
                # If we have obtained the initial data, wait 28 seconds after obtaining new data
                if data and data[0]["server_seed"] != previous_server_seed:
                    message_slot.success(f"New data obtained! Requests made in this round: {request_count_in_round}")
                    save_data_and_analyze(data)
                    previous_server_seed = data[0]["server_seed"]
                    request_count_in_round = 0

                    time.sleep(28)  # Wait 28 seconds before making the next request

        except requests.exceptions.RequestException as e:
            message_slot.error("Error in the request: " + str(e))

        time.sleep(1)

def main():
    check_server_seed()

if __name__ == '__main__':
    main()