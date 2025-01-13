import plotly.express as px
from dash import Dash, dcc, ctx
from pandas import DataFrame

from dash.dependencies import Input, Output, State

#Predefined colors for specific attributes
PREDEFINED_COLORS = {"Provoked/unprovoked": ["#00c49d","#c42e00","#dbdbdb"],
                     "Victim.gender":["#de05ff","#058aff","#dbdbdb"]}
#Plotly default color sequence (in order of normal selection).
PLOTLY_DEFAULT_COLORS = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692',
                        '#B6E880','#FF97FF','#FECB52']

"""
Creates a new scatter map instance component.
Dash app - The application (used for callbacks)
DataFrame data - Our pandas dataset
String id - A unique ID not used by any other component in our app

@Returns: A Dcc.Graph of a scatter map
"""
def render(app: Dash, all_data: DataFrame, id: str) -> dcc.Graph:
    @app.callback(
        Output("map", "figure"),
        Input("data_store", "data"),
        Input("map_dropdown", "value"),
        State("stackedbar_dropdown_x", "value"),
        State("stackedbar_dropdown_color", "value"),
        prevent_initial_call=True
    )
    def change_display(data, color_dropdown_value, bar_x_feature, bar_color_feature):
        trigger = ctx.triggered_id
        # Read data
        if data is None:
            data = all_data
        data = DataFrame(data)  # Convert stored JSON to dataframe

        # On map dropdown change, change the colors of all points to match the chosen category by the color dropdown.
        if trigger == "map_dropdown":
            color = None if color_dropdown_value == [] else color_dropdown_value
            colorSeq = None if color_dropdown_value == [] or color_dropdown_value not in PREDEFINED_COLORS.keys() else PREDEFINED_COLORS[color_dropdown_value]
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                                 zoom=3,
                                 custom_data=["UID"],
                                 hover_data=["UID","Present.at.time.of.bite", "Shark.behaviour","Victim.injury","Injury.location","Diversionary.action.taken"],
                                 color=color, color_discrete_sequence=colorSeq)

            fig.update_layout(map=dict(style="dark"))  # Dark, Light, Satelite
            return fig
        # If a bar is clicked in the barplot, change color based on the highlighted bar and opacity based on map area selection
        else:
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name", width=1000, height=700,
                                 zoom=3,
                                 custom_data=["UID"],
                                 hover_data=["Victim.activity", "Victim.gender", "Site.category", "Victim.injury"]
                                 )
            fig.update_layout(map=dict(style="dark"))  # Dark, Light, Satelite
            fig.update_traces(marker=dict(color=data['highlighted'], opacity=data['selected']))
            return fig

        
    return _render_default(all_data, id)

#Renders a default map with all points included. Nothing special
def _render_default(data: DataFrame, id: str) -> dcc.Graph:
    fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name", width=1000, height=700, zoom=3,
                         custom_data=["UID"],
                         hover_data=["UID","Present.at.time.of.bite", "Shark.behaviour","Victim.injury","Injury.location","Diversionary.action.taken"],
                         color=None)
    fig.update_layout(map=dict(style="dark"))  # Dark, Light, Satelite
    return dcc.Graph(figure=fig, id=id)