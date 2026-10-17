# data/weather.py
import requests
import re
from config import QWEATHER_KEY, QWEATHER_HOST, QWEATHER_LOCATION


def clean_html_tags(text):
    """清洗数据中的 HTML 标签"""
    if isinstance(text, str):
        return re.sub(r'<[^>]+>', '', text)
    return text


def fetch_weather_data():
    try:
        now_url = f"https://{QWEATHER_HOST}/v7/weather/now?location={QWEATHER_LOCATION}&key={QWEATHER_KEY}"
        now_res = requests.get(now_url, timeout=5).json()

        hourly_url = f"https://{QWEATHER_HOST}/v7/weather/24h?location={QWEATHER_LOCATION}&key={QWEATHER_KEY}"
        hourly_res = requests.get(hourly_url, timeout=5).json()

        if now_res.get("code") == "200" and hourly_res.get("code") == "200":
            for key, value in now_res["now"].items():
                now_res["now"][key] = clean_html_tags(value)

            for hour_data in hourly_res["hourly"]:
                for key, value in hour_data.items():
                    hour_data[key] = clean_html_tags(value)

            return {
                "status": "success",
                "now": now_res["now"],
                "hourly": hourly_res["hourly"]
            }
        else:
            return _get_mock_weather()
    except Exception as e:
        return _get_mock_weather()


def _get_mock_weather():
    import random
    return {
        "status": "mock",
        "now": {"temp": str(random.randint(20, 30)), "humidity": str(random.randint(40, 80)),
                "windSpeed": str(random.randint(1, 5)), "text": "多云"},
        "hourly": [
            {"fxTime": f"2024-06-01T{i:02d}:00+08:00", "temp": str(22 + i // 2),
             "precip": "0.0" if i % 3 != 0 else str(round(random.uniform(0.5, 2.0), 1))} for i in range(24)
        ]
    }