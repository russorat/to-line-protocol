This scripts in this folder parse data from github apis into line protocol.

```
pipenv run python parse_github_contribs.py -h                          
usage: parse_github_contribs.py [-h] [-r REPO] [-m MEASUREMENT] [--version]

optional arguments:
  -h, --help            show this help message and exit
  -r REPO, --repo REPO  The org and repo name seperated by a slash (<ORG>/<NAME>).
  -m MEASUREMENT, --measurement MEASUREMENT
                        The measurement to use in the line protocol.
  --version             show program's version number and exit
```

Schema:
```
github_contribs
  - tags
      - author
      - org
      - repo
  - fields
      - additions
      - deletions
      - commits
```

Example Output:
```
github_contribs,author=russorat,org=russorat,repo=to-line-protocol additions=849i,deletions=8i,commits=3i 1583625600000000000
```

To use this in [Telegraf](https://github.com/influxdata/telegraf), use the exec input something like this:

```
[[inputs.exec]]
  interval = "1h"
  commands = [
    "pipenv run python parse_github_contribs.py -r russorat/to-line-protocol"
  ]
  timeout = "30s"
  data_format = "influx"
```