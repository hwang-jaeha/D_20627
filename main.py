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
st.subheader('장르별 영화 편수 분포')

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

# 그래프 아래 '이 그래프로 알 수 있는 것' 구역
st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("박스오피스 상위권에 가장 많이 포진해 있는 주력 영화 장르가 무엇인지, 전체 영화 중 특정 장르가 차지하는 비중을 직관적으로 파악할 수 있습니다.")

# 두 번째 그래프 (분포와 관계 주제에 맞춘 첫 주 관객수 vs 총 관객수 산점도)
st.markdown("---")
st.subheader('개봉 첫 주 관객수와 총 관객수의 관계')

fig_relation = px.scatter(
    df, 
    x='first_week_audi', 
    y='total_audi', 
    hover_name='movieNm',
    labels={'first_week_audi': '개봉 첫 주 관객수', 'total_audi': '총 관객수'}
)
st.plotly_chart(fig_relation, use_container_width=True)

st.markdown("---")
st.markdown("**이 그래프로 알 수 있는 것**")
st.info("개봉 첫 주에 동원한 관객 규모가 최종 흥행 성적(총 관객수)에 미치는 영향력과 상관관계를 확인할 수 있습니다.")
