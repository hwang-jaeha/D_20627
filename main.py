import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# 전체 영화 목록 (누적관객수 내림차순 정렬)
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
# [세 번째 구역: 조건부(TOP10 20일 이상) 상위 5개 영화 다중 선 그래프]
# ==========================================
st.header("📌 3. 장기 흥행(TOP 10 20일 이상) 영화 TOP 5 흥행 비교")

# 1) 등장 일수(행 개수) 계산
days_in_top10 = df.groupby("영화명").size()

# 2) 20일 이상 진입한 영화 필터링
movies_over_20days = days_in_top10[days_in_top10 >= 20].index

# 3) 상위 5개 영화 선별
top5_filtered_movies = (
    df[df["영화명"].isin(movies_over_20days)]
    .groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

# 4) TOP 5 데이터 필터링
top5_filtered_df = df[df["영화명"].isin(top5_filtered_movies)]

# Plotly 다중 선 그래프 생성
fig3 = px.line(
    top5_filtered_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="TOP 10에 20일 이상 진입한 영화 중 누적관객수 TOP 5 추이 비교",
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
    "💡 **이 그래프로 알 수 있는 것:** 단기 반짝 흥행이 아닌 최소 20일 이상 박스오피스 상위권(TOP 10)을 유지하며 꾸준히 관객을 모은 대표 장기 흥행작 5편의 성장 속도를 비교해볼 수 있습니다."
)

st.divider()  # 구역 구분선


# ==========================================
# [네 번째 구역: 전체 TOP10 일별 총관객수 7일 이동평균선 그래프]
# ==========================================
st.header("📌 4. 박스오피스 전체 관객수 변동 및 7일 이동평균 추이")

# 1) 기준일자별 TOP10 영화 전체의 해당일관객수 합계 계산
daily_total_df = (
    df.groupby("기준일자")["해당일관객수"]
    .sum()
    .reset_index()
    .sort_values(by="기준일자")
)

# 2) 7일 이동평균 계산 (rolling window=7)
daily_total_df["7일_이동평균"] = (
    daily_total_df["해당일관객수"].rolling(window=7, min_periods=1).mean()
)

# 3) Plotly graph_objects(go)를 사용하여 커스텀 겹쳐그리기 그래프 생성
fig4 = go.Figure()

# (1) 일별 총관객수 (원본 선: 연하게)
fig4.add_trace(
    go.Scatter(
        x=daily_total_df["기준일자"],
        y=daily_total_df["해당일관객수"],
        mode="lines",
        name="일별 총관객수 (일간)",
        line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5),  # 반투명 회색 선
    )
)

# (2) 7일 이동평균선 (진하게)
fig4.add_trace(
    go.Scatter(
        x=daily_total_df["기준일자"],
        y=daily_total_df["7일_이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#E50914", width=3),  # 진한 붉은색 두꺼운 선
    )
)

# 그래프 레이아웃 커스텀
fig4.update_layout(
    title="기준일자별 TOP 10 전체 관객수 합계 및 7일 이동평균",
    xaxis_title="기준일자",
    yaxis_title="총 관객수(명)",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig4, use_container_width=True)

# 그래프 하단 설명 문구
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 주말과 평일 간의 심한 관객수 변동(노이즈)을 평탄화(7일 이동평균)하여, 전체 극가장 관객수의 전반적인 시장 트렌드와 성수기·비수기 흐름을 명확히 파악할 수 있습니다."
)

st.divider()  # 구역 구분선


# ==========================================
# [다섯 번째 구역: 월별 전체 관객수 합계 막대그래프]
# ==========================================
st.header("📌 5. 월별 박스오피스 총 관객수 비교")

# 1) '기준일자'를 기반으로 '연-월(YYYY-MM)' 컬럼 생성
daily_total_df["연월"] = daily_total_df["기준일자"].dt.to_period("M").astype(str)

# 2) 월 단위로 묶어서 일별 총관객수를 합산
monthly_total_df = (
    daily_total_df.groupby("연월")["해당일관객수"]
    .sum()
    .reset_index()
    .rename(columns={"해당일관객수": "월별총관객수"})
)

# 3) Plotly를 사용하여 월별 막대그래프 생성
fig5 = px.bar(
    monthly_total_df,
    x="연월",
    y="월별총관객수",
    title="월별 극장가 총 관객수 집계",
    text_auto=".2s",  # 막대 상단에 간략화된 수치 레이블 표시 (예: 1.2M)
)

# 그래프 레이아웃 커스텀
fig5.update_layout(
    xaxis_title="월(Year-Month)",
    yaxis_title="총 관객수(명)",
    xaxis=dict(type="category"),  # 월 항목이 문자열로 깔끔하게 정렬되도록 지정
)

# 막대 색상 및 디자인 설정
fig5.update_traces(marker_color="#2b5c8f")

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig5, use_container_width=True)

# 그래프 하단 설명 문구
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 연중 어떤 월(달)에 극장 방문 관객 수가 가장 많았는지 월별 총 수치를 직관적으로 비교하여 영화 시장의 월별 시즌성(성수기/비수기)을 파악할 수 있습니다."
)
