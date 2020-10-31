from urllib.request import urlopen
import xml.etree.ElementTree as ET
import datetime
from dateutil import tz
import pandas as pd
from win32api import GetSystemMetrics
from climacell_api.client import ClimacellApiClient



def convert_str_to_datetime(datetime_str):
    """ 
    Converts datetime_str time from the xml doc to a datetime object
    """
    try:
        time = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %I:%M:%S %p")
    except:
        try:
            time = datetime.datetime.strptime(datetime_str[:-6], "%Y-%m-%dT%H:%M:%S")
        except:
            try:
                time = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            except:
                raise ValueError("~Boone~ this method is meant to convert string into datetime objects, +"
                "in the following format \n %Y-%m-%d %I:%M:%S %p \n %Y-%m-%dT%H:%M:%S")
    dt = datetime.datetime(year=int(time.year), month=int(time.month), day=int(time.day), hour=int(time.hour), minute=int(time.minute))
    return dt


def convert_datetime_to_formatted_str(dt):
        return dt.strftime('%Y-%m-%d %I:%M:%S %p')

def get_xml_root(url):
    # get xml object from the internet
    data_page = urlopen(url)
    xml_doc = ET.parse(data_page)
    return xml_doc.getroot()


def bridge_to_fore(observed_df, filled_forecast_df):
    """ 
    Returns a pandas dataframe of fill data accounting for the gap between the 
    end of the observed flood level data and the forecasted flood level data.

            - if patch_to_forecasted is swtched to 'True', the function will return a 
            concatination of both the bridge data and the forecasted data. Otherwise,
            the function will return a dataframe of just the bridge data.
    """
    # start of data bridge = obs_last_time
    obs_last_time = str(observed_df['Time'].iloc[-1])
    obs_last_time = convert_str_to_datetime(obs_last_time)
    # end of data bridge = for_fist_time
    fore_first_time = str(filled_forecast_df['Time'].iloc[0]) 
    fore_first_time = convert_str_to_datetime(fore_first_time)
    # get the difference in time between the gap
    hours_difference = (fore_first_time - obs_last_time).total_seconds() / 60 / 60
    intervals = int(hours_difference * 4) # number of 15 minute intervals
    
    # create list of all time values in the bridge
    bridge_times = []
    t = obs_last_time + datetime.timedelta(minutes=15)
    bridge_times.append(convert_datetime_to_formatted_str(t))
    for i in range(intervals-2): # minues two b/c the first and last points are included on the observed df and the orginal df
        t = t + datetime.timedelta(minutes=15)
        bridge_times.append(t)

    # get beginning and ending forecast levels
    start_level = float(observed_df['Level'].iloc[-1])
    end_level = float(filled_forecast_df['Level'].iloc[0])
    # get list of levels using Euler's Rule
    level_range = float(end_level) - float(start_level)
    increment = level_range / intervals
    bridge_levels = []
    lvl = float(start_level + increment)
    bridge_levels.append(lvl)
    for k in range(intervals-2): # minues two b/c the first and last points are included on the observed df and the orginal df
        lvl += increment
        bridge_levels.append(lvl)
    
    bridge_data = pd.DataFrame(dict(Level=bridge_levels, Time=bridge_times))
    joint_bridge_forecast = pd.concat([bridge_data, filled_forecast_df])

    return joint_bridge_forecast


def fill_missing_time(given_time):
    """ Adds filler points to the forecast plot to account for the data being
    in 6 hour intervals instead of 15 minute intrevals like the observed plot.
    Allows the time and plot size to be consistent amongst the two plots. 

    @param time - list of datetimes
    """
    adjusted_times = []
    for i in range(len(given_time)-1):
        adjusted_times.append(given_time[i])
        fill_time = given_time[i] + datetime.timedelta(minutes=15)
        adjusted_times.append(fill_time)
        while fill_time < given_time[i+1]:
            fill_time = fill_time + datetime.timedelta(minutes=15)
            adjusted_times.append(fill_time)
    return adjusted_times


def fill_missing_levels(levels):
    adjusted_levels = []
    for i in range(len(levels)):
        current_level = float(levels[i])
        adjusted_levels.append(float(current_level))
        try:
            next_level = float(levels[i+1])
        except:
            break
        # compute rate of change per increment
        points = 23 # 24, 15-minute segments in 6 hours. Minus the last point because it it the next point
        rate_of_change = (1/points) * (next_level-current_level)
        # create each fill point
        fill_point = current_level + rate_of_change
        adjusted_levels.append(float(fill_point))
        for j in range(points-1): # create next points except for the last point which is given in the level param
            fill_point = fill_point + rate_of_change
            adjusted_levels.append(float(fill_point))
    return adjusted_levels


