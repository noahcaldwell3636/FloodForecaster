import dash
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
# MY IMPORTS
from helper_methods import *
from layout import *


#################################################################################
################################_GET_DATA_#######################################
#################################################################################
observed_data = get_observed_data()
forecast_data = get_forecast_data()
bridged_fore_data = bridge_to_fore(observed_data, forecast_data)


##################################################################################
##################################_LAYOUT_########################################
##################################################################################
# Create App

app = dash.Dash(__name__)
app.layout = html.Div(
    html.Div([
        html.H4('James River Flood Forecast'),
        html.Div(id='live-update-text'),
        create_flood_graph(
            observed_df=observed_data,
            forecast_df=bridged_fore_data
        ),
        create_flood_interval(15)
    ])
)

##################################################################################
##################################_CALLBACKS_#####################################
##################################################################################

# @app.callback(Output('live-update-text', 'children'),
#               [Input('interval-component', 'n_intervals')])
# def update_metrics(n):
#     data = get_observed_data()
#     current_level = float(data['Level'].iloc[-1])
#     style = {'padding': '5px', 'fontSize': '16px'}
#     return [
#         html.Span(f'Water Level: {current_level}', style=style)
#     ]


# Multiple components can update everytime interval gets fired.
# @app.callback(Output('live-update-graph', 'figure'),
#               [Input('interval-component', 'n_intervals')])
# def update_graph_observed(n):
#     data = get_observed_data()
#     fig = get_custom_graph()
#     fig.append_trace({
#         'x': data['time'],
#         'y': data['level'],
#         'name': 'Water Level',
#         'mode': 'lines+markers',
#         'type': 'scatter'
#     }, 1, 1)
#     return fig



if __name__ == '__main__':
    app.run_server(debug=True,port=6969)
    app.run_server(debug=True, dev_tools_silence_routes_logging = False)
    app.run_server(debug=True)
