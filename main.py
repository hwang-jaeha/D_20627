import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2", layout="wide")

st.title('영화 데이터 그래프 도감 2 - 분포와 관계')
st.write('최근 1년간 박스오피스 상위권에 진입한 216편의 영화 데이터를 바탕으로 장르별 분포와 주요 흥행 지표 간의 관계를 살펴봅니다.')

@st.cache_data
def load_data():
    url = 'https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv'
    df = pd.read_csv(url)
    # 세로막대 기호(|)가 포함된 장르의 경우 첫 번째 장르만 추출
    df['genre'] = df['genre'].apply(lambda x: str(x).split('|')[0].strip() if pd.notnull(x) else '기타')
    return df

df = load_data()

st.markdown("---")

# 1. 장르별 영화 편수 도넛 그래프
st.subheader('1. 장르별 영화 편수 분포')

genre_counts = df['genre'].value_counts().reset_index()
genre_counts.columns = ['genre', 'count']

fig_genre = px.pie(
    genre_counts, 
    names='genre', 
    values='count', 
    hole=0.4,
    labels={'genre': '장르', 'count': '편수'}
)
fig_genre.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_genre, use_container_width=True)

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("박스오피스 상위권에 가장 많이 포진해 있는 주력 영화 장르가 무엇인지, 전체 영화 중 특정 장르가 차지하는 비중을 직관적으로 파악할 수 있습니다.")

# 2. 장르-영화 트리맵 (총 관객수 기준)
st.markdown("---")
st.subheader('2. 장르 및 영화별 총 관객수 분포 (트리맵)')

fig_treemap = px.treemap(
    df,
    path=[px.Constant("전체"), 'genre', 'movieNm'],
    values='total_audi',
    hover_data={'movieNm': True, 'total_audi': ':,d'},
    labels={'movieNm': '영화명', 'total_audi': '총 관객수', 'genre': '장르'}
)

fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("각 장르가 전체 총 관객수에서 차지하는 비중뿐만 아니라, 특정 장르 내에서 어떤 영화가 관객수를 주로 견인했는지 직관적으로 비교할 수 있습니다.")

# 3. 총 관객수 히스토그램
st.markdown("---")
st.subheader('3. 총 관객수 히스토그램')

fig_hist = px.histogram(
    df,
    x='total_audi',
    nbins=20,
    labels={'total_audi': '총 관객수'},
)
fig_hist.update_layout(yaxis_title="영화 수")
st.plotly_chart(fig_hist, use_container_width=True)

# 최다 관객 영화 및 빈도 최다 구간 계산
top_movie_row = df.loc[df['total_audi'].idxmax()]
top_movie_name = top_movie_row['movieNm']
top_movie_audi = top_movie_row['total_audi']

counts, bin_edges = np.histogram(df['total_audi'], bins=20)
max_bin_idx = counts.argmax()
bin_start = int(bin_edges[max_bin_idx])
bin_end = int(bin_edges[max_bin_idx + 1])

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info(
    f"대부분의 영화는 **{bin_start:,}명 ~ {bin_end:,}명** 구간에 밀집되어 있으며, "
    f"가장 많은 관객을 동원한 영화는 **'{top_movie_name}'** (총 {top_movie_audi:,}명)입니다. "
    f"이를 통해 소수의 메가 히트작이 상위 관객수를 끌어올리는 오른쪽으로 치우친 분포 양상을 확인할 수 있습니다."
)

# 4. 개봉일 스크린수 vs 총 관객수 산점도
st.markdown("---")
st.subheader('4. 개봉일 스크린수와 총 관객수의 관계')

fig_scatter = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    hover_data={'first_scrn': ':,d', 'total_audi': ':,d', 'genre': True},
    labels={
        'first_scrn': '개봉일 스크린수',
        'total_audi': '총 관객수',
        'genre': '장르'
    }
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("개봉 첫날 확보한 스크린수가 최종 총 관객수에 얼마나 영향을 미치는지 양의 상관관계를 파악할 수 있으며, 장르별 스크린 확보 수준과 흥행 성과의 분포 양상을 비교할 수 있습니다.")

# 5. 주요 장르별 총 관객수 박스플롯
st.markdown("---")
st.subheader('5. 주요 장르별 총 관객수 분포 (상자 그림)')

genre_counts_series = df['genre'].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_major = df[df['genre'].isin(major_genres)]

fig_box = px.box(
    df_major,
    x='genre',
    y='total_audi',
    color='genre',
    hover_name='movieNm',
    hover_data={'total_audi': ':,d', 'genre': False},
    points='outliers',
    labels={
        'genre': '장르',
        'total_audi': '총 관객수'
    }
)

