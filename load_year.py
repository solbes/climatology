#!/usr/bin/env python
import cdsapi

c = cdsapi.Client()

years = ['1999']
#years = [str(1979 + i) for i in range(20)]
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10','11','12']
#months = ['05', '06', '07', '08', '09', '10','11','12']

variables = ['2m_temperature']

for variable in variables:
  for year in years:
    for month in months:

      c.retrieve(
      'reanalysis-era5-single-levels',
      {
          'product_type': 'reanalysis',
          'variable': variable,
          'year': year,
          'month': month,
          'day': [
              '01', '02', '03',
              '04', '05', '06',
              '07', '08', '09',
              '10', '11', '12',
              '13', '14', '15',
              '16', '17', '18',
              '19', '20', '21',
              '22', '23', '24',
              '25', '26', '27',
              '28', '29', '30',
              '31',
          ],
          'time': [
              '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00',
              '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00',
              '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00',
              '21:00', '22:00', '23:00'
          ],
          'format': 'netcdf',
          'area': [
              71.5, -10.5, 33.5, 35,
          ],
      },
      './data/{0}_{1}_{2}.nc'.format(variable, year, month)
      )
      