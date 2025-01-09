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

        # Make initial plot
        selected_sequence = PLOTLY_DEFAULT_COLORS
        fig = px.bar(value_counts, x=x_feature, y=y_feature, color=color_feature, color_discrete_sequence=selected_sequence)

        # If the user clicks a bar, grey out all other bars
        if trigger == "stacked_bar":
            #print(bar_clicked) #TEST
            curveNumber = bar_clicked["points"][0]["curveNumber"]
            pointNumber = bar_clicked["points"][0]["pointNumber"]
            x = bar_clicked["points"][0]["x"]
            #selected_color = PLOTLY_DEFAULT_COLORS[curveNumber % len(PLOTLY_DEFAULT_COLORS)]  # TEST

            # Regular bar chart
            if(color_feature == x_feature):
                # In this case a "trace" is one bar
                fig.for_each_trace(lambda trace: trace.update(marker_color = '#bababa') if trace.x != x else ()) # Set all unselected traces to grey
            
            # Stacked bar chart
            else:
                # In this case a trace consists of all sub-bars of the same type (i.e. all "injured" sub-bars)
                trace_names = value_counts[color_feature].drop_duplicates()  # Trace names are the unique values of the color feature
                fig.for_each_trace(lambda trace: trace.update(marker_color = '#bababa') if trace.name != trace_names[curveNumber] else ())  # Set all unselected *traces* to grey
                #fig.for_each_trace(lambda trace: print(trace.x)) # TEST
                fig.update_traces(selectedpoints = [pointNumber])  # Selects the full bar that was clicked (i.e. selects all sub-bars with the same pointNumber)
                fig.update_traces(unselected_marker_color = '#BABABA')  # Sets all unselected *bars* to grey

        return fig
    
    return dcc.Graph(id = id)
