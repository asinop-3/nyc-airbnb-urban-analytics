# this file is to handle any data loading and preprocessing
# will also initialize base version of map

import pandas as pd
import plotly.express as px
import json
import os
import sys
import plotly.graph_objects as go
from utils import point_in_district, point_in_ring
from scipy.spatial import cKDTree

# folder name for easy use
DATA_DIR = "data"

# this is where we construct paths to our data
# add whatever you need here to access your respective data files
AIRBNB_FILE = os.path.join(DATA_DIR, "airbnb_one_year.csv") # change this to one year file
AFFORDABLE_HOUSING_FILE = os.path.join(DATA_DIR, "Affordable_Housing_Production_by_Building.csv")
COUNCIL_GEOJSON_FILE = os.path.join(DATA_DIR, "nycc.json")
TAB_GEOJSON = os.path.join(DATA_DIR, "NYC_Neighborhood_Tabulation_Areas_2020.geojson")
AIRBNB_10K = os.path.join(DATA_DIR, "NTA_airbnb_10k.csv")
CRIME_ZIP_CSV = os.path.join(DATA_DIR, "merged_zip_data.csv")
ZIP_GEOJSON = os.path.join(DATA_DIR, "nyc_zipcodes.geojson")

# NYC bounding box
NYC_LAT_MIN = 40.45
NYC_LAT_MAX = 40.95
NYC_LON_MIN = -74.30
NYC_LON_MAX = -73.65

### LOAD DATA ### 

airbnb_df = pd.read_csv(AIRBNB_FILE) # airbnb data 

borough_list = airbnb_df['neighborhood_group_cleansed'].unique().tolist() # list for each borough 

aff_raw = pd.read_csv(AFFORDABLE_HOUSING_FILE) # affordable housing

airbnb_10k = pd.read_csv(AIRBNB_10K) # airbnb per 10k

with open(COUNCIL_GEOJSON_FILE, "r") as f: # council geojson
        council_geojson = json.load(f)

with open(TAB_GEOJSON, "r") as f:
    nta_geojson = json.load(f)

merged_zip_data = pd.read_csv(CRIME_ZIP_CSV)

with open(ZIP_GEOJSON, "r") as f:
    nyc_zip = json.load(f)

### DEFINE BASE MAP ###

base_map = go.Figure()

base_map.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=9.5,
    mapbox_center={"lat": 40.7, "lon": -74.0},
    height=600,
    margin={"l":0, "r":0, "t":0, "b":0}
)

# Fatima, most of your code logic is here now:

# -------------------------------------------------------------
# AFFORDABLE HOUSING POINTS (LAYER 2)
# -------------------------------------------------------------
# We'll use Building Completion Date to derive a year filter
aff_points = aff_raw.copy()

# Convert numeric fields
aff_points["Latitude"] = pd.to_numeric(aff_points["Latitude"], errors="coerce")
aff_points["Longitude"] = pd.to_numeric(aff_points["Longitude"], errors="coerce")
aff_points["All Counted Units"] = pd.to_numeric(
    aff_points["All Counted Units"], errors="coerce"
)

# Parse completion year from Building Completion Date
aff_points["Building Completion Date"] = pd.to_datetime(
    aff_points["Building Completion Date"], errors="coerce"
)
aff_points["CompletionYear"] = aff_points["Building Completion Date"].dt.year

# Keep rows with coordinates, units, and a valid completion year
aff_points = aff_points.dropna(
    subset=["Latitude", "Longitude", "All Counted Units", "CompletionYear"]
)

# NEW: only keep affordable housing points inside NYC bounding box
aff_points = aff_points[
    aff_points["Latitude"].between(NYC_LAT_MIN, NYC_LAT_MAX)
    & aff_points["Longitude"].between(NYC_LON_MIN, NYC_LON_MAX)
].copy()

# Determine slider range from available years
if not aff_points["CompletionYear"].dropna().empty:
    min_year = int(aff_points["CompletionYear"].min())
    max_year = int(aff_points["CompletionYear"].max())
else:
    # Fallback if no valid years (arbitrary)
    min_year = 2000
    max_year = 2025

# -------------------------------------------------------------
# COUNCIL DISTRICTS FROM nycc.json (LAYER 3)
# -------------------------------------------------------------
# nycc.json must be a FeatureCollection with "features" list.

features = council_geojson.get("features", [])
if not features:
    raise ValueError("nycc.json has no features.")

