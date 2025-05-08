import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
font_path = "NanumGothic.ttf"
fontprop = fm.FontProperties(fname=font_path, size=12)
plt.rc('font', family=fontprop.get_name())

# 데이터 불러오기
df = pd.read_excel("used_cars.xlsx", sheet_name=0)

# 연식, 키로수, 가격을 정수형으로 변환
df["연식(수)"] = df["연식(수)"].astype(int)
df["키로수"] = df["키로수"].astype(int)
df["가격(숫자)"] = df["가격(숫자)"].astype(int)

# 모델명 + 연식 범위 설정
model_summary = df.groupby(["회사", "모델"])["연식(수)"].agg(["min", "max"]).reset_index()
model_summary["모델명표시"] = model_summary.apply(
    lambda x: f"{x['모델']} ({x['min']}년~{x['max']}년식)", axis=1)

# 기본값 설정
default_model = "그랜저 IG"
default_index = model_summary[model_summary["모델"] == default_model].index[0]

# 사이드바 구성
st.set_page_config(page_title="중고차 최신시세조회", layout="wide")
st.title("🚗 중고차 최신시세조회")

st.markdown("간단한 필터를 통해 원하는 중고차 모델의 **연식별 및 키로수별 평균 시세**를 확인할 수 있습니다.")

# 모델 선택
selected_display = st.selectbox("📌 모델 선택", model_summary["모델명표시"], index=default_index)
selected_row = model_summary[model_summary["모델명표시"] == selected_display].iloc[0]
selected_company = selected_row["회사"]
selected_model = selected_row["모델"]

# 보기 옵션
st.markdown("### 📊 보기 옵션 선택")
view_option = st.radio("보기 옵션", ["연식별 시세", "키로수별 시세"], horizontal=True)

# 필터링
filtered = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# 시세 요약 텍스트
st.markdown("#### 💬 시세 요약")
summary_text = "· ".join(
    [f"{y}년식 {int(p):,}만원" for y, p in 
     filtered.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False).astype(int).items()]
)
st.write(f"💬 **{selected_model} 중고차 시세는** {summary_text} 입니다.")

# 차트 시각화
if view_option == "연식별 시세":
    st.markdown(f"### 📈 {selected_model} 연식별 시세 평균 중고차 시세")
    avg_by_year = filtered.groupby("연식(수)")["가격(숫자)"].mean().astype(int).sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(7, len(avg_by_year) * 0.6))
    bars = ax.barh(avg_by_year.index.astype(str), avg_by_year.values, color='orange')
    ax.set_xlabel("평균 시세 (만원)")
    ax.set_ylabel("연식")
    ax.invert_yaxis()
    for bar in bars:
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, f"{bar.get_width():,}만원", va='center')
    st.pyplot(fig)

elif view_option == "키로수별 시세":
    st.markdown(f"### 📉 {selected_model} 키로수별 평균 중고차 시세")
    bins = [0, 50000, 100000, 150000, 200000, 250000, 300000, 400000]
    labels = ["0~5만km", "5~10만km", "10~15만km", "15~20만km", "20~25만km", "25~30만km", "30만km 이상"]
    filtered["키로수범위"] = pd.cut(filtered["키로수"], bins=bins + [float('inf')], labels=labels, right=False)
    avg_by_km = filtered.groupby("키로수범위")["가격(숫자)"].mean().astype(int).sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(7, len(avg_by_km) * 0.6))
    bars = ax.barh(avg_by_km.index.astype(str), avg_by_km.values, color='orange')
    ax.set_xlabel("평균 시세 (만원)")
    ax.set_ylabel("키로수 구간")
    ax.invert_yaxis()
    for bar in bars:
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, f"{bar.get_width():,}만원", va='center')
    st.pyplot(fig)

# 유용한 팁
with st.expander("📌 중고차 시세 관련 팁 보기"):
    st.markdown("""
    ✅ **신차 대비 감가율이 높은 차량은 2~3년차 모델에서 시세 경쟁력이 있습니다.**  
    ✅ **동일 모델의 연료 유형(가솔린/LPG/디젤)에 따라 시세 차이가 크므로 주의하세요.**
    """)

# 매물 표 표시
with st.expander("📋 매물 목록 보기"):
    renamed_df = filtered.rename(columns={
        "연식(수)": "연식", "가격(숫자)": "가격(만원)"
    })
    st.dataframe(renamed_df[["회사", "모델", "연식", "키로수", "가격(만원)"]])
