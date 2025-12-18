import dash
from layout import create_layout
import plotly.graph_objects as go

# TOKEN-FREE MAPS:
go.layout.mapbox.style = "open-street-map"

# Create Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Set layout immediately (required by Plotly Cloud)
app.layout = create_layout()

# ---- Register callbacks AFTER app is fully created ----
# Import inside runtime, not at module import level
from callbacks import register_callbacks
register_callbacks(app)

# Local-only execution
if __name__ == "__main__":
    app.run_server(debug=True)
