import pandas as pd
from dash import Dash, html, dcc, Input, Output
from dash_bootstrap_components.themes import BOOTSTRAP

from components import dropdown_component, scattermap_component, barplot_component, scatterplot_component, parcat_component, stackedbar_component, checklist_component, data_cleaning, timeline_component

app = Dash(external_stylesheets=[BOOTSTRAP])

# Read in data
df = pd.read_excel('sharks_clean.xlsx')

# Options for dropdowns
plotable_columns = ["Incident.month", "Victim.injury", "State", "Site.category", "Provoked/unprovoked", # "Present.at.time.of.bite", "Injury.location", # These two attributes have a lot of unknown/other values, but might still give insights
                     "Victim.activity", "Injury.severity", "Victim.gender", "Data.source", "Shark.name"]
gradient_columns = ["Incident.month", "Incident.year", "Shark.length.m", "Victim.age", "Time.of.incident"]

# Create actual layout
def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className = "app-div",
        children=[
            #Toggle Button
            # Toggle button
            html.Div(
                style={"padding": "10px", "textAlign": "center", "display": "flex", "flexDirection": "column", "gap": "10px"},
                children=[
                    html.Button("Display Plots", id="toggle-button", n_clicks=0, style={"padding": "10px", "fontSize": "16px"}),
                    html.Button('Clear Plot', id='clear_selection_button', style={"padding": "10px", "fontSize": "16px"})
                ]
            ),
            html.Div( 
                id="left-col",
                className = "left-col",
                style={"flex": 1, "width": "34%", "padding": "10px"},
                children=[
                    # Data storage
                    html.Div(
                        className="data_store",
                        children=[
                            data_cleaning.store(app, id="data_store", all_data=df)
                        ]),
                    # Old barplot
                    #html.Div(
                    #    className = "bar_plot",
                    #    children=[
                    #        barplot_component.render(app, id="bar_plot", data=df),
                    #    ]),
                    # Stacked barplot
                    html.Div(
                        className = "stacked_bar",
                        children=[
                            stackedbar_component.render(app, id="stacked_bar", all_data=df),
                        ]),
                    # Parallel categories plot
                    html.Div(
                        className = "parcat",
                        children=[
                            parcat_component.render(app, id="parcat", data=df),
                        ]),
                    # Dropdowns
                    html.Div(
                        className = "drop_down",
                        children=[
                            #dropdown_component.render(app, id="barplot_dropdown", name="Barplot Attribute", 
                            #            values={col.replace(".", " "): col for col in plotable_columns}), # Old barplot dropdown
                            dropdown_component.render(app, id="primary_color_dropdown", name="Primary color attribute", 
                                        values={col.replace(".", " "): col for col in plotable_columns},
                                        default_value = "State")
                                        ,
                            dropdown_component.render(app, id="secondary_color_dropdown", name="Barplot: Secondary color attribute", 
                                        values={col.replace(".", " "): col for col in plotable_columns},
                                        default_value = []),
                            dropdown_component.render(app, id="parcat_dropdown", name="Parallel categories attributes", 
                                        values={col.replace(".", " "): col for col in plotable_columns}, is_multiple_choice=True,
                                        default_value = ["State", "Victim.injury"]),         
                            #dropdown_component.render(app, id="map_dropdown", name="Map Attribute", 
                            #                            values={col.replace(".", " "): col for col in
                            #                                    plotable_columns + gradient_columns}) # Old map dropdown
                        ]),
                    # Checklists
                    html.Div(
                        className = "Checklist",
                        style={"padding": "10px", "textAlign": "center"},
                        children=[
                            checklist_component.render(app, id="stackedbar_normalize_checkbox", values=["Normalize stacked bar chart"])
                        ]
                    ),
                    # Time slider
                    html.Div(
                        className = "TimeLine",
                        children = [
                            timeline_component.render(app, data=df, id = "timeline",)
                        ]
                    ),
                    
            ]),
            # Main map
            html.Div(
                id="right-col",
                className = "right-col",
                style={"flex": 1, "width": "64%", "padding": "10px"},
                children=[ 
                    scattermap_component.render(app, all_data=df, id="map")
            ]),
        ],
        style={"display": "flex", "flexDirection": "row", "gap": "10px", "margin": "20px"}
    )

app.title = "Map"
app.layout = create_layout(app)

@app.callback(
    [Output("left-col", "style"),
     Output("right-col", "style"),
     Output("toggle-button", "children")],
    Input("toggle-button", "n_clicks")
)
def toggle_columns(n_clicks):
    if n_clicks % 2 == 1:  # Collapse left column
        left_style = {"display": "none"}
        right_style = {
            "flex": 1,
            "width": "100%",
            "padding": "10px",
            "boxSizing": "border-box",
            "overflow": "hidden",  # Prevent overflow
        }
        button_text = "Show Plots"
    else:  # Show left column
        left_style = {
            "flex": 1,
            "width": "36%",
            "padding": "10px",
            "overflowY": "auto",  # Enable vertical scrolling
            "height": "calc(100vh - 40px)",  # Full viewport height minus some space
            "boxSizing": "border-box",
        }
        right_style = {
            "flex": 1,
            "width": "64%",
            "padding": "10px",
            "boxSizing": "border-box",
            "overflow": "hidden",  # Prevent overflow
        }
        button_text = "Hide Plots"

    return left_style, right_style, button_text


app.run_server(debug=True)