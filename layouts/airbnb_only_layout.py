# this will be the first layout seen when visiting our site
# airbnb data only

from dash import dcc, html
from data_manager import base_map, borough_list

airbnb_only_layout = html.Div([ 
        html.H1("Airbnb Listings & Density", style={'textAlign': 'center'}), 

        # drop down for neighborhood filter
        html.Div([ 
            html.Label("Select Neighborhood:"), 
            dcc.Dropdown( 
                id='airbnb-neighborhood-filter', 
                options=[{'label': i, 'value': i} for i in borough_list], 
                value=None, # no initial selection
                placeholder="All Neighborhoods", 
                multi=True # can select multiple boroughs at once
            ) 
        ], 
        id="airbnb-filter-container",
        style={'width': '50%', 'padding': '10px'}), 

        # needed to display base map
        dcc.Graph(id='airbnb-map', figure=base_map),

        html.Br(),

        html.Div(
            id="airbnb-description-box",
            children=[
                html.P([
                    "Airbnb Points shows the distribution of Airbnb listings across NYC.",
                    html.Br(),
                    "Population Choropleth shows how many Airbnb listings there are per 10k people, per Neighborhood Tabulation Area (NTA)."
                ],
                style={"fontSize": "16px", "marginTop": "10px"})
            ],
            style={"textAlign": "center", "padding": "10px 20px"}
        )
    ])