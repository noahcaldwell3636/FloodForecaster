import dash
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
import plotly.graph_objs as go
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
        html.Div(className='row', children=[html.Div(dcc.Graph(id='flood-graph', animate=False), className='')]),
        dcc.Interval(
            id='flood-update-interval',
            interval= 30 * 1000,
            n_intervals= 0
        )
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

@app.callback(
    Output(component_id='flood-graph', component_property='figure'),
    [Input('flood-update-interval', 'interval')])
def update_flood_graph(interval):
    obs_data = get_observed_data()
    obs_plot = go.Scatter(x=obs_data['Time'], y=obs_data['Level'])


    forecast_data = get_forecast_data()
    forecast_data = bridge_to_fore(observed_data, forecast_data)
    forecast_plot = go.Scatter(x=forecast_data['Time'], y=forecast_data['Level'])

    print("update!")

    return {
        'data': [obs_plot, forecast_plot]
    }



if __name__ == '__main__':
    app.run_server(debug=True,port=6969)
    app.run_server(debug=True, dev_tools_silence_routes_logging = False)
    app.run_server(debug=True)
