import dash
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.io as pio
# MY IMPORTS
from helper_methods import *
from layout import *

################################################################################
##########################_CONSTANTS_###########################################
################################################################################
app_colors = {
    'black': '#232931',
    'grey': '#393e46',
    'green': '#41aea9',
    'white': "#eeeeee",
    'blue': '#0278ae',
    'purple': '#9d65c9',
    'red': "#db675e",
}


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
    obs_plot = go.Scatter(
        x=obs_data['Time'], 
        y=obs_data['Level'],
        line = dict(color = (app_colors['blue']),
                            width = 6),
        fill='tozeroy',
        fillcolor=app_colors['blue'],
    )


    forecast_data = get_forecast_data()
    forecast_data = bridge_to_fore(observed_data, forecast_data)
    forecast_plot = go.Scatter(
        x=forecast_data['Time'],
        y=forecast_data['Level'],
        line = dict(
            color = (app_colors['green']),
            width = 6,
        ),
        fill='tozeroy',
        mode="lines",
        dx=5,
    )

    # get range of y axis
    y_lowest = min( min(list(obs_data['Level'])), min(list(forecast_data['Level'])) ) - 2
    y_highest = max( max(list(obs_data['Level'])), max(list(forecast_data['Level'])) ) + 5

    x_lowest = obs_data['Time'].iloc[0]
    x_highest = forecast_data['Time'].iloc[-1]
    print(x_lowest, x_highest)

    zone1 = go.Scatter(
        x=[x_lowest, x_highest], 
        y=[9, 9],
        fill=None,
        mode='lines',
        line_color='#696300')
    zone2 = go.Scatter(
        x=[x_lowest, x_highest],
        y=[12, 12],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', line_color='#696300')
    zone3 = go.Scatter(
        x=[x_lowest, x_highest],
        y=[15, 15],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', line_color='#694200')
    zone4 = go.Scatter(
        x=[x_lowest, x_highest],
        y=[22, 22],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', line_color='#691000')
    zone5 = go.Scatter(
        x=[x_lowest, x_highest],
        y=[28.62, 28.62],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines',
        line_color='#9c0000',
        )

    current_level = obs_data['Level'].iloc[-1]
    level_metric_str = "Level: " + str(current_level) + "ft"
    pio.templates["draft"] = go.layout.Template(
        layout_annotations=[
            dict(
                name="draft watermark",
                text=level_metric_str,
                textangle=0,
                opacity=0.9,
                font=dict(color=app_colors['red'], size=200),
                xref="paper",
                yref="paper",
                x=0,
                y=0,
                showarrow=False,
            )
        ]
    )



    return {
        'data': [obs_plot, forecast_plot, zone1, zone2, zone3, zone4, zone5],
        'layout': go.Layout(
            height=int(get_screen_resolution()['height'] * .667),
            width=int(get_screen_resolution()['width'] * .8),
            xaxis={
                'title': "Date",
                'color': 'white',
            },
            yaxis={
                'title': "Water Level ft.",
                'range': ([0, y_highest]),
                'color': 'white',
            },
            plot_bgcolor = app_colors['black'],
            paper_bgcolor = app_colors['black'],
            template="draft"
        )
    }




if __name__ == '__main__':
    app.run_server(debug=True,port=6969)
    app.run_server(debug=True, dev_tools_silence_routes_logging = False)
    app.run_server(debug=True)
