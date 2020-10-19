from urllib.request import urlopen
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
from win32api import GetSystemMetrics


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


def fill_missing_time(time):
    """ Adds filler points to the forecast plot to account for the data being
    in 6 hour intervals instead of 15 minute intrevals like the observed plot.
    Allows the time and plot size to be consistent amongst the two plots. 

    @param time - list of datetimes
    """
    adjusted_time = []
    for sixhr_interval in time:
        adjusted_time.append(sixhr_interval)
        fill_interval = sixhr_interval + datetime.timedelta(minutes=15)
        adjusted_time.append(fill_interval)
        for i in range(23):
            fill_interval = fill_interval + datetime.timedelta(minutes=15)
            adjusted_time.append(fill_interval)
    return adjusted_time



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

if __name__ == "__main__":
    # get dataframes of flood levels
    xml_root = get_xml_root('https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=xml')
    observed_data = get_flood_data(xml_root, 'observed')
    filled_forecast_data = get_flood_data(xml_root, 'forecast')
    bridge_data = bridge_obs_to_fore(observed_data, filled_forecast_data)

    print(observed_data, result, filled_forecast_data)