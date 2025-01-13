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
        [Input("data_store", "data"),
         Input("parcat_dropdown", "value"),
         Input("stackedbar_dropdown_x", "value")]
    )
    def update_figure(selected_data, selected_features, barplot_x_feature):
        # Read data from data storage
        if selected_data is None:
            selected_data = data
        selected_data = DataFrame(selected_data)
        filtered_data = selected_data.loc[selected_data['selected'] == 1]  # Only consider selected points

        # Return empty plot if no features are selected
        if selected_features is None or len(selected_features) == 0:
            return px.parallel_categories(dimensions=[])

        # Make PCP with color according to selected dropdown values
        print("BARPLOT FEATURE: ", barplot_x_feature)
        print("DATA COLUMNS: ", filtered_data.columns)
        #if barplot_x_feature in selected_features:
        #    fig = px.parallel_categories(filtered_data, dimensions=selected_features, color=barplot_x_feature)
        #else:
        #    fig = px.parallel_categories(filtered_data, dimensions=selected_features)
        fig = px.parallel_categories(filtered_data, dimensions=selected_features)

        return fig
    
    return dcc.Graph(id = id)
