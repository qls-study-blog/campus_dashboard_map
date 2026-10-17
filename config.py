# config.py
# 全局配置
import os


def _get_secret(name: str, default: str = "") -> str:
    """密钥读取优先级：Streamlit secrets → 环境变量 → 默认值。

    部署到公网（Streamlit Cloud）时，请在后台 Secrets 中配置
    AMAP_KEY / QWEATHER_KEY / QWEATHER_HOST，避免密钥随代码公开。
    本地运行时，密钥写在 .streamlit/secrets.toml（已被 .gitignore 排除，不会上传）。
    """
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name, default)


# 1. 高德地图 API（公网部署时在 Secrets 配置）
AMAP_KEY = _get_secret("AMAP_KEY", "")

# 2. 和风天气 API 配置
QWEATHER_KEY = _get_secret("QWEATHER_KEY", "")
# QWEATHER_HOST 是公网 API 网关地址（非密钥），保留默认值便于本地运行
QWEATHER_HOST = _get_secret("QWEATHER_HOST", "mg3h2tyr75.re.qweatherapi.com")
QWEATHER_LOCATION = "101300501"  # 桂林的城市ID

# 3. 颜色配置（亮色与暗色）
COLORS_LIGHT = {
    "bg": "#f5f7fa",
    "card": "#ffffff",
    "text": "#2c3e50",
    "primary": "#1f77b4",
    "secondary": "#ff7f0e"
}

COLORS_DARK = {
    "bg": "#1e1e1e",
    "card": "#2d2d2d",
    "text": "#e0e0e0",
    "primary": "#4a9eff",
    "secondary": "#ff9f4a"
}

# 4. 建筑类型颜色映射
TYPE_COLORS = {
    "学习": "#1f77b4", "餐饮": "#ff7f0e", "住宿": "#2ca02c",
    "运动": "#d62728", "服务": "#8c564b", "活动": "#e377c2",
    "景观": "#17becf", "出入口": "#7f7f7f"
}
