# this file will contain all HTML components for our UI

from dash import dcc, html
from layouts.airbnb_only_layout import airbnb_only_layout
from layouts.affordable_housing_layout import affordable_housing_layout

def create_layout():
    return html.Div([ 
        html.H1("Airbnb & Neighborhood Factors in NYC", style={'textAlign': 'center'}), 

        # the drop down for switching views
        html.Div(
            [
                html.Label("Select View:"),
                dcc.Dropdown(
                    id="view-selector",
                    options=[
                        {"label": "Airbnb Ditribution", "value": "airbnb_points"},
                        {"label": "Airbnb Density", "value": "population"},
                        {"label": "Affordable Housing", "value": "affh"},
                        {"label": "Transit", "value": "transit"},
                        {"label": "Crime", "value": "crime"},
                    ],
                    value="airbnb_points", # default
                    clearable=False,
                    style={"width": "50%", "margin": "0 auto"},
                ),
            ],
            style={"textAlign": "center", "padding": "10px"},
        ),
        
        html.Hr(),

        # start with airbnb only
        html.Div(id='page-content', children=airbnb_only_layout)
    ])