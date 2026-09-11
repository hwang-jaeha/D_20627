import datetime
import pandas as pd
import pytz
import requests
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(page_title="어제 박스오피스 순위", layout="wide")

st.title("🎬 어제 일별 박스오피스 TOP 10")


# --- 1. 한국 시간(KST) 기준 '어제' 날짜 계산 ---
def get_yesterday_kst():
    # 서버 시계와 상관없이 한국 시간대를 설정합니다.
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.datetime.now(kst)
    # 어제 날짜 구하기
    yesterday = now_kst - datetime.timedelta(days=1)
    # API 요청 형식인 YYYYMMDD 형태로 변환
    return yesterday.strftime("%Y%m%d")


# --- 2. API 데이터 요청 및 캐싱 함수 ---
# @st.cache_data를 사용하여 1시간(3600초) 동안 동일 요청 결과를 기억합니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key, target_date):
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        response = requests.get(url, params=params, timeout=10)
        # HTTP 응답 상태 코드 확인
        if response.status_code != 200:
            return None, f"서버 응답 오류 (상태 코드: {response.status_code})"

        data = response.json()

        # 인증키 오류 등으로 인한 faultInfo 반환 여부 확인
        if "faultInfo" in data:
            message = data["faultInfo"].get(
                "message", "인증키 또는 요청이 유효하지 않습니다."
            )
            return None, f"API 오류: {message}"

        # 정상 데이터 구조 확인
        box_office_result = data.get("boxOfficeResult", {})
        daily_list = box_office_result.get("dailyBoxOfficeList", [])

        if not daily_list:
            return None, "해당 날짜의 박스오피스 데이터가 비어 있습니다."

        return daily_list, None

    except Exception as e:
        return None, f"네트워크 요청 중 오류가 발생했습니다: {str(e)}"


# --- 3. 메인 로직 실행 ---

# Secrets에서 API 키 불러오기 확인
if "KOBIS_KEY" not in st.secrets:
    st.error(
        "Secrets에 'KOBIS_KEY'가 설정되지 않았습니다.\n\n"
        "**확인 사항:**\n"
        "1. Streamlit Cloud의 앱 설정에서 `Secrets` 메뉴를 엽니다.\n"
        "2. `KOBIS_KEY = '발급받은_키_문자열'` 형식으로 등록했는지 확인하세요."
    )
    st.stop()

api_key = st.secrets["KOBIS_KEY"]
target_date = get_yesterday_kst()

# 한국식 날짜 표시 형식 (YYYY년 MM월 DD일)
formatted_date = datetime.datetime.strptime(target_date, "%Y%m%d").strftime(
    "%Y년 %m월 %d일"
)
st.subheader(f"📅 기준일: {formatted_date}")

# 데이터 가공 시작
with st.spinner("박스오피스 데이터를 불러오는 중입니다..."):
    raw_data, error_msg = fetch_box_office_data(api_key, target_date)

# 오류가 있는 경우 사용자 안내 표시
if error_msg:
    st.error(
        f"❌ 데이터를 가져오지 못했습니다.\n\n"
        f"**오류 내용:** {error_msg}\n\n"
        f"**확인해야 할 사항:**\n"
        f"- Streamlit Secrets의 `KOBIS_KEY` 값이 정확한지 확인하세요.\n"
        f"- 영화진흥위원회(KOBIS) API 키 발급 상태를 확인하세요.\n"
        f"- 네트워크 연결 상태를 확인하세요."
    )
    st.stop()

# --- 4. 데이터 전처리 (문자열 -> 숫자 변환) ---
df = pd.DataFrame(raw_data)

# 숫자형으로 변환할 컬럼 지정
numeric_columns = ["rank", "audiCnt", "audiAcc", "scrnCnt"]
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# 필요한 컬럼 정렬 및 이름 변경
df_display = df[
    ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
].copy()
df_display.columns = [
    "순위",
    "영화명",
    "개봉일",
    "일별 관객수",
    "누적 관객수",
    "스크린수",
]
df_display = df_display.sort_values(by="순위")


# --- 5. 화면 구성 ---

# 1위 영화 지표 카드 (Metric)
top_1 = df_display.iloc[0]
st.markdown(f"### 🏆 1위 영화: **{top_1['영화명']}**")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="어제 관객수", value=f"{top_1['일별 관객수']:,} 명")
with col2:
    st.metric(label="누적 관객수", value=f"{top_1['누적 관객수']:,} 명")
with col3:
    st.metric(label="스크린수", value=f"{top_1['스크린수']:,} 개")

st.divider()

# 관객수 상위 5편 막대그래프
st.subheader("📊 상위 5개 영화 관객수 비교")
top_5_df = df_display.head(5)

# Streamlit 기본 막대그래프 (x: 영화명, y: 일별 관객수)
st.bar_chart(data=top_5_df, x="영화명", y="일별 관객수", use_container_width=True)

st.divider()

# 전체 10위 표 출력
st.subheader("📋 전체 순위표")

# 표 형식 맞춤 (숫자에 천 단위 쉼표 추가)
formatted_df = df_display.copy()
formatted_df["일별 관객수"] = formatted_df["일별 관객수"].apply(
    lambda x: f"{x:,}"
)
formatted_df["누적 관객수"] = formatted_df["누적 관객수"].apply(
    lambda x: f"{x:,}"
)
formatted_df["스크린수"] = formatted_df["스크린수"].apply(lambda x: f"{x:,}")

st.dataframe(formatted_df, hide_index=True, use_container_width=True)
