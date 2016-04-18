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

    try:
        info = image._getexif()
    except AttributeError:
        return {}
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
        cleaned["Latitude"], cleaned["Longitude"] = "None", "None"
        cleaned["Altitude"] = "None"
        cleaned["Speed"] = "None"
        cleaned["SpeedRef"] = "None"
        cleaned["Track"] = "None"
        cleaned["TrackRef"] = "None"
        cleaned["TimeStamp"] = "None"
    return cleaned


def print_and_reduce(dir, aw):
    separator = ","
    prefix = "GED"
    tar_separator = "|"
    exif_key_list = ["DateTime", "ExifImageHeight", "ExifImageWidth", "Orientation"]
    gps_key_list = ["Latitude", "Longitude", "Altitude"]
    pic_list = [x for x in os.listdir(dir) if x != "info.csv" and not x.startswith(prefix)]
    f = open(dir + "info.csv", "w")
    print("FileName" + separator + separator.join(exif_key_list) + separator + separator.join(gps_key_list))
    f.write("FileName" + separator + separator.join(exif_key_list) + separator + separator.join(gps_key_list))
    f.write("\n")
    for l in range(len(pic_list)):
        with Image.open(dir + pic_list[l]) as image:
            exif_data = get_exif_data(image)
            gps_info = []
            gps_info = clean_gps_info(exif_data)
            # do resolution reduce

            new_name = "{1}{0:04d}{2}".format(l, prefix, pic_list[l][pic_list[l].rindex("."):])
            line = [new_name]
            siz = image.size
            w = siz[0]
            h = siz[1]
            print(siz)

            nw = aw
            nh = aw / w * h;
            # nw=image.size[0]*factor
            # nh=image.size[1]*factor
            # image.save(new_name, dpi=(nw, nh))
            for i in exif_key_list:
                line.append(separator)

                try:
                    if i == "ExifImageHeight":
                        # nh = factor * exif_data[i]
                        line.append(str(nh))
                    elif i == "ExifImageWidth":
                        # nw = factor * exif_data[i]
                        line.append(str(nw))
                    else:
                        line.append(str(exif_data[i]))
                except KeyError:
                    if i == "ExifImageHeight":
                        try:
                            # line.append(str(factor * exif_data["ImageHeight"]))
                            # nh = factor * exif_data["ImageHeight"]
                            # nh = factor * h
                            line.append(str(nh))
                        except KeyError:
                            print("KeyError")
                    if i == "ExifImageWidth":
                        try:
                            # line.append(str(factor * exif_data["ImageWidth"]))
                            # nw = factor * exif_data["ImageWidth"]
                            # nw = factor * w
                            line.append(str(nw))
                        except KeyError:
                            print("KeyError")

            for i in gps_key_list:
                line.append(separator)
                line.append(gps_info[i])
            line = ["None" if x is None else str(x) for x in line]
            try:
                print("".join(line))
            except TypeError:
                print("TypeError", line)
            f.write("".join(line))
            f.write("\n")
    f.close()

    for l in range(len(pic_list)):
        im = Image.open(dir + pic_list[l])
        siz = im.size
        w = siz[0]
        h = siz[1]

        nw = aw
        nh = int(aw / w * h);
        im = im.resize((nw, nh), Image.ANTIALIAS)
        new_name = "{3}{1}{0:04d}{2}".format(l, prefix, pic_list[l][pic_list[l].rindex("."):], dir)
        print(new_name, nw, nh)
        im.save(new_name, optimize=True, quality=95)


base_dir = "/run/media/liwang/Other/photos/temp/"
if __name__ == "__main__":
    print_and_reduce(base_dir, aw=540)
