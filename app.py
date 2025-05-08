import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 📌 폰트 설정
font_path = "NanumGothic.ttf"
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# 📌 데이터 불러오기
df = pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

st.set_page_config(page_title="중고차 최신시세조회", layout="wide")

# 📌 앱 설명
st.markdown("## 🚗 중고차 최신시세조회")
st.markdown("간단한 필터를 통해 원하는 중고차 모델의 **연식별 및 키로수별 평균 시세**를 확인할 수 있습니다.")

# 📌 모델 선택
models = df["모델"].dropna().unique()
models.sort()
default_model = "그랜저 IG"
selected_model = st.selectbox("🚗 모델 선택", models, index=list(models).index(default_model))

# 📌 연식 범위 추출
model_df = df[df["모델"] == selected_model]
min_year = int(model_df["연식(수)"].min())
max_year = int(model_df["연식(수)"].max())
st.markdown(f"#### 📊 보기 옵션 선택")

# 📌 시세 보기 옵션
view_option = st.radio("", ["연식별 시세", "키로수별 시세"], horizontal=True)

# 📌 요약 텍스트
summary_price = model_df.groupby("연식(수)")["가격(숫자)"].mean().round().astype(int).sort_index(ascending=False)
summary_text = " · ".join([f"{y}년식 {v:,}만원" for y, v in summary_price.items()])
st.markdown(f"💬 **{selected_model} 중고차 시세는 {summary_text} 입니다.**")

# 📊 연식별 평균 시세
if view_option == "연식별 시세":
    avg_by_year = summary_price
    st.markdown(f"### 📈 {selected_model} 연식별 평균 중고차 시세")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(avg_by_year.index.astype(str), avg_by_year.values, color="orange")
    ax.invert_yaxis()
    ax.set_xlabel("평균 시세 (만원)")
    for i, v in enumerate(avg_by_year.values):
        ax.text(v + 10, i, f"{v:,}만원", va='center', fontproperties=font_prop)
    st.pyplot(fig)

# 📊 키로수별 평균 시세
else:
    st.markdown(f"### 📉 {selected_model} 키로수별 평균 중고차 시세")
    km_bins = [0, 50000, 100000, 150000, 200000, 250000, 300000, 400000]
    labels = [f"{int(km_bins[i]/1000)}~{int(km_bins[i+1]/1000)}천km" for i in range(len(km_bins)-1)]
    model_df["주행구간"] = pd.cut(model_df["키로수"], bins=km_bins, labels=labels)
    avg_by_km = model_df.groupby("주행구간")["가격(숫자)"].mean().round().astype(int)
    avg_by_km = avg_by_km.sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(avg_by_km.index.astype(str), avg_by_km.values, color="orange")
    ax.invert_yaxis()
    ax.set_xlabel("평균 시세 (만원)")
    for i, v in enumerate(avg_by_km.values):
        ax.text(v + 10, i, f"{v:,}만원", va='center', fontproperties=font_prop)
    st.pyplot(fig)

# 📋 매물 요약 표
with st.expander("📄 매물 목록 보기", expanded=False):
    renamed_df = model_df.rename(columns={"가격(숫자)": "가격(만원)"})
    st.dataframe(renamed_df[["회사", "모델", "연식(수)", "키로수", "가격(만원)"]])

# 💡 팁
with st.expander("📈 중고차 시세 관련 팁 보기"):
    st.info("✔ 신차 대비 감가율이 높은 차량은 2~3년차 모델에서 시세 경쟁력이 있습니다.\n✔ 동일 모델의 연료 유형(가솔린/LPG/디젤)에 따라 시세 차이가 크므로 주의하세요.")
