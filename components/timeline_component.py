from dash import Dash, html, dcc, Input, Output
import pandas as pd
from pandas import DataFrame


def render(app: Dash, data: DataFrame, id: str) -> html.Div:

    years = data["Incident.year"].dropna().astype(int)  # Assuming "Incident.year" is the column
    min_year, max_year = years.min(), years.max()

    # Define the callback to update the title based on slider value
    @app.callback(
        Output('title', 'children'),  # Output the updated title to the H6 element
        Input('slider', 'value')      # Input: the slider value
    )

    def update_title(slider_value):
    # Get the start and end year from the slider value
        start_year, end_year = slider_value
        return f"Incidents from {start_year} until {end_year}"

    return html.Div(
            children = [
                html.H6(id = "title", children = f"Incidents from {min_year} until {max_year}"),
                dcc.RangeSlider(
                    min_year,
                    max_year,
                    step=1,
                    value=[ min_year,  max_year ],
                    marks={str(year): str(year) for year in range( max_year, min_year, -15)},
                    # if we want the slider to go about rounded years:
                    # marks={str(year): str(year) for year in range(df['Incident.year'].max() + 1 ,df['Incident.year'].min(), -15)},
                    id= "slider"
                )
            ]
        )



