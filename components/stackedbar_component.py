from dash import Dash, html, dcc, Input, Output, ctx
import plotly.express as px
import pandas as pd
from pandas import DataFrame
from .data_cleaning import MONTH_ORDER

"""
Creates a new scatterplot component instance.
Dash app - The application (used for callbacks)
DataFrame data - Our pandas dataset
String id - A unique ID not used by any other component in our app

@Returns: A dcc.Graph containing the scatterplot

NOTE: This component is not to be used (in its current state), as a scatterplot turns out to be unhelpful for our (mostly categorical) data.
"""

app = Dash(__name__)

#Plotly default color sequence (in order of normal selection).
PLOTLY_DEFAULT_COLORS = ['#636EFA','#EF553B','#00CC96','#AB63FA','#FFA15A','#19D3F3','#FF6692',
                        '#B6E880','#FF97FF','#FECB52']

# Actual render function
def render(app: Dash, id: str, all_data: DataFrame)-> dcc.Graph:
    @app.callback(
        Output("stacked_bar", "figure"),
        Output("barplot_title", 'children'),
        [Input("data_store", "data"),
         Input("primary_color_dropdown", "value"),
         Input("secondary_color_dropdown", "value"),
         Input("stackedbar_normalize_checkbox", "value"),
         Input("stacked_bar", "clickData")]
    )
    def update_figure(data, primary_color_feature, secondary_color_feature, normalize, bar_clicked):
        # Read in data
        if data is None:
            data = all_data
        filtered_data = DataFrame(data)  # Convert JSON data to pandas dataframe
        filtered_data = filtered_data.loc[filtered_data['selected'] == 1]  # Use only points selected on the map
        if(len(filtered_data) == 0):
            return px.bar(None), ['Shark Incidents per [Primary color attribute]']

        trigger = ctx.triggered_id

        if primary_color_feature is None or primary_color_feature == []:
            return px.bar(None), ['Shark Incidents per [Primary color attribute]']
        else:
            if secondary_color_feature is None or secondary_color_feature == []: # Effectively this uses the default bar chart if no color attribute is selected
                secondary_color_feature = primary_color_feature
        
        ### Construct a new dataframe for plotting ###
        # For the default bar chart, this df has 2 columns: primary_color_feature and the number/proportion of incidents for that feature value.
        # For the stacked bar chart, it instead has 3 columns: primary_color_feature, secondary_color_feature, and the number of incidents for that (primary_color_feature, secondary_color_feature) combination.
        
        # Get counts for each (primary, secondary) combination. Note: for the stacked bar chart, not all combinations are present in this df!
        value_counts = pd.DataFrame(filtered_data.groupby([primary_color_feature])[secondary_color_feature].value_counts(normalize=normalize)).reset_index()
        # Whether we have count or proportion on the y-axis
        y_feature = 'proportion' if normalize else 'count' 

        # Default bar chart; we are done here.
        if(secondary_color_feature == primary_color_feature):
            all_combinations = value_counts
        # Stacked bar chart; in this case *all (primary, secondary) combinations have to be present* in the df, otherwise we get a lot of bugs. 
        # That's why the method below is a bit roundabout.
        else:
            # Get unique values for primary and secondary color features and create dataframe with every (primary, secondary) combination
            primary_feature_values = DataFrame(filtered_data[primary_color_feature].drop_duplicates())
            secondary_feature_values = DataFrame(filtered_data[secondary_color_feature].drop_duplicates())
            # Create dataframe with every combination of primary and secondary feature value
            all_combinations = primary_feature_values.merge(secondary_feature_values, how='cross')
            # Add the counts/proportions we calculated earlier; fill in a 0 if that combination does not occur in the dataset
            all_combinations = all_combinations.merge(value_counts, how='left', on=[primary_color_feature, secondary_color_feature])
            all_combinations[y_feature] = all_combinations[y_feature].fillna(0)
            if not normalize: 
                all_combinations[y_feature] = all_combinations[y_feature].astype(int)

        # Sort months according to special ordering, otherwise sort alphabetically
        if(primary_color_feature == 'Incident.month'):
            all_combinations = all_combinations.sort_values(by=[primary_color_feature, secondary_color_feature], key = lambda x: x.map(MONTH_ORDER))
        elif(secondary_color_feature == 'Incident.month'):
            all_combinations = all_combinations.sort_values(by=[primary_color_feature, secondary_color_feature], key = lambda x: x.map(MONTH_ORDER))
        else:
            all_combinations = all_combinations.sort_values(by=[primary_color_feature, secondary_color_feature])
        #print("COMBINED DATAFRAME: ", all_combinations)  # TEST: If you want to see what the df looks like

        # Make initial plot
        selected_sequence = PLOTLY_DEFAULT_COLORS
        fig = px.bar(all_combinations, x=primary_color_feature, y=y_feature, color=secondary_color_feature, color_discrete_sequence=selected_sequence,
                     labels={primary_color_feature: primary_color_feature.replace(".", " "), y_feature: y_feature.title(), secondary_color_feature: secondary_color_feature.replace(".", " ")})

        # If the user clicks a bar, grey out all other bars
        if trigger == "stacked_bar":
            curveNumber = bar_clicked["points"][0]["curveNumber"]
            pointNumber = bar_clicked["points"][0]["pointNumber"]
            x = bar_clicked["points"][0]["x"]

            # Regular bar chart
            if(secondary_color_feature == primary_color_feature):
                # In this case a "trace" is one bar
                fig.for_each_trace(lambda trace: trace.update(marker_color = '#bababa') if trace.x != x else ()) # Set all unselected traces to grey
            
            # Stacked bar chart
            else:
                # In this case a trace consists of all sub-bars of the same type (i.e. all "injured" sub-bars)
                trace_names = all_combinations[secondary_color_feature].drop_duplicates().tolist()  # Trace names are the unique values of the color feature
                fig.for_each_trace(lambda trace: trace.update(marker_color = '#bababa') if trace.name != trace_names[curveNumber] else ())  # Set all unselected *traces* to grey
                #fig.for_each_trace(lambda trace: print(trace.x)) # TEST
                fig.update_traces(selectedpoints = [pointNumber])  # Selects the full bar that was clicked (i.e. selects all sub-bars with the same pointNumber)
                fig.update_traces(unselected_marker_color = '#BABABA')  # Sets all unselected *bars* to grey
        
        # TEST: implementing animations "quick and dirty" using plotly's built-in stuff
        #fig.update_layout(transition_ordering="traces first")  # For smooth transitions between bars
        # This looks pretty cool in the regular bar plot, but does not work well at all in the stacked plot...

        fig.update_layout(
            paper_bgcolor="#2C353C",
            font=dict(color='#bcbcbc'),  # Text color
            margin=dict(l=20,r=20,t=10,b=20)
        )  # Stack bars on top of each other


        return fig, ['Shark Incidents per {}'.format(primary_color_feature.replace("."," "))]
    
    
    return html.Div( children= [html.H5('Shark Incidents per [Primary color attribute]', style={'textAlign': 'center'}, id='barplot_title'), dcc.Graph(id = id)], style={'backgroundColor': '#2C353C', 'padding': '10px',})