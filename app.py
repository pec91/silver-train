import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ✅ 한글 폰트 설정 (NanumGothic.ttf 를 같은 디렉토리에 업로드한 경우)
font_path = os.path.join(os.getcwd(), "NanumGothic.ttf")
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams["font.family"] = "NanumGothic"
else:
    st.warning("한글 폰트 파일이 없습니다. NanumGothic.ttf를 업로드하세요.")

# ✅ 페이지 설정
st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="wide")
st.title("🚗 중고차 최신시세조회")
st.markdown("간단한 필터를 통해 원하는 중고차 모델의 **연식별 및 키로수별 평균 시세**를 확인할 수 있습니다.")

# ✅ 데이터 불러오기
df = pd.read_excel("used_cars.xlsx")

# ✅ '그랜저 IG'만 필터링
df = df[df["모델"].str.contains("그랜저 IG", na=False)]

# ✅ 모델 정보 표시용
model_name = "그랜저 IG"
min_year = df["연식(수)"].min()
max_year = df["연식(수)"].max()
st.selectbox("🚘 모델 선택", [f"{model_name} ({min_year}년~{max_year}년식)"], index=0)

# ✅ 보기 옵션 선택
st.markdown("### 📊 보기 옵션 선택")
view_option = st.radio("보기 옵션", ["연식별 시세", "키로수별 시세"])

# ✅ 시세 요약
summary = df.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False).astype(int)
summary_text = " · ".join([f"{year}년식 {price:,}만원" for year, price in summary.items()])
st.markdown(f"💬 **{model_name} 중고차 시세는** {summary_text} 입니다.")

# ✅ 그래프 출력
if view_option == "연식별 시세":
    st.markdown(f"### 📈 {model_name} 연식별 시세 평균 중고차 시세")
    fig, ax = plt.subplots(figsize=(8, len(summary) * 0.6))
    summary.sort_index(ascending=True).plot(kind="barh", color="orange", ax=ax)
    for i, (value) in enumerate(summary.sort_index(ascending=True).values):
        ax.text(value + 30, i, f"{value:,}만원", va="center")
    ax.set_xlabel("평균 시세 (만원)")
    ax.set_ylabel("연식")
    st.pyplot(fig)

else:
    st.markdown(f"### 📉 {model_name} 키로수별 평균 중고차 시세")
    bins = list(range(0, 410000, 50000))
    labels = [f"{int(b/10000)}만~{int((b+50000)/10000)}만km" for b in bins[:-1]]
    df["키로수구간"] = pd.cut(df["키로수"], bins=bins, labels=labels, include_lowest=True)
    km_avg = df.groupby("키로수구간")["가격(숫자)"].mean().dropna().astype(int)
    fig, ax = plt.subplots(figsize=(8, len(km_avg) * 0.6))
    km_avg.sort_index(ascending=True).plot(kind="barh", color="orange", ax=ax)
    for i, value in enumerate(km_avg.values):
        ax.text(value + 30, i, f"{value:,}만원", va="center")
    ax.set_xlabel("평균 시세 (만원)")
    ax.set_ylabel("키로수 구간")
    st.pyplot(fig)

# ✅ 매물 보기
with st.expander("📋 매물 목록 보기", expanded=False):
    st.dataframe(df[["회사", "모델", "연식(수)", "키로수", "가격(숫자)"]].rename(columns={
        "연식(수)": "연식",
        "가격(숫자)": "가격(만원)"
    }))
