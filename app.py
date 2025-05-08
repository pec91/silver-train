import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ✅ 안전한 한글 폰트 설정 (OS에 따라 자동 적용, 에러 없음)
plt.rcParams['font.family'] = ['AppleGothic', 'Malgun Gothic', 'NanumGothic', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="wide")

@st.cache_data
def load_data():
    return pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

df = load_data()

# 💛 앱 제목 + 설명
st.markdown("<h1 style='color:gold;'>🚗 중고차 최신시세조회</h1>", unsafe_allow_html=True)
st.markdown("""
중고차 가격 데이터를 바탕으로 브랜드, 모델, 연식, 키로수에 따른 **평균 시세를 그래프로 조회**할 수 있는 앱입니다.  
- 제조사와 모델을 선택하고, 연식별 또는 키로수별 시세를 확인하세요.  
- 시세는 막대그래프와 함께 평균 가격이 표시되며, 아래 표에서 개별 매물도 확인할 수 있어요.
""")

# 🔧 기본 설정: 현대 / 그랜저 IG
default_company = "현대"
default_model = "그랜저 IG"

# 제조사 선택
company_list = sorted(df["회사"].dropna().unique())
selected_company = st.selectbox("🚘 제조사 선택", company_list, index=company_list.index(default_company))

# 모델 + 연식 표시
model_list = sorted(df[df["회사"] == selected_company]["모델"].dropna().unique())
model_years = df[df["모델"].isin(model_list)].groupby("모델")["연식(수)"].agg(["min", "max"])
model_options = [f"{m} ({int(model_years.loc[m, 'min'])}년~{int(model_years.loc[m, 'max'])}년식)" for m in model_list]
selected_label = st.selectbox("🚗 모델 선택", model_options, index=model_options.index(
    f"{default_model} ({int(model_years.loc[default_model, 'min'])}년~{int(model_years.loc[default_model, 'max'])}년식)"
))
selected_model = selected_label.split(" (")[0]

# 보기 선택
view_option = st.radio("📊 보기 옵션 선택", ["연식별 시세", "키로수별 시세"], horizontal=True)

# 필터링
filtered = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# 📌 요약 문장
def build_summary(data):
    by_year = data.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False).round(0)
    return f"{selected_model} 중고차 시세는 " + " · ".join([f"{int(y)}년식 {int(p):,}만원" for y, p in by_year.items()]) + " 입니다."

st.markdown(f"💬 <b>{build_summary(filtered)}</b>", unsafe_allow_html=True)

# 📈 차트 데이터 생성
if view_option == "연식별 시세":
    group_col = "연식(수)"
    xlabel = "평균 시세 (만원)"
    title = f"📈 {selected_model} 연식별 평균 중고차 시세"
    sort_asc = False
else:
    bin_edges = list(range(0, int(df["키로수"].max()) + 50000, 50000))
    df["키로수구간"] = pd.cut(df["키로수"], bins=bin_edges, labels=[
        f"{x//1000}~{(x+50000)//1000}천km" for x in bin_edges[:-1]])
    filtered["키로수구간"] = df["키로수구간"]
    group_col = "키로수구간"
    xlabel = "평균 시세 (만원)"
    title = f"📉 {selected_model} 키로수별 평균 중고차 시세"
    sort_asc = True

grouped = filtered.groupby(group_col)["가격(숫자)"].mean().dropna().sort_index(ascending=sort_asc)

# 📊 그래프 출력
st.subheader(title)
fig, ax = plt.subplots(figsize=(8, len(grouped) * 0.5))
bars = ax.barh(grouped.index.astype(str), grouped.values, color="orange")
ax.invert_yaxis()
ax.set_xlabel(xlabel)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 30, bar.get_y() + bar.get_height()/2, f"{int(width):,}만원", va='center', fontsize=9)

st.pyplot(fig)

# 📌 요약 정보
st.markdown("## 📌 요약 정보")
col1, col2, col3 = st.columns(3)
col1.metric("평균 연식", f"{int(filtered['연식(수)'].mean())}년")
col2.metric("평균 키로수", f"{int(filtered['키로수'].mean()):,} km")
col3.metric("매물 수", f"{len(filtered)}건")

# 📋 매물 테이블
with st.expander("📋 매물 목록 보기", expanded=False):
    table = filtered[["회사", "모델", "연식(수)", "키로수", "가격(숫자)"]].rename(columns={"가격(숫자)": "가격(만원)"})
    st.dataframe(table.reset_index(drop=True))

# 💡 유용한 팁
with st.expander("📈 중고차 시세 관련 팁 보기"):
    st.info(
        "✔ 신차 대비 감가율이 높은 차량은 2~3년차 모델에서 시세 경쟁력이 있습니다.\n"
        "✔ 동일 모델의 연료 유형(가솔린/LPG/디젤)에 따라 시세 차이가 크므로 주의하세요."
    )
