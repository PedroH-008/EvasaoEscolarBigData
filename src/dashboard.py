from pathlib import Path

from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "data" / "gold"
BRONZE = ROOT / "data" / "bronze"


@st.cache_data(ttl=600)
def read_gold(name: str) -> pd.DataFrame:
    folder = GOLD / f"{name}_csv"
    files = sorted(folder.glob("part-*.csv"))
    if not files:
        raise FileNotFoundError(f"Arquivo da camada gold nao encontrado: {folder}")
    return pd.read_csv(files[0])


@st.cache_data(ttl=600)
def read_bronze(name: str) -> pd.DataFrame:
    path = BRONZE / f"{name}.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

def fmt_int(x: int) -> str:
    return f"{int(x):,}".replace(",", ".")


st.set_page_config(page_title="Big Data - Evasao Escolar", layout="wide")
st.title("Painel Analitico de Prevencao da Evasao Escolar")
st.caption("Visao executiva + analise tatico-operacional para apoio a decisoes da escola")

# carregar dados
try:
    scores = read_gold("student_risk_scores")
    neighborhood = read_gold("dropout_by_neighborhood")
    subjects = read_gold("subject_absences")
    reasons = read_gold("dropout_reasons")
    kpis = read_gold("kpis").iloc[0]
except FileNotFoundError as e:
    st.error(str(e))
    st.stop()
students_b = read_bronze("students")
attendance_b = read_bronze("attendance")
grades_b = read_bronze("grades")
_engagement_b = read_bronze("digital_engagement")
_interventions_b = read_bronze("interventions")
_socio_b = read_bronze("socioeconomic")

students_bronze = read_bronze("students")
socio_bronze = read_bronze("socioeconomic")
attendance_bronze = read_bronze("attendance")
grades_bronze = read_bronze("grades")


# Sidebar: filtros globais e busca
st.sidebar.header("Filtros globais")
band_options = sorted(scores["risk_band"].unique(), reverse=True)
selected_band = st.sidebar.multiselect("Faixa de risco", band_options, default=band_options)
shift_options = sorted(scores["shift"].unique())
selected_shift = st.sidebar.multiselect("Turno", shift_options, default=shift_options)
grade_options = sorted(scores["grade_level"].unique())
selected_grade = st.sidebar.multiselect("Série", grade_options, default=grade_options)
min_absence = st.sidebar.slider("Frequência mínima (taxa de faltas)", 0.0, 1.0, 0.10, 0.01)

st.sidebar.markdown("---")
search_input = st.sidebar.text_input("Buscar aluno por nome ou ID")
top_n = st.sidebar.number_input("Mostrar top N alunos", min_value=10, max_value=1000, value=100, step=10)


filtered = scores[
    scores["risk_band"].isin(selected_band)
    & scores["shift"].isin(selected_shift)
    & scores["grade_level"].isin(selected_grade)
    & (scores["absence_rate"] >= min_absence)
]

if search_input:
    q = search_input.strip().lower()
    mask = filtered["name"].str.lower().str.contains(q) | (filtered["student_id"].astype(str) == q)
    filtered = filtered[mask]

st.sidebar.markdown(f"Alunos filtrados: **{len(filtered):,}**")

# Top KPIs
kp1, kp2, kp3, kp4 = st.columns(4)
kp1.metric("Alunos monitorados", fmt_int(kpis["total_students"]))
kp2.metric("Evadidos", fmt_int(kpis["dropouts"]))
kp3.metric("Risco médio", f"{kpis['avg_dropout_risk']:.1%}")
kp4.metric("AUC do modelo", f"{kpis['model_auc']:.3f}")

