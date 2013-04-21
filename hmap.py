#!/usr/bin/env python
import cgi
import numpy as np
import os
from osgeo import gdal
import pyproj
import random
import uuid
import heatmap

domain = 'http://smartcities.switchsystems.co.uk/cgi-bin/'
src_proj = pyproj.Proj(init='epsg:4326')
dest_proj = pyproj.Proj(init='epsg:900913')
img_folder = "img/"

'''
  Note:
  
  The png outputs can be used to create an animation through time using something like:
  convert -delay 100 -loop 0 -background black +matte *.png animation.gif
'''


def write_pts(pts):
  # get sensor ids - used for dev only
  sensor_ids = []
  with open('../../Readings.csv','r') as kml:
    for line in kml:
      content = line.split('"')
      sensor_ids.append(content[3])
      
  with open('rnd.csv','w') as csv_fh:
    # csv_fh.write("id,lat,lng\n") # insert manually in phpmyadmin
    fb = '";"' # field break (between fields and empty fields)
    for line_num in range(len(pts)):
      csv_fh.write('"'+sensor_ids[line_num]+fb*6+'BUCL_exeter'+fb+str(pts[line_num][1])+fb+str(pts[line_num][0])+fb*3+'"\n')


def extract_tag_value(direction, line):
  tag_start = line.find('<' + direction + '>')
  tag_end = line.find('</' + direction + '>')
  return float(line[tag_start+len(direction)+2:tag_end])


def export_geotiff(payload, fname, x_min, x_max, y_min, y_max):

    x_step = (x_max - x_min) / payload.shape[1]
    y_step = (y_max - y_min) / payload.shape[0]

    # hack: -y_step seems to work...
    padf_transform = (x_min, x_step, 0.0, y_max, 0.0, -y_step)

    #    # Flip the data so North is at the top
    #    data = data[::-1, :]

    driver = gdal.GetDriverByName('GTiff')
    data = driver.Create(fname, payload.shape[1], payload.shape[0],
                         3, gdal.GDT_Float32)

    data.SetGeoTransform(padf_transform)
    MDI = [53, 52, 61]
    for band_num in range(3):
      # ignore alpha band
      band = data.GetRasterBand(band_num + 1)
      band.WriteArray(payload[:,:,band_num])
      band.SetNoDataValue(MDI[band_num])


hm = heatmap.Heatmap()
pts = [(random.uniform(-3.5340, -3.5170), random.uniform(50.7212, 50.7290)) for x in range(21)]
##write_pts(pts)

for i in range(len(pts)):
  pts[i] = pyproj.transform(src_proj, dest_proj, pts[i][0], pts[i][1])

hm.heatmap(pts)

uid = str(uuid.uuid4())
uid = 'fixed_uid'

kml_fname = img_folder + uid + ".kml"
hm.saveKML(kml_fname)

nsew_vals = {'n': None, 's': None, 'e': None, 'w': None}

# Extract bbox from kml file
with open(kml_fname,'r') as kml:
  for line in kml:
    nsew = {'north': line.find('<north>'),
            'south': line.find('<south>'),
	    'east': line.find('<east>'),
	    'west': line.find('<west>')}

    if nsew['north'] > 0:
      nsew_vals['n'] = extract_tag_value('north', line)
    elif nsew['south'] > 0:
      nsew_vals['s'] = extract_tag_value('south', line)
    elif nsew['east'] > 0:
      nsew_vals['e'] = extract_tag_value('east', line)
    elif nsew['west'] > 0:
      nsew_vals['w'] = extract_tag_value('west', line)

x_step = hm.img.getbbox()[2]
y_step = hm.img.getbbox()[3]
x_min = nsew_vals['w']
x_max = nsew_vals['e']
y_min = nsew_vals['s']
y_max = nsew_vals['n']
data = np.array(hm.img.getdata())
data = data.reshape(1024,1024,4)
tif_fname = img_folder + uid + ".tif"
export_geotiff(data, tif_fname, x_min, x_max, y_min, y_max)
	    
#os.remove(kml_fname)


