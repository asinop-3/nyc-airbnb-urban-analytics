from dash import html, dcc
from data_manager import df_map

transit_layout = html.Div([
    html.H1("NYC Airbnb & Transit Analytics", style={'textAlign': 'center'}),

    # Dropdown
    html.Div([
        html.Label("Filter Dashboard by Room Type:"),
        dcc.Dropdown(
            id='transit-room-filter',
             options=[{"label": "Compare All Categories", "value": "ALL"}] +
            [{"label": rt, "value": rt} for rt in sorted(df_map['room_type'].unique())],
            value='ALL',
            clearable=False,
            style={'width': '50%'}
        )
    ], style={'padding': '10px'}),

    html.Hr(),

    # Map 1
    html.Div([
        html.H3("Listing Locations & Subway Lines", style={'marginBottom': '5px'}),
        dcc.Graph(id="transit-main-map")
    ], style={'padding': '10px'}),

    # Scatter Plot
    html.Div([
        html.H3("The 'Proximity Premium' Analysis", style={'marginBottom': '5px'}),
        dcc.Graph(id="transit-scatter")
    ], style={'padding': '10px'}),

    # Luxury Lines Map
    html.Div([
        html.H3("The 'Luxury Lines': Average Price by Subway Station"),
        dcc.Graph(id="transit-luxury-map")
    ], style={'padding': '10px'}),

    html.Br(),

    html.Div(
        id="transit-description-box",
        children=[
            html.P([
                "Listing locations: Different categories of Airbnb listings and subway stations in NYC.",
                html.Br(),
                "Proximity premium: Shows price trend of Airbnbs based on distance to the nearest subway station.",
                html.Br(),
                "Luxury lines: Subway stations colored by the average price of Airbnbs within a 10-minute walk (800m)."
            ],
            style={"fontSize": "16px", "marginTop": "10px"})
        ],
        style={"textAlign": "center", "padding": "10px 20px"}
    )
])
