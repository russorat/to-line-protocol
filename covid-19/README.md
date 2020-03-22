This script parses the data files found at in [CSSEGISandData/COVID-19](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports) into line protocol.



```
pipenv run python parse_covid_csv.py -h 
usage: parse_covid_csv.py [-h] [-l] [-a] [-m MEASUREMENT] [-d DATE] [--version]

optional arguments:
  -h, --help            show this help message and exit
  -l, --latest          Grabs the latest csv file based on the current date (default)
  -a, --all             Grabs all data from 01-22-2020 to now.
  -m MEASUREMENT, --measurement MEASUREMENT
                        Measurement name, defaults to covid
  -d DATE, --date DATE  Date daily csv data mm-dd-yyyy, for example: 02-03-2020
  --version             show program's version number and exit
```

Schema:
```
covid
  - tags
      - province
      - country
  - fields
      - confirmed
      - deaths
      - recovered
      - lat
      - lon
```

Example Output:
```
covid,province=Alaska,country=US confirmed=0,deaths=0,recoved=0,lat=61.3707,lon=-152.4044 1583836384000000000
covid,province=Idaho,country=US confirmed=0,deaths=0,recoved=0,lat=44.2405,lon=-114.4788 1583836384000000000
covid,province=Maine,country=US confirmed=0,deaths=0,recoved=0,lat=44.6939,lon=-69.3819 1583836384000000000
covid,province=West\ Virginia,country=US confirmed=0,deaths=0,recoved=0,lat=38.4912,lon=-80.9545 1583836384000000000
covid,country=occupied\ Palestinian\ territory confirmed=0,deaths=0,recoved=0,lat=31.9522,lon=35.2332 1583988782000000000
```

To use this in [Telegraf](https://github.com/influxdata/telegraf), use the exec input something like this:

```
[[inputs.exec]]
  interval = "24h"
  commands = [
    "pipenv run python parse_covid_csv.py"
  ]
  timeout = "9s"
  data_format = "influx"
```

If you are using Telegraf 1.14 or greater, you can also add the s2_cell_id and take advantage of the new
geotemporal functions within Flux.  Add this to your Telegraf config:
```
[[processors.s2geo]]
  ## The name of the lat and lon fields containing WGS-84 latitude and
  ## longitude in decimal degrees.
  lat_field = "lat"
  lon_field = "lon"

  ## New tag to create
  tag_key = "s2_cell_id"

  ## Cell level (see https://s2geometry.io/resources/s2cell_statistics.html)
  cell_level = 20
  ```
  
