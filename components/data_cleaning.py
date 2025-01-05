import pandas as pd
from pandas import DataFrame

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