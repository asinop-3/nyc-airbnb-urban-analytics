from dash import html, dcc

crime_layout = html.Div(
    [
        html.H1(
            "NYC Crime and Airbnb Activity",
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
            id="crime-description-box",
            style={
                "padding": "15px",
                "border": "1px solid #ccc",
                "borderRadius": "8px",
                "backgroundColor": "#f8f9fa",
                "width": "80%",
                "margin": "auto"
            }
        ),
    ]
)
