import pandas as pd
from dash import Dash, html, Output, Input
from dash_bootstrap_components.themes import BOOTSTRAP


from NickComponents import dropdown_component, scattermap_component

df = pd.read_excel('sharks_clean.xlsx')
plotable_columns = ["Victim.injury", "State", "Site.category", "Provoked/unprovoked",
                     "Victim.activity", "Injury.severity", "Victim.gender", "Data.source"]
gradient_columns = ["Incident.month", "Incident.year", "Shark.length.m", "Victim.age", "Time.of.incident"]


def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className = "app-div",
        children=[
            html.Div(
                className="dropdown-container",
                children=[
                    scattermap_component.render(app, data=df, id="map"),

                    dropdown_component.render(app, id="color_dropdown", name="Color Attribute",
                        values={col.replace(".", " "): col for col in plotable_columns+gradient_columns}),

                    dropdown_component.render(app, id="barplot_dropdown", name="Barplot Attribute",
                                              values={col.replace(".", " "): col for col in plotable_columns}),

                    html.Div(id="click-output")
                ]
            )
        ]
    )


app = Dash(external_stylesheets=[BOOTSTRAP])

"""
Callback function. Is called when either a selection is made on the map, or the barplot dropdown
changes value.
Returns:
- ids: An array of all UIDs of the selected data. Is empty if none selected.
- barplotColumn: The string name of the selected column. None if none selected.
"""
@app.callback(
    Output("click-output", "children"),
    [Input("map", "selectedData"),
    Input("barplot_dropdown", "value")]
)
def display_click_data(selectedData, value):
    barplotColumn = None if value == [] else value

    if selectedData is None or len(selectedData) == 0:
        return None

    #UIDs of selected data.
    ids = []
    for point in selectedData["points"]:
        ids.append(point["customdata"][0])
    return str(barplotColumn) + str(ids)


app.title = "Map"
app.layout = create_layout(app)


app.run_server(debug=True)