# Auto-detect the council district property name
district_prop = None
sample_props = features[0].get("properties", {})
for key in sample_props.keys():
    kl = key.lower()
    # handle "District", "district", "coundist", "council district", etc.
    if kl in ("district", "coundist", "council district", "council_dist") or (
        "coun" in kl and "dist" in kl
    ):
        district_prop = key
        break

if district_prop is None:
    raise ValueError(
        f"Could not find a council district field in nycc.json. "
        f"Properties in first feature: {list(sample_props.keys())}"
    )

# Normalize council district into a standard 'COUNDIST' property (int)
# Also extract population (Adj_Population) and area (Area) for each district,
# and store polygon rings for point-in-polygon tests.
pop_lookup = {}
area_lookup = {}
polygons_by_dist = {}

for feat in features:
    props = feat.get("properties", {})
    geom = feat.get("geometry", {})
    raw_val = props.get(district_prop)

    try:
        did = int(raw_val)
    except (TypeError, ValueError):
        did = None

    props["COUNDIST"] = did

    # Population and area from properties
    pop_val = props.get("Adj_Population")
    area_val = props.get("Area")  # NOTE: this is already in square miles

    if did is not None:
        pop_lookup[did] = pop_val
        area_lookup[did] = area_val

    # Extract exterior rings from geometry for spatial join
    rings = []
    gtype = geom.get("type")
    coords = geom.get("coordinates")

    if did is not None and gtype and coords:
        if gtype == "Polygon":
            # coords: [ [ [lon, lat], ... ] ]  (outer ring + holes)
            if len(coords) > 0:
                rings.append(coords[0])  # exterior ring only
        elif gtype == "MultiPolygon":
            # coords: [ [ [ [lon, lat], ... ], ... ], ... ]
            for poly in coords:
                if poly and len(poly) > 0:
                    rings.append(poly[0])  # exterior ring of each polygon

    if did is not None:
        polygons_by_dist[did] = rings

    feat["properties"] = props

# Save back mutated features
council_geojson["features"] = features

# -------------------------------------------------------------
# SPATIAL JOIN: COUNT AIRBNB LISTINGS PER DISTRICT
# -------------------------------------------------------------
airbnb_counts = {dist: 0 for dist in polygons_by_dist.keys()}

for _, row in airbnb_df.iterrows():
    lon = row.get("longitude")
    lat = row.get("latitude")
    if pd.isna(lon) or pd.isna(lat):
        continue

    # Check which district this point falls into (first match wins)
    for dist, rings in polygons_by_dist.items():
        if not rings:
            continue
        if point_in_district(lon, lat, rings):
            airbnb_counts[dist] += 1
            break

# -------------------------------------------------------------
# SUM TOTAL UNITS PER COUNCIL DISTRICT (CSV)
# -------------------------------------------------------------
aff_units = aff_raw.copy()
aff_units["Council District"] = pd.to_numeric(
    aff_units["Council District"], errors="coerce"
)
aff_units["Total Units"] = pd.to_numeric(
    aff_units["Total Units"], errors="coerce"
)

# Keep rows with valid district + total units
aff_units = aff_units.dropna(subset=["Council District", "Total Units"])

# Group by council district (for polygon layer) using Total Units
aff_by_council = (
    aff_units.groupby("Council District", as_index=False)["Total Units"]
    .sum()
    .rename(
        columns={
            "Council District": "COUNDIST",
            "Total Units": "total_units",
        }
    )
)

# Convert COUNDIST to int (and string for Plotly locations)
aff_by_council["COUNDIST"] = pd.to_numeric(
    aff_by_council["COUNDIST"], errors="coerce"
).astype("Int64")
aff_by_council = aff_by_council.dropna(subset=["COUNDIST"])
aff_by_council["COUNDIST_str"] = aff_by_council["COUNDIST"].astype(str)

# Map population, area, and Airbnb counts onto the council table
aff_by_council["Population"] = aff_by_council["COUNDIST"].map(pop_lookup)
aff_by_council["Area_sqmi"] = aff_by_council["COUNDIST"].map(area_lookup)
aff_by_council["airbnb_listings"] = (
    aff_by_council["COUNDIST"].map(airbnb_counts).fillna(0).astype(int)
)

# Color scale limits
max_units = aff_by_council["total_units"].max()
if pd.isna(max_units) or max_units <= 0:
    max_units = 1

# Build customdata for hover: [Total Units, # of listing, Population, Area_sqmi]
customdata = aff_by_council[
    ["total_units", "airbnb_listings", "Population", "Area_sqmi"]
].values

