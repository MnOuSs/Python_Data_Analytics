"""
Global Air Pollution Dashboard

Interactive dashboard for analyzing PM2.5 air pollution.
Includes geo-spatial visualization, filtering, and dynamic insights.
"""

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Load dataframe
df = pd.read_csv("data/cleaned_air_pollution.csv")


# Prepare data
df["location_name"] = (
    df["country"] +
    "<br>PM2.5: " + df["pm25"].round(1).astype(str)
)


# Visualization functions
def create_map(data):
    """Create scatter geo map (point-level pollution)."""
    fig = px.scatter_geo(
        data,
        lat="latitude",
        lon="longitude",
        color="pm25",
        size="pm25",
        hover_name="location_name",
        hover_data={"latitude": False, "longitude": False},
        custom_data=["country"],
        color_continuous_scale="YlOrRd",
        projection="natural earth"
    )

    fig.update_layout(
        title={"text": "<b>PM2.5 Measurements by Location</b>", "x": 0.5},
        geo=dict(showland=True, landcolor="white", showcountries=True),
        paper_bgcolor="white",
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )

    return fig

def create_choropleth(data):
    """Create country-level average PM2.5 map."""
    country_avg = (
        data.groupby("country")["pm25"]
        .mean()
        .reset_index()
    )

    fig = px.choropleth(
        country_avg,
        locations="country",
        locationmode="country names",
        color="pm25",
        color_continuous_scale="YlOrRd"
    )

    fig.update_layout(
        title={"text": "<b>Average PM2.5 Levels by Country</b>", "x": 0.5},
        paper_bgcolor="white"
    )

    fig.update_geos(showcountries=True, countrycolor="black")

    return fig


def create_bar(data, selected_country=None):
    """Create bar chart (top countries or selected country)."""
    top = (
        data.groupby("country")["pm25"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    if selected_country:
        title_text = f"<b>PM2.5 Levels in {selected_country}</b>"
    else:
        title_text = "<b>Top 10 Most Polluted Countries</b>"

    fig = px.bar(
        top,
        x="pm25",
        y="country",
        orientation="h",
        labels={"pm25": "PM2.5 (µg/m³)", "country": "Country"},
        color="pm25",
        color_continuous_scale="Reds"
    )

    fig.update_layout(
        title={"text": title_text, "x": 0.5},
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="white",
        plot_bgcolor="white",
        coloraxis_showscale=False
    )

    return fig

def create_box(data, selected_country=None):
    """Create boxplot of PM2.5 distribution."""
    if selected_country:
        title_text = f"<b>PM2.5 Distribution in {selected_country}</b>"
    else:
        title_text = "<b>Distribution of PM2.5 Across Countries</b>"

    fig = px.box(data, x="country", y="pm25")

    fig.update_layout(
        title={"text": title_text, "x": 0.5},
        xaxis_tickangle=-45,
        xaxis_title="Country",
        yaxis_title="PM2.5 (µg/m³)",
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig


# Dashboard App
app = Dash(__name__)

app.layout = html.Div([

    html.H1("Global Air Pollution Dashboard", style={"textAlign": "center"}),

    html.P(
        "Interactive analysis of global PM2.5 pollution",
        style={"textAlign": "center"}
    ),

    # KPIs
    html.Div([
        html.Div(f"Avg: {df['pm25'].mean():.1f}",
                 style={"width": "30%", "display": "inline-block"}),
        html.Div(f"Max: {df['pm25'].max():.1f}",
                 style={"width": "30%", "display": "inline-block"}),
        html.Div(f"# of observations: {len(df)}",
                 style={"width": "30%", "display": "inline-block"}),
    ], style={"textAlign": "center"}),

    # Filters
    html.Div([
        dcc.Dropdown(
            id="country-filter",
            options=[
                {"label": c, "value": c}
                for c in sorted(df["country"].dropna().astype(str).unique())
            ],
            placeholder="Filter by country"
        ),

        dcc.RangeSlider(
            id="pm25-slider",
            min=0,
            max=int(df["pm25"].max()),
            value=[0, 100],
            tooltip={"placement": "bottom"}
        ),
    ], style={"marginBottom": "20px"}),

    # Maps
    dcc.Graph(id="map"),
    dcc.Graph(id="choropleth-map"),

    # Charts
    html.Div([
        html.Div(dcc.Graph(id="bar-chart"), style={"width": "48%"}),
        html.Div(dcc.Graph(id="box-chart"), style={"width": "48%"})
    ], style={"display": "flex", "gap": "20px"}),

    # Insight
    html.Div(id="insight-text", style={"textAlign": "center"})

], style={
    "padding": "30px",
    "maxWidth": "1200px",
    "margin": "auto",
    "display": "flex",
    "flexDirection": "column",
    "gap": "30px"
})


# CALLBACK
@app.callback(
    Output("map", "figure"),
    Output("choropleth-map", "figure"),
    Output("bar-chart", "figure"),
    Output("box-chart", "figure"),
    Output("insight-text", "children"),
    Input("country-filter", "value"),
    Input("pm25-slider", "value"),
    Input("map", "clickData")
)
def update_dashboard(selected_country, slider_range, click_data):
    """Update all visuals based on filters and interactions."""

    filtered_df = df
    active_country = selected_country

    # Slider filter
    filtered_df = filtered_df[
        (filtered_df["pm25"] >= slider_range[0]) &
        (filtered_df["pm25"] <= slider_range[1])
    ]

    # Dropdown filter
    if selected_country:
        filtered_df = filtered_df[filtered_df["country"] == selected_country]

    # Map click
    if click_data:
        country_clicked = click_data["points"][0]["custom_data"][0]
        filtered_df = filtered_df[filtered_df["country"] == country_clicked]
        active_country = country_clicked

    avg = filtered_df["pm25"].mean() if not filtered_df.empty else 0
    insight = f"Average PM2.5 in selection: {avg:.1f}"

    return (
        create_map(filtered_df),
        create_choropleth(filtered_df),
        create_bar(filtered_df, active_country),
        create_box(filtered_df, active_country),
        insight
    )


# RUN
if __name__ == "__main__":
    app.run(debug=True)
