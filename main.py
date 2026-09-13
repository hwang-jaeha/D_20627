import pandas as pd
import plotly.express as px
import streamlit as st

# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 매번 불러오지 않고 캐싱 처리(재사용)합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치가 포함된 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 datetime 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 기준일자 순서대로 정렬 (오름차순)
    df = df.sort_values(by="기준일자")

    return df


# 페이지 기본 설정
st.set_page_config(page_title="영화 박스오피스 대시보드", layout="wide")
st.title("🎬 영화 박스오피스 관객수 분석")

# 데이터 로드
df = load_data()

# [3. 영화 선택 기능]
# 누적관객수 기준으로 영화 목록 정렬 (영화별 최대 누적관객수 추출 후 내림차순)
movie_rank = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에 영화 선택 드롭다운 생성
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요:", movie_rank
)

# 선택된 영화 데이터 필터링
filtered_df = df[df["영화명"] == selected_movie]

# [5. 구역 나누기 - 첫 번째 구역]
st.header(f"📌 '{selected_movie}' 관객수 추이")

# [4. 선그래프 그리기]
# Plotly를 사용하여 기준일자별 해당일관객수 선 그래프 생성
fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"{selected_movie} - 일별 관객수 변화",
    markers=True,  # 데이터 지점에 점 표시
)

# 그래프 레이아웃 커스텀
fig1.update_layout(
    xaxis_title="기준일자", yaxis_title="해당일 관객수(명)", hovermode="x unified"
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig1, use_container_width=True)

# [5. 그래프 하단 설명 문구 구역]
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 상영 기간 동안 일별 관객수의 증감 추이 및 Peak(최고 관객수 발생일)를 확인할 수 있습니다."
)

st.divider()  # 구역 구분을 위한 위젯

# [5. 향후 추가될 그래프를 위한 예시 구역]
st.header("📌 추가 분석 구역 (추후 업데이트 예정)")
st.info("여기에 추가 그래프가 들어갈 예정입니다.")
st.caption("💡 **이 그래프로 알 수 있는 것:** (설명 문구가 들어갈 자리입니다.)")
