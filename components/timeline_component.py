from dash import Dash, html, dcc, Input, Output
import pandas as pd
from pandas import DataFrame
import plotly.express as px
import plotly.graph_objects as go

def valAndFreqs(dataList):
    val = []  
    for item in dataList:  
        if item not in val:  
            val.append(item)  
    
    freq = [0] * len(val)
    for x in range(len(freq)):
        for item in dataList:
            if item == val[x]:
                freq[x]+=1
    valsAndfreqs = (val,freq)
    return valsAndfreqs

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
        return f"Incidents from years: {start_year} until {end_year}"
    
    @app.callback(
        Output('timehist', 'figure'), # Output the updated histogram above the slider
        Input('slider', 'value')      # Input: the slider value
    )

    def update_graph(input_year):
        # Filtered dynamic data
        filtered_data = data[(data['Incident.year'] >= input_year[0]) & (data['Incident.year'] <= input_year[1])]

        dyn_years, dyn_val = valAndFreqs(filtered_data["Incident.year"])
        stat_years, stat_val = valAndFreqs(years)

        dyn_years, dyn_val = valAndFreqs(filtered_data["Incident.year"])
        stat_years, stat_val = valAndFreqs(years)

        dynamic_area = go.Scatter(
            x=dyn_years,
            y=dyn_val,
            fill='tozeroy',  # Fill to the x-axis
            fillcolor='rgba(0, 0, 255, 0.7)',  # Blue with some opacity
            mode='lines',
            line=dict(color='blue'),
            name="",
            hovertemplate="<b>Selected years:</b><br>Year: %{x}<br>Incidents: %{y}<br>%{fullData.name}" 
        )

        # Static area plot for full data (use grey)
        static_area = go.Scatter(
            x=stat_years,
            y=stat_val,
            fill='tozeroy',  # Fill to the x-axis
            fillcolor='rgba(128, 128, 128, 0.4)',  # Grey with opacity
            mode='lines',
            line=dict(color='grey'),
            name="",
            hovertemplate="<b>Unselected years:</b><br>Year: %{x}<br>Incidents: %{y}<br>%{fullData.name}" 
        )

        # Combine both traces in a single figure
        fig = go.Figure(data=[static_area, dynamic_area])
        fig.update_layout(
            yaxis_title="Incidents",
            yaxis=dict(title_standoff=5),
            barmode='overlay',  
            xaxis_title=None, 
            xaxis=dict(showticklabels=False),
            showlegend=False, 
            paper_bgcolor="#2C353C",
            font=dict(color='#bcbcbc'),
            margin=dict(l=30,r=45,t=10,b=20),
            height = 200
        )
        return fig
        

    return html.Div(
            children = [
                html.H5(id = "timetitle", children = f"Incidents from years: {min_year} until {max_year}", className="timetitle", style={'textAlign': 'center'}),
                dcc.Graph(id = "timehist", className="timehist"),   
                html.Div(
                dcc.RangeSlider(
                    min=min_year,
                    max=max_year,
                    step=1,
                    value=[min_year, max_year],
                    marks={
                        str(year): {'label': str(year), 'style': {'transform': 'rotate(45deg)', 'whiteSpace': 'nowrap'}}
                        for year in range(max_year, min_year, -10)
                    },
                    id="slider",
                    className="timeslider"
                ),
                style={
                    'width': '93%',
                    'margin-left': 'auto',  # Center the slider horizontally
                    'margin-right': 'auto',  # Center the slider horizontally
                }
            )
            ],
        style={
            'backgroundColor': '#2C353C',  # Same background color as the plot
            'padding': '10px',
            'margin-top': '15px',
        }
        )