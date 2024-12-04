import plotly.express as px
from dash import Dash, html, dcc
from pandas import DataFrame

from dash.dependencies import Input, Output, State

#Predefined colors for specific attributes
PREDEFINED_COLORS = {"Provoked/unprovoked": ["#00c49d","#c42e00","#dbdbdb"],
                     "Victim.gender":["#de05ff","#058aff","#dbdbdb"]}

"""
Creates a new scatter map instance component.
Dash app - The application (used for callbacks)
DataFrame data - Our pandas dataset
String id - A unique ID not used by any other component in our app

@Returns: A Dcc.Graph of a scatter map
"""
def render(app: Dash, data: DataFrame, id: str) -> dcc.Graph:

    #When the value of color_dropdown changes, update the map with appropriate colors.
    @app.callback(
        Output("map", "figure"),
        Input("color_dropdown", "value")
    )
    def display_click_data(value):
        color = None if value == [] else value
        colorSeq = None if value == [] or value not in PREDEFINED_COLORS.keys() else PREDEFINED_COLORS[value]
        #width=1600, height=700,
        fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                             zoom=3,
                             custom_data=["UID"],
                             hover_data=["Present.at.time.of.bite", "Shark.behaviour","Injury.location","Diversionary.action.taken"],
                             color=color, color_discrete_sequence=colorSeq)

        fig.update_layout(map=dict(style="dark"))  # Dark, Light, Satelite
        return fig
    #Default instance when application initializes.
    fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name", width=1600, height=700, zoom=3,
                         custom_data=["UID"],
                         hover_data=["Victim.activity","Victim.gender","Site.category","Victim.injury"],
                         color=None)

    fig.update_layout(map=dict(style="dark")) #Dark, Light, Satelite
    return dcc.Graph(figure=fig, id=id)

#color="Victim.injury",
#  category_orders={"fatal":1,"injured":2,"uninjured":3,"unknown":4},
#  color_discrete_sequence=['red',"yellow","green","gray"]