from dash import Dash, html, dcc, Input, Output
import pandas as pd
from pandas import DataFrame
import plotly.express as px

def render(app: Dash, data: DataFrame, id: str) -> html.Div:

    years = data["Incident.year"]#.dropna().astype(int)  # Assuming "Incident.year" is the column
    min_year, max_year = years.min(), years.max()

    # Define the callback to update the title based on slider value
    @app.callback(
        Output('timetitle', 'children'), # Output the updated title to the H6 element
        Input('slider', 'value')         # Input: the slider value
    )
    def update_title(input_year):
    # Get the start and end year from the slider value
        start_year, end_year = input_year
        return f"Incidents from {start_year} until {end_year}"
    
    @app.callback(
        Output('timehist', 'figure'), # Output the updated histogram above the slider
        Input('slider', 'value')      # Input: the slider value
    )
    def update_graph(input_year):
        filtered_data = data[(data['Incident.year'] >= input_year[0]) & (data['Incident.year'] <= input_year[1])]
        hist = px.histogram(filtered_data, x='Incident.year', range_x=[min_year, max_year])
        hist.update_traces(xbins_size=1)
        hist.update_xaxes(visible=False, showticklabels=False)
        hist.update_layout(  
            yaxis_title="Incidents",
            yaxis=dict(title_standoff=5)
        )
        return hist

    return html.Div(
            children = [
                html.H6(id = "timetitle", children = f"Incidents from {min_year} until {max_year}", className="timetitle"),
                dcc.Graph(id = "timehist", className="timehist"),
                dcc.RangeSlider(
                    min_year,
                    max_year,
                    step=1,
                    value=[ min_year,  max_year ],
                    marks={str(year): str(year) for year in range(max_year, min_year, -15)},
                    # if we want the slider to go about rounded years:
                    # marks={str(year): str(year) for year in range(df['Incident.year'].max() + 1 ,df['Incident.year'].min(), -15)},
                    id= "slider",
                    className="timeslider"
                )
            ]
        )
        
        



