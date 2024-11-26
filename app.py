from jbi100_app.main import app
from jbi100_app.views.menu import make_menu_layout
from jbi100_app.views.main_map import MainMap
from jbi100_app.data import get_data

from dash import html
import plotly.express as px
from dash.dependencies import Input, Output


if __name__ == '__main__':
    # Create data
    df = get_data()

    # Instantiate custom views
    main_map = MainMap(df, "Shark attacks", "Incident.year")

    app.layout = html.Div(
        id="app-container",
        children=[
            html.Div(
                id="main-map",
                className="twelve columns",
                children=[main_map]
            )
        ],
    )

    # Define interactions
    #@app.callback(
    #    Output(main_map.html_id, "figure"), [
    #    Input("select-color-scatter-1", "value"),
    #])
    #def update_scatter_1(selected_color, selected_data):
    #    return main_map.update(selected_color, selected_data)

    app.run_server(debug=False, dev_tools_ui=False)