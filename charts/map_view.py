# charts/map_view.py
import folium
from data.mock import get_bus_stops, get_bus_route_from_amap, get_sightseeing_stops, get_staff_shuttle

def render_map(show_bus=True, show_shuttle=True, show_sightseeing=True, is_dark=False):
    df_bus = get_bus_stops()
    df_sightseeing = get_sightseeing_stops()
    df_staff = get_staff_shuttle()

    center_lat, center_lng = 25.0635, 110.2990
    tiles_url = "https://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}"

    m = folium.Map(location=[center_lat, center_lng], zoom_start=15, tiles=tiles_url, attr="高德地图")

    # ==========================================
    # 1. 绘制 5路公交（手工平滑拐点，贴合真实站点、无绕路岔路）
    # ==========================================
    if show_bus:
        # 高德驾车路径规划 API：贴合真实道路、平滑；API 内部已做岔路裁剪
        bus_coords = get_bus_route_from_amap()
        if not bus_coords:
            # API 失败时退回手工拐点
            bus_coords = df_bus[["纬度", "经度"]].values.tolist()

        # 画橘色线
        folium.PolyLine(
            bus_coords, color="#ff7f0e", weight=6, opacity=0.9, tooltip="5路公交路线"
        ).add_to(m)

        # 画 5 个公交站点的图标（遍历时过滤掉隐藏的空站名）
        for _, row in df_bus.iterrows():
            if row["站点"] == "":
                continue # 遇到隐藏点直接跳过，不画图标

            popup_html = f"""
            <div style="font-family: 'Microsoft YaHei', sans-serif; width: 200px;">
                <h4 style="color: #ff7f0e; margin: 0 0 5px 0;">🚌 {row['站点']}</h4>
                <p style="margin: 0; font-size: 12px;">运营线路：5路公交</p>
                <p style="margin: 0; font-size: 12px;">首末班：06:50 - 21:00</p>
            </div>
            """
            folium.Marker(
                location=[row["纬度"], row["经度"]],
                icon=folium.Icon(color="orange", icon="bus", prefix="fa"),
                tooltip=f"点击查看：{row['站点']}详情",
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)

    # ==========================================
    # 2. 绘制观光车呼叫点
    # ==========================================
    if show_sightseeing:
        for _, row in df_sightseeing.iterrows():
            popup_html = f"""
            <div style="font-family: 'Microsoft YaHei', sans-serif; width: 200px;">
                <h4 style="color: #2ca02c; margin: 0 0 5px 0;">🚐 {row['名称']}（观光车）</h4>
                <p style="margin: 0; font-size: 12px;">运营模式：招手即停 / 小程序呼叫</p>
            </div>
            """
            folium.Marker(
                location=[row["纬度"], row["经度"]],
                icon=folium.Icon(color="green", icon="shuttle-van", prefix="fa"),
                tooltip=f"点击查看：{row['名称']}观光车信息",
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)

    # ==========================================
    # 3. 绘制教职工通勤车（最后绘制=最上层，不被观光车遮挡）
    # ==========================================
    if show_shuttle:
        for _, row in df_staff.iterrows():
            popup_html = f"""
            <div style="font-family: 'Microsoft YaHei', sans-serif; width: 250px;">
                <h4 style="color: #9467bd; margin: 0 0 6px 0;">🚌 {row['名称']}（通勤车）</h4>
                <p style="margin: 0 0 6px 0; font-size: 12px;">运行区间：屏风校区 ↔ 雁山校区</p>
                <div style="background: #f3f0fa; border-radius: 6px; padding: 8px;">
                    <p style="margin: 0 0 4px 0; font-size: 12px; font-weight: bold; color:#5b3fa8;">📅 雁山 → 屏风（发车时间）</p>
                    <p style="margin: 0; font-size: 11px; line-height: 1.6;">
                        教四楼：10:20　12:15<br>　　　　16:20　17:10　18:20　22:00<br>
                        行知楼：17:20
                    </p>
                </div>
                <div style="background: #f3f0fa; border-radius: 6px; padding: 8px; margin-top:6px;">
                    <p style="margin: 0 0 4px 0; font-size: 12px; font-weight: bold; color:#5b3fa8;">📅 屏风 → 雁山（发车时间）</p>
                    <p style="margin: 0; font-size: 11px; line-height: 1.6;">
                        东城小区：7:20　8:00<br>
                        国际教育园区1号楼：7:20　8:05　9:15<br>　　　　　　　　13:20　15:05　20:30
                    </p>
                </div>
                <p style="margin: 6px 0 0 0; font-size: 11px; color:#888;">💳 教职工刷卡乘车，点对点直达，约 40 分钟</p>
            </div>
            """
            # 大号紫色自定义图标，确保视觉上不被观光车绿标盖住
            folium.Marker(
                location=[row["纬度"], row["经度"]],
                icon=folium.DivIcon(
                    html='<div style="width:44px;height:44px;line-height:44px;text-align:center;'
                         'font-size:26px;background:#7b3ff2;color:#fff;border-radius:50%;'
                         'border:3px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,.4);">🚌</div>',
                    icon_size=(44, 44),
                    icon_anchor=(22, 44),
                ),
                tooltip=f"点击查看：{row['名称']}通勤车时刻表",
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)

    return m