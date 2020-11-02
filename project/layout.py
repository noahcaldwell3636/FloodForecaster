from helper_methods import *


app_colors = {
    'black': '#232931',
    'grey': '#807875',
    'green': '#41aea9',
    'white': "#eeeeee",
    'blue': '#16697a',
    'purple': '#9d65c9',
    'red': "#ff5747",
}

def get_latitude_style():
    return {
        'color': app_colors['grey'],
        'display': 'inline-block',
        'font-size': '130%',
        'background-color': app_colors['black'],
        'text-align': 'right',
    }

def get_longitude_style():
    return {
        'color': app_colors['grey'],
        'display': 'inline-block',
        'font-size': '130%',
        'background-color': app_colors['black'],
        'text-align': 'left',
    }

def get_obs_time_style():
    return {
        'color': app_colors['grey'],
        'font-size': '130%',
        'background-color': app_colors['black'],
        'padding-bottom': '3%',
    }

def get_temp_style():
    return {
        'color': app_colors['red'],
        'font-size': '8em',
        'font-weight': 900,
        'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
        # 'background-color': app_colors['black'], # allows overlapping to deal with spacing 
        'margin-top': '-8%',
        'margin-bottom': '-7%',
        'z-index': 0,
        'margin-left': 'auto',
        'margin-right': 'auto',
    }

def get_feels_like_style():
    return {
        'color': app_colors['grey'],
        'font-size': '1.5em',
        'font-weight': 900,
        'text-shadow': '0.02em 0.02em 0 ' + app_colors['blue'], 
        'background-color': app_colors['black'],
        'margin-left': 'auto',
        'margin-right': 'auto',
    }


def get_weather_code_style():
    return {
        'color': app_colors['red'],
        'font-size': '2em',
        'font-weight': 900,
        'background-color': app_colors['black'],
        'text-align': 'center',
    }


def get_cloud_cover_style():
    return {
        'color': app_colors['red'],
        'font-size': '2em',
        'font-weight': 900,
        'background-color': app_colors['black'],
        'text-align': 'center',
    }


def get_barometer_style():
    return {
        'color': app_colors['red'],
        'font-size': '2em',
        'font-weight': 900,
        'background-color': app_colors['black'],
        'text-align': 'center',
    }

def get_humidity_style():
    return {
        'color': app_colors['red'],
        'font-size': '2em',
        'font-weight': 900,
        'background-color': app_colors['black'],
        'text-align': 'center',
        'margin': '0% 0% 0% 0%',
    },

def get_precipitation_type_style():
    return {
        'color': app_colors['red'],
        'font-size': '2em',
        'font-weight': 900,
        'background-color': app_colors['black'],
        'text-align': 'center',
        'margin': '0% 0% 0% 0%',
    }

def get_visability_style():
    return {
        'color': app_colors['red'],
        'font-size': '2em',
        'font-weight': 900,
        'background-color': app_colors['black'],
        'text-align': 'center',
        'margin': '0% 0% 0% 0%',
    }

def get_wind_gust_style():
    return {
        'color': app_colors['red'],
        'font-size': '2em',
        'font-weight': 900,
        'background-color': app_colors['black'],
        'text-align': 'center',
        'margin': '0% 0% 0% 0%',
    }

def get_wind_speed_style():
    return {
        'color': app_colors['red'],
        'font-size': '2em',
        'font-weight': 900,
        'background-color': app_colors['black'],
        'text-align': 'center',
        'margin': '0% 0% 0% 0%',
    }

def get_current_time_style():
    return {
        'background-color': app_colors['black']
    }


def get_time_postfix_style():
    return {
        'color': app_colors['red'],
        'font-size': '3em',
        'font-weight': 900,
        'margin-top': 'auto',
        'margin-bottom': 'auto',
        'background-color': app_colors['black'],
        'z-index': 1,
    }

def get_date_display_style():
    return {
        'color': app_colors['red'],
        'font-size': '3em',
        'font-weight': 900,
        'margin-top': 'auto',
        'margin-bottom': 'auto',
        'padding-left': '5%',
        'background-color': app_colors['black'],
        'z-index': 1,
    }





def get_gradient1_style(clima_data):
    return {
        'background': app_colors['black'],
        'background': get_gradient(
            1, 
            clima_data['sunrise_value'], 
            clima_data['sunset_value'], 
            app_colors['red'], 
            'yellow', 
            'black'
        ),
        'padding-left': 0,
        'padding-right': 0,
    }

def get_time_slider_style():
    return {
        'background': 'yellow',
        'width': '5px',
        'height': '45px',
        'margin-left': f'{int(get_mins_from_midnight() / (24 * 60))}%',
        'padding': 0,
    }

def get_sunrise_style():
    return {
        'color': app_colors['red'],
        'font-size': '1em',
        'font-weight': 900,
        'text-align': 'center',
        'float': 'left',
        'position': 'absolute',
        'z-index': '100',
    }

def get_gradient2_style(clima_data):
    return {
        'background': app_colors['red'],
        'background': get_gradient(
            2, 
            clima_data['sunrise_value'], 
            clima_data['sunset_value'],
            app_colors['red'], 
            'yellow', 
            'black'                            
        ),
    }


def get_sunset_style():
    return {
        'color': app_colors['red'],
        'font-size': '1em',
        'font-weight': 900,
        'text-align': 'center',
        'postion': 'absolute',
        'float': 'right',
    }

