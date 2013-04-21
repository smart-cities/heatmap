heatmap
=======

We're collecting point data in urban locations.

Can we create heat maps from the point data?  Initially this would not take into account city-scape features, it would just be a surface generated from sensor readings.

There won't be enought time to do this properly with "Geostatistical estimation" - http://en.wikipedia.org/wiki/Kriging.

We'll implement a server-side solution in Python that leverages an existing Open Source library

http://jjguy.com/heatmap/  >> http://jjguy.com/heatmap/

* Generate raster layers from point inputs to server as WMS (via TIFF and GeoServer) or as animated gif (via PNG)!

Basic project documentation is at: https://spaceapps.hackpad.com/Smart-Cities-Heat-Maps-YD69KnTMmLL

Dependencies:
http://jjguy.com/heatmap/ (MIT Licence)
