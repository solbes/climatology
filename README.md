# Global historical climatology data API

Download and utilize historical weather data (temperature, solar radiation, wind, rain, ...) for any global geolocation as hourly time-series data.

Based on [Copernicus Climate Data Store](https://cds.climate.copernicus.eu) service. This project provides tools for

- Querying and caching locally a dataset from the archive
- Running a HTTP api in localhost for utilizing e.g. location specific weather histories

## Setting up

### Create account in the Copernicus service
This is needed so that the loader can query data. You need to create a
configuration file `~/.cdsapirc`:

``` text
url: https://cds.climate.copernicus.eu/api
key: SECRET-KEY-OBTAINED-FROM-WEBSITE
```

### Clone git repository

``` bash
git clone git@github.com:solbes/climatology.git
```

### Create directory for climatology data

```bash
mkdir ~/.climatology/europe
mkdir ~/.climatology/beijing
```


### Create your data loader config file 

For example `~/.climatology/configs.json`:

```json
{
  "europe": {
    "variables": ["2m_temperature", "surface_net_solar_radiation"],
    "area": [73.0, -15.0, 30.0, 45.0],
    "start": 2018,
    "path": "/home/foobar/.climatology"
  },
  "beijing": {
    "variables": ["2m_temperature", "surface_net_solar_radiation"],
    "area": [45.0, 120.0, 35.0, 110.0],
    "start": 2018,
    "path": "/home/foobar/.climatology"
  }
}
```

**NOTE** The values of the `area` property define the lat/lon grid where data is
queried to. The list is of form `[North, West, South, East]` where `West/East` is between -180...180 and `North/South` between -90...90.

### Install virtual environment and activate it

``` bash
python -m venv /PATH/TO/VENVS/climatology
source /PATH/TO/VENVS/bin/activate
```
### Install the package ###

``` bash
cd /PATH/TO/ROOT/FOLDER
pip install --editable .
```

### Start data loader
```bash
python load_data.py --configs-file ~/.climatology/configs.json
```

### Start local historical weather service

``` bash
python api.py --configs-file ~/.climatology/configs.json
```

or, alternatively using the Flask CLI:

``` bash
flask --app 'api:create_app(configs_file="/home/foo/bar/cfg.json")' run --port 5555 --host 127.0.0.2
```

In the latter case all Flask's arguments can be utilized.

### Test query

``` bash
# NOTE: Make sure your geographical region contains the lat/lon coordinates
curl http://127.0.0.1:5000/api/by_range?variable=2m_temperature&lat=62.0&lon=22.5&start=2021-01-01
```

## API spec

TODO

## Examples

TODO


