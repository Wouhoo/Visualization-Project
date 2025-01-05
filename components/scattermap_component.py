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
def render(app: Dash, data: DataFrame, id: str) -> dcc.Graph:

    @app.callback(
        Output("map", "figure"),
        Input("map_dropdown", "value"),
        Input("bar_plot", "clickData"),
        State("barplot_dropdown","value"),
        prevent_initial_call=True
    )
    def change_display(color_dropdown_value, bar_clicked, bar_dropdown_value):
        trigger = ctx.triggered_id
        #On map dropdown change, change the colors of all points to match the chosen category by the color dropdown.
        if trigger == "map_dropdown":
            color = None if color_dropdown_value == [] else color_dropdown_value
            colorSeq = None if color_dropdown_value == [] or color_dropdown_value not in PREDEFINED_COLORS.keys() else PREDEFINED_COLORS[color_dropdown_value]
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                                 zoom=3,
                                 custom_data=["UID"],
                                 hover_data=["Present.at.time.of.bite", "Shark.behaviour","Injury.location","Diversionary.action.taken"],
                                 color=color, color_discrete_sequence=colorSeq)

            fig.update_layout(map=dict(style="dark"))  # Dark, Light, Satelite
            return fig
        #On clicking the bar plot, highlight all points with the same value as the clicked bar, on the column selected by
        #the barplot attribute dropdwon.
        elif trigger == "bar_plot":
            colorIndex = bar_clicked["points"][0]["curveNumber"]
            selectedColor = PLOTLY_DEFAULT_COLORS[colorIndex % len(PLOTLY_DEFAULT_COLORS)]
            columnValue = bar_clicked["points"][0]["x"]
            columnName = bar_dropdown_value
            data["highlight"] = data[columnName].apply(lambda x : "1" if x == columnValue else "0")

            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                                 zoom=3,
                                 custom_data=["UID"],
                                 hover_data=["Present.at.time.of.bite", "Shark.behaviour","Injury.location","Diversionary.action.taken"],
                                 color=data["highlight"], color_discrete_map={"1": selectedColor, "0": "gray"})

            fig.update_layout(map=dict(style="dark"))
            fig.update(layout_showlegend=False)
            return fig
        else:
            return _render_default(data, id)
    return _render_default(data, id)

#Renders a default map with all points included. Nothing special
def _render_default(data: DataFrame, id: str) -> dcc.Graph:
    fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name", width=1000, height=700, zoom=3,
                         custom_data=["UID"],
                         hover_data=["Victim.activity", "Victim.gender", "Site.category", "Victim.injury"],
                         color=None)
    fig.update_layout(map=dict(style="dark"))  # Dark, Light, Satelite
    return dcc.Graph(figure=fig, id=id)