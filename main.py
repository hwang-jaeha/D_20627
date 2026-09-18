import streamlit as st
import pandas as pd
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

# 마우스 호버 시 영화명과 총 관객수가 표시되도록 설정
fig_treemap.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>"
)

st.plotly_chart(fig_treemap, use_container_width=True)

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("각 장르가 전체 총 관객수에서 차지하는 비중뿐만 아니라, 특정 장르 내에서 어떤 영화가 관객수를 주로 견인했는지 직관적으로 비교할 수 있습니다.")
