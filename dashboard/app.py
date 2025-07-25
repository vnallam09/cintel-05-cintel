# --------------------------------------------
# Imports
# --------------------------------------------
from shiny import reactive, render
from shiny.express import ui
import random
from datetime import datetime
from faicons import icon_svg
from collections import deque
import pandas as pd
from shinywidgets import render_plotly
import plotly.graph_objects as go
import numpy as np
import requests
from datetime import datetime, timedelta

# --------------------------------------------
# Shiney UI setup
# --------------------------------------------

with ui.sidebar(open="open"):

    ui.h2("Teja's Antarctic Explorer Dashboard", class_="text-center")

    ui.p(
        "Simulated Real-time temperature readings in Antarctica.",
        class_="text-center",
    )

    ui.hr()

    ui.h6("Links:")

    ui.a(
        "GitHub Source",
        href="https://github.com/vnallam09/cintel-05-cintel",
        target="_blank",
    )

    ui.a(
        "GitHub App",
        href="https://github.com/vnallam09/cintel-05-cintel/blob/main/dashboard/app.py",
        target="_blank",
    )

    ui.a("PyShiny", href="https://shiny.posit.co/py/", target="_blank")

ui.h4("Weather Dashboard:")
with ui.layout_columns():

    @render.ui
    def temp_value_box():
        df, latest_dictionary_entry = reactive_calc_combined()
        temp = latest_dictionary_entry["temp"]

        if temp > -16.5:
            theme = "bg-gradient-orange-red"
            icon_name = "sun"
        elif temp < -17.5:
            theme = "bg-gradient-blue-purple"
            icon_name = "snowflake"
        else:
            theme = "bg-gradient-indigo-purple"
            icon_name = "thermometer"

        return ui.value_box(
            title="Temperature",
            value=f"{temp}°C",
            showcase=icon_svg(icon_name),
            theme=theme,
        )

    @render.ui
    def status_value_box():
        df, latest_dictionary_entry = reactive_calc_combined()
        temp = latest_dictionary_entry["temp"]

        if temp > -16.5:
            status = "Warm"
            theme = "bg-gradient-red-orange"
            icon_name = "sun"
        elif temp < -17.5:
            status = "Cold"
            theme = "bg-gradient-blue-cyan"
            icon_name = "snowflake"
        else:
            status = "Normal"
            theme = "bg-gradient-green-blue"
            icon_name = "thermometer"

        return ui.value_box(
            title="Status", value=status, showcase=icon_svg(icon_name), theme=theme
        )

    @render.ui
    def time_box():
        df, latest_dictionary_entry = reactive_calc_combined()
        time = latest_dictionary_entry["timestamp"]
        theme = "bg-gradient-indigo-purple"
        icon_name = "clock"

        return ui.value_box(
            title="Time", value=time, showcase=icon_svg(icon_name), theme=theme
        )

    ui.value_box(
        title="Location",
        value="Antarctica",
        showcase=icon_svg("map-pin"),
        theme="bg-gradient-purple-pink",
    )

ui.hr(
    style="margin-top: 10px; margin-bottom: 10px;"
)  # Adds 10px of space above and below the line

with ui.layout_columns():
    with ui.card():
        ui.card_header("Latest Snapshot of last 5 temperature readings")

        @render.data_frame
        def data_table():
            df, latest_dictionary_entry = reactive_calc_combined()
            pd.set_option("display.width", None)  # Use maximum width
            return render.DataGrid(df, width="100%")


ui.hr(
    style="margin-top: 10px; margin-bottom: 10px;"
)  # Adds 10px of space above and below the line

with ui.card():
    ui.card_header("Temperature Over Time")

    @render_plotly
    def display_temperature_plot():
        df, latest_dictionary_entry = reactive_calc_combined()
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            fig = go.Figure()

            # Temperature line
            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=df["temp"],
                    mode="lines+markers",
                    name="Temperature",
                    line=dict(color="#2980B9"),
                )
            )

            # Simple trend line
            if len(df) >= 2:
                x_numeric = np.arange(len(df))
                z = np.polyfit(x_numeric, df["temp"], 1)
                trend_y = np.polyval(z, x_numeric)

                fig.add_trace(
                    go.Scatter(
                        x=df["timestamp"],
                        y=trend_y,
                        mode="lines",
                        name="Trend",
                        line=dict(color="#85C1E9", dash="dash"),
                    )
                )

            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                plot_bgcolor="#F8FBFF",
                paper_bgcolor="#EBF5FB",
                font=dict(color="#1B4F72"),
                title_font=dict(size=20),
                transition=dict(duration=500),
            )
            return fig


