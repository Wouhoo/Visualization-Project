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
        State("data_store", "data"), # Wouldn't work as an Input fsr. We'll see if that causes issues.
        Input("map_dropdown", "value"),
        Input("stacked_bar", "clickData"),
        State("stackedbar_dropdown_x", "value"),
        State("stackedbar_dropdown_color", "value"),
        prevent_initial_call=True
    )
    def change_display(data, color_dropdown_value, bar_clicked, bar_x_feature, bar_color_feature):
        trigger = ctx.triggered_id

        # Read data
        if data is None:
            data = all_data
        data = DataFrame(data)  # Convert stored JSON to dataframe

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
        
        #On clicking the stacked bar plot, highlight all points corresponding to the clicked bar
        elif trigger == "stacked_bar":
            colorIndex = bar_clicked["points"][0]["curveNumber"]  # Index of bar (default) or trace (stacked) in bar chart
            selectedColor = PLOTLY_DEFAULT_COLORS[colorIndex % len(PLOTLY_DEFAULT_COLORS)]  # Actual selected color
            #selected_x_value = bar_clicked["points"][0]["x"] # x feature value corresponding to the selected (sub-)bar

            # Create map with highlighted data
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                                 zoom=3,
                                 #custom_data=["UID"],
                                 hover_data=["Present.at.time.of.bite", "Shark.behaviour","Injury.location","Diversionary.action.taken"],
                                 color=data["highlighted"], color_discrete_map={True: selectedColor, False: "gray"})

            # Restore selection
            print(data.loc[data['selected'] == True])  # TEST
            print([int(id) for id in data.loc[data['selected'] == True].index])  # TEST
            fig.update_traces(selectedpoints = [int(id) for id in data.loc[data['selected'] == True].index])
            fig.update_traces(unselected_marker_opacity=0)  # TEST: make unselected points invisible
            #fig.update_traces(selectedpoints=[0,34,60,78,91]) # This works, so the above should also work in principle
            # For some reason though, it seems to change the selection based on what bar you clicked?

            fig.update_layout(map=dict(style="dark"))
            fig.update(layout_showlegend=False)
            return fig

        else:
            return _render_default(data, id)
        
    return _render_default(all_data, id)

#Renders a default map with all points included. Nothing special
def _render_default(data: DataFrame, id: str) -> dcc.Graph:
    fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name", width=1000, height=700, zoom=3,
                         custom_data=["UID"],
                         hover_data=["Victim.activity", "Victim.gender", "Site.category", "Victim.injury"],
                         color=None)
    fig.update_layout(map=dict(style="dark"))  # Dark, Light, Satelite
    return dcc.Graph(figure=fig, id=id)