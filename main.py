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

# 플롯리 도넛 그래프 생성
fig1 = px.pie(
    filtered_df,
    names="날짜_str",
    values="일관객",
    title=f"[{selected_movie}] 날짜별 일관객 비율",
    hole=0.4,
)

fig1.update_traces(
    hovertemplate="<b>날짜:</b> %{label}<br><b>일관객:</b> %{value:,}명 (%{percent})<extra></extra>",
    textinfo="percent+label",
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    f"선택한 영화({selected_movie})의 전체 상영 기간 일관객 총합 중 특정 날짜가 차지하는 관객 비중과 집중도를 한눈에 비교할 수 있습니다."
)

st.divider()

# ==========================================
# 구역 2: 관객수 TOP 5 영화의 날짜별 일관객 추이 (선 그래프)
# ==========================================
st.header("📌 구역 2: 관객수 TOP 5 영화의 날짜별 일관객 추이")

top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .nlargest(5)
    .index
    .tolist()
)

top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    title="총 관객수 상위 5개 영화의 일별 관객수 변화 비교",
    labels={"날짜": "날짜", "일관객": "일일 관객수", "영화명": "영화 제목"},
    markers=True,
)

fig2.update_traces(
    hovertemplate="<b>영화:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>"
)
fig2.update_layout(
    hovermode="x unified",
    legend_title_text="영화 제목 (클릭 시 토글)",
)

st.plotly_chart(fig2, use_container_width=True)

top5_str = ", ".join(top5_movies)
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    f"기간 내 관객수 상위 5개 영화({top5_str})의 흥행 시기 겹침 여부와 일일 최대 관객수 동원력을 서로 비교해 볼 수 있으며, 범례의 영화명을 클릭하여 원하는 영화만 켜고 끌 수 있습니다."
)

st.divider()

# ==========================================
# 구역 3: 날짜별 Top 10 일관객 합계 추이 (영역 그래프 + TOP 3 주석)
# ==========================================
st.header("📌 구역 3: 일별 박스오피스 TOP 10 총 관객수 추이")

# 날짜별 10위권 일관객 합계 계산
daily_total = df.groupby("날짜")["일관객"].sum().reset_index()

# 합계 상위 3일 추출
top3_days = daily_total.nlargest(3, "일관객")

# 영역 그래프(Area Chart) 생성
fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="일별 박스오피스 TOP 10 전체 관객수 합계",
    labels={"날짜": "날짜", "일관객": "10위권 관객수 합계"},
)

fig3.update_traces(
    hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>총 관객수:</b> %{y:,}명<extra></extra>",
    line_color="#1f77b4",
)

# 관객수 합계 TOP 3 날짜에 에어로(화살표) 주석(Annotation) 표시
for rank, (_, row) in enumerate(top3_days.iterrows(), start=1):
    date_str = row["날짜"].strftime("%Y-%m-%d")
    val = row["일관객"]

    fig3.add_annotation(
        x=row["날짜"],
        y=val,
        text=f"<b>{rank}위: {date_str}</b><br>({val:,}명)",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor="#d62728",
        ax=0,
        ay=-40,
        bgcolor="rgba(255, 255, 255, 0.85)",
        bordercolor="#d62728",
        borderwidth=1,
        font=dict(size=11, color="black"),
    )

fig3.update_layout(hovermode="x unified")

st.plotly_chart(fig3, use_container_width=True)

# TOP 3 날짜 텍스트 요약
top3_text_list = [
    f"{i+1}위 {row['날짜'].strftime('%Y-%m-%d')}({row['일관객']:,}명)"
    for i, (_, row) in enumerate(top3_days.iterrows())
]
top3_summary = ", ".join(top3_text_list)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "전체 극장가의 관객 유입 규모(시장 파이)의 성수기와 비수기를 한눈에 볼 수 있으며, "
    f"가장 많은 관객이 방문한 상위 3개 날짜[{top3_summary}]를 직관적으로 확인할 수 있습니다."
)

st.divider()

# ==========================================
# 구역 4: [추가 예정] 추후 새로운 시간 분석 그래프 추가 구역
# ==========================================
st.header("📌 구역 4: 시간 관련 추가 분석 (예정)")
st.caption(
    "이곳에 '월별 총 관객수 추이', '요일별 관객 비중' 등 새로운 시간 관련 그래프를 추가할 수 있습니다."
)
