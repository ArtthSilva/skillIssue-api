import streamlit as st
import pandas as pd
from src.skills.analyzer import aggregate_descriptions, top_n

st.set_page_config(page_title="Radar de Vagas", layout="wide")
st.title("Radar de Vagas – Front-end JR (Brasil)")

@st.cache_data
def load_data(path: str = "data/jobs.csv"):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=["title","company","location","desc","source","url"]) 

query = st.text_input("Busca", value="front end junior")
location = st.text_input("Local", value="Brasil")

st.caption("Use o script de coleta para atualizar o arquivo data/jobs.csv")

df = load_data()
st.write(f"Vagas carregadas: {len(df)}")

if len(df):
    agg = aggregate_descriptions(df["desc"].dropna().tolist())
    top = top_n(agg, 15)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Stacks Dev")
        df_dev = pd.DataFrame(top["dev"], columns=["skill","freq"]).sort_values("freq", ascending=False)
        st.bar_chart(df_dev.set_index("skill"))
    with col2:
        st.subheader("Cloud/DevOps")
        df_cloud = pd.DataFrame(top["cloud"], columns=["skill","freq"]).sort_values("freq", ascending=False)
        st.bar_chart(df_cloud.set_index("skill"))
    with col3:
        st.subheader("Soft Skills")
        df_soft = pd.DataFrame(top["soft"], columns=["skill","freq"]).sort_values("freq", ascending=False)
        st.bar_chart(df_soft.set_index("skill"))

    with st.expander("Vagas (amostra)"):
        st.dataframe(df[["title","company","location","source","url"]].head(50))
else:
    st.info("Nenhum dado encontrado. Rode: python collect_and_analyze.py 'front end junior' --sources indeed --limit 50")
