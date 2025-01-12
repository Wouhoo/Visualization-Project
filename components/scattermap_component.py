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
        #Input("map", "selectedData"),
        #Input("stacked_bar", "selectedData"),
        State("stackedbar_dropdown_x", "value"),
        State("stackedbar_dropdown_color", "value"),
        # Inputs for old bar plot version
        #Input("bar_plot", "clickData"),  
        #State("barplot_dropdown","value"),
        prevent_initial_call=True
    )
    def change_display(data, color_dropdown_value, bar_clicked, bar_x_feature, bar_color_feature):
    #def change_display(color_dropdown_value, bar_clicked, bar_dropdown_value):  # Definition for old bar plot
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
            #print(selected_data) # TEST
            colorIndex = bar_clicked["points"][0]["curveNumber"]  # Index of bar (default) or trace (stacked) in bar chart
            selectedColor = PLOTLY_DEFAULT_COLORS[colorIndex % len(PLOTLY_DEFAULT_COLORS)]  # Actual selected color
            selected_x_value = bar_clicked["points"][0]["x"] # x feature value corresponding to the selected (sub-)bar
            #print(bar_color_feature) # TEST
            #print(selected_x_value) # TEST
            #print(data[bar_x_feature]) # TEST

            # Default bar chart
            if(bar_color_feature == [] or bar_color_feature == '-'):
                data["highlight"] = data[bar_x_feature].apply(lambda x : "1" if x == selected_x_value else "0")  # Select incidents to highlight
                
            # Stacked bar chart
            else:
                colorNames = data[bar_color_feature].value_counts().index  # Unique values for barplot color feature
                selected_color_value = colorNames[colorIndex]  # Color feature value corresponding to the selected sub-bar
                data["highlight"] = data.apply(lambda row : "1" if (row[bar_x_feature] == selected_x_value and row[bar_color_feature] == selected_color_value) else "0", axis=1)

            # Create map with highlighted data
            fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
                                 zoom=3,
                                 custom_data=["UID"],
                                 hover_data=["Present.at.time.of.bite", "Shark.behaviour","Injury.location","Diversionary.action.taken"],
                                 color=data["highlight"], color_discrete_map={"1": selectedColor, "0": "gray"})

            #fig.update_traces(selectedpoints=[point['pointNumber'] for point in selected_data["points"]])  # If an area was selected, preserve the selection
            #fig.update_traces(selectedpoints=[0,34,60,78,91]) # This works, so the above should also work in principle
            # The problem appears to be in giving the map component *its own* selected data as a callback input...



            # (now to find a way to keep the old selected points...)
            # Intuitively the easiest way to do this would be to have the map take a callback input from itself
            # (take selected points as input and force those points to be selected in the re-created figure)
            # However, this may cause problems where you can't actually change which points get selected.
            # If this doesn't work, we can try to have the stacked bar plot take the map's selected points as input (which it already does)
            # and return it back to the map (as a callback input)
            fig.update_layout(map=dict(style="dark"))
            fig.update(layout_showlegend=False)
            return fig

        # Code from old bar plot (new version only uses stacked bar plot)
        #elif trigger == "bar_plot":
        #    colorIndex = bar_clicked["points"][0]["curveNumber"]
        #    selectedColor = PLOTLY_DEFAULT_COLORS[colorIndex % len(PLOTLY_DEFAULT_COLORS)]
        #    columnValue = bar_clicked["points"][0]["x"]
        #    columnName = bar_dropdown_value
        #    data["highlight"] = data[columnName].apply(lambda x : "1" if x == columnValue else "0")
        
        #    fig = px.scatter_map(data, lat="Latitude", lon="Longitude", hover_name="Shark.name",
        #                         zoom=3,
        #                         custom_data=["UID"],
        #                         hover_data=["Present.at.time.of.bite", "Shark.behaviour","Injury.location","Diversionary.action.taken"],
        #                         color=data["highlight"], color_discrete_map={"1": selectedColor, "0": "gray"})
        
        #    fig.update_layout(map=dict(style="dark"))
        #    fig.update(layout_showlegend=False)
        #    return fig

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