import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ✅ 한글 폰트 설정 (NanumGothic.ttf 불필요)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# ✅ 페이지 설정
st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="centered")

# ✅ 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_excel("used_cars.xlsx")

df = load_data()

# ✅ 엑셀 컬럼 점검
required_cols = {"회사", "모델", "연식(수)", "키로수", "가격(숫자)"}
if not required_cols.issubset(set(df.columns)):
    st.error("❌ 데이터 파일의 컬럼명이 올바르지 않습니다. 다음 컬럼이 필요합니다: " + ", ".join(required_cols))
    st.stop()

# ✅ 제목 & 설명
st.title("🚗 중고차 최신시세조회")
st.markdown("""
간단한 필터를 통해 원하는 중고차 모델의 **연식별 및 키로수별 평균 시세**를 확인할 수 있습니다.
""")

# ✅ 기본값 설정
default_company = "현대"
default_model = "그랜저 IG"

# ✅ 제조사 선택
companies = sorted(df["회사"].dropna().unique())
selected_company = st.selectbox("🚘 제조사 선택", companies, index=companies.index(default_company) if default_company in companies else 0)

# ✅ 모델 선택
models = sorted(df[df["회사"] == selected_company]["모델"].dropna().unique())
model_years = df[df["모델"].isin(models)].groupby("모델")["연식(수)"].agg(["min", "max"])
model_options = [f"{m} ({int(model_years.loc[m, 'min'])}년~{int(model_years.loc[m, 'max'])}년식)" for m in models]

# ✅ 기본 모델 표시
default_model_full = f"{default_model} ({int(model_years.loc[default_model, 'min'])}년~{int(model_years.loc[default_model, 'max'])}년식)" if default_model in model_years.index else model_options[0]

selected_model_label = st.selectbox("🚗 모델 선택", model_options, index=model_options.index(default_model_full))
selected_model = selected_model_label.split(" (")[0]

# ✅ 시세 보기 옵션
view_option = st.radio("📊 보기 옵션", ["연식별 시세", "키로수별 시세"], horizontal=True)

# ✅ 필터링
filtered = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# ✅ 시세 요약
def make_summary(data):
    by_year = data.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False).round(0)
    return f"{selected_model} 중고차 시세는 " + " · ".join([f"{int(y)}년식 {int(p):,}만원" for y, p in by_year.items()]) + " 입니다."

st.markdown(f"💬 **{make_summary(filtered)}**")

# ✅ 시각화
if view_option == "연식별 시세":
    group_col = "연식(수)"
    xlabel = "평균 시세 (만원)"
    title = f"📈 {selected_model} 연식별 시세 평균 중고차 시세"
else:
    bin_edges = list(range(0, int(df["키로수"].max()) + 50000, 50000))
    df["키로수구간"] = pd.cut(df["키로수"], bins=bin_edges, labels=[
        f"{x//10000}만~{(x+50000)//10000}만km" for x in bin_edges[:-1]
    ])
    filtered["키로수구간"] = df["키로수구간"]
    group_col = "키로수구간"
    xlabel = "평균 시세 (만원)"
    title = f"📉 {selected_model} 키로수별 시세 평균 중고차 시세"

grouped = filtered.groupby(group_col)["가격(숫자)"].mean().dropna().sort_index(ascending=False)

# ✅ 그래프 출력
st.subheader(title)
fig, ax = plt.subplots(figsize=(7, len(grouped) * 0.45))
bars = ax.barh(grouped.index.astype(str), grouped.values, color="orange")
ax.invert_yaxis()
ax.set_xlabel(xlabel)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 30, bar.get_y() + bar.get_height()/2, f"{int(width):,}만원", va='center', fontsize=9)

st.pyplot(fig)

# ✅ 요약 지표
st.subheader("📌 요약 정보")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("평균 연식", f"{int(filtered['연식(수)'].mean())}년")
with col2:
    st.metric("평균 키로수", f"{int(filtered['키로수'].mean()):,} km")
with col3:
    st.metric("매물 수", f"{len(filtered)}건")

# ✅ 매물 목록
with st.expander("📋 매물 목록 보기", expanded=False):
    st.dataframe(filtered.reset_index(drop=True)[["회사", "모델", "연식(수)", "키로수", "가격(숫자)"]])

# ✅ 시세 팁
with st.expander("📈 중고차 시세 관련 팁 보기"):
    st.info(
        "✔ 신차 대비 감가율이 높은 차량은 2~3년차 모델에서 시세 경쟁력이 있습니다.\n"
        "✔ 동일 모델의 연료 유형(가솔린/LPG/디젤)에 따라 시세 차이가 크므로 주의하세요."
    )
