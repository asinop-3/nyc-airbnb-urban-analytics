# Visual Analytics Final Project

Creating an interactive web map for our final project in Data Visualization, Fall 2025.

## Getting the Project Running

I used an Anaconda environment with VS Code. Whatever you use, make sure to also have the dependencies installed (dash, plotly, pandas, etc).

To see the map:

&nbsp;&nbsp;&nbsp;&nbsp;Run app.py (I do this from VS Code, but you can use the terminal)
  
&nbsp;&nbsp;&nbsp;&nbsp;Open a browser and navigate to the link provided by the file
  
&nbsp;&nbsp;&nbsp;&nbsp;Should be: http://127.0.0.1:8050/

## Project Structure

data_manager.py - Handles data loading, preprocessing, and initial map creation

app.py - Creates core Dash instance

layout.py - Visual structure. Holds all HTML components for the UI

callbacks.py - Contains all callbacks that make the Dash app interactive

run.py - How to launch our project

FOLDERS:

data - Holds all of our data files

data_cleaning - Holds all of our data cleaning files

EDA - Holds all of our EDA
