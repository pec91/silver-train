import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ✅ 한글 폰트 설정
font_path = "NanumGothic.ttf"
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'NanumGothic'

# ✅ 페이지 기본 설정
st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="wide")
st.title("🚗 중고차 최신시세조회")
st.markdown("간단한 필터를 통해 원하는 중고차 모델의 **연식별 및 키로수별 평균 시세**를 확인할 수 있습니다.")

# ✅ 데이터 불러오기
df = pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

# ✅ 컬럼 이름 정리
renamed_df = df.rename(columns={
    "회사": "회사", "모델": "모델", "연식(수)": "연식",
    "키로수": "키로수", "가격(숫자)": "가격(만원)"
})

# ✅ 모델 정리 및 기본 선택값 설정
model_summary = (
    renamed_df.groupby(["회사", "모델"])
    .agg(최소연식=("연식", "min"), 최대연식=("연식", "max"))
    .reset_index()
)
model_summary["모델명 표시"] = model_summary.apply(
    lambda row: f"{row['회사']} {row['모델']} ({row['최소연식']}년~{row['최대연식']}년식)", axis=1
)

default_model = "현대 그랜저 IG"
default_index = model_summary[model_summary["모델명 표시"].str.contains(default_model)].index[0]

# ✅ 사용자 선택
selected_display = st.selectbox("🚘 모델 선택", model_summary["모델명 표시"].tolist(), index=default_index)
selected_row = model_summary[model_summary["모델명 표시"] == selected_display].iloc[0]
selected_company = selected_row["회사"]
selected_model = selected_row["모델"]

filtered = renamed_df[(renamed_df["회사"] == selected_company) & (renamed_df["모델"] == selected_model)]

# ✅ 보기 옵션
st.subheader("📊 보기 옵션 선택")
mode = st.radio("보기옵션", ["연식별 시세", "키로수별 시세"])

if mode == "연식별 시세":
    avg_by_year = filtered.groupby("연식")["가격(만원)"].mean().sort_index(ascending=False)
    summary_text = " · ".join([f"{year}년식 {int(price):,}만원" for year, price in avg_by_year.items()])
    st.markdown(f"💬 **{selected_model} 중고차 시세는** {summary_text} 입니다.")

elif mode == "키로수별 시세":
    bins = list(range(0, 401000, 50000))
    labels = [f"{i//10000}만~{(i+50000)//10000}만km" for i in bins[:-1]]
    filtered["키로수 구간"] = pd.cut(filtered["키로수"], bins=bins, labels=labels, right=False)
    avg_by_km = filtered.groupby("키로수 구간")["가격(만원)"].mean().sort_index(ascending=False)
    summary_text = " · ".join([f"{label} {int(price):,}만원" for label, price in avg_by_km.items()])
    st.markdown(f"💬 **{selected_model} 키로수별 시세는** {summary_text} 입니다.")

# ✅ 시각화
if mode == "연식별 시세":
    st.subheader(f"📉 {selected_model} 연식별 시세 평균 중고차 시세")
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(avg_by_year.index.astype(str), avg_by_year.values, color='orange')
    ax.invert_yaxis()
    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2, f"{int(bar.get_width()):,}만원", va='center')
    ax.set_xlabel("평균 시세 (만원)")
    st.pyplot(fig)

elif mode == "키로수별 시세":
    st.subheader(f"📉 {selected_model} 키로수별 평균 중고차 시세")
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(avg_by_km.index.astype(str), avg_by_km.values, color='orange')
    ax.invert_yaxis()
    for i, bar in enumerate(bars):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2, f"{int(bar.get_width()):,}만원", va='center')
    ax.set_xlabel("평균 시세 (만원)")
    st.pyplot(fig)

# ✅ 유용한 팁
with st.expander("📈 중고차 시세 관련 팁 보기"):
    st.info("✔️ 신차 대비 감가율이 높은 차량은 2~3년차 모델에서 시세 경쟁력이 있습니다.\n"
            "✔️ 동일 모델의 연료 유형(가솔린/LPG/디젤)에 따라 시세 차이가 크므로 주의하세요.")

# ✅ 전체 데이터 보기
with st.expander("📋 매물 목록 보기"):
    try:
        st.dataframe(filtered[["회사", "모델", "연식", "키로수", "가격(만원)"]])
    except:
        st.error("⚠️ 데이터 표시에 실패했습니다. 컬럼명을 확인하세요.")
