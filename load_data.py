import pandas as pd
import json
import cdsapi
import os
import xarray as xr
import glob


def load_month(variable, y, m, area, path):

    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': variable,
            'year': int(year),
            'month': int(month),
            'day': [
                '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
                '31',
            ],
            'time': [
                '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00',
                '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
                '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00',
                '21:00', '22:00', '23:00'
            ],
            'format': 'netcdf',
            'area': area,
        },
        os.path.join(path, '{0}_{1}-{2}.nc'.format(variable, y, m))
    )


with open('loader_config.json') as json_file:
    cfg_all = json.load(json_file)

regions = cfg_all.keys()

for region in regions:

    cfg = cfg_all[region]
    variables = cfg['variables']

    for var in variables:

        # calculate expected number of hours per month
        # TODO: this is a dumb way, could just use pd.Timestamp.daysinmonth
        hours = pd.date_range(start=str(cfg['start']), end=pd.Timestamp.now(),
                              freq='h')
        hours_str = [t.strftime('%Y-%m') for t in hours]
        expected_counts = pd.Series(hours_str).groupby(hours_str).count()

        # check how many hours per month exist in data
        # TODO: what if no files exist?
        path = os.path.join(cfg['path'], region, var + '*')
        if glob.glob(path):
            ds_disk = xr.open_mfdataset(path)
            existing_times = pd.to_datetime(ds_disk.time.to_series())
            existing_counts = existing_times.groupby(
                [t.strftime('%Y-%m') for t in existing_times]
            ).count().reindex(expected_counts.index).fillna(0)
        else:
            existing_counts = pd.Series(index=expected_counts.index, data=0)

        # figure out the months for which data is incomplete
        incomplete = existing_counts.index[existing_counts < expected_counts]

        years = [s.split('-')[0] for s in incomplete]
        months = [s.split('-')[1] for s in incomplete]

        # load the incomplete months
        for year, month in zip(years, months):
            load_month(var, year, month,
                       cfg['area'], os.path.join(cfg['path'], region))
