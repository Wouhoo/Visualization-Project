from dash import Dash, html, dcc, Input, Output, ctx
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

#Plotly default color sequence (in order of normal selection).
PLOTLY_DEFAULT_COLORS = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692',
                        '#B6E880','#FF97FF','#FECB52']

# Actual render function
def render(app: Dash, id: str, data: DataFrame)-> dcc.Graph:
    @app.callback(
        Output("stacked_bar", "figure"),
        [Input("map", "selectedData"),
         Input("stackedbar_dropdown_x", "value"),
         Input("stackedbar_dropdown_color", "value"),
         Input("stackedbar_normalize_checkbox", "value"),
         Input("stacked_bar", "clickData")]
    )
    def update_figure(selected_data, x_feature, color_feature, normalize, bar_clicked):
        trigger = ctx.triggered_id
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

        ### Code from Nick's barplot component for selecting & Brushing bars ###

        #Sorting values (and thus frequencies) for better visualization
        #plotted_data = {j:i for i,j in zip(values,frequencies)}
        #sorted_plotted_data = {k: v for k, v in sorted(plotted_data.items(), key=lambda item: item[1])}
        #values = list(sorted_plotted_data.values())
        #frequencies = list(sorted_plotted_data.keys())

        #selected_color = [str(i) for i in values]
        #selected_sequence = PLOTLY_DEFAULT_COLORS

        #If the trigger is clicking on a bar, change colors to focus on that bar.
        selected_sequence = PLOTLY_DEFAULT_COLORS
        if trigger == "stacked_bar":
            print(bar_clicked) #TEST
            colorIndex = bar_clicked["points"][0]["curveNumber"]
            #print("Colorindex:", colorIndex) # TEST
            print(filtered_data[color_feature].drop_duplicates()) #TEST
            no_colors = filtered_data[color_feature].drop_duplicates()  # Number of unique values for the color feature = number of colors used

            # Default bar chart
            if(color_feature == x_feature):
                selected_sequence = ["#bababa"]*len(no_colors)
                selected_sequence[colorIndex] = PLOTLY_DEFAULT_COLORS[colorIndex % len(PLOTLY_DEFAULT_COLORS)]
            # Stacked bar chart - TODO
            else:
                # In this case we'd want the user to be able to select a *sub-bar* (e.g. only highlight Fatal incidents in Queensland)
                # My first intuition to make this happen was to make the sequence s.t. only the clicked sub-bar (with the correct curve number *and* point number)
                # has a non-gray color. But plotly goes through the same color sequence for every bar, so this won't work.
                # It appears we *need* some way to override the color sequence for a specific (sub-)bar...
                selected_sequence = ["#bababa"]*len(no_colors)
                selected_sequence[colorIndex] = PLOTLY_DEFAULT_COLORS[colorIndex % len(PLOTLY_DEFAULT_COLORS)]

        #fig = px.bar(filtered_data, x= values, y = frequencies, color=selected_color,color_discrete_sequence=selected_sequence)
        # Make the plot
        fig = px.bar(value_counts, x=x_feature, y=y_feature, color=color_feature, color_discrete_sequence=selected_sequence)

        return fig
    
    return dcc.Graph(id = id)
