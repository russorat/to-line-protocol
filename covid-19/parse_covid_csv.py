#!/usr/bin/env python3

import csv
import requests
import time
import datetime
from datetime import date
import argparse
from contextlib import closing
import codecs
import validators
from influx_line_protocol import Metric

def main(measurement, url, all):
    if all:
        start = start = datetime.datetime.strptime("01-22-2020", "%m-%d-%Y")
        end = datetime.datetime.today()
        date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]

        for my_date in date_generated:
            print_lp(measurement,url.format(my_date.strftime("%d-%m-%Y")))
    else:
       print_lp(measurement,url)

def print_lp(measurement,url):
    with closing(requests.get(url, stream=True)) as r:
        reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'))
        row_count = 0
        for row in reader:
            if row_count == 0:
                row_count+=1
                continue
            else:
                metric = Metric(measurement)
                
                province = (row[0] or "").strip()
                if province:
                    metric.add_value("province", province)
                country = (row[1] or "").strip()
                if country:
                    metric.add_value("country", country)
                metric.with_timestamp(date_to_unix_timestamp((row[2] or "").strip()))
                
                metric.add_value("confirmed", int((row[3] or "0").strip()))
                metric.add_value("deaths", int((row[4] or "0").strip()))
                metric.add_value("recovered", int((row[5] or "0").strip()))
                
                if len(row) > 6:
                    metric.add_value("lat", float((row[6] or "").strip()))
                    metric.add_value("lon", float((row[7] or "").strip()))
                    
                print(metric)
                
def date_to_unix_timestamp(my_date):
    format = "%Y-%m-%dT%H:%M:%S"
    return int(time.mktime(datetime.datetime.strptime(my_date, format).utctimetuple())) * 1000000000

def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()

    # arguments
    parser.add_argument("-l","--latest", action='store_true', help="Grabs the latest csv file based on the current date (default)")
    parser.add_argument("-a","--all", action='store_true', help="Grabs all data from 01-22-2020 to now.")
    parser.add_argument("-m","--measurement", help="Measurement name, defaults to covid", default="covid")
    parser.add_argument("-d","--date", help="Date daily csv data mm-dd-yyyy, for example: 02-03-2020")

    # Print version
    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    # Parse arguments
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    # Parse the arguments
    args = parseArguments()
    covid_csv_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv"
    if args.all:
        main(args.measurement, covid_csv_url, True)
    elif args.date:
        main(args.measurement, covid_csv_url.format(args.date), False)
    else:
        today = date.today()
        d1 = today.strftime("%m-%d-%Y")
        main(args.measurement, covid_csv_url.format(d1), False)