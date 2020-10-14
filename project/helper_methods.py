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


def fill_missing_time(time):
    # compute the time fill points
    adjusted_time = []
    for six_hrs in time:
        adjusted_time.append(six_hrs)
        time_segments = six_hrs.split(" ")
        date, hour, post = (time_segments[0], int(time_segments[1].split(":")[0]), time_segments[2])
        minute = 0
        # create and append fill points
        for i in range(0,23): # 24, 15-minute intevals in six hours. Minus the last point as it is already accounted for.
            # create fill minute and hours data
            if minute == 45: # increment to next hour if 15 minutes away
                minute = 0
                # adjust for 12 hour clock
                if hour == 12:
                    hour == 1
                else:
                    hour += 1
            else: # add 15 minutes
                minute += 15
            # format hour int for output
            if hour <= 9:
                hour_str = "0" + str(hour)
            else:
                hour_str = str(hour)            
            # format minute int for output
            if minute == 0:
                minute_str = '00'
            else:
                minute_str = str(minute)
            # add fill point
            formatted_fill_point = date + " " + hour_str + ":" + minute_str + " " + post
            adjusted_time.append(formatted_fill_point)
    return adjusted_time

def fill_missing_levels(levels):
    adjusted_levels = []
    for i in range(len(levels)):
        current_level = float(levels[i])
        adjusted_levels.append(str(current_level))
        try:
            next_level = float(levels[i+1])
        except:
            break
        # compute rate of change per increment
        points = 23 # 24, 15-minute segments in 6 hours. Minus the last point because it it the next point
        rate_of_change = (1/23) * (next_level-current_level)
        # create each fill point
        fill_point = current_level + rate_of_change
        adjusted_levels.append(str(fill_point))
        for j in range(points-1): 
            fill_point = fill_point + rate_of_change
            adjusted_levels.append(str(fill_point))
    return adjusted_levels





def get_flood_data(xml_root, observed_or_forecast):
    elements = xml_root.findall(observed_or_forecast + '/datum')
    level = []
    time = []
    # get xml data
    for datum in elements:
        datetime_UTC = datum.find('valid').text
        water_level = datum.find('primary').text # in feet
        flow = datum.find('secondary').text # in kcfs
        pedts = datum.find('pedts').text
        level.append(water_level)
        formatted_datetime = convert_to_datetime_EST(datetime_UTC)
        time.append(formatted_datetime)
    # format xml data for dash
    if observed_or_forecast == 'observed':
        time.reverse()
        level.reverse()
    elif observed_or_forecast == 'forecast':
        time = fill_missing_time(time)
        level = fill_missing_levels(level)
    else:
        raise ValueError("~Boone~ the get_flood_data method expects the 'observed' or 'forecast'.")
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