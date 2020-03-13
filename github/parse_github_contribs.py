#!/usr/bin/env python3

import requests
import time
import datetime
import argparse
import validators
import json
from influx_line_protocol import Metric

def main(repo, measurement):
    f = requests.get("https://api.github.com/repos/{}/stats/contributors".format(repo))
    if f.status_code == 202:
        time.sleep(5)
        main(repo, measurement)
    for record in f.json():
        author = record.get("author","")
        for week in record.get("weeks",[]):
            metric = Metric(measurement)
            metric.add_tag("author",author.get("login",""))
            metric.add_tag("org",repo.split("/")[0])
            metric.add_tag("repo",repo.split("/")[1])

            metric.add_value("additions",int(week.get("a")))
            metric.add_value("deletions",int(week.get("d")))
            metric.add_value("commits",int(week.get("c")))

            metric.with_timestamp(week.get("w") * 1000000000)
            print(metric)

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-r","--repo", help="The org and repo name seperated by a slash (<ORG>/<NAME>).")
    parser.add_argument("-m","--measurement", help="The measurement to use in the line protocol.", default="github_contribs")

    parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parseArguments()

    run = True
    if not args.repo:
        print("Please add the org and repo name seperated by a slash (<ORG>/<NAME>).")
        run = False
    if run:
        main(args.repo, args.measurement)