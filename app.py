"""EUROCASH1 kavējumu Dashboard — PUBLISKA DEMONSTRĀCIJA.
Visi attēlotie ieraksti ir sintētiski. Nav pieslēguma OneDrive.
Nav autentifikācijas un nav piekļuves tiesību pārbaudes.
NEDRĪKST aizvietot demo datus ar īstiem personāla datiem un publicēt.
"""

import calendar
import random
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="EUROCASH1 | Kavējumu analītika — DEMO", page_icon="📊", layout="wide")

VADITAJI = [f"Vadītājs {n}" for n in range(1, 7)]
OBJEKTI = [f"Demo objekts {n:02d}" for n in range(1, 13)]
IEMESLI = ["Kavējums", "Cits pārkāpums", "Cits notikums"]


@st.cache_data

def ieladet_demo_datus():
    """Ģenerē sintētiskus datus — tie nav saistīti ar EUROCASH1 ierakstiem."""
    rng = random.Random(20261026)
    rindas = []
    for menesis in range(3, 11):
        skaits = rng.randint(90, 175)
        for n in range(skaits):
            diena = rng.randint(1, calendar.monthrange(2026, menesis)[1])
            vaditajs = rng.choice(VADITAJI)
            iemesls = rng.choices(IEMESLI, weights=[72, 22, 6])[0]
            rindas.append({
                "ID": f"DEMO-{menesis:02d}-{n:04d}",
                "Datums": datetime(2026, menesis, diena),
                "Mēnesis": f"2026-{menesis:02d}",
                "Gads": 2026,
                "Vadītājs": vaditajs,
                "Objekts": rng.choice(OBJEKTI),
                "Iemesls": iemesls,
                "Nenosegtās stundas": round(rng.uniform(0.25, 8), 2) if iemesls == "Kavējums" else 0,
            })
    return pd.DataFrame(rindas)


st.title("EUROCASH1 | Kavējumu analītika")
st.caption("Darbspējīgas lietotnes demonstrācija ar izdomātiem datiem")
st.error("DEMONSTRĀCIJA — visi dati ir izdomāti. Nav autentifikācijas, OneDrive savienojuma vai individuālu piekļuves tiesību. Neizmanto ar īstiem personāla datiem.")

dati = ieladet_demo_datus()
st.sidebar.header("Pārskata filtri")
st.sidebar.caption("Visi šeit pieejamie skati ir demonstrācijas skati.")

skats = st.sidebar.selectbox("Demonstrācijas skats", ["Vadība"] + VADITAJI)
if skats != "Vadība":
    dati = dati[dati["Vadītājs"] == skats].copy()

gadi = sorted(dati["Gads"].unique())
izveletie_gadi = st.sidebar.multiselect("Gads", gadi, default=gadi)
dati = dati[dati["Gads"].isin(izveletie_gadi)]

menesi = sorted(dati["Mēnesis"].unique())
izveletie_menesi = st.sidebar.multiselect("Mēneši", menesi, default=menesi)
dati = dati[dati["Mēnesis"].isin(izveletie_menesi)]

if not dati.empty:
    min_datums = dati["Datums"].min().date()
    max_datums = dati["Datums"].max().date()
    periods = st.sidebar.date_input("Datumu periods", (min_datums, max_datums), min_value=min_datums, max_value=max_datums)
    if isinstance(periods, (tuple, list)) and len(periods) == 2:
        dati = dati[dati["Datums"].dt.date.between(periods[0], periods[1])]

objekti = sorted(dati["Objekts"].unique())
filtra_objekti = st.sidebar.multiselect("Objekti", objekti)
if filtra_objekti:
    dati = dati[dati["Objekts"].isin(filtra_objekti)]

iemesli = sorted(dati["Iemesls"].unique())
filtra_iemesli = st.sidebar.multiselect("Iemesli", iemesli)
if filtra_iemesli:
    dati = dati[dati["Iemesls"].isin(filtra_iemesli)]

st.subheader("Kopējais pārskats" if skats == "Vadība" else f"{skats} — objektu pārskats")

if dati.empty:
    st.info("Izvēlētajiem filtriem nav datu.")
    st.stop()

visi = len(dati)
kavejumi = int((dati["Iemesls"] == "Kavējums").sum())
citi = visi - kavejumi
stundas = float(dati["Nenosegtās stundas"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Visi gadījumi", f"{visi:,}".replace(",", " "))
col2.metric("Kavējumi", f"{kavejumi:,}".replace(",", " "))
col3.metric("Citi gadījumi", f"{citi:,}".replace(",", " "))
col4.metric("Nenosegtās stundas", f"{stundas:,.1f}".replace(",", " "))

st.subheader("Gadījumu dinamika pa mēnešiem")
dinamika = dati.groupby(["Mēnesis", "Iemesls"], as_index=False).size().rename(columns={"size": "Gadījumi"})
fig = px.bar(dinamika, x="Mēnesis", y="Gadījumi", color="Iemesls", barmode="stack", text="Gadījumi")
fig.update_layout(xaxis_title="Mēnesis", yaxis_title="Gadījumu skaits", legend_title_text="Iemesls")
st.plotly_chart(fig, use_container_width=True)

kreisa, laba = st.columns(2)
with kreisa:
    st.subheader("Kavējumi pa objektiem")
    objektu_dati = dati.groupby("Objekts", as_index=False).size().rename(columns={"size": "Gadījumi"})
    objektu_dati = objektu_dati.sort_values("Gadījumi", ascending=False)
    st.plotly_chart(px.bar(objektu_dati, x="Objekts", y="Gadījumi", text="Gadījumi"), use_container_width=True)
with laba:
    st.subheader("Vadītāju salīdzinājums")
    vaditaju_dati = dati.groupby("Vadītājs", as_index=False).agg(Gadījumi=("ID", "count"), Nenosegtās_stundas=("Nenosegtās stundas", "sum"))
    st.plotly_chart(px.bar(vaditaju_dati, x="Vadītājs", y="Gadījumi", text="Gadījumi"), use_container_width=True)

st.subheader("Detalizētie demonstrācijas ieraksti")
redzamas = ["Datums", "Vadītājs", "Objekts", "Iemesls", "Nenosegtās stundas"]
st.dataframe(dati[redzamas].sort_values("Datums", ascending=False), hide_index=True, use_container_width=True)
st.download_button("Lejupielādēt demonstrācijas datus (CSV)", data=dati[redzamas].to_csv(index=False).encode("utf-8-sig"), file_name="demo_kavejumi.csv", mime="text/csv")
st.caption("Šī versija paredzēta tikai saskarnes un izvietošanas testēšanai. Produkcijai nepieciešams drošs datu avots un lietotāju tiesību pārbaude.")
