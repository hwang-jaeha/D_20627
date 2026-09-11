import datetime
import pandas as pd
import pytz
import requests
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="일별 박스오피스 조회", layout="wide")

st.title("🎬 일별 박스오피스 순위")


# --- 1. 한국 시간(KST) 기준 '어제' 날짜 구하기 ---
def get_yesterday_date():
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.datetime.now(kst)
    return (now_kst - datetime.timedelta(days=1)).date()


yesterday = get_yesterday_date()

# --- 2. 날짜 선택 달력 위젯 ---
# 선택 가능한 최대 날짜(max_value)를 '어제'로 설정하여 오늘 이후 날짜 선택 방지
selected_date = st.date_input(
    label="📅 조회할 날짜를 선택하세요 (최대 어제까지 가능)",
    value=yesterday,
    max_value=yesterday,
    min_value=datetime.date(2004, 1, 1),  # KOBIS 데이터 제공 시작 시점 즈음
)

target_date_str = selected_date.strftime("%Y%m%d")


# --- 3. API 데이터 요청 및 캐싱 함수 ---
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key, target_date):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None, f"서버 응답 오류 (상태 코드: {response.status_code})"

        data = response.json()

        # faultInfo 오류 상자 확인
        if "faultInfo" in data:
            message = data["faultInfo"].get(
                "message", "인증키 또는 요청이 유효하지 않습니다."
            )
            return None, f"API 오류: {message}"

        box_office_result = data.get("boxOfficeResult", {})
        daily_list = box_office_result.get("dailyBoxOfficeList", [])

        # 영화 목록이 비어 있는 경우
        if not daily_list:
            return None, "그날은 아직 집계 전입니다."

        return daily_list, None

    except Exception as e:
        return None, f"네트워크 요청 중 오류가 발생했습니다: {str(e)}"


# --- 4. 메인 로직 실행 ---

# Secrets에서 API 키 불러오기
if "KOBIS_KEY" not in st.secrets:
    st.error(
        "Secrets에 'KOBIS_KEY'가 설정되지 않았습니다.\n\n"
        "Streamlit Cloud 설정에서 KOBIS_KEY를 확인해 주세요."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]

# 데이터 불러오기
with st.spinner("박스오피스 데이터를 불러오는 중입니다..."):
    raw_data, error_msg = fetch_box_office_data(api_key, target_date_str)

# 데이터가 없거나 오류 발생 시 안내
if error_msg:
    if error_msg == "그날은 아직 집계 전입니다.":
        st.info(f"ℹ️ {error_msg}")
    else:
        st.error(
            f"❌ 데이터를 가져오지 못했습니다.\n\n"
            f"**오류 내용:** {error_msg}\n\n"
            f"**확인 사항:** API 키 등록 상태 및 네트워크 연결을 확인하세요."
        )
    st.stop()


# --- 5. 데이터 전처리 및 가공 ---
df = pd.DataFrame(raw_data)

# 숫자 데이터 변환 (rank, rankInten, audiCnt, audiAcc, scrnCnt)
numeric_cols = ["rank", "rankInten", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)


# [기능 1] 순위 증감(rankInten) 텍스트 및 화살표 가공
def format_rank_change(change):
    if change > 0:
        return f"🔺 {int(change)}"  # 빨간 위 화살표
    elif change < 0:
        return f"🔹 {abs(int(change))}"  # 파란 아래 화살표
    else:
        return "-"  # 변동 없음


df["순위변동"] = df["rankInten"].apply(format_rank_change)


# [기능 2] 누적관객 100만 이상 트로피 이모지 붙이기
def format_movie_name(row):
    name = row["movieNm"]
    if row["audiAcc"] >= 1000000:
        return f"🏆 {name}"
    return name


df["표시_영화명"] = df.apply(format_movie_name, axis=1)


# 표시용 데이터프레임 구성
df_display = df[
    [
        "rank",
        "순위변동",
        "표시_영화명",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
        "movieNm",
    ]
].copy()
df_display = df_display.sort_values(by="rank")


# --- 6. 화면 구성 ---

# 선택한 날짜 표시
formatted_date_display = selected_date.strftime("%Y년 %m월 %d일")
st.subheader(f"📊 {formatted_date_display} 박스오피스 결과")

# 1위 영화 지표 카드 (Metric)
top_1 = df_display.iloc[0]
st.markdown(f"### 🏆 1위 영화: **{top_1['표시_영화명']}**")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="일별 관객수", value=f"{int(top_1['audiCnt']):,} 명")
with col2:
    st.metric(label="누적 관객수", value=f"{int(top_1['audiAcc']):,} 명")
with col3:
    st.metric(label="스크린수", value=f"{int(top_1['scrnCnt']):,} 개")

st.divider()

# 관객수 상위 5편 막대그래프
st.subheader("📊 상위 5개 영화 관객수 비교")
top_5_df = df_display.head(5)
st.bar_chart(data=top_5_df, x="movieNm", y="audiCnt", use_container_width=True)

st.divider()

# 전체 10위 표 출력
st.subheader("📋 전체 순위표")

# 최종 표 가공 (컬럼명 변경 및 숫자 천 단위 쉼표 서식)
final_table = pd.DataFrame(
    {
        "순위": df_display["rank"],
        "전날 대비": df_display["순위변동"],
        "영화명": df_display["표시_영화명"],
        "개봉일": df_display["openDt"],
        "일별 관객수": df_display["audiCnt"].apply(lambda x: f"{int(x):,}"),
        "누적 관객수": df_display["audiAcc"].apply(lambda x: f"{int(x):,}"),
        "스크린수": df_display["scrnCnt"].apply(lambda x: f"{int(x):,}"),
    }
)

st.dataframe(final_table, hide_index=True, use_container_width=True)
