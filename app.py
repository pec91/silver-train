import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 기본 설정
st.set_page_config(page_title="중고차 시세 조회", page_icon="🚗")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_excel("used_cars.xlsx")

df = load_data()

# 필수 컬럼 확인
required_cols = {"회사", "모델", "연식(수)", "키로수", "가격(숫자)"}
if not required_cols.issubset(df.columns):
    st.error("❌ 필수 컬럼이 누락되었습니다.")
    st.stop()

# 기본값
default_company = "현대"
default_model = "그랜저 IG"

# 회사 선택
companies = sorted(df["회사"].dropna().unique())
selected_company = st.selectbox("🚘 제조사 선택", companies, index=companies.index(default_company) if default_company in companies else 0)

# 모델 선택
models = sorted(df[df["회사"] == selected_company]["모델"].dropna().unique())
if not models:
    st.warning("선택한 제조사의 모델이 없습니다.")
    st.stop()

selected_model = st.selectbox("🚗 모델 선택", models, index=models.index(default_model) if default_model in models else 0)

# 보기 옵션
view_type = st.radio("📊 보기 방식", ["연식별", "키로수별"], horizontal=True)

# 데이터 필터링
filtered = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]
if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

# 그래프용 데이터
if view_type == "연식별":
    grouped = filtered.groupby("연식(수)")["가격(숫자)"].mean().sort_index()
    xlabel = "연식"
else:
    bins = list(range(0, int(df["키로수"].max()) + 50000, 50000))
    labels = [f"{x//10000}만~{(x+50000)//10000}만km" for x in bins[:-1]]
    filtered["주행거리"] = pd.cut(filtered["키로수"], bins=bins, labels=labels)
    grouped = filtered.groupby("주행거리")["가격(숫자)"].mean().sort_index()
    xlabel = "주행거리 구간"

# 시각화
st.subheader(f"📈 {selected_model} {view_type} 평균 시세")
fig, ax = plt.subplots()
grouped.plot(kind="barh", ax=ax, color="orange")
ax.set_xlabel("평균 시세 (만원)")
st.pyplot(fig)

# 요약 정보
st.subheader("📌 요약")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("평균 연식", f"{filtered['연식(수)'].mean():.0f}년")
with col2:
    st.metric("평균 키로수", f"{filtered['키로수'].mean():,.0f} km")
with col3:
    st.metric("매물 수", f"{len(filtered)}건")

# 매물 표 보기
with st.expander("📋 매물 보기"):
    st.dataframe(filtered[["회사", "모델", "연식(수)", "키로수", "가격(숫자)"]].reset_index(drop=True))
