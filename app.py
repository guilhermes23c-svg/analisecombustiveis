import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuração da página orientada para preenchimento e impressão
st.set_page_config(page_title="Emissor RAQ - Geranius", page_icon="⛽", layout="wide")

# --- CONEXÃO COM BANCO DE DADOS LOCAL ---
conn = sqlite3.connect("historico_geranius.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS raq_registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_registro TEXT,
    produto TEXT,
    volume INTEGER,
    data_coleta TEXT,
    hora_coleta TEXT,
    distribuidor TEXT,
    cnpj_distribuidor TEXT,
    transportador TEXT,
    cnpj_transportador TEXT,
    nf TEXT,
    placa TEXT,
    motorista TEXT,
    cpf_motorista TEXT,
    quimico TEXT,
    aspecto TEXT,
    cor TEXT,
    compartimento TEXT,
    temp_obs REAL,
    dens_obs REAL,
    dens_20 REAL,
    teor_etanol REAL,
    teor_alcoolico REAL
)
""")
conn.commit()

# --- DADOS FIXOS DO POSTO ---
POSTO_RAZAO = "Auto Posto Geranius Cafuba"
POSTO_CNPJ = "28.571.216/0001-26"
POSTO_ENDERECO = "AVN DOUTOR RAUL DE OLIVEIRA RODRIGUES 1691 - PIRATININGA, NITEROI-RJ"

# --- BANCO DE DADOS AUXILIAR ---
DISTRIBUIDORAS = {
    "MINUANO PETRÓLEO LTDA": "06.031.802/0001-45",
    "PARAPANEMA DISTRIBUIDORA DE COMBUSTIVIES": "05.411.176/0003-11"
}
TRANSPORTADORAS = {
    "HG TRANSPORTES E LOCAÇÕES LTDA": "58.341.459/0001-39",
    "TRANSJU TRANSPORTE LTDA": "20.324.242/0001-48"
}
MOTORISTAS = {
    "Marcelo Pereira Machado": "079.410.237-92",
    "Vitor Ferreira de Souza": "184.665.697-40",
    "Jhonny Avelino Gomes": "148.918.307-86",
    "Gleison dos Santos Feliciano": "204.419.987-47",
    "Davi Barbosa de Souza Felisberto": "162.519.537-05"
}
PLACAS = ["LRF-9973", "LRH-6994", "HKE-0D06", "LPV-4C13", "ASW-9C86"]
QUIMICOS = ["Miguel Antonio Alves  C.R.Q: 03212571", "Não Informado"]

# --- FUNÇÃO MATEMÁTICA DE CONVERSÃO DA ANP ---
def calcular_densidade_20(d_obs, temp, prod):
    if "Gas" in prod:
        alfa = 0.0012
    elif "Diesel" in prod:
        alfa = 0.00085
    else:
        alfa = 0.0011
    
    delta_t = temp - 20.0
    return round(d_obs / (1 - alfa * delta_t), 4)

# --- NAVEGAÇÃO POR ABAS NO APP ---
aba_cadastro, aba_historico = st.tabs(["📄 Gerar Ficha RAQ Atual", "📜 Histórico de Lançamentos"])

with aba_cadastro:
    st.title("⛽ Emissor de RAQ Automatizado")
    st.subheader(f"{POSTO_RAZAO} | CNPJ: {POSTO_CNPJ}")
    
    st.markdown("### 📋 1. Dados de Recebimento da Carga")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        produto = st.selectbox("Produto analisado:", ["Gas. Comum", "Gas. Adv", "Etanol", "Diesel S10"])
    with c2:
        volume = st.number_input("Volume Recebido (Litros)", value=5000, step=500)
    with c3:
        data_col = st.date_input("Data da Coleta", datetime.today())
    with c4:
        hora_col = st.text_input("Hora da Coleta", datetime.now().strftime("%H:%M:%S"))
        
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        dist = st.selectbox("Distribuidor:", list(DISTRIBUIDORAS.keys()))
        cnpj_dist = DISTRIBUIDORAS[dist]
    with c6:
        transp = st.selectbox("Transportador:", list(TRANSPORTADORAS.keys()))
        cnpj_transp = TRANSPORTADORAS[transp]
    with c7:
        nf_prod = st.text_input("Nota Fiscal do Produto", placeholder="Ex: 67374")
    with c8:
        placa_cam = st.selectbox("Placa do Caminhão:", PLACAS)

    c9, c10, c11 = st.columns(3)
    with c9:
        mot = st.selectbox("Nome do Motorista:", list(MOTORISTAS.keys()))
        cpf_mot = MOTORISTAS[mot]
    with c10:
        st.markdown(f"**CPF do Motorista:**  \\n`{cpf_mot}`")
    with c11:
        resp_quimico = st.selectbox("Analista / Químico de Origem:", QUIMICOS)

    st.markdown("### 🧪 2. Resultados Físicos Cadastrados (Laboratório)")
    c12, c13, c14, c15 = st.columns(4)
    with c12:
        aspecto = st.selectbox("Aspecto Visual:", ["Limpido", "Turvo", "Com impurezas"])
    with c13:
        cor_sugerida = "Amarelada" if "Comum" in produto else "Verde" if "Adv" in produto else "Incolor" if "Etanol" in produto else "Castanho"
        cor = st.text_input("Cor do Produto:", value=cor_sugerida)
    with c14:
        comp = st.text_input("Nº Compartimento", value="1")
    with c15:
        temp_obs = st.number_input("Temperatura Observada (°C)", min_value=0.0, max_value=50.0, value=25.0, step=0.1, format="%.1f")

    c16, c17, c18 = st.columns(3)
    with c16:
        dens_obs = st.number_input("Massa Específica Observada (g/mL)", min_value=0.7000, max_value=0.9000, value=0.7420, step=0.0001, format="%.4f")
    with c17:
        teor_etan = st.number_input("Teor de Etanol Anidro na Gasolina (%)", min_value=0.0, max_value=100.0, value=27.0 if "Gas" in produto else 0.0, step=0.5)
    with c18:
        teor_alc = st.number_input("Teor Alcoólico no Etanol (°INPM)", min_value=0.0, max_value=100.0, value=93.2 if "Etanol" in produto else 0.0, step=0.1)

    dens_20 = calcular_densidade_20(dens_obs, temp_obs, produto)

    st.divider()
    st.markdown("### 📄 Modelo da Ficha RAQ Pronta para Impressão")
    st.info("Pressione `Ctrl + P` no computador para enviar direto para a impressora do posto.")

    teor_texto = f"{teor_etan} %" if "Gas" in produto else f"{teor_alc} °INPM" if "Etanol" in produto else "---"
    data_formatada = data_col.strftime('%d/%m/%Y')

    st.markdown(f"""
    ---
    ### FORMULÁRIO DE REGISTRO DAS ANÁLISE DE QUALIDADE (RAQ)
    **RAZÃO SOCIAL DO POSTO:** {POSTO_RAZAO}  
    **CNPJ DO POSTO:** {POSTO_CNPJ}  
    **ENDEREÇO:** {POSTO_ENDERECO}  
    
    ---
    #### DADOS DE RECEBIMENTO
    * **Produto Selecionado:** {produto}
    * **Volume recebido:** {volume} L
    * **Data / Hora da coleta:** {data_formatada} às {hora_col}
    * **Distribuidor:** {dist} | CNPJ: {cnpj_dist}
    * **Transportador:** {transp} | CNPJ: {cnpj_transp}
    * **Nota Fiscal do Produto:** {nf_prod}
    * **Placa do Caminhão / Motorista:** {placa_cam} - {mot} (CPF: {cpf_mot})
    * **Analista de Origem:** {resp_quimico}
    
    ---
    #### RESULTADOS DAS ANÁLISES
    * **Aspecto Visual:** {aspecto}
    * **Cor:** {cor}
    * **Compartimento analisado:** {comp}
    * **Temperatura Observada:** {temp_obs} °C
    * **Massa Específica Observada:** {dens_obs} g/mL
    * **MASSA ESPECÍFICA CONVERTIDA À 20°C:** **{dens_20} g/mL**
    * **Teor de Etanol / Alcoólico:** {teor_texto}
    
    ---
    \\n\\n\\n
    <center>____________________________________________________</center>
    <center><strong>ASSINATURA DO RESPONSÁVEL DO POSTO</strong></center>
    """, unsafe_allow_html=True)

    if st.button("💾 Gravar e Arquivar Análise no Histórico", type="primary"):
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor.execute("""
            INSERT INTO raq_registros (data_registro, produto, volume, data_coleta, hora_coleta, distribuidor, cnpj_distribuidor, transportador, cnpj_transportador, nf, placa, motorista, cpf_motorista, quimico, aspecto, cor, compartimento, temp_obs, dens_obs, dens_20, teor_etanol, teor_alcoolico)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (agora, produto, volume, data_col.strftime('%Y-%m-%d'), hora_col, dist, cnpj_dist, transp, cnpj_transp, nf_prod, placa_cam, mot, cpf_mot, resp_quimico, aspecto, cor, comp, temp_obs, dens_obs, dens_20, teor_etan, teor_alc))
        conn.commit()
        st.toast("RAQ arquivada com sucesso!", icon="✅")

with aba_historico:
    st.markdown("### 📜 Consultar Registros Salvos Eletronicamente")
    df_busca = pd.read_sql_query("SELECT id as 'ID', data_registro as 'Data do Lançamento', produto as 'Combustível', volume as 'Volume (L)', nf as 'Nota Fiscal', motorista as 'Motorista', dens_20 as 'Densidade a 20°C' FROM raq_registros ORDER BY id DESC", conn)
    
    if not df_busca.empty:
        st.dataframe(df_busca, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum lançamento foi armazenado no banco local até o momento.")
