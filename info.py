__author__ = 'liwang'
import os
import datetime as dt
from collections import OrderedDict
from glob import glob
from sys import argv

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    info = image._getexif()
    if not info:
        return {}
    exif_data = {TAGS.get(tag, tag): value for tag, value in info.items()}

    def is_fraction(val):
        return isinstance(val, tuple) and len(val) == 2 and isinstance(val[0], int) and isinstance(val[1], int)

    def frac_to_dec(frac):
        return float(frac[0]) / float(frac[1])

    if "GPSInfo" in exif_data:
        gpsinfo = {GPSTAGS.get(t, t): v for t, v in exif_data["GPSInfo"].items()}
        for tag, value in gpsinfo.items():
            if is_fraction(value):
                gpsinfo[tag] = frac_to_dec(value)
            elif all(is_fraction(x) for x in value):
                gpsinfo[tag] = tuple(map(frac_to_dec, value))
        exif_data["GPSInfo"] = gpsinfo
    return exif_data


def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data"""
    lat = None
    lon = None
    gps_info = exif_data.get("GPSInfo")

    def convert_to_degrees(value):
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    if gps_info:
        gps_latitude = gps_info.get("GPSLatitude")
        gps_latitude_ref = gps_info.get("GPSLatitudeRef")
        gps_longitude = gps_info.get("GPSLongitude")
        gps_longitude_ref = gps_info.get("GPSLongitudeRef")

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                lat = -lat

            lon = convert_to_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                lon = -lon

    return lat, lon


def get_gps_datetime(exif_data):
    """Returns the timestamp, if available, from the provided exif_data"""
    if "GPSInfo" not in exif_data:
        return None
    gps_info = exif_data["GPSInfo"]
    date_str = gps_info.get("GPSDateStamp")
    time = gps_info.get("GPSTimeStamp")
    if not date_str or not time:
        return None
    date = map(int, date_str.split(":"))
    timestamp = [*date, *map(int, time)]
    timestamp += [int((time[2] % 1) * 1e6)]  # microseconds
    return dt.datetime(*timestamp)


def clean_gps_info(exif_data):
    """Return GPS EXIF info in a more convenient format from the provided exif_data"""
    try:
        gps_info = exif_data["GPSInfo"]
        cleaned = OrderedDict()
        cleaned["Latitude"], cleaned["Longitude"] = get_lat_lon(exif_data)
        cleaned["Altitude"] = gps_info.get("GPSAltitude")
        cleaned["Speed"] = gps_info.get("GPSSpeed")
        cleaned["SpeedRef"] = gps_info.get("GPSSpeedRef")
        cleaned["Track"] = gps_info.get("GPSTrack")
        cleaned["TrackRef"] = gps_info.get("GPSTrackRef")
        cleaned["TimeStamp"] = get_gps_datetime(exif_data)
    except KeyError:
        cleaned = OrderedDict()
        cleaned["Latitude"], cleaned["Longitude"] = "None","None"
        cleaned["Altitude"] = "None"
        cleaned["Speed"] = "None"
        cleaned["SpeedRef"] = "None"
        cleaned["Track"] = "None"
        cleaned["TrackRef"] = "None"
        cleaned["TimeStamp"] = "None"
    return cleaned


def print_info(dir):
    separator = ","
    tar_separator = "|"
    exif_key_list = ["DateTime", "ExifImageHeight", "ExifImageWidth"]
    gps_key_list = ["Latitude", "Longitude", "Altitude"]
    pic_list = [x for x in os.listdir(dir) if x != "info.csv"]
    f = open(dir+"info.csv", "w")
    print("FileName" + separator + separator.join(exif_key_list) + separator + separator.join(gps_key_list))
    f.write("FileName" + separator + separator.join(exif_key_list) + separator + separator.join(gps_key_list))
    f.write("\n")
    for l in range(len(pic_list)):
        with Image.open(dir + pic_list[l]) as image:
            exif_data = get_exif_data(image)
            gps_info = []
            gps_info = clean_gps_info(exif_data)

            line = [pic_list[l]]

            for i in exif_key_list:
                line.append(separator)
                try:
                    line.append(str(exif_data[i]))
                except KeyError:
                    if i=="ExifImageHeight":
                        try:
                            line.append(str(exif_data["ImageHeight"]))
                        except KeyError:
                            print("KeyError")
                    if i=="ExifImageWidth":
                        try:
                            line.append(str(exif_data["ImageWidth"]))
                        except KeyError:
                            print("KeyError")

            for i in gps_key_list:
                line.append(separator)
                line.append(gps_info[i])
            line=["None" if x is None else str(x) for x in line]
            try:
                print("".join(line))
            except TypeError:
                print("TypeError", line)
            f.write("".join(line))
            f.write("\n")
    f.close()


base_dir = "/run/media/liwang/Other/photos/photodir/"
if __name__ == "__main__":
    print_info(base_dir)
