from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from pandas import DataFrame
from .data_cleaning import filter_low_freq

"""
Creates a new scatterplot component instance.
Dash app - The application (used for callbacks)
DataFrame data - Our pandas dataset
String id - A unique ID not used by any other component in our app

@Returns: A dcc.Graph containing the scatterplot

NOTE: This component is not to be used (in its current state), as a scatterplot turns out to be unhelpful for our (mostly categorical) data.
"""

app = Dash(__name__)

# Actual render function
def render(app: Dash, id: str, data: DataFrame)-> dcc.Graph:
    @app.callback(
        Output("stacked_bar", "figure"),
        [Input("map", "selectedData"),
         Input("stackedbar_dropdown_x", "value"),
         Input("stackedbar_dropdown_color", "value"),
         Input("stackedbar_normalize_checkbox", "value")]
    )
    def update_figure(selected_data, x_feature, color_feature, normalize):
        select_all_points = False

        if x_feature == [] or x_feature == "-":
            return px.bar(None)
        else:
            if color_feature == [] or color_feature == "-": # Effectively this uses the default bar chart if no color attribute is selected
                color_feature = x_feature
            if selected_data is None:
                select_all_points = True

        # Filter data based on map selection
        ids = []
        if not select_all_points:
            for point in selected_data["points"]:
                ids.append(point["customdata"][0])
        filtered_data = data.loc[data["UID"].isin(ids)] if select_all_points == False else data

        if len(filtered_data) == 0:
            return px.bar(None)
        
        # Group low-frequency values into "other" category to prevent clutter
        for feature in [x_feature, color_feature]:
            filtered_data = filter_low_freq(filtered_data, feature)
        
        # Calculate number of incidents for each unique x value
        # Returns a df with 3 columns: x_feature, color_feature, and the number of incidents for that (x_feature, color_feature) combination
        value_counts = pd.DataFrame(filtered_data.groupby([x_feature])[color_feature].value_counts(normalize=normalize)).reset_index()
        y_feature = 'proportion' if normalize else 'count' 
        #print(value_counts) # TEST: if you want to see what the table looks like

        # Make the plot
        fig = px.bar(value_counts, x=x_feature, y=y_feature, color=color_feature)

        ### Code from Nick's barplot component for selecting & Brushing bars ###

        #Sorting values (and thus frequencies) for better visualization
        #plotted_data = {j:i for i,j in zip(values,frequencies)}
        #sorted_plotted_data = {k: v for k, v in sorted(plotted_data.items(), key=lambda item: item[1])}
        #values = list(sorted_plotted_data.values())
        #frequencies = list(sorted_plotted_data.keys())

        #selected_color = [str(i) for i in values]
        #selected_sequence = PLOTLY_DEFAULT_COLORS

        #If the trigger is clicking on a bar, change colors to focus on that bar.
        #if trigger == "bar_plot":
        #    colorIndex = bar_clicked["points"][0]["curveNumber"]
        #    selected_sequence = ["#bababa"]*len(selected_color)
        #    selected_sequence[colorIndex] = PLOTLY_DEFAULT_COLORS[colorIndex % len(PLOTLY_DEFAULT_COLORS)]

        #fig = px.bar(filtered_data, x= values, y = frequencies, color=selected_color,color_discrete_sequence=selected_sequence)
        return fig
    
    return dcc.Graph(id = id)
