import streamlit as st
import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="국내 주식 확률 우위 스크리너 (≤50만원)",
    layout="wide"
)

st.title("📊 국내 주식 확률 우위 자동 스크리너 (1주 ≤ 50만원)")
st.markdown("""
**핵심 개념**
- 주가 수준과 무관
- 실제 자금 유입이 확인된 종목만
- 이미 상승을 시작했으나 과열되지 않은 구간
- 손실이 구조적으로 제한되는 위치
""")

today = datetime.today().strftime("%Y%m%d")

# -----------------------------
# 사이드바 파라미터
# -----------------------------
st.sidebar.header("🔧 스크리닝 조건")

MAX_PRICE = st.sidebar.number_input(
    "최대 주가 (원)", 10_000, 500_000, 500_000, 10_000
)

TRADING_RATIO = st.sidebar.slider(
    "20일 평균 거래대금 / 시가총액 (%)",
    0.01, 5.0, 2.0, 0.01
) / 100

LOOKBACK_DAYS = st.sidebar.slider(
    "가격 분석 기간 (일)", 40, 120, 60, 10
)

RISE_FROM_LOW = st.sidebar.slider(
    "저점 대비 상승률 (%)", 0, 80, 30, 5
) / 100

DROP_FROM_HIGH = st.sidebar.slider(
    "고점 대비 허용 하락 (%)", 5, 40, 20, 5
) / 100

MAX_DRAWDOWN = st.sidebar.slider(
    "저점 대비 최대 하락 (%)", 5, 50, 15, 5
) / 100

MAX_OUTPUT = st.sidebar.number_input(
    "최대 출력 종목 수", 1, 20, 5, 1
)

# -----------------------------
# 데이터 함수
# -----------------------------
@st.cache_data(show_spinner=False)
def get_price_filtered_stocks():
    tickers = stock.get_market_ticker_list(today, market="ALL")
    result = []

    for ticker in tickers:
        try:
            price = stock.get_market_ohlcv_by_date(
                today, today, ticker
            )["종가"].iloc[0]

            if price <= MAX_PRICE:
                result.append((ticker, price))
        except:
            continue

    return pd.DataFrame(result, columns=["티커", "현재가"])


def avg_trading_value(ticker, days=20):
    df = stock.get_market_ohlcv_by_date(
        (datetime.today() - timedelta(days=days * 2)).strftime("%Y%m%d"),
        today,
        ticker
    )
    return (df["거래량"] * df["종가"]).tail(days).mean()


def market_cap(ticker):
    return stock.get_market_cap_by_date(
        today, today, ticker
    )["시가총액"].iloc[0]


def price_action_filter(ticker):
    df = stock.get_market_ohlcv_by_date(
        (datetime.today() - timedelta(days=LOOKBACK_DAYS * 2)).strftime("%Y%m%d"),
        today,
        ticker
    )

    recent = df.tail(LOOKBACK_DAYS)
    low = recent["저가"].min()
    high = recent["고가"].max()
    current = recent["종가"].iloc[-1]

    cond1 = current >= low * (1 + RISE_FROM_LOW)
    cond2 = current >= high * (1 - DROP_FROM_HIGH)
    cond3 = current >= low * (1 - MAX_DRAWDOWN)

    return cond1 and cond2 and cond3, low, high, current


# -----------------------------
# 실행
# -----------------------------
if st.button("🚀 스크리닝 실행"):
    with st.spinner("시장 전체 스캔 중..."):

        base_df = get_price_filtered_stocks()
        st.subheader(f"① 가격 필터 통과 종목 수: {len(base_df)}")

        results = []

        for _, row in base_df.iterrows():
            ticker = row["티커"]

            try:
                avg_tv = avg_trading_value(ticker)
                mcap = market_cap(ticker)

                if avg_tv < TRADING_RATIO * mcap:
                    continue

                passed, low, high, current = price_action_filter(ticker)
                if not passed:
                    continue

                results.append({
                    "티커": ticker,
                    "종목명": stock.get_market_ticker_name(ticker),
                    "현재가": current,
                    "저점 대비 상승률 (%)": round((current / low - 1) * 100, 1),
                    "고점 대비 하락률 (%)": round((1 - current / high) * 100, 1),
                    "20일 평균 거래대금 (억)": round(avg_tv / 1e8, 2),
                    "시가총액 (억)": round(mcap / 1e8, 1)
                })

            except:
                continue

        df = pd.DataFrame(results)

        if df.empty:
            st.warning("조건을 만족하는 종목이 없습니다.")
        else:
            st.success(f"✅ 최종 후보 {len(df)}개")
            st.dataframe(
                df.sort_values("저점 대비 상승률 (%)", ascending=False)
                .head(MAX_OUTPUT),
                use_container_width=True
            )

            st.markdown("""
test
""")

# -----------------------------
# 하단
# -----------------------------
st.markdown("""
---
test
""")