# Pre-build council district choropleth trace using Plotly only
council_choropleth_trace = go.Choroplethmapbox(
    geojson=council_geojson,
    locations=aff_by_council["COUNDIST_str"],
    z=aff_by_council["total_units"],
    featureidkey="properties.COUNDIST",
    colorscale="YlOrRd",
    zmin=0,
    zmax=max_units,
    marker_opacity=0.45,
    marker_line_width=0.5,
    name="Council District Total Units",
    colorbar=dict(
        title="Total Units",
        x=1.08,
        y=0.5,
        len=0.9,
        thickness=20,
    ),
    customdata=customdata,
    hovertemplate=(
        "Council District: %{location}<br>"
        "Total affordable units (Total Units): %{customdata[0]}<br>"
        "Airbnb last 12 month listing (# of listings in this district): %{customdata[1]}<br>"
        "Council District Population (people currently living in this district): %{customdata[2]}<br>"
        "Council District Area: %{customdata[3]:.2f} square miles"
        "<extra></extra>"
    ),
)

### TRANSIT STUFF
all_listings = airbnb_df.copy()

# Clean price
df_clean = all_listings.dropna(subset=["price"]).copy()
df_clean['price_clean'] = df_clean['price'].replace('[$,]', '', regex=True).astype(float)

# Median price per listing
df_map = df_clean.groupby(
    ['id','latitude','longitude','neighborhood_group_cleansed','room_type']
    )['price_clean'].median().reset_index()

df_map = df_map[df_map['price_clean'] <= 5000]

# -------------------------------------------------
# Load Subway stations
# -------------------------------------------------
subway_df = pd.read_csv("https://data.ny.gov/api/views/39hk-dx4f/rows.csv?accessType=DOWNLOAD")
subway_df = subway_df.rename(columns={'GTFS Latitude': 'lat', 'GTFS Longitude': 'lon'})

# -------------------------------------------------
# Compute nearest subway distance for each listing
# -------------------------------------------------
coords_list = df_map[['latitude','longitude']].values
coords_stations = subway_df[['lat','lon']].values

tree = cKDTree(coords_stations)
distances, indices = tree.query(coords_list, k=1)

df_map['nearest_station_idx'] = indices
df_map['dist_to_subway_meters'] = distances * 111139

# -------------------------------------------------
# Colors
# -------------------------------------------------
room_colors = {
    "Entire home/apt": "#FDE725",  # yellow
    "Private room":    "#7AD151",  # green
    "Shared room":     "#22A884",  # teal
    "Hotel room":      "#440154",  # purple
}

### CRIME

crime_color_map = {
    "High crime / High listings": "#FDE725",  # yellow
    "High crime / Low listings":  "#7AD151",  # green
    "Low crime / High listings":  "#21918C",  # teal/blue
    "Low crime / Low listings":   "#440154",  # purple
}

# ------------------------------------------------------------
# CRIME / AIRBNB BIVARIATE CATEGORY + ZIP NORMALIZATION
# ------------------------------------------------------------

# Ensure ZIP codes are 5-digit strings
merged_zip_data["zipcode"] = (
    merged_zip_data["zipcode"]
    .astype(str)
    .str.zfill(5)
)

# Ensure the ZIP GeoJSON properties also match 5-digit ZIPs
if "features" in nyc_zip:
    for feature in nyc_zip["features"]:
        props = feature.get("properties", {})
        if "zipcode" in props:
            props["zipcode"] = str(props["zipcode"]).zfill(5)

# Compute medians for category breaks
crime_median = merged_zip_data["total_major_crime_reports"].median()
airbnb_median = merged_zip_data["airbnb_count"].median()

def classify_zip(row):
    crime = row["total_major_crime_reports"]
    airbnb = row["airbnb_count"]

    if crime >= crime_median and airbnb >= airbnb_median:
        return "High crime / High listings"
    elif crime >= crime_median and airbnb < airbnb_median:
        return "High crime / Low listings"
    elif crime < crime_median and airbnb >= airbnb_median:
        return "Low crime / High listings"
    else:
        return "Low crime / Low listings"

# Add bivariate classification column
merged_zip_data["crime_airbnb_category"] = merged_zip_data.apply(classify_zip, axis=1)

# Enforce ordering (helps produce nice legends)
merged_zip_data["crime_airbnb_category"] = pd.Categorical(
    merged_zip_data["crime_airbnb_category"],
    categories=[
        "High crime / High listings",
        "High crime / Low listings",
        "Low crime / High listings",
        "Low crime / Low listings"
    ],
    ordered=True
)
