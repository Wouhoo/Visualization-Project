import pandas as pd
from pandas import DataFrame
from dash import Dash, Input, Output, dcc

"""
In the new "centralized dataframe" architecture, this component is responsible for
storing and modifying the central dataframe.
It takes selections from all other components as inputs and returns the dataframe as output,
which is then used as input by all other components.
"""

app = Dash(__name__)

def store(app: Dash, id: str, all_data: DataFrame)-> dcc.Store:
    @app.callback(
        Output("data_store", "data"),
        [Input("map", "selectedData")]
    )
    def filter_dataframe(map_selected_data):
        filtered_data = all_data
        # All data is initially selected & highlighted.
        filtered_data['highlighted'] = [1]*len(all_data)

        # Filter based on map selection
        if(map_selected_data is None):
            filtered_data['selected'] = [1]*len(all_data)  # In this case all data is selected
        else:
            selected_ids = [point['pointNumber'] for point in map_selected_data['points']]  # Row numbers of selected points
            filtered_data['selected'] = [0]*len(all_data)  
            filtered_data['selected'].loc[selected_ids] = 1  # Now set selected to 1 only for selected points
            print(filtered_data.loc[filtered_data['selected'] == 1]) # TEST
            
        return filtered_data.to_dict()  # Note: data is stored as JSON, so it has to be converted to JSON
                               # and then converted back when reading it in another component

    return dcc.Store(id=id)









groupable_features = ["Incident.year", "Site.category", "No.sharks", "Victim.activity", "Present.at.time.of.bite", 
                      "Shark.behavior", "Injury.location", "Injury.severity", "Victim.age", "Diversionary.action.taken", 
                      "Data.source", "Shark.name"]  # Columns where low-frequency data should be grouped into an "other" category

# Auxiliary function for grouping low-frequency categories into "other"
def filter_low_freq(data: DataFrame, feature: str) -> DataFrame:
    '''
    Groups low-frequency values for the given feature into a category "other" to reduce data clutter.
    In the current implementation, a value is deemed "low-frequency" if it makes up less than 1% of the total values.
    Note: only some features are deemed "groupable", e.g. Victim.gender is not. See the list groupable_features above.
    '''
    if(feature in groupable_features):  # Only group data that makes sense to group (so not e.g. gender)
        one_percent = len(data[feature])/100
        value_freq = data[feature].value_counts()  # Find how many times each unique value for this feature occurs
        #print(value_freq) # TEST
        low_freq_values = value_freq[value_freq < one_percent]  # Find which values occur infrequently (in this case, which values account for less than 1% of the total)
        #print(low_freq_values) # TEST
        if(len(low_freq_values) > 0):
            data[feature] = data[feature].astype("string")    # If there are low frequency values, cast the column to string type and...
            data[feature].loc[data[feature].isin(low_freq_values.index.tolist())] = "other"  # ...replace low frequency values with "other"
    return data