import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 한글 포트 (너널 포트가 존재할 경우만 적용)
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="중고차 최신시세조회", page_icon="🚗", layout="centered")

@st.cache_data
def load_data():
    return pd.read_excel("used_cars.xlsx", sheet_name="Sheet1")

df = load_data()

# 기본사 값
default_company = "현대"
default_model = "그래낭 IG"

st.markdown("""
<h1 style='color:gold;'>🚗 중고차 최신시세조회</h1>
중고차 가격 데이터를 바탕으로 연시별, 키로수별 평균 시세를 통계창으로 해석합니다.<br>
제조사를 선택하고, 모델과 연시를 고르세요.
""", unsafe_allow_html=True)

# 회사 선택
company_list = sorted(df["회사"].dropna().unique().tolist())
selected_company = st.selectbox("🚗 회사 선택", company_list, index=company_list.index(default_company))

# 모델 및 연시 범위
model_list = df[df["\ud68c\uc0ac"] == selected_company]["\ubaa8\ub378"].dropna().unique().tolist()
if not model_list:
    st.warning(f"\uc120\ud0dd\ud55c \ud68c\uc0ac '{selected_company}'\uc5d0 \ud574\ub2f9\ud558\ub294 \ubaa8\ub378\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.")
    st.stop()

model_years = df[df["\ubaa8\ub378"].isin(model_list)].groupby("\ubaa8\ub378")["\uc5f0\uc2dc(\uc218)"].agg(["min", "max"])
model_summary = pd.DataFrame({
    "\ubaa8\ub378": model_years.index,
    "\uc5f0\uc2dc\ubc94\uc704": model_years.apply(lambda x: f"{int(x['min'])}\ub144~{int(x['max'])}\ub144\uc2dc", axis=1),
})
model_summary["\ubaa8\ub378\uba85 \ud45c\uc2dc"] = model_summary["\ubaa8\ub378"] + " (" + model_summary["\uc5f0\uc2dc\ubc94\uc704"] + ")"

# 기본 선택
model_options = model_summary["\ubaa8\ub378\uba85 \ud45c\uc2dc"].tolist()
default_label = f"{default_model} ({int(model_years.loc[default_model, 'min'])}\ub144~{int(model_years.loc[default_model, 'max'])}\ub144\uc2dc)"
default_index = model_options.index(default_label) if default_label in model_options else 0

selected_display = st.selectbox("🚗 모델 선택", model_options, index=default_index)
selected_model = selected_display.split(" (")[0]

# 보기 옵션
view_option = st.radio("\ud83d\udcca \ubcf4\uae30 \uc635\uc158 \uc120\ud0dd", ["\uc5f0\uc2dc\ubcc4 \uc2dc\uc138", "\ud0a4\ub85c\uc218\ubcc4 \uc2dc\uc138"], horizontal=True)

# 데이터 필터링
filtered = df[(df["\ud68c\uc0ac"] == selected_company) & (df["\ubaa8\ub378"] == selected_model)]

def build_summary(data):
    by_year = data.groupby("\uc5f0\uc2dc(\uc218)")["\uac00\uaca9(\uc22b\uc790)"]\
                .mean().sort_index(ascending=False).round(0)
    return f"{selected_model} \uc911\uace0\ucc28 \uc2dc\uc138\ub294 " + \
           " \u00b7 ".join([f"{int(y)}\ub144\uc2dc {int(p):,}\ub9cc\uc6d0" for y, p in by_year.items()]) + " \uc785\ub2c8\ub2e4."

st.markdown(f"💬 **{build_summary(filtered)}**")

# 그래프
if view_option == "\uc5f0\uc2dc\ubcc4 \uc2dc\uc138":
    group_col = "\uc5f0\uc2dc(\uc218)"
    xlabel = "\ud3c9\uade0 \uc2dc\uc138 (\ub9cc\uc6d0)"
    title = f"📈 {selected_model} \uc5f0\uc2dc\ubcc4 \ud3c9\uade0 \uc911\uace0\ucc28 \uc2dc\uc138"
else:
    bin_edges = list(range(0, int(df["\ud0a4\ub85c\uc218"].max()) + 50000, 50000))
    df["\ud0a4\ub85c\uc218\uad6c\uac04"] = pd.cut(df["\ud0a4\ub85c\uc218"], bins=bin_edges,
                              labels=[f"{x//10000}~{(x+50000)//10000}\ub9cckm" for x in bin_edges[:-1]])
    filtered["\ud0a4\ub85c\uc218\uad6c\uac04"] = df["\ud0a4\ub85c\uc218\uad6c\uac04"]
    group_col = "\ud0a4\ub85c\uc218\uad6c\uac04"
    xlabel = "\ud3c9\uade0 \uc2dc\uc138 (\ub9cc\uc6d0)"
    title = f"📉 {selected_model} \ud0a4\ub85c\uc218\ubcc4 \ud3c9\uade0 \uc911\uace0\ucc28 \uc2dc\uc138"

grouped = filtered.groupby(group_col)["\uac00\uaca9(\uc22b\uc790)"].mean().dropna().sort_index(ascending=False)

st.subheader(title)
fig, ax = plt.subplots(figsize=(7, len(grouped) * 0.45))
bars = ax.barh(grouped.index.astype(str), grouped.values, color="orange")
ax.invert_yaxis()
ax.set_xlabel(xlabel)

for bar in bars:
    width = bar.get_width()
    ax.text(width + 30, bar.get_y() + bar.get_height()/2, f"{int(width):,}\ub9cc\uc6d0", va='center', fontsize=9)

st.pyplot(fig)

st.subheader("📌 \uc694\uc57d \uc815\ubcf4")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("\ud3c9\uade0 \uc5f0\uc2dc", f"{int(filtered['\uc5f0\uc2dc(\uc218)'].mean())}\ub144")
with col2:
    st.metric("\ud3c9\uade0 \ud0a4\ub85c\uc218", f"{int(filtered['\ud0a4\ub85c\uc218'].mean()):,} km")
with col3:
    st.metric("\ub9e4\ubb3c \uc218", f"{len(filtered)}\uac74")

with st.expander("📋 \ub9e4\ubb3c \ubaa9록 \ubcf4기", expanded=False):
    st.dataframe(filtered.reset_index(drop=True)[["\ud68c\uc0ac", "\ubaa8\ub378", "\uc5f0\uc2dc(\uc218)", "\ud0a4\ub85c\uc218", "\uac00\uaca9(\uc22b\uc790)"]])

with st.expander("📈 \uc911\uace0\ucc28 \uc2dc\uc138 \uad00\ub828 \ud29c\ud1a0\uc9c0 \ubcf4기"):
    st.info("""
    ✔ 신차 대비 감가율이 높은 차량은 2~3년산 모델에서 시세 경쟁력이 있습니다.\n
    ✔ 동일 모델의 엔로 유형(가섹린/LPG/디젯)에 따라 시세 차이가 크니 주의하세요.
    """)
