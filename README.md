# Virual Computing

Interactive photograph displaying system

# How to use

1. Run pixel.html to see "Automatic Arrangement" and "Photo Focusing" functions.
* click photo after the animation stops, probably 10 ~ 12 seconds.
* If the distance method is switched, the current layout will not automatically change.
2. Run geo.html to see "Geo-location based placing" function.


# Python scripts
1. info.py `base_dir` is the folder which contains the photos, run this py file to read exif information from photos and generates smaller images files with reduced resolution, and a csv file which will be used in html application.
2. main.py change `dir` to the folder which contains the photos, run this py file to calculate cos and histogram similarity matrix.
3. image_similarity.py called by `main.py`
