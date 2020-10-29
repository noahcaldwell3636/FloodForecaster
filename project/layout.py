import dash_core_components as dcc
import dash_html_components as html



def get_latitude_div():
    return  html.Div(
                id='latitude',
                style={
                    'padding-left': '1%',
                    'padding-top': '1%',
                    'color': 'rgba(0,0,0,.3)',
                    'display': 'inline-block',
                    'font-size': '200%',
                    '-webkit-transform':'scale(2,1)',
                    'margin-left': '20%',
                },
            ),