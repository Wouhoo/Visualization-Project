from dash import Dash, html, dcc, Input, Output, ctx
import plotly.express as px
import pandas as pd
from pandas import DataFrame

app = Dash(__name__)

#Plotly default color sequence (in order of normal selection).
PLOTLY_DEFAULT_COLORS = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692',
                        '#B6E880','#FF97FF','#FECB52']

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
         Input("barplot_dropdown", "value"),
         Input("bar_plot", "clickData")]
    )
    def update_figure(selected_data, feature, bar_clicked):
        trigger = ctx.triggered_id

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


        #Sorting values (and thus frequencies) for better visualization
        plotted_data = {j:i for i,j in zip(values,frequencies)}
        sorted_plotted_data = {k: v for k, v in sorted(plotted_data.items(), key=lambda item: item[1])}
        values = list(sorted_plotted_data.values())
        frequencies = list(sorted_plotted_data.keys())

        selected_color = [str(i) for i in values]
        selected_sequence = PLOTLY_DEFAULT_COLORS

        #If the trigger is clicking on a bar, change colors to focus on that bar.
        if trigger == "bar_plot":
            colorIndex = bar_clicked["points"][0]["curveNumber"]
            selected_sequence = ["#bababa"]*len(selected_color)
            selected_sequence[colorIndex] = PLOTLY_DEFAULT_COLORS[colorIndex % len(PLOTLY_DEFAULT_COLORS)]

        fig = px.bar(filtered_data, x= values, y = frequencies, color=selected_color,color_discrete_sequence=selected_sequence)
        return fig
    return dcc.Graph(id = id)
