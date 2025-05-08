import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="centered")

# ✅ 한글 폰트 설정 (맑은 고딕 또는 나눔고딕)
plt.rcParams['font.family'] = 'Malgun Gothic' if 'Malgun Gothic' in fm.get_fontconfig_fonts() else 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_data():
    return pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

df = load_data()

st.markdown("<h1 style='color:gold;'>🚗 중고차 최신시세조회</h1>", unsafe_allow_html=True)

# 기본값: 현대 아반떼
default_company = "현대"
default_model = "아반떼"

# 🔍 필터 선택
company_list = sorted(df["회사"].dropna().unique())
selected_company = st.selectbox("🚘 제조사 선택", company_list, index=company_list.index(default_company) if default_company in company_list else 0)

model_list = sorted(df[df["회사"] == selected_company]["모델"].dropna().unique())
selected_model = st.selectbox("🚗 모델 선택", model_list, index=model_list.index(default_model) if default_model in model_list else 0)

view_option = st.radio("📊 보기 옵션 선택", ["연식별 시세", "키로수별 시세"], horizontal=True)

filtered = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# 💬 시세 요약 텍스트
def build_summary(data, count=2):
    recent = data.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False).head(count).round(0)
    summary = " · ".join([f"{int(y)}년식 {int(p):,}만원" for y, p in recent.items()])
    return f"{selected_model} 중고차 시세는 {summary}입니다."

st.markdown(f"💬 **{build_summary(filtered)}**")

# 📊 데이터 그룹핑
if view_option == "연식별 시세":
    group_col = "연식(수)"
    xlabel = "평균 시세 (만원)"
    title = f"📈 {selected_model} 연식별 평균 중고차 시세"
else:
    bin_edges = list(range(0, int(df["키로수"].max()) + 50000, 50000))
    df["키로수구간"] = pd.cut(df["키로수"], bins=bin_edges, labels=[f"{x//1000}~{(x+50000)//1000}천km" for x in bin_edges[:-1]])
    filtered["키로수구간"] = df["키로수구간"]
    group_col = "키로수구간"
    xlabel = "평균 시세 (만원)"
    title = f"📉 {selected_model} 키로수별 평균 중고차 시세"

grouped = filtered.groupby(group_col)["가격(숫자)"].mean().dropna().sort_index(ascending=False)

# 📉 그래프 시각화
st.subheader(title)
fig, ax = plt.subplots(figsize=(7, len(grouped) * 0.45))
bars = ax.barh(grouped.index.astype(str), grouped.values, color="orange")
ax.invert_yaxis()
ax.set_xlabel(xlabel)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 30, bar.get_y() + bar.get_height()/2, f"{int(width):,}만원", va='center', fontsize=9)

st.pyplot(fig)

# 📌 요약 정보
st.subheader("📌 요약 정보")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("평균 연식", f"{int(filtered['연식(수)'].mean())}년")
with col2:
    st.metric("평균 키로수", f"{int(filtered['키로수'].mean()):,} km")
with col3:
    st.metric("매물 수", f"{len(filtered)}건")

# 📋 매물 목록
with st.expander("📋 매물 목록 보기", expanded=False):
    st.dataframe(filtered.reset_index(drop=True)[["회사", "모델", "연식(수)", "키로수", "가격(숫자)"]])

# 💡 사용자 체류 팁
with st.expander("📈 중고차 시세 관련 팁 보기"):
    st.info(
        "✔ 신차 대비 감가율이 높은 차량은 2~3년차 모델에서 시세 경쟁력이 있습니다.\\n"
        "✔ 동일 모델의 연료 유형(가솔린/LPG/디젤)에 따라 시세 차이가 크므로 주의하세요."
    )
