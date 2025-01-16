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

#Plotly default color sequence (in order of normal selection).
PLOTLY_DEFAULT_COLORS = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692',
                        '#B6E880','#FF97FF','#FECB52']

app = Dash(__name__)

def render(app: Dash, id: str, data: DataFrame)-> dcc.Graph:
    @app.callback(
        Output("parcat", "figure"),
        [Input("data_store", "data"),
         Input("parcat_dropdown", "value"),
         Input("primary_color_dropdown", "value")]
    )
    def update_figure(selected_data, selected_features, primary_color_feature):
        # Read data from data storage
        if selected_data is None:
            selected_data = data
        selected_data = DataFrame(selected_data)
        filtered_data = selected_data.loc[selected_data['selected'] == 1]  # Only consider selected points

        # Return empty plot if no features are selected
        if selected_features is None or len(selected_features) == 0:
            return px.parallel_categories(dimensions=[])

        # Make PCP with color according to selected dropdown values
        # If anything is brushed, apply brushing colors - this is highest priority.
        if any([color != '#bababa' for color in filtered_data['highlighted']]):
            fig = px.parallel_categories(filtered_data, dimensions=selected_features, color='highlighted')
        # If nothing is brushed, but a barplot x feature is selected, color according to that feature
        elif not(primary_color_feature is None or primary_color_feature == []):
            # This should be doable with the line below, like we do it for the barplot and scattermap as well;
            #fig = px.parallel_categories(filtered_data, dimensions=selected_features, color=primary_color_feature)
            # However, for some godforsaken reason it won't work, so that's why we do this mess instead:
            barplot_x_values = filtered_data[primary_color_feature].value_counts().index.tolist()  # Get unique values for barplot x attribute
            colors = filtered_data[primary_color_feature].apply(lambda x: PLOTLY_DEFAULT_COLORS[barplot_x_values.index(x) % len(PLOTLY_DEFAULT_COLORS)])  # Color according to attribute value
            fig = px.parallel_categories(filtered_data, dimensions=selected_features, color=colors)
        # Otherwise, don't apply color at all
        else:
            colors = ['#bababa']*len(filtered_data)
            fig = px.parallel_categories(filtered_data, dimensions=selected_features, color=colors)

        return fig
    
    return dcc.Graph(id = id)