fig_box.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>총 관객수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("10편 이상 제작된 주요 장르 간의 관객수 중앙값과 변동성(분포 범위)을 비교할 수 있으며, 상자 밖의 이상치 점을 통해 해당 장르의 대표 대행진 흥행작들을 한눈에 확인할 수 있습니다.")

# 6. 버블 차트
st.markdown("---")
st.subheader('6. 스크린수, 총 관객수, 첫 주 관객수의 다차원 관계 (버블 차트)')

fig_bubble = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',
    color='genre',
    hover_name='movieNm',
    size_max=40,
    hover_data={
        'first_scrn': ':,d', 
        'total_audi': ':,d', 
        'first_week_audi': ':,d',
        'genre': True
    },
    labels={
        'first_scrn': '개봉일 스크린수',
        'total_audi': '총 관객수',
        'first_week_audi': '개봉 첫 주 관객수',
        'genre': '장르'
    }
)

st.plotly_chart(fig_bubble, use_container_width=True)

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("개봉일 스크린수(X축)와 최종 총 관객수(Y축)에 더해, 버블 크기(개봉 첫 주 관객수)를 함께 시각화함으로써 초반 흥행 기세가 최종 성적으로 이어졌는지 아니면 장기 입소문을 타며 역주행했는지 한 번에 종합적으로 비교·분석할 수 있습니다.")

# 7. 선버스트
st.markdown("---")
st.subheader('7. 제작 국가 및 장르 계층 구조 (선버스트)')

nation_genre_df = df.groupby(['nation', 'genre']).size().reset_index(name='movie_count')

fig_sunburst = px.sunburst(
    nation_genre_df,
    path=['nation', 'genre'],
    values='movie_count',
    labels={
        'nation': '제작 국가',
        'genre': '장르',
        'movie_count': '영화 편수'
    }
)

fig_sunburst.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<extra></extra>"
)

st.plotly_chart(fig_sunburst, use_container_width=True)

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("각 제작 국가가 전체 박스오피스 영화 편수에서 차지하는 비중과, 국가별로 주로 제작되어 공급되는 장르의 구성 계층 구조를 한눈에 파악할 수 있습니다.")

# 8. 질문 1: 10위권에 머문 날수는 대개 며칠쯤인가 (히스토그램)
st.markdown("---")
st.subheader('8. 10위권에 머문 날수는 대개 며칠쯤인가')

fig_q1 = px.histogram(
    df,
    x='days_in_top10',
    nbins=15,
    labels={'days_in_top10': '10위권 체류 일수'},
)
fig_q1.update_layout(yaxis_title="영화 수")
st.plotly_chart(fig_q1, use_container_width=True)

st.markdown("---")
st.markdown("**왜 이 그래프인가**")
st.info("단일 연속형 변수(체류 일수)의 빈도수 분포와 중심 경향을 확인하여 영화들이 대개 며칠 동안 상위권에 머무는지 파악하기에 히스토그램이 가장 적합합니다.")

# 9. 질문 2: 제작 국가별 영화 편수의 비율은 어떠한가 (파이 차트)
st.markdown("---")
st.subheader('9. 제작 국가별 영화 편수의 비율은 어떠한가')

nation_counts = df['nation'].value_counts().reset_index()
nation_counts.columns = ['nation', 'count']

fig_q2 = px.pie(
    nation_counts,
    names='nation',
    values='count',
    labels={'nation': '제작 국가', 'count': '영화 편수'}
)
fig_q2.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_q2, use_container_width=True)

st.markdown("---")
st.markdown("**왜 이 그래프인가**")
st.info("전체 데이터셋에서 각 제작 국가가 차지하는 상대적인 점유율과 점유 비율(%)을 한눈에 비교하기에 파이 차트(또는 도넛 차트)가 가장 직관적입니다.")

# 10. 질문 3: 10위권에 오래 머문 영화는 총 관객도 많은가 (2D 히스토그램 히트맵)
st.markdown("---")
st.subheader('10. 10위권에 오래 머문 영화는 총 관객도 많은가')

fig_q3_heatmap = px.density_heatmap(
    df,
    x='days_in_top10',
    y='total_audi',
    nbinsx=15,
    nbinsy=15,
    color_continuous_scale='Viridis',
    labels={
        'days_in_top10': '10위권에 머문 날수',
        'total_audi': '총 관객수'
    }
)

fig_q3_heatmap.update_layout(
    coloraxis_colorbar_title="영화 수"
)

st.plotly_chart(fig_q3_heatmap, use_container_width=True)

st.markdown("---")
st.markdown("**왜 이 그래프인가**")
st.info("두 연속형 변수(10위권 체류 일수와 총 관객수) 구간별로 영화 밀집도를 색상 명암으로 표현하여 관객수와 체류 일수의 밀집 패턴을 직관적으로 보여주기에 히트맵(2D Density Heatmap)이 적합합니다.")
