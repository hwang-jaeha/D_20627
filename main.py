import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터를 바탕으로 시간에 따른 변화를 탐색합니다.")


# 1. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df = pd.read_csv(url)

    # 날짜 열(8자리 숫자/문자열)을 datetime 객체로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df


df = load_data()

st.divider()

# ==========================================
# 구역 1: 영화별 일관객 점유율 (도넛 그래프)
# ==========================================
st.header("📌 구역 1: 영화별 일관객 점유율")

# 영화 선택 드롭다운 (영화명 기준 오름차순 정렬)
movie_list = sorted(df["영화명"].unique())
selected_movie = st.selectbox("영화를 선택하세요", movie_list)

# 선택한 영화 데이터 필터링
filtered_df = df[df["영화명"] == selected_movie].copy()
filtered_df["날짜_str"] = filtered_df["날짜"].dt.strftime("%Y-%m-%d")

# 플롯리 도넛 그래프 생성 (hole 파라미터로 도넛 형태 구현)
fig1 = px.pie(
    filtered_df,
    names="날짜_str",
    values="일관객",
    title=f"[{selected_movie}] 날짜별 일관객 비율",
    hole=0.4,
)

# 마우스 오버(Hover) 툴팁 및 표시 형식 설정
fig1.update_traces(
    hovertemplate="<b>날짜:</b> %{label}<br><b>일관객:</b> %{value:,}명 (%{percent})<extra></extra>",
    textinfo="percent+label",
)

# 그래프 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명 텍스트
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    f"선택한 영화({selected_movie})의 전체 상영 기간 일관객 총합 중 특정 날짜가 차지하는 관객 비중과 집중도를 한눈에 비교할 수 있습니다."
)

st.divider()

# ==========================================
# 구역 2: [추가 예정] 추후 새로운 시간 분석 그래프 추가 구역
# ==========================================
st.header("📌 구역 2: 시간 관련 추가 분석 (예정)")
st.caption(
    "이곳에 '월별 총 관객수 추이', '요일별 관객 비중' 등 새로운 시간 관련 그래프를 추가할 수 있습니다."
)
