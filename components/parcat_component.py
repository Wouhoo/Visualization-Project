from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from pandas import DataFrame
from .data_cleaning import filter_low_freq

"""
Creates a new parallel categories component instance.
Dash app - The application (used for callbacks)
DataFrame data - Our pandas dataset
String id - A unique ID not used by any other component in our app

@Returns: A dcc.Graph containing the parallel categories plot
"""

app = Dash(__name__)

def render(app: Dash, id: str, data: DataFrame)-> dcc.Graph:
    @app.callback(
        Output("parcat", "figure"),
        [Input("map", "selectedData")]#,
         #Input("scatterplot_dropdown_x", "value"),
         #Input("scatterplot_dropdown_y", "value")]
    )
    def update_figure(selected_data): #, x_feature, y_feature
        select_all_points = False

        # Empty PC plot if no features are provided
        if selected_data is None:
            select_all_points = True

        # Filter data based on selection in map
        ids = []
        if not select_all_points:
            for point in selected_data["points"]:
                ids.append(point["customdata"][0])
        filtered_data = data.copy().loc[data["UID"].isin(ids)] if select_all_points == False else data.copy()

        # Which columns to show (currently hardcoded, should be selectable)
        dimensions = ['Shark.name', 'Site.category', 'Victim.injury']

        if len(filtered_data) == 0:
            return px.parallel_categories(None)
        
        # Group low-frequency values into "other" category to prevent clutter
        for feature in dimensions:
            filtered_data = filter_low_freq(filtered_data, feature)

        # Make parallel categories plot
        fig = px.parallel_categories(filtered_data,
                                     dimensions=dimensions)
        return fig
    
    return dcc.Graph(id = id)
