import dash
import dash_html_components as html
import dash_daq as daq
import plotly
import dash_bootstrap_components as dbc
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
    'blue': '#16697a',
    'purple': '#9d65c9',
    'red': "#ff5747",
}

theme =  {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

external_stylesheets = [dbc.themes.BOOTSTRAP]

#################################################################################
################################_GET_DATA_#######################################
#################################################################################
observed_data = get_observed_data()
forecast_data = get_forecast_data()
bridged_fore_data = bridge_to_fore(observed_data, forecast_data)


##################################################################################
##################################_LAYOUT_########################################
##################################################################################

########### CREATE APP ######################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
########### CREATE APP ######################


########### LAYOUT ######################
app.layout = html.Div([

    dcc.Interval(
            id='flood-update-interval',
            interval= 30 * 1000,
            n_intervals= 0,
        ),

    dbc.Row([
        #################_FLOOD_GRAPH_###########################
        dbc.Col(html.Div(className='', children=[html.Div(dcc.Graph(id='flood-graph', animate=False), className='')],
            style={
                'display': 'inline-block',
            }
        ),
        width=9,
        ),
        #################_FLOOD_GRAPH_###########################

        ##################_METRICS_ON_RIGHT_#################################
        dbc.Col([

            ####################_COORDINATES_######################################
            dbc.Row([

                ##########LATITUDE##################
                html.Div(
                    id='latitude',
                    style={
                        'color': 'rgba(0,0,0,.3)',
                        'display': 'inline-block',
                        'font-size': '200%',
                        'padding-left': '25%',
                        'background-color': app_colors['black'],
                    },
                ),
                ##########LATITUDE##################

                ##########LATITUDE##################
                html.Div(
                    id='longitude',
                    style={
                        'color': 'rgba(0,0,0,.3)',
                        'display': 'inline-block',
                        'font-size': '200%',
                        'background-color': app_colors['black'],
                    },
                ),
                ##########LATITUDE##################

            ]),
            ####################_COORDINATES_######################################

            ####################_Temperature_######################################
            dbc.Row(html.Div(
                id='temp',
                style={
                    'color': app_colors['red'],
                    'font-size': '8em',
                    'font-weight': 900,
                    'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
                    'background-color': app_colors['black'],
                    'padding-left': '25%',
                },
            ),),
            ####################_Temperature_######################################

            ####################_Feels like temperature_######################################
            dbc.Row(html.Div(
                id='feels-like',
                style={
                    'color': app_colors['red'],
                    'font-size': '2em',
                    'font-weight': 900,
                    'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
                    'background-color': app_colors['black'],
                    'top': 0,
                    'left': '50%',
                    'text-align': 'center',
                },
            ),),
            ####################_Feels like temperature_######################################

            ####################_weather_description_######################################
            dbc.Row(html.Div(
                id='weather-code',
                style={
                    'display': 'table-row',
                    'color': app_colors['red'],
                    'font-size': '2em',
                    'font-weight': 900,
                    'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
                    'background-color': app_colors['black'],
                    'top': 0,
                    'left': '50%',
                    'text-align': 'center',
                    'margin': '0% 0% 0% 0%',
                    'z-index': 1,
                },
            ),),
            ####################_weather_description_######################################
        ],
        width=3,
        ),
    ],
    ),

    ####################################################################
    ##################_METRICS_ON_RIGHT#################################
    ####################################################################
    
    html.Div(
        id='cloud-cover',
        style={
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'left': '50%',
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),

    html.Div(
        id='barometer',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),

    html.Div(
        id='humidity',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),
    html.Div(
        id='obs_time',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'left': '50%',
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),
    html.Div(
        id='precipitation_type',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'left': '50%',
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),
    html.Div(
        id='sunrise',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'left': '50%',
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),
    html.Div(
        id='sunset',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'left': '50%',
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),
    html.Div(
        id='visability',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'left': '50%',
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),
    html.Div(
        id='wind-gust',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'left': '50%',
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),
    html.Div(
        id='wind-speed',
        style={
            'display': 'table-row',
            'color': app_colors['red'],
            'font-size': '2em',
            'font-weight': 900,
            'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
            'background-color': app_colors['black'],
            'top': 0,
            'left': '50%',
            'text-align': 'center',
            'margin': '0% 0% 0% 0%',
            'z-index': 1,
        },
    ),
    ]
)


##################################################################################
##################################_CALLBACKS_#####################################
##################################################################################

@app.callback(
    Output(component_id='flood-graph', component_property='figure'),
    [Input('flood-update-interval', 'interval')])
def update_flood_graph(interval):
    obs_data = get_observed_data()
    obs_plot = go.Scatter(
        name='Observed Level',
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
        name='Level Forecast',
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
        name='Action Stage',
        x=[x_lowest, x_highest], 
        y=[9, 9],
        fill=None,
        mode='lines',
        line_color='#696300')
    zone2 = go.Scatter(
        name='Flood Stage',
        x=[x_lowest, x_highest],
        y=[12, 12],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', line_color='#696300')
    zone3 = go.Scatter(
        name='Moderate Flood Stage',
        x=[x_lowest, x_highest],
        y=[15, 15],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', line_color='#694200')
    zone4 = go.Scatter(
        name='Major Flood Stage',
        x=[x_lowest, x_highest],
        y=[22, 22],
        fill='tonexty', # fill area between trace0 and trace1
        mode='lines', line_color='#691000')
    zone5 = go.Scatter(
        name='Record',
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
                font=dict(color=app_colors['red'], size=get_screen_resolution()['width']*.07),
                xref="paper",
                yref="paper",
                x=0,
                y=0,
                showarrow=False,
            ),
        ]
    )



    return {
        'data': [obs_plot, forecast_plot, zone1, zone2, zone3, zone4, zone5],
        'layout': go.Layout(
            height=int(get_screen_resolution()['height'] * .8),
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
            margin=dict(t=0, b=50, l=50, r=0),
            plot_bgcolor = app_colors['black'],
            paper_bgcolor = app_colors['black'],
            template="draft",
            legend=dict(
                # x=0,
                # y=0,
                bgcolor='rgba(0,0,0,0)',
                traceorder="reversed",
                title_font_family="Times New Roman",
                font=dict(
                    family="Courier",
                    size=12,
                    color="white",
                ),

            )
        )
    }


@app.callback(
    [
    Output(component_id='temp', component_property='children'),   
    Output(component_id='barometer', component_property='children'), 
    Output(component_id='cloud-cover', component_property='children'), 
    Output(component_id='feels-like', component_property='children'),  
    Output(component_id='humidity', component_property='children'), 
    Output(component_id='latitude', component_property='children'), 
    Output(component_id='longitude', component_property='children'),   
    Output(component_id='obs_time', component_property='children'), 
    Output(component_id='precipitation_type', component_property='children'), 
    Output(component_id='sunrise', component_property='children'), 
    Output(component_id='sunset', component_property='children'),  
    Output(component_id='visability', component_property='children'),  
    Output(component_id='weather-code', component_property='children'), 
    Output(component_id='wind-gust', component_property='children'),   
    Output(component_id='wind-speed', component_property='children'),  
    ],
    [Input(component_id='flood-update-interval', component_property='interval')]
)
def update_output_div(interval):
    data = get_climacell_data()

    return (
        str(round(data['temp_value'], 1)) + " " + str(data['temp_units']),
        str(data['baro_pressure_value']) + " " + data['baro_pressure_units'],
        "Cloud Cover: " + str(data['cloud_cover_value']) + str(data['cloud_cover_units']),
        "Feels Like: " + str(round(data['feels_like_value'], 1)) + str(data['feels_like_units']),
        "Humidity: " + str(data['humidity_value']) + str(data['humidity_units']),
        str(data['lat']) + "\N{DEGREE SIGN},",
        str(data['long']) + "\N{DEGREE SIGN}",
        "Last Updated: " + str(data['obs_time']),
        "Precipitation: " + str(data['precipitation_type_value']),
        "Sunset: " + str(data['sunset_value']),
        "Sunrise: " + str(data['sunrise_value']),
        "Visibility: " + str(data['visibility_value']) + str(data['visibility_units']),
        "Weather: " + str(data['weather_code_value']),
        "Top Wind Gust: " + str(data['wind_gust_value']) + str(data['wind_gust_value']),
        "Wind Speed: " + str(data['wind_speed_value']) + str(data['wind_speed_value']),
    )



if __name__ == '__main__':
    app.run_server(debug=True,port=6969)
    app.run_server(debug=True, dev_tools_silence_routes_logging = False)
    app.run_server(debug=True)
    print("something")
