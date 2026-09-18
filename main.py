import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 데이터 로드
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    layout="wide",
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown("---")


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    # 불러오는 열 정의: 날짜, 순위, 영화코드, 영화명, 일관객, 누적관객, 스크린수, 상영횟수
    df = pd.read_csv(
        url,
        names=[
            "날짜",
            "순위",
            "영화코드",
            "영화명",
            "일관객",
            "누적관객",
            "스크린수",
            "상영횟수",
        ],
    )

    # '날짜' 열을 문자열로 변환 후 datetime 객체로 변환 (YYYYMMDD 형식)
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df


df = load_data()


# -----------------------------------------------------------------------------
# [구역 1] 선택한 영화의 일관객 변화
# -----------------------------------------------------------------------------
st.header("📌 구역 1: 영화별 일관객수 추이")

# 영화 목록 추출 (알파벳/가나다순 정렬)
movie_list = sorted(df["영화명"].dropna().unique())

# 드롭다운 선택
selected_movie = st.selectbox(
    "조회할 영화를 선택하세요:",
    options=movie_list,
    index=0,
)

# 선택한 영화 데이터 필터링 및 날짜순 정렬
movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

if not movie_df.empty:
    # Plotly 선 그래프 생성
    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        title=f"<{selected_movie}> 일별 관객수 변화",
        labels={"날짜": "날짜", "일관객": "일일 관객수(명)"},
        markers=True,
    )

    # 마우스 오버 시 날짜와 관객수 표기 포맷 설정
    fig.update_traces(
        hovertemplate="<b>날짜</b>: %{x|%Y-%m-%d}<br><b>일관객수</b>: %{y:,}명<extra></extra>"
    )

    # 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 그래프 해설 문구 위치
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 일별 관객수 증감 흐름과 주요 전성기(피크) 시점을 파악할 수 있습니다."
    )
else:
    st.warning("선택한 영화의 데이터가 없습니다.")

st.markdown("---")


# -----------------------------------------------------------------------------
# [구역 2] 추후 그래프 추가 영역 (예시 구조)
# -----------------------------------------------------------------------------
st.header("📌 구역 2: (추가 예정 구역)")
st.caption("새로운 시간 축 기반 시각화 그래프가 들어갈 공간입니다.")

# 예시 자리 표시
# fig2 = px.line(...)
# st.plotly_chart(fig2, use_container_width=True)
st.info("💡 **이 그래프로 알 수 있는 것:** (그래프 추가 후 해석 문구를 작성하세요)")
