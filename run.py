from app import app
from layout import create_layout
from callbacks import register_callbacks
import data_manager
import utils
from layouts import airbnb_only_layout, affordable_housing_layout

# 1. Set the layout
app.layout = create_layout()

# 2. Register all callbacks
register_callbacks(app)

# 3. Run the app
if __name__ == '__main__': 
    app.run_server(debug=True)