import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)


@st.cache_data
def load_data():
    # 1년치(365일) 일별 박스오피스 10위권 기록을 불러옵니다.
    # CSV 파일에 헤더가 없으므로 names 옵션으로 열 이름을 직접 지정합니다.
    df = pd.read_csv(
        DATA_URL,
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
    # 여덟 자리 숫자로 된 날짜 열을 진짜 날짜로 바꿉니다.
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df


df = load_data()

# ── 그래프 1. 영화 하나의 흥행 곡선 ──────────────────────────
st.header("1. 한 영화의 흥행 곡선")

# 드롭다운으로 영화를 고릅니다.
movie_list = sorted(df["영화명"].dropna().unique())
movie = st.selectbox("영화를 고르세요", movie_list)

one = df[df["영화명"] == movie].sort_values("날짜")

if not one.empty:
    fig = px.line(
        one,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"<{movie}> 일별 관객수 추이",
        labels={"날짜": "날짜", "일관객": "일일 관객수(명)"},
    )
    fig.update_traces(
        hovertemplate="날짜 %{x|%Y-%m-%d}<br>관객 %{y:,}명<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")
else:
    st.warning("선택한 영화의 데이터가 없습니다.")

# ── 앞으로 그래프 2, 3, 4, 5가 이 아래에 추가됩니다 ──────────
