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
# 누적관객수 기준으로 전체 영화 목록 정렬 (영화별 최대 누적관객수 추출 후 내림차순)
movie_rank = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에 개별 영화 선택 드롭다운 생성
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요:", movie_rank
)

# 선택된 단일 영화 데이터 필터링
filtered_df = df[df["영화명"] == selected_movie]


# ==========================================
# [첫 번째 구역: 개별 영화 일별 해당일관객수 선 그래프]
# ==========================================
st.header(f"📌 1. '{selected_movie}' 일별 관객수 추이")

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

# 그래프 하단 설명 문구
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 상영 기간 동안 일별 관객수의 증감 추이 및 Peak(최고 관객수 발생일)를 확인할 수 있습니다."
)

st.divider()  # 구역 구분선


# ==========================================
# [두 번째 구역: 개별 영화 누적관객수 영역차트]
# ==========================================
st.header(f"📌 2. '{selected_movie}' 누적관객수 성장 추이")

# Plotly를 사용하여 기준일자별 누적관객수 영역 차트(area chart) 생성
fig2 = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"{selected_movie} - 누적관객수 추이",
)

# 그래프 레이아웃 커스텀
fig2.update_layout(
    xaxis_title="기준일자", yaxis_title="누적 관객수(명)", hovermode="x unified"
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 하단 설명 문구
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 시간 흐름에 따른 {selected_movie}의 누적 관객수 증가 속도와 총 누적 관객 수의 도달 과정을 한눈에 파악할 수 있습니다."
)

st.divider()  # 구역 구분선


# ==========================================
# [세 번째 구역: 상위 5개 영화 누적관객수 비교 다중 선 그래프]
# ==========================================
st.header("📌 3. 누적관객수 TOP 5 영화 흥행 비교")

# 누적관객수 상위 5개 영화 이름 추출
top5_movies = movie_rank[:5]

# 전체 데이터 중 TOP 5 영화 데이터만 필터링
top5_df = df[df["영화명"].isin(top5_movies)]

# Plotly를 사용하여 5개 영화의 누적관객수를 한 그래프에 겹쳐서 작성
# color="영화명"을 지정하여 영화별로 색상 구분 및 범례(Legend) 자동 생성
fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="상위 5개 영화의 누적관객수 추이 비교",
)

# 그래프 레이아웃 커스텀
fig3.update_layout(
    xaxis_title="기준일자",
    yaxis_title="누적 관객수(명)",
    legend_title="영화 제목",
    hovermode="x unified",
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 하단 설명 문구
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 역대 박스오피스 상위 5개 영화 간의 누적 관객수 증가 속도와 최종 흥행 규모를 직접 비교해볼 수 있습니다."
)
