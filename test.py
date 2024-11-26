from jbi100_app.data import get_data
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Create data
df = get_data()

# Create a Scattermap(box) trace
# Note: scattermapbox is deprecated, scattermap is the new version. 
# But this new function does *not* exist in the plotly version we're required to have for this course.
# Can we still use it then, or not?
trace = go.Scattermap(
    lat=df['Latitude'],
    lon=df['Longitude'],
    mode='markers',
    marker=dict(size=12, color=df['Injury_color'], opacity=0.7), # Marker column is based on victim injury
    text=df['Incident.year']  # Display year of attack on hover
)

# Set up map layout
layout = go.Layout(
    map=dict(
        style="carto-positron",
        center=dict(lat=-25, lon=133),  # Center the map on Australia
        zoom=4
    ),
    title="Shark attacks in Australia"
)

# Create figure and plot
fig = go.Figure(trace, layout)
fig.show()