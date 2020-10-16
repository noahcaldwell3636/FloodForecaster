from urllib.request import urlopen
import xml.etree.ElementTree as ET
import datetime
from plotly.subplots import make_subplots
import dash_core_components as dcc
import pandas as pd


def convert_xmlstr_to_datetime(datetime_str):
    """ 
    Converts datetime_str time from the xml doc to a datetime object
    """
    try:
        time = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %I:%M:%S")
    except:
        time = datetime.datetime.strptime(datetime_str[:-6], "%Y-%m-%dT%H:%M:%S")

    dt = datetime.datetime(year=int(time.year), month=int(time.month), day=int(time.day), hour=int(time.hour), minute=int(time.minute))
    return dt


def convert_datetime_to_str(dt):
        return dt.strftime('%Y-%m-%d %I:%M:%S')


def get_xml_root(url):
    # get xml object from the internet
    data_page = urlopen(url)
    xml_doc = ET.parse(data_page)
    return xml_doc.getroot()


def bridge_obs_to_fore(observed_df, filled_time_df, patch_to_forecasted=False):
    """ 
    Returns a pandas dataframe of fill data accounting for the gap between the 
    end of the observed flood level data and the forecasted flood level data.

            - if patch_to_forecasted is swtched to 'True', the function will return a 
            concatination of both the bridge data and the forecasted data. Otherwise,
            the function will return a dataframe of just the bridge data.
    """

    # start of data bridge = obs_last_time
    obs_last_time = str(observed_df['Time'].iloc[-1])
    obs_last_time = datetime.datetime.strptime(obs_last_time, "%Y-%m-%d %I:%M:%S")
    # end of data bridge = for_fist_time
    fore_first_time = str(filled_time_df['Time'].iloc[0]) 
    fore_first_time = datetime.datetime.strptime(fore_first_time, "%Y-%m-%d %I:%M:%S")

    # get the difference in time between the gap
    hours_difference = (fore_first_time - obs_last_time).total_seconds() / 60 / 60
    intervals = int(hours_difference * 4) # number of 15 minute intervals
    
    # create list of all time values in the bridge
    bridge_times = []
    t = obs_last_time + datetime.timedelta(minutes=15)
    bridge_times.append(convert_datetime_to_str(t))
    for i in range(intervals-2):
        t = t + datetime.timedelta(minutes=15)
        bridge_times.append(convert_datetime_to_str(t))

    # get beginning and ending forecast levels
    start_level = float(observed_df['Level'].iloc[-1])
    end_level = float(filled_time_df['Level'].iloc[0])
    # get list of levels using Euler's Rule
    level_range = end_level - start_level
    increment = level_range / intervals
    bridge_levels = []
    lvl = start_level + increment
    bridge_levels.append(lvl)
    for i in range(intervals-2):
        lvl += increment
        bridge_levels.append(lvl)

    # if patch_to_forecasted:
    #     return pd.concat([pd.DataFrame(dict(Level=bridge_levels, Time=bridge_times)), filled_time_df])
    # else:
        return pd.DataFrame(dict(Level=bridge_levels, Time=bridge_times))


def fill_missing_time(time):
    """ Adds filler points to the forecast plot to account for the data being
    in 6 hour intervals instead of 15 minute intrevals like the observed plot.
    Allows the time and plot size to be consistent amongst the two plots. 
    """
    adjusted_time = []
    for sixhr_interval in time:
        adjusted_time.append(convert_datetime_to_str(sixhr_interval))
        fill_interval = sixhr_interval + datetime.timedelta(minutes=15)
        adjusted_time.append(convert_datetime_to_str(fill_interval))
        for i in range(23):
            fill_interval = fill_interval + datetime.timedelta(minutes=15)
            adjusted_time.append(convert_datetime_to_str(fill_interval))
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
        rate_of_change = (1/points) * (next_level-current_level)
        # create each fill point
        fill_point = current_level + rate_of_change
        adjusted_levels.append(str(fill_point))
        for j in range(points-1): # create next points except for the last point which is given in the level param
            fill_point = fill_point + rate_of_change
            adjusted_levels.append(str(fill_point))
    return adjusted_levels


def get_flood_data(xml_root, observed_or_forecast):
    xml_elements = xml_root.findall(observed_or_forecast + '/datum')
    level = []
    forecast_time_list = []
    # get xml data
    for datum in xml_elements:
        datetime_UTC = datum.find('valid').text
        water_level = datum.find('primary').text # in feet
        flow = datum.find('secondary').text # in kcfs
        pedts = datum.find('pedts').text
        level.append(water_level)
        formatted_datetime = convert_xmlstr_to_datetime(datetime_UTC)
        forecast_time_list.append(formatted_datetime)
    # format xml data for dash
    if observed_or_forecast == 'observed':
        forecast_time_list.reverse()
        level.reverse()
    elif observed_or_forecast == 'forecast':
        forecast_time_list = fill_missing_time(forecast_time_list)
        level = fill_missing_levels(level)
    else:
        raise ValueError("~Boone~ the get_flood_data method expects the 'observed' or 'forecast'.")
    data = list(zip(forecast_time_list, level))
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


if __name__ == "__main__":
    xml_root = get_xml_root('https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=xml')
    observed_data = get_flood_data(xml_root, 'observed')
    filled_forecast_data = get_flood_data(xml_root, 'forecast')

    result = bridge_obs_to_fore(observed_data, filled_forecast_data)







# time_segments = six_hrs.split(" ")
        # date, hour, post = (time_segments[0], int(time_segments[1].split(":")[0]), time_segments[2])
        # minute = 0
        # # create and append fill points
        # for i in range(0,23): # 24, 15-minute intevals in six hours. Minus the last point as it is already accounted for.
        #     # increment time
        #     if hour == 12 and minute == 45:
        #         hour = 1
        #         minute = 0
        #     elif minute == 45:
        #         hour += 1
        #         minute = 0
        #     else:
        #         minute += 15
        #     # convert hour and minute to str format
        #     if hour <= 9:
        #         hour_str = "0" + str(hour)
        #     else:
        #         hour_str = str(hour)            
        #     # format minute int for output
        #     if minute == 0:
        #         minute_str = '00'
        #     else:
        #         minute_str = str(minute)
        #     # add fill point