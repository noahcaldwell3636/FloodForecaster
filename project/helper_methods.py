from urllib.request import urlopen
import xml.etree.ElementTree as ET
import datetime
from plotly.subplots import make_subplots
import dash_core_components as dcc
import pandas as pd


def convert_to_datetime_EST(datetime_str):
    date = datetime_str.split('T')[0].split('-')
    year, month, day = (int(date[0]), int(date[1]), int(date[2]))
    time = datetime_str.split('T')[1].split('-')[0].split(":")
    hour, minute, second = time[0], time[1], time[2]
    dt_conversion = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute))
    datetime_12hour = datetime.datetime.strptime(str(dt_conversion), "%Y-%m-%d %H:%M:%S")
    datetime_12hour = datetime_12hour.strftime('%x %I:%M %p')
    return datetime_12hour


def get_xml_root(url):
    # get xml object from the internet
    data_page = urlopen(url)
    xml_doc = ET.parse(data_page)
    return xml_doc.getroot()


def fill_missing_forecasted():
    pass


def get_flood_data(xml_root, observed_or_forecast):
    elements = xml_root.findall(observed_or_forecast + '/datum')
    level = []
    time = []
    for datum in elements:
        datetime_UTC = datum.find('valid').text
        water_level = datum.find('primary').text # in feet
        flow = datum.find('secondary').text # in kcfs
        pedts = datum.find('pedts').text
        level.append(water_level)
        formatted_datetime = convert_to_datetime_EST(datetime_UTC)
        time.append(formatted_datetime)
    if observed_or_forecast == 'observed':
        time.reverse()
        level.reverse()
    data = list(zip(time, level))
    return pd.DataFrame(data, columns=['Time', 'Level'])


def get_observed_data():
    # get xml object from the internet
    xml_root = get_xml_root(url='https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=xml')
    return get_flood_data(xml_root, "observed")


def get_forecast_data():
    xml_root = get_xml_root(url='https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=xml')
    return get_flood_data(xml_root, "forecast")

def get_custom_graph():
    # Create the graph with subplots
    fig = make_subplots(rows=1, cols=1, vertical_spacing=0.2)
    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    return fig

def create_flood_graph():
    observed_df = get_observed_data()
    forecast_data = get_forecast_data()

    return dcc.Graph(
        figure=dict(
            data=[
                dict(
                    x=observed_df['Time'],
                    y=observed_df['Level'],
                    name='Observed',
                    marker=dict(
                        color='rgb(55, 83, 109)'
                    )
                ),
                dict(
                    x=forecast_data['Time'],
                    y=forecast_data['Level'],
                    name='Forecasted',
                    marker=dict(
                        color='rgb(26, 118, 255)'
                    )
                )
            ],
            layout=dict(
                title='James River Flood Level (Richmond-Westham)',
                showlegend=True,
                legend=dict(
                    x=0,
                    y=1.0
                ),
                margin=dict(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 700},
        id='my-graph'
    )  

def create_flood_interval(frequency_secs):
    return dcc.Interval(
            id='interval-component',
            interval= frequency_secs * 1000,
            n_intervals= 0
        )