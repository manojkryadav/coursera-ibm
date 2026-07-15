import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        dcc.Dropdown(
            id="site-dropdown",
            options=[{"label": "All Sites", "value": "ALL"}]
            + [
                {"label": site, "value": site}
                for site in sorted(spacex_df["Launch Site"].unique())
            ],
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),
        html.Br(),
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={0: "0", 2500: "2500", 5000: "5000", 7500: "7500", 10000: "10000"},
            value=[min_payload, max_payload],
        ),
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        all_sites_df = spacex_df.groupby("Launch Site", as_index=False)["class"].sum()
        return px.pie(
            all_sites_df,
            values="class",
            names="Launch Site",
            title="Total Successful Launches by Site",
        )

    filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
    outcome_df = (
        filtered_df["class"]
        .value_counts()
        .rename_axis("class")
        .reset_index(name="count")
    )
    outcome_df["Outcome"] = outcome_df["class"].map({1: "Success", 0: "Failure"})
    return px.pie(
        outcome_df,
        values="count",
        names="Outcome",
        title=f"Launch Outcomes for {entered_site}",
    )


@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    payload_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low)
        & (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if entered_site == "ALL":
        return px.scatter(
            payload_df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Payload vs. Launch Outcome for All Sites",
        )

    site_df = payload_df[payload_df["Launch Site"] == entered_site]
    return px.scatter(
        site_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=f"Payload vs. Launch Outcome for {entered_site}",
    )


if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=8050)
    except Exception:
        app.run_server(debug=True, host="0.0.0.0", port=8050)
