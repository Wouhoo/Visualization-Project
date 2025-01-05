from dash import Dash, html, dcc

"""
Creates a checklist/checkbox instance.

Dash app - The application (used for callbacks)
String id - A unique ID not used by any other component in our app
List|Dict values - Either a list of options for the checklist menu OR a dictionary containing pairs of <label:value> where
  label is the name visible to the user and value is the name used by the application.
List selected - The value that is selected by default (none by default)

@Return A Div object containing a dropdown menu.
"""
def render(app: Dash, id: str, values: list|dict, selected: list = []) -> html.Div:
    selected = [] if selected is None else selected
    choices = None
    if type(values) is list:
        choices = [{"label": col, "value": col} for col in values]
    else:
        choices = [{"label": i, "value": values[i]} for i in values]

    return html.Div(
        children=[
            dcc.Checklist(
                id=id,
                options=choices,
                value=selected
            )
        ]
    )