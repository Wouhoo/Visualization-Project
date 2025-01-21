import pandas as pd
from pandas import DataFrame
from dash import Dash, Input, Output, State, dcc, ctx

"""
In the new "centralized dataframe" architecture, this component is responsible for
storing and modifying the central dataframe.
It takes selections from all other components as inputs and returns the dataframe as output,
which is then used as input by all other components.
"""

#Plotly default color sequence (in order of normal selection).
PLOTLY_DEFAULT_COLORS = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692',
                        '#B6E880','#FF97FF','#FECB52']

# Columns where low-frequency data should be grouped into an "other" category
GROUPABLE_FEATURES = ["Incident.year", "Site.category", "No.sharks", "Victim.activity", "Present.at.time.of.bite", 
                      "Injury.location", "Injury.severity", "Victim.age", "Diversionary.action.taken", 
                      "Data.source", "Shark.name"]  

# Custom sort order for month
MONTH_ORDER = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}

# Opacity of points not selected on the map
UNSELECTED_OPACITY = 0.05
GRAYED_OUT_COLOR = '#bababa'

app = Dash(__name__)

def store(app: Dash, id: str, all_data: DataFrame)-> dcc.Store:
    @app.callback(
        Output("data_store", "data"),
        [Input("map", "selectedData"),
         Input("slider", "value"),
         Input("stacked_bar", "clickData"),
         Input("parcat", "clickData"),
         Input("clear_selection_button", "n_clicks"),
         State("primary_color_dropdown", "value"),
         State("secondary_color_dropdown", "value")]
    )
    def filter_dataframe(map_selected_data, input_year, bar_clicked, parcat_clicked, clear_selection_button, primary_color_feature, secondary_color_feature):
        filtered_data = all_data.copy()
        trigger = ctx.triggered_id  # Find out which figure was clicked

        ### Filter based on map selection & timescale ###
        # Note: "selected" is the opacity value the point should have on the map (1 if selected, 0.05 if not)
        # Timescale selection
        # "Hard-filter" version: points outside the selected year range are outright removed from the dataframe
        filtered_data = filtered_data.loc[(filtered_data['Incident.year'] >= input_year[0]) & (filtered_data['Incident.year'] <= input_year[1])]
        # "Soft-filter" version: points outside the selected year range are set to selected = 0
        #filtered_data['selected'] = filtered_data['Incident.year'].apply(lambda year: 1 if (year >= input_year[0] and year <= input_year[1]) else UNSELECTED_OPACITY)
        # Map selection
        if(map_selected_data is None):
            filtered_data['selected'] = [1]*len(filtered_data)  # In this case all data is selected
        else:
            #print("MAP DATA: ", [point['customdata'][0] for point in map_selected_data['points']])  # TEST
            selected_ids = [point['customdata'][0] for point in map_selected_data['points']]  # Row numbers of selected points
            filtered_data['selected'] = filtered_data['UID'].apply(lambda id: 1 if id in selected_ids else UNSELECTED_OPACITY) 

        ### Group low-frequency points ###
        # Group low-frequency points into an "other" category to reduce clutter (particularly in the bar and PC plots) 
        # Which features are considered groupable is defined above.
        for feature in GROUPABLE_FEATURES:
            filtered_data = filter_low_freq(filtered_data, feature)

        ### Highlight based on clicked bar in barplot or PCP ###
        # Note: "highlighted" is the color the point should have in all plots (colored if highlighted, grey (#bababa) otherwise)
        # User clicked on barplot bar
        if trigger == "stacked_bar":
            color_index = bar_clicked["points"][0]["curveNumber"]  # Index of bar (default) or trace (stacked) in bar chart
            selected_color = PLOTLY_DEFAULT_COLORS[color_index % len(PLOTLY_DEFAULT_COLORS)]  # Actual selected color
            selected_x_value = bar_clicked["points"][0]["x"] # x feature value corresponding to the selected (sub-)bar

            # Default bar chart
            if(secondary_color_feature is None or secondary_color_feature == []):
                filtered_data["highlighted"] = filtered_data[primary_color_feature].apply(lambda x : selected_color if x == selected_x_value else GRAYED_OUT_COLOR)  # Select incidents to highlight

            # Stacked bar chart
            else:
                color_names = filtered_data[secondary_color_feature].value_counts().index.tolist()  # Unique values for barplot color feature
                color_names = sorted(color_names)  # Sort alphabetically
                selected_color_value = color_names[color_index]  # Color feature value corresponding to the selected sub-bar
                filtered_data["highlighted"] = filtered_data.apply(lambda row : selected_color if (row[primary_color_feature] == selected_x_value and row[secondary_color_feature] == selected_color_value) else GRAYED_OUT_COLOR, axis=1)
        
        # User clicked on parcat bar
        elif trigger == "parcat":
            #print("PARCAT POINTS CLICKED:", [point['pointNumber'] for point in parcat_clicked['points']])  # TEST
            # For a variety of reasons, getting the color of whatever you clicked in the PCP is very hard.
            # That's why we instead use the unique "brushing color" below, which is exclusive to the PCP to highlight points.
            brushing_color = '#FFFFFF'
            clicked_points = [point['pointNumber'] for point in parcat_clicked['points']]  # This is the indices of the points which have been clicked
            # Problem: the numbers here are the indices of *only the selected points, renumbered from 0*. That's why we have to do this roundabout shit:
            selected_UIDs = filtered_data.loc[filtered_data['selected'] == 1, 'UID'].reset_index()  # Get UIDs of selected points & renumber them
            selected_UIDs = selected_UIDs.loc[selected_UIDs.index.isin(clicked_points), 'UID'].tolist()  # Keep only the ones that were clicked in the PCP
            filtered_data['highlighted'] = filtered_data['UID'].apply(lambda uid: brushing_color if (uid in selected_UIDs) else GRAYED_OUT_COLOR)  # Color only clicked points (determined by UID)
        
        # User clicked on clear selection button: clear both map selection and highlights
        elif trigger == "clear_selection_button":
            filtered_data['selected'] = [1]*len(filtered_data)
            filtered_data['highlighted'] = [GRAYED_OUT_COLOR]*len(filtered_data)

        # User clicked something else: clear highlights
        else:
            filtered_data['highlighted'] = [GRAYED_OUT_COLOR]*len(filtered_data)

        # Return data with correct filtering/highlighting
        return filtered_data.to_dict()  # Note: data is stored as JSON, so it has to be converted to JSON and then converted back when reading it in another component

    return dcc.Store(id=id)

# Auxiliary function for grouping low-frequency categories into "other"
def filter_low_freq(data: DataFrame, feature: str) -> DataFrame:
    '''
    Groups low-frequency values for the given feature into a category "other" to reduce data clutter.
    In the current implementation, a value is deemed "low-frequency" if it makes up less than 1% of the total values for that attribute among the selected points.
    Note: only some features are deemed "groupable", e.g. Victim.gender is not. See the list groupable_features above.
    '''
    if(feature in GROUPABLE_FEATURES):  # Only group data that makes sense to group (so not e.g. gender)
        one_percent = len(data[feature].loc[data['selected'] == 1])/100  # 1% of the amount of selected points
        value_freq = data[feature].loc[data['selected'] == 1].value_counts()  # Find how many times each unique value for this feature occurs in the selected points
        low_freq_values = value_freq[value_freq < one_percent]  # Find which values occur infrequently (in this case, which values account for less than 1% of the total)
        if(len(low_freq_values) > 0):
            data[feature] = data[feature].astype("string")    # If there are low frequency values, cast the column to string type and...
            data[feature] = data[feature].apply(lambda value: "~Other" if value in low_freq_values else value) # ...replace low frequency values with "other"
    return data