def get_flood_data(xml_root, observed_or_forecast):
    xml_elements = xml_root.findall(observed_or_forecast + '/datum')
    levels = []
    time_list = []
    # get parse xml elements with flood data
    for datum in xml_elements:
        date_UTC_str = datum.find('valid').text
        water_level = datum.find('primary').text # in feet
        # below values not currently being put to use
        # flow = datum.find('secondary').text # in kcfs
        # pedts = datum.find('pedts').text
        levels.append(float(water_level))
        dt = convert_str_to_datetime(date_UTC_str)
        time_list.append(dt)
    # format xml data for dash
    if observed_or_forecast == 'observed': #observed data is flipped in xml
        time_list.reverse()
        levels.reverse()
    elif observed_or_forecast == 'forecast': #forecasted data is incremented by 6hours not 15min
        time_list = fill_missing_time(time_list)
        levels = fill_missing_levels(levels)
    else:
        raise ValueError("~Boone~ the get_flood_data method expects the 'observed' or 'forecast'.")
    data = list(zip(time_list, levels))
    return pd.DataFrame(data, columns=['Time', 'Level'])


def get_screen_resolution():
    return {"width": GetSystemMetrics(0), "height": GetSystemMetrics(1)}


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


def convert_utc_est(utc):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    utc = utc.replace(tzinfo=from_zone)
    return utc.astimezone(to_zone).strftime('%b. %d, %Y %I:%M %p')

def get_time():
    time = datetime.datetime.now().strftime('%I:%M')
    if time[0] == '0':
        return time[1:]
    return time

def get_time_postfix():
    return datetime.datetime.now().strftime('%p')

def get_date():
    return datetime.datetime.now().strftime('%x')

def get_climacell_data():
    key = "96Sx5iofKooIKqeBycfPBZfAmOTSnUa1"
    client = ClimacellApiClient(key)
    # 4700 welby turn = (37.558331, -77.639555)
    rt = client.realtime(lat=37.558, lon=-77.639, fields=[
        'temp',
        'feels_like',
        'humidity',
        'wind_speed',
        'wind_gust',
        'baro_pressure',
        'precipitation',
        'precipitation_type',
        # 'precipitation_probability',
        # 'precipitation_accumulation',
        'sunrise',
        'sunset',
        'visibility',
        'cloud_cover',
        'weather_code',
    ])
    rt_data = rt.data()
    rt_measurements = rt_data.measurements

    def convert_to_farhrenheit(temp_c):
        temp_c /= 5
        temp_c *= 9
        temp_c += 32
        return temp_c

    return {
        'obs_time': convert_utc_est(rt_data.observation_time),
        'lat': rt_data.lat,
        'long': rt_data.lon,
        'temp_value': convert_to_farhrenheit(rt_measurements['temp'].value),
        'temp_units': 'F\N{DEGREE SIGN}',
        'feels_like_value': convert_to_farhrenheit(rt_measurements['feels_like'].value),
        'feels_like_units': 'F\N{DEGREE SIGN}',
        'humidity_value': rt_measurements['humidity'].value,
        'humidity_units': rt_measurements['humidity'].units,
        'wind_speed_value': rt_measurements['wind_speed'].value,
        'wind_speed_units': rt_measurements['wind_speed'].units,
        'wind_gust_value': rt_measurements['wind_gust'].value,
        'wind_gust_units': rt_measurements['wind_gust'].units,
        'baro_pressure_value': rt_measurements['baro_pressure'].value,
        'baro_pressure_units': rt_measurements['baro_pressure'].units,
        'precipitation_value': rt_measurements['precipitation'].value,
        'precipitation_units': rt_measurements['precipitation'].units,
        'precipitation_type_value': rt_measurements['precipitation_type'].value,
        'sunrise_value': convert_utc_est(convert_str_to_datetime(rt_measurements['sunrise'].value)),
        'sunset_value': convert_utc_est(convert_str_to_datetime(rt_measurements['sunset'].value)),
        'visibility_value': rt_measurements['visibility'].value,
        'visibility_units': rt_measurements['visibility'].units,
        'cloud_cover_value': rt_measurements['cloud_cover'].value,
        'cloud_cover_units': rt_measurements['cloud_cover'].units,
        'weather_code_value': rt_measurements['weather_code'].value,
    }


if __name__ == "__main__":
    # get dataframes of flood levels
    xml_root = get_xml_root('https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=xml')
    observed_data = get_flood_data(xml_root, 'observed')
    filled_forecast_data = get_flood_data(xml_root, 'forecast')
    bridge_data = bridge_to_fore(observed_data, filled_forecast_data)  