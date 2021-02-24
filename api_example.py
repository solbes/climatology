import flask
from flask import request, jsonify
import logging
import pandas as pd
import xarray as xr
import requests
import json
import matplotlib.pyplot as plt

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

ds_disk = xr.open_mfdataset('./data/2m_temperature*.nc')


@app.route('/', methods=['GET'])
def home():

    mon = pd.Timestamp.now().month
    day = pd.Timestamp.now().day

    req = 'http://127.0.0.1:5000/api/by_day/temperature?lat=61.75&lon=22.5' \
          '&month={0}&day={1}&start=2016'.format(mon, day)

    res = requests.get(req)

    ds = pd.DataFrame(json.loads(res.content))
    ds = ds.set_index(pd.to_datetime(ds.time)).drop(columns='time')

    plt.figure()
    plt.scatter(ds.index.hour, ds.temperature, c=ds.index.year, s=10)
    plt.xlabel('hour')
    plt.ylabel('2m temperature [C]')
    plt.title('Todays temperature in Kankaanpää, color=year since 2016')
    plt.grid(True)
    plt.savefig('./static/home_fig.png', dpi=200)

    return "<h1>Climatology API</h1>" \
           "<p>This site is a prototype API for historical weather data.</p>" \
           "<figure><img src='/static/home_fig.png' style='width:40%'></figure>"


@app.route('/api/by_range/temperature', methods=['GET'])
def api_temperature():

    lat = float(request.args['lat'])
    lon = float(request.args['lon'])

    start = request.args['start'] if 'start' in request.args else '2020'
    end = request.args['end'] if 'end' in request.args else pd.Timestamp.now()

    temp_series = ds_disk.sel(
        time=slice(start, end),
        longitude=lon,
        latitude=lat
    ).to_dataframe()['t2m']-273.15

    out = {'time': list(temp_series.index.astype(str)),
           'temperature': list(temp_series)}

    return jsonify(out)


@app.route('/api/by_day/temperature', methods=['GET'])
def api_temperature_day():

    print(request.args)

    lat = float(request.args['lat'])
    lon = float(request.args['lon'])
    mon = int(request.args['month'])
    day = int(request.args['day'])

    start = int(request.args['start']) if 'start' in request.args else 1979
    end = int(request.args['end']) if 'end' in request.args else \
        pd.Timestamp.now().year

    time = ds_disk.time.to_dataframe().index

    ii_mon = time.month == mon
    ii_day = time.day == day
    ii_year = (time.year >= start) & (time.year <= end)

    temp_series = ds_disk.sel(
        time=(ii_mon & ii_day & ii_year), longitude=lon, latitude=lat,
    ).to_dataframe()['t2m']-273.15

    out = {'time': list(temp_series.index.astype(str)),
           'temperature': list(temp_series)}

    return jsonify(out)


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


app.run()
