# this file will contain all of our callbacks

import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash import html
import pandas as pd

from data_manager import airbnb_df, aff_points, council_choropleth_trace, nta_geojson, airbnb_10k, df_map, subway_df, room_colors
from data_manager import (
    merged_zip_data,
    nyc_zip,
    crime_color_map
)   
from layouts.airbnb_only_layout import airbnb_only_layout
from layouts.affordable_housing_layout import affordable_housing_layout
from layouts.transit_layout import transit_layout
from layouts.crime_layout import crime_layout



def register_callbacks(app):

    # ------------------------------------------------------------
    # Airbnb-only map callback
    # ------------------------------------------------------------
    @app.callback(
        Output("airbnb-map", "figure"),
        [
            Input("airbnb-neighborhood-filter", "value"),
            Input("view-selector", "value")
        ]
    )
    def update_airbnb_map(selected_neighborhoods, view_mode):

        fig = go.Figure()

        airbnb_df_filtered = airbnb_df.copy()

        if selected_neighborhoods:
            airbnb_df_filtered = airbnb_df_filtered[
                airbnb_df_filtered["neighborhood_group_cleansed"].isin(selected_neighborhoods)
            ]

        # PLACEHOLDER CODE FOR FIRST TRY OF POLYGONS:

        # plot Airbnb points only if selected
        if view_mode == "airbnb_points":
            fig.add_trace(go.Scattermapbox(
                lat=airbnb_df_filtered["latitude"],
                lon=airbnb_df_filtered["longitude"],
                mode="markers",
                marker=dict(size=4, opacity=0.15),
                hovertext=airbnb_df_filtered["name"],
                hoverinfo="text"
            ))

        # choropleth if selected
        if view_mode == "population":
            # NTA choropleth
            fig.add_trace(go.Choroplethmapbox(
                geojson=nta_geojson,
                locations=airbnb_10k["NTA2020"],
                z=airbnb_10k["airbnb_per_10k"],
                featureidkey="properties.NTA2020",
                colorscale="Viridis",
                marker_opacity=1,
                marker_line_width=1,
                marker_line_color="black",
                # show something nice when you hover over
                hovertext=(
                    "Borough: " + airbnb_10k["neighborhood_group_cleansed"] +
                    "<br>NTA: " + airbnb_10k["NTAName"] +
                    "<br>Airbnbs per 10k: " + airbnb_10k["airbnb_per_10k"].astype(str)
                    ),
                hoverinfo="text",
                # deal with high and low values dominating color scale:
                zmin=airbnb_10k["airbnb_per_10k"].quantile(0.05),
                zmax=airbnb_10k["airbnb_per_10k"].quantile(0.95)
            ))
        
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=10,
            mapbox_center={"lat": 40.7128, "lon": -74.0060},
            margin={"l":0, "r":0, "t":0, "b":0}
        )

        return fig
    
    # only show neighborhood filter when "airbnb_points" is selected
    @app.callback(
        Output("airbnb-filter-container", "style"),
        Input("view-selector", "value")
    )
    def toggle_airbnb_filter(view_mode):
        
        # show filter for air_bnb points
        if view_mode == "airbnb_points":
            return {'width': '50%', 'padding': '10px'}

        # hide otherwise
        return {'display': 'none'}

    # SWITCH LAYER CALLBACK 
    @app.callback(
        Output("page-content", "children"),
        Input("view-selector", "value"),
    )
    def switch_layout(selected_view):
        # Airbnb points
        if selected_view == "airbnb_points":
            return airbnb_only_layout

        # Population choropleth
        if selected_view == "population":
            return airbnb_only_layout  # Same layout, BUT callback will return different map

        # Affordable Housing
        if selected_view == "affh":
            return affordable_housing_layout

        if selected_view == "transit":
            return transit_layout

        if selected_view == "crime":
            return crime_layout

        # Fallback
        return airbnb_only_layout

    # ------------------------------------------------------------
    # 3) Affordable Housing multi-layer map callback (final styled)
    # ------------------------------------------------------------
    @app.callback(
        Output("affh-map", "figure"),
        [
            Input("affh-neighborhood-filter", "value"),
            Input("affh-layer-toggle", "value"),
            Input("affh-year-slider", "value"),
        ],
    )
    def update_affh_map(selected_neighborhoods, selected_layers, year_range):
        # If nothing is selected, treat as empty list
        if not selected_layers:
            selected_layers = []
        
        fig = go.Figure()

        # Base figure / mapbox config
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=10.5,
            mapbox_center={"lat": 40.7128, "lon": -74.0060},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height= 800,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.01,
                xanchor="left",
                x=0.01,
                font=dict(size=14)
            ),
        )

        # --------------------------------------------------------
        # 1) Airbnb Listings layer
        # --------------------------------------------------------
        if "airbnb" in selected_layers:
            df_copy = airbnb_df.copy()
            if selected_neighborhoods:
                df_copy = df_copy[
                    df_copy["neighborhood_group_cleansed"].isin(
                        selected_neighborhoods
                    )
                ]

            fig.add_trace(
                go.Scattermapbox(
                    lat=df_copy["latitude"],
                    lon=df_copy["longitude"],
                    mode="markers",
                    marker=dict(
                        size=7,
                        opacity=0.65
                    ),
                    name="Airbnb Listings",
                    text=df_copy["name"],
                    hovertemplate="Airbnb: %{text}<extra></extra>",
                )
            )

        # --------------------------------------------------------
        # 2) Affordable Housing points (All Counted Units)
        # --------------------------------------------------------
        if "aff_points" in selected_layers:
            points = aff_points.copy()

            if year_range is not None and len(year_range) == 2:
                yr_min, yr_max = year_range
                points = points[
                    (points["CompletionYear"] >= yr_min)
                    & (points["CompletionYear"] <= yr_max)
                ]

            if not points.empty:
                units = points["All Counted Units"].fillna(0)
                units_clipped = units.clip(lower=0, upper=200)

                # Marker size scaled by units
                if units.max() > 0:
                    marker_sizes = 6 + (units / units.max()) * 24
                else:
                    marker_sizes = [10] * len(points)

                fig.add_trace(
                    go.Scattermapbox(
                        lat=points["Latitude"],
                        lon=points["Longitude"],
                        mode="markers",
                        marker=dict(
                            size=marker_sizes,
                            sizemode="area",
                            sizemin=5,
                            opacity=0.9,
                            color=units_clipped,
                            colorscale="Viridis",  # MATCH standalone script
                            cmin=0,
                            cmax=200,
                            showscale=True,
                            colorbar=dict(
                                title="Units by project",
                                len=0.55,  
                                lenmode="fraction",
                                thickness=18,
                                x=0.88,
                            ),
                        ),
                        name="Affordable Housing (points)",
                        customdata=points[
                            ["Project Name", "All Counted Units", "CompletionYear"]
                        ].values,
                        hovertemplate=(
                            "Project: %{customdata[0]}<br>"
                            "All Counted Units: %{customdata[1]}<br>"
                            "Completion Year: %{customdata[2]}"
                            "<extra></extra>"
                        ),
                    )
                )

        # --------------------------------------------------------
        # 3) Council District polygon layer (Total Units)
        # --------------------------------------------------------
        if "council" in selected_layers:
            # Build the council choropleth exactly like standalone version
            council_trace = go.Choroplethmapbox(
                geojson=council_choropleth_trace.geojson,
                locations=council_choropleth_trace.locations,
                z=council_choropleth_trace.z,
                featureidkey="properties.COUNDIST",
                colorscale="GnBu",
                zmin=0,
                zmax=max(1, max(council_choropleth_trace.z)),
                marker_opacity=0.45,
                marker_line_width=0.5,
                name="Council District Total Units",
                customdata=council_choropleth_trace.customdata,
                hovertemplate=(
                    "Council District: %{location}<br>"
                    "Total affordable units (Total Units): %{customdata[0]}<br>"
                    "Airbnb last 12 month listing (# in district): %{customdata[1]}<br>"
                    "Council District Population: %{customdata[2]}<br>"
                    "District Area: %{customdata[3]:.2f} sq mi"
                    "<extra></extra>"
                ),
                colorbar=dict(
                    title="Total Units",
                    len=0.55,
                    thickness=18,
                    x=0.96,
                    tickformat=",d"
                ),
            )

            fig.add_trace(council_trace)


        # --------------------------------------------------------
        # 4) If both aff_points + council are on, arrange colorbars
        # --------------------------------------------------------
        if "aff_points" in selected_layers and "council" in selected_layers:

            aff_colorbar = None
            council_colorbar = None

            for trace in fig.data:
                if trace.name == "Affordable Housing (points)":
                    aff_colorbar = trace.marker.colorbar
                if trace.name == "Council District Total Units":
                    council_colorbar = trace.colorbar

            if aff_colorbar and council_colorbar:
                # AH slightly left
                aff_colorbar.x = 0.88
                aff_colorbar.y = 0.5
                aff_colorbar.len = 0.55

                # Council slightly right
                council_colorbar.x = 0.96
                council_colorbar.y = 0.5
                council_colorbar.len = 0.55

        # If no layers selected, add an invisible trace so Mapbox renders
        if len(selected_layers) == 0:
            fig.add_trace(go.Scattermapbox(
                lat=[40.7128], lon=[-74.0060],
                mode="markers",
                marker=dict(size=0, opacity=0),
                hoverinfo="skip",
                showlegend=False
            ))

        return fig

    # TRANSIT CALLBACK

    @app.callback(
    [
        Output("transit-main-map", "figure"),
        Output("transit-scatter", "figure"),
        Output("transit-luxury-map", "figure"),
        Output("transit-room-filter", "options"),
    ],
    Input("transit-room-filter", "value")
    )
    def update_transit_dashboard(selected_category):

        # Build dropdown options on load
        dropdown_options = [{"label": "Compare All Categories", "value": "ALL"}] + \
                        [{"label": rt, "value": rt} for rt in df_map['room_type'].unique()]

        # Filter
        if selected_category == "ALL":
            filt = df_map
            categories = room_colors.keys()
        else:
            filt = df_map[df_map['room_type'] == selected_category]
            categories = [selected_category]

        # ------------------------------------------
        # 1. MAP — Listing Locations + Subway
        # ------------------------------------------
        map_fig = go.Figure()

        for rt in categories:
            sub = filt[filt['room_type'] == rt]
            if sub.empty: continue

            # Outline
            map_fig.add_trace(go.Scattermapbox(
                lat=sub['latitude'], lon=sub['longitude'],
                mode="markers",
                marker=dict(size=5, color="white", opacity=0.5),
                hoverinfo="skip",
                showlegend=False
            ))

            # Colored dots
            map_fig.add_trace(go.Scattermapbox(
                lat=sub['latitude'], lon=sub['longitude'],
                mode="markers",
                marker=dict(size=3, opacity=0.8, color=room_colors[rt]),
                name=rt,
                text=sub['price_clean'],
                hovertemplate="Price: $%{text}<extra></extra>"
            ))

        # Subway
        map_fig.add_trace(go.Scattermapbox(
            lat=subway_df['lat'], lon=subway_df['lon'],
            mode="markers",
            marker=dict(size=5, color="black"),
            name="Subway Station",
            hovertext=subway_df['Stop Name']
        ))

        map_fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_center={"lat": 40.7128, "lon": -74.0060},
            mapbox_zoom=10.5,
            margin={"l":0,"r":0,"t":40,"b":0}
        )

        # ------------------------------------------
        # 2. SCATTER — Price vs Distance
        # ------------------------------------------
        scatter_df = filt[(filt["price_clean"] < 1000) & (filt["dist_to_subway_meters"] < 3000)]

        scatter_fig = px.scatter(
            scatter_df,
            x="dist_to_subway_meters",
            y="price_clean",
            color=None if selected_category != "ALL" else "room_type",
            color_discrete_map=room_colors,
            opacity=0.4,
            trendline="ols",
            labels={
                "dist_to_subway_meters": "Distance to Subway (meters)",
                "price_clean": "Price ($)"
            },
            template="plotly_white"
        )

        # ------------------------------------------
        # 3. LUXURY MAP — Avg Price Near Stations
        # ------------------------------------------
        walk = filt[filt['dist_to_subway_meters'] < 800]

        grouped = walk.groupby("nearest_station_idx")['price_clean'].median()
        listing_count = walk.groupby("nearest_station_idx")['price_clean'].count()

        stats = pd.DataFrame({"avg_price": grouped, "count": listing_count}).reset_index()
        merged = subway_df.reset_index().merge(stats, left_on="index", right_on="nearest_station_idx", how="left")
        merged = merged[merged['avg_price'].notna()]

        lux_fig = go.Figure()

        lux_fig.add_trace(go.Scattermapbox(
            lat=merged['lat'],
            lon=merged['lon'],
            mode="markers",
            marker=dict(
                size=12,
                color=merged['avg_price'],
                colorscale="Viridis",
                cmin=0, cmax=300,
                showscale=True
            ),
            text=merged.apply(lambda r: f"{r['Stop Name']}<br>${r['avg_price']:.0f}<br>Listings: {r['count']}", axis=1),
            hoverinfo="text"
        ))

        lux_fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_center={"lat": 40.7128, "lon": -74.0060},
            mapbox_zoom=11,
            margin={"l":0,"r":0,"t":40,"b":0}
        )

        return map_fig, scatter_fig, lux_fig, dropdown_options
    

    # ------------------------------------------------------------
    # 4) CRIME DASHBOARD CALLBACK
    # ------------------------------------------------------------

    @app.callback(
        Output("crime-map", "figure"),
        Input("crime-map-selector", "value")
    )

    def update_crime_visualization(view_mode):

        df = merged_zip_data.copy()

        # Base map settings
        common_layout = dict(
            mapbox_style="carto-positron",
            mapbox_zoom=9.5,
            mapbox_center={"lat": 40.7128, "lon": -74.0060},
            margin={"l":0, "r":0, "t":40, "b":0},
        )

        # --------------------------------------------------------
        # MODE 1: Crime Choropleth
        # --------------------------------------------------------
        if view_mode == "crime":
            fig = px.choropleth_mapbox(
                df,
                geojson=nyc_zip,
                locations="zipcode",
                featureidkey="properties.zipcode",
                color="total_major_crime_reports",
                hover_data=["zipcode", "total_major_crime_reports", "airbnb_count", "average_price"],
                color_continuous_scale="Viridis",
                opacity=0.7,
            )
            fig.update_layout(**common_layout)

            return fig

        # --------------------------------------------------------
        # MODE 2: Airbnb Count Choropleth
        # --------------------------------------------------------
        if view_mode == "airbnb_count":
            fig = px.choropleth_mapbox(
                df,
                geojson=nyc_zip,
                locations="zipcode",
                featureidkey="properties.zipcode",
                color="airbnb_count",
                hover_data=["zipcode", "total_major_crime_reports", "airbnb_count", "average_price"],
                color_continuous_scale="Viridis",
                opacity=0.7,
            )
            fig.update_layout(**common_layout)

            return fig

        # --------------------------------------------------------
        # MODE 3: Average Price Choropleth
        # --------------------------------------------------------
        if view_mode == "average_price":
            fig = px.choropleth_mapbox(
                df,
                geojson=nyc_zip,
                locations="zipcode",
                featureidkey="properties.zipcode",
                color="average_price",
                hover_data=["zipcode", "total_major_crime_reports", "airbnb_count", "average_price"],
                color_continuous_scale="Viridis",
                opacity=0.7,
            )
            fig.update_layout(**common_layout)

            return fig

        # --------------------------------------------------------
        # MODE 4: Bivariate Crime × Airbnb Classification
        # --------------------------------------------------------
        if view_mode == "bivariate":
            fig = px.choropleth_mapbox(
                df,
                geojson=nyc_zip,
                locations="zipcode",
                featureidkey="properties.zipcode",
                color="crime_airbnb_category",
                hover_data=[
                    "zipcode",
                    "total_major_crime_reports",
                    "airbnb_count",
                    "average_price",
                    "crime_airbnb_category"
                ],
                color_discrete_map=crime_color_map,
                opacity=0.75,
            )
            fig.update_layout(**common_layout)

            return fig

        # fallback
        return go.Figure(), "Select a layer to begin."

        