ui.hr(style="margin-top: 10px; margin-bottom: 10px;")

with ui.card():
    ui.card_header("Temperature real time from Antarctica")
    @render_plotly
    def current_display_temperature_plot():
        df = fetch_weather_data(-82.86, 0.0000, 100) #antarctic coordinates
        
        fig = go.Figure()
        
        # Temperature line 2m
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["temperature_2m"],
            mode="lines+markers",
            name="temperature_2m",
            line=dict(color="#2980B9"),
        ))
        # apparent_temperature line 2m
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["apparent_temperature"],
            mode="lines+markers",
            name="apparent_temperature",
            line=dict(color="#1B4F72"),
        ))
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Temperature (°C)",
            plot_bgcolor="#F8FBFF",
            paper_bgcolor="#EBF5FB",
            font=dict(color="#1B4F72"),
            title_font=dict(size=20),
            transition=dict(duration=500)
        )
        return fig

with ui.layout_columns():
    with ui.card():
        ui.card_header("Snowfall vs Time")
        @render_plotly
        def snowfall():
            df = fetch_weather_data(-82.86, 0.0000, 100)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["snowfall"],
                mode="lines+markers",
                name="Snowfall",
                line=dict(color="#2980B9", width=2),
                marker=dict(color="#1B4F72", size=4),
                fill='tozeroy',
                fillcolor='rgba(41, 128, 185, 0.1)'
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Snowfall (cm)",
                plot_bgcolor="#F8FBFF",
                paper_bgcolor="#EBF5FB",
                font=dict(color="#1B4F72"),
                title_font=dict(size=16),
                showlegend=False,
                transition=dict(duration=500),
                hovermode='x unified'
            )
            return fig

    with ui.card():
        ui.card_header("Snow Depth vs Time")
        @render_plotly
        def snow_depth():
            df = fetch_weather_data(-82.86, 0.0000, 100)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["snow_depth"],
                mode="lines+markers",
                name="Snow Depth",
                line=dict(color="#27AE60", width=2),
                marker=dict(color="#1E8449", size=4),
                fill='tozeroy',
                fillcolor='rgba(39, 174, 96, 0.1)'
            ))
            
            # Add reference line for average
            avg_depth = df["snow_depth"].mean()
            fig.add_hline(
                y=avg_depth, 
                line_dash="dash", 
                line_color="#E74C3C",
                annotation_text=f"Average: {avg_depth:.1f} cm"
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Snow Depth (cm)",
                plot_bgcolor="#F8FBFF",
                paper_bgcolor="#EBF5FB",
                font=dict(color="#1B4F72"),
                title_font=dict(size=16),
                showlegend=False,
                transition=dict(duration=500),
                hovermode='x unified'
            )
            return fig

# --------------------------------------------
# Constants and reactive data setup
# --------------------------------------------

UPDATE_INTERVAL_SECS: int = 5
DEQUE_SIZE: int = 5
reactive_value_wrapper = reactive.value(deque(maxlen=DEQUE_SIZE))


@reactive.calc()
def reactive_calc_combined():
    reactive.invalidate_later(UPDATE_INTERVAL_SECS)

    temp = round(random.uniform(-18, -16), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    latest_dictionary_entry = {"temp": temp, "timestamp": timestamp}

    # getting 5 data points for plotting
    reactive_value_wrapper.get().append(latest_dictionary_entry)
    deque_snapshot = reactive_value_wrapper.get()

    df = pd.DataFrame(deque_snapshot)

    return df, latest_dictionary_entry


# --------------------------------------------
# Fetching weather data from Open Meteo API 
# https://open-meteo.com/en/docs?timezone=auto#location_and_time
# --------------------------------------------

def fetch_weather_data(latitude, longitude, days):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": [
            "temperature_2m_mean",
            "apparent_temperature_mean",
            "snowfall_sum",
            "snow_depth_mean",
        ],
        "timezone": "auto",
    }

    response = requests.get(url, params=params)
    data = response.json()
    daily_data = data["daily"]

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(daily_data["time"]),
            "temperature_2m": daily_data["temperature_2m_mean"],
            "apparent_temperature": daily_data["apparent_temperature_mean"],
            "snowfall": daily_data["snowfall_sum"],
            "snow_depth": daily_data["snow_depth_mean"],
        }
    )
    df['date'] = pd.to_datetime(df['date'])
    
    return df
