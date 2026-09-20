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

# 첫 번째 그래프: 장르별 영화 편수 도넛 그래프
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

# 두 번째 그래프: 장르-영화 트리맵 (총 관객수 기준)
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

# 세 번째 그래프: 총 관객수 히스토그램
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

# 최다 관객 영화 계산
top_movie_row = df.loc[df['total_audi'].idxmax()]
top_movie_name = top_movie_row['movieNm']
top_movie_audi = top_movie_row['total_audi']

# 가장 많은 영화가 집중된 관객수 구간 계산
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

# 네 번째 그래프: 개봉일 스크린수 vs 총 관객수 산점도
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
