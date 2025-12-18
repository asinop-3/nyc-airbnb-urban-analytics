from dash import html, dcc

transit_layout = html.Div([
    html.H1("NYC Airbnb & Transit Analytics", style={'textAlign': 'center'}),

    # Dropdown
    html.Div([
        html.Label("Filter Dashboard by Room Type:"),
        dcc.Dropdown(
            id='transit-room-filter',
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
    ], style={'padding': '10px'})
])
