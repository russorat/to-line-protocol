This script parses the data from https://www.ndbc.noaa.gov into line protocol.

```
pipenv run python parse_noaa.py -h      
usage: parse_noaa.py [-h] [-l] [-m MEASUREMENT] [-s STATION] [-u URL] [--version]

optional arguments:
  -h, --help            show this help message and exit
  -l, --latest          Grabs the latest measurements from https://www.ndbc.noaa.gov/data/latest_obs/latest_obs.txt
  -m MEASUREMENT, --measurement MEASUREMENT
                        Measurement name, defaults to noaa
  -s STATION, --station STATION
                        Station name, stored in station tag, for example: ftpc1
  -u URL, --url URL     Url to station data, for example: https://www.ndbc.noaa.gov/data/realtime2/FTPC1.txt
  --version             show program's version number and exit
```

Schema:
```
ndbc
  - tags
      - station_id
      - elev
      - name
      - owner
      - pgm
      - type
      - met
      - currents
      - waterquality
      - dart
  - fields
      - lat
      - lon
      - wind_dir_degt
      - wind_speed_mps
      - gust_speed_mps
      - sea_level_pressure_hpa
      - sea_surface_temp_degc
      - air_temp_degc
      - dewpoint_temp_degc
      - water_level_ft
```

Example Output:
```
ndbc,station_id=wrbf1,elev=0,name=Whipray\ Basin\,\ FL,owner=Everglades\ National\ Park,pgm=IOOS\ Partners,type=fixed,met=y,currents=n,waterquality=y,dart=n lat=25.072,lon=-80.735,wind_dir_degt=40.0,wind_speed_mps=4.1,dewpoint_temp_degc=27.1,water_level_ft=-0.46 1584068400000000000
ndbc,station_id=wycm6,elev=0,name=8747437\ -\ Bay\ Waveland\ Yacht\ Club\,\ MS,owner=NOS,pgm=NOS/CO-OPS,type=fixed,met=y,currents=n,waterquality=n,dart=n lat=30.326,lon=-89.326,wind_dir_degt=200.0,wind_speed_mps=3.1,gust_speed_mps=4.1,sea_level_pressure_hpa=1017.2,sea_surface_temp_degc=21.3,dewpoint_temp_degc=21.3 1584075240000000000
ndbc,station_id=yata2,elev=6.6,name=9453220\ -\ Yakutat\,\ Yakutat\ Bay\,\ AK,owner=NOS,pgm=NOS/CO-OPS,type=fixed,met=y,currents=n,waterquality=n,dart=n lat=59.548,lon=-139.733,sea_level_pressure_hpa=1042.3,air_temp_degc=2.3,dewpoint_temp_degc=4.5 1584075600000000000
ndbc,station_id=ykrv2,name=8637611\ -\ York\ River\ East\ Rear\ Range\ Light\,\ VA,owner=NOS,pgm=NOS/CO-OPS,type=fixed,met=y,currents=n,waterquality=n,dart=n lat=37.251,lon=-76.342,wind_dir_degt=160.0,wind_speed_mps=4.1,gust_speed_mps=4.1,sea_level_pressure_hpa=1015.7,air_temp_degc=-0.8,sea_surface_temp_degc=10.1 1584075600000000000
ndbc,station_id=yktv2,elev=3.7,name=8637689\ -\ Yorktown\ USCG\ Training\ Center\,\ VA,owner=NOS,pgm=NOS/CO-OPS,type=fixed,met=y,currents=n,waterquality=n,dart=n lat=37.227,lon=-76.479,wind_dir_degt=140.0,wind_speed_mps=1.5,gust_speed_mps=2.1,sea_level_pressure_hpa=1014.5,air_temp_degc=-0.9,sea_surface_temp_degc=11.3,dewpoint_temp_degc=10.3 1584075600000000000
ndbc,station_id=yrsv2,elev=11,name=Taskinas\ Creek\,\ Chesapeake\ Bay\ Reserve\,\ VA,owner=National\ Estuarine\ Research\ Reserve\ System,pgm=NERRS,type=fixed,met=y,currents=n,waterquality=n,dart=n lat=37.414,lon=-76.712,wind_dir_degt=150.0,wind_speed_mps=1.0,sea_level_pressure_hpa=1016.0,sea_surface_temp_degc=11.2,station_visibility_nmi=10.0 1584073800000000000
```

To use this in [Telegraf](https://github.com/influxdata/telegraf), use the exec input something like this:

```
[[inputs.exec]]
  interval = "5m"
  commands = [
    "pipenv run python parse_noaa.py --latest"
  ]
  timeout = "9s"
  data_format = "influx"
```