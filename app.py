import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 📌 나눔고딕 폰트 설정
font_path = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rc('font', family='NanumGothic')

# 📁 데이터 불러오기
df = pd.read_excel("used_cars.xlsx", sheet_name=0)
df = df.dropna(subset=["회사", "모델", "연식(수)", "가격(숫자)", "키로수"])  # 필수 칼럼 정리

# 📊 모델 요약 생성 (회사 + 모델 + 연식 범위)
summary_df = df.groupby(["회사", "모델"])["연식(수)"].agg(["min", "max"]).reset_index()
summary_df["모델명표시"] = summary_df["모델"] + " (" + summary_df["min"].astype(str) + "년~" + summary_df["max"].astype(str) + "년식)"
model_summary = summary_df

# 기본값 설정 - 예외 처리 포함
try:
    default_index = model_summary[model_summary["모델"] == "그랜저 IG"].index[0]
except IndexError:
    default_index = 0

# 🏷️ UI 시작
st.set_page_config("중고차 시세 조회", page_icon="🚗", layout="wide")
st.title("🚗 중고차 최신시세조회")
st.caption("간단한 필터를 통해 원하는 중고차 모델의 **연식별 및 키로수별 평균 시세**를 확인할 수 있습니다.")

# 📍 모델 선택
selected_display = st.selectbox("📌 모델 선택", model_summary["모델명표시"].tolist(), index=default_index)
selected_row = model_summary[model_summary["모델명표시"] == selected_display].iloc[0]
selected_company, selected_model = selected_row["회사"], selected_row["모델"]

# 🔎 보기 옵션 선택
st.markdown("### 🖼️ 보기 옵션 선택")
view_option = st.radio("보기 옵션", ["연식별 시세", "키로수별 시세"], horizontal=True)

# 📑 선택한 모델 데이터 필터링
filtered = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# 📌 시세 요약
st.markdown("### 💬 중고차 시세 요약")
year_price = filtered.groupby("연식(수)")["가격(숫자)"].mean().round().astype(int).sort_index(ascending=False)
summary_text = " · ".join([f"{year}년식 {price:,}만원" for year, price in year_price.items()])
st.markdown(f"💭 **{selected_model} 중고차 시세는** {summary_text} 입니다.")

# 📊 차트 시각화
st.markdown(f"### {'📈' if view_option=='연식별 시세' else '📉'} {selected_model} {view_option} 평균 중고차 시세")

fig, ax = plt.subplots(figsize=(6, 4))

if view_option == "연식별 시세":
    avg_price = filtered.groupby("연식(수)")["가격(숫자)"].mean().round().astype(int).sort_index(ascending=False)
    avg_price.plot(kind="barh", ax=ax, color="orange")
    for i, (val, idx) in enumerate(zip(avg_price, avg_price.index)):
        ax.text(val + 50, i, f"{val:,}만원", va="center")
    ax.set_ylabel("연식")
else:
    bins = list(range(0, 401, 50))
    labels = [f"{i//10}만~{(i+50)//10}만km" for i in bins[:-1]]
    filtered["주행구간"] = pd.cut(filtered["키로수"], bins=bins, labels=labels, right=False)
    km_price = filtered.groupby("주행구간")["가격(숫자)"].mean().round().astype(int).sort_index(ascending=False)
    km_price.plot(kind="barh", ax=ax, color="orange")
    for i, (val, idx) in enumerate(zip(km_price, km_price.index)):
        ax.text(val + 50, i, f"{val:,}만원", va="center")
    ax.set_ylabel("주행거리")

ax.invert_yaxis()
ax.set_xlabel("평균 시세 (만원)")
st.pyplot(fig)

# 📘 유용한 팁
with st.expander("📈 중고차 시세 관련 팁 보기", expanded=False):
    st.markdown("""
    - ✅ 신차 대비 감가율이 높은 차량은 **2~3년차 모델**에서 시세 경쟁력이 있습니다.  
    - ✅ 동일 모델의 **연료 유형(가솔린/LPG/디젤)** 에 따라 시세 차이가 크므로 주의하세요.
    """)

# 📋 매물 목록 확인
with st.expander("📄 매물 목록 보기"):
    renamed_df = filtered.rename(columns={"가격(숫자)": "가격(만원)"})
    try:
        st.dataframe(renamed_df[["회사", "모델", "연식(수)", "키로수", "가격(만원)"]])
    except:
        st.write("표시할 데이터가 없습니다.")
