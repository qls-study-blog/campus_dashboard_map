# app.py
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from data.weather import fetch_weather_data
from charts.map_view import render_map
from charts.analytics import render_bar_chart, render_line_chart, render_pie_chart, render_table

# 1. 页面基本配置
st.set_page_config(
    page_title="校园地图数据看板",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 session_state 用于保存坐标记录
if 'picked_coords' not in st.session_state:
    st.session_state.picked_coords = []
if 'current_lat' not in st.session_state:
    st.session_state.current_lat = 0.0
if 'current_lng' not in st.session_state:
    st.session_state.current_lng = 0.0

# 2. 侧边栏设置
with st.sidebar:
    st.header("⚙️ 设置")
    dark_mode = st.toggle("开启暗色模式", value=False)
    st.markdown("---")

    # ==========================================
    # 🌟 新增：坐标收集工具
    # ==========================================
    st.header("📍 坐标拾取器")
    pick_mode = st.checkbox("开启地图点击拾取")

    if pick_mode:
        st.info(
            f"当前点击坐标：\n\n纬度: `{st.session_state.current_lat:.6f}`\n\n经度: `{st.session_state.current_lng:.6f}`")

        if st.button("➕ 记录当前坐标"):
            if st.session_state.current_lat != 0.0:
                st.session_state.picked_coords.append({
                    "序号": len(st.session_state.picked_coords) + 1,
                    "纬度": round(st.session_state.current_lat, 6),
                    "经度": round(st.session_state.current_lng, 6)
                })
                st.success("已记录！")
            else:
                st.warning("请先在地图上点击一个点")

        if len(st.session_state.picked_coords) > 0:
            st.write("📋 **已记录的坐标列表：**")
            df_coords = pd.DataFrame(st.session_state.picked_coords)
            # 显示表格
            st.dataframe(df_coords, hide_index=True, use_container_width=True)

            # 方便一键复制
            csv = df_coords.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 下载坐标 CSV (或直接复制)",
                data=csv,
                file_name='picked_coords.csv',
                mime='text/csv',
            )

            if st.button("🗑️ 清空所有记录"):
                st.session_state.picked_coords = []
                st.rerun()
    else:
        st.info("💡 校园地图与交通数据看板")

    st.markdown("---")

# 3. 动态 CSS 注入
if dark_mode:
    bg_color = "#1a1a24"
    text_color = "#e0e0e0"
    card_bg = "#2a2a35"
    metric_text = "#ffffff"
else:
    bg_color = "#f5f7fa"
    text_color = "#2c3e50"
    card_bg = "#ffffff"
    metric_text = "#1f77b4"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color} !important; }}
    h1, h2, h3, h4, h5, h6, p, span, label {{ color: {text_color} !important; }}
    [data-testid="stSidebar"] {{ background-color: {card_bg}; }}
    div[data-testid="stMetric"] {{
        background-color: {card_bg};
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        border-left: 4px solid {metric_text};
    }}
    div[data-testid="stMetricLabel"] > div {{ color: {text_color} !important; opacity: 0.8; }}
    div[data-testid="stMetricValue"] > div {{ color: {metric_text} !important; font-weight: bold; }}
    th {{ color: {text_color} !important; }}
</style>
""", unsafe_allow_html=True)

# 4. 标题
st.title("🏫 校园地图与天气数据看板")
st.caption("📅 数据实时更新 | 桂林理工大学雁山校区")
st.divider()

# 5. 概览区
weather_data = fetch_weather_data()
now_weather = weather_data["now"]

st.subheader("🌤️ 天气概览")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="当前温度", value=f"{now_weather['temp']} ℃")
with col2:
    st.metric(label="相对湿度", value=f"{now_weather['humidity']} %")
with col3:
    st.metric(label="风速", value=f"{now_weather['windSpeed']} km/h")
with col4:
    st.metric(label="天气状况", value=now_weather['text'])

st.divider()

# 6. 地图区
st.subheader("🗺️ 校园地图")

col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    show_bus = st.checkbox("显示 5路公交", value=True)
with col_t2:
    show_shuttle = st.checkbox("显示 通勤车", value=True)
with col_t3:
    show_sightseeing = st.checkbox("显示 观光车呼叫点", value=True)

fig_map = render_map(show_bus, show_shuttle, show_sightseeing, is_dark=dark_mode)

# 接收地图点击事件，并实时更新到 session_state 中
map_data = st_folium(
    fig_map,
    width="100%",
    height=600,
    key="campus_map",
    returned_objects=["last_clicked"]
)

# 如果捕获到了点击，更新当前坐标
if map_data and map_data.get("last_clicked"):
    st.session_state.current_lat = map_data["last_clicked"]["lat"]
    st.session_state.current_lng = map_data["last_clicked"]["lng"]

st.divider()

# 7. 图表区
st.subheader("📊 数据分析图表")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    st.markdown("##### 各类型建筑人流量排行")
    st.plotly_chart(render_bar_chart(is_dark=dark_mode), use_container_width=True)
with row1_col2:
    st.markdown("##### 未来24小时温度与降水趋势")
    st.plotly_chart(render_line_chart(is_dark=dark_mode), use_container_width=True)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    st.markdown("##### 校园人群活动结构")
    st.plotly_chart(render_pie_chart(is_dark=dark_mode), use_container_width=True)
with row2_col2:
    st.markdown("##### 校园建筑明细")
    st.dataframe(render_table(), width="stretch", height=350, hide_index=True)