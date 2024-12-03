from dash import Dash, html, dcc

"""
Creates a Dropdown menu instance component.

Dash app - The application (used for callbacks)
String id - A unique ID not used by any other component in our app
String name - The displayed name of the dropdown menu
List|Dict values - Either a list of options for the dropdown menu OR a dictionary containing pairs of <label:value> where
  label is the name visible to the user and value is the name used by the application.
bool is_multiple_choice - True if we can select more than one item. False by default

@Return A Div object containing a dropdown menu.
"""
def render(app: Dash, id: str, name: str, values: list|dict, is_multiple_choice: bool = False) -> html.Div:
    dropdown_options = ["Option 1", "Option 2", "Option 3"] if values is None else values
    choices = None
    if type(values) is list:
        choices = [{"label": col, "value": col} for col in values]
    else:
        choices = [{"label": i, "value": values[i]} for i in values]



    return html.Div(
        children=[
            html.H6(name),
            dcc.Dropdown(
                id=id,
                multi=is_multiple_choice,
                value=[],
                options=choices
            )
        ]
    )