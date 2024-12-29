import pandas as pd
from dash import Dash, html
from dash_bootstrap_components.themes import BOOTSTRAP

from components import dropdown_component, scattermap_component, barplot_component

df = pd.read_excel('sharks_clean.xlsx')
plotable_columns = ["Incident.month", "Victim.injury", "State", "Site.category", "Provoked/unprovoked",
                     "Victim.activity", "Injury.severity", "Victim.gender", "Data.source"]
gradient_columns = ["Incident.month", "Incident.year", "Shark.length.m", "Victim.age", "Time.of.incident"]


def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className = "app-div",
        children=[
            html.Div( 
                className = "left-col",
                children=[
                     html.Div(
                        className = "bar_plot",
                        children=[
                            barplot_component.render(app, id="bar_plot", data=df),
                        ]),
                    html.Div(
                        className = "drop_down",
                        children=[
                            dropdown_component.render(app, id="barplot_dropdown", name="Barplot Attribute", 
                                        values={col.replace(".", " "): col for col in plotable_columns}),
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


app = Dash(external_stylesheets=[BOOTSTRAP])

app.title = "Map"
app.layout = create_layout(app)

app.run_server(debug=True)