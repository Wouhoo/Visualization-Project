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

GROUPABLE_FEATURES = ["Incident.year", "Site.category", "No.sharks", "Victim.activity", "Present.at.time.of.bite", 
                      "Injury.location", "Injury.severity", "Victim.age", "Diversionary.action.taken", 
                      "Data.source", "Shark.name"]  # Columns where low-frequency data should be grouped into an "other" category

UNSELECTED_OPACITY = 0.05

app = Dash(__name__)

def store(app: Dash, id: str, all_data: DataFrame)-> dcc.Store:
    @app.callback(
        Output("data_store", "data"),
        [Input("map", "selectedData"),
         Input("slider", "value"),
         Input("stacked_bar", "clickData"),
         Input("parcat", "clickData"),
         State("primary_color_dropdown", "value"),
         State("secondary_color_dropdown", "value")]
    )
    def filter_dataframe(map_selected_data, input_year, bar_clicked, parcat_clicked, primary_color_feature, secondary_color_feature):
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
            selected_ids = [point['pointNumber'] for point in map_selected_data['points']]  # Row numbers of selected points
            filtered_data['selected'] = filtered_data['UID'].apply(lambda id: 1 if id in selected_ids else UNSELECTED_OPACITY) 
            # Old version below; the new version (line above) gets rid of a warning from pandas :)
            #filtered_data['selected'] = [UNSELECTED_OPACITY]*len(filtered_data)
            #filtered_data['selected'].loc[selected_ids] = 1  # Now set selected to 1 only for selected points

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
            if(secondary_color_feature == [] or secondary_color_feature == '-'):
                filtered_data["highlighted"] = filtered_data[primary_color_feature].apply(lambda x : selected_color if x == selected_x_value else "#bababa")  # Select incidents to highlight

            # Stacked bar chart
            else:
                color_names = filtered_data[secondary_color_feature].value_counts().index  # Unique values for barplot color feature
                selected_color_value = color_names[color_index]  # Color feature value corresponding to the selected sub-bar
                filtered_data["highlighted"] = filtered_data.apply(lambda row : selected_color if (row[primary_color_feature] == selected_x_value and row[secondary_color_feature] == selected_color_value) else "#bababa", axis=1)
        
        # User clicked on parcat bar
        elif trigger == "parcat":
            #print("PARCAT BAR CLICKED:", parcat_clicked)  # TEST
            #color_index = parcat_clicked["points"][0]["curveNumber"]  # Index of clicked barcat bar
            #selected_color = PLOTLY_DEFAULT_COLORS[color_index % len(PLOTLY_DEFAULT_COLORS)]  # Actual selected color
            # NOTE: This selected color is currently *always blue*, since color_index is always 0 (all parts of the parcat plot have curveNumber 0)
            # I can think of *some* ways in which we could preserve the color, but they are pretty roundabout.
            # Instead, we could just always use one color, like below:
            selected_color = '#FFFFFF'  # Solid white - currently hard to see in the PCP, but this will hopefully change when we switch to dark mode
            clicked_points = [point['pointNumber'] for point in parcat_clicked['points']]  # Parcat gives us the dataframe IDs of all clicked points
            print(filtered_data.columns)
            filtered_data['highlighted'] = filtered_data.apply(lambda row: selected_color if (row['UID'] in clicked_points and row['selected'] == 1) else '#bababa', axis=1)  # Color only clicked points
        # User clicked something else
        else:
            filtered_data['highlighted'] = ["#bababa"]*len(filtered_data)  # In this case, grey out all data

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
            data[feature].loc[data[feature].isin(low_freq_values.index.tolist())] = "other"  # ...replace low frequency values with "other"
    return data