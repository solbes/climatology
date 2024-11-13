"""Script for starting weather data Flask server

"""

import argparse
import json
import logging
import os
import requests

import flask
from flask import request, jsonify
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr


def in_area(lat, lon, area):
    return (lat > area[2]) and (lat < area[0]) and (lon > area[1]) and \
           (lon < area[3])


def region_from_coords(lat, lon, confs):
    areas = {reg: config['area'] for reg, config in confs.items()}
    ok_areas = dict(filter(
        lambda items: in_area(lat, lon, items[1]),
        areas.items()
    ))
    return list(ok_areas.keys())[0]


def round_to_base(x, prec=2, base=.25):
    return round(base * round(float(x)/base), prec)


def create_app(configs):

    # open all data files
    ds_disks = {key: {} for key in configs}
    for (region, config) in configs.items():
        for var in config['variables']:
            glob_path = os.path.join(config['path'], region, var + '*.nc')
            print(glob_path)
            ds_disks[region][var] = xr.open_mfdataset(glob_path)

    app = flask.Flask(__name__)
    app.config["DEBUG"] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    @app.route('/', methods=['GET'])
    def home():

        mon = pd.Timestamp.now().month
        day = pd.Timestamp.now().day

        req = 'http://127.0.0.1:5000/api/by_day?variable' \
            '=2m_temperature&lat=61.75&lon=22.5' \
            '&month={0}&day={1}&start=2016'.format(mon, day)

        res = requests.get(req)

        ds = pd.DataFrame(json.loads(res.content))
        ds = ds.set_index(pd.to_datetime(ds.time)).drop(columns='time')-273.15

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

    @app.route('/api/by_range', methods=['GET'])
    def api_by_range():

        lat = float(request.args['lat'])
        lon = float(request.args['lon'])
        variable = request.args['variable']

        # figure out the region to use
        ok_region = region_from_coords(lat, lon, configs)
        if not ok_region:
            return "No suitable area found with given lat-lon."

        ds_disk = ds_disks[ok_region][variable]

        start = request.args['start'] if 'start' in request.args else '2020'
        end = request.args['end'] if 'end' in request.args else pd.Timestamp.now()

        # here we add support for location interpolation
        # * method='nearest': Select the nearest data point
        # * method='pad': Select the data point with the closest coordinate that is 
        #                 less than or equal to the target coordinate
        # * method='backfill': Select the data point with the closest coordinate that is 
        #                 greater than or equal to the target coordinate
        temp_series = ds_disk.sel(
            valid_time=slice(start, end),
            longitude=lon,
            latitude=lat,
            method='nearest'
        )

        # in some files you get a nasty extra dimension 'expver' in addition to
        # time, see some discussion here:
        # https://confluence.ecmwf.int/pages/viewpage.action?pageId=173385064
        # this is a workaround to drop the extra dimension
        if 'expver' in list(temp_series.indexes.keys()):
            temp_series = temp_series.reduce(np.nansum, 'expver')

        # drop lat and lon --> you have a dataframe with just one variable
        temp_series = temp_series.to_dataframe().drop(columns=['latitude', 'longitude'])

        out = {'time': list(temp_series.index.astype(str)),
            'temperature': list(temp_series.values[:, 0].astype(float))}

        return jsonify(out)

    @app.route('/api/by_day', methods=['GET'])
    def api_temperature_day():

        print(request.args)

        lat = float(request.args['lat'])
        lon = float(request.args['lon'])        
        mon = int(request.args['month'])
        day = int(request.args['day'])
        variable = request.args['variable']

        # figure out the region to use
        ok_region = region_from_coords(lat, lon, configs)
        if not ok_region:
            return "No suitable area found with given lat-lon."

        ds_disk = ds_disks[ok_region][variable]

        start = int(request.args['start']) if 'start' in request.args else 1979
        end = int(request.args['end']) if 'end' in request.args else \
            pd.Timestamp.now().year

        time = ds_disk.time.to_dataframe().index

        ii_mon = time.month == mon
        ii_day = time.day == day
        ii_year = (time.year >= start) & (time.year <= end)

        # same as line 101, we add support for location interpolation
        temp_series = ds_disk.sel(
            valid_time=(ii_mon & ii_day & ii_year), 
            longitude=lon, 
            latitude=lat,
            method='nearest'
        )

        # in some files you get a nasty extra dimension 'expver' in addition to
        # time, see some discussion here:
        # https://confluence.ecmwf.int/pages/viewpage.action?pageId=173385064
        # this is a workaround to drop the extra dimension
        if 'expver' in list(temp_series.indexes.keys()):
            temp_series = temp_series.reduce(np.nansum, 'expver')

        temp_series = temp_series.to_dataframe().drop(
            columns=['latitude', 'longitude'])

        out = {'time': list(temp_series.index.astype(str)),
            'temperature': list(temp_series.values[:, 0].astype(float))}

        return jsonify(out)

    # No caching at all for API endpoints.
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'public, max-age=0'
        return response

    return app


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Data loader arguments")
    parser.add_argument('-c', '--configs-file', help='path to configuration JSON file')
    args = parser.parse_args()

    # load configurations
    with open(args.configs_file) as f:
        configs = json.load(f)

    app = create_app(configs)

    # -- Run server -- #
    app.run()  #########
    # -----------------#
