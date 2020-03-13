#!/usr/bin/env python3

import requests
import time
import datetime
import argparse
import validators
from xml.etree import ElementTree as ET
from influx_line_protocol import Metric

def main(measurement, station, url, latest):
    default_columns   =  "wind_dir_degt,wind_speed_mps,gust_speed_mps,significant_wave_height_m,dominant_wave_period_sec,avg_wave_period_sec,wave_dir_degt,sea_level_pressure_hpa,air_temp_degc,sea_surface_temp_degc,dewpoint_temp_degc,station_visibility_nmi,pressure_tendency_hpa,water_level_ft".split(",")
    realtime_columns  =  "wind_dir_degt,wind_speed_mps,gust_speed_mps,significant_wave_height_m,dominant_wave_period_sec,avg_wave_period_sec,wave_dir_degt,sea_level_pressure_hpa,air_temp_degc,sea_surface_temp_degc,dewpoint_temp_degc,station_visibility_nmi,water_level_ft".split(",")
    missing_data_list =  "MM,999,9999.0,999.0,99.0,99.00".split(",")

    f = requests.get(url)
    metadata_map = pull_station_metadata()
    for line in f.text.splitlines():
        if not is_comment(line):
            metric = Metric(measurement)
            values_list = line.split()
            if latest:
                station_id = values_list.pop(0)
                values_list.pop(0) # lat
                values_list.pop(0) # lon
                for key,value in metadata_map[station_id.lower()].items():
                    if key == 'id':
                        key = 'station_id'
                    if len(value) > 0:
                        if key in ["lat","lon"]:
                            metric.add_value(key,float(value))
                        else:
                            metric.add_tag(key,value)
            date = "{}-{}-{}T{}:{}+0700".format(values_list.pop(0),values_list.pop(0),values_list.pop(0),values_list.pop(0),values_list.pop(0)) #2006-01-02T15:04
            metric.with_timestamp(date_to_unix_timestamp(date))
            is_historical = (len(values_list) == 13)
            for i in range(len(values_list)):
                if values_list[i] not in missing_data_list:
                    if latest or is_historical:
                        metric.add_value(default_columns[i],float(values_list[i]))
                    else:
                        metric.add_value(realtime_columns[i],float(values_list[i]))
            if station:
                metric.add_tag("station_id",station)
            print(metric)

def date_to_unix_timestamp(my_date):
    format = "%Y-%m-%dT%H:%M%z"
    return int(time.mktime(datetime.datetime.strptime(my_date, format).utctimetuple())) * 1000000000

def is_comment(line):
    return line.startswith("#") or line.startswith("YYYY")

def pull_station_metadata():
    metadata_url = "https://www.ndbc.noaa.gov/activestations.xml"
    f = requests.get(metadata_url)

    tree = ET.fromstring(f.text)
    results_map = {}
    for s in tree.findall('.//station'):
        #<station id="00922" lat="30" lon="-90" name="OTN201 - 4800922" owner="Dalhousie University" pgm="IOOS Partners"
        # type="other" met="n" currents="n" waterquality="n" dart="n" />
        results_map[s.attrib['id']] = s.attrib

    return results_map

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-l","--latest", action='store_true', help="Grabs the latest measurements from https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt")
    parser.add_argument("-m","--measurement", help="Measurement name, defaults to noaa", default="ndbc")
    parser.add_argument("-s","--station", help="Station name, stored in station tag, for example: ftpc1")
    parser.add_argument("-u","--url", help="Url to station data, for example: https://www.ndbc.noaa.gov/data/realtime2/FTPC1.txt")

    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parseArguments()

    if args.latest:
        main(args.measurement, "", "https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt", True)
    else:
        run = True
        if not args.station:
            print("Please add a station id")
            run = False
        if not args.url or not validators.url(args.url):
            print("Invalid url: {}".format(args.url))
            run = False
        if run:
            main(args.measurement, args.station, args.url, False)
