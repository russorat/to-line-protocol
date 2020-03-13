#!/usr/bin/env python3

import requests
import time
import datetime
import argparse
import validators
from xml.etree import ElementTree as ET

def main(measurement, station, url, latest):
    latest_columns =     "wind_dir_degt,wind_speed_mps,gust_speed_mps,significant_wave_height_m,dominant_wave_period_sec,avg_wave_period_sec,wave_dir_degt,sea_level_pressure_hpa,air_temp_degc,sea_surface_temp_degc,dewpoint_temp_degc,station_visibility_nmi,pressure_tendency_hpa,water_level_ft".split(",")
    realtime_columns =   "wind_dir_degt,wind_speed_mps,gust_speed_mps,significant_wave_height_m,dominant_wave_period_sec,avg_wave_period_sec,wave_dir_degt,sea_level_pressure_hpa,air_temp_degc,sea_surface_temp_degc,dewpoint_temp_degc,station_visibility_nmi,water_level_ft".split(",")
    historical_columns = "wind_dir_degt,wind_speed_mps,gust_speed_mps,significant_wave_height_m,dominant_wave_period_sec,avg_wave_period_sec,wave_dir_degt,sea_level_pressure_hpa,air_temp_degc,sea_surface_temp_degc,dewpoint_temp_degc,station_visibility_nmi,pressure_tendency_hpa,water_level_ft".split(",")
    missing_data_list = "MM,999,9999.0,999.0,99.0,99.00".split(",")

    f = requests.get(url)
    metadata_map = pull_station_metadata()
    for line in f.text.splitlines():
        if not is_comment(line):
            values_list = line.split()
            line_protocol_list = []
            if latest:
                station_id = values_list.pop(0)
                lat = float(values_list.pop(0))
                lon = float(values_list.pop(0))
                tags = []
                for key,value in metadata_map[station_id.lower()].items():
                    if key == 'id':
                        key = 'station_id'
                    value = value.replace(',','\,').replace(' ','\ ').replace('=','\=')
                    if len(value) > 0:
                        if key in ["lat","lon"]:
                            line_protocol_list.append("{}={}".format(key,value))
                        else:
                            tags.append("{}={}".format(key,value))
            date = "{}-{}-{}T{}:{}+0700".format(values_list.pop(0),values_list.pop(0),values_list.pop(0),values_list.pop(0),values_list.pop(0)) #2006-01-02T15:04
            is_historical = (len(values_list) == 13)
            for i in range(len(values_list)):
                if values_list[i] not in missing_data_list:
                    if latest:
                        line_protocol_list.append("{}={}".format(latest_columns[i],float(values_list[i])))
                    elif is_historical:
                        line_protocol_list.append("{}={}".format(historical_columns[i],float(values_list[i])))
                    else:
                        line_protocol_list.append("{}={}".format(realtime_columns[i],float(values_list[i])))
            if len(line_protocol_list) == 0:
                continue
            if latest:
                print("{},".format(measurement) + ",".join(tags) + " " + ",".join(line_protocol_list) + " {}".format(date_to_unix_timestamp(date)) )
            else:
                print("{},station_id={} ".format(measurement,station) + ",".join(line_protocol_list) + " {}".format(date_to_unix_timestamp(date)))

def date_to_unix_timestamp(my_date):
    format = "%Y-%m-%dT%H:%M%z"
    return str(int(time.mktime(datetime.datetime.strptime(my_date, format).utctimetuple()))) + "000000000"

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
