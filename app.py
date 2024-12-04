import pandas as pd
from dash import Dash, html, Output, Input
import dash_bootstrap_components as dbc
from dash_bootstrap_components.themes import BOOTSTRAP

from components import dropdown_component, scattermap_component, barplot_component

df = pd.read_excel('sharks_clean.xlsx')
plotable_columns = ["Victim.injury", "State", "Site.category", "Provoked/unprovoked",
                     "Victim.activity", "Injury.severity", "Victim.gender", "Data.source"]
gradient_columns = ["Incident.month", "Incident.year", "Shark.length.m", "Victim.age", "Time.of.incident"]


def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className = "app-div",
        children=[
                dbc.Row([
                    dbc.Col(html.Div(children=[
                        barplot_component.render(app, id="bar_plot", data=df),
                        dropdown_component.render(app, id="color_dropdown", name="Color Attribute",
                                                  values={col.replace(".", " "): col for col in
                                                          plotable_columns + gradient_columns}),
                        dropdown_component.render(app, id="barplot_dropdown", name="Barplot Attribute",
                                                  values={col.replace(".", " "): col for col in plotable_columns})
                    ])),
                    dbc.Col(html.Div(children=[
                        scattermap_component.render(app, data=df, id="map")
                    ]), width = 6)
                ])



        ]
    )


app = Dash(external_stylesheets=[BOOTSTRAP])

app.title = "Map"
app.layout = create_layout(app)


app.run_server(debug=True)