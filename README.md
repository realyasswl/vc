# Virual Computing

Dynamic display system

# How to use

* First of all, you need to have a running http server, `nginx` or `apache httpd`, and put all files in right place. If you run into any problem in this step, please contact us at any time. Due to local static file restriction this html application cannot run directly with only browsers.
* Run `pixel.html` to see "Automatic Arrangement" function.
* Click photo after the animation stops to see "Photo Focusing", animation probably lasts for 10 ~ 12 seconds.
* If the distance method is switched, the current layout will not automatically change.
* Run `geo.html` to see "Geo-location based placing" function.


# Python scripts
0. Python scripts are used to initialize new photo sets, once set up, the application is fully functional without these python scripts.
1. info.py `base_dir` is the folder which contains the photos, run this py file to read exif information from photos and generates smaller images files with reduced resolution, and a csv file which will be used in html application.
2. main.py change `dir` to the folder which contains the photos, run this py file to calculate cos and histogram similarity matrix.
3. image_similarity.py called by `main.py`
