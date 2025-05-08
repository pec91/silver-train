
import streamlit as st
import pandas as pd

st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="wide")

st.markdown("<h1 style='color: gold;'>🚗 중고차 최신시세조회</h1>", unsafe_allow_html=True)

# 데이터 불러오기
df = pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

# 필터 항목
brands = st.multiselect("브랜드 선택", df["회사"].dropna().unique())
year_range = st.slider("연식 범위", int(df["연식(수)"].min()), int(df["연식(수)"].max()), (2010, 2023))
price_range = st.slider("가격 범위 (만원)", int(df["가격(숫자)"].min()), int(df["가격(숫자)"].max()), (200, 2000))
km_range = st.slider("키로수 범위", int(df["키로수"].min()), int(df["키로수"].max()), (0, 200000))

# 필터 적용
filtered_df = df[
    (df["회사"].isin(brands)) &
    (df["연식(수)"].between(year_range[0], year_range[1])) &
    (df["가격(숫자)"].between(price_range[0], price_range[1])) &
    (df["키로수"].between(km_range[0], km_range[1]))
]

st.write(f"조회된 차량 수: {len(filtered_df)}대")
st.dataframe(filtered_df)
