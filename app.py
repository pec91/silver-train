import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 폰트 설정
font_path = "NanumGothic.ttf"
fontprop = fm.FontProperties(fname=font_path, size=12)
plt.rcParams["font.family"] = fontprop.get_name()

# 데이터 불러오기
df = pd.read_excel("used_cars.xlsx", sheet_name=0)

# 데이터 전처리 (열 이름 문자열화)
df.columns = df.columns.astype(str)

# 모델 이름 + 연식 범위 합치기
model_years = df.groupby("모델")["연식(수)"].agg(["min", "max"])
model_with_years = [f"{model} ({row['min']}년~{row['max']}년식)" for model, row in model_years.iterrows()]
model_mapping = dict(zip(model_with_years, model_years.index))

# 앱 기본 설정
st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="centered")

st.markdown("## 🚗 중고차 최신시세조회")
st.markdown("간단한 필터를 통해 원하는 중고차 모델의 **연식별 및 키로수별 평균 시세**를 확인할 수 있습니다.")

# 모델 선택
selected_full = st.selectbox("🚗 모델 선택", options=model_with_years, index=model_with_years.index("그랜저 IG (2016년~2019년식)"))
selected_model = model_mapping[selected_full]

# 보기 옵션 선택
st.markdown("### 📊 보기 옵션 선택")
option = st.radio("보기 옵션", ["연식별 시세", "키로수별 시세"], horizontal=True)

# 필터링
filtered = df[df["모델"] == selected_model]

# 요약 텍스트
year_summary = (
    filtered.groupby("연식(수)")["가격(숫자)"]
    .mean()
    .sort_index(ascending=False)
    .astype(int)
    .apply(lambda x: f"{x:,}만원")
)
summary_text = " · ".join([f"{year}년식 {price}" for year, price in year_summary.items()])
st.markdown(f"💬 **{selected_model} 중고차 시세는** {summary_text} 입니다.")

# 시각화
st.markdown(f"### 📈 {selected_model} {option} 평균 중고차 시세")

fig, ax = plt.subplots(figsize=(8, len(filtered["연식(수)"].unique()) if option == "연식별 시세" else 6))

if option == "연식별 시세":
    grouped = filtered.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False)
    ax.barh(grouped.index.astype(str), grouped.values, color="orange")
    for i, (year, val) in enumerate(grouped.items()):
        ax.text(val + 30, i, f"{int(val):,}만원", va="center", fontproperties=fontprop)
    ax.set_ylabel("연식", fontproperties=fontprop)

else:
    bins = range(0, 410000, 50000)
    labels = [f"{int(b/1000)}~{int((b+50000)/1000)}㎞" for b in bins[:-1]]
    filtered["km_bin"] = pd.cut(filtered["키로수"], bins=bins, labels=labels)
    grouped = filtered.groupby("km_bin")["가격(숫자)"].mean().dropna().astype(int)
    grouped = grouped[::-1]
    ax.barh(grouped.index.astype(str), grouped.values, color="orange")
    for i, (label, val) in enumerate(grouped.items()):
        ax.text(val + 30, i, f"{int(val):,}만원", va="center", fontproperties=fontprop)
    ax.set_ylabel("키로수", fontproperties=fontprop)

ax.set_xlabel("평균 시세 (만원)", fontproperties=fontprop)
st.pyplot(fig)

# 유용한 팁
with st.expander("📈 중고차 시세 관련 팁 보기"):
    st.markdown(
        """
        ✅ 신차 대비 감가율이 높은 차량은 **2~3년차 모델**에서 시세 경쟁력이 있습니다.  
        ✅ 동일 모델의 **연료 유형(가솔린/LPG/디젤)**에 따라 시세 차이가 크므로 주의하세요.
        """,
        unsafe_allow_html=True
    )

# 매물 목록 출력
with st.expander("📋 매물 목록 보기", expanded=False):
    renamed_df = filtered.rename(columns={"가격(숫자)": "가격(만원)"})
    st.dataframe(renamed_df[["회사", "모델", "연식(수)", "키로수", "가격(만원)"]].reset_index(drop=True))
