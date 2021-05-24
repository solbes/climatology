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
url: https://cds.climate.copernicus.eu/api/v2
key: SECRET-KEY-OBTAINED-FROM-
```

### Clone git repository

``` bash
git clone git@github.com:solbes/climatology.git
```

### Create directory for climatology data

```bash
mkdir ~/.climatology/europe
```


### Create your data loader config file 

For example `~/climatology_config.json`:

```json
{
  "europe": {
    "variables": ["2m_temperature", "surface_net_solar_radiation"],
    "area": [73.0, -15.0, 30.0, 45.0],
    "start": 2018,
    "path": "/home/foobar/.climatology/europe"
  },
  "beijing": {
    "variables": ["2m_temperature", "surface_net_solar_radiation"],
    "area": [45.0, 120.0, 35.0, 110.0],
    "start": 2018,
    "path": "/home/foobar/.climatology/beijing"
  }
}
```

**NOTE** The values of the `area` property define the lat/lon grid where data is
queried to. The list is of form `[North, West, South, East]` where `West/East` is between -180...180 and `North/South` between -90...90.

### Install virtual environment using Conda

``` bash
# Use your local conda, e.g. ~/miniconda/bin/conda
~/miniconda/bin/conda env create --force --name climatology --file environment.yml
source ~/miniconda/bin/activate climatology
```

### Start data loader
```bash
python load_data.py --configs-file /path/to/climatology_config.json
```

### Start local historical weather service

``` bash
python api.py --configs-file /path/to/climatology_config.json
```

### Test query

``` bash
curl http://127.0.0.1:5000/api/by_range?variable=2m_temperature&lat=62.0&lon=22.5&start=2021-01-01
```

## API spec

TODO

## Examples

TODO


