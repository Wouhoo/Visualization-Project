import plotly.express as px
from dash import Dash, dcc, ctx
from pandas import DataFrame
from dash.dependencies import Input, Output, State
from .data_cleaning import MONTH_ORDER, GRAYED_OUT_COLOR, UNSELECTED_OPACITY

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

### A WORD OF WARNING: SCATTERMAP TRACES ###
# If *no* color attribute is selected, all points belong to the same trace.
# In this case, the update_traces method can be applied directly to modify the one trace;
# for example, fig.update_traces(marker_opacity=data['selected']) reduces the opacity of unselected points.
# If a color attribute *is* selected, there are several traces (one for each unique value of the attribute), with the points divided among them.
# For example, if "State" is selected as the color attribute, there are traces for "NSW", "NT", "QLD", etc., each with their own color and array of points.
# In this case, update_traces *updates all traces at once*, and *should not be used to update individual traces*.
# DASH DOES NOT THROW AN ERROR when you e.g. try to set marker_opacity with an array longer than the array of points in that trace;
# this is why it took us so f*cking long to figure out what was up.
# Instead, use for_each_trace with a different update depending on the trace's name. For example, to reduce the opacity of unselected points:
# fig.for_each_trace(lambda trace: trace.update(marker_opacity = data.loc[data[color_feature] == trace.name, 'selected']))

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
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                                 zoom=3,
                                 custom_data=GLOBAL_CUSTOM_DATA)
            fig.update_traces(marker_color=data['highlighted'])
            fig.update_traces(marker_opacity=data['selected'])  # Reduce opacity of unselected points
            fig.update_traces(hoverinfo="text", 
                              hovertemplate=[None if hoverable == 0 else _get_hover_template(color_feature) for hoverable in data['selected']]) # Set Hoverable template for all points. Points that are NOT selected (aka not visible) have no hover info.

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
            fig.for_each_trace(lambda trace: trace.update(marker_opacity = data.loc[data[color_feature] == trace.name, 'selected']))  # Reduce opacity of unselected points
            fig.for_each_trace(lambda trace: trace.update(hoverinfo="text", 
                                                          hovertemplate=[None if hoverable == UNSELECTED_OPACITY else _get_hover_template(color_feature) for hoverable in data.loc[data[color_feature] == trace.name, 'selected']])) # Set Hoverable template for all points. Points that are NOT selected (aka not visible) have no hover info.

        # If no primary color attribute is selected, grey out all points
        else:
            colorSeq = [GRAYED_OUT_COLOR]
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                                 zoom=3,
                                 custom_data=GLOBAL_CUSTOM_DATA,
                                 color=None, color_discrete_sequence=colorSeq)
            fig.update_traces(marker_opacity=data['selected'])  # Reduce opacity of unselected points
            fig.update_traces(hoverinfo="text", hovertemplate=[None if hoverable == 0 else _get_hover_template(color_feature) for hoverable in data['selected']]) # Set Hoverable template for all points. Points that are NOT selected (aka not visible) have no hover info.
        
        # Set map to dark mode & return figure
        fig.update_layout(map=dict(style="dark"), font_color="#bcbcbc")  # Dark, Light, Satelite
        fig.update_layout(margin=dict(l=0, r=0, t=40, b=0),paper_bgcolor="#2C353C")

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
    fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name", width=1000, height=860, zoom=3,
                         custom_data=["UID"],
                         hover_data=["UID","Present.at.time.of.bite", "Shark.behaviour","Victim.injury","Injury.location","Diversionary.action.taken"],
                         color=None)
    fig.update_layout(map=dict(style="dark"), font_color="#bcbcbc")  # Dark, Light, Satelite
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0),paper_bgcolor="#2C353C")
    return dcc.Graph(figure=fig, id=id, style={
            "width": "100%",    # Make the graph take full width of the parent container
            "height": "95vh",   # Height dynamically adjusts to 75% of the viewport height
            "display": "block", # Ensures proper layout
            "margin": "0 auto"  # Center it horizontally (optional)
        })