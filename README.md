# JBI100 - Shark visualizer
A tool for visualizing shark incidents in Australia, developed by Group 31 (T. Fotoglou, C. Koster, W. Leenen, N. Taflampas) for the Visualization course @ TU/e. The tool visualizes the ASID database, which can be found here: https://github.com/cjabradshaw/AustralianSharkIncidentDatabase.

## How to run the app
Simply run app.py in any Python 3.10+ environment, and go to the link shown in the terminal in your browser (by default this is http://127.0.0.1:8050/). The python environment needs to have several packages installed; we recommend anaconda, which has most of them pre-installed. Any packages not found in anaconda by default can be found in requirements.txt and can be installed using the console command `pip install -r requirements.txt`.

## Code structure
On a high level, the code is structured as follows:
- The `components` folder contains code for the individual components of the app (barplot, scattermap, dropdowns, etc.). Each of these components has a `render` function that renders the component in the app, and an `update_figure` function with callbacks that update the figure when any callback input changes.
- The components are put together into an HTML page in `app.py`, which is styled using CSS found in the `assets` folder.
- An important component is the data store, defined in `data_cleaning.py`. This component stores a central dataframe which is used by all plots. It takes selections and filters from all plots as callback inputs, filters and highlights the data accordingly, and outputs the dataframe, which is used as a callback input by the plots.