import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

df = load_data()

st.markdown("<h1 style='color:gold;'>🚗 중고차 최신시세조회</h1>", unsafe_allow_html=True)

# 🔍 필터 선택
col1, col2 = st.columns(2)
with col1:
    selected_company = st.selectbox("🚘 제조사 선택", sorted(df["회사"].dropna().unique()))
with col2:
    models = df[df["회사"] == selected_company]["모델"].dropna().unique()
    selected_model = st.selectbox("🚗 모델 선택", sorted(models))

# 📊 데이터 필터링
filtered = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# 📈 연식별 평균 가격 계산
avg_by_year = filtered.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False)

# ✅ 막대 그래프 표시
st.subheader(f"📊 {selected_model} 연식별 평균 중고차 시세")
fig, ax = plt.subplots(figsize=(8, 6))
avg_by_year.plot(kind="barh", ax=ax, color="orange")
ax.invert_yaxis()
ax.set_xlabel("평균 시세 (만원)")
ax.set_ylabel("연식")
st.pyplot(fig)

# 🧾 요약 통계 정보
st.subheader("📌 요약 정보")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("평균 연식", f"{int(filtered['연식(수)'].mean())}년")
with col2:
    st.metric("평균 키로수", f"{int(filtered['키로수'].mean()):,} km")
with col3:
    st.metric("매물 수", f"{len(filtered)}건")

# 🔽 매물 데이터 표
with st.expander("📋 개별 매물 보기", expanded=False):
    st.dataframe(filtered.reset_index(drop=True))
