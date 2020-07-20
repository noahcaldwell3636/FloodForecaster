import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import xml.etree.ElementTree as ET
from urllib.request import urlopen


def convert_to_datetime_EST(datetime_str):
    date = datetime_str.split('T')[0].split('-')
    year, month, day = (int(date[0]), int(date[1]), int(date[2]))
    time = datetime_str.split('T')[1].split('-')[0].split(":")
    hour, minute, second = time[0], time[1], time[2]
    dt_conversion = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute))
    datetime_12hour = datetime.datetime.strptime(str(dt_conversion), "%Y-%m-%d %H:%M:%S")
    datetime_12hour = datetime_12hour.strftime('%x %I:%M %p')
    print(datetime_12hour)
    return datetime_12hour

def get_xml_data():
    # get xml object from the internet
    data_url = urlopen('https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=xml')
    xml_doc = ET.parse(data_url)
    root = xml_doc.getroot()
    observed = root.findall('observed/datum')
    level = []
    time = []
    for datum in observed:
        datetime_UTC = datum.find('valid').text
        water_level = datum.find('primary').text # in feet
        flow = datum.find('secondary').text # in kcfs
        pedts = datum.find('pedts').text
        level.append(water_level)
        formatted_datetime = convert_to_datetime_EST(datetime_UTC)
        time.append(formatted_datetime)
    level.reverse()
    time.reverse()
    return {'time':time, 'level':level}

# attatch CSS 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Create App

UPDATE_FREQUENCY_MINUTES = 15
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('James River Flood Forecast'),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=UPDATE_FREQUENCY_MINUTES*60*1000, # minutes
            n_intervals=0
        )
    ])
)


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    data = get_xml_data()
    current_level = float(data['level'][-1])
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span(f'Water Level: {current_level}', style=style)
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    data = get_xml_data()
    # Create the graph with subplots
    fig = make_subplots(rows=1, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    fig.append_trace({
        'x': data['time'],
        'y': data['level'],
        'name': 'Water Level',
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True,port=6969)
    app.run_server(debug=True, dev_tools_silence_routes_logging = False)
    app.run_server(debug=True)