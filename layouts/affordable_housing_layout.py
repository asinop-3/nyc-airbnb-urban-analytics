# this is the affordable housing layout Fatima made

from dash import dcc, html
from data_manager import borough_list, min_year, max_year

affordable_housing_layout = html.Div(
    [
        html.H1(
            "NYC Airbnb & Affordable Housing Layers",
            style={"textAlign": "center"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Select Neighborhood (Airbnb):"),
                        dcc.Dropdown(
                            id="affh-neighborhood-filter",
                            options=[
                                {"label": i, "value": i}
                                for i in borough_list
                            ],
                            value=None,
                            placeholder="All Neighborhoods",
                            multi=True,
                        ),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                    },
                ),
                html.Div(
                    [
                        html.Label("Toggle Layers:"),
                        dcc.Checklist(
                            id="affh-layer-toggle",
                            options=[
                                {
                                    "label": "Airbnb Listings",
                                    "value": "airbnb",
                                },
                                {
                                    "label": "Affordable Housing Points",
                                    "value": "aff_points",
                                },
                                {
                                    "label": "Council District Totals (Total Units)",
                                    "value": "council",
                                },
                            ],
                            value=["aff_points", "council"],
                            inline=True,
                        ),
                        html.Br(),
                        html.Label(
                            "Filter Affordable Housing by Completion Year:"
                        ),
                        dcc.RangeSlider(
                            id="affh-year-slider",
                            min=min_year,
                            max=max_year,
                            value=[min_year, max_year],
                            marks={
                                year: str(year)
                                for year in range(min_year, max_year + 1)
                            },
                            step=1,
                        ),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "paddingLeft": "20px",
                    },
                ),
            ],
            style={"padding": "10px 20px"},
        ),
        dcc.Graph(id="affh-map"),

        html.Br(),

        html.Div(
            id="affh-description-box",
            children=[
                html.P([
                    "Airbnb Listings – Blue points showing Airbnb listings from the last 12 months, filtered by neighborhood if selected.",
                    html.Br(),
                    "Affordable Housing Units (by Project) – Greenish circles whose size and color reflect the number of ‘All Counted Units’ at each project. The year slider controls which completion years are shown.",
                    html.Br(),
                    "Total Affordable Units (within Council District) – Purple/blue polygons representing the total number of affordable units in each NYC Council District, with darker colors indicating more units."
                ],
                style={"fontSize": "16px", "marginTop": "10px"})
            ],
            style={"textAlign": "center", "padding": "10px 20px"}
        )
    ]
)