from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from pandas import DataFrame

app = Dash(__name__)

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


def render(app: Dash, id: str, data: DataFrame)-> dcc.Graph:
    @app.callback(
        Output("bar_plot", "figure"),
        [Input("map", "selectedData"),
         Input("barplot_dropdown", "value")]
    )
    def update_figure(selected_data, feature):
        select_all_points = False

        if feature == []:
            return px.bar(None)
        else:
            if selected_data is None:
                select_all_points = True


        ids = []
        if not select_all_points:
            for point in selected_data["points"]:
                ids.append(point["customdata"][0])
        filtered_data = data.loc[data["UID"].isin(ids)] if select_all_points == False else data

        if len(filtered_data) == 0:
            return px.bar(None)

        vals_and_freqs = valAndFreqs(filtered_data[feature])
        values = vals_and_freqs[0]
        frequencies = vals_and_freqs[1]

        for value in data[feature].drop_duplicates().tolist():
            if value not in values:
                values.append(value)
                frequencies.append(0)

        fig = px.bar(filtered_data, x= values, y = frequencies)
        return fig
    return dcc.Graph(id = id)
