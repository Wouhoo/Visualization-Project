import plotly.express as px
from dash import Dash, dcc, ctx
from pandas import DataFrame
from dash.dependencies import Input, Output, State
from .data_cleaning import MONTH_ORDER, GRAYED_OUT_COLOR

#Predefined colors for specific attributes
PREDEFINED_COLORS = {"Provoked/unprovoked": ["#00c49d","#c42e00","#dbdbdb"],
                     "Victim.gender":["#de05ff","#058aff","#dbdbdb"]}
#Plotly default color sequence (in order of normal selection).
PLOTLY_DEFAULT_COLORS = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692',
                        '#B6E880','#FF97FF','#FECB52']
GLOBAL_CUSTOM_DATA = ["UID", "selected", "Incident.month", "Incident.year", "Victim.injury", "State", "Site.category", "Provoked/unprovoked",
                      "Victim.activity", "Injury.severity", "Victim.gender", "Data.source", "Shark.name", "Victim.age"]
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
        Input("primary_color_dropdown", "value"),
        Input("secondary_color_dropdown", "value"),
        prevent_initial_call=True
    )
    def change_display(data, primary_color_feature, secondary_color_feature):
        # Read data
        if data is None:
            data = all_data
        data = DataFrame(data)  # Convert stored JSON to dataframe

        # Find highest-priority color feature
        if not(secondary_color_feature is None or secondary_color_feature == []):
            color_feature = secondary_color_feature
        else:
            color_feature = primary_color_feature

        # If a bar is clicked in the barplot or PCP, change color based on the highlighted bar
        if any([color != GRAYED_OUT_COLOR for color in data['highlighted']]):
            data = data.sort_values('highlighted', ascending=False)  # Sort so highlighted points are drawn on top
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name", width=1000, height=700,
                                 zoom=3,
                                 custom_data=GLOBAL_CUSTOM_DATA)
            fig.update_traces(marker_color=data['highlighted'])

        # Otherwise, change color based on primary color attribute if one is selected
        elif not(color_feature is None or color_feature == []):
            # Sort months according to special ordering, otherwise sort alphabetically
            if(color_feature == 'Incident.month'):
                data = data.sort_values(color_feature, key=lambda x: x.map(MONTH_ORDER))
            else:
                data = data.sort_values(color_feature)
            # Make figure
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                        zoom=3,
                        custom_data=GLOBAL_CUSTOM_DATA,
                        color=color_feature, labels={color_feature: color_feature.replace(".", " ")})

        # If no primary color attribute is selected, grey out all points
        else:
            colorSeq = [GRAYED_OUT_COLOR]
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                                 zoom=3,
                                 custom_data=GLOBAL_CUSTOM_DATA,
                                 color=None, color_discrete_sequence=colorSeq)
        
        # Set map to dark mode, make unselected points transparent & return figure
        fig.update_layout(map_style="dark")  # Dark, Light, Satelite
        fig.update_traces(marker_opacity=data['selected'])
        # Unsuccesful tests
        #fig.for_each_trace("TRACE IDs: ", lambda trace: print(trace.name, ": ", trace.ids))  # Always None fsr...
        #fig.update_traces(selectedpoints=data.loc[data['selected']==1].index)
        #fig.update_traces(selectedpoints=data.loc[data['selected']==1, 'UID'])

        #Set Hoverable template for all points. Points that are NOT selected (aka not visible) have no hover info.
        fig.update_traces(
            hoverinfo="text",
            hovertemplate=[
                None if hoverable == 0 else _get_hover_template(color_feature)
                for hoverable in data['selected']
            ]
        )
        return fig

    return _render_default(all_data, id)

def _get_hover_template(color_feature) -> str:
    if(color_feature in GLOBAL_CUSTOM_DATA):
        titleIndex = GLOBAL_CUSTOM_DATA.index(color_feature)
    else:
        titleIndex = 0

    return "<b>Selected: %{customdata["+str(titleIndex)+"]}</b><br>" +\
            "%{customdata["+str(GLOBAL_CUSTOM_DATA.index("Provoked/unprovoked"))+"]} " +\
            "attack occured in %{customdata["+str(GLOBAL_CUSTOM_DATA.index("Incident.month"))+"]}" +\
            " %{customdata["+str(GLOBAL_CUSTOM_DATA.index("Incident.year"))+"]}" +\
            " at a %{customdata["+str(GLOBAL_CUSTOM_DATA.index("Site.category"))+"]} site" +\
            " in %{customdata["+str(GLOBAL_CUSTOM_DATA.index("State"))+"]}.<br>" +\
        "Victim (%{customdata["+str(GLOBAL_CUSTOM_DATA.index("Victim.age"))+"]}%{customdata["+str(GLOBAL_CUSTOM_DATA.index("Victim.gender"))+"]})" +\
        " was %{customdata["+str(GLOBAL_CUSTOM_DATA.index("Victim.activity"))+"]} at time of incident.<br>" +\
        "Victim sustained %{customdata["+str(GLOBAL_CUSTOM_DATA.index("Injury.severity"))+"]}" +\
        " at the hands of a %{customdata["+str(GLOBAL_CUSTOM_DATA.index("Shark.name"))+"]}.<br>" +\
        "Source: %{customdata["+str(GLOBAL_CUSTOM_DATA.index("Data.source"))+"]}"

#Renders a default map with all points included. Nothing special
def _render_default(data: DataFrame, id: str) -> dcc.Graph:
    fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name", width=1000, height=700, zoom=3,
                         custom_data=["UID"],
                         hover_data=["UID","Present.at.time.of.bite", "Shark.behaviour","Victim.injury","Injury.location","Diversionary.action.taken"],
                         color=None)
    fig.update_layout(map=dict(style="dark"))  # Dark, Light, Satelite
    return dcc.Graph(figure=fig, id=id)