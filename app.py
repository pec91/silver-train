import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 나눔고딕 폰트 설정
font_path = "./NanumGothic.ttf"
fm.fontManager.addfont(font_path)
plt.rc("font", family="NanumGothic")

# 엑셀 데이터 불러오기
df = pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

# 모델 요약 생성
model_group = df.groupby(["사회", "모델"])
model_summary = model_group["연식(수)"].agg(["min", "max"]).reset_index()
model_summary["모델명표시"] = model_summary["모델"] + " (" + model_summary["min"].astype(str) + "년~" + model_summary["max"].astype(str) + "년시)"

# 기본 선택값 설정
default_index = model_summary[(model_summary["회사"] == "현대") & (model_summary["모델"] == "그랜저 IG")].index[0]

# 제목 및 설명 표시
st.title("🚗 중고차 최신시세조회")
st.write("간단한 필터를 통해 원하는 중고차 모델의 **연식별 및 키로수별 평균 시세**를 확인할 수 있습니다.")

# 모델 선택
selected_display = st.selectbox("🚗 모델 선택", model_summary["모델명표시"].tolist(), index=default_index)
selected_row = model_summary[model_summary["모델명표시"] == selected_display].iloc[0]
selected_company = selected_row["회사"]
selected_model = selected_row["모델"]
filtered_df = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# 보기 옵션
st.subheader("📊 보기 옵션 선택")
option = st.radio("보기옵션", ["연식별 시세", "키로수별 시세"])

# 시세 요약 텍스트
summary_text = "💬 **{} 중고차 시세는** ".format(selected_model)
price_summary = filtered_df.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False).round().astype(int)
summary_text += " ・ ".join([f"{year}년시 {price:,}만원" for year, price in price_summary.items()]) + " 입니다."
st.markdown(summary_text)

# 시세 차트
if option == "연식별 시세":
    avg_by_year = price_summary
    st.subheader(f"📈 {selected_model} 연식별 시세 평균 중고차 시세")
    fig, ax = plt.subplots()
    avg_by_year.plot(kind="barh", ax=ax, color="orange")
    for i, v in enumerate(avg_by_year):
        ax.text(v + 50, i, f"{v:,}만원", va="center")
    ax.invert_yaxis()
    ax.set_xlabel("평균 시세 (만원)")
    ax.set_ylabel("연식")
    st.pyplot(fig)
else:
    st.subheader(f"📉 {selected_model} 키로수별 평균 중고차 시세")
    bins = list(range(0, 401000, 50000))
    labels = [f"{i//10000}~{(i+50000)//10000}만km" for i in bins[:-1]]
    filtered_df["키로수구간"] = pd.cut(filtered_df["키로수"], bins=bins, labels=labels, right=False)
    avg_by_km = filtered_df.groupby("키로수구간")["가격(숫자)"].mean().round().astype(int)
    avg_by_km = avg_by_km[::-1]
    fig, ax = plt.subplots()
    avg_by_km.plot(kind="barh", ax=ax, color="orange")
    for i, v in enumerate(avg_by_km):
        ax.text(v + 50, i, f"{v:,}만원", va="center")
    ax.set_xlabel("평균 시세 (만원)")
    ax.set_ylabel("키로수")
    st.pyplot(fig)

# 팁 표시
with st.expander("📌 중고차 시세 관련 팁 보기"):
    st.markdown("""
    ✔️ 신차 대비 감가율이 높은 차량은 2~3년차 모델에서 시세 경쟁력이 있습니다.  
    ✔️ 동일 모델의 연료 유형(가솔린/LPG/디젤)에 따라 시세 차이가 크므로 주의하세요.
    """)

# 매물 리스트
with st.expander("📋 매물 목록 보기"):
    renamed_df = filtered_df.rename(columns={"가격(숫자)": "가격(만원)"})
    st.dataframe(renamed_df[["회사", "모델", "연식(수)", "키로수", "가격(만원)"]].reset_index(drop=True))
