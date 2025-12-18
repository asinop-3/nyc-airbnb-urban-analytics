# NYC Airbnb, Housing, Transit & Neighborhood Analytics - Methodology

## 1. Overview: Domain
This project investigates how short-term rental activity (Airbnb) interacts with urban infrastructure, housing pressure, and neighborhood conditions across New York City. In a city where tourism, public transit, housing affordability, and population density are tightly interconnected, this analysis explores how Airbnb listings relate to transit accessibility, eviction activity, crime reports, residential population patterns, and affordable housing development.

Rather than making causal claims, the project focuses on identifying spatial and statistical patterns at the ZIP-code, Neighborhood Tabulation Area (NTA), and City Council District levels. The goal is to provide a data-driven foundation for understanding how Airbnb activity concentrates across NYC and how it aligns with broader housing and neighborhood dynamics.

The analysis integrates multiple publicly available datasets:
* **Airbnb Listings (Source: Inside Airbnb):** Active Airbnb listings including price, room type, and geographic coordinates.
* **NYC Subway Stations (Source: NY State Open Data):** Geospatial coordinates for all active subway stations.
* **Eviction Filings (Source: NYC Open Data):** Annual eviction case filings aggregated by ZIP code.
* **Major Crime Reports (Source: NYPD / NYC Open Data):** Reported major crime incidents aggregated by ZIP code.
* **NYC Census Population Data (Source: U.S. Census / NYC Planning):** Population counts by Neighborhood Tabulation Area (NTA), used to normalize Airbnb density.
* **Affordable Housing Production (Source: NYC Open Data):** Building-level records of affordable housing units completed between 2014–2024, including unit counts and locations.
* **NYC Council District Boundaries (Source: NYC Open Data):** Administrative boundaries used to aggregate affordable housing activity at the district level.

## 2. Methodology: Data Processing Pipeline
Urban datasets are rarely analysis-ready. To ensure consistency, spatial accuracy, and analytical validity, a multi-stage data cleaning, spatial processing, and integration pipeline was implemented.

### A. Data Cleaning & Standardization
* Each dataset was independently inspected for missing values, invalid geographic identifiers, and duplicate records.
* Airbnb price fields containing currency symbols and string formatting were cleaned and converted to numeric values.
* Records with missing or invalid latitude and longitude values were removed.
* ZIP codes, NTAs, and district identifiers with inconsistent reporting were filtered to maintain alignment across datasets.
* All datasets were standardized to a common coordinate reference system to ensure accurate spatial joins and distance calculations.

### B. Outlier Detection & Filtering
* Extreme anomalies were identified in the Airbnb pricing data, including placeholder listings priced far above realistic market values.
* To prevent these outliers from skewing summary statistics and visualization color scales, nightly prices were capped at a reasonable upper threshold prior to analysis.

### C. Geographic & Spatial Engineering
Because datasets could not be joined using simple neighborhood labels, spatial techniques were required:
* **cKDTree nearest-neighbor search** was used to calculate the distance (in meters) from each Airbnb listing to its closest subway station.
* **Geopandas and Shapely spatial joins** were used to assign Airbnb listing points to Neighborhood Tabulation Areas (NTAs).
* **Council district spatial joins** were applied to aggregate affordable housing units by district boundaries.
* **ZIP-code–level aggregation** was used for eviction and crime data to maintain consistency with administrative reporting boundaries.

### D. Population & Housing Normalization
To account for variation in neighborhood size and population, normalization techniques were applied:
* Airbnb listings were counted within each NTA.
* Counts were divided by total NTA population.
* Values were scaled to **Airbnbs per 10,000 residents**, forming the basis of the Airbnb vs. Housing choropleth map.
* Affordable housing units were aggregated by building and summed at the council district level to examine spatial relationships between short-term rentals and long-term housing development.

### E. Dataset Integration
After cleaning, spatial processing, and temporal alignment, all datasets were merged into unified, analysis-ready tables. Variable names were standardized for clarity, and derived metrics were created to support exploratory visualization, correlation analysis, and clustering.

## 3. Dashboard & Visualization User Guide
The interactive dashboard is designed for exploration rather than prediction, allowing users to examine Airbnb activity across NYC under multiple analytical lenses.

### Global Controls
* **Filter by Room Type:** View patterns for Entire Homes, Private Rooms, Shared Rooms, or Hotel Rooms.
* **Hover Interactions:** Tooltips display exact values for each geographic unit.
* **View Switching:** Users can move between maps and plots to explore different relationships.

### Layer 1: Airbnb Distribution Map (Geographic Patterns)
* **Visualization:** Point map of Airbnb listings across NYC.
* **Insight:** Reveals dense clustering in Manhattan and transit-accessible areas, with increasing dispersion into outer boroughs depending on room type.

### Layer 2: Airbnb vs. Transit Scatter Plot (Convenience Premium)
* **Visualization:** Distance to nearest subway station (X-axis) vs. nightly Airbnb price (Y-axis).
* **Trendline:** Ordinary Least Squares (OLS) regression line summarizes the relationship.
* **Interpretation:**
    * **Downward slope:** Indicates a “convenience premium,” where proximity to transit is associated with higher prices.
    * **Flat slope:** Suggests transit saturation or reduced price sensitivity.

### Layer 3: The “Luxury Lines” Map (Transit Economic Overlay)
* **Visualization:** Subway stations are colored based on nearby Airbnb prices.
* **Method:** Stations are colored using the median Airbnb price within an 800m (~10-minute walk) radius.
* **Insight:** Bright colors indicate high-value corridors, while darker tones represent more affordable zones, visualizing economic patterns through transit access.

### Layer 4: Airbnb vs. Housing Choropleth (Population-Normalized)
* **Visualization:** Choropleth map showing Airbnbs per 10,000 residents by NTA.
* **Purpose:** Adjusts for population size to reveal neighborhoods with disproportionately high Airbnb presence.
* **Insight:** Highlights areas where short-term rentals may exert greater housing pressure relative to resident population.

### Layer 5: Affordable Housing & District-Level Context
* **Visualization:** Council district–level maps aggregating affordable housing units.
* **Purpose:** Provides political and administrative context for housing development.
* **Insight:** Allows comparison between short-term rental concentration and long-term affordable housing investment across districts.

### Layer 6: Airbnb, Evictions & Crime (Neighborhood Conditions)
* **Visualization:** Scatter plots and ZIP-level choropleths comparing Airbnb density with eviction filings and crime reports.
* **Trendlines:** OLS regression lines summarize overall associations.
* **Insight:** Explores whether higher Airbnb activity aligns with increased housing instability or public safety indicators.

### Layer 7: Clustering & Pattern Detection
* **Visualization:** K-means clustering groups ZIP codes with similar profiles.
* **Purpose:** Identifies shared neighborhood typologies (e.g., high Airbnb / high eviction).
* **Insight:** Reveals multidimensional patterns not visible in single-variable analyses.

## 4. Limitations & Future Work
* **Correlation vs. Causation:** All findings are observational and do not imply causal relationships.
* **Geographic Boundaries:** ZIP codes, NTAs, and council districts may mask within-neighborhood variation.
* **Reporting Bias:** Eviction, crime, and housing data may be underreported or inconsistently recorded.
* **Distance Measurement:** Transit distances are calculated using Euclidean distance rather than actual walking routes.
* **Temporal Scope:** The analysis reflects snapshots in time and does not fully capture seasonal or long-term trends.
* **Future Work:** Could incorporate network-based walking distances, time-series analysis, zoning and policy overlays, or additional socioeconomic variables to deepen interpretation.

