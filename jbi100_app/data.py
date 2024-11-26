import pandas as pd

# DO PREPROCESSING HERE (or in an external app and read in the modified file here)
def get_data():
    # Read data
    df = pd.read_csv('Shark_data.csv', sep=';') # If you modify the file, make sure you save it in utf-8 encoding
    # TODO: Replace ^ with cleaned data
    df = df.dropna(subset='UIN')
    df['Latitude'] = df['Latitude'].str.replace(',','.')
    df['Longitude'] = df['Longitude'].str.replace(',','.')
    df['Injury_color'] = injury_color(df['Victim.injury']) # As an example, use injury as color attribute

    # TODO: Do preprocessing

    return df

def injury_color(injury_col):
    # Map Victim.injury to a color dictated by the dict below
    color_dict = {'uninjured' : 'yellow', 'injured' : 'orange', 'fatal' : 'red', 'unknown' : 'gray'}
    return [color_dict[entry.lower()] for entry in injury_col]

# DEBUG
#print(get_data())