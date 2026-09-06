import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuração da página orientada para preenchimento
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

# --- 1. MOTOR DE CONVERSÃO EXATA (PADRÃO ANP) ---
def calcular_densidade_20_exata(d_obs, temp, prod):
    if "Etanol" in prod:
        alfa = 0.00086
    elif "Gas" in prod:
        alfa = 0.00122
    else:
        alfa = 0.00085
    
    delta_t = temp - 20.0
    dens_20 = d_obs + (alfa * delta_t)
    return round(dens_20, 4)

# --- 2. TABELA DE BUSCA DE INPM EXATA (NBR 5992) ---
def buscar_inpm_na_tabela(dens_20):
    tabela_inpm = {
        0.8113: 92.5, 0.8110: 92.6, 0.8107: 92.7, 0.8104: 92.8, 0.8101: 92.9,
        0.8098: 93.0, 0.8094: 93.1, 0.8091: 93.2, 0.8088: 93.3, 0.8085: 93.4,
        0.8082: 93.5, 0.8079: 93.6, 0.8076: 93.7, 0.8072: 93.8, 0.8069: 93.9,
        0.8066: 94.0, 0.8063: 94.1, 0.8060: 94.2, 0.8057: 94.3, 0.8053: 94.4,
        0.8050: 94.5, 0.8047: 94.6, 0.8044: 94.7, 0.8041: 94.8, 0.8038: 94.9,
        0.8035: 95.0, 0.8031: 95.1, 0.8028: 95.2, 0.8025: 95.3, 0.8022: 95.4
    }
    if dens_20 in tabela_inpm:
        return tabela_inpm[dens_20]
    else:
        dens_proxima = min(tabela_inpm.keys(), key=lambda k: abs(k - dens_20))
        return tabela_inpm[dens_proxima]

# --- NAVEGAÇÃO POR ABAS NO APP ---
aba_cadastro, aba_historico = st.tabs(["📄 Lançar Nova Análise", "📜 Histórico de Lançamentos"])

with aba_cadastro:
    st.title("⛽ Lançamento de Análises de Combustível")
    st.subheader(f"{POSTO_RAZAO}")
    
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
        st.markdown(f"**CPF do Motorista:** <br>`{cpf_mot}`", unsafe_allow_html=True)
    with c11:
        resp_quimico = st.selectbox("Analista / Químico de Origem:", QUIMICOS)

    st.markdown("### 🧪 2. Resultados Físicos Cadastrados (Laboratório)")
    
    c12, c13, c14 = st.columns(3)
    with c12:
        aspecto = st.selectbox("Aspecto Visual:", ["Limpido", "Turvo", "Com impurezas"])
    with c13:
        cor_sugerida = "Amarelada" if "Comum" in produto else "Verde" if "Adv" in produto else "Incolor" if "Etanol" in produto else "Castanho"
        cor = st.text_input("Cor do Produto:", value=cor_sugerida)
    with c14:
        comp = st.text_input("Nº Compartimento", value="1")

    st.markdown("#### 🌡️ Termodensimetria (Informe o que está na proveta)")
    c15, c16 = st.columns(2)
    with c15:
        temp_obs = st.number_input("Temperatura Observada (°C)", min_value=10.0, max_value=40.0, value=25.0, step=0.5, format="%.1f")
    with c16:
        val_dens = 0.8048 if "Etanol" in produto else 0.7400 if "Gas" in produto else 0.8400
        dens_obs = st.number_input("Massa Específica Observada (g/mL)", min_value=0.7000, max_value=0.9000, value=val_dens, step=0.0005, format="%.4f")

    dens_20 = calcular_densidade_20_exata(dens_obs, temp_obs, produto)

    st.markdown("#### ⚙️ Teores Calculados (Automático)")
    c17, c18 = st.columns(2)
    
    teor_etan = 0.0
    teor_alc = 0.0

    if "Etanol" in produto:
        teor_alc = buscar_inpm_na_tabela(dens_20)
        with c17:
            st.info(f"**Densidade Convertida a 20°C:**\n\n {dens_20} g/mL")
        with c18:
            st.success(f"**Teor Alcoólico (Tabela NBR 5992):**\n\n {teor_alc} °INPM")
            
    elif "Gas" in produto:
        with c17:
            vol_aquoso = st.number_input("Leitura da Fase Aquosa na Proveta (mL)", value=63.5, step=0.5)
            teor_etan = ((vol_aquoso - 50) * 2) + 1
        with c18:
            st.success(f"**Dens. 20°C:** {dens_20} g/mL \n\n **Teor de Etanol Anidro:** {teor_etan} %")
            
    else: 
        with c17:
            st.info(f"**Densidade Convertida a 20°C:**\n\n {dens_20} g/mL")

    st.divider()

    if st.button("💾 Gravar e Arquivar Análise no Histórico", type="primary"):
        if not nf_prod.strip():
            st.error("⚠️ O campo 'Nota Fiscal do Produto' é obrigatório. Preencha antes de salvar!")
        else:
            try:
                agora = datetime.now().strftime("%d/%m/%Y %H:%M")
                cursor.execute("""
                    INSERT INTO raq_registros (data_registro, produto, volume, data_coleta, hora_coleta, distribuidor, cnpj_distribuidor, transportador, cnpj_transportador, nf, placa, motorista, cpf_motorista, quimico, aspecto, cor, compartimento, temp_obs, dens_obs, dens_20, teor_etanol, teor_alcoolico)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (agora, produto, volume, data_col.strftime('%Y-%m-%d'), hora_col, dist, cnpj_dist, transp, cnpj_transp, nf_prod, placa_cam, mot, cpf_mot, resp_quimico, aspecto, cor, comp, temp_obs, dens_obs, dens_20, teor_etan, teor_alc))
                conn.commit()
                st.toast("RAQ arquivada com sucesso!", icon="✅")
            except Exception as e:
                st.error(f"Erro ao salvar no banco de dados: {e}")

with aba_historico:
    st.markdown("### 📜 Consultar Registros Salvos Eletronicamente")
    try:
        df_busca = pd.read_sql_query("SELECT id as 'ID', data_registro as 'Data do Lançamento', produto as 'Combustível', volume as 'Volume (L)', nf as 'Nota Fiscal', motorista as 'Motorista', dens_20 as 'Densidade a 20°C' FROM raq_registros ORDER BY id DESC", conn)
        
        if not df_busca.empty:
            st.dataframe(df_busca, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum lançamento foi armazenado no banco local até o momento.")
    except Exception as e:
        st.error(f"Erro ao carregar o histórico: {e}")
