from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from pandas import DataFrame

"""
Creates a new scatterplot component instance.
Dash app - The application (used for callbacks)
DataFrame data - Our pandas dataset
String id - A unique ID not used by any other component in our app

@Returns: A dcc.Graph containing the scatterplot

NOTE: This component is not to be used (in its current state), as a scatterplot turns out to be unhelpful for our (mostly categorical) data.
"""

app = Dash(__name__)

def render(app: Dash, id: str, data: DataFrame)-> dcc.Graph:
    @app.callback(
        Output("scatterplot", "figure"),
        [Input("map", "selectedData"),
         Input("stackedbar_dropdown_x", "value"),
         Input("stackedbar_dropdown_color", "value")]
    )
    def update_figure(selected_data, x_feature, y_feature):
        select_all_points = False

        # Empty scatterplot if no features are provided
        if x_feature == [] or y_feature == []:
            return px.scatter(None)
        else:
            if selected_data is None:
                select_all_points = True

        # Filter data
        ids = []
        if not select_all_points:
            for point in selected_data["points"]:
                ids.append(point["customdata"][0])
        filtered_data = data.loc[data["UID"].isin(ids)] if select_all_points == False else data

        if len(filtered_data) == 0:
            return px.scatter(None)

        # Make scatterplot
        fig = px.scatter(filtered_data, x = x_feature, y = y_feature)
        return fig
    
    return dcc.Graph(id = id)
