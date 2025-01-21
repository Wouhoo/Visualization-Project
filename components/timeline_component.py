from dash import Dash, html, dcc, Input, Output
import pandas as pd
from pandas import DataFrame
import plotly.express as px
import plotly.graph_objects as go

def render(app: Dash, data: DataFrame, id: str) -> html.Div:

    years = data["Incident.year"]
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
        # Filtered dynamic data
        filtered_data = data[(data['Incident.year'] >= input_year[0]) & (data['Incident.year'] <= input_year[1])]

        # Dynamic histogram for filtered data
        dynamic_trace = go.Histogram(
            x=filtered_data['Incident.year'],
            xbins=dict(size=1), 
            marker_color = "blue",
            opacity=0.7, 
            name="",
            hovertemplate="<b>Selected years:</b><br>Year: %{x}<br>Incidents: %{y}<br>%{fullData.name}" 
        )

        # Static plot trace (remains the same)
        static_trace = go.Histogram(
            x=data['Incident.year'],
            xbins=dict(size=1),
            marker_color='grey',
            opacity=0.4, 
            name="",
            hovertemplate="<b>Unselected years:</b><br>Year: %{x}<br>Incidents: %{y}<br>%{fullData.name}" 
        )

        # Combine both traces in a single figure
        fig = go.Figure(data=[static_trace, dynamic_trace])
        fig.update_layout(
            yaxis_title="Incidents",
            yaxis=dict(title_standoff=5),
            barmode='overlay',  
            showlegend=False, 
        )
        fig.update_xaxes(visible=False, showticklabels=False)

        fig.update_layout(
            paper_bgcolor="#2C353C",
            font=dict(color='#bcbcbc'),  # Text color
            margin=dict(l=0, r=20, t=50, b=50)  # Adjust left (l), right (r), top (t), bottom (b) margins
        )

        return fig
        

    return html.Div(
            children = [
                html.H6(id = "timetitle", children = f"Incidents from {min_year} until {max_year}", className="timetitle", style={'textAlign': 'center'}),
                dcc.Graph(id = "timehist", className="timehist"),
                dcc.RangeSlider(
                    min_year,
                    max_year,
                    step=1,
                    value=[ min_year,  max_year ],
                    
                    # marks = {i: '{}'.format(i) for i in range(min_year,max_year, 10), style = {'writingMode': 'vertical-rl', 'textOrientation': 'mixed'}},
    
                    marks={
                        str(year): {'label': str(year), 'style' : {'transform': 'rotate(45deg)', 'whiteSpace': 'nowrap'}}
                            for year in range(max_year, min_year, -10)},
                    # if we want the slider to go about rounded years:
                    # marks={str(year): str(year) for year in range(max_year + 1 ,min_year, -20)},
                    id= "slider",
                    className="timeslider"
                )
            ]
        )