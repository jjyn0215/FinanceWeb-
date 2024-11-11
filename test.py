import requests
import json
from token_control import auth, read_token
from datetime import datetime, timedelta
 
APP_KEY = "PSedNV2FutO0im3DxCJ6vhit84wHyyfC6ZxY"
APP_SECRET = "fnAIq3eGjYzdlIaaQcpSxWh3rtfTYh/JqUdiBdtd455FqVOH0/AmrOp4Tv30mlufobSclfiuUl6EM7vj0/JBGf2DpoCa74VNGz4yx4rjiR2702LNHg2rcUHJevgDMXzlMx+uNWwTFjrdrDwyjq7Q3nR+AMGOemoOkTp1YtclMbfKzolxhtc="
ACCESS_TOKEN = read_token()
URL_BASE = "https://openapi.koreainvestment.com:9443" #실전투자

# Auth
# def auth():
#     headers = {"content-type":"application/json"}
#     body = {
#         "grant_type":"client_credentials",
#         "appkey":APP_KEY, 
#         "appsecret":APP_SECRET
#         }
#     PATH = "oauth2/tokenP"
#     URL = f"{URL_BASE}/{PATH}"
#     res = requests.post(URL, headers=headers, data=json.dumps(body))
#     print(headers, body)
#     global ACCESS_TOKEN
#     print(res.json())
#     ACCESS_TOKEN = res.json()["access_token"]

# 주식현재가 시세
def get_current_price(stock_no):
    PATH = "uapi/domestic-stock/v1/quotations/inquire-price"
    URL = f"{URL_BASE}/{PATH}"

    # 헤더 설정
    headers = {"Content-Type":"application/json", 
            "authorization": f"Bearer {ACCESS_TOKEN}",
            "appKey":APP_KEY,
            "appSecret":APP_SECRET,
            "tr_id":"FHPST01060000"}

    params = {
        "fid_cond_mrkt_div_code":"J",
        "fid_input_iscd": stock_no,
        # "fid_input_date_1": "20231110",
        # "fid_input_date_2": datetime.today().strftime("%Y%m%d"),
        # "FID_PERIOD_DIV_CODE": "D",
        # "FID_ORG_ADJ_PRC": "1"
        "FID_INPUT_HOUR_1": "000000"

    }
    # 호출
    res = requests.get(URL, headers=headers, params=params)

    if res.status_code == 200 and res.json()["rt_cd"] == "0" :
        print(res.json())
    # 토큰 만료 시
    elif res.status_code == 200 and res.json()["msg_cd"] == "EGW00123" :
        auth()
        get_current_price(stock_no)
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None


get_current_price("005930")