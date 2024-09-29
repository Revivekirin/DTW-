from params import params

# 한국 소형주 8개와 대형주 2개 (yfinance ticker)
korean_stocks = [
    "068270.KS",  # 셀트리온헬스케어
    "357780.KQ",  # 솔브레인
    "277810.KS",  # 레인보우로보틱스
    "096530.KQ",  # 씨젠
    "247540.KQ",  # 에코프로비엠
    "112040.KQ",  # 위메이드
    "293490.KQ",  # 카카오게임즈
    "009830.KS",  # 한화솔루션
    "005930.KS",  # 삼성전자 (대형주)
    "051910.KS"   # LG화학 (대형주)
]


# 미국 소형주 8개와 대형주 2개 (yfinance ticker)
us_stocks = [
    "ROKU",     # Roku, Inc.
    "SQ",       # Square, Inc.
    "PLUG",     # Plug Power Inc.
    "UPWK",     # Upwork Inc.
    "BYND",     # Beyond Meat, Inc.
    "RUN",      # Sunrun Inc.
    "Z",        # Zillow Group, Inc.
    "TDOC",     # Teladoc Health, Inc.
    "AAPL",     # Apple Inc. (대형주)
    "MSFT",     # Microsoft Corporation (대형주)
    "NVDA",     # Nvidea (대형 기술주)
    "KO",       # 코카콜라 (대형 배당주)
    "JNJ",      # 존슨앤존스 (대형 배당주)
    "LLY",      # 일라일리리 (대형 바이오주)
    "GS",       # 골드만삭스 (대형 금융주)
    "ALTR",     # 알테어 엔지니어링 (중형 기술주)
    "IONQ",     # 아이온큐 (소형 기술주)
]
for idx in range(len(korean_stocks)):
    params(korean_stocks[idx])

for idx in range(len(us_stocks)):
    params(us_stocks[idx])

