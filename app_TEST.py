import pandas as pd
from dash import Dash, html, dcc, Input, Output
from dash_bootstrap_components.themes import BOOTSTRAP

from components import dropdown_component, scattermap_component, barplot_component, scatterplot_component, parcat_component, stackedbar_component

app = Dash(external_stylesheets=[BOOTSTRAP])

############################
#
# Attempt at making a dropdown which allows you to choose which plot to show.
# CURRENTLY NOT FUNCTIONAL.
#
############################

# Read in data
df = pd.read_excel('sharks_clean.xlsx')

# Options for dropdowns
plotable_columns = ["Incident.month", "Victim.injury", "State", "Site.category", "Provoked/unprovoked",
                     "Victim.activity", "Injury.severity", "Victim.gender", "Data.source"]
gradient_columns = ["Incident.month", "Incident.year", "Shark.length.m", "Victim.age", "Time.of.incident"]
plot_types = ["Bar plot", "Stacked bar plot", "Parallel categories plot", "Scatterplot"]

# Create actual layout
def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className = "app-div",
        children=[
            html.Div( 
                className = "left-col",
                children=[
                    html.Div(
                        className = "generic_plot",
                        children=[
                            dcc.Graph(id='generic_plot') # Placeholder graph, updated by select_plot function
                        ]),
                    #html.Div(
                    #    className = "bar_plot",
                    #    children=[
                    #        barplot_component.render(app, id="bar_plot", data=df),
                    #    ]),
                    #html.Div(
                    #    className = "parcat",
                    #    children=[
                    #        parcat_component.render(app, id="parcat", data=df),
                    #    ]),
                    html.Div(
                        className = "drop_down",
                        children=[
                            dropdown_component.render(app, id="plottype_dropdown", name="Plot to show", 
                                        values=plot_types),
                            dropdown_component.render(app, id="barplot_dropdown", name="Barplot Attribute", 
                                        values={col.replace(".", " "): col for col in plotable_columns}),
                            #dropdown_component.render(app, id="scatterplot_dropdown_x", name="Scatterplot x Attribute", 
                            #            values={col.replace(".", " "): col for col in plotable_columns}),
                            #dropdown_component.render(app, id="scatterplot_dropdown_y", name="Scatterplot y Attribute", 
                            #            values={col.replace(".", " "): col for col in plotable_columns}),
                            dropdown_component.render(app, id="map_dropdown", name="Map Attribute", 
                                                        values={col.replace(".", " "): col for col in
                                                                plotable_columns + gradient_columns})
                        ]),
            ]),
            html.Div(
                className = "right-col",
                children=[ 
                    scattermap_component.render(app, data=df, id="map")
            ]),
        ]
    )

# Auxiliary function for choosing a plot
@app.callback(
    Output('generic_plot', 'figure'),
    [Input('plottype_dropdown', 'value')]
)
def select_plot(plot_type: str) -> dcc.Graph:
    if plot_type == "Bar plot":
        return barplot_component.render(app, id="bar_plot", data=df)
    elif plot_type == "Stacked bar plot":
        return stackedbar_component.render(app, id="stacked_bar_plot", data=df)
    elif plot_type == "Parallel categories plot":
        return parcat_component.render(app, id="parcat_plot", data=df)
    elif plot_type == "Scatterplot":
        return scatterplot_component.render(app, id="scatterplot", data=df)
    return dcc.Graph()

app.title = "Map"
app.layout = create_layout(app)

app.run_server(debug=True)