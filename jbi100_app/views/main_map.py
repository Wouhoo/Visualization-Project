from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px

class MainMap(html.Div):
    def __init__(self, df, name, feature_color):
        self.html_id = name.lower().replace(" ", "-")
        self.df = df
        self.feature_color = feature_color

        # Equivalent to `html.Div([...])`
        super().__init__(
            className="graph_card",
            children=[
                html.H6(name),
                dcc.Graph(id=self.html_id)
            ],
        )

    def update(self, selected_color, selected_data):
        self.fig = go.Figure()

        # Set data
        self.fig.add_trace(go.Scattermap(
            lat=self.df['Latitude'],
            lon=self.df['Longitude'],
            mode='markers',
            marker=dict(size=12, color=self.df['Injury_color'], opacity=0.7), # Marker column is based on victim injury
            text=self.df['Incident.year']  # Display year of attack on hover
        ))

        # Set layout
        self.fig.update_layout(go.Layout(
            mapbox=dict(
                style="carto-positron",
                center=dict(lat=-25, lon=133),  # Center the map on Australia
                zoom=4
            ),
            title="Shark attacks in Australia"
        ))
        
        return self.fig
    
    # OLD STUFF FROM THE SCATTERPLOT TEMPLATE
        #self.fig.update_traces(mode='markers', marker_size=10)
        #self.fig.update_layout(
        #    yaxis_zeroline=False,
        #    xaxis_zeroline=False,
        #    dragmode='select'
        #)
        #self.fig.update_xaxes(fixedrange=True)
        #self.fig.update_yaxes(fixedrange=True)

        # highlight points with selection other graph
        #if selected_data is None:
        #    selected_index = self.df.index  # show all
        #else:
        #    selected_index = [  # show only selected indices
        #        x.get('pointIndex', None)
        #        for x in selected_data['points']
        #    ]

        #self.fig.data[0].update(
        #    selectedpoints=selected_index,
#
#            # color of selected points
#            selected=dict(marker=dict(color=selected_color)),
#
#            # color of unselected pts
#            unselected=dict(marker=dict(color='rgb(200,200,200)', opacity=0.9))
#        )

        # update axis titles
#        self.fig.update_layout(
#            xaxis_title=self.feature_x,
#            yaxis_title=self.feature_y,
#        )