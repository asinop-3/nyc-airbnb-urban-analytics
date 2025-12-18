from dash import html, dcc

crime_layout = html.Div(
    [
        html.H1(
            "NYC Crime & Airbnb Activity",
            style={"textAlign": "center", "marginBottom": "20px"}
        ),

        html.Div(
            [
                html.Label("Select Visualization:"),
                dcc.Dropdown(
                    id="crime-map-selector",
                    options=[
                        {"label": "Crime Choropleth", "value": "crime"},
                        {"label": "Bivariate Crime Airbnb Classification", "value": "bivariate"}
                    ],
                    value="bivariate",   # default panel
                    clearable=False,
                    style={"width": "50%"}
                )
            ],
            style={"padding": "10px"}
        ),

        html.Hr(),

        # ---- Map Output Container ----
        dcc.Graph(id="crime-map", style={"height": "750px"}),

        html.Br(),

        html.Div(
            id="transit-description-box",
            children=[
                html.P([
                    "This visualization maps the relationship between Airbnb listings and crime reports across NYC ZIP codes using simple high- and low-category groupings. Manhattan and parts of Brooklyn show higher concentrations of both Airbnb listings and crime, while many outer-borough areas fall into the low crime–low listing category. The map emphasizes spatial patterns and comparison without implying causation."
                    ],
                style={"fontSize": "16px", "marginTop": "10px"})
            ],
            style={"textAlign": "center", "padding": "10px 20px"}
        )
    ]
)
