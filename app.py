import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

# 회사 및 모델 필터
selected_company = st.selectbox("회사 선택", sorted(df["회사"].dropna().unique()))
models = df[df["회사"] == selected_company]["모델"].dropna().unique()
selected_model = st.selectbox("모델 선택", sorted(models))

# 해당 모델 필터링
filtered = df[(df["회사"] == selected_company) & (df["모델"] == selected_model)]

# 연식별 평균 가격 계산
avg_by_year = filtered.groupby("연식(수)")["가격(숫자)"].mean().sort_index(ascending=False)

# 📊 막대그래프 표시
st.subheader(f"{selected_model} 연식별 평균 중고차 시세")
fig, ax = plt.subplots()
avg_by_year.plot(kind="barh", ax=ax)
ax.invert_yaxis()
ax.set_xlabel("평균 시세 (만원)")
ax.set_ylabel("연식")
st.pyplot(fig)

# 📋 평균 정보 요약
st.subheader("📌 평균 정보")
st.write({
    "평균 연식": int(filtered["연식(수)"].mean()),
    "평균 키로수": f'{int(filtered["키로수"].mean()):,}km',
    "총 매물 수": len(filtered)
})
