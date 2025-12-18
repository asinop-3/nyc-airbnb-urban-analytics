# this will be the first layout seen when visiting our site
# airbnb data only

from dash import dcc, html
from data_manager import base_map, borough_list

airbnb_only_layout = html.Div([ 
        html.H1("Interactive Airbnb Map", style={'textAlign': 'center'}), 

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
        dcc.Graph(id='airbnb-map', figure=base_map) 
    ])