# Row with distribution and neighborhood
dist_col, neigh_col = st.columns([2, 3])
with dist_col:
    st.subheader("Distribuição de risco")
    fig = px.histogram(
        scores,
        x="dropout_risk",
        nbins=30,
        color="risk_band",
        labels={"dropout_risk": "Probabilidade de evasão"},
        marginal="box",
    )
    fig.update_layout(xaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

with neigh_col:
    st.subheader("Risco médio por bairro")
    fig = px.bar(
        neighborhood.sort_values("dropout_rate", ascending=False).head(20),
        x="neighborhood",
        y="avg_risk",
        color="dropout_rate",
        labels={"avg_risk": "Risco médio", "neighborhood": "Bairro", "dropout_rate": "Taxa de evasão"},
    )
    fig.update_layout(yaxis_tickformat=".0%", xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)


# Subjects absences
sub_col1, sub_col2 = st.columns(2)
with sub_col1:
    st.subheader("Faltas por disciplina (top 15)")
    fig = px.bar(
        subjects.sort_values("absence_rate", ascending=False).head(15),
        x="subject_name",
        y="absence_rate",
        color="absence_rate",
        labels={"subject_name": "Disciplina", "absence_rate": "Taxa de faltas"},
    )
    fig.update_layout(yaxis_tickformat=".0%", xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

with sub_col2:
    st.subheader("Motivos de evasão")
    if reasons.empty:
        st.info("Nenhum aluno evadido na base.")
    else:
        fig = px.pie(reasons, names="dropout_reason", values="students", hole=0.35)
        st.plotly_chart(fig, use_container_width=True)


# Scatter: notas vs faltas
st.subheader("Relação entre notas, faltas e risco")
fig = px.scatter(
    filtered.head(1000),
    x="absence_rate",
    y="avg_grade",
    color="risk_band",
    size="dropout_risk",
    hover_data=["name", "grade_level", "shift", "neighborhood"],
    labels={"absence_rate": "Taxa de faltas", "avg_grade": "Média de notas", "risk_band": "Risco"},
)
fig.update_layout(xaxis_tickformat=".0%")
st.plotly_chart(fig, use_container_width=True)


# Tabela com ações: seleção e download
st.subheader("Alunos prioritários")
columns = [
    "student_id",
    "name",
    "grade_level",
    "shift",
    "neighborhood",
    "dropout_risk",
    "risk_band",
    "absence_rate",
    "avg_grade",
    "distance_km",
    "internet_access",
    "works_after_school",
    "intervention_count",
]

display_df = filtered[columns].copy()
display_df["dropout_risk"] = (display_df["dropout_risk"] * 100).round(2).astype(str) + "%"
display_df["absence_rate"] = (display_df["absence_rate"] * 100).round(2).astype(str) + "%"

st.dataframe(display_df.head(top_n), use_container_width=True, height=420)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Exportar filtrado (CSV)", csv_bytes, file_name="alunos_filtrados.csv", mime="text/csv")


# Painel de detalhe do aluno
st.sidebar.markdown("---")
st.sidebar.header("Detalhe do aluno")
student_selection: Optional[str] = st.sidebar.selectbox(
    "Escolha um aluno (ID) para visualizar detalhes",
    options=[""] + filtered["student_id"].astype(str).tolist(),
)
if student_selection:
    sid = int(student_selection)
    student_row = scores[scores["student_id"] == sid].iloc[0]
    st.sidebar.markdown(f"**{student_row['name']}** - {student_row['grade_level']} / {student_row['shift']}")
    # juntar info bronze
    student_info = students_bronze[students_bronze["student_id"] == sid]
    socio_info = socio_bronze[socio_bronze["student_id"] == sid]
    st.sidebar.write(student_info.to_dict(orient="records"))
    st.sidebar.write(socio_info.to_dict(orient="records"))

    # Main details
    st.subheader(f"Perfil detalhado: {student_row['name']} (ID {sid})")
    cols = st.columns(3)
    cols[0].metric("Risco de evasão", f"{student_row['dropout_risk']:.1%}")
    cols[1].metric("Taxa de faltas", f"{student_row['absence_rate']:.1%}")
    cols[2].metric("Média", f"{student_row['avg_grade']:.2f}")

    # attendance and grades charts
    att = attendance_bronze[attendance_bronze["student_id"] == sid]
    grd = grades_bronze[grades_bronze["student_id"] == sid]

    if not att.empty:
        att_summary = att.groupby("subject_id", as_index=False).agg(total_absences=("absences", "sum"))
        # join subject names if available
        subjects_b = read_bronze("subjects")
        att_summary = att_summary.merge(subjects_b, on="subject_id", how="left")
        fig = px.bar(att_summary.sort_values("total_absences", ascending=False), x="subject_name", y="total_absences", labels={"subject_name": "Disciplina", "total_absences": "Faltas"})
        st.plotly_chart(fig, use_container_width=True)

    if not grd.empty:
        grd_summary = grd.groupby("subject_id", as_index=False).agg(avg_grade=("grade", "mean"))
        subjects_b = read_bronze("subjects")
        grd_summary = grd_summary.merge(subjects_b, on="subject_id", how="left")
        fig = px.bar(grd_summary.sort_values("avg_grade", ascending=True), x="subject_name", y="avg_grade", labels={"subject_name": "Disciplina", "avg_grade": "Média"}, color="avg_grade", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)

    # quick action: marcar intervenção
    if st.sidebar.button("Marcar intervenção (simulação)"):
        st.sidebar.success("Intervenção registrada (simulada).")

