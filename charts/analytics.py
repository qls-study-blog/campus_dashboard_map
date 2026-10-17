# charts/analytics.py
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data.mock import get_campus_data
from data.weather import fetch_weather_data


def render_bar_chart(is_dark=False):
    df = get_campus_data()
    area_flow = df.groupby("类型")["人流量"].sum().reset_index()
    area_flow = area_flow[area_flow["类型"] != "出入口"].sort_values("人流量", ascending=True)

    fig = px.bar(area_flow, x="人流量", y="类型", orientation="h", color="人流量", color_continuous_scale="Blues",
                 text="人流量")
    fig.update_traces(texttemplate="%{text}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly", showlegend=False, height=350,
        margin=dict(l=10, r=10, t=20, b=10), coloraxis_showscale=False, yaxis_title=None, xaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def render_line_chart(is_dark=False):
    data = fetch_weather_data()
    hourly = pd.DataFrame(data["hourly"])
    hourly["时间"] = pd.to_datetime(hourly["fxTime"]).dt.strftime('%H:00')
    hourly["温度"] = hourly["temp"].astype(float)
    hourly["降水量"] = hourly["precip"].astype(float)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=hourly["时间"], y=hourly["温度"], name="温度 (℃)", line=dict(color="#d62728", width=3),
                             mode="lines+markers"), secondary_y=False)
    fig.add_trace(go.Bar(x=hourly["时间"], y=hourly["降水量"], name="降水量 (mm)", marker_color="#1f77b4", opacity=0.5),
                  secondary_y=True)

    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly", height=350, hovermode="x unified",
        margin=dict(l=10, r=10, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    fig.update_xaxes(tickangle=-45, nticks=15)
    fig.update_yaxes(title_text="温度 (℃)", secondary_y=False)
    fig.update_yaxes(title_text="降水量 (mm)", secondary_y=True)
    return fig


def render_pie_chart(is_dark=False):
    df = get_campus_data()
    df = df[df["类型"] != "出入口"]

    fig = px.pie(df, names="类型", values="人流量", hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition="outside", textinfo="percent+label")
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly", height=350, margin=dict(l=30, r=30, t=20, b=20),
        showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def render_table():
    df = get_campus_data()
    return df.sort_values("人流量", ascending=False)[["名称", "类型", "人流量", "使用率(%)"]].reset_index(drop=True)