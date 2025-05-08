import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 📁 한글 폰트 설정 (나눔고딕)
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="centered")

# 📊 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

df = load_data()

# 🧱 초기 기본값 설정
default_company = "현대"
default_model = "그랜저 IG"

# 📌 제목 및 설명
st.markdown("""
<h1 style='color:darkblue;'>🚗 중고차 최신시세조회</h1>
<p>간단한 필터를 통해 원하는 중고차 모델의 <b>연식별 및 키로수별 평균 시세</b>를 확인할 수 있습니다.</p>
""", unsafe_allow_html=True)

# 🚘 회사 선택
company_list = sorted(df["회사"].dropna().unique())
selected_company = st.selectbox("🚘 제조사 선택", company_list, index=company_list.index(default_company))

# 🚗 모델 선택
model_list = sorted(df[df["회사"] == selected_company]["모델"].dropna().unique())
model_years = df[df["모델"].isin(model_list)].groupby("모델")["연식(수)"].agg(["min", "max"])
model_options = [f"{m} ({int(model_years.loc[m, 'min'])}년~{int(model_years.loc[m, 'max'])}년식)" for m in model_list]
def_label = f"{default_model} ({int(model_years.loc[default_model, 'min'])}년~{int(model_years.loc[default_model, 'max'])}년식)"
selected_label = st.selectbox("🚗 모델 선택", model_options, index=model_options.index(def_label))
selected_model = selected_label.split(" (")[0]

# 📋 보기 옵션 선택
tab1, tab2 = st.tabs(["연식별 시세", "키로수별 시세"])

# 🔍 선택된 모델 필터링
df_selected = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# 📢 요약 정보 함수
def summary_text(data):
    by_year = data.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False).round(0)
    return f"{selected_model} 중고차 시세는 " + " · ".join([f"{int(y)}년식 {int(p):,}만원" for y, p in by_year.items()]) + " 입니다."

# ✅ 연식별 시세
def show_year_plot():
    st.markdown(f"💬 **{summary_text(df_selected)}**")
    grouped = df_selected.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(7, len(grouped) * 0.5))
    bars = ax.barh(grouped.index.astype(str), grouped.values, color="orange")
    ax.invert_yaxis()
    ax.set_xlabel("평균 시세 (만원)")
    ax.set_title(f"📈 {selected_model} 연식별 시세 평균 중고차 시세")
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 30, bar.get_y() + bar.get_height()/2, f"{int(width):,}만원", va='center')
    st.pyplot(fig)

# ✅ 키로수별 시세

def show_km_plot():
    bins = list(range(0, int(df["키로수"].max()) + 50000, 50000))
    labels = [f"{x//10000+1}만km" for x in bins[:-1]]
    df_selected["키로수구간"] = pd.cut(df_selected["키로수"], bins=bins, labels=labels, right=False)
    grouped = df_selected.groupby("키로수구간")["가격(숫자)"].mean().dropna().sort_index(ascending=False)
    st.markdown(f"💬 **{summary_text(df_selected)}**")
    fig, ax = plt.subplots(figsize=(7, len(grouped) * 0.5))
    bars = ax.barh(grouped.index.astype(str), grouped.values, color="orange")
    ax.invert_yaxis()
    ax.set_xlabel("평균 시세 (만원)")
    ax.set_title(f"📉 {selected_model} 키로수별 시세 평균 중고차 시세")
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 30, bar.get_y() + bar.get_height()/2, f"{int(width):,}만원", va='center')
    st.pyplot(fig)

with tab1:
    show_year_plot()
with tab2:
    show_km_plot()

# 📊 요약 지표
st.subheader("📌 요약 정보")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("평균 연식", f"{int(df_selected['연식(수)'].mean())}년")
with col2:
    st.metric("평균 키로수", f"{int(df_selected['키로수'].mean()):,} km")
with col3:
    st.metric("매물 수", f"{len(df_selected)}건")

# 📋 매물 목록
with st.expander("📋 매물 목록 보기", expanded=False):
    st.dataframe(df_selected.reset_index(drop=True)[["회사", "모델", "연식(수)", "키로수", "가격(숫자)"]])

# ℹ️ 팁
with st.expander("📈 중고차 시세 관련 팁 보기"):
    st.info("""
✔ 신차 대비 감가율이 높은 차량은 2~3년차 모델에서 시세 경쟁력이 있습니다.
✔ 동일 모델의 연료 유형(가솔린/LPG/디젤)에 따라 시세 차이가 크므로 주의하세요.
""")
